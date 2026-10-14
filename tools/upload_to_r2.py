#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""多线程上传 Day One 照片到 R2，并更新 md 引用。"""
import boto3, os, re, json, mimetypes, sys
from botocore.config import Config
from concurrent.futures import ThreadPoolExecutor, as_completed

SRC_DIR = r"F:\2025-2-7-DayOne"
PHOTOS_DIR = os.path.join(SRC_DIR, "photos")
POSTS_DIR = r"E:\KimiData\kimi\Workspaces\lokiBLOG\source\_posts"
PUBLIC_BASE = "https://pub-30d17fc7e72a4ebd980e1c0a6fcb7acc.r2.dev/dayone"
BUCKET = "blog-media"

def get_s3():
    return boto3.client(
        "s3",
        endpoint_url="https://9d5103824db34d6b961fb70a9b0d3b0c.r2.cloudflarestorage.com",
        aws_access_key_id="a0cf6b40646492939e89c68921659b7a",
        aws_secret_access_key="60d8e04c0aabd4ec70e9e8bcd2d47e4f6c2de25184873188beeb4fba1c560d5c",
        region_name="auto",
        config=Config(s3={"addressing_style": "path"}, max_pool_connections=50),
    )

s3 = get_s3()

# 1. 建立 identifier -> (md5, ext) 映射
uuid_to_md5 = {}
for fn in os.listdir(SRC_DIR):
    if not fn.endswith(".json"):
        continue
    with open(os.path.join(SRC_DIR, fn), "r", encoding="utf-8") as f:
        data = json.load(f)
    for e in data.get("entries", []):
        for p in e.get("photos", []):
            ident = p.get("identifier", "")
            md5 = p.get("md5", "")
            ext = p.get("type", "jpg")
            if ident and md5:
                uuid_to_md5[ident] = (md5, ext)
print(f"映射表: {len(uuid_to_md5)} 条")

# 2. 收集已上传对象
existing = set()
paginator = s3.get_paginator("list_objects_v2")
for page in paginator.paginate(Bucket=BUCKET, Prefix="dayone/"):
    for obj in page.get("Contents", []):
        existing.add(obj["Key"].replace("dayone/", ""))
print(f"R2 已有: {len(existing)} 个对象")

# 3. 收集所有需要上传的照片
to_upload = {}  # md5.ext -> local_path
md_files = [f for f in os.listdir(POSTS_DIR) if f.startswith("dayone-") and f.endswith(".md")]
uuid_to_url = {}

for md in md_files:
    path = os.path.join(POSTS_DIR, md)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    for uuid in re.findall(r"dayone-moment://([A-Fa-f0-9]+)", content):
        info = uuid_to_md5.get(uuid)
        if not info:
            continue
        md5, ext = info
        fname = f"{md5}.{ext}"
        local = os.path.join(PHOTOS_DIR, fname)
        if not os.path.exists(local):
            for e2 in (".jpg", ".jpeg", ".png"):
                if os.path.exists(os.path.join(PHOTOS_DIR, md5 + e2)):
                    local = os.path.join(PHOTOS_DIR, md5 + e2)
                    fname = md5 + e2
                    ext = e2.lstrip(".")
                    break
        if os.path.exists(local):
            to_upload[fname] = local

print(f"需要上传: {len(to_upload)} 张")

# 4. 多线程上传
uploaded = 0
failed = []
def upload_one(fname, local):
    key = f"dayone/{fname}"
    ct = mimetypes.guess_type(local)[0] or "image/jpeg"
    s3.upload_file(local, BUCKET, key, ExtraArgs={"ContentType": ct})
    return fname

with ThreadPoolExecutor(max_workers=16) as pool:
    futures = {}
    for fname, local in to_upload.items():
        if fname in existing:
            continue
        futures[pool.submit(upload_one, fname, local)] = fname
    for fut in as_completed(futures):
        fname = futures[fut]
        try:
            fut.result()
            uploaded += 1
            if uploaded % 50 == 0:
                print(f"  已上传 {uploaded}/{len(futures)}")
        except Exception as ex:
            failed.append((fname, str(ex)))

print(f"上传完成: {uploaded} 成功, {len(failed)} 失败")

# 5. 更新 md 文件中的引用
replaced = 0
for md in md_files:
    path = os.path.join(POSTS_DIR, md)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    new_content = content
    for uuid in re.findall(r"dayone-moment://([A-Fa-f0-9]+)", content):
        info = uuid_to_md5.get(uuid)
        if not info:
            new_content = re.sub(r"!\[\]\(dayone-moment://" + re.escape(uuid) + r"\)\n?", "", new_content)
            continue
        md5, ext = info
        fname = f"{md5}.{ext}"
        if fname in existing or fname in to_upload:
            url = f"{PUBLIC_BASE}/{fname}"
            new_content = new_content.replace(f"![](dayone-moment://{uuid})", f"![]({url})")
            replaced += 1
        else:
            new_content = re.sub(r"!\[\]\(dayone-moment://" + re.escape(uuid) + r"\)\n?", "", new_content)
    if new_content != content:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)

print(f"md 引用替换: {replaced} 处")
if failed:
    print("失败示例:", failed[:5])
