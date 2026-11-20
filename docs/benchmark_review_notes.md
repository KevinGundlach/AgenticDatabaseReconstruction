# Benchmark review notes — non-blind analysis only

Last consolidated: **2026-11-19**.

**This file contains CRA reference answers and paper-specific analyses. Do not read it in a blind registration or enrichment context.** It is for development, comparison, thesis discussion and review. The startup guide is [AGENTS.md](../AGENTS.md).

This preserves findings from earlier chats, not an independent re-extraction of the papers. Corpus counts below were recomputed during this documentation update. Detailed audits are historical findings; where noted, the PDF was visually checked in earlier work. Matching-agent statements remain agent judgments unless independently checked. Reopen the cited sources before making a strong scientific claim or changing data. Do not silently correct canonical outputs from this document.

## Where to resume

- Current code and comparison policies: [benchmark.py](../benchmark.py), [benchmark plots](../reporting/benchmark_plots.py), and the API summary in `AGENTS.md`.
- Source literature: [papers/](../papers/), with reference-prefixed PDF names. PDF page numbers below are one-based; printed page labels can differ.
- Original CRA: [pitting_potential_complete.csv](../citrine_database/pitting_potential_complete.csv), original workbook and per-reference CSVs in [citrine_database/](../citrine_database/). `No.` is the identifier; never use CSV line position.
- Exact saved evidence: [observation_registry/](../observation_registry/), [matched_observations/](../matched_observations/), [enriched_observations/](../enriched_observations/), each with `paper_<reference>.json` and companion reports. Compare hashes before joining different runs.
- Current plots: [plots/](../plots/). Rounding-only figures are `gap_histogram.png`, `gap_histogram_2.png`, `gaps_by_field.png`; optional 1% figures are `gap_histogram_3.png`, `gaps_by_field_2.png`.

The latest user work was an advisor-status email discussing extraction, matching, benchmark gaps and hurdles. Diagrams are in [output/pdf/](../output/pdf/); `three_agent_workflow_simplified.pdf` is the preferred overview. No agent sent that email.

## Current numerical baseline

Recomputed read-only on 2026-11-19 using current loaders and default composition policies:

- 77 enriched documents, **2,176** enriched records; 61 alignment documents.
- **850** observations have supported links, producing **873** links to **667** distinct CRA identifiers out of **810** original rows.
- **22** observations link to multiple CRA rows; **45** CRA rows have multiple observations. Strict one-to-one filtering leaves **577** pairs.
- Rounding-only: **2,888** gaps, **4** zero-gap records, maximum **14**; pitting **266**, pH **312**.
- Optional CRA-relative 1%: **2,643** gaps, **11** zero-gap records, maximum **14**; pitting **137**, pH **305**.
- All-field reasons change from 2,300 missing / 135 conversion / 453 mismatch to 2,300 / 135 / 208. Tolerance cannot repair missing values or unsupported conversions.

Do not describe 2,176 records as 2,176 independently verified unique experiments. Registration intentionally retains uncertain duplicates, different methods/replicates and some cited/derived outcomes. CRA has its own scope and duplicate/summary relationships. The 577-pair cohort excludes ambiguity in either direction; it is not a random sample of all papers or all CRA records.

### Pitting-potential gaps

Earlier decomposition of the same 577-pair cohort:

| Outcome | Rounding-only | CRA-relative 1% |
|---|---:|---:|
| Numerical agreement | 245 | 374 |
| Numerical mismatch | 225 | 96 |
| Conversion unavailable | 41 | 41 |
| Unscored | 66 | 66 |

Of the 225 rounding-only mismatches, 205 primary readings were digitized and 20 transcribed. Of the remaining 96 at 1%, **84 were digitized, 12 transcribed**. Among those 84 digitized mismatches, 29 differed by at most 5 mV and 53 by at most 10 mV. These are compatible with graphical-resolution issues in many cases, not proof that every discrepancy is harmless.

The matching agent labeled 76 of those 84 digitized links `within_precision` and 8 `discrepant`; among 12 transcribed links, 8 and 4 respectively. Its precision judgments are not independently validated tolerances. Near zero, 1% can be less than 1 mV. Relative differences in electrode potential also depend on the reference zero, so 1% is an exploratory comparison, not a universal scientific rule.

The **41 conversion failures** occurred in papers 1 (17), 12 (5), 25 (1), 36 (6), and 66 (12). All their primary locations were included among the matching links' supporting locations. The matching assessments were 21 `within_precision`, 19 `not_comparable`, 1 `discrepant`. A matching status is an identity judgment, not an assertion that the standalone conversion helper has enough metadata.

