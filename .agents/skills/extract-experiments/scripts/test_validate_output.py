"""Exercise the skill's standalone validation CLI using synthetic extractions."""

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


SKILL_DIR = Path(__file__).resolve().parents[1]


def example_paper():
    return {
        "schema_version": "1.0",
        "paper_name": "80_example.pdf",
        "reference_number": 80,
        "experiments": [{
            "alloy": {
                "preparation": "Solution treated at 1050 degC and water quenched.",
                "composition": [
                    {"element_symbol": "Cr", "amount": {"value": 18, "unit": "wt%"}},
                    {"element_symbol": "Fe", "amount": "balance"},
                    {"element_symbol": "Mo", "amount": None},
                ],
                "microstructure": "",
                "material_class": "Fe Alloy",
            },
            "test_temperature": {"value": 25, "unit": "degC"},
            "test_solution": {
                "preparation": "Deaerated with nitrogen.",
                "solvent": "Water",
                "composition": [{"solute": "NaCl", "amount": {"value": 0.1, "unit": "mol/L"}}],
                "ph": None,
                "chloride_concentration": None,
            },
            "test_method": {
                "test_types": ["potentiodynamic polarization"],
                "procedure_description": "Scanned at 0.1 mV/s, then at 0.5 mV/s above 200 mV.",
                "scan_rate": None,
                "potential_step": None,
                "step_hold_duration": None,
                "pitting_criterion": "",
            },
            "pitting_potential": {"value": 300, "min": 280, "max": 330, "unit": "mV (SCE)"},
            "result_note": "Mean with asymmetric error bars.",
            "failure_notes": "",
        }],
    }


class StandaloneValidatorTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        # Only the skill is copied; no project source, configuration, or imports.
        self.skill = self.root / "extract-experiments"
        shutil.copytree(SKILL_DIR, self.skill, ignore=shutil.ignore_patterns("__pycache__"))
        self.script = self.skill / "scripts" / "validate_output.py"
        self.input = self.root / "extraction.json"

    def run_validator(self, data=None, raw=None):
        content = raw if raw is not None else json.dumps(data, allow_nan=False)
        self.input.write_text(content, encoding="utf-8")
        result = subprocess.run(
            # Ignore PYTHONPATH but retain normal sibling-module imports.
            [sys.executable, "-E", str(self.script), "--input", str(self.input)],
            cwd=self.root, capture_output=True, text=True, check=False,
        )
        self.assertEqual(self.input.read_text(encoding="utf-8"), content)
        return result

    def test_standalone_valid_record_and_empty_paper(self):
        result = self.run_validator(example_paper())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("1 experiments, 0 flagged rows", result.stdout)
        data = example_paper()
        data["experiments"] = []
        self.assertEqual(self.run_validator(data).returncode, 0)

    def test_flagged_row_is_retained_and_reported(self):
        data = example_paper()
        data["experiments"][0]["alloy"]["composition"] = []
        data["experiments"][0]["failure_notes"] = "Figure 2: cannot recover alloy assignment."
        result = self.run_validator(data)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("1 flagged rows", result.stdout)
        self.assertIn("experiments indices: 0", result.stdout)

    def test_missing_null_failure_notes_and_removed_id_are_rejected(self):
        for mode in ("missing", "null", "experiment_id"):
            with self.subTest(mode=mode):
                data = example_paper()
                row = data["experiments"][0]
                if mode == "missing":
                    del row["failure_notes"]
                elif mode == "null":
                    row["failure_notes"] = None
                else:
                    row["experiment_id"] = "invented"
                self.assertEqual(self.run_validator(data).returncode, 1)

    def test_cross_field_bounds_and_empty_measurements_are_rejected(self):
        for measurement in ({}, {"min": 350, "max": 300},
                            {"value": 400, "max": 300}, {"min": 300, "plus_minus": 10}):
            with self.subTest(measurement=measurement):
                data = example_paper()
                data["experiments"][0]["pitting_potential"] = measurement
                result = self.run_validator(data)
                self.assertEqual(result.returncode, 1)
                self.assertIn("/experiments/0/pitting_potential", result.stderr)

    def test_strict_json_and_overflow_are_rejected(self):
        for raw in ('{"paper_name":"one", "paper_name":"two"}', '{"x": NaN}', '{"x": Infinity}'):
            with self.subTest(raw=raw):
                result = self.run_validator(raw=raw)
                self.assertEqual(result.returncode, 1)
                self.assertIn("Invalid JSON", result.stderr)
        raw = json.dumps(example_paper()).replace('"value": 300', '"value": 1e309')
        self.assertEqual(self.run_validator(raw=raw).returncode, 1)

    def test_missing_schema_is_setup_failure(self):
        (self.skill / "references" / "paper_extraction.schema.json").unlink()
        self.assertEqual(self.run_validator(example_paper()).returncode, 2)


if __name__ == "__main__":
    unittest.main()
