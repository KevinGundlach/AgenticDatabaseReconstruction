# Audit Report: Citrine Pitting-Potential Records for Reference 16

## Scope

Compared 12 records (Excel rows 478-489) with [Azuma et al. (1991)](<../papers/16_S. Azuma et al. , in Proceedings of the International Conference on Stainless Steels, Iron and Steel Institute of Japan, Tokyo, p. 133, 1991.pdf>). Workbook evidence: 【CRA_database_Scientific_Data_Publication_12102020.xlsx:Pitting Potential:A478:AM489】. Audit date: 2026-09-04.

## Executive summary

The four-alloy by three-temperature Figure 7 matrix is represented and the readings are plausible. Values near 1.0 V, however, lie at the plot/test ceiling and may denote transpassivity or right-censoring rather than precisely measured pitting potentials. The database also omits substantial additional pitting-potential series from Figures 4, 10, 11, and 13.

| Severity | Finding |
|---|---|
| High | At least 24 additional discrete pitting observations in other figures are absent. |
| Medium | Values around 1000-1020 mV are stored as exact although the source indicates a ceiling/transition region. |
| Medium | The 28Cr processing condition reported in the source is missing from row metadata. |
| Low | `[Cl-]=0.546 M` is a derived seawater estimate, not source-reported. |

## Reconciliation

The stored series—28Cr: 1010/1020/850; alloy 2942: 1010/1010/493; alloy 254: 1000/1010/782; and 329J2L: 1010/330/240 mV—agrees with Figure 7 within graphical uncertainty. The scan conversion 20 mV/min = 0.333 mV/s is correct.

## Recommended corrections

Flag ceiling values as censored/ambiguous, add figure-derived uncertainty, restore processing metadata, and extract the omitted marker series with figure and endpoint provenance.

## Overall assessment

**Potentials: plausible with censoring caveat. Coverage: fail.**
