# Extract-series batch: Papers 11–20

Scope: the extract-series skill's default selection of explicit pitting-potential figures and tables. Supporting composition tables were not requested. All 76 pages present in the ten supplied PDFs were visually inspected using Poppler renders; enlarged figure views were used where needed. The PDFs were the sole evidence source. No OCR, automated marker detection, or curve tracing was used.

**Source limitation: Paper 18 is incomplete.** Its PDF contains a ResearchGate cover and only article page C424. Article pages C425–C430 are missing. No eligible source appears on the supplied article page; the empty JSON does not establish that the full article has no eligible results. A complete PDF is needed to finish that paper's article-wide coverage.

## Outputs and validation

All ten JSON files passed the skill's validate_output.py with the project's frozen uv environment. Filenames and reference numbers match the source PDFs. Validation checks structure and internal consistency, not scientific fidelity or article completeness.

| Paper | Output | Complete | Partial | None | Rows |
|---|---|---:|---:|---:|---:|
| 11 | [paper_11.json](paper_11.json) | 1 | 0 | 0 | 12 |
| 12 | [paper_12.json](paper_12.json) | 9 | 2 | 0 | 31 |
| 13 | [paper_13.json](paper_13.json) | 0 | 0 | 0 | 0 |
| 14 | [paper_14.json](paper_14.json) | 1 | 8 | 0 | 86 |
| 15 | [paper_15.json](paper_15.json) | 0 | 0 | 0 | 0 |
| 16 | [paper_16.json](paper_16.json) | 13 | 0 | 0 | 44 |
| 17 | [paper_17.json](paper_17.json) | 2 | 2 | 0 | 51 |
| 18 | [paper_18.json](paper_18.json) — incomplete PDF | 0 | 0 | 0 | 0 |
| 19 | [paper_19.json](paper_19.json) | 1 | 0 | 0 | 4 |
| 20 | [paper_20.json](paper_20.json) | 4 | 0 | 0 | 18 |
| **Total** | **10 files** | **31** | **12** | **0** | **246** |

The 43 series include companion non-target quantities shown with the selected results. Rows are source-specific records, not independent experiments: some figures repeat table data or earlier figures, and a row can contain several measured quantities. Plotted coordinates are visual estimates; fitted/connecting lines did not supply additional points. Printed inequalities and plotted upward limits are retained. Uncertainty meaning is left unspecified unless the source identifies it.

## Items needing attention

- **Paper 12, Table 3:** annealed Mo is associated with intergranular attack. The annealed block is retained as partial with provisional is_target=false because its breakdown column mixes mechanisms. The quenched block is separate.
- **Paper 12, Figure 3:** the Ti marker near 0.2 wt.% overlaps another symbol; the Ti series is partial because coincident points cannot be counted reliably. The upper Mo marker reads about 1.22 V, while Table 3 reports 1.20 V; both source values are retained.
- **Paper 14, Figures 1–2:** the upper plateau is explicitly associated with transpassivity. The four alloy series in each figure are partial with provisional is_target=false, since individual markers are not fully classified. Some overlapping markers/error bars near 25–30°C and 800–830 mV remain omitted. Figure 2 repeats Figure 1's potential-scan data and adds T500 points at a fixed applied 500 mV; those companion points are marked non-target. Numerical point annotations in Figure 1 are preserved where their attachment is clear.
- **Paper 16, Figure 10:** the 28Cr ferrite-content point at 1623 K is about 55%, while the prose states 65%. The plotted value is retained.
- **Paper 16, Figure 11:** the approximately 0.5 V point lies near 13.5 kJ/cm, while the prose discusses about 0.5 V at 12 kJ/cm. The plotted coordinate is retained.
- **Paper 17, Figure 1:** some small error-bar endpoints are obscured by symbols or unresolved in the supplied raster. Both Epit and Ecorr series are partial; central values and clearly distinguishable bounds are retained.
- **Paper 17, Table 3:** the printed average Epit − Ecorr of 260 mV for CoCrFeNi (SPS^) is inconsistent with its printed potentials. It is transcribed without correction.
- **Paper 20, Tables 3 and 5:** HEA in 1 M NaCl has Ecorr/Epit of −0.53/−0.25 V in Table 3 and −0.77/−0.49 V in Table 5. The source values are retained independently.
- **Paper 20, Tables 4 and 5:** chloride-free acid potentials also differ (−0.17/0.09 V versus −0.41/−0.15 V for Ecorr/Eb). The chloride-free Table 5 row is retained separately with is_target=false; the paper explicitly identifies this breakdown as non-pitting.
- **Papers 13 and 15:** no eligible discrete pitting-potential series were found in the complete supplied articles. Their series arrays are empty.
- **Paper 18:** missing article pages prevent article-wide completion. Its empty series array describes only the supplied page and must not be treated as a confirmed negative screen of the full article.

## Source coverage and exclusions

| Paper | Extracted sources | Excluded sources and reason |
|---|---|---|
| 11 | Table IV | Table I: composition. Tables II–III and Figure 7: passivation/current quantities. Figures 1–6 and 8: polarization curves; Figure 4's qualitative arrows do not print numerical pitting potentials. |
| 12 | Figure 3; Table 3, split by heat-treatment block | Table 1: composition. Table 2: pit distribution. Figure 1: corrosion rate. Figures 2, 5–6: photographs. Figure 4: apparatus. Figures 7–8: polarization curves. |
| 13 | None | Table 1: composition and crevice-corrosion temperatures. Figure 1: critical pitting/crevice temperatures. Figure 2: corrosion rates. |
| 14 | Figures 1–2, including Figure 2's T500 companion points | Table 1: composition. Tables 2–3 and Figure 3: critical temperatures/exposure outcomes. Thermodynamic reference lines and connecting curves in Figures 1–2 were not sampled. |
| 15 | None | Table 1: composition. Figure 1: exposure-temperature limits at solution potentials, not measured pitting potentials. Figures 2–6: critical pitting temperatures. |
| 16 | Figures 4, 7, 10–11, 13; Figure 10's ferrite-content companion panel | Tables 1–2: composition. Figures 1–2, 6, 12: process/specimen schematics. Figure 3: toughness. Figure 5: alloy-design region with a potential criterion, not discrete potential measurements. Figures 8–9: crevice-corrosion results. |
| 17 | Figure 1; Tables 1 and 3 | Figures 2 and 4: polarization curves and microscopy. Figures 3, 5–7: diffraction, microscopy and elemental maps. Table 2: mixing enthalpies. Table 4: EDS composition. |
| 18 | None on the supplied page | Table I on C424: composition. Remaining article pages C425–C430 are absent and could not be screened. |
| 19 | Table 5 | Tables 1–2: composition. Table 3: mixing enthalpies. Table 4: corrosion rates. Figures 1, 3–4: microscopy. Figure 2: diffraction. Figure 5: polarization curves. |
| 20 | Tables 3 and 5; Figure 13 | Table 1: composition. Table 2: elemental properties. Table 4: explicitly non-pitting breakdown in chloride-free acid. Figure 1: apparatus. Figures 2–7: microscopy, diffraction, elemental mapping and thermal analysis. Figures 8–12 and 14: polarization curves. Figures 15–16: microscopy. |

Cover pages, adjacent-article fragments, prose-only numerical examples, and bibliographic lists were outside the figure/table extraction scope. No pitting potentials were inferred from polarization curves. Future batches will use this report format, including validation, uncertainties, and source coverage.
