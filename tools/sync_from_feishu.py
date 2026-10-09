#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sync_from_feishu.py — 把飞书云文档同步为 Hexo 博客文章

工作流程
========
1. 用 FEISHU_APP_ID / FEISHU_APP_SECRET 换取 tenant_access_token
2. 列出 FEISHU_FOLDER_TOKEN 文件夹下的全部文档（分页）
3. 逐篇读取 docx 文档的 blocks，转换成 Markdown + front-matter
4. 文档中的图片下载到 BLOG_IMAGES_DIR，Markdown 用站点根相对路径引用
5. 与磁盘上已有的 .md 对比，内容不变则跳过（幂等，保持 git 历史干净）
6. 打印本次新增/更新/无变化的摘要

文档标题规范（重要）
====================
  建议每篇文档标题按以下格式命名，脚本会自动解析 front-matter：
    2026-10-01-我的第一篇博客          -> title: 我的第一篇博客, date: 2026-10-01
    我的第二篇博客                     -> title: 我的第二篇博客, date: 当天

分类（categories）
------------------
  按文档所在的子文件夹自动归类，例如：
    博客文章/日记/xxx  -> categories: [日记]
    博客文章/周报/xxx  -> categories: [周报]
  直接放在「博客文章」根目录的文档：categories 为空。
  在飞书里把文档拖进/拖出子文件夹即可改分类，无需改文档内容。

标签（tags）
------------
  在文档正文最开头单独一行写（脚本会识别并从正文中移除）：
    标签：飞书同步, Hexo, wenfang主题
  多个标签用中英文逗号或顿号分隔。不写这行则 tags 为空。

环境变量
========
  FEISHU_APP_ID       必填 飞书自建应用 App ID
  FEISHU_APP_SECRET   必填 飞书自建应用 App Secret
  FEISHU_FOLDER_TOKEN 必填 存放博客文档的飞书文件夹 token
  FEISHU_BASE_URL     可选 默认 https://open.feishu.cn
  BLOG_POSTS_DIR      可选 默认 source/_posts（相对仓库根目录）
  BLOG_IMAGES_DIR     可选 默认 source/images/feishu
  FEISHU_DRY_RUN      可选 设为 1 时只打印将写入的文件，不落盘

