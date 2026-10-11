#!/usr/bin/env python3
"""Exercise four concrete failure modes in disposable collection copies.

SPDX-License-Identifier: MIT
The mutations target catalog drift, unknown status vocabulary, duplicate JSON
keys and a manifest that omits a shipped file. They do not modify the source.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import tempfile

from catalog import ROOT, rendered_catalog
from verify_collection import execute


def check(root: Path):
    positive = execute(root)
    cases = [
        ("C01-catalog-drift", "generated catalog drift"),
        ("C02-unknown-status", "is not one of"),
        ("C03-duplicate-key", "duplicate JSON key"),
        ("C04-omitted-manifest-entry", "package manifest file-set mismatch"),
    ]
    results = []
    for case_id, expected_reason in cases:
        with tempfile.TemporaryDirectory(prefix="wexp-collection-control-") as temporary:
            copy = Path(temporary) / "collection"
            shutil.copytree(root, copy, ignore=shutil.ignore_patterns(".git", "__pycache__"))
            package = copy / "experiments/emilia-interop-001/packages/pkg-001"
            record = package / "record.json"
            if case_id == "C01-catalog-drift":
                target = copy / "catalog.json"
                target.write_bytes(target.read_bytes() + b"\n")
            elif case_id == "C02-unknown-status":
                data = json.loads(record.read_text())
                data["status"]["comparison"] = "bridge-needed"
                record.write_text(json.dumps(data) + "\n")
            elif case_id == "C03-duplicate-key":
                record.write_text(record.read_text().replace('{', '{"schema_version":"0.1.0",', 1))
            else:
                target = package / "PACKAGE-MANIFEST.sha256"
                rows = target.read_text().splitlines()
                target.write_text("\n".join(rows[:-1]) + "\n")
            reason = None
            try:
                execute(copy)
            except (ValueError, OSError) as error:
                reason = str(error)
            results.append({"id": case_id, "expected_reason_fragment": expected_reason,
                            "observed_error": reason, "rejected_as_expected": reason is not None and expected_reason in reason})
    return {"schema": "collection-negative-controls-001", "observed_at_utc": datetime.now(timezone.utc).isoformat(),
            "status": "PASS" if all(row["rejected_as_expected"] for row in results) else "FAIL",
            "baseline": positive, "cases": results,
            "source_catalog_sha256": hashlib.sha256((root / "catalog.json").read_bytes()).hexdigest(),
            "mutations_applied_to_disposable_copies_only": True,
            "scope": "four maintenance failure controls, not experiment conformance or exhaustive validator proof"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists() or args.out.resolve().is_relative_to(args.root.resolve()):
        parser.error("--out must be new and outside the source repository")
    report = check(args.root.resolve())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": report["status"], "cases": len(report["cases"]), "report": str(args.out)}))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
