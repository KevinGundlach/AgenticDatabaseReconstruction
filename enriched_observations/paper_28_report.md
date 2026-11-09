# Paper 28: observation enrichment

PDF: `28_Shi, Y., et al. (2018). Corrosion Science 133_ 120-131.pdf`  
Registry: `paper_28.json`  
Resolved reference: 28  
Output: [paper_28.json](paper_28.json)

- Visual overview, one-based supplied-PDF pages actually viewed: 1–12.
- Detailed sources: Manufacturing and distinct forging/equilibration schedules (p. 2); electrode protocol and phases (p. 3); phase-specific Table 1 and TEM/EBSD discussion (pp. 4–6); Ep criterion (p. 7); Table 3, SD caption and Fig. 8 (p. 9); Fig. 11 all symbols/legend, caption and comparison scope (p. 11).
- Access: All supplied pages accessible; visually inspected PDFium page images. Embedded text used for navigation; no OCR, automatic table extraction or curve tracing.
- Counts: supplied 21; eligible 21; written 21; skipped failed 0; flagged output 3.
- Skipped failed IDs: none.
- Flagged output IDs (nonblank failure_notes): obs_007, obs_008, obs_009.

All 21 eligible IDs retained. obs_007–obs_009 are flagged because Figure 11 does not associate each HEA marker with a unique Al content or treatment state; no Table 3 matching is guessed and possible duplicate presentations remain separate. Cited comparison points receive material class and 3.5 wt.% NaCl scope only, without current-study temperature/rate or guessed commercial chemistry. Six Table 3 records retain state-specific microstructure, nominal atomic ratios and reported SDs; phase EDS is not bulk chemistry. Electrolyte 20 ± 2 °C is separate from 1250 °C treatment. The 100 µA/cm² initiation criterion differs from the 1 mA/cm² scan endpoint; selective dissolution qualifications retained.

Validation: actual exit code 0; PASS. Checked schemas/models, exact input fingerprints, eligible-ID coverage/order and unchanged raw potential objects. Structural validation does not certify scientific associations or benchmark suitability.

```text
VALID: C:\Archives\School\HHU\HHU Courses\Max Plank\Thesis - Work\AgenticDatabaseReconstruction\enriched_observations\paper_28.json
Supplied=21; eligible=21; written=21; skipped_failed=0; flagged=3.
Skipped failed IDs: none
Flagged output IDs: obs_007, obs_008, obs_009
Scientific fidelity, retained qualification meanings and actual visual coverage are not certified.

```
