# Project context for agents

Last reviewed: **2026-11-19**. This is durable project context, not a task queue or a record of every conversation. Verify current code/data before reusing numerical snapshots.

## Research goal and current focus

This is the main repository for the master's thesis **Automated Ontology Construction for Explainable Feature Discovery in Alloy Corrosion Resistance**. The broad aim is to extract corrosion experiments from literature, learn useful structure/features, and eventually study how material and environmental parameters affect pitting resistance.

The immediate task is narrower: extract pitting-potential outcomes and their experimental context, align them with the manually curated Citrine corrosion-resistant alloy (CRA) dataset, and benchmark context recovery. **An initial field-level gap benchmark, conversion helpers and Matplotlib plots are implemented.** Interpreting/auditing the gaps is the current work. Ontology learning, automatic prompt refinement and predictive modelling are not implemented in this repository. Prioritize concrete, inspectable results over redesigning the ontology or building a general framework.

All three active skills have already been run across the available corpus. Saved outputs and reports exist; inspect what is present before proposing to regenerate anything. Corpus-wide execution does not establish that every extraction or match is scientifically correct. Read [README.md](README.md) for the short human-facing overview. Current files and the user's latest instructions take precedence over historical plans or this contextual summary.

Paths below are relative to this repository unless stated otherwise. Run project commands here, not from the parent thesis workspace.

For a new chat, establish whether the task is blind extraction or non-blind development/review first. Read only the relevant code/skill resources. For non-blind benchmark work, [benchmark review notes](docs/benchmark_review_notes.md) preserve detailed diagnostics, paper-specific findings and unresolved questions from earlier chats. **Do not open those notes for blind registration/enrichment.** Do not regenerate the corpus or redesign schemas merely to resume the project.

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
- [models/observation_enrichment.py](models/observation_enrichment.py) and [models/alignment.py](models/alignment.py): separate project-level models used by Python consumers. Skills use their own local definitions. Do not silently synchronize both copies when a request is scoped to only one.
- [main.py](main.py): prints exploratory statistics through `reporting.database_reports`; not an agent pipeline runner.
- [benchmark.py](benchmark.py): in-memory comparison of one enriched experiment against one already-linked CRA row. See scoring rules below.
- [reporting/benchmark_plots.py](reporting/benchmark_plots.py): gap distributions and horizontal field totals for the supported one-to-one cohort.
- [reporting/database_reports.py](reporting/database_reports.py): saved-corpus loaders and exploratory counts. Its loader limitations and in-memory ID prefixing matter when joining records; see below.
- [utils/](utils/): focused composition, electrolyte and potential conversions, CRA text parsers, SQL helpers and older exploratory conversion code. Current APIs are summarized below.
- [analysis.py](analysis.py): exploratory CSV loading/splitting, reference inspection and SQL imports; not a general pipeline runner.
- [utils/process_observations.py](utils/process_observations.py): earlier helpers for selecting matched observations and loading enriched records; no longer at the repository root.
- [update_observation_ids.py](update_observation_ids.py): idempotent migration of IDs and prose references in the three saved-corpus folders. `--dry-run` previews changes; a write run preserves original bytes in `tmp/observation_id_backups/` and updates registry fingerprints only after verifying their existing lineage.
- [utils/postgres.py](utils/postgres.py): nested-JSON-to-related-tables importer, including `recreate_and_insert_many` for independent dataset roots. [utils/traversal.py](utils/traversal.py) prepares selected in-memory measurement shapes for SQL; it is not scientific unit normalization. Do not write those transformed objects back as canonical extraction data.
- [tmp/](tmp/): exploratory inventories, including `test_solutions.txt`, `test_methods.txt`, `microstructures.txt`, and `heat_treatments.txt`. These informed the parsers; they are not runtime dependencies or authoritative schema definitions.
- [plots/](plots/): benchmark PNGs. [output/pdf/](output/pdf/): schema and workflow diagrams for advisor communication; see artifact descriptions below.
- [docs/benchmark_review_notes.md](docs/benchmark_review_notes.md): non-blind analysis history, evidence pointers and paper-specific examples. Contains reference answers; not startup reading for extraction.
- [tests/](tests/): helper and remaining legacy tests. Active skill tests are bundled within each skill.

