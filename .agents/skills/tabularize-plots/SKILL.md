---
name: tabularize-plots
description: Extract and digitize pitting potential plot figures and metadata into schema-compliant JSON format. Use whenever asked to tabularize, digitize, or extract data from images in Images/Batch_*.
---

# Tabularize Plots Skill

This skill extracts and digitizes pitting-potential plot figures from materials science corrosion papers into structured, schema-compliant JSON files.

## Input & Output Locations

* **Input Images & Metadata**: `Images/Batch_{n}/` (contains paired `*.jpg` figures and `*.json` metadata files).
* **Output Destination**: `Output/Batch_{n}/tabularized_{image_name}.json`.
* **Output Schema**: [references/digitized_pitting_potential_plot.schema.json](./references/digitized_pitting_potential_plot.schema.json) (or root `digitized_pitting_potential_plot.schema.json`).

---

## Schema & Extraction Rules

All generated JSON files must strictly adhere to the `digitized-pitting-potential-plot:v2` schema:

1. **Direct Multimodal Vision Extraction**:
   * **Rely on Native Vision**: Use your built-in multimodal capabilities to directly view and read figures via `view_file`. Directly inspect tick marks, axis bounds, data points, error bars, markers, and legends.
   * **No Complex CV Scripting**: Do **NOT** generate complex Python scripts involving OpenCV, contour detection, OCR, or pixel heuristics to extract data points. Direct multimodal inspection is faster, more robust, and significantly more accurate for materials science plots.

2. **Root Fields**:
   * `schema_version`: Must be the integer `2`.
   * `paper_reference`: Stable string identifier copied unchanged from the paired metadata JSON.
   * `source_chart_manifest`: Manifest identifier copied unchanged from metadata JSON.
   * `plot_metadata`: Classifier metadata object copied unchanged from metadata JSON.
   * `digitization_status`: One of `"complete"`, `"partial"`, `"needs_review"`, `"skipped"`, or `"unprocessed"`.
   * `digitization_notes`: Array of descriptive strings (required and non-empty for `partial`, `needs_review`, and `skipped`).
   * `plot_data`: Array of extracted series objects.

3. **Status Rules**:
   * `"complete"`: All visible supported target series were extracted (`plot_data` must have $\ge 1$ series).
   * `"partial"`: Some reliable target data were extracted (`plot_data` must have $\ge 1$ series, and `digitization_notes` must describe omitted series).
   * `"needs_review"` / `"skipped"`: No data emitted (`plot_data` must be empty `[]`, `digitization_notes` must contain at least 1 explanatory note).

4. **Series & Axis Rules**:
   * Each series must have a unique `series_id` within the file.
   * In each series, both `x_axis` and `y_axis` must define `"is_target": boolean`. Exactly **one** axis per series must have `"is_target": true` (the pitting potential axis).
   * Ancillary series (e.g. repassivation, corrosion rate, fitted/trend lines without markers) are excluded unless specified.

---

## Step-by-Step Execution Runbook

### Step 1: Identify Target Batch
* If the user specified a batch number or directory in their prompt (e.g., `Batch 1`, `Images/Batch_2`), target that batch.
* If unspecified, ask the user which batch (`1` through `10`) to process.

### Step 2: Prepare Target Output Directory
* Ensure the target directory `Output/Batch_{n}` exists (create it if missing).

### Step 3: Discover Input Files
* List all files in `Images/Batch_{n}/`.
* Identify each paired `.jpg` and `.json` metadata file.

### Step 4: Process Each Plot Image (Direct Multimodal Vision)
For each plot figure in the batch, process one figure at a time and write out its file immediately:
1. **Metadata Context**: Read the corresponding `.json` metadata file (e.g. `Images/Batch_{n}/{image_name}.json`) to obtain `paper_reference`, `source_chart_manifest`, and `plot_metadata`.
2. **Visual Inspection**: View and inspect the `.jpg` image using the `view_file` tool to examine axes, tick marks, legends, labels, and marker positions directly with multimodal vision.
3. **Digitize Points**: Directly extract data points, series names, tags, and coordinates using native vision capabilities. Do not write CV/image-processing code.
4. **Construct & Write Output JSON**: 
   * Retain `paper_reference`, `source_chart_manifest`, and `plot_metadata` verbatim from the input metadata.
   * Set `schema_version: 2`.
   * Set `digitization_status` (`"complete"`, `"partial"`, `"needs_review"`, or `"skipped"`).
   * Include `digitization_notes` (array of strings, required if partial/needs_review/skipped).
   * Populate `plot_data`: ensure each series defines unique `series_id`, `tags`, `data_points`, and both `x_axis` and `y_axis` with `type` (`"numeric"` / `"categorical"`) and exactly one `is_target: true`.
   * Immediately save the output file to `Output/Batch_{n}/tabularized_{image_name}.json` before proceeding to the next figure.

### Step 5: Validate Outputs
* Execute the permanent validation script:
  ```bash
  uv run .agents/skills/tabularize-plots/scripts/validate_outputs.py {n}
  ```
* If validation identifies schema or semantic discrepancies, correct the generated output JSON files and re-validate.

### Step 6: Present Summary Report
* Print a clear final summary table listing:
  * Total files processed in `Batch_{n}`.
  * Number of `complete`, `partial`, and `needs_review` / `skipped` files.
  * Any specific notes or warnings regarding difficult figures.

---

## Environment & Scripting Rules

* **Virtual Environment & System-wide `uv`**: `uv` is installed system-wide. If `uv` is not recognized or not found when running a command, that is likely only due to it being blocked by the sandboxed environment (switch to bypass sandbox mode / `BypassSandbox: true` if needed).
* **Direct LLM Extraction**: Python scripting is not needed for plot digitizing; use Python solely for validation (`validate_outputs.py`).
* **Execution via `uv run`**: Always run Python scripts using `uv run <path_to_script.py>`.
* **No Inline Python**: Do **NOT** execute inline Python code on the command line (e.g., avoid `python -c "..."` or command-line one-liners).
* **Script Storage Rules**:
  * **Permanent / Skill Scripts**: All reusable, permanent scripts belong inside `.agents/skills/tabularize-plots/scripts/` (e.g., `validate_outputs.py`).
  * **Ad-hoc Scripts**: If any non-digitization calculation script is needed, store it in `Temporary_Scripts/`.
* **Strict Error Handling & Abort Policy**: If `uv run` fails due to permission denial or environment errors (and is not resolved by bypassing sandbox restrictions), **stop immediately and report the error directly to the user**. Do **NOT** attempt ad-hoc workarounds, shell probing, or command guessing.
