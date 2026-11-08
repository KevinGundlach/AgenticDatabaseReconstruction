# Observation-to-CRA alignment

Paper: 25_Hong-lei Wang, Tai-Xiu Gao, Jia-zheng Niu, Pei-jian Shi, Jing Xu, and Yan Wang. International Journal of Minerals, Metallury, and Materials, 23 (1) (2016), 77-82.pdf; reference 25. Registry: paper_25.json; CSV: pitting_potential_25.csv. Supplied observations=1; CRA rows=1.

These are automated alignment proposals for this exact supplied registry. Unlinked rows are unassigned in this input, not proven absent from the paper. Avg is a database column label, not evidence of a source-reported mean.

| Observation | Registered reading / location | Supported CRA No. | Candidate CRA No. | CRA targets (mV SCE) | Evidence / conversion | Status / notes |
|---|---|---|---|---|---|---|
| obs_001 | loc 0: -0.56 V (Ag/AgCl) (transcribed); PDF p. 4 / printed p. 80, 3.4. Corrosion resistance of the as-sintered FeSiBAlNi HEA, and −0.56 V vs. Ag/AgCl,<br>loc 1: -0.68 V (Ag/AgCl) (digitized); PDF p. 4 / printed p. 80, Fig. 5, 520°C; dashed black curve, labeled Epit vertical guide, SPS temperature=520.0 °C, annotation=Epit | 592 | none | 592 (supported): Avg=-602; Min=; Max= | 592 / Fe: paper=Nominal equiatomic FeSiBAlNi; atomic/molar coefficient Fe=1; CRA=31.0; C1: 100*1*55.845/180.415000 = 30.9536 wt.%; compare with original CRA wt.% cell.<br>592 / Si: paper=Nominal equiatomic FeSiBAlNi; atomic/molar coefficient Si=1; CRA=16.0; C1: 100*1*28.085/180.415000 = 15.5669 wt.%; compare with original CRA wt.% cell.<br>592 / B: paper=Nominal equiatomic FeSiBAlNi; atomic/molar coefficient B=1; CRA=6.0; C1: 100*1*10.81/180.415000 = 5.9917 wt.%; compare with original CRA wt.% cell.<br>592 / Al: paper=Nominal equiatomic FeSiBAlNi; atomic/molar coefficient Al=1; CRA=14.0; C1: 100*1*26.982/180.415000 = 14.9555 wt.%; compare with original CRA wt.% cell.<br>592 / Ni: paper=Nominal equiatomic FeSiBAlNi; atomic/molar coefficient Ni=1; CRA=33.0; C1: 100*1*58.693/180.415000 = 32.5322 wt.%; compare with original CRA wt.% cell.<br>592 / Heat treatment: paper=240 h mechanical alloying; SPS 520 C for 10 min, 40 C/min, 80 MPa in Ar; free cooling; CRA=as-milled powders consolidated by SPS @520C for 10 min, heating rate 40C/min, 80MPa in Ar, cooled freely; Distinctive processing sequence agrees with CRA; p.78 methods.<br>592 / Test Solution: paper=Artificial sea salt : distilled water = 1:30 by mass; CRA=Sea Water 1:30; Corresponds to CRA Sea Water 1:30 label; it does not establish the CRA chloride molarity.<br>592 / Scan Rate mV/s: paper=3 mV/s; CRA=3; Exact sweep rate (PDF p.2).<br>592 / Avg Epit mV (SCE): paper=Text: -0.56 V vs Ag/AgCl; secondary Fig.5 guide: approximately -0.68 V vs Ag/AgCl; CRA=-602; Scaling alone gives -560 and approximately -680 mV vs Ag/AgCl; neither is yet an SCE value. Filling solution and reference temperature are unspecified, so -602 mV(SCE) cannot be defensibly compared numerically.<br>592: not_comparable; Equiatomic alloy family plus the exact 520 C SPS sequence, 1:30 artificial-sea-salt medium and 3 mV/s scan identify CRA 592 (PDF pp.1-2,4). Calculated nominal Al is about 15 wt.% versus CRA 14 wt.%; this discrepancy is retained. The two registered readings disagree; neither is substituted or corrected. The 1080 C material is not this registered outcome. | matched |

Status counts: matched=1; ambiguous=0; unmatched=0; not_assessed=0.
ambiguous IDs: none.
unmatched IDs: none.
not_assessed IDs: none.

Supported shared-row groups: none.
Unlinked CRA No. in this input: none.

Shared qualifications:

- C1: Nominal atomic/molar coefficients are converted only for chemistry comparison: wt.%_i = 100*n_i*M_i / sum(n_j*M_j), over the complete stated formula. CIAAW abridged standard atomic weights 2024: Al 26.982, Co 58.933, Cr 51.996, Fe 55.845, Ni 58.693, Si 28.085, B 10.81 (https://ciaaw.org/abridged-atomic-weights.htm). Calculated nominal wt.% is not a measured analysis.
- The registered primary text reports -0.56 V vs Ag/AgCl; the registered Fig.5 Epit guide reads approximately -0.68 V on the same scale, a 120 mV internal source disagreement. Both locations are retained.
- Methods (PDF p.2) identify Ag/AgCl but omit its filling solution and reference-electrode temperature. No Ag/AgCl-to-SCE offset is fitted to CRA -602 mV. Numerical comparison is not_comparable.
- The solution is artificial sea salt dissolved in distilled water at a 1:30 mass ratio, not an established 1:30 seawater dilution. No sea-salt recipe, chloride molarity or pH is supplied for conversion.

Visually inspected PDF pages: 1, 2, 4.
Coverage/access: All supplied observations/CSV records considered. Initial Poppler rendering of the long original path failed with I/O Error: Couldn't open file. Rendering a short-named byte-identical copy (SHA-256 verified) succeeded; PDF pp.1,2,4 actually viewed, including both registered anchors. Fingerprint remains that of the original PDF.

Structural validation: PASS against the bundled schema/model and exact supplied inputs. Scientific fidelity, conversion arithmetic/assumptions, identity and benchmark suitability are not certified. Only supported links enter default joins; shared rows must not be counted as independent benchmark rows without review.
