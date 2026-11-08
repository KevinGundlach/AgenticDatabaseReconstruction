# Observation-to-CRA alignment

Paper: 35_I. Olefjord, L. Wegrelius, Corros. Sci. 38 (1996)_ p. 1203.pdf; reference 35. Registry: paper_35.json; CSV: pitting_potential_35.csv. Supplied observations=2; CRA rows=2.

These are automated alignment proposals for this exact supplied registry. Unlinked rows are unassigned in this input, not proven absent from the paper. Avg is a database column label, not evidence of a source-reported mean.

| Observation | Registered reading / location | Supported CRA No. | Candidate CRA No. | CRA targets (mV SCE) | Evidence / conversion | Status / notes |
|---|---|---|---|---|---|---|
| obs_001 | loc 0: max=500.0 mV (SCE) (transcribed); PDF p. 3 / printed p. 1205, EXPERIMENTAL RESULTS, steadily increasing current due to propagation of active pits. | none | none | — | — | unmatched: Low-N Mo-bearing steel at 65 C, +500 mV potentiostatic exposure: active pits propagate after an induction period, giving Epit &lt;=500 mV. CRA 305 instead specifies the 22 C, 1 mV/s scan with central target 841.509 mV; same alloy/solution alone does not establish the same outcome. Both source presentations (PDF pp.3,11) considered. |
| obs_002 | loc 0: 500.0 mV (SCE) (transcribed); PDF p. 16 / printed p. 1218, DISCUSSION, the pitting potential of the Mo-free alloy is about 500 mV | none | none | — | — | unmatched: Cited Fe-20Cr-20Ni Mo-free comparison (~500 mV at room temperature, PDF p.16) has no supplied material counterpart: both CRA records contain approximately 6 wt.% Mo. No exclusion solely because the result is cited. |

Status counts: matched=0; ambiguous=0; unmatched=2; not_assessed=0.
ambiguous IDs: none.
unmatched IDs: obs_001, obs_002.
not_assessed IDs: none.

Supported shared-row groups: none.
Unlinked CRA No. in this input: 305, 306.

Shared qualifications:

- The +500 mV potentiostatic outcome is an at-or-below upper bound at 65 C, not an exact scan-derived Epit. The cited room-temperature Mo-free result is assessed without excluding its provenance category.

Visually inspected PDF pages: 3, 11, 16.
Coverage/access: Rendered a short-named, byte-identical PDF copy after verifying its SHA-256 against the original. Input fingerprints refer to original supplied bytes. Only listed PDF pages were actually viewed. Both supplied observations and both CSV rows considered. Primary and secondary anchors on PDF pp.3,11,16 visually inspected. The 841.509 mV CSV targets are not used to invent unregistered scan thresholds.

Structural validation: PASS against the bundled schema/model and exact supplied inputs. Scientific fidelity, conversion arithmetic/assumptions, identity and benchmark suitability are not certified. Only supported links enter default joins; shared rows must not be counted as independent benchmark rows without review.
