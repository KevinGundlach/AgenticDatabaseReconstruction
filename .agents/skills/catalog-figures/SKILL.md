---
name: catalog-figures
description: Catalog every MinerU chart and table in one paper by identifying the plot-specific Tidy Data variables needed for later tabularization. Use for semantic figure inventory and variable mapping; do not use to extract data values.
---

# Catalog Figures

Create one complete, source-traceable catalog of the variables represented in
every MinerU chart and table from a paper. Catalog variable definitions only;
leave all category levels, constants, plotted points, and table cells for a
later tabularization skill.

## Workflow

1. Accept one `mineru_output/paper_<reference>` folder. Build the catalog
   skeleton without overwriting existing work:

   ```powershell
   uv run <skill-dir>/scripts/identify_figures.py --input_path <paper-folder>
   ```

   The folder must contain exactly one `*_content_list_v2.json` and one
   `*_origin.pdf`.
2. Read [catalog.schema.json](references/catalog.schema.json). Read the entire
   source PDF before cataloging, focusing on terminology, abbreviations, units,
   and experimental design. Do not save a paper summary or collections of
   nearby paragraphs.
3. Inspect every chart and table image directly. Use the PDF to resolve meaning
   and to add conditions only when their application to that figure is clear.
4. Replace every skeleton entry's null status. Split a multipanel chart into
   separate entries that retain the same `source_figure_id` and provenance.
   Use its printed panel label, or `panel_1`, `panel_2`, and so on in reading
   order when labels are absent. Give each panel a `catalog_id` such as
   `<source_figure_id>__panel_a` or `<source_figure_id>__panel_1`.
5. Map each variable to `vocabularies/variables.json`. Reuse an entry only when
   its definition matches. Add a concise, source-independent entry when a clear
   concept is genuinely new; never add paper aliases or units to the global
   vocabulary and never broaden an existing definition to force a match.
6. Validate the completed catalog:

   ```powershell
   uv run <skill-dir>/scripts/validate_catalog.py `
     --input <paper-folder>/paper_<reference>_figures.json `
     --vocabulary <project-root>/vocabularies/variables.json
   ```

Do not claim completion when validation fails.

## Identifying variables

Imagine the future tidy table for the figure. Include a concept when it would
need a column because it varies across observations, series, rows, or columns;
or because it is a scientifically meaningful condition needed to interpret the
observations and can vary in comparable figures, even if constant here.

- Classify each variable only as `condition` or `measured`.
- Preserve the exact printed variable label when one exists. Use null when the
  variable is clear but has no explicit label.
- Preserve the figure-specific unit. Use `""` for a genuinely unitless
  variable and null when the unit is unstated or unknown. Never infer a unit.
- Treat element quantities as separate canonical variables: for example,
  `Mo wt%` maps to `molybdenum` with unit `wt%`, while `Cr wt%` maps to
  `chromium` with the same local unit.
- Attach an uncertainty descriptor to a measured variable when the figure
  reports error bars or an interval. Preserve the stated meaning; use
  `unspecified` when the source does not define it.
- When meaning remains ambiguous after reading the paper, retain the raw label,
  set `canonical_name` to null, mark the entry `needs_review`, and continue.

Axes, secondary-axis placement, marker and line styles, color, tick ranges, and
legend placement are presentation encodings, not scientific variables. They
may help interpret a figure but must not appear in the catalog. Do not record
variable values, category levels, constants, data points, or table cells.

Use `not_data_figure` only for an obvious MinerU false detection. Account for
every source block at least once.