`README.md` is the short human-facing overview. The former `README_Codex.md` and `Notes/` directory are not present in the current checkout; do not rely on old chat paths or recreate them incidentally.

**Output-name mismatch:** the saved corpus uses `matched_observations/` and `enriched_observations/`, while the matching/enrichment skills currently default to `observation_matches/` and `enrich-observations/`. Specify the current corpus destinations explicitly when continuing those runs. The exploratory Python scripts also retain old paths, sample filenames and filters; inspect them before use rather than assuming they match the current layout.

Each skill saves JSON plus a companion Markdown report and preserves existing pairs with `_run_2`, `_run_3`, etc. unless replacement is requested. Reports document ambiguity, exclusions, coverage and validation; they are part of the research results. Do not overwrite, rename, reformat or regenerate existing scientific artifacts as incidental cleanup.

## Data contracts to preserve

- Registry schema **1.1**: [observation_registry.schema.json](.agents/skills/register-observations/references/observation_registry.schema.json). Root collection: `observations`.
- Alignment schema **1.0**: [observation_alignment.schema.json](.agents/skills/match-observations-cra-database/references/observation_alignment.schema.json). Root collection: `observations`.
- Enrichment schema **1.0**: [observation_enrichment.schema.json](.agents/skills/enrich-observations/references/observation_enrichment.schema.json). Root collection: `experiments`.

Use the bundled schema/model as the detailed contract; do not invent fields. Earlier registry versions are not silently upgraded. Refactoring Python code alone must preserve schema generation, required fields, descriptions, defaults, validators and serialization. Enrichment models have been flattened into the skill's `scripts/observation_enrichment.py`: retain the shared strict base and meaningful nested models, without reintroducing the retired `PaperExtraction`/`Experiment` compatibility layers.

Important semantics:

- New registrations use paper-prefixed `observation_id` values such as `42_obs_001`, using the resolved positive literature reference and a sequence padded to at least three digits. Matching/enrichment preserve the whole supplied ID. The skills still accept legacy unprefixed IDs unchanged; do not migrate saved artifacts incidentally. An ID need not match one from an independently regenerated run. Partial batches may have gaps; do not renumber. Alignment/enrichment input filenames and SHA-256 hashes bind outputs to exact file bytes. Check lineage when joining subsets or runs; do not rewrite hashes merely to make stale outputs pass. Project-level models/loaders are separate from these skill-local contracts; their older ID validation/prefixing needs review before consuming new prefixed outputs.
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

## How matching actually works

The LLM visually reasons over the paper, supplied registry and CRA rows. The Python helpers prepare strict inputs, calculate fingerprints, validate output and format reports; they do **not** solve the scientific assignment problem. There is no implemented nearest-neighbor matcher, confidence probability or optimization that minimizes benchmark gaps.

Use sample/composition, varying coordinates, electrolyte, temperature, preparation and method as needed to establish identity. Potential equality alone is insufficient, and a supported identity can survive a potential disagreement. Consider secondary registered locations too. A `matched` observation can have multiple supported links and additional unresolved candidates. Explain shared-row/summary relationships rather than silently selecting the numerically closest target. Never change the registry to make an assignment easier.

`inspected_pdf_pages` records pages actually inspected, not a claim that all omitted pages are irrelevant. `shared_qualifications` records source/conversion limitations applying to multiple assignments. Neither field automatically proves/excludes a match. Each link's `location_indices` identifies the registered readings supporting that link, not new locations in the matching file.

## Benchmark code and current scoring rules

[benchmark.py](benchmark.py) exposes:

```python
benchmark_experiment(
    experiment, cra_row, *, calculate_balance=False,
    assume_percent_is_weight=False, tolerances=None, relative_tolerance=None,
)  # -> BenchmarkResult
count_gaps(experiment, cra_row, **options)  # -> int
```

