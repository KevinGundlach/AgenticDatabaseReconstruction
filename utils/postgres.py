from collections.abc import Mapping
from contextlib import closing
from dataclasses import dataclass
import hashlib
import json
import math

import psycopg2
from psycopg2 import sql
from psycopg2.extras import Json
import pandas as pd
from sqlalchemy import create_engine


# Nested objects become related tables; arrays of values are preserved as JSONB.

DefaultDBParams = {
    "user": "postgres",
    "password": "badwolf",
    "host": "localhost",
    "port": "5432"
}

@dataclass
class _Field:
    kind: str
    name: str  # SQL column name, or child table name for a relationship.


def _identifier(name):
    """Keep identifiers within PostgreSQL's 63-byte limit, including Unicode."""
    encoded = name.encode("utf-8")
    if len(encoded) <= 63:
        return name
    suffix = "_" + hashlib.sha256(encoded).hexdigest()[:12]
    return encoded[:63 - len(suffix)].decode("utf-8", errors="ignore") + suffix


def _valid_name(name, path):
    if not isinstance(name, str) or not name or "\x00" in name:
        raise ValueError(f"{path}: expected a nonempty string without NUL characters")
    try:
        name.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise ValueError(f"{path}: invalid Unicode") from exc


def _validate_json(value, path):
    """Validate even values inside JSONB before any destructive operation."""
    if value is None or isinstance(value, (bool, int)):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"{path}: non-finite numbers are not supported")
        return
    if isinstance(value, str):
        if "\x00" in value:
            raise ValueError(f"{path}: NUL characters are not supported by PostgreSQL")
        try:
            value.encode("utf-8")
        except UnicodeEncodeError as exc:
            raise ValueError(f"{path}: invalid Unicode") from exc
        return
    if isinstance(value, dict):
        for key, item in value.items():
            _valid_name(key, path)
            _validate_json(item, f"{path}[{key!r}]")
        return
    if isinstance(value, list):
        for i, item in enumerate(value):
            _validate_json(item, f"{path}[{i}]")
        return
    raise ValueError(f"{path}: unsupported JSON value {type(value).__name__}")


