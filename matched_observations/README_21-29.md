# Observation alignment: papers 21-29

Six alignment/report pairs passed the bundled structural validator. Papers 21, 23 and 24 lack their required paper-specific CSVs and have diagnostic reports only. All supplied PDFs, registries and CSVs were preserved. Only reference numbers 21 through 29 were processed; paper 30 was not expected or sought.

The complete input sets contain 49 supplied observations: 15 matched, 2 candidate-only, 32 unmatched and 0 not assessed. The missing-CSV cases contain 30 registry entries and are excluded from these assessment counts. The supported links cover 15 distinct CRA records out of 16 supplied records.

| Paper | Result | Registry entries | Matched | Candidate only | Unmatched | Alignment | Report |
|---|---|---:|---:|---:|---:|---|---|
| 21 | Missing CSV | 9 | — | — | — | Not created | [Report](paper_21_report.md) |
| 22 | Validated | 7 | 6 | 0 | 1 | [paper_22.json](paper_22.json) | [Report](paper_22_report.md) |
| 23 | Missing CSV | 20 | — | — | — | Not created | [Report](paper_23_report.md) |
| 24 | Missing CSV | 1 | — | — | — | Not created | [Report](paper_24_report.md) |
| 25 | Validated | 1 | 1 | 0 | 0 | [paper_25.json](paper_25.json) | [Report](paper_25_report.md) |
| 26 | Validated | 10 | 2 | 0 | 8 | [paper_26.json](paper_26.json) | [Report](paper_26_report.md) |
| 27 | Validated | 8 | 2 | 0 | 6 | [paper_27.json](paper_27.json) | [Report](paper_27_report.md) |
| 28 | Validated | 21 | 3 | 2 | 16 | [paper_28.json](paper_28.json) | [Report](paper_28_report.md) |
| 29 | Validated | 2 | 1 | 0 | 1 | [paper_29.json](paper_29.json) | [Report](paper_29_report.md) |

These are automated identity-alignment proposals, not human confirmation or benchmark certification. Structural validation checks fingerprints, schema, original cell strings, observation coverage and bookkeeping; it does not certify scientific assignments. Use `matches` for default joins; `candidates` are unresolved alternatives. No observation was added, renumbered, consolidated or corrected.

Material qualifications retained in the individual outputs:

- Paper 22: heat-treatment identity supports both high-temperature links despite apparently transposed 800 C and 950 C CRA potentials; those two potential comparisons are discrepant.
- Paper 25: text (-0.56 V) and figure (about -0.68 V) disagree. Ag/AgCl filling/reference-temperature information is insufficient for an SCE offset, so potential agreement is not comparable despite supported experiment identity. The 1:30 artificial-sea-salt recipe and nominal Al/CRA composition discrepancy are preserved.
- Paper 26: the two SHE-to-SCE comparisons are conditional on an explicitly sourced 25 C reference convention. Chloride-free acid endpoints retain the source transpassive-dissolution qualification.
- Paper 27: the HCl experiment uses Ag/AgCl, whereas CRA labels its unchanged raw value SCE. This is a discrepant potential comparison; the NaCl experiment uses SCE directly.
- Paper 28: mean +/- SD endpoints correspond arithmetically to CRA bounds, without establishing observed extrema. The source 20 +/- 2 C versus CRA 25 C conflict and current-criterion/selective-dissolution qualifications are retained. Two unlabeled Fig.11 markers remain candidate-only; their possible repeated-presentation identities are unresolved.
- Paper 29: A35 metastable-pit breakdown and repeated SCE/SHE presentations are retained, along with the source initial pH 8.4 versus CRA pH 7 conflict.

CRA 601 (paper 29) remains unlinked relative to the supplied registry; no A36 observation was invented to fill it. Unlinked does not mean absent from the paper. Candidate links to CRA 597/598 do not create supported shared-row assignments.