`experiment` is a project-level `EnrichedExperiment`; `cra_row` is a column-to-value dictionary. These functions perform no file/database access and modify neither argument. `BenchmarkResult` contains `gaps`, `skipped`, `compared`, `derived`, and a `gap_count` property. `compared` counts assessable opportunities, including gaps. The function assumes an existing link; it does not verify or choose the CRA counterpart.

- Count one gap per alloy element, required solution ingredient or scalar field. Keys include `alloy.Cr`, `test_solution.NaCl`, `pitting_potential`, `test_temperature`, `chloride_concentration`, `ph`, and `material_class`. Missing extraction, failed conversion and numerical mismatch are different reason strings, not extra gaps for the same field.
- Compare alloy composition, pitting potential, test temperature, solution composition, chloride concentration, pH and material class. Heat treatment/alloy preparation, test method, scan rate, microstructure and comments are currently outside this metric. Material class is compared case-insensitively.
- Missing/unusable CRA targets are **unscored**, not agreements. An unlisted element whose CRA amount is zero is unscored, while an explicitly extracted amount can disagree with a CRA zero. Extra extracted solutes not listed by CRA are unscored. Solvent is compared only if CRA explicitly names it.
- Explicit alloy `"balance"` is unscored by default to avoid counting propagated errors twice; `calculate_balance=True` opts in. Ambiguous bare `%` remains unsupported unless `assume_percent_is_weight=True`. Do not silently turn either assumption on to improve results.
- Use reported pH/chloride when present. Estimate only a missing field using the electrolyte helpers, never choose whichever estimate agrees better with CRA. Estimation has restrictive chemical/representation assumptions; failure to estimate can be a benchmark gap without being an extraction failure.
- Compare a numerical CRA potential `Avg` to the extracted central value. If `Avg` is absent, compare explicit `Min`/`Max` endpoints. Do not manufacture midpoints or uncertainty-derived extrema. Incompatible point/range roles, qualitative/inequality targets such as `Transpassive` or `>800`, and unresolved named recipes are skipped with reasons.
- Parse CRA solution text into ingredients; missing identity and quantity for one ingredient is one gap. Compare in mol/L when supported, otherwise an explicitly shared concentration basis. Do not assume density, percent basis or a seawater recipe.

**Tolerances:** defaults use `math.isclose` with absolute and relative tolerances of `1e-6`. The `tolerances` mapping supplies absolute margins by field/group, e.g. `{"alloy": 0.01, "pitting_potential": 5}` means wt percentage points and mV (SCE). Other standardized units are °C, mol/L for chloride, and pH units; solution amounts may retain their shared basis.

`relative_tolerance=0.01` is an optional exploratory alternative: after conversion, allow `max(absolute_tolerance, 0.01 * abs(CRA_value))`. It is anchored to the **CRA** value, not the larger of the two values. Each bound uses its own target; zero keeps the absolute allowance. This changes numerical agreement only, not missing/conversion gaps, skipped fields or categorical checks. It is not the new default or a scientifically justified universal digitization tolerance. `EnrichedExperiment` itself has no per-field `reading_method`; the registry can supply potential-reading information for later analyses.

The metric measures **dataset disagreement**, not automatically an agent error. CRA is a comparator, not unquestioned ground truth. A gap can originate in registration, association, enrichment, conversion assumptions, CRA curation or the source paper. A small gap count with many skipped comparisons does not demonstrate complete extraction. The user intentionally wants a count rather than magnitude-weighted error; supplement it with coverage and reason breakdowns rather than replacing it with MAE.

### Current cohort and plots

[reporting/benchmark_plots.py](reporting/benchmark_plots.py) exposes:

- `plot_gap_histogram(output_path="plots/gap_histogram.png", **options)`: 10 bins; returns the experiment gap counts.
- `plot_gap_count_bars(output_path="plots/gap_histogram_2.png", **options)`: one vertical bar for every integer from zero to the observed maximum, including empty bins; returns counts by gap count. The maximum is not fixed at 14.
- `plot_gaps_by_field(output_path="plots/gaps_by_field.png", **options)`: horizontal field totals, sorted by count; returns the field counts.

