# Extract-series batch: Papers 21–29

## Scope

Requested papers: 21, 22, 23, 24, 25, 26, 27, 28, and 29. Paper 30 was intentionally not requested because that reference number is absent. The selection follows the skill default: explicit pitting-potential figures/tables, including companion quantities within selected sources. Supporting composition tables were not requested.

All 79 supplied PDF pages were visually inspected using Poppler renders, with enlarged views for small tables and plotted markers. The PDFs were the sole evidence source. No OCR, automated marker detection, or curve tracing was used. No missing main-article pages were identified. Paper 29 includes 11 article pages and one publisher advertisement. Paper 28 references supplementary figures that are not embedded in its supplied PDF; those external materials were not inspected.

## Outputs and validation

All nine JSON files passed the skill’s validate_output.py in the project’s frozen uv environment. Counts below were computed from the saved JSON. Validation checks structure and internal consistency; it does not certify scientific fidelity or article-wide completeness.

| Paper | Pages supplied / inspected | Output | Validation | Complete | Partial | None | Rows |
|---|---:|---|---|---:|---:|---:|---:|
| 21 | 6 / 6 | [paper_21.json](paper_21.json) | Passed | 1 | 0 | 0 | 6 |
| 22 | 7 / 7 | [paper_22.json](paper_22.json) | Passed | 1 | 0 | 0 | 7 |
| 23 | 9 / 9 | [paper_23.json](paper_23.json) | Passed | 6 | 0 | 0 | 20 |
| 24 | 11 / 11 | [paper_24.json](paper_24.json) | Passed | 2 | 0 | 0 | 4 |
| 25 | 6 / 6 | [paper_25.json](paper_25.json) | Passed | 0 | 0 | 0 | 0 |
| 26 | 8 / 8 | [paper_26.json](paper_26.json) | Passed | 3 | 3 | 0 | 8 |
| 27 | 8 / 8 | [paper_27.json](paper_27.json) | Passed | 2 | 0 | 0 | 10 |
| 28 | 12 / 12 | [paper_28.json](paper_28.json) | Passed | 1 | 5 | 1 | 16 |
| 29 | 12 / 12 | [paper_29.json](paper_29.json) | Passed | 2 | 0 | 0 | 4 |
| **Total** | **79 / 79** | **9 files** | **All passed** | **18** | **8** | **1** | **75** |

The 27 series include companion non-target quantities. Rows are source-specific records, not independent experiments; figures can repeat tabulated results. Digitized coordinates are visual estimates. Connecting lines, fitted curves, and shaded region boundaries were not sampled. Table 3 in Paper 28 explicitly reports standard deviations, which are preserved.

## Items needing attention

- **Paper 21:** Poppler emitted malformed-dictionary warnings, but all six article pages rendered and were inspected. Figure 4 was readable.
- **Paper 23, Figure 10:** C-0 bars are explicitly associated with oxygen evolution in Section 3.4 despite the Epit axis label. They are retained as non-target companions. The chloride-free bars are also separated as non-target transpassive results. Chloride-containing C-0.25, C-0.50, C-1.00, and 304SS bars retain the paper’s pitting-potential designation.
- **Paper 24, Table 6:** Mo-free Eb is a pitting-potential target. The Mo-containing alloys are explicitly reported to be free from pitting in the tested NaCl solution, so their Eb values are preserved as non-target breakdown potentials. Repassivation and protection potentials are not targets.
- **Paper 25:** The complete supplied article contains no eligible discrete pitting-potential figure or table. Figure 5 is a polarization curve with qualitative Epit arrows; the numerical Epit quoted in prose is outside this figure/table extraction scope. Its JSON has an empty series array.
- **Paper 26, Table 3:** The 0.10 M NaCl rows have high Epit values near the transpassive region without an unambiguous event classification. Both are partial with provisional is_target=false. The Al-free 0.25–0.50 M NaCl series is also partial: Section 3.4 describes pits and calls the values pitting potentials, while Section 3.2 and the conclusions say the Al-free alloy is not susceptible to localized corrosion. The Al0.3 0.25–0.50 M rows are confirmed targets. Chloride-free rows are non-target companions. The printed –ᵃ entries are preserved; footnote a says the passive region was small enough to neglect.
- **Paper 28, Figure 11:** Hatching and overlapping symbols prevent full digitization. Five legend groups are partial, and stainless steels is none because no red-circle coordinates could be separated reliably from the red outline and arrow. Only distinguishable markers are included; the total marker count remains unresolved. Approximate HEA plot coordinates do not fully match Table 3, and no values were copied from the table to fill the chart. The table itself is complete.
- **Paper 29, Table 2:** A35 and SS316 breakdown values are pitting targets. A36 and C-276 values are separated as non-target companions because the paper reports general corrosion without pit formation for those alloys.
- **Papers 22 and 27:** No unresolved transcription issues were identified in the selected tables.

