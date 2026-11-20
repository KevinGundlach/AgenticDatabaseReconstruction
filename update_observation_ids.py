"""Prefix saved observation IDs and prose references with their paper number.

Run from any directory: python update_observation_ids.py [--dry-run].
Only JSON/Markdown under the three corpus folders is edited. Formatting, BOMs,
line endings and scientific values are retained. Registry fingerprints are
updated only after verifying the old fingerprints. Each write run first saves
the original files and a before/after hash manifest in a ZIP under tmp/.
"""

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
import math
import os
from pathlib import Path
import re
import sys
import tempfile
from zipfile import ZIP_DEFLATED, ZipFile


CORPUS_FOLDERS = ("observation_registry", "matched_observations", "enriched_observations")
OBSERVATION_ID = re.compile(r"(?:([1-9][0-9]*)_)?obs_[0-9]{3,}")
ID_REFERENCE = re.compile(
    r"(?<![A-Za-z0-9_])(?:(?P<prefix>[1-9][0-9]*)_)?obs_"
    r"(?P<sequence>[0-9]{3,})(?![A-Za-z0-9_])"
    r"(?P<tail>(?:[ \t]*[/\-\u2013\u2014][ \t]*[0-9]{3,}(?![A-Za-z0-9_]))*)",
    re.IGNORECASE,
)
PAPER_FILENAME = re.compile(r"^paper_([1-9][0-9]*)(?=_|\.)")
REGISTRY_HASH = re.compile(r'("registry"\s*:\s*\{[^{}]*"sha256"\s*:\s*")([0-9a-f]{64})(")')


def load_json(content):
    """Reject duplicate keys and non-finite numbers without rewriting JSON."""
    def unique_keys(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"Duplicate JSON key: {key}")
            result[key] = value
        return result

    def finite_number(value):
        number = float(value)
        if not math.isfinite(number):
            raise ValueError(f"Non-finite JSON number: {value}")
        return number

    return json.loads(content, object_pairs_hook=unique_keys,
                      parse_float=finite_number, parse_constant=finite_number)


def replace_ids(text, reference):
    """Also expand obs_001/003 and obs_001–003; already prefixed IDs stay so."""
    def replace(match):
        prefix = match["prefix"] or reference
        if prefix is None:
            raise ValueError(f"Cannot determine the paper for {match.group(0)!r}")
        tail = re.sub(r"[0-9]{3,}", lambda number: f"{prefix}_obs_{number.group(0)}", match["tail"])
        return f"{prefix}_obs_{match['sequence']}{tail}"

    return ID_REFERENCE.sub(replace, text)


def replace_markdown(text, reference):
    if reference is not None:
        return replace_ids(text, reference)
    # Batch READMEs have paper-specific bullets such as "- **44:** ...".
    # Never apply one paper number to a whole multi-paper summary.
    lines = []
    current = None
    for line in text.splitlines(keepends=True):
        heading = re.match(r"^#{1,6}\s+(?:Paper|Reference)\s+([1-9][0-9]*)\b", line, re.IGNORECASE)
        bullet = re.match(r"^\s*-\s+\*\*([1-9][0-9]*):?\*\*:?", line)
        if heading or bullet:
            current = int((heading or bullet).group(1))
        elif re.match(r"^#|^\s*-\s+\*\*", line):
            current = None
        lines.append(replace_ids(line, current))
    return "".join(lines)


def replace_json_strings(value, reference):
    """Expected semantic change, checked against the format-preserving edits."""
    if isinstance(value, str):
        return replace_ids(value, reference)
    if isinstance(value, list):
        return [replace_json_strings(item, reference) for item in value]
    if isinstance(value, dict):
        return {replace_ids(key, reference): replace_json_strings(item, reference)
                for key, item in value.items()}
    return value


def check_ids(document, reference, collection):
    identifiers = []
    for row in document[collection]:
        identifier = row["observation_id"]
        match = OBSERVATION_ID.fullmatch(identifier)
        if match is None or (match[1] is not None and int(match[1]) != reference):
            raise ValueError(f"Invalid observation ID for paper {reference}: {identifier!r}")
        identifiers.append(identifier)
    if len(identifiers) != len(set(identifiers)):
        raise ValueError(f"Duplicate observation IDs for paper {reference}")


