from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from types import ModuleType


SKILL_DIR = Path(__file__).resolve().parents[1]


def _load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


prepare_module = _load_module(
    "prepare_digitization_v2", SKILL_DIR / "scripts" / "prepare_digitization.py"
)
validate_module = _load_module(
    "validate_digitization_v2", SKILL_DIR / "scripts" / "validate_digitization.py"
)


class DigitizationContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir_context = tempfile.TemporaryDirectory()
        self.temp_dir = Path(self.temp_dir_context.name)
        self.image = self.temp_dir / "paper_9_page_0008_item_0002.jpg"
        self.metadata_path = self.image.with_suffix(".json")
        self.image.write_bytes(b"synthetic-jpeg-fixture")
        self.metadata = {
            "paper_reference": "9",
            "source_chart_manifest": "paper_9_charts.json",
            "plot_metadata": {
                "chart_id": "page_0008_item_0002",
                "image_path": "images/source.jpg",
                "caption": "Pitting potential versus pH.",
                "reason_code": "direct_pitting_potential_plot",
                "reason": "Pitting potential is directly plotted.",
                "confidence": 0.98,
                "relevant_panels": [],
                "target_series": ["alloy A pitting potential"],
                "x_axis": {"label": "pH", "unit": "", "scale": "linear"},
                "y_axis": {"label": "Ep", "unit": "mV", "scale": "linear"},
            },
            "plot_data": [],
        }
        self.metadata_path.write_text(json.dumps(self.metadata), encoding="utf-8")
        self.result = prepare_module.prepare(self.metadata)

    def tearDown(self) -> None:
        self.temp_dir_context.cleanup()

    def _complete_result(self) -> dict:
        result = copy.deepcopy(self.result)
        result.update(
            {
                "digitization_status": "complete",
                "digitization_notes": [],
                "plot_data": [
                    {
                        "series_id": "alloy_a_nacl",
                        "tags": [
                            {"name": "material", "value": "Alloy A"},
                            {"name": "test_solution", "value": "NaCl"},
                        ],
                        "x_axis": {
                            "label": "pH",
                            "type": "numeric",
                            "unit": "",
                            "scale": "linear",
                            "is_target": False,
                        },
                        "y_axis": {
                            "label": "Ep",
                            "type": "numeric",
                            "unit": "mV",
                            "scale": "linear",
                            "is_target": True,
                        },
                        "data_points": [
                            {
                                "x": 3,
                                "y": 200,
                                "y_lower": 180,
                                "y_upper": 225,
                                "y_interval_meaning": "25th and 75th percentile",
                                "label": "Sample A",
                            }
                        ],
                    }
                ],
            }
        )
        return result

    def _validate(self, result: dict):
        return validate_module.validate(
            result, self.metadata, self.image, self.metadata_path
        )

    def test_complete_numeric_series_with_label_and_interval(self) -> None:
        self.assertEqual(self._validate(self._complete_result()), ("complete", 1, 1))

    def test_categorical_range_only_point(self) -> None:
        result = self._complete_result()
        series = result["plot_data"][0]
        series["x_axis"]["type"] = "categorical"
        series["data_points"] = [
            {
                "x": "UNS S30400 in NaCl",
                "y": None,
                "y_lower": 50,
                "y_upper": 90,
                "y_interval_meaning": "experimental range",
            }
        ]
        self.assertEqual(self._validate(result), ("complete", 1, 1))

    def test_rejects_unprocessed_template(self) -> None:
        with self.assertRaisesRegex(validate_module.ValidationError, "finalized"):
            self._validate(self.result)

    def test_rejects_schema_error(self) -> None:
        result = self._complete_result()
        del result["plot_data"][0]["y_axis"]["unit"]
        with self.assertRaisesRegex(validate_module.ValidationError, "JSON Schema"):
            self._validate(result)

    def test_rejects_duplicate_series_ids(self) -> None:
        result = self._complete_result()
        result["plot_data"].append(copy.deepcopy(result["plot_data"][0]))
        with self.assertRaisesRegex(validate_module.ValidationError, "duplicate series_id"):
            self._validate(result)

    def test_rejects_wrong_coordinate_type(self) -> None:
        result = self._complete_result()
        result["plot_data"][0]["data_points"][0]["x"] = "three"
        with self.assertRaisesRegex(validate_module.ValidationError, "numeric axis"):
            self._validate(result)

    def test_rejects_invalid_interval(self) -> None:
        result = self._complete_result()
        point = result["plot_data"][0]["data_points"][0]
        point["y_lower"] = 250
        with self.assertRaisesRegex(validate_module.ValidationError, "must not exceed"):
            self._validate(result)

    def test_rejects_central_value_outside_interval(self) -> None:
        result = self._complete_result()
        result["plot_data"][0]["data_points"][0]["y"] = 250
        with self.assertRaisesRegex(validate_module.ValidationError, "fall within"):
            self._validate(result)

    def test_rejects_both_axes_as_targets(self) -> None:
        result = self._complete_result()
        result["plot_data"][0]["x_axis"]["is_target"] = True
        with self.assertRaisesRegex(validate_module.ValidationError, "exactly one axis"):
            self._validate(result)

    def test_rejects_points_in_deferred_result(self) -> None:
        result = self._complete_result()
        result["digitization_status"] = "needs_review"
        result["digitization_notes"] = ["Series mapping is unclear."]
        with self.assertRaisesRegex(validate_module.ValidationError, "JSON Schema"):
            self._validate(result)

    def test_rejects_identifier_mismatch(self) -> None:
        result = self._complete_result()
        result["paper_reference"] = "10"
        with self.assertRaisesRegex(validate_module.ValidationError, "paired metadata"):
            self._validate(result)


if __name__ == "__main__":
    unittest.main()
