# Audit Report: Citrine Pitting-Potential Records for Reference 1

## Scope

This report compares the Reference 1 records in the Citrine `Pitting Potential` dataset with:

- [J. Horvath and H. H. Uhlig, "Critical Potentials for Pitting Corrosion of Ni, Cr-Ni, Cr-Fe, and Related Stainless Steels," J. Electrochem. Soc. 115 (1968), 791-795](../papers/1_J.%20Horvath,%20H.%20H.%20Uhlig,%20J.%20Electrochem.%20Soc.%20115%20(1968)_%20p.%20791.pdf)
- [Citrine source workbook](../citrine_database/CRA_database_Scientific_Data_Publication_12102020.xlsx), sheet `Pitting Potential`, Excel rows 334-351 (database record numbers 332-349)

Audit date: 2026-09-03

The audit covered all 18 records assigned to Reference 1. Values in charts and tables were checked visually against the paper. The repository's [figure catalog](../mineru_output/paper_1/paper_1_figures.json) and [figure extraction](../mineru_output/paper_1/paper_1_figure_extractions.json) were also validated and used as secondary cross-checks.

**Correction note (2026-09-03):** An earlier version of this report incorrectly claimed that Citrine inserted `not` into the definition of the steady-state critical potential. Direct reinspection of the typeset PDF confirms that the source itself says "pitting could not be observed." That finding and its associated recommendation have been retracted below.

## Executive summary

The 18 recorded pitting-potential values are consistent with the paper. The paper plots potentials on the hydrogen scale, while Citrine reports mV versus SCE. Using the conventional conversion

`E(SCE) ~= E(H2) - 0.241 V`, 

every Citrine value falls within 0-6 mV of the visually read source point. This is compatible with the precision of the plots and the paper's stated reproducibility of approximately +/-5 mV. No material numerical error was found in the pitting-potential values themselves.

Several other discrepancies were found:

| Severity | Finding | Affected records |
|---|---|---:|
| High | `pH = 7` is entered for every record, but the paper does not report the pH of the NaCl or NaBr test solutions. | 332-349 (18) |
| Medium | Several source observations that appear eligible for this dataset are absent. Seventeen unique candidate omissions were identified across Figures 1, 2, and 5. Table I independently repeats the pure-Ni value plotted in Figure 2. | Dataset coverage |
| Medium | Three nominally Mo-free observations are stored as containing 0.006 or 0.016 wt% Mo. The source identifies these points as zero Mo. | 339, 344, 346 |
| Medium | Most compositions are reported to three decimal places even though the paper exposes only rounded or graphical compositions. The precision cannot be traced to values printed in the paper. | 332, 334-349 (17) |
| Medium | The experiment's nitrogen deaeration is not represented in the record metadata, although the paper treats it as part of the test conditions. | 332-349 (18) |
| Medium | A generic heat-treatment paragraph containing several mutually alternative preparation routes is copied into every record rather than identifying the route applicable to each alloy. | 332-349 (18) |
| Low | `Scan Rate` contains the text `steady state`; this is an endpoint/protocol classification, not a scan rate. | 332-349 (18) |
| Low | NaBr records contain `[Cl-] = 0`, but no structured field captures the stated 0.1N bromide concentration. | 344-349 (6) |

## Record-level potential reconciliation

The source values below are approximate visual readings from Figures 5, 6, and 8. The `Implied source-scale` column converts the Citrine value back to the paper's hydrogen scale by adding 0.241 V. `Delta` is the Citrine value minus the approximate source value after conversion to SCE.

