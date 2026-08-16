import csv
import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from corrosion_plot_digitizer.finalize import RawDigitizationError, finalize_spec


def raw_spec(image_path: Path) -> dict:
    return {
        "schema_version": 1,
        "paper_id": "80",
        "figure_id": "1",
        "source_image": str(image_path),
        "caption": "Pitting potentials for AlNb alloys.",
        "x_axis": {"label": "Nb", "unit": "at.%", "scale": "linear"},
        "y_axis": {
            "label": "Potential",
            "unit": "mV",
            "reference": "SCE",
            "scale": "linear",
        },
        "composition_context": {"base_element": "Al", "solute_element": "Nb"},
        "calibration": {
            "plot_box": [10, 10, 90, 90],
            "x": [{"pixel": 10, "value": 0}, {"pixel": 90, "value": 40}],
            "y": [{"pixel": 90, "value": -500}, {"pixel": 10, "value": 1000}],
        },
        "series": [
            {
                "series_id": "ep",
                "label": "Ep",
                "metric": "pitting_potential",
                "sample_condition": "fresh",
                "marker_type": "triangle",
                "points": [{"x": 5, "y": 100, "confidence": 0.9}],
            },
            {
                "series_id": "er",
                "label": "ER",
                "metric": "repassivation_potential",
                "points": [{"x": 5, "y": 0, "confidence": 0.9}],
            },
        ],
    }


class FinalizeTests(unittest.TestCase):
    def test_finalizer_converts_with_python_and_filters_metric(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            image_path = root / "figure.png"
            Image.new("RGB", (100, 100), "white").save(image_path)
            input_path = root / "raw.json"
            input_path.write_text(json.dumps(raw_spec(image_path)), encoding="utf-8")
            output = root / "output"

            metadata = finalize_spec(input_path, output)

            self.assertEqual(metadata["point_count"], 1)
            self.assertEqual(len(metadata["excluded_series"]), 1)
            with (output / "points.csv").open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["x_unit_raw"], "at.%")
            self.assertEqual(rows[0]["x_unit_normalized"], "wt.%")
            self.assertAlmostEqual(float(rows[0]["x_value_normalized"]), 15.3423, places=4)
            composition = json.loads(rows[0]["composition_wt_percent_json"])
            self.assertAlmostEqual(sum(composition.values()), 100.0, places=8)
            self.assertTrue((output / "digitization_overlay.png").is_file())

    def test_model_supplied_normalized_field_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            image_path = root / "figure.png"
            Image.new("RGB", (100, 100), "white").save(image_path)
            spec = raw_spec(image_path)
            spec["series"][0]["points"][0]["x_normalized"] = 15.36
            input_path = root / "raw.json"
            input_path.write_text(json.dumps(spec), encoding="utf-8")
            with self.assertRaises(RawDigitizationError):
                finalize_spec(input_path, root / "output")


if __name__ == "__main__":
    unittest.main()
