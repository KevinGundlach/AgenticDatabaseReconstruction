# Paper 3 observation enrichment

- PDF: `3_N. Pessall, J. I. Nurminen, Corrosion 30 (1974)_ p. 381..pdf`; resolved reference **3**.
- Input subset: `paper_3_matched_only.json` (registry version 1.1).
- Output: [paper_3_matched_only.json](paper_3_matched_only.json) (enrichment version 1.0); exact input-byte SHA-256 fingerprints are stored in the JSON.
- Counts: **56 supplied; 56 eligible; 56 written; 0 skipped failed; 0 flagged**. Every eligible supplied ID remains in input order with its exact raw pitting-potential object.
- Skipped failed IDs: none.
- Flagged output IDs: none.

## Visual inspection and access

Actual visual overview covered every supplied-PDF page: **1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12** (printed pp. 381-392). All pages were rendered with Poppler and actually viewed; none were inaccessible or unviewed. Detailed visual inspection covered Materials and 50 gm melting/preparation (pp. 1-2), all relevant Table 3 compositions and headers (p. 2), polarization-solution conditioning, scan/scratch/current-time distinctions, Table 4 footnote scope and every supplied Table 5 anchor (p. 3), Figure 2 legend/group annotations and B-series final heat treatment (p. 4), and all registered Figure 7/8 specimen labels and captions (p. 5). Thus all supplied primary and secondary locations were inspected. An optional system MiKTeX text-layer locator returned access-denied cache warnings but produced searchable text; the bundled Poppler installation had no pdftotext executable. These text-locator issues did not affect visual rendering or inspection.

Only this supplied PDF, its supplied subset and bundled enrichment resources were used. No CRA data, matching/locating reports, parent registry, prior extraction/enrichment outputs or external experimental sources were read. No new observations were discovered, split, merged or renumbered. No OCR, automated table/curve extraction or scientific/unit calculations were performed.

## Qualifications and missing context

- The 56 records contain **28 scan and 28 scratch results**, including separate Table 5 runs of F464B. Scan rate 10 mV/min applies to scan results; scratch rates/steps/holds remain null. The source's qualifications about method dependence and preference for scratch comparisons are retained without merging methods or runs.
- Nominal Table 3 compositions are copied in **Wt %**, including explicit numerical Fe. Figure 2's rounded group labels and atomic-percent substitution descriptions do not replace them. The F474B middle-marker qualification (0.51 Nb + 0.13 Mn instead of the group header) remains explicit for obs_097 and obs_098.
- The **34 B-series** records use the stated final treatment of 1 hour at 1049 °C (1920 °F), water quench. The **22 A-series** records retain their identities and common 50 gm preparation, but their final annealing schedule is not supplied and is not inferred. Specimen-specific microstructures from the separate W-series metallography are not transferred to these F-series samples. Table 4's pickling footnote is scoped to its plant-exposure specimens and is not assigned to Table 5 F-series records.
- All selected pitting tests use **deaerated synthetic seawater at 90 °C, pH 7.2 ± 0.2**. Sulfuric-acid neutralization followed by boiling is retained in reported order. No seawater recipe, solvent specification or chloride-ion concentration is invented. Earlier referenced cell/scratch details are not retrieved.
- The original **obs_085** conflict remains: Table 5 reports F469B scratch potential 165 mV, while the Figure 7 label reports 265 mV. This is a paper-source disagreement; the primary anchor is unchanged. Figure 7/8 labels occur beneath ferric-chloride crevice exposures at 21 ± 1 °C, but those exposure conditions are not substituted for the Table 5 pitting-test context. No confirmed registry correction was made.

## Validation

Bundled `validate_output.py` exit code: **0**.

```text
VALID: C:\Archives\School\HHU\HHU Courses\Max Plank\Thesis - Work\AgenticDatabaseReconstruction\enrich-observations\paper_3_matched_only.json
Supplied=56; eligible=56; written=56; skipped_failed=0; flagged=0.
Skipped failed IDs: none
Flagged output IDs: none
Scientific fidelity, retained qualification meanings and actual visual coverage are not certified.
```

Structural validation checks schemas/models, fingerprints, reference consistency, exact eligible-ID coverage/order and raw potential preservation. It does not certify scientific associations, qualification meanings, actual visual inspection or benchmark suitability. Ordinary unreported information is represented by empty/null fields; an unflagged row is not thereby certified benchmark-ready.
