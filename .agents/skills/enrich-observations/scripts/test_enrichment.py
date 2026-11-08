"""Synthetic model/CLI tests; never enriches real papers or reads CRA data.

PDF fixture bytes intentionally are not renderable. The read-only helpers only
fingerprint PDFs; structural success cannot establish actual visual access.
"""

from copy import deepcopy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from jsonschema import Draft202012Validator
from pydantic import ValidationError

from enrichment_io import (
    InvalidData, SetupError, checked_schema, load_json, parse_json, prepare_inputs,
    validate_enrichment, validate_model,
)
from observation_enrichment import ObservationEnrichment
from observation_registry import ObservationRegistry


SKILL = Path(__file__).resolve().parents[1]
REFERENCES = SKILL / "references"


def dump(path, document):
    path.write_text(json.dumps(document, ensure_ascii=False, allow_nan=False, indent=2) + "\n", encoding="utf-8")


class EnrichmentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="observation-enrichment-")
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.pdf = self.directory / "9002_invented_enrichment.pdf"
        self.pdf.write_bytes(b"%PDF-1.4\n% Bookkeeping fixture only, not visual evidence.\n")
        self.registry = self.directory / "paper_9002_subset.json"
        self.registry_document = load_json(REFERENCES / "example_registry.json")
        dump(self.registry, self.registry_document)
        self.output = self.directory / "enrichment.json"

    def prepared(self):
        return prepare_inputs(self.pdf, self.registry)

    def enrichment(self):
        document = load_json(REFERENCES / "example_enrichment.json")
        prepared = self.prepared()
        document.update(inputs=prepared.inputs.model_dump(mode="json"), paper_name=prepared.paper_name,
                        reference_number=prepared.reference_number)
        return document

    def validate(self, document=None):
        return validate_enrichment(document if document is not None else self.enrichment(), self.prepared())

    def cli(self, script="validate_output.py", folder=SKILL, no_site=False):
        env = os.environ.copy()
        env.pop("PYTHONPATH", None)
        env["PYTHONUTF8"] = "1"
        command = [sys.executable, "-B"]
        if no_site:
            command.append("-S")
        command += [str(folder / "scripts" / script), "--pdf", str(self.pdf), "--registry", str(self.registry)]
        if script == "validate_output.py":
            command += ["--input", str(self.output)]
        return subprocess.run(command, cwd=self.directory, env=env, capture_output=True,
                              text=True, encoding="utf-8", timeout=30)

    def copy_skill(self):
        folder = self.directory / "standalone-skill"
        shutil.copytree(SKILL, folder, ignore=shutil.ignore_patterns("__pycache__"))
        return folder

    def snapshot(self):
        return {p.relative_to(self.directory).as_posix(): p.read_bytes()
                for p in self.directory.rglob("*") if p.is_file()}

    def test_bundled_models_and_schemas_agree(self):
        for model, name in [
            (ObservationRegistry, "observation_registry.schema.json"),
            (ObservationEnrichment, "observation_enrichment.schema.json"),
        ]:
            schema = checked_schema(model, name)
            self.assertEqual(schema, model.model_json_schema())
        validate_model(load_json(REFERENCES / "example_registry.json"), ObservationRegistry, "observation_registry.schema.json")
        validate_model(load_json(REFERENCES / "example_enrichment.json"), ObservationEnrichment, "observation_enrichment.schema.json")
        self.validate()

    def test_schema_and_serialized_field_order_match_bundled_contract(self):
        schema = load_json(REFERENCES / "observation_enrichment.schema.json")
        self.assertEqual(schema, ObservationEnrichment.model_json_schema())
        model = ObservationEnrichment.model_validate(self.enrichment())
        for exclude_unset in (False, True):
            with self.subTest(exclude_unset=exclude_unset):
                serialized = model.model_dump(mode="json", exclude_unset=exclude_unset)
                Draft202012Validator(schema).validate(serialized)
                self.assertEqual(list(serialized), list(schema["properties"]))
                for row in serialized["experiments"]:
                    self.assertEqual(list(row), list(schema["$defs"]["EnrichedExperiment"]["properties"]))

    def test_full_input_routes_complete_partial_and_failed(self):
        prepared = self.prepared()
        result = self.validate()
        self.assertEqual(prepared.eligible_ids, ["obs_003", "obs_009", "obs_012", "obs_018", "obs_030"])
        self.assertEqual(prepared.skipped_failed_ids, ["obs_024"])
        self.assertEqual([r.observation_id for r in result.experiments], prepared.eligible_ids)

    def test_subset_keeps_noncontiguous_ids_and_order(self):
        document = self.enrichment()
        self.registry_document["observations"] = [self.registry_document["observations"][i] for i in (1, 3)]
        dump(self.registry, self.registry_document)
        document["experiments"] = [document["experiments"][i] for i in (1, 3)]
        document["inputs"] = self.prepared().inputs.model_dump(mode="json")
        self.assertEqual([r.observation_id for r in self.validate(document).experiments], ["obs_009", "obs_018"])

    def test_empty_and_failed_only_registries(self):
        for failed_only in (False, True):
            with self.subTest(failed_only=failed_only):
                document = self.enrichment()
                self.registry_document["observations"] = [load_json(REFERENCES / "example_registry.json")["observations"][4]] if failed_only else []
                dump(self.registry, self.registry_document)
                document.update(experiments=[], inputs=self.prepared().inputs.model_dump(mode="json"))
                self.assertEqual(self.validate(document).experiments, [])
                dump(self.output, document)
                response = self.cli()
                self.assertEqual(response.returncode, 0, response.stderr)
                self.assertIn("No eligible observations were supplied", response.stdout)
                if failed_only:
                    self.assertIn("Skipped failed IDs: obs_024", response.stdout)

    def test_all_origin_types_are_eligible(self):
        for origin in ("reported_experimental", "interpolated", "calculated", "cited", "reference_value", "unclear"):
            self.registry_document["observations"][0]["result_type"] = origin
            dump(self.registry, self.registry_document)
            with self.subTest(origin=origin):
                self.assertEqual(self.validate().experiments[0].observation_id, "obs_003")

    def test_resolved_partial_context_is_not_automatically_flagged(self):
        result = self.validate()
        self.assertEqual(self.prepared().registry.observations[3].extraction_status, "partial")
        self.assertEqual(result.experiments[3].failure_notes, "")
        self.assertTrue(result.experiments[2].failure_notes)

    def test_null_anchor_is_retained_with_recovered_context(self):
        row = self.validate().experiments[2]
        self.assertIsNone(row.pitting_potential)
        self.assertEqual(row.test_temperature.value, 25)
        self.assertTrue(row.failure_notes)

    def test_shared_context_and_distinct_possible_duplicate_records(self):
        result = self.validate()
        self.assertEqual(result.experiments[0].alloy, result.experiments[-1].alloy)
        self.assertNotEqual(result.experiments[0].observation_id, result.experiments[-1].observation_id)
        self.assertIn("may repeat obs_003", result.experiments[-1].result_note)
        self.assertEqual(result.experiments[0].pitting_potential.unit, "V (SCE)")
        self.assertEqual(result.experiments[-1].pitting_potential.unit, "mV (SCE)")

    def test_even_identical_readings_do_not_permit_dropping_a_registered_id(self):
        document = self.enrichment()
        source = self.registry_document["observations"][-1]
        source["pitting_potential"] = deepcopy(self.registry_document["observations"][0]["pitting_potential"])
        source["locations"][0]["pitting_potential"] = deepcopy(source["pitting_potential"])
        dump(self.registry, self.registry_document)
        document["inputs"] = self.prepared().inputs.model_dump(mode="json")
        document["experiments"][-1]["pitting_potential"] = deepcopy(source["pitting_potential"])
        self.validate(document)
        document["experiments"].pop()
        with self.assertRaisesRegex(InvalidData, "cover complete/partial input IDs"):
            self.validate(document)

    def test_scientific_qualifications_and_conflicts_do_not_force_failure(self):
        document = self.enrichment()
        row = document["experiments"][0]
        row["result_note"] += " Primary remains 0.31 V despite the secondary 0.33 V reading."
        result = self.validate(document)
        self.assertEqual(result.experiments[0].failure_notes, "")
        self.assertIn("current-criterion", result.experiments[0].result_note)

    def test_partial_access_records_retain_every_eligible_id(self):
        document = self.enrichment()
        for row in document["experiments"]:
            row["alloy"] = {"preparation": "", "composition": [], "microstructure": "", "material_class": ""}
            row["failure_notes"] = "Composition/methods page inaccessible; retain only verified context and locked outcome."
        self.assertEqual(len(self.validate(document).experiments), len(self.prepared().eligible_ids))

    def test_source_missing_fields_use_existing_empty_null_conventions(self):
        document = self.enrichment()
        row = document["experiments"][0]
        row["alloy"]["microstructure"] = ""
        row["test_solution"]["ph"] = None
        row["test_solution"]["chloride_concentration"] = None
        row["alloy"]["composition"].append({"element_symbol": "N", "amount": None})
        self.assertEqual(self.validate(document).experiments[0].failure_notes, "")

    def test_missing_required_fields_and_unexpected_fields(self):
        base = self.enrichment()
        cases = []
        for key in base:
            bad = deepcopy(base); del bad[key]; cases.append(bad)
        for key in base["experiments"][0]:
            bad = deepcopy(base); del bad["experiments"][0][key]; cases.append(bad)
        for target in (lambda d: d, lambda d: d["experiments"][0], lambda d: d["experiments"][0]["alloy"], lambda d: d["inputs"]):
            bad = deepcopy(base); target(bad)["citrine_no"] = 12; cases.append(bad)
        for index, bad in enumerate(cases):
            with self.subTest(case=index), self.assertRaises(InvalidData): self.validate(bad)

    def test_duplicate_unknown_failed_omitted_reordered_and_renumbered_ids(self):
        base = self.enrichment()
        variants = []
        bad = deepcopy(base); bad["experiments"].append(deepcopy(bad["experiments"][0])); variants.append(bad)
        bad = deepcopy(base); bad["experiments"][0]["observation_id"] = "obs_999"; variants.append(bad)
        bad = deepcopy(base); bad["experiments"][0]["observation_id"] = "obs_024"; variants.append(bad)
        bad = deepcopy(base); bad["experiments"].pop(0); variants.append(bad)
        bad = deepcopy(base); bad["experiments"].reverse(); variants.append(bad)
        bad = deepcopy(base); bad["experiments"][0]["observation_id"] = "obs_001"; variants.append(bad)
        for index, bad in enumerate(variants):
            with self.subTest(case=index), self.assertRaises(InvalidData): self.validate(bad)

    def test_anchored_value_unit_bounds_uncertainty_cannot_change(self):
        for key, value in [("value", 0.32), ("min", 0.28), ("max", 0.34), ("unit", "mV (SCE)"), ("plus_minus", 0.02)]:
            document = self.enrichment()
            document["experiments"][0]["pitting_potential"][key] = value
            with self.subTest(key=key), self.assertRaisesRegex(InvalidData, "raw registry observation-level"):
                self.validate(document)

    def test_a_secondary_reading_cannot_replace_the_primary_anchor(self):
        document = self.enrichment()
        document["experiments"][0]["pitting_potential"] = deepcopy(self.registry_document["observations"][0]["locations"][1]["pitting_potential"])
        with self.assertRaisesRegex(InvalidData, "do not substitute a secondary reading"):
            self.validate(document)

    def test_null_anchor_cannot_be_filled_and_nonnull_cannot_be_removed(self):
        for index, value in [(2, {"value": 300, "unit": "mV (SCE)"}), (0, None)]:
            document = self.enrichment(); document["experiments"][index]["pitting_potential"] = value
            with self.subTest(index=index), self.assertRaisesRegex(InvalidData, "raw registry observation-level"):
                self.validate(document)

    def test_optional_field_omissions_and_explicit_null_are_preserved(self):
        base = self.enrichment()
        variants = []
        bad = deepcopy(base); bad["experiments"][1]["pitting_potential"]["max"] = None; variants.append(bad)
        bad = deepcopy(base); del bad["experiments"][1]["pitting_potential"]["value"]; variants.append(bad)
        for index, bad in enumerate(variants):
            with self.subTest(case=index), self.assertRaisesRegex(InvalidData, "optional-field presence"):
                self.validate(bad)
        source = self.registry_document["observations"][-1]
        source["pitting_potential"] = {"value": 310}
        source["locations"][0]["pitting_potential"] = {"value": 310}
        dump(self.registry, self.registry_document)
        good = self.enrichment(); good["experiments"][-1]["pitting_potential"] = {"value": 310}
        self.validate(good)
        good["experiments"][-1]["pitting_potential"]["unit"] = ""
        with self.assertRaisesRegex(InvalidData, "optional-field presence"): self.validate(good)

    def test_model_serialization_defaults_are_detected(self):
        original = self.enrichment()
        model = ObservationEnrichment.model_validate(original)
        with self.assertRaisesRegex(InvalidData, "serialize added defaults"):
            self.validate(model.model_dump(mode="json"))
        self.validate(model.model_dump(mode="json", exclude_unset=True))

    def test_each_input_fingerprint_and_filename_is_checked(self):
        for key in ("pdf", "registry"):
            for field, value in (("sha256", "f" * 64), ("filename", "other.pdf" if key == "pdf" else "other.json")):
                bad = self.enrichment(); bad["inputs"][key][field] = value
                with self.subTest(key=key, field=field), self.assertRaisesRegex(InvalidData, "fingerprints"):
                    self.validate(bad)

    def test_byte_changes_in_inputs_invalidate_old_output(self):
        for path in (self.pdf, self.registry):
            document = self.enrichment(); original = path.read_bytes()
            path.write_bytes(original + b"\n")
            with self.subTest(path=path.name), self.assertRaisesRegex(InvalidData, "fingerprints"):
                self.validate(document)
            path.write_bytes(original)

    def test_output_paper_reference_and_version_must_match(self):
        for key, value in (("paper_name", "different.pdf"), ("reference_number", 9003), ("schema_version", "2.0")):
            bad = self.enrichment(); bad[key] = value
            with self.subTest(key=key), self.assertRaises(InvalidData): self.validate(bad)

    def test_unsupported_registry_versions_are_not_upgraded(self):
        for version in ("1.0", "2.0"):
            self.registry_document["schema_version"] = version
            dump(self.registry, self.registry_document)
            with self.subTest(version=version), self.assertRaisesRegex(InvalidData, "unsupported registry version.*expected '1.1'.*No automatic upgrade"):
                self.prepared()

    def test_reference_conflicts_and_numbered_filenames(self):
        for kind in ("metadata", "pdf", "registry", "paper_name"):
            bad = deepcopy(self.registry_document)
            pdf, registry = self.pdf, self.registry
            if kind == "metadata": bad["reference_number"] = 9003
            elif kind == "paper_name": bad["paper_name"] = "9003_different.pdf"
            elif kind == "pdf":
                pdf = self.directory / "9003_wrong.pdf"; pdf.write_bytes(self.pdf.read_bytes())
            else: registry = self.directory / "paper_9003_subset.json"
            dump(registry, bad)
            with self.subTest(kind=kind), self.assertRaisesRegex(InvalidData, "Reference conflict"):
                prepare_inputs(pdf, registry)
            dump(self.registry, self.registry_document)

    def test_unknown_reference_is_allowed(self):
        self.pdf = self.directory / "unnumbered.pdf"
        self.pdf.write_bytes(b"%PDF fixture\n")
        self.registry = self.directory / "registry_subset.json"
        self.registry_document.update(reference_number=None, paper_name=self.pdf.name)
        dump(self.registry, self.registry_document)
        self.assertIsNone(self.prepared().reference_number)
        self.assertIsNone(self.validate().reference_number)

    def test_null_reference_can_resolve_from_numbered_files(self):
        self.registry_document["reference_number"] = None
        dump(self.registry, self.registry_document)
        self.assertEqual(self.prepared().reference_number, 9002)

    def test_renamed_pdf_produces_a_warning(self):
        renamed = self.directory / "9002_renamed.pdf"; renamed.write_bytes(self.pdf.read_bytes())
        prepared = prepare_inputs(renamed, self.registry)
        self.assertEqual(prepared.reference_number, 9002)
        self.assertTrue(prepared.warnings)

    def test_zero_reference_filename_and_wrong_extensions_are_rejected(self):
        wrong = self.directory / "0_bad.pdf"; wrong.write_bytes(self.pdf.read_bytes())
        with self.assertRaisesRegex(InvalidData, "reference must be positive"):
            prepare_inputs(wrong, self.registry)
        with self.assertRaisesRegex(InvalidData, "Expected a .pdf"):
            prepare_inputs(self.directory / "paper.txt", self.registry)

    def test_duplicate_json_keys_nonfinite_overflow_and_encoding_are_rejected(self):
        for payload in (b'{"a":1,"a":2}', b'{"x":{"a":1,"a":2}}', b'{"n":NaN}', b'{"n":Infinity}', b'{"n":-Infinity}', b'{"n":1e9999}', b'\x96', b'{broken'):
            with self.subTest(payload=payload), self.assertRaises(InvalidData): parse_json(payload, "test")

    def test_bom_registry_and_output_are_accepted(self):
        self.registry.write_bytes(b"\xef\xbb\xbf" + self.registry.read_bytes())
        document = self.enrichment()
        dump(self.output, document)
        self.output.write_bytes(b"\xef\xbb\xbf" + self.output.read_bytes())
        self.assertEqual(self.cli().returncode, 0)

    def test_registry_regressions_for_ids_locations_primary_and_status(self):
        base = deepcopy(self.registry_document)
        for case in ("duplicate_id", "page", "kind", "primary_index", "primary_value", "complete_null", "partial_notes", "unknown_field", "missing_status", "missing_origin"):
            bad = deepcopy(base); source = bad["observations"][0]
            if case == "duplicate_id": bad["observations"][1]["observation_id"] = source["observation_id"]
            elif case == "page": source["locations"][0]["pdf_page"] = 0
            elif case == "kind": source["locations"][0]["kind"] = "text"
            elif case == "primary_index": source["primary_location"] = 999
            elif case == "primary_value": source["pitting_potential"] = {"value": 7}
            elif case == "complete_null": source["pitting_potential"] = source["locations"][0]["pitting_potential"] = None
            elif case == "partial_notes": bad["observations"][2]["failure_notes"] = ""
            elif case == "unknown_field": source["citrine_no"] = 1
            elif case == "missing_status": del source["extraction_status"]
            else: del source["result_type"]
            dump(self.registry, bad)
            with self.subTest(case=case), self.assertRaises(InvalidData): self.prepared()

    def test_measurement_regressions_in_context(self):
        for value in ({}, {"unit": "°C"}, {"min": 10, "max": 5}, {"value": 7, "min": 8}, {"value": 7, "max": 6}, {"min": 2, "plus_minus": 1}, {"value": 2, "plus_minus": -1}, {"value": "25"}, {"value": True}):
            bad = self.enrichment(); bad["experiments"][0]["test_temperature"] = value
            with self.subTest(value=value), self.assertRaises(InvalidData): self.validate(bad)

    def test_context_types_categories_and_nonnullable_strings(self):
        base = self.enrichment()
        variants = []
        bad = deepcopy(base); bad["experiments"][0]["failure_notes"] = None; variants.append(bad)
        bad = deepcopy(base); bad["experiments"][0]["alloy"]["preparation"] = None; variants.append(bad)
        bad = deepcopy(base); bad["experiments"][0]["alloy"]["material_class"] = "Steel"; variants.append(bad)
        bad = deepcopy(base); bad["experiments"][0]["alloy"]["composition"][0]["amount"] = 18; variants.append(bad)
        bad = deepcopy(base); bad["experiments"][0]["test_method"]["scan_rate"] = "steady state"; variants.append(bad)
        bad = deepcopy(base); bad["experiments"][0]["experiment_id"] = "experiment-1"; variants.append(bad)
        for index, bad in enumerate(variants):
            with self.subTest(case=index), self.assertRaises(InvalidData): self.validate(bad)
        good = self.enrichment(); good["experiments"][0]["test_solution"]["ph"] = -0.5
        self.validate(good)

    def test_original_units_stepped_procedure_and_no_derived_chloride(self):
        result = self.validate()
        first, bound = result.experiments[:2]
        self.assertEqual(first.test_temperature.unit, "K")
        self.assertIsNone(first.test_solution.chloride_concentration)
        self.assertIsNone(first.test_method.scan_rate)
        self.assertEqual(bound.test_solution.composition, [])
        self.assertIsNone(bound.test_method.scan_rate)
        self.assertEqual(bound.test_method.potential_step.value, 20)
        self.assertEqual(bound.test_method.step_hold_duration.value, 60)
        self.assertIsNone(bound.pitting_potential.value)

    def test_prepare_cli_is_read_only_and_preserves_raw_registry(self):
        before = self.snapshot()
        response = self.cli("prepare_inputs.py")
        self.assertEqual(response.returncode, 0, response.stderr)
        prepared = json.loads(response.stdout)
        self.assertEqual(prepared["registry"], self.registry_document)
        self.assertEqual(prepared["eligible_observation_ids"], self.prepared().eligible_ids)
        self.assertEqual(prepared["skipped_failed_observation_ids"], ["obs_024"])
        self.assertEqual(before, self.snapshot())

    def test_validator_cli_counts_flags_and_skips_without_writing(self):
        dump(self.output, self.enrichment())
        before = self.snapshot()
        response = self.cli()
        self.assertEqual(response.returncode, 0, response.stderr)
        self.assertIn("Supplied=6; eligible=5; written=5; skipped_failed=1; flagged=1", response.stdout)
        self.assertIn("Skipped failed IDs: obs_024", response.stdout)
        self.assertIn("Flagged output IDs: obs_012", response.stdout)
        self.assertEqual(before, self.snapshot())

    def test_invalid_data_exit_one_without_success_output(self):
        for kind in ("version", "potential", "json"):
            document = self.enrichment()
            if kind == "version": document["schema_version"] = "2.0"
            elif kind == "potential": document["experiments"][0]["pitting_potential"]["value"] = 0.32
            dump(self.output, document)
            if kind == "json": self.output.write_text('{"a":1,"a":2}', encoding="utf-8")
            response = self.cli()
            with self.subTest(kind=kind):
                self.assertEqual(response.returncode, 1)
                self.assertNotIn("VALID:", response.stdout)
        self.assertFalse((self.directory / "enrichment_report.md").exists())

    def test_missing_files_are_setup_io_failures(self):
        self.assertEqual(self.cli().returncode, 2)
        self.registry.unlink()
        response = self.cli("prepare_inputs.py")
        self.assertEqual(response.returncode, 2)
        self.assertIn("Cannot read", response.stderr)

    def test_invalid_registry_cli_has_clear_version_diagnostic(self):
        self.registry_document["schema_version"] = "1.0"
        dump(self.registry, self.registry_document)
        response = self.cli("prepare_inputs.py")
        self.assertEqual(response.returncode, 1)
        self.assertIn("unsupported registry version '1.0'", response.stderr)

    def test_standalone_clis_work_outside_project_and_write_no_caches(self):
        folder = self.copy_skill()
        dump(self.output, self.enrichment())
        before = self.snapshot()
        for script in ("prepare_inputs.py", "validate_output.py"):
            with self.subTest(script=script):
                response = self.cli(script, folder=folder)
                self.assertEqual(response.returncode, 0, response.stderr)
        self.assertEqual(before, self.snapshot())
        self.assertFalse(list(folder.rglob("__pycache__")))

    def test_missing_dependencies_and_corrupt_resources_are_setup_failures(self):
        dump(self.output, self.enrichment())
        response = self.cli(no_site=True)
        self.assertEqual(response.returncode, 2)
        self.assertIn("Setup failure", response.stderr)
        folder = self.copy_skill()
        for name in ("observation_registry.schema.json", "observation_enrichment.schema.json"):
            resource = folder / "references" / name
            original = resource.read_bytes()
            resource.write_text('{}', encoding="utf-8")
            response = self.cli(folder=folder)
            with self.subTest(resource=name):
                self.assertEqual(response.returncode, 2)
                self.assertIn("differs from its Pydantic model", response.stderr)
            resource.write_bytes(original)


if __name__ == "__main__":
    unittest.main()
