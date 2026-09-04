# Audit Report: Citrine Pitting-Potential Records for Reference 9

## Scope

This report compares all 39 Reference 9 records in the Citrine `Pitting Potential` sheet with:

- [W. M. Carroll and E. E. Lynskey, Corrosion Science 36 (1994), 1667](<../papers/9_W. M. Carroll, E. E. Lynskey, Corros. Sci. 36 (1994)_ p. 1667.pdf>)
- [Citrine source workbook](../citrine_database/CRA_database_Scientific_Data_Publication_12102020.xlsx), Excel rows 490-528 (record numbers 488-526)

Audit date: 2026-09-03

Workbook evidence: 【CRA_database_Scientific_Data_Publication_12102020.xlsx:Pitting Potential:A490:AM528】

The experimental section, Figure 9, and the paper's other pitting-potential tables and graphs were checked visually. The repository's [figure catalog](../mineru_output/paper_9/paper_9_figures.json) and [figure extraction](../mineru_output/paper_9/paper_9_figure_extractions.json) were used as secondary cross-checks.

## Executive summary

All 39 Citrine values are digitizations of Figure 9 and lie on or near the intended plotted series. One of Figure 9's 40 markers—Ni in 1.0M NaBr at pH 5—is missing. The database also assigns unjustified two-decimal precision to graph readings, represents commercially sourced elemental wires as exactly 100% pure, and loses the paper's warning that some plotted endpoints are not definite pitting potentials but potentials at a current-density criterion. Most of the paper's primary stainless-steel pitting data are not included at all.

| Severity | Finding | Affected records |
|---|---|---:|
| High | Figure 9 contains a Ni/1.0M NaBr/pH 5 point near -50 mV SCE, but no corresponding row exists. | Coverage within Figure 9 |
| High | Some Figure 9 points use the potential at 10 microA/cm2 because definite pitting was not evident; Citrine labels every point simply as pitting potential and does not preserve this endpoint distinction. | Indeterminate subset of 488-526 |
| Medium | Graph-derived values are stored to 0.01 mV although the printed plot supports only approximate readings. | 488-526 |
| Medium | Commercial Fe, Ni, and Mo wires are encoded as exactly 100 wt% despite no chemical analyses being reported. | 488-516 |
| Medium | The paper's extensive 316L, 316, and 302 pitting-potential datasets are absent. | Coverage |
| Low | NaBr rows use `[Cl-] = 0`, but no structured field preserves the 1.0M bromide concentration. | NaBr rows |

## Figure 9 reconciliation

Figure 9 plots Fe, Ni, Mo, and Ni80Cr20 in 1.0M NaCl and 1.0M NaBr at pH 3, 4, 5, 7, and 9: 4 materials x 2 solutions x 5 pH values = 40 markers.

| Material | NaCl points stored | NaBr points stored | Assessment |
|---|---:|---:|---|
| Fe | 5/5 | 5/5 | Complete |
| Ni | 5/5 | 4/5 | **pH 5 missing** |
| Mo | 5/5 | 5/5 | Complete |
| Ni80Cr20 | 5/5 | 5/5 | Complete |
| **Total** | **20/20** | **19/20** | **39 of 40** |

The missing point is approximately **-50 mV SCE** for Ni in 1.0M NaBr at pH 5.

Manual visual readings of the plot are generally within about 0-23 mV of the Citrine values. That spread is compatible with interpreting a small printed graph and is not evidence that the underlying series were assigned incorrectly. It does show that entries such as -661.26, -22.71, and 342.67 mV are falsely precise. A source-faithful representation should round the values and attach digitization uncertainty.

## Endpoint-definition discrepancy

The paper states that where definite pitting potentials were not evident on the polarization plots, it used the potential corresponding to an anodic current density of 10 microA/cm2 in Figure 9. It does not identify each substituted point individually.

Citrine provides no flag for this distinction. Consequently, users cannot tell which rows represent observed pit initiation and which represent a current-density proxy. This is a material semantic loss: a proxy threshold should not be silently treated as the same measurement endpoint as a definite pitting potential.

## Composition and condition provenance

- The paper describes Fe, Ni, and Mo as commercially available wires of similar thickness; it does not report analyses demonstrating 100.000 wt% purity. `Fe = 100`, `Ni = 100`, and `Mo = 100` should be nominal identities or material labels, not exact measured compositions.
- Ni80Cr20 is explicitly described as an 80% Ni:20% Cr wire, so its nominal 80/20 representation is traceable.
- The 1 mV/s scan rate, nitrogen purging, pH adjustment with sulfuric acid or NaOH, and SCE reference are faithfully represented.
- The paper does not state a test temperature; Citrine's `NA` is correct.
- The authors say reported results are averages of at least three identical experiments, but the database preserves neither replicate count nor uncertainty.

## Broader coverage audit

Reference 9 is primarily a pitting-potential paper about stainless-steel wire electrodes, yet Citrine selects only Figure 9's elemental/80Ni-20Cr comparison. It omits discrete pitting-potential results from:

- Figure 2: 316L as a function of halide concentration and pH;
- Figure 4 and Table 1: 316 wire as a function of halide concentration, pH, and loop size;
- Figure 5: 302 wire versus pH;
- Figure 6: 316 wire in pure and mixed NaCl/NaBr solutions;
- Figure 8: 316 wire in halide/sulfate mixtures; and
- Table 2: chemically pretreated 316 wire.

Some points overlap across tables and figures, so a unique missing-record total should be established by de-duplicating material, solution, pH, pretreatment, geometry, and run. The undercoverage itself is unambiguous and substantial.

## Recommended corrections

1. Add the missing Ni/1.0M NaBr/pH 5 point at approximately -50 mV SCE, with digitization uncertainty.
2. Add an endpoint flag distinguishing definite pitting potential from the 10 microA/cm2 proxy used by the authors.
3. Round Figure 9 digitizations to defensible precision and preserve graph-reading uncertainty.
4. Represent elemental wires as nominal material identities unless verified purity analyses are available.
5. Add a structured bromide concentration field or general anion/concentration schema.
6. Curate the omitted stainless-steel datasets after de-duplicating table and figure presentations.

## Overall assessment

**Stored Figure 9 series: broadly accurate but incomplete.** The 39 values follow the source graph, but one of 40 points is missing and the numerical precision is unjustified.

**Endpoint semantics: needs correction.** Citrine loses the distinction between actual pitting and a 10 microA/cm2 surrogate.

**Coverage: severely incomplete.** Most of the paper's stainless-steel pitting-potential evidence is absent.
