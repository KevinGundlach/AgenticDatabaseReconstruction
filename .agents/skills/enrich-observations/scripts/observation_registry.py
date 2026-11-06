"""Self-contained Pydantic classes for a paper's observation registry.

Generate the bundled JSON Schema with ObservationRegistry.model_json_schema().
Pydantic additionally checks numerical bound ordering, primary-location indices
and measurement equality, and observation-ID uniqueness. Status/note consistency
is enforced by both JSON Schema and Pydantic. Dump with
model_dump(mode="json", exclude_unset=True) to omit unused measurement subfields.
"""

from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class RegistryModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, allow_inf_nan=False)


class Measurement(RegistryModel):
    """Reported central value or bounds, preserving original units."""

    model_config = ConfigDict(
        json_schema_extra={
            "anyOf": [
                {"required": [name], "properties": {name: {"type": "number"}}}
                for name in ("value", "min", "max")
            ],
            "if": {
                "required": ["plus_minus"],
                "properties": {"plus_minus": {"type": "number"}},
            },
            "then": {
                "required": ["value"],
                "properties": {"value": {"type": "number"}},
            },
        }
    )

    value: float | None = Field(default=None, description="Reported single or central value; null or omitted if unavailable.")
    min: float | None = Field(default=None, description="Reported lower endpoint or bound; null or omitted if unavailable.")
    max: float | None = Field(default=None, description="Reported upper endpoint or bound; null or omitted if unavailable.")
    unit: str = Field(
        default="",
        description=(
            "Original reported unit. Include the stated electrode reference for potentials, "
            "e.g. 'mV (SCE)' or 'V (Ag/AgCl, saturated KCl)'. Use an empty string or omit "
            "for dimensionless quantities or unavailable units. Do not infer units or electrode details."
        ),
    )
    plus_minus: float | None = Field(
        default=None, ge=0,
        description=(
            "Reported symmetric uncertainty in the same unit as value; requires a numerical value. "
            "Do not infer from bounds or substitute relative percent uncertainty. Null or omitted if unavailable."
        ),
    )

    @model_validator(mode="after")
    def check_values(self) -> Self:
        if all(v is None for v in (self.value, self.min, self.max)):
            raise ValueError("A measurement needs at least one numerical value, min, or max")
        if self.plus_minus is not None and self.value is None:
            raise ValueError("plus_minus requires a numerical value")
        if self.min is not None and self.max is not None and self.min > self.max:
            raise ValueError("min must not exceed max")
        if self.value is not None:
            if self.min is not None and self.value < self.min:
                raise ValueError("value must not be below min")
            if self.max is not None and self.value > self.max:
                raise ValueError("value must not exceed max")
        return self


class NamedValue(RegistryModel):
    """A condition or coordinate used to identify a particular outcome."""

    name: str = Field(description="Paper's label for this coordinate or condition, e.g. Nb content, pH, or test method.")
    value: str | Measurement | None = Field(
        description=(
            "Reported text/categorical value, a measurement for a numerical value (including "
            "dimensionless numbers), or null if unreadable/unavailable. Preserve original terminology and units."
        )
    )


class Location(RegistryModel):
    pdf_page: int = Field(ge=1, description="One-based page number in the supplied PDF, not the printed page number.")
    printed_page: str = Field(description="Printed page label, including prefixes if present; empty string if unavailable.")
    reading_method: Literal["transcribed", "digitized"] = Field(
        description="Transcribed for printed numerical values; digitized when a numerical value or endpoint is read graphically."
    )
    pitting_potential: Measurement | None = Field(
        description=(
            "Pitting outcome as read at this location, in its original units/reference. "
            "Null if no numerical value or bound can be recovered. Never insert a converted value."
        )
    )


class TableLocation(Location):
    kind: Literal["table"]
    table_label: str = Field(description="Printed table identifier; empty string if absent or unreadable.")
    row_label: str = Field(description="Row/sample label or concise distinguishing row description; empty string if unavailable.")
    column_label: str = Field(description="Full result-column label, including scoped headers, units, and method distinction when stated.")
    conditions: list[NamedValue] = Field(description="Additional reported conditions needed to identify the cell; [] if none extracted.")


class PlotLocation(Location):
    kind: Literal["plot"]
    figure_label: str = Field(description="Printed figure identifier; empty string if absent or unreadable.")
    panel_label: str = Field(description="Panel label such as (b); empty string for an unlabeled or single-panel figure.")
    series_label: str = Field(description="Legend/series label and distinguishing symbol, e.g. Alloy B, open circles; empty string if unavailable.")
    coordinates: list[NamedValue] = Field(
        description="Independent-variable coordinates identifying the point, in original units; [] if none can be recovered."
    )


class TextLocation(Location):
    kind: Literal["text"]
    section_heading: str = Field(description="Section heading containing the outcome; empty string if absent or unreadable.")
    text_anchor: str = Field(description="Short exact identifying quotation, sufficient to find the passage; empty string if unreadable.")


ObservationLocation = Annotated[
    TableLocation | PlotLocation | TextLocation,
    Field(discriminator="kind"),
]


ResultType = Literal[
    "reported_experimental", "interpolated", "calculated", "cited", "reference_value", "unclear"
]
ExtractionStatus = Literal["complete", "partial", "failed"]


