from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import re
import urllib.parse
import urllib.request
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable

try:
    from bs4 import BeautifulSoup
except ImportError:  # pragma: no cover
    BeautifulSoup = None

try:
    from markdownify import markdownify as markdownify_html
except ImportError:  # pragma: no cover
    markdownify_html = None


DOWNLOAD_TIMEOUT_SECONDS = 30
BLOG_BASE_URL = "https://dwdestiny.github.io/dang-wei-content"


class ArchiveError(RuntimeError):
    pass


@dataclass(slots=True)
class RawArticle:
    title: str
    article_url: str
    publish_date: str
    cover_url: str
    markdown_content: str = ""
    html_content: str = ""


def parse_raw_articles(raw_payload: list[dict]) -> list[RawArticle]:
    articles: list[RawArticle] = []
    for raw_item in raw_payload:
        title = str(raw_item.get("title", "")).strip()
        article_url = str(raw_item.get("article_url", "")).strip()
        publish_date = normalize_publish_date(str(raw_item.get("publish_date", "")).strip())
        cover_url = str(raw_item.get("cover_url", "")).strip()
        markdown_content = str(raw_item.get("markdown_content", "")).strip()
        html_content = str(raw_item.get("html_content", "")).strip()

        if not title:
            raise ArchiveError("存在缺少标题的文章记录")
        if not article_url:
            raise ArchiveError(f"文章《{title}》缺少 article_url")
        if not publish_date:
            raise ArchiveError(f"文章《{title}》缺少 publish_date")
        if not cover_url:
            raise ArchiveError(f"文章《{title}》缺少 cover_url")
        if not markdown_content and not html_content:
            raise ArchiveError(f"文章《{title}》既没有 markdown_content 也没有 html_content")

        articles.append(
            RawArticle(
                title=title,
                article_url=article_url,
                publish_date=publish_date,
                cover_url=cover_url,
                markdown_content=markdown_content,
                html_content=html_content,
            )
        )
    return articles


def normalize_publish_date(publish_date: str) -> str:
    if not publish_date:
        return ""

    date_candidates = [
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%fZ",
    ]
    for date_format in date_candidates:
        try:
            return datetime.strptime(publish_date, date_format).strftime("%Y-%m-%d")
        except ValueError:
            continue

    try:
        return datetime.fromisoformat(publish_date.replace("Z", "+00:00")).strftime("%Y-%m-%d")
    except ValueError as exc:
        raise ArchiveError(f"无法解析发布日期: {publish_date}") from exc


def article_directory_from_date(publish_date: str) -> Path:
    year_text, month_text, day_text = publish_date.split("-")
    return Path(year_text) / month_text / day_text


def build_article_id(publish_date: str, title: str) -> str:
    title_hash = hashlib.md5(title.encode("utf-8")).hexdigest()[:8]
    ascii_words = re.findall(r"[a-z0-9]+", title.lower())
    suffix = "-".join(ascii_words[:6]).strip("-")
    if suffix:
        return f"{publish_date}-{suffix}-{title_hash}"
    return f"{publish_date}-article-{title_hash}"


def sanitize_markdown(markdown_text: str) -> str:
    normalized_text = markdown_text.replace("\r\n", "\n").replace("\r", "\n").strip()
    normalized_text = re.sub(r"\n{3,}", "\n\n", normalized_text)
    return normalized_text


def html_to_markdown(html_content: str) -> str:
    if not BeautifulSoup or not markdownify_html:
        raise ArchiveError("缺少 HTML 转 Markdown 所需依赖，请安装 beautifulsoup4 和 markdownify")

    soup = BeautifulSoup(html_content, "html.parser")
    content_node = soup.select_one("#js_content") or soup.body
    if content_node is None:
        raise ArchiveError("HTML 中未找到正文容器")

    for useless_selector in [
        "script",
        "style",
        ".wx_profile_card_inner",
        ".wx_tap_link",
        ".js_uneditable",
        ".original_primary_card_tips",
    ]:
        for node in content_node.select(useless_selector):
            node.decompose()

    return sanitize_markdown(markdownify_html(str(content_node), heading_style="ATX"))


