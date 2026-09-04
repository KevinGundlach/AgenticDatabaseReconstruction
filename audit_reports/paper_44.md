# Audit Report: Citrine Pitting-Potential Records for Reference 44

## Scope

Reviewed 92 records (Excel rows 600-691) against [Wong (2009 dissertation)](<../papers/44_Wong, Fariaty. Diss. The Ohio State University, 2009.pdf>). Workbook evidence: 【CRA_database_Scientific_Data_Publication_12102020.xlsx:Pitting Potential:A600:AM691】. Audit date: 2026-09-04.

## Findings

The 23-composition × four-temperature matrix from the principal figure is substantially complete and spot-checked values agree within graphical uncertainty. The source uses a test/plot ceiling for alloys that remain passive to transpassivity; Citrine mixes the literal string `Transpassive` into the numeric average field. Those are censored/no-pitting observations, not numbers or ordinary Epit. Figure readings also lack uncertainty, and pH 7 is unreported for 0.5 M NaCl.

## Recommended corrections

Normalize `Transpassive` to a structured censoring/status field with the tested lower bound, retain digitization uncertainty, and mark pH unreported. Preserve composition-specific processing where available.

## Overall assessment

**Numeric values/coverage: generally pass. Data typing and censoring semantics: fail.**
