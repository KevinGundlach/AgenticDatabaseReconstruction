# Extraction run report

Input: `49_Malik, A. U., et al. Corrosion science 37.10 (1995)_ 1521-1535.pdf`

Pages supplied and visually inspected: all 15 PDF pages (journal pp. 1521-1535).

Sources covered: all 75 Epit cells of Table 5; Table 1 alloy compositions; Table 2 seawater ions; Materials, Techniques and procedures, and Potentiodynamic polarization measurements sections. Figures 2, 5 and 6 were visually reviewed and reconciled as presentations of these results rather than additional experiments.

Association map: Table 1 commercial alloy names link to Table 5 rows. Each alloy has four aqueous chloride conditions (300, 500, 1000, 5000 ppm Cl-, pH 7.8) and natural Gulf seawater (pH 8.2, 24090 mg/L Cl-), all at 50 degC. Distilled water is stated for the prepared chloride solutions. The seawater solvent is not separately named. Table 1 does not identify a weight/atomic composition basis, so its numeric amounts have an empty unit. Cb is transcribed as Nb. The joint Cb+Ta additions (0.6 for Duplex 2205; 5 for 20 Cb3) are retained in result notes, with individual amounts null. No residual Fe or missing Mo was calculated.

Exclusions: corrosion potentials/rates, salt-spray tests, crevice attack depths and times, active peak heights, CCS pH results, and cited literature comparisons are not pitting-potential outcomes. The accelerated CCS protocol (600-grit finish, HNO3 passivation, N2 deaeration, -600 to +100 mV at 10 mV/s) belongs to a different experiment and was not assigned to the Table 5 pitting measurements. Their scan rate and specific surface finish are not provided here.

Limitations: natural-seawater pitting values for 17-4PH (printed 1516 mV), Duplex 2205, SMO 254 and Monit 44635 have conflicting figure annotations/assignments; the explicit Table 5 numbers are retained and affected rows flagged. Duplex 2205 has an unlabeled 0.15 in Table 1, so this amount was not assigned to an element and all five rows are flagged. Figure 5 also has inconsistent horizontal placement relative to its log chloride axis, so Table 5 concentration columns take precedence. All pages were accessible; no automatic table extraction or curve tracing was used.

Output: [paper_49.json](paper_49.json)

Experiment-array record count, derived from saved JSON: 75. Flagged partial/conflicted records: 8.

Structural validation: PASS (validator exit code 0). Schema/Pydantic validation checks structure, not scientific fidelity or completeness.

Rows with nonempty failure_notes (zero-based experiments indices):

- `29`: Table 5 prints 1516 mV; Figure 2 labels the 17-4PH curve 94 mV, while Figure 6 places it at about 156 mV. The seawater ranking in the text also differs from Table 5. Table 5 value retained; unresolved source conflict.
- `34`: Table 5 gives 813 mV, while Figure 6 labels 254 near 721 mV (the Table 5 Monit 44635 value). Table 5 value retained; unresolved figure/table assignment conflict.
- `64`: Table 5 gives 721 mV, while Figure 6 labels 44653 near 813 mV (the Table 5 SMO 254 value). Table 5 value retained; unresolved figure/table assignment conflict.
- `70`: Table 1, Duplex 2205: the 0.15 amount in the Others column has no element label; no element was guessed. 
- `71`: Table 1, Duplex 2205: the 0.15 amount in the Others column has no element label; no element was guessed. 
- `72`: Table 1, Duplex 2205: the 0.15 amount in the Others column has no element label; no element was guessed. 
- `73`: Table 1, Duplex 2205: the 0.15 amount in the Others column has no element label; no element was guessed. 
- `74`: Table 1, Duplex 2205: the 0.15 amount in the Others column has no element label; no element was guessed. Table 5 and Figure 6 give approximately 629 mV, but Figure 2 labels the Duplex 2205 curve 826 mV. Table 5 value retained; unresolved source conflict.

Access/tool notes: local PDF pages rendered with Poppler and actually viewed. Existing embedded PDF text was used only as a passage locator (pypdf fallback after the system MiKTeX pdftotext wrapper emitted a local cache-access error). Rendering succeeded; no OCR, automatic marker detection, curve tracing, or programmatic table extraction was used.
