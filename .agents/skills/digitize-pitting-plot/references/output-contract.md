# Digitized pitting-plot output contract

Write one schema-version-2 JSON object for one staged image/metadata pair. The
machine-readable contract is [digitization.schema.json](digitization.schema.json).

```json
{
  "schema_version": 2,
  "paper_reference": "9",
  "source_chart_manifest": "paper_9_charts.json",
  "plot_metadata": {
    "chart_id": "page_0008_item_0002",
    "image_path": "images/source-image.jpg",
    "caption": "Fig. 9. ...",
    "reason_code": "direct_pitting_potential_plot",
    "reason": "Pitting potential is directly plotted.",
    "confidence": 0.98,
    "relevant_panels": [],
    "target_series": ["Ni80Cr20 pitting potential"],
    "x_axis": {"label": "pH", "unit": "", "scale": "linear"},
    "y_axis": {"label": "Ep", "unit": "mV", "scale": "linear"}
  },
  "digitization_status": "complete",
  "digitization_notes": [],
  "plot_data": []
}
```

The preparation script copies the three upstream metadata fields. Do not edit
them while digitizing.

## Status

- `complete`: all visible discrete target series were digitized.
- `partial`: some reliable target data were digitized; explain omissions in
  `digitization_notes`.
- `needs_review`: no points are emitted because interpretation is unresolved;
  explain why.
- `skipped`: no points are emitted because the geometry is outside the current
  scope; explain why.
- `unprocessed`: preparation-template value only. Final validation rejects it.

`complete` and `partial` require at least one series. `partial`, `needs_review`,
and `skipped` require at least one note. Deferred outputs have empty
`plot_data`.

## Series

`plot_data` contains one self-contained object per pitting-potential series:

```json
{
  "series_id": "ni80cr20_nacl",
  "panel": null,
  "tags": [
    {"name": "material", "value": "Ni80Cr20"},
    {"name": "test_solution", "value": "NaCl"}
  ],
  "x_axis": {
    "label": "pH",
    "type": "numeric",
    "unit": "",
    "scale": "linear",
    "is_target": false
  },
  "y_axis": {
    "label": "Ep",
    "type": "numeric",
    "unit": "mV",
    "scale": "linear",
    "is_target": true
  },
  "data_points": []
}
```

- `series_id` is a concise unique identifier within the artifact.
- `panel` is optional. Use a visible label such as `panel (b)`; omit it for a
  single-panel image.
- `tags` are flexible name/value pairs. Preserve the visible value rather than
  normalizing it. Use names such as `material`, `test_solution`, `condition`,
  `method`, or `unknown`.
- Axis `type` is `numeric`, `categorical`, or `mixed`.
- Axis `scale` is optional and, when present, is `linear`, `log`,
  `categorical`, or `unknown`.
- Exactly one axis must have `is_target: true`. Pitting potential may be on
  either axis.

Repeating axes per series is intentional. It keeps each series self-contained
and naturally supports figures with multiple y-axes.

## Points and intervals

Ordinary points contain scalar coordinates:

```json
{"x": 3, "y": 240}
```

Coordinates may be numbers, categorical strings, or null for a range-only
measurement. A point-specific visible annotation uses the optional `label`:

```json
{"x": 3, "y": 240, "label": "Sample A"}
```

Keep central values scalar and put interval endpoints in separate fields:

```json
{
  "x": 5,
  "y": 320,
  "y_lower": 310,
  "y_upper": 330,
  "y_interval_meaning": "unknown"
}
```

For a range without a displayed central value:

```json
{
  "x": "UNS S30400 in NaCl",
  "y": null,
  "y_lower": 50,
  "y_upper": 90,
  "y_interval_meaning": "experimental range"
}
```

Horizontal intervals use `x_lower`, `x_upper`, and `x_interval_meaning` in the
same way. Lower/upper fields must occur as a pair, the lower bound cannot exceed
the upper bound, and a numeric central value must fall within its bounds. Copy
the caption's description of the interval when available; otherwise use
`unknown`.

