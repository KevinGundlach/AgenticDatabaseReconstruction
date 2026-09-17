"""Validate extracted JSON only; never reads or processes a source PDF.

Requires jsonschema>=4.23,<5. Exit codes: 0 valid, 1 invalid data, 2 setup/I/O error.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import re
import sys

try:
    from jsonschema import Draft202012Validator
    from jsonschema.exceptions import SchemaError
except ImportError:
    raise SystemExit("Missing dependency: use the project's Python environment with jsonschema>=4.23,<5.")


SCHEMA_PATH = Path(__file__).resolve().parents[1] / "references" / "series_extraction.schema.json"


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
    return "/" + "/".join(str(p).replace("~", "~0").replace("/", "~1") for p in parts)


def _nonfinite(value, parts=()):
    if isinstance(value, float) and not math.isfinite(value):
        yield f"{_pointer(parts)}: number must be finite"
    elif isinstance(value, dict):
        for key, child in value.items():
            yield from _nonfinite(child, (*parts, key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _nonfinite(child, (*parts, index))


def validate_document(document, schema=None):
    """Return diagnostics without modifying the input or interpreting scientific units."""
    if schema is None:
        schema = load_json(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    errors = list(_nonfinite(document))
    errors.extend(
        f"{_pointer(error.absolute_path)}: {error.message}"
        for error in Draft202012Validator(schema).iter_errors(document)
    )
    if errors:
        return errors  # Semantic checks below assume the structural contract.

    prefix = re.match(r"^(\d+)", document["paper_name"])
    if prefix and int(prefix.group(1)) != document["reference_number"]:
        errors.append("/reference_number: does not match the filename's leading number")

    for si, series in enumerate(document["series"]):
        base = ("series", si)
        names = set()
        for ci, column in enumerate(series["columns"]):
            name = column["name"].strip()
            if name in names:
                errors.append(f"{_pointer((*base, 'columns', ci, 'name'))}: duplicate column name {name!r}")
            names.add(name)

        width = len(series["columns"])
        for ri, row in enumerate(series["rows"]):
            location = (*base, "rows", ri)
            if len(row) != width:
                errors.append(f"{_pointer(location)}: expected {width} cells, found {len(row)}")
            for ci, cell in enumerate(row):
                if not isinstance(cell, dict):
                    continue
                path = _pointer((*location, ci))
                if "min" in cell and "max" in cell and cell["min"] > cell["max"]:
                    errors.append(f"{path}: min exceeds max")
                if "value" in cell:
                    if "min" in cell and cell["value"] < cell["min"]:
                        errors.append(f"{path}: value is below min")
                    if "max" in cell and cell["value"] > cell["max"]:
                        errors.append(f"{path}: value is above max")
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Extraction JSON to validate (read-only)")
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
    print(f"VALID: {args.input} ({len(document['series'])} series). Scientific fidelity and coverage not checked.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
