# Extraction run report

Input: `9_W. M. Carroll, E. E. Lynskey, Corros. Sci. 36 (1994)_ p. 1667.pdf`

Pages supplied and visually inspected: all 12 PDF pages (journal pp. 1667-1678). Figures 2, 4-6, 8/9 and both tables were enlarged for marker/legend review.

Sources covered: Figure 2(a,b) 316L bar data; Figure 4(a,b) and Figure 6 316 wire data; Figure 5 302 wire; Figure 8 sulfate mixtures; Tables 1/2 loop size and chemical pretreatment; Figure 9 Ni80Cr20 and pure-metal points; explicit Cr pitting values on p. 1676. Figure 1 and Experimental method establish holders, 0.25 mm wire, washing, nitrogen conditioning and -800 mV/5 min plus 60 mV/min scans. All reported results are averages of at least three identical experiments.

Association map: Figure 2 uses 316L bar with the argon-filled Teflon collar (Figure 1a), while Figures 4-9 and Tables 1/2 use the wire-loop assembly (Figure 1b) unless flat Cr is explicitly specified. The default wire loop is 25 mm; Table 1 overrides loop size. Acid pretreatment is assigned only to the appropriate Table 2 rows. Numerical preparation temperatures (50/65 degC) were not transferred to electrolyte test temperature. The electrochemical test temperature is not numerically stated. 316 wire Mo is described as just over 2.0%, retained as a strict lower bound with unspecified percent basis; other commercial compositions were not inferred from grade names.

Deduplication: the 0.5 M/pH 4 points shared by Figure 2 panels, the 0.5 M/pH 5.5 points shared by Figure 4 panels, single-halide data repeated in Figure 6, the shared mixed-halide end point, and the untreated 25 mm 1 M NaCl control repeated in both tables are each retained once. Figure 8 pH is not stated, so its outcomes were not merged with known-pH single-halide tests. Its sulfate-only control is retained once. Log-axis concentrations and discrete potentials were visually read; no fitted line was sampled.

Exclusions: Figure 3 unannotated continuous polarization curves; Figures 7/10 imposed-potential current-time traces (300/400 mV are applied potentials, not thresholds); literature-only measurements in the Discussion; commercial 304L statements with no recoverable numerical outcome. No pitting potential was derived from a continuous-curve shape or by subtracting qualitative offsets.

Limitations: six Figure 5 rows have a legend/prose conflict in NaCl versus NaBr assignment and are flagged. Thirty pure Fe/Ni/Mo Figure 9 rows are partial: the source substitutes a 10 microA/cm2 threshold where definite pitting is absent, but does not identify which markers use the substitute. Their plotted numbers are preserved in result_note, pitting_potential is null, and all thirty rows are flagged. Ni80Cr20 points are explicitly presented as the alloy comparison and retained numerically. Mixed- and sulfate-solution amounts retain the reported totals/balance wording rather than calculated component amounts. Figure 8 pH is unavailable. Plot numbers are approximate (generally 5-10 mV); apparent scatter between repeated presentations was not made into extra replicates. All pages were accessible.

Output: [paper_9.json](paper_9.json)

Experiment-array record count, derived from saved JSON: 117. Flagged partial/conflicted records: 36.

Structural validation: PASS (validator exit code 0). Schema/Pydantic validation checks structure, not scientific fidelity or completeness.

Rows with nonempty failure_notes (zero-based experiments indices):