def plan_updates(root):
    """Preflight the whole corpus before writing any file."""
    originals = {}
    documents = {}
    references = {}
    registries = {}
    for folder in CORPUS_FOLDERS:
        directory = root / folder
        if not directory.is_dir():
            raise ValueError(f"Missing corpus directory: {directory}")
        for path in sorted(directory.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in (".json", ".md"):
                continue
            originals[path] = path.read_bytes()
            filename = PAPER_FILENAME.match(path.name)
            reference = int(filename[1]) if filename else None
            references[path] = reference
            if path.suffix.lower() != ".json":
                continue
            if reference is None:
                raise ValueError(f"JSON filename has no paper reference: {path}")
            document = load_json(originals[path])
            metadata = document["reference_number"]
            if metadata is not None and (type(metadata) is not int or metadata != reference):
                raise ValueError(f"Filename/reference_number conflict: {path}")
            collection = "experiments" if folder == "enriched_observations" else "observations"
            check_ids(document, reference, collection)
            documents[path] = document
            if folder == "observation_registry":
                if path.name in registries:
                    raise ValueError(f"Ambiguous registry filename: {path.name}")
                registries[path.name] = path

    updated = {}
    for path, content in originals.items():
        text = content.decode("utf-8")  # Retains a BOM and the original newline characters.
        rewrite = replace_ids if path in documents else replace_markdown
        updated[path] = rewrite(text, references[path]).encode("utf-8")

    hash_updates = {
        sha256(originals[path]).hexdigest(): sha256(updated[path]).hexdigest()
        for path in registries.values() if originals[path] != updated[path]
    }
    hash_count = 0
    for path, document in documents.items():
        expected = replace_json_strings(document, references[path])
        registry_input = document.get("inputs", {}).get("registry")
        if registry_input is not None:
            source = registries.get(registry_input["filename"])
            if source is None:
                raise ValueError(f"Missing registry input for {path}: {registry_input['filename']}")
            old_hash = sha256(originals[source]).hexdigest()
            if registry_input["sha256"] != old_hash:
                raise ValueError(f"Already-stale registry fingerprint in {path}; refusing to repair lineage")
            if references[source] != references[path]:
                raise ValueError(f"Registry belongs to a different paper: {path}")
            new_hash = sha256(updated[source]).hexdigest()
            if new_hash != old_hash:
                text, count = REGISTRY_HASH.subn(
                    lambda match: match[1] + new_hash + match[3], updated[path].decode("utf-8")
                )
                if count != 1:
                    raise ValueError(f"Expected exactly one registry fingerprint in {path}, found {count}")
                updated[path] = text.encode("utf-8")
                hash_count += 1
            expected["inputs"]["registry"]["sha256"] = new_hash
        actual = load_json(updated[path])
        if actual != expected:
            raise ValueError(f"Unexpected JSON content change in {path}")
        collection = "experiments" if path.is_relative_to(root / "enriched_observations") else "observations"
        check_ids(actual, references[path], collection)

    for path in originals.keys() - documents.keys():
        # Update any literal registry hashes quoted in supporting Markdown too.
        for old_hash, new_hash in hash_updates.items():
            updated[path] = updated[path].replace(old_hash.encode(), new_hash.encode())
    return originals, updated, hash_count


def write_updates(root, originals, updated):
    changed = {path: content for path, content in updated.items() if content != originals[path]}
    if not changed:
        return None
    # Recheck all inputs before the first write, including unchanged registries.
    for path, content in originals.items():
        if path.read_bytes() != content:
            raise ValueError(f"File changed since preflight: {path}")
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    backup = root / "tmp" / "observation_id_backups" / f"{timestamp}.zip"
    backup.parent.mkdir(parents=True, exist_ok=True)
    manifest = {
        str(path.relative_to(root)): {"before": sha256(originals[path]).hexdigest(),
                                     "after": sha256(content).hexdigest()}
        for path, content in changed.items()
    }
    with ZipFile(backup, "x", compression=ZIP_DEFLATED) as archive:
        for path in changed:
            archive.writestr(path.relative_to(root).as_posix(), originals[path])
        archive.writestr("migration_manifest.json", json.dumps(manifest, indent=2) + "\n")
    print(f"Backup: {backup}", flush=True)
    for path, content in changed.items():
        # Replace each file atomically. The ZIP retains originals if interrupted.
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".observation_ids_", delete=False) as stream:
                temporary = Path(stream.name)
                stream.write(content)
            os.replace(temporary, path)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
    for path, content in updated.items():
        if path.read_bytes() != content:
            raise ValueError(f"Post-write verification failed: {path}; backup: {backup}")
    return backup


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent,
                        help="Project root (defaults to this script's directory).")
    parser.add_argument("--dry-run", action="store_true", help="Check and summarize without writing files.")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        originals, updated, hash_count = plan_updates(root)
        changed = [path for path in originals if originals[path] != updated[path]]
        for folder in CORPUS_FOLDERS:
            paths = [path for path in changed if path.is_relative_to(root / folder)]
            print(f"{folder}: {len(paths)} files to update "
                  f"({sum(path.suffix == '.json' for path in paths)} JSON, "
                  f"{sum(path.suffix == '.md' for path in paths)} Markdown)")
        print(f"Registry fingerprints to update: {hash_count}")
        if args.dry_run:
            print(f"Dry run: {len(changed)} of {len(originals)} files would change; no files written.")
        else:
            write_updates(root, originals, updated)
            print(f"Updated and verified {len(changed)} of {len(originals)} files.")
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"Migration failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
