# Observation alignment: papers 11-20

Six alignment/report pairs passed the bundled structural validator. Papers 13, 14, 15 and 18 lack their required paper-specific CSVs and have diagnostic reports only. All source PDFs, registries and CSVs were preserved.

The valid input sets contain 121 supplied observations: 58 matched, 4 candidate-only, 59 unmatched and 0 not assessed. The blocked input sets contain 26 observations, all in paper 14; papers 13, 15 and 18 have empty registries.

| Paper | Result | Supplied observations | Matched | Candidate only | Unmatched | Alignment | Report |
|---|---|---:|---:|---:|---:|---|---|
| 11 | Validated | 15 | 12 | 1 | 2 | [paper_11.json](paper_11.json) | [Report](paper_11_report.md) |
| 12 | Validated | 32 | 23 | 3 | 6 | [paper_12.json](paper_12.json) | [Report](paper_12_report.md) |
| 13 | Missing CSV | 0 | — | — | — | Not created | [Report](paper_13_report.md) |
| 14 | Missing CSV | 26 | — | — | — | Not created | [Report](paper_14_report.md) |
| 15 | Missing CSV | 0 | — | — | — | Not created | [Report](paper_15_report.md) |
| 16 | Validated | 37 | 12 | 0 | 25 | [paper_16.json](paper_16.json) | [Report](paper_16_report.md) |
| 17 | Validated | 23 | 6 | 0 | 17 | [paper_17.json](paper_17.json) | [Report](paper_17_report.md) |
| 18 | Missing CSV | 0 | — | — | — | Not created | [Report](paper_18_report.md) |
| 19 | Validated | 4 | 3 | 0 | 1 | [paper_19.json](paper_19.json) | [Report](paper_19_report.md) |
| 20 | Validated | 10 | 2 | 0 | 8 | [paper_20.json](paper_20.json) | [Report](paper_20_report.md) |

These are automated identity-alignment proposals, not human confirmation or benchmark certification. Use `matches` for default joins; `candidates` are unresolved alternatives. Numerical potential agreement is assessed separately from identity. No observations were added, renumbered, consolidated or corrected.

Material qualifications in the individual outputs include:

- Paper 11: unavailable source analyses, a titanium-content conflict, strict scan bounds, and a representative-run candidate against a source average.
- Paper 12: conditional hydrogen-to-SCE conversion, unresolved partial-registry cluster labels, two potential discrepancies, and qualified annealed/intergranular breakdown.
- Paper 16: base metal, HAZ and weld conditions kept distinct; upward testing limits preserved rather than certified as exact numerical thresholds.
- Paper 17: nominal atomic-ratio to wt.% comparison with explicit assumptions for grouped formulas; unspecified uncertainty type and a source processing-label conflict retained.
- Paper 19: explicitly labelled pitting outcomes retained with the source interdendritic galvanic-attack qualification.
- Paper 20: primary -0.25 V and secondary -0.49 V source readings both preserved for the 1 M NaCl HEA result, along with pH and phase-description conflicts.

CRA 377, 379 and 380 (paper 12) remain unlinked because their assignments are candidate-only. Unlinked means unassigned relative to this supplied registry, not proven absent from the paper.
