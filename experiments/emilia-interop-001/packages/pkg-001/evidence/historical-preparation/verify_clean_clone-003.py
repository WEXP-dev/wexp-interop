#!/usr/bin/env python3
"""Verify EMILIA archive bytes, Git modes and verifier in a fresh Git clone.

The destination and report must not exist. Clone uses Git's transport with
--no-local; no worktree copying or object hardlink reuse is used. Only the
pinned archived verifier is executed, after all 68 payload files match.
"""

from __future__ import annotations

import argparse
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
ENV = {k: v for k, v in os.environ.items() if k not in {"PYTHONPATH", "PYTHONHOME"}}
ENV.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull, GIT_ATTR_NOSYSTEM="1",
           PYTHONDONTWRITEBYTECODE="1", PYTHONNOUSERSITE="1")
GIT = ["git", "-c", "core.autocrlf=true", "-c", "core.filemode=true", "-c", "core.attributesFile=" + os.devnull]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def blob_oid(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run(command: list[str], *, cwd: Path | None = None, data: bytes | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(command, cwd=cwd, input=data, env=ENV, capture_output=True,
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
    require(observed_parents == [args.base_commit], "Candidate parent differs from the specified public base.")
    require(git(destination, "rev-parse", "--show-object-format").decode().strip() == "sha1", "This profile requires Git SHA-1 objects.")
    status_before = git(destination, "status", "--porcelain=v1", "--untracked-files=all").decode()
    require(not status_before, "The fresh clone has changes before verification.")
    report["git"] = {"version": git(destination, "--version").decode().strip(), "commit": observed_commit,
                     "parents": observed_parents, "tree": git(destination, "rev-parse", "HEAD^{tree}").decode().strip(),
                     "status_before": status_before, "configuration_for_all_git_commands": {
                         "core.autocrlf": "true", "core.filemode": "true", "core.attributesFile": os.devnull,
                         "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "GIT_ATTR_NOSYSTEM": "1"}}
    candidate_tree = tree(destination, args.commit)
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
    source_archive = destination / args.package_path / "source-artifacts" / ZIP_NAME
    source_freeze = destination / args.package_path / "source-artifacts" / FREEZE_NAME
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
    status_after = git(destination, "status", "--porcelain=v1", "--untracked-files=all").decode()
    require(not status_after, "Verifier or other checks changed the clone.")
    report["git"]["status_after"] = status_after
    report["summary"] = {"payload_regular_file_bytes_match": 68, "payload_git_modes_and_blobs_match": 68,
                         "payload_posix_permissions_match_under_recorded_umask": 68,
                         "payload_directories_checked_including_root": len(directory_checks),
                         "payload_paths_with_text_unset": len(attr_checks), "prior_main_files_preserved": len(preserved),
                         "declared_archive_to_git_permission_changes": sum(r["archive_to_git_mode_projection_changes_permissions"] for r in file_checks),
                         "original_verifier_status": "PASS", "fresh_clone_checked": True,
                         "wexp_or_emilia_implementation_executed": False, "new_interoperability_established": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", required=True, help="Git URL, Git repository or self-contained bundle")
    parser.add_argument("--commit", required=True)
    parser.add_argument("--base-commit", default=BASE)
    parser.add_argument("--package-path", default=PACKAGE)
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--destination", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()
    if os.name != "posix":
        parser.error("This POSIX permission profile requires a POSIX host.")
    if not re.fullmatch(r"[0-9a-f]{40}", args.commit) or not re.fullmatch(r"[0-9a-f]{40}", args.base_commit):
        parser.error("Exact SHA-1 Git commit identities are required.")
    if args.destination.exists() or args.report.exists():
        parser.error("Destination and report must be new; existing runs are never overwritten.")
    if args.destination.resolve() in args.report.resolve().parents:
        parser.error("The report must be outside the clone.")
    report = {"schema": "emilia-clean-clone-verification-002", "status": "FAIL", "started_at_utc": now(),
              "verification_script_sha256": sha(Path(__file__).read_bytes()), "repository_input": args.repository,
              "requested_commit": args.commit, "requested_parent_commit": args.base_commit,
              "destination": str(args.destination.resolve()), "package_path": args.package_path,
              "environment": {"python": sys.version, "platform": platform.platform(),
                              "child_process_umask": "0022", "filesystem_permissions_scope": "actual POSIX stat, separately from Git modes"},
              "public_pr_status_checked": False, "release_status_checked": False,
              "limitations": ["This result applies to the exact commit tested; a later migration HEAD needs its own clone check.",
                              "Git clone preserves the declared file bytes and executable-bit projection, not every ZIP metadata field.",
                              "The original verifier checks archived recorded bytes and relationships, not a new implementation execution or interoperability.",
                              "The selected SHA-256 source is public and dated after the historical release; this check does not establish continuous asset non-replacement."]}
    try:
        execute(args, report)
        report["status"] = "PASS"
    except (OSError, RuntimeError, ValueError, KeyError, subprocess.SubprocessError, zipfile.BadZipFile) as exc:
        report["error"] = str(exc)
    report["finished_at_utc"] = now()
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "report": str(args.report.resolve()),
                      "commit": args.commit, "summary": report.get("summary"), "error": report.get("error")}, ensure_ascii=False))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
