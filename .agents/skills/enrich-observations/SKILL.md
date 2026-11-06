---
name: enrich-observations
description: Enrich a full or partial paper observation registry with alloy, electrolyte, and test context from the supplied PDF, preserving observation IDs and anchored pitting potentials. Use for paper-only experiment enrichment before blind benchmarking, not CRA alignment or discovery of new outcomes.
---

# Enrich Observations

Accept one PDF and one **version 1.1 observation registry**, possibly a subset with noncontiguous IDs. Save one **version 1.0 enrichment JSON** plus a brief Markdown report. Enrich only supplied `complete` and `partial` observations. List skipped `failed` IDs in the report. Do not enrich real papers unless this skill is invoked for that work.

Read [enrichment conventions](references/enrichment_conventions.md) and the [output schema](references/observation_enrichment.schema.json), then the copied [data-field conventions](references/extraction_conventions.md). The enrichment conventions override the older unanchored workflow, result selection and potential-reading rules. Scientific fields reuse the local [extraction models](scripts/paper_extraction.py); the [enrichment model](scripts/observation_enrichment.py) adds required observation IDs and input fingerprints. The input [registry schema](references/observation_registry.schema.json) and [classes](scripts/observation_registry.py) are also local. The invented [registry](references/example_registry.json) and [enrichment](references/example_enrichment.json) illustrate routing, shared context, a bound, scientific qualifications and incomplete recovery. Their PDF fingerprint is a placeholder, not evidence of inspection.

## Inputs and blindness

Resolve relative paths from the project root. Require a fresh context containing only the supplied PDF, paper-only registry and bundled resources. Do not use a chat that has already seen CRA values or matching reports for this paper. Do not read CRA CSVs, matching/locating reports, previous enrichment/extraction outputs, selection scripts, external experimental sources, or the parent/full registry when a subset was supplied. A filename such as `matched_only` is not permission to open its matching output. Resource examples illustrate structure, never experimental evidence.

Use the existing Python environment (`pydantic>=2.13.5`, `jsonschema>=4.23,<5`) for read-only preparation:

```powershell
.\.venv\Scripts\python.exe .agents/skills/enrich-observations/scripts/prepare_inputs.py --pdf "papers/49_example.pdf" --registry observation_registry/paper_49_matched_only.json
```

Stdout contains the unchanged registry, exact PDF/registry fingerprints, resolved paper/reference, eligible IDs and skipped failed IDs. Do not infer a reference from the bibliography. Conflicting reference numbers block the run; a renamed-PDF warning requires verifying that it is the same paper. Unavailable reference numbers may remain null. Reject unsupported registry versions without upgrading or rewriting them.

## Inspect and enrich

Perform a **visual overview of every supplied PDF page** before detailed extraction so that important context tables or figures are not missed just because they lack a registered anchor. Record the pages actually viewed. Then inspect every eligible observation's primary/secondary locations and the relevant compositions, material treatments, solution descriptions, methods, captions, legends, scoped headers and footnotes in detail. Reuse a working context map only where the paper establishes shared scope.

Direct visual PDF access is acceptable; otherwise render pages and actually view the images, enlarging dense details as needed. Rendering a page, reading its path or searching its text layer does not count as viewing it. Embedded text may locate passages; verify consequential values and associations visually. Rendering/image viewing and arithmetic-free bookkeeping are allowed; automated OCR, table extraction, marker detection and curve tracing are excluded. Preserve the PDF.

Produce exactly one experiment per eligible supplied ID, in input order. Keep `observation_id` unchanged. Do not discover new records, merge possible duplicates, split a registered mean/range into replicates, or renumber a subset. An additional source may clarify context without creating an outcome. Do not filter on `result_type`; contextualize cited/interpolated/calculated/reference/unclear outcomes as far as the supplied paper supports, without following outside citations.

