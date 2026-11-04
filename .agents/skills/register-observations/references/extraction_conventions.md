# Observation registry conventions

Version 1.1 is the paper-derived handoff for later context extraction. Each observation represents an identifiable, condition-specific numerical pitting-related value or bound, with supported equivalent presentations nested in `locations`. It contains no database matches and is not a complete experiment dataset. Broad screening ranges across unspecified conditions and purely qualitative statements go in the report. A mean/range for one condition is eligible; retain its meaning in `result_note`.

## Required fields and missing information

Root, observation, and applicable location/condition fields are required, including `result_type` and `extraction_status` without defaults. Missing text is `""`; empty collections are `[]`; unavailable measurements/condition values are null. None means zero or explicit scientific absence. Reject unmodeled fields. Only measurement subfields may be omitted. Required location labels may be empty if genuinely unavailable. Source omissions do not alone make extraction incomplete. Explain a recovery problem in `failure_notes` only when the paper appears to provide information the extractor cannot recover.

Existing 1.0 registries and reports are preserved. The current classes/schema/validator accept 1.1 only. Do not fill new fields by guessing from old notes or silently upgrade existing outputs; a fresh extraction or explicitly requested classification review is necessary.

`observation_id` is a registry-scoped bookkeeping key. Assign `obs_001`, `obs_002`, etc. when creating a registry; retain established IDs during edits, even if deletions leave gaps. Preserve author-supplied sample names separately in `sample_label`. Do not derive IDs from target values, composition, or any database identifier.

## Measurements and qualifiers

Use the five-field measurement shape: `value`, `min`, `max`, `unit`, `plus_minus`. At least one finite numerical value/bound is required. Null applies to the whole measurement when no numerical value/bound can be read; `{}`, unit-only objects and all-null numerical subfields are invalid. Optional numerical subfields can be omitted or null, and `unit` can be omitted or `""` but is never null.

Retain reported units and stated electrode reference, e.g. `V (SCE)` or `mV (Ag/AgCl, saturated KCl)`. Do not add details the paper does not state. Expand truly shared table/axis units into the affected measurements, but do not normalize units or convert reference scales. Dimensionless numeric coordinates (including pH) use a measurement such as `{"value": 7}`; condition/coordinate values are text, measurements or null, never bare numbers or booleans.

`plus_minus` is a nonnegative symmetric offset in the same unit as a numerical `value`. Do not calculate it from bounds, treat relative percent as an absolute offset, or substitute digitization uncertainty. Preserve asymmetric interval/error-bar endpoints with `min`/`max` where recoverable. Use only defensible graphical precision. The validator checks bound ordering and that a central value lies within supplied bounds.

Put source statistical meaning, strict inequalities, no-pitting limits, annotations and distinctions such as scan/scratch in `result_note` when needed. For a source-reported `Epit > 800 mV (SCE)`, a lower bound plus the original inequality preserves the qualification without asserting pitting at 800 mV. Do not turn a range into an unreported midpoint/mean or invent replicates underlying a reported summary. A purely qualitative no-pitting statement goes in the report; retain a numerical bound only when the paper supports that interpretation. Do not invent a bound merely to make a qualitative statement eligible.

## Result origin and extraction status

`result_type` describes the origin of the potential selected from `primary_location`, independently of its scientific credibility and the extractor's reading method:

| Value | Meaning |
|---|---|
| `reported_experimental` | Reported from the authors' own experiments, including routine summaries of measured replicates. |
| `interpolated` | Explicitly estimated between other results. |
| `calculated` | Explicitly derived through a calculation or model, beyond routine summaries of measured replicates. |
| `cited` | The reported value is attributed to another publication/external source. |
| `reference_value` | Explicitly presented as a standard, conventional, or reference value. |
| `unclear` | The paper reports a value but does not establish its origin. |

Use `reference_value` when the paper explicitly assigns that standard/conventional role, including with a citation; otherwise use `cited` for an externally attributed value. A cited result may itself have been calculated/interpolated: keep `cited` and explain the derivation in `result_note`. If the present authors derive a new value from cited inputs, classify their new value as calculated/interpolated. Use the more specific interpolated category when that method is explicit. Do not infer provenance or industry-standard status from common knowledge. Classify the primary reading; describe differently derived alternative presentations in `result_note` when relevant, and consolidate only when correspondence is supported.

Reading a plotted experimental point is digitization, not interpolation. Routine experimental means/ranges retain experimental origin and their statistical qualification. Classify the target potential, not how an electrolyte concentration or other contextual field was obtained. A known experimental origin remains `reported_experimental` when the paper leaves the physical meaning or measurement criterion uncertain.

`extraction_status` describes recovery of the registry information:

| Status | Requirements and default routing |
|---|---|
| `complete` | Recovered as far as the paper supplies. Potential is non-null; `failure_notes` is exactly `""`. Continue to enrichment/alignment attempts. |
| `partial` | A recovery problem remains, but useful information/anchors survive. `failure_notes` must contain non-whitespace text. Potential may be null. Continue with the limitation retained. |
| `failed` | Recovery is insufficient for useful automatic processing. `failure_notes` must contain non-whitespace text. Preserve any recovered data and location; retain for review instead of continuing automatically. |

Partial/failed entries describe identifiable numerical occurrences that could not be fully recovered, not general qualitative statements or invented placeholders. Status is an extractor judgment about recovery, not a claim that an observation is true or false. An unreported alloy identifier, unknown origin, source conflict, or unresolved duplicate relationship does not alone lower status. Missing expected database fields and lack of a database counterpart must not influence registration.

