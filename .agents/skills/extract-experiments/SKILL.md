---
name: extract-experiments
description: Extract full pitting-potential experiment records from a research paper, combining visually inspected plots and tables with alloy, electrolyte, and test details. Use for paper-level Citrine-style datasets; selected figure/table series alone belong to extract-series.
---

# Extract Experiments

Produce one JSON document per paper, with one experiment record per reported pitting outcome. Read the [bundled JSON Schema](references/paper_extraction.schema.json) and [extraction conventions](references/extraction_conventions.md) before extracting. The bundled [Pydantic classes](scripts/paper_extraction.py) and [validator](scripts/validate_output.py) enforce the same contract. These resources are local to this skill.

## Input and output

Accept a paper PDF, an optional literature reference number, and an optional output location. For multiple papers, write separate documents. Use the PDF's filename, including its extension, for `paper_name`. Use a supplied reference number or the filename's leading positive integer; otherwise set `reference_number` to null. This is the project's literature reference, not a reference cited inside the paper.

Default output: `experiment_extractions/paper_<reference>.json` relative to the project root, or `<pdf_stem>.json` in that directory when no reference is available. Preserve existing outputs by choosing the next unused `_run_2`, `_run_3`, etc. suffix unless replacement was requested. Always save a companion `<output_stem>_report.md` for every attempted paper, including incomplete or blocked attempts, using the planned output stem when no extraction JSON can be saved. Also save the [batch JSON summary](#batch-summary) for every invocation, including single-paper runs. Write UTF-8 strict JSON, without comments, NaN, or Infinity. Do not load outputs into a database as part of extraction.

## Visual access

Visual PDF inspection is required. Direct PDF visual input works; otherwise render local pages and actually view the resulting images. A path, text extraction, or rendering images without viewing them is insufficient. Inspect the full paper for relevant results and supporting context, including captions, tables, footnotes, and legends. Follow the available PDF skill's rendering guidance when useful; otherwise use an available PDF renderer and image-viewing tool directly. Enlarge dense tables or small symbols as needed. Preserve the original PDF.

The agent reads tables and digitizes plots visually. Do not run OCR, automatic marker detection, curve tracing, or programmatic chart/table extraction. Existing PDF text can locate passages but verify extracted values and consequential labels against visible pages. The paper is the evidence source; do not fill gaps from Citrine, previous extractions, external databases, or expected chemistry.

If visual access fails, report the actual tool/capability failure and incomplete coverage. Do not manufacture an empty dataset suggesting the paper was inspected. A blocked run must still have a saved Markdown report and an entry in the batch summary. If only part of the paper is accessible, retain usable results and disclose incomplete coverage; do not claim a complete extraction.

## Extract and associate results

1. Survey the paper's results, plots, tables, and text for explicit pitting-potential outcomes. Include discrete plotted values, not just printed numbers. Establish what each potential means from the paper's terminology. Do not substitute corrosion potential, repassivation potential, imposed potential, or an unrelated breakdown potential.
2. Build a working map of sample labels, compositions, processing conditions, electrolytes, temperatures, and protocols. Link each outcome through labels, captions, headers, and scoped methods statements. Do not join on composition alone: identical compositions may have different processing or test conditions. Apply shared conditions only where the paper establishes their scope. Keep this map in working notes/report rather than adding fields to the JSON.
3. Transcribe tables, text, and numerical plot annotations; visually digitize discrete markers, bars, and error-bar endpoints when numerical values are not printed. Check axis units, linear/log scales, panels, legends, and merged headers. Use defensible precision. Connecting or fitted lines do not create extra observations. Do not infer a pitting threshold from an unannotated continuous polarization curve. A clearly identified pitting-potential annotation on such a curve is eligible.
4. For each outcome, populate the complete experiment structure using the conventions. Repeat shared context as needed; there are no separate material/setup tables or experiment IDs. Preserve original units and electrode references. Do not compute missing compositions, pH, chloride concentration, reference conversions, or standard room-temperature values.
5. Reconcile repeated presentations of the same outcome in text, tables, and plots into one record, preferring an explicit numerical statement when consistent. Distinct conditions or explicitly separate replicates remain distinct records. Preserve a reported mean/range as one outcome; do not invent its underlying replicates. Investigate contradictory values and ambiguous assignments. Retain recoverable partial rows with specific `failure_notes` rather than guessing or silently dropping them.
6. Review coverage against the survey and verify associations against the original pages. Ordinary unreported fields use the schema's missing-value conventions without a failure warning. An extraction problem, such as an illegible reported value or a result with no recoverable alloy assignment, requires nonempty `failure_notes` on the affected row. Keep scientific qualifications in `result_note` instead.
7. Validate the saved document, repair structural errors without fabricating scientific information, and save the run report. After all requested papers have been attempted, save the batch summary from the final saved outputs and actual validation results. An inspected paper with no eligible outcomes can have `experiments: []`; distinguish that from blocked or incomplete inspection. Validation proves structure, not scientific fidelity or completeness.

## Validation

Use the existing project Python environment with `pydantic>=2.13.5` and `jsonschema>=4.23,<5`:

```powershell
.\.venv\Scripts\python.exe .agents/skills/extract-experiments/scripts/validate_output.py --input experiment_extractions/paper_80.json
```

Alternatively run that script with another environment containing these dependencies; it locates its resources relative to itself, independent of the working directory. The validator reads only the extraction JSON and bundled schema. Exit codes: 0 valid, 1 invalid extraction, 2 setup or I/O failure. A structurally valid row with nonempty `failure_notes` remains flagged and must not be presented as a fully recovered experiment.

## Run report

Save a concise Markdown report with the input filename, pages supplied and visually inspected, results sources covered (figure/table/panel or text section), exclusions and reasons, output link, validation result, and experiment count derived from the saved JSON. List rows with nonempty `failure_notes` by their zero-based `experiments` array index. Describe unresolved conflicts, skipped/unreadable sources, and incomplete coverage even when no row can carry that problem. Do not add per-value provenance fields to the dataset for this pilot.

## Batch summary

Always save one strict JSON summary in the requested output directory, even for a single-paper invocation. Use `batch_<references_in_request_order>_summary.json` when every reference number is available (for example, `batch_49_3_9_71_80_summary.json`); otherwise use `batch_summary.json`. Preserve existing summaries with the next unused `_run_2`, `_run_3`, etc. suffix unless replacement was requested.

Use a top-level array with one entry per attempted paper in request order, including blocked or failed attempts. Each entry must contain:

- `reference_number`: the literature reference number, or null when unavailable.
- `extraction`: the saved extraction JSON path relative to the summary file, or null when no extraction was saved.
- `report`: the saved Markdown report path relative to the summary file.
- `records`: the length of the saved JSON's `experiments` array, or null when it cannot be read.
- `flagged`: the number of saved rows with nonempty `failure_notes`, or null when it cannot be determined.
- `validation_exit_code`: the actual validator exit code (0, 1, or 2), or null when validation was not run.

Derive counts from the final saved JSON; do not estimate them or count flagged rows as fully recovered experiments. Use zero only when a readable extraction actually contains zero matching rows. Check that the summary parses as strict JSON and its non-null file paths resolve. Keep this summary separate from the per-paper extraction schema; report coverage gaps and scientific limitations in each Markdown report even when structural validation passes.

Finish with links to the extraction(s), Markdown report(s), and batch summary, and a brief statement of material limitations. Do not describe schema validation as verification of correct scientific extraction.
