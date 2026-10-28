#!/usr/bin/env python3
"""Check cards, generated catalog, package manifests and new local links.

SPDX-License-Identifier: MIT
New collection tooling, 2026-10-11. This checks the declared collection
surface. A schema or hash PASS does not validate an experiment's conclusion.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

from catalog import ROOT, load_json, load_records, rendered_catalog


def package_path(package: Path, value: str) -> Path:
    if not value or value.startswith("/") or "\\" in value or any(part in {"", ".", ".."} for part in value.split("/")):
        raise ValueError(f"noncanonical package path: {value}")
    candidate = package / value
    if not candidate.resolve().is_relative_to(package.resolve()) or candidate.is_symlink():
        raise ValueError(f"package path escapes or is a symlink: {value}")
    return candidate


def verify_manifest(package: Path):
    manifest = package / "PACKAGE-MANIFEST.sha256"
    rows = {}
    for line in manifest.read_text(encoding="utf-8").splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        if not match:
            raise ValueError(f"malformed package manifest: {manifest}")
        digest, relative = match.groups()
        if relative == manifest.name or relative in rows:
            raise ValueError(f"duplicate or self-referential manifest path: {relative}")
        path = package_path(package, relative)
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError(f"package manifest mismatch: {relative}")
        rows[relative] = digest
    actual = set()
    for path in package.rglob("*"):
        if path.is_symlink():
            raise ValueError(f"package symlink: {path}")
        if path.is_file() and path != manifest:
            actual.add(path.relative_to(package).as_posix())
    if set(rows) != actual:
        raise ValueError(f"package manifest file-set mismatch: omitted={sorted(actual-set(rows))}, absent={sorted(set(rows)-actual)}")
    return len(rows)


def new_markdown(root: Path):
    for path in sorted(root.rglob("*.md")):
        relative = path.relative_to(root)
        if ".git" in relative.parts or any(part in {"payload", "publication-history", "historical-preparation"} for part in relative.parts):
            continue
        yield path


def check_links(root: Path):
    checked = 0
    for path in new_markdown(root):
        text = path.read_text(encoding="utf-8")
        for target in re.findall(r"(?<!!)\[[^\]]*\]\(([^\s)]+)\)", text):
            parsed = urlsplit(target)
            if parsed.scheme or target.startswith("#"):
                continue
            relative = unquote(parsed.path)
            resolved = (path.parent / relative).resolve()
            if not resolved.is_relative_to(root.resolve()) or not resolved.exists():
                raise ValueError(f"unresolved local link in {path.relative_to(root)}: {target}")
            checked += 1
    return checked


def execute(root: Path):
    if (root / "CITATION.cff").exists():
        raise ValueError("collection root must not impersonate a package with CITATION.cff")
    if (root / "catalog.json").read_bytes() != rendered_catalog(root):
        raise ValueError("generated catalog drift")
    records = load_records(root)
    counts = []
    for record_path, record in records:
        package = record_path.parent
        artifact = record["artifact"]
        archive = package_path(package, artifact["path"])
        data = archive.read_bytes()
        if len(data) != artifact["bytes"] or hashlib.sha256(data).hexdigest() != artifact["sha256"]:
            raise ValueError(f"artifact identity mismatch: {archive}")
        for relative in [record["citation_path"], record["license"]["scope_path"],
                         record["verification"]["instructions"], *record["verification"]["evidence"],
                         *record["independence"]["evidence"]]:
            if not package_path(package, relative).is_file():
                raise ValueError(f"missing package reference: {relative}")
        payload = package_path(package, record["payload"]["path"])
        if not payload.is_dir():
            raise ValueError("payload directory absent")
        payload_files = [path for path in payload.rglob("*") if path.is_file()]
        if len(payload_files) != record["payload"]["regular_files"]:
            raise ValueError("payload regular-file count differs from card")
        export_path = package / "evidence/EXPORT-MANIFEST.json"
        if export_path.is_file():
            exported = load_json(export_path)["entries"]
            exported_paths = set()
            for entry in exported:
                exported_file = package_path(package, entry["path"])
                data = exported_file.read_bytes()
                if entry["path"] in exported_paths or entry["transformation"] != "none" or len(data) != entry["bytes"] or hashlib.sha256(data).hexdigest() != entry["sha256"]:
                    raise ValueError("exported historical source identity mismatch")
                exported_paths.add(entry["path"])
            historical_files = {path.relative_to(package).as_posix() for path in (package / "evidence/historical-preparation").rglob("*") if path.is_file()}
            if exported_paths != historical_files:
                raise ValueError("export allowlist differs from preserved historical files")
        checked = {"experiment_id": record["experiment_id"], "package_id": record["package_id"],
                   "manifest_entries": verify_manifest(package)}
        if record["verification"]["profile"] == "aar-pilot-v1":
            from verify_aar import execute_package
            checked["aar_saved_evidence"] = execute_package(package, record)
        elif record["verification"]["profile"] == "wimse-core02-migration-v1":
            from verify_wimse_core02 import verify_package
            checked["wimse_core02_saved_evidence"] = verify_package(package, record)
        counts.append(checked)
    return {"status": "PASS", "scope": "cards/catalog/manifests/local links; bounded AAR saved-evidence checks where selected",
            "packages": counts, "local_links_checked": check_links(root),
            "experiment_execution_performed": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        print(json.dumps(execute(args.root.resolve()), ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError) as error:
        print(json.dumps({"status": "FAIL", "error": str(error)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
