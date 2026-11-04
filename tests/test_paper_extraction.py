"""Contract tests for the full-paper JSON Schema and Pydantic models."""

import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator
from pydantic import ValidationError

from models import Measurement, PaperExtraction


SCHEMA_PATH = Path(__file__).resolve().parents[1] / "models" / "paper_extraction.schema.json"


def example_paper():
    return {
        "schema_version": "1.0",
        "paper_name": "example.pdf",
        "reference_number": 1,
        "experiments": [{
            "alloy": {
                "preparation": "No heat treatment was applied.",
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
                "ph": 7,
                "chloride_concentration": None,
            },
            "test_method": {
                "test_types": ["potentiodynamic polarization"],
                "procedure_description": "",
                "scan_rate": {"value": 0.1, "unit": "mV/s"},
                "potential_step": None,
                "step_hold_duration": None,
                "pitting_criterion": "",
            },
            "pitting_potential": {"value": 300, "unit": "mV (SCE)", "plus_minus": 10},
            "result_note": "",
            "failure_notes": "",
        }],
    }


class PaperExtractionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        cls.validator = Draft202012Validator(cls.schema)

    def assert_valid(self, data):
        self.validator.validate(data)
        model = PaperExtraction.model_validate(data)
        # Unused measurement subfields are omitted; required nulls stay present.
        encoded = model.model_dump_json(exclude_unset=True)
        decoded = json.loads(encoded)
        self.validator.validate(decoded)
        self.assertEqual(decoded, data)
        return model

    def assert_invalid(self, data):
        self.assertFalse(self.validator.is_valid(data))
        with self.assertRaises(ValidationError):
            PaperExtraction.model_validate(data)

    def test_schema_is_valid_and_matches_models(self):
        Draft202012Validator.check_schema(self.schema)
        self.assertEqual(self.schema, PaperExtraction.model_json_schema())
        self.assertEqual(set(self.schema["$defs"]["Measurement"]["properties"]),
                         {"value", "min", "max", "unit", "plus_minus"})

    def test_full_record_round_trip(self):
        model = self.assert_valid(example_paper())
        self.assertIsInstance(model.experiments[0].pitting_potential, Measurement)

    def test_empty_paper(self):
        self.assert_valid({"schema_version": "1.0", "paper_name": "example.pdf",
                           "reference_number": None, "experiments": []})

    def test_failure_notes_are_required_text_and_retain_unresolved_rows(self):
        data = example_paper()
        data["experiments"][0]["alloy"]["composition"] = []
        data["experiments"][0]["failure_notes"] = (
            "Figure 3: cannot determine which alloy the 300 mV point represents."
        )
        self.assert_valid(data)
        data["experiments"][0]["failure_notes"] = None
        self.assert_invalid(data)
        del data["experiments"][0]["failure_notes"]
        self.assert_invalid(data)

    def test_missing_information_uses_empty_strings_arrays_and_nulls(self):
        data = example_paper()
        experiment = data["experiments"][0]
        experiment["alloy"] = {"preparation": "", "composition": [],
                                "microstructure": "", "material_class": ""}
        experiment["test_temperature"] = None
        experiment["test_solution"] = {"preparation": "", "solvent": "", "composition": [],
                                        "ph": None, "chloride_concentration": None}
        experiment["test_method"] = {"test_types": [], "procedure_description": "",
                                      "scan_rate": None, "potential_step": None,
                                      "step_hold_duration": None, "pitting_criterion": ""}
        experiment["pitting_potential"] = None
        experiment["result_note"] = "No pitting observed within the tested potential range."
        self.assert_valid(data)

    def test_measurement_forms_and_dimensionless_ph(self):
        values = [
            {"value": 0},
            {"min": 300},
            {"max": 350},
            {"min": 300, "max": 350, "unit": "mV (SCE)"},
            {"value": 325, "min": 300, "max": 350},
            {"value": 300, "plus_minus": 0},
            {"value": None, "min": 300, "max": None, "plus_minus": None},
        ]
        for value in values:
            with self.subTest(value=value):
                data = example_paper()
                data["experiments"][0]["pitting_potential"] = value
                self.assert_valid(data)
        for ph in (None, -0.5, 14.5, {"value": 7, "plus_minus": 0.2}, {"min": 6.8, "max": 7.2}):
            with self.subTest(ph=ph):
                data = example_paper()
                data["experiments"][0]["test_solution"]["ph"] = ph
                self.assert_valid(data)

    def test_fields_are_required_and_strings_are_not_nullable(self):
        for key in ("preparation", "microstructure", "material_class"):
            for missing in (True, False):
                with self.subTest(key=key, missing=missing):
                    data = example_paper()
                    if missing:
                        del data["experiments"][0]["alloy"][key]
                    else:
                        data["experiments"][0]["alloy"][key] = None
                    self.assert_invalid(data)
        data = example_paper()
        del data["experiments"][0]["test_temperature"]
        self.assert_invalid(data)

    def test_bad_measurement_shapes_are_rejected_by_both(self):
        invalid = [
            {}, {"unit": "mV"}, {"value": None}, {"value": None, "min": None, "max": None},
            {"plus_minus": 10}, {"min": 300, "plus_minus": 10},
            {"value": 300, "plus_minus": -1}, {"value": "300"},
            {"value": True}, {"value": 300, "unit": None},
        ]
        for value in invalid:
            with self.subTest(value=value):
                data = example_paper()
                data["experiments"][0]["pitting_potential"] = value
                self.assert_invalid(data)

    def test_removed_metadata_and_extra_fields_are_rejected(self):
        for key in ("plus_minus_unit", "error_bar_type", "qualifier", "statistic", "label"):
            with self.subTest(key=key):
                data = example_paper()
                data["experiments"][0]["pitting_potential"][key] = "unused"
                self.assert_invalid(data)
        data = example_paper()
        data["provenance"] = {}
        self.assert_invalid(data)

    def test_amounts_need_measurement_objects_and_categories_are_explicit(self):
        data = example_paper()
        data["experiments"][0]["alloy"]["composition"][0]["amount"] = 18
        self.assert_invalid(data)
        data = example_paper()
        data["experiments"][0]["alloy"]["material_class"] = "unknown"
        self.assert_invalid(data)

    def test_pydantic_checks_bound_order_and_finite_numbers(self):
        # Inequalities between fields are additional Pydantic checks, not JSON Schema rules.
        for value in ({"min": 2, "max": 1}, {"value": 0, "min": 1},
                      {"value": 3, "max": 2}):
            with self.subTest(value=value), self.assertRaises(ValidationError):
                Measurement.model_validate(value)
        for value in (float("nan"), float("inf"), float("-inf")):
            with self.subTest(value=value), self.assertRaises(ValidationError):
                Measurement.model_validate({"value": value})


if __name__ == "__main__":
    unittest.main()
