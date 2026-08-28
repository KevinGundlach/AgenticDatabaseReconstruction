# Structural parsing guide

## Coordinates and spans

- Grid coordinates are one-based and inclusive.
- A merged cell occupies every position from `row_start` through `row_end` and
  `column_start` through `column_end`.
- Do not duplicate a merged cell into the positions it covers.
- Cell IDs must be unique within a grid. Use concise IDs such as `r1c2` or
  `r2c1_r4c1`.
- Cells may not overlap. Every visible logical cell must be represented,
  including empty cells that affect structure.

## Cell roles and values

- `column_header`: labels a column or group of columns.
- `row_header`: labels a row or group of rows.
- `corner_header`: header at the intersection of row and column headers.
- `section_header`: divides repeated sections inside one grid.
- `stub`: structural label that is not itself a data-series header.
- `data`: observed table content.
- `blank`: a visibly empty physical cell.
- `unknown`: use only when the role cannot be resolved.

Always preserve the visible transcription in `raw_text`, including meaningful
symbols and line breaks. Set `value` conservatively:

- Use a JSON number for an unambiguous numeric value.
- Separate visible footnote markers, so `0.2*` has `raw_text: "0.2*"`,
  `value: 0.2`, and `footnote_markers: ["*"]`.
- Use a string for textual, categorical, inequality, range, formula, or
  otherwise non-scalar content.
- Use `null` for a genuinely blank cell, an explicit missing-value mark such as
  an em dash, or illegible content. Preserve the mark in `raw_text` and explain
  illegibility in `notes`.

## Header links

For each data cell, list every effective header cell ID:

- `row_header_ids` contains the direct row label and any parent row-group
  headers.
- `column_header_ids` contains the leaf column label and all merged parent
  headers.
- Keep both arrays empty for header and structural cells.

For example, a nitrogen composition value under `Composition, %` links to both
the `N` leaf header and the merged `Composition, %` parent header. A value in a
three-row Ti group links to the merged `Ti` row header.

## MinerU comparison

- `consistent`: structure and visible text agree apart from inconsequential
  whitespace.
- `minor_errors`: isolated OCR or formatting errors do not change the table
  structure.
- `major_errors`: merged rows, columns, headers, or values materially alter the
  table.
- `unusable`: HTML cannot be aligned reliably with the visible table.
- `not_available`: no MinerU HTML was supplied.

The parsed image remains authoritative for every status.
