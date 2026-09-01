from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = SKILL_DIR.parents[2]
sys.path.insert(0, str(SKILL_DIR / "scripts"))

from identify_figures import (  # noqa: E402
    CatalogSkeletonError,
    build_catalog_skeleton,
    main as identify_main,
)
from validate_catalog import CatalogValidationError, validate  # noqa: E402


SCHEMA = SKILL_DIR / "references" / "catalog.schema.json"
VOCABULARY = PROJECT_ROOT / "vocabularies" / "variables.json"


def variable(
    source_label: str | None,
    canonical_name: str | None,
    data_type: str,
    unit: str | None,
    role: str,
    uncertainty: dict[str, str] | None = None,
) -> dict[str, object]:
    result: dict[str, object] = {
        "source_label": source_label,
        "canonical_name": canonical_name,
        "data_type": data_type,
        "unit": unit,
        "role": role,
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
        (self.paper_dir / "99_demo_origin.pdf").write_bytes(b"%PDF-1.4\n%%EOF\n")

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _completed_catalog(self) -> dict[str, object]:
        catalog = build_catalog_skeleton(self.paper_dir)
        chart = catalog["figures"][0]
        chart["status"] = "cataloged"
        chart["variables"] = [
            variable("pH", "ph", "numeric", "", "condition"),
            variable(
                "Ep",
                "pitting_potential",
                "numeric",
                "mV",
                "measured",
                {"kind": "error_bar", "meaning": "unspecified"},
            ),
        ]
        table = catalog["figures"][1]
        table["status"] = "needs_review"
        table["variables"] = [
            variable("Mo wt%", "molybdenum", "numeric", "wt%", "condition"),
            variable("Cr wt%", "chromium", "numeric", "wt%", "condition"),
            variable("X", None, "unknown", None, "measured"),
        ]
        table["notes"] = ["The paper does not define X."]
        return catalog

    def _write_and_validate(self, catalog: dict[str, object]) -> int:
        path = Path(self.temp_dir.name) / "catalog.json"
        path.write_text(json.dumps(catalog), encoding="utf-8")
        return validate(path, SCHEMA, VOCABULARY)

    def test_skeleton_has_stable_provenance_and_requires_review(self) -> None:
        catalog = build_catalog_skeleton(self.paper_dir)
        self.assertEqual(catalog["paper_reference"], "99")
        self.assertTrue(catalog["source_pdf"].endswith("99_demo_origin.pdf"))
        self.assertEqual(
            [entry["source_figure_id"] for entry in catalog["figures"]],
            ["page_0001_item_0002", "page_0001_item_0003"],
        )
        self.assertEqual(catalog["figures"][0]["caption"], "Fig. 1. $E_p$ versus pH.")
        self.assertIsNone(catalog["figures"][0]["status"])

    def test_exactly_one_content_list_and_origin_pdf_are_required(self) -> None:
        (self.paper_dir / "duplicate_origin.pdf").write_bytes(b"%PDF")
        with self.assertRaisesRegex(CatalogSkeletonError, "expected exactly one"):
            build_catalog_skeleton(self.paper_dir)
        (self.paper_dir / "duplicate_origin.pdf").unlink()
        (self.paper_dir / "99_demo_origin.pdf").unlink()
        with self.assertRaisesRegex(CatalogSkeletonError, "found 0"):
            build_catalog_skeleton(self.paper_dir)
        (self.paper_dir / "99_demo_origin.pdf").write_bytes(b"%PDF")
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

    def test_unknown_canonical_name_fails(self) -> None:
        catalog = self._completed_catalog()
        catalog["figures"][0]["variables"][0]["canonical_name"] = "not_in_vocab"
        with self.assertRaisesRegex(CatalogValidationError, "absent from the vocabulary"):
            self._write_and_validate(catalog)

    def test_unresolved_mapping_must_retain_source_label(self) -> None:
        catalog = self._completed_catalog()
        catalog["figures"][1]["variables"][2]["source_label"] = None
        with self.assertRaisesRegex(CatalogValidationError, "retain the ambiguous"):
            self._write_and_validate(catalog)

    @unittest.skipUnless(
        (PROJECT_ROOT / "mineru_output" / "paper_9").is_dir(),
        "Paper 9 MinerU output is not available",
    )
    def test_paper_9_figure_9_contract(self) -> None:
        catalog = build_catalog_skeleton(PROJECT_ROOT / "mineru_output" / "paper_9")
        figure_9 = next(
            entry for entry in catalog["figures"] if entry["caption"].startswith("Fig. 9.")
        )
        figure_9["variables"] = [
            variable("Ep", "pitting_potential", "numeric", "mV", "measured"),
            variable("pH", "ph", "numeric", "", "condition"),
            variable(None, "material", "categorical", None, "condition"),
            variable(None, "electrolyte", "categorical", None, "condition"),
            variable(
                None,
                "electrolyte_concentration",
                "numeric",
                "M",
                "condition",
            ),
        ]
        self.assertEqual(
            {item["canonical_name"] for item in figure_9["variables"]},
            {
                "pitting_potential",
                "ph",
                "material",
                "electrolyte",
                "electrolyte_concentration",
            },
        )
        self.assertFalse(FORBIDDEN_KEYS.intersection(figure_9))

    @unittest.skipUnless(
        (PROJECT_ROOT / "mineru_output" / "paper_16").is_dir(),
        "Paper 16 MinerU output is not available",
    )
    def test_paper_16_figure_10_panels_and_unspecified_error_bars(self) -> None:
        catalog = build_catalog_skeleton(PROJECT_ROOT / "mineru_output" / "paper_16")
        for entry in catalog["figures"]:
            entry["status"] = "needs_review"
            entry["notes"] = ["Outside this focused fixture."]

        index = next(
            position
            for position, entry in enumerate(catalog["figures"])
            if entry["caption"].startswith("Fig.10")
        )
        source = catalog["figures"][index]
        upper = copy.deepcopy(source)
        upper["catalog_id"] += "__panel_a"
        upper["panel_label"] = "a"
        upper["status"] = "cataloged"
        upper["notes"] = []
        upper["variables"] = [
            variable(
                "Heating Temp.",
                "heat_treatment_temperature",
                "numeric",
                "K",
                "condition",
            ),
            variable(None, "material", "categorical", None, "condition"),
            variable(
                "Ferrite Content",
                "ferrite_content",
                "numeric",
                "%",
                "measured",
                {"kind": "error_bar", "meaning": "unspecified"},
            ),
        ]
        lower = copy.deepcopy(source)
        lower["catalog_id"] += "__panel_b"
        lower["panel_label"] = "b"
        lower["status"] = "cataloged"
        lower["notes"] = []
        lower["variables"] = [
            variable(
                "Heating Temp.",
                "heat_treatment_temperature",
                "numeric",
                "K",
                "condition",
            ),
            variable(None, "material", "categorical", None, "condition"),
            variable("Epit", "pitting_potential", "numeric", "mV", "measured"),
        ]
        catalog["figures"][index : index + 1] = [upper, lower]
        self.assertEqual(self._write_and_validate(catalog), 14)
        self.assertEqual(
            upper["variables"][2]["uncertainty"]["meaning"], "unspecified"
        )


FORBIDDEN_KEYS = {
    "x_axis",
    "y_axis",
    "marker_style",
    "line_style",
    "values",
    "data_points",
}


if __name__ == "__main__":
    unittest.main()
