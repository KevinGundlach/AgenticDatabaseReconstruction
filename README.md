# Corrosion plot digitizer

Phase one of the corrosion-literature pipeline: find figures that explicitly plot
pitting potential, collect raw chart observations with a Codex skill, and turn the
validated observations into CSV files.

The model-facing contract deliberately contains no normalized composition fields.
Atomic-percent to weight-percent conversion is performed only by versioned Python
functions in `corrosion_plot_digitizer.chemistry`.

## Development commands

```powershell
uv sync
uv run corrosion-plot-digitizer discover `
  --markdown "mineru_output/paper_80/80_G.S. Frankel, R.C. Newman, C.V. Jahnes, M.A. Russak, J Electrochem Soc, 140 (1993) 2192-2197.md" `
  --paper-id 80 `
  --output runs/paper_80/figure_manifest.json

uv run corrosion-plot-digitizer finalize `
  --input examples/paper_80_figure_1.raw.json `
  --output-dir runs/paper_80/figure_1

uv run python -m unittest discover -s tests -v
```

Invoke `$digitize-corrosion-plots` in Codex to run the complete agent-assisted
workflow. The CSV is an observation-level artifact, not the final flattened
Citrine database.

