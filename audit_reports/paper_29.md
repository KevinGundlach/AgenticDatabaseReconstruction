# Audit Report: Citrine Pitting-Potential Records for Reference 29

## Scope

Compared two records (Excel rows 598-599) with [Rodriguez et al. (2018)](<../papers/29_A.A. Rodriguez, J.H. Tylczak, M.C. Gao, P.D. Jablonski, M. Detrois, M. Ziomek-Moroz, J.A. Hawk, Advances in Materials Science and Engineering, 2018 (2018) 11.pdf>). Workbook evidence: 【CRA_database_Scientific_Data_Publication_12102020.xlsx:Pitting Potential:A598:AM599】. Audit date: 2026-09-04.

## Executive summary

The stored 320 and 910 mV breakdown values match Table 2. The source electrolyte starts at pH 8.4, not pH 7. More importantly, the higher value for A36 is a breakdown/passive-film event without observed pitting, while A35 did pit; treating both identically as Epit is misleading.

| Severity | Finding |
|---|---|
| High | A36's 910 mV breakdown is labeled Epit despite no pitting being observed. |
| High | pH is 8.4 in the source, not 7. |
| Medium | Detailed homogenization/hot-working history is omitted. |
| Medium | C276 (740 mV) and 316 SS (270 mV) comparison results are absent. |

## Recommended corrections

Correct pH to 8.4; retain A35 as a pitting result; reclassify A36 as breakdown/no-pit or censored; restore processing metadata; and add the two comparators if applying the workbook's broad material scope.

## Overall assessment

**Numeric transcription: pass. Endpoint semantics and conditions: fail.**
