# Audit Report: Citrine Pitting-Potential Records for Reference 32

## Scope

Compared 16 records (Excel rows 777-792) with [Lucente and Scully (2007)](<../papers/32_A.M. Lucente, J.R. Scully, Electrochemical and Solid-State Letters, 10 (2007) C39-C43.pdf>). Workbook evidence: 【CRA_database_Scientific_Data_Publication_12102020.xlsx:Pitting Potential:A777:AM792】. Audit date: 2026-09-04.

## Executive summary

These are figure-derived medians for amorphous/nanocrystalline Al alloys, but Citrine repeats a bulk composition while dropping the nanocrystal size, volume fraction, and condition that distinguish the points. One value, +980 mV for Al90Fe5Gd5, is plainly inconsistent with Figure 5 and should be near -90 mV. Quartile/error information is also discarded.

| Severity | Finding |
|---|---|
| Critical | +980 mV is a transcription/digitization error; the plotted point is near -90 mV. |
| High | Multiple records become indistinguishable because nanostructural state/x-axis condition is omitted. |
| Medium | Source at% nominal compositions are converted to wt% without provenance. |
| Medium | Figure medians and 25th/75th-percentile spreads are stored as exact single values. |
| Low | pH 7 is unreported. |

## Recommended corrections

Correct the +980 mV point from the figure, add nanocrystal size/state and source figure coordinates, populate uncertainty fields from the plotted quartiles, and label composition conversion and pH provenance.

## Overall assessment

**Potentials/structure: fail. Coverage appears substantial but records are not scientifically identifiable.**
