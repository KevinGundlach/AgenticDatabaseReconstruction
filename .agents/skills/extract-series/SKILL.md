---
name: extract-series
description: Read a PDF through native multimodal input and transcribe tables or digitize discrete plotted series into compact JSON with column defaults and heterogeneous cells. Use for extracting selected figures/tables from a paper, particularly explicit pitting-potential results and requested composition tables.
---

# Extract Series

Produce one JSON document per paper using [the output conventions](references/output_conventions.md) and [the schema](references/series_extraction.schema.json). Read both before extracting. The PDF is the sole evidence source.

## Input and access

Accept one PDF, an optional figure/table or subject selection, and an optional output path. By default select explicit pitting-potential plots/tables; include supporting tables when requested. Do not extract unrelated figures automatically. Derive the literature reference from the filename's leading number. If absent or ambiguous, ask for the reference.

**Native visual PDF access is required.** Confirm that the host actually exposes the PDF contents visually to the model. A path, extracted text, or the ability to open a viewer for the user is not sufficient. If native access is unavailable, stop before extraction, explain the limitation, and request the PDF through a supported native input route. Do not create an empty result implying that the paper was inspected.

Do not invoke or write local PDF parsers/renderers, OCR, OpenCV, image processing, or curve-tracing code. Do not convert the PDF into Markdown, text, or local page images. Use native multimodal interpretation for both transcription and digitization. Local code may write JSON and validate it; the validator must not access the PDF.

## Extraction

1. Inspect the whole paper as needed to identify eligible sources and interpret labels, captions, units, footnotes, and error bars. Revisit pages through the native interface when supported.
2. Group data into series with a shared column layout. Identify the figure/table, panel, and legend label in `source`. A table usually forms one series; a plot may contain several. Keep sample identifiers or varying coordinates needed to distinguish rows.
3. Define columns, preserving printed labels and units. Resolve hierarchical table headers into unambiguous names. Set error-bar interpretation once per column when supported, including the confidence level or multiplier in its category.
4. Transcribe written values or visually digitize discrete markers, bars, and error-bar endpoints. Check linear/logarithmic axes and legend assignments. Use only defensible precision. Connecting/fitted lines do not add points. Do not derive pitting potential from continuous polarization curves.
5. Retain source strings such as `Bal.` and unusual notation; use null for missing or unreadable cells. Do not drop usable rows because one cell is unusual. Repeat merged table labels only where their scope is clear. Preserve composition tables separately rather than joining them to plots.
6. Use the entire paper to interpret this source, but do not populate unrelated contextual fields, normalize units, calculate balance compositions, or derive scientific quantities. Explain consequential interpretations and ambiguities, with their source locations, once in `notes`.
7. Write progress after each completed series. Default output: `series_extractions/paper_<reference>.json` relative to the project root. Preserve existing files; choose the next unused `_run_2`, `_run_3`, etc. filename unless replacement was requested. A checkpoint is not evidence that the requested scope is complete.
8. Validate the finished output, repair structural errors, and report the path, validation result, counts by status, and any excluded sources. Never claim all requested sources were processed based solely on schema validation.

Use `partial` when some requested information remains unreadable or omitted, and `none` with empty rows when an identified eligible series cannot be extracted. Lack of native PDF access is a task-level blocker, not a `none` result for an unseen paper.

## Validate

From the project root, with the project's existing environment:

```powershell
uv --cache-dir .uv-cache run --frozen .agents/skills/extract-series/scripts/validate_output.py --input series_extractions/paper_80.json
```

Alternatively use an existing Python environment containing `jsonschema>=4.23,<5` to run the same script. Do not install PDF/image dependencies. The validator reads only JSON and its bundled schema; it checks structure and consistency, not scientific fidelity. A failed validator is not a successful extraction.
