from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_DIR / "scripts"))

from prepare_extraction import (  # noqa: E402
    build_extraction_skeleton,
    main as prepare_main,
)
from validate_extraction import (  # noqa: E402
    ExtractionValidationError,
    validate,
)


SCHEMA = SKILL_DIR / "references" / "extraction.schema.json"


def variable(name: str | None, data_type: str) -> dict[str, object]:
    return {
        "source_label": name,
        "interpreted_name": name,
        "data_type": data_type,
        "unit": "",
        "interpretation_source": "visual" if name is not None else "unresolved",
        "interpretation_evidence": None,
    }


def figure(
    catalog_id: str,
    status: str,
    variables: list[dict[str, object]],
) -> dict[str, object]:
    return {
        "catalog_id": catalog_id,
        "status": status,
        "variables": variables,
    }


class ExtractionScriptTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_root = Path(self.temp_dir.name)
        self.paper_dir = self.project_root / "mineru_output" / "paper_99"
        self.paper_dir.mkdir(parents=True)
        self.catalog_path = self.paper_dir / "paper_99_figures.json"
        self.catalog = {
            "schema_version": 2,
            "paper_reference": "99",
            "figures": [
                figure(
                    "page_0001_item_0001",
                    "cataloged",
                    [variable("potential", "numeric"), variable("alloy", "categorical")],
                ),
                figure(
                    "page_0001_item_0002",
                    "cataloged",
                    [
                        variable("chloride_concentration", "categorical"),
                        variable("ph_range", "numeric"),
                    ],
                ),
                figure(
                    "page_0001_item_0003",
                    "cataloged",
                    [
                        variable("alloy", "categorical"),
                        variable("parameter", "categorical"),
                        variable("test_solution", "categorical"),
                        variable("parameter_value", "unknown"),
                        variable("pren", "numeric"),
                    ],
                ),
                figure(
                    "page_0001_item_0004",
                    "needs_review",
                    [variable(None, "unknown")],
                ),
                figure("page_0001_item_0005", "not_data_figure", []),
            ],
        }
        self.catalog_path.write_text(
            json.dumps(self.catalog), encoding="utf-8"
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _completed_extraction(self) -> dict[str, object]:
        extraction = build_extraction_skeleton(self.paper_dir, self.project_root)
        chart = extraction["extractions"][0]
        chart["status"] = "complete"
        chart["rows"] = [[250.0, "316L"]]

        range_table = extraction["extractions"][1]
        range_table["status"] = "complete"
        range_table["layout"] = [
            {"variable_index": 0, "component": "value"},
            {"variable_index": 1, "component": "lower_bound"},
            {"variable_index": 1, "component": "upper_bound"},
            {"variable_index": 1, "component": "lower_inclusive"},
            {"variable_index": 1, "component": "upper_inclusive"},
        ]
        range_table["rows"] = [
            ["Seawater + 1.5M NaCl", 2.1, 2.4, None, None],
            ["Seawater + 5.5M NaCl", None, 1.0, None, False],
        ]

        long_table = extraction["extractions"][2]
        long_table["status"] = "complete"
        long_table["rows"] = [
            ["304L", "Ecor (mV)", "300 ppm Cl-", -185, 18],
            ["304L", "Corrosion rate (mpy)", "300 ppm Cl-", 0.082, 18],
            ["304L", "Epit (mV)", "300 ppm Cl-", 287, 18],
            ["316L", "Epit (mV)", "Natural seawater", None, 25],
        ]
        return extraction

    def _write_and_validate(self, extraction: dict[str, object]):
        path = self.project_root / "extraction.json"
        path.write_text(json.dumps(extraction), encoding="utf-8")
        return validate(path, SCHEMA, self.project_root)

    def test_preparation_has_complete_coverage_and_default_layouts(self) -> None:
        extraction = build_extraction_skeleton(self.paper_dir, self.project_root)
        self.assertEqual(extraction["schema_version"], 1)
        self.assertEqual(
            extraction["source_catalog"],
            "mineru_output/paper_99/paper_99_figures.json",
        )
        self.assertEqual(len(extraction["extractions"]), 5)
        self.assertEqual(extraction["extractions"][0]["status"], "unprocessed")
        self.assertEqual(
            extraction["extractions"][0]["layout"],
            [
                {"variable_index": 0, "component": "value"},
                {"variable_index": 1, "component": "value"},
            ],
        )
        self.assertEqual(extraction["extractions"][3]["status"], "needs_review")
        self.assertEqual(
            extraction["extractions"][4]["status"], "not_data_figure"
        )

    def test_existing_output_is_not_silently_overwritten(self) -> None:
        output = self.project_root / "paper_99_figure_extractions.json"
        arguments = [
            "--input_path",
            str(self.paper_dir),
            "--output_file",
            str(output),
            "--project-root",
            str(self.project_root),
        ]
        self.assertEqual(prepare_main(arguments), 0)
        original = output.read_bytes()
        self.assertEqual(prepare_main(arguments), 1)
        self.assertEqual(output.read_bytes(), original)

    def test_paper_49_table_3_ranges_and_table_5_long_rows_validate(self) -> None:
        statuses = self._write_and_validate(self._completed_extraction())
        self.assertEqual(statuses["complete"], 3)
        self.assertEqual(statuses["needs_review"], 1)
        self.assertEqual(statuses["not_data_figure"], 1)

    def test_visible_error_bar_absolute_bounds_validate(self) -> None:
        extraction = self._completed_extraction()
        chart = extraction["extractions"][0]
        chart["layout"] = [
            {"variable_index": 0, "component": "value"},
            {"variable_index": 0, "component": "lower_bound"},
            {"variable_index": 0, "component": "upper_bound"},
            {"variable_index": 1, "component": "value"},
        ]
        chart["rows"] = [[250.0, 240.0, 260.0, "316L"]]
        self._write_and_validate(extraction)

    def test_paper_9_figure_3_markerless_chart_has_no_discrete_values(self) -> None:
        extraction = self._completed_extraction()
        chart = extraction["extractions"][0]
        chart["status"] = "no_discrete_values"
        chart["rows"] = []
        self._write_and_validate(extraction)

    def test_paper_9_figure_9_discrete_rows_validate(self) -> None:
        extraction = self._completed_extraction()
        self.assertEqual(extraction["extractions"][0]["rows"], [[250.0, "316L"]])
        self._write_and_validate(extraction)

    def test_wrong_row_width_fails(self) -> None:
        extraction = self._completed_extraction()
        extraction["extractions"][0]["rows"] = [[250.0]]
        with self.assertRaisesRegex(ExtractionValidationError, "layout has 2"):
            self._write_and_validate(extraction)

    def test_catalog_value_type_is_enforced(self) -> None:
        extraction = self._completed_extraction()
        extraction["extractions"][0]["rows"] = [["250", "316L"]]
        with self.assertRaisesRegex(ExtractionValidationError, "data_type numeric"):
            self._write_and_validate(extraction)

    def test_partial_rows_require_notes(self) -> None:
        extraction = self._completed_extraction()
        chart = extraction["extractions"][0]
        chart["status"] = "partial"
        chart["rows"] = [[250.0, None]]
        chart["notes"] = ["The alloy label for the first marker is unreadable."]
        self._write_and_validate(extraction)

        chart["notes"] = []
        with self.assertRaisesRegex(ExtractionValidationError, "non-empty"):
            self._write_and_validate(extraction)

    def test_invalid_variable_index_fails(self) -> None:
        extraction = self._completed_extraction()
        extraction["extractions"][0]["layout"].append(
            {"variable_index": 99, "component": "value"}
        )
        extraction["extractions"][0]["rows"][0].append("unexpected")
        with self.assertRaisesRegex(ExtractionValidationError, "outside"):
            self._write_and_validate(extraction)

    def test_duplicate_layout_component_fails(self) -> None:
        extraction = self._completed_extraction()
        extraction["extractions"][0]["layout"].append(
            {"variable_index": 0, "component": "value"}
        )
        extraction["extractions"][0]["rows"][0].append(250.0)
        with self.assertRaisesRegex(ExtractionValidationError, "repeats variable"):
            self._write_and_validate(extraction)

    def test_bounds_on_non_numeric_variable_fail(self) -> None:
        extraction = self._completed_extraction()
        extraction["extractions"][0]["layout"][1]["component"] = "lower_bound"
        with self.assertRaisesRegex(ExtractionValidationError, "non-numeric"):
            self._write_and_validate(extraction)

    def test_reversed_bounds_fail(self) -> None:
        extraction = self._completed_extraction()
        extraction["extractions"][1]["rows"][0][1:3] = [2.4, 2.1]
        with self.assertRaisesRegex(ExtractionValidationError, "greater than"):
            self._write_and_validate(extraction)

    def test_central_value_outside_error_bar_fails(self) -> None:
        extraction = self._completed_extraction()
        chart = extraction["extractions"][0]
        chart["layout"] = [
            {"variable_index": 0, "component": "value"},
            {"variable_index": 0, "component": "lower_bound"},
            {"variable_index": 0, "component": "upper_bound"},
            {"variable_index": 1, "component": "value"},
        ]
        chart["rows"] = [[270.0, 240.0, 260.0, "316L"]]
        with self.assertRaisesRegex(ExtractionValidationError, "above upper_bound"):
            self._write_and_validate(extraction)

    def test_duplicate_and_missing_catalog_entries_fail(self) -> None:
        extraction = self._completed_extraction()
        extraction["extractions"][1]["catalog_id"] = extraction["extractions"][0][
            "catalog_id"
        ]
        with self.assertRaisesRegex(ExtractionValidationError, "duplicate"):
            self._write_and_validate(extraction)

        extraction = self._completed_extraction()
        extraction["extractions"].pop()
        with self.assertRaisesRegex(ExtractionValidationError, "missing catalog"):
            self._write_and_validate(extraction)

    def test_catalog_review_and_unprocessed_statuses_fail(self) -> None:
        extraction = self._completed_extraction()
        review = extraction["extractions"][3]
        review["status"] = "complete"
        review["rows"] = [["X"]]
        with self.assertRaisesRegex(ExtractionValidationError, "must remain needs_review"):
            self._write_and_validate(extraction)

        extraction = self._completed_extraction()
        extraction["extractions"][0]["status"] = "unprocessed"
        extraction["extractions"][0]["rows"] = []
        with self.assertRaisesRegex(ExtractionValidationError, "not final"):
            self._write_and_validate(extraction)

    def test_inclusive_flag_requires_bound_value(self) -> None:
        extraction = self._completed_extraction()
        extraction["extractions"][1]["rows"][1][3] = True
        with self.assertRaisesRegex(
            ExtractionValidationError, "lower_inclusive without a lower_bound"
        ):
            self._write_and_validate(extraction)

    def test_source_catalog_path_must_be_project_relative(self) -> None:
        extraction = self._completed_extraction()
        extraction["source_catalog"] = str(self.catalog_path.resolve())
        with self.assertRaisesRegex(ExtractionValidationError, "relative"):
            self._write_and_validate(extraction)

        extraction = self._completed_extraction()
        extraction["source_catalog"] = "mineru_output\\paper_99\\paper_99_figures.json"
        with self.assertRaisesRegex(ExtractionValidationError, "POSIX-style"):
            self._write_and_validate(extraction)


if __name__ == "__main__":
    unittest.main()
