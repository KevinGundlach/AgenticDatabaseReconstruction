# Extract-series batch: Papers 51–60

## Scope

Requested papers: 51, 52, 53, 54, 55, 56, 57, 58, 59, and 60. All ten PDFs were present. Selection follows the skill default: explicit pitting-potential plots/tables, retaining companion quantities within selected sources. Supporting composition tables were not requested.

All 116 supplied PDF pages were visually inspected using Poppler renders, with enlarged views of dense plots and small tables. The PDFs were the sole evidence source. No OCR, automated marker detection, curve tracing, or programmatic chart extraction was used. No missing main-article pages were identified. Neighboring articles beginning on the final pages of Papers 53 and 54, and publisher calendar material in Paper 51, were excluded. Paper 55 is an 11-page manuscript version, which differs in pagination from the citation in its filename.

## Outputs and validation

All ten JSON files passed the skill’s validate_output.py in the project’s frozen uv environment. The counts below are derived from the saved JSON. Validation checks structure and internal consistency; it does not certify scientific fidelity or resolve overlapping markers.

| Paper | Pages supplied / inspected | Output | Validation | Complete | Partial | None | Rows |
|---|---:|---|---|---:|---:|---:|---:|
| 51 | 7 / 7 | [paper_51.json](paper_51.json) | Passed | 0 | 0 | 0 | 0 |
| 52 | 13 / 13 | [paper_52.json](paper_52.json) | Passed | 3 | 4 | 0 | 48 |
| 53 | 8 / 8 | [paper_53.json](paper_53.json) | Passed | 3 | 0 | 0 | 32 |
| 54 | 10 / 10 | [paper_54.json](paper_54.json) | Passed | 2 | 0 | 0 | 64 |
| 55 | 11 / 11 | [paper_55.json](paper_55.json) | Passed | 3 | 1 | 0 | 20 |
| 56 | 12 / 12 | [paper_56.json](paper_56.json) | Passed | 7 | 14 | 0 | 242 |
| 57 | 21 / 21 | [paper_57.json](paper_57.json) | Passed | 0 | 0 | 0 | 0 |
| 58 | 20 / 20 | [paper_58.json](paper_58.json) | Passed | 0 | 0 | 0 | 0 |
| 59 | 10 / 10 | [paper_59.json](paper_59.json) | Passed | 0 | 0 | 0 | 0 |
| 60 | 4 / 4 | [paper_60.json](paper_60.json) | Passed | 1 | 0 | 0 | 8 |
| **Total** | **116 / 116** | **10 files** | **All passed** | **19** | **19** | **0** | **414** |

The 38 series include non-target companions and explicitly labeled calculated results. Rows are source-specific records, not independent experiments. Tables and figures may repeat results, and rows with unresolved cells still count as rows. Digitized coordinates and interval endpoints are visual estimates. Connecting lines, fitted relationships and continuous envelopes were not sampled.

## Items needing attention

- **Paper 52, Figures 17–18:** Four groups are partial because overlapping markers limit recovery and exact counts near PREN 24. Figure 17 states n = 8 for the base-metal fit, but only six filled-marker centers are distinguishable; obscured replicates were not reconstructed from Table 2. Figure 18’s calculated values are kept separate from experimental values, and its dotted calculated range is a continuous envelope rather than discrete error bars. Figure 8’s interval endpoints are retained with unspecified statistical interpretation; n and Al annotations are included as visible row identifiers.
- **Paper 53, Table 5:** The final steel group is printed E, whereas its caption refers to D,F and the matching entries in Table 3 are labeled F. The printed E is retained. Ur is the onset of repassivating pit formation and Ub is stable pit formation: both are targets. Up is pit repassivation and is a non-target companion. Blank/dash entries are null; horizontal alignment in the table is preserved without claiming separate-method columns represent paired experiments.
- **Paper 54, Tables 2–3:** No-breakdown qualifications are retained as strings rather than exact measured pitting potentials. For specimen 21 in the 30 C NaCl column, Table 2 gives a scan ceiling of 708 mV, whereas Table 3’s footnote gives 908 mV. These differing qualifications are preserved. Table 2’s other unqualified dashes remain dashes.
- **Paper 55, Figure 8:** The repassivation-potential group is partial because interval endpoints at 1, 10 and 1000 h cannot be distinguished from the square markers. Their centers are retained. Table 2’s printed plus/minus terms and Figure 8’s visible intervals have no unambiguously stated statistical category in this supplied manuscript, so none was imposed.
- **Paper 56, Figures 4, 7 and 8:** Dense and overlapping distribution markers make 14 groups partial. Separable centers are retained, but full replicate recovery is not established. Percent ordinates were read from the nonlinear probability scales; Figure 7 survival probabilities were read on its logarithmic ordinate. Small differences among repeated plotted distributions and the printed table were not reconciled by replacing source values. Figure 9 reports pitting-potential differences, which are retained as non-target quantities rather than absolute pitting potentials.
- **Papers 56 and 60, printed tables:** Both explicitly report 99% confidence intervals. Paper 56 Table 1 prints −0.044 ± 0.130 V for nanocrystalline Al90Fe5Gd5, whereas Paper 60 Table II prints +0.044 ± 0.130 V. Both signs are retained. Paper 60 does not print Ep entries for the bracketed Al87Ni8.7Y4.3 rows; these are null, while its printed Er entries are preserved.
- **Papers 51, 57, 58 and 59:** All supplied pages were inspected, but no eligible discrete pitting-potential figure/table was found. These outputs contain empty series arrays. Paper 51 measures critical pitting/crevice temperatures. Papers 57–59 contain polarization or surface-analysis results, with no pitting potential inferred from their curves.
- **Rendering:** Poppler reported unavailable font names for several PDFs. Visible selected values and consequential labels were reviewed in the rendered pages; unrelated garbled symbols were not used to populate extraction fields. No specific unresolved target-unit glyph was identified in the selected sources.

