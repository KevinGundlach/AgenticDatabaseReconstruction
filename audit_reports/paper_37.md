# Audit Report: Citrine Pitting-Potential Records for Reference 37

## Scope

Compared 16 records (Excel rows 107-122) with [Jargelius-Pettersson (1999)](<../papers/37_R. F. A. Jargelius-Pettersson, Corros. Sci. 41 (1999)_ p. 1639.pdf>). Workbook evidence: 【CRA_database_Scientific_Data_Publication_12102020.xlsx:Pitting Potential:A107:AM122】. Audit date: 2026-09-04.

## Findings

The database correctly aggregates the plotted replicate final-breakdown values into means and minima/maxima for four nitrogen levels at 40/50 °C and four Mo-bearing alloys at 75/90 °C. The source distinguishes first repassivating pit initiation (`E_init`) from final breakdown (`E_b`); Citrine stores `E_b`, which is defensible but should be explicit. pH 7 is not reported.

## Recommended corrections

Add endpoint metadata identifying `E_b`, retain the replicate-aggregation method, and mark pH as unreported.

## Overall assessment

**Potentials, compositions, and coverage: pass with endpoint/provenance qualification.**