### pH: more than missing seawater assumptions

Earlier audit of the 312 rounding-only pH gaps:

- **286** lacked a reported/calculable value, **22** disagreed with an explicitly extracted pH, and **4** were small derived-value differences (`0.3010299957...` versus CRA 0.3).
- Of the 286 missing estimates, **237** were blocked solely by an empty solvent string even though the recipe otherwise fell within the restricted helper. An in-memory water assumption would make 231 agree and leave 6 disagreeing. This was a sensitivity analysis, **not an adopted policy or data correction**.
- The remaining 49 recipes were unsupported even with water supplied: e.g. sulfuric acid, additives, chloride-only representations or seawater. Only **one** seawater-related pH gap occurred in this one-to-one cohort.
- **249 of the 312** gap targets were CRA pH 7. Elsewhere, 204 reported values and 30 calculated values agreed; 31 CRA pH targets were unavailable and skipped.

The helper requires explicit recognized water and assumes an ideal supported solution at 25 °C. Its inability to calculate is not necessarily a failure to read the paper. Conversely, a default-looking CRA pH does not establish how the curators obtained it. Avoid saying all pH gaps are external assumptions or all are extraction errors.

### Alloy conversion applicability

Earlier strict-conversion diagnostic across 2,176 records: **440** passed; the first blocking reasons were unsupported unit 702, missing amount 563, empty composition 77, missing central value 184, and total not 100% 210.

Across the 850 observations with supported CRA links: **290** passed; unsupported unit 305, missing amount 146, missing central value 80, total not 100% 29. These counts report the first exception only. Strict conversion applicability is not extraction accuracy. The benchmark now uses the permissive converter, retaining usable weight amounts and leaving unknown listed amounts as `None`.

Bare `%` often numerically agrees with CRA when treated as wt%, motivating an **explicit sensitivity option**, not proof of basis or of the curators' reasoning. Do not call ambiguous units nonsense, discard whole experiments merely for one unknown element, assume all missing amounts are trace quantities, or infer an unstated balance element. Atomic-percent and ratio conversion can make all converted amounts depend on one missing constituent; a balance calculation can similarly propagate another element's error. The benchmark's default leaves explicit balance unscored to avoid double attribution.

## Reference metadata can be known but lost from the anchor: paper 12

This is the clearest pipeline-design limitation found recently. Inspect [registry](../observation_registry/paper_12.json), [matching](../matched_observations/paper_12.json), and [enrichment](../enriched_observations/paper_12.json) together only in a non-blind review.

- `obs_011` has a plot location reading **1.2 V (normal hydrogen electrode)** and a table location reading **1.2 Volts**. The table is primary (`primary_location: 1`), so the observation-level unit is the less informative `Volts`.
- The enrichment skill copies that whole primary measurement unchanged, as required. It did not add the reference clarification to that record's notes/procedure. This does **not** prove what the model noticed internally, and is not simply a new numerical extraction error.
- Earlier visual inspection: PDF p. 3 / printed 168t discusses 1.5 V “relative to normal hydrogen electrode” in the Figure 3 breakdown context; Table 3 on PDF p. 6 / printed 171t says only “Breakdown Potential, Volts.” Applying the former to the latter is a contextual association, not an explicit electrode statement in every cell or proof of a particular physical reference assembly.
- Matching used an NHE-to-SCE offset of **−244 mV**: `obs_011` → CRA **373**, 1.2 V → **956 mV (SCE)**. Likewise `obs_027` → **384**, 0.659 V → **415 mV (SCE)**.
- Among 32 enriched records, 22 carry NHE units, 8 `Volts`, 2 `v`. The converter sees the anchored measurement only and deliberately refuses bare `Volts`/`v`; it cannot consult secondary locations or matching prose.

Possible future fix: keep the raw anchored reading and store a separate, paper-supported reference clarification/resolved comparison view. This would need an agreed contract and validation; **it is not implemented**. Do not change canonical units or copy matching knowledge into a supposedly blind enrichment run. The helper's fixed 241 mV SCE convention also differs from the 244 mV used in some matching calculations; document the convention rather than fitting it to each CRA answer.

### Other electrode-conversion examples

