---
name: match-observations-cra-database
description: Match a full or partial paper observation registry to original Citrine CRA pitting-potential row IDs using the supplied PDF, paired context, and justified unit conversions. Produce separate alignment JSON and a compact report, retaining ambiguous alternatives without changing the paper-only registry.
---

# Match Observations to the CRA Database

Given one paper PDF, its paper-specific CRA pitting-potential CSV, and a full or partial **version 1.1** observation registry, assign supported original `No.` identifiers to supplied observation IDs. Save a **version 1.0 alignment JSON** plus a brief Markdown report. This is identity alignment, separately from numerical agreement; it is not experiment enrichment or benchmark certification.

Read [matching conventions](references/matching_conventions.md), the [output schema](references/observation_alignment.schema.json), and [conversion guidance](references/unit_matching.md) before matching. The [invented example](references/example_alignment.json) has corresponding [registry](references/example_registry.json) and [CSV](references/example_cra.csv); its fingerprints are illustrative, not fingerprints of real experimental inputs. The local [registry schema](references/observation_registry.schema.json) and [Pydantic definitions](scripts/observation_registry.py) freeze the accepted input contract. Everything needed for validation is bundled here.

## Prepare the inputs

Resolve relative paths from the project root. Run the read-only helper with the project's existing Python environment (`pydantic>=2.13.5`, `jsonschema>=4.23,<5`):

```powershell
.\.venv\Scripts\python.exe .agents/skills/match-observations-cra-database/scripts/prepare_inputs.py --pdf "papers/49_example.pdf" --csv citrine_database/by_reference/pitting_potential_49.csv --registry observation_registry/paper_49.json
```

Its stdout supplies original CSV strings, registry data, the resolved literature reference and SHA-256 fingerprints. Use `No.` as the stable CRA identifier, never CSV record/line position. Inspect every supplied observation and every supplied CSV row as potential matching input. A partial registry is a valid root object with a subset of existing observations and unchanged IDs; do not require contiguous IDs, renumber, or supplement it. Reject unsupported versions without upgrading them.

Resolve reference conflicts before scientific work. A renamed PDF warning requires verifying that the PDF is the registry's paper; a consistent number alone is not visual proof. Preserve all inputs. On invalid input or setup failure, save an explanatory report with the actual diagnostic, identify validation as failed/not applicable, and do not create a success-shaped alignment. The helper does not create that report.

## Verify and align

Use only the supplied PDF, registry and CSV for experimental evidence. Do not read previous locating reports, other extraction outputs, or enrichment results. Authoritative external references may supply conversion constants only. Alignment sees Citrine; keep its outputs and this chat out of any later blind enrichment context.

Visually inspect each relevant registered anchor and the captions, footnotes, methods or material descriptions needed to distinguish counterparts. Direct visual PDF access works; otherwise render pages and actually view the images, enlarging dense labels and symbols. Text search may locate passages, but paths, rendered images not viewed, and text-layer hits do not establish visual verification. Record one-based pages actually viewed. Do not run OCR, automated table extraction, marker detection or curve tracing. Code may render images, perform arithmetic on values read by the agent, prepare JSON and validate bookkeeping.

Match only supplied IDs. Consider every registered location, including secondary readings, and retain the indices supporting each link. Do not rewrite the registry, select a new primary, consolidate observations, infer unannotated pitting thresholds from continuous curves, or invent observations for unlinked CRA rows. A full-paper census is not required: consult additional paper sections only as necessary to resolve supplied observations.

Use minimum decisive context rather than reconstructing every database field. Pair every variable actually used with its original CSV cell and paper value/units; potential equality alone is insufficient. Distinguish source omissions, source conflicts, recovery problems and unresolved duplicate identities. Follow the conventions for supported shared links, summaries, discrepant targets, qualitative targets, and candidate-only assignments. Do not assume the CSV or registry is scientifically infallible.

Assess `complete` and `partial` inputs. Keep `failed` inputs as `not_assessed`, retaining their recovery limitation in `notes`. Do not exclude an origin category or an observation merely because it has scientific qualifications. If visual access is blocked, do not claim absence: save a valid alignment with affected IDs `not_assessed` and the actual access error in coverage notes. With no visual access at all, all IDs are `not_assessed`; save its report as well. An empty supplied registry can produce an empty alignment without implying that the paper has no outcomes.

## Save and validate

Default destinations relative to the project root:

- `observation_matches/<registry_stem>.json`
- `observation_matches/<registry_stem>_report.md`

Honor explicit destinations. Unless replacement was requested, preserve both members of an existing output pair: select the next unused `_run_2`, `_run_3`, etc. JSON stem for which neither companion exists. Recheck at write time and use exclusive creation where practical. Create the output directory as needed. Write UTF-8 strict JSON, rejecting extra fields, duplicate keys, NaN and Infinity. Copy fingerprints from prepared input, not invented examples.

Use the schema's required fields and [conventions](references/matching_conventions.md). Include every supplied ID once and in order. `unlinked_citrine_nos` is the complement of supported links in original CSV order; candidate-only rows remain unlinked. This describes only this exact supplied registry, not paper-wide absence. Never combine independently regenerated IDs or auto-merge batches.

```powershell
.\.venv\Scripts\python.exe .agents/skills/match-observations-cra-database/scripts/validate_output.py --input observation_matches/paper_49.json --pdf "papers/49_example.pdf" --csv citrine_database/by_reference/pitting_potential_49.csv --registry observation_registry/paper_49.json
```

Exit codes for both helpers: **0** structurally valid data (including ambiguity/blocked assessments), **1** invalid data, **2** setup/I/O failure. They write no files, perform no scientific PDF inspection, and do not certify conversion arithmetic or assignments. Repair structural mistakes without inventing evidence. Record actual validation errors if a file cannot pass.

After successful validation, rerun the validator with `--report-stdout` to obtain the compact report and save that stdout to the chosen report destination. This mode still writes no files. It creates one row per supplied observation, status counts, shared-row groups, unlinked IDs, shared qualifications, inspected pages/access limitations and the actual structural validation result. Keep scientific notes brief; do not append per-observation narratives. If report writing fails, disclose the error and return the report text in chat.

Finish with links to the alignment and report and material limitations. Do not update datasets, run database imports, implement enrichment, score a benchmark, or assert that matching proves which presentation the original curators used. Default joins use `matches`, never `candidates`; shared row assignments require care to avoid counting a CRA row repeatedly.
