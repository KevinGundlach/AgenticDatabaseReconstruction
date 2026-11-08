# Observation-to-CRA alignment

Paper: 43_V. Guillaumin, G. Mankowski, Corrosion Science, 41 (1998) 421-438.pdf; reference 43. Registry: paper_43.json; CSV: pitting_potential_43.csv. Supplied observations=1; CRA rows=1.

These are automated alignment proposals for this exact supplied registry. Unlinked rows are unassigned in this input, not proven absent from the paper. Avg is a database column label, not evidence of a source-reported mean.

| Observation | Registered reading / location | Supported CRA No. | Candidate CRA No. | CRA targets (mV SCE) | Evidence / conversion | Status / notes |
|---|---|---|---|---|---|---|
| obs_001 | loc 0: -620.0 mV (SCE) (transcribed); PDF p. 6 / printed p. 426, 3.2. Polarization curve in sodium chloride solution and breakdown potential, the more noble one Eb2, close to | none | none | — | — | unmatched: The registered matrix-pitting event Eb2 is about -620 mV(SCE), whereas sole CRA No.802 is -720 mV(SCE). PDF p.6 explicitly associates -720 (Eb1) with selective dissolution/dealloying of S-phase Al2CuMg; matrix pitting/intergranular attack begins at Eb2, confirmed by Fig.7, p.15 discussion and p.17 conclusion. Same alloy/medium cannot establish counterpart identity for these different outcomes; No.802 stays unlinked. No new Eb1 observation is created. |

Status counts: matched=0; ambiguous=0; unmatched=1; not_assessed=0.
ambiguous IDs: none.
unmatched IDs: obs_001.
not_assessed IDs: none.

Supported shared-row groups: none.
Unlinked CRA No. in this input: 802.

Shared qualifications:

- The roughly 100 mV difference is not repaired as a transcription or reference-electrode error: the paper distinguishes S-phase dissolution from matrix pitting. Only the supplied matrix-pitting ID is assessed.

Visually inspected PDF pages: 6, 7, 15, 17.
Coverage/access: Every supplied observation and CSV row was considered. All registered anchor pages were visually inspected, including secondary locations. This is registry-scoped identity alignment, not a full-paper census or proof of the original curator's chosen presentation. Inputs are unchanged.

Structural validation: PASS against the bundled schema/model and exact supplied inputs. Scientific fidelity, conversion arithmetic/assumptions, identity and benchmark suitability are not certified. Only supported links enter default joins; shared rows must not be counted as independent benchmark rows without review.
