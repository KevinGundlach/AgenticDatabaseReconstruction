# Project context for agents

## Research goal and current focus

This is the main repository for the master's thesis **Automated Ontology Construction for Explainable Feature Discovery in Alloy Corrosion Resistance**. The broad aim is to extract corrosion experiments from literature, learn useful structure/features, and eventually study how material and environmental parameters affect pitting resistance.

The immediate task is narrower: extract pitting-potential outcomes and their experimental context, align them with the manually curated Citrine corrosion-resistant alloy (CRA) dataset, and benchmark context recovery. Prioritize concrete, inspectable results over redesigning the ontology or building a general framework. Ontology learning, systematic benchmark scoring and predictive modelling are later work, not completed features.

All three active skills have already been run across the available corpus. Saved outputs and reports exist; inspect what is present before proposing to regenerate anything. Corpus-wide execution does not establish that every extraction or match is scientifically correct. Read [README.md](README.md) for the short human-facing overview. Current files and the user's latest instructions take precedence over historical plans or this contextual summary.

Paths below are relative to this repository unless stated otherwise. Run project commands here, not from the parent thesis workspace.

## Active pipeline and evidence boundaries

Read the relevant skill's `SKILL.md` and requested supporting resources before performing its work. Each skill is self-contained: instructions, schemas, Pydantic models, examples, validation helpers and tests live together.

1. **[register-observations](.agents/skills/register-observations/SKILL.md)** takes a PDF and discovers identifiable numerical pitting-related outcomes in tables, discrete plot points, annotations and text. It records original readings, source locations and minimal association clues; it consolidates repeated presentations only when the paper supports their correspondence.
2. **[match-observations-cra-database](.agents/skills/match-observations-cra-database/SKILL.md)** takes a PDF, registry and paper-specific CRA CSV. It proposes supported CRA row assignments and unresolved candidates, with paired evidence and justified conversion calculations.
3. **[enrich-observations](.agents/skills/enrich-observations/SKILL.md)** takes a PDF and registry. It adds alloy composition/preparation, microstructure, electrolyte, temperature and procedure information for eligible observations, preserving their registered potentials.

Matching and enrichment are **separate branches from the registry**, not an information handoff from matching to enrichment. The comparison should test whether an agent can recover experimental context without seeing the reference answers.

- Registration and enrichment require fresh paper-only contexts. Do not read CRA CSVs, matching reports, previous extraction/enrichment outputs, paper-specific comparison notes or predecessor extraction results for those tasks. If the chat has already seen reference answers, it is not a blind extraction context; use it for development/review rather than claiming a new blind run.
- For a supplied registry subset, do not open the full registry or infer extra records from matching outputs. A filename containing `matched_only` is not permission to read its selection source. Preserve IDs and the supplied scope.
- Matching may read the supplied CRA CSV. External authoritative resources may supply conversion constants, not missing experimental observations. Its assignments and reasoning must stay out of blind enrichment.
- This AGENTS file deliberately contains no paper-specific target values or CRA row assignments. Keep future additions free of benchmark answers too.

Use actual visual PDF inspection. Rendering without viewing is insufficient; embedded text may locate passages but does not replace checking consequential values and labels visually. Current skills exclude automated OCR, table extraction, marker detection and curve tracing. Registration surveys the paper for outcomes; enrichment requires an overview of every page followed by detailed context reading. Matching inspects registered sources and supporting context as needed. Disclose actual coverage/access limits; do not claim a full survey from a few selected pages.

## Where the important resources are

- [papers/](papers/): source literature. Filenames begin with the project's literature reference number, for example `49_...pdf`.
- [citrine_database/](citrine_database/): original `CRA_database_Scientific_Data_Publication_12102020.xlsx`, its pitting-potential export `pitting_potential_complete.csv`, and a separately retained `..._Compatible.csv` variant. Do not silently substitute variants.
- [citrine_database/by_reference/](citrine_database/by_reference/): paper-specific inputs named `pitting_potential_<reference>.csv`. `Reference` identifies the paper; `No.` is the original CRA record identifier, not CSV line position.
- [observation_registry/](observation_registry/): paper-derived registries and coverage reports.
- [matched_observations/](matched_observations/): current saved alignments and matching reports.
- [enriched_observations/](enriched_observations/): current saved experiment-context extractions and reports.
- [models/observation_enrichment.py](models/observation_enrichment.py): a separate project-level model used by Python consumers. Skills use their own local definitions. Do not silently synchronize both copies when a request is scoped to only one.
- [analysis.py](analysis.py): exploratory CSV loading/splitting, reference inspection and SQL imports; not a general pipeline runner.
- [process_observations.py](process_observations.py): earlier helpers for selecting matched observations and loading enriched records.
- [utils/postgres.py](utils/postgres.py): nested-JSON-to-related-tables importer, including `recreate_and_insert_many` for independent dataset roots. [utils/traversal.py](utils/traversal.py) prepares selected in-memory measurement shapes for SQL; it is not scientific unit normalization. Do not write those transformed objects back as canonical extraction data.
- [Notes/](Notes/): research notes and earlier schema ideas, including GEMD exploration. These are background, not the active format contract.
- [tests/](tests/): helper and remaining legacy tests. Active skill tests are bundled within each skill.

