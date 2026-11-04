# Paper 9: observation-registry coverage

Input: `9_W. M. Carroll, E. E. Lynskey, Corros. Sci. 36 (1994)_ p. 1667.pdf`. Literature reference: 9. Evidence: supplied PDF only; no database, prior extraction, or locating report was read.

Supplied pages: 12. Visually inspected: PDF pp. 1–12 (printed pp. 1667–1678), including every plot, table, caption, and relevant passage. Figs. 2, 4–6, 8–9 and Tables 1–2 received enlarged review; Fig. 6 was additionally cropped at 300 dpi to check overlapping markers. Full paper survey completed; no page-access limitation. Eligible coverage: every discrete E_p marker in Figs. 2, 4–6, 8–9; all potential cells in Tables 1–2; the two text-only flat-Cr potentials; and the two numerical cited outcomes on p. 1677. Repeated pH/concentration intersections and explicitly re-presented single-halide series are consolidated, with each original reading retained as a location.

Registry: [paper_9.json](paper_9.json) (schema 1.1). Actual saved observations: **120**. Complete: **120**; partial: **0**; failed: **0**.

- Partial IDs: none
- Failed IDs: none

## Source qualifications and consolidation

The paper states that presented experimental results average at least three identical experiments. These remain experimental summaries. Fig. 2 concerns steel 316L in the bar-electrode system, while subsequent 316 results concern wire loops. Original logarithmic coordinates are explicit in plot selectors. The Fig. 4 single-halide concentration data are explicitly included in Fig. 6 and are consolidated; graphical differences remain in their individual locations. Pure-halide mixed-series endpoints in Fig. 6 share those conditions. Table 2’s untreated 1.0 M NaCl, pH 3 baseline is consolidated with Table 1’s standard 25 mm loop. Fig. 8 does not state pH; no value is inferred, and uncertain endpoint repeats remain separate rather than being counted as proven independent experiments. For Fe, Ni, and Mo in Fig. 9 the paper conditionally uses a 10 μA cm−2 proxy when a definite pitting potential is not evident, without identifying affected points. Each recovered marker is experimental and complete while retaining this scientific qualification. The **550 mV(SCE)** and **at least 850 mV** occurrences are **cited**; the latter describes about 25% of the cited wire population. Most graphical potentials are read to 5–10 mV, with coarser precision for the high-potential sulphate plot.

## Exclusions

Fig. 1 is apparatus. Fig. 3 shows continuous polarization curves without explicit numerical pitting annotations; no bend was inferred as a threshold. Figs. 7 and 10 show current–time traces at imposed 400/300 mV, not numerical pitting-potential measurements; the imposed potentials were not registered as thresholds or invented bounds. Approximate differences between halides (100/200 mV) and offsets from chosen hold potentials are not condition-specific absolute pitting potentials. Qualitative breakdown ordering, unquantified literature comparisons, and other potential concepts such as zero charge were excluded. Connecting/fitted lines and legend symbols were not counted as data markers.

## Validation

Bundled validator exit code: **0**. Structural/internal-consistency validation passed. It does not certify scientific interpretation, consolidation, or coverage.

```text
VALID: C:\Archives\School\HHU\HHU Courses\Max Plank\Thesis - Work\AgenticDatabaseReconstruction\observation_registry\paper_9.json (120 observations).
Extraction status: complete=120; partial=0; failed=0
Partial observation IDs: none
Failed observation IDs: none
Default routing: complete and partial continue; failed require review.
Scientific fidelity, consolidation, coverage, and benchmark suitability not checked.
```
