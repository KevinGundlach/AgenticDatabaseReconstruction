# Extract-series batch: Papers 71–85

## Scope

Requested papers: 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, and 85. Fourteen PDFs were supplied; no file beginning with reference 79 was found in the papers folder. Selection follows the skill default: explicit pitting-potential plots/tables, retaining companion quantities in selected sources. Supporting composition tables were not requested.

All 125 pages of the 14 supplied PDFs were visually inspected using Poppler renders and enlarged views. The PDFs were the sole evidence source; no OCR, automated marker detection, curve tracing, or programmatic chart extraction was used. No missing main-article pages were identified. Publisher material and neighboring articles were excluded. Paper 80 is a 12-page manuscript version; source locators use PDF page numbers.

## Outputs and validation

All 14 JSON files passed the skill’s validate_output.py in the frozen project environment. Counts below are derived from the saved JSON. Structural validation checks format and consistency; it does not certify scientific fidelity or resolve partial extractions.

| Paper | Pages supplied / inspected | Output | Validation | Complete | Partial | None | Rows |
|---|---:|---|---|---:|---:|---:|---:|
| 71 | 4 / 4 | [paper_71.json](paper_71.json) | Passed | 2 | 0 | 0 | 21 |
| 72 | 5 / 5 | [paper_72.json](paper_72.json) | Passed | 3 | 0 | 0 | 19 |
| 73 | 6 / 6 | [paper_73.json](paper_73.json) | Passed | 0 | 0 | 0 | 0 |
| 74 | 16 / 16 | [paper_74.json](paper_74.json) | Passed | 1 | 4 | 0 | 51 |
| 75 | 12 / 12 | [paper_75.json](paper_75.json) | Passed | 4 | 0 | 0 | 20 |
| 76 | 5 / 5 | [paper_76.json](paper_76.json) | Passed | 6 | 0 | 0 | 30 |
| 77 | 12 / 12 | [paper_77.json](paper_77.json) | Passed | 0 | 0 | 0 | 0 |
| 78 | 10 / 10 | [paper_78.json](paper_78.json) | Passed | 0 | 0 | 0 | 0 |
| 79 | Not supplied / 0 | No output: missing PDF | Not run | — | — | — | — |
| 80 | 12 / 12 | [paper_80.json](paper_80.json) | Passed | 12 | 6 | 0 | 98 |
| 81 | 3 / 3 | [paper_81.json](paper_81.json) | Passed | 4 | 0 | 0 | 12 |
| 82 | 20 / 20 | [paper_82.json](paper_82.json) | Passed | 0 | 0 | 0 | 0 |
| 83 | 9 / 9 | [paper_83.json](paper_83.json) | Passed | 0 | 8 | 0 | 163 |
| 84 | 6 / 6 | [paper_84.json](paper_84.json) | Passed | 0 | 0 | 0 | 0 |
| 85 | 5 / 5 | [paper_85.json](paper_85.json) | Passed | 6 | 0 | 0 | 18 |
| **Total** | **125 / 125** | **14 files; 1 PDF missing** | **All 14 passed** | **38** | **18** | **0** | **432** |

The 56 series contain 432 source-specific rows, including companion quantities and repeated results. These are not counts of independent experiments. Digitized values are visual estimates; fitted and connecting lines were not sampled. Papers 73, 77, 78, 82, and 84 were inspected and contain empty series arrays because no eligible sources were found.

## Items needing attention

- **Paper 79:** Missing PDF; not inspected, no JSON created, validation not run.
- **Paper 71, Table II:** Steel 19 nitrogen is printed as 0.435%, whereas Table I gives 0.455%. Table II was retained as printed. Crevice breakdown is a non-target companion; plain-surface breakdown is a target.
- **Paper 72:** Table 3 retains printed dashes for alloy 4. Ec−Ep in Figure 4 is a potential difference, not itself a pitting-potential target.
- **Paper 74, Figures 3–4:** Four series are partial because overlapping markers prevent full replicate recovery. The shared zero-addition cluster is stored with the W group. The lowest 8W point is approximately −300 mV in Figure 3 but −200 mV in Figure 4; source-specific values are retained.
- **Paper 75, Figure 3:** The rightmost 1 M NaCl marker plots near pH 10.2 despite prose describing a range up to pH 10. Its plotted coordinate is retained.
- **Paper 76:** The filename cites page 349, while the scanned article occupies printed pages 394–398. Figure 2 square markers annotated “no pitting” with upward arrows are lower bounds. Table 2 inequalities and Figure 4 intervals are retained without inventing an error-bar statistical interpretation.
- **Paper 80:** Six series are partial because dense or overlapping markers limit replicate recovery (Figure 2, Figure 3 W fresh, and Figure 4 fresh/aged). The paper questions the measured composition of its anomalous 10 at.% Mo sample; its plotted coordinates are retained. Ep and aged Ep are targets; ER is not.
- **Paper 83, Figures 6–8:** Eight series are partial. Each Z plot combines pitting and transpassive results; upper-branch and unresolved transition values are retained in a separate non-target column. Lower-branch values are pitting targets. Marker overlap and the transition between mechanisms limit definitive point assignment and replicate counting. No values were inferred from polarization curves.
- **Papers 84–85:** Captions or internal labels sometimes say pitting potential while the actual ordinate is current density. These sources are excluded rather than classified as pitting-potential measurements. Paper 85 Figure 1 has a shared endpoint near 0.16% N and 1150 mV for both carbon groups; it is represented in each group.
- **Rendering:** Poppler reported unavailable-font warnings for Papers 71, 78, 80, and 85. The selected labels, axes, values, and annotations were visually readable in the page images and enlarged views.

