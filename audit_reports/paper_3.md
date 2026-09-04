# Audit Report: Citrine Pitting-Potential Records for Reference 3

## Scope

This report compares all 54 Reference 3 records in the Citrine `Pitting Potential` sheet with:

- [N. Pessall and J. I. Nurminen, Corrosion 30 (1974), 381](<../papers/3_N. Pessall, J. I. Nurminen, Corrosion 30 (1974)_ p. 381..pdf>)
- [Citrine source workbook](../citrine_database/CRA_database_Scientific_Data_Publication_12102020.xlsx), Excel rows 406-459 (record numbers 404-457)

Audit date: 2026-09-03

Workbook evidence: 【CRA_database_Scientific_Data_Publication_12102020.xlsx:Pitting Potential:A406:AM459】

The source tables and figures were checked visually. The repository's [figure catalog](../mineru_output/paper_3/paper_3_figures.json) and [figure extraction](../mineru_output/paper_3/paper_3_figure_extractions.json) were used as secondary cross-checks.

## Executive summary

The 54 stored potential values agree with Table 5. Citrine preserves the important distinction between conventional scan values and scratch potentials. No incorrect pitting-potential number was found. The main issue is selective coverage: Table 4, the E-Brite row in Table 5, and the third endpoint column in Table 5 are absent. The chloride molarity is also not stated in the paper and is therefore an inferred value.

| Severity | Finding | Affected records |
|---|---|---:|
| Medium | All 28 scan/scratch fields in Table 4 are omitted. | Coverage |
| Medium | The E-Brite comparison row in Table 5 (136 mV scan; 128 mV scratch) is omitted. | Coverage |
| Medium | Seventeen reported censored `E_c^(l-t)` upper bounds from Table 5 are omitted. | Coverage |
| Medium | `[Cl-] = 0.546 M` is not stated in the paper and cannot be independently traced from it. | 404-457 |
| Low | The database stores pH as exactly 7.2 and loses the source uncertainty of +/-0.2. | 404-457 |
| Low | Two F464B runs are collapsed into a range, losing run identity. | 430 and corresponding scratch record |

## Record reconciliation

The stored rows divide cleanly into the Table 5 series:

| Citrine records | Source group | Count | Result |
|---:|---|---:|---|
| 404-414 | A-series, `E_c^scan` | 11 | All values match Table 5 |
| 415-425 | A-series, `E_c^scr` | 11 | All values match Table 5 |
| 426-441 | B-series, `E_c^scan` | 16 | All values match Table 5 |
| 442-457 | B-series, `E_c^scr` | 16 | All values match Table 5 |

The source uses 10 mV/min for the conventional scan, equivalent to Citrine's 0.167 mV/s. Scratch measurements appropriately have no scan rate. Compositions agree with Tables 2 and 3 for the represented alloys.

Table 5 contains two F464B runs. Citrine retains both scan values as a min/max range (125-142 mV), while the identical scratch result is represented once. This is numerically defensible as aggregation, but a run-level audit trail would be preferable because the source supplies separate run numbers.

## Conditions and method

- The paper specifies deaerated synthetic seawater at 90 C and pH 7.2 +/- 0.2. These core conditions are represented, except that the pH uncertainty is discarded.
- The B-series final treatment of 1 h at 1049 C followed by water quenching is correctly assigned. The stored text contains a minor typo (`comepared`) but not a scientific error.
- The A-series heat-treatment field is a broad preparation narrative rather than a normalized, specimen-specific condition. It is traceable to the paper but should be structured more precisely.
- The paper does not print a chloride molarity of 0.546 M. That value may have been calculated from a synthetic-seawater recipe or external convention, but such a derivation is not documented in the record.
- The authors state that alloy ranking was based solely on the scratch potential because it is less dependent on finish and scan rate. Citrine labels scan and scratch records separately, which is essential and correct.

## Coverage audit

### Confirmed omitted source fields

| Source | Omitted fields | Notes |
|---|---:|---|
| Table 4 | 14 `E_c^scan` and 14 `E_c^scr` fields | Includes ranges for some alloys; all are pitting-potential measurements |
| Table 5, E-Brite | 2 | 136 mV scan and 128 mV scratch |
| Table 5, `E_c^(l-t)` | 17 censored values | Reported as upper bounds such as `<135`; endpoint method must remain distinct |
| **Total printed fields** | **47** | Counts source fields, not de-duplicated individual replicate measurements |

Figures 2 and 3 graph values that substantially overlap the tables and should not be added as independent duplicates. Figure 1 contains a broader composition map of scratch potentials and may include additional source observations, but it requires alloy-level reconciliation before determining a unique omission count.

## Recommended corrections

1. Add the Table 4 scan and scratch measurements, preserving heat-treatment condition and source ranges.
2. Add the Table 5 E-Brite comparison row.
3. Decide explicitly whether `E_c^(l-t)` belongs in the target dataset; if included, preserve its method label and `<` censoring.
4. Change `[Cl-]` to `NA` unless the external calculation is documented, or mark 0.546 M as derived with its recipe and assumptions.
5. Preserve pH as 7.2 +/- 0.2 rather than exact 7.2.
6. Retain separate source run identifiers for the two F464B measurements.

## Overall assessment

**Stored potential values: pass.** All 54 agree with Table 5.

**Conditions and provenance: minor-to-moderate correction needed.** Chloride molarity is not traceable within the cited paper, and source uncertainty/run identity are lost.

**Coverage: materially incomplete.** At least 47 printed pitting-potential fields in Tables 4 and 5 are not represented.