- **Paper 1:** conditional hydrogen-scale assumptions produced 16 `within_precision` and one `discrepant` conversion-blocked links. `obs_032` → CRA 332: 0.38 V on the hydrogen scale becomes 139 mV under −241, versus CRA 137; composition/electrolyte/temperature and steady-state criterion support identity separately. `obs_039` → 339: primary 0.78 `v` would give 539 versus 558, while a secondary ~0.80 reading gives ~559. Calibration and source conflicts cannot be erased by selecting the closest number.
- **Paper 25:** `obs_001` → CRA 592 is identified by nominal equiatomic FeSiBAlNi, SPS preparation, solution and rate. Primary −0.56 V (Ag/AgCl), secondary ~−0.68 V, CRA −602 mV (SCE). Filling solution/temperature are insufficiently specified for an unconditional conversion.
- **Paper 36:** six Table 2 stepped readings have Ag/AgCl saturated units and tests at 80 ± 2 °C. For `obs_045` → CRA 99, 500 versus 455 mV resembles a −45 mV offset (199 − 244 at a selected room-temperature convention), but the hot-reference calibration is not established. Do not treat numerical reproduction as proof.
- **Paper 66:** twelve readings use `mV_H`. `obs_002` → CRA 282: 750 − 241 = 509 versus 505.82578; `obs_004` → 288: 1100 − 241 = 859 versus 852.86411. Figure series, heat state, chemistry/Mn and chloride provide identity evidence. The unspecified hydrogen scale still prevents unconditional conversion.

## Source scope, repeated presentations and contradictions

### Papers 3, 9 and 49

Current saved counts were rechecked for this update: paper 3 has **170** observations versus 54 CRA rows; paper 9 **124** versus 39; paper 49 **110** versus 65. Older chat references to 115 observations for paper 49 describe an earlier run, not the current registry.

- **Paper 3:** several methods, cited/interpolated values, replicates and possible repeated presentations explain why counting registry entries is not directly comparable to counting CRA rows. A plot against Cr + Mo does not uniquely specify Cr and Mo separately. Empty `failure_notes` means no unresolved recovery problem, not proven independence or benchmark readiness. Do not accuse the original curators of laziness from the count difference.
- **Paper 9:** Figure 9 may use the potential at 10 µA/cm² where definite pitting potentials were not evident; affected individual points are not identified. This is a source qualification in `result_note`, not proof that every point is a proxy and not automatically a recovery failure. `obs_109` → CRA 505 has registry +60 mV while a prior visual check found ~+20 and CRA +18.09: likely registry reading error, not a reason to revise the anchor silently. `obs_098` → CRA 514 differs by only 1.27 mV (−55 vs −53.73), but fails a 1% allowance of 0.5373 mV.
- **Paper 49:** Table 5 (PDF p. 7) lists chloride columns 300/500/1000/5000 ppm, while Figure 5's log axis 2.5/3/3.5/4 corresponds to ~316/1000/3162/10000. Establishing table/plot correspondence is not a simple equality check. CRA labels concentrations as ppm NaCl while the source indicates ppm Cl−, a chemically meaningful distinction.
- For **17-4PH** in paper 49, Table 5 literally reports **1516 mV** in seawater, while Figure 2 annotates **94** and Figure 6 is around **160**. These are source conflicts; do not silently repair digits or force consolidation. Other issues include SMO 254 Table 8 PREN 43.5 versus a Figure 6 label near PREN 38/~720, and duplex 2205 table 629 versus Figure 2 ~826/Figure 6 ~630. `obs_110`'s 44653 label has an unresolved relation to Monit 44635/SMO 254. Current matching statuses were 65 matched, 31 ambiguous, 14 unmatched; they are not a scientific resolution of those conflicts.

### Other checks worth retaining

