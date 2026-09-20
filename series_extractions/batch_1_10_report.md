# Extract-series batch: Papers 1–10

Scope: the extract-series skill's default selection of explicit pitting-potential figures and tables. Supporting composition tables were not requested. All 65 PDF pages (including delivery/cover pages and adjacent-article fragments) were visually inspected using Poppler renders; enlarged figure views were used where needed. The PDFs were the sole evidence source. No OCR, automated marker detection, or curve tracing was used.

## Outputs and validation

All ten JSON files passed the skill's validate_output.py with the project's frozen uv environment. Filenames and reference numbers match the source PDFs. Validation checks structure and internal consistency, not scientific fidelity.

| Paper | Output | Complete | Partial | None | Rows |
|---|---|---:|---:|---:|---:|
| 1 | [paper_1.json](paper_1.json) | 9 | 0 | 0 | 49 |
| 2 | [paper_2.json](paper_2.json) | 4 | 0 | 0 | 36 |
| 3 | [paper_3.json](paper_3.json) | 11 | 1 | 0 | 194 |
| 4 | [paper_4.json](paper_4.json) | 0 | 5 | 0 | 24 |
| 5 | [paper_5.json](paper_5.json) | 0 | 0 | 0 | 0 |
| 6 | [paper_6.json](paper_6.json) | 10 | 0 | 0 | 81 |
| 7 | [paper_7.json](paper_7.json) | 6 | 0 | 0 | 38 |
| 8 | [paper_8.json](paper_8.json) | 5 | 2 | 0 | 39 |
| 9 | [paper_9.json](paper_9.json) | 17 | 8 | 0 | 134 |
| 10 | [paper_10.json](paper_10.json) | 0 | 0 | 0 | 0 |
| **Total** | **10 files** | **62** | **16** | **0** | **595** |

The 78 series include companion non-target quantities shown with the selected results. Rows are source-specific records, not independent experiments: some figures repeat table data, and a row can contain more than one target value. Plotted coordinates are visual estimates at defensible precision; fitted/connecting lines did not supply additional points.

## Items needing attention

- **Paper 1, Figure 6:** the zero-Mo marker at 0°C lies near 0.80 V; the text states 0.78 V. The plotted coordinate is retained with a note.
- **Paper 3, Figure 22:** dense overlap near 22–24 wt.% (Cr + Mo) prevents a reliable count of any coincident additional markers. Recoverable coordinates and annotations are retained; this series is partial.
- **Paper 3, Figure 7 versus Table 5:** F469B is printed as 265 mV in the figure and 165 mV in the table. Both source values are retained.
- **Paper 4, Figure 4:** all five series report passivation-breakdown potentials without separating crevice from pitting breakdown. Values are retained, but their potential columns have provisional is_target=false and the series are partial.
- **Paper 8, Figure 4:** the UNS N08904/NaCl and UNS S31254/NaBr series combine transpassive and pitting potentials, including transition-temperature markers whose classification is unresolved. These two series are partial with provisional is_target=false. Clearly identified transpassive companion results elsewhere are also marked false.
- **Paper 9, Figure 5:** its legend places NaBr above NaCl, contrary to the ordering stated in the text. The visible legend assignments are preserved and flagged.
- **Paper 9, Figure 9:** the authors used potentials at 10 μA cm⁻² when definite pitting potentials were absent, without identifying the affected markers. All eight series are retained as partial with provisional is_target=false.
- **Papers 5 and 10:** no eligible discrete pitting-potential series were found. Their series arrays are empty; these are inspected, out-of-scope results, not extraction failures.

## Source coverage and exclusions

| Paper | Extracted sources | Excluded sources and reason |
|---|---|---|
| 1 | Table I; Figures 1, 2, 5, 6, 8 | Figures 3, 4, 7: polarization curves. Table II: thermodynamic data. |
| 2 | Tables III, IV; Figure 7 | Table I: composition. Table II and Figures 2–3: passivation/current quantities. Figures 1, 4–6: polarization curves. Table V: exposure/weight loss. Figure 8: photographs. |
| 3 | Tables 4–5; Figures 1–3, 21–22; explicit Ec annotations in Figures 7–10 | Tables 1–3: compositions. Table 6 and Figures 4–5, 18: corrosion rates. Figures 6, 13: apparatus. Figures 11–12, 14–17, 19–20: photographs/micrographs without eligible potential data. Continuous interpolated curves and corrosion-region boundaries were not sampled. |
| 4 | Figure 4, with unresolved target classification | Table 1: composition. Figures 1–2: corrosion-mode maps. Figure 3: polarization curves. Figure 5: microscopy. Figures 6–7: crevice-corrosion exposure maps. |
| 5 | None | Table 1: composition. Tables 2–3 and Figures 1–7: critical crevice temperature, rather than pitting potential. |
| 6 | Tables II–IV; Figures 2, 4 | Table I: composition. Tables V–VI: corrosion rates. Figure 1: polarization curve. Figure 3: micrograph. |
| 7 | Table I potential block; Figures 1, 5–6 | Table I metal-analysis block: composition. Table II: adsorption ratios. Figures 2–3: inhibitor/halide activity relationships. Figure 4: corrosion-potential time trace. Figure 7: pit counts versus inhibitor activity. Figure 5's corrosion-potential comparison is retained as a non-target companion series. |
| 8 | Figures 3–5 | Table 1: composition. Table 2: critical pitting temperature. Figures 1–2, 6: polarization curves. Figures 7–8: micrographs. |
| 9 | Tables 1–2; Figures 2, 4–6, 8–9 | Figure 1: apparatus. Figure 3: polarization curves. Figures 7, 10: current–time traces. |
| 10 | None | Tables I–II: compositions/mechanical properties. Table III: corrosion rates. Figures 1–2: pitting-current density. Figure 3: continuous polarization curves requiring inference of pitting potential. Figures 4–6: photographs. |

Adjacent articles, cover pages, prose-only numerical examples, and bibliographic lists were outside the figure/table extraction scope. No pitting potentials were inferred from continuous polarization curves.