| Excel row | Record no. | Source | Test condition | Citrine composition of plotted variable (wt%) | Source composition shown | Source Epit, H2 scale (V) | Citrine Epit (mV SCE) | Implied source-scale (V) | Delta (mV) | Assessment |
|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---|
| 334 | 332 | Fig. 5 | 0.1N NaCl, 25 C | Ni 59.939 | Ni ~60 | 0.380 | 137 | 0.378 | -2 | Potential agrees; composition is overprecise |
| 335 | 333 | Fig. 6 | 0.1N NaCl, 25 C | Mo 0 | Mo 0 | 0.280 | 33 | 0.274 | -6 | Potential agrees within plot-reading uncertainty |
| 336 | 334 | Fig. 6 | 0.1N NaCl, 25 C | Mo 0.436 | Mo ~0.45-0.50 | 0.300 | 58 | 0.299 | -1 | Potential agrees; composition is overprecise |
| 337 | 335 | Fig. 6 | 0.1N NaCl, 25 C | Mo 0.954 | Mo ~1.0 | 0.340 | 98 | 0.339 | -1 | Potential agrees; composition is overprecise |
| 338 | 336 | Fig. 6 | 0.1N NaCl, 25 C | Mo 1.448 | Mo ~1.45 | 0.400 | 162 | 0.403 | +3 | Potential agrees; composition is overprecise |
| 339 | 337 | Fig. 6 | 0.1N NaCl, 25 C | Mo 1.904 | Mo ~1.9 | 0.530 | 290 | 0.531 | +1 | Potential agrees; composition is overprecise |
| 340 | 338 | Fig. 6 | 0.1N NaCl, 25 C | Mo 2.418 | Mo ~2.4 | 0.720 | 481 | 0.722 | +2 | Potential agrees; composition is overprecise |
| 341 | 339 | Fig. 6 | 0.1N NaCl, 0 C | Mo 0.006 | Mo 0 | 0.800 | 558 | 0.799 | -1 | Potential agrees; Mo should be zero |
| 342 | 340 | Fig. 6 | 0.1N NaCl, 0 C | Mo 0.443 | Mo ~0.45-0.50 | 0.500 | 253 | 0.494 | -6 | Potential agrees within plot-reading uncertainty |
| 343 | 341 | Fig. 6 | 0.1N NaCl, 0 C | Mo 0.955 | Mo ~1.0 | 0.420 | 176 | 0.417 | -3 | Potential agrees; composition is overprecise |
| 344 | 342 | Fig. 6 | 0.1N NaCl, 0 C | Mo 1.448 | Mo ~1.45 | 0.380 | 139 | 0.380 | 0 | Potential agrees; composition is overprecise |
| 345 | 343 | Fig. 6 | 0.1N NaCl, 0 C | Mo 1.911 | Mo ~1.9 | 0.320 | 78 | 0.319 | -1 | Potential agrees; composition is overprecise |
| 346 | 344 | Fig. 8 | 0.1N NaBr, 0 C | Mo 0.006 | Mo 0 | 0.420 | 179 | 0.420 | 0 | Potential agrees; Mo should be zero |
| 347 | 345 | Fig. 8 | 0.1N NaBr, 0 C | Mo 0.443 | Mo ~0.43-0.50 | 0.310 | 68 | 0.309 | -1 | Potential agrees; composition is overprecise |
| 348 | 346 | Fig. 8 | 0.1N NaBr, 25 C | Mo 0.016 | Mo 0 | 0.540 | 295 | 0.536 | -4 | Potential agrees; Mo should be zero |
| 349 | 347 | Fig. 8 | 0.1N NaBr, 25 C | Mo 0.449 | Mo ~0.45 | 0.525 | 281 | 0.522 | -3 | Potential agrees; composition is overprecise |
| 350 | 348 | Fig. 8 | 0.1N NaBr, 25 C | Mo 1.446 | Mo ~1.45 | 0.510 | 265 | 0.506 | -4 | Potential agrees; composition is overprecise |
| 351 | 349 | Fig. 8 | 0.1N NaBr, 25 C | Mo 2.395 | Mo ~2.4 | 0.470 | 226 | 0.467 | -3 | Potential agrees; composition is overprecise |

### Interpretation of the potential comparison

