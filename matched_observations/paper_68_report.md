# Observation-to-CRA alignment

Paper: 68_Newman, R. C. Corrosion Science 25.5 (1985)_ 341-350.pdf; reference 68. Registry: paper_68.json; CSV: pitting_potential_68.csv. Supplied observations=3; CRA rows=2.

These are automated alignment proposals for this exact supplied registry. Unlinked rows are unassigned in this input, not proven absent from the paper. Avg is a database column label, not evidence of a source-reported mean.

| Observation | Registered reading / location | Supported CRA No. | Candidate CRA No. | CRA targets (mV SCE) | Evidence / conversion | Status / notes |
|---|---|---|---|---|---|---|
| obs_001 | loc 0: -75.0 mV (SCE) (transcribed); PDF p. 7 / printed p. 347, Table 3, Fe–Cr–Ni, Ep (mV SCE) | 541 | none | 541 (supported): Avg=-75; Min=; Max= | 541 / Cr: paper=18.7 wt% Cr, Table1, PDF p.2; CRA=18.7; Independent source alloy analysis.<br>541 / Ni: paper=10.3 wt% Ni, Table1; CRA=10.3; Independent source alloy analysis.<br>541 / Mo: paper=Source Table1 dash (no listed Mo addition); CRA=0.0; Distinguishes experimental Fe-Cr-Ni and Fe-Cr-Ni-Mo materials; dash is not an invented measured zero.<br>541 / Test Solution: paper=Neutral1 M KCl, Table3 / PDF p.4; CRA=1M KCl; Same explicitly stated salt/molarity; no exact pH is inferred.<br>541 / Test Temp C: paper=22+/-1 C throughout, PDF p.4; CRA=22.0; CRA22 C is the nominal test temperature.<br>541 / Test Method: paper=Mechanically polished0.4 cm2 coupons; upward25 mV steps every400 s beginning-300 mV(SCE), PDF p.4; CRA=To measure the pitting potentials, the potential was stepped upwards by 25 mV every 400 s, beginning at -300 mV(SCE).; Same independent pitting protocol; distinct from artificial-pit kinetics.<br>541 / Scan Rate mV/s: paper=25 mV increment /400 s dwell; CRA=0.0625; C1:25/400=0.0625 mV/s nominal stepped rate.<br>541 / Avg Epit mV (SCE): paper={"unit": "mV (SCE)", "value": -75}; CRA=-75; Both use mV(SCE). Table3 printed Ep agrees exactly; adjacent Epp is excluded.<br>541: exact; Table1 source composition and Table3 named experimental-alloy row, with the independent coupon protocol, identify the counterpart (PDF pp.2,4,7). | matched |
| obs_002 | loc 0: 50.0 mV (SCE) (transcribed); PDF p. 7 / printed p. 347, Table 3, Fe–Cr–Ni–Mo, Ep (mV SCE) | 542 | none | 542 (supported): Avg=50; Min=; Max= | 542 / Cr: paper=16.6 wt% Cr, Table1, PDF p.2; CRA=16.6; Independent source alloy analysis.<br>542 / Ni: paper=11 wt% Ni, Table1; CRA=11.0; Independent source alloy analysis.<br>542 / Mo: paper=2.7 wt% Mo, Table1; CRA=2.7; Distinguishes experimental Fe-Cr-Ni and Fe-Cr-Ni-Mo materials; dash is not an invented measured zero.<br>542 / Test Solution: paper=Neutral1 M KCl, Table3 / PDF p.4; CRA=1M KCl; Same explicitly stated salt/molarity; no exact pH is inferred.<br>542 / Test Temp C: paper=22+/-1 C throughout, PDF p.4; CRA=22.0; CRA22 C is the nominal test temperature.<br>542 / Test Method: paper=Mechanically polished0.4 cm2 coupons; upward25 mV steps every400 s beginning-300 mV(SCE), PDF p.4; CRA=To measure the pitting potentials, the potential was stepped upwards by 25 mV every 400 s, beginning at -300 mV(SCE).; Same independent pitting protocol; distinct from artificial-pit kinetics.<br>542 / Scan Rate mV/s: paper=25 mV increment /400 s dwell; CRA=0.0625; C1:25/400=0.0625 mV/s nominal stepped rate.<br>542 / Avg Epit mV (SCE): paper={"unit": "mV (SCE)", "value": 50}; CRA=50; Both use mV(SCE). Table3 printed Ep agrees exactly; adjacent Epp is excluded.<br>542: exact; Table1 source composition and Table3 named experimental-alloy row, with the independent coupon protocol, identify the counterpart (PDF pp.2,4,7). | matched |
| obs_003 | loc 0: 100.0 mV (SCE) (transcribed); PDF p. 7 / printed p. 347, Table 3, 304L SS, Ep (mV SCE) | none | none | — | — | unmatched: This Table3 result is for commercial304L SS, distinct from both experimental-alloy Table1 analyses represented by CRA541/542. Its100 mV result does not identify another material by a nearby potential. |

Status counts: matched=2; ambiguous=0; unmatched=1; not_assessed=0.
ambiguous IDs: none.
unmatched IDs: obs_003.
not_assessed IDs: none.

Supported shared-row groups: none.
Unlinked CRA No. in this input: none.

Shared qualifications:

- Table3 (PDF p.7) explicitly reports pitting Ep separately from protection Epp. Pitting was verified microscopically (PDF p.4). No artificial-pit imposed potential, protection potential or modeled Tafel displacement is substituted for Ep.
- C1: potential steps25 mV every400 s give nominal25/400=0.0625 mV/s. This is a stepped test, not a continuous sweep. Test temperature is22+/-1 C; the nominal22 C CRA cell is retained.
- Source Table1 sulfur is&lt;0.005 wt%, whereas CRA stores0.005 as an exact cell. Table1 Fe is balance; no precise source Fe value is invented. Source medium is neutral1 M KCl; neutral does not establish a measured pH exactly7.0.
- The1200 C/24 h anneal sentence explicitly concerns the wires used for artificial pits (PDF p.3); it does not independently establish the same treatment for the mechanically polished pitting coupons. Coupon composition, medium, temperature and stepped protocol suffice for alignment without resolving that CRA heat-field scope.

Visually inspected PDF pages: 1, 2, 3, 4, 7.
Coverage/access: Every supplied observation and CRA row was considered. Every registered anchor page, including secondary locations, was actually viewed. Context pages and enlarged source plots were consulted where needed. This is alignment of the exact supplied registry, not a full-paper census or proof of the presentation selected by the original curators. Inputs are unchanged.

Structural validation: PASS against the bundled schema/model and exact supplied inputs. Scientific fidelity, conversion arithmetic/assumptions, identity and benchmark suitability are not certified. Only supported links enter default joins; shared rows must not be counted as independent benchmark rows without review.