class AutoSchemaDB:
    """Infer a forest of JSON objects without connecting to PostgreSQL.

    Nested table names join root/property names with ``__``. Every table has an
    ``id`` primary key; children have a ``<parent_table>_id`` foreign key.
    Long identifiers receive a stable hash suffix. Name collisions are rejected.
    """

    def __init__(self, db_params, target_db_name):
        _valid_name(target_db_name, "target_db_name")
        if len(target_db_name.encode("utf-8")) > 63:
            raise ValueError("target_db_name: exceeds PostgreSQL's 63-byte limit")
        self.db_params = dict(db_params)
        self.target_db_name = target_db_name
        self.tables = {}
        self.fks = {}
        self.fields = {}
        self.roots = {}
        self._table_paths = {}
        self._datasets = {}

    def _get_pg_type(self, val):
        if isinstance(val, bool):
            return "BOOLEAN"
        if isinstance(val, int):
            if -(2**31) <= val < 2**31:
                return "INTEGER"
            if -(2**63) <= val < 2**63:
                return "BIGINT"
            return "NUMERIC"
        if isinstance(val, float):
            return "DOUBLE PRECISION"
        return "TEXT"

    def _resolve_type(self, old_type, new_type):
        if old_type == new_type:
            return old_type
        if "TEXT" in (old_type, new_type):
            return "TEXT"
        numeric = ["INTEGER", "BIGINT", "NUMERIC", "DOUBLE PRECISION"]
        if old_type in numeric and new_type in numeric:
            return numeric[max(numeric.index(old_type), numeric.index(new_type))]
        raise ValueError(f"incompatible scalar types: {old_type} vs {new_type}")

    def infer_datasets(self, datasets):
        """Validate and infer every root before opening a database connection.

        Roots must be lists of dictionaries. Nulls do not determine a field's
        shape; fields containing only nulls become nullable TEXT columns.
        """
        if not isinstance(datasets, Mapping) or not datasets:
            raise ValueError("datasets: expected a nonempty mapping of names to record lists")
        for root, records in datasets.items():
            _valid_name(root, "datasets root name")
            path = f"datasets[{root!r}]"
            if not isinstance(records, list):
                raise ValueError(f"{path}: expected a list of objects")
            for i, row in enumerate(records):
                if not isinstance(row, dict):
                    raise ValueError(f"{path}[{i}]: expected an object")
                _validate_json(row, f"{path}[{i}]")

        self.tables.clear()
        self.fks.clear()
        self.fields.clear()
        self.roots.clear()
        self._table_paths.clear()
        self._datasets = dict(datasets)
        for root, records in datasets.items():
            observations = [(row, f"datasets[{root!r}][{i}]") for i, row in enumerate(records)]
            self.roots[root] = self._infer_table(observations, (root,))

    def infer_schema(self, data_list, table_name):
        """Compatibility helper: add a root and re-infer all known datasets."""
        self.infer_datasets({**self._datasets, table_name: data_list})

    def _infer_table(self, records, path, parent_table=None):
        table = _identifier("__".join(path))
        if table in self._table_paths and self._table_paths[table] != path:
            raise ValueError(f"{path!r}: table name collision with {self._table_paths[table]!r}")
        self._table_paths[table] = path
        columns = {"id": "SERIAL PRIMARY KEY"}
        if parent_table is not None:
            fk_col = _identifier(f"{parent_table}_id")
            columns[fk_col] = "INTEGER"
            self.fks[table] = (parent_table, fk_col)
        self.tables[table] = columns
        self.fields[table] = {}

        observations = {}
        for row, row_path in records:
            for key, value in row.items():
                observations.setdefault(key, []).append((value, f"{row_path}[{key!r}]"))
        names = dict.fromkeys(columns, "generated column")
        for key, values in observations.items():
            column = _identifier(key)
            location = values[0][1]
            if column in names:
                raise ValueError(f"{location}: column name collision with {names[column]}")
            names[column] = repr(key)
            nonnull = [(v, p) for v, p in values if v is not None]
            shapes = {"object" if isinstance(v, dict) else "array" if isinstance(v, list)
                      else "scalar" for v, _ in nonnull}
            if len(shapes) > 1:
                locations = ", ".join(p for _, p in nonnull[:3])
                raise ValueError(f"{location}: incompatible input shapes {sorted(shapes)} ({locations})")
            shape = next(iter(shapes), "scalar")
            object_array = (shape == "array" and any(v for v, _ in nonnull)
                            and all(isinstance(item, dict) for v, _ in nonnull for item in v))
            if shape == "object" or object_array:
                children = []
                for value, value_path in nonnull:
                    if shape == "object":
                        children.append((value, value_path))
                    else:
                        children.extend((item, f"{value_path}[{i}]") for i, item in enumerate(value))
                child = self._infer_table(children, path + (key,), table)
                self.fields[table][key] = _Field("relation", child)
            elif shape == "array":
                columns[column] = "JSONB"
                self.fields[table][key] = _Field("jsonb", column)
            else:
                types = {self._get_pg_type(v) for v, _ in nonnull}
                pg_type = "TEXT" if not types or "TEXT" in types else None
                if pg_type is None:
                    try:
                        for item_type in sorted(types):
                            pg_type = item_type if pg_type is None else self._resolve_type(pg_type, item_type)
                    except ValueError as exc:
                        raise ValueError(f"{location}: {exc}") from exc
                columns[column] = pg_type
                self.fields[table][key] = _Field("scalar", column)
        return table

    def _connect(self, dbname):
        params = {k: v for k, v in self.db_params.items() if k not in ("dbname", "database")}
        return psycopg2.connect(**params, dbname=dbname)

    def recreate_database(self):
        """Drop/recreate only the explicitly named target using a maintenance DB."""
        maintenance = "template1" if self.target_db_name == "postgres" else "postgres"
        print(f"Recreating database '{self.target_db_name}'...")
        with closing(self._connect(maintenance)) as conn:
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute(sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(self.target_db_name)))
                cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(self.target_db_name)))

    def create_tables(self, conn=None):
        """Create tables in inference order (parents precede children)."""
        if conn is None:
            with closing(self._connect(self.target_db_name)) as owned:
                with owned:
                    self.create_tables(owned)
            return
        with conn.cursor() as cur:
            for table, columns in self.tables.items():
                definitions = [sql.SQL("{} {}").format(sql.Identifier(name), sql.SQL(pg_type))
                               for name, pg_type in columns.items()]
                if table in self.fks:
                    parent, fk_col = self.fks[table]
                    definitions.append(sql.SQL("FOREIGN KEY ({}) REFERENCES {} (id) ON DELETE CASCADE")
                                       .format(sql.Identifier(fk_col), sql.Identifier(parent)))
                cur.execute(sql.SQL("CREATE TABLE {} ({})").format(
                    sql.Identifier(table), sql.SQL(", ").join(definitions)))

    def insert_data(self, data_list, table_name, parent_id=None, conn=None):
        """Insert using the inferred layout; a supplied connection owns the transaction."""
        table = self.roots.get(table_name, table_name)
        if conn is None:
            with closing(self._connect(self.target_db_name)) as owned:
                with owned:
                    self._insert_rows(data_list, table, parent_id, owned)
            return
        self._insert_rows(data_list, table, parent_id, conn)

    def _insert_rows(self, records, table, parent_id, conn):
        with conn.cursor() as cur:
            for row in records:
                values = {}
                children = []
                if table in self.fks:
                    values[self.fks[table][1]] = parent_id
                for key, value in row.items():
                    field = self.fields[table][key]
                    if field.kind == "relation":
                        if value is not None:
                            children.append((field.name, [value] if isinstance(value, dict) else value))
                    elif field.kind == "jsonb":
                        values[field.name] = None if value is None else Json(value, dumps=_json_dumps)
                    else:
                        # Explicit conversion makes mixed numeric/text fields predictable.
                        values[field.name] = (str(value) if value is not None
                                              and self.tables[table][field.name] == "TEXT" else value)
                if values:
                    query = sql.SQL("INSERT INTO {} ({}) VALUES ({}) RETURNING id").format(
                        sql.Identifier(table), sql.SQL(", ").join(map(sql.Identifier, values)),
                        sql.SQL(", ").join(sql.Placeholder() for _ in values))
                else:
                    query = sql.SQL("INSERT INTO {} DEFAULT VALUES RETURNING id").format(sql.Identifier(table))
                cur.execute(query, list(values.values()))
                new_id = cur.fetchone()[0]
                for child_table, child_rows in children:
                    self._insert_rows(child_rows, child_table, new_id, conn)


