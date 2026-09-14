#!/usr/bin/env python3
"""Build a deterministic chart manifest from MinerU content_list_v2 JSON."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
PAPER_DIR_RE = re.compile(r"^paper_(\d+)$", re.IGNORECASE)
FILE_REF_RE = re.compile(r"^(\d+)_")
SPACE_RE = re.compile(r"\s+")
SPACE_BEFORE_PUNCTUATION_RE = re.compile(r"\s+([,.;:!?%)\]])")
SPACE_AFTER_OPEN_RE = re.compile(r"([(\[])\s+")


class ManifestError(ValueError):
    """Raised when the MinerU folder does not meet the input contract."""


def _normalize_text(text: str) -> str:
    text = SPACE_RE.sub(" ", text).strip()
    text = SPACE_BEFORE_PUNCTUATION_RE.sub(r"\1", text)
    return SPACE_AFTER_OPEN_RE.sub(r"\1", text)


def _join_text(parts: list[str]) -> str:
    return _normalize_text(" ".join(part for part in parts if part.strip()))


def flatten_text(value: Any) -> str:
    """Flatten MinerU text/equation fragments without traversing image metadata."""
    if value is None:
        return ""
    if isinstance(value, str):
        return _normalize_text(value)
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return str(value)
    if isinstance(value, list):
        return _join_text([flatten_text(item) for item in value])
    if not isinstance(value, dict):
        return ""

    node_type = value.get("type")
    content = value.get("content")
    if node_type == "text" and isinstance(content, str):
        return _normalize_text(content)
    if node_type in {"equation_inline", "equation_interline"} and isinstance(
        content, str
    ):
        equation = _normalize_text(content)
        return f"${equation}$" if equation else ""

    for key in (
        "paragraph_content",
        "title_content",
        "item_content",
        "list_items",
        "chart_caption",
        "chart_footnote",
    ):
        if key in value:
            return flatten_text(value[key])

    if isinstance(content, (str, list, dict)):
        return flatten_text(content)
    return ""


def flatten_block(block: dict[str, Any]) -> str:
    return flatten_text(block.get("content"))


def _paper_reference(paper_dir: Path, content_list: Path) -> str:
    folder_match = PAPER_DIR_RE.fullmatch(paper_dir.name)
    file_match = FILE_REF_RE.match(content_list.name)
    folder_ref = folder_match.group(1) if folder_match else None
    file_ref = file_match.group(1) if file_match else None
    if folder_ref and file_ref and int(folder_ref) != int(file_ref):
        raise ManifestError(
            f"paper reference mismatch: folder={folder_ref}, file={file_ref}"
        )
    reference = folder_ref or file_ref
    if reference is None:
        raise ManifestError(
            "cannot determine paper reference; use paper_<number> or a numbered JSON file"
        )
    return str(int(reference))


def _find_content_list(paper_dir: Path) -> Path:
    matches = sorted(paper_dir.glob("*_content_list_v2.json"))
    if len(matches) != 1:
        raise ManifestError(
            f"expected exactly one *_content_list_v2.json in {paper_dir}, found {len(matches)}"
        )
    return matches[0]


def _find_markdown(paper_dir: Path, content_list: Path) -> Path | None:
    suffix = "_content_list_v2.json"
    expected = paper_dir / f"{content_list.name.removesuffix(suffix)}.md"
    if expected.is_file():
        return expected.resolve()
    matches = sorted(paper_dir.glob("*.md"))
    return matches[0].resolve() if len(matches) == 1 else None


def _load_pages(content_list: Path) -> list[list[dict[str, Any]]]:
    try:
        raw = json.loads(content_list.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ManifestError(f"cannot read {content_list}: {exc}") from exc

    if not isinstance(raw, list):
        raise ManifestError("content_list_v2 root must be an array")
    if not raw:
        return []
    if all(isinstance(item, dict) for item in raw):
        raw = [raw]
    if not all(isinstance(page, list) for page in raw):
        raise ManifestError("content_list_v2 must contain page arrays")

    pages: list[list[dict[str, Any]]] = []
    for page_number, page in enumerate(raw, start=1):
        if not all(isinstance(block, dict) for block in page):
            raise ManifestError(f"page {page_number} contains a non-object block")
        pages.append(page)
    return pages


def _bbox(block: dict[str, Any]) -> list[float | int] | None:
    value = block.get("bbox")
    if (
        isinstance(value, list)
        and len(value) == 4
        and all(
            isinstance(item, (int, float)) and not isinstance(item, bool)
            for item in value
        )
    ):
        return value
    return None


def _paragraph_record(
    block: dict[str, Any], page_number: int, item_index: int
) -> dict[str, Any] | None:
    text = flatten_block(block)
    if not text:
        return None
    return {
        "page_number": page_number,
        "item_index": item_index + 1,
        "bbox": _bbox(block),
        "text": text,
    }


def _nearby_paragraphs(
    page: list[dict[str, Any]],
    chart_index: int,
    page_number: int,
    count: int,
    direction: int,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    index = chart_index + direction
    while 0 <= index < len(page) and len(records) < count:
        block = page[index]
        if block.get("type") == "paragraph":
            record = _paragraph_record(block, page_number, index)
            if record:
                records.append(record)
        index += direction
    if direction < 0:
        records.reverse()
    return records


def _nearest_section_title(
    page: list[dict[str, Any]], chart_index: int, page_number: int
) -> dict[str, Any] | None:
    for index in range(chart_index - 1, -1, -1):
        block = page[index]
        if block.get("type") == "title":
            text = flatten_block(block)
            if text:
                return {
                    "page_number": page_number,
                    "item_index": index + 1,
                    "bbox": _bbox(block),
                    "text": text,
                }
    return None


def _image_paths(
    paper_dir: Path, chart_content: dict[str, Any]
) -> tuple[str, str, bool]:
    source = chart_content.get("image_source")
    raw_path = source.get("path") if isinstance(source, dict) else None
    relative_path = raw_path.strip() if isinstance(raw_path, str) else ""
    if not relative_path:
        return "", "", False
    normalized = relative_path.replace("\\", "/")
    candidate = Path(relative_path)
    absolute = candidate if candidate.is_absolute() else paper_dir / candidate
    absolute = absolute.resolve()
    return normalized, str(absolute), absolute.is_file()


def build_manifest(
    paper_dir: Path, context_before: int, context_after: int
) -> dict[str, Any]:
    if context_before < 0 or context_after < 0:
        raise ManifestError("context counts must be non-negative")
    paper_dir = paper_dir.resolve()
    if not paper_dir.is_dir():
        raise ManifestError(f"paper folder does not exist: {paper_dir}")

    content_list = _find_content_list(paper_dir)
    reference = _paper_reference(paper_dir, content_list)
    pages = _load_pages(content_list)
    markdown = _find_markdown(paper_dir, content_list)
    charts: list[dict[str, Any]] = []

    for page_number, page in enumerate(pages, start=1):
        for item_index, block in enumerate(page):
            if block.get("type") != "chart":
                continue
            content = block.get("content")
            content = content if isinstance(content, dict) else {}
            image_path, image_absolute_path, image_exists = _image_paths(
                paper_dir, content
            )
            charts.append(
                {
                    "chart_id": f"page_{page_number:04d}_item_{item_index + 1:04d}",
                    "page_number": page_number,
                    "item_index": item_index + 1,
                    "bbox": _bbox(block),
                    "image_path": image_path,
                    "image_absolute_path": image_absolute_path,
                    "image_exists": image_exists,
                    "caption": flatten_text(content.get("chart_caption")),
                    "caption_segments": content.get("chart_caption", []),
                    "footnote": flatten_text(content.get("chart_footnote")),
                    "footnote_segments": content.get("chart_footnote", []),
                    "section_title": _nearest_section_title(
                        page, item_index, page_number
                    ),
                    "context_before": _nearby_paragraphs(
                        page, item_index, page_number, context_before, -1
                    ),
                    "context_after": _nearby_paragraphs(
                        page, item_index, page_number, context_after, 1
                    ),
                }
            )

    source_bytes = content_list.read_bytes()
    return {
        "schema_version": SCHEMA_VERSION,
        "paper_reference": reference,
        "paper_folder": str(paper_dir),
        "source_content_list": str(content_list.resolve()),
        "source_content_list_sha256": hashlib.sha256(source_bytes).hexdigest(),
        "source_markdown": str(markdown) if markdown else None,
        "context_policy": {
            "scope": "same_page",
            "eligible_block_type": "paragraph",
            "paragraphs_before": context_before,
            "paragraphs_after": context_after,
        },
        "summary": {
            "page_count": len(pages),
            "chart_count": len(charts),
            "charts_missing_caption": sum(not chart["caption"] for chart in charts),
            "charts_missing_image": sum(
                not chart["image_exists"] for chart in charts
            ),
        },
        "charts": charts,
    }


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paper_folder", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--context-before", type=int, default=2)
    parser.add_argument("--context-after", type=int, default=2)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        manifest = build_manifest(
            args.paper_folder, args.context_before, args.context_after
        )
        output = args.output
        if output is None:
            output = args.paper_folder / (
                f"paper_{manifest['paper_reference']}_charts.json"
            )
        output = output.resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    except (ManifestError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"Wrote {len(manifest['charts'])} charts to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