- The database consistently applies an approximately 241 mV hydrogen-to-SCE offset. This is appropriate, but the conversion and reference-electrode normalization should be explicit in the provenance metadata.
- The largest differences are 6 mV for records 333 and 340. Because the source values must be read from plotted markers and the authors report roughly +/-5 mV reproducibility, these are not persuasive evidence of erroneous pitting potentials.
- The database correctly excludes the 0 C observations for which the paper reports no definite pitting potential: approximately 2.4% Mo in NaCl and approximately 1.43% Mo and above in NaBr. Those tests entered the transpassive region without an established breakdown potential.
- The database also correctly labels its included values as steady-state values rather than mixing them with the paper's shorter-term `Vc'` values.

## Detailed discrepancies

### Transcription check: the word `not` is present in the source

The Citrine text states that Vc is:

> The lowest potential for which pitting **could not be observed** after a 10-hr or longer period ... was considered the steady-state critical pitting potential, Vc.

The typeset paper contains the same wording: "The lowest potential for which pitting could not be observed after a 10-hr or longer period of constant polarization was considered to be the steady-state value Vc." The database did **not** insert the word `not`; this is a faithful transcription. Although the sentence may appear counterintuitive when compared with a conventional threshold definition, any possible source-level ambiguity is not a Citrine transcription discrepancy and is outside the scope of this audit.

### 1. Unsupported pH values

All 18 records contain `pH = 7`. The paper specifies 0.1N NaCl for most experiments and 0.1N NaBr for the bromide comparison, but it does not report a measured or adjusted pH for these solutions anywhere in the five-page article. Neutral pH may have been inferred from an unadjusted salt solution, but it is not a reported experimental value.

Under a strict source-provenance standard, these entries should be `NA` or `not reported`, not 7. If an inferred value is retained, it should be explicitly marked as inferred rather than transcribed.

### 2. Composition precision and zero-Mo points

The paper says the compositions were chemically determined, but it does not print the exact chemical-analysis values used in the Citrine rows. Figures 5, 6, and 8 show rounded graphical coordinates, and the prose refers to rounded values such as 1.43%, 1.45%, 2%, 2.4%, and 3.2% Mo. Consequently, values such as 0.436, 0.443, 0.449, 1.448, and 2.418 wt% cannot be independently recovered from the publication.

The varying third-decimal values for nominally equivalent alloys across temperature or solution series look like unrounded digitizer x-coordinates, not source-reported analytical precision. This is especially clear for three points shown as the Mo-free baseline:

| Record no. | Citrine Mo (wt%) | Source representation | Recommended correction |
|---:|---:|---:|---:|
| 339 | 0.006 | 0 | 0 |
| 344 | 0.006 | 0 | 0 |
| 346 | 0.016 | 0 | 0 |

Because Fe is calculated as the balance, correcting these points to zero Mo would also change their nominal Fe values from 71.994 or 71.984 to 72 wt% for the 15Cr-13Ni alloy.

Record 332 presents the same precision issue: Figure 5 supports approximately 60% Ni and 25% Fe, not specifically 59.939% Ni and 25.061% Fe.

### 3. Incomplete environmental metadata

The experimental section says that the 0.1N NaCl solution was deaerated with purified nitrogen before the measurement, and that nitrogen flow was stopped during the actual measurement. This condition is important to interpretation but is absent from the Citrine solution and method fields.

For the six NaBr observations, `[Cl-] = 0` is chemically reasonable, but the schema does not preserve the positive bromide concentration of 0.1N as a structured quantity. The solution name contains `0.1N NaBr`, so the information is human-readable but not available in a corresponding ionic-concentration field.

### 4. Heat-treatment field is not record-specific

Every Reference 1 row repeats one paragraph describing several different specimen-preparation routes:

- cold rolling and annealing for Ni-Cr, Ni-Mo, and Cr-Fe alloys;
- machining high-Cr alloys from forged bars; and
- cold swaging lower-Cr alloys and stainless steels before annealing.

These are alternatives for different alloy families, not a single treatment applied to every record. For the 15Cr-13Ni-Mo and 15Cr-Ni series that supply the Citrine rows, the stored field does not isolate the applicable preparation route and therefore overstates what is known for each individual record.

### 5. `Scan Rate` is not a scan rate

The value `steady state` appears in the `Scan Rate` column for all 18 rows. The paper did not use a conventional continuous potential scan for these measurements. It first stepped the potential in 50 mV increments at five-minute intervals to locate an approximate critical value, then used long potentiostatic holds of ten hours or more to determine the steady-state value.

`Steady state` is therefore a measurement classification, not a rate. A source-faithful representation would leave scan rate unreported/not applicable and store the step protocol and long-hold criterion separately.

## Coverage audit: candidate missing observations

The database includes all finite steady-state values visible in Figures 6 and 8, but it does not include most of the other steady-state critical-potential observations presented in the paper.

| Source | Source observations apparently eligible as pitting potentials | Included for Ref. 1 | Candidate omissions | Notes |
|---|---:|---:|---:|---|
| Table I | 1 present-study value for pure Ni | 0 | 0 additional | Ni, approximately 0.28 V on H2 scale; this is the same observation as the zero-Cr point in Figure 2, not an additional record |
| Figure 1 | Approximately 5 finite Cr-Fe pitting points | 0 | 5 | Higher-Cr points without pitting/transpassive behavior should remain excluded |
| Figure 2 | 8 steady-state Cr-Ni points | 0 | 8 | Open-circle `Vc` series; the solid-circle `Vc'` series should not be substituted |
| Figure 5 | 5 steady-state 15Cr-Fe-Ni points | 1 | 4 | Only the approximately 60% Ni point appears as record 332 |
| Figure 6 | 11 finite steady-state NaCl points | 11 | 0 | Complete for plotted finite values |
| Figure 8 | 6 finite steady-state NaBr points | 6 | 0 | Complete for plotted finite values |
| **Unique total** | **35 candidate finite values** | **18** | **17** | The Table I/Figure 2 pure-Ni duplicate is counted once; inclusion remains subject to the database's documented policy |

