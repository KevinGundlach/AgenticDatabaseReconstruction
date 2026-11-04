# Paper 49: observation-registry coverage

Input: `49_Malik, A. U., et al. Corrosion science 37.10 (1995)_ 1521-1535.pdf`. Literature reference: 49. Evidence: supplied PDF only; no database, prior extraction, or locating report was read.

Supplied pages: 15. Visually inspected: PDF pp. 1–15 (printed pp. 1521–1535), including all tables, figures, captions, footnotes, and text. Table 5 and Figs. 2, 5, 6 were rechecked at higher resolution. Full paper survey completed; no page-access limitation. Eligible coverage: all 75 E_pit cells in Table 5, five explicit Fig. 2 annotations, 40 discrete Fig. 5 markers, and 14 Fig. 6 markers. Supported same-alloy seawater presentations are nested under their Table 5 observations.

Registry: [paper_49.json](paper_49.json) (schema 1.1). Actual saved observations: **115**. Complete: **115**; partial: **0**; failed: **0**.

- Partial IDs: none
- Failed IDs: none

## Source qualifications and consolidation

Table 5 is primary for its observations. Its 17-4PH seawater cell is visibly **1516 mV** and is preserved literally. Fig. 2 labels Duplex 2205 at **826 mV**, versus **629 mV** in the table; its 17-4 pH curve is annotated **94 mV**, versus **1516 mV** in the table. Fig. 6 also conflicts for 17-4PH and appears to exchange the SMO 254/Monit potential–PREN associations; the printed readings are retained without repair. Monit is labeled 44653 in Fig. 6. The 40 Fig. 5 records form uncertain duplicate groups with each alloy’s four aqueous Table 5 results because the plotted log-concentration coordinates differ from the table columns. They are not claimed as 40 additional independent experiments. Figure values are approximate graphical readings, generally to 10 mV. All registered primary potentials have reported experimental origin.

## Exclusions

Tables 1–3 describe compositions/solutions; Table 4 gives general corrosion rates; Tables 6–8 give crevice-exposure attack, depth, timing, and indices, not pitting potentials. Figs. 1, 3, 4, 7 concern polarization resistance or critical crevice solution/pH. Continuous portions of Fig. 2 and all fitted/connecting lines were not converted into thresholds or extra points. Qualitative rankings, PREN equations, general corrosion rates, and crevice-corrosion conclusions are outside this registry. No broad numerical pitting screening range required separate registration.

## Validation

Bundled validator exit code: **0**. Structural/internal-consistency validation passed. It does not certify scientific interpretation, consolidation, or coverage.

```text
VALID: C:\Archives\School\HHU\HHU Courses\Max Plank\Thesis - Work\AgenticDatabaseReconstruction\observation_registry\paper_49.json (115 observations).
Extraction status: complete=115; partial=0; failed=0
Partial observation IDs: none
Failed observation IDs: none
Default routing: complete and partial continue; failed require review.
Scientific fidelity, consolidation, coverage, and benchmark suitability not checked.
```
