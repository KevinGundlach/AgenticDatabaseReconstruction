# CRA observation matching: papers 63–69

The six available papers (63, 64, 66, 67, 68 and 69) were processed from the supplied `papers`, `citrine_database/by_reference` and `observation_registry` folders. Paper 65 received a diagnostic report because its PDF and registry JSON are missing. References 61, 62 and 70 are outside this batch and were not processed.

Across the six complete input sets: **70 supplied observations**, **33 matched**, **6 ambiguous**, **31 unmatched**, **0 not assessed**. Supported links cover **32 of 36 distinct supplied CRA rows**, counting rows within each paper. Paper 67 has one supported shared row (CRA 551); its two presentations are not proven identical runs. The four unlinked rows are paper 69 CRA 721, 723, 725 and 727, retained as candidates.

| Paper | Supplied observations | Matched | Ambiguous | Unmatched | Not assessed | Supported CRA rows / supplied | Alignment | Report |
|---|---:|---:|---:|---:|---:|---:|---|---|
| 63 | 2 | 2 | 0 | 0 | 0 | 2 / 2 | [JSON](paper_63.json) | [Report](paper_63_report.md) |
| 64 | 4 | 2 | 0 | 2 | 0 | 2 / 2 | [JSON](paper_64.json) | [Report](paper_64_report.md) |
| 65 | — | — | — | — | — | — | Not created: missing inputs | [Diagnostic](paper_65_report.md) |
| 66 | 36 | 12 | 0 | 24 | 0 | 12 / 12 | [JSON](paper_66.json) | [Report](paper_66_report.md) |
| 67 | 13 | 10 | 0 | 3 | 0 | 9 / 9 | [JSON](paper_67.json) | [Report](paper_67_report.md) |
| 68 | 3 | 2 | 0 | 1 | 0 | 2 / 2 | [JSON](paper_68.json) | [Report](paper_68_report.md) |
| 69 | 12 | 5 | 6 | 1 | 0 | 5 / 9 | [JSON](paper_69.json) | [Report](paper_69_report.md) |

All six saved alignments passed the bundled `validate_output.py` against their original PDF, CSV and registry inputs (exit 0). Each companion report is the exact subsequent `--report-stdout` output, with one row per supplied observation (70 rows total). Original input SHA-256 fingerprints, observation IDs/order, CRA No. identifiers and cell strings were verified. Structural validation does not certify scientific assignments or conversion assumptions.

Material qualifications:

- **63:** The two printed Table 2 Epit values agree exactly. The source table says aerated, while the methods say argon de-aerated. Source composition upper limits remain limits rather than exact measurements.
- **64:** The scanned control and implanted sample 10 match. The 500 mV hold outcomes remain distinct; sample 9 also has a different retained implant dose. Approximate Ec values retain the source reproducibility qualification.
- **65:** The CRA CSV exists, but no matching PDF or `paper_65.json` exists. Input resolution failed before the preparation helper could run; no alignment JSON was generated.
- **66:** Only quenched outcomes at the two supplied chloride concentrations are assigned. Forged specimens and 0.01 N no-pitting bounds remain distinct. Hydrogen-to-SCE calculations are explicitly conditional; definitive numerical agreement is marked not comparable because reference calibration/temperature is unresolved. Rendering warnings did not block the visually legible anchors.
- **67:** CRA wt% fields repeat the source atomic-percent numbers; full composition conversions expose this basis error. Potential comparisons use an explicit conditional SCE convention. Table/figure differences and the two possible FA-72C presentations sharing CRA 551 remain discrepant. Different Table 7 materials are not substituted by potential similarity.
- **68:** Two experimental-alloy Ep values match exactly. The commercial 304L result has no supplied counterpart. Pitting/protection potentials and stepped versus continuous procedures remain distinct.
- **69:** Five identities are supported, including the 4.0 at% marker with a discrepant potential. Six observations retain composition alternatives, including the crowded 5.0/5.4 at% region; original coordinates are unchanged. The Al–13Mo bound has no supplied composition counterpart. No marker was selected from the smooth fitted line.

External references supplied conversion constants only: [CIAAW atomic weights](https://ciaaw.org/abridged-atomic-weights.htm) and the [Corrtest 25 °C saturated-calomel reference value](https://www.corrtestinstruments.com/en/02437.html). Experimental evidence came only from each supplied PDF, registry and CRA CSV.

Use `matches` for supported joins; `candidates` remain unresolved. Shared assignments require care to avoid counting the same CRA row repeatedly. Results concern only the exact supplied registries and do not establish which presentation the original curators used. Inputs, datasets, enrichment results and earlier batch outputs were preserved.
