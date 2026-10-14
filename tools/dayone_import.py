#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""重新生成 Day One 日记：标题用日期，原标题放正文；图片引用先保留占位。"""
import json, os, re
from datetime import datetime, timezone, timedelta

SRC_DIR = r"F:\2025-2-7-DayOne"
OUT_DIR = r"E:\KimiData\kimi\Workspaces\lokiBLOG\source\_posts"
CST = timezone(timedelta(hours=8))

def sanitize(name):
    return re.sub(r'[\\/:*?"<>|#\[\]]', '', name).strip()[:80]

def make_title(text, dt):
    for line in text.strip().split('\n'):
        line = line.strip().lstrip('#').strip()
        if line and not line.startswith('!') and not line.startswith('dayone-moment'):
            return sanitize(line)
    return ''

def convert():
    entries = []
    for fn in os.listdir(SRC_DIR):
        if fn.endswith('.json'):
            with open(os.path.join(SRC_DIR, fn), 'r', encoding='utf-8') as f:
                data = json.load(f)
                entries.extend(data.get('entries', []))
    seen = set()
    uniq = []
    for e in entries:
        u = e.get('uuid')
        if u and u not in seen:
            seen.add(u)
            uniq.append(e)
    entries = sorted(uniq, key=lambda e: e.get('creationDate', ''))

    # 先删除旧的 dayone-*.md
    for f in os.listdir(OUT_DIR):
        if f.startswith('dayone-') and f.endswith('.md'):
            os.remove(os.path.join(OUT_DIR, f))

    count = 0
    for e in entries:
        raw = e.get('text', '').strip()
        if not raw or raw.startswith('# Day One 基本指南'):
            continue
        dt_str = e.get('creationDate', '')
        try:
            dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00')).astimezone(CST)
        except:
            continue

        tags = e.get('tags', [])
        if isinstance(tags, str):
            tags = [tags]
        tags = [t for t in tags if t and t != 'Daily Prompt']

        orig_title = make_title(raw, dt)
        # 标题用日期
        title = dt.strftime('%Y/%m/%d')
        # 正文：保留 dayone-moment 图片引用（后续上传脚本替换为 R2 URL）
        body = raw.strip()
        # 如果原标题和正文开头不一样，把原标题加进去
        if orig_title and not body.startswith('# ' + orig_title):
            body = f'**{orig_title}**\n\n' + body

        fname = f"dayone-{dt.strftime('%Y-%m-%d')}-{count}.md"
        fpath = os.path.join(OUT_DIR, fname)

        fm = [
            '---',
            f'title: "{title}"',
            f'date: {dt.strftime("%Y-%m-%dT%H:%M:%S+08:00")}',
            'categories: [日记]',
        ]
        if tags:
            fm.append('tags: [' + ', '.join(f'"{t}"' for t in tags) + ']')
        fm.append('---')
        fm.append('')
        fm.append(body)

        with open(fpath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(fm))
        count += 1

    print(f"完成：{count} 篇")

if __name__ == '__main__':
    convert()