**Output-name mismatch:** the saved corpus uses `matched_observations/` and `enriched_observations/`, while the matching/enrichment skills currently default to `observation_matches/` and `enrich-observations/`. Specify the current corpus destinations explicitly when continuing those runs. The exploratory Python scripts also retain old paths, sample filenames and filters; inspect them before use rather than assuming they match the current layout.

Each skill saves JSON plus a companion Markdown report and preserves existing pairs with `_run_2`, `_run_3`, etc. unless replacement is requested. Reports document ambiguity, exclusions, coverage and validation; they are part of the research results. Do not overwrite, rename, reformat or regenerate existing scientific artifacts as incidental cleanup.

## Data contracts to preserve

- Registry schema **1.1**: [observation_registry.schema.json](.agents/skills/register-observations/references/observation_registry.schema.json). Root collection: `observations`.
- Alignment schema **1.0**: [observation_alignment.schema.json](.agents/skills/match-observations-cra-database/references/observation_alignment.schema.json). Root collection: `observations`.
- Enrichment schema **1.0**: [observation_enrichment.schema.json](.agents/skills/enrich-observations/references/observation_enrichment.schema.json). Root collection: `experiments`.

Use the bundled schema/model as the detailed contract; do not invent fields. Earlier registry versions are not silently upgraded. Refactoring Python code alone must preserve schema generation, required fields, descriptions, defaults, validators and serialization. Enrichment models have been flattened into the skill's `scripts/observation_enrichment.py`: retain the shared strict base and meaningful nested models, without reintroducing the retired `PaperExtraction`/`Experiment` compatibility layers.

Important semantics:

- `observation_id` is generated within a registry and preserved downstream. It need not match IDs from an independently regenerated run. Partial batches may have gaps; do not renumber. Alignment/enrichment input filenames and SHA-256 hashes bind outputs to exact file bytes. Check lineage when joining subsets or runs; do not rewrite hashes merely to make stale outputs pass.
- Registry `primary_location` and alignment `location_indices` are zero-based indices into that observation's `locations`. `pdf_page` is one-based; printed page labels are separate. A primary reading is a storage choice, not a resolution of scientific truth.
- `result_type` describes origin: `reported_experimental`, `interpolated`, `calculated`, `cited`, `reference_value`, or `unclear`. Digitization is not interpolation; scientific uncertainty does not itself make an experimental origin unclear.
- `extraction_status` describes recovery. `complete` requires a non-null potential and empty `failure_notes`; `partial` and `failed` require nonblank failure notes. Complete/partial continue downstream; matching retains failed entries as `not_assessed`, while enrichment skips and reports them. Completion does not certify independence or benchmark suitability.
- `association_notes` holds paper-derived context clues. The singular **`result_note`** holds scientific qualifications, provenance uncertainty, source disagreements and possible duplicate relationships. `failure_notes` records recovery/association problems, not every ordinary unreported field. Enrichment can resolve a contextual problem from a partial registry without changing the registry itself.
- Measurements use `value`, `min`, `max`, `unit`, `plus_minus`. Optional measurement subfields may be omitted; finite-number and bound-consistency checks apply. Required text is non-null, using `""` when unavailable; collections use `[]`, missing numeric/measurement values use null. None implies zero or explicit absence. JSON must reject duplicate keys, NaN and Infinity.
- Enrichment copies the raw observation-level `pitting_potential` unchanged, including nulls, original units, uncertainty and omitted subfields. Do not substitute secondary readings or let model serialization insert extra defaults. Record suspected errors/corrections in notes. Do not consolidate distinct IDs during enrichment.
- Keep context in reported units. Do not calculate unreported pH, chloride concentration, residual alloy composition, standard seawater recipes or assumed room temperature. Use alloy `"balance"` only when stated. Preserve multi-step processing and multi-rate/stepped test schedules in prose where one scalar is inadequate.
- Supported alignment `matches` and unresolved `candidates` are separate. Default joins use supported links. Many-to-many assignments are allowed; shared rows can reflect summaries or repeated presentations. Do not force a one-to-one mapping, treat candidates as assignments, or count every joined row as an independent benchmark experiment.
- Identity and numeric agreement are separate: strong independent evidence may identify a counterpart despite a discrepant potential. `unlinked_citrine_nos` means no supported assignment within the supplied registry, not absence from the paper. Shared qualifications are explanatory text, not automatic exclusion rules.
- CRA comparison units are wt% for alloy elements, mV (SCE) for potentials, °C for test temperature and mV/s for applicable sweep rates. Electrode conversion needs justified reference/filling-solution/temperature information; composition-basis conversion needs sufficient composition. Preserve bounds and qualitative targets such as `Transpassive`; `steady state` and potential steps are not numerical sweep rates. Never fit a conversion to the expected answer.

