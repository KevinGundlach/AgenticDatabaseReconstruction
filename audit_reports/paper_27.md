# Audit Report: Citrine Pitting-Potential Records for Reference 27

## Scope

Compared two records (Excel rows 593-594) with [Shang et al. (2018)](<../papers/27_Shang, X., et al. (2018). Science China Technological Sciences 61(2)_ 189-196.pdf>). Workbook evidence: 【CRA_database_Scientific_Data_Publication_12102020.xlsx:Pitting Potential:A593:AM594】. Audit date: 2026-09-04.

## Executive summary

The 805 mV SCE value in 0.1 M NaCl agrees with the source. The 246 mV HCl value is reported versus Ag/AgCl (3.5 M KCl) but is stored without conversion even though the dataset otherwise normalizes potentials to SCE. It should be about 207 mV SCE, subject to the exact reference offset used.

| Severity | Finding |
|---|---|
| High | The HCl value retains its Ag/AgCl numerical value while being placed in an SCE-normalized field. |
| Low | pH 7 in NaCl is not source-reported. |

## Coverage

The selected quaternary NiCoCrFe alloy is represented in both electrolytes. Lower-order Ni/NiCo/NiCoFe materials are omitted; this is defensible only if a high-entropy/multicomponent scope rule is explicit.

## Recommended corrections

Convert 246 mV Ag/AgCl to approximately 207 mV SCE and retain original scale/conversion metadata. Clarify the material-scope rule.

## Overall assessment

**NaCl record: pass. HCl potential: fail reference-scale normalization.**
