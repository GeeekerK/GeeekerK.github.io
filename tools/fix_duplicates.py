#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""去掉 Day One 日记中重复的标题行。"""
import os, re, glob

POSTS_DIR = r"E:\KimiData\kimi\Workspaces\lokiBLOG\source\_posts"

def fix_file(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 分离 frontmatter 和正文
    parts = content.split("---\n", 2)
    if len(parts) < 3:
        return False
    fm = parts[0] + "---\n" + parts[1] + "---\n"
    body = parts[2]

    lines = body.split("\n")
    # 找第一个非空行
    i = 0
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i >= len(lines):
        return False

    first = lines[i].strip()
    # 检查是不是 **标题** 格式
    m = re.match(r"^\*\*(.+?)\*\*$", first)
    if not m:
        return False

    title_text = m.group(1).strip()

    # 在后续行里找这个标题文本（允许中间有空行和图片行）
    found = False
    for j in range(i + 1, min(i + 10, len(lines))):
        stripped = lines[j].strip()
        if not stripped:
            continue
        # 跳过图片行
        if stripped.startswith("![]("):
            continue
        # 跳过 markdown 标题行
        if stripped.startswith("#"):
            continue
        # 比较
        if stripped.rstrip("。.!？!？") == title_text.rstrip("。.!？!？") or stripped == title_text:
            found = True
            break
        else:
            break

    if not found:
        return False

    # 删掉这个加粗标题行
    lines[i] = ""
    new_body = "\n".join(lines)
    # 清理多余空行
    new_body = re.sub(r"\n{3,}", "\n\n", new_body)
    new_content = fm + new_body

    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)
    return True

count = 0
for path in glob.glob(os.path.join(POSTS_DIR, "dayone-*.md")):
    if fix_file(path):
        count += 1

print(f"清理了 {count} 个文件的重复标题")
