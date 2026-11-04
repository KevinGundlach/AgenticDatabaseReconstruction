# Compact Markdown comparison report

The comparison table is the main deliverable. Do not add per-row headings, repeated targets/context, ranked-candidate paragraphs, or routine manual-review questions. Put row-specific evidence and issues in the table. Describe a recurring caveat or conversion once in short shared notes, referenced from the affected cells.

## Opening

Use a short input/coverage paragraph: CSV/PDF filenames, resolved literature reference, selected-row count, supplied and visually inspected one-based PDF pages, printed-page correspondence if available, and limitations. State once that matches are automated proposals. `Avg` is the database's label, not proof of a source-reported mean; missing markers are not zero.

## Comparison table

Use this exact header and original CSV row order, one table row per selected identifier:

| Citrine No. | Database target value(s) | Paper pitting potential(s) | Other matching variables (paper / Citrine) | Best proposed location | Conversion / comparison | Assessment |
|---|---|---|---|---|---|---|

- **Database target value(s):** use the helper's `target_display` verbatim: all three original column labels and cell strings, including missing markers. Do not normalize or reformat database numbers. Their units are in the labels, mV (SCE).
- **Paper pitting potential(s):** record the source number(s), original units and electrode reference, paper's potential label when useful, and `printed` or `~digitized`. Retain bounds, error bars, scan/scratch distinction and statistical roles where present. Do not replace this cell with a converted value. If unavailable, state why (e.g. `Not located`, `Not assessed`, or `Value unreadable`).
- **Other matching variables (paper / Citrine):** pair each variable actually used to identify the observation as `<variable>: paper=<reported value and units>; Citrine=<original cell string and dataset units>`. Use `<br>` between pairs if helpful. For an Epit-versus-Nb plot, Nb is required; include additional series-defining variables such as temperature or solution if used. Composition elements in this dataset use wt%; pH is dimensionless. Pair categorical values too when relevant. A missing counterpart or a discrepancy must be labeled, not described as a match. Do not dump the entire CSV record or reconstruct every field's source. Use `None established` when no independent association is recoverable, or `Not assessed` for a blocker; numerical coincidence alone cannot support a strong candidate.
- **Best proposed location:** give a precise target locator. Plot: PDF/printed page, figure/panel, series or symbol, and independent-variable coordinate. Table: page, table, row/sample and target-column header. Passage: page, section/paragraph and a short identifying phrase. Do not add full provenance locators for every supporting variable. State an absent/unreadable locator component rather than inventing it.
- **Conversion / comparison:** show any required arithmetic and the paper value in Citrine units, followed by agreement or discrepancy for each populated target and relevant variable. Define differences as converted paper minus Citrine. Same units may simply say `Same units; exact agreement`. For plots/rounded values say `within visual/printed precision`, with a defensible discrepancy if recoverable; do not invent a fixed tolerance. If conversion is underdetermined, say `Not comparable` and identify the missing input. Reusable formulas/constants can be a short shared note (e.g. C1); keep each row's converted result and comparison here. Preserve the distinction between a strong source location and a discrepant number.
- **Assessment:** exactly one of the four labels below.

Keep each Markdown row on one physical line. Escape literal pipes as `\|`. Use brief phrases; `<br>` is available for pairs or genuine alternatives. Do not bury all evidence in linked prose. If a row is ambiguous between distinct observations, label up to three alternatives A/B/C consistently across the source-value, paired-variable, locator and comparison cells. Do not create duplicate rows for alternatives. Equivalent presentations of one observation can share a locator cell.

Assessments:

- **Strong candidate:** a specific observation and its association are well supported. A numerical discrepancy can coexist with this location assessment when independent context identifies the observation; show the discrepancy.
- **Ambiguous:** competing observations, a weak value-only lead, or unresolved identity/interpretation/conversion prevents a defensible unique match. State the issue briefly.
- **Not located:** relevant paper coverage was inspected without finding a defensible candidate.
- **Not assessed:** access or coverage prevented assessment. A candidate found within limited coverage can still be shown with that limitation disclosed.

Preserve one-to-many assignments and possible duplicate database records; do not force a unique source per row. Do not treat another potential/current criterion as Epit without the paper's support.

After the table, include derived totals (including zeros):

`Assessment totals: Strong candidate=0; Ambiguous=0; Not located=0; Not assessed=0`

## Short shared notes and validation

Only add notes needed to explain shared conversions/assumptions, ambiguity groups, potential duplicates, conflicting or non-pitting results, and incomplete coverage. Name affected identifiers. Avoid a paper-wide methods summary, an inventory of unrelated results, and per-row prose. End with a short structural validation result; it does not verify PDF fidelity, arithmetic or scientific assignments.

For zero selected rows, retain the empty table and zero totals and explain that selection outcome. For access failure after selection, keep every selected row with its original targets, `Not assessed` and concise blocker cells; explain the blocker once. For CSV input failure, save an input-failure report and mark coverage validation not applicable.

## Illustrative row (invented values)

| Citrine No. | Database target value(s) | Paper pitting potential(s) | Other matching variables (paper / Citrine) | Best proposed location | Conversion / comparison | Assessment |
|---|---|---|---|---|---|---|
| 12 | Avg Epit mV (SCE): 300; Max Epit mV (SCE): NA; Min Epit mV (SCE): NA | ~0.30 V (SCE), digitized | Nb: paper=0.005 mass fraction; Citrine=0.5 wt% | PDF p. 4 / printed p. 104, Fig. 3(b), open circles, Nb mass fraction 0.005 | Epit: 0.30 x 1000 = 300 mV (SCE), delta Avg=0 mV, within visual precision; Nb: 0.005 x 100 = 0.5 wt%, exact agreement | Strong candidate |
