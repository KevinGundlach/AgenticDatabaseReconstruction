# Observation alignment: papers 31-40

All ten input sets passed preparation. Ten alignment/report pairs passed the bundled structural validator. The source PDFs, CSVs and version 1.1 registries were preserved, along with earlier batches.

The supplied registries contain 289 entries: 108 matched, 28 candidate-only, 153 unmatched and 0 not assessed. Supported links cover 59 distinct CRA records out of 80 supplied records. Individual readings sharing one CRA summary must not be counted as independent database records.

| Paper | Registry entries | Matched | Candidate only | Unmatched | Supported CRA rows | Alignment | Report |
|---|---:|---:|---:|---:|---:|---|---|
| 31 | 1 | 1 | 0 | 0 | 1 | [paper_31.json](paper_31.json) | [Report](paper_31_report.md) |
| 32 | 30 | 0 | 17 | 13 | 0 | [paper_32.json](paper_32.json) | [Report](paper_32_report.md) |
| 33 | 0 | 0 | 0 | 0 | 0 | [paper_33.json](paper_33.json) | [Report](paper_33_report.md) |
| 34 | 11 | 8 | 1 | 2 | 8 | [paper_34.json](paper_34.json) | [Report](paper_34_report.md) |
| 35 | 2 | 0 | 0 | 2 | 0 | [paper_35.json](paper_35.json) | [Report](paper_35_report.md) |
| 36 | 53 | 6 | 0 | 47 | 6 | [paper_36.json](paper_36.json) | [Report](paper_36_report.md) |
| 37 | 125 | 64 | 6 | 55 | 16 | [paper_37.json](paper_37.json) | [Report](paper_37_report.md) |
| 38 | 23 | 17 | 0 | 6 | 17 | [paper_38.json](paper_38.json) | [Report](paper_38_report.md) |
| 39 | 40 | 8 | 4 | 28 | 7 | [paper_39.json](paper_39.json) | [Report](paper_39_report.md) |
| 40 | 4 | 4 | 0 | 0 | 4 | [paper_40.json](paper_40.json) | [Report](paper_40_report.md) |

These are automated identity-alignment proposals. Structural validation checks schema, original fingerprints/cell strings, IDs/order, location references and the unlinked-row complement; it does not certify scientific assignments or conversion assumptions. Use `matches` for default joins; `candidates` remain unresolved. No observations were added, renumbered, consolidated or corrected.

Material qualifications retained in the individual outputs:

- Paper 31: exact tabulated Epit correspondence, with the Fe-analysis discrepancy retained and transpassive columns kept distinct.
- Paper 32: repeated same-alloy CRA records omit microstructure and nanocrystal-size selectors. Seventeen plausible links remain candidates. Example scans, medians/percentiles and metastable events retain their roles; the +980 mV target is not repaired by a guessed sign or decimal change.
- Paper 33: the supplied registry is empty. The valid empty alignment leaves both CRA rows unlinked and does not imply that the paper has no outcomes.
- Paper 34: eight L-series correspondences are supported, including a retained potential discrepancy. The Mn-rich M3 representative scan remains a candidate because of its electrolyte conflict and unresolved relation to the database central value.
- Paper 35: neither supplied observation is the 22 C scan outcome in the database. The 65 C potentiostatic upper bound and the cited Mo-free result remain unmatched.
- Paper 36: six Table 2 stepped-polarization identities are supported. Hot Ag/AgCl reference conditions do not establish an unconditional SCE conversion; potential agreement is not comparable. Scratching and transient experiments remain separate.
- Paper 37: 64 final-breakdown readings share 16 condition-summary rows. First-repassivating-pit endpoints remain unmatched, and six overlapping-marker partial entries remain candidates. No mean, hidden replicate count or pairing of initial/final events was invented.
- Paper 38: 17 base-metal/aging correspondences are supported; simulated high-temperature HAZ outcomes remain unmatched. The approximate 0.13% nitrogen caption and exact 0.137% alloy-D context are both retained.
- Paper 39: seven concentration-specific plotted correspondences plus one compatible strict region bound are supported. NHE-to-SCE comparison uses an explicitly sourced 25 C convention; activity and concentration axes are distinguished. Four expected-phase/aged-state relations remain candidates.
- Paper 40: all four 2 h annealing counterparts agree exactly; the 50 microA/cm2 current criterion and 65 C SCE reference conditions remain explicit.

Unlinked CRA rows, in each paper's original CSV order:

| Paper | Unlinked CRA No. |
|---|---|
| 32 | 779, 780, 781, 782, 783, 784, 785, 786, 787, 788, 789, 790, 791, 792, 793, 794 |
| 33 | 294, 295 |
| 34 | 300 |
| 35 | 305, 306 |

Unlinked means unassigned relative to the exact supplied registry, not absent from the paper. Candidate-only links do not remove rows from the unlinked list. Each compact report contains one table row per supplied ID and the actual structural validation result.
