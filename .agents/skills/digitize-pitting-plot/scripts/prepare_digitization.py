#!/usr/bin/env python3
"""Prepare a non-overwriting v2 digitization template for one staged plot pair."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


SCHEMA_PATH = Path(__file__).resolve().parents[1] / "references" / "digitization.schema.json"


class PreparationError(ValueError):
    """Raised when a staged image/metadata pair cannot seed a template."""


def _load_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PreparationError(f"cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise PreparationError(f"{path} must contain a JSON object")
    return value


def _load_schema() -> dict[str, Any]:
    return _load_object(SCHEMA_PATH)


def _schema_error(instance: dict[str, Any], schema: dict[str, Any]) -> str | None:
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(instance), key=lambda error: error.json_path)
    if not errors:
        return None
    return "; ".join(f"{error.json_path}: {error.message}" for error in errors[:5])


def prepare(metadata: dict[str, Any]) -> dict[str, Any]:
    result = {
        "schema_version": 2,
        "paper_reference": metadata.get("paper_reference"),
        "source_chart_manifest": metadata.get("source_chart_manifest"),
        "plot_metadata": metadata.get("plot_metadata"),
        "digitization_status": "unprocessed",
        "digitization_notes": ["Not yet digitized."],
        "plot_data": [],
    }
    error = _schema_error(result, _load_schema())
    if error:
        raise PreparationError(f"classifier metadata cannot seed v2 output: {error}")
    return result


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", required=True, type=Path)
    parser.add_argument("--metadata", type=Path)
    parser.add_argument("--output", type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        image = args.image.resolve()
        if not image.is_file():
            raise PreparationError(f"image does not exist: {image}")
        if image.suffix.lower() != ".jpg":
            raise PreparationError("image must use the .jpg extension")

        metadata_path = (
            args.metadata.resolve()
            if args.metadata is not None
            else image.with_suffix(".json")
        )
        if not metadata_path.is_file():
            raise PreparationError(f"metadata does not exist: {metadata_path}")
        if metadata_path.stem != image.stem:
            raise PreparationError("image and metadata must have the same basename")

        output = (
            args.output.resolve()
            if args.output is not None
            else (
                image.parent.parent
                / "digitized_pitting_potential_plots"
                / f"{image.stem}.json"
            ).resolve()
        )
        if output.suffix.lower() != ".json":
            raise PreparationError("output must use the .json extension")
        if output.exists():
            raise PreparationError(f"refusing to overwrite existing output: {output}")

        metadata = _load_object(metadata_path)
        result = prepare(metadata)
        expected_stem = (
            f"paper_{result['paper_reference']}_{result['plot_metadata']['chart_id']}"
        )
        if image.stem != expected_stem:
            raise PreparationError(
                f"image stem must be {expected_stem!r} for the supplied metadata"
            )

        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(result, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    except (PreparationError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"Prepared unprocessed v2 digitization template at {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