## Source coverage and exclusions

| Paper | Extracted sources | Excluded sources and reason |
|---|---|---|
| 21 | Figure 4 | Table 1: composition. Table 2: passivation treatments. Table 3: binding energies. Figures 1, 6–7: polarization curves. Figures 2–3: critical pitting temperatures. Figure 5: concentrations for inhibition, not pitting potentials. |
| 22 | Table 4 | Tables 1–3: compositions, mixing enthalpies, and segregation ratios. Figure 1: hardness. Figure 2: diffraction. Figures 3–4 and 6: microscopy/elemental maps. Figure 5: polarization curves. |
| 23 | Figure 10, all five alloy groups, with non-target companions separated | Tables 1 and 6: composition. Tables 2–5: passivation/corrosion, Tafel, Arrhenius, and impedance parameters. Figures 1, 3, 9: polarization curves. Figure 2: corrosion rates. Figures 4–8: Arrhenius, impedance, circuits, and oxide-layer properties. Figures 11–13: microscopy/EDS. |
| 24 | Table 6, split by confirmed pitting versus non-pitting breakdown | Tables 1–2 and 7: composition. Table 3: mixing enthalpy. Tables 4–5: acid/alkaline passivation and breakdown without explicit pitting targets. Figure 1: diffraction. Figures 2 and 6–8: microscopy. Figures 3–5: polarization curves; printed annotations are secondary passivation, repassivation, or protection potentials, not pitting targets. |
| 25 | None | Figures 1–2: diffraction/thermal analysis. Figure 3: microscopy. Figure 4: thermal analysis. Figure 5: continuous polarization curves without printed numerical Epit annotations. Figure 6: corrosion mass percentage/rate. No tables. |
| 26 | Table 3, split by alloy and solution/event classification | Table 1: composition. Table 2: corrosion/passivation quantities, no explicit Epit. Table 4: impedance model parameters. Figures 1, 3–5: polarization curves. Figure 2: diffraction. Figures 6–8: impedance and equivalent circuits. Figures 9–10: microscopy. |
| 27 | Tables 1–2 | Tables 3–5: EDS/XPS composition. Figures 1 and 3: polarization curves. Figures 2 and 4: microscopy. Figures 5–6: XPS spectra. |
| 28 | Table 3; Figure 11 (five partial groups and one none group) | Table 1: composition. Table 2: work functions. Figure 1: diffraction. Figures 2–5 and 8: microscopy, phase maps, and composition profiles. Figure 6: contact-potential maps/profiles. Figure 7: polarization curves. Figure 9: phase fractions. Figure 10: work functions. Figure 11 region outlines and hatching are not discrete data. Supplementary figures referenced in the article are not supplied. |
| 29 | Table 2, split by pitting versus non-pitting breakdown | Table 1: composition, grain size, and entropy. Table 3: impedance model parameters. Figure 1: phase fractions. Figure 2: specimen schematic. Figures 3–5: microscopy. Figures 6–7: polarization curves. Figures 8–9: impedance and equivalent circuits. Final PDF page: publisher advertisement. |

Prose-only numerical examples, bibliographic lists, and publisher material were outside the figure/table selection. No pitting potentials were inferred from polarization curves.
