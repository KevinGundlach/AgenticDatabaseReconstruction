"""Contract fixtures and command-line checks. No PDF access or model calls."""

import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from validate_output import SCHEMA_PATH, load_json, validate_document


def fixture(cell=300):
    return {
        "paper_name": "80_example.pdf", "reference_number": 80,
        "series": [{
            "source": "Figure 3(a), alloy B", "method": "digitized", "status": "complete",
            "columns": [{"name": "pH"}, {"name": "Epit", "default_unit": "mV (SCE)",
                                                "default_error_bar_type": "confidence_interval_95"}],
            "rows": [[2, cell]], "notes": ""
        }]
    }


class ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = load_json(SCHEMA_PATH)

    def errors(self, document):
        return validate_document(document, self.schema)

    def test_valid_cells_and_no_mutation(self):
        cells = [300, "Bal.", "not tested", ">300", None,
                 {"value": 120, "unit": "ppm"}, {"min": 300}, {"max": 300},
                 {"min": 290, "max": 310}, {"value": 300, "min": 290, "max": 310},
                 {"value": 300, "plus_minus": 10},
                 {"value": 0.92, "label": "Chromates Only"},
                 {"min": 300, "label": ">300"},
                 {"value": 300, "min": 290, "max": 310, "label": "estimated"},
                 {"value": 300, "plus_minus": 5, "plus_minus_unit": "%", "error_bar_type": "unknown"},
                 {"value": 300, "plus_minus": 0, "error_bar_type": "confidence_interval_99"}]
        for cell in cells:
            with self.subTest(cell=cell):
                doc = fixture(cell)
                original = copy.deepcopy(doc)
                self.assertEqual([], self.errors(doc))
                self.assertEqual(original, doc)

    def test_invalid_cells(self):
        cells = [True, [], {}, {"unit": "ppm"}, {"value": "300"}, {"value": None},
                 {"value": True}, {"min": 310, "max": 290},
                 {"value": 280, "min": 290}, {"value": 320, "max": 310},
                 {"value": 300, "plus_minus": -1}, {"plus_minus": 10},
                 {"value": 300, "plus_minus": 10, "min": 290},
                 {"value": 300, "plus_minus": 10, "max": 310},
                 {"value": 300, "plus_minus_unit": "%"},
                 {"value": 300, "unit": None}, {"value": 300, "error_bar_type": " "},
                 {"label": "Chromates Only"}, {"value": 300, "label": ""},
                 {"value": 300, "label": " "}, {"value": 300, "label": None},
                 {"value": 300, "label": 1},
                 {"value": 300, "extra": 1}, float("inf"), float("nan")]
        for cell in cells:
            with self.subTest(cell=cell):
                self.assertTrue(self.errors(fixture(cell)))

    def test_statuses_and_empty_paper(self):
        complete = fixture()
        self.assertFalse(self.errors(complete))
        complete["series"][0]["notes"] = "Plot and prose disagree on this value."
        self.assertFalse(self.errors(complete))
        doc = fixture(None)
        series = doc["series"][0]
        series["status"] = "partial"
        series["notes"] = "Point obscured."
        self.assertFalse(self.errors(doc))
        series["notes"] = " "
        self.assertTrue(self.errors(doc))
        series.update(status="none", rows=[], columns=[], notes="Source is unreadable.")
        self.assertFalse(self.errors(doc))
        series["rows"] = [[1]]
        self.assertTrue(self.errors(doc))
        doc["series"] = []
        self.assertFalse(self.errors(doc))

    def test_columns_shape_and_identity(self):
        mutations = [
            lambda d: d["series"][0]["rows"].append([1]),
            lambda d: d["series"][0]["columns"][1].update(name="pH"),
            lambda d: d["series"][0]["columns"][0].update(name=" "),
            lambda d: d["series"][0]["columns"][0].update(data_type="number"),
            lambda d: d["series"][0].update(default_error_bar_type="stdev"),
            lambda d: d["series"][0].update(rows=[]),
            lambda d: d["series"][0].update(method="mixed"),
            lambda d: d.update(reference_number=81),
            lambda d: d.update(paper_name="papers/80_example.pdf"),
            lambda d: d.update(paper_name="papers\\80_example.pdf"),
        ]
        for mutate in mutations:
            doc = fixture()
            mutate(doc)
            self.assertTrue(self.errors(doc), doc)
        doc = fixture()
        doc["series"][0]["method"] = "transcribed"
        doc["series"][0]["rows"] = [["A", "Bal."], ["B", {"value": 120, "unit": "ppm"}]]
        self.assertFalse(self.errors(doc))

    def test_documented_example(self):
        conventions = SCHEMA_PATH.with_name("output_conventions.md").read_text(encoding="utf-8")
        example = conventions.split("```json\n", 1)[1].split("```", 1)[0]
        self.assertFalse(self.errors(json.loads(example)))

    def test_cli_and_strict_json(self):
        script = Path(__file__).with_name("validate_output.py")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "output.json"
            for content, expected in [
                (json.dumps(fixture()), 0),
                (json.dumps(fixture({})), 1),
                ('{"x": 1, "x": 2}', 1),
                ('{"x": NaN}', 1),
                (json.dumps(fixture()).replace("300", "1e999"), 1),
                ('{', 1),
            ]:
                path.write_text(content, encoding="utf-8")
                result = subprocess.run([sys.executable, str(script), "--input", str(path)], capture_output=True, text=True)
                self.assertEqual(expected, result.returncode, result.stderr)
            missing = subprocess.run([sys.executable, str(script), "--input", str(path.with_name("missing.json"))], capture_output=True)
            self.assertEqual(2, missing.returncode)
            pdf = subprocess.run([sys.executable, str(script), "--input", str(path.with_suffix(".pdf"))], capture_output=True)
            self.assertEqual(2, pdf.returncode)


if __name__ == "__main__":
    unittest.main()
