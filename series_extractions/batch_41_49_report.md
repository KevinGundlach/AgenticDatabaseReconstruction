# Extract-series batch: Papers 41–49

## Scope

Requested papers: 41, 42, 43, 44, 45, 46, 47, 48, and 49. Paper 42 is absent from the papers folder; no extraction JSON was created for that unseen reference. Paper 50 is outside this request and is known to be absent. Eight PDFs were supplied, totaling 269 pages. Selection follows the skill default: explicit pitting-potential figures/tables and companion quantities within selected sources. Supporting composition tables were not requested.

167 pages were visually inspected using Poppler renders and enlarged views. All supplied pages were inspected for Papers 41, 43, and 45–49. Paper 44, a 191-page dissertation, received selective visual review of 89 pages: PDF pages 1, 7–21, 60–70, 79–90, 93–108, 126–141, and 161–178. Its figure/table inventories, corresponding source pages, and supporting discussion were reviewed; the remaining 102 pages were not individually inspected. This is not a claim of full-page coverage for Paper 44. No missing main-article pages were identified in the supplied files. A neighboring article fragment at the end of Paper 46 was excluded.

The PDFs were the sole evidence source. No OCR, automated marker detection, or curve tracing was used. Prose-only numbers and values that would require inference from polarization curves were excluded.

## Outputs and validation

All eight saved JSON files passed validate_output.py in the project’s frozen uv environment. Counts below are derived from the saved JSON. Structural validation checks format and internal consistency; it does not certify scientific fidelity or resolve incomplete sources.

| Paper | Pages supplied / inspected | Output | Validation | Complete | Partial | None | Rows |
|---|---:|---|---|---:|---:|---:|---:|
| 41 | 9 / 9 | [paper_41.json](paper_41.json) | Passed | 7 | 0 | 0 | 39 |
| 42 | Not supplied / 0 | Missing PDF; no output | Not run | — | — | — | — |
| 43 | 18 / 18 | [paper_43.json](paper_43.json) | Passed | 0 | 0 | 0 | 0 |
| 44 | 191 / 89 | [paper_44.json](paper_44.json) | Passed | 0 | 12 | 0 | 95 |
| 45 | 15 / 15 | [paper_45.json](paper_45.json) | Passed | 0 | 0 | 0 | 0 |
| 46 | 5 / 5 | [paper_46.json](paper_46.json) | Passed | 2 | 0 | 0 | 10 |
| 47 | 6 / 6 | [paper_47.json](paper_47.json) | Passed | 2 | 0 | 0 | 13 |
| 48 | 10 / 10 | [paper_48.json](paper_48.json) | Passed | 2 | 0 | 0 | 14 |
| 49 | 15 / 15 | [paper_49.json](paper_49.json) | Passed | 10 | 2 | 1 | 130 |
| **Total supplied** | **269 / 167** | **8 files** | **All passed** | **23** | **14** | **1** | **301** |

The 38 series include companion non-target quantities. Rows are source-specific records, not independent experiments; figures and tables can repeat results. Rows with unresolved cells still count as rows. Digitized coordinates and interval endpoints are visual estimates. Connecting/fitted lines were not sampled.

## Items needing attention

- **Paper 42:** Missing PDF; extraction and validation could not be run. This differs from an inspected paper with no eligible sources.
- **Paper 44, Figure 3.9(a–d):** All 12 groups are partial. Overlapping markers, especially near PREN 49 and the 600 mV ceiling, prevent exact recovery of all coordinates and counts. Section 3.3.4 explicitly assigns 600 mV when no distinct pitting occurs before transpassivity; these assigned values are retained separately as non-target companions. Each panel’s negative-potential point may belong to an alloy described as lacking a passive region, but its plotted identity is not explicit; those four groups have provisional false target flags. Below-ceiling points identified as pitting potentials retain true target flags. Page coverage is selective as detailed above.
- **Paper 49, Figure 5:** The 904L point at Log Cl = 3.0 and the 2205 point at Log Cl = 2.5 overlap other symbols; their ordinates are null and the corresponding series are partial. The 654 inverted-triangle group is identified in the legend but distinct markers cannot be resolved in an enlarged rendering; it has status none and no inferred rows. The plotted x coordinates (approximately 2.5, 3.0, 3.5, 4.0) do not match the logarithms of all Table 5 concentration headings. Source-specific coordinates are retained.
- **Paper 49, Table 5 and Figures 2/6:** Source disagreements are preserved. Table 5 prints 1516 mV for 17-4PH in seawater, Figure 6 plots approximately 160 mV, and Figure 2 labels 17-4 pH at 94 mV. Figure 2 labels Duplex 2205 at 826 mV while Table 5 lists 629 mV. Figure 6 labels an alloy 44653, whereas Table 5 calls it Monit 44635; the figure’s labels and coordinates are not silently reassigned. SMO 254 and some other coordinates also differ between sources. Complete status means the visible entries in that source were captured, not that these disagreements were resolved.
- **Paper 41:** Figure 12/15 standard-procedure bars without distinct central markers are represented by endpoints only. Where the source identifies the interval as total scatter, the column uses minmax; no arithmetic midpoint was invented. The low-potential current-excursion points are non-target companions. Figure estimates and printed Table 2 values are retained independently.
- **Paper 48, Figure 2:** Visible error-bar endpoints are retained; the paper does not establish an unambiguous statistical category for these intervals, so their interpretation remains unspecified.
- **Papers 43 and 45:** All supplied pages were inspected but no eligible discrete pitting-potential source was found. Their JSON files contain empty series arrays. Numerical pitting potentials appearing only in prose were excluded.
- **Papers 46 and 47:** No unresolved extraction issues were identified in the selected sources. Paper 46’s >0.900 value is preserved as a qualified string.

