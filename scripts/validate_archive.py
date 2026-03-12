from __future__ import annotations

import json
import re
from pathlib import Path


def validate_archive(repository_root: Path) -> dict:
    metadata_path = repository_root / "metadata.json"
    metadata_payload = json.loads(metadata_path.read_text(encoding="utf-8"))
    article_paths = sorted(repository_root.glob("20*/**/article.md"))

    missing_files: list[str] = []
    missing_images: list[str] = []
    metadata_paths = {item["path"] for item in metadata_payload.get("articles", [])}

    for article_path in article_paths:
        relative_path = str(article_path.relative_to(repository_root))
        if relative_path not in metadata_paths:
            missing_files.append(relative_path)

        article_text = article_path.read_text(encoding="utf-8")
        for image_path in re.findall(r"!\[[^\]]*]\((images/[^)]+)\)", article_text):
            absolute_image_path = article_path.parent / image_path
            if not absolute_image_path.exists():
                missing_images.append(f"{relative_path}: {image_path}")

    return {
        "metadata_count": len(metadata_payload.get("articles", [])),
        "article_count": len(article_paths),
        "missing_metadata_entries": missing_files,
        "missing_image_refs": missing_images,
    }


def main() -> int:
    repository_root = Path(".").resolve()
    result = validate_archive(repository_root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["missing_metadata_entries"] or result["missing_image_refs"]:
      return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

