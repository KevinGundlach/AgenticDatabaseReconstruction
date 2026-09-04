# Audit Report: Citrine Pitting-Potential Records for Reference 85

## Scope

Compared eight records (Excel rows 326-333) with [Clark and Guha (1983)](<../papers/85_C.A. Clark & P. Guha. Improvements in corrosion resistance … Werkstoffe und Korrosion, 34. 1983.pdf>). Workbook evidence: 【CRA_database_Scientific_Data_Publication_12102020.xlsx:Pitting Potential:A326:AM333】. Audit date: 2026-09-04.

## Executive summary

The eight Figure 4 values are plausible after converting the SHE axis to SCE. Several points at 1150 mV SHE are plot-ceiling/lower-bound observations and become 906 mV SCE in Citrine; they should be right-censored, not exact. Composition handling is seriously flawed: source specification ranges/minima/maxima are replaced by midpoints/exact values, and the cast 20-type alloy's `Nb = 8 × %C` is entered as N = 0.56 wt% with Nb = 0.

| Severity | Finding |
|---|---|
| Critical | Cast 20-type Nb (~0.56 wt% from 8×0.07%C) is placed in the N column; Nb is set to zero. |
| High | Specification ranges and limits for Ferralium 255/288 and cast 20-type are converted to exact midpoints/minima/maxima. |
| High | 1150 mV SHE ceiling points are stored as exact 906 mV SCE. |
| High | Figure 1 nitrogen series, Figure 2 nickel series, Figure 3 copper series, and the 18Cr10Ni3Mo Figure 4 series are omitted. |
| Medium | SHE-to-SCE conversion is undocumented; method and scan rate are `NA`. |

## Recommended corrections

Move 0.56 from N to Nb for cast 20-type; restore ranges/limit qualifiers or identify midpoint calculations; encode ceiling points as `>906 mV SCE`; document conversion; and add the omitted discrete figure series with composition/temperature provenance.

## Overall assessment

**Stored Figure 4 readings: plausible with censoring. Composition and coverage: fail.**
