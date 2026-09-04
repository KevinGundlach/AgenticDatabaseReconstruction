# Audit Report: Citrine Pitting-Potential Records for Reference 6

## Scope

This report compares all 10 Reference 6 records in the Citrine `Pitting Potential` sheet with:

- [A. P. Bond, J. Electrochem. Soc. 120 (1973), 603](<../papers/6_A. P. Bond, Electrochem. Soc. 120 (1973)_ p. 603.pdf>)
- [Citrine source workbook](../citrine_database/CRA_database_Scientific_Data_Publication_12102020.xlsx), Excel rows 460-469 (record numbers 458-467)

Audit date: 2026-09-03

Workbook evidence: 【CRA_database_Scientific_Data_Publication_12102020.xlsx:Pitting Potential:A460:AM469】

The source tables and figures were checked visually. The repository's [figure catalog](../mineru_output/paper_6/paper_6_figures.json) and [figure extraction](../mineru_output/paper_6/paper_6_figure_extractions.json) were used as secondary cross-checks.

## Executive summary

The seven graph-derived NaCl/NaBr ranges are consistent with the plotted source points. The three Table IV records contain a confirmed composition omission, two missing maxima, and an incorrect table citation. The exact pH assigned to every row is not reported by the paper. Coverage is also substantially incomplete.

| Severity | Finding | Affected records |
|---|---|---:|
| High | Ti is omitted from Ti-stabilized heat 4073A; Table IV reports 0.47 wt% Ti. | 458-460 |
| High | Maximum values of 350 and 590 mV are omitted from two aggregated Table IV records. | 458, 460 |
| Medium | The comment says the values came from Table VI; the actual source is Table IV. | 458-460 |
| Medium | Many additional pitting-potential observations in Figures 2 and 4 and Tables II-III are absent. | Coverage |
| Medium | `pH = 7` is not reported for the nitrogen-saturated NaCl/NaBr tests. | 458-467 |
| Low | NaBr rows use `[Cl-] = 0`, but no structured field preserves bromide concentration. | 465-467 |

## Record reconciliation

### Table IV: Ti-stabilized heat 4073A

The source composition includes **0.47 wt% Ti**. Citrine omits Ti in all three rows and calculates Fe as though the Ti were absent. If Fe remains a calculated balance, including Ti changes it from approximately 81.227 to 80.757 wt%.

| Record | Heat treatment | Source Epit values (mV SCE) | Citrine | Assessment |
|---:|---|---|---|---|
| 458 | 815 C | 270, 350, 290 | avg 300; min 270; max `NA` | Average/minimum reasonable; maximum 350 is missing |
| 459 | 925 C | 300 | avg 300 | Correct |
| 460 | 1035 C | 530, 590, 500 | avg 540; min 500; max `NA` | Average/minimum correct; maximum 590 is missing |

The common database comment `Data was extracted fromTable VI` is wrong; these values appear in Table IV.

### Figures 2 and 4: heat 4354A

| Records | Source | Condition | Citrine range(s) | Assessment |
|---:|---|---|---|---|
| 461-464 | Figure 2 | 1.0M NaCl; 1, 25, 45, 70 C; 200 mV/h | 250-270, 20-70, -40-20, -170 to -160 mV | Consistent with plotted points |
| 465-467 | Figure 4 | 1.0M NaBr; 1, 25, 45 C; 200 mV/h | 330-330, 230-250, 95-170 mV | Consistent with plotted points |

The conversion of 200 mV/h to 0.0556 mV/s is correct. The Table IV rate of 2000 mV/h is also correctly converted to 0.556 mV/s.

## Conditions and provenance

- The paper specifies nitrogen-saturated 1.0M NaCl or NaBr. It does not specify a pH of 7; those entries are inferred and should not be presented as measured values.
- The NaBr records correctly contain zero chloride, but the schema has no structured `[Br-]` field. The 1.0M bromide condition survives only in the solution text.
- Min/max aggregation is acceptable when all source values share the same material and protocol, but it should not drop the extrema as records 458 and 460 do.

## Coverage audit

The database captures only the near-zero-Mo ranges from Figures 2 and 4 plus the three heat-treatment rows in Table IV. It omits most of the plotted Mo series and several tabulated comparisons:

- Figure 2 contains approximately 38 individual plotted observations; the four stored ranges account for about eight of them.
- Figure 4 contains approximately 30 plotted observations; the three stored ranges account for about six.
- Table III includes three 980 C observations not duplicated by the represented 815 C figure data.
- Table II includes two 2000 mV/h observations not duplicated by the 200 mV/h plotted series.

After excluding obvious overlaps, this is approximately **59 additional individual source observations**. That count is a coverage estimate because coincident markers and table/figure duplication must be reconciled at the run level.

## Recommended corrections

1. Add Ti = 0.47 wt% to records 458-460 and recalculate Fe balance if applicable.
2. Set record 458 maximum to 350 mV and record 460 maximum to 590 mV.
3. Change the provenance comment from Table VI to Table IV.
4. Replace pH 7 with `NA`/`not reported`, or explicitly label it inferred.
5. Add a structured bromide concentration field or a general anion/concentration representation.
6. Review the omitted Figure 2, Figure 4, Table II, and Table III observations against the inclusion policy, preserving run-level values where available.

## Overall assessment

**Stored graph-derived potentials: pass.** Records 461-467 agree with the figures.

**Table-derived rows: needs correction.** Ti and two maxima are missing, and the provenance table number is wrong.

**Coverage: substantially incomplete.** Most of the paper's pitting-potential observations are absent.
