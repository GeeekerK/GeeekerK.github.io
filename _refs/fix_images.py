# -*- coding: utf-8 -*-
"""把迁移文章中的本地图片路径改写为 /images/<basename>"""
import os, re, glob

POSTS = r"E:\KimiData\kimi\Workspaces\lokiBLOG\source\_posts"
IMAGES = r"E:\KimiData\kimi\Workspaces\lokiBLOG\source\images"

known = {os.path.basename(p) for p in glob.glob(os.path.join(IMAGES, "*"))}

# 匹配 markdown 图片：![alt](url "title")，其中 alt/url 可能带引号或反斜杠路径
img_re = re.compile(r'!\[([^\]]*)\]\(\s*("?)([^)\s"]+)\2(?:\s+"[^"]*")?\s*\)')

def fix(md_path):
    with open(md_path, "r", encoding="utf-8") as f:
        text = f.read()
    changed = [0]

    def repl(m):
        alt, _, url = m.groups()
        # 从 alt 或 url 中提取可能的文件名
        candidates = [url]
        m2 = re.search(r'[\\/"]([^\\/"]+\.(?:png|jpe?g|gif|webp))', url, re.I)
        if m2:
            candidates.append(m2.group(1))
        m3 = re.search(r'[\\/"]([^\\/"]+\.(?:png|jpe?g|gif|webp))', alt, re.I)
        if m3:
            candidates.append(m3.group(1))
        for c in candidates:
            base = os.path.basename(c.strip('"'))
            if base in known:
                name = os.path.splitext(base)[0]
                changed[0] += 1
                return "![%s](/images/%s)" % (name, base)
        return m.group(0)  # 远程图片或未识别的保持原样

    out = img_re.sub(repl, text)
    if changed[0]:
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(out)
    return changed[0]

total = 0
for p in glob.glob(os.path.join(POSTS, "*.md")):
    n = fix(p)
    if n:
        print("%s: %d 处图片路径已修正" % (os.path.basename(p), n))
        total += n
print("共修正 %d 处" % total)