## Development and verification

Python **3.11+**, managed with `uv`; dependencies are in `pyproject.toml` and `uv.lock`. Use `uv sync` when environment setup is needed. Windows commands below assume the repository root and its existing `.venv`.

Run focused tests for the affected skill, selecting the appropriate skill name:

```powershell
$skill = "enrich-observations"
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s ".agents/skills/$skill/scripts" -p "test_*.py"
```

The other skill names are `register-observations` and `match-observations-cra-database`. Their tests use invented data and standalone copies. Do not rerun real paper extractions to verify code/documentation changes. If Windows sandbox permissions block the default temporary directory, use process-local `TEMP`/`TMP` under a task-specific directory in `tmp/`.

Each skill's `scripts/validate_output.py` is read-only. Registry validation uses `--input`; matching also requires `--pdf --csv --registry`; enrichment also requires `--pdf --registry`. Matching/enrichment have read-only `prepare_inputs.py` helpers without `--input`. Matching validation additionally supports `--report-stdout`. Exit codes: **0** structurally valid (including flagged/ambiguous records), **1** invalid data, **2** setup/I/O failure. Schema success does not verify scientific fidelity, actual visual inspection or benchmark correctness.

When changing a skill, check its local links and run the installed skill-creator's packaging validator as appropriate. Keep skills self-contained; do not add cross-skill imports. For contract-preserving refactors, compare generated schemas with the existing bundled files rather than regenerating the files to hide drift. Top-level tests for removed skills/models may be stale; do not restore archived components merely to satisfy unrelated tests.

The user prefers SQL for exploring data. Support PostgreSQL exploration where useful, while preserving canonical paper-derived JSON. **Do not run `analysis.py` as a harmless inspection command:** its `main()` currently calls a drop-and-recreate import into the working `agenticdb` database. Rebuild that database only when the user's task explicitly requests it. For importer verification, `tests/test_postgres.py` enables disposable `importer_test_<uuid>` databases via `RUN_POSTGRES_TESTS=1`; never target the working database for those tests. Connection settings are in `utils/postgres.py`; keep credential values out of documentation and logs.

## Predecessor work and background reading

These resources are in the **parent thesis workspace**, outside this Git repository. Consult them when relevant to historical/design work, not during blind paper extraction. Earlier projects can contain extracted answers.

- [../OntologyRefiner/](../OntologyRefiner/): the predecessor developed during the lab rotation. Reuse of this work in the thesis is explicitly permitted. Relevant older code includes `agents/data_extractor.py`, `agents/critic.py`, `agents/consolidator.py`, and `extractor_critic_consolidator_refiner_output/initial_schema.json`.
- [Lab Rotation II Report](<../Lab Rotation Writeup/Lab Rotation II Report.pdf>): writeup of that predecessor.
- [../Artifacts of AgenticDatabaseReconstruction/](<../Artifacts of AgenticDatabaseReconstruction/>): archived skills/experiments. `extract-series`, `extract-experiments`, and `locate-pitting-sources` are no longer active repository skills or dependencies.
- [2021 - Nyby.pdf](<../2021 - Nyby.pdf>): background on the CRA database.
- [2022 - Sasidhar.pdf](<../2022 - Sasidhar.pdf>) and [2023 - Sasidhar.pdf](<../2023 - Sasidhar.pdf>): related work using CRA data and textual processing information.

Do not edit predecessor/archive projects when working on the active repository unless the user requests it. Avoid silently importing their schemas or changing the current experiment structure to match old designs.

## Collaboration preferences

- Keep scope narrow and work toward a usable benchmark before broad ontology redesign, elaborate normalization frameworks or unsolicited automation.
- Preserve the user's edits and current work; inspect Git status before changes and do not undo archive moves or unrelated modifications.
- Communicate plainly and concisely. Human-facing documentation should be easy for thesis advisors to skim. Use ordinary unordered lists for folder descriptions, not padded code-block directory trees.
- Keep reports compact: useful comparison tables and shared notes, without long repetitive narratives for every observation. Put detailed field rules in the relevant skill resources instead of bloating the README.
- Check current files when resuming: directory names, scripts and research priorities can change. Update this context when a task explicitly changes a durable project convention; do not put temporary task logs or paper-specific benchmark answers here.
