# Audit Report: Citrine Pitting-Potential Records for Reference 67

## Scope

Compared nine records (Excel rows 547-555) with [Kim and Buchanan (1994)](<../papers/67_Kim, J. G., and R. A. Buchanan. Corrosion 50.9 (1994)_ 658-668.pdf>). Workbook evidence: 【CRA_database_Scientific_Data_Publication_12102020.xlsx:Pitting Potential:A547:AM555】. Audit date: 2026-09-04.

## Executive summary

The figure-derived potentials are plausible after an undocumented SHE-to-SCE conversion, but composition handling is wrong. Table 1 reports atomic percent; Citrine places those raw at% numbers directly in wt% columns. A Zr-containing composition also loses Zr and is incorrectly closed to 100% without it. One Mo-free B-containing alloy point is omitted.

| Severity | Finding |
|---|---|
| Critical | Atomic-percent chemistry is mislabeled as weight percent for all nine records. |
| High | Zr is omitted from a source composition and Fe balance is consequently wrong. |
| Medium | The FA-84/Mo-free B-series pitting point is omitted. |
| Medium | SHE-to-SCE conversion and digitization uncertainty are not recorded. |

## Recommended corrections

Convert chemistry properly or retain it as at%; add a Zr-capable field/qualified raw composition; add the missing marker; and document potential conversion.

## Overall assessment

**Potentials: plausible. Compositions: fail. Coverage: incomplete.**
