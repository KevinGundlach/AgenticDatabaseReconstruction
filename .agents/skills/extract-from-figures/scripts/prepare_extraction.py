#!/usr/bin/env python3
"""Create an extraction skeleton from one completed figure catalog."""

from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 2
PAPER_DIR_RE = re.compile(r"^paper_(\d+)$", re.IGNORECASE)


class ExtractionPreparationError(ValueError):
    """Raised when extraction preparation inputs violate the contract."""


def _resolve_project_root(project_root: Path | None) -> Path:
    root = (project_root or Path.cwd()).resolve()
    if not root.is_dir():
        raise ExtractionPreparationError(f"project root does not exist: {root}")
    return root


def resolve_project_path(path: Path, project_root: Path) -> Path:
    """Resolve a path inside project_root and reject paths that escape it."""
    root = project_root.resolve()
    candidate = path if path.is_absolute() else root / path
    resolved = candidate.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ExtractionPreparationError(
            f"path must be inside the project root {root}: {resolved}"
        ) from exc
    return resolved


def _project_relative(path: Path, project_root: Path) -> str:
    return path.resolve().relative_to(project_root.resolve()).as_posix()


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ExtractionPreparationError(f"cannot read {path}: {exc}") from exc


def _find_catalog(paper_dir: Path) -> Path:
    matches = sorted(paper_dir.glob("paper_*_figures.json"))
    if len(matches) != 1:
        raise ExtractionPreparationError(
            f"expected exactly one paper_*_figures.json in {paper_dir}, "
            f"found {len(matches)}"
        )
    return matches[0].resolve()


def _catalog_entries(catalog: Any) -> list[dict[str, Any]]:
    if not isinstance(catalog, dict):
        raise ExtractionPreparationError("catalog root must be an object")
    figures = catalog.get("figures")
    if not isinstance(figures, list):
        raise ExtractionPreparationError("catalog.figures must be an array")
    for index, figure in enumerate(figures):
        if not isinstance(figure, dict):
            raise ExtractionPreparationError(
                f"catalog.figures[{index}] must be an object"
            )
        if not isinstance(figure.get("catalog_id"), str):
            raise ExtractionPreparationError(
                f"catalog.figures[{index}].catalog_id must be a string"
            )
        if figure.get("status") not in {
            "cataloged",
            "needs_review",
            "not_data_figure",
        }:
            raise ExtractionPreparationError(
                f"catalog.figures[{index}] is not a completed catalog entry"
            )
        if not isinstance(figure.get("variables"), list):
            raise ExtractionPreparationError(
                f"catalog.figures[{index}].variables must be an array"
            )
    return figures


def build_extraction_skeleton(
    input_path: Path, project_root: Path | None = None
) -> dict[str, Any]:
    """Build one extraction entry for every figure in a completed catalog."""
    root = _resolve_project_root(project_root)
    paper_dir = resolve_project_path(input_path, root)
    if not paper_dir.is_dir():
        raise ExtractionPreparationError(f"paper folder does not exist: {paper_dir}")

    folder_match = PAPER_DIR_RE.fullmatch(paper_dir.name)
    if folder_match is None:
        raise ExtractionPreparationError(
            f"paper folder must be named paper_<reference>: {paper_dir.name}"
        )

    catalog_path = _find_catalog(paper_dir)
    catalog = _load_json(catalog_path)
    entries = _catalog_entries(catalog)
    paper_reference = str(catalog.get("paper_reference", ""))
    if paper_reference != str(int(folder_match.group(1))):
        raise ExtractionPreparationError(
            "paper reference differs between the folder and catalog"
        )

    extractions: list[dict[str, Any]] = []
    for figure in entries:
        catalog_status = figure["status"]
        if catalog_status == "needs_review":
            status = "needs_review"
            notes = ["Resolve the catalog entry before extracting values."]
        elif catalog_status == "not_data_figure":
            status = "not_data_figure"
            notes = []
        else:
            status = "unprocessed"
            notes = []
        layout = [
            {"variable_index": index, "component": "value"}
            for index, _variable in enumerate(figure["variables"])
        ]
        extractions.append(
            {
                "catalog_id": figure["catalog_id"],
                "status": status,
                "variables": copy.deepcopy(figure["variables"]),
                "layout": layout,
                "rows": [],
                "notes": notes,
            }
        )

    return {
        "schema_version": SCHEMA_VERSION,
        "source_catalog": _project_relative(catalog_path, root),
        "extractions": extractions,
    }


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
        root = _resolve_project_root(args.project_root)
        skeleton = build_extraction_skeleton(args.input_path, root)
        source_catalog = root / Path(skeleton["source_catalog"])
        paper_reference = _load_json(source_catalog)["paper_reference"]
        output_file = args.output_file
        if output_file is None:
            output_file = source_catalog.parent / (
                f"paper_{paper_reference}_figure_extractions.json"
            )
        output_file = output_file.resolve()
        if output_file.exists() and not args.overwrite:
            raise ExtractionPreparationError(
                f"output already exists: {output_file}; preserve it or rerun with --overwrite"
            )
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(
            json.dumps(skeleton, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    except (ExtractionPreparationError, OSError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(
        f"Wrote {len(skeleton['extractions'])} extraction skeleton entries to "
        f"{output_file}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
