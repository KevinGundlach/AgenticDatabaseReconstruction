#!/usr/bin/env python3
"""
Validation script for digitized pitting-potential plot JSON outputs.
Validates output JSON files against the standardized schema and semantic rules.
"""

import sys
import json
import argparse
from pathlib import Path

def find_schema(script_dir: Path, workspace_root: Path) -> Path:
    candidates = [
        script_dir.parent / "references" / "digitized_pitting_potential_plot.schema.json",
        workspace_root / "digitized_pitting_potential_plot.schema.json",
        workspace_root / ".agents" / "skills" / "tabularize-plots" / "references" / "digitized_pitting_potential_plot.schema.json"
    ]
    for p in candidates:
        if p.exists():
            return p
    raise FileNotFoundError("Could not find digitized_pitting_potential_plot.schema.json in skill references or workspace root.")

def find_input_metadata(output_file: Path, input_dir: Path) -> Path:
    """Return the expected input metadata path for an output JSON file."""
    # Output file: tabularized_{stem}.json
    stem = output_file.stem
    if stem.startswith("tabularized_"):
        stem = stem[len("tabularized_"):]

    return input_dir / f"{stem}.json"

def semantic_checks(data: dict, file_path: Path, input_dir: Path) -> tuple[list[str], list[str]]:
    """Perform non-schema semantic checks described in the schema specification."""
    errors = []
    warnings = []
    plot_data = data.get("plot_data", [])

    # 1. Cross-reference with input metadata if available
    input_meta_path = find_input_metadata(file_path, input_dir)
    if input_meta_path.exists():
        try:
            with open(input_meta_path, "r", encoding="utf-8") as f:
                input_meta = json.load(f)
            if data.get("paper_reference") != input_meta.get("paper_reference"):
                errors.append(f"paper_reference mismatch: got '{data.get('paper_reference')}', expected '{input_meta.get('paper_reference')}'.")
            if data.get("source_chart_manifest") != input_meta.get("source_chart_manifest"):
                errors.append(f"source_chart_manifest mismatch: got '{data.get('source_chart_manifest')}', expected '{input_meta.get('source_chart_manifest')}'.")
            if data.get("plot_metadata") != input_meta.get("plot_metadata"):
                errors.append("plot_metadata does not exactly match the input metadata file.")
        except Exception as e:
            errors.append(f"Failed to read paired input metadata {input_meta_path.name}: {e}")
    else:
        warnings.append(f"Paired input metadata not found: {input_meta_path}")

    # 2. series_id uniqueness within plot_data
    seen_series = set()
    for idx, series in enumerate(plot_data):
        s_id = series.get("series_id")
        if s_id in seen_series:
            errors.append(f"Series #{idx}: duplicate series_id '{s_id}'.")
        seen_series.add(s_id)
        
        # Check target axis count
        x_target = series.get("x_axis", {}).get("is_target", False)
        y_target = series.get("y_axis", {}).get("is_target", False)
        if (x_target and y_target) or (not x_target and not y_target):
            errors.append(f"Series '{s_id}': Exactly one axis must have is_target=True (x={x_target}, y={y_target}).")

        # Check intervals lower <= upper and central point inside interval
        for p_idx, pt in enumerate(series.get("data_points", [])):
            if "x_lower" in pt and "x_upper" in pt:
                if pt["x_lower"] is not None and pt["x_upper"] is not None:
                    if pt["x_lower"] > pt["x_upper"]:
                        errors.append(f"Series '{s_id}' point #{p_idx}: x_lower ({pt['x_lower']}) > x_upper ({pt['x_upper']}).")
                    if pt.get("x") is not None and isinstance(pt["x"], (int, float)):
                        if not (pt["x_lower"] <= pt["x"] <= pt["x_upper"]):
                            errors.append(f"Series '{s_id}' point #{p_idx}: x value ({pt['x']}) not in [{pt['x_lower']}, {pt['x_upper']}].")
            
            if "y_lower" in pt and "y_upper" in pt:
                if pt["y_lower"] is not None and pt["y_upper"] is not None:
                    if pt["y_lower"] > pt["y_upper"]:
                        errors.append(f"Series '{s_id}' point #{p_idx}: y_lower ({pt['y_lower']}) > y_upper ({pt['y_upper']}).")
                    if pt.get("y") is not None and isinstance(pt["y"], (int, float)):
                        if not (pt["y_lower"] <= pt["y"] <= pt["y_upper"]):
                            errors.append(f"Series '{s_id}' point #{p_idx}: y_value ({pt['y']}) not in [{pt['y_lower']}, {pt['y_upper']}].")

    return errors, warnings

