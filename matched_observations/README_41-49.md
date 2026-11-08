# CRA observation matching: papers 41-49

Seven complete input sets were processed from `papers`, `citrine_database/by_reference` and `observation_registry`. Papers 42 and 48 have missing required inputs and received diagnostic reports only. Paper 50 is outside this batch and was not processed.

Across the seven valid input sets: **269 supplied observations**, **187 matched**, **32 ambiguous**, **50 unmatched**, **0 not assessed**. Supported links cover **181 of 183 distinct supplied CRA rows** (counting rows within each paper); CRA 802 in paper 43 and CRA 677 in paper 44 remain unlinked. Paper 41 has six shared-row groups, so observation and unique-row totals differ.

| Paper | Supplied observations | Matched | Ambiguous | Unmatched | Not assessed | Supported CRA rows / supplied | Alignment | Report |
|---|---:|---:|---:|---:|---:|---:|---|---|
| 41 | 26 | 12 | 0 | 14 | 0 | 6 / 6 | [JSON](paper_41.json) | [Report](paper_41_report.md) |
| 42 | — | — | — | — | — | — | Not created: missing inputs | [Diagnostic](paper_42_report.md) |
| 43 | 1 | 0 | 0 | 1 | 0 | 0 / 1 | [JSON](paper_43.json) | [Report](paper_43_report.md) |
| 44 | 101 | 91 | 1 | 9 | 0 | 91 / 92 | [JSON](paper_44.json) | [Report](paper_44_report.md) |
| 45 | 9 | 4 | 0 | 5 | 0 | 4 / 4 | [JSON](paper_45.json) | [Report](paper_45_report.md) |
| 46 | 14 | 8 | 0 | 6 | 0 | 8 / 8 | [JSON](paper_46.json) | [Report](paper_46_report.md) |
| 47 | 8 | 7 | 0 | 1 | 0 | 7 / 7 | [JSON](paper_47.json) | [Report](paper_47_report.md) |
| 48 | — | — | — | — | — | — | Not created: missing inputs | [Diagnostic](paper_48_report.md) |
| 49 | 110 | 65 | 31 | 14 | 0 | 65 / 65 | [JSON](paper_49.json) | [Report](paper_49_report.md) |

All seven saved alignment JSON files passed the bundled `validate_output.py` against the original PDF, CSV and registry inputs (exit 0). Each companion report is the validator's exact `--report-stdout` output, with one row per supplied observation (269 rows in total). Input SHA-256 fingerprints, original CSV strings and No. identifiers are preserved. Structural validation does not certify the scientific assignments or conversion assumptions.

Material qualifications:

- **41:** Alloy/standard-procedure identities are supported, including possible repeated table/plot presentations. SHE-to-SCE calculations are explicitly conditional on a 25 C saturated-KCl reference and are labeled not comparable for definitive numerical agreement because reference-cell calibration/temperature is unresolved. Modified scan histories remain separate. The illustrative constant is from [Corrtest's SCE specification](https://www.corrtestinstruments.com/en/02437.html).
- **42:** No matching PDF and no `observation_registry/paper_42.json`; input resolution failed before preparation. No alignment JSON was generated.
- **43:** CRA -720 mV corresponds to the source's distinct S-phase dissolution event; the supplied registry records matrix pitting near -620 mV. Its sole observation is unmatched.
- **44:** The source's 600 mV transpassivity surrogate supports specific qualitative counterparts without becoming a numerical pitting bound. Registry obs_029/031 have apparent swapped readings, retained as discrepant links. obs_079 / CRA 677 remains candidate-only. Several CRA procedure/processing fields conflict with the source.
- **45-47:** Stepped versus continuous scanning and distinct hold/processing histories are preserved. Paper 45 has a zero-chloride CRA conflict for 1 N HCl; paper 46 has a pH conflict; paper 47 labels chloride ppm where CRA labels NaCl ppm. Font warnings for papers 45-46 did not prevent visual inspection.
- **48:** `citrine_database/by_reference/pitting_potential_48.csv` is missing; preparation returned setup/I/O exit 2. No alignment JSON was generated.
- **49:** Table/figure potential, marker-label and concentration conflicts remain explicit. Fig.5 candidates retain the plotted log coordinates and alternative concentration-based identities; Fig.6 label 44653 retains two alternatives. Salt ppm is not equated with chloride ppm. The supplied CRA has no Remanit4565/4575 rows.

Use `matches` for supported joins; `candidates` are unresolved alternatives. Shared assignments do not establish identical runs. These outputs concern only the exact supplied registries and do not prove which source presentation the original curators used. No input registry, PDF, CSV, dataset or earlier batch output was changed.
