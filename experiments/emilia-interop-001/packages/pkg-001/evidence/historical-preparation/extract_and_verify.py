#!/usr/bin/env python3
"""Extract the inspected EMILIA ZIP and run its unmodified recorded-byte verifier.

This is an archive extraction check, not a Git migration or implementation run.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import os
from pathlib import Path
import platform
import stat
import subprocess
import sys
import zipfile

BASE = Path(__file__).resolve().parent
ARCHIVE = BASE / "zenodo/WEXP-EMILIA-INTEROP-001-PUBLICATION-CANDIDATE.zip"
INSPECTION = BASE / "archive-inspection-001.json"
DESTINATION = BASE / "extracted-001"
RESULT = BASE / "extraction-verification-001.json"
MANIFEST_SHA256 = "4172c2d0d9f4cfaddaa4036a7d92e53d1ee6c2c290654daedaa5806e5281ad6a"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def main():
    started = now()
    if DESTINATION.exists() or RESULT.exists():
        raise SystemExit("Refusing to overwrite existing extraction or evidence.")
    inspection_bytes = INSPECTION.read_bytes()
    inspection = json.loads(inspection_bytes)
    if (not inspection["summary"]["structural_inspection_passed"]
            or inspection["archive"]["expected_sha256_matches"] is not True):
        raise SystemExit("Passing pinned-archive inspection is required first.")
    if digest(ARCHIVE.read_bytes()) != inspection["archive"]["sha256"]:
        raise SystemExit("Archive changed after inspection.")
    DESTINATION.mkdir()
    directories = []
    with zipfile.ZipFile(ARCHIVE) as archive:
        for info in archive.infolist():
            name = info.orig_filename
            parts = name.rstrip("/").split("/")
            if (name.startswith(("/", "\\")) or "\\" in name or ":" in name
                    or any(p in {"", ".", ".."} for p in parts)):
                raise SystemExit("Unsafe path in inspected archive.")
            target = DESTINATION.joinpath(*parts)
            if not target.resolve().is_relative_to(DESTINATION.resolve()):
                raise SystemExit("Extraction path escapes destination.")
            if info.create_system != 3:
                raise SystemExit("This extraction procedure requires explicit Unix modes.")
            unix_mode = info.external_attr >> 16
            kind = stat.S_IFMT(unix_mode)
            if kind == stat.S_IFDIR and info.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                directories.append((target, stat.S_IMODE(unix_mode)))
            elif kind == stat.S_IFREG and not info.is_dir():
                target.parent.mkdir(parents=True, exist_ok=True)
                with target.open("xb") as output:
                    output.write(archive.read(info))
                target.chmod(stat.S_IMODE(unix_mode))
            else:
                raise SystemExit("Unexpected entry type; no type conversion allowed.")
        for directory, mode in reversed(directories):
            directory.chmod(mode)

    checks = []
    for entry in inspection["members"]:
        target = DESTINATION / entry["name"].rstrip("/")
        observed_stat = target.lstat()
        expected_type = "directory" if entry["directory_by_name"] else "regular"
        observed_type = "directory" if stat.S_ISDIR(observed_stat.st_mode) else "regular" if stat.S_ISREG(observed_stat.st_mode) else "other"
        expected_mode = int(entry["unix_permissions"], 8)
        same_bytes = None if entry["directory_by_name"] else digest(target.read_bytes()) == entry["sha256"]
        row = {"name": entry["name"], "type_equal": observed_type == expected_type,
               "permissions_equal": stat.S_IMODE(observed_stat.st_mode) == expected_mode,
               "expected_permissions": entry["unix_permissions"],
               "observed_permissions": f"{stat.S_IMODE(observed_stat.st_mode):04o}",
               "bytes_equal": same_bytes}
        checks.append(row)
    if not all(c["type_equal"] and c["permissions_equal"] and c["bytes_equal"] is not False for c in checks):
        raise SystemExit("Extracted member comparison failed; verifier was not run.")
    payload = DESTINATION / "WEXP-EMILIA-INTEROP-001-PUBLICATION-CANDIDATE"
    verifier = payload / "reproduction/verify_final.py"
    command = [sys.executable, "-B", str(verifier), "--manifest-sha256", MANIFEST_SHA256]
    environment = {k: v for k, v in os.environ.items() if k not in {"PYTHONPATH", "PYTHONHOME"}}
    environment.update(PYTHONDONTWRITEBYTECODE="1", PYTHONNOUSERSITE="1")
    verifier_started = now()
    completed = subprocess.run(command, cwd=payload, env=environment, capture_output=True, timeout=60)
    observation = {
        "schema": "emilia-extraction-verification-001", "started_at_utc": started,
        "finished_at_utc": now(), "archive_sha256": inspection["archive"]["sha256"],
        "inspection_sha256": digest(inspection_bytes),
        "audit_script_sha256": digest(Path(__file__).read_bytes()),
        "extraction_root": str(DESTINATION), "payload_root": str(payload),
        "member_checks": checks,
        "regular_file_bytes_verified": sum(c["bytes_equal"] is True for c in checks),
        "all_member_types_and_unix_permissions_verified": True,
        "zip_timestamps_or_extended_metadata_restored": False,
        "verifier": {"path": str(verifier), "sha256": digest(verifier.read_bytes()),
                     "command": command, "cwd": str(payload), "started_at_utc": verifier_started,
                     "python": sys.version, "platform": platform.platform(),
                     "returncode": completed.returncode,
                     "stdout_utf8": completed.stdout.decode(), "stderr_utf8": completed.stderr.decode(),
                     "stdout_sha256": digest(completed.stdout), "stderr_sha256": digest(completed.stderr)},
        "git_migration_performed": False, "fresh_git_clone_checked": False,
        "wexp_or_emilia_implementation_executed": False,
        "limitation": "The original verifier checks archived evidence bytes and recorded relationships. It does not execute a WEXP or EMILIA implementation or establish new interoperability.",
    }
    RESULT.write_text(json.dumps(observation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"report": str(RESULT), "regular_file_bytes_verified": observation["regular_file_bytes_verified"],
                     "all_member_types_and_unix_permissions_verified": True,
                     "verifier_returncode": completed.returncode,
                     "verifier_stdout": completed.stdout.decode(),
                     "fresh_git_clone_checked": False}, ensure_ascii=False, indent=2))
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
