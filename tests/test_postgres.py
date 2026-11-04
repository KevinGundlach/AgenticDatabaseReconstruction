"""Run unit tests with: python -m unittest discover -s tests -v

Set RUN_POSTGRES_TESTS=1 to also create/drop isolated importer_test_<uuid>
databases on the local server using the importer's default connection settings.
These tests never use agenticdb.
"""

from contextlib import closing
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch
import uuid

import psycopg2
from psycopg2 import sql

from utils import postgres as pg


PROJECT = Path(__file__).resolve().parents[1]


def extraction_records():
    return [json.loads(path.read_text(encoding="utf-8"))
            for path in sorted((PROJECT / "series_extractions").glob("*.json"))]


class InferenceTests(unittest.TestCase):
    def infer(self, datasets):
        db = pg.AutoSchemaDB({}, "importer_test_inference")
        db.infer_datasets(datasets)
        return db

    def test_containers_and_independent_roots(self):
        db = self.infer({
            "left": [{"items": [{"details": {}}]}],
            "right": [{"items": [{"name": "other"}]}],
        })
        self.assertEqual(db.tables["left"], {"id": "SERIAL PRIMARY KEY"})
        self.assertEqual(db.fks["left__items"], ("left", "left_id"))
        self.assertEqual(db.fks["left__items__details"], ("left__items", "left__items_id"))
        self.assertIn("right__items", db.tables)
        self.assertNotIn("name", db.tables["left__items"])

    def test_array_classification_uses_all_observations(self):
        rows = [{"objects": [], "empty": [], "mixed": []},
                {"objects": [{"n": 1}], "mixed": [{"value": 2}, None, "text", 3]}]
        for records in (rows, list(reversed(rows))):
            with self.subTest(records=records):
                db = self.infer({"root": records})
                self.assertEqual(db.fields["root"]["objects"].kind, "relation")
                self.assertEqual(db.tables["root"]["empty"], "JSONB")
                self.assertEqual(db.tables["root"]["mixed"], "JSONB")

    def test_nullable_and_mixed_scalar_fields(self):
        db = self.infer({"root": [{"null": None, "n": 1, "text": True},
                                  {"n": 2.5, "text": 7}, {"text": "raw"}]})
        self.assertEqual(db.tables["root"]["null"], "TEXT")
        self.assertEqual(db.tables["root"]["n"], "DOUBLE PRECISION")
        self.assertEqual(db.tables["root"]["text"], "TEXT")

    def test_invalid_inputs_fail_before_any_connection(self):
        cases = [
            ({"root": [{"id": 1}]}, "id"),
            ({"root": [{"child": {"root_id": 1}}]}, "root_id"),
            ({"root": [{"v": {}}, {"v": 1}]}, "v"),
            ({"root": [{"v": []}, {"v": "text"}]}, "v"),
            ({"root": [{"v": True}, {"v": 1}]}, "v"),
            ({"root": [{"v": float("nan")}]}, "v"),
            ({"root": [{"rows": [[float("inf")]]}]}, "rows"),
            ({"root": [{"v": "bad\x00text"}]}, "v"),
            ({"root": [{"v": {1, 2}}]}, "v"),
            ({"root": [1]}, "root"),
            ({"root": {}}, "root"),
            ({"root": [{"a": {}}], "root__a": []}, "collision"),
            ({"root": [{"a__b": {}, "a": {"b": {}}}]}, "collision"),
            ({}, "datasets"),
        ]
        for datasets, message in cases:
            with self.subTest(datasets=datasets), patch.object(pg.psycopg2, "connect") as connect:
                with self.assertRaisesRegex(ValueError, message):
                    pg.recreate_and_insert_many(datasets, "importer_test_invalid")
                connect.assert_not_called()

    def test_identifiers_are_bounded_deterministic_and_collision_checked(self):
        root = "r" * 80
        key = "温度" * 40
        db = self.infer({root: [{key: 1, "child": [{"x": 2}]}]})
        other = self.infer({root: [{key: 1, "child": [{"x": 2}]}]})
        self.assertEqual(db.tables, other.tables)
        self.assertEqual(db.fks, other.fks)
        for table, columns in db.tables.items():
            for name in (table, *columns):
                self.assertLessEqual(len(name.encode("utf-8")), 63)
        shortened = pg._identifier(key)
        with self.assertRaisesRegex(ValueError, "collision"):
            self.infer({"root": [{key: 1, shortened: 2}]})

    def test_actual_extraction_layout(self):
        records = extraction_records()
        self.assertTrue(records)
        db = self.infer({"papers": records})
        self.assertEqual(db.tables["papers__series"]["rows"], "JSONB")
        self.assertEqual(db.fields["papers__series"]["columns"].kind, "relation")

    def test_single_root_wrapper(self):
        rows = [{"x": 1}]
        params = {"host": "localhost"}
        with patch.object(pg, "recreate_and_insert_many") as load:
            pg.recreate_and_insert(rows, "example", "root", params)
        load.assert_called_once_with({"root": rows}, "example", params)


@unittest.skipUnless(os.environ.get("RUN_POSTGRES_TESTS") == "1",
                     "set RUN_POSTGRES_TESTS=1 for disposable PostgreSQL integration tests")
