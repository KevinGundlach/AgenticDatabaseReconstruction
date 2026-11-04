# Full-paper extraction conventions

The JSON Schema is the field contract. All paper/experiment and nested context fields are required. Missing text is `""`, collections are `[]`, and unavailable numeric/measurement values are null. None means zero or an explicit scientific absence. Optional subfields inside a measurement may be omitted. `schema_version` is `"1.0"`; there is no `experiment_id`.

## One record per outcome

Each `experiments` entry combines an alloy, solution, procedure, and pitting outcome. Expand each eligible row of a results table or discrete plotted point into this structure, resolving its context from the whole paper. Do not create records for composition-table rows without a pitting outcome. Normally extract experiments reported in this paper; do not turn cited literature comparisons into new experiments unless requested. A source-reported no-pitting outcome can be a record with null `pitting_potential` and an explanatory `result_note`.

Treat a changing independent variable as row-specific context. For example, points in pitting potential versus molybdenum content must have their corresponding compositions, while points versus pH must have their corresponding pH. Copy shared details only when their applicability is established. Source sample identifiers can guide association without becoming extra schema fields.

## Measurements

Use objects such as `{"value": 300, "unit": "mV (SCE)"}`, `{"value": 300, "unit": "mV (SCE)", "plus_minus": 10}`, or `{"min": 280, "max": 320, "unit": "mV (SCE)"}`. At least one finite numerical `value`, `min`, or `max` is necessary. Use null for the whole measurement when none can be recovered; never emit `{}` or a unit-only object. Retain available units even when the numeric value comes from a plot. Missing units must not be invented; use `""` or omit `unit` and flag it if an extraction failure caused the loss.

- Preserve printed units and composition bases, e.g. wt%, at%, mol/L, mol/kg. Do not normalize them during extraction. Expand a genuinely shared table/axis unit into each relevant measurement.
- Potentials include the reported electrode reference in `unit`, e.g. `mV (SCE)`. Include filling-solution details only if reported. An electrode's KCl filling solution is not the tested electrolyte's composition.
- Use `plus_minus` only for a reported symmetric offset in the same unit as the central value. Do not reinterpret relative percentage uncertainty as an absolute offset. Use reported/digitized bounds when appropriate; asymmetrical endpoints need not be forced into symmetric uncertainty. Record a consequential statistical qualification in `result_note` since this version has no statistic/error-bar-type fields. Error bars are not digitization uncertainty.
- `min` and `max` are reported endpoints/bounds, not automatically observed extrema. Preserve inequalities or other qualifications in `result_note` (e.g. `Epit > 800 mV (SCE)`, represented with `min: 800`), without asserting pitting occurred at the bound. Do not replace a reported range by a calculated midpoint. Reported mean values remain means; do not calculate an unreported mean.
- Dimensionless pH may be a bare number, a measurement for a range/uncertainty, or null. Do not impose 0–14 bounds. All other measured amounts use measurement objects, not bare numbers.

## Alloy

`preparation` describes manufacturing, thermal/mechanical treatment, and specimen surface preparation, retaining process order and conditions in prose. Use `microstructure` for reported phases, grains, precipitates, or inclusions in the tested condition, not general corrosion explanations or post-test damage.

Composition includes only explicitly reported elements. Use `"balance"` only when stated; never calculate a residual or infer composition from a commercial alloy name. A mentioned element without an amount can have null `amount`; do not emit a fixed periodic-table list of nulls. Repeated units are acceptable in this pilot.

`material_class` allows `""`, `Fe Alloy`, `Al Alloy`, `HEA`, `NiCrMo Alloy`, and `Other`. Use a category only when supported by the paper's designation; use `""` when unresolved or competing labels cannot be resolved. `Other` indicates a known different class, not missing information. Do not invent additional labels.

## Electrolyte and procedure

Put mixing, deaeration/aeration gas and duration, pH adjustment, and continued gas flow in solution `preparation`. These are not solutes. Record only a stated solvent; do not assume water. Do not replace a named solution with a guessed recipe. If a paper only names seawater or another solution, retain that wording in solution `preparation` and leave unavailable component amounts unset as null/[] according to the schema.

Extract pH and chloride-ion concentration when the authors report them, including authors' explicitly reported calculations. Do not calculate missing pH or chloride concentration yourself or assume standard seawater values. A NaCl concentration is not itself an explicitly reported chloride concentration.

`test_temperature` is the test/electrolyte temperature, not a processing temperature. Keep an unquantified phrase like room temperature in `procedure_description`; leave the numeric field null.

Use applicable `test_types` labels and describe the complete reported sequence in `procedure_description`. A single `scan_rate` is appropriate only if it adequately describes the relevant scan. Describe multi-rate schedules in prose and leave the scalar null. `Steady state` is prose, not a numeric scan rate. For stepped tests, use `potential_step` and `step_hold_duration` when reported; do not divide them to invent a scan rate. `pitting_criterion` holds the authors' criterion, not one supplied by the extractor.

## Failure notes versus result notes

`failure_notes` is required text, normally `""`. It marks an extraction failure that makes the row unreliable or incomplete, not a scientific outcome and not every ordinary missing field. State the affected field and problem concisely; a local figure/table locator can disambiguate the issue without introducing a provenance system.

Examples:

- `"Figure 4(b): 350 mV point is visible, but its legend symbol cannot be assigned to alloy A or B."` Retain the potential and clearly shared conditions; leave unresolved alloy-specific details empty/null. Never copy an arbitrary alloy to complete the row.
- `"Table 3, sample B: reported pitting-potential digits are illegible after enlargement."` Retain supported context and use null for the potential. Do not silently omit this outcome.
- `"Table 2 and Figure 5 give conflicting pitting potentials for this condition; correspondence cannot be resolved."` Explain the conflicting values in `result_note`; do not silently average them or invent an exact resolution.

An unreported pH or microstructure alone is not a failure. A deliberate no-pitting observation, an inequality, a source-reported mean, or a known experimental limit belongs in `result_note`; these do not automatically require `failure_notes`. When an entire source cannot be enumerated or the paper is inaccessible, describe that limitation in the run report rather than fabricating placeholder rows. Never add `experiment_id` or unmodeled fields.
