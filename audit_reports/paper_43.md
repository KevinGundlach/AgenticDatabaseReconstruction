# Audit Report: Citrine Pitting-Potential Records for Reference 43

## Scope

Compared the single record (Excel row 800) with [Guillaumin and Mankowski (1998)](<../papers/43_V. Guillaumin, G. Mankowski, Corrosion Science, 41 (1998) 421-438.pdf>). Workbook evidence: 【CRA_database_Scientific_Data_Publication_12102020.xlsx:Pitting Potential:A800:AM800】. Audit date: 2026-09-04.

## Executive summary

Figure 6 shows two breakdown events: `Eb1` near -720 mV SCE, associated with coarse S-phase particle/dissolved-zone activity, and `Eb2` near -620 mV, associated with matrix breakdown/pitting/intergranular attack. Citrine stores only -720 mV as generic Epit. That loses the endpoint identity and omits the second event.

## Recommended correction

Represent both `Eb1` and `Eb2` with their distinct physical definitions. Do not label `Eb1` simply as the matrix pitting potential.

## Overall assessment

**Fail—endpoint semantics are incorrect and coverage is incomplete.**
