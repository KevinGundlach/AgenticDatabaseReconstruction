---
name: catalog-corrosion-tables
description: Inventory and classify every table in one paper's MinerU content_list_v2 output, preserving source context and mapping visible table fields to the Citrine pitting-potential schema. Use before parsing corrosion table images; do not use to transcribe table cells.
---

# Catalog Corrosion Tables

Build an auditable table manifest, inspect every detected table, and stage every
processable table for structural parsing. All genuine legible tables are useful;
Citrine overlap is metadata, not an acceptance criterion.

## Workflow

1. Accept one MinerU paper directory such as `mineru_output/paper_44`.
2. Build the non-overwriting manifest from `content_list_v2.json` only:

   ```powershell
   uv run <skill-dir>/scripts/extract_table_manifest.py <paper-folder>
   ```

   This writes `<paper-folder>/paper_<reference>_tables.json` and captures every
   table, its image and MinerU HTML, captions, footnotes, hierarchical section
   path, cross-page context, and explicit textual references.
3. Create a non-overwriting catalog template:

   ```powershell
   uv run <skill-dir>/scripts/prepare_catalog.py `
     --manifest <paper-folder>/paper_<reference>_tables.json
   ```

4. Read [catalog-output-contract.md](references/catalog-output-contract.md) and
   [citrine-fields.json](references/citrine-fields.json). Inspect every table
   image directly. Treat the image as primary evidence and MinerU HTML as a
   fallible aid. Fill every catalog entry and update the summary.
5. Stage processable tables centrally:

   ```powershell
   uv run <skill-dir>/scripts/stage_cataloged_tables.py `
     --manifest <paper-folder>/paper_<reference>_tables.json `
     --catalog <paper-folder>/paper_<reference>_cataloged_tables.json `
     --output corrosion_tables/images
   ```

   The staging script refuses to overwrite an existing image or sidecar.
6. Report the processable, needs-review, and non-table counts plus all output
   paths. Do not claim that a paper was fully cataloged while any entry remains
   `unclassified`.

## Cataloging rules

- Mark every genuine, legible table `processable`, regardless of whether it
  overlaps the Citrine schema.
- Use `needs_review` for a missing or unreadable crop, ambiguous visual table
  boundary, or evidence insufficient to classify the source.
- Use `non_table` only when MinerU's table detection is not actually a table.
- Assign every applicable controlled `table_role`; use `other` when none fit.
- Map a Citrine field only when a visible row or column header represents that
  field. Preserve the visible label and classify the match as `exact`,
  `synonym`, or `semantic`. Do not inspect Citrine database rows.
- Select only context block IDs that materially help interpret the table.
- Do not transcribe cells, normalize units, infer missing values, or assemble
  corrosion records in this skill.

## Integrity rules

- Account for every manifest `table_id` exactly once.
- Preserve stable table identity, image path, caption, page, and bounding box.
- Never classify from MinerU HTML alone when an image exists.
- Do not use legacy `content_list.json` or Markdown as the table inventory.
- Preserve existing manifest, catalog, and staged files; the scripts stop on
  output collisions.
