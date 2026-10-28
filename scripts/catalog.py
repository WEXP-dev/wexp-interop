#!/usr/bin/env python3
"""Validate versioned package cards and deterministically generate catalog.json.

SPDX-License-Identifier: MIT
New collection tooling, 2026-10-11. The catalog contains no independent facts:
each entry is a projection of one validated record.json and its byte identity.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError(f"non-JSON constant: {value}")))


def load_records(root: Path = ROOT):
    validators = {}
    for version, name in (("0.1.0", "record.schema.json"), ("0.2.0", "record-0.2.0.schema.json")):
        schema = load_json(root / "schemas" / name)
        Draft202012Validator.check_schema(schema)
        validators[version] = Draft202012Validator(schema, format_checker=FormatChecker())
    records = []
    identities = set()
    for path in sorted(root.glob("experiments/*/packages/*/record.json")):
        data = load_json(path)
        if not isinstance(data, dict) or data.get("schema_version") not in validators:
            raise ValueError("unsupported package card schema version")
        validator = validators[data["schema_version"]]
        errors = sorted(validator.iter_errors(data), key=lambda error: list(map(str, error.path)))
        if errors:
            raise ValueError(f"{path.relative_to(root)}: {'/'.join(map(str, errors[0].path))}: {errors[0].message}")
        identity = (data["experiment_id"], data["package_id"])
        if identity in identities:
            raise ValueError(f"duplicate package identity: {identity}")
        identities.add(identity)
        expected = root / "experiments" / identity[0] / "packages" / identity[1] / "record.json"
        if path != expected:
            raise ValueError(f"card identity disagrees with path: {path.relative_to(root)}")
        if data["status"]["execution"] == "archived-evidence-replayed" and data["verification"]["implementation_execution_performed"]:
            raise ValueError("archived-evidence-replayed cannot claim a new implementation execution")
        if data["status"]["execution"] == "local-run-completed" and not data["verification"]["implementation_execution_performed"]:
            raise ValueError("local-run-completed requires a recorded implementation execution")
        if data["status"]["execution"] == "not-run" and (data["verification"]["implementation_execution_performed"] or data["status"]["comparison"] != "not-evaluated"):
            raise ValueError("not-run cannot claim implementation execution or an evaluated comparison")
        if data["status"]["publication"] == "published" and not data["publication"]["carriers"]:
            raise ValueError("published requires an identified public carrier")
        if data["status"]["independent_reproduction"] == "performed" and not data["independence"]["evidence"]:
            raise ValueError("independent reproduction requires scoped evidence")
        records.append((path, data))
    if not records:
        raise ValueError("no package records found")
    return records


def rendered_catalog(root: Path = ROOT) -> bytes:
    entries = []
    for path, data in load_records(root):
        relative = path.parent.relative_to(root).as_posix()
        entries.append({
            "experiment_id": data["experiment_id"], "package_id": data["package_id"],
            "title": data["title"], "summary": data["summary"], "status": data["status"],
            "card": f"{relative}/README.md", "record": f"{relative}/record.json",
            "record_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "citation": f"{relative}/{data['citation_path']}",
            "publication": data["publication"], "result": data["result"],
        })
    return (json.dumps({"schema_version": "0.1.0", "generated_from": "experiments/*/packages/*/record.json",
                       "packages": entries}, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--check", action="store_true", help="fail if catalog.json differs; do not write")
    args = parser.parse_args()
    try:
        expected = rendered_catalog(args.root.resolve())
        target = args.root / "catalog.json"
        if args.check:
            if not target.is_file() or target.read_bytes() != expected:
                raise ValueError("catalog.json differs from its generated projection; run scripts/catalog.py")
        else:
            target.write_bytes(expected)
        print(json.dumps({"status": "PASS", "mode": "check" if args.check else "generate",
                          "packages": len(load_records(args.root.resolve())),
                          "catalog_sha256": hashlib.sha256(expected).hexdigest()}))
        return 0
    except (OSError, ValueError) as error:
        print(json.dumps({"status": "FAIL", "error": str(error)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
