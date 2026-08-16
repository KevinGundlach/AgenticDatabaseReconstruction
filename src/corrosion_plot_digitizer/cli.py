"""Command-line interface for discovery, conversion, and finalization."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .chemistry import binary_atomic_percent_to_weight_percent
from .discovery import discover_figures, write_manifest
from .finalize import finalize_spec


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="corrosion-plot-digitizer")
    subparsers = parser.add_subparsers(dest="command", required=True)

    discover = subparsers.add_parser("discover", help="Find and screen figures in MinerU Markdown")
    discover.add_argument("--markdown", required=True, type=Path)
    discover.add_argument("--paper-id", required=True)
    discover.add_argument("--output", required=True, type=Path)

    finalize = subparsers.add_parser("finalize", help="Validate raw agent output and create CSV")
    finalize.add_argument("--input", required=True, type=Path)
    finalize.add_argument("--output-dir", required=True, type=Path)
    finalize.add_argument(
        "--include-metric",
        action="append",
        dest="include_metrics",
        help="Metric to include; repeatable (default: pitting_potential)",
    )

    convert = subparsers.add_parser("convert-binary", help="Convert a binary at.%% coordinate to wt.%%")
    convert.add_argument("--base", required=True)
    convert.add_argument("--solute", required=True)
    convert.add_argument("--solute-at-percent", required=True, type=float)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "discover":
        candidates = discover_figures(args.markdown, args.paper_id)
        write_manifest(candidates, args.output, args.markdown)
        relevant = sum(candidate.relevant for candidate in candidates)
        print(f"Wrote {len(candidates)} figures ({relevant} explicit candidates) to {args.output}")
        return 0
    if args.command == "finalize":
        metadata = finalize_spec(
            args.input,
            args.output_dir,
            set(args.include_metrics) if args.include_metrics else None,
        )
        print(json.dumps(metadata, indent=2))
        return 0
    if args.command == "convert-binary":
        result = binary_atomic_percent_to_weight_percent(
            args.base, args.solute, args.solute_at_percent
        )
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    raise AssertionError(f"Unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())