def render_article_markdown(title: str, markdown_body: str, image_mapping: dict[str, str], article_url: str) -> str:
    normalized_body = sanitize_markdown(markdown_body)
    for remote_url, local_path in image_mapping.items():
        normalized_body = normalized_body.replace(f"({remote_url})", f"({local_path})")
        normalized_body = normalized_body.replace(f"({remote_url.replace('&', '&amp;')})", f"({local_path})")

    title_header = f"# {title}".strip()
    if normalized_body.startswith("# "):
        normalized_body = re.sub(r"^# .+\n+", "", normalized_body, count=1).strip()

    article_markdown = f"{title_header}\n\n{normalized_body}\n\n*原文发布于：{article_url}*\n"
    return sanitize_markdown(article_markdown) + "\n"


def guess_extension(asset_url: str, content_type: str, default_extension: str) -> str:
    parsed_url = urllib.parse.urlparse(asset_url)
    query_params = urllib.parse.parse_qs(parsed_url.query)
    wx_format = query_params.get("wx_fmt", [])
    if wx_format:
        return normalize_extension(wx_format[0], default_extension)

    content_extension = mimetypes.guess_extension(content_type.split(";")[0].strip()) if content_type else None
    if content_extension:
        return normalize_extension(content_extension, default_extension)

    path_extension = Path(parsed_url.path).suffix
    if path_extension:
        return normalize_extension(path_extension, default_extension)

    return default_extension


def normalize_extension(extension_text: str, default_extension: str) -> str:
    extension_value = extension_text.strip().lower().lstrip(".")
    if not extension_value:
        return default_extension
    if extension_value == "jpeg":
        extension_value = "jpg"
    return f".{extension_value}"


def default_download_asset(asset_url: str) -> tuple[bytes, str]:
    request = urllib.request.Request(asset_url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=DOWNLOAD_TIMEOUT_SECONDS) as response:
        return response.read(), response.headers.get("Content-Type", "")


def extract_image_urls(markdown_body: str) -> list[str]:
    image_urls = re.findall(r"!\[[^\]]*]\((https?://[^)]+)\)", markdown_body)
    unique_urls: list[str] = []
    seen_urls: set[str] = set()
    for image_url in image_urls:
        if image_url not in seen_urls:
            seen_urls.add(image_url)
            unique_urls.append(image_url)
    return unique_urls


def localize_assets(
    article: RawArticle,
    markdown_body: str,
    article_directory: Path,
    download_asset: Callable[[str], tuple[bytes, str]] = default_download_asset,
) -> dict[str, str]:
    images_directory = article_directory / "images"
    images_directory.mkdir(parents=True, exist_ok=True)

    image_mapping: dict[str, str] = {}

    cover_bytes, cover_content_type = download_asset(article.cover_url)
    cover_extension = guess_extension(article.cover_url, cover_content_type, ".jpg")
    cover_filename = f"cover{cover_extension}"
    (images_directory / cover_filename).write_bytes(cover_bytes)

    image_urls = extract_image_urls(markdown_body)
    for image_index, image_url in enumerate(image_urls, start=1):
        image_bytes, image_content_type = download_asset(image_url)
        image_extension = guess_extension(image_url, image_content_type, ".jpg")
        image_filename = f"image-{image_index:02d}{image_extension}"
        (images_directory / image_filename).write_bytes(image_bytes)
        image_mapping[image_url] = f"images/{image_filename}"

    return {
        "cover_path": f"images/{cover_filename}",
        "image_mapping": image_mapping,
    }


def load_metadata(metadata_path: Path) -> dict:
    if metadata_path.exists():
        return json.loads(metadata_path.read_text(encoding="utf-8"))
    return {"version": "1.0", "lastUpdated": "", "articles": []}


