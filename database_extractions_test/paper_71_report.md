# Extraction run report

Input: `71_Truman, J. E., M. J. Coleman, and K. R. Pirt. British corrosion journal 12.4 (1977)_ 236-238.pdf`

Pages supplied and visually inspected: all 4 PDF pages (cover plus journal pp. 236-238).

Sources covered: Table I compositions; Table II plain and creviced pitting potentials; Testing section for melting, preparation, electrolyte and potential sequence. The summary on p. 238 repeats a subset of Table II and was deduplicated.

Association map: steel numbers 1-19 link Table I compositions to both Table II potential columns. The crevice column uses the same electrolyte/protocol with the neoprene ring described on p. 236. No numerical electrochemical test temperature or solvent is stated; ambient temperature belongs to the separate immersion tests and was not transferred.

Exclusions: Table II gravimetric weight losses and the separate unpolarized FeCl3/acidified NaCl immersion tests are not pitting-potential measurements. Literature background was not extracted.

Limitations: the authors acknowledge coating-edge crevice attack and scatter. Steel 19 has a source conflict in N content (0.455 wt% in Table I; 0.435 wt% in Table II and discussion). Both steel 19 outcomes retain the Table I composition and are flagged. All paper pages were accessible.

Output: [paper_71.json](paper_71.json)

Experiment-array record count, derived from saved JSON: 38. Flagged partial/conflicted records: 2.

Structural validation: PASS (validator exit code 0). Schema/Pydantic validation checks structure, not scientific fidelity or completeness.

Rows with nonempty failure_notes (zero-based experiments indices):

- `36`: Nitrogen composition conflict for steel 19: Table I reports 0.455 wt% and Table II reports 0.435 wt%; unresolved.
- `37`: Nitrogen composition conflict for steel 19: Table I reports 0.455 wt% and Table II reports 0.435 wt%; unresolved.

Access/tool notes: local PDF pages rendered with Poppler and actually viewed. Existing embedded PDF text was used only as a passage locator (pypdf fallback after the system MiKTeX pdftotext wrapper emitted a local cache-access error). Rendering succeeded; no OCR, automatic marker detection, curve tracing, or programmatic table extraction was used.
