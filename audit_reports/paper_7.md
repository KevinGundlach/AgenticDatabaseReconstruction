# Audit Report: Citrine Pitting-Potential Records for Reference 7

## Scope

This report compares all 12 Reference 7 records in the Citrine `Pitting Potential` sheet with:

- [H. Bohni and H. H. Uhlig, J. Electrochem. Soc. 116 (1969), 906](<../papers/7_H. Bohni, H. H. Uhlig, J. Electrochem Soc. 116 (1969)_ p. 906.pdf>)
- [Citrine source workbook](../citrine_database/CRA_database_Scientific_Data_Publication_12102020.xlsx), Excel rows 801-812 (record numbers 803-814)

Audit date: 2026-09-03

Workbook evidence: 【CRA_database_Scientific_Data_Publication_12102020.xlsx:Pitting Potential:A801:AM812】

The relevant graph, table, composition analysis, and experimental method were checked visually. The repository's [figure catalog](../mineru_output/paper_7/paper_7_figures.json) and [figure extraction](../mineru_output/paper_7/paper_7_figure_extractions.json) were used as secondary cross-checks.

## Executive summary

All 12 potentials are consistent with Figure 1 and Table I after converting the paper's hydrogen-scale potentials to SCE. The audit nevertheless found a chemically impossible chloride entry for sodium perchlorate, a solution-name typo, missing Mg composition values, an unsupported pH assignment, and a misleading scan-rate representation. One record is explicitly secondary data cited by the paper rather than a measurement made in Reference 7.

| Severity | Finding | Affected records |
|---|---|---:|
| High | 0.1M sodium perchlorate is assigned `[Cl-] = 0.1 M`; perchlorate contains no chloride. | 810 |
| Medium | Mg reported in the metal analyses is omitted from 11 records. | 803-813 |
| Medium | The nominal `99.4% Al` label is combined with listed impurities, making the stored composition sum exceed 100%. | 812 |
| Medium | `pH = 7` is not reported for these tests. | 803-814 |
| Medium | A continuous scan rate of 0.167 mV/s is assigned, but the method used 50 mV steps with five-minute intervals followed by long potentiostatic holds. | 803-814 |
| Medium | The 0.5M NaCl point is explicitly attributed in Table I to Bond et al., not measured in Reference 7. | 811 |
| Low | `NaCIO4` uses capital `I` instead of lowercase `l`; the compound should be `NaClO4`. | 810 |

## Potential reconciliation

### Figure 1: high-purity aluminum in 0.1M NaCl

Records 803-807 correspond to 0, 15, 25, 32, and 40 C. Citrine stores approximately -646, -645, -649, -653, and -667 mV SCE. After adding the approximately 0.24 V SCE-to-hydrogen offset, these align with the plotted source values near -0.40, -0.40, -0.41, -0.41, and -0.43 V on the hydrogen scale.

The numerical agreement is good, but values carried to thousandths of a millivolt imply far more precision than the printed graph supports. They should be rounded to an uncertainty appropriate for graph digitization.

### Table I

| Record(s) | Source condition | Citrine Epit (mV SCE) | Assessment |
|---:|---|---:|---|
| 808-809 | 0.1M NaBr at 25 and 0 C | -534, -564 | Consistent after reference conversion |
| 810 | 0.1M NaClO4 at 25 C | -244 | Potential consistent; chloride field is wrong |
| 811 | 0.5M NaCl at 25 C | -744 | Numerically consistent; source marks it as Bond et al. data |
| 812-814 | 99.4% Al, 1.3% Mn-Al, and 2.4% Mg-Al in 0.1M NaCl | -654, -694, -684 | Consistent after reference conversion |

## Composition discrepancies

The source metal analyses include Mg values that Citrine drops:

- approximately 0.0005 wt% Mg for the 99.99% Al material used in records 803-811;
- 0.0004 wt% Mg for the material labeled 99.4% Al in record 812; and
- 0.001 wt% Mg for the 1.3% Mn-Al alloy in record 813.

Record 812 also stores Al = 99.4 wt% alongside Fe, Si, Cr, Mn, and Cu impurities, totaling about 100.066 wt% even before the missing Mg is restored. `99.4% Al` is the material's nominal label, not an independent analyzed Al value to be summed with every impurity. Based on the listed impurities, a calculated Al balance would be approximately 99.3336 wt%.

Record 813's calculated Al balance appears to account for the 0.001% Mg even though the Mg field itself is blank. This creates an internally non-transparent composition.

## Conditions, method, and provenance

- The paper uses a potentiostatic step procedure: advance by 50 mV, wait five minutes, then determine the steady-state threshold through long constant-potential observations. Dividing 50 mV by five minutes yields 10 mV/min, but this is not a continuous scan and should not be stored unqualified as 0.167 mV/s.
- The paper does not specify that these solutions had pH 7. It discusses pH behavior generally, so exact pH 7 entries are unsupported.
- The paper reports potentials on the hydrogen scale; Citrine consistently applies an SCE conversion. That normalization is reasonable but should be explicit in provenance.
- The experimental electrolyte was deaerated. This is not adequately represented in the concise database method metadata.
- Table I explicitly labels the 0.5M NaCl value as coming from Bond et al. Citrine's `Reference = 7` obscures that secondary provenance. Other secondary comparison values in the same table are not included, making selection inconsistent.

## Coverage audit

The database includes the five Figure 1 points and the relevant present-study Table I values, plus the one Bond et al. comparison. No clear primary pitting-potential omission was found in the audited figure/table set. The main coverage problem is provenance consistency: either secondary values should point to their original reference and follow a documented selection rule, or record 811 should not be attributed solely to Reference 7.

## Recommended corrections

1. Correct record 810 to `NaClO4` and set `[Cl-] = 0`.
2. Restore the source Mg values in records 803-813.
3. Treat `99.4% Al` as a nominal material label or recalculate record 812's Al balance; do not retain a composition over 100%.
4. Replace pH 7 with `NA`/`not reported`, or mark it inferred.
5. Replace the scan-rate value with a structured stepped-potential protocol and long-hold criterion.
6. Preserve the original hydrogen-scale values and reference conversion.
7. Reassign or cross-link record 811 to the Bond et al. primary source and document the policy for secondary values.
8. Round graph-derived potentials to defensible precision.

## Overall assessment

**Potential values: pass.** All 12 agree with the source within graph-reading and reference-conversion uncertainty.

**Chemistry, method, and provenance: needs correction.** The perchlorate chloride value is unequivocally wrong; Mg values, pH status, measurement protocol, and secondary sourcing also require repair.

**Coverage: essentially complete for primary values reviewed, but provenance is inconsistent.**
