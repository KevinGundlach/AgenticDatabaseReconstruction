# Extract-series batch: Papers 31–40

## Scope

Requested papers: 31, 32, 33, 34, 35, 36, 37, 38, 39, and 40. All ten requested references were present. Selection follows the skill default: explicit pitting-potential figures/tables, including companion quantities within selected sources. Supporting composition tables were not requested.

All 130 supplied PDF pages were visually inspected using Poppler renders, with enlarged views for small symbols and tables. The PDFs were the sole evidence source. No OCR, automated marker detection, or curve tracing was used. No missing main-article pages were identified. Papers 36 and 38 include fragments of neighboring articles; these were excluded. Paper 39 includes two unnumbered figure plates within its 15 PDF pages.

## Outputs and validation

All ten JSON files passed the skill’s validate_output.py in the project’s frozen uv environment. Counts below are derived from the saved JSON. Validation checks structure and internal consistency; it does not certify scientific fidelity or completeness of the source values.

| Paper | Pages supplied / inspected | Output | Validation | Complete | Partial | None | Rows |
|---|---:|---|---|---:|---:|---:|---:|
| 31 | 11 / 11 | [paper_31.json](paper_31.json) | Passed | 0 | 1 | 0 | 5 |
| 32 | 5 / 5 | [paper_32.json](paper_32.json) | Passed | 0 | 4 | 0 | 20 |
| 33 | 10 / 10 | [paper_33.json](paper_33.json) | Passed | 0 | 0 | 0 | 0 |
| 34 | 16 / 16 | [paper_34.json](paper_34.json) | Passed | 2 | 0 | 0 | 8 |
| 35 | 18 / 18 | [paper_35.json](paper_35.json) | Passed | 0 | 0 | 0 | 0 |
| 36 | 7 / 7 | [paper_36.json](paper_36.json) | Passed | 9 | 0 | 0 | 43 |
| 37 | 26 / 26 | [paper_37.json](paper_37.json) | Passed | 0 | 8 | 0 | 118 |
| 38 | 10 / 10 | [paper_38.json](paper_38.json) | Passed | 4 | 0 | 0 | 23 |
| 39 | 15 / 15 | [paper_39.json](paper_39.json) | Passed | 7 | 0 | 0 | 28 |
| 40 | 12 / 12 | [paper_40.json](paper_40.json) | Passed | 0 | 0 | 0 | 0 |
| **Total** | **130 / 130** | **10 files** | **All passed** | **22** | **13** | **0** | **245** |

The 35 series include companion non-target quantities. Rows are source-specific records, not independent experiments; sources can repeat results. Digitized coordinates are visual estimates. Connecting lines, fitted curves, and region boundaries were not sampled.

## Items needing attention

- **Paper 31, Table 3:** Poppler reported unavailable fonts. The rendered current-unit glyph appears as α rather than µ and is preserved provisionally as αA/cm²; the series is partial pending verification of this glyph. Table 3 prints icrit = 30.0 for the 6% Mo steel, whereas nearby prose prints 30.3. The tabulated value is retained. Only Epit is a target; corrosion, passivation, and transpassive potentials are companions.
- **Paper 32, Figures 5–8:** All four series are partial because several small repassivation-potential intervals cannot be distinguished from marker footprints. Visible separable intervals are retained. Captions identify the intervals as the 25th and 75th percentiles, represented by percentile_25_75. Figure 5 has a marker near 10.7 nm although Table I gives a nominal 10 nm microstructure; the plotted coordinate is retained. Epit is a target and Erp is not.
- **Paper 37, Figure 3:** All eight groups are partial. Overlapping diamonds prevent recovery of every replicate; only distinguishable centers are retained, and closely spaced coordinates are approximate. The total number of obscured replicates is unresolved. Final breakdown Eb is the pitting-potential target. Einit, the first repassivating-pit onset, is preserved separately as a non-target companion.
- **Papers 33, 35, and 40:** The complete supplied articles contain no eligible discrete pitting-potential plots or tables. Their JSON files contain empty series arrays. Paper 40 reports numerical Ep values in prose, but these are outside the requested figure/table scope; no values were inferred from its polarization curves.
- **Paper 36:** Figure 1 distinguishes repassivating pits, stable pitting, and potentiostatically initiated pits; these retain separate series identities. The source labels the plotted quantity Ep. Table 2 preserves separate scan and scratch pitting targets and non-target protection potentials.
- **Paper 39, Table 2:** Printed > +3.0 values are retained as qualified strings. The intergranular-corrosion test potentials are non-target companions. Figure 3’s explicitly printed pitting potential is transcribed from its caption; the current-time trace is not digitized.
- **Papers 34 and 38:** No unresolved extraction issues were identified in the selected discrete series.

