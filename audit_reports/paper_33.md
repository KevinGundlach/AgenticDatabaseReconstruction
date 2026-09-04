# Audit Report: Citrine Pitting-Potential Records for Reference 33

## Scope

Compared two records (Excel rows 296-297) with [Vanini, Audouard, and Marcus (1994)](<../papers/33_A. Sadough Vanini, J. P. Audouard, P. Marcus, Corros. Sci. 36 (1994)_p. 1825.pdf>). Workbook evidence: 【CRA_database_Scientific_Data_Publication_12102020.xlsx:Pitting Potential:A296:AM297】. Audit date: 2026-09-04.

## Finding

Both 860.69 mV records are false inclusions. The chloride-free 0.5 M H2SO4 study concerns passivity; it reports corrosion/peak/passive parameters and no pitting potential. The stored number appears to represent an upper/transpassive curve feature, not Epit.

## Recommended correction

Remove both rows from the pitting-potential dataset. Preserve any desired passive-film quantities only in a schema with their actual source definitions.

## Overall assessment

**Fail—wrong endpoint.**
