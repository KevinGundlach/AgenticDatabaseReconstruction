# Raw digitization contract

The raw JSON is the boundary between model interpretation and deterministic
normalization.

## Model-owned fields

- Figure identity, caption, axis labels, printed units, and reference electrode.
- Series label, condition, metric classification, and marker type.
- Raw x/y coordinates, pixel coordinates when measurable, uncertainty, and
  confidence.
- Binary composition context: base and solute element names only.

## Code-owned fields

- Weight-percent values and normalized composition objects.
- Potentials normalized to mV vs. SCE.
- Conversion identifiers and pinned physical constants.
- Inclusion filtering, CSV serialization, validation result, and overlay.

Any raw key containing `normalized`, `weight_percent`, `wt_percent`, or
`conversion_id` causes finalization to fail. This is intentional: delete the
model-supplied normalized value and rerun the deterministic finalizer.

For a mixed plot such as Paper 80 Figure 1, represent `Ep`, `Ep^a`, and `ER` as
separate series. Classify the first two as `pitting_potential` and `ER` as
`repassivation_potential`. The finalizer includes only the pitting-potential
series while recording why `ER` was excluded.