def validate_outputs(input_dir: Path, output_dir: Path, schema_path: Path):
    try:
        import jsonschema
        from jsonschema import Draft202012Validator
    except ImportError:
        print("[ERROR] 'jsonschema' library is required. Install via: uv add jsonschema", file=sys.stderr)
        sys.exit(1)

    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    validator = Draft202012Validator(schema)

    json_files = sorted(list(output_dir.glob("tabularized_*.json")) or list(output_dir.glob("*.json")))
    if not json_files:
        print(f"[WARN] No JSON files found in {output_dir}")
        return True

    print(f"\n--- Validating {len(json_files)} output file(s) in {output_dir} ---")
    print(f"Using input metadata from: {input_dir}")
    print(f"Using schema: {schema_path.name}\n")

    total_valid = 0
    total_invalid = 0
    status_counts = {"complete": 0, "partial": 0, "needs_review": 0, "skipped": 0, "unprocessed": 0}

    for jf in json_files:
        try:
            with open(jf, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"[FAIL] {jf.name}: Invalid JSON syntax - {e}")
            total_invalid += 1
            continue

        schema_errors = list(validator.iter_errors(data))
        sem_errors, sem_warnings = semantic_checks(data, jf, input_dir)

        for warning in sem_warnings:
            print(f"[WARN] {jf.name}: {warning}")

        if not schema_errors and not sem_errors:
            status = data.get("digitization_status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
            total_valid += 1
            print(f"[PASS] {jf.name} (status: {status})")
        else:
            total_invalid += 1
            print(f"[FAIL] {jf.name}:")
            for err in schema_errors:
                path = " -> ".join(str(p) for p in err.absolute_path) or "root"
                print(f"   • Schema error at [{path}]: {err.message}")
            for err in sem_errors:
                print(f"   • Semantic error: {err}")

    print("\n" + "="*50)
    print(f"Summary for {output_dir.name}:")
    print(f"  Total Checked : {len(json_files)}")
    print(f"  Valid         : {total_valid}")
    print(f"  Invalid       : {total_invalid}")
    print("  Status breakdown:")
    for status, count in status_counts.items():
        if count > 0:
            print(f"    - {status}: {count}")
    print("="*50 + "\n")

    return total_invalid == 0

def main():
    parser = argparse.ArgumentParser(description="Validate digitized pitting potential JSON outputs.")
    parser.add_argument("--input", required=True, type=Path, help="Directory containing paired input metadata JSON files.")
    parser.add_argument("--output", required=True, type=Path, help="Directory containing tabularized output JSON files.")
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    workspace_root = Path.cwd()
    schema_path = find_schema(script_dir, workspace_root)

    input_dir = args.input.expanduser().resolve()
    output_dir = args.output.expanduser().resolve()

    for label, directory in (("Input", input_dir), ("Output", output_dir)):
        if not directory.exists():
            print(f"[ERROR] {label} directory '{directory}' does not exist.", file=sys.stderr)
            sys.exit(1)
        if not directory.is_dir():
            print(f"[ERROR] {label} path '{directory}' is not a directory.", file=sys.stderr)
            sys.exit(1)

    success = validate_outputs(input_dir, output_dir, schema_path)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
