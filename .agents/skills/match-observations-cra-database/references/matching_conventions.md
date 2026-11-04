# Alignment conventions

## Identity and comparison are separate

An alignment link says that a supplied observation corresponds to a CRA record. A numerical disagreement can coexist with a supported identity when material/condition/source evidence identifies the counterpart independently. Explain both. An accepted link is an automated proposal, not proof of scientific truth or human confirmation.

Source-reported provenance, current-criterion proxies, uncertain physical meaning, source contradictions and unresolved repeated presentations do not alone exclude a known experimental result. Preserve relevant qualifications in the alignment's `shared_qualifications` or link notes. Never turn a different quantity, such as corrosion/repassivation/imposed potential, into pitting potential simply to fit a target.

For `complete` and `partial` entries assess the registered source using the paper. A partial result with a null potential can have a supported context-based identity if evidence genuinely suffices, with `potential_agreement: "not_comparable"`. Failed entries remain `not_assessed`; carry their failure explanation forward, without reclassifying the registry. Source uncertainty alone must not be treated as extraction failure.

## Root and input scope

All output fields are required. Use `""` for unnecessary free text and `[]` for empty collections; the output format has no nullable measurements because readings remain in the immutable registry. `inputs.pdf`, `inputs.csv` and `inputs.registry` each have `filename` (basename) and lowercase hexadecimal `sha256` of original bytes. Preserve `paper_name` and the resolved positive `reference_number` from preparation. The output has `schema_version: "1.0"`.

`inspected_pdf_pages` lists unique one-based pages actually viewed; it does not certify full-paper coverage. `coverage_notes` discloses relevant limitations and actual access errors. `shared_qualifications` is a list of short nonblank shared notes. Mention affected IDs/CRA rows and label reusable conversions C1, C2, etc. when helpful. An example fingerprint cannot be used for real inputs.

Registry version 1.1 is accepted, including valid subsets with gaps in IDs. Earlier schemas are rejected, without inferring classifications. The CSV must have `No.`, `Reference`, `Avg Epit mV (SCE)`, `Min Epit mV (SCE)` and `Max Epit mV (SCE)`; other headers supply association evidence. UTF-8 and UTF-8 with BOM are supported; an encoding error is a diagnostic, not permission for lossy decoding. All data rows must have a single positive Reference. An empty CSV is permitted if another input resolves the reference.

Preparation checks the registry reference, CSV Reference, leading PDF/registry-paper numbers, trailing CSV `_number`, and registry `paper_number...` filename when present. Conflicts block matching. Preserve cell strings, whitespace, missing markers, quotes and multiline contents. Numeric identifier forms such as `49.0` resolve to integer 49; duplicates are checked after resolution. Do not normalize scientific field strings. Missing numeric cells are not zero; literal text such as heat treatment `None` is not globally replaced with missing data.

## Observation results

Each result has `observation_id`, `status`, `matches`, `candidates` and `notes`. Exactly cover supplied IDs in original order. Required statuses have no defaults:

| Status | Meaning / requirements |
|---|---|
| `matched` | At least one supported link; additional unresolved candidates may remain. |
| `ambiguous` | No supported links, at least one candidate, and nonblank explanatory notes. |
| `unmatched` | Assessed without a defensible counterpart in the supplied CSV; no links and nonblank notes. |
| `not_assessed` | Blocked/skipped, including failed registry entries; no links and nonblank reason. |

No `citrine_no` can occur twice within an observation's combined matches/candidates. Distinct CRA IDs may be supported for one observation, and one CRA ID may be supported for multiple observations. Do not impose one-to-one assignment, arbitrarily choose a winner, or trim candidates to a fixed count. Preserve all defensible alternatives, not every coincidental number.

Explain each supported shared row: it may represent equivalent/possibly repeated presentations, duplicate database records, or individual readings included in a database range/summary. These are different relationships. Several readings sharing conditions do not prove they are the same run; replicate identity remains uncertain unless supported. A possible shared condition without enough evidence for counterpart identity remains a candidate. Never manufacture a mean or treat a single replicate as the reported aggregate. Do not merge observations, change primary readings or resolve a source contradiction by choosing the value closest to Citrine.

