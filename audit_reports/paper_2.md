# Audit Report: Citrine Pitting-Potential Records for Reference 2

## Scope

This report compares all 16 Reference 2 records in the Citrine `Pitting Potential` sheet with:

- [A. P. Bond and E. A. Lizlovs, "Anodic Polarization of Austenitic Stainless Steels in Chloride Media," J. Electrochem. Soc. 115 (1968), 1130-1135](<../papers/2_A. P. Bond, E. A. Lizlovs, J. Electrochem. Soc. 115 (1968)_ p. 1130.pdf>)
- [Citrine source workbook](../citrine_database/CRA_database_Scientific_Data_Publication_12102020.xlsx), Excel rows 390-405 (record numbers 388-403)

Audit date: 2026-09-03

Workbook evidence: 【CRA_database_Scientific_Data_Publication_12102020.xlsx:Pitting Potential:A390:AM405】

The paper's tables, graph, and experimental section were checked visually. The repository's [figure catalog](../mineru_output/paper_2/paper_2_figures.json) and [figure extraction](../mineru_output/paper_2/paper_2_figure_extractions.json) were used as secondary cross-checks.

## Executive summary

The pitting-potential values transcribed from Table III are accurate, including the database's interpretation of `NP` as a right-censored value greater than 800 mV SCE. The first two single-rate results in Table IV are also correct. The audit found two confirmed data problems, several provenance limitations, and incomplete coverage.

| Severity | Finding | Affected records |
|---|---|---:|
| High | Five alloys whose Cr and Ni were not reanalyzed are represented as approximately 97-99% Fe, even though Table III identifies their nominal compositions as 20Cr-39Ni or 18Cr-14Ni. | 389, 390, 393-395 |
| High | Values from two distinct two-stage scan protocols are merged into one min/max record. | 402 |
| Medium | The two-stage scan histories are reduced to their final scan rates, losing the initial 600 mV/h segment and switching potential. | 402-403 |
| Medium | Figure 7 contains additional plotted pitting-potential observations that are not represented. | Coverage |
| Low | `pH = 1` and `pH = 7` are inferred/calculated rather than directly reported measurements. | 388-403 |

## Record reconciliation

### Table III: 0.1N HCl

Records 388-399 reproduce all 12 Table III rows:

| Source alloy series | Table III result | Citrine records | Potential assessment |
|---|---|---:|---|
| 20Cr-39Ni, 0 Mo | 0.64 V SCE | 388 | Correct: 640 mV |
| 20Cr-39Ni, 1, 3, and 5 Mo | `NP` through 0.8 V | 389-391 | Correctly stored as `>800` mV |
| 18Cr-14Ni, 2 Mo | 0.39 V SCE | 392 | Correct: 390 mV |
| 18Cr-14Ni, 2.5, 3, 3.5, and 4 Mo | `NP` through 0.8 V | 393-396 | Correctly stored as `>800` mV |
| 18Cr-16Ni high-purity series, 0, 2.5, and 5 Mo | `NP` through 0.8 V | 397-399 | Correctly stored as `>800` mV |

The numerical endpoints pass. The composition mapping does not. Table I marks some analyses as `NA`—not analyzed, but within the range of the series. Citrine treated those unreported elements as zero and calculated Fe by difference:

| Record | Citrine composition pattern | Source-supported nominal alloy |
|---:|---|---|
| 389-390 | Fe about 97-99%, Mo about 1 or 3%; Cr and Ni absent | 20Cr-39Ni with 1 or 3 Mo, Fe balance |
| 393-395 | Fe about 97%, Mo about 2.5-3.5%; Cr and Ni absent | 18Cr-14Ni with 2.5-3.5 Mo, Fe balance |

`NA` analytical cells must remain unknown or inherit only a clearly labeled nominal series composition; they must not be converted to zero.

### Table IV: scan-rate study in 1.0M NaCl

| Record | Citrine representation | Source | Assessment |
|---:|---|---|---|
| 400 | 430 mV at 0.556 mV/s | 0.43 V at 2000 mV/h | Correct |
| 401 | 470 mV at 0.167 mV/s | 0.47 V at 600 mV/h | Correct |
| 402 | min 495, max 525 mV at 0.0167 mV/s | 0.525 V after 600 mV/h to +0.3 V, then 60 mV/h; 0.495 V after the same initial segment, then 20 mV/h | Incorrect aggregation; different protocols were merged |
| 403 | 655 mV at 0.0167 mV/s | second result at the 20 mV/h final stage | Correct value, but incomplete protocol metadata |

Record 402 should be split. The 525 mV result belongs to a final rate of 60 mV/h (0.0167 mV/s), while the 495 mV result belongs to 20 mV/h (0.00556 mV/s). Records 402 and 403 should also preserve the preceding 600 mV/h scan from -0.7 to +0.3 V.

## Conditions and provenance

- The paper reports argon-saturated 0.1N HCl and 1.0M NaCl, an SCE reference, and 24 +/- 1 C. These conditions are otherwise represented consistently.
- The paper discusses the comparison between pH 1 and 7, but does not report a measured pH for each test solution. Citrine's exact `1` and `7` entries are reasonable chemical/contextual inferences, not direct transcriptions, and should be marked as such.
- The database correctly distinguishes the stable-growth pitting potential from lower-potential transient, repassivating pit events.
- `>800` is a defensible normalization of `NP`: the source says the scans reached 0.8 V without pitting. The original censoring statement should remain available in provenance.

## Coverage audit

Table III is complete and Table IV is represented, although one Table IV row is incorrectly aggregated. Figure 7 also plots pitting potential against Mo content for several alloy series in 1.0M NaCl. Most of those finite plotted observations are absent from Reference 2. Some overlap the Table IV alloy and some are replicate observations, so they should be reconciled by specimen and run rather than blindly appended. Nevertheless, the current 16-row selection does not cover the full pitting-potential evidence in the paper.

Figures 1-6 primarily show polarization behavior, passivation properties, or curves supporting the tabulated endpoints; they should not be digitized as independent records without a clear de-duplication rule.

## Recommended corrections

1. Restore the nominal Cr-Ni series identities for records 389, 390, and 393-395; do not interpret `not analyzed` as zero.
2. Split record 402 into the 60 and 20 mV/h final-stage protocols and associate 495 and 525 mV with the correct rates.
3. Preserve the full two-stage scan descriptions for records 402-403.
4. Mark the pH values as inferred unless independent source documentation supports them.
5. Review Figure 7 against the database's inclusion policy and add eligible, de-duplicated observations.

## Overall assessment

**Potential values: mostly pass.** Table III and the unaggregated Table IV values are faithful.

**Compositions and protocol provenance: needs correction.** Five composition rows convert unknown analyses into zero, and record 402 merges unlike scan histories.

**Coverage: incomplete.** Figure 7 contains additional pitting-potential evidence not represented in the dataset.
