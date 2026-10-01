#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""端到端模拟：mock 飞书 API 响应，验证 main() 全流程（首次写入 + 二次幂等跳过）"""

import json
import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import sync_from_feishu as sfs


def build_fake_responses():
    """构造与真实飞书接口同构的假响应"""
    doc_blocks = {
        "code": 0,
        "data": {
            "has_more": False,
            "items": [
                {"block_id": "root", "block_type": 1, "parent_id": "docx1"},
                {"block_id": "h1", "block_type": 3, "parent_id": "root",
                 "text": {"elements": [{"text_run": {"content": "模拟标题"}}]}},
                {"block_id": "p1", "block_type": 2, "parent_id": "root",
                 "text": {"elements": [{"text_run": {"content": "这是正文段落"}}]}},
                {"block_id": "i1", "block_type": 27, "parent_id": "root",
                 "image": {"token": "img_v2_fake"}},
            ],
        },
    }

    def http_handler(method, url, token=None, body=None, timeout=30):
        if "tenant_access_token" in url:
            return {"code": 0, "tenant_access_token": "t-fake"}
        if "/drive/v1/files" in url:
            return {"code": 0, "data": {"has_more": False, "files": [
                {"name": "2026-10-01-模拟文章", "token": "docx1", "type": "docx", "url": "https://feishu.cn/docx1"},
            ]}}
        if "/docx/v1/documents/docx1/blocks" in url:
            return doc_blocks
        if "batch_get_tmp_download_url" in url:
            assert body == {"file_tokens": ["img_v2_fake"]}, body
            return {"code": 0, "data": {"tmp_download_urls": [
                {"file_token": "img_v2_fake", "tmp_download_url": "https://fake.download/img"},
            ]}}
        raise AssertionError("未预期的请求: %s %s" % (method, url))

    return http_handler


class TestEndToEnd(unittest.TestCase):
    def test_full_flow_and_idempotency(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = {
                "FEISHU_APP_ID": "cli_fake",
                "FEISHU_APP_SECRET": "sec_fake",
                "FEISHU_FOLDER_TOKEN": "fld_fake",
                "BLOG_POSTS_DIR": os.path.join(tmp, "source", "_posts"),
                "BLOG_IMAGES_DIR": os.path.join(tmp, "source", "images", "feishu"),
                "FEISHU_BASE_URL": "https://open.feishu.cn",
            }
            with mock.patch.dict(os.environ, env, clear=False):
                with mock.patch.object(sfs, "_http", side_effect=build_fake_responses()):
                    with mock.patch.object(
                        sfs, "download_media", side_effect=lambda url, dest: _fake_download(dest)
                    ):
                        # 第一次：应写入 1 篇
                        rc1 = sfs.main()
                        self.assertEqual(rc1, 0)
                        posts_dir = os.path.join(tmp, "source", "_posts")
                        files = os.listdir(posts_dir)
                        self.assertEqual(len(files), 1)
                        md_path = os.path.join(posts_dir, files[0])
                        with open(md_path, encoding="utf-8") as f:
                            content = f.read()
                        self.assertIn("title: 模拟文章", content)
                        self.assertIn("date: 2026-10-01 00:00:00", content)
                        self.assertIn("# 模拟标题", content)
                        self.assertIn("这是正文段落", content)
                        # 图片路径应指向 images 目录
                        self.assertIn("img_v2_fake", content)
                        img_path = os.path.join(tmp, "source", "images", "feishu",
                                                files[0][:-3], "img_v2_fake.img")
                        self.assertTrue(os.path.exists(img_path))

                        # 第二次：内容未变，应全部跳过
                        rc2 = sfs.main()
                        self.assertEqual(rc2, 0)
                        self.assertEqual(os.listdir(posts_dir), files)


def _fake_download(dest):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "wb") as f:
        f.write(b"\x89PNG fake image bytes")
    return os.path.getsize(dest)


if __name__ == "__main__":
    unittest.main(verbosity=2)
