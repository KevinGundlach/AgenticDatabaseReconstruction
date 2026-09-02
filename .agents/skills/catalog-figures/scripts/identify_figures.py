#!/usr/bin/env python3
"""Create a provenance skeleton for every MinerU chart and table in one paper."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 2
PAPER_DIR_RE = re.compile(r"^paper_(\d+)$", re.IGNORECASE)
FILE_REF_RE = re.compile(r"^(\d+)_")
SPACE_RE = re.compile(r"\s+")
SPACE_BEFORE_PUNCTUATION_RE = re.compile(r"\s+([,.;:!?%)\]])")
SPACE_AFTER_OPEN_RE = re.compile(r"([(\[])\s+")


class CatalogSkeletonError(ValueError):
    """Raised when a MinerU paper folder violates the input contract."""


def _resolve_project_root(project_root: Path | None) -> Path:
    root = (project_root or Path.cwd()).resolve()
    if not root.is_dir():
        raise CatalogSkeletonError(f"project root does not exist: {root}")
    return root


def resolve_project_path(path: Path, project_root: Path) -> Path:
    """Resolve a path inside project_root and reject paths that escape it."""
    root = project_root.resolve()
    candidate = path if path.is_absolute() else root / path
    resolved = candidate.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise CatalogSkeletonError(
            f"path must be inside the project root {root}: {resolved}"
        ) from exc
    return resolved


def _project_relative(path: Path, project_root: Path) -> str:
    return path.resolve().relative_to(project_root.resolve()).as_posix()


def _normalize_text(text: str) -> str:
    text = SPACE_RE.sub(" ", text).strip()
    text = SPACE_BEFORE_PUNCTUATION_RE.sub(r"\1", text)
    return SPACE_AFTER_OPEN_RE.sub(r"\1", text)


def _join_text(parts: list[str]) -> str:
    return _normalize_text(" ".join(part for part in parts if part.strip()))


def flatten_text(value: Any) -> str:
    """Flatten MinerU text and equation fragments without walking metadata."""
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
        "chart_caption",
        "chart_footnote",
        "table_caption",
        "table_footnote",
    ):
        if key in value:
            return flatten_text(value[key])
    if isinstance(content, (str, list, dict)):
        return flatten_text(content)
    return ""


def _find_exactly_one(paper_dir: Path, pattern: str) -> Path:
    matches = sorted(paper_dir.glob(pattern))
    if len(matches) != 1:
        raise CatalogSkeletonError(
            f"expected exactly one {pattern} in {paper_dir}, found {len(matches)}"
        )
    return matches[0].resolve()


def _paper_reference(paper_dir: Path, content_list: Path) -> str:
    folder_match = PAPER_DIR_RE.fullmatch(paper_dir.name)
    file_match = FILE_REF_RE.match(content_list.name)
    folder_ref = folder_match.group(1) if folder_match else None
    file_ref = file_match.group(1) if file_match else None
    if folder_ref and file_ref and int(folder_ref) != int(file_ref):
        raise CatalogSkeletonError(
            f"paper reference mismatch: folder={folder_ref}, file={file_ref}"
        )
    reference = folder_ref or file_ref
    if reference is None:
        raise CatalogSkeletonError(
            "cannot determine paper reference; use paper_<number> or a numbered content-list file"
        )
    return str(int(reference))


def _load_pages(content_list: Path) -> list[list[dict[str, Any]]]:
    try:
        raw = json.loads(content_list.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise CatalogSkeletonError(f"cannot read {content_list}: {exc}") from exc

    if not isinstance(raw, list):
        raise CatalogSkeletonError("content_list_v2 root must be an array")
    if not raw:
        return []
    if all(isinstance(item, dict) for item in raw):
        raw = [raw]
    if not all(isinstance(page, list) for page in raw):
        raise CatalogSkeletonError("content_list_v2 must contain page arrays")

    pages: list[list[dict[str, Any]]] = []
    for page_number, page in enumerate(raw, start=1):
        if not all(isinstance(block, dict) for block in page):
            raise CatalogSkeletonError(
                f"page {page_number} contains a non-object block"
            )
        pages.append(page)
    return pages


def _image_path(content: dict[str, Any]) -> str | None:
    source = content.get("image_source")
    raw_path = source.get("path") if isinstance(source, dict) else None
    if not isinstance(raw_path, str) or not raw_path.strip():
        return None
    return raw_path.strip().replace("\\", "/")


def _figure_entry(
    block: dict[str, Any], page_number: int, item_index: int
) -> dict[str, Any]:
    figure_type = block.get("type")
    if figure_type not in {"chart", "table"}:
        raise CatalogSkeletonError("block is not a chart or table")
    content = block.get("content")
    content = content if isinstance(content, dict) else {}
    caption_key = "chart_caption" if figure_type == "chart" else "table_caption"
    source_figure_id = f"page_{page_number:04d}_item_{item_index:04d}"
    return {
        "catalog_id": source_figure_id,
        "source_figure_id": source_figure_id,
        "panel_label": None,
        "type": figure_type,
        "page_number": page_number,
        "item_index": item_index,
        "image_path": _image_path(content),
        "caption": flatten_text(content.get(caption_key)),
        "status": None,
        "variables": [],
        "notes": [],
    }


def build_catalog_skeleton(
    input_path: Path, project_root: Path | None = None
) -> dict[str, Any]:
    """Build the incomplete catalog that an agent will semantically fill."""
    root = _resolve_project_root(project_root)
    paper_dir = resolve_project_path(input_path, root)
    if not paper_dir.is_dir():
        raise CatalogSkeletonError(f"paper folder does not exist: {paper_dir}")

    content_list = _find_exactly_one(paper_dir, "*_content_list_v2.json")
    source_markdown = _find_exactly_one(paper_dir, "*.md")
    paper_reference = _paper_reference(paper_dir, content_list)
    markdown_match = FILE_REF_RE.match(source_markdown.name)
    if markdown_match and int(markdown_match.group(1)) != int(paper_reference):
        raise CatalogSkeletonError(
            "paper reference mismatch: "
            f"catalog={paper_reference}, source Markdown={markdown_match.group(1)}"
        )
    pages = _load_pages(content_list)

    figures: list[dict[str, Any]] = []
    for page_number, page in enumerate(pages, start=1):
        for zero_based_index, block in enumerate(page):
            if block.get("type") in {"chart", "table"}:
                figures.append(
                    _figure_entry(block, page_number, zero_based_index + 1)
                )

    return {
        "schema_version": SCHEMA_VERSION,
        "paper_reference": paper_reference,
        "input_path": _project_relative(paper_dir, root),
        "source_content_list": _project_relative(content_list, root),
        "source_markdown": _project_relative(source_markdown, root),
        "figures": figures,
    }


def find_figures(
    input_path: Path, project_root: Path | None = None
) -> list[dict[str, Any]]:
    """Return chart/table skeleton entries for compatibility with callers."""
    return build_catalog_skeleton(input_path, project_root)["figures"]


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input_path", type=Path, required=True)
    parser.add_argument("--output_file", type=Path)
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="base directory for serialized project-relative paths (default: cwd)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="replace an existing output file explicitly",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        project_root = _resolve_project_root(args.project_root)
        catalog = build_catalog_skeleton(args.input_path, project_root)
        output_file = args.output_file
        if output_file is None:
            output_file = project_root / Path(catalog["input_path"]) / (
                f"paper_{catalog['paper_reference']}_figures.json"
            )
        output_file = output_file.resolve()
        if output_file.exists() and not args.overwrite:
            raise CatalogSkeletonError(
                f"output already exists: {output_file}; preserve it or rerun with --overwrite"
            )
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(
            json.dumps(catalog, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    except (CatalogSkeletonError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(
        f"Wrote {len(catalog['figures'])} chart/table skeleton entries to "
        f"{output_file}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
