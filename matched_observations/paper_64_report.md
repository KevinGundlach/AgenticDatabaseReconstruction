# Observation-to-CRA alignment

Paper: 64_Ives, M. B., et al. Corrosion science 31 (1990)_ 367-376.pdf; reference 64. Registry: paper_64.json; CSV: pitting_potential_64.csv. Supplied observations=4; CRA rows=2.

These are automated alignment proposals for this exact supplied registry. Unlinked rows are unassigned in this input, not proven absent from the paper. Avg is a database column label, not evidence of a source-reported mean.

| Observation | Registered reading / location | Supported CRA No. | Candidate CRA No. | CRA targets (mV SCE) | Evidence / conversion | Status / notes |
|---|---|---|---|---|---|---|
| obs_001 | loc 0: max=500.0 mV (SCE) (transcribed); PDF p. 4 / printed p. 370, Electrochemical Tests, also exhibits breakdown | none | none | — | — | unmatched: This control result is an upper limit from a500 mV(SCE) hold with chloride added after30 min (PDF pp.4-5). CRA566 is identified with the separate scanned Ec transition; the hold endpoint is not that measured threshold. |
| obs_002 | loc 0: max=500.0 mV (SCE) (transcribed); PDF p. 4 / printed p. 370, Electrochemical Tests, also exhibits breakdown | none | none | — | — | unmatched: This upper limit is from the chloride-addition hold on sample9 (3.10*10^16 Mo ions/cm2), not the scanned sample10 dose5.55*10^16 represented by CRA567. Both specimen and protocol differ; no counterpart is supplied. |
| obs_003 | loc 0: 0.45 V (SCE) (digitized); PDF p. 5 / printed p. 371, Fig. 3, UNS S30100 ss control; thin curve; Ec annotation, Solution=0.1 M Na2SO4 + 0.6 M NaCl; deaerated with N2 | 566 | none | 566 (supported): Avg=449; Min=; Max= | 566 / Cr: paper=17.0 wt% Cr, Table1, PDF p.2; CRA=17.0; Independent substrate analysis.<br>566 / Ni: paper=8.1 wt% Ni, Table1; CRA=8.1; Independent substrate analysis.<br>566 / Mo: paper=0.17 wt% bulk Mo, Table1; CRA=0.17; Substrate composition, not the near-surface implant concentration.<br>566 / Test Solution: paper=0.1 M Na2SO4 +0.6 M NaCl, Fig.3, N2 de-aerated; CRA=0.1M Na2SO4 + 0.6M NaCl; Same independently labeled electrolyte and gas.<br>566 / Heat treatment: paper=Annealed UNS S30100; unimplanted control, Fig.3; CRA=annealed UNS S30100 austenitic stainless steel; Source substrate state and implant condition identify the counterpart; sample9 has a different dose.<br>566 / Avg Epit mV (SCE): paper={"unit": "V (SCE)", "value": 0.45}; CRA=449; V(SCE)*1000=mV(SCE): approximately450 mV from the explicitly Ec-labeled transition, compatible with CRA graphical precision. This is not the500 mV hold endpoint.<br>566: within_precision; Independent substrate composition, electrolyte and control versus sample10 implant identity select the Fig.3 counterpart (PDF pp.2,4-5). Apparent Ec and its reproducibility qualification are preserved. | matched |
| obs_004 | loc 0: 0.38 V (SCE) (digitized); PDF p. 5 / printed p. 371, Fig. 3, Mo ion-implanted UNS S30100 ss; thick curve; Ec annotation, Solution=0.1 M Na2SO4 + 0.6 M NaCl; deaerated with N2 | 567 | none | 567 (supported): Avg=379; Min=; Max= | 567 / Cr: paper=17.0 wt% Cr, Table1, PDF p.2; CRA=17.0; Independent substrate analysis.<br>567 / Ni: paper=8.1 wt% Ni, Table1; CRA=8.1; Independent substrate analysis.<br>567 / Mo: paper=0.17 wt% bulk Mo, Table1; CRA=0.17; Substrate composition, not the near-surface implant concentration.<br>567 / Test Solution: paper=0.1 M Na2SO4 +0.6 M NaCl, Fig.3, N2 de-aerated; CRA=0.1M Na2SO4 + 0.6M NaCl; Same independently labeled electrolyte and gas.<br>567 / Heat treatment: paper=Annealed UNS S30100; sample10,140 keV,5.55*10^16 retained Mo ions/cm2, Table2/Fig.3; CRA=annealed UNS S30100 austenitic stainless steel, ion implanted with Mo implanted  with 5.55*1016 molybdenum ions/cm2 ; Source substrate state and implant condition identify the counterpart; sample9 has a different dose.<br>567 / Avg Epit mV (SCE): paper={"unit": "V (SCE)", "value": 0.38}; CRA=379; V(SCE)*1000=mV(SCE): approximately380 mV from the explicitly Ec-labeled transition, compatible with CRA graphical precision. This is not the500 mV hold endpoint.<br>567: within_precision; Independent substrate composition, electrolyte and control versus sample10 implant identity select the Fig.3 counterpart (PDF pp.2,4-5). Apparent Ec and its reproducibility qualification are preserved. | matched |

Status counts: matched=2; ambiguous=0; unmatched=2; not_assessed=0.
ambiguous IDs: none.
unmatched IDs: obs_001, obs_002.
not_assessed IDs: none.

Supported shared-row groups: none.
Unlinked CRA No. in this input: none.

Shared qualifications:

- Source Table1 independently identifies the annealed UNS S30100 substrate (PDF p.2). Table2 distinguishes implanted sample9 (140 keV,3.10*10^16 retained Mo ions/cm2) from sample10 (140 keV,5.55*10^16), PDF p.4. Implant dose is not converted to a bulk Mo wt%.
- Fig.3 labels apparent critical pitting Ec on the forward polarization characteristics; the authors emphasize its poor reproducibility and no consistent beneficial Ec shift (PDF pp.4-5). The labeled transitions were visually enlarged; no extra onset was traced from unannotated curves.
- The500 mV(SCE) chloride-addition holds (control and sample9) produce only upper limits on pitting threshold. They are distinct from the scanned control/sample10 outcomes represented by the two CRA rows. V(SCE)*1000=mV(SCE), without a reference offset.
- CRA25 C and any numerical scan rate are not independently supplied by the inspected source electrochemical passages. The text specifies room-temperature implantation, which is not automatically the test temperature.

Visually inspected PDF pages: 1, 2, 3, 4, 5.
Coverage/access: Every supplied observation and CRA row was considered. Every registered anchor page, including secondary locations, was actually viewed. Context pages and enlarged source plots were consulted where needed. This is alignment of the exact supplied registry, not a full-paper census or proof of the presentation selected by the original curators. Inputs are unchanged.

Structural validation: PASS against the bundled schema/model and exact supplied inputs. Scientific fidelity, conversion arithmetic/assumptions, identity and benchmark suitability are not certified. Only supported links enter default joins; shared rows must not be counted as independent benchmark rows without review.