class PostgreSQLTests(unittest.TestCase):
    def setUp(self):
        self.dbname = "importer_test_" + uuid.uuid4().hex
        self.params = {**pg.DefaultDBParams, "connect_timeout": 5}
        self.addCleanup(self.drop_test_database)

    def drop_test_database(self):
        # Only delete the exact randomly generated test database for this test.
        if not self.dbname.startswith("importer_test_"):
            raise AssertionError("Refusing to drop a non-test database")
        with closing(psycopg2.connect(**self.params, dbname="postgres")) as conn:
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute(sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(self.dbname)))

    def query(self, statement, args=None):
        with closing(psycopg2.connect(**self.params, dbname=self.dbname)) as conn:
            with conn.cursor() as cur:
                cur.execute(statement, args)
                return cur.fetchall()

    def test_multiple_roots_containers_foreign_keys_and_rebuild(self):
        datasets = {
            "left": [{"items": [{"details": {}}, {"details": {}}]}, {}],
            "right": [{"items": [{"name": "independent"}]}],
        }
        original = pg.AutoSchemaDB.recreate_database
        calls = []

        def recreate(db):
            calls.append(db.target_db_name)
            original(db)

        with patch.object(pg.AutoSchemaDB, "recreate_database", recreate):
            pg.recreate_and_insert_many(datasets, self.dbname, self.params)
        self.assertEqual(calls, [self.dbname])
        self.assertEqual(self.query('SELECT count(*) FROM "left"'), [(2,)])
        self.assertEqual(self.query('SELECT count(*) FROM left__items'), [(2,)])
        self.assertEqual(self.query('SELECT count(*) FROM left__items__details'), [(2,)])
        self.assertEqual(self.query('SELECT name FROM right__items'), [("independent",)])
        self.assertEqual(self.query('SELECT count(*) FROM "left" p JOIN left__items c '
                                    'ON c.left_id=p.id JOIN left__items__details d '
                                    'ON d.left__items_id=c.id'), [(2,)])
        self.assertEqual(self.query("SELECT count(*) FROM pg_constraint WHERE contype='f'"), [(3,)])
        with closing(psycopg2.connect(**self.params, dbname=self.dbname)) as conn:
            with conn.cursor() as cur:
                with self.assertRaises(psycopg2.errors.ForeignKeyViolation):
                    cur.execute("INSERT INTO left__items (left_id) VALUES (-1)")
        # A second rebuild removes old tables and preserves the old Python API.
        pg.recreate_and_insert([{"fresh": True}], self.dbname, "replacement", self.params)
        self.assertEqual(self.query("SELECT tablename FROM pg_tables WHERE schemaname='public'"),
                         [("replacement",)])

    def test_extractions_and_lossless_jsonb(self):
        papers = extraction_records()
        raw = [[1.25, "text", None, {"value": 4, "plus_minus": 0.2}], ["温度", -2]]
        pg.recreate_and_insert_many({
            "papers": papers,
            "other": [{"rows": raw, "empty": [], "null": None},
                      {"rows": [], "empty": []}],
        }, self.dbname, self.params)
        self.assertEqual(self.query("SELECT count(*) FROM papers"), [(len(papers),)])
        expected_series = sum(len(paper["series"]) for paper in papers)
        self.assertEqual(self.query("SELECT count(*) FROM papers__series"), [(expected_series,)])
        expected_columns = sum(len(series["columns"]) for paper in papers for series in paper["series"])
        self.assertEqual(self.query("SELECT count(*) FROM papers__series__columns"), [(expected_columns,)])
        saved = self.query("SELECT p.reference_number, s.source, s.rows FROM papers p "
                           "JOIN papers__series s ON s.papers_id=p.id ORDER BY p.id, s.id")
        expected = [(p["reference_number"], s["source"], s["rows"])
                    for p in papers for s in p["series"]]
        self.assertEqual(saved, expected)
        self.assertEqual(self.query('SELECT rows, empty, "null" FROM other ORDER BY id'),
                         [(raw, [], None), ([], [], None)])
        self.assertEqual(self.query("SELECT rows->0->3->>'value' FROM other WHERE id=1"), [("4",)])

    def test_failed_load_rolls_back_all_tables_and_closes_connections(self):
        original = pg.AutoSchemaDB.insert_data
        opened = []
        connect = pg.AutoSchemaDB._connect

        def track_connect(db, name):
            conn = connect(db, name)
            opened.append(conn)
            return conn

        def fail_second_root(db, records, table, parent_id=None, conn=None):
            original(db, records, table, parent_id, conn)
            if table == "second":
                raise RuntimeError("injected insertion failure")

        with patch.object(pg.AutoSchemaDB, "insert_data", fail_second_root), \
                patch.object(pg.AutoSchemaDB, "_connect", track_connect):
            with self.assertRaisesRegex(RuntimeError, "injected"):
                pg.recreate_and_insert_many({"first": [{"x": 1}], "second": [{"x": 2}]},
                                            self.dbname, self.params)
        self.assertTrue(opened)
        self.assertTrue(all(conn.closed for conn in opened))
        self.assertEqual(self.query("SELECT tablename FROM pg_tables WHERE schemaname='public'"), [])


if __name__ == "__main__":
    unittest.main()
