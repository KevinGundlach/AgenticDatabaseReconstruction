---
name: catalog-figures
description: Catalog the data fields visibly represented in every MinerU chart and table from one paper, using targeted Markdown only to interpret visible labels. Use before tabularization; do not extract values or add contextual conditions.
---

# Catalog Figures

Create a source-traceable inventory of the data fields visibly represented in
every MinerU chart and table from one paper. The image determines which fields
exist. The MinerU Markdown may only resolve the meaning of a field already
evidenced by the image.

## Workflow

Run every command from the project root. Keep uv's cache inside the writable
workspace so Codex does not use its normally inaccessible user cache.

1. Accept one `mineru_output/paper_<reference>` folder and read
   [catalog.schema.json](references/catalog.schema.json). Build the schema-v2
   skeleton without overwriting existing work:

   ```powershell
   uv --cache-dir .uv-cache run --frozen <skill-dir>/scripts/identify_figures.py --input_path <paper-folder>
   ```

   The folder must contain exactly one `*_content_list_v2.json` and one
   Markdown file. The skeleton records `input_path`, `source_content_list`, and
   `source_markdown` as POSIX-style paths relative to the project root. Do not
   open, parse, or extract text from a PDF.
2. Inspect every chart and table image directly. For each image, make one
   provisional list containing only fields visibly evidenced by axis labels,
   row or column headers, legend titles or unmistakable untitled groupings,
   panel titles, or repeated labeled data annotations. Preserve printed labels
   and units exactly.
3. Collect the visible labels whose meanings are unclear. Search the source
   Markdown for those exact labels and read only the shortest relevant
   passages. Markdown may expand or disambiguate an existing visible field; it
   must not introduce a field, unit, value, or condition. Copy the shortest
   exact supporting excerpt into `interpretation_evidence` when Markdown
   determines `interpreted_name`.
4. Treat the skeleton's root provenance and each entry's `source_figure_id`,
   `type`, `page_number`, `item_index`, `image_path`, and `caption` as
   immutable. In particular, preserve each MinerU-generated caption verbatim;
   do not retype, normalize, repair, or reconstruct it. Replace every skeleton
   entry's null status. Split a multipanel chart into separate entries that
   retain the same `source_figure_id` and provenance.
   Use its printed panel label, or `panel_1`, `panel_2`, and so on in reading
   order when labels are absent. Give each panel a `catalog_id` such as
   `<source_figure_id>__panel_a` or `<source_figure_id>__panel_1`.
5. Fill the catalog once, using concise notes only for unresolved or structural
   ambiguity. Do not read or update any global variable vocabulary.
6. Validate the completed catalog and fix only reported errors:

   ```powershell
   uv --cache-dir .uv-cache run --frozen <skill-dir>/scripts/validate_catalog.py `
     --input <paper-folder>/paper_<reference>_figures.json
   ```

Do not claim completion when validation fails.

## What counts as a variable

A variable is a data field visibly represented by the chart or table: a
property, measurement, identifier, or grouping for which the visual assigns
values or categories to observations, series, rows, or columns.

- Include a labeled axis, row or column header, legend dimension, panel
  dimension, or repeated labeled quantity. A table column remains a variable
  even when all visible cells happen to contain the same value.
- An untitled grouping may use `source_label: null` only when its visible
  entries make its meaning unambiguous. Otherwise mark the figure
  `needs_review`, explain the ambiguity, and do not invent a field.
- `interpreted_name` is a lower-snake-case, paper-local interpretation, not a
  global canonical name. Use `interpretation_source: visual` when the image
  itself makes the meaning clear, `markdown` when an exact Markdown excerpt is
  needed, and `unresolved` when a printed label remains ambiguous.
- Preserve the visually printed unit. Use `""` for a genuinely unitless field
  and null when the visual does not state a unit. Never take a unit from the
  caption or prose.
- Attach uncertainty only when error bars or an interval are visible. Preserve
  its stated meaning; use `unspecified` when the visual does not define it.

Do not record individual values, category levels, constants, plotted points,
table cells, colors, marker or line styles, tick ranges, or legend placement.
Captions are provenance. They may resolve an existing visual label, but they
must never create a variable or add a condition that applies uniformly to the
figure.

Examples:

- A visible `Epit` axis is a variable. If the Markdown explicitly identifies
  it as pitting potential, record `interpreted_name: pitting_potential`,
  `interpretation_source: markdown`, and the shortest exact defining excerpt.
- A legend headed `Solution` is a `test_solution` field. `1.0 M NaCl` is a
  category value for later extraction, not another variable.
- If `1.0 M NaCl` appears only in the caption and applies to every point, omit
  it. A later context-enrichment stage may attach it to extracted observations.
- A visible `Temperature (°C)` table column is a variable even when every row
  displays the same temperature.

Use `not_data_figure` only for an obvious MinerU false detection. Account for
every MinerU chart and table block at least once.
