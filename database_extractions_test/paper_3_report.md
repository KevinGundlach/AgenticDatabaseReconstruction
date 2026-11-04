# Extraction run report

Input: `3_N. Pessall, J. I. Nurminen, Corrosion 30 (1974)_ p. 381..pdf`

Pages supplied and visually inspected: all 12 PDF pages (journal pp. 381-392); Tables 4/5 and Figures 21/22 additionally enlarged.

Sources covered: Tables 1-3 (compositions/preparation map), both pitting-potential columns of Table 4, all three pitting-result columns of Table 5, discrete Figure 1 markers, numerical Ec annotations in Figures 7-10, Figures 2/3 (duplicates), and Figures 21/22 (correlation/overlap review). Methods on pp. 381-384 and microstructure discussion on pp. 388-390 were reviewed.

Association map: W5-W8 are the 50 lb induction-melted heats; Table 4 specimen suffixes select the reported rolling/heat-treatment condition. Their extracted compositions are explicitly the Table 1 aim values, not a fabricated average of the top/bottom analyses. The F460-F475 labels link Table 3 compositions to the distinct A/B-series runs in Table 5; two F464B runs remain separate. B-series Figure 2 data have the stated 1049 degC/1 h/water-quench treatment; A-series final treatment is not identified and was not guessed. Table 2 identifies ternary alloys for the Figure 1 branches and the numbered photograph annotations. Commercial Figure 1 markers are reported measurements in this paper; numerical nominal composition is only assigned when actually given in the text.

Distinct result types: scan Ec scan, scratch Ec scr, and current-time Ec (I-t) strict upper bounds are separate outcomes, with method-specific protocols. Table 4 printed ranges remain single ranged measurements. Figure 2/3, the repeated photograph labels, and Figure 21/22 points that are recoverably linked to earlier data were deduplicated. Figure 21 points A/B are assigned using the explicit Discussion statement (Fe-21.7Cr-4.0Mo, with the stated Si/Ni addition for A), without joining to another specimen on composition. F469B scratch potential conflicts (165 in Table 5 versus 265 mV in Figure 7) are retained and flagged.

Exclusions: corrosion-rate plots (Figures 4/5/18), crevice attack photographs as independent exposure outcomes, weight losses, plant exposure results, micrographs, interpolated/broken/fitted curves, and general discussion of no-pitting areas are not new pitting-potential outcomes. F230B has a composition-table entry but no uniquely recoverable outcome assignment and was not turned into an experiment solely from its composition. The Figure 21/22 contour boundaries do not create observations.

Limitations: five additional unlabeled markers in the Figure 21/22 correlation region are retained as flagged partial outcomes. Their specimen identity and whether they repeat Tables 4/5 cannot be resolved; do not treat the raw array length as a count of independently established experiments. Some dense overlapping markers in those correlation figures cannot be uniquely enumerated or assigned, so numerical coverage there remains incomplete. A-series heat-treatment details and the detailed scratch protocol are not supplied. Small ternary/commercial markers are approximate visual readings (typically about 5-10 mV precision). All pages were visually accessible; this is not a claim that every unlabeled overlapping correlation marker has been uniquely recovered.

Output: [paper_3.json](paper_3.json)

Experiment-array record count, derived from saved JSON: 138. Flagged partial/conflicted records: 6.

Structural validation: PASS (validator exit code 0). Schema/Pydantic validation checks structure, not scientific fidelity or completeness.

Rows with nonempty failure_notes (zero-based experiments indices):

- `57`: Scratch potential conflict: Table 5 F469B = 165 mV; Figure 7 F469B = 265 mV. Table 5 value retained.
- `131`: Figure 21/22 marker has no recoverable sample label; association with Tables 4/5 or another alloy and duplicate status cannot be resolved. Alloy-specific fields left unavailable.
- `134`: Figure 21/22 marker has no recoverable sample label; association with Tables 4/5 or another alloy and duplicate status cannot be resolved. Alloy-specific fields left unavailable.
- `135`: Figure 21/22 marker has no recoverable sample label; association with Tables 4/5 or another alloy and duplicate status cannot be resolved. Alloy-specific fields left unavailable.
- `136`: Figure 21/22 marker has no recoverable sample label; association with Tables 4/5 or another alloy and duplicate status cannot be resolved. Alloy-specific fields left unavailable.
- `137`: Figure 21/22 marker has no recoverable sample label; association with Tables 4/5 or another alloy and duplicate status cannot be resolved. Alloy-specific fields left unavailable.

Access/tool notes: local PDF pages rendered with Poppler and actually viewed. Existing embedded PDF text was used only as a passage locator (pypdf fallback after the system MiKTeX pdftotext wrapper emitted a local cache-access error). Rendering succeeded; no OCR, automatic marker detection, curve tracing, or programmatic table extraction was used.
