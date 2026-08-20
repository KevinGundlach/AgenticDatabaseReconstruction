#!/usr/bin/env python3
"""Validate one digitized pitting plot against its staged image and metadata."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sys
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
TOP_FIELDS = {"schema_version", "source", "digitization"}
SOURCE_FIELDS = {
    "paper_reference",
    "source_chart_manifest",
    "image",
    "metadata",
    "plot_metadata",
}
FILE_REFERENCE_FIELDS = {"path", "sha256"}
DIGITIZATION_FIELDS = {
    "status",
    "reason_code",
    "reason",
    "confidence",
    "issues",
    "panels",
}
ISSUE_FIELDS = {"code", "message", "target_series_refs"}
PANEL_FIELDS = {"panel_id", "label_raw", "notes", "axes", "series", "omitted_series"}
AXIS_FIELDS = {
    "axis_id",
    "dimension",
    "side",
    "label_raw",
    "unit_raw",
    "scale",
    "value_type",
    "target_metric",
    "breaks",
}
SERIES_FIELDS = {
    "series_id",
    "target_series_refs",
    "labels_raw",
    "tags",
    "x_axis_id",
    "y_axis_id",
    "visual_encoding",
    "observations",
}
TAG_FIELDS = {"key", "value_raw", "evidence_source"}
VISUAL_ENCODING_FIELDS = {"color_raw", "marker_raw", "line_raw", "fill_raw"}
OBSERVATION_FIELDS = {
    "observation_id",
    "mark_type",
    "values",
    "label_raw",
    "confidence",
    "notes",
}
VALUE_FIELDS = {"axis_id", "value", "interval"}
INTERVAL_FIELDS = {"lower", "upper", "kind", "meaning_raw"}
OMITTED_SERIES_FIELDS = {"label_raw", "reason_code", "notes"}

STATUS_REASON_CODES = {
    "complete": {"digitized_discrete_marks"},
    "partial": {"partially_digitized"},
    "needs_review": {
        "ambiguous_axis",
        "ambiguous_series_mapping",
        "ambiguous_mark_semantics",
        "insufficient_resolution",
    },
    "skipped": {
        "markerless_trace",
        "unsupported_geometry",
        "no_discrete_target_marks",
    },
}
ISSUE_CODES = {
    "ambiguous_axis",
    "ambiguous_series_mapping",
    "ambiguous_mark_semantics",
    "insufficient_resolution",
    "occluded_marks",
    "unresolved_target_series",
    "unsupported_geometry",
}
DIMENSIONS = {"x", "y"}
SIDES = {"bottom", "top", "left", "right", "unknown"}
SCALES = {"linear", "log", "categorical", "unknown"}
VALUE_TYPES = {"numeric", "categorical", "mixed", "unknown"}
EVIDENCE_SOURCES = {
    "legend",
    "plot_annotation",
    "caption",
    "axis",
    "classifier_metadata",
}
MARK_TYPES = {"marker", "bar", "range", "other_discrete"}
INTERVAL_KINDS = {"error_bar", "reported_range", "other"}
OMISSION_CODES = {
    "non_pitting_metric",
    "fitted_or_connecting_line",
    "other_out_of_scope",
}
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


class ValidationError(ValueError):
    """Raised when a digitization violates the output contract."""


def _load_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValidationError(f"cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValidationError(f"{path} must contain a JSON object")
    return value


def _require_exact_fields(value: Any, fields: set[str], location: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValidationError(f"{location} must be an object")
    actual = set(value)
    if actual != fields:
        raise ValidationError(
            f"{location} fields mismatch; missing={sorted(fields - actual)}, "
            f"extra={sorted(actual - fields)}"
        )
    return value


def _require_string(value: Any, field: str, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str) or (not allow_empty and not value.strip()):
        qualifier = "a string" if allow_empty else "a non-empty string"
        raise ValidationError(f"{field} must be {qualifier}")
    return value


def _require_string_list(
    value: Any, field: str, *, nonempty: bool = False, unique: bool = True
) -> list[str]:
    if (
        not isinstance(value, list)
        or (nonempty and not value)
        or not all(isinstance(item, str) and item.strip() for item in value)
    ):
        qualifier = "a non-empty array" if nonempty else "an array"
        raise ValidationError(f"{field} must be {qualifier} of non-empty strings")
    if unique and len(value) != len(set(value)):
        raise ValidationError(f"{field} must not contain duplicates")
    return value


def _require_array(value: Any, field: str) -> list[Any]:
    if not isinstance(value, list):
        raise ValidationError(f"{field} must be an array")
    return value


def _require_confidence(value: Any, field: str) -> float | int:
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        or not 0 <= value <= 1
    ):
        raise ValidationError(f"{field} must be between 0 and 1")
    return value


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
    except OSError as exc:
        raise ValidationError(f"cannot hash {path}: {exc}") from exc
    return digest.hexdigest()


def _portable_relative_path(path: Path, output_parent: Path) -> str:
    return Path(os.path.relpath(path, output_parent)).as_posix()


def _validate_file_reference(
    value: Any, location: str, path: Path, output_parent: Path
) -> None:
    ref = _require_exact_fields(value, FILE_REFERENCE_FIELDS, location)
    expected_path = _portable_relative_path(path, output_parent)
    actual_path = _require_string(ref["path"], f"{location}.path")
    if actual_path != expected_path:
        raise ValidationError(
            f"{location}.path must be the portable relative path {expected_path!r}"
        )
    digest = _require_string(ref["sha256"], f"{location}.sha256")
    if not SHA256_PATTERN.fullmatch(digest):
        raise ValidationError(f"{location}.sha256 must be lowercase SHA-256 hex")
    expected_digest = _sha256(path)
    if digest != expected_digest:
        raise ValidationError(f"{location}.sha256 does not match {path}")


def _validate_source(
    value: Any,
    metadata: dict[str, Any],
    image: Path,
    metadata_path: Path,
    output_path: Path,
) -> list[str]:
    source = _require_exact_fields(value, SOURCE_FIELDS, "source")
    if source["paper_reference"] != metadata.get("paper_reference"):
        raise ValidationError("source.paper_reference differs from metadata")
    if source["source_chart_manifest"] != metadata.get("source_chart_manifest"):
        raise ValidationError("source.source_chart_manifest differs from metadata")
    _require_string(source["paper_reference"], "source.paper_reference")
    _require_string(source["source_chart_manifest"], "source.source_chart_manifest")
    _validate_file_reference(source["image"], "source.image", image, output_path.parent)
    _validate_file_reference(
        source["metadata"], "source.metadata", metadata_path, output_path.parent
    )
    if source["plot_metadata"] != metadata.get("plot_metadata"):
        raise ValidationError("source.plot_metadata differs from metadata.plot_metadata")
    plot = source["plot_metadata"]
    targets = _validate_plot_metadata(plot)
    expected_stem = f"paper_{source['paper_reference']}_{plot['chart_id']}"
    if image.stem != expected_stem:
        raise ValidationError(
            f"image stem must be {expected_stem!r} for source.plot_metadata"
        )
    return targets


def _validate_classifier_axis(value: Any, location: str) -> None:
    if not isinstance(value, dict):
        raise ValidationError(f"{location} must be an object")
    _require_string(value.get("label"), f"{location}.label", allow_empty=True)
    _require_string(value.get("unit"), f"{location}.unit", allow_empty=True)
    scale = _require_string(value.get("scale"), f"{location}.scale")
    if scale not in SCALES:
        raise ValidationError(f"{location}.scale is not allowed")


def _validate_plot_metadata(value: Any) -> list[str]:
    location = "source.plot_metadata"
    if not isinstance(value, dict):
        raise ValidationError(f"{location} must be an object")
    _require_string(value.get("chart_id"), f"{location}.chart_id")
    _require_string(value.get("image_path"), f"{location}.image_path", allow_empty=True)
    _require_string(value.get("caption"), f"{location}.caption", allow_empty=True)
    if value.get("reason_code") != "direct_pitting_potential_plot":
        raise ValidationError(
            f"{location}.reason_code must be direct_pitting_potential_plot"
        )
    _require_string(value.get("reason"), f"{location}.reason")
    _require_confidence(value.get("confidence"), f"{location}.confidence")
    _require_string_list(value.get("relevant_panels"), f"{location}.relevant_panels")
    targets = _require_string_list(
        value.get("target_series"), f"{location}.target_series", nonempty=True
    )
    _validate_classifier_axis(value.get("x_axis"), f"{location}.x_axis")
    _validate_classifier_axis(value.get("y_axis"), f"{location}.y_axis")
    return targets


def _validate_issue(
    value: Any, location: str, known_targets: set[str]
) -> set[str]:
    issue = _require_exact_fields(value, ISSUE_FIELDS, location)
    code = _require_string(issue["code"], f"{location}.code")
    if code not in ISSUE_CODES:
        raise ValidationError(f"{location}.code is not allowed")
    _require_string(issue["message"], f"{location}.message")
    refs = set(
        _require_string_list(
            issue["target_series_refs"],
            f"{location}.target_series_refs",
            nonempty=True,
        )
    )
    unknown = refs - known_targets
    if unknown:
        raise ValidationError(f"{location} references unknown targets: {sorted(unknown)}")
    return refs


def _validate_axis(value: Any, location: str) -> tuple[str, str, str, bool]:
    axis = _require_exact_fields(value, AXIS_FIELDS, location)
    axis_id = _require_string(axis["axis_id"], f"{location}.axis_id")
    dimension = _require_string(axis["dimension"], f"{location}.dimension")
    if dimension not in DIMENSIONS:
        raise ValidationError(f"{location}.dimension must be x or y")
    side = _require_string(axis["side"], f"{location}.side")
    if side not in SIDES:
        raise ValidationError(f"{location}.side is not allowed")
    _require_string(axis["label_raw"], f"{location}.label_raw", allow_empty=True)
    _require_string(axis["unit_raw"], f"{location}.unit_raw", allow_empty=True)
    scale = _require_string(axis["scale"], f"{location}.scale")
    if scale not in SCALES:
        raise ValidationError(f"{location}.scale is not allowed")
    value_type = _require_string(axis["value_type"], f"{location}.value_type")
    if value_type not in VALUE_TYPES:
        raise ValidationError(f"{location}.value_type is not allowed")
    if not isinstance(axis["target_metric"], bool):
        raise ValidationError(f"{location}.target_metric must be boolean")
    _require_string_list(axis["breaks"], f"{location}.breaks")
    return axis_id, dimension, value_type, axis["target_metric"]


def _validate_tag(value: Any, location: str) -> None:
    tag = _require_exact_fields(value, TAG_FIELDS, location)
    _require_string(tag["key"], f"{location}.key")
    _require_string(tag["value_raw"], f"{location}.value_raw")
    evidence = _require_string(tag["evidence_source"], f"{location}.evidence_source")
    if evidence not in EVIDENCE_SOURCES:
        raise ValidationError(f"{location}.evidence_source is not allowed")


def _validate_interval(value: Any, location: str) -> tuple[float, float]:
    interval = _require_exact_fields(value, INTERVAL_FIELDS, location)
    lower = interval["lower"]
    upper = interval["upper"]
    if (
        isinstance(lower, bool)
        or not isinstance(lower, (int, float))
        or not math.isfinite(lower)
        or isinstance(upper, bool)
        or not isinstance(upper, (int, float))
        or not math.isfinite(upper)
    ):
        raise ValidationError(f"{location}.lower and upper must be numeric")
    if lower > upper:
        raise ValidationError(f"{location}.lower must not exceed upper")
    kind = _require_string(interval["kind"], f"{location}.kind")
    if kind not in INTERVAL_KINDS:
        raise ValidationError(f"{location}.kind is not allowed")
    _require_string(interval["meaning_raw"], f"{location}.meaning_raw", allow_empty=True)
    return lower, upper


def _validate_coordinate_value(
    value: Any, location: str, axis_value_type: str
) -> tuple[str, bool]:
    coordinate = _require_exact_fields(value, VALUE_FIELDS, location)
    axis_id = _require_string(coordinate["axis_id"], f"{location}.axis_id")
    raw_value = coordinate["value"]
    if (
        isinstance(raw_value, bool)
        or not isinstance(raw_value, (int, float, str, type(None)))
        or (isinstance(raw_value, (int, float)) and not math.isfinite(raw_value))
    ):
        raise ValidationError(f"{location}.value must be a number, string, or null")
    if isinstance(raw_value, str) and not raw_value.strip():
        raise ValidationError(f"{location}.value string must not be empty")
    if axis_value_type == "numeric" and raw_value is not None and not isinstance(raw_value, (int, float)):
        raise ValidationError(f"{location}.value must be numeric for a numeric axis")
    if axis_value_type == "categorical" and not isinstance(raw_value, str):
        raise ValidationError(f"{location}.value must be a string for a categorical axis")

    interval_value = coordinate["interval"]
    has_interval = interval_value is not None
    if interval_value is not None:
        if axis_value_type == "categorical":
            raise ValidationError(f"{location}.interval is invalid for a categorical axis")
        lower, upper = _validate_interval(interval_value, f"{location}.interval")
        if isinstance(raw_value, (int, float)) and not lower <= raw_value <= upper:
            raise ValidationError(f"{location}.value must fall within its interval")
    if raw_value is None and interval_value is None:
        raise ValidationError(f"{location} must contain a value or interval")
    return axis_id, has_interval


def _validate_observation(
    value: Any,
    location: str,
    expected_axes: set[str],
    axis_value_types: dict[str, str],
) -> tuple[str, bool]:
    observation = _require_exact_fields(value, OBSERVATION_FIELDS, location)
    observation_id = _require_string(
        observation["observation_id"], f"{location}.observation_id"
    )
    mark_type = _require_string(observation["mark_type"], f"{location}.mark_type")
    if mark_type not in MARK_TYPES:
        raise ValidationError(f"{location}.mark_type is not allowed")
    values = _require_array(observation["values"], f"{location}.values")
    seen_axes: set[str] = set()
    has_interval = False
    for position, coordinate in enumerate(values):
        coordinate_location = f"{location}.values[{position}]"
        if not isinstance(coordinate, dict):
            raise ValidationError(f"{coordinate_location} must be an object")
        axis_id_hint = coordinate.get("axis_id")
        axis_value_type = axis_value_types.get(axis_id_hint, "unknown")
        axis_id, coordinate_has_interval = _validate_coordinate_value(
            coordinate, coordinate_location, axis_value_type
        )
        if axis_id in seen_axes:
            raise ValidationError(f"{location} repeats axis_id {axis_id!r}")
        seen_axes.add(axis_id)
        has_interval = has_interval or coordinate_has_interval
    if seen_axes != expected_axes:
        raise ValidationError(
            f"{location} axis coverage mismatch; expected={sorted(expected_axes)}, "
            f"actual={sorted(seen_axes)}"
        )
    if mark_type == "range" and not has_interval:
        raise ValidationError(f"{location} range mark must contain an interval")
    _require_string(observation["label_raw"], f"{location}.label_raw", allow_empty=True)
    _require_confidence(observation["confidence"], f"{location}.confidence")
    _require_string(observation["notes"], f"{location}.notes", allow_empty=True)
    return observation_id, has_interval


def _validate_series(
    value: Any,
    location: str,
    axes: dict[str, tuple[str, str, bool]],
    known_targets: set[str],
    seen_series_ids: set[str],
    seen_observation_ids: set[str],
) -> tuple[set[str], int]:
    series = _require_exact_fields(value, SERIES_FIELDS, location)
    series_id = _require_string(series["series_id"], f"{location}.series_id")
    if series_id in seen_series_ids:
        raise ValidationError(f"duplicate series_id: {series_id}")
    seen_series_ids.add(series_id)

    refs = set(
        _require_string_list(
            series["target_series_refs"],
            f"{location}.target_series_refs",
            nonempty=True,
        )
    )
    unknown = refs - known_targets
    if unknown:
        raise ValidationError(f"{location} references unknown targets: {sorted(unknown)}")
    _require_string_list(series["labels_raw"], f"{location}.labels_raw")
    for position, tag in enumerate(_require_array(series["tags"], f"{location}.tags")):
        _validate_tag(tag, f"{location}.tags[{position}]")

    x_axis_id = _require_string(series["x_axis_id"], f"{location}.x_axis_id")
    y_axis_id = _require_string(series["y_axis_id"], f"{location}.y_axis_id")
    if x_axis_id not in axes or axes[x_axis_id][0] != "x":
        raise ValidationError(f"{location}.x_axis_id must reference a panel x-axis")
    if y_axis_id not in axes or axes[y_axis_id][0] != "y":
        raise ValidationError(f"{location}.y_axis_id must reference a panel y-axis")
    if not (axes[x_axis_id][2] or axes[y_axis_id][2]):
        raise ValidationError(f"{location} must bind to a target_metric axis")

    encoding = _require_exact_fields(
        series["visual_encoding"], VISUAL_ENCODING_FIELDS, f"{location}.visual_encoding"
    )
    for field in sorted(VISUAL_ENCODING_FIELDS):
        _require_string(
            encoding[field], f"{location}.visual_encoding.{field}", allow_empty=True
        )

    observations = _require_array(series["observations"], f"{location}.observations")
    if not observations:
        raise ValidationError(f"{location}.observations must not be empty")
    axis_value_types = {
        x_axis_id: axes[x_axis_id][1],
        y_axis_id: axes[y_axis_id][1],
    }
    for position, observation in enumerate(observations):
        observation_id, _ = _validate_observation(
            observation,
            f"{location}.observations[{position}]",
            {x_axis_id, y_axis_id},
            axis_value_types,
        )
        if observation_id in seen_observation_ids:
            raise ValidationError(f"duplicate observation_id: {observation_id}")
        seen_observation_ids.add(observation_id)
    return refs, len(observations)


def _validate_omitted_series(value: Any, location: str) -> None:
    omitted = _require_exact_fields(value, OMITTED_SERIES_FIELDS, location)
    _require_string(omitted["label_raw"], f"{location}.label_raw")
    reason_code = _require_string(omitted["reason_code"], f"{location}.reason_code")
    if reason_code not in OMISSION_CODES:
        raise ValidationError(f"{location}.reason_code is not allowed")
    _require_string(omitted["notes"], f"{location}.notes", allow_empty=True)


def _validate_panel(
    value: Any,
    location: str,
    known_targets: set[str],
    seen_panel_ids: set[str],
    seen_series_ids: set[str],
    seen_observation_ids: set[str],
) -> tuple[set[str], int]:
    panel = _require_exact_fields(value, PANEL_FIELDS, location)
    panel_id = _require_string(panel["panel_id"], f"{location}.panel_id")
    if panel_id in seen_panel_ids:
        raise ValidationError(f"duplicate panel_id: {panel_id}")
    seen_panel_ids.add(panel_id)
    _require_string(panel["label_raw"], f"{location}.label_raw", allow_empty=True)
    _require_string(panel["notes"], f"{location}.notes", allow_empty=True)

    axes: dict[str, tuple[str, str, bool]] = {}
    for position, axis in enumerate(_require_array(panel["axes"], f"{location}.axes")):
        axis_id, dimension, value_type, target_metric = _validate_axis(
            axis, f"{location}.axes[{position}]"
        )
        if axis_id in axes:
            raise ValidationError(f"{location} repeats axis_id {axis_id!r}")
        axes[axis_id] = (dimension, value_type, target_metric)

    covered: set[str] = set()
    observation_count = 0
    for position, series in enumerate(
        _require_array(panel["series"], f"{location}.series")
    ):
        series_refs, count = _validate_series(
            series,
            f"{location}.series[{position}]",
            axes,
            known_targets,
            seen_series_ids,
            seen_observation_ids,
        )
        covered.update(series_refs)
        observation_count += count

    for position, omitted in enumerate(
        _require_array(panel["omitted_series"], f"{location}.omitted_series")
    ):
        _validate_omitted_series(omitted, f"{location}.omitted_series[{position}]")
    return covered, observation_count


def validate(
    result: dict[str, Any],
    metadata: dict[str, Any],
    image: Path,
    metadata_path: Path,
    output_path: Path,
) -> tuple[str, int, int, int]:
    _require_exact_fields(result, TOP_FIELDS, "root")
    if result["schema_version"] != SCHEMA_VERSION:
        raise ValidationError(f"schema_version must be {SCHEMA_VERSION}")
    targets = _validate_source(
        result["source"], metadata, image, metadata_path, output_path
    )
    known_targets = set(targets)

    digitization = _require_exact_fields(
        result["digitization"], DIGITIZATION_FIELDS, "digitization"
    )
    status = _require_string(digitization["status"], "digitization.status")
    if status not in STATUS_REASON_CODES:
        raise ValidationError("digitization.status is not allowed")
    reason_code = _require_string(
        digitization["reason_code"], "digitization.reason_code"
    )
    if reason_code not in STATUS_REASON_CODES[status]:
        raise ValidationError(
            f"digitization.reason_code {reason_code!r} is invalid for status {status!r}"
        )
    _require_string(digitization["reason"], "digitization.reason")
    _require_confidence(digitization["confidence"], "digitization.confidence")

    issues = _require_array(digitization["issues"], "digitization.issues")
    issue_targets: set[str] = set()
    for position, issue in enumerate(issues):
        issue_targets.update(
            _validate_issue(issue, f"digitization.issues[{position}]", known_targets)
        )

    seen_panel_ids: set[str] = set()
    seen_series_ids: set[str] = set()
    seen_observation_ids: set[str] = set()
    covered_targets: set[str] = set()
    observation_count = 0
    panels = _require_array(digitization["panels"], "digitization.panels")
    for position, panel in enumerate(panels):
        panel_targets, count = _validate_panel(
            panel,
            f"digitization.panels[{position}]",
            known_targets,
            seen_panel_ids,
            seen_series_ids,
            seen_observation_ids,
        )
        covered_targets.update(panel_targets)
        observation_count += count

    accounted_targets = covered_targets | issue_targets
    if accounted_targets != known_targets:
        raise ValidationError(
            "classifier target coverage mismatch; "
            f"missing={sorted(known_targets - accounted_targets)}, "
            f"extra={sorted(accounted_targets - known_targets)}"
        )
    if status == "complete":
        if issues:
            raise ValidationError("complete digitization must not contain issues")
        if covered_targets != known_targets or observation_count == 0:
            raise ValidationError(
                "complete digitization must observe every classifier target"
            )
    elif status == "partial":
        if not issues or observation_count == 0:
            raise ValidationError(
                "partial digitization must contain observations and issues"
            )
    else:
        if not issues:
            raise ValidationError(f"{status} digitization must contain an issue")
        if observation_count != 0:
            raise ValidationError(f"{status} digitization must not contain observations")

    return status, len(seen_series_ids), observation_count, len(issues)


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
        if metadata_path.stem != image.stem:
            raise ValidationError("image and metadata must have the same basename")

        metadata = _load_object(metadata_path)
        result = _load_object(output_path)
        status, series_count, observation_count, issue_count = validate(
            result, metadata, image, metadata_path, output_path
        )
    except ValidationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(
        f"Validated {status} digitization: {series_count} pitting series, "
        f"{observation_count} observations, {issue_count} issues"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
