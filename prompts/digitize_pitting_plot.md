# Digitize an explicit pitting-potential plot

Inspect the supplied figure, its caption, and nearby paper text. Produce one raw
JSON document conforming to `schemas/raw_figure_digitization.schema.json`.

## Scope

- Include every visually distinguishable marker in every series.
- Classify each series independently. Mixed figures may contain both
  `pitting_potential` and excluded metrics such as `repassivation_potential`.
- Treat fresh, aged, heat-treated, solution-specific, or other conditions as
  distinct series when the legend distinguishes them.
- Do not infer pitting potential from a polarization/current-density curve in
  phase one.
- Ignore explanatory arrows, construction lines, and schematic annotations.

## Raw values only

- Record x and y values in the units printed on the axes.
- Never convert at.% to wt.% and never estimate a wt.% value.
- Never add normalized fields or conversion identifiers.
- When the x-axis is binary-alloy composition, identify `base_element` and
  `solute_element`; deterministic Python will perform the conversion later.
- Record uncertainty and confidence. Do not use excess numeric precision beyond
  what the plot resolution supports.

## Calibration and QA

- Prefer two widely separated labeled ticks for each linear-axis calibration.
- Provide pixel coordinates when measurable. Otherwise provide tick calibration
  so the finalizer can project raw values into an overlay.
- Preserve repeated observations at the same x coordinate.
- If a marker cannot be separated from another marker, describe the ambiguity in
  its notes rather than inventing an observation.

