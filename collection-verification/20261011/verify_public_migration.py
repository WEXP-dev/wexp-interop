#!/usr/bin/env python3
"""Verify an exact public collection commit in a fresh Git transport clone.

The destination, report and auxiliary output must be new. Checks include
all 68 archived payload file bytes and mode projections, all 69 earlier
main file blobs, the original verifier, current collection validators and
whole-tree case/Unicode/path conflicts. No implementation experiment runs.

Derived from verify_clean_clone.py in clean-clone-003, SHA-256
377187e715aa1e2ec44755fcc76f6aa0981fd067dc3c7038ddad89ca1225840e.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import platform
import re
import stat
import subprocess
import sys
import unicodedata
import zipfile


BASE = "d951b0b4170c3b169deb3cfe5ced85232a0a4f88"
PACKAGE = "experiments/emilia-interop-001/packages/pkg-001"
ZIP_NAME = "WEXP-EMILIA-INTEROP-001-PUBLICATION-CANDIDATE.zip"
ZIP_ROOT = ZIP_NAME.removesuffix(".zip")
ZIP_SHA = "f27b4ffc4259a91cdb11dd28424946612b723b0cffe62e588d1740c6a15c951f"
FREEZE_NAME = "WEXP-EMILIA-INTEROP-001-PUBLICATION-CANDIDATE-FREEZE-002.yaml"
FREEZE_SHA = "750b9632a1e4e3774618b3e7150b66ab2ac714b9123a70ee917d798d4a6acff5"
MANIFEST_SHA = "4172c2d0d9f4cfaddaa4036a7d92e53d1ee6c2c290654daedaa5806e5281ad6a"
VERIFIER_SHA = "f4237c5db7a5668abe9a8d452ee2ca9d939eb0ccd6220a0574320ab2773dcca3"
HISTORY_FILES = {"README.md", "CITATION.cff", "PUBLICATION-METADATA.yaml", "PUBLICATION-STATE-001.md"}
ENV = {k: v for k, v in os.environ.items()
       if not k.startswith("GIT_") and k not in {"PYTHONPATH", "PYTHONHOME"}}
ENV.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull, GIT_ATTR_NOSYSTEM="1",
           PYTHONDONTWRITEBYTECODE="1", PYTHONNOUSERSITE="1")
GIT = ["git", "-c", "core.autocrlf=true", "-c", "core.filemode=true", "-c", "core.attributesFile=" + os.devnull]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def blob_oid(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run(command: list[str], *, cwd: Path | None = None, data: bytes | None = None,
        environment: dict | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(command, cwd=cwd, input=data, env=environment or ENV, capture_output=True,
                          timeout=120, preexec_fn=lambda: os.umask(0o022))


def git(repo: Path, *args: str, data: bytes | None = None) -> bytes:
    completed = run(GIT + ["-C", str(repo), *args], data=data)
    if completed.returncode:
        raise RuntimeError(f"git {args!r} failed: {completed.stderr.decode(errors='replace')}")
    return completed.stdout


def tree(repo: Path, commit: str) -> dict[str, dict[str, str]]:
    result = {}
    for row in git(repo, "ls-tree", "-r", "-z", commit).split(b"\0"):
        if row:
            meta, path = row.split(b"\t", 1)
            mode, kind, oid = meta.decode().split()
            result[path.decode()] = {"mode": mode, "kind": kind, "oid": oid}
    return result


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise RuntimeError(reason)


def path_checks(entries: dict) -> dict:
    """Check components, including implicit directories, not just leaf names."""
    files = set(entries)
    directories = set()
    for name, entry in entries.items():
        parts = name.split("/")
        require(not name.startswith("/") and "\\" not in name and ":" not in name
                and all(part not in {"", ".", ".."} for part in parts)
                and not any(ord(ch) < 32 or ord(ch) == 127 for ch in name),
                f"Unsafe or noncanonical tracked path: {name}")
        require(entry["kind"] == "blob" and entry["mode"] in {"100644", "100755"},
                f"Unsupported tracked object kind or mode: {name}")
        directories.update("/".join(parts[:end]) for end in range(1, len(parts)))
    conflicts = sorted(files & directories)
    require(not conflicts, f"File/directory conflicts: {conflicts}")
    transforms = {
        "NFC": lambda value: unicodedata.normalize("NFC", value),
        "NFD": lambda value: unicodedata.normalize("NFD", value),
        "casefold": str.casefold,
        "NFD-casefold-NFD": lambda value: unicodedata.normalize(
            "NFD", unicodedata.normalize("NFD", value).casefold()),
    }
    collisions = {}
    for label, transform in transforms.items():
        groups = defaultdict(list)
        for path in sorted(files | directories):
            key = "/".join(transform(part) for part in path.split("/"))
            groups[key].append(path)
        collisions[label] = [{"comparison_key": key, "paths": paths}
                             for key, paths in groups.items() if len(paths) > 1]
    require(not any(collisions.values()), "Case/Unicode normalized tracked-path collision.")
    return {"status": "PASS", "tracked_regular_files": len(files),
            "implicit_directories": len(directories),
            "file_directory_conflicts": conflicts, "component_collisions": collisions,
            "unicode_database": unicodedata.unidata_version,
            "scope": "Listed names and modes; not a claim of portability to all filesystems."}


def recorded_command(command: list[str], cwd: Path, environment: dict) -> dict:
    started = now()
    completed = run(command, cwd=cwd, environment=environment)
    parsed = None
    if completed.returncode == 0:
        try:
            parsed = json.loads(completed.stdout)
        except (ValueError, UnicodeDecodeError):
            pass
    return {"command": command, "cwd": str(cwd), "started_at_utc": started,
            "finished_at_utc": now(), "returncode": completed.returncode,
            "stdout_utf8": completed.stdout.decode(errors="replace"),
            "stderr_utf8": completed.stderr.decode(errors="replace"),
            "stdout_sha256": sha(completed.stdout), "stderr_sha256": sha(completed.stderr),
            "parsed_stdout": parsed}


def collection_checks(args: argparse.Namespace, destination: Path, report: dict) -> None:
    env = dict(ENV)
    if args.dependencies:
        dependencies = args.dependencies.resolve()
        require(dependencies.is_dir() and not dependencies.is_relative_to(destination),
                "Dependencies must be an existing directory outside the clone.")
        env["PYTHONPATH"] = str(dependencies)
    requirements_path = destination / "requirements-verification.txt"
    expected = {}
    for line in requirements_path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = re.fullmatch(r"([A-Za-z0-9_.-]+)==([A-Za-z0-9_.+-]+)", line)
        require(match is not None, "Every verification dependency must be exactly version-pinned.")
        require(match[1] not in expected, "Duplicate requirement pin.")
        expected[match[1]] = match[2]
    metadata_code = ("import importlib.metadata as m,json,sys;"
                     "print(json.dumps({name:m.version(name) for name in sys.argv[1:]}))")
    dependency_command = [sys.executable, "-B", "-c", metadata_code, *expected]
    dependency_run = recorded_command(dependency_command, destination, env)
    report["dependencies"] = {"requirements_sha256": sha(requirements_path.read_bytes()),
                              "expected_versions": expected, "probe": dependency_run,
                              "dependency_directory": str(args.dependencies.resolve()) if args.dependencies else None}
    require(dependency_run["returncode"] == 0 and dependency_run["parsed_stdout"] == expected,
            "Installed collection verification dependencies differ from the public version pins.")
    output = args.artifacts.resolve()
    output.mkdir(parents=True)
    checks = [
        ("catalog", [sys.executable, "-B", "scripts/catalog.py", "--check"]),
        ("collection", [sys.executable, "-B", "scripts/verify_collection.py"]),
        ("emilia", [sys.executable, "-B", "scripts/verify_emilia.py", "--out", str(output / "emilia")]),
    ]
    report["current_collection_checks"] = {}
    for label, command in checks:
        result = recorded_command(command, destination, env)
        report["current_collection_checks"][label] = result
        require(result["returncode"] == 0 and isinstance(result["parsed_stdout"], dict)
                and result["parsed_stdout"].get("status") == "PASS",
                f"Current public {label} validator failed.")
    freeze_result = json.loads((output / "emilia/freeze.json").read_text(encoding="utf-8"))
    inspection_result = json.loads((output / "emilia/archive-inspection.json").read_text(encoding="utf-8"))
    report["current_freeze_binding_result"] = freeze_result
    report["current_archive_inspection_summary"] = inspection_result["summary"]
    require(freeze_result.get("status") == "PASS" and freeze_result.get("all_byte_and_binding_checks_passed") is True
            and len(freeze_result.get("checks", {})) == 11 and all(freeze_result["checks"].values())
            and len(freeze_result.get("additional_checks", {})) == 3 and all(freeze_result["additional_checks"].values())
            and freeze_result.get("wexp_or_emilia_implementation_executed") is False,
            "Current freeze verifier did not pass the expected 11 binding and 3 additional checks.")
    require(inspection_result["summary"]["structural_inspection_passed"] is True,
            "Current archive inspector did not pass its declared checks.")
    report["auxiliary_artifact_identities"] = [
        {"path": path.relative_to(output).as_posix(), "bytes": path.stat().st_size,
         "sha256": sha(path.read_bytes())} for path in sorted(output.rglob("*")) if path.is_file()
    ]


def execute(args: argparse.Namespace, report: dict) -> None:
    destination = args.destination.resolve()
    archive_data = args.archive.read_bytes()
    require((len(archive_data), sha(archive_data)) == (200140, ZIP_SHA), "Archive public SHA-256 pin mismatch.")
    report["archive"] = {"path": str(args.archive.resolve()), "bytes": len(archive_data), "sha256": sha(archive_data),
                         "expected_sha256_source": "https://github.com/WEXP-dev/wexp-interop/blob/4075939139d56b40e6e08788959de169559919af/PUBLICATION-METADATA.yaml"}
    source_path = Path(args.repository)
    if source_path.is_file():
        report["source_carrier"] = {"kind": "Git bundle", "path": str(source_path.resolve()),
                                    "bytes": source_path.stat().st_size, "sha256": sha(source_path.read_bytes())}
    clone_command = GIT + ["clone", "--no-local", "--no-checkout", args.repository, str(destination)]
    clone_started = now()
    cloned = run(clone_command)
    report["clone"] = {"command": clone_command, "started_at_utc": clone_started,
                       "finished_at_utc": now(), "returncode": cloned.returncode,
                       "stdout_utf8": cloned.stdout.decode(errors="replace"), "stderr_utf8": cloned.stderr.decode(errors="replace"),
                       "git_transport_clone": True, "worktree_copied": False,
                       "local_object_hardlink_reuse": False}
    require(cloned.returncode == 0, "Git clone failed.")
    git(destination, "checkout", "--detach", args.commit)
    observed_commit = git(destination, "rev-parse", "HEAD").decode().strip()
    observed_parents = git(destination, "show", "-s", "--format=%P", "HEAD").decode().strip().split()
    require(observed_commit == args.commit, "Checked-out commit differs from the exact requested commit.")
    require(run(GIT + ["-C", str(destination), "merge-base", "--is-ancestor", args.base_commit, args.commit]).returncode == 0,
            "Candidate does not descend from the specified historical public base.")
    observed_tree = git(destination, "rev-parse", "HEAD^{tree}").decode().strip()
    require(observed_tree == args.expected_tree, "Public candidate tree differs from the supplied exact tree identity.")
    require(git(destination, "rev-parse", "--show-object-format").decode().strip() == "sha1", "This profile requires Git SHA-1 objects.")
    status_before = git(destination, "status", "--porcelain=v1", "--untracked-files=all").decode()
    require(not status_before, "The fresh clone has changes before verification.")
    report["git"] = {"version": git(destination, "--version").decode().strip(), "commit": observed_commit,
                     "parents": observed_parents, "tree": observed_tree,
                     "status_before": status_before, "configuration_for_all_git_commands": {
                         "core.autocrlf": "true", "core.filemode": "true", "core.attributesFile": os.devnull,
                         "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "GIT_ATTR_NOSYSTEM": "1"}}
    candidate_tree = tree(destination, args.commit)
    report["whole_tree_path_checks"] = path_checks(candidate_tree)
    checked_out_tree = []
    for name, entry in sorted(candidate_tree.items()):
        path = destination / name
        require(path.is_file() and not path.is_symlink(), f"Tracked regular file is missing or symlinked: {name}")
        data = path.read_bytes()
        expected_permissions = "0755" if entry["mode"] == "100755" else "0644"
        actual_permissions = f"{stat.S_IMODE(path.lstat().st_mode):04o}"
        row = {"path": name, "bytes": len(data), "sha256": sha(data), "git_blob": entry["oid"],
               "checkout_matches_git_blob": blob_oid(data) == entry["oid"], "git_mode": entry["mode"],
               "expected_checkout_permissions": expected_permissions,
               "observed_checkout_permissions": actual_permissions}
        checked_out_tree.append(row)
        require(row["checkout_matches_git_blob"] and expected_permissions == actual_permissions,
                f"Whole-tree checkout bytes or mode differ from the Git entry: {name}")
    report["whole_tree_checkout_checks"] = checked_out_tree
    require(git(destination, "remote", "get-url", "origin").decode().strip() == args.repository,
            "The fresh clone's recorded origin URL differs from the requested public repository.")
    base_tree = tree(destination, args.base_commit)
    payload_relative = f"{args.package_path}/payload"
    payload = destination / payload_relative
    expected_files = {}
    expected_directories = {""}
    with zipfile.ZipFile(io.BytesIO(archive_data)) as archive:
        require(archive.testzip() is None, "ZIP CRC failure.")
        for member in archive.infolist():
            parts = PurePosixPath(member.filename).parts
            require(parts[0] == ZIP_ROOT, "ZIP container path differs.")
            relative = PurePosixPath(*parts[1:]).as_posix() if len(parts) > 1 else ""
            mode = member.external_attr >> 16
            if member.is_dir():
                require(stat.S_ISDIR(mode), "ZIP directory has wrong Unix type.")
                expected_directories.add(relative)
            else:
                require(stat.S_ISREG(mode) and relative not in expected_files, "ZIP regular-file type or uniqueness failure.")
                expected_files[relative] = {"data": archive.read(member), "permissions": stat.S_IMODE(mode)}
    require(len(expected_files) == 68, "Unexpected regular-file count.")
    actual_files = set()
    actual_directories = {""}
    for path in payload.rglob("*"):
        relative = path.relative_to(payload).as_posix()
        entry_mode = path.lstat().st_mode
        require(not stat.S_ISLNK(entry_mode), f"Symlink found in clone: {relative}")
        if stat.S_ISREG(entry_mode):
            actual_files.add(relative)
        elif stat.S_ISDIR(entry_mode):
            actual_directories.add(relative)
        else:
            raise RuntimeError(f"Special filesystem entry: {relative}")
    require(actual_files == set(expected_files), "Clone payload regular-file set differs from ZIP.")
    require(actual_directories == expected_directories, "Clone payload directory set differs from ZIP.")
    tree_payload = {p.removeprefix(payload_relative + "/"): entry for p, entry in candidate_tree.items() if p.startswith(payload_relative + "/")}
    require(set(tree_payload) == set(expected_files), "Git payload file set differs from ZIP.")
    file_checks = []
    for relative, expected in sorted(expected_files.items()):
        checkout = payload / relative
        data = checkout.read_bytes()
        expected_git_mode = "100755" if expected["permissions"] & 0o111 else "100644"
        expected_posix = 0o755 if expected_git_mode == "100755" else 0o644
        observed_posix = stat.S_IMODE(checkout.lstat().st_mode)
        observed_tree = tree_payload[relative]
        row = {"path": relative, "archive_bytes": len(expected["data"]), "archive_sha256": sha(expected["data"]),
               "checkout_bytes": len(data), "checkout_sha256": sha(data), "bytes_equal": data == expected["data"],
               "archive_permissions": f"{expected['permissions']:04o}", "expected_git_mode": expected_git_mode,
               "observed_git_mode": observed_tree["mode"], "expected_git_blob": blob_oid(expected["data"]),
               "observed_git_blob": observed_tree["oid"], "expected_checkout_permissions": f"{expected_posix:04o}",
               "observed_checkout_permissions": f"{observed_posix:04o}",
               "archive_to_git_mode_projection_changes_permissions": expected["permissions"] != expected_posix,
               "git_mode_matches": observed_tree["kind"] == "blob" and observed_tree["mode"] == expected_git_mode,
               "git_blob_matches": observed_tree["oid"] == blob_oid(expected["data"]),
               "checkout_permissions_match": observed_posix == expected_posix}
        file_checks.append(row)
    report["payload_file_checks"] = file_checks
    require(all(r["bytes_equal"] and r["git_mode_matches"] and r["git_blob_matches"] and r["checkout_permissions_match"] for r in file_checks),
            "Payload bytes, Git mode/blob, or POSIX permissions mismatch.")
    directory_checks = [{"path": relative or ".", "expected_checkout_permissions": "0755",
                         "observed_checkout_permissions": f"{stat.S_IMODE((payload / relative).lstat().st_mode):04o}"}
                        for relative in sorted(expected_directories)]
    report["payload_directory_checks"] = directory_checks
    require(all(row["observed_checkout_permissions"] == "0755" for row in directory_checks), "Directory permissions mismatch under umask 022.")
    attributes = git(destination, "check-attr", "-z", "--stdin", "text",
                     data=b"\0".join(f"{payload_relative}/{p}".encode() for p in sorted(expected_files)) + b"\0")
    parts = attributes.split(b"\0")[:-1]
    require(len(parts) == len(expected_files) * 3, "Unexpected check-attr result.")
    attr_checks = [{"path": parts[i].decode(), "attribute": parts[i+1].decode(), "value": parts[i+2].decode()}
                   for i in range(0, len(parts), 3)]
    report["payload_text_attributes"] = attr_checks
    require(all(r["attribute"] == "text" and r["value"] == "unset" for r in attr_checks), "A payload path lacks -text.")
    history_root = f"{args.package_path}/publication-history/{args.base_commit}"
    preserved = []
    for old_path, original in sorted(base_tree.items()):
        new_path = f"{history_root}/{old_path}" if old_path in HISTORY_FILES else f"{payload_relative}/{old_path}"
        checkout = destination / new_path
        expected_data = git(destination, "cat-file", "blob", original["oid"])
        current = candidate_tree.get(new_path)
        preserved.append({"source_path": old_path, "destination_path": new_path,
                          "git_entry_identical": current == original,
                          "checkout_bytes_identical": checkout.is_file() and checkout.read_bytes() == expected_data})
    report["prior_main_preservation_checks"] = preserved
    require(len(preserved) == 69 and all(r["git_entry_identical"] and r["checkout_bytes_identical"] for r in preserved), "A prior main file changed or was lost.")
    source_archive = destination / args.package_path / "source-archive" / ZIP_NAME
    source_freeze = destination / args.package_path / "source-archive" / FREEZE_NAME
    require(source_archive.read_bytes() == archive_data, "Cloned authoritative archive differs.")
    require((source_freeze.stat().st_size, sha(source_freeze.read_bytes())) == (2260, FREEZE_SHA), "Cloned freeze differs.")
    report["cloned_source_artifacts"] = {"archive_sha256": sha(source_archive.read_bytes()),
                                         "freeze_sha256": sha(source_freeze.read_bytes()), "byte_identities_match": True}
    verifier = payload / "reproduction/verify_final.py"
    require(sha(verifier.read_bytes()) == VERIFIER_SHA, "Archived verifier identity differs; it was not executed.")
    command = [sys.executable, "-I", "-B", str(verifier), "--manifest-sha256", MANIFEST_SHA]
    verifier_started = now()
    completed = run(command, cwd=payload)
    verifier_result = json.loads(completed.stdout) if completed.returncode == 0 else None
    report["verifier"] = {"path": str(verifier), "sha256": sha(verifier.read_bytes()), "command": command,
                          "cwd": str(payload), "started_at_utc": verifier_started, "finished_at_utc": now(),
                          "returncode": completed.returncode, "stdout_utf8": completed.stdout.decode(errors="replace"),
                          "stderr_utf8": completed.stderr.decode(errors="replace"), "stdout_sha256": sha(completed.stdout),
                          "stderr_sha256": sha(completed.stderr), "parsed_stdout": verifier_result}
    require(completed.returncode == 0 and verifier_result["status"] == "PASS" and
            verifier_result["payload_entries_verified"] == 67 and verifier_result["frozen_identities_verified"] == 15 and
            verifier_result["terminal_branch"] == "A — EXPLICIT BRIDGE REQUIRED" and
            verifier_result["implementation_execution_performed"] is False, "Archived verifier failed or returned an unexpected scope.")
    collection_checks(args, destination, report)
    status_after = git(destination, "status", "--porcelain=v1", "--untracked-files=all").decode()
    require(not status_after, "Verifier or other checks changed the clone.")
    report["git"]["status_after"] = status_after
    report["summary"] = {"payload_regular_file_bytes_match": 68, "payload_git_modes_and_blobs_match": 68,
                         "payload_posix_permissions_match_under_recorded_umask": 68,
                         "payload_directories_checked_including_root": len(directory_checks),
                         "payload_paths_with_text_unset": len(attr_checks), "prior_main_files_preserved": len(preserved),
                         "declared_archive_to_git_permission_changes": sum(r["archive_to_git_mode_projection_changes_permissions"] for r in file_checks),
                         "original_verifier_status": "PASS", "fresh_clone_checked": True,
                         "whole_tracked_tree_paths_checked": len(candidate_tree),
                         "whole_tracked_tree_checkout_bytes_and_modes_checked": len(checked_out_tree),
                         "current_catalog_check": "PASS", "current_collection_check": "PASS",
                         "current_emilia_archive_and_freeze_check": "PASS",
                         "new_surface_local_links_checked": report["current_collection_checks"]["collection"]["parsed_stdout"]["local_links_checked"],
                         "remote_link_availability_checked_by_this_driver": False,
                         "wexp_or_emilia_implementation_executed": False, "new_interoperability_established": False}


def public_summary(report: dict) -> dict:
    """A non-circular, path-free result that can live in a separate commit."""
    result = {"schema": "wexp-public-migration-verification-001", "status": report["status"],
              "repository": report["repository_input"], "tested_commit": report["requested_commit"],
              "tested_tree": report.get("git", {}).get("tree"),
              "historical_base_commit": report["historical_base_commit"],
              "started_at_utc": report["started_at_utc"], "finished_at_utc": report["finished_at_utc"],
              "verification_script_sha256": report["verification_script_sha256"],
              "input_archive": {"name": ZIP_NAME, "bytes": 200140, "sha256": ZIP_SHA,
                                "expected_sha256_source": "https://github.com/WEXP-dev/wexp-interop/blob/4075939139d56b40e6e08788959de169559919af/PUBLICATION-METADATA.yaml"},
              "checks": report.get("summary"),
              "environment": {"python": report["environment"]["python"],
                              "platform": report["environment"]["platform"], "child_process_umask": "0022",
                              "git": report.get("git", {}).get("version"),
                              "git_configuration": report.get("git", {}).get("configuration_for_all_git_commands"),
                              "verification_dependency_versions": report.get("dependencies", {}).get("expected_versions")},
              "limitations": report["limitations"],
              "full_result_sha256": report["full_result_sha256"],
              "public_detail_sha256": report["public_detail_sha256"],
              "carrier_rule": "Publish this observation in a later, separate commit or PR record identifying tested_commit. It does not claim to verify its own carrier commit."}
    if report.get("error"):
        result["error"] = report["error"]
    return result


def normalized_public_detail(args: argparse.Namespace, report: dict) -> dict:
    """Normalize execution-local paths without dropping checks or input identities.

    stdout/stderr byte hashes continue to describe the raw retained execution
    streams; their displayed text undergoes the same declared path replacement.
    No emails, account captures or private research bytes enter this driver.
    """
    replacements = [
        (str(args.archive.resolve()), "${REFERENCE_ARCHIVE}/" + ZIP_NAME),
        (str(args.destination.resolve()), "${CHECKOUT}"),
        (str(args.artifacts.resolve()), "${AUXILIARY_OUTPUT}"),
        (str(args.report.resolve()), "${RAW_RESULT}"),
        (str(Path(sys.executable).resolve()), "${PYTHON}"),
        (sys.executable, "${PYTHON}"),
    ]
    if args.dependencies:
        replacements.append((str(args.dependencies.resolve()), "${VERIFICATION_DEPENDENCIES}"))
    replacements.sort(key=lambda pair: -len(pair[0]))

    def convert(value):
        if isinstance(value, str):
            for original, replacement in replacements:
                value = value.replace(original, replacement)
            return value
        if isinstance(value, list):
            return [convert(item) for item in value]
        if isinstance(value, dict):
            return {key: convert(item) for key, item in value.items()}
        return value

    public = convert(report)
    public["public_path_normalization"] = {
        "schema": "execution-path-normalization-001",
        "operation": "String replacement of local execution paths only; no check, result, byte identity or timestamp removed.",
        "variables": ["REFERENCE_ARCHIVE", "CHECKOUT", "AUXILIARY_OUTPUT", "RAW_RESULT", "PYTHON", "VERIFICATION_DEPENDENCIES"],
        "stream_hashes": "stdout_sha256 and stderr_sha256 identify the raw retained streams, before displayed execution paths are normalized.",
        "private_raw_result_sha256": report["full_result_sha256"],
        "evidence_boundary": "The public detail carries all listed checks. Its raw counterpart contains only equivalent unnormalized execution paths, not additional authority or private evidence."
    }
    return public


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", default="https://github.com/WEXP-dev/wexp-interop.git",
                        choices=["https://github.com/WEXP-dev/wexp-interop.git"], help="Public repository URL; no local repository or bundle")
    parser.add_argument("--commit", required=True)
    parser.add_argument("--expected-tree", required=True)
    parser.add_argument("--base-commit", default=BASE)
    parser.add_argument("--package-path", default=PACKAGE)
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--destination", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--artifacts", required=True, type=Path, help="new auxiliary result directory outside clone")
    parser.add_argument("--public-summary", required=True, type=Path, help="new public-safe result JSON outside clone")
    parser.add_argument("--public-detail", required=True, type=Path, help="new path-normalized full detail JSON outside clone")
    parser.add_argument("--dependencies", type=Path, help="explicit optional dependency target, recorded separately from the clone")
    args = parser.parse_args()
    if os.name != "posix":
        parser.error("This POSIX permission profile requires a POSIX host.")
    if not all(re.fullmatch(r"[0-9a-f]{40}", value) for value in [args.commit, args.base_commit, args.expected_tree]):
        parser.error("Exact SHA-1 Git commit identities are required.")
    if any(path.exists() for path in [args.destination, args.report, args.artifacts, args.public_summary, args.public_detail]):
        parser.error("Destination, report, artifacts and public summary must be new; existing runs are never overwritten.")
    if any(path.resolve().is_relative_to(args.destination.resolve()) for path in [args.report, args.artifacts, args.public_summary, args.public_detail]):
        parser.error("All reports must be outside the clone.")
    report = {"schema": "wexp-public-migration-verification-detail-001", "status": "FAIL", "started_at_utc": now(),
              "verification_script_sha256": sha(Path(__file__).read_bytes()), "repository_input": args.repository,
              "requested_commit": args.commit, "expected_tree": args.expected_tree, "historical_base_commit": args.base_commit,
              "destination": str(args.destination.resolve()), "package_path": args.package_path,
              "environment": {"python": sys.version, "platform": platform.platform(),
                              "child_process_umask": "0022", "filesystem_permissions_scope": "actual POSIX stat, separately from Git modes"},
              "public_pr_status_checked": False, "release_status_checked": False,
              "limitations": ["This result applies to the exact commit tested; a later migration HEAD needs its own clone check.",
                              "Git clone preserves the declared file bytes and executable-bit projection, not every ZIP metadata field.",
                              "The original verifier checks archived recorded bytes and relationships, not a new implementation execution or interoperability.",
                              "The selected SHA-256 source is public and dated after the historical release; this check does not establish continuous asset non-replacement.",
                              "The freeze is an unsigned inventory; successful binding checks are not a signature or independent timestamp.",
                              "Collection validation checks the stated schema, catalog, manifests and local link targets, not every historical claim or remote link availability.",
                              "This run is in the publisher-controlled environment; it is not an independent external reproduction."]}
    try:
        execute(args, report)
        report["status"] = "PASS"
    except (OSError, RuntimeError, ValueError, KeyError, subprocess.SubprocessError, zipfile.BadZipFile) as exc:
        report["error"] = str(exc)
    report["finished_at_utc"] = now()
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report["full_result_sha256"] = sha(args.report.read_bytes())
    args.public_detail.parent.mkdir(parents=True, exist_ok=True)
    args.public_detail.write_text(json.dumps(normalized_public_detail(args, report), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report["public_detail_sha256"] = sha(args.public_detail.read_bytes())
    args.public_summary.parent.mkdir(parents=True, exist_ok=True)
    args.public_summary.write_text(json.dumps(public_summary(report), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "report": str(args.report.resolve()),
                      "commit": args.commit, "summary": report.get("summary"), "error": report.get("error")}, ensure_ascii=False))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
