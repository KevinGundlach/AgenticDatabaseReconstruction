# Audit Report: Citrine Pitting-Potential Records for Reference 73

## Scope

Compared 17 records (Excel rows 90-100 and 541-546) with [Bui et al. (1983)](<../papers/73_Bui, N., et al. Corrosion 39.12 (1983)_ 491-496.pdf>). Workbook evidence: 【CRA_database_Scientific_Data_Publication_12102020.xlsx:Pitting Potential:A90:AM100】 and 【CRA_database_Scientific_Data_Publication_12102020.xlsx:Pitting Potential:A541:AM546】. Audit date: 2026-09-04.

## Executive summary

Three NaCl W-series values are entered twice: once as high-precision digitized readings (about 77.7/214.3/297.1 mV) and again as the paper's rounded 80/210/300 mV text values. The base W=0 condition appears a third time in the tungstate series. For 0.2 M HCl, Citrine records pH 1; nominal strong-acid pH is about 0.70.

| Severity | Finding |
|---|---|
| Critical | Three W-series source observations are duplicated; the base condition is triplicated. |
| High | pH for 0.2 M HCl is wrong (1 instead of approximately 0.70, if calculated ideally). |
| Medium | Figure readings have excessive precision and implicit potential conversion. |
| Low | NaCl pH 7 is unreported. |

## Recommended corrections

Prefer the paper's text-stated 80/210/300 mV values, remove duplicates, retain one base control shared by the tungstate series, correct/qualify pH, and document conversion/provenance.

## Overall assessment

**Values broadly plausible; duplication and pH handling fail.**
