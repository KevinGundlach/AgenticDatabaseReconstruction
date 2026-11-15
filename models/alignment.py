"""Strict output models for registry-to-CRA alignment, version 1.0.

Cross-input checks live in matching_io.py. Regenerate the bundled output schema
with ObservationAlignment.model_json_schema(). All fields are required.
"""

from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


Nonblank = Annotated[str, Field(pattern=r"\S")]
PositiveInt = Annotated[int, Field(ge=1)]
LocationIndex = Annotated[int, Field(ge=0)]
MatchStatus = Literal["matched", "ambiguous", "unmatched", "not_assessed"]
PotentialAgreement = Literal["exact", "within_precision", "discrepant", "not_comparable"]


class AlignmentModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, allow_inf_nan=False)


class InputFile(AlignmentModel):
    filename: str = Field(pattern=r"^[^/\\]+$", description="Input basename, without directories.")
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$", description="SHA-256 of the original file bytes, before decoding.")


class InputFiles(AlignmentModel):
    pdf: InputFile
    csv: InputFile
    registry: InputFile


class CRAPotential(AlignmentModel):
    avg: str = Field(description="Exact Avg Epit mV (SCE) cell string, including missing markers or qualitative text.")
    min: str = Field(description="Exact Min Epit mV (SCE) cell string.")
    max: str = Field(description="Exact Max Epit mV (SCE) cell string.")


class ComparisonEvidence(AlignmentModel):
    field: Nonblank = Field(description="Exact CSV column header for this comparison, e.g. Nb or Avg Epit mV (SCE).")
    paper_value: Nonblank = Field(description="Paper value and original units/meaning; explicitly state unavailable information.")
    cra_value: str = Field(description="Exact original CSV cell string for field; may be empty.")
    comparison: Nonblank = Field(description="Association, agreement or discrepancy; show conversion arithmetic and assumptions when used.")


class CRALink(AlignmentModel):
    citrine_no: PositiveInt = Field(description="Original positive No. identifier, never CSV line position.")
    location_indices: list[LocationIndex] = Field(
        min_length=1, json_schema_extra={"uniqueItems": True},
        description="Zero-based indices into the supplied observation's locations used to support this link.",
    )
    cra_potential: CRAPotential
    potential_agreement: PotentialAgreement = Field(description="Numerical agreement, separately from the decision to link identities.")
    evidence: list[ComparisonEvidence] = Field(min_length=1, description="Only decisive paired values, including non-potential association evidence.")
    notes: Nonblank = Field(description="Identity rationale, limitations and any shared-row, repeated-presentation or summary-member relationship.")

    @model_validator(mode="after")
    def unique_locations(self) -> Self:
        if len(set(self.location_indices)) != len(self.location_indices):
            raise ValueError("location_indices must be unique")
        return self


def _status_rule(status, matches, candidates):
    properties = {"matches": matches, "candidates": candidates}
    if status != "matched":
        properties["notes"] = {"pattern": r"\S"}
    return {
        "if": {"required": ["status"], "properties": {"status": {"const": status}}},
        "then": {"properties": properties},
    }


class ObservationMatch(AlignmentModel):
    model_config = ConfigDict(json_schema_extra={"allOf": [
        _status_rule("matched", {"minItems": 1}, {}),
        _status_rule("ambiguous", {"maxItems": 0}, {"minItems": 1}),
        _status_rule("unmatched", {"maxItems": 0}, {"maxItems": 0}),
        _status_rule("not_assessed", {"maxItems": 0}, {"maxItems": 0}),
    ]})

    observation_id: str = Field(pattern=r"^obs_[0-9]{3,}$")
    status: MatchStatus
    matches: list[CRALink] = Field(description="Supported assignments; many-to-many links are allowed.")
    candidates: list[CRALink] = Field(description="Unresolved alternatives, excluded from default joins.")
    notes: str = Field(description="Concise explanation; nonblank unless status is matched.")

    @model_validator(mode="after")
    def check_decisions(self) -> Self:
        if self.status == "matched" and not self.matches:
            raise ValueError("matched requires at least one supported link")
        if self.status != "matched" and self.matches:
            raise ValueError("Only matched observations may have supported links")
        if self.status == "ambiguous" and not self.candidates:
            raise ValueError("ambiguous requires at least one candidate")
        if self.status in ("unmatched", "not_assessed") and self.candidates:
            raise ValueError("unmatched/not_assessed cannot contain candidates")
        if self.status != "matched" and not self.notes.strip():
            raise ValueError("Non-matched observations require explanatory notes")
        identifiers = [link.citrine_no for link in self.matches + self.candidates]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("Duplicate citrine_no within an observation's matches/candidates")
        return self


class ObservationAlignment(AlignmentModel):
    model_config = ConfigDict(
        title="Observation-to-CRA alignment",
        json_schema_extra={
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$comment": (
                "Use strict JSON: reject duplicate keys, NaN and Infinity. All fields are required. "
                "The bundled validator also checks input fingerprints, IDs/order, source cell strings, "
                "location indices and the unlinked-row complement. Scientific fidelity is not validated."
            ),
        },
    )

    schema_version: Literal["1.0"]
    paper_name: str = Field(pattern=r"^[^/\\]+\.[pP][dD][fF]$")
    reference_number: PositiveInt
    inputs: InputFiles
    inspected_pdf_pages: list[PositiveInt] = Field(
        json_schema_extra={"uniqueItems": True},
        description="One-based supplied-PDF pages actually viewed, not merely rendered or text-searched.",
    )
    coverage_notes: str = Field(description="Input-scoped coverage and access limitations, including actual errors; empty if unnecessary.")
    shared_qualifications: list[Nonblank] = Field(description="Concise shared scientific/conversion/duplicate notes; [] if none.")
    observations: list[ObservationMatch] = Field(description="Exactly one entry per supplied registry observation, in the same order.")
    unlinked_citrine_nos: list[PositiveInt] = Field(
        json_schema_extra={"uniqueItems": True},
        description="CSV No. identifiers without a supported link, in CSV order; candidate-only rows remain unlinked.",
    )

    @model_validator(mode="after")
    def unique_bookkeeping(self) -> Self:
        identifiers = [item.observation_id for item in self.observations]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("Duplicate observation_id in alignment")
        for name in ("inspected_pdf_pages", "unlinked_citrine_nos"):
            values = getattr(self, name)
            if len(values) != len(set(values)):
                raise ValueError(f"{name} must be unique")
        return self
