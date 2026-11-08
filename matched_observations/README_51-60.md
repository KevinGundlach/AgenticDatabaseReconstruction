# CRA observation matching: papers 51-60

Papers 54–60 were processed using the supplied `papers`, `citrine_database/by_reference` and `observation_registry` folders. Papers 51–53 have missing CRA CSV files and received diagnostic reports only. All inputs and earlier batch outputs were preserved.

Across the seven complete input sets: **237 supplied observations**, **177 matched**, **16 ambiguous**, **44 unmatched**, **0 not assessed**. Supported links cover **47 of 79 distinct supplied CRA rows**, counting rows within each paper. The difference between observation and unique-row totals comes from paper 56 population members linking to six shared summary rows.

| Paper | Supplied observations | Matched | Ambiguous | Unmatched | Not assessed | Supported CRA rows / supplied | Alignment | Report |
|---|---:|---:|---:|---:|---:|---:|---|---|
| 51 | — | — | — | — | — | — | Not created: missing CSV | [Diagnostic](paper_51_report.md) |
| 52 | — | — | — | — | — | — | Not created: missing CSV | [Diagnostic](paper_52_report.md) |
| 53 | — | — | — | — | — | — | Not created: missing CSV | [Diagnostic](paper_53_report.md) |
| 54 | 67 | 30 | 0 | 37 | 0 | 30 / 30 | [JSON](paper_54.json) | [Report](paper_54_report.md) |
| 55 | 9 | 4 | 1 | 4 | 0 | 4 / 5 | [JSON](paper_55.json) | [Report](paper_55_report.md) |
| 56 | 143 | 138 | 3 | 2 | 0 | 8 / 8 | [JSON](paper_56.json) | [Report](paper_56_report.md) |
| 57 | 3 | 1 | 2 | 0 | 0 | 1 / 26 | [JSON](paper_57.json) | [Report](paper_57_report.md) |
| 58 | 8 | 0 | 8 | 0 | 0 | 0 / 4 | [JSON](paper_58.json) | [Report](paper_58_report.md) |
| 59 | 2 | 0 | 2 | 0 | 0 | 0 / 2 | [JSON](paper_59.json) | [Report](paper_59_report.md) |
| 60 | 5 | 4 | 0 | 1 | 0 | 4 / 4 | [JSON](paper_60.json) | [Report](paper_60_report.md) |

All seven saved alignments passed the bundled `validate_output.py` against the original PDF, CSV and registry inputs (exit 0). Each report is the exact subsequent `--report-stdout` output, with one row per supplied observation (237 rows total). Input fingerprints, original observation IDs/order, original CRA No. identifiers and cell strings were verified. Structural validation does not certify scientific identities or conversion assumptions.

Material qualifications:

- **51–53:** Each required `pitting_potential_51.csv`, `pitting_potential_52.csv` or `pitting_potential_53.csv` is missing. Preparation returned setup/I/O exit 2. No alignment JSON was created for these papers.
- **54:** Material analyses and condition columns support 30 rows. Acid scans use 6 mV/min rather than the CRA 20 mV/min equivalent. CRA 245 has a chloride concentration conflict. The neutral specimen 21 no-breakdown limits of 708/908 mV and separate 70 °C tests remain distinct from measured acid thresholds.
- **55:** Atomic-percent formulas were converted to wt% using complete ternary compositions. The pure-Al potential disagreement is retained as a discrepant match. Fully crystalline CRA 778 remains candidate-only because source processing identity is missing from its metadata and its mean/uncertainty differs. The 100 °C aging series remains distinct.
- **56:** Individual plot readings link to population summaries without being equated to means or confidence endpoints. Shared CRA 700/701/702/703/705/707 links must not be counted as independent summary records. Registry Fig. 8(b) area labels conflict with the PDF caption/arrows; both descriptions are preserved. Partial upper-marker alternatives remain candidates. CRA 707 has an atomic/wt% basis error and a 551/550 °C discrepancy. Source table/text and distribution conflicts remain explicit.
- **57:** The 17Cr–25Ni–5Mo numerical onset is supported. No-pitting bounds that end at transpassivity remain candidates, preserving analytical/nominal alloy alternatives. A stepped 25 mV/one-minute procedure is not treated as a continuous sweep.
- **58–59:** Applied 200/500 mV hydrogen-reference holds establish no-pitting lower limits. Shared materials/media alone do not identify these bounds with the numerical CRA targets; proposed counterparts remain candidates. Paper 58 also has source 65 °C versus CRA 25 °C and protocol conflicts. No fitted electrode offset or new threshold from continuous curves was used.
- **60:** Four Table II microelectrode means and confidence endpoints agree. The separate large-area pure-Al footnote has no supplied counterpart. The source positive nanocrystalline value is retained. Font warnings did not block visual inspection.

Composition constants only were verified externally using [CIAAW Abridged Standard Atomic Weights](https://ciaaw.org/abridged-atomic-weights.htm). Experimental evidence came only from each supplied PDF, registry and CRA CSV.

Use `matches` for supported joins; `candidates` are unresolved alternatives. These results are scoped to the exact supplied registries. Shared assignments do not prove common-run identity or establish which source presentation the original curators used. No registry, PDF, CSV, dataset, enrichment result or earlier batch output was modified.