## Source coverage and exclusions

| Paper | Extracted sources | Excluded sources and reason |
|---|---|---|
| 51 | None | Table 1: compositions and critical pitting/crevice temperatures, not pitting potentials. Figure 1: apparatus. Figures 2–4: critical pitting temperature. Figure 5: critical crevice temperature. Figures 6–7: microscopy and composition profiles. Publisher calendar excluded. |
| 52 | Table 2 (PDF p. 3); Figure 3 (p. 4); Figure 8 (p. 8); Figure 17, base/welded groups (p. 11); Figure 18, experimental/calculated groups (p. 12) | Tables 1/4: compositions/inclusions. Table 3: passive-film constituents/depths. Table 5: current density at an applied potential. Figures 1–2, 13–15: polarization curves. Figures 4–5: XPS profiles. Figures 6–7, 9–12: microscopy. Figure 16: regression fit quality versus weighting factor. Figure 19: continuous theoretical relationship plotted as perspective ridges, not discrete measured markers/bars. |
| 53 | Tables 3 (PDF p. 4), 4 and 5 (p. 5) | Table 1: composition. Table 2: indicator-test attack categories versus heat treatment/concentration. Table 6: pit counts at applied test potentials, not measured pitting potentials. Figure 1: microscopy. Figures 2–5: stress-corrosion lifetime versus stress/applied potential. Neighboring article excluded. |
| 54 | Tables 2 (PDF p. 3) and 3 (p. 4) | Tables 1/5: composition. Table 4: passive current density. Table 6: polarization resistance/Tafel/current results. Figures 1–2, 4–5, 11–12: polarization curves. Figures 3, 6–7: microscopy. Figure 8: phase boundaries. Figures 9–10: EDX spectra. Neighboring article excluded. |
| 55 | Table 2 (PDF p. 9); Figure 8, Epit/OCP/Erp groups (p. 11) | Table I: composition. Figure 1: composition/structure map. Figure 2: diffraction. Figures 3/7: OCP. Figure 4: passive currents. Figures 5/9: polarization curves. Figure 6: repassivation-only plot. Figure 8 continuous crystalline reference lines were not sampled as discrete points. |
| 56 | Table 1 (PDF p. 5); Figure 4(a–b), Epit/Ecorr/Erp (p. 6); Figure 7, four survival groups (p. 7); Figure 8(a–b), four groups per panel (p. 8); Figure 9(a–b), pitting-potential difference bars (p. 8) | Figures 1–2: microscopy. Figure 3: polarization/microscopy; definition arrows are not numerical Ep annotations. Figures 5–6 and 10: repassivation-only distributions. Figures 11–12: microscopy/AFM. |
| 57 | None | Table 1: composition. Table 2: optical constants/film thickness. Tables 3–4: XPS binding energies. Figures 1–6: polarization curves. Figures 7–8: impedance. Figures 9–10: ellipsometry. Figure 11: XPS spectra. Figures 12–14: spectral peak-area ratios. Prose-only numerical pitting potentials excluded. |
| 58 | None | Table 1: composition. Tables 2–3: spectroscopy peaks, energies and sensitivity factors. Figures 1–2: polarization curves. Figure 3: current-time transients. Figures 4/11: XPS spectra. Figure 5: film thickness. Figure 6: cation fractions. Figures 7–10, 12–15: AES/SIMS profiles. Applied film-formation potentials are not pitting potentials. |
| 59 | None | Figure 1: literature summary of chloride detection. Figure 2: experimental conditions and applied potentials. Figure 3: polarization curves. Figures 4–5, 7–8: AES/SIMS depth profiles. Figure 6: film thickness. |
| 60 | Table II, including footnote a (PDF p. 4) | Table I: tensile strength/density. Figures 1–3: microscopy/diffraction. Figure 4(a–b): ohmically corrected artificial-pit growth-potential/current curves, not explicit pitting-potential result series. |

Full supplied-page coverage does not resolve the partial-series issues listed above. No pitting potentials were inferred from polarization curves.
