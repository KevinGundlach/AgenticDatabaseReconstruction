#!/usr/bin/env python3
"""Prepare a non-overwriting classification template from a chart manifest."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


class PreparationError(ValueError):
    """Raised when the manifest cannot seed a classification template."""


def _load_manifest(path: Path) -> dict[str, Any]:
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PreparationError(f"cannot read {path}: {exc}") from exc
    if not isinstance(manifest, dict) or manifest.get("schema_version") != 1:
        raise PreparationError("manifest must be a schema-version-1 JSON object")
    if not isinstance(manifest.get("paper_reference"), str):
        raise PreparationError("manifest paper_reference must be a string")
    if not isinstance(manifest.get("charts"), list):
        raise PreparationError("manifest charts must be an array")
    return manifest


def prepare(manifest: dict[str, Any], manifest_name: str) -> dict[str, Any]:
    charts: list[dict[str, Any]] = []
    seen: set[str] = set()
    for position, chart in enumerate(manifest["charts"]):
        if not isinstance(chart, dict):
            raise PreparationError(f"manifest chart {position} must be an object")
        chart_id = chart.get("chart_id")
        image_path = chart.get("image_path")
        caption = chart.get("caption")
        if not isinstance(chart_id, str) or not chart_id:
            raise PreparationError(f"manifest chart {position} lacks chart_id")
        if chart_id in seen:
            raise PreparationError(f"duplicate chart_id: {chart_id}")
        if not isinstance(image_path, str) or not isinstance(caption, str):
            raise PreparationError(
                f"manifest chart {chart_id} must have string image_path and caption"
            )
        seen.add(chart_id)
        charts.append(
            {
                "chart_id": chart_id,
                "image_path": image_path,
                "caption": caption,
                "reason_code": "unclassified",
                "reason": "Not yet classified.",
                "confidence": 0,
                "relevant_panels": [],
                "target_series": [],
            }
        )

    return {
        "schema_version": 2,
        "paper_reference": manifest["paper_reference"],
        "source_chart_manifest": manifest_name,
        "summary": {
            "chart_count": len(charts),
            "accepted": 0,
            "rejected": 0,
            "needs_review": len(charts),
        },
        "simple_plots": [],
        "rejected_charts": [],
        "needs_review": charts,
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
                f"paper_{manifest['paper_reference']}_simple_plots.json"
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
    print(f"Prepared {len(result['needs_review'])} unclassified charts at {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
