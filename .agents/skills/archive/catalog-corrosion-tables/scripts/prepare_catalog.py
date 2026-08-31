#!/usr/bin/env python3
"""Prepare a non-overwriting catalog template from a table manifest."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


class PreparationError(ValueError):
    """Raised when a manifest cannot seed a catalog template."""


def _load_manifest(path: Path) -> dict[str, Any]:
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PreparationError(f"cannot read {path}: {exc}") from exc
    if not isinstance(manifest, dict) or manifest.get("schema_version") != 1:
        raise PreparationError("manifest must be a schema-version-1 JSON object")
    if not isinstance(manifest.get("paper_reference"), str):
        raise PreparationError("manifest paper_reference must be a string")
    if not isinstance(manifest.get("tables"), list):
        raise PreparationError("manifest tables must be an array")
    return manifest


def prepare(manifest: dict[str, Any], manifest_name: str) -> dict[str, Any]:
    tables: list[dict[str, Any]] = []
    seen: set[str] = set()
    for position, table in enumerate(manifest["tables"]):
        if not isinstance(table, dict):
            raise PreparationError(f"manifest table {position} must be an object")
        table_id = table.get("table_id")
        if not isinstance(table_id, str) or not table_id:
            raise PreparationError(f"manifest table {position} lacks table_id")
        if table_id in seen:
            raise PreparationError(f"duplicate table_id: {table_id}")
        seen.add(table_id)
        tables.append(
            {
                "table_id": table_id,
                "page_number": table.get("page_number"),
                "item_index": table.get("item_index"),
                "bbox": table.get("bbox"),
                "image_path": table.get("image_path", ""),
                "caption": table.get("caption", ""),
                "status": "unclassified",
                "table_roles": [],
                "reason": "Not yet cataloged.",
                "confidence": 0,
                "relevant_context_block_ids": [],
                "citrine_field_mappings": [],
            }
        )
    return {
        "schema_version": 1,
        "paper_reference": manifest["paper_reference"],
        "source_table_manifest": manifest_name,
        "summary": {
            "table_count": len(tables),
            "processable": 0,
            "needs_review": 0,
            "non_table": 0,
            "unclassified": len(tables),
        },
        "tables": tables,
    }


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        manifest_path = args.manifest.resolve()
        manifest = _load_manifest(manifest_path)
        output = args.output
        if output is None:
            output = manifest_path.parent / (
                f"paper_{manifest['paper_reference']}_cataloged_tables.json"
            )
        output = output.resolve()
        if output.exists():
            raise PreparationError(f"refusing to overwrite existing output: {output}")
        output.parent.mkdir(parents=True, exist_ok=True)
        result = prepare(manifest, manifest_path.name)
        output.write_text(
            json.dumps(result, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    except (PreparationError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"Prepared {len(result['tables'])} unclassified tables at {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
