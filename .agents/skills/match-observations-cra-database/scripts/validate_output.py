"""Read-only alignment validation. Exit 0 valid, 1 invalid data, 2 setup/I/O failure."""

import argparse
from collections import Counter
from pathlib import Path
import sys
from typing import get_args

sys.dont_write_bytecode = True
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8")
try:
    from alignment import MatchStatus
    from matching_io import InvalidData, SetupError, load_json, prepare_inputs, shared_rows, validate_alignment
except ImportError as error:
    print(f"Setup failure: requires pydantic>=2.13.5 and jsonschema>=4.23,<5: {error}", file=sys.stderr)
    raise SystemExit(2) from error


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--pdf", required=True, type=Path)
    parser.add_argument("--csv", required=True, type=Path)
    parser.add_argument("--registry", required=True, type=Path)
    parser.add_argument("--report-stdout", action="store_true", help="Print a compact Markdown report after validation; writes no files")
    args = parser.parse_args(argv)
    try:
        if args.input.suffix.lower() != ".json":
            raise InvalidData("Alignment input must be a .json file")
        prepared = prepare_inputs(args.pdf, args.csv, args.registry)
        result = validate_alignment(load_json(args.input), prepared)
    except InvalidData as error:
        print(f"Invalid data: {error}", file=sys.stderr)
        return 1
    except SetupError as error:
        print(f"Setup/I/O failure: {error}", file=sys.stderr)
        return 2
    if args.report_stdout:
        from alignment_report import render_report
        print(render_report(result, prepared))
        return 0
    counts = Counter(o.status for o in result.observations)
    print(f"VALID: {args.input} ({len(result.observations)} supplied observations).")
    print("Status counts: " + "; ".join(f"{status}={counts[status]}" for status in get_args(MatchStatus)))
    for status in ("ambiguous", "unmatched", "not_assessed"):
        ids = [o.observation_id for o in result.observations if o.status == status]
        print(f"{status} IDs: " + (", ".join(ids) or "none"))
    groups = shared_rows(result)
    print("Supported shared CRA rows: " + ("; ".join(f"{n}: {', '.join(ids)}" for n, ids in groups.items()) or "none"))
    print("Unlinked CRA No. in this input: " + (", ".join(map(str, result.unlinked_citrine_nos)) or "none"))
    print("Only supported links enter default joins. Partial-input coverage is not paper-wide coverage.")
    print("Scientific fidelity, conversion arithmetic/assumptions, identity and benchmark suitability are not certified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
