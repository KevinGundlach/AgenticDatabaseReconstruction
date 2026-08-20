#!/usr/bin/env python3
"""Prepare a non-overwriting digitization template for one staged plot pair."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any


class PreparationError(ValueError):
    """Raised when a staged image/metadata pair cannot seed a template."""


AXIS_SCALES = {"linear", "log", "categorical", "unknown"}


def _load_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PreparationError(f"cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise PreparationError(f"{path} must contain a JSON object")
    return value


def _require_string(value: Any, field: str, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str) or (not allow_empty and not value.strip()):
        qualifier = "a string" if allow_empty else "a non-empty string"
        raise PreparationError(f"{field} must be {qualifier}")
    return value


def _require_string_list(value: Any, field: str, *, nonempty: bool = False) -> list[str]:
    if (
        not isinstance(value, list)
        or (nonempty and not value)
        or not all(isinstance(item, str) and item.strip() for item in value)
    ):
        qualifier = "a non-empty array" if nonempty else "an array"
        raise PreparationError(f"{field} must be {qualifier} of non-empty strings")
    if len(value) != len(set(value)):
        raise PreparationError(f"{field} must not contain duplicates")
    return value


def _validate_classifier_axis(value: Any, field: str) -> None:
    if not isinstance(value, dict):
        raise PreparationError(f"{field} must be an object")
    _require_string(value.get("label"), f"{field}.label", allow_empty=True)
    _require_string(value.get("unit"), f"{field}.unit", allow_empty=True)
    scale = _require_string(value.get("scale"), f"{field}.scale")
    if scale not in AXIS_SCALES:
        raise PreparationError(
            f"{field}.scale must be one of: {', '.join(sorted(AXIS_SCALES))}"
        )


def validate_metadata(metadata: dict[str, Any], image: Path, metadata_path: Path) -> None:
    paper_reference = _require_string(
        metadata.get("paper_reference"), "metadata.paper_reference"
    )
    _require_string(
        metadata.get("source_chart_manifest"), "metadata.source_chart_manifest"
    )
    if "plot_data" in metadata and not isinstance(metadata["plot_data"], list):
        raise PreparationError("metadata.plot_data must be an array when present")

    plot = metadata.get("plot_metadata")
    if not isinstance(plot, dict):
        raise PreparationError("metadata.plot_metadata must be an object")
    chart_id = _require_string(plot.get("chart_id"), "plot_metadata.chart_id")
    _require_string(
        plot.get("image_path"), "plot_metadata.image_path", allow_empty=True
    )
    _require_string(plot.get("caption"), "plot_metadata.caption", allow_empty=True)
    if plot.get("reason_code") != "direct_pitting_potential_plot":
        raise PreparationError(
            "plot_metadata.reason_code must be direct_pitting_potential_plot"
        )
    _require_string(plot.get("reason"), "plot_metadata.reason")
    confidence = plot.get("confidence")
    if (
        isinstance(confidence, bool)
        or not isinstance(confidence, (int, float))
        or not 0 <= confidence <= 1
    ):
        raise PreparationError("plot_metadata.confidence must be between 0 and 1")
    _require_string_list(plot.get("relevant_panels"), "plot_metadata.relevant_panels")
    _require_string_list(
        plot.get("target_series"), "plot_metadata.target_series", nonempty=True
    )
    _validate_classifier_axis(plot.get("x_axis"), "plot_metadata.x_axis")
    _validate_classifier_axis(plot.get("y_axis"), "plot_metadata.y_axis")

    expected_stem = f"paper_{paper_reference}_{chart_id}"
    if image.stem != expected_stem:
        raise PreparationError(
            f"image stem must be {expected_stem!r} for the supplied metadata"
        )
    if metadata_path.stem != image.stem:
        raise PreparationError("image and metadata must have the same basename")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
    except OSError as exc:
        raise PreparationError(f"cannot hash {path}: {exc}") from exc
    return digest.hexdigest()


def _portable_relative_path(path: Path, output_parent: Path) -> str:
    return Path(os.path.relpath(path, output_parent)).as_posix()


def prepare(
    metadata: dict[str, Any], image: Path, metadata_path: Path, output: Path
) -> dict[str, Any]:
    target_series = metadata["plot_metadata"]["target_series"]
    return {
        "schema_version": 1,
        "source": {
            "paper_reference": metadata["paper_reference"],
            "source_chart_manifest": metadata["source_chart_manifest"],
            "image": {
                "path": _portable_relative_path(image, output.parent),
                "sha256": _sha256(image),
            },
            "metadata": {
                "path": _portable_relative_path(metadata_path, output.parent),
                "sha256": _sha256(metadata_path),
            },
            "plot_metadata": metadata["plot_metadata"],
        },
        "digitization": {
            "status": "needs_review",
            "reason_code": "unprocessed",
            "reason": "Not yet digitized.",
            "confidence": 0,
            "issues": [
                {
                    "code": "unresolved_target_series",
                    "message": "Target series have not yet been digitized.",
                    "target_series_refs": target_series,
                }
            ],
            "panels": [],
        },
    }


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
        validate_metadata(metadata, image, metadata_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        result = prepare(metadata, image, metadata_path, output)
        output.write_text(
            json.dumps(result, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    except (PreparationError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"Prepared unprocessed digitization template at {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