- **Paper 44:** a prior visual check of PDF p. 80 / printed 59 described a “neutral” 0.5 M NaCl solution, with tests at 45/60/75/90 °C. Neutral is not necessarily a reported numerical pH 7, particularly across temperatures. This paper contributed 91 default one-to-one pH gaps. `obs_001` → CRA 602, 260 versus 262.1 mV, is a small graphical difference. `obs_029` → 629, 580 versus 496.8, and `obs_031` → 631, 500 versus 580.4, were flagged as likely registry point swaps.
- **Paper 46:** visually checked PDF p. 2 / printed 776 explicitly reports final **pH 6.3** for 1 M NaCl in distilled water at 25 °C. Eight one-to-one CRA targets are 7 while enrichment retains 6.3. Here the source supports the extracted value over the CRA comparator.
- **Paper 80:** a prior visual check distinguished cited fresh results at pH 10 in NaOH / 0.2 mV/s from current aged-material tests in stagnant-air 0.1 M NaCl / 1 mV/s. Some CRA fresh records have pH 7 versus enrichment 10. Scope of shared methods and cited results matters; do not transfer one setup to all figures.
- **Paper 22:** printed Table 4 potentials 0.14/0.18 V (SCE) appear swapped against CRA 591 = 180 and 590 = 140 mV when identity is determined from heat state. Choosing the closest potential would conceal the discrepancy.
- **Paper 27:** `obs_007` → CRA 596 reports 246 mV (Ag/AgCl, 3.5 M KCl), giving 210 mV (SCE) under the current helper, while CRA stores 246. This suggests an unconverted number, conditional on the electrode interpretation.
- **Paper 55:** `obs_001` → CRA 774 reports −0.701 ± 0.016 V (SCE) versus CRA −550 mV. A large source/target disagreement cannot be justified by an arbitrary reference offset; uncertainty endpoints are not automatically population extrema.
- **Paper 67:** nominal Fe68Al28Cr4 at% appears as 68/28/4 in CRA weight columns; conversion gives approximately 79.7628/15.8686/4.36855 wt%. Several transcribed SHE potentials differ by 3 mV between −241 and a −244 convention compatible with CRA. Compatibility does not prove the curators' chosen constant.
- **Paper 6:** prior visual checks of Tables I/IV support Cr 18.45 and Ti 0.47 for records corresponding to CRA 458/460, versus CRA Cr 16.45 and Ti 0. A matching evidence passage itself has an 18.15 typo: generated rationale is not ground truth either.
- **Paper 56:** Al90Fe5Gd5 at% was retained as 90/5/5 in CRA weight columns (CRA 707); weight conversion is approximately 69.5043/7.9919/22.5038. The summary observation and individual plotted distribution members must not be treated as independent disagreements with one database mean.

## Many-to-many assignments and what enrichment can clarify

### Paper 71: two CRA groups from the same paper

See [matching](../matched_observations/paper_71.json) and [enrichment](../enriched_observations/paper_71.json). The two groups of CRA rows are **not different references**.

- Nineteen odd-numbered plain-pitting observations (`obs_001` through `obs_037`) link to paired CRA groups **69–87** and **253–271**. Source Table II also has crevice results represented by the even IDs; do not merge plain and crevice tests.
- `obs_001` → CRA **69 and 253** has pH **7.68 versus 8.3**. The paper's relevant test is aerated 0.6 M NaCl + 0.1 M NaHCO3, with no recovered numerical bulk pH. A different acidified immersion test at pH 2 must not be transferred to it.
- Earlier workbook inspection confirmed the two pH cells (AF71 and AF255) are hardcoded values, with no formulas/comments explaining them. The disagreement is not introduced by CSV export. An 8.3 bicarbonate convention is plausible, not proven; 7.68's provenance remains unresolved.
- The paired heat-treatment texts describe the same casting/hot-rolling / 20 mm bars / 1100 °C for 30 min / still-air sequence, with extra manufacturing detail in one. Different prose does not establish different material states.
- Steel 6 has Cr 16.66 in the source, versus CRA 74 = 16.86 and CRA 258 = 16.66. Duplicate database rows can disagree internally.

### Broader audit

- Paper 73 links `obs_001` → 88/543/546, `obs_004` → 89/544, `obs_005` → 90/545; repeated CRA entries appear to explain these groups.
- Of the 45 shared CRA identifiers, papers 37/6/41/56 account for 16/9/6/6; papers 3 and 8 have two each; papers 1/2/39/67 one each. Earlier context comparison found 36 groups with exactly the same enriched context and 7 mainly differing in procedure annotations. Equality of extracted context supports review but does not prove physical identity.
- **Paper 1:** `obs_028` (Figure 5, H. Feller series near 14% Ni) and `obs_033` (Figure 6, lab alloy 13% Ni) both link to CRA 333. The latter appears the clearer counterpart; the former is a questionable additional assignment, not conclusively disproven.
- **Paper 39:** Figure 5's NaCl activity 0.7 corresponds to 1 M on its upper concentration axis. Do not read an activity coordinate as 0.7 M.
- **Paper 56:** summary `obs_009` and individual distribution readings `obs_088`–`obs_103` share CRA 707. Individual readings are not interchangeable with the database summary. Overlapping markers and caption/geometry conflicts also caused enrichment flags.
- **Paper 67:** two FA72C presentations (520/480 mV SHE) share CRA 551 with the same context. Selecting CRA 555 solely for potential proximity would change identity without support.

