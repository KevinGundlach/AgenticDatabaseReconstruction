# Observation-to-CRA alignment

Paper: 63_Lu, Y. C., C. R. Clayton, and A. R. Brooks. Corrosion science 29.7 (1989)_ 863-880.pdf; reference 63. Registry: paper_63.json; CSV: pitting_potential_63.csv. Supplied observations=2; CRA rows=2.

These are automated alignment proposals for this exact supplied registry. Unlinked rows are unassigned in this input, not proven absent from the paper. Avg is a database column label, not evidence of a source-reported mean.

| Observation | Registered reading / location | Supported CRA No. | Candidate CRA No. | CRA targets (mV SCE) | Evidence / conversion | Status / notes |
|---|---|---|---|---|---|---|
| obs_001 | loc 0: -50.0 mV (SCE) (transcribed); PDF p. 5 / printed p. 867, Table 2, 0.3 M NaCl (pH 5.4), Epit (mV) | 209 | none | 209 (supported): Avg=-50; Min=; Max= | 209 / Cr: paper=19.2 wt% Cr, Table1, PDF p.3; CRA=19.2; Independent measured alloy identity.<br>209 / Ni: paper=9.0 wt% Ni, Table1; CRA=9.0; Independent measured alloy identity.<br>209 / Test Solution: paper=0.3 M NaCl, pH5.4; aerated in Table2, de-aerated with argon in methods; CRA= deaerated 0.3M NaCl (pH 5.4); Same salt/pH condition; the source atmosphere contradiction and original CRA de-aerated label are retained.<br>209 / pH: paper=5.4, Table2; CRA=5.4; Same source-reported pH; pH9 NaOH adjustment is not molybdate addition.<br>209 / Scan Rate mV/s: paper=1 mV/s, PDF p.3; CRA=1; Same actual anodic sweep rate.<br>209 / Test Method: paper=Cathodic pretreatment-1.150 V(SCE),15 min; then anodic sweep, PDF p.3; CRA=Potentiodynamic Polarization. Before athe test, specimens were cathodically polarized at - 1.150 V(SCE) for 15 min to reduce the polish-formed film.; Same independently specified pretreatment/procedure.<br>209 / Avg Epit mV (SCE): paper={"unit": "mV (SCE)", "value": -50}; CRA=-50; Both source and CRA are mV(SCE); the printed Table2 Epit agrees exactly. Adjacent Ecorr, primary-passivation and transpassive columns are different quantities.<br>209: exact; Table1 alloy analysis and Table2 electrolyte/pH column identify the counterpart independently of potential equality (PDF pp.3,5). The unresolved source atmosphere conflict remains attached. | matched |
| obs_002 | loc 0: 525.0 mV (SCE) (transcribed); PDF p. 5 / printed p. 867, Table 2, 0.3 M NaCl (pH 9.0), Epit (mV) | 210 | none | 210 (supported): Avg=525; Min=; Max= | 210 / Cr: paper=19.2 wt% Cr, Table1, PDF p.3; CRA=19.2; Independent measured alloy identity.<br>210 / Ni: paper=9.0 wt% Ni, Table1; CRA=9.0; Independent measured alloy identity.<br>210 / Test Solution: paper=0.3 M NaCl, pH9; aerated in Table2, de-aerated with argon in methods; CRA=deaerated 0.3M NaCl (pH 9.0); Same salt/pH condition; the source atmosphere contradiction and original CRA de-aerated label are retained.<br>210 / pH: paper=9, Table2; CRA=9.0; Same source-reported pH; pH9 NaOH adjustment is not molybdate addition.<br>210 / Scan Rate mV/s: paper=1 mV/s, PDF p.3; CRA=1; Same actual anodic sweep rate.<br>210 / Test Method: paper=Cathodic pretreatment-1.150 V(SCE),15 min; then anodic sweep, PDF p.3; CRA=Potentiodynamic Polarization. Before athe test, specimens were cathodically polarized at - 1.150 V(SCE) for 15 min to reduce the polish-formed film.; Same independently specified pretreatment/procedure.<br>210 / Avg Epit mV (SCE): paper={"unit": "mV (SCE)", "value": 525}; CRA=525; Both source and CRA are mV(SCE); the printed Table2 Epit agrees exactly. Adjacent Ecorr, primary-passivation and transpassive columns are different quantities.<br>210: exact; Table1 alloy analysis and Table2 electrolyte/pH column identify the counterpart independently of potential equality (PDF pp.3,5). The unresolved source atmosphere conflict remains attached. | matched |

Status counts: matched=2; ambiguous=0; unmatched=0; not_assessed=0.
ambiguous IDs: none.
unmatched IDs: none.
not_assessed IDs: none.

Supported shared-row groups: none.
Unlinked CRA No. in this input: none.

Shared qualifications:

- Table 2 (PDF p.5) labels its solutions aerated, whereas the experimental method uses argon de-aeration and an argon-purged glove box (PDF pp.2-3); this source conflict is retained. It does not remove the independent alloy, electrolyte and pH identities.
- Table 1 gives Cr19.2/Ni9.0 wt%, but C&lt;0.05, N&lt;0.002 and S&lt;0.025 wt% (PDF p.3). CRA stores those limit numbers as exact cells and calculates a precise Fe value; neither the limits nor source Fe balance are asserted to be exact measured compositions here.
- All source potentials are versus SCE. The anodic sweep is1 mV/s after cathodic polarization at-1.150 V(SCE) for15 min (PDF p.3). Source temperature is not independently established as a numerical25 C in these passages. The pH9 NaOH-adjusted NaCl condition is distinct from the Na2MoO4-added solution, whose table entry is transpassive rather than one of these Epit values.

Visually inspected PDF pages: 1, 2, 3, 5.
Coverage/access: Every supplied observation and CRA row was considered. Every registered anchor page, including secondary locations, was actually viewed. Context pages and enlarged source plots were consulted where needed. This is alignment of the exact supplied registry, not a full-paper census or proof of the presentation selected by the original curators. Inputs are unchanged.

Structural validation: PASS against the bundled schema/model and exact supplied inputs. Scientific fidelity, conversion arithmetic/assumptions, identity and benchmark suitability are not certified. Only supported links enter default joins; shared rows must not be counted as independent benchmark rows without review.
