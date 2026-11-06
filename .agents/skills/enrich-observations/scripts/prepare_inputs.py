"""Read-only PDF/registry preparation; emit input metadata, registry and routing IDs as JSON."""

import argparse
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8")
try:
    from enrichment_io import InvalidData, SetupError, prepare_inputs
except ImportError as error:
    print(f"Setup failure: requires pydantic>=2.13.5 and jsonschema>=4.23,<5: {error}", file=sys.stderr)
    raise SystemExit(2) from error


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", required=True, type=Path)
    parser.add_argument("--registry", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        prepared = prepare_inputs(args.pdf, args.registry)
    except InvalidData as error:
        print(f"Invalid input: {error}", file=sys.stderr)
        return 1
    except SetupError as error:
        print(f"Setup/I/O failure: {error}", file=sys.stderr)
        return 2
    print(json.dumps(prepared.as_document(), ensure_ascii=False, allow_nan=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