The present plots deliberately leave all such groups out. A future audit may classify duplicate database rows, repeated presentations, summary/member relationships and actual questionable assignments separately. Do not count all joined links as independent samples or use enriched-context agreement as automatic ground truth.

## Why several CRA fields are deferred

- **Scan rate:** tests may include a sweep, staircase, long hold, scratch or different rates in different voltage regions. A potential step is not a sweep rate; a post-initiation hold need not determine the reported pitting threshold. CRA's observed inventory included 136 missing, 18 `steady state`, and 10 paper-65 entries `20mV steps by manual increament`. A 50 mV / 5 min staircase has a nominal rate of ~0.1667 mV/s but also involved 12–15 h holds; replacing the whole procedure with that number loses meaning. No universal curation rule was established.
- **Test method:** one record may mention several tests but one stage determines the pitting outcome. A small canonical category can be useful if that stage is identifiable, with `ambiguous`/`unknown` available. This is what the current parser estimates; it does not replace the full procedure or establish comparability of all reported thresholds.
- **Microstructure:** text mixes phase identities/fractions, FCC/BCC structure, amorphous/crystalline state, grain size, precipitates/inclusions and generic descriptions. Several labels can apply simultaneously. FCC is not automatically synonymous with austenitic steel. A single forced categorical value can lose scientifically relevant distinctions.
- **Heat treatment:** often reducible to temperature + duration + cooling, but fabrication, atmosphere, multiple cycles, alternatives and relative references to earlier treatments complicate parsing. The exploratory audit of 810 rows classified 65 as one simple cycle, 22 plus atmosphere, 94 plus fabrication, 32 requiring relative context, 165 multi-stage/alternative, 8 other complex, 48 sparse and 376 missing (311 NA, 65 None). These are descriptive audit categories, not an automated scientific ontology. Missing description does not prove untreated material. Counting 181 simple final cycles by ignoring atmosphere/fabrication is a policy choice, not lossless normalization.
- **Comments:** potentially valuable context with no agreed atomic comparison representation. It is not currently scored.

### Related work and ontology direction

[Sasidhar 2022](<../../2022 - Sasidhar.pdf>) Methods p. 7 describes eight microstructure categories encoded as positive integers. The colleague described the categorization as manual and interpretive; do not assume raw CRA prose maps cleanly into that taxonomy. The same page describes composition imputation from commercial grades, average impurity levels and zeros for other missing elements. This applies to that modified dataset, not proof that original CRA curators made each such assumption.

[Sasidhar 2023](<../../2023 - Sasidhar.pdf>) p. 2 treats heat treatment, test method, comments and scan rate as text and uses a 769-row modified dataset rather than the original 810. Keep the compatible CSV distinct from the original benchmark.

The predecessor OntologyRefiner is described in the [lab rotation report](<../../Lab Rotation Writeup/Lab Rotation II Report.pdf>) and [older repository](../../OntologyRefiner/). Its fixed base-material → conditioned-material → experiment hierarchy struggled with multistep preparation and attaching discovered attributes to specific process steps. There was also a tension between broad paragraph extraction and learning fine-grained attributes. Reuse is authorized, but it remains separate from this active pipeline.

Possible thesis narrative: first demonstrate a transparent disagreement/coverage benchmark for the simpler fields, then discuss richer structure for these text fields using the predecessor as a separate ontology chapter. Any automated prompt-refinement experiment should reserve whole papers as held-out tests before refinement. Neither that optimizer nor a new ontology learner has been implemented here.

## Open questions, not settled conclusions

- Which potential discrepancies are point-reading mistakes, tolerable digitization, reference conventions, source contradictions or CRA transcription errors? Keep reason categories and supporting locations.
- Should a future comparison representation allow paper-supported reference clarifications while preserving raw anchored measurements? Decide explicitly before changing schemas/contracts.
- Would an explicit water/ideal-solution estimation policy be defensible for a separate sensitivity analysis? Do not silently turn a plausible solvent into reported evidence.
- Which ambiguous-percent assumptions are defensible from the paper, and which merely reproduce CRA's numbers? Matching agreement cannot prove a basis.
- How should summaries, replicates and duplicate CRA entries contribute to evaluation without double-counting? Continue reporting the strict one-to-one baseline alongside any expanded analysis.
- If prompts are improved from gap audits, how will paper-level holdout, rerun lineage and attribution of improvements be preserved?

These are research options. The user's priority is narrow, inspectable progress with simple Python, not a generic conversion/ontology framework or automatic corpus regeneration.
