"""Read-only enrichment validation. Exit 0 valid, 1 invalid data, 2 setup/I/O failure."""

import argparse
from pathlib import Path
import sys

sys.dont_write_bytecode = True
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8")
try:
    from enrichment_io import InvalidData, SetupError, load_json, prepare_inputs, validate_enrichment
except ImportError as error:
    print(f"Setup failure: requires pydantic>=2.13.5 and jsonschema>=4.23,<5: {error}", file=sys.stderr)
    raise SystemExit(2) from error


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--pdf", required=True, type=Path)
    parser.add_argument("--registry", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        if args.input.suffix.lower() != ".json":
            raise InvalidData("Enrichment input must be a .json file")
        prepared = prepare_inputs(args.pdf, args.registry)
        result = validate_enrichment(load_json(args.input), prepared)
    except InvalidData as error:
        print(f"Invalid data: {error}", file=sys.stderr)
        return 1
    except SetupError as error:
        print(f"Setup/I/O failure: {error}", file=sys.stderr)
        return 2
    flagged = [row.observation_id for row in result.experiments if row.failure_notes.strip()]
    print(f"VALID: {args.input}")
    print(f"Supplied={len(prepared.registry.observations)}; eligible={len(prepared.eligible_ids)}; "
          f"written={len(result.experiments)}; skipped_failed={len(prepared.skipped_failed_ids)}; flagged={len(flagged)}.")
    print("Skipped failed IDs: " + (", ".join(prepared.skipped_failed_ids) or "none"))
    print("Flagged output IDs: " + (", ".join(flagged) or "none"))
    for warning in prepared.warnings:
        print("Input warning: " + warning)
    if not prepared.eligible_ids:
        print("No eligible observations were supplied; this does not mean the paper contains no outcomes.")
    print("Scientific fidelity, retained qualification meanings and actual visual coverage are not certified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