Copy the observation-level `pitting_potential` **unchanged from the raw registry JSON**, including nulls, original units, bounds, uncertainty and optional-field omissions. It is the primary reading already selected upstream. Do not choose a secondary value, normalize units, repair an apparent error or add default subfields. Copy from raw input when assembling saved JSON: generic model serialization can insert defaults; even `exclude_unset=True` cannot undo defaults the caller explicitly supplied.

Use the current data-field conventions for the context. Preserve original units and reported order of preparation/procedure steps. Do not calculate missing pH, chloride molarity, alloy balances, composition-basis conversions or typical temperatures; do not infer commercial compositions or seawater recipes. Distinguish processing temperature from test temperature, electrode filling solution from test electrolyte, sweep rates from potential steps/holds, and independent-variable coordinates from shared setup. A changing variable belongs to its own observation's context.

Carry source scientific qualifications into `result_note` and append relevant paper-derived clarification. Source contradictions or proposed registry corrections are notes, never permission to replace an anchor. A confirmed registry reading/association error is a recovery problem for `failure_notes`; genuine disagreement in the paper alone is a scientific qualification. Never resolve missing context by taking the most plausible alloy or by copying a benchmark value.

## Access limits and missing data

Missing text is `""`, collections `[]`, and numeric/measurement values null, as in the copied schema. All context fields are required. Ordinary unreported information is not automatically an extraction failure. Leave unresolved context empty/null and explain an actual recovery/association failure in `failure_notes`. Do not fabricate a complete-looking row. Previously partial contextual information may be recovered from other paper sections, so do not blindly retain a resolved failure; preserve scientific qualifications and unresolved problems.

With partial access, retain one record per eligible ID using the locked potential and any supported context. Flag affected recovery in `failure_notes`, and disclose inaccessible pages/sources in the report. If **all visual access fails** and eligible IDs exist, save an explanatory report without enrichment JSON; do not create empty or all-missing rows suggesting successful inspection. With no eligible IDs (empty or failed-only registry), `experiments: []` is valid without a paper survey; report that nothing was selected, not that the paper has no outcomes.

## Save and validate

Default outputs relative to the project root:

- `enrich-observations/<registry_stem>.json`
- `enrich-observations/<registry_stem>_report.md`

The output directory is separate from this skill's folder. Honor explicit destinations. Preserve both members of existing output pairs by choosing the next unused `_run_2`, `_run_3`, etc. stem unless replacement was requested; recheck at write time and use exclusive creation where practical. Create directories as needed. Write UTF-8 strict JSON without duplicate keys, NaN or Infinity. Use the actual preparation fingerprints, never example hashes.

```powershell
.\.venv\Scripts\python.exe .agents/skills/enrich-observations/scripts/validate_output.py --input enrich-observations/paper_49_matched_only.json --pdf "papers/49_example.pdf" --registry observation_registry/paper_49_matched_only.json
```

Both helpers are read-only: they create no reports or data files and do not inspect scientific PDF contents. Exit codes are **0** structurally valid data (including flagged records), **1** invalid data, **2** setup/I/O failure. The validator checks schemas/models, fingerprints, paper/reference consistency, exact eligible-ID coverage/order and unchanged raw anchored potentials. Its stdout supplies counts, skipped IDs and flagged IDs for the report. Repair structural mistakes without inventing scientific evidence. Validation does not certify visual inspection, context associations, qualification meanings or benchmark suitability.

Save a brief report for every attempted input, including invalid inputs and blocked attempts. Follow the [report checklist](references/enrichment_conventions.md#brief-report): actual overview coverage, detailed sources, access limitations, eligible/written/skipped counts, skipped failed IDs, flagged output IDs, concise shared qualifications and the actual validation result. Do not append per-observation narratives or an aggregate batch summary. If report saving fails, disclose the error and return its text in chat.

Finish with links to saved outputs and material limitations. Do not change registries, schemas outside this skill, matching outputs, datasets or dependencies; do not split/merge batches automatically, align to CRA, score benchmarks or load a database. For multiple PDF/registry pairs apply the workflow separately, keeping their IDs and fingerprints scoped to their own files.
