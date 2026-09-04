# Audit Report: Citrine Pitting-Potential Records for Reference 31

## Scope

Compared the single record (Excel row 154) with [Halada, Kim, and Clayton (1996)](<../papers/31_G. P. Halada , D. Kim , C.R. Clayton , Corrosion 52 (1996)_ p. 36.pdf>). Workbook evidence: 【CRA_database_Scientific_Data_Publication_12102020.xlsx:Pitting Potential:A154:AM154】. Audit date: 2026-09-04.

## Findings

The 239 mV pitting potential and Fe-20Cr-20Ni composition agree with Table 3/Table 1. The Mo-bearing alloys did not pit before transpassivity and are correctly not entered as ordinary numeric Epit values. The 0.1 M HCl + 0.4 M NaCl electrolyte, SCE scale, 1 mV/s scan, and processing are consistent with the source. Citrine's pH 1 is calculated from nominal acid concentration, not a measured value.

## Recommended correction

Label pH as derived. Optionally encode the Mo-bearing no-pitting limits as censored observations rather than silently omitting them.

## Overall assessment

**Potential/composition: pass. Coverage: pass for uncensored Epit.**