def _json_dumps(value):
    return json.dumps(value, allow_nan=False)


def recreate_and_insert_many(datasets, target_db_name, db_params=DefaultDBParams):
    """Rebuild a database from independent named lists of JSON objects.

    Example::

        recreate_and_insert_many(
            {"papers": papers, "citrine": citrine_records}, "agenticdb")

    All shape/name validation precedes DROP DATABASE. Table creation and every
    root's inserts share one transaction. A load failure leaves a newly empty
    database: the previously dropped database cannot be restored by rollback.
    Arrays of values/mixed items become JSONB; nonempty arrays containing only
    objects become child tables. Only-empty arrays also become JSONB.
    """
    autoschema = AutoSchemaDB(db_params, target_db_name)
    autoschema.infer_datasets(datasets)
    autoschema.recreate_database()
    with closing(autoschema._connect(target_db_name)) as conn:
        with conn:
            autoschema.create_tables(conn)
            for root, rows in datasets.items():
                autoschema.insert_data(rows, root, conn=conn)


def recreate_and_insert(data_list, target_db_name, root_table_name, db_params=DefaultDBParams):
    """Single-root compatibility wrapper for :func:`recreate_and_insert_many`."""
    recreate_and_insert_many({root_table_name: data_list}, target_db_name, db_params)


def df_to_postgres(df, db_name, table_name, dbparams=DefaultDBParams, if_exists='replace'):
    """
    Uploads a pandas DataFrame to a PostgreSQL database.

    Parameters:
    - df (pd.DataFrame): The pandas DataFrame to upload.
    - db_name (str): Name of the database.
    - table_name (str): The name of the target table in the database.
    - dbparams (dict): Parameters for connecting to the database {user, password, host, port}.
    - if_exists (str): Behavior when the table already exists.
                       Options: 'fail', 'replace', 'append'. Default is 'replace'.
    """

    db_user = dbparams['user'] 
    db_password = dbparams['password']
    db_host = dbparams['host']
    db_port = dbparams['port']
  
    # 1. Construct the SQLAlchemy connection string
    # Format: postgresql+psycopg2://user:password@host:port/dbname
    connection_string = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

    # 2. Create the SQLAlchemy engine
    engine = create_engine(connection_string)

    try:
        print(f"Uploading data to table '{table_name}'...")
        
        # 3. Execute the .to_sql() method
        df.to_sql(
            name=table_name,
            con=engine,
            if_exists=if_exists,
            index=False # Set to True if you want the DataFrame's index written as a column
        )
        print("Upload completed successfully!")

    except Exception as e:
        print(f"An error occurred: {e}")
        
    finally:
        # 4. Dispose of the engine connection pool to free up resources
        engine.dispose()
