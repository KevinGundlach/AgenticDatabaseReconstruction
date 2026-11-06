"""Registry-anchored enrichment v1.0; all scientific fields reuse local models.

Generate the output schema with ObservationEnrichment.model_json_schema().
Input-dependent checks (IDs, fingerprints, raw potential preservation) live in
enrichment_io.py. No imports from project code or another skill are needed.
"""

from typing import Self

from pydantic import ConfigDict, Field, model_validator

from paper_extraction import Experiment, ExtractionModel, PaperExtraction


class InputFile(ExtractionModel):
    filename: str = Field(pattern=r"^[^/\\]+$", description="Input basename, without directories.")
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$", description="SHA-256 of the exact original file bytes.")


class InputFiles(ExtractionModel):
    pdf: InputFile
    registry: InputFile


class EnrichedExperiment(Experiment):
    observation_id: str = Field(
        pattern=r"^obs_[0-9]{3,}$",
        description="Unchanged registry-scoped ID; not an author-supplied experiment identifier.",
    )


class ObservationEnrichment(PaperExtraction):
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
