#!/usr/bin/env python3
"""Validate a pitting-plot classification against its chart manifest."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


MANIFEST_SCHEMA_VERSION = 1
CLASSIFICATION_SCHEMA_VERSION = 2
BUCKETS = ("simple_plots", "rejected_charts", "needs_review")
BASE_ENTRY_FIELDS = {
    "chart_id",
    "image_path",
    "caption",
    "reason_code",
    "reason",
    "confidence",
    "relevant_panels",
    "target_series",
}
AXIS_FIELDS = {"x_axis", "y_axis"}
AXIS_OBJECT_FIELDS = {"label", "unit", "scale"}
AXIS_SCALES = {"linear", "log", "categorical", "unknown"}
REASON_CODES = {
    "simple_plots": {"direct_pitting_potential_plot"},
    "rejected_charts": {
        "polarization_curve",
        "current_density_only",
        "other_electrochemical_metric",
        "not_pitting_potential",
        "not_digitizable",
        "non_plot_chart",
        "unreadable",
        "other",
    },
    "needs_review": {
        "insufficient_evidence",
        "missing_image",
        "ambiguous_metric",
        "ambiguous_chart_type",
    },
}


class ValidationError(ValueError):
    """Raised when a classification violates the output contract."""


def _load_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValidationError(f"cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValidationError(f"{path} must contain a JSON object")
    return value


def _require_string(value: Any, field: str, allow_empty: bool = False) -> str:
    if not isinstance(value, str) or (not allow_empty and not value.strip()):
        qualifier = "a string" if allow_empty else "a non-empty string"
        raise ValidationError(f"{field} must be {qualifier}")
    return value


def _require_string_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not all(
        isinstance(item, str) and item.strip() for item in value
    ):
        raise ValidationError(f"{field} must be an array of non-empty strings")
    return value


def _validate_axis(value: Any, field: str) -> None:
    if not isinstance(value, dict):
        raise ValidationError(f"{field} must be an object")
    fields = set(value)
    if fields != AXIS_OBJECT_FIELDS:
        missing = sorted(AXIS_OBJECT_FIELDS - fields)
        extra = sorted(fields - AXIS_OBJECT_FIELDS)
        raise ValidationError(
            f"{field} fields mismatch; missing={missing}, extra={extra}"
        )
    _require_string(value["label"], f"{field}.label")
    _require_string(value["unit"], f"{field}.unit", allow_empty=True)
    scale = _require_string(value["scale"], f"{field}.scale")
    if scale not in AXIS_SCALES:
        allowed = ", ".join(sorted(AXIS_SCALES))
        raise ValidationError(f"{field}.scale must be one of: {allowed}")


def _validate_entry(
    entry: Any,
    bucket: str,
    position: int,
    manifest_charts: dict[str, dict[str, Any]],
) -> str:
    location = f"{bucket}[{position}]"
    if not isinstance(entry, dict):
        raise ValidationError(f"{location} must be an object")
    expected_fields = BASE_ENTRY_FIELDS | (
        AXIS_FIELDS if bucket == "simple_plots" else set()
    )
    fields = set(entry)
    if fields != expected_fields:
        missing = sorted(expected_fields - fields)
        extra = sorted(fields - expected_fields)
        raise ValidationError(
            f"{location} fields mismatch; missing={missing}, extra={extra}"
        )

    chart_id = _require_string(entry["chart_id"], f"{location}.chart_id")
    source = manifest_charts.get(chart_id)
    if source is None:
        raise ValidationError(f"{location}.chart_id is absent from the manifest")
    image_path = _require_string(
        entry["image_path"], f"{location}.image_path", allow_empty=True
    )
    caption = _require_string(
        entry["caption"], f"{location}.caption", allow_empty=True
    )
    if image_path != source.get("image_path"):
        raise ValidationError(f"{location}.image_path differs from the manifest")
    if caption != source.get("caption"):
        raise ValidationError(f"{location}.caption differs from the manifest")

    reason_code = _require_string(
        entry["reason_code"], f"{location}.reason_code"
    )
    if reason_code not in REASON_CODES[bucket]:
        allowed = ", ".join(sorted(REASON_CODES[bucket]))
        raise ValidationError(
            f"{location}.reason_code must be one of: {allowed}"
        )
    _require_string(entry["reason"], f"{location}.reason")
    confidence = entry["confidence"]
    if (
        isinstance(confidence, bool)
        or not isinstance(confidence, (int, float))
        or not 0 <= confidence <= 1
    ):
        raise ValidationError(f"{location}.confidence must be between 0 and 1")
    _require_string_list(entry["relevant_panels"], f"{location}.relevant_panels")
    target_series = _require_string_list(
        entry["target_series"], f"{location}.target_series"
    )
    if bucket == "simple_plots" and not target_series:
        raise ValidationError(
            f"{location}.target_series must identify at least one pitting-potential series"
        )
    if bucket == "simple_plots":
        _validate_axis(entry["x_axis"], f"{location}.x_axis")
        _validate_axis(entry["y_axis"], f"{location}.y_axis")
    return chart_id


def validate(manifest: dict[str, Any], result: dict[str, Any], manifest_name: str) -> None:
    if manifest.get("schema_version") != MANIFEST_SCHEMA_VERSION:
        raise ValidationError("unsupported manifest schema_version")
    if result.get("schema_version") != CLASSIFICATION_SCHEMA_VERSION:
        raise ValidationError("classification schema_version must be 2")
    reference = manifest.get("paper_reference")
    if result.get("paper_reference") != reference:
        raise ValidationError("paper_reference differs from the manifest")
    if result.get("source_chart_manifest") != manifest_name:
        raise ValidationError(
            f"source_chart_manifest must be the manifest filename {manifest_name!r}"
        )

    raw_charts = manifest.get("charts")
    if not isinstance(raw_charts, list):
        raise ValidationError("manifest.charts must be an array")
    manifest_charts: dict[str, dict[str, Any]] = {}
    for position, chart in enumerate(raw_charts):
        if not isinstance(chart, dict) or not isinstance(chart.get("chart_id"), str):
            raise ValidationError(f"manifest.charts[{position}] lacks a valid chart_id")
        chart_id = chart["chart_id"]
        if chart_id in manifest_charts:
            raise ValidationError(f"duplicate manifest chart_id: {chart_id}")
        manifest_charts[chart_id] = chart

    seen: set[str] = set()
    bucket_counts: dict[str, int] = {}
    for bucket in BUCKETS:
        entries = result.get(bucket)
        if not isinstance(entries, list):
            raise ValidationError(f"{bucket} must be an array")
        bucket_counts[bucket] = len(entries)
        for position, entry in enumerate(entries):
            chart_id = _validate_entry(entry, bucket, position, manifest_charts)
            if chart_id in seen:
                raise ValidationError(f"chart_id classified more than once: {chart_id}")
            seen.add(chart_id)

    expected = set(manifest_charts)
    missing = sorted(expected - seen)
    extra = sorted(seen - expected)
    if missing or extra:
        raise ValidationError(
            f"classification coverage mismatch; missing={missing}, extra={extra}"
        )

    expected_summary = {
        "chart_count": len(expected),
        "accepted": bucket_counts["simple_plots"],
        "rejected": bucket_counts["rejected_charts"],
        "needs_review": bucket_counts["needs_review"],
    }
    if result.get("summary") != expected_summary:
        raise ValidationError(f"summary must equal {expected_summary}")


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--input", required=True, type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        manifest = _load_object(args.manifest)
        result = _load_object(args.input)
        validate(manifest, result, args.manifest.name)
    except ValidationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(
        "Validated "
        f"{result['summary']['chart_count']} charts: "
        f"{result['summary']['accepted']} accepted, "
        f"{result['summary']['rejected']} rejected, "
        f"{result['summary']['needs_review']} needing review"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
