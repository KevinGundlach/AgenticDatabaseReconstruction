#!/usr/bin/env python3
"""Upgrade a schema-v1 extraction by copying variables from its catalog."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any

from prepare_extraction import resolve_project_path


class ExtractionUpgradeError(ValueError):
    """Raised when an existing extraction cannot be upgraded safely."""


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ExtractionUpgradeError(f"cannot read {path}: {exc}") from exc


def upgrade(extraction_path: Path, project_root: Path) -> dict[str, Any]:
    """Return a v2 artifact without changing statuses, layouts, rows, or notes."""
    extraction = _load_json(extraction_path)
    if not isinstance(extraction, dict) or extraction.get("schema_version") not in {1, 2}:
        raise ExtractionUpgradeError("input must be a schema-version 1 or 2 extraction")

    stored_catalog = extraction.get("source_catalog")
    if not isinstance(stored_catalog, str) or (
        PurePosixPath(stored_catalog).is_absolute()
        or PureWindowsPath(stored_catalog).is_absolute()
        or "\\" in stored_catalog
        or ".." in PurePosixPath(stored_catalog).parts
    ):
        raise ExtractionUpgradeError("source_catalog must be a project-relative POSIX path")

    catalog_path = resolve_project_path(Path(stored_catalog), project_root)
    catalog = _load_json(catalog_path)
    figures = catalog.get("figures") if isinstance(catalog, dict) else None
    entries = extraction.get("extractions")
    if not isinstance(figures, list) or not isinstance(entries, list):
        raise ExtractionUpgradeError("catalog and extraction must contain entry arrays")
    if len(figures) != len(entries):
        raise ExtractionUpgradeError("catalog coverage differs from the extraction")

    upgraded = copy.deepcopy(extraction)
    for index, (figure, entry) in enumerate(zip(figures, upgraded["extractions"], strict=True)):
        if not isinstance(figure, dict) or not isinstance(entry, dict):
            raise ExtractionUpgradeError(f"entry {index} is not an object")
        if entry.get("catalog_id") != figure.get("catalog_id"):
            raise ExtractionUpgradeError(f"catalog_id mismatch at entry {index}")
        catalog_variables = figure.get("variables")
        if not isinstance(catalog_variables, list):
            raise ExtractionUpgradeError(f"catalog variables missing at entry {index}")
        existing_variables = entry.get("variables")
        if existing_variables is not None and existing_variables != catalog_variables:
            raise ExtractionUpgradeError(
                f"existing variables differ from the catalog at entry {index}"
            )
        entry["variables"] = copy.deepcopy(catalog_variables)

    upgraded["schema_version"] = 2
    return upgraded


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="replace the output explicitly, including an in-place upgrade",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        root = args.project_root.resolve()
        upgraded = upgrade(args.input.resolve(), root)
        output = args.output.resolve()
        if output.exists() and not args.overwrite:
            raise ExtractionUpgradeError(
                f"output already exists: {output}; rerun with --overwrite"
            )
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(upgraded, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    except (ExtractionUpgradeError, OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"Upgraded {len(upgraded['extractions'])} extraction entries in {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
