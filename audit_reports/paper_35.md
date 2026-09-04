# Audit Report: Citrine Pitting-Potential Records for Reference 35

## Scope

Compared two records (Excel rows 307-308) with [Olefjord and Wegrelius (1996)](<../papers/35_I. Olefjord, L. Wegrelius, Corros. Sci. 38 (1996)_ p. 1203.pdf>). Workbook evidence: 【CRA_database_Scientific_Data_Publication_12102020.xlsx:Pitting Potential:A307:AM308】. Audit date: 2026-09-04.

## Finding

The paper states that the two 6% Mo steels do not pit in deaerated 0.1 M HCl + 0.4 M NaCl; passivity persists to transpassive dissolution. Citrine nevertheless stores 841.509 mV as Epit for both. This is a false endpoint assignment.

## Recommended correction

Remove the two numeric Epit records or replace them with explicitly censored `no pitting before transpassivity` observations. Mark pH 1 as derived if retained in another endpoint table.

## Overall assessment

**Fail—transpassive/no-pitting behavior is mislabeled as Epit.**
