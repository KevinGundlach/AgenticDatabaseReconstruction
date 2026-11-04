"""Validate extraction JSON with bundled JSON Schema and Pydantic classes.

Reads no PDFs and never modifies input. Requires pydantic>=2.13.5 and
jsonschema>=4.23,<5. Exit codes: 0 valid, 1 invalid data, 2 setup/I/O error.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

try:
    from jsonschema import Draft202012Validator
    from jsonschema.exceptions import SchemaError
    from pydantic import ValidationError
    from paper_extraction import PaperExtraction
except ImportError as error:
    print(
        "Missing dependency: use Python with pydantic>=2.13.5 and jsonschema>=4.23,<5. "
        f"Details: {error}", file=sys.stderr,
    )
    raise SystemExit(2) from error


SCHEMA_PATH = Path(__file__).resolve().parents[1] / "references" / "paper_extraction.schema.json"


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key!r}")
        result[key] = value
    return result


def _reject_constant(value):
    raise ValueError(f"Non-JSON numeric constant: {value}")


def load_json(path: Path):
    return json.loads(
        path.read_text(encoding="utf-8-sig"),
        object_pairs_hook=_unique_object,
        parse_constant=_reject_constant,
    )


def _pointer(parts):
    return "/" + "/".join(str(part).replace("~", "~0").replace("/", "~1") for part in parts)


def validate_document(document):
    """Return field diagnostics; flagged rows can be structurally valid."""
    schema = load_json(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    if schema != PaperExtraction.model_json_schema():
        raise ValueError("Bundled JSON Schema differs from the bundled Pydantic classes")
    errors = [
        f"{_pointer(error.absolute_path)}: {error.message}"
        for error in Draft202012Validator(schema).iter_errors(document)
    ]
    if errors:
        return errors
    try:
        PaperExtraction.model_validate(document)
    except ValidationError as error:
        errors.extend(
            f"{_pointer(item['loc'])}: {item['msg']}"
            for item in error.errors(include_url=False)
        )
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Extraction JSON (read-only)")
    args = parser.parse_args(argv)
    if args.input.suffix.lower() != ".json":
        print("Input must be a .json file; this validator does not read PDFs.", file=sys.stderr)
        return 2
    try:
        document = load_json(args.input)
    except OSError as error:
        print(f"Cannot read input: {error}", file=sys.stderr)
        return 2
    except (ValueError, UnicodeError) as error:
        print(f"Invalid JSON: {error}", file=sys.stderr)
        return 1
    try:
        errors = validate_document(document)
    except (OSError, ValueError, SchemaError) as error:
        print(f"Cannot load/validate bundled schema: {error}", file=sys.stderr)
        return 2
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    flagged = [i for i, row in enumerate(document["experiments"]) if row["failure_notes"].strip()]
    print(f"VALID: {args.input} ({len(document['experiments'])} experiments, {len(flagged)} flagged rows).")
    if flagged:
        print("ATTENTION: nonempty failure_notes at experiments indices: " + ", ".join(map(str, flagged)))
    print("Scientific fidelity and coverage not checked.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
