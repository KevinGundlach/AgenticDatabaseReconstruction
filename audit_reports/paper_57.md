# Audit Report: Citrine Pitting-Potential Records for Reference 57

## Scope

Reviewed 26 records (Excel rows 178-203) against [Sugimoto and Sawada (1977)](<../papers/57_Sugimoto, K., and Y. Sawada. Corrosion Science 17.5 (1977)_ 425-445.pdf>). Workbook evidence: 【CRA_database_Scientific_Data_Publication_12102020.xlsx:Pitting Potential:A178:AM203】. Audit date: 2026-09-04.

## Executive summary

The set is heavily contaminated by non-pitting endpoints digitized from continuous polarization curves. Pure Fe and Ni in 1 N HCl actively dissolve; high-Cr and high-Mo alloys remain passive to transpassivity; Fe-Mo rows in chloride-free H2SO4 cannot be chloride pitting results. Citrine nevertheless assigns numeric Epit values to these cases.

| Severity | Finding |
|---|---|
| Critical | Active-dissolution, transpassive, and scan-ceiling values are mixed with genuine pitting potentials. |
| High | Continuous-curve readings carry no endpoint classification or digitization uncertainty. |

## Recommended correction

Reconstruct the set curve by curve. Retain only source-confirmed pitting events as Epit; encode no-pitting/transpassive limits as censored or move them to the proper endpoint table. Exclude chloride-free Fe-Mo values from this dataset.

## Overall assessment

**Fail—substantial endpoint misclassification.**
