"""Validate raw agent output and generate normalized observation artifacts."""

from __future__ import annotations

import csv
import json
from math import isfinite
from pathlib import Path
from typing import Any, Iterable

from .chemistry import (
    BINARY_ATOMIC_TO_WEIGHT_CONVERSION_ID,
    POTENTIAL_CONVERSION_ID,
    ConversionError,
    binary_atomic_percent_to_weight_percent,
    potential_to_mv_sce,
)
from .overlay import render_overlay


RAW_FORBIDDEN_KEY_FRAGMENTS = ("normalized", "weight_percent", "wt_percent", "conversion_id")
ATOMIC_PERCENT_UNITS = {"at.%", "at%", "atomic%", "atomicpercent", "atomicpercentage"}
WEIGHT_PERCENT_UNITS = {"wt.%", "wt%", "weight%", "weightpercent"}
METRICS = {
    "pitting_potential",
    "repassivation_potential",
    "corrosion_potential",
    "current_density",
    "other",
}
ROOT_KEYS = {
    "schema_version",
    "paper_id",
    "figure_id",
    "source_image",
    "caption",
    "x_axis",
    "y_axis",
    "composition_context",
    "calibration",
    "series",
    "notes",
}
AXIS_KEYS = {"label", "unit", "reference", "reference_vs_she_mv", "scale"}
SERIES_KEYS = {"series_id", "label", "metric", "sample_condition", "marker_type", "points"}
POINT_KEYS = {
    "x",
    "y",
    "pixel_x",
    "pixel_y",
    "uncertainty_x",
    "uncertainty_y",
    "confidence",
    "notes",
}

CSV_FIELDS = [
    "paper_id",
    "figure_id",
    "caption",
    "series_id",
    "series_label",
    "metric",
    "sample_condition",
    "x_value_raw",
    "x_unit_raw",
    "x_value_normalized",
    "x_unit_normalized",
    "composition_wt_percent_json",
    "y_value_raw",
    "y_unit_raw",
    "y_reference_raw",
    "y_value_normalized",
    "y_unit_normalized",
    "pixel_x",
    "pixel_y",
    "estimated_uncertainty_x",
    "estimated_uncertainty_y",
    "marker_type",
    "confidence",
    "value_origin",
    "x_conversion_id",
    "y_conversion_id",
    "source_image",
]


class RawDigitizationError(ValueError):
    """Raised when model-facing raw digitization violates its contract."""


