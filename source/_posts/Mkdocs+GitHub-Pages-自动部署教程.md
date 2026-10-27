---
title: Mkdocs+GitHub Pages 自动部署教程
date: 2026-10-27 00:00:00 +0800
categories: [技术]
tags: [GitHub, MkDocs, 文档部署]
hidden: true
---

# Mkdocs+GitHub Pages 自动部署教程

参考 [https://www.mkdocs.org/getting-started/](https://www.mkdocs.org/getting-started/)

## 新建站点

创建好文件夹（即站点目录），进入其中。使用 `mkdocs new .` 将当前目录作为站点目录，然后修改 mkdocs.yml，比如下面：

```

repo_url: https://github.com/0xFUDAO/Roadmap
site_name: FUDAO RoadMap
site_author: FUDAO
site_url: https://tech.c01dkit.com
docs_dir: docs
copyright: '2023 Content provided by FUDAO'

nav:
  - Home: index.md
  - 开发技术: 技术开发.md
  - 投资调研: 投资调研.md
  - 每周分享: 每周分享.md
  - 相关资源: 相关资源.md
  - About: about.md

theme: readthedocs

```

后面也可以加入 MD 拓展等，但基础运行必要的话这些足够了，如下：

```

markdown_extensions:
  - attr_list
  - md_in_html
  - pymdownx.superfences
  - pymdownx.critic
  - pymdownx.caret
  - pymdownx.keys
  - pymdownx.mark
  - pymdownx.tilde

```

其中 nav 部分用于设置页面左侧的目录栏，可以完全自己制定展开集。上面 nav 生成的页面会有侧边导航菜单（Home 展开状态，Commands、Project layout 等英文选项，以及开发技术、投资调研、每周分享、相关资源等中文分类项，最底部是 About 选项）。

其中每个页面是一个 md 文件，都要放在 docs 目录下。

然后在当前目录运行 `mkdocs serve` 可以在本地 http://127.0.0.1:8000 预览结果。

## 部署站点

1. 在 github 新建一个空仓库

1. （可选）项目中右边击 site/ 新建 .gitignore 文件，防止后续 mkdocs 生成的站点直接上传过去

1. 再本地初始化好仓库（参考上面 GitHub 新建仓库指引），依次运行：

1. `git init` 进行仓库初始化

1. `git add .` 将当前所有文件纳入管理

1. `git commit -m "first commit"` 初始提交

1. `git branch -M main`

1. `git remote add origin git@github.com:xxxx/xxxx.git`

1. `git push -u origin main`

1. `mkdocs gh-deploy --clean` 构建本地站点并自动推送到远程 gh-pages 分支，这条命令会自动生成站点，并创建 gh-pages 分支（若没有），并推送到远程仓库。

1. 随后在 github 仓库选择 Settings，选择左侧 Pages，然后 Build and deployment 部分（如果没有看是不是自己把仓库默认成 Private 了👀）选择 Deploy from a branch，选择对应的 gh-pages 的 root

1. 然后等待构建即可。

## 附加

### 自定义域名

上述默认构建在 https://.github.io/ 里，如果希望自定义域名，可以在 docs 里放上 CNAME，里面写上自定义域名，然后 setting 里填上域名；同时需要在域名管理添加 github 的 CNAME 解析。
