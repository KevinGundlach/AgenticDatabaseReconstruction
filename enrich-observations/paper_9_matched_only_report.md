# Paper 9 observation enrichment

- PDF: `9_W. M. Carroll, E. E. Lynskey, Corros. Sci. 36 (1994)_ p. 1667.pdf`; resolved reference **9**.
- Input subset: `paper_9_matched_only.json` (registry version 1.1).
- Output: [paper_9_matched_only.json](paper_9_matched_only.json) (enrichment version 1.0); exact input-byte SHA-256 fingerprints are stored in the JSON.
- Counts: **39 supplied; 39 eligible; 39 written; 0 skipped failed; 0 flagged**. Every eligible supplied ID remains in input order with its exact raw pitting-potential object.
- Skipped failed IDs: none.
- Flagged output IDs: none.

## Visual inspection and access

Actual visual overview covered every supplied-PDF page: **1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12** (printed pp. 1667-1678). Every page was rendered with Poppler and actually viewed; none were inaccessible or unviewed and there were no visual-access errors. Detailed visual inspection covered Figure 1b and Experimental method (p. 2), its cathodic pre-hold/scan-rate/reference-electrode/averaging continuation and chemical-pretreatment scope (p. 3), all supplied Figure 9 markers, solid/dashed halide keys, material labels, pH axis and caption, with Table 2 scope checked (p. 8), and Discussion's constituent-wire identities, 80% Ni:20% Cr composition and conditional 10 μA cm^-2 criterion (p. 10). All supplied observations have their sole location in Figure 9.

Only this supplied PDF, its supplied subset and bundled enrichment resources were used. No CRA data, matching/locating reports, parent registry, prior extraction/enrichment outputs or external experimental sources were read. No new observations were discovered, split, merged or renumbered. No OCR, automated table/curve extraction or scientific/unit calculations were performed.

## Qualifications and missing context

- All **39 supplied Figure 9 outcomes** are retained, including the input's gap at obs_104; no missing point or replicate is created. Material, 1.0 M NaCl/NaBr and pH (3, 4, 5, 7 or 9) are specific to each supplied marker. Original digitized potentials remain unchanged.
- The source says presented results average **at least three identical experiments**. Original mean qualifications are retained without inventing replicates or uncertainty. For Fe, Ni and Mo (obs_087-obs_103 and obs_105-obs_116), definite pitting potentials were used where evident and otherwise a **10 μA cm^-2** anodic-current criterion was used. Affected individual markers are not identified; the original conditional qualification is retained without classifying particular points as proxies. This source qualification alone is not an extraction failure.
- The paper reports Ni80Cr20 as **80% Ni:20% Cr**, without a mass/atomic basis, so composition uses `%`. Fe, Ni and Mo wire identities do not establish numerical purity; element amounts remain null. These elemental-metal and Ni-Cr comparison samples use material class `Other`; no commercial alloy recipe or trace analysis is inferred. Microstructure is unreported.
- Solutions were made with reagent-grade chemicals and distilled water, pH-adjusted with H2SO4 or NaOH as required, deaerated with nitrogen for **24 h** and purged during measurements. Salt molarity is preserved; chloride-ion concentration is not calculated from NaCl, and no zero chloride concentration is inferred for NaBr.
- The general protocol holds specimens at **-800 mV (SCE) for 5 min**, then scans at **60 mV min^-1**. The initial cathodic hold is retained in procedure prose rather than as a stepped-test hold. Constituent wires are described as similar in thickness to steel; exact individual dimensions are not inferred from the steel's default geometry. Test temperature is unreported and remains null. The **50 °C/65 °C** acid-bath temperatures and Table 2 chemical pretreatments apply to a separate 316-wire experiment set and are not assigned to these Figure 9 records. No confirmed registry correction or unresolved material/condition association was found.

## Validation

Bundled `validate_output.py` exit code: **0**.

```text
VALID: C:\Archives\School\HHU\HHU Courses\Max Plank\Thesis - Work\AgenticDatabaseReconstruction\enrich-observations\paper_9_matched_only.json
Supplied=39; eligible=39; written=39; skipped_failed=0; flagged=0.
Skipped failed IDs: none
Flagged output IDs: none
Scientific fidelity, retained qualification meanings and actual visual coverage are not certified.
```

Structural validation checks schemas/models, fingerprints, reference consistency, exact eligible-ID coverage/order and raw potential preservation. It does not certify scientific associations, qualification meanings, actual visual inspection or benchmark suitability. Ordinary unreported information is represented by empty/null fields; an unflagged row is not thereby certified benchmark-ready.
