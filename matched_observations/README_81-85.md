# Observation-to-CRA matching: papers 81–85

Applied `match-observations-cra-database` using only the supplied `papers/`, `citrine_database/by_reference/` and `observation_registry/` experimental inputs. Saved outputs in this folder without modifying inputs or adding observations.

Three valid input sets contain 37 observations and 35 CRA rows: 23 matched, 3 ambiguous, 11 unmatched and 0 not assessed. Supported links cover 23 distinct CRA rows; 12 remain unlinked. Candidates are excluded from supported joins.

| Paper | Observations | Matched | Ambiguous | Unmatched | Not assessed | CRA linked / total | Outputs |
|---|---:|---:|---:|---:|---:|---:|---|
| 81 | 12 | 12 | 0 | 0 | 0 | 12 / 12 | [JSON](paper_81.json), [report](paper_81_report.md) |
| 82 | — | — | — | — | — | — | [Input-failure report](paper_82_report.md) |
| 83 | — | — | — | — | — | — | [Input-failure report](paper_83_report.md) |
| 84 | 3 | 3 | 0 | 0 | 0 | 3 / 15 | [JSON](paper_84.json), [report](paper_84_report.md) |
| 85 | 22 | 8 | 3 | 11 | 0 | 8 / 8 | [JSON](paper_85.json), [report](paper_85_report.md) |

- Papers82 and83: PDFs and registries exist, but their respective CRA CSVs `pitting_potential_82.csv` and `pitting_potential_83.csv` are missing. The preparation helper actually returned2 for each. Diagnostic reports preserve the actual errors; no success-shaped alignment JSON was produced.
- Paper81: all twelve alloy/electrolyte/temperature counterparts are supported. CRA omits the .84/1.84 wt% Re additions and omits them from its Fe balances; these discrepancies remain explicit. The step-and-hold endpoint is preserved and the reported average stepping rate is not called a continuous sweep.
- Paper84: the three text-reported chloride pitting results are supported. Acid curves, composition studies and processing variants remain outside the supplied registry; twelve CRA rows remain unlinked. The approximate800 mV Ferralium text is retained alongside CRA850.
- Paper85: eight named-product/temperature Figure4 results are supported. Three cited/generic high-nitrogen results remain candidate-only against the30°C Ferralium255 row; their exact product/specimen identity is unresolved. Eleven other observations have no defensible counterpart. Table2 Cast20-type specifies Nb=8×%C, whereas CRA puts .56 in N and0.0 in Nb; this is recorded as a field conflict, without rewriting either input. Composition ranges/minima/maxima are not treated as measured specimen analyses.

Potential comparisons for papers81/85 are conditional on documented25°C saturated-KCl SCE conventions. Both manufacturer constants are shown: [ALS/BAS +0.244 V versus SHE](https://www.als-japan.com/2137.html) and [Corrtest +0.241 V versus NHE at25°C](https://www.corrtestinstruments.com/en/02437.html). Physical reference temperature/calibration is not established by the supplied inputs; assay temperature is not substituted for it. External sources supplied conversion constants only. Paper84 uses the same stated SCE scale directly.

Every relevant registered anchor and necessary contextual passage was visually inspected; the actual one-based pages are recorded in each alignment. Paper85 render font diagnostics are disclosed; anchors remained legible and Table2 was enlarged to verify its Nb subheading. No OCR, automatic table extraction or curve/marker detection was used.

All three final saved JSON files passed the bundled validator (exit0), followed by a separate successful `--report-stdout` invocation. Each report is saved exactly from that stdout and contains one ordered row per supplied observation. Validation checks structure, IDs/order, exact cells, location indices, fingerprints and unlinked-row complements; it does not certify scientific correctness or curator provenance.

Input hashes and pre-existing output hashes were checked unchanged. Earlier batches are preserved and are not automatically merged. Default downstream joins use `matches`, not `candidates`; possible repeated presentations must not be counted as established duplicate runs.
