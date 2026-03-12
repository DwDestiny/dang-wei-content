from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.archive_wechat_articles import RawArticle, archive_articles


class ArchiveLayoutTest(unittest.TestCase):
    def test_archive_articles_writes_expected_layout(self) -> None:
        raw_article = RawArticle(
            title="测试文章",
            article_url="https://mp.weixin.qq.com/s/test",
            publish_date="2026-03-12",
            cover_url="https://example.com/cover.png",
            markdown_content="第一段\n\n![图一](https://example.com/body-image.jpg)",
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            repository_root = Path(temporary_directory)
            metadata_path = repository_root / "metadata.json"
            metadata_path.write_text(
                json.dumps({"version": "1.0", "lastUpdated": "", "articles": []}, ensure_ascii=False),
                encoding="utf-8",
            )

            def fake_download_asset(asset_url: str) -> tuple[bytes, str]:
                if asset_url.endswith(".png"):
                    return b"cover-bytes", "image/png"
                return b"body-bytes", "image/jpeg"

            archive_articles(
                raw_articles=[raw_article],
                repository_root=repository_root,
                metadata_path=metadata_path,
                download_asset=fake_download_asset,
            )

            article_path = repository_root / "2026" / "03" / "12" / "article.md"
            cover_path = repository_root / "2026" / "03" / "12" / "images" / "cover.png"
            image_path = repository_root / "2026" / "03" / "12" / "images" / "image-01.jpg"

            self.assertTrue(article_path.exists())
            self.assertTrue(cover_path.exists())
            self.assertTrue(image_path.exists())

            article_text = article_path.read_text(encoding="utf-8")
            self.assertIn("# 测试文章", article_text)
            self.assertIn("![图一](images/image-01.jpg)", article_text)


if __name__ == "__main__":
    unittest.main()

