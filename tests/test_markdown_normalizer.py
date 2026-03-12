from __future__ import annotations

import unittest

from scripts.archive_wechat_articles import render_article_markdown


class MarkdownNormalizerTest(unittest.TestCase):
    def test_render_article_markdown_rewrites_remote_images(self) -> None:
        markdown_body = """
## 第二节

正文段落

![示意图](https://example.com/image-a.png)
"""
        article_markdown = render_article_markdown(
            title="我的文章",
            markdown_body=markdown_body,
            image_mapping={"https://example.com/image-a.png": "images/image-01.png"},
            article_url="https://mp.weixin.qq.com/s/example",
        )

        self.assertTrue(article_markdown.startswith("# 我的文章"))
        self.assertIn("## 第二节", article_markdown)
        self.assertIn("![示意图](images/image-01.png)", article_markdown)
        self.assertIn("*原文发布于：https://mp.weixin.qq.com/s/example*", article_markdown)


if __name__ == "__main__":
    unittest.main()

