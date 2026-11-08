# Observation alignment: papers 1-10

Eight alignment/report pairs passed the bundled structural validator, including paper 10 with an empty supplied registry. Papers 4 and 5 lack their required CSV inputs and have diagnostic reports only. All source PDFs, registries and CSVs were preserved.

Valid input sets contain 565 supplied observations: unmatched 377, matched 176, ambiguous 12. Paper 4 has 26 registry observations blocked by its missing CSV; papers 5 and 10 have zero supplied observations.

| Paper | Result | Matched | Candidate only | Unmatched | Alignment | Report |
|---|---|---:|---:|---:|---|---|
| 1 | Validated | 19 | 0 | 32 | [paper_1.json](paper_1.json) | [Report](paper_1_report.md) |
| 2 | Validated | 17 | 2 | 24 | [paper_2.json](paper_2.json) | [Report](paper_2_report.md) |
| 3 | Validated | 56 | 6 | 108 | [paper_3.json](paper_3.json) | [Report](paper_3_report.md) |
| 4 | Missing CSV | — | — | — | Not created | [Report](paper_4_report.md) |
| 5 | Missing CSV | — | — | — | Not created | [Report](paper_5_report.md) |
| 6 | Validated | 22 | 0 | 60 | [paper_6.json](paper_6.json) | [Report](paper_6_report.md) |
| 7 | Validated | 12 | 0 | 52 | [paper_7.json](paper_7.json) | [Report](paper_7_report.md) |
| 8 | Validated | 11 | 4 | 16 | [paper_8.json](paper_8.json) | [Report](paper_8_report.md) |
| 9 | Validated | 39 | 0 | 85 | [paper_9.json](paper_9.json) | [Report](paper_9_report.md) |
| 10 | Validated; empty registry | 0 | 0 | 0 | [paper_10.json](paper_10.json) | [Report](paper_10_report.md) |

These are automated identity-alignment proposals, not human confirmation or benchmark certification. Default joins must use `matches`, not `candidates`, and account for shared CRA rows. Potential agreement is assessed separately from identity.

Material qualifications are recorded in each pair: conditional electrode conversion (paper 1), incomplete CSV alloy compositions and a scan-rate conflict (paper 2), distinct scan/scratch/current-time outcomes and source conflicts (paper 3), CSV composition/source-table conflicts (paper 6), source-calibrated electrode comparison and perchlorate/chloride distinction (paper 7), heat identity and pitting/transpassive uncertainty (paper 8), and the unlocalized current criterion plus a visible registry-reading discrepancy (paper 9).

Paper 8 CRA 471 and paper 10 CRA 307/308 remain unlinked. That complement is relative to the supplied registry only; unlinked rows do not establish absence from a paper.
