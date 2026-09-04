# Audit Report: Citrine Pitting-Potential Records for Reference 24

## Scope

Reviewed the zero-row result against [Chou, Yeh, and Shih (2010)](<../papers/24_Y.L.Chou, J.W.Yeh, and H.C. Shih. Corrosion Science, 52 (2010),2571-2581.pdf>). Audit date: 2026-09-04.

## Executive summary

Table 6 reports four breakdown potentials in 1 M NaCl for Mo = 0, 0.1, 0.5, and 0.8 alloys. Only the Mo-free alloy showed confirmed pitting; the Mo-containing alloys showed negative hysteresis/no pits. Zero rows therefore misses at least one true pitting endpoint and also loses three informative non-pitting breakdown/censored observations.

| Severity | Finding |
|---|---|
| High | The confirmed Mo-free 1 M NaCl pitting potential is omitted. |
| Medium | Three breakdown-without-pitting results require endpoint/censoring semantics, not ordinary Epit labels. |

## Recommended correction

Add the Mo-free value as `Epit`. If the schema supports breakdown or censored observations, add the other three with explicit “no pit observed” status. Exclude chloride-free sulfate/NaOH transpassive behavior.

## Overall assessment

**Coverage: fail, with endpoint ambiguity requiring careful reconstruction.**
