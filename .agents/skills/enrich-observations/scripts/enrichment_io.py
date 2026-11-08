"""Read-only enrichment preparation and validation; never interprets PDF contents."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
import re

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError
from pydantic import ValidationError

from observation_enrichment import InputFile, InputFiles, ObservationEnrichment
from observation_registry import ObservationRegistry


REFERENCES = Path(__file__).resolve().parents[1] / "references"


class InvalidData(ValueError):
    """Invalid supplied data; CLI exit 1."""


class SetupError(RuntimeError):
    """Missing/unreadable files, dependencies or inconsistent bundled resources; exit 2."""


def read_bytes(path: Path):
    try:
        return path.read_bytes()
    except OSError as error:
        raise SetupError(f"Cannot read {path}: {error}") from error


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


def checked_schema(model, name):
    try:
        schema = load_json(REFERENCES / name)
        Draft202012Validator.check_schema(schema)
        if schema != model.model_json_schema():
            raise SetupError(f"Bundled {name} differs from its Pydantic model")
        return schema
    except (InvalidData, SchemaError) as error:
        raise SetupError(f"Cannot use bundled {name}: {error}") from error


def validate_model(document, model, name):
    schema = checked_schema(model, name)
    expected = schema["properties"]["schema_version"]["const"]
    if isinstance(document, dict) and "schema_version" in document and document["schema_version"] != expected:
        kind = "registry" if model is ObservationRegistry else "enrichment"
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


def fingerprint(path: Path, data: bytes):
    return InputFile(filename=path.name, sha256=hashlib.sha256(data).hexdigest())


@dataclass
class PreparedInputs:
    paper_name: str
    reference_number: int | None
    inputs: InputFiles
    registry_document: dict
    registry: ObservationRegistry
    warnings: list[str]

    @property
    def eligible_ids(self):
        return [o.observation_id for o in self.registry.observations if o.extraction_status in ("complete", "partial")]

    @property
    def skipped_failed_ids(self):
        return [o.observation_id for o in self.registry.observations if o.extraction_status == "failed"]

    def as_document(self):
        return {
            "paper_name": self.paper_name,
            "reference_number": self.reference_number,
            "inputs": self.inputs.model_dump(mode="json"),
            "registry": self.registry_document,
            "eligible_observation_ids": self.eligible_ids,
            "skipped_failed_observation_ids": self.skipped_failed_ids,
            "input_warnings": self.warnings,
        }


def prepare_inputs(pdf: Path, registry_path: Path):
    for path, extension in ((pdf, ".pdf"), (registry_path, ".json")):
        if path.suffix.lower() != extension:
            raise InvalidData(f"Expected a {extension} input: {path}")
    registry_bytes = read_bytes(registry_path)
    document = parse_json(registry_bytes, str(registry_path))
    registry = validate_model(document, ObservationRegistry, "observation_registry.schema.json")
    references = []
    if registry.reference_number is not None:
        references.append(("registry reference_number", registry.reference_number))
    for label, stem, pattern in [
        ("PDF filename", pdf.stem, r"^(\d+)(?=\D|$)"),
        ("registry paper_name", Path(registry.paper_name).stem, r"^(\d+)(?=\D|$)"),
        ("registry filename", registry_path.stem, r"^paper_(\d+)(?=_|$)"),
    ]:
        match = re.search(pattern, stem)
        if match:
            number = int(match.group(1))
            if number < 1:
                raise InvalidData(f"{label}: reference must be positive")
            references.append((label, number))
    if len({value for _, value in references}) > 1:
        raise InvalidData("Reference conflict: " + "; ".join(f"{label}={value}" for label, value in references))
    pdf_bytes = read_bytes(pdf)  # Fingerprinting only, not a claim of PDF validity or visual access.
    warnings = []
    if registry.paper_name != pdf.name:
        warnings.append(
            f"Registry paper_name {registry.paper_name!r} differs from supplied PDF {pdf.name!r}; "
            "verify visually that it is the same paper before enriching."
        )
    return PreparedInputs(
        paper_name=pdf.name,
        reference_number=references[0][1] if references else None,
        inputs=InputFiles(pdf=fingerprint(pdf, pdf_bytes), registry=fingerprint(registry_path, registry_bytes)),
        registry_document=document, registry=registry, warnings=warnings,
    )


def validate_enrichment(document, prepared: PreparedInputs):
    result = validate_model(document, ObservationEnrichment, "observation_enrichment.schema.json")
    errors = []
    if result.inputs != prepared.inputs:
        errors.append("/inputs: filenames/SHA-256 fingerprints do not match the exact supplied files")
    if result.paper_name != prepared.paper_name:
        errors.append("/paper_name: must equal the supplied PDF filename")
    if result.reference_number != prepared.reference_number:
        errors.append("/reference_number: differs from the resolved input reference")
    if [row.observation_id for row in result.experiments] != prepared.eligible_ids:
        errors.append("/experiments: must cover complete/partial input IDs exactly once, in input order; failed IDs must be skipped")
    sources = {o["observation_id"]: o for o in prepared.registry_document["observations"]}
    for index, row in enumerate(document["experiments"]):
        source = sources.get(row["observation_id"])
        if source is not None and row["pitting_potential"] != source["pitting_potential"]:
            errors.append(
                f"/experiments/{index}/pitting_potential: must equal the raw registry observation-level "
                "measurement, including nulls, units, bounds, uncertainty and optional-field presence; "
                "do not substitute a secondary reading or serialize added defaults"
            )
    if errors:
        raise InvalidData("\n".join(errors))
    return result
