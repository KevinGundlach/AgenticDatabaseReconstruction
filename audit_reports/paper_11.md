# Audit Report: Citrine Pitting-Potential Records for Reference 11

## Scope

Compared the 12 Reference 11 records (Excel rows 352-363; record numbers 350-361) with [Lizlovs and Bond (1969)](<../papers/11_E. A. Lizlovs, A. P. Bond, J. Electrochem. Soc. 116 (1969)_ p. 574.pdf>) and the [Citrine workbook](../citrine_database/CRA_database_Scientific_Data_Publication_12102020.xlsx). Audit date: 2026-09-04. Workbook evidence: 【CRA_database_Scientific_Data_Publication_12102020.xlsx:Pitting Potential:A352:AM363】

## Executive summary

All 12 Table IV pitting potentials are represented and agree with the paper, including the three right-censored values reported as `>0.80 V`. One composition error was found: the high-Ti alloy is reported as 1.86 wt% Ti in Tables I and IV, but Citrine stores 1.88 wt% Ti. Several unanalysed source fields were filled by assumption, and the generic heat-treatment text lists alternatives without identifying which treatment applies to each row.

| Severity | Finding | Affected records |
|---|---|---:|
| High | Ti is 1.88 wt% in Citrine but 1.86 wt% in the source. | high-Ti alloy |
| Medium | Source `NA`/not-analysed chemistry is represented as zero or copied from a related composition. | several |
| Medium | Multi-option processing text is not record-specific. | all 12 |
| Low | pH 1 is inferred from 0.1 N HCl, not measured. | all 12 |

## Reconciliation and coverage

The source sequence 180, 190, 260, 320, >800, 310, 350, 340, >800, 630, >800, and 620 mV is faithfully reproduced. The 12/12 coverage is complete. The scan-rate field retains the final slow stage but does not fully preserve the paper's staged protocol. Right-censored observations should remain explicitly censored rather than treated as exact 800 mV values.

## Recommended corrections

Correct Ti to 1.86 wt%; preserve source `NA` and inequality qualifiers; make the heat treatment record-specific; label pH as derived; and retain the `>800 mV` censoring semantics.

## Overall assessment

**Potentials: pass. Compositions: one confirmed error plus provenance caveats. Coverage: pass.**
