#!/usr/bin/env python3
"""Build a deterministic table manifest from MinerU content_list_v2 JSON."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
PAPER_DIR_RE = re.compile(r"^paper_(\d+)$", re.IGNORECASE)
FILE_REF_RE = re.compile(r"^(\d+)_")
SPACE_RE = re.compile(r"\s+")
TABLE_LABEL_RE = re.compile(
    r"\btable\s*([a-z]?\d+(?:[.\-]\d+)*(?:\s*[a-z])?|[ivxlcdm]+)\b",
    re.IGNORECASE,
)
TEXT_BLOCK_TYPES = {"paragraph", "list", "equation_interline"}


class ManifestError(ValueError):
    """Raised when the MinerU folder does not meet the input contract."""


def _normalize_text(text: str) -> str:
    return SPACE_RE.sub(" ", text).strip()


def _join_text(parts: list[str]) -> str:
    return _normalize_text(" ".join(part for part in parts if part.strip()))


def flatten_text(value: Any) -> str:
    """Flatten MinerU span structures without traversing unrelated metadata."""
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
        "math_content",
        "page_number_content",
        "table_caption",
        "table_footnote",
    ):
        if key in value:
            return flatten_text(value[key])
    if isinstance(content, (str, list, dict)):
        return flatten_text(content)
    return ""


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


def _block_record(
    block: dict[str, Any], page_number: int, item_index: int
) -> dict[str, Any] | None:
    text = flatten_text(block.get("content"))
    if not text:
        return None
    return {
        "block_id": f"page_{page_number:04d}_item_{item_index:04d}",
        "type": block.get("type", "unknown"),
        "page_number": page_number,
        "item_index": item_index,
        "bbox": _bbox(block),
        "text": text,
    }


def _normalized_reference(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.casefold())


def _table_reference_key(caption: str) -> str | None:
    match = TABLE_LABEL_RE.search(caption)
    if not match:
        return None
    return _normalized_reference(f"table{match.group(1)}")


def _table_reference_keys(text: str) -> set[str]:
    return {
        _normalized_reference(f"table{match.group(1)}")
        for match in TABLE_LABEL_RE.finditer(text)
    }


def _image_info(paper_dir: Path, content: dict[str, Any]) -> tuple[str, bool]:
    source = content.get("image_source")
    raw_path = source.get("path") if isinstance(source, dict) else None
    relative_path = raw_path.strip() if isinstance(raw_path, str) else ""
    normalized = relative_path.replace("\\", "/")
    if not normalized or normalized.endswith("/"):
        return normalized, False
    candidate = Path(relative_path)
    absolute = candidate if candidate.is_absolute() else paper_dir / candidate
    return normalized, absolute.resolve().is_file()


def build_manifest(
    paper_dir: Path, context_before: int, context_after: int, mention_limit: int
) -> dict[str, Any]:
    if min(context_before, context_after, mention_limit) < 0:
        raise ManifestError("context and mention counts must be non-negative")
    paper_dir = paper_dir.resolve()
    if not paper_dir.is_dir():
        raise ManifestError(f"paper folder does not exist: {paper_dir}")

    content_list = _find_content_list(paper_dir)
    reference = _paper_reference(paper_dir, content_list)
    pages = _load_pages(content_list)
    text_records: list[tuple[int, dict[str, Any]]] = []
    table_positions: list[
        tuple[int, int, int, dict[str, Any], list[dict[str, Any]]]
    ] = []
    heading_stack: list[dict[str, Any]] = []
    document_position = 0

    for page_number, page in enumerate(pages, start=1):
        for item_index, block in enumerate(page, start=1):
            position = document_position
            document_position += 1
            block_type = block.get("type")
            if block_type == "title":
                record = _block_record(block, page_number, item_index)
                content = block.get("content")
                level = content.get("level") if isinstance(content, dict) else None
                if record and isinstance(level, int) and level >= 1:
                    record["level"] = level
                    heading_stack = [
                        heading for heading in heading_stack if heading["level"] < level
                    ]
                    heading_stack.append(record)
            if block_type in TEXT_BLOCK_TYPES:
                record = _block_record(block, page_number, item_index)
                if record:
                    text_records.append((position, record))
            if block_type == "table":
                table_positions.append(
                    (
                        position,
                        page_number,
                        item_index,
                        block,
                        [dict(heading) for heading in heading_stack],
                    )
                )

    page_labels: dict[int, str] = {}
    for page_number, page in enumerate(pages, start=1):
        labels = [
            flatten_text(block.get("content"))
            for block in page
            if block.get("type") == "page_number"
        ]
        page_labels[page_number] = _join_text(labels)

    text_frequencies = Counter(
        _normalize_text(record["text"]).casefold() for _, record in text_records
    )
    context_records = [
        (position, record)
        for position, record in text_records
        if text_frequencies[_normalize_text(record["text"]).casefold()] < 2
    ]

    tables: list[dict[str, Any]] = []
    for position, page_number, item_index, block, section_path in table_positions:
        content = block.get("content")
        content = content if isinstance(content, dict) else {}
        caption_segments = content.get("table_caption", [])
        footnote_segments = content.get("table_footnote", [])
        caption = flatten_text(caption_segments)
        reference_key = _table_reference_key(caption)
        before = [record for pos, record in context_records if pos < position][
            -context_before:
        ]
        after = [record for pos, record in context_records if pos > position][
            :context_after
        ]
        mentions: list[dict[str, Any]] = []
        if reference_key:
            for _, record in text_records:
                if reference_key in _table_reference_keys(record["text"]):
                    mentions.append(record)
                    if len(mentions) >= mention_limit:
                        break
        image_path, image_exists = _image_info(paper_dir, content)
        html = content.get("html")
        tables.append(
            {
                "table_id": f"page_{page_number:04d}_item_{item_index:04d}",
                "page_number": page_number,
                "page_index": page_number - 1,
                "printed_page_label": page_labels.get(page_number, ""),
                "item_index": item_index,
                "bbox": _bbox(block),
                "image_path": image_path,
                "image_exists": image_exists,
                "caption": caption,
                "caption_segments": caption_segments
                if isinstance(caption_segments, list)
                else [],
                "footnote": flatten_text(footnote_segments),
                "footnote_segments": footnote_segments
                if isinstance(footnote_segments, list)
                else [],
                "mineru_html": html if isinstance(html, str) else "",
                "mineru_table_type": content.get("table_type"),
                "mineru_table_nest_level": content.get("table_nest_level"),
                "section_path": section_path,
                "context_before": before,
                "context_after": after,
                "reference_mentions": mentions,
            }
        )

    source_bytes = content_list.read_bytes()
    return {
        "schema_version": SCHEMA_VERSION,
        "paper_reference": reference,
        "paper_folder": str(paper_dir),
        "source_content_list_v2": str(content_list.resolve()),
        "source_content_list_v2_sha256": hashlib.sha256(source_bytes).hexdigest(),
        "context_policy": {
            "scope": "cross_page_document_order",
            "eligible_block_types": sorted(TEXT_BLOCK_TYPES),
            "exclude_exact_text_repeated_at_least": 2,
            "blocks_before": context_before,
            "blocks_after": context_after,
            "explicit_reference_limit": mention_limit,
        },
        "summary": {
            "page_count": len(pages),
            "table_count": len(tables),
            "tables_missing_caption": sum(not table["caption"] for table in tables),
            "tables_missing_image": sum(
                not table["image_exists"] for table in tables
            ),
            "tables_missing_html": sum(not table["mineru_html"] for table in tables),
        },
        "tables": tables,
    }


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paper_folder", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--context-before", type=int, default=3)
    parser.add_argument("--context-after", type=int, default=2)
    parser.add_argument("--reference-limit", type=int, default=5)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        manifest = build_manifest(
            args.paper_folder,
            args.context_before,
            args.context_after,
            args.reference_limit,
        )
        output = args.output
        if output is None:
            output = args.paper_folder / f"paper_{manifest['paper_reference']}_tables.json"
        output = output.resolve()
        if output.exists():
            raise ManifestError(f"refusing to overwrite existing output: {output}")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    except (ManifestError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"Wrote {len(manifest['tables'])} tables to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