def _walk_keys(value: Any, path: str = "$") -> Iterable[tuple[str, str]]:
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            yield key, child_path
            yield from _walk_keys(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk_keys(child, f"{path}[{index}]")


def _number(value: Any, name: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise RawDigitizationError(f"{name} must be numeric") from exc
    if not isfinite(result):
        raise RawDigitizationError(f"{name} must be finite")
    return result


def _unit_key(unit: str) -> str:
    return unit.strip().lower().replace(" ", "")


def _reject_unknown_keys(value: dict[str, Any], allowed: set[str], path: str) -> None:
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise RawDigitizationError(
            f"Unknown fields at {path}: {', '.join(unknown)}"
        )


def validate_raw_spec(spec: dict[str, Any]) -> None:
    if spec.get("schema_version") != 1:
        raise RawDigitizationError("schema_version must be 1")

    for key, path in _walk_keys(spec):
        lowered = key.lower()
        if any(fragment in lowered for fragment in RAW_FORBIDDEN_KEY_FRAGMENTS):
            raise RawDigitizationError(
                f"Raw model output contains forbidden normalized field at {path}"
            )

    required = ("paper_id", "figure_id", "source_image", "caption", "x_axis", "y_axis", "series")
    missing = [key for key in required if key not in spec]
    if missing:
        raise RawDigitizationError(f"Missing required fields: {', '.join(missing)}")
    if not isinstance(spec["series"], list) or not spec["series"]:
        raise RawDigitizationError("series must be a non-empty list")
    _reject_unknown_keys(spec, ROOT_KEYS, "$")

    composition_context = spec.get("composition_context")
    if composition_context is not None:
        if not isinstance(composition_context, dict):
            raise RawDigitizationError("composition_context must be an object")
        _reject_unknown_keys(
            composition_context, {"base_element", "solute_element"}, "$.composition_context"
        )
        if not all(composition_context.get(key) for key in ("base_element", "solute_element")):
            raise RawDigitizationError(
                "composition_context requires base_element and solute_element"
            )

    calibration = spec.get("calibration")
    if calibration is not None:
        if not isinstance(calibration, dict):
            raise RawDigitizationError("calibration must be an object")
        _reject_unknown_keys(calibration, {"plot_box", "x", "y"}, "$.calibration")
        plot_box = calibration.get("plot_box")
        if plot_box is not None:
            if not isinstance(plot_box, list) or len(plot_box) != 4:
                raise RawDigitizationError("calibration.plot_box must contain four numbers")
            for index, value in enumerate(plot_box):
                _number(value, f"calibration.plot_box[{index}]")
        for calibration_axis in ("x", "y"):
            calibration_points = calibration.get(calibration_axis)
            if calibration_points is None:
                continue
            if not isinstance(calibration_points, list) or len(calibration_points) != 2:
                raise RawDigitizationError(
                    f"calibration.{calibration_axis} must contain exactly two points"
                )
            for index, point in enumerate(calibration_points):
                if not isinstance(point, dict):
                    raise RawDigitizationError(
                        f"calibration.{calibration_axis}[{index}] must be an object"
                    )
                _reject_unknown_keys(
                    point, {"pixel", "value"}, f"$.calibration.{calibration_axis}[{index}]"
                )
                _number(point.get("pixel"), f"calibration.{calibration_axis}[{index}].pixel")
                _number(point.get("value"), f"calibration.{calibration_axis}[{index}].value")

    for axis_name in ("x_axis", "y_axis"):
        axis = spec[axis_name]
        if not isinstance(axis, dict):
            raise RawDigitizationError(f"{axis_name} must be an object")
        _reject_unknown_keys(axis, AXIS_KEYS, f"$.{axis_name}")
        if not all(axis.get(key) for key in ("label", "unit", "scale")):
            raise RawDigitizationError(f"{axis_name} requires label, unit, and scale")
        if axis["scale"] not in {"linear", "log10", "ln"}:
            raise RawDigitizationError(f"Unsupported {axis_name} scale: {axis['scale']}")

    for series_index, series in enumerate(spec["series"]):
        if not isinstance(series, dict):
            raise RawDigitizationError(f"series[{series_index}] must be an object")
        _reject_unknown_keys(series, SERIES_KEYS, f"$.series[{series_index}]")
        for key in ("series_id", "label", "metric", "points"):
            if key not in series:
                raise RawDigitizationError(f"series[{series_index}].{key} is required")
        if not isinstance(series["points"], list):
            raise RawDigitizationError(f"series[{series_index}].points must be a list")
        if series["metric"] not in METRICS:
            raise RawDigitizationError(
                f"Unsupported metric in series[{series_index}]: {series['metric']}"
            )
        for point_index, point in enumerate(series["points"]):
            if not isinstance(point, dict):
                raise RawDigitizationError(
                    f"series[{series_index}].points[{point_index}] must be an object"
                )
            _reject_unknown_keys(
                point, POINT_KEYS, f"$.series[{series_index}].points[{point_index}]"
            )
            _number(point.get("x"), f"series[{series_index}].points[{point_index}].x")
            _number(point.get("y"), f"series[{series_index}].points[{point_index}].y")
            for optional_number in ("pixel_x", "pixel_y", "uncertainty_x", "uncertainty_y"):
                if optional_number in point:
                    numeric = _number(
                        point[optional_number],
                        f"series[{series_index}].points[{point_index}].{optional_number}",
                    )
                    if optional_number.startswith("uncertainty") and numeric < 0:
                        raise RawDigitizationError("Point uncertainty cannot be negative")
            confidence = _number(
                point.get("confidence", 0.5),
                f"series[{series_index}].points[{point_index}].confidence",
            )
            if not 0 <= confidence <= 1:
                raise RawDigitizationError("Point confidence must be between 0 and 1")


def _resolve_source_image(spec: dict[str, Any], input_path: Path) -> None:
    source = Path(spec["source_image"])
    if not source.is_absolute():
        source = (input_path.parent / source).resolve()
    if not source.is_file():
        raise RawDigitizationError(f"Source image does not exist: {source}")
    spec["source_image"] = str(source)


def _normalize_x(
    raw_x: float, unit: str, composition_context: dict[str, Any] | None
) -> tuple[str, str, str, str]:
    unit_key = _unit_key(unit)
    if unit_key in ATOMIC_PERCENT_UNITS:
        if not composition_context:
            raise RawDigitizationError(
                "Atomic-percent axes require composition_context with base_element and solute_element"
            )
        try:
            composition = binary_atomic_percent_to_weight_percent(
                composition_context["base_element"],
                composition_context["solute_element"],
                raw_x,
            )
        except (KeyError, ConversionError) as exc:
            raise RawDigitizationError(f"Cannot normalize atomic composition: {exc}") from exc
        solute = composition_context["solute_element"].strip().capitalize()
        return (
            f"{composition[solute]:.10g}",
            "wt.%",
            json.dumps(composition, sort_keys=True, separators=(",", ":")),
            BINARY_ATOMIC_TO_WEIGHT_CONVERSION_ID,
        )
    if unit_key in WEIGHT_PERCENT_UNITS:
        return f"{raw_x:.10g}", "wt.%", "", "identity:weight_percent:v1"
    return "", "", "", ""


def _normalize_y(raw_y: float, axis: dict[str, Any]) -> tuple[str, str, str]:
    reference = axis.get("reference")
    if not reference:
        return "", "", ""
    try:
        normalized = potential_to_mv_sce(
            raw_y,
            unit=axis["unit"],
            reference=reference,
            reference_vs_she_mv=axis.get("reference_vs_she_mv"),
        )
    except ConversionError as exc:
        raise RawDigitizationError(f"Cannot normalize potential axis: {exc}") from exc
    return f"{normalized:.10g}", "mV vs. SCE", POTENTIAL_CONVERSION_ID


def finalize_spec(
    input_path: Path,
    output_dir: Path,
    include_metrics: set[str] | None = None,
) -> dict[str, Any]:
    include_metrics = include_metrics or {"pitting_potential"}
    spec = json.loads(input_path.read_text(encoding="utf-8"))
    if not isinstance(spec, dict):
        raise RawDigitizationError("Root value must be an object")
    validate_raw_spec(spec)
    _resolve_source_image(spec, input_path)

    output_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, str]] = []
    excluded_series: list[dict[str, str]] = []
    x_axis = spec["x_axis"]
    y_axis = spec["y_axis"]
    composition_context = spec.get("composition_context")

    for series in spec["series"]:
        if series["metric"] not in include_metrics:
            excluded_series.append(
                {
                    "series_id": str(series["series_id"]),
                    "metric": str(series["metric"]),
                    "reason": "metric excluded by phase-one policy",
                }
            )
            continue
        for point in series["points"]:
            raw_x = _number(point["x"], "point.x")
            raw_y = _number(point["y"], "point.y")
            normalized_x, normalized_x_unit, composition_json, x_conversion = _normalize_x(
                raw_x, x_axis["unit"], composition_context
            )
            normalized_y, normalized_y_unit, y_conversion = _normalize_y(raw_y, y_axis)
            rows.append(
                {
                    "paper_id": str(spec["paper_id"]),
                    "figure_id": str(spec["figure_id"]),
                    "caption": str(spec["caption"]),
                    "series_id": str(series["series_id"]),
                    "series_label": str(series["label"]),
                    "metric": str(series["metric"]),
                    "sample_condition": str(series.get("sample_condition", "")),
                    "x_value_raw": f"{raw_x:.10g}",
                    "x_unit_raw": str(x_axis["unit"]),
                    "x_value_normalized": normalized_x,
                    "x_unit_normalized": normalized_x_unit,
                    "composition_wt_percent_json": composition_json,
                    "y_value_raw": f"{raw_y:.10g}",
                    "y_unit_raw": str(y_axis["unit"]),
                    "y_reference_raw": str(y_axis.get("reference", "")),
                    "y_value_normalized": normalized_y,
                    "y_unit_normalized": normalized_y_unit,
                    "pixel_x": str(point.get("pixel_x", "")),
                    "pixel_y": str(point.get("pixel_y", "")),
                    "estimated_uncertainty_x": str(point.get("uncertainty_x", "")),
                    "estimated_uncertainty_y": str(point.get("uncertainty_y", "")),
                    "marker_type": str(series.get("marker_type", "")),
                    "confidence": str(point.get("confidence", "")),
                    "value_origin": "digitized_from_figure",
                    "x_conversion_id": x_conversion,
                    "y_conversion_id": y_conversion,
                    "source_image": str(spec["source_image"]),
                }
            )

    csv_path = output_dir / "points.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    overlay_warnings = render_overlay(spec, output_dir / "digitization_overlay.png")
    metadata = {
        "schema_version": 1,
        "paper_id": str(spec["paper_id"]),
        "figure_id": str(spec["figure_id"]),
        "source_image": str(spec["source_image"]),
        "caption": str(spec["caption"]),
        "raw_digitization": str(input_path.resolve()),
        "included_metrics": sorted(include_metrics),
        "point_count": len(rows),
        "excluded_series": excluded_series,
    }
    (output_dir / "figure_metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )
    validation = {
        "valid": True,
        "errors": [],
        "warnings": overlay_warnings,
        "point_count": len(rows),
        "excluded_series_count": len(excluded_series),
    }
    (output_dir / "validation.json").write_text(
        json.dumps(validation, indent=2), encoding="utf-8"
    )
    return metadata
