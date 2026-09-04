# Audit Report: Citrine Pitting-Potential Records for Reference 71

## Scope

Compared 38 records (Excel rows 71-89 and 255-273) with [Truman, Coleman, and Pirt (1977)](<../papers/71_Truman, J. E., M. J. Coleman, and K. R. Pirt. British corrosion journal 12.4 (1977)_ 236-238.pdf>). Workbook evidence: 【CRA_database_Scientific_Data_Publication_12102020.xlsx:Pitting Potential:A71:AM89】 and 【CRA_database_Scientific_Data_Publication_12102020.xlsx:Pitting Potential:A255:AM273】. Audit date: 2026-09-04.

## Executive summary

The same 19 source “plain specimen” values are entered twice. The two copies differ only in unsupported pH/temperature metadata. The source states aerated 0.6 M NaCl + 0.1 M NaHCO3 but does not report either pH 7.68 or 8.3, nor an exact polarization temperature. Two composition errors also recur, and the parallel 19-value crevice configuration is omitted.

| Severity | Finding |
|---|---|
| Critical | Complete duplicate: 19 source values are stored twice. |
| High | Source pH is unreported; the duplicate sets assign conflicting 7.68 and 8.3. |
| High | Steel 6 Cr is 16.66 wt%; one copy stores 16.86. Steel 19 N is 0.435 wt%; both copies store 0.455. |
| Medium | Nineteen distinct neoprene-ring/crevice breakdown values are omitted. |

## Recommended corrections

Keep one plain-specimen set, correct chemistry, set unsupported conditions to `NA`, and add the crevice series only with explicit configuration/endpoint labels.

## Overall assessment

**Potentials: duplicated. Compositions/conditions: fail. Coverage: incomplete.**
