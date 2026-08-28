---
name: parse-corrosion-tables
description: Reconstruct staged corrosion table images into source-faithful, queryable JSON with physical cell spans, parsed values, and hierarchical header links. Use after catalog-corrosion-tables; do not use for semantic corrosion claims, unit normalization, or record assembly.
---

# Parse Corrosion Tables

Parse every staged table image from direct visual evidence and write one
schema-compliant JSON artifact per image.

## Inputs and outputs

- Read paired table images and JSON sidecars from `corrosion_tables/images`.
- Write `parsed_<image-stem>.json` to `corrosion_tables/tabularized` immediately
  after completing each image.
- Use the canonical
  [digitized table schema](../../../schemas/digitized_corrosion_table.schema.json).
- Read [parsing-guide.md](references/parsing-guide.md) before producing output.

If the user supplies different input or output directories, use those paths.
Never infer an unstaged table directly from the MinerU corpus.

## Workflow

1. Verify that each image has a same-stem JSON sidecar and read the source and
   catalog metadata.
2. Inspect the table image with native vision. Treat the image as primary
   evidence; use MinerU HTML only as a fallible transcription and comparison.
3. Reconstruct every physical cell, including merged spans and visually implied
   rows. Create multiple grids only when the crop contains distinct table
   regions that cannot share one coordinate system.
4. Preserve exact visible cell text in `raw_text`. Add the conservative parsed
   `value`, footnote markers, transcription status, and any notes.
5. Link every data cell to all effective row and column headers, including
   merged parent headers.
6. Assess MinerU's HTML and select `consistent`, `minor_errors`, `major_errors`,
   `unusable`, or `not_available` with concise notes.
7. Save the result before advancing to the next image.

In `source.image_path`, record the staged image filename beside the sidecar;
retain the original MinerU image path through the referenced sidecar metadata.

## Boundaries

- Do not normalize units or reference electrodes.
- Do not calculate, infer, or fill values not printed in the table.
- Do not convert the table into Citrine records or domain claims.
- Do not silently use MinerU text when it conflicts with the visible image.
- Use `partial` for reliable output with documented omissions; use
  `needs_review` when no reliable grid can be emitted.

## Completion report

Report counts for `complete`, `partial`, `needs_review`, and `skipped`, plus the
output directory and any images whose structure or transcription remains
uncertain.
