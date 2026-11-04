"""Contract and standalone CLI tests using invented observation records."""

from copy import deepcopy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from jsonschema import Draft202012Validator
from pydantic import ValidationError

from observation_registry import Measurement, ObservationRegistry
import validate_output as validator


SKILL_DIR = Path(__file__).resolve().parents[1]
EXAMPLE_PATH = SKILL_DIR / "references" / "example_registry.json"


def example_registry():
    return validator.load_json(EXAMPLE_PATH)


def single_location_registry(kind="table"):
    data = example_registry()
    if kind == "text":
        observation = data["observations"][1]
    else:
        observation = data["observations"][0]
        location = next(item for item in observation["locations"] if item["kind"] == kind)
        observation["locations"] = [location]
        observation["pitting_potential"] = deepcopy(location["pitting_potential"])
    observation["primary_location"] = 0
    data["observations"] = [observation]
    return data


def set_potential(data, value):
    observation = data["observations"][0]
    observation["pitting_potential"] = deepcopy(value)
    observation["locations"][observation["primary_location"]]["pitting_potential"] = deepcopy(value)


class RegistryContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = validator.load_json(validator.SCHEMA_PATH)
        cls.schema_validator = Draft202012Validator(cls.schema)

    def assert_valid(self, data):
        original = deepcopy(data)
        self.schema_validator.validate(data)
        self.assertEqual(validator.validate_document(data), [])
        model = ObservationRegistry.model_validate(data)
        decoded = json.loads(model.model_dump_json(exclude_unset=True))
        self.schema_validator.validate(decoded)
        self.assertEqual(decoded, original)
        self.assertEqual(data, original)
        return model

    def assert_invalid(self, data):
        self.assertTrue(validator.validate_document(data))
        with self.assertRaises(ValidationError):
            ObservationRegistry.model_validate(data)

    def assert_schema_and_model_invalid(self, data):
        self.assertFalse(self.schema_validator.is_valid(data))
        self.assert_invalid(data)

    def test_schema_is_valid_and_matches_bundled_models(self):
        Draft202012Validator.check_schema(self.schema)
        self.assertEqual(self.schema, ObservationRegistry.model_json_schema())
        self.assertEqual(set(self.schema["$defs"]["Measurement"]["properties"]),
                         {"value", "min", "max", "unit", "plus_minus"})

    def test_example_consolidates_locations_and_preserves_different_units(self):
        model = self.assert_valid(example_registry())
        observation = model.observations[0]
        self.assertEqual(len(observation.locations), 2)
        self.assertEqual(observation.pitting_potential.value, 300)
        self.assertEqual(observation.locations[1].pitting_potential.value, 0.30)
        self.assertEqual(observation.locations[1].pitting_potential.unit, "V (SCE)")

    def test_each_location_variant_can_be_the_primary(self):
        for kind in ("table", "plot", "text"):
            with self.subTest(kind=kind):
                model = self.assert_valid(single_location_registry(kind))
                self.assertEqual(model.observations[0].locations[0].kind, kind)

    def test_primary_can_point_to_a_later_location(self):
        data = example_registry()
        observation = data["observations"][0]
        observation["primary_location"] = 1
        observation["pitting_potential"] = deepcopy(observation["locations"][1]["pitting_potential"])
        self.assert_valid(data)

    def test_empty_registry_is_valid(self):
        data = example_registry()
        data["observations"] = []
        self.assert_valid(data)

    def test_partial_null_and_condition_specific_no_pitting_bound(self):
        data = single_location_registry("text")
        self.assert_valid(data)
        observation = data["observations"][0]
        set_potential(data, {"min": 800, "unit": "mV (SCE)"})
        observation["extraction_status"] = "complete"
        observation["failure_notes"] = ""
        observation["result_note"] = "Reported Epit > 800 mV (SCE); no pitting within this condition's tested range."
        self.assert_valid(data)

    def test_all_result_types_are_representable_without_status_gating(self):
        for result_type in ("reported_experimental", "interpolated", "calculated", "cited", "reference_value", "unclear"):
            with self.subTest(result_type=result_type):
                data = single_location_registry()
                data["observations"][0]["result_type"] = result_type
                self.assert_valid(data)

    def test_classifications_are_required_and_have_no_fallback(self):
        for field in ("result_type", "extraction_status"):
            data = single_location_registry()
            del data["observations"][0][field]
            self.assert_schema_and_model_invalid(data)
            for value in (None, "", "unknown", True):
                with self.subTest(field=field, value=value):
                    data = single_location_registry()
                    data["observations"][0][field] = value
                    self.assert_schema_and_model_invalid(data)

    def test_complete_requires_a_potential_and_exactly_empty_failure_notes(self):
        for note in ("A provided label was unreadable.", " ", "\n"):
            with self.subTest(note=note):
                data = single_location_registry()
                data["observations"][0]["failure_notes"] = note
                self.assert_schema_and_model_invalid(data)
        data = single_location_registry()
        set_potential(data, None)
        self.assert_schema_and_model_invalid(data)

    def test_partial_and_failed_require_nonblank_failure_notes(self):
        for status in ("partial", "failed"):
            for note in ("", " \t\n"):
                with self.subTest(status=status, note=note):
                    data = single_location_registry()
                    data["observations"][0]["extraction_status"] = status
                    data["observations"][0]["failure_notes"] = note
                    self.assert_schema_and_model_invalid(data)

    def test_partial_and_failed_retain_recovered_values_and_locations(self):
        for status in ("partial", "failed"):
            for potential in (None, {"value": 300, "unit": "mV (SCE)"}):
                with self.subTest(status=status, potential=potential):
                    data = single_location_registry()
                    observation = data["observations"][0]
                    observation["extraction_status"] = status
                    observation["failure_notes"] = "The provided condition labels could not be recovered."
                    set_potential(data, potential)
                    model = self.assert_valid(data)
                    self.assertEqual(len(model.observations[0].locations), 1)

    def test_source_qualifications_do_not_lower_complete_status(self):
        notes = (
            "The criterion for this marker is either a definite pitting potential or the paper's fallback current criterion; it is unspecified.",
            "The paper does not establish whether another plot repeats this measurement.",
            "The paper does not give an alloy identifier for this marker.",
        )
        for note in notes:
            with self.subTest(note=note):
                data = single_location_registry()
                observation = data["observations"][0]
                observation["result_note"] = note
                observation["sample_label"] = ""
                self.assert_valid(data)
        data = example_registry()
        observation = data["observations"][0]
        observation["locations"][1]["pitting_potential"] = {"value": 0.20, "unit": "V (SCE)"}
        observation["result_note"] = "The table and plot give conflicting values; the table is selected without correcting either reading."
        self.assert_valid(data)

    def test_version_one_is_rejected_without_inferring_classifications(self):
        data = example_registry()
        data["schema_version"] = "1.0"
        for observation in data["observations"]:
            del observation["result_type"]
            del observation["extraction_status"]
        original = deepcopy(data)
        self.assert_schema_and_model_invalid(data)
        errors = validator.validate_document(data)
        self.assertEqual(len(errors), 1)
        self.assertIn("/schema_version", errors[0])
        self.assertIn("'1.0'", errors[0])
        self.assertIn("'1.1'", errors[0])
        self.assertEqual(data, original)

    def test_measurement_forms_preserve_bounds_and_uncertainty(self):
        for value in ({"value": 0}, {"min": 300}, {"max": 350},
                      {"min": 300, "max": 350, "unit": "mV (SCE)"},
                      {"value": 325, "min": 300, "max": 350},
                      {"value": 300, "plus_minus": 0},
                      {"value": None, "min": 300, "max": None, "plus_minus": None}):
            with self.subTest(value=value):
                data = single_location_registry()
                set_potential(data, value)
                self.assert_valid(data)

    def test_named_values_allow_only_text_measurements_or_null(self):
        data = single_location_registry()
        conditions = data["observations"][0]["locations"][0]["conditions"]
        conditions.extend([{"name": "Method", "value": "Scratch"},
                           {"name": "pH", "value": {"value": 7}},
                           {"name": "Unreadable coordinate", "value": None}])
        self.assert_valid(data)
        for value in (0.5, True, [], {}):
            with self.subTest(value=value):
                conditions[0]["value"] = value
                self.assert_invalid(data)

    def test_missing_or_nullable_required_text_is_rejected(self):
        for field in ("sample_label", "association_notes", "result_note", "failure_notes"):
            for missing in (True, False):
                with self.subTest(field=field, missing=missing):
                    data = single_location_registry()
                    if missing:
                        del data["observations"][0][field]
                    else:
                        data["observations"][0][field] = None
                    self.assert_invalid(data)

    def test_location_specific_fields_are_required(self):
        fields = {"table": ("table_label", "row_label", "column_label", "conditions"),
                  "plot": ("figure_label", "panel_label", "series_label", "coordinates"),
                  "text": ("section_heading", "text_anchor")}
        for kind, names in fields.items():
            for name in names:
                with self.subTest(kind=kind, name=name):
                    data = single_location_registry(kind)
                    del data["observations"][0]["locations"][0][name]
                    self.assert_invalid(data)

    def test_unknown_kind_and_cross_variant_fields_are_rejected(self):
        data = single_location_registry()
        data["observations"][0]["locations"][0]["kind"] = "figure"
        self.assert_invalid(data)
        data = single_location_registry()
        data["observations"][0]["locations"][0]["figure_label"] = "Fig. 1"
        self.assert_invalid(data)

    def test_page_numbers_and_reference_are_strict_positive_integers(self):
        for value in (0, -1, True, "1", 1.5):
            with self.subTest(value=value):
                data = single_location_registry()
                data["observations"][0]["locations"][0]["pdf_page"] = value
                self.assert_invalid(data)
                data = single_location_registry()
                data["reference_number"] = value
                self.assert_invalid(data)

    def test_empty_locations_and_invalid_primary_indices_are_rejected(self):
        data = single_location_registry()
        data["observations"][0]["locations"] = []
        self.assert_invalid(data)
        for value in (-1, 1, True, "0", 0.5):
            with self.subTest(value=value):
                data = single_location_registry()
                data["observations"][0]["primary_location"] = value
                self.assert_invalid(data)

    def test_primary_mismatch_does_not_accept_conversion_or_averaging(self):
        for potential in ({"value": 0.3, "unit": "V (SCE)"},
                          {"value": 301, "unit": "mV (SCE)"},
                          {"value": 300, "unit": "mV (SCE)", "plus_minus": 10}, None):
            with self.subTest(potential=potential):
                data = single_location_registry()
                data["observations"][0]["pitting_potential"] = potential
                self.assert_invalid(data)

    def test_duplicate_ids_are_rejected_and_gaps_are_allowed(self):
        data = example_registry()
        data["observations"][1]["observation_id"] = data["observations"][0]["observation_id"]
        self.assert_invalid(data)
        data["observations"][1]["observation_id"] = "obs_017"
        self.assert_valid(data)

    def test_unknown_fields_including_database_identifiers_are_rejected(self):
        for level, key in (("root", "citrine_rows"), ("observation", "citrine_no"),
                           ("location", "source_id"), ("measurement", "error_bar_type")):
            with self.subTest(level=level):
                data = single_location_registry()
                containers = {"root": data, "observation": data["observations"][0],
                              "location": data["observations"][0]["locations"][0],
                              "measurement": data["observations"][0]["pitting_potential"]}
                containers[level][key] = "unexpected"
                self.assert_invalid(data)

    def test_invalid_measurements_and_nonfinite_numbers_are_rejected(self):
        values = ({}, {"unit": "mV"}, {"value": None}, {"plus_minus": 1},
                  {"min": 300, "plus_minus": 10}, {"value": 300, "plus_minus": -1},
                  {"value": "300"}, {"value": True}, {"value": 300, "unit": None},
                  {"min": 350, "max": 300}, {"value": 200, "min": 300},
                  {"value": 400, "max": 350}, {"value": float("nan")},
                  {"value": float("inf")}, {"value": float("-inf")})
        for value in values:
            with self.subTest(value=value):
                data = single_location_registry()
                set_potential(data, value)
                self.assert_invalid(data)
                with self.assertRaises(ValidationError):
                    Measurement.model_validate(value)


class StandaloneCliTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.skill = self.root / "register-observations"
        shutil.copytree(SKILL_DIR, self.skill, ignore=shutil.ignore_patterns("__pycache__"))
        self.script = self.skill / "scripts" / "validate_output.py"
        self.input = self.root / "registry.json"

    def run_validator(self, data=None, raw=None):
        content = raw if raw is not None else json.dumps(data, ensure_ascii=False, allow_nan=False)
        self.input.write_text(content, encoding="utf-8")
        before = self.input.read_bytes()
        # Ignore PYTHONPATH; use normal sibling imports from the copied skill.
        result = subprocess.run(
            [sys.executable, "-E", str(self.script), "--input", str(self.input)],
            cwd=self.root, capture_output=True, text=True, check=False,
        )
        self.assertEqual(self.input.read_bytes(), before)
        return result

    def test_standalone_valid_registry_reports_statuses_and_routing_ids(self):
        result = self.run_validator(example_registry())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("4 observations", result.stdout)
        self.assertIn("complete=2; partial=1; failed=1", result.stdout)
        self.assertIn("Partial observation IDs: obs_002", result.stdout)
        self.assertIn("Failed observation IDs: obs_004", result.stdout)

    def test_all_failed_records_are_still_structurally_valid(self):
        data = example_registry()
        data["observations"] = [data["observations"][3]]
        result = self.run_validator(data)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("complete=0; partial=0; failed=1", result.stdout)
        self.assertIn("Failed observation IDs: obs_004", result.stdout)

    def test_empty_registry_has_zero_counts_and_no_routing_ids(self):
        data = example_registry()
        data["observations"] = []
        result = self.run_validator(data)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("complete=0; partial=0; failed=0", result.stdout)
        self.assertIn("Partial observation IDs: none", result.stdout)
        self.assertIn("Failed observation IDs: none", result.stdout)

    def test_version_one_has_clear_diagnostic_and_exit_one(self):
        data = example_registry()
        data["schema_version"] = "1.0"
        for observation in data["observations"]:
            del observation["result_type"]
            del observation["extraction_status"]
        result = self.run_validator(data)
        self.assertEqual(result.returncode, 1)
        self.assertIn("unsupported registry version '1.0'", result.stderr)
        self.assertIn("expected '1.1'", result.stderr)
        self.assertIn("no automatic upgrade", result.stderr)

    def test_invalid_primary_has_field_diagnostic_and_exit_one(self):
        data = single_location_registry()
        data["observations"][0]["primary_location"] = 2
        result = self.run_validator(data)
        self.assertEqual(result.returncode, 1)
        self.assertIn("/observations/0", result.stderr)
        self.assertIn("primary_location", result.stderr)

    def test_duplicate_keys_and_non_json_constants_are_rejected(self):
        for raw in ('{"observations": [], "observations": []}', '{"value": NaN}',
                    '{"value": Infinity}', '{"value": -Infinity}'):
            with self.subTest(raw=raw):
                result = self.run_validator(raw=raw)
                self.assertEqual(result.returncode, 1)
                self.assertIn("Invalid JSON", result.stderr)

    def test_overflowing_json_number_is_rejected(self):
        raw = json.dumps(single_location_registry()).replace('"value": 300', '"value": 1e309')
        result = self.run_validator(raw=raw)
        self.assertEqual(result.returncode, 1)
        self.assertIn("finite", result.stderr)

    def test_missing_schema_is_a_setup_failure(self):
        (self.skill / "references" / "observation_registry.schema.json").unlink()
        result = self.run_validator(example_registry())
        self.assertEqual(result.returncode, 2)
        self.assertIn("bundled schema", result.stderr)

    def test_schema_model_drift_is_a_setup_failure(self):
        (self.skill / "references" / "observation_registry.schema.json").write_text("{}", encoding="utf-8")
        result = self.run_validator(example_registry())
        self.assertEqual(result.returncode, 2)
        self.assertIn("differs", result.stderr)


if __name__ == "__main__":
    unittest.main()
