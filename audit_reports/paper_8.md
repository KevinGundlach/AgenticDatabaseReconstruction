# Audit Report: Citrine Pitting-Potential Records for Reference 8

## Scope

This report compares all eight Reference 8 records in the Citrine `Pitting Potential` sheet with:

- [R. Guo and M. B. Ives, Corrosion 46 (1990), 125](<../papers/8_R. Guo, M. B. Ives, Corrosion 46 {1990)_ p. 125.pdf>)
- [Citrine source workbook](../citrine_database/CRA_database_Scientific_Data_Publication_12102020.xlsx), Excel rows 470-477 (record numbers 468-475)

Audit date: 2026-09-03

Workbook evidence: 【CRA_database_Scientific_Data_Publication_12102020.xlsx:Pitting Potential:A470:AM477】

The relevant composition table, experimental method, and Figures 3-5 were checked visually. The repository's [figure catalog](../mineru_output/paper_8/paper_8_figures.json) and [figure extraction](../mineru_output/paper_8/paper_8_figure_extractions.json) were used as secondary cross-checks.

## Executive summary

The eight records accurately reproduce the central values and indicated experimental ranges in Figure 3. Compositions, temperature, solution concentration, pH description, and scan rate are consistent with the paper. No confirmed record-level error was found. The main open question is coverage: Figures 4 and 5 contain additional potential values, but the paper labels some of them `transpassive and/or pitting`, so automatic inclusion as pitting potential would be unsafe.

## Record reconciliation

All measurements are at 70 C in nitrogen-deaerated 0.6M sodium halide, using a 600 mV/h scan (0.167 mV/s). The paper describes the solutions as neutral, pH approximately 7.

| Alloy / material | NaCl source range; Citrine (mV SCE) | NaBr source range; Citrine (mV SCE) | Assessment |
|---|---:|---:|---|
| UNS S30100 | 43-90; avg 63 | 245-290; avg 273 | Match |
| UNS S31600 | 138-200; avg 168 | 306-350; avg 330 | Match |
| UNS N08904 | 587-640; avg 620 | 456-500; avg 476 | Match |
| UNS S31254, Heat 2 | 1000-1050; avg 1028 | 573-660; avg 620 | Match |

The average values appear to be digitized from bar heights, while min/max values reproduce the printed range marks. The source's graphical resolution does not support treating the averages as exact to better than several millivolts, but the database uses sensible whole-millivolt precision.

## Composition and conditions

- Stored compositions agree with Table 1 for the four represented materials.
- The S31254 entries correctly use Heat 2, which is the cleaner heat represented in Figure 3.
- `pH = 7` is a minor normalization of the source's `pH ~ 7`; preserving the approximation would be more exact but does not constitute a material error.
- The scan-rate conversion from 600 mV/h to 0.167 mV/s is correct.
- The source reports nitrogen deaeration for one hour before and throughout the tests; this should remain explicit in method provenance.
- NaBr records necessarily have `[Cl-] = 0`, but the schema lacks a corresponding bromide-concentration field. The 0.6M NaBr condition is retained in solution text only.

## Coverage audit

Figure 3 is complete: four alloys multiplied by two halide solutions gives the eight stored records.

Figures 4 and 5 together contain approximately 31 additional discrete potential observations across temperature and mixed chloride/bromide composition. They are **coverage candidates, not confirmed omissions**, because:

- Figure 4 is expressly labeled `transpassive and/or pitting potentials`; and
- below or above the critical pitting temperature, a plotted endpoint may represent transpassivity rather than localized breakdown.

These values should be reviewed point by point using the paper's critical-temperature interpretation. Only points identified as pitting potentials should enter this dataset; ambiguous values should retain an endpoint qualifier or go into a broader breakdown-potential table.

The continuous polarization curves in Figures 1, 2, and 6 should not be digitized as independent discrete records without a documented curve-reading method and de-duplication against Figure 3.

## Recommended actions

1. Retain the eight Figure 3 records; no numerical correction is required.
2. Preserve pH as approximately 7 and make nitrogen deaeration explicit.
3. Add a general anion/concentration representation so 0.6M bromide is structured rather than text-only.
4. Manually classify the approximately 31 Figure 4/5 candidate points as pitting, transpassive, or ambiguous before deciding on inclusion.

## Overall assessment

**Record accuracy: pass.** No confirmed numerical, compositional, or condition error was found.

**Coverage: complete for Figure 3; policy-dependent for Figures 4-5.** Additional points exist, but their endpoint identity must be resolved before they can safely be called pitting potentials.
