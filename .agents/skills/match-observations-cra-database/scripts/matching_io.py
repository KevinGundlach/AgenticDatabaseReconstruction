"""Read-only input preparation and cross-input alignment checks. No PDF parsing."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import hashlib
import io
import json
import math
from pathlib import Path
import re

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError
from pydantic import ValidationError

from alignment import InputFile, InputFiles, ObservationAlignment
from observation_registry import ObservationRegistry


REFERENCES = Path(__file__).resolve().parents[1] / "references"
TARGET_COLUMNS = {
    "avg": "Avg Epit mV (SCE)",
    "min": "Min Epit mV (SCE)",
    "max": "Max Epit mV (SCE)",
}
REQUIRED_COLUMNS = ("No.", "Reference", *TARGET_COLUMNS.values())


class InvalidData(ValueError):
    """Invalid supplied data: CLI exit 1."""


class SetupError(RuntimeError):
    """Missing/unreadable files, dependencies or damaged bundled schemas: exit 2."""


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise InvalidData(f"Duplicate JSON key: {key!r}")
        result[key] = value
    return result


def _reject_constant(value):
    raise InvalidData(f"Non-finite JSON number: {value}")


def _finite_float(value):
    result = float(value)
    if not math.isfinite(result):
        raise InvalidData(f"Non-finite JSON number: {value}")
    return result


def read_bytes(path: Path) -> bytes:
    try:
        return path.read_bytes()
    except OSError as error:
        raise SetupError(f"Cannot read {path}: {error}") from error


def parse_json(data: bytes, label: str):
    try:
        return json.loads(
            data.decode("utf-8-sig"), object_pairs_hook=_unique_object,
            parse_constant=_reject_constant, parse_float=_finite_float,
        )
    except (ValueError, UnicodeError) as error:
        raise InvalidData(f"{label}: {error}") from error


def load_json(path: Path):
    return parse_json(read_bytes(path), str(path))


def _pointer(parts):
    return "/" + "/".join(str(part).replace("~", "~0").replace("/", "~1") for part in parts)


def validate_model(document, model, schema_name: str):
    """Validate through both the bundled JSON Schema and Pydantic definition."""
    try:
        schema = load_json(REFERENCES / schema_name)
        Draft202012Validator.check_schema(schema)
        if schema != model.model_json_schema():
            raise SetupError(f"Bundled {schema_name} differs from its Pydantic model")
    except (InvalidData, SchemaError) as error:
        raise SetupError(f"Cannot use bundled {schema_name}: {error}") from error
    expected = schema["properties"]["schema_version"]["const"]
    if isinstance(document, dict) and "schema_version" in document and document["schema_version"] != expected:
        kind = "registry" if model is ObservationRegistry else "alignment"
        raise InvalidData(
            f"/schema_version: unsupported {kind} version {document['schema_version']!r}; "
            f"expected {expected!r}. No automatic upgrade is performed."
        )
    errors = [f"{_pointer(e.absolute_path)}: {e.message}" for e in Draft202012Validator(schema).iter_errors(document)]
    if errors:
        raise InvalidData("\n".join(errors))
    try:
        return model.model_validate(document)
    except ValidationError as error:
        raise InvalidData("\n".join(
            f"{_pointer(e['loc'])}: {e['msg']}" for e in error.errors(include_url=False)
        )) from error


def positive_identifier(value, label):
    try:
        number = Decimal(str(value).strip())
        if not number.is_finite() or number <= 0 or number != number.to_integral_value():
            raise ValueError
        return int(number)
    except (InvalidOperation, ValueError, OverflowError) as error:
        raise InvalidData(f"{label}: expected a positive integer, got {value!r}") from error


def fingerprint(path: Path, data: bytes) -> InputFile:
    return InputFile(filename=path.name, sha256=hashlib.sha256(data).hexdigest())


def parse_csv(data: bytes, label: str):
    try:
        reader = csv.DictReader(io.StringIO(data.decode("utf-8-sig"), newline=""), strict=True)
        columns = reader.fieldnames
        if not columns or any(not c.strip() for c in columns) or len(columns) != len(set(columns)):
            raise InvalidData(f"{label}: CSV requires nonempty, unique headers")
        missing = [c for c in REQUIRED_COLUMNS if c not in columns]
        if missing:
            raise InvalidData(f"{label}: missing required columns: {', '.join(missing)}")
        rows, seen, references = [], set(), set()
        for index, row in enumerate(reader, 1):
            if None in row or any(v is None for v in row.values()):
                raise InvalidData(f"{label}: CSV data record {index}: field count differs from header")
            identifier = positive_identifier(row["No."], f"{label}: record {index} No.")
            reference = positive_identifier(row["Reference"], f"{label}: record {index} Reference")
            if identifier in seen:
                raise InvalidData(f"{label}: duplicate No. identifier {identifier}")
            seen.add(identifier)
            references.add(reference)
            rows.append({
                "citrine_no": identifier,
                "cra_potential": {key: row[column] for key, column in TARGET_COLUMNS.items()},
                "fields": row,
            })
        if len(references) > 1:
            raise InvalidData(f"{label}: expected a paper-specific CSV with one Reference; found {sorted(references)}")
        return columns, rows, next(iter(references), None)
    except (UnicodeError, csv.Error) as error:
        raise InvalidData(f"{label}: invalid UTF-8 CSV: {error}") from error


@dataclass
class PreparedInputs:
    paper_name: str
    reference_number: int
    inputs: InputFiles
    registry_document: dict
    registry: ObservationRegistry
    columns: list[str]
    rows: list[dict]
    warnings: list[str]

    def as_document(self):
        return {
            "paper_name": self.paper_name, "reference_number": self.reference_number,
            "inputs": self.inputs.model_dump(mode="json"),
            "registry": self.registry_document, "csv_columns": self.columns, "cra_rows": self.rows,
            "input_warnings": self.warnings,
        }


def prepare_inputs(pdf: Path, csv_path: Path, registry_path: Path) -> PreparedInputs:
    for path, extension in ((pdf, ".pdf"), (csv_path, ".csv"), (registry_path, ".json")):
        if path.suffix.lower() != extension:
            raise InvalidData(f"Expected a {extension} input: {path}")
    registry_bytes = read_bytes(registry_path)
    document = parse_json(registry_bytes, str(registry_path))
    registry = validate_model(document, ObservationRegistry, "observation_registry.schema.json")
    csv_bytes = read_bytes(csv_path)
    columns, rows, csv_reference = parse_csv(csv_bytes, str(csv_path))
    references = []
    for label, reference in (("registry reference_number", registry.reference_number), ("CSV Reference", csv_reference)):
        if reference is not None:
            references.append((label, reference))
    filename_patterns = [
        ("PDF filename", pdf.stem, r"^(\d+)(?=\D|$)"),
        ("registry paper_name", Path(registry.paper_name).stem, r"^(\d+)(?=\D|$)"),
        ("CSV filename", csv_path.stem, r"_(\d+)$"),
        ("registry filename", registry_path.stem, r"^paper_(\d+)(?=_|$)"),
    ]
    for label, stem, pattern in filename_patterns:
        match = re.search(pattern, stem)
        if match:
            references.append((label, positive_identifier(match.group(1), label)))
    if not references:
        raise InvalidData("Cannot resolve a positive paper reference from the supplied inputs")
    if len({number for _, number in references}) != 1:
        raise InvalidData("Reference conflict: " + "; ".join(f"{label}={value}" for label, value in references))
    pdf_bytes = read_bytes(pdf)  # Fingerprint only; scientific/visual PDF reading belongs to the agent.
    warnings = []
    if registry.paper_name != pdf.name:
        warnings.append(
            f"Registry paper_name {registry.paper_name!r} differs from supplied PDF {pdf.name!r}; "
            "verify visually that this is a renamed copy of the same paper before matching."
        )
    return PreparedInputs(
        paper_name=pdf.name, reference_number=references[0][1],
        inputs=InputFiles(pdf=fingerprint(pdf, pdf_bytes), csv=fingerprint(csv_path, csv_bytes),
                          registry=fingerprint(registry_path, registry_bytes)),
        registry_document=document, registry=registry, columns=columns, rows=rows, warnings=warnings,
    )


def validate_alignment(document, prepared: PreparedInputs) -> ObservationAlignment:
    result = validate_model(document, ObservationAlignment, "observation_alignment.schema.json")
    errors = []
    if result.inputs != prepared.inputs:
        errors.append("/inputs: filenames/SHA-256 fingerprints do not match the exact supplied files")
    if result.paper_name != prepared.paper_name:
        errors.append("/paper_name: must equal the supplied PDF filename")
    if result.reference_number != prepared.reference_number:
        errors.append("/reference_number: differs from supplied inputs")
    expected_ids = [o.observation_id for o in prepared.registry.observations]
    if [o.observation_id for o in result.observations] != expected_ids:
        errors.append("/observations: IDs must cover the supplied registry exactly once, in input order")
    sources = {o.observation_id: o for o in prepared.registry.observations}
    rows = {r["citrine_no"]: r for r in prepared.rows}
    supported = set()
    for index, observation in enumerate(result.observations):
        source = sources.get(observation.observation_id)
        if source is None:
            continue
        prefix = f"/observations/{index}"
        if source.extraction_status == "failed" and observation.status != "not_assessed":
            errors.append(f"{prefix}/status: failed registry observations must remain not_assessed")
        for group in ("matches", "candidates"):
            for position, link in enumerate(getattr(observation, group)):
                pointer = f"{prefix}/{group}/{position}"
                if group == "matches":
                    supported.add(link.citrine_no)
                row = rows.get(link.citrine_no)
                if row is None:
                    errors.append(f"{pointer}/citrine_no: unknown CSV No. {link.citrine_no}")
                else:
                    if link.cra_potential.model_dump() != row["cra_potential"]:
                        errors.append(f"{pointer}/cra_potential: must preserve original avg/min/max cell strings")
                    for e_index, evidence in enumerate(link.evidence):
                        if evidence.field not in row["fields"]:
                            errors.append(f"{pointer}/evidence/{e_index}/field: unknown CSV column {evidence.field!r}")
                        elif evidence.cra_value != row["fields"][evidence.field]:
                            errors.append(f"{pointer}/evidence/{e_index}/cra_value: differs from original CSV cell")
                for location_index in link.location_indices:
                    if location_index >= len(source.locations):
                        errors.append(f"{pointer}/location_indices: {location_index} is outside this observation's locations")
                    elif source.locations[location_index].pdf_page not in result.inspected_pdf_pages:
                        errors.append(f"{pointer}/location_indices: linked PDF page must be listed as visually inspected")
    expected_unlinked = [r["citrine_no"] for r in prepared.rows if r["citrine_no"] not in supported]
    if result.unlinked_citrine_nos != expected_unlinked:
        errors.append("/unlinked_citrine_nos: must be the unsupported CSV No. complement in original CSV order; candidates do not assign rows")
    if errors:
        raise InvalidData("\n".join(errors))
    return result


def shared_rows(alignment: ObservationAlignment):
    groups = {}
    for observation in alignment.observations:
        for link in observation.matches:
            groups.setdefault(link.citrine_no, []).append(observation.observation_id)
    return {identifier: ids for identifier, ids in groups.items() if len(ids) > 1}
