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


# INTEROP-002 Candidate 003 (package emilia-interop-002/pkg-001). Added 2026-11-11.
# Differences from INTEROP-001 that this path handles explicitly: the ZIP has no
# directory entries, member modes carry permission bits without a file-type bit,
# and there is no separate FREEZE record. The candidate's own internal manifest and
# its two-scope verdict record are checked instead. No archived code is executed.
PACKAGE_002 = "experiments/emilia-interop-002/packages/pkg-001"
ZIP_NAME_002 = "WEXP-EMILIA-INTEROP-002-PUBLICATION-CANDIDATE-003.zip"
ZIP_BYTES_002 = 192089
ZIP_SHA_002 = "37412ba521b9bca9901b54142290356a0aedf8bc7cd635e731d7660916cf770e"
INTERNAL_MANIFEST_002 = "publication-candidate/PUBLICATION-CANDIDATE-MANIFEST-003.json"
INTERNAL_MANIFEST_SHA_002 = "b7d3e62036d3905e686fba4e28c8051eeece13a89a15e5d722f51c241604c50b"
VERDICT_RECORD_002 = "publication-candidate/FINAL-RECORD-002.json"
VERDICT_RECORD_SHA_002 = "4768decf3721e2dfcfddab2028e0ea35e6352d00efb1bf24ecdaf67c7c389266"
EXECUTION_RECORD_002 = "execution/EXECUTION-RECORD-001.json"
INCONCLUSIVE_002 = ["H-01-b", "H-01-c", "H-02", "H-03", "B-01"]
NOT_DERIVED_002 = ["C-00", "H-01-a"]