Do not automatically exclude a `result_type`. Downstream selection uses status (`complete` or `partial` continue), not whether notes are present. Later stages may still fail to enrich or align the observation; completion does not guarantee benchmark suitability. Validation exit 0 means the file is structurally consistent, even when every contained observation has failed status.

## Source-specific locations

Every location has:

- `kind`: `table`, `plot`, or `text`.
- `pdf_page`: one-based page in the supplied PDF. Do not substitute the printed page number.
- `printed_page`: original page label as text, or `""` if absent.
- `reading_method`: `transcribed` when numbers are printed, `digitized` when a value/endpoint is graphically read. Printed labels alone do not make a graphical reading transcribed. Use digitized when a central value is printed but an endpoint is read graphically.
- `pitting_potential`: the reading at this location, in original units, or null when no numerical content is recoverable.

Additional fields depend on `kind`:

| Kind | Required selectors |
|---|---|
| `table` | `table_label`, `row_label`, full `column_label`, and `conditions` for additional scoped conditions distinguishing the cell. |
| `plot` | `figure_label`, `panel_label`, `series_label` including its symbol where useful, and independent-variable `coordinates` identifying the marker/bar. |
| `text` | `section_heading` and short exact `text_anchor` quotation identifying the passage. |

Do not swap selectors between variants. For an unlabeled table row, `row_label` may be a concise positional description using visible landmarks. For overlapping plot markers, retain the recoverable coordinate/symbol and explain whether information is absent from the source (`result_note`) or cannot be recovered despite appearing available (`failure_notes` and partial/failed status). No bounding boxes or external image paths are required. If a numerical outcome is only described in a caption, use a text location with a caption-identifying section heading and exact anchor unless a specific point/cell is actually identified.

Each coordinate/condition has `name` and `value`. Preserve the paper's terminology and concentration/composition basis rather than mapping names to database columns. Logarithmic-axis labels should remain explicit; do not silently describe a log coordinate as an untransformed concentration. Store categorical selectors as text. These are the selectors needed for this outcome, not a copy of every experimental detail.

`sample_label` preserves a stated author identifier; leave it empty if unavailable. `association_notes` supplies a short paper-derived linking clue not already expressed by the selectors, e.g. that the caption identifies solution-treated specimens. It must not become a full preparation/electrolyte/procedure summary.

## Consolidation and the primary reading

Consolidation is a scientific association made from the paper, not a numeric deduplication operation. A matching number can occur for different materials, conditions, replicates, or methods. A plot and table can also give slightly different readings of the same outcome. Combine them only when sample/condition labels, captions, or text support correspondence. Preserve separate outcomes when the relationship remains uncertain, using their IDs in `result_note` to identify a possible duplicate after IDs have been assigned. This uncertainty alone does not lower extraction status or justify treating retained records as independent experiments.

Separate scan and scratch pitting results are distinct observations even if they occupy the same table row. A source-reported mean with extrema/bounds describing that same condition's outcome is one observation; do not create three separate experiments from those endpoints. If their grouping is unclear, explain it in `result_note` instead of inferring aggregation.

`primary_location` is a zero-based index into the nonempty `locations` array. `pitting_potential` at observation level must copy that location's measurement exactly, including units and supplied bounds/uncertainty. Prefer an explicit number over approximate digitization when correspondence is established. Never average source readings or convert units to synthesize a primary value. Reordering/removing locations requires updating the index. Different units/readings at other locations are retained independently; their presence alone does not prove a conflict. Explain unresolved source disagreements in `result_note`. Selecting a primary reading is a storage choice, not a resolution of which published reading is scientifically correct.

## Scientific qualifications versus failures

`association_notes` gives paper-derived linking clues for later context extraction. `result_note` clarifies scientific meaning, provenance uncertainty, source conflicts, and unresolved duplicate relationships. `failure_notes` describes what the extractor could not recover despite the paper appearing to provide it. All remain required text. Keep the existing singular `result_note` spelling. Missing unreported information is not itself a failure.

Examples of recovery failures (`failure_notes`, with partial/failed status):

- A legend appears to supply an alloy/series assignment, but its symbol or text cannot be read after enlargement.
- A reported digit is illegible after enlargement; retain the location and set its measurement to null.

Examples of source qualifications (`result_note`, without lowering status solely for that reason):

- The authors use a current-criterion proxy when a definite pitting threshold is not evident, but do not identify affected markers. Each recovered numerical marker can be complete and reported_experimental while retaining the conditional criterion and uncertainty. Do not assert every point is a proxy.
- A table and plot give conflicting values or conditions. Preserve both source readings when correspondence is supported, choose a primary, and document the disagreement without treating accurate recovery as failed extraction.
- A plot/table pair may be duplicates but the paper provides insufficient run information. Retain separate observations and describe the possible relationship.
- The paper clearly reports a value but omits its origin or alloy identity. Use `unclear` only if origin is unknown, leave unreported text empty, and describe the relevant source limitation.

The Paper 3-style statement that screening spanned 100-500 mV across unspecified alloys belongs in the report, as do qualitative edge-pitting observations without a numerical value/bound. They are outside registry scope, not failed extractions. Current-time bounds for identifiable conditions remain eligible, with their method/inequality in `result_note`.

Clearly unrelated quantities are excluded, with a brief reason in the coverage report. Unenumerable/unseen sources and paper-wide access failures belong in the report rather than fabricated placeholder observations. Statuses and schema validation do not establish scientific correctness or complete paper coverage. Report complete/partial/failed counts from the saved categorical field, list partial/failed IDs, and describe significant source qualifications separately in short shared notes.
