---
name: extract-series
description: Read PDF pages visually using GPT's multimodal capabilities and transcribe tables or digitize discrete plotted series into compact JSON with column defaults and heterogeneous cells. Use for extracting selected figures/tables from a paper, particularly explicit pitting-potential results and requested composition tables.
---

# Extract Series

Produce one JSON document per paper using [the output conventions](references/output_conventions.md) and [the schema](references/series_extraction.schema.json), plus a Markdown run report for every invocation. Read both references before extracting. The PDF is the sole evidence source.

## Input and access

Accept one PDF or a batch of PDFs, an optional figure/table or subject selection, and an optional output path. By default select explicit pitting-potential plots/tables; include supporting tables when requested. Do not extract unrelated figures automatically. Derive each literature reference from the filename's leading number. If absent or ambiguous, ask for the reference.

**Visual access to PDF pages is required.** Use direct visual PDF input when available; otherwise render the local PDF to page images and supply those images to the model through an image-viewing tool. A local PDF path alone is not visual input. Opening a viewer for the user or creating images without viewing them does not constitute inspection. Lack of direct PDF attachment support is not a blocker when rendering and image viewing are available.

For local PDF rendering, read and follow the bundled `pdf:pdf` skill's reading/rendering workflow, using its location in the current skill catalog. It uses bundled or system Poppler (`pdftoppm`); locate bundled tools through `load_workspace_dependencies` when needed. Keep helper code minimal and temporary. Use sufficient resolution to distinguish small symbols; re-render at higher resolution or inspect a crop when necessary. Preserve the original PDF and keep page numbers identifiable. This skill governs extraction scope, JSON output paths, and validation.

**GPT performs the reading and scientific interpretation.** Do not run local OCR or use OpenCV, automated marker detection, curve tracing, or programmatic chart/table-data extraction. Local code may prepare visual inputs, write JSON, and validate it; the validator must not access the PDF.

Treat the visible PDF pages as authoritative, including for scanned papers. Read visually by default. Optional extraction of an existing text layer may help locate passages, but must not supply unverified output values or replace visual reading. Existing text layers, including hidden OCR layers, can garble reading order, equations, subscripts, superscripts, Greek letters, chemical charges, signs, and units. Verify every extracted value and consequential label or interpretation against the visible source. Resolve discrepancies from the page image, not from extracted text or a chemically plausible guess. If a symbol remains unclear after closer inspection, preserve the uncertainty in `notes` and use null/partial where information cannot be recovered.

If neither direct visual input nor rendering plus image viewing is available, stop before extraction and report the specific missing capability or tool error. Distinguish missing dependencies or visual-input support from filesystem permission failures. Do not create an empty result implying that an unseen paper was inspected.

## Extraction

1. Inspect the whole paper as needed to identify eligible sources and interpret labels, captions, units, footnotes, and error bars. Revisit the original page images or direct visual input and inspect enlarged views as needed.
2. Group data into series with a shared column layout. Identify the figure/table, panel, and legend label concisely in `source`; do not copy captions or add contextual metadata. A table usually forms one series; a plot may contain several. Keep sample identifiers or varying coordinates needed to distinguish rows.
3. Define columns, preserving printed labels and units. Include a required boolean `is_target` on every column: `true` for each pitting-potential column and `false` for all other columns, following the target-identification rules in the output conventions. Resolve hierarchical table headers into unambiguous names. Set error-bar interpretation once per column when supported, including the confidence level or multiplier in its category.
4. Transcribe written values or visually digitize discrete markers, bars, and error-bar endpoints. Check linear/logarithmic axes and legend assignments. Use only defensible precision. Connecting/fitted lines do not add points. Do not derive pitting potential from continuous polarization curves.
5. Retain source strings such as `Bal.` and unusual notation; use null for missing or unreadable cells. Preserve special annotations on individual numeric points in the cell's optional `label`, following the output conventions. Do not drop usable rows because one cell is unusual. Repeat merged table labels only where their scope is clear. Preserve composition tables separately rather than joining them to plots.
6. Use the entire paper to interpret this source, but do not populate unrelated contextual fields, normalize units, calculate balance compositions, or derive scientific quantities. Set `notes` to `""` by default. Use notes only to explain `partial`/`none` status or flag extraction anomalies and unclear edge cases that need the user's attention, locating the affected source/row. Do not include captions, routine method descriptions, contextual information, or successful-check summaries. A `complete` series may have notes when an extraction anomaly warrants attention.
7. Write progress after each completed series. Default output: `series_extractions/paper_<reference>.json` relative to the project root. Preserve existing files; choose the next unused `_run_2`, `_run_3`, etc. filename unless replacement was requested. A checkpoint is not evidence that the requested scope is complete.
8. Validate each finished output, repair structural errors, and write the required run report below. Never claim all requested sources were processed based solely on schema validation.

Use `partial` when some requested information remains unreadable or omitted, and `none` with empty rows when an identified and visually inspected eligible series cannot be extracted. Lack of any working visual-access route is a task-level blocker, not a `none` result for an unseen paper.

## Run report (required)

Always save a Markdown report, including for single-paper runs, runs with no eligible sources, and partial or blocked runs. A final chat summary does not replace the saved report. If report writing itself is blocked, explicitly disclose the failure and provide the report contents in the final response.

Save it beside the extraction JSON files unless the user specifies another location. Default names: `batch_<first>_<last>_report.md` for a contiguous batch, `batch_<references_joined_by_underscores>_report.md` for a noncontiguous batch, and `paper_<reference>_report.md` for a single paper. If references cannot yet be resolved, use `extraction_run_report.md` and list the supplied filenames. Preserve existing reports using the next unused `_run_2`, `_run_3`, etc. suffix before `.md`, unless replacement was requested.

Use the following structure, matching the existing batch reports:

- **Scope:** List the exact requested papers and selection, supplied versus visually inspected page coverage, and any missing pages or access limitations.
- **Outputs and validation:** Provide a per-paper table linking saved JSON files, with validation results, counts of `complete`/`partial`/`none` series, row counts, and batch totals. Derive counts from the saved JSON. Mark missing outputs or unrun validation explicitly. Rows may include companion values or repeated results; do not describe them as independent experiments.
- **Items needing attention:** Identify unreadable values, uncertain symbols or target assignments, conflicting source statements, incomplete coverage, and blockers by paper and source. State when there are no outstanding issues.
- **Source coverage and exclusions:** Provide a per-paper table of extracted figures/tables/panels and excluded sources with reasons. Distinguish an inspected paper with no eligible sources from an unseen or incompletely supplied paper. Do not create empty extraction JSON merely to fill the report.

Separate structural validation from scientific fidelity and scope completion. End the user response with a link to the report, extraction output locations, and any material limitations.

## Validate

From the project root, with the project's existing environment:

```powershell
uv --cache-dir .uv-cache run --frozen .agents/skills/extract-series/scripts/validate_output.py --input series_extractions/paper_80.json
```

Alternatively use an existing Python environment containing `jsonschema>=4.23,<5` to run the same script. Validation requires no PDF/image dependencies. The validator reads only JSON and its bundled schema; it checks structure and consistency, not scientific fidelity. A failed validator is not a successful extraction.