def execute_002(root: Path, out: Path, report: dict):
    package = root / PACKAGE_002
    archive = package / "source-archive" / ZIP_NAME_002
    data = archive.read_bytes()
    require((len(data), sha(data)) == (ZIP_BYTES_002, ZIP_SHA_002), "archive identity mismatch")
    inspection = inspect(archive, None, ZIP_SHA_002)
    require(inspection["summary"]["structural_inspection_passed"], "archive name/type/collision inspection failed")
    require(inspection["summary"]["explicit_directories"] == 0, "unexpected explicit directory entries")
    require({m["unix_type"] for m in inspection["members"]} == {"not-specified"}
            and {m["unix_permissions"] for m in inspection["members"]} == {"0644"},
            "member mode differs from the recorded 0644 without a file-type bit")
    inspection["archive"]["local_path"] = PACKAGE_002 + "/source-archive/" + ZIP_NAME_002
    (out / "archive-inspection.json").write_text(json.dumps(inspection, ensure_ascii=False, indent=2) + "\n")
    payload = package / "payload"
    prefix = ZIP_NAME_002[:-4] + "/"
    comparisons = []
    expected_files = set()
    expected_directories = {""}
    with zipfile.ZipFile(io.BytesIO(data)) as zipped:
        for member in zipped.infolist():
            require(member.orig_filename.startswith(prefix), "unexpected ZIP prefix")
            require(not member.is_dir(), "unexpected directory entry")
            relative = member.orig_filename[len(prefix):]
            expected_files.add(relative)
            parts = relative.split("/")
            expected_directories.update("/".join(parts[:end]) for end in range(1, len(parts)))
            path = payload / relative
            require(path.is_file() and not path.is_symlink(), f"payload missing/symlink: {relative}")
            expected = zipped.read(member)
            actual = path.read_bytes()
            comparisons.append({"path": relative, "sha256": sha(actual), "bytes": len(actual),
                                "bytes_match": expected == actual,
                                "archive_permissions": f"{stat.S_IMODE(member.external_attr >> 16):04o}",
                                "archive_file_type_bits": f"{stat.S_IFMT(member.external_attr >> 16):o}"})
    actual_files = {path.relative_to(payload).as_posix() for path in payload.rglob("*") if path.is_file()}
    actual_directories = {""} | {path.relative_to(payload).as_posix() for path in payload.rglob("*") if path.is_dir()}
    require(not any(path.is_symlink() for path in payload.rglob("*")), "payload symlink")
    require(expected_files == actual_files and len(expected_files) == 57, "payload file-set mismatch")
    require(expected_directories == actual_directories, "payload directory-set mismatch (implicit directories)")
    require(all(row["bytes_match"] for row in comparisons), "payload byte mismatch")
    report["payload_files"] = comparisons
    report["payload_directories_implicit"] = len(expected_directories)
    manifest_bytes = (payload / INTERNAL_MANIFEST_002).read_bytes()
    require(sha(manifest_bytes) == INTERNAL_MANIFEST_SHA_002, "internal manifest pin mismatch")
    manifest = json.loads(manifest_bytes)
    require(manifest.get("status") == "CANDIDATE / NOT PUBLISHED", "internal manifest status changed")
    entries = manifest["files"]
    require(len(entries) == manifest["file_count"] == 56, "internal manifest entry count mismatch")
    for entry in entries:
        content = (payload / entry["path"]).read_bytes()
        require(len(content) == entry["bytes"] and sha(content) == entry["sha256"],
                f"internal manifest mismatch: {entry['path']}")
    require(actual_files - {entry["path"] for entry in entries} == {INTERNAL_MANIFEST_002},
            "files outside the internal manifest other than the self-excluded manifest")
    verdict_bytes = (payload / VERDICT_RECORD_002).read_bytes()
    require(sha(verdict_bytes) == VERDICT_RECORD_SHA_002, "verdict record pin mismatch")
    scopes = json.loads(verdict_bytes)["TWO_SCOPES_NOT_ONE_VERDICT"]
    bridge, joint = scopes["WEXP_BRIDGE_SUFFICIENCY"], scopes["JOINT_WEXP_EMILIA_COMPARISON"]
    require(bridge["verdict"] == "SUPPORTED", "bridge sufficiency verdict changed")
    require(joint["verdict"] == "INCONCLUSIVE for every case lacking native EMILIA output"
            and joint["inconclusive_cases"] == INCONCLUSIVE_002
            and joint["cases_with_a_pre_existing_native_emilia_output"] == NOT_DERIVED_002
            and joint["state_for_those_two"] == "NOT_DERIVED_UNDER_THIS_ORDER", "joint comparison verdict changed")
    require("MUST NOT be collapsed" in scopes["instruction"], "two-scope instruction absent")
    bound = manifest["verdicts_bound"]
    require(bound["WEXP_BRIDGE_SUFFICIENCY"] == bridge["verdict"] and bound["JOINT_WEXP_EMILIA_COMPARISON"] == joint["verdict"]
            and bound["inconclusive_cases"] == INCONCLUSIVE_002, "internal manifest and verdict record disagree")
    execution = json.loads((payload / EXECUTION_RECORD_002).read_bytes())
    require(execution["execution_status"] == "EXECUTED", "historical execution status changed")
    report["recorded_verdicts"] = {"WEXP_BRIDGE_SUFFICIENCY": bridge["verdict"],
                                   "JOINT_WEXP_EMILIA_COMPARISON": joint["verdict"],
                                   "inconclusive_cases": INCONCLUSIVE_002, "not_derived_cases": NOT_DERIVED_002,
                                   "historical_execution_status": execution["execution_status"]}
    report["summary"] = {"payload_files_identical": 57, "zip_directory_entries": 0,
                         "member_mode": "0644 without file-type bit", "freeze_record": "none in this candidate",
                         "internal_manifest_entries_verified": 56, "split_verdict_checked": True,
                         "archived_code_executed": False, "implementation_execution_performed": False,
                         "fresh_git_clone_checked_by_this_command": False}


PACKAGES = {"emilia-interop-001/pkg-001": execute, "emilia-interop-002/pkg-001": execute_002}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--out", type=Path, required=True, help="new report directory outside repository")
    parser.add_argument("--package", choices=sorted(PACKAGES), default="emilia-interop-001/pkg-001",
                        help="EMILIA package to check; the default and its behaviour are unchanged")
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
    if args.package != "emilia-interop-001/pkg-001":
        report["schema"] = "emilia-public-collection-replay-002"
        report["package"] = args.package
    try:
        PACKAGES[args.package](root, out, report)
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
