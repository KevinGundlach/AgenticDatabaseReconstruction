# Audit Report: Citrine Pitting-Potential Records for Reference 81

## Scope

Compared 12 records (Excel rows 213-224) with [Böhni and Uhlig (1969)](<../papers/81_H. Boehni, H. H. Uhlig, Corros. Sci. 9 (1969)_ p. 353.pdf>). Workbook evidence: 【CRA_database_Scientific_Data_Publication_12102020.xlsx:Pitting Potential:A213:AM224】. Audit date: 2026-09-04.

## Executive summary

All 12 plotted conditions (three alloys × NaCl/NaBr × 0/25 °C) are represented, but Citrine omits rhenium—the independent alloying variable—from every composition. Source alloys 2 and 3 contain 0.84 and 1.84 wt% Re; Citrine stores Re = 0 and closes Fe to 100%, making the chemistry scientifically wrong. Values are graph readings stored with many unjustified decimals.

| Severity | Finding |
|---|---|
| Critical | Re is omitted from all Re-bearing records (0.84 and 1.84 wt% in Table 1). |
| High | Fe balance is correspondingly overstated for those alloys. |
| Medium | Graph-derived values have excessive precision and no ±10-15 mV source reproducibility. |
| Medium | 0.16666 mV/s represents 50 mV/5 min staging, followed by 12-15 h steady-state holds—not a simple scan. |
| Low | pH 7 is unreported. |

## Recommended corrections

Populate Re, recalculate Fe, round values/attach the stated reproducibility, and preserve the staged plus long-hold endpoint protocol.

## Overall assessment

**Potentials/coverage: plausible/pass. Compositions: critical fail.**