- `44`: Figure 5 legend implies NaBr has the higher pitting potential, but the surrounding text and abstract say Br- is more aggressive for 302; salt/series assignment conflict remains unresolved.
- `45`: Figure 5 legend implies NaBr has the higher pitting potential, but the surrounding text and abstract say Br- is more aggressive for 302; salt/series assignment conflict remains unresolved.
- `46`: Figure 5 legend implies NaBr has the higher pitting potential, but the surrounding text and abstract say Br- is more aggressive for 302; salt/series assignment conflict remains unresolved.
- `47`: Figure 5 legend implies NaBr has the higher pitting potential, but the surrounding text and abstract say Br- is more aggressive for 302; salt/series assignment conflict remains unresolved.
- `48`: Figure 5 legend implies NaBr has the higher pitting potential, but the surrounding text and abstract say Br- is more aggressive for 302; salt/series assignment conflict remains unresolved.
- `49`: Figure 5 legend implies NaBr has the higher pitting potential, but the surrounding text and abstract say Br- is more aggressive for 302; salt/series assignment conflict remains unresolved.
- `85`:  Figure 9 does not distinguish actual pitting potentials from current-threshold substitutes for this metal; pitting_potential left null.
- `86`:  Figure 9 does not distinguish actual pitting potentials from current-threshold substitutes for this metal; pitting_potential left null.
- `87`:  Figure 9 does not distinguish actual pitting potentials from current-threshold substitutes for this metal; pitting_potential left null.
- `88`:  Figure 9 does not distinguish actual pitting potentials from current-threshold substitutes for this metal; pitting_potential left null.
- `89`:  Figure 9 does not distinguish actual pitting potentials from current-threshold substitutes for this metal; pitting_potential left null.
- `90`:  Figure 9 does not distinguish actual pitting potentials from current-threshold substitutes for this metal; pitting_potential left null.
- `91`:  Figure 9 does not distinguish actual pitting potentials from current-threshold substitutes for this metal; pitting_potential left null.
- `92`:  Figure 9 does not distinguish actual pitting potentials from current-threshold substitutes for this metal; pitting_potential left null.
- `93`:  Figure 9 does not distinguish actual pitting potentials from current-threshold substitutes for this metal; pitting_potential left null.
- `94`:  Figure 9 does not distinguish actual pitting potentials from current-threshold substitutes for this metal; pitting_potential left null.
- `95`:  Figure 9 does not distinguish actual pitting potentials from current-threshold substitutes for this metal; pitting_potential left null.
- `96`:  Figure 9 does not distinguish actual pitting potentials from current-threshold substitutes for this metal; pitting_potential left null.
- `97`:  Figure 9 does not distinguish actual pitting potentials from current-threshold substitutes for this metal; pitting_potential left null.
- `98`:  Figure 9 does not distinguish actual pitting potentials from current-threshold substitutes for this metal; pitting_potential left null.
- `99`:  Figure 9 does not distinguish actual pitting potentials from current-threshold substitutes for this metal; pitting_potential left null.
- `100`:  Figure 9 does not distinguish actual pitting potentials from current-threshold substitutes for this metal; pitting_potential left null.
- `101`:  Figure 9 does not distinguish actual pitting potentials from current-threshold substitutes for this metal; pitting_potential left null.
- `102`:  Figure 9 does not distinguish actual pitting potentials from current-threshold substitutes for this metal; pitting_potential left null.
- `103`:  Figure 9 does not distinguish actual pitting potentials from current-threshold substitutes for this metal; pitting_potential left null.
- `104`:  Figure 9 does not distinguish actual pitting potentials from current-threshold substitutes for this metal; pitting_potential left null.
- `105`:  Figure 9 does not distinguish actual pitting potentials from current-threshold substitutes for this metal; pitting_potential left null.
- `106`:  Figure 9 does not distinguish actual pitting potentials from current-threshold substitutes for this metal; pitting_potential left null.
- `107`:  Figure 9 does not distinguish actual pitting potentials from current-threshold substitutes for this metal; pitting_potential left null.
- `108`:  Figure 9 does not distinguish actual pitting potentials from current-threshold substitutes for this metal; pitting_potential left null.
- `109`:  Figure 9 does not distinguish actual pitting potentials from current-threshold substitutes for this metal; pitting_potential left null.
- `110`:  Figure 9 does not distinguish actual pitting potentials from current-threshold substitutes for this metal; pitting_potential left null.
- `111`:  Figure 9 does not distinguish actual pitting potentials from current-threshold substitutes for this metal; pitting_potential left null.
- `112`:  Figure 9 does not distinguish actual pitting potentials from current-threshold substitutes for this metal; pitting_potential left null.
- `113`:  Figure 9 does not distinguish actual pitting potentials from current-threshold substitutes for this metal; pitting_potential left null.
- `114`:  Figure 9 does not distinguish actual pitting potentials from current-threshold substitutes for this metal; pitting_potential left null.

Access/tool notes: local PDF pages rendered with Poppler and actually viewed. Existing embedded PDF text was used only as a passage locator (pypdf fallback after the system MiKTeX pdftotext wrapper emitted a local cache-access error). Rendering succeeded; no OCR, automatic marker detection, curve tracing, or programmatic table extraction was used.
