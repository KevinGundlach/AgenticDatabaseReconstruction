---
name: register-observations
description: Build a paper-only registry of condition-specific numerical pitting outcomes with precise locations, result-origin classifications, and extraction statuses, consolidating repeated presentations. Use to anchor later experiment-context extraction independently of Citrine or other databases.
---

# Register Observations

Create one version **1.1** JSON observation registry from one supplied paper PDF, plus a brief coverage report. Read the [JSON Schema](references/observation_registry.schema.json) and [extraction conventions](references/extraction_conventions.md) before extraction. The [invented example](references/example_registry.json) illustrates a table/plot consolidation, a scientifically qualified complete result, and partial/failed recoveries. The bundled [Pydantic classes](scripts/observation_registry.py) and [validator](scripts/validate_output.py) are self-contained.

## Inputs and outputs

Accept a PDF, optional positive literature reference number, and optional output location. Use the PDF filename (including extension, without directories) for `paper_name`. Use a supplied reference or the filename's leading positive integer; use null when neither is available. Clarify a conflict between an explicit reference and the filename rather than silently choosing one. Do not obtain a reference from a database or the paper's bibliography.

Default JSON: `observation_registry/paper_<reference>.json` relative to the project root, or `observation_registry/<pdf_stem>.json` when no reference is available. Save `<json_stem>_report.md` beside it. Create the output directory as needed and honor explicit destinations. Preserve both existing registries and reports: choose the next unused `_run_2`, `_run_3`, etc. JSON stem for which neither companion exists, unless replacement was requested. Write UTF-8 strict JSON; no comments, duplicate keys, NaN, or Infinity. No database import, Citrine alignment, full experiment extraction, or additional batch-summary artifact is part of this skill. If several PDFs are requested, apply this workflow separately to each.

This format applies to new outputs. Preserve existing version 1.0 registries/reports; do not infer new classifications from old notes or rewrite those files. The updated validator accepts 1.1 only and explains the version mismatch for older inputs. Classification of an older extraction requires an explicitly requested review or fresh extraction.

## Evidence and visual access

Use only the supplied paper for experimental evidence. Do not read Citrine, locating reports, or saved extraction outputs. For blind benchmarking, invoke this skill in a fresh context containing only the PDF and these resources; do not reuse a conversation containing database values for this paper. The output contains no Citrine identifiers, expected database values, or database-derived matching hints.

Visually inspect the full paper's plots, tables, captions, footnotes, and relevant text. Direct visual PDF input works; otherwise render the PDF to page images and actually view them. A path, text layer, or rendered image that has not been viewed is not visual inspection. Use available PDF rendering guidance/tools and an image viewer; enlarge dense cells, legends, and symbols when needed. Existing text may locate passages, but verify output values and consequential labels against the visible paper.

The agent reads and interprets the paper. Do not run OCR, automated table extraction, marker detection, or curve tracing. Code may prepare visual inputs, write output, assign bookkeeping IDs, and validate JSON. Preserve the original PDF.

If no visual-access route works, save a report with the actual tool/capability error and do not create an empty registry implying successful inspection. With partial access, retain identifiable numerical occurrences, assign statuses according to their actual recovery, and disclose uninspected pages/sources in the report. A checkpoint or schema-valid file does not establish paper-wide completion.

## Register observations

