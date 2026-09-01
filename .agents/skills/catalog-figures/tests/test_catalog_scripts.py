from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_DIR / "scripts"))

from identify_figures import (  # noqa: E402
    CatalogSkeletonError,
    build_catalog_skeleton,
    main as identify_main,
)
from validate_catalog import CatalogValidationError, validate  # noqa: E402


SCHEMA = SKILL_DIR / "references" / "catalog.schema.json"


def variable(
    source_label: str | None,
    interpreted_name: str | None,
    data_type: str,
    unit: str | None,
    interpretation_source: str,
    interpretation_evidence: str | None = None,
    uncertainty: dict[str, str] | None = None,
) -> dict[str, object]:
    result: dict[str, object] = {
        "source_label": source_label,
        "interpreted_name": interpreted_name,
        "data_type": data_type,
        "unit": unit,
        "interpretation_source": interpretation_source,
        "interpretation_evidence": interpretation_evidence,
    }
    if uncertainty is not None:
        result["uncertainty"] = uncertainty
    return result


class CatalogScriptTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.paper_dir = Path(self.temp_dir.name) / "paper_99"
        self.paper_dir.mkdir()
        pages = [
            [
                {"type": "paragraph", "content": {"paragraph_content": "Text"}},
                {
                    "type": "chart",
                    "content": {
                        "image_source": {"path": "images/chart.jpg"},
                        "chart_caption": [
                            {"type": "text", "content": "Fig. 1. "},
                            {"type": "equation_inline", "content": "E_p"},
                            {"type": "text", "content": " versus pH."},
                        ],
                    },
                },
                {
                    "type": "table",
                    "content": {
                        "image_source": {"path": "images/table.jpg"},
                        "table_caption": {
                            "type": "text",
                            "content": "Table 1. Alloy composition.",
                        },
                    },
                },
            ]
        ]
        (self.paper_dir / "99_demo_content_list_v2.json").write_text(
            json.dumps(pages), encoding="utf-8"
        )
        (self.paper_dir / "99_demo.md").write_text(
            "The pitting potential, Ep, was measured against pH.\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _completed_catalog(self) -> dict[str, object]:
        catalog = build_catalog_skeleton(self.paper_dir)
        chart = catalog["figures"][0]
        chart["status"] = "cataloged"
        chart["variables"] = [
            variable("pH", "ph", "numeric", "", "visual"),
            variable(
                "Ep",
                "pitting_potential",
                "numeric",
                "mV",
                "markdown",
                "The pitting potential, Ep, was measured against pH.",
                {"kind": "error_bar", "meaning": "unspecified"},
            ),
        ]
        table = catalog["figures"][1]
        table["status"] = "needs_review"
        table["variables"] = [
            variable("Mo wt%", "molybdenum", "numeric", "wt%", "visual"),
            variable("Cr wt%", "chromium", "numeric", "wt%", "visual"),
            variable("X", None, "unknown", None, "unresolved"),
        ]
        table["notes"] = ["The paper does not define X."]
        return catalog

    def _write_and_validate(self, catalog: dict[str, object]) -> int:
        path = Path(self.temp_dir.name) / "catalog.json"
        path.write_text(json.dumps(catalog), encoding="utf-8")
        return validate(path, SCHEMA)

    def test_skeleton_has_stable_provenance_and_requires_review(self) -> None:
        catalog = build_catalog_skeleton(self.paper_dir)
        self.assertEqual(catalog["schema_version"], 2)
        self.assertEqual(catalog["paper_reference"], "99")
        self.assertTrue(catalog["source_markdown"].endswith("99_demo.md"))
        self.assertNotIn("source_pdf", catalog)
        self.assertEqual(
            [entry["source_figure_id"] for entry in catalog["figures"]],
            ["page_0001_item_0002", "page_0001_item_0003"],
        )
        self.assertEqual(catalog["figures"][0]["caption"], "Fig. 1. $E_p$ versus pH.")
        self.assertIsNone(catalog["figures"][0]["status"])

    def test_exactly_one_content_list_and_markdown_are_required(self) -> None:
        (self.paper_dir / "duplicate.md").write_text("duplicate", encoding="utf-8")
        with self.assertRaisesRegex(CatalogSkeletonError, "expected exactly one"):
            build_catalog_skeleton(self.paper_dir)
        (self.paper_dir / "duplicate.md").unlink()
        (self.paper_dir / "99_demo.md").unlink()
        with self.assertRaisesRegex(CatalogSkeletonError, "found 0"):
            build_catalog_skeleton(self.paper_dir)
        (self.paper_dir / "99_demo.md").write_text("restored", encoding="utf-8")
        (self.paper_dir / "99_duplicate_content_list_v2.json").write_text(
            "[]", encoding="utf-8"
        )
        with self.assertRaisesRegex(CatalogSkeletonError, "found 2"):
            build_catalog_skeleton(self.paper_dir)

    def test_existing_output_is_not_silently_overwritten(self) -> None:
        output = Path(self.temp_dir.name) / "paper_99_figures.json"
        arguments = [
            "--input_path",
            str(self.paper_dir),
            "--output_file",
            str(output),
        ]
        self.assertEqual(identify_main(arguments), 0)
        original = output.read_bytes()
        self.assertEqual(identify_main(arguments), 1)
        self.assertEqual(output.read_bytes(), original)

    def test_complete_catalog_with_ambiguity_and_uncertainty_validates(self) -> None:
        self.assertEqual(self._write_and_validate(self._completed_catalog()), 2)

    def test_panel_split_and_cross_figure_units_validate(self) -> None:
        catalog = self._completed_catalog()
        source = catalog["figures"][0]
        panel_a = copy.deepcopy(source)
        panel_a["catalog_id"] += "__panel_a"
        panel_a["panel_label"] = "a"
        panel_b = copy.deepcopy(source)
        panel_b["catalog_id"] += "__panel_b"
        panel_b["panel_label"] = "b"
        panel_b["variables"][1]["unit"] = "V"
        catalog["figures"] = [panel_a, panel_b, catalog["figures"][1]]
        self.assertEqual(self._write_and_validate(catalog), 3)

    def test_missing_source_figure_fails(self) -> None:
        catalog = self._completed_catalog()
        catalog["figures"].pop()
        with self.assertRaisesRegex(CatalogValidationError, "omits MinerU"):
            self._write_and_validate(catalog)

    def test_forbidden_presentation_or_data_field_fails(self) -> None:
        catalog = self._completed_catalog()
        catalog["figures"][0]["x_axis"] = "pH"
        with self.assertRaisesRegex(CatalogValidationError, "schema error"):
            self._write_and_validate(catalog)

    def test_removed_v1_fields_fail(self) -> None:
        catalog = self._completed_catalog()
        catalog["figures"][0]["variables"][0]["canonical_name"] = "ph"
        catalog["figures"][0]["variables"][0]["role"] = "condition"
        with self.assertRaisesRegex(CatalogValidationError, "schema error"):
            self._write_and_validate(catalog)

    def test_unresolved_interpretation_requires_label_and_review(self) -> None:
        catalog = self._completed_catalog()
        catalog["figures"][1]["variables"][2]["source_label"] = None
        with self.assertRaisesRegex(CatalogValidationError, "schema error"):
            self._write_and_validate(catalog)

        catalog = self._completed_catalog()
        catalog["figures"][1]["status"] = "cataloged"
        with self.assertRaisesRegex(CatalogValidationError, "schema error"):
            self._write_and_validate(catalog)

    def test_markdown_interpretation_requires_exact_evidence(self) -> None:
        catalog = self._completed_catalog()
        variable_entry = catalog["figures"][0]["variables"][1]
        variable_entry["interpretation_evidence"] = "not in the Markdown"
        with self.assertRaisesRegex(CatalogValidationError, "exact excerpt"):
            self._write_and_validate(catalog)

        variable_entry["interpretation_evidence"] = None
        with self.assertRaisesRegex(CatalogValidationError, "schema error"):
            self._write_and_validate(catalog)

    def test_unlabeled_unambiguous_grouping_validates(self) -> None:
        catalog = self._completed_catalog()
        chart = catalog["figures"][0]
        chart["variables"].append(
            variable(None, "material", "categorical", None, "visual")
        )
        self.assertEqual(self._write_and_validate(catalog), 2)

    def test_duplicate_interpreted_name_fails(self) -> None:
        catalog = self._completed_catalog()
        chart = catalog["figures"][0]
        chart["variables"].append(
            variable("Acidity", "ph", "numeric", "", "visual")
        )
        with self.assertRaisesRegex(CatalogValidationError, "repeats variable ph"):
            self._write_and_validate(catalog)

if __name__ == "__main__":
    unittest.main()
