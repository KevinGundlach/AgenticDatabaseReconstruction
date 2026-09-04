# Audit Report: Citrine Pitting-Potential Records for Reference 25

## Scope

Compared the single record (Excel row 590) with [Wang et al. (2016)](<../papers/25_Hong-lei Wang, Tai-Xiu Gao, Jia-zheng Niu, Pei-jian Shi, Jing Xu, and Yan Wang. International Journal of Minerals, Metallury, and Materials, 23 (1) (2016), 77-82.pdf>). Workbook evidence: 【CRA_database_Scientific_Data_Publication_12102020.xlsx:Pitting Potential:A590:AM590】. Audit date: 2026-09-04.

## Executive summary

The stored -602 mV SCE is a plausible conversion from the paper's -0.56 V versus Ag/AgCl for the 520 °C SPS sample. The reference-electrode filling solution is not specified, so the exact conversion is uncertain. The serious error is `[Cl-] = 0.0182 M`: the paper gives an artificial-sea-salt:water mass ratio of 1:30, not NaCl molarity. Citrine appears to have mistaken a dilution ratio for chloride concentration.

| Severity | Finding |
|---|---|
| High | 0.0182 M chloride is unsupported and chemically implausible for the stated artificial seawater preparation. |
| Medium | Ag/AgCl-to-SCE conversion is undocumented and reference-electrode details are insufficient for an exact offset. |
| Low | pH 7 is not reported. |

## Coverage

The 1080 °C sample did not exhibit a usable passive plateau/Epit, so its absence is appropriate.

## Recommended corrections

Remove 0.0182 M or recalculate chloride only from the actual salt recipe; record the original -0.56 V Ag/AgCl value and conversion uncertainty; mark pH unreported.

## Overall assessment

**Potential: plausible. Electrolyte metadata: fail. Coverage: pass.**
