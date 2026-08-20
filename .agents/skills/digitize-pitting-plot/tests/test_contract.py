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
    "prepare_digitization", SKILL_DIR / "scripts" / "prepare_digitization.py"
)
validate_module = _load_module(
    "validate_digitization", SKILL_DIR / "scripts" / "validate_digitization.py"
)


class DigitizationContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir_context = tempfile.TemporaryDirectory()
        self.temp_dir = Path(self.temp_dir_context.name)
        self.image = self.temp_dir / "paper_9_page_0008_item_0002.jpg"
        self.metadata_path = self.image.with_suffix(".json")
        self.output = self.temp_dir / "digitized" / self.metadata_path.name
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
        self.metadata_path.write_text(
            json.dumps(self.metadata), encoding="utf-8"
        )
        self.result = prepare_module.prepare(
            self.metadata,
            self.image,
            self.metadata_path,
            self.output,
        )

    def tearDown(self) -> None:
        self.temp_dir_context.cleanup()

    def _complete_result(self) -> dict:
        result = copy.deepcopy(self.result)
        result["digitization"] = {
            "status": "complete",
            "reason_code": "digitized_discrete_marks",
            "reason": "All target markers were digitized.",
            "confidence": 0.95,
            "issues": [],
            "panels": [
                {
                    "panel_id": "whole_image",
                    "label_raw": "",
                    "notes": "",
                    "axes": [
                        {
                            "axis_id": "x_ph",
                            "dimension": "x",
                            "side": "bottom",
                            "label_raw": "pH",
                            "unit_raw": "",
                            "scale": "linear",
                            "value_type": "numeric",
                            "target_metric": False,
                            "breaks": [],
                        },
                        {
                            "axis_id": "y_ep",
                            "dimension": "y",
                            "side": "left",
                            "label_raw": "Ep",
                            "unit_raw": "mV",
                            "scale": "linear",
                            "value_type": "numeric",
                            "target_metric": True,
                            "breaks": [],
                        },
                        {
                            "axis_id": "y_ancillary",
                            "dimension": "y",
                            "side": "right",
                            "label_raw": "Corrosion rate",
                            "unit_raw": "mm/yr",
                            "scale": "linear",
                            "value_type": "numeric",
                            "target_metric": False,
                            "breaks": [],
                        },
                    ],
                    "series": [
                        {
                            "series_id": "alloy_a_nacl",
                            "target_series_refs": ["alloy A pitting potential"],
                            "labels_raw": ["Alloy A", "NaCl"],
                            "tags": [
                                {
                                    "key": "material",
                                    "value_raw": "Alloy A",
                                    "evidence_source": "plot_annotation",
                                },
                                {
                                    "key": "test_solution",
                                    "value_raw": "NaCl",
                                    "evidence_source": "legend",
                                },
                            ],
                            "x_axis_id": "x_ph",
                            "y_axis_id": "y_ep",
                            "visual_encoding": {
                                "color_raw": "black",
                                "marker_raw": "filled circle",
                                "line_raw": "solid",
                                "fill_raw": "filled",
                            },
                            "observations": [
                                {
                                    "observation_id": "alloy_a_nacl_point_001",
                                    "mark_type": "marker",
                                    "values": [
                                        {
                                            "axis_id": "x_ph",
                                            "value": 3.0,
                                            "interval": None,
                                        },
                                        {
                                            "axis_id": "y_ep",
                                            "value": 200.0,
                                            "interval": {
                                                "lower": 180.0,
                                                "upper": 225.0,
                                                "kind": "error_bar",
                                                "meaning_raw": "25th and 75th percentile",
                                            },
                                        },
                                    ],
                                    "label_raw": "",
                                    "confidence": 0.93,
                                    "notes": "",
                                }
                            ],
                        }
                    ],
                    "omitted_series": [
                        {
                            "label_raw": "Corrosion rate",
                            "reason_code": "non_pitting_metric",
                            "notes": "Uses the right y-axis.",
                        }
                    ],
                }
            ],
        }
        return result

    def _validate(self, result: dict):
        return validate_module.validate(
            result,
            self.metadata,
            self.image,
            self.metadata_path,
            self.output,
        )

    def test_complete_dual_axis_and_error_interval(self) -> None:
        self.assertEqual(self._validate(self._complete_result()), ("complete", 1, 1, 0))

    def test_categorical_range_only_observation(self) -> None:
        result = self._complete_result()
        panel = result["digitization"]["panels"][0]
        panel["axes"][0]["value_type"] = "categorical"
        observation = panel["series"][0]["observations"][0]
        observation["mark_type"] = "range"
        observation["values"][0]["value"] = "UNS S30400 in NaCl"
        observation["values"][1] = {
            "axis_id": "y_ep",
            "value": None,
            "interval": {
                "lower": 50.0,
                "upper": 90.0,
                "kind": "reported_range",
                "meaning_raw": "experimental range",
            },
        }
        self.assertEqual(self._validate(result), ("complete", 1, 1, 0))

    def test_rejects_mismatched_hash(self) -> None:
        result = self._complete_result()
        result["source"]["image"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(validate_module.ValidationError, "does not match"):
            self._validate(result)

    def test_rejects_missing_target_coverage(self) -> None:
        result = self._complete_result()
        result["digitization"]["panels"][0]["series"] = []
        with self.assertRaisesRegex(validate_module.ValidationError, "coverage mismatch"):
            self._validate(result)

    def test_rejects_duplicate_observation_ids(self) -> None:
        result = self._complete_result()
        series = result["digitization"]["panels"][0]["series"][0]
        series["observations"].append(copy.deepcopy(series["observations"][0]))
        with self.assertRaisesRegex(validate_module.ValidationError, "duplicate observation_id"):
            self._validate(result)

    def test_rejects_nonexistent_axis_reference(self) -> None:
        result = self._complete_result()
        result["digitization"]["panels"][0]["series"][0]["y_axis_id"] = "missing"
        with self.assertRaisesRegex(validate_module.ValidationError, "panel y-axis"):
            self._validate(result)

    def test_rejects_invalid_interval(self) -> None:
        result = self._complete_result()
        interval = result["digitization"]["panels"][0]["series"][0]["observations"][0]["values"][1]["interval"]
        interval["lower"] = 250.0
        with self.assertRaisesRegex(validate_module.ValidationError, "must not exceed"):
            self._validate(result)

    def test_rejects_observations_in_deferred_output(self) -> None:
        result = self._complete_result()
        result["digitization"].update(
            {
                "status": "needs_review",
                "reason_code": "ambiguous_mark_semantics",
                "reason": "Marks cannot be interpreted without more context.",
                "issues": [
                    {
                        "code": "ambiguous_mark_semantics",
                        "message": "The plotted ellipses have unclear semantics.",
                        "target_series_refs": ["alloy A pitting potential"],
                    }
                ],
            }
        )
        with self.assertRaisesRegex(validate_module.ValidationError, "must not contain observations"):
            self._validate(result)


if __name__ == "__main__":
    unittest.main()

