---
name: digitize-corrosion-plots
description: Find figures in MinerU-parsed research papers that explicitly plot pitting potential, digitize their raw series and marker values, and generate validated observation-level CSV files and visual overlays. Use for pitting-potential-versus-composition, pH, temperature, or solution plots; do not use for inferring Epit from polarization curves or for current-density-only figures.
---

# Digitize Corrosion Plots

Create raw, evidence-linked observations with model vision, then delegate all
normalization to deterministic project code.

## Workflow

1. Locate the paper's MinerU Markdown and paper identifier.
2. Run figure discovery from the repository root:

   ```powershell
   uv run corrosion-plot-digitizer discover --markdown <paper.md> --paper-id <id> --output runs/<run-id>/figure_manifest.json
   ```

3. Review every explicit candidate and every `requires_agent_review` entry.
   Inspect its image, caption, and nearby Markdown. Reject current-density-only,
   repassivation-only, and polarization-curve figures.
4. For each accepted figure, read `prompts/digitize_pitting_plot.md` and
   `schemas/raw_figure_digitization.schema.json`, then write
   `runs/<run-id>/<paper-id>/figure_<id>/raw_digitization.json`.
5. Record all raw series in mixed figures and classify their metrics. Never
   convert at.% to wt.%, never estimate wt.%, and never add normalized fields.
6. Finalize the raw artifact:

   ```powershell
   uv run corrosion-plot-digitizer finalize --input <raw_digitization.json> --output-dir <figure-output-dir>
   ```

7. Inspect `digitization_overlay.png`. Correct raw values or calibration when
   overlay crosses do not coincide with markers, rerun finalization, and retain
   uncertainty rather than inventing precision.
8. Report accepted/rejected figures, included pitting-potential point counts,
   excluded series, warnings, and output paths.

## Integrity rules

- Treat the model artifact as untrusted raw observations.
- Preserve repeated markers at the same coordinate.
- Separate fresh, aged, or otherwise distinguished conditions.
- Include pitting-potential series in phase-one CSV output; record other series
  only so the finalizer can explicitly exclude and log them.
- Do not access `citrine_database/` while extracting or digitizing. Ground-truth
  data belongs only to later evaluation.
- Stop on schema or conversion errors. Do not bypass the finalizer.

Read [raw-contract.md](references/raw-contract.md) when constructing or debugging
a raw digitization artifact.
