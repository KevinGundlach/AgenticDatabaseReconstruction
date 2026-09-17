# Series output conventions

## Paper and series

Root properties are `paper_name` (filename including extension, no directory), `reference_number` (nonnegative integer), and `series` (array). Match the filename's leading number when present; otherwise use the user-supplied reference. One document represents one paper. No version, type declarations, or point-level provenance fields are added.

Every series has `source`, `method`, `status`, `columns`, `rows`, and `notes`. For example, `source` can be `Figure 3(b), open circles, alloy B`. Include a PDF page number there when needed to locate unnamed/ambiguous sources. Use different source descriptions for different panels/series.

Columns contain `name` and optionally `default_unit` and `default_error_bar_type`. Names must be nonblank and distinct within a series. All rows have exactly the same length as `columns`; order supplies the mapping. Defaults live only on columns, never on series. Preserve compound unit labels such as `mV (SCE)` without splitting out a reference-electrode field.

## Cells

A cell is a string, finite number, null, or numeric object. Booleans and nested arrays are not cells. Strings preserve text, categorical labels, `Bal.`, or unusual notation. No categorical/text/unidentified discriminator is needed. Use ordinary numbers whenever no bounds, error bars, or overrides are needed.

Numeric objects allow only:

| Property | Meaning |
| --- | --- |
| `value` | Numeric central or explicit value |
| `min`, `max` | Numeric lower and upper endpoints; either can occur alone |
| `unit` | Override of the column unit for this cell |
| `plus_minus` | Nonnegative symmetric offset, requiring numeric `value` |
| `plus_minus_unit` | Unit for the offset, requiring `plus_minus` |
| `error_bar_type` | Override of the column's error-bar interpretation |

All object properties are optional individually, but at least one of `value`, `min`, or `max` is required. When present, those fields are numbers, never strings or null. An entire cell may be null. Omit absent optional fields rather than setting them to null.

Do not combine `plus_minus` with either bound. Require `min <= max` when both exist and require a central value to lie within any supplied bounds. A unit-only or interpretation-only object is invalid. Inclusive/exclusive fields are not used: retain `>300` as a string or preserve the original qualifier in notes when encoding a one-sided bound.

## Units and uncertainty

- A cell `unit` overrides its column `default_unit`; with neither, the unit is unspecified. All three of `value`, `min`, and `max` use this effective unit.
- `plus_minus_unit` inherits the effective value unit unless explicitly present. An explicit `%` means relative percentage uncertainty, not percentage points. Thus `20 +/- 2 wt.%` uses `unit: "wt.%"` and no offset-unit override; `20 wt.% +/- 2% relative` uses `plus_minus_unit: "%"`. Preserve ambiguous notation as text rather than guessing.
- Cell `error_bar_type` overrides the column default; with neither, interpretation is unknown. Explicit `unknown` overrides a known default. There is no further cascade.
- Use categorical strings, not a separate confidence-level property. Initial labels: `stdev`, `stderr`, `minmax`, `confidence_interval_95`, `confidence_interval_90`, `unknown`. Other source-supported labels are permitted, e.g. `stdev_2`, `confidence_interval_99`, `tolerance`. Explain unusual categories once in notes. The schema intentionally accepts nonblank strings rather than imposing a closed enum.
- `stdev` means one standard deviation. Preserve stated multipliers and confidence levels. Do not infer meaning from the shape or symmetry of the bars. Locate the explanation in captions, footnotes, or paper text and cite that location in notes when consequential.
- Bounds are observed sample extrema only for a source-supported `minmax` interpretation. Otherwise they describe the stated interval. Error bars do not represent digitization confidence. If bounds have different units that cannot fit one cell faithfully, retain the original expression as text and explain.

## Methods and statuses

`transcribed` means numbers are explicitly printed, including numerical annotations on a plot. `digitized` means coordinates or endpoints are visually estimated. Reading printed labels does not make a digitized series mixed. If central values are printed but endpoints are digitized, choose `digitized` and explain once in notes.

| Status | Required content |
| --- | --- |
| `complete` | Nonempty rows and columns; all eligible entries within this series' stated scope captured |
| `partial` | Nonempty rows and columns; notes explain omitted/unreadable/unresolved information |
| `none` | Empty rows; notes explain why no reliable rows could be extracted; columns may be empty |

Source blanks and faithfully retained raw text can occur in a complete transcription. Unreadable cells should be null with explanatory notes and a partial status if source information was lost. Preserve meaningful placeholders such as `not tested` as strings; do not interpret them as zero.

Emit `none` only for a source actually identified and inspected. A paper with no eligible sources can have `series: []` after inspection. Mention out-of-scope exclusions in the run report rather than inventing rows. A structurally valid checkpoint does not certify paper-wide completeness.

## Illustrative output (invented data)

```json
{
  "paper_name": "80_example.pdf",
  "reference_number": 80,
  "series": [
    {
      "source": "Table 1, alloy compositions",
      "method": "transcribed",
      "status": "complete",
      "columns": [
        {"name": "Sample"},
        {"name": "Cr", "default_unit": "wt.%"},
        {"name": "Fe", "default_unit": "wt.%"}
      ],
      "rows": [["A", 18, "Bal."], ["B", {"value": 120, "unit": "ppm"}, "Bal."]],
      "notes": "Bal. is preserved as reported; no balance percentages calculated."
    },
    {
      "source": "Figure 3(a), alloy A, circles",
      "method": "digitized",
      "status": "partial",
      "columns": [
        {"name": "pH"},
        {"name": "Epit", "default_unit": "mV (SCE)", "default_error_bar_type": "confidence_interval_95"}
      ],
      "rows": [
        [2, {"value": 300, "min": 280, "max": 320}],
        [4, {"value": 350, "min": 325, "max": 375}],
        [6, null]
      ],
      "notes": "Caption defines bars as 95% confidence intervals. The result at pH 6 is obscured."
    }
  ]
}
```
