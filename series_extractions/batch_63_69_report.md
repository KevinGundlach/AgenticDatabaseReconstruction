# Extract-series batch: Papers 63–69

## Scope

Requested papers: 63, 64, 65, 66, 67, 68, and 69. Six PDFs were supplied; no file beginning with reference 65 was found in the papers folder. Papers 61 and 62 are outside this batch. Selection follows the skill default: explicit pitting-potential plots/tables, retaining companion quantities within selected sources. Supporting composition tables were not requested.

All 61 pages of the six supplied PDFs were visually inspected using Poppler renders, with enlarged views for overlapping symbols and plotted values. The PDFs were the sole evidence source. No OCR, automated marker detection, curve tracing, or programmatic chart extraction was used. No missing main-article pages were identified in the supplied files. Neighboring article material on Paper 66’s final page, reference material from a preceding article on Paper 69’s first page, and publisher advertising in Paper 67 were excluded.

## Outputs and validation

All six JSON files passed the skill’s validate_output.py in the project’s frozen uv environment. Counts below are derived from the saved JSON. Structural validation checks format and internal consistency; it does not certify scientific fidelity.

| Paper | Pages supplied / inspected | Output | Validation | Complete | Partial | None | Rows |
|---|---:|---|---|---:|---:|---:|---:|
| 63 | 18 / 18 | [paper_63.json](paper_63.json) | Passed | 1 | 0 | 0 | 3 |
| 64 | 10 / 10 | [paper_64.json](paper_64.json) | Passed | 0 | 0 | 0 | 0 |
| 65 | Not supplied / 0 | No output: missing PDF | Not run | — | — | — | — |
| 66 | 4 / 4 | [paper_66.json](paper_66.json) | Passed | 6 | 0 | 0 | 36 |
| 67 | 11 / 11 | [paper_67.json](paper_67.json) | Passed | 6 | 0 | 0 | 21 |
| 68 | 10 / 10 | [paper_68.json](paper_68.json) | Passed | 1 | 0 | 0 | 3 |
| 69 | 8 / 8 | [paper_69.json](paper_69.json) | Passed | 2 | 0 | 0 | 12 |
| **Total** | **61 / 61** | **6 files; 1 PDF missing** | **All 6 passed** | **16** | **0** | **0** | **75** |

The 16 series contain 75 source-specific rows, including companion quantities and repeated results. These are not counts of independent experiments. Digitized coordinates are visual estimates; connecting and fitted lines were not sampled. Complete status applies to each extracted series and does not imply that missing Paper 65 was processed.

## Items needing attention

- **Paper 65:** PDF missing. It was not inspected, no extraction JSON was created, and no validation was run.
- **Paper 66, Figure 5:** The two square-marker groups carry upward arrows and the annotation “no pitting.” They are retained as lower bounds near 1150 mV_H, with the annotation, rather than exact observed pitting potentials. The closely spaced Mn compositions were resolved using the visible composition table; composition data were not separately extracted.
- **Paper 67, Figures 4 and 7 / Table 4:** Figure 7 shows Eb around 560 mV at 2 at% Mo, whereas Table 4 prints 580 mV. The zero-Mo Eb in Figure 7 is about 480 mV, versus about 520 mV for 4 at% Cr in Figure 4. Figure 7’s Ep values at 0.5, 1, and 2 at% Mo are approximately −140, 40, and 260 mV; Table 4 prints −150, 20, and 250 mV. Source-specific values are retained separately, with warnings in the affected series.
- **Paper 67, Table 7:** Crevice and noncrevice columns are separated. Noncrevice Eb is a pitting-potential target; crevice Eb, protection potential Ep, Ecorr, and differences are non-target companions.
- **Paper 68, Table 3:** Ep is pitting potential, Epp is protection potential. Printed potential differences are retained as non-target companion quantities.
- **Paper 69, Figure 6:** The open circle at approximately 13 at% Mo has an upward arrow at 0 mV. It is retained as a lower bound with the arrow label, not an exact measured breakdown potential. The nearby prose reports no degradation after polarization to 0 V.
- **Paper 64:** All ten pages were inspected; no eligible discrete pitting-potential source was found. Its JSON contains an empty series array. The Ec indication in Figure 3 labels a continuous polarization curve and supplies no explicit numerical pitting-potential annotation.
- **Rendering:** Poppler emitted embedded-font/stream warnings for Paper 66 and unavailable-font warnings for Papers 67 and 69. Selected values, units, legends, and annotations remained visually readable in the page images and enlarged views. No unresolved target glyph was identified.

## Source coverage and exclusions

| Paper | Extracted sources | Excluded sources and reason |
|---|---|---|
| 63 | Table 2 (PDF p. 5), including companion electrochemical parameters | Table 1: composition. Tables 3–5: XPS peak areas. Figure 1: continuous polarization curves. Figures 2–8: XPS spectra. |
| 64 | None; all supplied pages inspected | Table 1: composition. Table 2: implantation parameters and concentration. Figures 1–2: backscattering/depth profiles. Figure 3: continuous polarization curves. Figure 4: current-time response at an applied potential. Figures 5–10 and 12: microscopy/diffraction. Figure 11: schematic. |
| 65 | Not inspected: missing PDF | No source classification possible. |
| 66 | Figure 5, six electrolyte/condition groups (PDF p. 3) | Table 1: composition. Figures 1–2: polarization curves. Figure 3: critical passivation potential, not pit nucleation potential. Figure 4: passive current density. Figures 6–8: microscopy. Neighboring article on PDF p. 4 excluded. |
| 67 | Tables 3–4 and Figure 4 (PDF p. 5); Figure 7, Eb and Ep groups (p. 6); Table 7 (p. 10) | Table 1: composition. Tables 2/5: XPS factors/composition. Table 6: initiation time. Table 8: crevice-attack counts/depths. Figures 1/9: apparatus/crystal structures. Figures 2–3, 5–6, 8, 11, 16–18: polarization curves. Figure 10: microscopy. Figure 12: Ecorr-time traces. Figures 13–15: XPS spectra and surface ratios. Publisher advertising excluded. |
| 68 | Table 3 (PDF p. 7) | Table 1: composition. Table 2: current-density ratios. Figures 1–3: thermodynamic diagram and apparatus/protocol schematics. Figures 4–6: dissolution kinetics in artificial pits, not explicit pitting-potential series. |
| 69 | Figure 6, filled circles and upward-bound open circle (PDF p. 5) | Table I: spectral sensitivity factors. Table II: corrosion potential/Tafel slope, with no pitting-potential column. Figure 1: polarization curves. Figures 2–3/11: microscopy/diffraction. Figures 4–5/8–9: corrosion-potential trends. Figures 7/10: XPS spectra/film chemistry. Figure 12: schematic kinetic diagram. Preceding article reference material excluded. |

No pitting potential was inferred from a polarization curve. No outstanding unreadable cells remain in the selected sources; missing Paper 65 and source discrepancies are the material limitations.