class Observation(RegistryModel):
    model_config = ConfigDict(
        json_schema_extra={
            "allOf": [
                {
                    "if": {
                        "required": ["extraction_status"],
                        "properties": {"extraction_status": {"const": "complete"}},
                    },
                    "then": {
                        "properties": {
                            "pitting_potential": {"not": {"type": "null"}},
                            "failure_notes": {"const": ""},
                        },
                    },
                },
                {
                    "if": {
                        "required": ["extraction_status"],
                        "properties": {"extraction_status": {"enum": ["partial", "failed"]}},
                    },
                    "then": {"properties": {"failure_notes": {"pattern": r"\S"}}},
                },
            ]
        }
    )

    observation_id: str = Field(
        pattern=r"^obs_[0-9]{3,}$",
        description="Registry-scoped bookkeeping identifier, e.g. obs_001; preserve during later edits and enrichment.",
    )
    result_type: ResultType = Field(
        description=(
            "Origin of the potential selected from primary_location: reported_experimental for the "
            "authors' experiments (including routine summaries), interpolated or calculated when "
            "explicitly derived, cited when attributed to another source, reference_value when "
            "explicitly standard/conventional, or unclear when origin is not established. "
            "Digitization is a reading method, not interpolation. Scientific uncertainty alone "
            "does not change a known experimental origin."
        )
    )
    extraction_status: ExtractionStatus = Field(
        description=(
            "complete: recovered as far as the paper supplies, with a non-null potential and empty "
            "failure_notes; partial: a recovery problem remains but useful input survives; failed: "
            "recovery is insufficient for automatic downstream processing. partial/failed require "
            "nonblank failure_notes. Default routing continues complete/partial and retains failed "
            "for review; it does not certify scientific validity or benchmark suitability."
        )
    )
    pitting_potential: Measurement | None = Field(
        description="Exact copy of the primary location's measurement, without conversion or averaging; null when that reading is null."
    )
    sample_label: str = Field(description="Author-supplied sample/alloy identifier; empty string if unavailable. Do not invent one.")
    association_notes: str = Field(
        description="Brief paper-derived clue linking this outcome to its experimental context; empty string if unnecessary. Not a full methods summary."
    )
    result_note: str = Field(
        description=(
            "Scientific qualifications, provenance or measurement-criterion uncertainty, source "
            "disagreements, and unresolved duplicate relationships. Include statistical meanings, "
            "inequalities, or reported no-pitting limits when relevant. Empty string if unnecessary."
        )
    )
    failure_notes: str = Field(
        description=(
            "Information the extractor could not recover despite the paper appearing to provide it, "
            "e.g. illegible digits or unreadable legend assignments. Empty for complete observations; "
            "nonblank for partial/failed. Source omissions, scientific uncertainty, and source "
            "conflicts belong in result_note and do not alone make extraction incomplete."
        )
    )
    primary_location: int = Field(ge=0, description="Zero-based index of the preferred reading in locations.")
    locations: list[ObservationLocation] = Field(
        min_length=1,
        description="Specific paper locations reporting this same outcome; retain each location's original reading and units.",
    )

    @model_validator(mode="after")
    def check_primary_location(self) -> Self:
        if self.primary_location >= len(self.locations):
            raise ValueError("primary_location must index an entry in locations")
        if self.pitting_potential != self.locations[self.primary_location].pitting_potential:
            raise ValueError("pitting_potential must equal the primary location's measurement without conversion or averaging")
        return self

    @model_validator(mode="after")
    def check_extraction_status(self) -> Self:
        if self.extraction_status == "complete":
            if self.pitting_potential is None:
                raise ValueError("complete extraction_status requires a non-null pitting_potential")
            if self.failure_notes != "":
                raise ValueError("complete extraction_status requires empty failure_notes")
        elif not self.failure_notes.strip():
            raise ValueError("partial/failed extraction_status requires nonblank failure_notes")
        return self


class ObservationRegistry(RegistryModel):
    """Condition-specific numerical outcomes and paper-derived anchors from one paper."""

    model_config = ConfigDict(
        title="Paper observation registry",
        json_schema_extra={
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$comment": (
                'Use "" for unavailable text, [] for empty collections, and null for unavailable '
                "measurements or condition values. Neither implies zero or explicit absence. "
                "Use a strict JSON parser rejecting duplicate keys, NaN, and Infinity. Pydantic "
                "additionally validates bounds, primary-location consistency, and unique observation IDs."
            ),
        },
    )

    schema_version: Literal["1.1"]
    paper_name: str = Field(pattern=r"^[^/\\]+\.[pP][dD][fF]$", description="Filename of the supplied paper PDF, including extension and excluding directory.")
    reference_number: int | None = Field(ge=1, description="Supplied literature reference or leading positive filename number; null if unavailable.")
    observations: list[Observation] = Field(
        description=(
            "One record per identifiable, condition-specific numerical pitting-related value or bound, "
            "including incomplete recovery of such occurrences. Consolidate only supported equivalent "
            "presentations; broad screening ranges and purely qualitative statements belong in the report."
        )
    )

    @model_validator(mode="after")
    def check_observation_ids(self) -> Self:
        seen = set()
        for observation in self.observations:
            if observation.observation_id in seen:
                raise ValueError(f"Duplicate observation_id: {observation.observation_id}")
            seen.add(observation.observation_id)
        return self
