from __future__ import annotations

import unittest

from scripts.archive_wechat_articles import RawArticle, build_metadata_article, merge_metadata_articles


class MetadataWriterTest(unittest.TestCase):
    def test_merge_metadata_articles_preserves_existing_id_for_same_path(self) -> None:
        raw_article = RawArticle(
            title="示例文章",
            article_url="https://mp.weixin.qq.com/s/example",
            publish_date="2026-03-11",
            cover_url="https://example.com/cover.png",
            markdown_content="正文",
        )
        existing_article = {
            "id": "2026-03-11-existing-id",
            "date": "2026-03-11",
            "title": "旧标题",
            "path": "2026/03/11/article.md",
            "cover": "2026/03/11/images/cover.png",
            "platforms": {
                "blog": {"status": "published", "url": "https://old.example/article.md"},
                "wechat": {"status": "draft", "htmlPath": "2026/03/11/wechat/article.html", "imagesMapped": False},
                "xiaohongshu": {"status": "draft", "imagesPath": "2026/03/11/xiaohongshu"},
            },
        }

        new_article = build_metadata_article(
            raw_article=raw_article,
            relative_article_path="2026/03/11/article.md",
            relative_cover_path="images/cover.png",
            existing_article=existing_article,
        )

        merged_articles = merge_metadata_articles(
            existing_articles=[existing_article],
            new_articles=[new_article],
        )

        self.assertEqual(len(merged_articles), 1)
        self.assertEqual(merged_articles[0]["id"], "2026-03-11-existing-id")
        self.assertEqual(merged_articles[0]["title"], "示例文章")
        self.assertEqual(merged_articles[0]["platforms"]["blog"]["status"], "published")


if __name__ == "__main__":
    unittest.main()

