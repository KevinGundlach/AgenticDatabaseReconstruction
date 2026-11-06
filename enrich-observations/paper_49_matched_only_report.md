# Paper 49 observation enrichment

- PDF: `49_Malik, A. U., et al. Corrosion science 37.10 (1995)_ 1521-1535.pdf`; reference **49**.
- Registry: `paper_49_matched_only.json` (version 1.1; supplied subset only).
- Enrichment: [paper_49_matched_only.json](paper_49_matched_only.json) (version 1.0). Input-byte SHA-256 fingerprints are stored in the JSON.
- Counts: **74 supplied; 74 eligible; 74 written; 0 skipped failed; 14 flagged**. The input contains 74 complete and 0 partial observations. The 65 Table 5 and 9 Figure 5 entries retain their supplied order, noncontiguous IDs, and exact raw anchored potentials.
- Skipped failed IDs: none.
- Flagged output IDs: obs_071, obs_072, obs_073, obs_074, obs_075, obs_076, obs_080, obs_084, obs_088, obs_092, obs_096, obs_100, obs_108, obs_112.

## Inspection and scope

Visual overview completed for every supplied-PDF page: **1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15** (printed pages 1521-1535). No pages were inaccessible or unviewed; there were no visual-access errors. Poppler-rendered page images were actually viewed. Detailed visual inspection covered Materials, electrochemical specimen geometry and Table 1 (p. 3, including enlarged Others and UNS columns); Table 2 and the scope of accelerated-test preparation/cell statements (p. 4); the continuation of accelerated methods and distinction from polarization measurements (p. 5); the pitting definition and result discussion (p. 6); all supplied Table 5 anchors, row and column labels (p. 7); Figure 2 curves, annotations and caption (p. 8); Discussion's alloy-type statements (p. 11); and Figure 5/6 axes, symbols, labels, captions and associated discussion (p. 12). Every primary and secondary location in the supplied subset was covered by these detailed views.

Only the supplied paper, supplied subset and bundled skill resources were used. No matching results, CRA data, parent registry, previous extraction/enrichment output or external cited experimental source was read. The paper's setup reference 37 was not followed. No OCR, automated table/curve extraction, chemistry calculation or unit normalization was performed. Read-only rendering and registry bookkeeping were used.

## Qualifications and unresolved context

- Table 1 gives no composition basis/unit, so numerical composition units remain blank. Explicit Fe balances are retained; dashes are not zero. Named but unquantified trace elements remain null. The combined `5Cb + Ta` for 20 Cb3 and `0.6 (Cb + Ta)` for Duplex 2205 are preserved in notes without disaggregation or correction; Cb is represented as Nb. The unlabeled `0.15` in the Duplex row cannot be assigned to an element, affecting obs_071-obs_075 and obs_108 and accounting for six composition-recovery flags.
- The nine Figure 5 entries (obs_076, obs_080, obs_084, obs_088, obs_092, obs_096, obs_100, obs_108, obs_112) retain the printed Log Cl (ppm) = 2.5 coordinate in prose. Their concentration cannot be uniquely associated with the table's chloride conditions; `chloride_concentration` remains null and the association is flagged. No inverse-log calculation or ordinal table matching was applied. Their original approximate-reading and possible-duplicate qualifications remain intact; they are not asserted to be independent experiments.
- Original Table 5/Figure 2 conflicts for obs_030 (1516 versus 94 mV) and obs_075 (629 versus 826 mV), and Figure 6 potential/PREN/label disagreements for obs_030, obs_035 and obs_065, remain in result notes. The Monit 44635/44653 spelling difference is disclosed; Table 1/Table 5 identify the composition. Table 1's hMo 3127 UNS entry is preserved as printed, `N0828`. These are paper-source qualifications, not permission to change a potential. No confirmed anchor correction was made.
- All selected pitting measurements are contextualized at 50 °C. The aqueous NaCl solutions were made in distilled water and adjusted with NaOH to pH 7.8; reported chloride concentrations remain in ppm. Natural Gulf seawater uses Table 2's pH 8.2, ion concentrations in mg l^-1, and explicitly reported chloride **24090 mg l^-1**. Its solvent is not separately specified in the paper and is left blank. No typical seawater recipe is substituted.
- Commercial sheet/rod supply and no further heat treatment apply generally. The pitting-specific surface finish, scan rate, scan limits and stabilization time are not specified here. The 600-grit finish, 30 min air exposure, 17% HNO3 passivation, nitrogen deaeration, acidic simulated-crevice solutions and -600 to +100 mV / 10 mV s^-1 schedule occur under Accelerated tests and are not assigned to these pitting records. The globally worded corrosion-cell statement supplies SCE/KCl-bridge and graphite-counter context, with its wording identified in each procedure. Ordinary unreported context uses empty/null fields rather than failure flags.

## Validation

Bundled `validate_output.py` exit code: **0**.

```text
VALID: C:\Archives\School\HHU\HHU Courses\Max Plank\Thesis - Work\AgenticDatabaseReconstruction\enrich-observations\paper_49_matched_only.json
Supplied=74; eligible=74; written=74; skipped_failed=0; flagged=14.
Skipped failed IDs: none
Flagged output IDs: obs_071, obs_072, obs_073, obs_074, obs_075, obs_076, obs_080, obs_084, obs_088, obs_092, obs_096, obs_100, obs_108, obs_112
Scientific fidelity, retained qualification meanings and actual visual coverage are not certified.
```

Validation checks structure, exact input fingerprints, eligible-ID coverage/order and unchanged raw anchored potentials. It does not certify scientific associations, qualification meanings, visual inspection or benchmark suitability; unflagged records are not thereby certified benchmark-ready.
