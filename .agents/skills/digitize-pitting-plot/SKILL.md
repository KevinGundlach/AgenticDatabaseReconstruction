---
name: digitize-pitting-plot
description: Digitize discrete pitting-potential data from one staged plot image and its classifier metadata into simple series-oriented JSON. Use for accepted pitting plots with markers, bars, or explicit ranges; defer markerless or ambiguous geometry and do not enrich or normalize the extracted data.
---

# Digitize Pitting Plot

Convert exactly one staged `.jpg` and its same-basename classifier `.json` into
a separately validated digitization artifact.

## Workflow

1. Prepare a non-overwriting template:

   ```powershell
   uv run <skill-dir>/scripts/prepare_digitization.py `
     --image <path-to-plot.jpg>
   ```

   The default output is
   `digitized_pitting_potential_plots/<plot-name>.json`. `--metadata` and
   `--output` override the standard paths.
2. Read [output-contract.md](references/output-contract.md), inspect the image
   with vision, and use only the paired metadata and visible caption as context.
3. Change `digitization_status` from `unprocessed` and fill `plot_data` with one
   object per pitting-potential series. Inspect every relevant panel and every
   visible target series.
4. Validate the result:

   ```powershell
   uv run <skill-dir>/scripts/validate_digitization.py `
     --image <path-to-plot.jpg> `
     --input <path-to-digitization.json>
   ```

5. Report the status, series count, point count, notes, and output path. Do not
   claim completion when validation fails.

## Extraction boundary

- Record raw plotted values, labels, units, scales, and visible tags. Do not
  normalize units or names.
- Extract only series for which pitting potential is one coordinate. Do not
  transcribe ancillary corrosion, repassivation, or rate series.
- Each series contains its own x- and y-axis descriptions. This intentionally
  permits different axes in dual-axis or multipanel figures without a separate
  axis-reference system.
- Use named tags such as `material`, `test_solution`, or `heat_treatment` while
  preserving the visible text as the tag value. Use `unknown` when the role is
  unclear.
- Store a central plotted value in `x` or `y`. Store experimental error bars or
  ranges separately as lower and upper bounds, with their stated meaning. Do
  not put intervals into a two-element `x` or `y` list.
- Add the optional point `label` only when a point has its own visible label.
  Add the optional series `panel` only for a multipanel figure.
- Connecting and fitted lines do not create additional points. If the target
  exists only as a markerless trace, use `skipped` rather than sampling it.
- Use `partial` when some reliable target data were extracted, `needs_review`
  for unresolved interpretation, and `skipped` for intentionally unsupported
  geometry. Explain non-complete outcomes in `digitization_notes`.

## Integrity rules

- Preserve `paper_reference`, `source_chart_manifest`, and `plot_metadata` from
  the paired classifier JSON. Stable identifiers, not content hashes, connect
  the stages.
- Keep `series_id` values unique within the artifact. Exactly one axis in every
  extracted series must have `is_target: true`.
- Bounds represent experimental intervals, not digitization confidence. Do not
  add subjective confidence scores to digitized series or points.
- Do not consult the source paper, `mineru_output/`, `papers/`,
  `citrine_database/`, or evaluation artifacts. Context enrichment, semantic
  normalization, unit conversion, and CSV export are later stages.
- Never modify the paired classifier JSON or overwrite an existing output.

