#!/usr/bin/env python3
"""Validate a figure-extraction artifact against its source catalog."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any

from jsonschema import Draft202012Validator

from prepare_extraction import ExtractionPreparationError, resolve_project_path


BOUND_COMPONENTS = {
    "lower_bound",
    "upper_bound",
    "lower_inclusive",
    "upper_inclusive",
}
FINAL_STATUSES = {
    "complete",
    "partial",
    "no_discrete_values",
    "needs_review",
    "not_data_figure",
}


class ExtractionValidationError(ValueError):
    """Raised when an extraction artifact violates its contract."""


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ExtractionValidationError(f"cannot read {path}: {exc}") from exc


def _default_schema() -> Path:
    return Path(__file__).resolve().parent.parent / "references" / "extraction.schema.json"


def _format_json_path(parts: Any) -> str:
    return "$" + "".join(
        f"[{part}]" if isinstance(part, int) else f".{part}" for part in parts
    )


def _validate_schema(extraction: Any, schema: Any) -> None:
    try:
        Draft202012Validator.check_schema(schema)
    except Exception as exc:
        raise ExtractionValidationError(f"invalid extraction schema: {exc}") from exc
    errors = sorted(
        Draft202012Validator(schema).iter_errors(extraction),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        first = errors[0]
        raise ExtractionValidationError(
            f"schema error at {_format_json_path(first.absolute_path)}: {first.message}"
        )


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _value_matches_type(value: Any, data_type: str) -> bool:
    if value is None:
        return True
    if data_type == "numeric":
        return _is_number(value)
    if data_type in {"categorical", "text", "datetime"}:
        return isinstance(value, str)
    if data_type == "boolean":
        return isinstance(value, bool)
    if data_type == "unknown":
        return _is_number(value) or isinstance(value, (str, bool))
    return False


def _validate_source_path(stored_path: str, project_root: Path) -> Path:
    if (
        PurePosixPath(stored_path).is_absolute()
        or PureWindowsPath(stored_path).is_absolute()
        or "\\" in stored_path
        or ".." in PurePosixPath(stored_path).parts
    ):
        raise ExtractionValidationError(
            "source_catalog must be a POSIX-style path relative to the project root"
        )
    try:
        return resolve_project_path(Path(stored_path), project_root)
    except ExtractionPreparationError as exc:
        raise ExtractionValidationError(str(exc)) from exc


def _catalog_figures(catalog: Any) -> list[dict[str, Any]]:
    if not isinstance(catalog, dict) or not isinstance(catalog.get("figures"), list):
        raise ExtractionValidationError("source catalog has no figures array")
    figures = catalog["figures"]
    for index, figure in enumerate(figures):
        if not isinstance(figure, dict):
            raise ExtractionValidationError(
                f"source catalog figures[{index}] must be an object"
            )
        if not isinstance(figure.get("catalog_id"), str):
            raise ExtractionValidationError(
                f"source catalog figures[{index}] has no catalog_id"
            )
        if not isinstance(figure.get("variables"), list):
            raise ExtractionValidationError(
                f"source catalog figures[{index}] has no variables array"
            )
    return figures


def _validate_status(
    entry: dict[str, Any], figure: dict[str, Any], location: str
) -> None:
    status = entry["status"]
    catalog_status = figure.get("status")
    if catalog_status == "needs_review" and status != "needs_review":
        raise ExtractionValidationError(
            f"{location}.status must remain needs_review until its catalog entry is resolved"
        )
    if catalog_status == "not_data_figure" and status != "not_data_figure":
        raise ExtractionValidationError(
            f"{location}.status must mirror catalog status not_data_figure"
        )
    if catalog_status == "cataloged" and status == "not_data_figure":
        raise ExtractionValidationError(
            f"{location}.status cannot override a cataloged figure as not_data_figure"
        )
    if status not in FINAL_STATUSES:
        raise ExtractionValidationError(
            f"{location}.status is not final: {status}"
        )


def _validate_layout(
    entry: dict[str, Any], location: str
) -> dict[int, dict[str, int]]:
    variables = entry["variables"]
    positions_by_variable: dict[int, dict[str, int]] = defaultdict(dict)
    seen: set[tuple[int, str]] = set()

    for position, layout_item in enumerate(entry["layout"]):
        variable_index = layout_item["variable_index"]
        component = layout_item["component"]
        key = (variable_index, component)
        if key in seen:
            raise ExtractionValidationError(
                f"{location}.layout repeats variable {variable_index} component {component}"
            )
        seen.add(key)
        if variable_index >= len(variables):
            raise ExtractionValidationError(
                f"{location}.layout[{position}].variable_index is outside the catalog variables"
            )
        data_type = variables[variable_index].get("data_type")
        if component in BOUND_COMPONENTS and data_type != "numeric":
            raise ExtractionValidationError(
                f"{location}.layout[{position}] uses {component} for non-numeric "
                f"variable {variable_index}"
            )
        positions_by_variable[variable_index][component] = position

    expected_indexes = set(range(len(variables)))
    missing_indexes = sorted(expected_indexes - set(positions_by_variable))
    if missing_indexes:
        raise ExtractionValidationError(
            f"{location}.layout omits catalog variable indexes {missing_indexes}"
        )

    for variable_index, components in positions_by_variable.items():
        if "lower_inclusive" in components and "lower_bound" not in components:
            raise ExtractionValidationError(
                f"{location}.layout variable {variable_index} has lower_inclusive "
                "without lower_bound"
            )
        if "upper_inclusive" in components and "upper_bound" not in components:
            raise ExtractionValidationError(
                f"{location}.layout variable {variable_index} has upper_inclusive "
                "without upper_bound"
            )
    return positions_by_variable


def _validate_rows(
    entry: dict[str, Any],
    positions_by_variable: dict[int, dict[str, int]],
    location: str,
) -> None:
    variables = entry["variables"]
    layout = entry["layout"]
    for row_index, row in enumerate(entry["rows"]):
        row_location = f"{location}.rows[{row_index}]"
        if len(row) != len(layout):
            raise ExtractionValidationError(
                f"{row_location} has {len(row)} values but layout has {len(layout)} positions"
            )
        for position, layout_item in enumerate(layout):
            value = row[position]
            variable_index = layout_item["variable_index"]
            component = layout_item["component"]
            if component == "value":
                data_type = variables[variable_index].get("data_type")
                if not _value_matches_type(value, data_type):
                    raise ExtractionValidationError(
                        f"{row_location}[{position}] does not match catalog data_type "
                        f"{data_type} for variable {variable_index}"
                    )
            elif component in {"lower_bound", "upper_bound"}:
                if value is not None and not _is_number(value):
                    raise ExtractionValidationError(
                        f"{row_location}[{position}] must be numeric or null for {component}"
                    )
            elif value is not None and not isinstance(value, bool):
                raise ExtractionValidationError(
                    f"{row_location}[{position}] must be boolean or null for {component}"
                )

        for variable_index, components in positions_by_variable.items():
            lower = (
                row[components["lower_bound"]]
                if "lower_bound" in components
                else None
            )
            upper = (
                row[components["upper_bound"]]
                if "upper_bound" in components
                else None
            )
            central = row[components["value"]] if "value" in components else None
            if lower is not None and upper is not None and lower > upper:
                raise ExtractionValidationError(
                    f"{row_location} has lower_bound greater than upper_bound for "
                    f"variable {variable_index}"
                )
            if _is_number(central):
                if lower is not None and central < lower:
                    raise ExtractionValidationError(
                        f"{row_location} central value is below lower_bound for "
                        f"variable {variable_index}"
                    )
                if upper is not None and central > upper:
                    raise ExtractionValidationError(
                        f"{row_location} central value is above upper_bound for "
                        f"variable {variable_index}"
                    )
            if "lower_inclusive" in components:
                inclusive = row[components["lower_inclusive"]]
                if inclusive is not None and lower is None:
                    raise ExtractionValidationError(
                        f"{row_location} sets lower_inclusive without a lower_bound "
                        f"for variable {variable_index}"
                    )
            if "upper_inclusive" in components:
                inclusive = row[components["upper_inclusive"]]
                if inclusive is not None and upper is None:
                    raise ExtractionValidationError(
                        f"{row_location} sets upper_inclusive without an upper_bound "
                        f"for variable {variable_index}"
                    )


def _validate_semantics(extraction: dict[str, Any], project_root: Path) -> Counter[str]:
    catalog_path = _validate_source_path(extraction["source_catalog"], project_root)
    catalog = _load_json(catalog_path)
    figures = _catalog_figures(catalog)
    entries = extraction["extractions"]

    catalog_ids = [figure["catalog_id"] for figure in figures]
    extraction_ids = [entry["catalog_id"] for entry in entries]
    duplicates = [
        catalog_id
        for catalog_id, count in Counter(extraction_ids).items()
        if count > 1
    ]
    if duplicates:
        raise ExtractionValidationError(
            f"duplicate extraction catalog_id: {sorted(duplicates)[0]}"
        )
    if extraction_ids != catalog_ids:
        missing = sorted(set(catalog_ids) - set(extraction_ids))
        unexpected = sorted(set(extraction_ids) - set(catalog_ids))
        if missing:
            detail = f"missing catalog entries {missing}"
        elif unexpected:
            detail = f"unexpected catalog entries {unexpected}"
        else:
            detail = "entry order differs from the source catalog"
        raise ExtractionValidationError(f"extraction coverage mismatch: {detail}")

    statuses: Counter[str] = Counter()
    for index, (entry, figure) in enumerate(zip(entries, figures, strict=True)):
        location = f"extractions[{index}]"
        if entry["variables"] != figure["variables"]:
            raise ExtractionValidationError(
                f"{location}.variables must exactly match the source catalog entry"
            )
        _validate_status(entry, figure, location)
        positions = _validate_layout(entry, location)
        _validate_rows(entry, positions, location)
        statuses[entry["status"]] += 1
    return statuses


def validate(
    extraction_path: Path,
    schema_path: Path,
    project_root: Path | None = None,
) -> Counter[str]:
    extraction = _load_json(extraction_path)
    schema = _load_json(schema_path)
    _validate_schema(extraction, schema)
    if not isinstance(extraction, dict):
        raise ExtractionValidationError("extraction root must be an object")
    root = (project_root or Path.cwd()).resolve()
    if not root.is_dir():
        raise ExtractionValidationError(f"project root does not exist: {root}")
    return _validate_semantics(extraction, root)


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--schema", type=Path, default=_default_schema())
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="base directory for resolving source_catalog (default: cwd)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        statuses = validate(
            args.input.resolve(),
            args.schema.resolve(),
            args.project_root.resolve(),
        )
    except ExtractionValidationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    summary = ", ".join(
        f"{status}={count}" for status, count in sorted(statuses.items())
    )
    print(f"Validated {sum(statuses.values())} extraction entries ({summary})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
