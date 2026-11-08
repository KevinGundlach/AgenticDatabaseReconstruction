# Observation-to-CRA alignment

Paper: 31_G. P. Halada , D. Kim , C.R. Clayton , Corrosion 52 (1996)_ p. 36.pdf; reference 31. Registry: paper_31.json; CSV: pitting_potential_31.csv. Supplied observations=1; CRA rows=1.

These are automated alignment proposals for this exact supplied registry. Unlinked rows are unassigned in this input, not proven absent from the paper. Avg is a database column label, not evidence of a source-reported mean.

| Observation | Registered reading / location | Supported CRA No. | Candidate CRA No. | CRA targets (mV SCE) | Evidence / conversion | Status / notes |
|---|---|---|---|---|---|---|
| obs_001 | loc 0: 239.0 mV (SCE) (transcribed); PDF p. 5 / printed p. 40, TABLE 3, Fe-20% Cr-20% Ni, Epit | 152 | none | 152 (supported): Avg=239; Min=; Max= | 152 / Cr: paper=Table 1 Mo-free Fe-20Cr-20Ni alloy: 20.12 wt.% Cr; CRA=20.12; Direct source wt.% agrees.<br>152 / Ni: paper=Table 1 Mo-free Fe-20Cr-20Ni alloy: 20.18 wt.% Ni; CRA=20.18; Direct source wt.% agrees.<br>152 / Mo: paper=Table 1 Mo-free Fe-20Cr-20Ni alloy: 0.01 wt.% Mo; CRA=0.01; Direct source wt.% agrees.<br>152 / N: paper=Table 1 Mo-free Fe-20Cr-20Ni alloy: 0.011 wt.% N; CRA=0.011; Direct source wt.% agrees.<br>152 / Test Solution: paper=0.1 M HCl + 0.4 M NaCl; Ar deaerated at least 2 h; CRA=0.1 M HCl + 0.4 M NaCl; Exact electrolyte and gas preparation; p.3 methods and Fig.1 caption.<br>152 / Scan Rate mV/s: paper=1 mV/s; CRA=1; Exact sweep rate.<br>152 / Heat treatment: paper=1100 C for 3 h, water quenched; polished to 0.25 micrometre diamond finish; CRA=0.25 um diamond finish, annealed at 1100C for 3h and water quenched; Matches processing on PDF p.2.<br>152 / Avg Epit mV (SCE): paper={"unit": "mV (SCE)", "value": 239}; CRA=239; Table 3 Epit=239 mV(SCE), exactly CRA 239; same electrode scale.<br>152: exact; Mo-free high-Ni alloy chemistry plus the chloride mixture and sweep identify the Table 3 Epit counterpart (PDF pp.2-3,5). The Fe-analysis discrepancy is retained without modifying either input. | matched |

Status counts: matched=1; ambiguous=0; unmatched=0; not_assessed=0.
ambiguous IDs: none.
unmatched IDs: none.
not_assessed IDs: none.

Supported shared-row groups: none.
Unlinked CRA No. in this input: none.

Shared qualifications:

- Table 3 explicitly distinguishes Epit from transpassive Etr. No new Epit is inferred for its blank cells.
- Table 1 reports Fe 59.58 wt.% for the Mo-free alloy, whereas CRA Fe is 59.3898 wt.%; this context discrepancy is retained. The directly matching Cr/Ni/Mo/N analysis and experiment identify the counterpart.

Visually inspected PDF pages: 2, 3, 5.
Coverage/access: Rendered a short-named, byte-identical PDF copy after verifying its SHA-256 against the original. Input fingerprints refer to original supplied bytes. Only listed PDF pages were actually viewed. One registry entry and one CRA record considered. Table 3 and Fig.1 caption on PDF p.5, Table 1/procedure on p.3 and heat treatment on p.2 visually inspected. Poppler issued missing display-font warnings for Symbol and ArialNarrow variants; the decisive table numbers and captions were visually legible.

Structural validation: PASS against the bundled schema/model and exact supplied inputs. Scientific fidelity, conversion arithmetic/assumptions, identity and benchmark suitability are not certified. Only supported links enter default joins; shared rows must not be counted as independent benchmark rows without review.
