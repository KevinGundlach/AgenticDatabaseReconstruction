---
name: tabularize-plots
description: Extract and digitize pitting potential plot figures and paired metadata from a user-supplied input directory into schema-compliant JSON files in a user-supplied output directory.
---

# Tabularize Plots Skill

This skill extracts and digitizes pitting-potential plot figures from materials science corrosion papers into structured, schema-compliant JSON files.

## Input & Output Locations

* **Input Images & Metadata**: A required user-supplied directory containing paired `*.jpg` figures and `*.json` metadata files.
* **Output Destination**: A required user-supplied directory. Write each result as `tabularized_{image_name}.json` inside it.
* **Output Schema**: [references/digitized_pitting_potential_plot.schema.json](./references/digitized_pitting_potential_plot.schema.json) (or root `digitized_pitting_potential_plot.schema.json`).

Both directory paths must be explicitly supplied by the user. Do not infer, search for, or default either path. If either path is missing, ask for the missing path and do not continue until it is supplied.

---

## Schema & Extraction Rules

All generated JSON files must strictly adhere to the `digitized-pitting-potential-plot:v2` schema:

1. **Direct Multimodal Vision Extraction**:
   * **Rely on Native Vision**: Use your built-in multimodal capabilities to directly view and read figures using the available image-viewing tool (e.g., `view_file` in Antigravity or `view_image` in Codex). Directly inspect tick marks, axis bounds, data points, error bars, markers, and legends.
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

### Step 1: Collect Required Paths
* Require the user to supply both the input directory and output directory.
* If either path is missing, ask for it and stop. Do not discover a likely directory or substitute a default.

### Step 2: Verify Input and Prepare Output
* Confirm that the supplied input path exists and is a directory. If not, report the error and stop.
* Ensure the explicitly supplied output directory exists; create it if missing.

### Step 3: Discover Input Files
* List all files in the supplied input directory.
* Identify each paired `.jpg` and `.json` metadata file.

### Step 4: Process Each Plot Image (Direct Multimodal Vision)
For each plot figure in the input directory, process one figure at a time and write out its file immediately:
1. **Metadata Context**: Read the corresponding `{image_name}.json` metadata file from the supplied input directory to obtain `paper_reference`, `source_chart_manifest`, and `plot_metadata`.
2. **Visual Inspection**: View and inspect the `.jpg` image using the available image-viewing tool (e.g., `view_file` in Antigravity or `view_image` in Codex) to examine axes, tick marks, legends, labels, and marker positions directly with multimodal vision.
3. **Digitize Points**: Directly extract data points, series names, tags, and coordinates using native vision capabilities. Do not write CV/image-processing code.
4. **Construct & Write Output JSON**: 
   * Retain `paper_reference`, `source_chart_manifest`, and `plot_metadata` verbatim from the input metadata.
   * Set `schema_version: 2`.
   * Set `digitization_status` (`"complete"`, `"partial"`, `"needs_review"`, or `"skipped"`).
   * Include `digitization_notes` (array of strings, required if partial/needs_review/skipped).
   * Populate `plot_data`: ensure each series defines unique `series_id`, `tags`, `data_points`, and both `x_axis` and `y_axis` with `type` (`"numeric"` / `"categorical"`) and exactly one `is_target: true`.
   * Immediately save the output file as `tabularized_{image_name}.json` in the supplied output directory before proceeding to the next figure.

### Step 5: Validate Outputs
* Execute the permanent validation script:
  ```text
  uv run .agents/skills/tabularize-plots/scripts/validate_outputs.py --input "<input-directory>" --output "<output-directory>"
  ```
* If validation identifies schema or semantic discrepancies, correct the generated output JSON files and re-validate.

### Step 6: Present Summary Report
* Print a clear final summary table listing:
  * Total files processed from the supplied input directory.
  * Number of `complete`, `partial`, and `needs_review` / `skipped` files.
  * Any specific notes or warnings regarding difficult figures.

---

## Environment & Scripting Rules

* **Virtual Environment & System-wide `uv`**: `uv` is installed system-wide. If `uv run` is blocked by sandbox permissions, use the available sandbox-bypass or permission-escalation mechanism (e.g., `BypassSandbox` in Antigravity or permission escalation in Codex).
* **Direct Multimodal Extraction**: Python scripting is not needed for plot digitizing; use Python solely for validation (`validate_outputs.py`).
* **Execution via `uv run`**: Always run Python scripts using `uv run <path_to_script.py>`.
* **No Inline Python**: Do **NOT** execute inline Python code on the command line (e.g., avoid `python -c "..."` or command-line one-liners).
* **Script Storage Rules**:
  * **Permanent / Skill Scripts**: All reusable, permanent scripts belong inside `.agents/skills/tabularize-plots/scripts/` (e.g., `validate_outputs.py`).
  * **Ad-hoc Scripts**: If any non-digitization calculation script is needed, store it in `.agents/skills/tabularize-plots/temp_scripts/`.
* **Strict Error Handling & Abort Policy**: If `uv run` still fails because of permissions or environment errors, **stop and report the exact error**. Do **NOT** attempt ad-hoc workarounds, shell probing, or command guessing.
