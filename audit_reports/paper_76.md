# Audit Report: Citrine Pitting-Potential Records for Reference 76

## Scope

Compared ten records (Excel rows 274-283) with [Janik-Czachor, Lunarska, and Szklarska-Smialowska (1975)](<../papers/76_Janik-Czachor, E. Lunarska, Z. Szklarska-Smialowska, Corrosion 31 (1975)_ p. 349.pdf>). Workbook evidence: 【CRA_database_Scientific_Data_Publication_12102020.xlsx:Pitting Potential:A274:AM283】. Audit date: 2026-09-04.

## Findings

The ten values plausibly represent the five nitrogen alloys at 0.1 and 0.05 N NaCl, digitized from Figure 2 and converted from NHE to SCE. Table 2 additionally gives five potentiostatic lower-limit `E_np` ranges in 0.05 N NaCl (100-115, 90-115, 340-360, 190-215, and 315-340 mV NHE); these distinct endpoints are omitted. The database calls the stepped/dynamic protocol simply potentiodynamic and stores excessive decimal precision. pH 1 is derived.

## Recommended corrections

Add the five Table 2 interval observations with min/max and endpoint label, document NHE-to-SCE conversion, and round/qualify Figure 2 readings.

## Overall assessment

**Stored values: plausible. Coverage: incomplete by five range-valued endpoints.**
