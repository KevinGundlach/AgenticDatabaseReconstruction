# Audit Report: Citrine Pitting-Potential Records for Reference 84

## Scope

Compared 15 records (Excel rows 311-325) with [Machin and Guha (1974)](<../papers/84_R. Machin & P. Guha. Werkstoffe und Korrosion 25. 1974.pdf>). Workbook evidence: 【CRA_database_Scientific_Data_Publication_12102020.xlsx:Pitting Potential:A311:AM325】. Audit date: 2026-09-04.

## Executive summary

Nine rows are not pitting potentials. Eight use chloride-free 1 N H2SO4 and one uses chloride-free 10 N H2SO4; the paper discusses active/passive ranges and transpassive limits in those figures. Citrine inserts `[Cl-]=0.000001 M` and labels upper curve values (600-940 mV) as Epit. Only the six 3% NaCl rows correspond to chloride breakdown/pitting behavior.

| Severity | Finding |
|---|---|
| Critical | Nine chloride-free sulfuric-acid passivity/transpassive values are false Epit inclusions. |
| High | Artificial `0.000001 M` chloride masks the fact that the electrolyte contains no chloride. |
| Medium | Nominal/approximate alloy compositions are stored as exact measured values. |
| Low | Method spelling varies (`ASTM G1`, `ASTMG1`, `ASTMG!`). |

The valid NaCl source values include -50 mV for 18Cr10Ni, 200 mV for 18Cr10Ni3Mo, about 800-850 mV for Ferralium, and processing-dependent Ferralium values. The source uses 10 mV/min steps, consistent with 0.166 mV/s only as an equivalent rate.

## Recommended corrections

Remove/reclassify the nine acid-only rows, use true zero chloride, retain the six NaCl observations with graphical/endpoint qualification, and normalize method text.

## Overall assessment

**Fail—major endpoint contamination; six chloride rows remain usable.**
