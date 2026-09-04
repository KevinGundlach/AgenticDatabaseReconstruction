# Audit Report: Citrine Pitting-Potential Records for Reference 80

## Scope

Compared 33 records (Excel rows 739-771) with [Frankel et al. (1993)](<../papers/80_G.S. Frankel, R.C. Newman, C.V. Jahnes, M.A. Russak, J Electrochem Soc, 140 (1993) 2192-2197.pdf>). Workbook evidence: 【CRA_database_Scientific_Data_Publication_12102020.xlsx:Pitting Potential:A739:AM771】. Audit date: 2026-09-04.

## Executive summary

The user's spot-check is confirmed. Four Al-Nb, seven Al-Mo, and three Al-Cr records—14 total, Excel rows 739-742, 748-754, and 761-763—use pH 10 data from the authors' earlier study, not experiments conducted under this paper's main protocol. The paper explicitly says the earlier work used pH 10 and 0.2 mV/s; Citrine assigns all 14 to Reference 80 and gives them 1 mV/s. The current paper uses unadjusted, air-exposed 0.1 M NaCl at 1 mV/s.

| Severity | Finding |
|---|---|
| Critical | Fourteen pH-10 records are prior-publication data misattributed to Reference 80. |
| High | Those 14 records have scan rate 1 mV/s but the paper states the earlier study used 0.2 mV/s. |
| High | Fresh, aged, and repassivation series are not structurally distinguished. |
| Low | pH 7 on current-paper rows is an assumption; the source says air-exposed 0.1 M NaCl, not adjusted pH 7. |

The remaining 19 rows are plausible fresh-state values shown in Figures 1-4, but their state/series identity and graphical uncertainty should be explicit. Source compositions are atomic percentages converted to wt% in Citrine.

## Recommended corrections

Reassign the 14 pH-10 observations to their actual cited paper (or mark them secondary literature), change their scan rate to 0.2 mV/s, remove assumed pH 7 from current tests, and add fields distinguishing fresh/aged pitting and repassivation potential.

## Overall assessment

**The reported values are broadly traceable, but provenance is a major fail; the user's 14-record finding is confirmed.**
