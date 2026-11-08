"""Self-contained Pydantic models for registry-anchored enrichment v1.0.

Generate the output schema with ObservationEnrichment.model_json_schema().
Input-dependent checks (IDs, fingerprints, raw potential preservation) live in
enrichment_io.py. No imports from project code or another skill are needed.
"""

from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ExtractionModel(BaseModel):
    """Reject extra fields, implicit type coercion, and non-finite numbers."""

    model_config = ConfigDict(extra="forbid", strict=True, allow_inf_nan=False)


class Measurement(ExtractionModel):
    """Reported value or bounds, optionally with units and symmetric uncertainty."""

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

    value: float | None = Field(
        default=None, description="Single or central reported value; null or omitted if unavailable."
    )
    min: float | None = Field(
        default=None, description="Reported lower endpoint or lower bound; null or omitted if unavailable."
    )
    max: float | None = Field(
        default=None, description="Reported upper endpoint or upper bound; null or omitted if unavailable."
    )
    unit: str = Field(
        default="",
        description=(
            "Original reported unit, e.g. wt%, at%, mol/L, or degC. Include the reported "
            "electrode reference for potentials, e.g. 'mV (SCE)' or 'V (Ag/AgCl, saturated KCl)'. "
            "Use an empty string or omit for dimensionless quantities or unavailable units. "
            "Do not infer units or electrode details."
        ),
    )
    plus_minus: float | None = Field(
        default=None,
        ge=0,
        description=(
            "Magnitude of reported symmetric uncertainty, in the same unit as value. "
            "Requires a numerical value. Do not infer from minima and maxima. "
            "Null or omitted if unavailable."
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


MaterialClass = Literal["", "Fe Alloy", "Al Alloy", "HEA", "NiCrMo Alloy", "Other"]


class AlloyComponent(ExtractionModel):
    element_symbol: str = Field(description="Reported chemical element symbol, e.g. Fe, Cr, or Ni.")
    amount: Measurement | Literal["balance"] | None = Field(
        description=(
            "Reported amount with its original basis, e.g. wt% or at%. Use 'balance' "
            "only when explicitly reported. Use null if unavailable; do not substitute zero."
        )
    )


class Alloy(ExtractionModel):
    preparation: str = Field(
        description=(
            "Reported manufacturing, thermal treatment, mechanical processing, and specimen "
            "surface preparation applicable to the tested material. Preserve ordering and "
            "conditions in prose. Use an empty string if unavailable; retain explicit statements "
            "such as 'No heat treatment was applied'."
        )
    )
    composition: list[AlloyComponent] = Field(
        description=(
            "Reported composition of the tested alloy. Include explicitly reported elements only. "
            "Use [] if no composition is extracted; this does not imply a pure material."
        )
    )
    microstructure: str = Field(
        description=(
            "Reported microstructure in the tested condition, including phases, grain size, "
            "precipitates, and inclusions when stated. Do not substitute general explanations "
            "or post-corrosion morphology. Use an empty string if unavailable."
        )
    )
    material_class: MaterialClass = Field(
        description=(
            "Citrine-style category under the project's classification rules. Use an empty string "
            "if unresolved. Other is a positive classification, not a missing-value marker."
        )
    )


class SolutionComponent(ExtractionModel):
    solute: str = Field(description="Reported solute name or formula, e.g. NaCl or H2SO4.")
    amount: Measurement | None = Field(
        description=(
            "Reported solute amount or concentration with original units. Preserve distinctions "
            "such as mol/L, mol/kg, wt%, and volume percent. Use null if unavailable."
        )
    )


class TestSolution(ExtractionModel):
    preparation: str = Field(
        description=(
            "Reported solution preparation and conditioning, including mixing, gas identity, "
            "deaeration/aeration duration, pH adjustment, and whether gas flow continued during "
            "testing. Deaeration is not itself a solute. Use an empty string if unavailable."
        )
    )
    solvent: str = Field(
        description=(
            "Reported solvent or solvent mixture. Use an empty string if unavailable; "
            "do not assume water."
        )
    )
    composition: list[SolutionComponent] = Field(
        description=(
            "Reported solutes and their amounts. Use [] if unavailable; this does not establish "
            "that no solutes were present."
        )
    )
    ph: float | Measurement | None = Field(
        description=(
            "Reported pH as a number or a measurement object for a range or uncertainty. "
            "Use null if unavailable. Do not calculate missing pH or restrict it to 0-14."
        )
    )
    chloride_concentration: Measurement | None = Field(
        description=(
            "Explicitly reported chloride-ion concentration, including values calculated and "
            "then reported by the authors. Use null if unavailable. Do not calculate from salt "
            "composition during extraction or substitute typical seawater values."
        )
    )


class TestMethod(ExtractionModel):
    test_types: list[str] = Field(
        description=(
            "Applicable method labels, e.g. potentiodynamic polarization, potentiostatic "
            "polarization, or cyclic polarization. Several may apply. Use [] if unavailable; "
            "describe their order in procedure_description."
        )
    )
    procedure_description: str = Field(
        description=(
            "Reported testing sequence and conditions relevant to this outcome, including "
            "pretreatment, stabilization, potential ranges, changing scan rates, holds, and "
            "reversals. Use an empty string if unavailable."
        )
    )
    scan_rate: Measurement | None = Field(
        description=(
            "One reported scan rate adequately describing the scan relevant to this result. "
            "For multiple rates across protocol segments, use null and describe the schedule "
            "in procedure_description. 'Steady state' is not a numerical scan rate."
        )
    )
    potential_step: Measurement | None = Field(
        description=(
            "Reported potential increment for stepped testing, e.g. 20 mV; not a scan rate. "
            "Use null if unavailable, inapplicable, or not adequately represented by one value."
        )
    )
    step_hold_duration: Measurement | None = Field(
        description=(
            "Reported duration of each potential step. Use null if unavailable or inapplicable. "
            "Describe varying schedules in procedure_description rather than forcing one duration."
        )
    )
    pitting_criterion: str = Field(
        description=(
            "Reported criterion for identifying pitting, e.g. a current-density threshold, "
            "sustained current increase, or visual confirmation. Use an empty string if unavailable."
        )
    )


class InputFile(ExtractionModel):
    filename: str = Field(pattern=r"^[^/\\]+$", description="Input basename, without directories.")
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$", description="SHA-256 of the exact original file bytes.")


class InputFiles(ExtractionModel):
    pdf: InputFile
    registry: InputFile


class EnrichedExperiment(ExtractionModel):
    alloy: Alloy
    test_temperature: Measurement | None = Field(
        description=(
            "Reported electrolyte temperature during testing; null if unavailable. Do not "
            "substitute preparation temperature or assume a number for 'room temperature'. "
            "Retain unresolved wording in procedure_description."
        )
    )
    test_solution: TestSolution
    test_method: TestMethod
    pitting_potential: Measurement | None = Field(
        description=(
            "Reported pitting potential in original units including the reported reference "
            "electrode. Use null if no numerical result can be represented. Do not substitute "
            "corrosion potential, repassivation potential, or non-pitting breakdown. Preserve "
            "unsupported inequality/statistical distinctions in result_note."
        )
    )
    result_note: str = Field(
        description=(
            "Brief clarification, e.g. no pitting observed, a strict inequality, experimental "
            "limit, statistical meaning, or conflicting values. Use an empty string if unnecessary."
        )
    )
    failure_notes: str = Field(
        description=(
            "Extraction failures that make this row unreliable or incomplete, e.g. a pitting "
            "potential cannot be linked to its alloy, an ambiguous condition assignment, or "
            "an unreadable reported value. Identify the affected field and unresolved problem. "
            "Use an empty string normally. Ordinary unreported information is not a failure; "
            "scientific qualifications belong in result_note."
        )
    )
    observation_id: str = Field(
        pattern=r"^obs_[0-9]{3,}$",
        description="Unchanged registry-scoped ID; not an author-supplied experiment identifier.",
    )


class ObservationEnrichment(ExtractionModel):
    model_config = ConfigDict(
        title="Registry-anchored observation enrichment",
        json_schema_extra={
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$comment": (
                'Use "" for unavailable text, [] for collections, and null for unavailable measurements. '
                "All fields except measurement subfields are required. Reject duplicate keys, NaN and "
                "Infinity. The bundled validator also checks exact input fingerprints, eligible-ID "
                "coverage/order, and unchanged raw pitting_potential objects, including omitted fields. "
                "Validation does not certify scientific fidelity or visual coverage."
            ),
        },
    )

    schema_version: Literal["1.0"] = Field(description="Version of this extraction format.")
    paper_name: str = Field(description="Filename of the paper processed.")
    reference_number: int | None = Field(ge=1, description="Reference number of the paper.")
    experiments: list[EnrichedExperiment] = Field(
        description=(
            "Exactly one record for each supplied complete or partial registry observation, in input "
            "order. Skip failed observations; preserve separate IDs even for possible duplicates. "
            "Copy each anchored pitting_potential unchanged. [] means no eligible supplied IDs."
        ),
    )
    inputs: InputFiles

    @model_validator(mode="after")
    def unique_observation_ids(self) -> Self:
        identifiers = [row.observation_id for row in self.experiments]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("Duplicate observation_id in experiments")
        return self
