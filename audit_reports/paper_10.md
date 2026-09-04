# Audit Report: Citrine Pitting-Potential Records for Reference 10

## Scope

This report compares both Reference 10 records in the Citrine `Pitting Potential` sheet with:

- [W. H. Richardson and P. Guha, "Improved Ferritic-Austenitic Stainless Steel" (1979), 167-171](<../papers/10_W.H. Richardson & P. Guha (1979) Improved Ferritic-Austenitic Stainless Steel, British Corrosion Journal, 167-171.pdf>)
- [Citrine source workbook](../citrine_database/CRA_database_Scientific_Data_Publication_12102020.xlsx), Excel rows 309-310 (record numbers 307-308)

Audit date: 2026-09-03

Workbook evidence: 【CRA_database_Scientific_Data_Publication_12102020.xlsx:Pitting Potential:A309:AM310】

Table I, Figure 3, its caption, and the experimental discussion were checked visually. The repository's [figure catalog](../mineru_output/paper_10/paper_10_figures.json) and [figure extraction](../mineru_output/paper_10/paper_10_figure_extractions.json) were used as secondary cross-checks.

## Executive summary

The two stored pitting potentials—860 and 160 mV SCE—are plausible approximate readings of Figure 3 for alloys 5 and 6. Both database compositions, however, omit the roughly 3 wt% Cu printed in Table I and therefore overstate calculated Fe by the same amount. The nitrogen-deaerated condition is also missing. No eligible discrete pitting-potential series beyond these two alloys was found.

| Severity | Finding | Affected records |
|---|---|---:|
| High | Cu is omitted: Table I reports 3.04 wt% for alloy 5 and 3.15 wt% for alloy 6. | 307-308 |
| High | Fe was calculated without Cu and is therefore too high by 3.04 and 3.15 percentage points. | 307-308 |
| Medium | Figure-derived endpoints are stored as exact values without a digitization/interpretation qualifier. | 307-308 |
| Medium | Figure 3 specifies N2-purged 3% NaCl, but nitrogen deaeration is absent from database method/solution metadata. | 307-308 |
| Low | `[Cl-] = 0.53 M` is calculated rather than printed in the paper; its mass-percent and density assumptions are undocumented. | 307-308 |

## Record reconciliation

| Record | Source alloy | Source composition relevant to discrepancy (wt%) | Citrine Epit | Source Figure 3 | Assessment |
|---:|---|---|---:|---|---|
| 307 | Alloy 5 | N 0.16, Cr 25.1, Ni 5.00, Mo 2.46, **Cu 3.04**, C 0.065 | 860 mV SCE | breakdown/plateau near 0.86-0.90 V | Plausible graph reading; Cu missing |
| 308 | Alloy 6 | N 0.05, Cr 25.3, Ni 5.23, Mo 2.44, **Cu 3.15**, C 0.032 | 160 mV SCE | breakdown/plateau near 0.16-0.20 V | Plausible graph reading; Cu missing |

The paper does not print 860 or 160 mV as tabulated numbers. They are interpretations of continuous polarization curves. The values are reasonable, but provenance should say they were digitized/visually inferred from Figure 3 rather than directly transcribed.

### Corrected Fe balances

| Record | Citrine Fe (wt%) | Missing Cu (wt%) | Fe balance including Cu (wt%) |
|---:|---:|---:|---:|
| 307 | 67.215 | 3.04 | 64.175 |
| 308 | 66.948 | 3.15 | 63.798 |

These balances assume the database continues its current practice of calculating Fe as 100 minus the reported alloying elements.

## Conditions and method

- Figure 3 specifies 3% NaCl, nitrogen purging, and 30 C. Temperature and solution are correctly stored; nitrogen purging is missing.
- The paper states that potentiostatic polarization followed the ASTM G1 Committee recommendations and that all potentials refer to SCE. Citrine's `ASTM G1` text is abbreviated but traceable to the source; it is not a transcription error.
- The source gives no pH or scan rate for Figure 3. Citrine correctly stores both as `NA`.
- The 2 h at 1120 C, water-quenched condition and 76 mm thick cast section agree with Table I.
- Figure 3's caption rounds alloy 5 nitrogen to 0.15%, whereas Table I gives 0.16%. Citrine uses the more specific Table I value. This is an internal source inconsistency, not a database error.
- Converting 3% NaCl to 0.53 M requires an assumption about how the percentage is defined and about solution volume/density. The result should be labeled calculated, not source-reported.

## Coverage audit

Figure 3 contains the two relevant polarization curves and both are represented. Figures 1 and 2 report pitting **current density after 16 h**, not pitting potential. The remaining corrosion results are immersion corrosion rates or qualitative pitting/crevice outcomes. They should not be added to this target field as `Epit`.

No confirmed pitting-potential omission was found for Reference 10.

## Recommended corrections

1. Add Cu = 3.04 wt% to record 307 and Cu = 3.15 wt% to record 308.
2. Recalculate Fe as approximately 64.175 and 63.798 wt%, respectively, if Fe remains a balance.
3. Add the N2-purged condition to the test metadata.
4. Mark 860 and 160 mV as approximate Figure 3 readings and attach suitable digitization uncertainty.
5. Mark 0.53 M chloride as derived and document its conversion assumptions, or retain only the source's 3% NaCl statement.

## Overall assessment

**Pitting-potential values: plausible/pass with qualification.** They agree with Figure 3 but are graph-derived, not printed measurements.

**Compositions: fail.** Both omit a major alloying element and consequently report incorrect Fe balances.

**Coverage: pass.** Both source curves relevant to pitting potential are represented; other corrosion metrics should remain separate.