## Source coverage and exclusions

| Paper | Extracted sources | Excluded sources and reason |
|---|---|---|
| 71 | Table II (PDF p. 3); unnumbered summary table (p. 4) | Table I: composition. Publisher cover and advertising excluded. |
| 72 | Tables 2–3 (pp. 2, 4); Figure 4 (p. 4), potential difference with companion weight loss | Table 1: composition; Table 4: corrosion rates. Figure 1: micrograph; Figure 2: continuous polarization with a qualitative Ec indication; Figure 3: schematic. Neighboring article material excluded. |
| 73 | None; all six pages inspected | Table 1: composition. Figures 1–3 and 7: polarization curves; Figures 4–6: ESCA; Figure 8: Pourbaix diagram. Prose-only potentials and neighboring article material excluded. |
| 74 | Figures 3–4, Mo/W groups (pp. 6–7); Figure 5 (p. 8) | Table 1: composition; Table 2: elemental properties. Figures 1–2 and 6–7: polarization curves; Figure 8: schematic; Figures 9–10: primary passivation potential; Figures 11–12: critical anodic current. |
| 75 | Figure 1 (p. 6); Table 1 (p. 8); Figure 3, two concentration groups (p. 10) | Figure 2: current-time curves; Figure 4: polarization curves. Theoretical equations and fitted lines were not sampled. |
| 76 | Figure 2, three electrolyte groups (p. 2); Table 2 and Figure 4, two potential definitions (p. 3) | Table 1: composition. Figure 1: polarization; Figure 3: induction time/pit count versus applied potential, with a qualitative Enp band; Figure 5: pit counts; Figures 6–8: micrographs. Neighboring article material excluded. |
| 77 | None; all 12 pages inspected | Table 1: composition. Figures 1–3: polarization curves; Figures 4a/b: AES; Figures 5–7: depth profiles. Prose-only pitting potentials excluded. |
| 78 | None; all ten pages inspected | Tables 1, 3, 4: compositions; Table 2: elongation. Figure 1: polarization; Figures 2–3 and 11: critical pitting temperature; Figures 4/6: stress–strain; Figure 5: impact energy; Figure 7: XRD; Figures 8–10/12: microscopy. Prose-only potentials excluded. |
| 79 | Not inspected: missing PDF | No source classification possible. |
| 80 | Figures 1–4, including fresh/aged pitting and companion repassivation groups (PDF pp. 4–6) | Figures 5–6: pit-growth current versus applied potential and repassivation endpoints; no pitting potential inferred from those curves. |
| 81 | Figures 1–2, NaCl and NaBr at 0 and 25 °C (pp. 2–3) | Table 1: composition. Prose reproducibility estimates are not plotted error bars. |
| 82 | None; all 20 pages inspected | Table 1: composition; Table 2: PREN, critical crevice corrosion temperature, and qualitative pitting occurrence at LiCl concentrations. Figures 1–2: PREN; Figure 3: apparatus; Figures 4–13: continuous polarization curves. No explicit discrete pitting-potential results. |
| 83 | Figures 6–7 (p. 4) and Figure 8 (p. 5): eight legend groups, retaining transpassive/transition potentials as non-target companions | Table 1: composition; Tables 2–3: CPT and applied test potentials. Figures 1–2: schematics; Figures 3–4: polarization; Figures 5/12–13: microscopy; Figure 9: CPT; Figure 10: potentiostatic CPT versus applied potential (markerless Z-envelope not sampled); Figure 11: current-time; Figures 14–15: PRE/PREN versus CPT. |
| 84 | None; all six pages inspected | Figures 1–12 and 17: continuous polarization curves. Figure 13: isocorrosion chart. Figures 14–16: current density at an applied potential, despite potential wording in some captions. Figures 18–20: photographs. Unnumbered composition summary excluded. |
| 85 | Figure 1, two carbon groups (p. 2); Figure 4, four steels (p. 4) | Figure 2: continuous polarization; Figure 3: markerless current-density/corrosion-rate traces, despite an internal pitting potential label; Figure 5: isocorrosion chart. Table 2: composition/microstructure; Tables 1/3/4: mechanical properties. |

All supplied pages were inspected. Missing Paper 79 and the partial series in Papers 74, 80, and 83 remain the material limitations. No pitting potential was inferred from a continuous polarization curve.
