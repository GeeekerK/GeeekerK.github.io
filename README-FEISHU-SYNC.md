# 飞书写博客 → GitHub 自动发布（Hexo）

用飞书云文档写作（手机 / 电脑 / 网页多端），通过 GitHub Actions 定时同步文章并自动构建部署到
GitHub Pages。**写作入口收敛到飞书，写完后最多 15 分钟内自动上线。**

```
飞书 App（多端写作）
   │  飞书开放 API（tenant_access_token）
   ▼
GitHub Actions（每 15 分钟定时）
   ├─ 1. 读取「博客」文件夹下的文档
   ├─ 2. 转 Markdown + front-matter，图片转存 source/images/feishu
   ├─ 3. 提交到仓库（内容不变则跳过，保持 git 历史干净）
   └─ 4. hexo generate → 部署 GitHub Pages
   ▼
geeekerk.github.io 自动更新
```

## 目录

- [A. 一次性配置（约 20 分钟）](#a-一次性配置)
  - [A1. 飞书侧：创建应用并授权](#a1-飞书侧创建应用并授权)
  - [A2. GitHub 侧：配置 Secrets 与 Pages](#a2-github-侧配置-secrets-与-pages)
  - [A3. 把源码迁移到仓库](#a3-把源码迁移到仓库)
- [B. 日常使用](#b-日常使用)
- [C. 手动触发 / 本地自测](#c-手动触发--本地自测)
- [D. 排错 FAQ](#d-排错-faq)

---

## A. 一次性配置

### A1. 飞书侧：创建应用并授权

1. 打开飞书开放平台 <https://open.feishu.cn/app>，登录你的飞书账号（个人版账号同样可以创建应用）。
2. 点击「创建企业自建应用」，填写名称（如 `blog-sync`）和描述，创建后进入应用后台。
3. 左侧「凭证与基础信息」页面，记下 **App ID** 和 **App Secret**（App Secret 只显示一次，如没保存可重置）。
4. 左侧「权限管理」→ 搜索并开通以下权限（只读即可）：
   - `查看升级版文档`（读文档内容，docx 相关）
   - `查看、评论和下载云空间中所有文件`（列文件夹 + 下载图片）
   - 若找不到上面两个，可按页面提示搜索 `docx`、`drive` 相关只读权限申请。
5. 左侧「应用能力」→ 添加「机器人」能力（用于把应用加入群，从而获得你个人云空间的文件夹访问授权，见第 7 步）。
6. 左侧「版本管理与发布」→ 创建版本并发布。**自建应用必须发布后 API 才可用**。
7. 在飞书客户端里：
   - 新建一个群（如「博客同步」），把刚创建的应用（机器人）拉进群；
   - 在云空间新建文件夹「博客文章」（存放所有博客文档）；
   - 把这个文件夹**分享给这个群**（点文件夹 → 分享 → 添加群 → 权限选「可管理」或「可编辑」）。
   - 这样应用（用 tenant_access_token 调用 API 时）就能访问该文件夹。这是官方 FAQ 推荐的做法。
8. 拿到文件夹 token：
   - 在云空间网页版打开「博客文章」文件夹，URL 形如
     `https://xxx.feishu.cn/drive/folder/<文件夹token>`，尖括号里那串就是 **folder token**（形如 `fldxxxxxxxx`）。

> 备选：如果不想用「群分享」方式，也可以用你个人账号的 `user_access_token` 直接访问自有资源，
> 但 user_access_token 有效期只有 2 小时，不适合定时任务，不推荐作为长期方案。

### A2. GitHub 侧：配置 Secrets 与 Pages

在博客源码仓库（`geeekerk/geeekerk.github.io`）中：

1. **配置 Secrets**：仓库 `Settings → Secrets and variables → Actions → New repository secret`，新增 3 个：
   | 名称 | 值 |
   | --- | --- |
   | `FEISHU_APP_ID` | A1 第 3 步拿到的 App ID |
   | `FEISHU_APP_SECRET` | A1 第 3 步拿到的 App Secret |
   | `FEISHU_FOLDER_TOKEN` | A1 第 8 步拿到的文件夹 token |
2. **确认 Pages 发布方式**：`Settings → Pages → Build and deployment → Source` 选择
   **GitHub Actions**（workflow 通过 `deploy-pages` 发布，这是本方案要求的方式）。
3. **确认 workflow 存在**：把本目录的 `.github/workflows/blog-sync.yml` 和 `tools/` 放进仓库并提交。

### A3. 把源码迁移到仓库

> ⚠️ 执行前先在本地备份：`git clone` 一份当前 `geeekerk.github.io` 仓库，以及备份你本地的
> `lokiBLOG` 项目文件夹。下面操作会把仓库 `main` 分支从「编译产物」替换为「Hexo 源码」，
> 替换后旧产物会被 workflow 重新生成，博客内容不丢失（前提：源码的 `source/_posts` 完整）。

1. 把本地 Hexo 项目（`lokiBLOG`，含 `_config.yml`、`scaffolds/`、`source/`、`package.json` 等）拷贝进本仓库目录：
   ```
   # 在仓库目录下
   cp -r <本地 lokiBLOG 路径>/* .
   cp -r <本地 lokiBLOG 路径>/.gitignore . 2>/dev/null || true
   ```
2. 解压本交付包 `lokiBLOG-feishu-sync-package.zip` 到项目根目录（包含 `.github/workflows/blog-sync.yml`、
   `tools/sync_from_feishu.py`、`tools/tests/`、`README-FEISHU-SYNC.md`）：
   ```
   unzip lokiBLOG-feishu-sync-package.zip
   ```
3. 提交并推送（会覆盖旧产物分支历史，使用 force push，确认无误后执行）：
   ```
   git add -A
   git commit -m "feat: migrate to Hexo source + Feishu sync"
   git push origin main --force
   ```
4. 去仓库 `Actions` 页，点「Blog Sync & Deploy」→「Run workflow」手动触发一次，
   观察首次运行是否成功；成功后打开 <https://geeekerk.github.io> 确认站点正常。

> 仓库默认分支保持 `main` 即可（schedule 定时任务只认默认分支上的 workflow 文件）。
> 当前仓库 `main` 分支里的旧产物（index.html、archives 等）在迁移后会被源码替代，无需保留。
> 提示：`db.json` 是 Hexo 的构建缓存，会随每次构建变化。若它已在 git 追踪中，
> 建议执行一次 `git rm --cached db.json` 让 `.gitignore` 生效，避免每次构建产生无关 diff。

---

## B. 日常使用

**写作**：在飞书云空间的「博客文章」文件夹里新建文档，标题按以下格式命名：

```
2026-10-01-我的第一篇博客
```

- 日期前缀可选。带日期 → 作为文章 `date`；不带 → 取当天日期。
- 正文用飞书文档的标题、列表、引用、代码块、图片等即可，会自动转成 Markdown。
- 图片会自动下载到 `source/images/feishu/<文章名>/` 并在文中引用，无需手动处理。
- 写完**不需要任何其他操作**，等下一次定时任务（≤15 分钟）自动同步并发布。
- 想立即生效：到仓库 `Actions` 页手动点一次「Run workflow」。

**分类 / 标签**：目前自动生成空的 `categories: []`、`tags: []`，需要时直接在
`source/_posts/<文章>.md` 的 front-matter 里补上（或在飞书文档里约定特殊格式，后续可扩展）。

**编辑已发布文章**：直接改飞书文档，脚本检测到内容变化会覆盖更新对应的 md 并重新部署。
内容完全没变时不会产生提交（幂等）。

---

## C. 手动触发 / 本地自测

**手动触发**：仓库 `Actions` 页 → `Blog Sync & Deploy` → `Run workflow`。

**本地自测**（可选，不依赖 GitHub）：
```bash
# 需要先设置环境变量
export FEISHU_APP_ID=cli_xxx
export FEISHU_APP_SECRET=xxx
export FEISHU_FOLDER_TOKEN=fldxxx

# 只预览不落盘
FEISHU_DRY_RUN=1 python3 tools/sync_from_feishu.py

# 真正写入 source/_posts（在博客项目根目录执行）
python3 tools/sync_from_feishu.py
```

---

## D. 排错 FAQ

| 现象 | 原因与处理 |
| --- | --- |
| `code=99991400` / 限频 | 文档类接口单应用 QPS 3 次/秒，脚本已带指数退避重试；持续出现说明文档太多，可调大 `MAX_RETRY`。 |
| 403 / 无权限 | ① 应用未发布（A1 第 6 步）；② 文件夹没分享给应用所在群（A1 第 7 步）；③ 权限没开通完整（A1 第 4 步）；④ 分享权限太低，改成「可管理」。 |
| `tenant_access_token` 获取失败 | App Secret 复制错误或已重置，回开放平台重新复制。 |
| 图片没显示 | 图片下载需要 `查看、评论和下载云空间中所有文件` 权限；检查图片是否在文档中被删除或链接过期。 |
| Actions 没按定时跑 | ① workflow 文件必须存在于**默认分支**；② 仓库默认分支是否还是 `main`；③ 定时任务有分钟级延迟，属正常。 |
| npm ci 报错 | 项目没有 `package-lock.json` 时会自动 fallback 到 `npm install`；仍失败请确认 `package.json` 完整。 |
| 私有仓库 Actions 额度 | 私有仓库免费 2000 分钟/月，当前 15 分钟一次约消耗 300 分钟/月，够用；public 仓库不限时。 |

---

## 备选：不改 Pages 设置（从分支发布）的旧模式

如果不想把 Pages Source 改成 GitHub Actions，也可以保留「Deploy from a branch: main」：
workflow 构建后把 `public/` 强制推送到 `main` 分支。代价是 `main` 分支始终是产物，
源码需要放到另一个分支（如 `source`），并且 workflow 文件必须复制一份到 `main` 分支
（否则 schedule 不触发），`main` 每次部署时要保留 `.github/` 目录。复杂度更高，
**不推荐**，本交付物默认采用官方推荐的 GitHub Actions 发布模式。
