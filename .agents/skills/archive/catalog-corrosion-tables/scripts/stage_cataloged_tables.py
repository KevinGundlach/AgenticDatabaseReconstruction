#!/usr/bin/env python3
"""Stage processable cataloged table images and self-contained metadata sidecars."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any


class StagingError(ValueError):
    """Raised when manifest and catalog inputs cannot be staged safely."""


def _load_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise StagingError(f"cannot read {label} {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise StagingError(f"{label} must be a JSON object")
    return value


def _indexed_tables(value: dict[str, Any], label: str) -> dict[str, dict[str, Any]]:
    tables = value.get("tables")
    if not isinstance(tables, list):
        raise StagingError(f"{label} tables must be an array")
    indexed: dict[str, dict[str, Any]] = {}
    for position, table in enumerate(tables):
        if not isinstance(table, dict):
            raise StagingError(f"{label} table {position} must be an object")
        table_id = table.get("table_id")
        if not isinstance(table_id, str) or not table_id:
            raise StagingError(f"{label} table {position} lacks table_id")
        if table_id in indexed:
            raise StagingError(f"duplicate {label} table_id: {table_id}")
        indexed[table_id] = table
    return indexed


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--catalog", required=True, type=Path)
    parser.add_argument("--output", type=Path, default=Path("corrosion_tables/images"))
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        manifest_path = args.manifest.resolve()
        catalog_path = args.catalog.resolve()
        manifest = _load_object(manifest_path, "manifest")
        catalog = _load_object(catalog_path, "catalog")
        if manifest.get("schema_version") != 1 or catalog.get("schema_version") != 1:
            raise StagingError("manifest and catalog must both use schema version 1")
        if manifest.get("paper_reference") != catalog.get("paper_reference"):
            raise StagingError("manifest and catalog paper references differ")
        if catalog.get("source_table_manifest") != manifest_path.name:
            raise StagingError("catalog source_table_manifest does not match manifest filename")

        manifest_tables = _indexed_tables(manifest, "manifest")
        catalog_tables = _indexed_tables(catalog, "catalog")
        if set(manifest_tables) != set(catalog_tables):
            raise StagingError("manifest and catalog table IDs differ")

        output_dir = args.output.resolve()
        paper_dir = Path(manifest.get("paper_folder", manifest_path.parent)).resolve()
        paper_reference = manifest["paper_reference"]
        jobs: list[tuple[Path, Path, Path, dict[str, Any]]] = []
        missing: list[str] = []
        for table_id, catalog_entry in catalog_tables.items():
            if catalog_entry.get("status") != "processable":
                continue
            source_entry = manifest_tables[table_id]
            image_path = source_entry.get("image_path")
            source_image = (
                paper_dir / image_path
                if isinstance(image_path, str) and image_path
                else Path()
            )
            if not source_image.is_file():
                missing.append(table_id)
                continue
            suffix = source_image.suffix.lower() or ".jpg"
            stem = f"paper_{paper_reference}_{table_id}"
            destination_image = output_dir / f"{stem}{suffix}"
            destination_sidecar = output_dir / f"{stem}.json"
            sidecar = {
                "schema_version": 1,
                "paper_reference": paper_reference,
                "source_table_manifest": manifest_path.name,
                "source_table_catalog": catalog_path.name,
                "source_table": source_entry,
                "catalog_entry": catalog_entry,
            }
            jobs.append(
                (source_image, destination_image, destination_sidecar, sidecar)
            )

        collisions = [
            str(path)
            for _, image, sidecar, _ in jobs
            for path in (image, sidecar)
            if path.exists()
        ]
        if collisions:
            raise StagingError(
                "refusing to overwrite existing staged files: " + ", ".join(collisions)
            )

        output_dir.mkdir(parents=True, exist_ok=True)
        for source_image, destination_image, destination_sidecar, sidecar in jobs:
            shutil.copyfile(source_image, destination_image)
            destination_sidecar.write_text(
                json.dumps(sidecar, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
    except (StagingError, OSError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"Staged {len(jobs)} processable tables in {output_dir}")
    if missing:
        print("Skipped processable tables with missing images: " + ", ".join(missing))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
