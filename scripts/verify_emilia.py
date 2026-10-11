#!/usr/bin/env python3
"""Verify the exact EMILIA source archive, extraction and original byte verifier.

SPDX-License-Identifier: MIT
New collection tooling, 2026-10-11. Outputs are written to a new directory
outside the repository. A fresh Git transport clone is a separate procedure.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import stat
import subprocess
import sys
import zipfile

from emilia.inspect_archive import inspect

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "experiments/emilia-interop-001/packages/pkg-001"
ZIP_NAME = "WEXP-EMILIA-INTEROP-001-PUBLICATION-CANDIDATE.zip"
ZIP_SHA = "f27b4ffc4259a91cdb11dd28424946612b723b0cffe62e588d1740c6a15c951f"
FREEZE_NAME = "WEXP-EMILIA-INTEROP-001-PUBLICATION-CANDIDATE-FREEZE-002.yaml"
FREEZE_SHA = "750b9632a1e4e3774618b3e7150b66ab2ac714b9123a70ee917d798d4a6acff5"
MANIFEST_SHA = "4172c2d0d9f4cfaddaa4036a7d92e53d1ee6c2c290654daedaa5806e5281ad6a"
METADATA_SHA = "45885e423193ebadb83f34c80e1941e38e13c7b01ea1f38c89ced69e4e10f73d"
METADATA_BLOB = "ae90a4ab9331d986d163c0f6db18cd9201ff5d61"
METADATA_URL = "https://github.com/WEXP-dev/wexp-interop/blob/4075939139d56b40e6e08788959de169559919af/PUBLICATION-METADATA.yaml"
VERIFIER_SHA = "f4237c5db7a5668abe9a8d452ee2ca9d939eb0ccd6220a0574320ab2773dcca3"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def execute(root: Path, out: Path, report: dict):
    package = root / PACKAGE
    archive = package / "source-archive" / ZIP_NAME
    data = archive.read_bytes()
    require((len(data), sha(data)) == (200140, ZIP_SHA), "archive identity mismatch")
    inspection = inspect(archive, "https://zenodo.org/api/records/22056151/files/" + ZIP_NAME + "/content", ZIP_SHA)
    require(inspection["summary"]["structural_inspection_passed"], "archive name/type/collision inspection failed")
    (out / "archive-inspection.json").write_text(json.dumps(inspection, ensure_ascii=False, indent=2) + "\n")
    payload = package / "payload"
    comparisons = []
    expected_files = set()
    expected_directories = {""}
    with zipfile.ZipFile(io.BytesIO(data)) as zipped:
        for member in zipped.infolist():
            prefix = ZIP_NAME[:-4] + "/"
            require(member.orig_filename.startswith(prefix), "unexpected ZIP prefix")
            relative = member.orig_filename[len(prefix):].rstrip("/")
            if member.is_dir():
                expected_directories.add(relative)
                continue
            expected_files.add(relative)
            path = payload / relative
            require(path.is_file() and not path.is_symlink(), f"payload missing/symlink: {relative}")
            expected = zipped.read(member)
            actual = path.read_bytes()
            comparisons.append({"path": relative, "sha256": sha(actual), "bytes": len(actual),
                                "bytes_match": expected == actual,
                                "archive_permissions": f"{stat.S_IMODE(member.external_attr >> 16):04o}"})
    actual_files = {path.relative_to(payload).as_posix() for path in payload.rglob("*") if path.is_file()}
    actual_directories = {""} | {path.relative_to(payload).as_posix() for path in payload.rglob("*") if path.is_dir()}
    require(not any(path.is_symlink() for path in payload.rglob("*")), "payload symlink")
    require(expected_files == actual_files and len(expected_files) == 68, "payload file-set mismatch")
    require(expected_directories == actual_directories, "payload directory-set mismatch")
    require(all(row["bytes_match"] for row in comparisons), "payload byte mismatch")
    report["payload_files"] = comparisons
    report["payload_directories"] = len(expected_directories)
    freeze = package / "source-archive" / FREEZE_NAME
    require((freeze.stat().st_size, sha(freeze.read_bytes())) == (2260, FREEZE_SHA), "freeze identity mismatch")
    metadata = package / "evidence/historical-preparation/expected-sha-source-PUBLICATION-METADATA.yaml"
    command = [sys.executable, "-B", str(root / "scripts/emilia/verify_freeze_bindings.py"),
               "--archive", str(archive), "--freeze", str(freeze), "--metadata", str(metadata),
               "--metadata-sha256", METADATA_SHA, "--metadata-git-blob", METADATA_BLOB,
               "--metadata-source-url", METADATA_URL,
               "--manifest-member", ZIP_NAME[:-4] + "/MANIFEST.sha256", "--out", str(out / "freeze.json")]
    freeze_run = subprocess.run(command, capture_output=True, timeout=60)
    report["freeze"] = {"command": command, "exit_code": freeze_run.returncode,
                         "stdout": freeze_run.stdout.decode(), "stderr": freeze_run.stderr.decode()}
    require(freeze_run.returncode == 0, "freeze verifier failed")
    verifier = payload / "reproduction/verify_final.py"
    require(sha(verifier.read_bytes()) == VERIFIER_SHA, "original verifier pin mismatch; not executed")
    command = [sys.executable, "-I", "-B", str(verifier), "--manifest-sha256", MANIFEST_SHA]
    executed = subprocess.run(command, cwd=payload, capture_output=True, timeout=60)
    result = json.loads(executed.stdout) if executed.returncode == 0 else {}
    report["original_verifier"] = {"command": command, "exit_code": executed.returncode,
                                   "stdout": executed.stdout.decode(), "stderr": executed.stderr.decode(),
                                   "result": result}
    require(executed.returncode == 0 and result.get("status") == "PASS" and result.get("payload_entries_verified") == 67
            and result.get("frozen_identities_verified") == 15
            and result.get("terminal_branch") == "A — EXPLICIT BRIDGE REQUIRED"
            and result.get("implementation_execution_performed") is False,
            "original verifier failed or exceeded expected scope")
    report["summary"] = {"payload_files_identical": 68, "freeze_checks_passed": 11,
                         "freeze_additional_checks_passed": 3, "original_verifier_status": "PASS",
                         "implementation_execution_performed": False,
                         "fresh_git_clone_checked_by_this_command": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--out", type=Path, required=True, help="new report directory outside repository")
    args = parser.parse_args()
    root = args.root.resolve()
    out = args.out.resolve()
    if out.exists() or out.is_relative_to(root):
        parser.error("--out must be a new directory outside the repository")
    out.mkdir(parents=True)
    report = {"schema": "emilia-public-collection-replay-001", "status": "FAIL",
              "started_at_utc": datetime.now(timezone.utc).isoformat(),
              "environment": {"python": sys.version, "platform": platform.platform()},
              "script_sha256": sha(Path(__file__).read_bytes()),
              "scope": "exact archive and current payload byte replay, not a new experiment run"}
    try:
        execute(root, out, report)
        report["status"] = "PASS"
    except (OSError, ValueError, KeyError, subprocess.SubprocessError, zipfile.BadZipFile) as error:
        report["error"] = str(error)
    report["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
    (out / "verification.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": report["status"], "report": str(out / "verification.json"),
                      "summary": report.get("summary"), "error": report.get("error")}))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
