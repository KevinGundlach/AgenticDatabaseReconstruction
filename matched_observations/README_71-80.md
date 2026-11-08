# Observation-to-CRA matching: papers 71–80

Inputs: `papers/`, `citrine_database/by_reference/`, `observation_registry/`. Outputs: this folder. Applied `match-observations-cra-database` to the supplied registries without modifying them or inventing observations.

Completed 8 valid input sets: 204 supplied observations and 126 CRA records. Observation statuses: 73 matched, 38 ambiguous, 93 unmatched, 0 not_assessed.
96 distinct CRA rows have supported links; 30 remain unlinked. Counts are summed within these separate paper-specific inputs; ambiguous candidates are excluded from supported joins.

| Paper | Observations | Matched | Ambiguous | Unmatched | Not assessed | CRA rows linked / total | Output |
|---|---:|---:|---:|---:|---:|---:|---|
| 71 | 38 | 19 | 0 | 19 | 0 | 38 / 38 | [JSON](paper_71.json), [report](paper_71_report.md) |
| 72 | — | — | — | — | — | — | [Input-failure diagnostic](paper_72_report.md) |
| 73 | 5 | 5 | 0 | 0 | 0 | 9 / 17 | [JSON](paper_73.json), [report](paper_73_report.md) |
| 74 | 28 | 6 | 4 | 18 | 0 | 6 / 8 | [JSON](paper_74.json), [report](paper_74_report.md) |
| 75 | 16 | 13 | 1 | 2 | 0 | 13 / 13 | [JSON](paper_75.json), [report](paper_75_report.md) |
| 76 | 35 | 10 | 0 | 25 | 0 | 10 / 10 | [JSON](paper_76.json), [report](paper_76_report.md) |
| 77 | 0 | 0 | 0 | 0 | 0 | 0 / 4 | [JSON](paper_77.json), [report](paper_77_report.md) |
| 78 | 13 | 3 | 0 | 10 | 0 | 3 / 3 | [JSON](paper_78.json), [report](paper_78_report.md) |
| 79 | — | — | — | — | — | — | [Input-failure diagnostic](paper_79_report.md) |
| 80 | 69 | 17 | 33 | 19 | 0 | 17 / 33 | [JSON](paper_80.json), [report](paper_80_report.md) |

- Paper 72: supplied PDF and registry exist; `citrine_database/by_reference/pitting_potential_72.csv` is missing. Preparation helper returned 2. Diagnostic only; no alignment JSON.
- Paper 79: no matching supplied PDF, CRA CSV or observation registry. Input resolution failed before helper invocation. Diagnostic only; no alignment JSON.
- Paper 77: valid empty registry. Its empty alignment retains all four CRA IDs as unlinked; this says nothing about paper-wide absence of outcomes.
- Paper 71: two CRA copies of the nineteen plain-specimen results are supported; the nineteen crevice results are distinct and unmatched.
- Paper 74: close repeated measurements leave two CRA rows candidate-only. Figure 3/4 source discrepancies and separate Figure 5 results are preserved.
- Paper 75: repeated concentration/pH-series markers remain distinct; one additional .5 M marker has only a candidate link.
- Paper 76: conditional NHE-to-SCE conversion and conflicting primary/secondary readings are documented. Induction-time bounds are separate from scan thresholds.
- Paper 78: text/curve-order conflict is preserved. CPT imposed-potential bounds are separate from polarization pitting potentials.
- Paper 80: composition, potential-sign, protocol and fresh/aged ambiguities remain explicit. Candidates are not accepted assignments; growth-curve presentations are not asserted to be duplicate runs.

Each valid saved JSON passed the bundled validator (exit 0), followed by a separate successful `--report-stdout` invocation. Each companion report is that stdout exactly, with one row per supplied observation. Checks cover schema, IDs/order, original cells, location indices, fingerprints and unlinked complements; structural validation does not certify scientific correctness. Registered anchors and necessary context were visually inspected, with one-based viewed pages recorded in each alignment. Font-substitution diagnostics for papers 71/78/80 are disclosed; inspected content remained legible.

External sources were used only for conversion constants: [Corrtest SCE potential at 25°C](https://www.corrtestinstruments.com/en/02437.html) and [CIAAW atomic weights](https://ciaaw.org/abridged-atomic-weights.htm). All experimental association evidence comes from the current supplied PDF, registry and CSV.

Inputs and pre-existing outputs were preserved. Default joins must use `matches` and account for shared CRA IDs; do not join candidates or treat duplicate database rows as independent experiments. This batch is not automatically merged with other registries or batches.
