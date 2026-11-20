"""Bookkeeping migration tests with invented data only."""

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest
from zipfile import ZipFile

from update_observation_ids import (
    CORPUS_FOLDERS, load_json, main, plan_updates, replace_ids,
    replace_markdown, write_updates,
)


class ObservationIdMigrationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        for folder in CORPUS_FOLDERS:
            (self.root / folder).mkdir()
        self.registry = self.root / "observation_registry" / "paper_42.json"
        self.document = {
            "reference_number": 42,
            "observations": [
                {"observation_id": "obs_001", "pitting_potential": {"value": 100.25, "unit": "mV (SCE)"},
                 "result_note": "Obs_001/003 remain separate; obs_001–010 is a range."},
                {"observation_id": "obs_003", "pitting_potential": None},
                {"observation_id": "obs_010", "pitting_potential": {"min": 200}},
            ],
        }
        # Exercise exact byte preservation, including BOM and CRLF.
        self.registry.write_bytes(b"\xef\xbb\xbf" + json.dumps(self.document, ensure_ascii=False, indent=2).replace("\n", "\r\n").encode() + b"\r\n")
        self.output = self.root / "enriched_observations" / "paper_42.json"
        self.enrichment = {
            "reference_number": 42,
            "inputs": {"registry": {"filename": "paper_42.json", "sha256": sha256(self.registry.read_bytes()).hexdigest()},
                       "pdf": {"filename": "42_example.pdf", "sha256": "f" * 64}},
            "experiments": deepcopy(self.document["observations"][:2]),
        }
        self.output.write_text(json.dumps(self.enrichment, ensure_ascii=False), encoding="utf-8")
        self.report = self.root / "matched_observations" / "README_41-49.md"
        self.report.write_bytes(b"# Papers 41-49\r\n\r\n- **42:** obs_001/003\r\n- **43:** Obs_001\r\n")

    def test_references_ranges_case_and_idempotence(self):
        source = "obs_001/003/010; Obs_001–003; 42_obs_010; xobs_001; prefix_obs_001; obs_001, 100 mV"
        expected = "42_obs_001/42_obs_003/42_obs_010; 42_obs_001–42_obs_003; 42_obs_010; xobs_001; prefix_obs_001; 42_obs_001, 100 mV"
        self.assertEqual(replace_ids(source, 42), expected)
        self.assertEqual(replace_ids(expected, 42), expected)

    def test_batch_markdown_uses_each_papers_context(self):
        expected = "# Papers 41-49\r\n\r\n- **42:** 42_obs_001/42_obs_003\r\n- **43:** 43_obs_001\r\n"
        self.assertEqual(replace_markdown(self.report.read_bytes().decode(), None), expected)
        with self.assertRaisesRegex(ValueError, "Cannot determine the paper"):
            replace_markdown("# Papers 41-49\nUnscoped obs_001\n", None)

    def test_preserves_scientific_data_formatting_and_verified_lineage(self):
        originals, updated, hashes = plan_updates(self.root)
        self.assertEqual(hashes, 1)
        original_registry = self.registry.read_bytes()
        expected_registry = original_registry.replace(b"obs_", b"42_obs_").replace(b"Obs_", b"42_obs_")
        expected_registry = expected_registry.replace(b"/003", b"/42_obs_003").replace("–010".encode(), "–42_obs_010".encode())
        self.assertEqual(updated[self.registry], expected_registry)
        enrichment = load_json(updated[self.output])
        self.assertEqual(enrichment["experiments"][0]["pitting_potential"], self.enrichment["experiments"][0]["pitting_potential"])
        self.assertEqual(enrichment["inputs"]["pdf"], self.enrichment["inputs"]["pdf"])
        self.assertEqual(enrichment["inputs"]["registry"]["sha256"], sha256(updated[self.registry]).hexdigest())
        self.assertEqual(self.registry.read_bytes(), originals[self.registry])

    def test_backup_contains_originals_and_rerunning_changes_nothing(self):
        originals, updated, _ = plan_updates(self.root)
        backup = write_updates(self.root, originals, updated)
        with ZipFile(backup) as archive:
            self.assertIsNone(archive.testzip())
            for path, content in originals.items():
                self.assertEqual(archive.read(path.relative_to(self.root).as_posix()), content)
            self.assertIn("migration_manifest.json", archive.namelist())
        second_originals, second_updated, hashes = plan_updates(self.root)
        self.assertEqual(second_originals, second_updated)
        self.assertEqual(hashes, 0)
        self.assertIsNone(write_updates(self.root, second_originals, second_updated))

    def test_stale_lineage_blocks_the_whole_migration(self):
        self.enrichment["inputs"]["registry"]["sha256"] = "a" * 64
        self.output.write_text(json.dumps(self.enrichment), encoding="utf-8")
        before = self.registry.read_bytes()
        with self.assertRaisesRegex(ValueError, "Already-stale registry fingerprint"):
            plan_updates(self.root)
        self.assertEqual(self.registry.read_bytes(), before)
        self.assertFalse((self.root / "tmp").exists())

    def test_reference_conflicts_and_id_collisions_are_rejected(self):
        for identifier in ("43_obs_003", "42_obs_001"):
            document = deepcopy(self.document)
            document["observations"][1]["observation_id"] = identifier
            self.registry.write_text(json.dumps(document), encoding="utf-8")
            with self.subTest(identifier=identifier), self.assertRaises(ValueError):
                plan_updates(self.root)

    def test_files_changed_after_preflight_are_not_overwritten(self):
        originals, updated, _ = plan_updates(self.root)
        self.report.write_bytes(b"User edited this report.")
        with self.assertRaisesRegex(ValueError, "File changed since preflight"):
            write_updates(self.root, originals, updated)
        self.assertEqual(self.report.read_bytes(), b"User edited this report.")

    def test_dry_run_writes_nothing(self):
        before = {path: path.read_bytes() for path in self.root.rglob("*") if path.is_file()}
        self.assertEqual(main(["--root", str(self.root), "--dry-run"]), 0)
        self.assertEqual(before, {path: path.read_bytes() for path in self.root.rglob("*") if path.is_file()})

    def test_invalid_json_does_not_get_silently_rewritten(self):
        for content in (b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":1e999}'):
            with self.subTest(content=content), self.assertRaises(ValueError):
                load_json(content)


if __name__ == "__main__":
    unittest.main()
