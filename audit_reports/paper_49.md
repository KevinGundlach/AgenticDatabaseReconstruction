# Audit Report: Citrine Pitting-Potential Records for Reference 49

## Scope

Audited 65 records (Excel rows 3-67) against [Malik et al. (1995)](<../papers/49_Malik, A. U., et al. Corrosion science 37.10 (1995)_ 1521-1535.pdf>). Workbook evidence: 【CRA_database_Scientific_Data_Publication_12102020.xlsx:Pitting Potential:A3:AM67】. Audit date: 2026-09-04.

## Executive summary

The 65 Table 5 pitting potentials are complete and correctly transcribed. The chemistry contains a systematic tenfold sulfur error, confirming the user's spot check. Citrine also duplicates each source `Nb+Ta` combined value into both Nb and Ta, thereby double-counting it, and uses 0.546 M chloride for natural seawater even though Table 2's 24,090 mg/L chloride corresponds to about 0.679 M.

| Severity | Finding | Affected records |
|---|---|---:|
| Critical | Every sulfur value is 10× the source Table 1 value. | all records with S |
| Critical | Combined `Nb+Ta` is copied independently into both Nb and Ta. | Nb/Ta-bearing alloys |
| High | Natural-seawater chloride is 0.546 M instead of about 0.679 M from the reported analysis. | seawater rows |

Source pH 8.2 for seawater and 7.8 for low-NaCl media, and 0.1 mV/s scan, are supported.

## Recommended corrections

Divide sulfur entries by ten; preserve `Nb+Ta` as combined/ambiguous instead of duplicating it; correct seawater chloride from the source analysis; and document any chemistry normalization.

## Overall assessment

**Potentials/coverage: pass. Composition and seawater chemistry: fail.**
