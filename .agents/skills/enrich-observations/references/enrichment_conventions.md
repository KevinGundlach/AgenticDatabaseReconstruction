# Anchored enrichment conventions

## Relationship to the copied extraction format

The local `paper_extraction.py`, `paper_extraction.schema.json` and `extraction_conventions.md` are frozen copies of the current extraction format. Keep their scientific fields and missing-value rules. The active enrichment format adds only required `observation_id` to each experiment and required root `inputs`. Its independent schema version is `"1.0"` and its list remains `experiments`.

These anchored rules override the copied conventions wherever the older workflow calls for discovering all outcomes, excluding cited results by default, reading a new potential, deduplicating, or omitting unrecovered outcomes. Enrich every supplied `complete`/`partial` observation, regardless of origin, exactly once and in order. Skip `failed` inputs and report their IDs. No `experiment_id`, outcome discovery, deduplication or new origin/status/provenance fields are introduced. Classification and source-location details remain available through the immutable registry.

At the root retain `schema_version`, `paper_name`, `reference_number`, `experiments` and add:

```json
"inputs": {
  "pdf": {"filename": "9002_invented_enrichment.pdf", "sha256": "<actual SHA-256>"},
  "registry": {"filename": "paper_9002_subset.json", "sha256": "<actual SHA-256>"}
}
```

This fragment illustrates metadata only, not a valid complete output. Copy real 64-character lowercase hashes from preparation. IDs are scoped to that exact registry; independent regenerations are not interchangeable. Hashes are of original bytes, including whitespace/BOM, not normalized JSON. Filenames are basenames, not absolute paths.

Strict JSON parsers reject duplicate keys, NaN, Infinity and overflowing numeric literals. UTF-8 with or without BOM is accepted. Preserve IDs with gaps. Resolve references from registry metadata and numbered PDF/registry filenames; any disagreement blocks preparation. Unknown references remain null. A renamed file is a warning requiring paper-identity verification, not permission to assume identity. The helpers check bookkeeping, not PDF renderability or true visual inspection.

## Immutable outcome, paper-derived context

Copy the raw observation-level `pitting_potential`, which already equals its primary reading under registry rules. Preserve its key set and values: omitted `unit` or bounds remain omitted, explicit null subfields remain null, and a null measurement remains null. JSON numeric spellings such as 1 and 1.0 represent the same number; do not round or change its numerical value. Copy the raw object after any context-model processing instead of using a serialization that materializes extra defaults. Do not select another `locations` entry's measurement even if it looks clearer or closer to an expected value.

Visually verify primary/secondary sources to understand the association and qualifications. New tables or figures may clarify material identity, preparation or procedure, but do not become new outcomes or replace the locked reading. Preserve separate runs, scan/scratch methods and possible repeated presentations. Shared context can be repeated across records when supported; duplication is acceptable in this pilot.

Each independent-variable coordinate is specific to its row. Apply a header, caption, treatment or methods statement only within its established scope. Equal compositions do not establish identical preparation or conditions; a summed Cr+Mo coordinate does not establish a complete composition. Do not use an unrelated exposure temperature, electrolyte or procedure to complete a pitting experiment. Cited results receive only context actually supplied by this PDF, not details retrieved from the cited paper.

For data fields follow the copied conventions: ordered processing prose, tested-state microstructure, explicitly reported elements and composition basis, solution conditioning separate from solutes, reported solvent, original temperature/rate/concentration units, and method-specific steps/holds. No new unit-conversion or chemistry-calculation stage is added. Multi-rate/variable-duration procedures belong in prose when one scalar is inadequate.

## Result notes and recovery failures

Carry meaningful registry `result_note` qualifications into the output `result_note`, adding source-derived clarifications. Keep reported means/ranges, inequalities, current-criterion proxies, source disagreements and possible duplicate relationships explicit. No averaging, midpoint construction or guessing which points satisfy a conditional criterion. Scientific qualifications alone do not make an enrichment failure.

Use `failure_notes` for information/associations that cannot be recovered despite appearing available, or an extraction problem making the row unreliable. Identify affected fields and leave them empty/null rather than choosing arbitrary details. A registry reading contradicted by the visible source may itself be an error: keep its numeric value locked, explain the suspected correction in `result_note`, and flag the recovery problem. A genuine table/figure disagreement in the paper alone is a scientific qualification rather than an automatically failed extraction.

An earlier registry `partial` status does not force an output failure if the relevant contextual problem has now been resolved. Conversely, a registry `complete` status does not guarantee that context can be enriched successfully. Carry unresolved registry limitations forward when still relevant. A null locked potential cannot be repaired here; explain any unresolved numerical recovery even when context is recovered. Missing unreported pH, microstructure or composition amounts alone use ordinary empty/null values without a failure warning.

For partially inaccessible PDFs, retain all eligible IDs with any supported context, locked potentials and specific failure notes for blocked recovery. Do not drop difficult rows. For entirely unavailable visual access with eligible inputs, write a report only and no enrichment dataset. For empty/failed-only inputs, an empty `experiments` array is a routing result, not evidence that the paper has no outcomes.

## Brief report

Save one short Markdown report beside the extraction, including failed/blocked attempts:

- Input PDF and registry filenames, resolved reference, and saved JSON link if present.
- Actual visual overview coverage: list one-based supplied-PDF pages viewed, disclose inaccessible/unviewed pages and actual capability errors. Rendered-but-unviewed pages are not inspected.
- Sources read in detail: relevant figures/tables/sections, captions, footnotes and material/procedure context. Do not claim a full detailed reading merely from a page overview.
- Counts derived from saved JSON and prepared inputs: supplied, eligible, written, skipped failed, and flagged output records. If no JSON was saved, report written as unavailable/not saved rather than a successful zero-row extraction.
- Skipped failed IDs and output IDs with nonblank `failure_notes`; zero/none is explicit. An entry with empty failure notes is not certified as benchmark-ready.
- Concise shared scientific qualifications, contradictions, proposed anchor corrections, unresolved associations and partial coverage. Mention affected IDs where useful, without per-observation narratives or repeating full methods.
- Actual validator exit code and outcome, or not run and why. Structural success does not verify experimental associations or source interpretation.

Do not create an aggregate batch-summary JSON. Do not import matching results to add CRA row IDs or exclude ambiguous matches. If several input pairs are requested, write separate scoped files with collision-preserving names. Helpers write only stdout/stderr; saving the JSON and report is the invoking agent's responsibility.
