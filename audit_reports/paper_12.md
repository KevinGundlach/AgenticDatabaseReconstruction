# Audit Report: Citrine Pitting-Potential Records for Reference 12

## Scope

Compared 26 records (Excel rows 364-389) with [Tomashov, Chernova, and Markova (1964)](<../papers/12_N. D. Tomashov, G. P. Chernova, O. N. Markova, Corrosion 20 (1964)_ p. 166t.pdf>). Workbook evidence: 【CRA_database_Scientific_Data_Publication_12102020.xlsx:Pitting Potential:A364:AM389】. Audit date: 2026-09-04.

## Executive summary

The database captures the 22 Figure 3 composition points and four annealed-alloy values from Table 3. The tabulated values were converted from NHE to SCE consistently: 0.659, 0.810, 0.744, and 0.659 V NHE become approximately 415, 566, 500, and 415 mV SCE. The conversion is not documented, and the graph-derived values are stored with more certainty than the figure supports.

| Severity | Finding | Affected records |
|---|---|---:|
| Medium | NHE-to-SCE conversion is implicit rather than recorded. | Table 3-derived rows |
| Medium | Figure readings lack an approximate/digitized qualifier and uncertainty. | Figure 3-derived rows |
| Low | pH 7 is not reported for the 0.1 N NaCl electrolyte. | all 26 |

## Conditions and coverage

The four annealed conditions and their potentials agree with Table 3. The plotted composition series is substantially complete; duplicated or limiting points are explainable by the source presentation. No confirmed missing discrete pitting-potential series was found.

## Recommended corrections

Record the original NHE scale and conversion used; round graph-derived values to defensible precision or attach digitization uncertainty; and mark pH as unreported/assumed.

## Overall assessment

**Potentials: pass with provenance qualifications. Compositions: pass. Coverage: pass.**