These 17 unique observations are classified as *candidate* omissions because the Citrine publication's selection rules may intentionally exclude some alloy families or summary-table values. Nevertheless, no source-level reason is evident for including one Figure 5 point while omitting the other four, or for omitting the complete steady-state series from Figures 1 and 2. These records merit a targeted inclusion-policy review.

Figures 3, 4, and 7 contain continuous polarization curves rather than a discrete table of steady-state pitting potentials and should not be automatically digitized as additional database records. Likewise, the paper's `Vc'` values are short-term onset estimates and should remain distinct from the steady-state `Vc` values represented here.

## Recommended corrections and follow-up

1. Replace `pH = 7` with `NA`/`not reported`, or add an explicit provenance flag identifying the value as inferred.
2. Set Mo to 0 for records 339, 344, and 346; update Fe balance to 72 wt% if the database continues to calculate the balance.
3. Round graph-derived compositions to the precision supported by the axes, or preserve the digitized values in a separate field that records digitization uncertainty and clearly distinguishes them from chemical-analysis values.
4. Add the nitrogen-deaeration condition to the test metadata.
5. Move `steady state` out of `Scan Rate`; record the 50 mV/five-minute exploratory steps and the ten-hour-or-longer potentiostatic criterion in dedicated protocol fields.
6. Split the generic heat-treatment paragraph into alloy-specific preparation records, or explicitly mark it as contextual source text rather than a treatment assigned to every specimen.
7. Add a bromide concentration field, or a general anion/concentration representation, for the NaBr records.
8. Review the 17 unique candidate omissions from Figures 1, 2, and 5 against the project's inclusion rules; use the matching Table I pure-Ni entry as a cross-check.
9. Preserve the original hydrogen-scale values and the H2-to-SCE conversion as explicit provenance rather than only storing the converted result.

## Overall assessment

**Numerical pitting potentials: pass.** The 18 values are faithful digitizations after reference-electrode conversion, within the resolution of the source figures.

**Conditions and provenance: needs correction.** The unsupported pH entries are substantive errors. The omitted deaeration condition, non-specific heat-treatment text, misuse of the scan-rate field, and unjustified compositional precision reduce traceability. The `could not be observed` wording, however, matches the paper and is not a database error.

**Coverage: incomplete or undocumented.** The database captures Figures 6 and 8 well but omits 17 other candidate finite steady-state values without an evident source-based rationale.
