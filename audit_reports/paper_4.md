# Audit Report: Citrine Pitting-Potential Records for Reference 4

## Scope

This report compares the Citrine `Pitting Potential` sheet with:

- [J. R. Postlethwaite, J. Scoular, and M. H. Dobbin, Corrosion 44 (1988), 199](<../papers/4_J. R. Postlethwaite, J. Scoular, M. H. Dobbin, Corrosion 44 (1988)_ p. 199..pdf>)
- [Citrine source workbook](../citrine_database/CRA_database_Scientific_Data_Publication_12102020.xlsx)

Audit date: 2026-09-03

Workbook evidence (full-sheet reference search): 【CRA_database_Scientific_Data_Publication_12102020.xlsx:Pitting Potential:A1:AM812】

The workbook contains **no `Pitting Potential` rows assigned to Reference 4**. The paper's relevant figures and methods were checked visually, with the repository's [figure catalog](../mineru_output/paper_4/paper_4_figures.json) and [figure extraction](../mineru_output/paper_4/paper_4_figure_extractions.json) used as secondary aids.

## Executive summary

No record-level transcription error can exist because Reference 4 has no rows in this dataset. The absence is defensible under a strict pitting-potential definition: the paper explicitly describes its cyclic-polarization endpoint as a passivation-breakdown or damaging potential and says the method cannot distinguish pitting from crevice corrosion. If Citrine intends to include broader localized-corrosion breakdown potentials, however, Figure 4 is a clear coverage candidate.

## Source-method assessment

The paper studies molybdenum-bearing nickel alloys in chloride solutions using cyclic potentiodynamic polarization. Key conditions include:

- nitrogen-deaerated electrolyte;
- a 20 mV/min forward scan;
- scan reversal at 1 mA/cm2;
- SCE reference at temperatures up to 100 C and an external Ag/AgCl reference at higher temperatures, with potentials converted to the standard hydrogen scale at test temperature.

The authors label the relevant quantity `E_b`, a passivation breakdown or damaging potential. They also state that their cyclic-polarization procedure cannot distinguish whether the localized attack is pitting or crevice corrosion. Treating every `E_b` point as `Epit` would therefore overstate the source.

## Coverage assessment

Figure 4 contains numerous discrete `E_b` markers versus temperature for alloys C-276 and 625 at several chloride concentrations. Those are potentially valuable localized-corrosion data, but their endpoint semantics differ from an unambiguous pitting potential.

| Dataset policy | Assessment of zero Reference 4 rows |
|---|---|
| Strictly pitting potentials only | Reasonable; no correction required |
| Pitting plus ambiguous localized-breakdown potentials | Incomplete; Figure 4 should be reviewed and added with an ambiguity flag |

The curve/legend complexity and endpoint ambiguity make automatic ingestion inappropriate. Any inclusion should preserve `E_b`, cyclic-polarization method, possible crevice contribution, reference-electrode conversion, temperature, and chloride concentration.

## Recommended action

1. Document whether the `Pitting Potential` dataset excludes endpoints that the authors cannot attribute specifically to pitting.
2. If it does, retain zero rows and record Reference 4 as reviewed/out of scope.
3. If broader breakdown potentials are allowed, manually curate Figure 4 into a distinct `breakdown/damaging potential` class rather than silently relabeling it `Epit`.

## Overall assessment

**Record accuracy: not applicable.** No Reference 4 rows exist.

**Coverage: policy-dependent.** The current exclusion is scientifically defensible, but it should be explicit rather than indistinguishable from an unaudited omission.