## Source coverage and exclusions

| Paper | Extracted sources | Excluded sources and reason |
|---|---|---|
| 31 | Table 3 (PDF page 5) | Tables 1, 2, 4: composition, XPS sensitivity/free paths, and XPS areas. Figures 1–2: polarization curves. Figures 3–5 and 8: XPS spectra. Figures 6–7 and 9: composition/intensity ratios. Editorial material excluded. |
| 32 | Figures 5–8 (PDF page 4) | Table I: heat treatments and microstructures. Figure 1: TEM. Figures 2–4: polarization and current-time traces; arrows without printed numerical pitting-potential values were not digitized. |
| 33 | None | Table 1: composition. Table 2: corrosion potentials, peak currents, and passive currents. Figures 1 and 3: polarization curves. Figure 2: current-time response. Figures 4–5: XPS spectra. Figures 6–7: XPS intensity profiles. |
| 34 | Figure 4, 1.0 M KCl and 0.5 M HCl groups (PDF page 9) | Table 1: composition. Figures 1–3: polarization/current-potential curves; Figure 2 has qualitative pitting arrows without printed numerical values. Figures 5–10: microscopy/EDS. |
| 35 | None | Tables 1–3: composition, dissolved nitrogen species, and binding/free energies. Figure 1: polarization. Figure 2: current-time response. Figure 3: microscopy. Figures 4, 8, 11–12: ESCA spectra. Figures 5–7, 9–10, 13: film thickness, intensity ratios, nitrogen coverage, and composition. Applied potentials are not pitting-potential results. |
| 36 | Table 2 (PDF page 5); Figure 1, eight groups (PDF page 2) | Table 1: composition. Figures 2–3: scratch-current response and microscopy. Figures 4–5: polarization curves. Figure 6: nickel content versus concentration ratio at minimum Ep, without a measured pitting-potential axis. Neighboring article fragments on first/last pages excluded. |
| 37 | Figure 3, four panels with open/solid diamonds separated (PDF page 11) | Table 1: composition. Figure 1: critical pitting temperature. Figure 2: pit-initiation location fractions. Figure 4: polarization/microscopy. Figures 5–6: passive currents, transients, spectra and counts. Figures 7–9: polarization/peak-current results. Figures 10–11: impedance parameters and polarization. Figure 12: Pourbaix regions and dissolved-nitrogen fractions. Figure 13: polarization in artificial-pit solutions. |
| 38 | Figure 6, two groups (PDF page 4); Figure 14 upper panel (PDF page 6); Figure 18 lower panel (PDF page 8) | Table 1: composition. Table 2: SCC outcomes. Figures 1–5: mechanical properties, heat cycle, apparatus, schematics, and microscopy. Figures 7 and 18 upper panel: critical pitting temperature. Figures 8–10, 15, 17, 19: SCC, Strauss/Huey tests, and corrosion rates. Figures 11–12, 16, 20, 22: microscopy. Figure 13: continuous time–temperature boundaries for pitting-potential regions, no discrete values. Figure 14 lower panel: corrosion rate. Figure 21: EPMA composition. Neighboring article fragments excluded. |
| 39 | Figure 5, five alloy/purity groups (PDF page 6); Table 2 (PDF page 12); Figure 3 caption (PDF page 4) | Table 1: attack classifications across applied-potential ranges, not explicit measured pitting-potential entries. Figures 1, 8, 10: schematics. Figures 2, 6, 12: polarization curves. Figures 3–4: current-time traces. Figures 7, 9, 11, 13: microscopy with applied-potential examples/schematic curves. Figures 14–15: continuous schematic potential/region diagrams. |
| 40 | None | Tables 1–2: bulk/phase compositions and PREN. Figures 1–2: critical-pitting-temperature/current/potential traces. Figure 3: continuous polarization curves. Figures 4–5: microscopy. Figures 6–7: composition profiles. Figure 8: PREN, not pitting potential. Prose-only numerical Ep values excluded. |

Prose-only numerical examples, bibliographic lists, and unrelated publisher material were outside the figure/table selection. No pitting potentials were inferred from polarization curves. Full page coverage does not resolve the partial-series issues listed above.
