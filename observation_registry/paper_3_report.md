# Paper 3: observation-registry coverage

Input: `3_N. Pessall, J. I. Nurminen, Corrosion 30 (1974)_ p. 381..pdf`. Literature reference: 3. Evidence: supplied PDF only; no database, prior extraction, or locating report was read.

Supplied pages: 12. Visually inspected: PDF pp. 1–12 (printed pp. 381–392), including all 22 figures, six tables, captions, footnotes, and relevant text. Tables 4–5 and Figs. 1–3, 7–10, 21–22 received enlarged review. Full paper survey completed; no page-access limitation. Eligible sources: scan/scratch values in Table 4, ternary/commercial scratch markers in Fig. 1, all numerical scan/scratch/current–time cells in Table 5, experimental and explicitly interpolated Fig. 2 markers, Fig. 3 repeats, printed E_c labels in Figs. 7–10, and discrete pitting markers in Figs. 21–22. Repeated supported presentations are nested in locations.

Registry: [paper_3.json](paper_3.json) (schema 1.1). Actual saved observations: **171**. Complete: **171**; partial: **0**; failed: **0**.

- Partial IDs: none
- Failed IDs: none

## Source qualifications and consolidation

Scan, scratch, and current–time results remain separate; repeated F464B runs 1134 and 1123 remain separate. Table 4 printed scan ranges are single condition-specific range observations. Table 5 current–time entries preserve strict “<” upper bounds. Fig. 2 base scan markers are classified **interpolated**; its experimental markers use Table 5 as primary. Specimen-photo E_c labels report the earlier seawater scratch potentials, not thresholds in the photographed crevice-exposure environment. F469B conflicts: Table 5 scratch **165 mV**, Fig. 7 **265 mV**; both are retained, table primary. The unnamed additional markers in Figs. 21–22 are enumerated by their plotted coordinates and visible selectors; uncertain relationships to earlier data or one another are documented, without treating them as independent experiments. E-Brite values with unestablished specimen/run correspondence remain separate. Scientific source uncertainty does not constitute a recovery failure. Graphical precision is typically 5–10 mV and approximately 0.1–0.5 wt% for unlabelled horizontal coordinates.

## Exclusions

The p. 381 screening range **100–500 mV vs SCE** spans unspecified selected alloys and is excluded as a broad screening statement. Tables 1–3 are compositions; Table 6, Figs. 4–5 and 18, and the exposure coupon labels give corrosion rates/weight losses rather than pitting potentials. Figs. 6, 11–17, 19–20 depict apparatus, qualitative attack, or microstructures without new numerical pitting outcomes. Qualitative edge pitting/no-crevice-attack statements on p. 385 and elsewhere have no threshold and are excluded. Broken comparison curves, fitted/connecting lines, and crevice-classification contours do not create extra observations. Only marked points are registered; no sampling of the continuous interpolated curves is performed.

## Validation

Bundled validator exit code: **0**. Structural/internal-consistency validation passed. It does not certify scientific interpretation, consolidation, or coverage.

```text
VALID: C:\Archives\School\HHU\HHU Courses\Max Plank\Thesis - Work\AgenticDatabaseReconstruction\observation_registry\paper_3.json (171 observations).
Extraction status: complete=171; partial=0; failed=0
Partial observation IDs: none
Failed observation IDs: none
Default routing: complete and partial continue; failed require review.
Scientific fidelity, consolidation, coverage, and benchmark suitability not checked.
```
