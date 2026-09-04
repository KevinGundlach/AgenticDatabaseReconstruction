# Audit Report: Citrine Pitting-Potential Records for Reference 54

## Scope

Compared 30 records (Excel rows 225-254) with [Bandy and van Rooyen (1983)](<../papers/54_R. Bandy, D. van Rooyen, Corrosion 39 (1983)_ p. 227.pdf>). Workbook evidence: 【CRA_database_Scientific_Data_Publication_12102020.xlsx:Pitting Potential:A225:AM254】. Audit date: 2026-09-04.

## Executive summary

Most stored Table 2/Table 3 values are accurate, but one record has the wrong electrolyte and temperature, and at least 12 numeric source observations are omitted.

| Severity | Finding |
|---|---|
| Critical | The specimen-25 value 268 mV is assigned to 1.5 M chloride + acid at 50 °C; it belongs to 1 N NaCl at 30 °C. |
| High | Specimen 8 (101 mV) is omitted. |
| High | Seven commercial-alloy Table 2 values and four commercial-alloy Table 3 values are omitted. |
| Medium | Source approximation/limit symbols in chemistry are flattened to exact numbers. |
| Low | pH 7 for 1 N NaCl is unreported. |

The seven aggressive-electrolyte entries (-185, -155, -152, -88, 149, 145, and 281 mV) agree with Table 3; their slower 6 mV/min protocol should remain distinct from Table 2's 20 mV/min tests.

## Recommended corrections

Move 268 mV to 1 N NaCl/30 °C; add the 12 omitted numeric observations; preserve chemistry qualifiers, source pH status, and the two scan protocols.

## Overall assessment

**Most stored potentials pass. One major condition error and major coverage omissions remain.**
