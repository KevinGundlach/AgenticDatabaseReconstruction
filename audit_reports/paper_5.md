# Audit Report: Citrine Pitting-Potential Records for Reference 5

## Scope

This report compares the Citrine `Pitting Potential` sheet with:

- [E. L. Hibner, Materials Performance 26(3) (1987), 37-40](<../papers/5_Hibner, E. L., Materials performance 26.3 (1987)_ 37-40.pdf>)
- [Citrine source workbook](../citrine_database/CRA_database_Scientific_Data_Publication_12102020.xlsx)

Audit date: 2026-09-03

Workbook evidence (full-sheet reference search): 【CRA_database_Scientific_Data_Publication_12102020.xlsx:Pitting Potential:A1:AM812】

The workbook contains **no `Pitting Potential` rows assigned to Reference 5**. The paper's tables and figures were checked visually, with the repository's [figure catalog](../mineru_output/paper_5/paper_5_figures.json) and [figure extraction](../mineru_output/paper_5/paper_5_figure_extractions.json) used as secondary cross-checks.

## Executive summary

The absence of Reference 5 records is correct for the `Pitting Potential` dataset. This paper concerns modifications to the critical crevice temperature (CCT) test in ferric chloride. It reports temperatures, exposure conditions, and crevice-corrosion outcomes—not electrode pitting potentials.

## Source-content assessment

The paper's quantitative tables and figures concern:

- critical crevice temperature;
- ferric-chloride immersion procedures;
- specimen geometry and crevice-forming assemblies;
- test duration and temperature; and
- observed crevice attack.

None of these measurements is an `Epit` value. Critical crevice temperature is a separate response variable and should not be converted into or stored as pitting potential.

## Recommended action

1. Retain zero Reference 5 rows in the `Pitting Potential` sheet.
2. Mark the reference as reviewed and out of scope so the absence is not mistaken for unfinished extraction.
3. If the broader project later includes critical-temperature data, curate this paper into a separate CCT/crevice-corrosion dataset with its own endpoint definition.

## Overall assessment

**Record accuracy: not applicable.** No Reference 5 rows exist.

**Coverage: pass for pitting potential.** The paper does not report the target property.
