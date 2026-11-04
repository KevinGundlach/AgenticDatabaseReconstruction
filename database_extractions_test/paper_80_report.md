# Extraction run report

Input: `80_G.S. Frankel, R.C. Newman, C.V. Jahnes, M.A. Russak, J Electrochem Soc, 140 (1993) 2192-2197.pdf`

Pages supplied and visually inspected: all 12 PDF pages (the supplied reformatted article); all six figures, methods, results, discussion and references were inspected. Figures 1-4 and the crowded fresh-sample clusters were enlarged; Figures 5/6 endpoints were also enlarged.

Sources covered: Figure 1 aged AlNb circles; Figure 2 aged AlMo circles and ambiguous new-fresh candidates; Figure 3 fresh AlW and aged AlV/AlMn; Figure 4 aged AlCr and newly deposited fresh Cr specimens; explicit pure-Al -690 mV and Al-5.2 at% W -60 mV text; Figure 5 pitting-identified highest-potential endpoints. Figure 6 highest endpoints agree approximately with the aged Cr scatter groups and are deduplicated. Pure-Al baselines repeated across figures are retained once per visible outcome.

Association map: all films are sputter-deposited, 1000-2000 angstrom, washed only with water, and tested in stagnant air-exposed 0.1 M NaCl with SCE reference. The present scan is 1 mV/s; bulk-solution pH and numerical test temperature are not supplied. Aged samples were stored in laboratory air at room temperature, generally 2-4 years (V/Mn about 2 years); fresh means within a few months. No Al balance or numerical purity was calculated. The Nb/Cr group compositions labeled in Figures 5/6 support corresponding groups in Figures 1/4; other concentrations were visually digitized and remain approximate.

Exclusions: repassivation ER symbols and the abscissa symbols in Figures 5/6; intermediate imposed growth potentials/current densities; schematic arrows; lines without markers; literature values including the >800 mV Al-W comparison. Historical connected fresh-sample reference series from the authors' earlier paper were excluded where identifiable. Their protocol was 0.2 mV/s in pH 10, unlike the present study, and was not silently assigned to current measurements. No general-current curve was used to infer an unlabeled threshold: Figure 5 endpoints are eligible because the text explicitly identifies their highest potentials as pitting potentials.

Limitations: graph readings are approximate (typically about 10-20 mV and 0.5-1 at% for concentrations read from axes); this is not reported uncertainty and was not entered as plus_minus. The crowded AlMo fresh cluster has unresolved historical/current origin and multiplicity; three candidate rows are flagged and may duplicate historical comparators. The superimposed low-Nb aged circle and low-Cr fresh marker are flagged for overlap. Two Figure 5 Nb endpoints have unresolved fresh/aged assignment. Dense overlapping fresh markers may not be uniquely enumerable; their numerical coverage is incomplete and the raw array length is not a count of fully resolved independent experiments. The paper itself questions the original composition measurement of the anomalous 10% Mo sample. All pages were accessible.

Output: [paper_80.json](paper_80.json)

Experiment-array record count, derived from saved JSON: 44. Flagged partial/conflicted records: 7.

Structural validation: PASS (validator exit code 0). Schema/Pydantic validation checks structure, not scientific fidelity or completeness.

Rows with nonempty failure_notes (zero-based experiments indices):

- `3`: Figure 1: aged circle overlaps a fresh triangle at about -180 mV; circle/triangle separation limits precision.
- `36`: Low-Cr fresh marker overlaps the historical fresh triangle; exact numerical separation is unresolved.
- `39`: Figure 2 uses the same triangle symbol for fresh results and gives no separate key for historical versus newly deposited samples; marker multiplicity/origin and hence scan-rate/pH assignment are unresolved. May duplicate a historical comparator.
- `40`: Figure 2 uses the same triangle symbol for fresh results and gives no separate key for historical versus newly deposited samples; marker multiplicity/origin and hence scan-rate/pH assignment are unresolved. May duplicate a historical comparator.
- `41`: Figure 2 uses the same triangle symbol for fresh results and gives no separate key for historical versus newly deposited samples; marker multiplicity/origin and hence scan-rate/pH assignment are unresolved. May duplicate a historical comparator.
- `42`: The individual Figure 5 15.5 at% Nb growth runs cannot be assigned to a fresh/aged state or matched uniquely to the Figure 1 pitting markers.
- `43`: The individual Figure 5 15.5 at% Nb growth runs cannot be assigned to a fresh/aged state or matched uniquely to the Figure 1 pitting markers.

Access/tool notes: local PDF pages rendered with Poppler and actually viewed. Existing embedded PDF text was used only as a passage locator (pypdf fallback after the system MiKTeX pdftotext wrapper emitted a local cache-access error). Rendering succeeded; no OCR, automatic marker detection, curve tracing, or programmatic table extraction was used.
