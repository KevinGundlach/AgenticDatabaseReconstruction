#!/usr/bin/env python3
"""Validate a completed figure-variable catalog against its MinerU source."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from identify_figures import CatalogSkeletonError, build_catalog_skeleton


VOCABULARY_FIELDS = {"canonical_name", "preferred_label", "definition"}
CANONICAL_NAME_RE = re.compile(r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$")
FORBIDDEN_FIELDS = {
    "categories",
    "category_levels",
    "color",
    "constant_value",
    "data",
    "data_points",
    "legend_position",
    "levels",
    "line_style",
    "marker_style",
    "observations",
    "tick_range",
    "value",
    "values",
    "x_axis",
    "y_axis",
}
PROVENANCE_FIELDS = (
    "source_figure_id",
    "type",
    "page_number",
    "item_index",
    "image_path",
    "caption",
)


class CatalogValidationError(ValueError):
    """Raised when the final catalog violates its contract."""


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise CatalogValidationError(f"cannot read {path}: {exc}") from exc


def _default_schema() -> Path:
    return Path(__file__).resolve().parent.parent / "references" / "catalog.schema.json"


def _default_vocabulary() -> Path | None:
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "vocabularies" / "variables.json"
        if candidate.is_file():
            return candidate
    return None


def _format_json_path(parts: Any) -> str:
    return "$" + "".join(
        f"[{part}]" if isinstance(part, int) else f".{part}" for part in parts
    )


def _validate_schema(catalog: Any, schema: Any) -> None:
    try:
        Draft202012Validator.check_schema(schema)
    except Exception as exc:  # jsonschema exposes several schema error types
        raise CatalogValidationError(f"invalid catalog schema: {exc}") from exc
    errors = sorted(
        Draft202012Validator(schema).iter_errors(catalog),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        first = errors[0]
        raise CatalogValidationError(
            f"schema error at {_format_json_path(first.absolute_path)}: {first.message}"
        )


def _validate_vocabulary(value: Any) -> set[str]:
    if not isinstance(value, dict) or set(value) != {"schema_version", "variables"}:
        raise CatalogValidationError(
            "vocabulary must contain only schema_version and variables"
        )
    if value["schema_version"] != 1:
        raise CatalogValidationError("vocabulary schema_version must be 1")
    entries = value["variables"]
    if not isinstance(entries, list):
        raise CatalogValidationError("vocabulary.variables must be an array")

    names: set[str] = set()
    for position, entry in enumerate(entries):
        location = f"vocabulary.variables[{position}]"
        if not isinstance(entry, dict) or set(entry) != VOCABULARY_FIELDS:
            raise CatalogValidationError(
                f"{location} must contain only {sorted(VOCABULARY_FIELDS)}"
            )
        if not all(
            isinstance(entry[field], str) and entry[field].strip()
            for field in VOCABULARY_FIELDS
        ):
            raise CatalogValidationError(
                f"{location} fields must be non-empty strings"
            )
        name = entry["canonical_name"]
        if not CANONICAL_NAME_RE.fullmatch(name):
            raise CatalogValidationError(
                f"{location}.canonical_name must be lower snake case"
            )
        if name in names:
            raise CatalogValidationError(f"duplicate vocabulary name: {name}")
        names.add(name)
    return names


def _find_forbidden_fields(value: Any, path: str = "$") -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in FORBIDDEN_FIELDS:
                found.append(child_path)
            found.extend(_find_forbidden_fields(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(_find_forbidden_fields(child, f"{path}[{index}]"))
    return found


def _validate_catalog_semantics(
    catalog: dict[str, Any], vocabulary_names: set[str]
) -> None:
    forbidden = _find_forbidden_fields(catalog)
    if forbidden:
        raise CatalogValidationError(
            f"catalog contains forbidden data or presentation field: {forbidden[0]}"
        )

    try:
        expected = build_catalog_skeleton(Path(catalog["input_path"]))
    except (CatalogSkeletonError, OSError) as exc:
        raise CatalogValidationError(f"cannot rebuild source inventory: {exc}") from exc

    for field in (
        "paper_reference",
        "input_path",
        "source_content_list",
        "source_pdf",
    ):
        if catalog[field] != expected[field]:
            raise CatalogValidationError(f"{field} differs from the source inventory")

    expected_by_id = {
        entry["source_figure_id"]: entry for entry in expected["figures"]
    }
    entries_by_source: dict[str, list[dict[str, Any]]] = defaultdict(list)
    catalog_ids: set[str] = set()

    for position, entry in enumerate(catalog["figures"]):
        location = f"figures[{position}]"
        catalog_id = entry["catalog_id"]
        if catalog_id in catalog_ids:
            raise CatalogValidationError(f"duplicate catalog_id: {catalog_id}")
        catalog_ids.add(catalog_id)

        source_id = entry["source_figure_id"]
        source = expected_by_id.get(source_id)
        if source is None:
            raise CatalogValidationError(
                f"{location}.source_figure_id is absent from the MinerU inventory"
            )
        for field in PROVENANCE_FIELDS:
            if entry[field] != source[field]:
                raise CatalogValidationError(
                    f"{location}.{field} differs from the MinerU inventory"
                )
        if not catalog_id.startswith(source_id):
            raise CatalogValidationError(
                f"{location}.catalog_id must begin with its source_figure_id"
            )
        entries_by_source[source_id].append(entry)

        seen_variables: set[str] = set()
        for variable_index, variable in enumerate(entry["variables"]):
            canonical_name = variable["canonical_name"]
            if canonical_name is None:
                if entry["status"] != "needs_review":
                    raise CatalogValidationError(
                        f"{location}.variables[{variable_index}] has an unresolved "
                        "mapping outside a needs_review entry"
                    )
                if variable["source_label"] is None:
                    raise CatalogValidationError(
                        f"{location}.variables[{variable_index}] must retain the "
                        "ambiguous source label"
                    )
                continue
            if canonical_name not in vocabulary_names:
                raise CatalogValidationError(
                    f"{location}.variables[{variable_index}].canonical_name "
                    f"is absent from the vocabulary: {canonical_name}"
                )
            if canonical_name in seen_variables:
                raise CatalogValidationError(
                    f"{location} repeats canonical variable {canonical_name}"
                )
            seen_variables.add(canonical_name)

    missing = sorted(set(expected_by_id) - set(entries_by_source))
    if missing:
        raise CatalogValidationError(
            f"catalog omits MinerU source figures: {missing}"
        )

    for source_id, entries in entries_by_source.items():
        panel_labels = [entry["panel_label"] for entry in entries]
        if len(entries) > 1:
            if any(label is None for label in panel_labels):
                raise CatalogValidationError(
                    f"split source figure {source_id} requires a panel_label on every entry"
                )
            if len(set(panel_labels)) != len(panel_labels):
                raise CatalogValidationError(
                    f"split source figure {source_id} repeats a panel_label"
                )
        for entry in entries:
            if entry["panel_label"] is None and entry["catalog_id"] != source_id:
                raise CatalogValidationError(
                    f"unsplit source figure {source_id} must use its source ID as catalog_id"
                )
            if entry["panel_label"] is not None and not entry["catalog_id"].startswith(
                f"{source_id}__panel_"
            ):
                raise CatalogValidationError(
                    f"panel entry for {source_id} must use a __panel_ catalog_id suffix"
                )


def validate(catalog_path: Path, schema_path: Path, vocabulary_path: Path) -> int:
    catalog = _load_json(catalog_path)
    schema = _load_json(schema_path)
    vocabulary = _load_json(vocabulary_path)
    _validate_schema(catalog, schema)
    if not isinstance(catalog, dict):
        raise CatalogValidationError("catalog root must be an object")
    vocabulary_names = _validate_vocabulary(vocabulary)
    _validate_catalog_semantics(catalog, vocabulary_names)
    return len(catalog["figures"])


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--schema", type=Path, default=_default_schema())
    parser.add_argument("--vocabulary", type=Path, default=_default_vocabulary())
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    if args.vocabulary is None:
        print(
            "error: cannot locate vocabularies/variables.json; pass --vocabulary",
            file=sys.stderr,
        )
        return 1
    try:
        entry_count = validate(
            args.input.resolve(), args.schema.resolve(), args.vocabulary.resolve()
        )
    except CatalogValidationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"Validated {entry_count} catalog entries with complete source coverage")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