All use the same supported one-to-one cohort: an observation has exactly one supported CRA link, and **no other observation in any loaded alignment** links to that CRA row. Reverse links are counted before filtering, including multi-target observations. Candidates are not assignments. Thus these charts exclude both directions of many-to-many mapping; they do not cherry-pick a best row. They check matching/enrichment PDF and registry filename/hash agreement, CRA reference/identifier validity and required enrichment presence. They do not rehash every on-disk source; use skill validators for that.

Run from the project root. Plot functions pass benchmark options through, create destination folders and **overwrite the explicitly named image** on rerun; they do not modify scientific JSON or databases. No GUI is opened. Current alternate images can be reproduced with:

```python
from reporting.benchmark_plots import plot_gap_count_bars, plot_gaps_by_field

plot_gaps_by_field("plots/gaps_by_field_2.png", relative_tolerance=0.01)
plot_gap_count_bars("plots/gap_histogram_3.png", relative_tolerance=0.01)
```

**Read-only snapshot, recomputed 2026-11-19:** 77 enrichment files contain 2,176 records; 61 alignment files contain 850 observations with supported matches, 873 supported links and 667 distinct assigned CRA identifiers. There are 22 observations with multiple supported targets and 45 CRA rows shared by observations. The original pitting dataset has 810 rows. The plotted one-to-one cohort has **577 pairs**. More extracted observations does not establish more unique experiments: coverage, repeated presentations, replicates and summaries differ.

| Same 577 pairs, default composition policies | Rounding tolerance | Optional CRA-relative 1% |
|---|---:|---:|
| Total gaps | 2,888 | 2,643 |
| Records with zero scored gaps | 4 | 11 |
| Maximum gaps observed | 14 | 14 |
| Pitting-potential gaps | 266 | 137 |
| pH gaps | 312 | 305 |
| Missing-value gap reasons, all fields | 2,300 | 2,300 |
| Conversion gap reasons, all fields | 135 | 135 |
| Numerical mismatch reasons, all fields | 453 | 208 |

These are descriptive snapshots, not test expectations. Recompute if inputs, cohort or policies change. Detailed causes and paper-level checks are in the non-blind review notes.

### Loader caveats

`reporting.database_reports.load_enriched_observations()`, `load_aligned_observations()` and `load_cra_records()` read files, not PostgreSQL. They currently search canonical `paper_<reference>.json` names for references 0–99, relative to the working directory; they do not discover arbitrary subsets or `_run_` variants. The first two validate models and then prefix IDs **in memory** as `<reference>-obs_NNN`. Do not serialize these prefixed IDs into canonical registries/outputs. For raw documents, join by paper, original ID and exact input lineage.

The CRA loader uses Pandas, so missing markers can become NaN and cell types can be coerced. Use the matching helper or `csv.DictReader` with `utf-8-sig` when original cell strings matter. Pandas dictionaries should use `orient="records"`; non-finite Pandas values must not be written into strict JSON. Earlier CSV trouble included a non-UTF-8 export and export/import interpretation, not evidence that quoted commas are inherently invalid CSV.

## Focused conversion and parsing helpers

All scientific transformations are in memory. Do not rewrite enriched JSON with standardized/derived values.

