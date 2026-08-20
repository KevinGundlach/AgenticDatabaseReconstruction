---
name: digitize-pitting-plot
description: Digitize discrete pitting-potential data from one staged plot image and its classifier metadata into auditable JSON. Use for accepted pitting plots with markers, bars, or explicit ranges; defer markerless or ambiguous geometry and do not enrich or normalize the extracted data.
---

# Digitize Pitting Plot

Convert exactly one staged plot image and its same-basename classifier JSON into
a separately validated digitization artifact.

## Workflow

1. Accept one `.jpg` in `pitting_potential_plots/`. Derive its metadata by
   replacing `.jpg` with `.json` unless an explicit metadata path is supplied.
2. Create a non-overwriting template:

   ```powershell
   uv run <skill-dir>/scripts/prepare_digitization.py `
     --image <path-to-plot.jpg>
   ```

   The default output is
   `digitized_pitting_potential_plots/<plot-name>.json`. Use `--metadata` or
   `--output` only when the standard paths do not apply.
3. Read [output-contract.md](references/output-contract.md) completely, inspect
   the image with vision, and use only the paired metadata and its visible
   caption as supporting evidence.
4. Replace the template's deliberately invalid `unprocessed` reason code and
   fill the digitization object. Inspect all relevant panels and account for
   every classifier `target_series` string.
5. Validate the finished artifact:

   ```powershell
   uv run <skill-dir>/scripts/validate_digitization.py `
     --image <path-to-plot.jpg> `
     --input <path-to-digitization.json>
   ```

6. Report the status, number of digitized pitting series and observations, any
   deferred target series, and the output path. Do not claim completion when
   validation fails.

## Extraction boundary

- Record raw visual values, labels, units, scales, and visible series tags.
  Do not normalize units or names.
- Extract only series for which pitting potential is one plotted coordinate.
  List recognizable ancillary series under `omitted_series` instead of
  digitizing them.
- Record all visible axes needed to interpret each relevant panel. Bind each
  extracted series to one x-axis and one y-axis; this supports plots with a
  second y-axis and plots where pitting potential is on the x-axis.
- Extract discrete markers, bars, and explicit ranges. Preserve experimental
  error-bar or range endpoints as absolute lower and upper values and transcribe
  their stated meaning when present.
- Connecting lines and fitted trend lines do not create observations. If the
  target exists only as a markerless trace, use `skipped` rather than sampling
  the trace.
- Use `partial` only when at least one discrete target observation is reliable.
  Put each unresolved classifier target in a structured issue.
- Use `needs_review` without observations when axes, series mapping, or mark
  semantics are ambiguous. Use `skipped` without observations for geometry
  intentionally unsupported by this version.

## Integrity rules

- Preserve the upstream `plot_metadata` verbatim. The helper scripts bind both
  inputs with SHA-256 hashes and portable relative paths.
- Give panels, axes, series, and observations stable unique IDs. Every
  observation must contain one value for each axis bound to its series.
- Experimental intervals are data; `confidence` is confidence in the visual
  transcription. Never use confidence as an error bar.
- Do not consult the source paper, `mineru_output/`, `papers/`,
  `citrine_database/`, or later evaluation artifacts. Context enrichment,
  semantic normalization, unit conversion, and CSV export are separate stages.
- Never write into the paired classifier JSON or replace an existing output.