依赖：仅 Python 3 标准库，无需 pip install。
"""

import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from collections import defaultdict

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------
BASE_URL = os.environ.get("FEISHU_BASE_URL", "https://open.feishu.cn").rstrip("/")
DRY_RUN = os.environ.get("FEISHU_DRY_RUN", "0") == "1"
MAX_RETRY = 5


def posts_dir():
    return os.environ.get("BLOG_POSTS_DIR", "source/_posts")


def manifest_path():
    return os.path.join(posts_dir(), ".sync-manifest.json")


def load_manifest():
    """加载飞书文档 token → slug 映射，保证同一文档永远写到同一个 md。"""
    try:
        with open(manifest_path(), "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_manifest(m):
    try:
        with open(manifest_path(), "w", encoding="utf-8") as f:
            json.dump(m, f, ensure_ascii=False, indent=2)
            f.write("\n")
    except Exception as e:
        print("[warn] 写 manifest 失败: %s" % e)


def images_dir():
    return os.environ.get("BLOG_IMAGES_DIR", "source/images/feishu")

# docx block_type 枚举（官方定义）
BT_PAGE = 1
BT_TEXT = 2
BT_H1, BT_H9 = 3, 11            # Heading1..Heading9
BT_BULLET = 12
BT_ORDERED = 13
BT_CODE = 14
BT_QUOTE = 15
BT_CALLOUT = 18
BT_TODO = 17
BT_DIVIDER = 22
BT_IMAGE = 27
BT_TABLE = 31
BT_TABLE_CELL = 32

HEADING_LEVEL = {BT_H1 + i: i + 1 for i in range(BT_H9 - BT_H1 + 1)}

# ---------------------------------------------------------------------------
# HTTP 工具
# ---------------------------------------------------------------------------
class FeishuError(RuntimeError):
    pass


def _http(method, url, token=None, body=None, timeout=30):
    headers = {"Content-Type": "application/json; charset=utf-8"}
    if token:
        headers["Authorization"] = "Bearer " + token
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
    except urllib.error.HTTPError as e:
        raw = e.read()
        if e.code == 429:
            raise FeishuError("限频 429: %s" % raw[:300])
        raise FeishuError("HTTP %s: %s" % (e.code, raw[:300]))
    except urllib.error.URLError as e:
        raise FeishuError("网络错误: %s" % e)
    try:
        parsed = json.loads(raw.decode("utf-8"))
    except Exception:
        raise FeishuError("响应不是合法 JSON: %s" % raw[:300])
    if parsed.get("code", 0) != 0:
        raise FeishuError("code=%s msg=%s" % (parsed.get("code"), parsed.get("msg")))
    return parsed


def get_tenant_token(app_id, app_secret):
    """换取 tenant_access_token（有效期 2 小时）"""
    url = BASE_URL + "/open-apis/auth/v3/tenant_access_token/internal"
    resp = _http("POST", url, body={"app_id": app_id, "app_secret": app_secret})
    token = resp.get("tenant_access_token")
    if not token:
        raise FeishuError("tenant_access_token 获取失败: %s" % resp)
    return token


def _api_get(path, token, params=None, retries=MAX_RETRY):
    """GET 请求 + 限频指数退避重试"""
    query = ("?" + urllib.parse.urlencode(params)) if params else ""
    url = BASE_URL + path + query
    for attempt in range(retries):
        try:
            return _http("GET", url, token=token)
        except FeishuError as e:
            if "99991400" in str(e) or "429" in str(e):
                wait = 2 ** attempt
                print("[warn] 触发限频，%ss 后重试 (%s/%s)" % (wait, attempt + 1, retries))
                time.sleep(wait)
                continue
            raise
    raise FeishuError("接口重试 %s 次仍失败: %s" % (retries, path))


# ---------------------------------------------------------------------------
# 飞书接口
# ---------------------------------------------------------------------------
def list_folder_files(folder_token, token):
    """列出文件夹下的所有文件（分页拉全）"""
    files, page_token = [], ""
    while True:
        params = {"page_size": 200, "order_by": "EditedTime", "direction": "DESC"}
        if folder_token:
            params["folder_token"] = folder_token
        if page_token:
            params["page_token"] = page_token
        resp = _api_get("/open-apis/drive/v1/files", token, params)
        data = resp.get("data", {})
        files.extend(data.get("files", []))
        if not data.get("has_more"):
            break
        page_token = data.get("page_token", "")
        if not page_token:
            break
    return files


def list_folder_tree(folder_token, token, category=""):
    """递归列出文件夹下所有 docx。

    返回 [{name, token, url, category, created_time}]；category 是文档所在一级子文件夹名。
    """
    result = []
    for f in list_folder_files(folder_token, token):
        ftype = f.get("type")
        if ftype == "docx":
            result.append({
                "name": f.get("name", ""),
                "token": f.get("token", ""),
                "url": f.get("url", ""),
                "category": category,
                "created_time": f.get("created_time") or f.get("CreatedTime") or "",
            })
        elif ftype == "folder":
            sub = (f.get("name") or "").strip()
            if sub:
                result.extend(list_folder_tree(f["token"], token, sub))
    return result


def get_document_blocks(document_id, token):
    """获取整篇文档的所有块（分页拉全）"""
    blocks, page_token = [], ""
    while True:
        params = {"page_size": 500}
        if page_token:
            params["page_token"] = page_token
        resp = _api_get(
            "/open-apis/docx/v1/documents/%s/blocks" % urllib.parse.quote(document_id),
            token,
            params,
        )
        data = resp.get("data", {})
        blocks.extend(data.get("items", []))
        if not data.get("has_more"):
            break
        page_token = data.get("page_token", "")
        if not page_token:
            break
    return blocks


def get_media_download_url(file_token, token):
    """获取素材临时下载链接（POST 接口，24h 有效）"""
    url = BASE_URL + "/open-apis/drive/v1/medias/batch_get_tmp_download_url"
    for attempt in range(MAX_RETRY):
        try:
            resp = _http("POST", url, token=token, body={"file_tokens": [file_token]})
            break
        except FeishuError as e:
            if "99991400" in str(e) or "429" in str(e):
                wait = 2 ** attempt
                print("[warn] 素材接口限频，%ss 后重试" % wait)
                time.sleep(wait)
                continue
            raise
    else:
        raise FeishuError("素材下载链接接口重试 %s 次仍失败" % MAX_RETRY)
    tmp = resp.get("data", {}).get("tmp_download_urls", [])
    return tmp[0].get("tmp_download_url") if tmp else None


def download_media(tmp_url, dest_path):
    """下载素材到本地"""
    req = urllib.request.Request(tmp_url, method="GET")
    with urllib.request.urlopen(req, timeout=60) as resp, open(dest_path, "wb") as f:
        f.write(resp.read())
    return os.path.getsize(dest_path)


# ---------------------------------------------------------------------------
# blocks -> Markdown
# ---------------------------------------------------------------------------
def text_from_elements(elements):
    """把 text.elements 渲染成 Markdown 文本（支持粗体/斜体/链接）"""
    parts = []
    for el in elements or []:
        run = el.get("text_run") or {}
        content = run.get("content") or ""
        style = run.get("text_element_style") or {}
        if el.get("mention_user"):
            parts.append("@%s" % (el["mention_user"].get("user_name") or "用户"))
            continue
        if el.get("mention_doc"):
            parts.append("[%s]" % (el["mention_doc"].get("title") or "文档"))
            continue
        if not content:
            continue
        # 转义会影响渲染的裸字符，避免破坏 Markdown
        link = style.get("link")
        if link and link.get("url"):
            content = "[%s](%s)" % (content, link["url"])
        if style.get("bold"):
            content = "**%s**" % content
        if style.get("italic"):
            content = "*%s*" % content
        if style.get("inline_code"):
            content = "`%s`" % content
        parts.append(content)
    return "".join(parts)


def block_text(block):
    """从 block 的 text/heading*/bullet/ordered/code/quote/todo 等结构里取文本"""
    for key in ("text", "heading1", "heading2", "heading3", "heading4",
                "heading5", "heading6", "heading7", "heading8", "heading9",
                "bullet", "ordered", "code", "quote", "todo"):
        obj = block.get(key)
        if obj and isinstance(obj, dict):
            els = obj.get("elements")
            if els:
                return text_from_elements(els)
    return ""


class DocConverter:
    """把平铺的 block 列表转成 Markdown"""

    def __init__(self, document_id, token, slug):
        self.document_id = document_id
        self.token = token
        self.slug = slug
        self.children = defaultdict(list)
        self.order = {}

    def build(self, blocks):
        for i, b in enumerate(blocks):
            self.children[b.get("parent_id", "")].append(b)
            self.order[b.get("block_id")] = i
        roots = [b for b in blocks if b.get("block_type") == BT_PAGE]
        root = roots[0] if roots else blocks[0]
        return self._render_children(root.get("block_id"), depth=0)

    def _render_children(self, parent_id, depth):
        lines = []
        for block in sorted(self.children.get(parent_id, []), key=lambda b: self.order.get(b.get("block_id"), 0)):
            lines.extend(self._render_block(block, depth))
        return lines

    def _render_block(self, block, depth):
        btype = block.get("block_type")
        bid = block.get("block_id", "")
        if btype in HEADING_LEVEL:
            level = HEADING_LEVEL[btype]
            text = block_text(block).strip()
            return ["%s %s" % ("#" * level, text)] if text else []
        if btype == BT_TEXT:
            text = block_text(block).strip()
            return [text] if text else []
        if btype == BT_BULLET:
            text = block_text(block).strip()
            return ["- %s" % text] if text else []
        if btype == BT_ORDERED:
            text = block_text(block).strip()
            return ["1. %s" % text] if text else []
        if btype == BT_TODO:
            text = block_text(block).strip()
            if not text:
                return []
            done = bool((block.get("todo") or {}).get("style", {}).get("done"))
            return ["- [x] %s" % text if done else "- [ ] %s" % text]
        if btype == BT_CODE:
            code = block.get("code") or {}
            lang = code.get("language") or ""
            body = block_text(block)
            fence = "```"
            if lang:
                fence += " " + lang
            return [fence, body, "```"]
        if btype == BT_QUOTE:
            text = block_text(block).strip()
            if text:
                return ["> " + t for t in text.splitlines()]
            return ["> " + l for l in self._render_children(bid, depth + 1)]
        if btype == BT_CALLOUT:
            return self._render_children(bid, depth + 1)
        if btype == BT_DIVIDER:
            return ["---"]
        if btype == BT_IMAGE:
            return self._render_image(block)
        if btype == BT_TABLE:
            return self._render_table(block)
        # 其余类型（表格单元格、内嵌、思维笔记、电子表格等）：
        # 容器类继续递归，叶节点忽略
        child_lines = self._render_children(bid, depth + 1)
        if child_lines:
            return child_lines
        return []

    def _render_image(self, block):
        img = block.get("image") or {}
        file_token = img.get("token")
        if not file_token:
            return []
        rel = self._download_image(file_token)
        if not rel:
            return []
        return ["![%s](%s)" % (self.slug, rel)]

    def _download_image(self, file_token):
        """下载图片到 images 目录，返回站点相对路径；已存在则跳过"""
        img_root = images_dir()
        dest_dir = os.path.join(img_root, self.slug)
        os.makedirs(dest_dir, exist_ok=True)
        dest = os.path.join(dest_dir, "%s.img" % file_token)
        rel = "/%s/%s/%s.img" % (img_root.replace("source/", ""), self.slug, file_token)
        if os.path.exists(dest) and os.path.getsize(dest) > 0:
            return rel
        tmp_url = get_media_download_url(file_token, self.token)
        if not tmp_url:
            print("[warn] 无法获取图片下载链接: %s" % file_token)
            return None
        try:
            size = download_media(tmp_url, dest)
            if size <= 0:
                os.remove(dest)
                return None
            return rel
        except Exception as e:
            print("[warn] 图片下载失败 %s: %s" % (file_token, e))
            return None

    def _render_table(self, block):
        """基础表格渲染：按行列拼 Markdown 表格"""
        prop = block.get("table", {}).get("property", {}) or {}
        rows, cols = prop.get("row_size", 0), prop.get("column_size", 0)
        if rows <= 0 or cols <= 0:
            return []
        cells = {}
        for cell in self.children.get(block.get("block_id", ""), []):
            if cell.get("block_type") != BT_TABLE_CELL:
                continue
            tc = cell.get("table_cell") or {}
            r, c = tc.get("row_index", -1), tc.get("column_index", -1)
            if r < 0 or c < 0:
                continue
            # 单元格内容：优先自身文本，其次子块文本（真实结构中文本是 cell 的子块）
            own = block_text(cell).strip()
            if own:
                text = own
            else:
                text = " ".join(
                    l.strip()
                    for l in self._render_children(cell.get("block_id", ""), 0)
                    if l.strip()
                )
            cells[(r, c)] = text.replace("|", "\\|")
        lines = []
        for r in range(rows):
            row_cells = [cells.get((r, c), "") for c in range(cols)]
            if r == 0:
                lines.append("| " + " | ".join(row_cells) + " |")
                lines.append("| " + " | ".join(["---"] * cols) + " |")
            else:
                lines.append("| " + " | ".join(row_cells) + " |")
        return lines


# ---------------------------------------------------------------------------
# 标题解析 / front-matter
# ---------------------------------------------------------------------------
DATE_RE = re.compile(r"^(\d{4})[-/](\d{1,2})[-/](\d{1,2})[-_\s]*(.*)$")
TAG_LINE_RE = re.compile(r"^标签[:：]\s*(.+?)\s*$")


def parse_title(name):
    """从文档名解析 (date, title)。去掉 .md 后缀"""
    name = re.sub(r"\.md$", "", name.strip())
    m = DATE_RE.match(name)
    if m:
        date = "%s-%02d-%02d" % (m.group(1), int(m.group(2)), int(m.group(3)))
        title = m.group(4).strip() or name
        return date, title
    return time.strftime("%Y-%m-%d"), name


def slugify(title, date):
    """生成安全的文件名：去非法字符，保留中文。
    若 title 本身就是日期（纯日期命名），文件名只用 date，避免 2026-10-03-2026-10-03 这种重复。
    若 date 为空（长文类），只保留标题。"""
    if re.fullmatch(r"[\d/\-年月日\s]+", title or ""):
        return date
    # 去掉中英文标点里不适合做 URL 的字符，保留中文和常见标点
    clean = re.sub(r'[\\/:*?"<>|\s《》〈〉「」『』]+', "-", title).strip("-")
    return "%s-%s" % (date, clean) if date else clean


def extract_tags(body_lines):
    """在正文开头找「标签：xxx, yyy」行，返回 (tags, remaining_lines)。

    只检查跳过空行后的第一行；找不到则 tags 为空、原文不动。
    """
    rest = list(body_lines)
    i = 0
    while i < len(rest) and not rest[i].strip():
        i += 1
    if i < len(rest):
        m = TAG_LINE_RE.match(rest[i].strip())
        if m:
            tags = [t.strip() for t in re.split(r"[,，、]", m.group(1)) if t.strip()]
            return tags, rest[:i] + rest[i + 1:]
    return [], rest


def _yaml_list(items):
    """把列表格式化成 YAML flow list，含中文不需要引号"""
    return "[" + ", ".join(items) + "]" if items else "[]"


def make_front_matter(title, date, categories=None, tags=None, hidden=False):
    fm = (
        "---\n"
        "title: %s\n"
        "date: %s 00:00:00 +0800\n"
        "categories: %s\n"
        "tags: %s\n"
    ) % (title, date, _yaml_list(categories or []), _yaml_list(tags or []))
    if hidden:
        fm += "hidden: true\n"
    fm += "---\n\n"
    return fm


def _pub_entry(title, date, slug):
    """构造 publications.json 里 articles 数组的一条记录"""
    y, m, d = date.split("-")
    return {
        "title": title,
        "venue": "本站 · 读书",
        "year": int(y),
        "link": "/%s/%s/%s/%s/" % (y, m, d, slug),
    }


def _sync_publications(pub_articles):
    """把「文章」文件夹下的文档合并进 source/_data/publications.json 的 articles 数组。

    - 按 link 去重，飞书文档优先（同名手动条目保留）
    - 按 year 倒序、同年按 link 日期倒序
    - 保留手动维护的 papers/books/podcasts/videos 字段
    """
    path = "source/_data/publications.json"
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {"papers": [], "books": [], "articles": [], "podcasts": [], "videos": []}

    existing = data.get("articles", []) or []
    seen = set()
    merged = []
    # 先保留手动条目（link 不以本站 /YYYY/ 日期路径开头的）
    # 自动条目每次全量重建，避免旧版本残留
    for item in existing:
        link = item.get("link", "")
        if re.match(r"^/\d{4}/\d{2}/\d{2}/", link):
            continue  # 自动生成的，丢弃，下面重新加
        seen.add(link)
        merged.append(item)
    # 再加入/更新飞书文章
    for art in pub_articles:
        link = art["link"]
        merged = [m for m in merged if m.get("link") != link]
        merged.append(art)
        seen.add(link)

    # 排序：year 倒序
    merged.sort(key=lambda x: (x.get("year", 0), x.get("link", "")), reverse=True)
    data["articles"] = merged
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("== publications.json 已更新，共 %d 篇文章 ==" % len(merged))


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------
def main():
    app_id = os.environ.get("FEISHU_APP_ID", "").strip()
    app_secret = os.environ.get("FEISHU_APP_SECRET", "").strip()
    folder_token = os.environ.get("FEISHU_FOLDER_TOKEN", "").strip()
    if not (app_id and app_secret):
        print("错误：缺少 FEISHU_APP_ID / FEISHU_APP_SECRET 环境变量", file=sys.stderr)
        return 2

    print("== 获取 tenant_access_token ==")
    token = get_tenant_token(app_id, app_secret)

    print("== 列出飞书文件夹文档（folder_token=%s，含子文件夹）==" % (folder_token or "我的空间根目录"))
    docs = list_folder_tree(folder_token, token)
    print("共文档 %s 篇" % len(docs))
    if not docs:
        print("没有找到文档，结束。")
        return 0

    os.makedirs(posts_dir(), exist_ok=True)
    added, updated, skipped, failed = [], [], [], []
    pub_articles = []  # category=="文章" 的文档，待写入 publications.json
    seen_tokens = set()  # 按飞书文档 token 去重，同一文档不重复处理
    manifest = load_manifest()  # token → slug 映射

    for doc in docs:
        name = doc.get("name", "")
        document_id = doc.get("token", "")
        category = doc.get("category", "")
        created_ts = doc.get("created_time") or ""
        if not document_id:
            failed.append((name, "缺少 token"))
            continue
        if document_id in seen_tokens:
            print("-- 跳过（同文档已处理过）: %s" % name)
            continue
        seen_tokens.add(document_id)
        cat_desc = ("（分类: %s）" % category) if category else "（根目录/未分类）"
        print("-- 处理: %s %s" % (name, cat_desc))
        try:
            blocks = get_document_blocks(document_id, token)
            date, title = parse_title(name)
            # 「文章」类长文：slug 固定为标题（不带日期前缀），date 用飞书文档创建时间
            is_article = (category == "文章")
            if is_article:
                if created_ts:
                    try:
                        # 飞书 created_time 是秒级 Unix 时间戳
                        date = time.strftime("%Y-%m-%d", time.localtime(int(created_ts)))
                    except Exception:
                        pass
                new_slug = slugify(title, "")  # date 留空，只保留标题
            else:
                new_slug = slugify(title, date)
            # 同一飞书文档 token 永远用同一个 slug（即使标题改了也不生成新文件）
            slug = manifest.get(document_id) or new_slug
            manifest[document_id] = slug
            converter = DocConverter(document_id, token, slug)
            body_lines = converter.build(blocks)
            tags, body_lines = extract_tags(body_lines)
            if tags:
                print("  提取标签: %s" % ", ".join(tags))
            categories = [category] if category else []
            body = "\n\n".join(body_lines).strip() + "\n"
            content = make_front_matter(title, date, categories, tags, hidden=is_article) + body
            dest = os.path.join(posts_dir(), slug + ".md")
            if os.path.exists(dest):
                with open(dest, "r", encoding="utf-8") as f:
                    old = f.read()
                if old == content:
                    skipped.append(name)
                    print("  无变化，跳过: %s" % slug)
                    if is_article:
                        pub_articles.append(_pub_entry(title, date, slug))
                    continue
                updated.append(name)
            else:
                added.append(name)
            if DRY_RUN:
                print("  [dry-run] 将写入 %s（%d 字符）" % (dest, len(content)))
            else:
                with open(dest, "w", encoding="utf-8") as f:
                    f.write(content)
                print("  已写入 %s" % dest)
            if is_article:
                pub_articles.append(_pub_entry(title, date, slug))
        except Exception as e:
            failed.append((name, str(e)))
            print("  [error] %s: %s" % (name, e))

    # 同步 publications.json：把「文章」文件夹下的文档加进 articles 数组
    if not DRY_RUN:
        _sync_publications(pub_articles)
        save_manifest(manifest)

    print("\n== 摘要 ==")
    print("新增 %d 篇: %s" % (len(added), ", ".join(added) or "-"))
    print("更新 %d 篇: %s" % (len(updated), ", ".join(updated) or "-"))
    print("无变化 %d 篇" % len(skipped))
    if failed:
        print("失败 %d 篇:" % len(failed))
        for n, err in failed:
            print("  - %s : %s" % (n, err))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
