#!/usr/bin/env python3
"""Validate one v2 digitized pitting plot and its stable source identifiers."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


SCHEMA_PATH = Path(__file__).resolve().parents[1] / "references" / "digitization.schema.json"


class ValidationError(ValueError):
    """Raised when a digitization violates the v2 output contract."""


def _load_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValidationError(f"cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValidationError(f"{path} must contain a JSON object")
    return value


def _validate_schema(result: dict[str, Any]) -> None:
    schema = _load_object(SCHEMA_PATH)
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(result), key=lambda error: error.json_path)
    if errors:
        details = "; ".join(
            f"{error.json_path}: {error.message}" for error in errors[:5]
        )
        raise ValidationError(f"JSON Schema validation failed: {details}")


def _validate_identifiers(
    result: dict[str, Any], metadata: dict[str, Any], image: Path, metadata_path: Path
) -> None:
    if metadata_path.stem != image.stem:
        raise ValidationError("image and metadata must have the same basename")
    if result["paper_reference"] != metadata.get("paper_reference"):
        raise ValidationError("paper_reference differs from paired metadata")
    if result["source_chart_manifest"] != metadata.get("source_chart_manifest"):
        raise ValidationError("source_chart_manifest differs from paired metadata")
    metadata_plot = metadata.get("plot_metadata")
    if not isinstance(metadata_plot, dict):
        raise ValidationError("paired metadata.plot_metadata must be an object")
    if result["plot_metadata"]["chart_id"] != metadata_plot.get("chart_id"):
        raise ValidationError("plot_metadata.chart_id differs from paired metadata")
    expected_stem = (
        f"paper_{result['paper_reference']}_{result['plot_metadata']['chart_id']}"
    )
    if image.stem != expected_stem:
        raise ValidationError(
            f"image stem must be {expected_stem!r} for the output identifiers"
        )


def _is_number(value: Any) -> bool:
    return (
        not isinstance(value, bool)
        and isinstance(value, (int, float))
        and math.isfinite(value)
    )


def _validate_coordinate_type(value: Any, axis_type: str, location: str) -> None:
    if value is None:
        return
    if axis_type == "numeric" and not _is_number(value):
        raise ValidationError(f"{location} must be numeric for a numeric axis")
    if axis_type == "categorical" and not isinstance(value, str):
        raise ValidationError(f"{location} must be a string for a categorical axis")
    if axis_type == "mixed" and not (_is_number(value) or isinstance(value, str)):
        raise ValidationError(f"{location} must be numeric or a string for a mixed axis")


def _validate_interval(point: dict[str, Any], coordinate: str, location: str) -> None:
    lower_key = f"{coordinate}_lower"
    upper_key = f"{coordinate}_upper"
    if lower_key not in point:
        return
    lower = point[lower_key]
    upper = point[upper_key]
    if not (_is_number(lower) and _is_number(upper)):
        raise ValidationError(f"{location} interval bounds must be finite numbers")
    if lower > upper:
        raise ValidationError(f"{location}.{lower_key} must not exceed {upper_key}")
    central = point[coordinate]
    if central is not None:
        if not _is_number(central):
            raise ValidationError(
                f"{location}.{coordinate} must be numeric when interval bounds exist"
            )
        if not lower <= central <= upper:
            raise ValidationError(
                f"{location}.{coordinate} must fall within its interval"
            )


def _validate_series_semantics(result: dict[str, Any]) -> tuple[int, int]:
    seen_series_ids: set[str] = set()
    point_count = 0
    for series_position, series in enumerate(result["plot_data"]):
        location = f"plot_data[{series_position}]"
        series_id = series["series_id"]
        if series_id in seen_series_ids:
            raise ValidationError(f"duplicate series_id: {series_id}")
        seen_series_ids.add(series_id)
        if series["x_axis"]["is_target"] == series["y_axis"]["is_target"]:
            raise ValidationError(
                f"{location} must have exactly one axis with is_target true"
            )
        for point_position, point in enumerate(series["data_points"]):
            point_location = f"{location}.data_points[{point_position}]"
            _validate_coordinate_type(
                point["x"], series["x_axis"]["type"], f"{point_location}.x"
            )
            _validate_coordinate_type(
                point["y"], series["y_axis"]["type"], f"{point_location}.y"
            )
            _validate_interval(point, "x", point_location)
            _validate_interval(point, "y", point_location)
            point_count += 1
    return len(seen_series_ids), point_count


def validate(
    result: dict[str, Any], metadata: dict[str, Any], image: Path, metadata_path: Path
) -> tuple[str, int, int]:
    _validate_schema(result)
    if result["digitization_status"] == "unprocessed":
        raise ValidationError("digitization_status must be finalized before validation")
    _validate_identifiers(result, metadata, image, metadata_path)
    series_count, point_count = _validate_series_semantics(result)
    return result["digitization_status"], series_count, point_count


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", required=True, type=Path)
    parser.add_argument("--metadata", type=Path)
    parser.add_argument("--input", required=True, type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        image = args.image.resolve()
        metadata_path = (
            args.metadata.resolve()
            if args.metadata is not None
            else image.with_suffix(".json")
        )
        output_path = args.input.resolve()
        if not image.is_file():
            raise ValidationError(f"image does not exist: {image}")
        if not metadata_path.is_file():
            raise ValidationError(f"metadata does not exist: {metadata_path}")
        if not output_path.is_file():
            raise ValidationError(f"digitization does not exist: {output_path}")
        if image.suffix.lower() != ".jpg":
            raise ValidationError("image must use the .jpg extension")

        metadata = _load_object(metadata_path)
        result = _load_object(output_path)
        status, series_count, point_count = validate(
            result, metadata, image, metadata_path
        )
    except ValidationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(
        f"Validated {status} digitization: {series_count} pitting series, "
        f"{point_count} data points"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
