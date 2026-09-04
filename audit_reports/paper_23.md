# Audit Report: Citrine Pitting-Potential Records for Reference 23

## Scope

Reviewed the zero-row result against [Kao et al. (2010)](<../papers/23_Yih-Farn Kao, Tsung-Dar Lee, Swe-Kai Chen, and Yee-Shyi Chang. Corrosion Science, 52 (2010), 1026-1034.pdf>). Audit date: 2026-09-04.

## Executive summary

Figure 10 directly plots breakdown/pitting potentials for four carbon levels and 304 stainless steel at four chloride concentrations in sulfuric acid. The three chloride-containing conditions yield roughly 15 eligible discrete observations; the zero-chloride points are transpassive controls and should not be relabeled as pitting.

| Severity | Finding |
|---|---|
| High | Approximately 15 chloride-containing pitting-potential bars are completely omitted. |
| Medium | Source potentials are versus SHE; conversion must be documented. |

## Recommended correction

Extract the chloride-containing bars only, attach alloy/carbon level and electrolyte composition, and preserve the SHE scale or explicitly convert it. Keep the chloride-free controls outside `Epit`.

## Overall assessment

**Coverage: fail—major omission.**
