# Audit Report: Citrine Pitting-Potential Records for Reference 26

## Scope

Compared two records (Excel rows 591-592) with [Lee et al. (2008)](<../papers/26_C.P. Lee, C.C. Chang, Y.Y. Chen, J.W. Yeh, and H.C. Shih. Corrosion Science, 50 (2008) 2053-2060.pdf>). Workbook evidence: 【CRA_database_Scientific_Data_Publication_12102020.xlsx:Pitting Potential:A591:AM592】. Audit date: 2026-09-04.

## Executive summary

Both records are false inclusions. The tests use chloride-free 0.5 M H2SO4, and the paper discusses passivation/transpassive breakdown—not chloride pitting. The stored 931 and 923 mV values appear to be constructed from passivation-table quantities or a transpassive limit.

| Severity | Finding |
|---|---|
| Critical | Chloride-free transpassive/passive-range values are mislabeled as pitting potentials. |

## Recommended correction

Remove both records from the pitting-potential dataset. If useful, move the source quantities to a separate passivation/transpassive endpoint table with their original definitions. Do not add the third alloy as Epit.

## Overall assessment

**Potentials: fail—wrong endpoint. Coverage: not applicable after removal.**
