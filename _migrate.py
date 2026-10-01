# -*- coding: utf-8 -*-
"""Migrate selected posts from E:\\Blog\\myblog into lokiBLOG."""
import os, re, shutil, sys

SRC = r"E:\Blog\myblog\source\_posts"
DST = r"E:\KimiData\kimi\Workspaces\lokiBLOG\source\_posts"
IMG_DST = r"E:\KimiData\kimi\Workspaces\lokiBLOG\source\images"

# filename -> (category, tags, title_override, date_override)
MAP = {
    "Blog Record.md":        ("笔记", ["blog", "Markdown"], None, None),
    "CTF Daily.md":          ("笔记", ["CTF", "Crypto"], None, None),
    "CTF Diary.md":          ("日记", ["CTF", "记录"], None, None),
    "CTF Wiki地址.md":       ("笔记", ["CTF", "资源"], None, None),
    "CTF-Crypto.md":         ("技术", ["CTF", "Crypto"], None, None),
    "CTF-Mobile.md":         ("技术", ["CTF", "Mobile"], None, None),
    "CTF-Reverese.md":       ("技术", ["CTF", "Reverse"], "CTF Reverse", None),
    "CTF之Misc篇.md":        ("技术", ["CTF", "Misc"], None, None),
    "CTF基础知识.md":        ("技术", ["CTF", "基础"], None, None),
    "CTF工具箱.md":          ("笔记", ["CTF", "工具"], None, None),
    "Cookies.md":            ("技术", ["Web", "Cookie"], None, None),
    "HeTianLab-Forensics.md":("技术", ["CTF", "取证"], "HeTianLab 流量取证笔记", None),
    "HetianLab.md":          ("笔记", ["记录"], None, None),
    "xim-yi.md":             ("技术", ["CTF", "Writeup"], None, None),
    "代码开发训练.md":       ("技术", ["Code", "训练"], None, None),
    "工具软件下载.md":       ("笔记", ["工具"], None, None),
    "网络安全学习网址.md":   ("笔记", ["安全", "资源"], "网络安全学习网址", "2023-02-21 23:13:30"),
}

IMG_RE = re.compile(r'!\[([^\]]*)\]\(\s*"?(?:[A-Za-z]:[\\/])?Blog[\\/]myblog[\\/]source[\\/]_posts[\\/]([^"\)]+?\.(?:png|jpg|jpeg|gif))"?(?:\s+"[^"]*")?\s*\)', re.I)

def fix_images(body):
    return IMG_RE.sub(lambda m: '![%s](/images/%s)' % (m.group(1), m.group(2)), body)

def migrate(fname, cat, tags, title_o, date_o):
    raw = open(os.path.join(SRC, fname), encoding="utf-8").read()
    m = re.match(r'^---\r?\n(.*?)\r?\n---\r?\n?', raw, re.S)
    fm, body = (m.group(1), raw[m.end():]) if m else ("", raw)
    title = date = None
    if fm:
        tm = re.search(r'^title:\s*(.*)$', fm, re.M)
        dm = re.search(r'^date:\s*(.*)$', fm, re.M)
        title = (tm.group(1).strip() if tm else "") or None
        date = dm.group(1).strip() if dm else None
    title = title_o or title or os.path.splitext(fname)[0]
    date = date_o or date or "2023-02-21 00:00:00"
    tags_yaml = "\n".join("  - " + t for t in tags)
    new_fm = "---\ntitle: %s\ndate: %s\ncategories:\n  - %s\ntags:\n%s\n---\n" % (title, date, cat, tags_yaml)
    body = fix_images(body).lstrip("\n")
    out = os.path.join(DST, fname.replace(" ", "-"))
    open(out, "w", encoding="utf-8", newline="\n").write(new_fm + "\n" + body)
    return out, date

os.makedirs(IMG_DST, exist_ok=True)
done = []
for fname, (cat, tags, t, d) in MAP.items():
    out, date = migrate(fname, cat, tags, t, d)
    done.append((fname, date))

# copy referenced images
imgs = ["W型栅栏密码路径演示.png", "摩尔斯码.png", "ASCII码.png", "Tap Code敲击码.png",
        "二维码隐写.jpg", "二维码补全2.png", "键盘加密1.png", "键盘加密2.png"]
for img in imgs:
    shutil.copy2(os.path.join(SRC, img), os.path.join(IMG_DST, img))

done.sort(key=lambda x: x[1])
for f, d in done:
    print("%-28s %s" % (f, d))
print("earliest:", done[0][1])
print("images copied:", len(os.listdir(IMG_DST)))
