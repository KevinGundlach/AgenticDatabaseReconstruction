# Observation-to-CRA alignment

Paper: 29_A.A. Rodriguez, J.H. Tylczak, M.C. Gao, P.D. Jablonski, M. Detrois, M. Ziomek-Moroz, J.A. Hawk, Advances in Materials Science and Engineering, 2018 (2018) 11.pdf; reference 29. Registry: paper_29.json; CSV: pitting_potential_29.csv. Supplied observations=2; CRA rows=2.

These are automated alignment proposals for this exact supplied registry. Unlinked rows are unassigned in this input, not proven absent from the paper. Avg is a database column label, not evidence of a source-reported mean.

| Observation | Registered reading / location | Supported CRA No. | Candidate CRA No. | CRA targets (mV SCE) | Evidence / conversion | Status / notes |
|---|---|---|---|---|---|---|
| obs_001 | loc 0: 0.32 V (SCE) (transcribed); PDF p. 4 / printed p. 4, 3.2. Electrochemical Testing, breakdown potential of 0.32 V<br>loc 1: 0.32 V (SCE) (transcribed); PDF p. 5 / printed p. 5, 3.2. Electrochemical Testing, and its breakdown potential<br>loc 2: 0.56 V (SHE) (transcribed); PDF p. 5 / printed p. 5, 3.2. Electrochemical Testing, (0.56 V versus SHE).<br>loc 3: 0.32 V (SCE) (transcribed); PDF p. 7 / printed p. 7, Table 2, A35, Ebre (V versus SCE)<br>loc 4: 0.32 V (SCE) (transcribed); PDF p. 9 / printed p. 9, 4. Conclusions, Ebre of 0.32 V versus SCE<br>loc 5: 0.56 V (SHE) (transcribed); PDF p. 9 / printed p. 9, 4. Conclusions, (0.56 V versus SHE). | 600 | none | 600 (supported): Avg=320; Min=; Max= | 600 / Fe: paper=Table 1 A35: 19.98 wt.% Fe; CRA=19.98; Direct source wt.% matches; distinguishes A35 from Mo-bearing A36 (PDF p.3).<br>600 / Cr: paper=Table 1 A35: 18.4 wt.% Cr; CRA=18.4; Direct source wt.% matches; distinguishes A35 from Mo-bearing A36 (PDF p.3).<br>600 / Ni: paper=Table 1 A35: 40.84 wt.% Ni; CRA=40.84; Direct source wt.% matches; distinguishes A35 from Mo-bearing A36 (PDF p.3).<br>600 / Co: paper=Table 1 A35: 20.67 wt.% Co; CRA=20.67; Direct source wt.% matches; distinguishes A35 from Mo-bearing A36 (PDF p.3).<br>600 / Mo: paper=A35 Table 1 Mo cell is an em dash; base formula CoCrFeNi2; CRA=0.0; Source base alloy has no stated Mo addition; distinguishes CRA 600 from 601 (7.64 wt.% Mo), without interpreting arbitrary missing cells as zero.<br>600 / Test Solution: paper=3.5 wt.% NaCl, nondeaerated; CRA=3.5wt% NaCl; Exact electrolyte (PDF pp.2-3).<br>600 / Test Temp C: paper=25 C; CRA=25.0; Exact test temperature (PDF p.3 and Table 2).<br>600 / Scan Rate mV/s: paper=1 mV/s; CRA=1; Exact sweep rate (PDF p.4).<br>600 / pH: paper=Initial pH 8.4; final pH for A35 10.9; CRA=7.0; Disagrees with CRA pH 7.0; source value retained.<br>600 / Avg Epit mV (SCE): paper={"unit": "V (SCE)", "value": 0.32}; CRA=320; Primary Table 2 and registered text/conclusion: 0.32 V(SCE)*1000=320 mV(SCE), exact. Secondary 0.56 V(SHE) is explicitly presented by the source as the same endpoint; source rounded equivalence (0.56-0.24)*1000=320 mV(SCE). This is source-supplied equivalence, not a fitted external calibration.<br>600: exact; A35 measured chemistry and 25 C nondeaerated NaCl test identify CRA 600 independently (PDF pp.2-4, Table 1). All six registered locations support the same source-described endpoint; no extra replicate is inferred. Primary Table 2 and repeated SCE values agree; secondary SHE equivalence, metastable-pit meaning and pH conflict retained. | matched |
| obs_002 | loc 1: 0.27 V (SCE) (transcribed); PDF p. 7 / printed p. 7, Table 2, SS316, Ebre (V versus SCE) | none | none | — | — | unmatched: SS316/316L comparator in text/Table 2 has no counterpart: supplied CRA rows are A35 and Mo-bearing A36. Source naming inconsistency retained; origin category is not the exclusion reason. |

Status counts: matched=1; ambiguous=0; unmatched=1; not_assessed=0.
ambiguous IDs: none.
unmatched IDs: obs_002.
not_assessed IDs: none.

Supported shared-row groups: none.
Unlinked CRA No. in this input: 601.

Shared qualifications:

- A35 Ebre marks pseudopassive breakdown and metastable-pit initiation, not necessarily a stable-pitting threshold (PDF pp.4-5). The registered endpoint is retained with this qualification.
- PDF pp.5,9 explicitly give the same A35 Ebre as 0.32 V vs SCE and 0.56 V vs SHE; their source-supplied rounded equivalence is a 0.24 V offset. Primary SCE value is unchanged, and secondary SHE readings remain in their original scale.
- PDF pp.4-5 give initial pH 8.4 and final pH 10.9 for A35; CRA pH is 7.0. This context conflict does not change the identity.
- obs_002 retains the source SS316/316L naming inconsistency; it has no supplied CRA material counterpart.

Visually inspected PDF pages: 2, 3, 4, 5, 7, 9.
Coverage/access: All two supplied observations and both CSV records considered. Initial Poppler rendering of the long original path failed with I/O Error: Couldn't open file. A short-named byte-identical copy (SHA-256 verified) rendered successfully. All registered anchors (PDF pp.4,5,7,9) and composition/procedure context (pp.2-3) actually viewed. CRA 601 remains unlinked relative to this registry; no new A36 observation was added.

Structural validation: PASS against the bundled schema/model and exact supplied inputs. Scientific fidelity, conversion arithmetic/assumptions, identity and benchmark suitability are not certified. Only supported links enter default joins; shared rows must not be counted as independent benchmark rows without review.
