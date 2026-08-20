# Digitized pitting-plot output contract

Create one schema-version-1 JSON object for one staged `.jpg` and its
same-basename classifier `.json`. The preparation script supplies `source`
verbatim and binds both inputs with SHA-256 hashes. Edit only `digitization`.

The machine-readable structural contract is
[digitization.schema.json](digitization.schema.json). The validator additionally
checks the input hashes, copied metadata, cross-references, status invariants,
target-series coverage, and interval ordering.

## Top level

```json
{
  "schema_version": 1,
  "source": {
    "paper_reference": "9",
    "source_chart_manifest": "paper_9_charts.json",
    "image": {
      "path": "../pitting_potential_plots/paper_9_page_0008_item_0002.jpg",
      "sha256": "64-lowercase-hex-characters"
    },
    "metadata": {
      "path": "../pitting_potential_plots/paper_9_page_0008_item_0002.json",
      "sha256": "64-lowercase-hex-characters"
    },
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
    }
  },
  "digitization": {
    "status": "complete",
    "reason_code": "digitized_discrete_marks",
    "reason": "All discrete pitting-potential markers were digitized.",
    "confidence": 0.94,
    "issues": [],
    "panels": []
  }
}
```

`source.plot_metadata` must equal the paired metadata's `plot_metadata` object.
Source paths use `/` separators and are relative to the digitization artifact.

## Status and reason codes

Use exactly one status and a compatible reason code:

| Status | Allowed reason codes | Required behavior |
| --- | --- | --- |
| `complete` | `digitized_discrete_marks` | At least one observation; every classifier target is referenced; no issues. |
| `partial` | `partially_digitized` | At least one observation and one issue; digitized series plus issues account for every classifier target. |
| `needs_review` | `ambiguous_axis`, `ambiguous_series_mapping`, `ambiguous_mark_semantics`, `insufficient_resolution` | At least one issue and no observations; issues account for every classifier target. |
| `skipped` | `markerless_trace`, `unsupported_geometry`, `no_discrete_target_marks` | At least one issue and no observations; issues account for every classifier target. |

Each issue has `code`, `message`, and `target_series_refs`. Allowed issue codes
are `ambiguous_axis`, `ambiguous_series_mapping`, `ambiguous_mark_semantics`,
`insufficient_resolution`, `occluded_marks`, `unresolved_target_series`, and
`unsupported_geometry`. Every reference must exactly match a string in
`source.plot_metadata.target_series`.

## Panels and axes

Use `whole_image` as the only `panel_id` when the image is not divided into
panels. Otherwise, use stable IDs such as `panel_a`; transcribe the visible
panel label into `label_raw`.

Each axis contains:

```json
{
  "axis_id": "y_potential_left",
  "dimension": "y",
  "side": "left",
  "label_raw": "Potential",
  "unit_raw": "V SCE",
  "scale": "linear",
  "value_type": "numeric",
  "target_metric": true,
  "breaks": []
}
```

- `dimension`: `x` or `y`.
- `side`: `bottom`, `top`, `left`, `right`, or `unknown`.
- `scale`: `linear`, `log`, `categorical`, or `unknown`. A visibly linear axis
  whose label is already transformed, such as `Log Cl`, remains `linear`.
- `value_type`: `numeric`, `categorical`, `mixed`, or `unknown`.
- `target_metric` is true only for an axis representing pitting potential.
- `breaks` contains concise raw descriptions of visible discontinuities.

Record distinct left and right y-axes even when only one has a pitting series.

## Series, tags, and omissions

```json
{
  "series_id": "ni80cr20_nacl",
  "target_series_refs": ["Ni80Cr20 pitting potential"],
  "labels_raw": ["Ni80Cr20", "NaCl"],
  "tags": [
    {
      "key": "material",
      "value_raw": "Ni80Cr20",
      "evidence_source": "plot_annotation"
    },
    {
      "key": "test_solution",
      "value_raw": "NaCl",
      "evidence_source": "legend"
    }
  ],
  "x_axis_id": "x_ph",
  "y_axis_id": "y_ep",
  "visual_encoding": {
    "color_raw": "black",
    "marker_raw": "filled diamond",
    "line_raw": "solid",
    "fill_raw": "filled"
  },
  "observations": []
}
```

`key` is deliberately open-ended; use a concise semantic dimension such as
`material`, `test_solution`, `condition`, or `method`, while preserving the
visible value in `value_raw`. Evidence sources are `legend`, `plot_annotation`,
`caption`, `axis`, or `classifier_metadata`.

List recognizable out-of-scope series under the panel's `omitted_series`:

```json
{
  "label_raw": "Corrosion rate, Icorr",
  "reason_code": "non_pitting_metric",
  "notes": "Uses the right y-axis."
}
```

Allowed omission reasons are `non_pitting_metric`,
`fitted_or_connecting_line`, and `other_out_of_scope`.

## Observations and intervals

Every observation supplies exactly one value for the series' x-axis and y-axis:

```json
{
  "observation_id": "ni80cr20_nacl_point_001",
  "mark_type": "marker",
  "values": [
    {"axis_id": "x_ph", "value": 3.0, "interval": null},
    {"axis_id": "y_ep", "value": 230.0, "interval": null}
  ],
  "label_raw": "",
  "confidence": 0.93,
  "notes": ""
}
```

`mark_type` is `marker`, `bar`, `range`, or `other_discrete`. Numeric and mixed
axes accept numbers; categorical and mixed axes accept strings. A null `value`
is allowed only when an interval supplies a range-only measurement.

Experimental error bars and ranges use absolute plotted endpoints, not plus/minus
deltas:

```json
{
  "axis_id": "y_ep",
  "value": 0.30,
  "interval": {
    "lower": 0.12,
    "upper": 0.39,
    "kind": "error_bar",
    "meaning_raw": "25th and 75th percentile"
  }
}
```

Allowed interval kinds are `error_bar`, `reported_range`, and `other`. If a
central value is visible, it must fall within the interval. Use `range` as the
mark type when an observation is range-only.

