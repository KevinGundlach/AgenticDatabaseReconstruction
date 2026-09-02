---
name: extract-from-figures
description: Extract discrete plotted points, bars, annotations, and table values from a completed catalog-figures paper catalog using native multimodal vision. Flag markerless continuous traces instead of digitizing them; do not use custom OCR or computer-vision pipelines.
---

# Extract From Figures

Turn one completed `paper_<reference>_figures.json` catalog into compact,
queryable rows. The catalog remains the sole source of variable definitions and
provenance; the extraction file contains only catalog references, storage
layout, extracted values, statuses, and concise exception notes.

## Workflow

Run commands from the project root and keep uv's cache inside the workspace.

1. Accept one `mineru_output/paper_<reference>` folder. It must contain exactly
   one `paper_<reference>_figures.json`. Validate that catalog first with the
   `catalog-figures` validator.
2. Read [extraction.schema.json](references/extraction.schema.json), then create
   the extraction skeleton without overwriting existing work:

   ```powershell
   uv --cache-dir .uv-cache run --frozen <skill-dir>/scripts/prepare_extraction.py `
     --input_path <paper-folder>
   ```

3. Process every extraction entry in catalog order. Resolve its image from the
   catalog and inspect it directly with the native image-viewing tool. Use the
   matching panel only when the catalog entry names a panel.
4. Replace `unprocessed` with a final status, adjust the layout when a logical
   variable needs multiple value components, and fill the rows. Preserve the
   skeleton's `source_catalog`, entry order, and `catalog_id` values.
5. Validate the completed paper artifact and fix reported errors:

   ```powershell
   uv --cache-dir .uv-cache run --frozen <skill-dir>/scripts/validate_extraction.py `
     --input <paper-folder>/paper_<reference>_figure_extractions.json
   ```

Do not claim completion when validation fails or any entry remains
`unprocessed`.

## Native Vision Only

Use the model's native multimodal understanding to read figures. Do not create,
invoke, or fall back to OpenCV, OCR engines, contour detection, pixel
heuristics, curve tracing, or similar image-processing code. Deterministic
scripts are only for skeleton generation and validation. If native image
inspection is unavailable, stop and report the blocker.

Do not open a PDF or obtain row values from Markdown or captions. Captions may
help locate a panel through the catalog, but they must not supply values or
conditions absent from the image.

## What to Extract

- Charts: extract scatter markers, markers joined by lines, bars, and explicit
  numeric point annotations. Connecting and fitted lines do not create rows.
- Markerless polarization curves, current-time profiles, and other continuous
  traces have `status: no_discrete_values` and no rows. Do not resample them or
  derive electrochemical features from them.
- Mixed charts: extract reliable discrete series. Use `partial` with a note if
  a distinct markerless or unreadable series is omitted.
- Tables: emit one logical observation per written value. Expand hierarchical
  headers and repeat merged or group-level values so every row is independently
  queryable. A table organized by alloy, parameter, and solution therefore has
  one row per alloy-parameter-solution value.

Apply these established decisions when the cited papers are processed:

- Paper 9 Figure 3: `no_discrete_values`; its markerless potentiodynamic
  polarization traces are not rows.
- Paper 9 Figure 9: extract the visibly plotted discrete points as rows.
- Paper 49 Table 3: represent two-sided and one-sided pH ranges with bound
  components.
- Paper 49 Table 5: emit long-form logical observations over alloy, parameter,
  test solution, parameter value, and PREN, repeating merged labels.

Read categorical and text values as printed. Store numeric values as JSON
numbers in the original catalog unit, using only visually defensible precision.
Use `null` for blank cells, dash placeholders, and unreadable positions. A
visible placeholder does not make an otherwise complete transcription partial;
use `partial` when information was actually omitted or could not be read.

## Layout and Ranges

Each layout position contains a zero-based `variable_index` into the matching
catalog entry plus one component. Row values follow layout order.

- Ordinary scalar: `value`.
- Two-sided or one-sided numeric range: `lower_bound`, `upper_bound`,
  `lower_inclusive`, and `upper_inclusive` as needed. Normalize printed endpoint
  order so the lower bound is numerically smaller. Use null inclusivity when a
  dash-delimited range does not state it.
- Visible error bar or interval around a central point: `value`, `lower_bound`,
  and `upper_bound`, using absolute endpoints.

Storage components do not create new scientific variables. Every catalog
variable must appear in the layout at least once, including entries with empty
rows.

## Statuses and Notes

- `complete`: all identifiable discrete values were extracted.
- `partial`: reliable rows were emitted but some information was unreadable or
  omitted; notes must explain what is missing.
- `no_discrete_values`: no identifiable individual point or value exists.
- `needs_review`: discrete values appear to exist but cannot be assigned
  reliably; emit no rows and explain the ambiguity.
- `not_data_figure`: mirror that catalog status and emit no rows.

Use concise entry-level notes. Identify a problematic row or variable by its
row number or catalog variable name when useful; do not add per-cell evidence,
pixel coordinates, confidence scores, or duplicated provenance.