## Source coverage and exclusions

| Paper | Extracted sources | Excluded sources and reason |
|---|---|---|
| 41 | Figure 3 (PDF p. 3); Figure 12, three groups (p. 6); Table 2 (p. 7); Figure 15, two groups (p. 8) | Table 1: composition. Figures 1–2: polarization schematic and specimen mount. Figures 4–5, 9–10, 13: polarization curves. Figures 6, 16: open-circuit potential. Figures 7–8: critical passivation current/potential. Figure 11: microscopy. Figure 14: chromium fractions. |
| 42 | Not inspected; PDF missing | No source-level conclusions possible. |
| 43 | None | Table 1: composition. Figures 1–6, 8, 12, 15–16: microscopy. Figures 7 and 13: polarization/current-time traces, with no directly transcribable numerical pitting-potential annotations. Figures 9–11: surface profiles. Figure 14: composition. First/second breakdown discussion and prose values were not converted into figure points. |
| 44 | Figure 3.9(a–d), three groups per panel (PDF p. 101; thesis p. 80) | Figure 3.11: continuous ternary contour surface; composition markers do not provide discrete measured Ep values. Tables 3.2–3.5: regression equations, including pitting/repassivation fits, not measured result rows. Other tables: composition/XPS. Figures 2.1–2.10: schematics, Pourbaix/polarization/current-transient or crevice-event plots. Figures 3.1/3.10: composition ternaries; 3.2/3.3/3.5/3.7: polarization; 3.4/3.6/3.8: microscopy. Figures 4.1–4.15: polarization and metastable-current/count/time/radius/rate distributions. Figures 5.1–5.16: polarization, galvanostatic potential-time/repassivation components and XPS spectra/intensities. |
| 45 | None | Table 1: composition. Table 2: corrosion products, mass/charge and applied test potentials. Figures 1, 3–6, 11: polarization/schematic. Figures 2, 7–10: current-time. Figures 12–15: corrosion/redox potential-time. Figure 16: nitrogen ratio versus applied potential. Figures 17–19: AES profiles. Numerical Ep values appear only in prose. |
| 46 | Table II (PDF p. 2); Table III (p. 3) | Table I: composition. Table IV: weight loss/applied potentials. Figures 1, 3–4, 7: polarization/schematic. Figures 2, 5: photographs. Figure 6: corrosion-potential/time. Neighboring technical note excluded. |
| 47 | Figure 2 (PDF p. 3); Figure 5 (p. 5) | Table I: composition. Figure 1: polarization intersections requiring inference. Figure 3: austenite fraction. Figure 4: microscopy. The selected ordinate is explicitly defined as offset pitting potential. |
| 48 | Figure 2, ferritic and austenitic groups (PDF p. 3) | Table 1: composition. Figures 1, 3–4, 6, 14: pitting/crevice/general corrosion rate or weight loss. Figure 5: corrosion-potential/time. Figures 7–12: polarization/schematic curves. Figure 13: crevice repassivation potential, not pitting potential. |
| 49 | Table 5 (PDF p. 7); Figure 2 printed annotations (p. 8); Figure 5, ten legend groups, including one none (p. 12); Figure 6 (p. 12) | Tables 1–3: alloy/seawater/test-solution composition. Table 4: corrosion rates. Tables 6–8: crevice exposure outcomes. Figure 1: polarization resistance. Figure 2 continuous traces not digitized; only explicit numerical annotations transcribed. Figures 3–4, 7: active-peak heights and critical-crevice-solution pH/ranking/PREN, not pitting potential. |

Full-page coverage for seven supplied papers and inventory-led review of Paper 44 do not resolve the partial/none sources above. No pitting potentials were inferred from polarization curves.
