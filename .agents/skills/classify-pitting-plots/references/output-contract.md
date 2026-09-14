# Classification output contract

Write `paper_<reference>_simple_plots.json` beside the chart manifest. Preserve
each chart's `chart_id`, `image_path`, and flattened `caption` exactly as they
appear in the manifest.

```json
{
  "schema_version": 2,
  "paper_reference": "80",
  "source_chart_manifest": "paper_80_charts.json",
  "summary": {
    "chart_count": 2,
    "accepted": 1,
    "rejected": 1,
    "needs_review": 0
  },
  "simple_plots": [
    {
      "chart_id": "page_0004_item_0001",
      "image_path": "images/example.jpg",
      "caption": "Fig. 1. Pitting potential versus alloy content.",
      "reason_code": "direct_pitting_potential_plot",
      "reason": "Pitting potential is directly plotted against alloy content with discrete markers.",
      "confidence": 0.98,
      "relevant_panels": [],
      "target_series": ["fresh-sample pitting potential"],
      "x_axis": {
        "label": "Alloy content",
        "unit": "at. %",
        "scale": "linear"
      },
      "y_axis": {
        "label": "Pitting potential",
        "unit": "mV SCE",
        "scale": "linear"
      }
    }
  ],
  "rejected_charts": [
    {
      "chart_id": "page_0005_item_0003",
      "image_path": "images/polarization.jpg",
      "caption": "Fig. 2. Potentiodynamic polarization curves.",
      "reason_code": "polarization_curve",
      "reason": "Potential is plotted against current density and Epit would require interpretation.",
      "confidence": 0.99,
      "relevant_panels": [],
      "target_series": []
    }
  ],
  "needs_review": []
}
```

An empty `relevant_panels` array means the whole image. For a mixed or
multipanel figure, identify labels such as `panel (b)` or `right panel`.

Every accepted entry must include `x_axis` and `y_axis`. Transcribe the visible
axis label and unit; use an empty unit string for a unitless axis. Set `scale`
to `linear`, `log`, `categorical`, or `unknown`. Do not add axis objects to
rejected or review entries.

Use `direct_pitting_potential_plot` for accepted charts. Use one of these codes
for rejected charts:

- `polarization_curve`
- `current_density_only`
- `other_electrochemical_metric`
- `not_pitting_potential`
- `not_digitizable`
- `non_plot_chart`
- `unreadable`
- `other`

Use one of these codes for charts needing review:

- `insufficient_evidence`
- `missing_image`
- `ambiguous_metric`
- `ambiguous_chart_type`

Set `confidence` from 0 to 1. Use a concise evidence-based `reason`. Identify at
least one `target_series` for every accepted chart; use an empty array when no
pitting-potential series has been established.
