"""Focused structural/CLI tests; no real papers, model calls or databases.

PDF fixture bytes intentionally are not renderable: helpers fingerprint PDFs but
never claim to inspect scientific content. Example assignments are invented.
"""

from copy import deepcopy
import csv
import io
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

from alignment import ObservationAlignment
from alignment_report import measurement, render_report
from matching_io import (
    InvalidData, SetupError, load_json, parse_json, prepare_inputs, shared_rows,
    validate_alignment, validate_model,
)
from observation_registry import Measurement, ObservationRegistry


SKILL = Path(__file__).resolve().parents[1]
REFS = SKILL / "references"


def dump(path, document):
    path.write_text(json.dumps(document, ensure_ascii=False, allow_nan=False, indent=2) + "\n", encoding="utf-8")


class MatchingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="cra-matching-")
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.pdf = self.directory / "9001_invented_corrosion_study.pdf"
        self.pdf.write_bytes(b"%PDF-1.4\n% Bookkeeping-only invented fixture; not visual evidence.\n")
        self.csv = self.directory / "pitting_potential_9001.csv"
        self.csv.write_bytes((REFS / "example_cra.csv").read_bytes())
        self.registry = self.directory / "paper_9001_batch.json"
        self.registry_document = load_json(REFS / "example_registry.json")
        dump(self.registry, self.registry_document)
        self.output = self.directory / "alignment.json"

    def prepared(self):
        return prepare_inputs(self.pdf, self.csv, self.registry)

    def alignment(self):
        result = load_json(REFS / "example_alignment.json")
        result["inputs"] = self.prepared().inputs.model_dump(mode="json")
        return result

    def validate(self, result=None):
        return validate_alignment(result if result is not None else self.alignment(), self.prepared())

    def write_csv(self, rows, headers=None):
        stream = io.StringIO(newline="")
        if headers is None:
            headers = list(rows[0])
        writer = csv.DictWriter(stream, headers, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        self.csv.write_text(stream.getvalue(), encoding="utf-8", newline="")

    def rows(self):
        return [deepcopy(row["fields"]) for row in self.prepared().rows]

    def cli(self, script="validate_output.py", extra=(), folder=SKILL, no_site=False):
        env = os.environ.copy()
        env.pop("PYTHONPATH", None)
        env["PYTHONUTF8"] = "1"
        command = [sys.executable, "-B"]
        if no_site:
            command.append("-S")
        command += [str(folder / "scripts" / script), "--pdf", str(self.pdf), "--csv", str(self.csv), "--registry", str(self.registry)]
        if script == "validate_output.py":
            command += ["--input", str(self.output)]
        command += list(extra)
        return subprocess.run(command, cwd=self.directory, env=env, capture_output=True, text=True, encoding="utf-8", timeout=30)

    def copy_skill(self):
        destination = self.directory / "standalone-skill"
        shutil.copytree(SKILL, destination, ignore=shutil.ignore_patterns("__pycache__"))
        return destination

    def test_example_and_bundled_schema_model_agreement(self):
        for model, name in [(ObservationRegistry, "observation_registry.schema.json"), (ObservationAlignment, "observation_alignment.schema.json")]:
            schema = load_json(REFS / name)
            Draft202012Validator.check_schema(schema)
            self.assertEqual(schema, model.model_json_schema())
        validate_model(load_json(REFS / "example_registry.json"), ObservationRegistry, "observation_registry.schema.json")
        validate_model(load_json(REFS / "example_alignment.json"), ObservationAlignment, "observation_alignment.schema.json")
        self.validate()

    def test_complete_input_statuses_and_candidate_only_complement(self):
        result = self.validate()
        self.assertEqual([o.status for o in result.observations], ["matched", "matched", "ambiguous", "matched", "unmatched", "not_assessed"])
        self.assertEqual(result.unlinked_citrine_nos, [91003, 91004])
        self.assertEqual(shared_rows(result), {91001: ["obs_007", "obs_008"]})

    def test_partial_registry_with_nonsequential_ids(self):
        result = self.alignment()
        chosen = [self.registry_document["observations"][i] for i in (2, 4)]
        self.registry_document["observations"] = chosen
        dump(self.registry, self.registry_document)
        result["observations"] = [result["observations"][i] for i in (2, 4)]
        result["unlinked_citrine_nos"] = [r["citrine_no"] for r in self.prepared().rows]
        result["inputs"] = self.prepared().inputs.model_dump(mode="json")
        self.assertEqual([o.observation_id for o in self.validate(result).observations], ["obs_011", "obs_023"])

    def test_empty_registry_retains_all_unlinked_rows(self):
        result = self.alignment()
        self.registry_document["observations"] = []
        dump(self.registry, self.registry_document)
        result.update(observations=[], inspected_pdf_pages=[], unlinked_citrine_nos=[91001, 91002, 91003, 91004])
        result["inputs"] = self.prepared().inputs.model_dump(mode="json")
        validated = self.validate(result)
        self.assertEqual(validated.observations, [])
        self.assertIn("No observations were supplied", render_report(validated, self.prepared()))

    def test_empty_csv_with_reference_from_registry(self):
        headers = list(self.rows()[0])
        self.write_csv([], headers)
        result = self.alignment()
        for item in result["observations"]:
            item.update(status="not_assessed" if item["observation_id"] == "obs_030" else "unmatched", matches=[], candidates=[], notes="No CRA rows supplied; failed recovery remains unassessed where applicable.")
        result["unlinked_citrine_nos"] = []
        self.validate(result)

    def test_partial_null_reading_can_have_context_supported_identity(self):
        result = self.alignment()
        item = result["observations"][2]
        item["status"] = "matched"
        item["matches"] = [item["candidates"][0]]
        item["candidates"] = []
        self.assertEqual(self.validate(result).observations[2].matches[0].potential_agreement, "not_comparable")

    def test_scientific_qualification_and_discrepancy_do_not_block_identity(self):
        result = self.validate()
        self.assertEqual(result.observations[1].status, "matched")
        self.assertEqual(result.observations[1].matches[0].potential_agreement, "discrepant")
        self.assertTrue(result.shared_qualifications)
        self.assertEqual(self.prepared().registry.observations[1].extraction_status, "complete")

    def test_all_result_origins_can_be_aligned_without_filtering(self):
        for origin in ("reported_experimental", "interpolated", "calculated", "cited", "reference_value", "unclear"):
            self.registry_document["observations"][0]["result_type"] = origin
            dump(self.registry, self.registry_document)
            with self.subTest(origin=origin):
                self.assertEqual(self.validate().observations[0].status, "matched")

    def test_report_does_not_round_registered_values_to_six_significant_digits(self):
        value = Measurement(value=0.123456789012345, min=0.123456789012344, max=0.123456789012346,
                            plus_minus=0.000000000000001, unit="V (SCE)")
        text = measurement(value)
        for number in (value.value, value.min, value.max, value.plus_minus):
            self.assertIn(str(number), text)

    def test_many_to_many_and_matched_with_additional_candidate(self):
        result = self.alignment()
        item = result["observations"][0]
        # Structurally supported multiple identities, not a claim about real science.
        item["matches"].append(deepcopy(result["observations"][3]["matches"][0]))
        candidate = deepcopy(result["observations"][2]["candidates"][1])
        item["candidates"].append(candidate)
        self.assertEqual(len(self.validate(result).observations[0].matches), 2)

    def test_individual_readings_link_to_range_summary(self):
        result = self.alignment()
        row = next(r for r in self.prepared().rows if r["citrine_no"] == 91004)
        for i, endpoint in ((0, "min"), (1, "max")):
            link = result["observations"][i]["matches"][0]
            link.update(citrine_no=91004, cra_potential=row["cra_potential"], potential_agreement="not_comparable", notes="Individual run is a member of this reported range; it is not the mean.")
            column = "Min Epit mV (SCE)" if endpoint == "min" else "Max Epit mV (SCE)"
            link["evidence"] = [dict(field=column, paper_value=row["fields"][column] + " mV (SCE)", cra_value=row["fields"][column], comparison="Range endpoint member; no central value is inferred.")]
        result["unlinked_citrine_nos"] = [91001, 91003]
        self.assertEqual(shared_rows(self.validate(result)), {91004: ["obs_007", "obs_008"]})

    def test_original_units_bounds_uncertainty_and_conversion_evidence(self):
        before = self.registry.read_bytes()
        result = self.validate()
        source = self.prepared().registry.observations[0].pitting_potential
        self.assertEqual((source.value, source.plus_minus, source.unit), (0.3, 0.01, "V (SCE)"))
        self.assertEqual(result.observations[0].matches[0].cra_potential.avg, "300")
        self.assertIn("0.005 × 100 = 0.5 wt%", result.observations[0].matches[0].evidence[1].comparison)
        bound = self.prepared().registry.observations[3].pitting_potential
        self.assertEqual((bound.min, bound.value, bound.unit), (0.8, None, "V (SCE)"))
        self.assertEqual(result.observations[3].matches[0].cra_potential.avg, ">800")
        self.assertEqual(self.registry.read_bytes(), before)

    def test_secondary_location_can_support_a_link(self):
        result = self.alignment()
        result["observations"][0]["matches"][0]["location_indices"] = [1]
        self.validate(result)
        self.assertEqual(self.prepared().registry.observations[0].primary_location, 0)

    def test_transpassive_missing_and_scan_text_are_preserved(self):
        prepared = self.prepared()
        row = prepared.rows[2]
        self.assertEqual(row["cra_potential"], {"avg": "Transpassive", "min": "NA", "max": "NA"})
        self.assertEqual(row["fields"]["Scan Rate mV/s"], "20mV steps by manual increament")
        self.assertEqual(prepared.rows[1]["fields"]["Scan Rate mV/s"], "steady state")
        candidate = self.validate().observations[2].candidates[1]
        self.assertEqual(candidate.potential_agreement, "not_comparable")

    def test_missing_required_fields_bad_enums_and_unexpected_fields(self):
        base = self.alignment()
        variants = []
        for key in base:
            bad = deepcopy(base); del bad[key]; variants.append(bad)
        for value in ("success", "", None):
            bad = deepcopy(base); bad["observations"][0]["status"] = value; variants.append(bad)
        bad = deepcopy(base); bad["observations"][0]["matches"][0]["potential_agreement"] = "close"; variants.append(bad)
        for where in (lambda d: d, lambda d: d["observations"][0], lambda d: d["observations"][0]["matches"][0], lambda d: d["observations"][0]["matches"][0]["evidence"][0]):
            bad = deepcopy(base); where(bad)["unexpected"] = "x"; variants.append(bad)
        for i, bad in enumerate(variants):
            with self.subTest(case=i), self.assertRaises(InvalidData):
                self.validate(bad)

    def test_status_consistency_in_both_schema_and_model(self):
        base = self.alignment()
        for status, matches, candidates, notes in [
            ("matched", [], [], ""),
            ("ambiguous", [], [], "why"),
            ("ambiguous", base["observations"][0]["matches"], [], "why"),
            ("unmatched", [], base["observations"][2]["candidates"], "why"),
            ("not_assessed", [], [], "  "),
        ]:
            with self.subTest(status=status, matches=bool(matches), candidates=bool(candidates)):
                bad = deepcopy(base)
                bad["observations"][0].update(status=status, matches=matches, candidates=candidates, notes=notes)
                self.assertTrue(list(Draft202012Validator(load_json(REFS / "observation_alignment.schema.json")).iter_errors(bad)))
                with self.assertRaises(ValidationError):
                    ObservationAlignment.model_validate(bad)

    def test_failed_registry_observation_cannot_be_assessed(self):
        result = self.alignment()
        result["observations"][-1]["status"] = "unmatched"
        with self.assertRaisesRegex(InvalidData, "failed registry observations"):
            self.validate(result)

    def test_duplicate_ids_pairs_locations_and_complement_values(self):
        base = self.alignment()
        variants = []
        bad = deepcopy(base); bad["observations"].append(bad["observations"][0]); variants.append(bad)
        bad = deepcopy(base); bad["observations"][0]["matches"].append(bad["observations"][0]["matches"][0]); variants.append(bad)
        bad = deepcopy(base); bad["observations"][0]["candidates"] = deepcopy(bad["observations"][0]["matches"]); variants.append(bad)
        bad = deepcopy(base); bad["observations"][0]["matches"][0]["location_indices"] = [0, 0]; variants.append(bad)
        bad = deepcopy(base); bad["inspected_pdf_pages"].append(1); variants.append(bad)
        bad = deepcopy(base); bad["unlinked_citrine_nos"].append(91003); variants.append(bad)
        for i, bad in enumerate(variants):
            with self.subTest(case=i), self.assertRaises(InvalidData): self.validate(bad)

    def test_exact_input_id_coverage_and_order(self):
        base = self.alignment()
        for ids in (base["observations"][:-1], list(reversed(base["observations"]))):
            bad = deepcopy(base); bad["observations"] = ids
            with self.assertRaisesRegex(InvalidData, "cover the supplied registry"):
                self.validate(bad)
        bad = deepcopy(base); bad["observations"][0]["observation_id"] = "obs_999"
        with self.assertRaisesRegex(InvalidData, "cover the supplied registry"):
            self.validate(bad)

    def test_unknown_row_and_invalid_indices_or_pages(self):
        base = self.alignment()
        for field, value in [("citrine_no", 99999), ("citrine_no", 0), ("citrine_no", True), ("location_indices", [99]), ("location_indices", [-1]), ("location_indices", [])]:
            bad = deepcopy(base); bad["observations"][0]["matches"][0][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(InvalidData): self.validate(bad)
        for pages in ([0], [2, 3, 4]):
            bad = deepcopy(base); bad["inspected_pdf_pages"] = pages
            with self.subTest(pages=pages), self.assertRaises(InvalidData): self.validate(bad)

    def test_target_and_supporting_cell_strings_are_checked(self):
        base = self.alignment()
        for change in ("target", "evidence", "column"):
            bad = deepcopy(base); link = bad["observations"][0]["matches"][0]
            if change == "target": link["cra_potential"]["avg"] = "300.0"
            elif change == "evidence": link["evidence"][0]["cra_value"] = "300.0"
            else: link["evidence"][0]["field"] = "unknown column"
            with self.subTest(change=change), self.assertRaises(InvalidData): self.validate(bad)

    def test_unlinked_complement_uses_supported_links_and_csv_order(self):
        for values in ([91004, 91003], [91004], [91002, 91003, 91004]):
            bad = self.alignment(); bad["unlinked_citrine_nos"] = values
            with self.subTest(values=values), self.assertRaisesRegex(InvalidData, "unsupported CSV No. complement"):
                self.validate(bad)

    def test_each_input_fingerprint_and_filename_is_checked(self):
        for key in ("pdf", "csv", "registry"):
            bad = self.alignment(); bad["inputs"][key]["sha256"] = "f" * 64
            with self.subTest(key=key), self.assertRaisesRegex(InvalidData, "fingerprints"):
                self.validate(bad)
        bad = self.alignment(); bad["inputs"]["registry"]["filename"] = "different.json"
        with self.assertRaisesRegex(InvalidData, "fingerprints"): self.validate(bad)

    def test_byte_changes_in_inputs_invalidate_existing_alignment(self):
        for path in (self.pdf, self.csv, self.registry):
            original = path.read_bytes(); result = self.alignment()
            path.write_bytes(original + b"\n")
            with self.subTest(path=path.name), self.assertRaisesRegex(InvalidData, "fingerprints"):
                self.validate(result)
            path.write_bytes(original)

    def test_output_paper_and_reference_are_checked(self):
        for key, value in (("paper_name", "different.pdf"), ("reference_number", 9002), ("schema_version", "2.0")):
            bad = self.alignment(); bad[key] = value
            with self.subTest(key=key), self.assertRaises(InvalidData): self.validate(bad)

    def test_registry_version_1_0_has_explicit_diagnostic(self):
        self.registry_document["schema_version"] = "1.0"
        dump(self.registry, self.registry_document)
        with self.assertRaisesRegex(InvalidData, "unsupported registry version '1.0'.*expected '1.1'"):
            self.prepared()

    def test_registry_measurement_location_and_primary_regressions(self):
        base = deepcopy(self.registry_document)
        for case in ("bounds", "uncertainty", "primary", "location_kind", "page", "duplicate_id", "unknown", "null_complete"):
            bad = deepcopy(base); source = bad["observations"][0]
            if case == "bounds": source["pitting_potential"] = source["locations"][0]["pitting_potential"] = {"value": 1, "min": 2, "unit": "V (SCE)"}
            elif case == "uncertainty": source["pitting_potential"] = source["locations"][0]["pitting_potential"] = {"min": 2, "plus_minus": 0.1}
            elif case == "primary": source["primary_location"] = 999
            elif case == "location_kind": source["locations"][0]["kind"] = "text"
            elif case == "page": source["locations"][0]["pdf_page"] = 0
            elif case == "duplicate_id": bad["observations"][1]["observation_id"] = source["observation_id"]
            elif case == "unknown": source["unexpected"] = "x"
            else: source["pitting_potential"] = source["locations"][0]["pitting_potential"] = None
            dump(self.registry, bad)
            with self.subTest(case=case), self.assertRaises(InvalidData): self.prepared()

    def test_primary_measurement_mismatch_is_rejected(self):
        self.registry_document["observations"][0]["pitting_potential"]["value"] = 0.4
        dump(self.registry, self.registry_document)
        with self.assertRaisesRegex(InvalidData, "must equal the primary"):
            self.prepared()

    def test_strict_json_duplicate_keys_nonfinite_and_invalid_encoding(self):
        for payload in (b'{"a":1,"a":2}', b'{"nested":{"a":1,"a":2}}', b'{"x":NaN}', b'{"x":Infinity}', b'{"x":-Infinity}', b'{"x":1e9999}', b'\x96', b'{broken'):
            with self.subTest(payload=payload), self.assertRaises(InvalidData): parse_json(payload, "test")

    def test_csv_duplicate_headers_missing_columns_and_malformed_records(self):
        original = self.csv.read_text(encoding="utf-8")
        header = original.splitlines()[0]
        for payload in (header + ",No.\n", "No.,Reference\n1,9001\n", header + '\n"unclosed', header + "\n1,9001\n", header + "\n" + ",".join(["x"] * (len(header.split(",")) + 1)) + "\n"):
            self.csv.write_text(payload, encoding="utf-8")
            with self.subTest(payload=payload[:60]), self.assertRaises(InvalidData): self.prepared()

    def test_csv_duplicate_nonpositive_noninteger_identifiers(self):
        base = self.rows()
        for column, value in [("No.", "0"), ("No.", "-1"), ("No.", "1.5"), ("No.", "NaN"), ("Reference", "0"), ("Reference", "1.5"), ("No.", "91001.0")]:
            rows = deepcopy(base)
            rows[1][column] = value
            self.write_csv(rows)
            with self.subTest(column=column, value=value), self.assertRaises(InvalidData): self.prepared()

    def test_mixed_csv_references_and_reference_conflicts(self):
        rows = self.rows(); rows[1]["Reference"] = "9002"; self.write_csv(rows)
        with self.assertRaisesRegex(InvalidData, "paper-specific CSV"): self.prepared()
        rows[1]["Reference"] = "9001"; self.write_csv(rows)
        self.registry_document["reference_number"] = 9002
        dump(self.registry, self.registry_document)
        with self.assertRaisesRegex(InvalidData, "Reference conflict"): self.prepared()

    def test_numbered_filenames_are_checked(self):
        for kind in ("pdf", "csv", "registry", "registry_paper"):
            with self.subTest(kind=kind):
                if kind == "registry_paper":
                    bad = deepcopy(self.registry_document); bad["paper_name"] = "9002_wrong.pdf"; dump(self.registry, bad)
                    paths = (self.pdf, self.csv, self.registry)
                else:
                    source = getattr(self, kind)
                    name = {"pdf": "9002_wrong.pdf", "csv": "pitting_potential_9002.csv", "registry": "paper_9002_batch.json"}[kind]
                    copied = self.directory / name; copied.write_bytes(source.read_bytes())
                    paths = tuple(copied if key == kind else getattr(self, key) for key in ("pdf", "csv", "registry"))
                with self.assertRaisesRegex(InvalidData, "Reference conflict"): prepare_inputs(*paths)

    def test_null_registry_reference_resolves_from_other_inputs(self):
        self.registry_document["reference_number"] = None
        dump(self.registry, self.registry_document)
        self.assertEqual(self.prepared().reference_number, 9001)

    def test_renamed_pdf_is_a_warning_not_automatic_rejection(self):
        renamed = self.directory / "9001_renamed.pdf"; renamed.write_bytes(self.pdf.read_bytes())
        prepared = prepare_inputs(renamed, self.csv, self.registry)
        self.assertEqual(prepared.reference_number, 9001)
        self.assertTrue(prepared.warnings)

    def test_csv_bom_quotes_multiline_whitespace_and_missing_strings(self):
        rows = self.rows()
        rows[0]["Comments"] = ' A | B, "quoted"\nsecond line μ '
        rows[0]["Min Epit mV (SCE)"] = " NA "
        self.write_csv(rows)
        self.csv.write_bytes(b"\xef\xbb\xbf" + self.csv.read_bytes())
        prepared = self.prepared()
        self.assertEqual(prepared.rows[0]["fields"]["Comments"], rows[0]["Comments"])
        self.assertEqual(prepared.rows[0]["cra_potential"]["min"], " NA ")

    def test_prepare_cli_emits_original_data_and_writes_nothing(self):
        before = {p.name: p.read_bytes() for p in self.directory.iterdir()}
        result = self.cli("prepare_inputs.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data["registry"], self.registry_document)
        self.assertEqual(data["cra_rows"][2]["cra_potential"]["avg"], "Transpassive")
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.directory.iterdir()})

    def test_validator_cli_summary_and_read_only_operation(self):
        dump(self.output, self.alignment())
        before = {p.name: p.read_bytes() for p in self.directory.iterdir()}
        result = self.cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("matched=3; ambiguous=1; unmatched=1; not_assessed=1", result.stdout)
        self.assertIn("91001: obs_007, obs_008", result.stdout)
        self.assertIn("ambiguous IDs: obs_011", result.stdout)
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.directory.iterdir()})

    def test_report_cli_has_one_compact_row_per_supplied_observation(self):
        dump(self.output, self.alignment())
        result = self.cli(extra=("--report-stdout",))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len([line for line in result.stdout.splitlines() if line.startswith("| obs_")]), 6)
        self.assertIn("&gt;800", result.stdout)
        self.assertIn("Transpassive", result.stdout)
        self.assertIn("Structural validation: PASS", result.stdout)
        self.assertFalse((self.directory / "alignment_report.md").exists())

    def test_report_escapes_pipe_and_multiline_source_cells(self):
        rows = self.rows(); rows[0]["Comments"] = ' A | B, "quoted"\nsecond line μ '; self.write_csv(rows)
        result = self.alignment()
        result["observations"][0]["matches"][0]["evidence"].append(dict(field="Comments", paper_value="A | B", cra_value=rows[0]["Comments"], comparison="Quoted source label."))
        report = render_report(self.validate(result), self.prepared())
        self.assertIn(r"A \| B", report)
        self.assertIn("second line μ", report)
        self.assertEqual(len([line for line in report.splitlines() if line.startswith("| obs_")]), 6)

    def test_blocked_visual_access_remains_valid_and_is_reported(self):
        result = self.alignment()
        result["inspected_pdf_pages"] = []
        result["coverage_notes"] = "Renderer unavailable: example actual capability error."
        result["unlinked_citrine_nos"] = [91001, 91002, 91003, 91004]
        for item in result["observations"]:
            item.update(status="not_assessed", matches=[], candidates=[], notes="Visual access blocked; registry recovery limitation retained where applicable.")
        dump(self.output, result)
        response = self.cli(extra=("--report-stdout",))
        self.assertEqual(response.returncode, 0, response.stderr)
        self.assertIn("not_assessed=6", response.stdout)
        self.assertIn("Renderer unavailable", response.stdout)

    def test_invalid_data_and_io_failures_have_distinct_cli_exit_codes(self):
        self.output.write_text('{"schema_version":"wrong"}', encoding="utf-8")
        result = self.cli(extra=("--report-stdout",))
        self.assertEqual(result.returncode, 1)
        self.assertNotIn("PASS", result.stdout)
        self.assertIn("unsupported alignment version", result.stderr)
        self.output.unlink()
        self.assertEqual(self.cli().returncode, 2)
        self.registry.write_text('{"schema_version":"1.0"}', encoding="utf-8")
        result = self.cli("prepare_inputs.py")
        self.assertEqual(result.returncode, 1)
        self.assertIn("unsupported registry version", result.stderr)

    def test_standalone_clis_outside_project_directory(self):
        folder = self.copy_skill()
        dump(self.output, self.alignment())
        for script in ("prepare_inputs.py", "validate_output.py"):
            with self.subTest(script=script):
                result = self.cli(script, folder=folder)
                self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(list(folder.rglob("__pycache__")))

    def test_missing_dependency_and_corrupt_schema_are_setup_failures(self):
        dump(self.output, self.alignment())
        result = self.cli(no_site=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("Setup failure", result.stderr)
        folder = self.copy_skill()
        (folder / "references" / "observation_alignment.schema.json").write_text('{}', encoding="utf-8")
        result = self.cli(folder=folder)
        self.assertEqual(result.returncode, 2)
        self.assertIn("differs from its Pydantic model", result.stderr)


if __name__ == "__main__":
    unittest.main()