- [utils/weight_pct_conversion.py](utils/weight_pct_conversion.py): `to_weight_percent_strict(Alloy)` returns a complete numerical composition or raises `InvalidAlloyCompositionError` with an `AlloyCompositionErrorReason`. It requires total 100 within 0.1 percentage point and reports the first blocking cause, not every cause. `to_weight_percent(alloy, *, calculate_balance=True, assume_percent_is_weight=False)` retains independently usable weight amounts and returns `None` for listed elements with unknown amounts; it can retain `"balance"`. **Its balance default is True; the benchmark's default is False.** Atomic-percent/ratio conversion requires a complete consistent composition and uses fixed atomic masses. Never infer an unstated balance element or treat unspecified traces as zero. Bare `%` is opt-in; ppm/purity/formula labels need justified semantics, not blanket rewriting. Ranges without usable central values remain outside this simple converter.
- [utils/electrolyte.py](utils/electrolyte.py): `estimate_ph(TestSolution)` and `estimate_cl(TestSolution)` return a float or `None`, ignoring the existing reported pH/chloride fields. Chloride is total stoichiometric mol/L, not activity. The pH helper is a restricted ideal 25 °C strong-acid/base calculation, requires an explicit recognized water solvent and a supported recipe, and does not model general equilibrium, buffers, sulfuric acid, gas effects or seawater. Concentration bases needing unknown density are not silently converted. A blank solvent alone can block otherwise usable pH estimation; distinguish representation/helper limitations from absence in the paper.
- [utils/experiment_conversions.py](utils/experiment_conversions.py): `standardize_pitting_potential(Measurement)` returns a new `Measurement` in `mV (SCE)` or raises `PittingPotentialConversionError`. It handles observed unit spellings, using a fixed 25 °C convention (SCE 241 mV vs SHE; explicit NHE treated on the same zero; supported Ag/AgCl filling solutions have their own constants). Scale/offset central values and bounds; scale uncertainty magnitudes only; preserve optional-field presence. Bare V/mV, unidentified hydrogen scales, missing Ag/AgCl filling details or unsupported temperature dependence can fail. This function sees only the measurement, not paper context, registry secondary readings or matching prose. A successful LLM identity assignment therefore need not imply automatic numerical convertibility. Never fit an offset to CRA.
- [utils/cra_electrolyte_parsing.py](utils/cra_electrolyte_parsing.py): `parse_test_solution(text)` returns `TestSolution` or raises `TestSolutionParsingError`. Deterministic rules informed by the observed CRA inventory separate ingredients from preparation, preserve concentration basis and avoid inventing recipes, water, pH or chloride values. Unsupported leftovers raise. Former name `cra_parsing.py` is retired.
- [utils/cra_test_method_parsing.py](utils/cra_test_method_parsing.py): `estimate_test_type(text)` returns `CanonicalTestType`: `potentiodynamic`, `potentiostatic`, `potential_step`, `scratch`, `ambiguous`, or `unknown`. It estimates the stage determining the pitting result, not every method mentioned or the first label. Preparation-only text or merely naming a potentiostat is insufficient. This helper is not included in the current gap benchmark and is not a universal electrochemistry ontology.
- [utils/unit_conversions_codex.py](utils/unit_conversions_codex.py) and [utils/derived_columns_codex.py](utils/derived_columns_codex.py): older, broader implementations retained for reference. The user found their generic machinery and per-observation override/context design overengineered. Do not revive them as the default or add a general conversion engine without an explicit need.

## Open findings and possible next directions

These are options to discuss, **not authorization to implement everything**:

- Separate gap reasons and skipped denominators by field/paper. Audit a sample against the PDF and distinguish source/CRA disagreements from recovery or conversion limitations. Current field charts combine these causes.
- Quantify conversion applicability separately from agreement; compare explicit-unit and opt-in ambiguous-percent policies. Unknown listed amounts are not proof that only negligible trace elements are missing. Atomic conversion and balance can propagate one error across several outputs; avoid attributing all propagated gaps independently.
- Audit potential digitization/point association and reference-electrode metadata. The 1% plot still has 137 potential gaps: 96 numerical mismatches and 41 conversion failures. Some are small graphical differences, some source disagreements/reading errors; matching uses independent context and is not guaranteed to maximize numerical agreement.
- Consider a separately recorded, paper-supported reference clarification while preserving the raw potential anchor. Current enrichment must copy the whole anchored measurement, even if a secondary source supplies clearer reference metadata. This is a known contract limitation, not permission to silently fix existing JSON or leak matching answers into enrichment.
- Review pH assumptions and solvent/recipe representation. High pH gap counts are not primarily explained by seawater in the current cohort; many estimates are blocked by empty solvent or unsupported chemistry. Do not infer that every CRA pH value was calculated or sourced externally.
- Review many-to-many links with enriched context. Some are duplicate CRA entries; others are repeated presentations, different methods/conditions, distributions summarized by one row, or questionable associations. Do not force one-to-one identity merely to grow the benchmark cohort.
- Heat treatment, test method, scan rate, microstructure and comments remain useful ontology targets. Multi-step/multi-stage procedures and several simultaneous microstructural descriptions do not generally reduce to one category. Sasidhar's manual preprocessing is a useful comparison, not a scientific ground-truth ontology. Keep these fields outside the initial gap score unless a separate representation/evaluation is agreed.
- A later prompt-refinement loop could inspect development-set gaps and propose general prompt changes. Split held-out data **by paper** before refinement; keep test papers, their CRA rows and analyses out of optimization. No refinement skill, held-out protocol, automated scoring of text fields or benchmark-driven matcher is implemented yet.