`unlinked_citrine_nos` is every supplied CSV No. with no supported link, preserving CSV order. Candidate-only rows remain unlinked. Do not infer that unlinked records were absent from the paper, or search for unregistered outcomes to complete coverage. There is no automatic cross-batch merge; registry-scoped IDs from independent regenerations are not interchangeable. Default downstream joins use supported links only and must account for shared CRA rows rather than silently expanding benchmark counts.

## Link evidence

Both accepted and candidate links use the same shape:

- `citrine_no`: original positive No. identifier.
- `location_indices`: nonempty, unique zero-based indices of supporting registered locations. Their PDF pages must appear among inspected pages. Use secondary locations when relevant without replacing primary values.
- `cra_potential`: `avg`, `min`, `max` are exact strings from the three original target columns. Include blanks, `NA`, `>800` or `Transpassive` unchanged. Do not replace a cell with a parsed number.
- `potential_agreement`: `exact`, `within_precision`, `discrepant`, or `not_comparable`.
- `evidence`: nonempty list of `{field, paper_value, cra_value, comparison}`. `field` is an exact CSV header, `cra_value` its exact original cell, and `paper_value` the paper's actual reading/units or explicitly unavailable information. `comparison` pairs the values, their roles and any conversion arithmetic/limitation. Record decisive non-potential evidence, not just a target coincidence. A missing supporting field belongs in notes, not an invented CSV column.
- `notes`: nonblank identity rationale and qualifications. For shared rows explain summary-member versus possible repetition. For candidates state what prevents assignment. Locate newly consulted contextual evidence briefly here (page/table/section); do not reconstruct every field's provenance.

Keep paper readings in original units. Describe comparison calculations separately. If a registry reading conflicts with visible paper content, identify that disagreement explicitly in notes/evidence; never silently repair the registry or substitute an unregistered location. Strong independent identity may still support a discrepant link; otherwise retain a candidate. No evidence can be invented by copying a CSV value to the paper side.

Use potential agreement for comparable target roles: `discrepant` if a justified comparison contradicts a populated target; otherwise `within_precision` for compatible rounding/digitization, or `exact` for established exact agreement. Use `not_comparable` if no defensible numerical/semantic potential comparison can be made. Explain partially comparable avg/min/max roles individually in evidence. Blank targets do not count as disagreement; `Avg` is not proof of a mean. A range member can link to a summary row without asserting that it equals a central value. No fixed tolerance or numerical confidence score is prescribed.

Do not convert `Transpassive` to a number or an inferred pitting bound. A numerical observation and qualitative CRA target require explicit paper-supported counterpart identity; matching alloy/conditions alone does not establish that different outcome quantities are equivalent. Without adequate evidence retain a candidate or leave the row unlinked. Preserve the qualification even if identity is supported.

## Compact report and error behavior

After validation, `validate_output.py --report-stdout` renders exactly one Markdown table row per supplied ID. It includes original readings/locations, supported/candidate CRA IDs, original targets, decisive paired variables/conversions and status. Counts and shared groups are derived from the saved alignment, not prose. Original multiline CSV cells are preserved in JSON and rendered inline safely; literal pipes are escaped. Avoid per-observation headings and repeated paragraphs.

Shared notes cover scientific criteria, source disagreements, conversions, duplicate groups and limitations once. A blocked visual run still has a structurally valid alignment, with affected IDs not assessed, and must disclose its failure. Invalid inputs instead get an explanatory report and no success-shaped alignment; helpers report diagnostics only, so the agent saves that error report. Structural validation is not a scientific check, and invalid outputs must not be accompanied by a PASS report.

## Scenario review

- Paper 3 pattern: preserve scan/scratch distinctions and individual runs. One CRA range can correspond to several registered readings; unsupported extra source observations can remain unmatched without being extraction failures.
- Paper 9 pattern: a paper may leave individual current-criterion substitutions unidentified. Retain the shared scientific qualification; do not automatically downgrade otherwise recoverable identities or claim all outcomes are confirmed pitting thresholds.
- Paper 49 pattern: inconsistent table/plot concentrations and conflicting potentials do not justify guessing corrections. Compare actual registered readings, retain discrepancies, and leave unresolved identities as candidates. Shared assignments do not prove all source presentations are duplicate runs.

These are decision scenarios, not expected assignments or permission to read prior matching reports. Do not encode paper-specific row mappings into this skill.
