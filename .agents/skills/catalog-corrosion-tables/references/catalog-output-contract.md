# Catalog output contract

Write `paper_<reference>_cataloged_tables.json` beside the table manifest. Keep
one entry in `tables` for every manifest table, in manifest order.

```json
{
  "schema_version": 1,
  "paper_reference": "44",
  "source_table_manifest": "paper_44_tables.json",
  "summary": {
    "table_count": 2,
    "processable": 1,
    "needs_review": 1,
    "non_table": 0,
    "unclassified": 0
  },
  "tables": [
    {
      "table_id": "page_0070_item_0001",
      "page_number": 70,
      "item_index": 1,
      "bbox": [281, 258, 776, 458],
      "image_path": "images/example.jpg",
      "caption": "Table 2.1. Alloy compositions.",
      "status": "processable",
      "table_roles": ["alloy_composition", "material_identifiers"],
      "reason": "The image is a legible composition table.",
      "confidence": 0.99,
      "relevant_context_block_ids": ["page_0069_item_0012"],
      "citrine_field_mappings": [
        {
          "citrine_field": "Cr",
          "source_label": "Cr",
          "header_role": "column_header",
          "match_type": "exact",
          "confidence": 1.0
        }
      ]
    }
  ]
}
```

## Status

- `processable`: a genuine table whose visible contents can be structurally
  parsed.
- `needs_review`: genuine or possible table evidence that cannot yet be parsed
  reliably, including missing or unreadable crops.
- `non_table`: a false MinerU table detection.
- `unclassified`: template-only state; forbidden in a completed catalog.

## Controlled table roles

- `alloy_composition`
- `corrosion_measurements`
- `test_environment`
- `test_method`
- `material_processing`
- `microstructure_phase`
- `mechanical_properties`
- `regression_model_results`
- `material_identifiers`
- `other`

A table can have several roles. A completed processable entry must contain at
least one role. Review and non-table entries may use an empty array.

## Citrine field mappings

Use only exact values from `citrine-fields.json` for `citrine_field`.

- `source_label` is the visible table header, preserved as printed.
- `header_role` is `column_header` or `row_header`.
- `match_type` is `exact`, `synonym`, or `semantic`.
- `confidence` is between 0 and 1.

An empty array means no visible table header maps to a Citrine field. Do not map
values mentioned only in captions or surrounding prose.