## Communication artifacts

[output/pdf/](output/pdf/) contains one-page vector PDFs with PNG previews: `enriched_document_schema`, `observation_registry_schema`, and `observation_alignment_schema`. The preferred overview is **[three_agent_workflow_simplified.pdf](output/pdf/three_agent_workflow_simplified.pdf)**, with PNG and editable SVG beside it. It follows the user's Excalidraw layout: paper → registration → registry, then separate enrichment/matching branches, with CRA supplied only to matching. Its tabular values are invented illustrations. `three_agent_workflow.pdf` is the older, denser version the user did not prefer.

Status email drafts to supervisors Dierk and Marco have been discussed, but no email was sent by the agent. Do not claim it was sent. For polished PDF work use available bundled tooling rather than adding project dependencies solely for diagrams. Previous generators were temporary; inspect current assets rather than assuming a generator script exists.

## Development and verification

Python **3.11+**, managed with `uv`; dependencies are in `pyproject.toml` and `uv.lock`. Use `uv sync` when environment setup is needed. Windows commands below assume the repository root and its existing `.venv`.

For benchmark/plot changes:

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -p "test_benchmark*.py" -v
```

The latest implementation verification had **43 passing tests** (33 benchmark, 10 plotting). Utility tests are `test_weight_pct_conversion.py`, `test_electrolyte.py`, `test_experiment_conversions.py`, `test_cra_electrolyte_parsing.py`, and `test_cra_test_method_parsing.py` under `tests/`; run the relevant file pattern. Tests should verify policies and meaningful failures, not merely mirror implementation. Documentation-only updates need link/fact/diff checks, not corpus extraction or database rebuilds.

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

The importer supports independent roots through `recreate_and_insert_many({root_name: records, ...}, target_db_name=...)`; `recreate_and_insert(...)` remains the single-root wrapper. It infers/validates all datasets before dropping the explicitly named target, recreates once and loads tables in one transaction with rollback/connection cleanup. Objects containing only children still receive rows. Nested table names include the full root/property path (long identifiers use deterministic hash suffixes); object arrays become child tables, while other arrays, including extraction rows, remain JSONB. Preserve these behaviors when touching SQL code.

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
- Prefer simple functions and explicit policies. The user reviews the Python code and has repeatedly asked to simplify generic converters, inheritance layers, excessive categories and per-record override machinery. Do not introduce another framework merely to cover hypothetical edge cases.
- Preserve the user's edits and current work; inspect Git status before changes and do not undo archive moves or unrelated modifications.
- Communicate plainly and concisely. Human-facing documentation should be easy for thesis advisors to skim. Use ordinary unordered lists for folder descriptions, not padded code-block directory trees.
- Keep reports compact: useful comparison tables and shared notes, without long repetitive narratives for every observation. Put detailed field rules in the relevant skill resources instead of bloating the README.
- Check current files when resuming: directory names, scripts and research priorities can change. Update this context when a task explicitly changes a durable project convention; do not put temporary task logs or paper-specific benchmark answers here.
- The thesis is time-constrained, but earlier relative statements such as "two months left" do not establish a current absolute deadline. Confirm a deadline if scheduling depends on it.