1. Survey all supplied pages for identifiable, condition-specific numerical pitting-related values or bounds. Include printed values, discrete plotted markers/bars and numerical text-only results, including source-reported means/ranges for one condition. Put broad screening ranges and purely qualitative pitting/no-pitting statements in the coverage report. Read the paper's terminology to distinguish pitting from corrosion, repassivation, imposed potential, or other breakdown events. Do not infer a pitting threshold from an unannotated continuous polarization curve; an explicitly identified numerical pitting annotation is eligible.
2. Record each outcome with its original value/bounds, unit, electrode reference, and source-specific selectors. Read axes (including logarithmic scales), scoped headers, symbols and captions carefully. Use defensible graphical precision; connecting/fitted lines do not create observations. Preserve condition-specific numerical occurrences whose recovery is partial/failed, using nulls and `failure_notes` where needed. Put scientific/measurement-criterion uncertainty inherited from the paper in `result_note` rather than treating it as a recovery failure. Do not fabricate individual entries for an unreadable source whose outcomes cannot be enumerated.
3. Capture only the labels, independent-variable coordinates, and minimal conditions/clues needed to associate the outcome with later context extraction. Do not expand this into a full alloy/solution/procedure record. Never infer missing units, reference-electrode details, compositions, pH, or standard conditions. No unit normalization is performed here.
4. Consolidate equivalent presentations only where the paper supports the same sample, conditions, outcome type, and reported result. Same numbers or compositions alone do not prove identity. Retain each presentation as a separate location with its own reading. Preserve separate runs, replicates and scan/scratch outcomes. Keep uncertain duplicate candidates separate and explain the possible relationship in `result_note`; this alone does not downgrade extraction status.
5. Choose the primary location using the best supported reading, normally an explicit number over approximate digitization. Copy its measurement exactly to the observation level, without averaging, rounding further, or converting units. Preserve differing readings in their locations and explain source conflicts in `result_note`. Selecting a primary reading does not resolve scientific truth. Assign required `result_type` and `extraction_status` using the definitions below and the conventions; neither has a default.
6. After consolidation, assign sequential registry-scoped IDs using `obs_001`, `obs_002`, etc. in first-encounter order. During explicitly requested edits to a 1.1 registry preserve existing IDs; append unused IDs for additions and do not renumber survivors. IDs need not coincide across independent runs. Neither a numerical value nor an author-supplied sample label is an observation ID.
7. Review source coverage and associations against the original pages, save the JSON, run validation, and repair structural errors without inventing scientific information. Save the brief report from the final saved output. An inspected paper with no eligible outcomes can have `observations: []`; inaccessible or incomplete inspection must be disclosed rather than described as no outcomes.

## Classification and routing

`result_type` describes the origin of the primary potential: `reported_experimental`, `interpolated`, `calculated`, `cited`, `reference_value`, or `unclear`. Classify the potential, not every contextual attribute. Digitization is a reading method, and ordinary summaries of experimental replicates remain experimental. A known experimental origin remains `reported_experimental` even if the paper leaves the physical measurement criterion uncertain. Detailed category definitions and overlapping-source cases are in the conventions.

`extraction_status` describes recovery: `complete` means recovered as far as the paper supplies, with a non-null potential and empty `failure_notes`; `partial` means a recovery problem remains but useful input survives; `failed` means insufficient recovery for useful automatic processing. Both partial and failed require nonblank `failure_notes`. Missing information the paper never supplies, source conflicts, and unresolved duplicate relationships belong in `result_note` and do not alone lower status.

Default downstream routing continues `complete` and `partial`, and retains `failed` for review. Do not automatically exclude any `result_type`, or infer routing from note presence. Routing authorizes an attempt at later enrichment/alignment; it does not certify correctness, benchmark suitability, or the existence of a database counterpart. This skill records those fields but does not run the downstream processes.

## Validate

With the project's existing Python environment (`pydantic>=2.13.5`, `jsonschema>=4.23,<5`):

```powershell
.\.venv\Scripts\python.exe .agents/skills/register-observations/scripts/validate_output.py --input observation_registry/paper_9_run_2.json
```

The script also works from another directory/environment containing those dependencies; resource paths are relative to the script. It reads only JSON and its bundled schema, never the PDF, and changes no files. Exit codes: 0 structurally valid registry (including valid failed records), 1 invalid data or unsupported version, 2 setup/I/O failure. It reports total observations, counts for all three statuses, and partial/failed IDs. Validation checks structure and internal consistency, not correct scientific interpretation, deduplication, or completeness. An exit code of 0 does not mean all observations were recovered successfully.

## Brief coverage report

Save a concise report for every attempted paper, including blocked attempts. State input filename/reference, supplied and visually inspected pages, completion/access limitations, covered figures/tables/text sections, and exclusions with reasons (including broad ranges and qualitative statements). Give a link to the registry if saved, its actual observation count, complete/partial/failed counts (including zeros), partial/failed IDs, and the actual validation outcome (or not run and why). Derive counts from saved `extraction_status` fields, not notes. Report significant source qualifications/conflicts and uncertain duplicate groups separately from recovery failures in concise shared notes. Do not call unresolved duplicate records independent experiments. Do not append a methods summary or per-observation narratives. If report writing fails, disclose the error and return its contents in chat.

Finish with links to the saved registry and report and any material coverage limitations.
