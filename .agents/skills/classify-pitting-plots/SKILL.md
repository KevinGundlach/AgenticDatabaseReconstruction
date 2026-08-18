---
name: classify-pitting-plots
description: Screen charts from one paper's MinerU output folder and classify every chart as an explicit, readily digitizable pitting-potential plot, a rejection, or needing review. Use when given a paper_N MinerU directory and asked to find Epit, Ep, breakdown-potential, or pitting-potential plots before digitization; exclude polarization curves and figures that require inferring pitting potential.
---

# Classify Pitting Plots

Create a deterministic chart manifest from MinerU JSON, inspect every chart with
vision and local context, and save an auditable semantic classification.

## Workflow

1. Accept one MinerU paper directory such as `mineru_output/paper_80`.
2. Run the bundled extractor with uv to use an available Python 3.11+ 
   interpreter in the project's local virtual environment. 
    
   ```powershell
   uv run <skill-dir>/scripts/extract_chart_manifest.py <paper-folder>
   ```

   This writes `<paper-folder>/paper_<reference>_charts.json`. Do not discover
   figures by parsing Markdown or by applying caption keywords.
3. Create a non-overwriting classification template that copies every chart's
   stable fields and marks it with the deliberately invalid `unclassified`
   reason code:

   ```powershell
   uv run <skill-dir>/scripts/prepare_classification.py `
     --manifest <paper-folder>/paper_<reference>_charts.json
   ```

   If the output already exists, preserve it; the script stops instead of
   overwriting prior work.
4. Read the manifest and inspect the image for every entry in `charts`. Treat the
   image as primary evidence; use its caption, footnote, section title, and
   nearby paragraphs as supporting evidence. If evidence remains insufficient,
   consult `source_markdown` selectively.
5. Move every template entry into exactly one of `simple_plots`,
   `rejected_charts`, or `needs_review`. For every accepted simple plot, record
   the visible x- and y-axis labels, units, and scales. Read
   [output-contract.md](references/output-contract.md) before writing
   `<paper-folder>/paper_<reference>_simple_plots.json`.
6. Update the summary and validate completeness and provenance:

   ```powershell
   uv run <skill-dir>/scripts/validate_simple_plots.py `
     --manifest <paper-folder>/paper_<reference>_charts.json `
     --input <paper-folder>/paper_<reference>_simple_plots.json
   ```

7. Report all three counts and both output paths. Do not claim success if the
   validator fails.

## Classification rules

- Accept when pitting potential or corrosion breakdown potential is itself a
  plotted variable against composition, concentration, pH, temperature,
  environment, alloy condition, or another independent quantity, and target
  values are represented by digitizable markers, bars, or an unambiguous trace.
- Accept a mixed or multipanel figure only when at least one pitting-potential
  series is directly plotted and separable. Record the relevant panels and
  target series.
- For each accepted plot, transcribe the visible axis labels and units rather
  than silently normalizing them. Set each scale to `linear`, `log`,
  `categorical`, or `unknown`.
- Reject potential-versus-current or current-density polarization curves even
  if nearby prose discusses pitting potential. Reject any figure that requires
  domain inference to obtain Epit.
- Reject current-density-only, repassivation-only, corrosion-potential-only,
  open-circuit-potential-only, and critical-pitting-temperature-only plots when
  pitting potential is not also directly plotted.
- Reject tables, micrographs, schematics, and non-plots that MinerU mislabeled
  as charts.
- Use `needs_review` for missing, unreadable, or genuinely ambiguous evidence.
  Do not force a binary decision.

## Integrity rules

- Inspect every chart image; never accept or reject solely from the caption.
- Account for every manifest `chart_id` exactly once and preserve its image path
  and flattened caption verbatim in the classification file.
- Include valid `x_axis` and `y_axis` objects on every accepted entry. Do not add
  axis objects to rejected or review entries.
- Do not access `citrine_database/` or any later evaluation artifact while
  classifying.
- Treat MinerU's `chart` label as a candidate filter, not ground truth. The
  standard workflow intentionally does not audit entries labeled `image`.
- An empty paper is valid: write all three classification arrays empty and run
  the validator.