def save_metadata(metadata_path: Path, metadata_payload: dict) -> None:
    metadata_path.write_text(
        json.dumps(metadata_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def build_metadata_article(
    raw_article: RawArticle,
    relative_article_path: str,
    relative_cover_path: str,
    existing_article: dict | None,
) -> dict:
    if existing_article:
        metadata_article = deepcopy(existing_article)
    else:
        metadata_article = {
            "platforms": {
                "blog": {"status": "draft", "url": None},
                "wechat": {"status": "draft", "htmlPath": str(Path(relative_article_path).parent / "wechat" / "article.html"), "imagesMapped": False},
                "xiaohongshu": {"status": "draft", "imagesPath": str(Path(relative_article_path).parent / "xiaohongshu")},
            }
        }

    metadata_article["id"] = metadata_article.get("id") or build_article_id(raw_article.publish_date, raw_article.title)
    metadata_article["date"] = raw_article.publish_date
    metadata_article["title"] = raw_article.title
    metadata_article["path"] = relative_article_path
    metadata_article["cover"] = str(Path(relative_article_path).parent / relative_cover_path)
    metadata_article["source_url"] = raw_article.article_url
    metadata_article["platforms"]["blog"]["url"] = f"{BLOG_BASE_URL}/{relative_article_path}"
    return metadata_article


def merge_metadata_articles(existing_articles: list[dict], new_articles: list[dict]) -> list[dict]:
    merged_by_path = {article["path"]: deepcopy(article) for article in existing_articles}
    for article in new_articles:
        merged_by_path[article["path"]] = deepcopy(article)

    merged_articles = list(merged_by_path.values())
    merged_articles.sort(key=lambda article: (article["date"], article["title"]), reverse=True)
    return merged_articles


def archive_articles(
    raw_articles: list[RawArticle],
    repository_root: Path,
    metadata_path: Path,
    download_asset: Callable[[str], tuple[bytes, str]] = default_download_asset,
) -> list[dict]:
    archived_articles: list[dict] = []
    metadata_payload = load_metadata(metadata_path)
    existing_articles = metadata_payload.get("articles", [])
    existing_by_path = {article["path"]: article for article in existing_articles}

    for raw_article in raw_articles:
        article_directory = repository_root / article_directory_from_date(raw_article.publish_date)
        article_directory.mkdir(parents=True, exist_ok=True)

        markdown_body = raw_article.markdown_content or html_to_markdown(raw_article.html_content)
        localized_assets = localize_assets(raw_article, markdown_body, article_directory, download_asset=download_asset)
        article_markdown = render_article_markdown(
            title=raw_article.title,
            markdown_body=markdown_body,
            image_mapping=localized_assets["image_mapping"],
            article_url=raw_article.article_url,
        )

        article_path = article_directory / "article.md"
        article_path.write_text(article_markdown, encoding="utf-8")

        relative_article_path = str(article_path.relative_to(repository_root))
        metadata_article = build_metadata_article(
            raw_article=raw_article,
            relative_article_path=relative_article_path,
            relative_cover_path=localized_assets["cover_path"],
            existing_article=existing_by_path.get(relative_article_path),
        )
        archived_articles.append(metadata_article)

    metadata_payload["articles"] = merge_metadata_articles(existing_articles, archived_articles)
    metadata_payload["lastUpdated"] = datetime.now().astimezone().isoformat(timespec="seconds")
    save_metadata(metadata_path, metadata_payload)
    return archived_articles


def build_argument_parser() -> argparse.ArgumentParser:
    argument_parser = argparse.ArgumentParser(description="将公众号原始导出数据落库到内容仓库")
    argument_parser.add_argument("--input", required=True, help="原始导出 JSON 文件路径")
    argument_parser.add_argument("--root", default=".", help="仓库根目录")
    argument_parser.add_argument("--metadata", default="metadata.json", help="metadata.json 路径")
    return argument_parser


def main() -> int:
    argument_parser = build_argument_parser()
    argument_values = argument_parser.parse_args()

    repository_root = Path(argument_values.root).resolve()
    metadata_path = (repository_root / argument_values.metadata).resolve()
    raw_file_path = Path(argument_values.input).resolve()

    raw_payload = json.loads(raw_file_path.read_text(encoding="utf-8"))
    raw_articles = parse_raw_articles(raw_payload)
    archived_articles = archive_articles(
        raw_articles=raw_articles,
        repository_root=repository_root,
        metadata_path=metadata_path,
    )
    print(json.dumps({"archived_count": len(archived_articles)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

