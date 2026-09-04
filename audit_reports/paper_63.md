# Audit Report: Citrine Pitting-Potential Records for Reference 63

## Scope

Compared two records (Excel rows 211-212) with [Lu, Clayton, and Brooks (1989)](<../papers/63_Lu, Y. C., C. R. Clayton, and A. R. Brooks. Corrosion science 29.7 (1989)_ 863-880.pdf>). Workbook evidence: 【CRA_database_Scientific_Data_Publication_12102020.xlsx:Pitting Potential:A211:AM212】. Audit date: 2026-09-04.

## Findings

The -50 mV value at pH 5.4 and 525 mV at pH 9.0 in 0.3 M NaCl agree with Table 2. The source chemistry uses upper limits C <0.05, N <0.002, and S <0.025, but Citrine stores those limits as exact values and computes Fe accordingly. The molybdate solution's 838 mV transpassive/no-pitting value is appropriately excluded.

## Recommended correction

Restore the `<` qualifiers and identify Fe as a balance calculated with censored inputs.

## Overall assessment

**Potentials/coverage: pass. Composition qualifiers: fail.**
