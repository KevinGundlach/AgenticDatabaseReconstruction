# Audit Report: Citrine Pitting-Potential Records for Reference 78

## Scope

Compared three records (Excel rows 570-572) with [Kim and Kwon (1999)](<../papers/78_Kim, J-S., and H-S. Kwon. Corrosion 55.5 (1999)_ 512-521.pdf>). Workbook evidence: 【CRA_database_Scientific_Data_Publication_12102020.xlsx:Pitting Potential:A570:AM572】. Audit date: 2026-09-04.

## Executive summary

The 609, 758, and 515 mV SCE values and compositions exactly match the text/Table 1 for solution-annealed alloys in deaerated 4 M NaCl at 80 °C. Citrine's heat-treatment text instead implies these Epit values belong to 850 °C-aged samples, and its microstructure says secondary phases are present. Both are wrong for Figure 1's solution-annealed state. The paper reports 30-100 mV scatter, which is omitted.

| Severity | Finding |
|---|---|
| High | Epit rows are mislabeled as aged rather than solution-annealed. |
| High | `secondary phases present` contradicts the tested solution-annealed state. |
| Medium | Reported 30-100 mV scatter is discarded. |
| Low | pH 7 is unreported. |

The database's 1 mV/s may have been borrowed from the CPT ramp; the source passage does not clearly specify that rate for the Epit sweep.

## Recommended corrections

Set treatment to solution annealed 1050 °C/2 h, remove the secondary-phase label, record scatter, and verify the Epit scan rate independently.

## Overall assessment

**Potentials/compositions: pass. Processing/microstructure metadata: fail.**
