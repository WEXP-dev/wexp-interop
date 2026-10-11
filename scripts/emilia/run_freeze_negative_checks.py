#!/usr/bin/env python3
"""Run bounded negative controls for verify_freeze_bindings.py.

Stores exact mutated inputs, commands, stdout/stderr, individual verifier
reports and an aggregate result in a new directory. No historical input is
changed. The source pins must be supplied independently, as in the verifier.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import io
import json
from pathlib import Path
import platform
import subprocess
import sys
import zipfile


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def replace_once(data, old, new):
    if data.count(old) != 1:
        raise ValueError(f"mutation source is not unique: {old!r}")
    return data.replace(old, new, 1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verifier", type=Path, required=True)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--freeze", type=Path, required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--metadata-sha256", required=True)
    parser.add_argument("--metadata-git-blob", required=True)
    parser.add_argument("--metadata-source-url", required=True)
    parser.add_argument("--manifest-member", required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=False)
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    archive_bytes = args.archive.read_bytes()
    freeze_bytes = args.freeze.read_bytes()
    metadata_bytes = args.metadata.read_bytes()

    changed_manifest_zip = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as source, zipfile.ZipFile(changed_manifest_zip, "w") as target:
        for member in source.infolist():
            data = source.read(member)
            if member.orig_filename == args.manifest_member:
                # Change a digest character while retaining a valid manifest line,
                # member name, entry count, and uncompressed manifest size.
                data = (b"1" if data[:1] == b"0" else b"0") + data[1:]
            target.writestr(member, data)

    false_inventory = replace_once(freeze_bytes, b"candidate_archive: " + args.archive.name.encode() + b"\n",
                                   b"candidate_archive: WRONG-PUBLICATION-CANDIDATE.zip\n")
    false_inventory = replace_once(false_inventory, b"archive_bytes: 200140\n", b"archive_bytes: 200141\n")
    false_inventory = replace_once(false_inventory, b"payload_entries_verified: 67\n", b"payload_entries_verified: 68\n")
    correction_line = (b"  corrected_root_manifest_sha256: "
                       b"4172c2d0d9f4cfaddaa4036a7d92e53d1ee6c2c290654daedaa5806e5281ad6a\n")
    # Hex letters keep this an unquoted YAML string. An all-zero scalar is an
    # integer in SafeLoader and exercises the type guard rather than the digest
    # comparison. The first observed run with that fixture is retained in 001.
    false_correction = replace_once(freeze_bytes, correction_line,
                                    b"  corrected_root_manifest_sha256: " + b"a" * 64 + b"\n")
    cases = [
        {"id": "N01-zip-extra-byte", "mutation": "Append LF to an otherwise readable ZIP.",
         "changed": {"archive": archive_bytes + b"\n"}, "status": "FAIL",
         "failed": ["archive_size_binding_matches_bytes", "archive_sha256_binding_matches_bytes"]},
        {"id": "N02-root-manifest-digest-change", "mutation": "Rebuild ZIP with one root-manifest digest character changed; valid manifest syntax and same uncompressed manifest size/count.",
         "changed": {"archive": changed_manifest_zip.getvalue()}, "status": "FAIL",
         "failed": ["archive_sha256_binding_matches_bytes", "manifest_sha256_binding_matches_bytes"]},
        {"id": "N03-false-name-size-count", "mutation": "Change freeze's declared archive name, size and payload count while retaining a syntactically valid YAML inventory.",
         "changed": {"freeze": false_inventory}, "status": "FAIL",
         "failed": ["archive_name_matches_metadata", "archive_size_binding_matches_bytes",
                    "manifest_nonempty_entry_count_matches_declared"]},
        {"id": "N04-false-correction", "mutation": "Set corrected manifest digest to a well-formed but wrong SHA-256.",
         "changed": {"freeze": false_correction}, "status": "FAIL",
         "failed": ["corrected_manifest_pin_matches_binding"]},
        {"id": "N05-malformed-yaml", "mutation": "Append an unclosed YAML flow sequence.",
         "changed": {"freeze": freeze_bytes + b"malformed: [\n"}, "status": "ERROR", "failed": [],
         "error_contains": "expected the node content"},
        {"id": "N06-duplicate-yaml-key", "mutation": "Append a second archive_sha256 key; a permissive last-key-wins loader would collapse it.",
         "changed": {"freeze": freeze_bytes + b"archive_sha256: " + b"0" * 64 + b"\n"},
         "status": "ERROR", "failed": [], "error_contains": "duplicate mapping key"},
        {"id": "N07-metadata-pin-change", "mutation": "Append whitespace to metadata without changing its independently supplied byte pins.",
         "changed": {"metadata": metadata_bytes + b"\n"}, "status": "ERROR", "failed": [],
         "error_contains": "metadata SHA-256 pin mismatch"},
        {"id": "N08-nested-manifest-selection", "mutation": "Select an existing nested manifest instead of the root manifest.",
         "changed": {}, "status": "ERROR", "failed": [],
         "manifest_member": "WEXP-EMILIA-INTEROP-001-PUBLICATION-CANDIDATE/source/original/WEXP-EMILIA-INTEROP-001/MANIFEST.sha256",
         "error_contains": "declared root manifest"},
    ]
    observations = []
    source_paths = {"archive": args.archive.resolve(), "freeze": args.freeze.resolve(),
                    "metadata": args.metadata.resolve()}
    for case in cases:
        case_dir = args.out_dir / case["id"]
        case_dir.mkdir()
        paths = dict(source_paths)
        mutations = []
        for role, data in case["changed"].items():
            path = case_dir / source_paths[role].name
            path.write_bytes(data)
            paths[role] = path.resolve()
            mutations.append({"role": role, "path": str(path.resolve()), "bytes": len(data), "sha256": sha256(data)})
        result_path = (case_dir / "verification.json").resolve()
        command = [sys.executable, "-B", str(args.verifier.resolve()),
                   "--archive", str(paths["archive"]), "--freeze", str(paths["freeze"]),
                   "--metadata", str(paths["metadata"]), "--metadata-sha256", args.metadata_sha256,
                   "--metadata-git-blob", args.metadata_git_blob, "--metadata-source-url", args.metadata_source_url,
                   "--manifest-member", case.get("manifest_member", args.manifest_member), "--out", str(result_path)]
        completed = subprocess.run(command, capture_output=True, timeout=30)
        (case_dir / "stdout.txt").write_bytes(completed.stdout)
        (case_dir / "stderr.txt").write_bytes(completed.stderr)
        result = json.loads(result_path.read_bytes()) if result_path.exists() else {}
        matched = (completed.returncode == (1 if case["status"] == "FAIL" else 2)
                   and result.get("status") == case["status"]
                   and set(case["failed"]).issubset(result.get("failed_checks", []))
                   and case.get("error_contains", "") in result.get("error", {}).get("message", "")
                   and result.get("all_byte_and_binding_checks_passed") is False)
        observations.append({"id": case["id"], "mutation": case["mutation"],
                             "mutated_inputs": mutations, "command": command,
                             "expected": {"status": case["status"], "required_failed_checks": case["failed"],
                                          "error_contains": case.get("error_contains")},
                             "observed": {"returncode": completed.returncode, "status": result.get("status"),
                                          "failed_checks": result.get("failed_checks"), "error": result.get("error")},
                             "result_path": str(result_path),
                             "result_sha256": sha256(result_path.read_bytes()) if result_path.exists() else None,
                             "expected_rejection_observed": matched})
    report = {
        "schema": "emilia-freeze-bindings-negative-controls-001", "started_at_utc": started,
        "finished_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "command": [sys.executable, *sys.argv], "working_directory": str(Path.cwd()),
        "runtime": {"python": sys.version, "platform": platform.platform()},
        "suite_script_sha256": sha256(Path(__file__).read_bytes()),
        "verifier_script_sha256": sha256(args.verifier.read_bytes()),
        "original_input_identities": {role: {"path": str(path), "bytes": len(path.read_bytes()),
                                              "sha256": sha256(path.read_bytes())} for role, path in source_paths.items()},
        "cases": observations, "expected_rejections_observed": sum(case["expected_rejection_observed"] for case in observations),
        "cases_total": len(observations), "passed": all(case["expected_rejection_observed"] for case in observations),
        "limits": "These are bounded verifier rejection controls, not exhaustive parser testing, certification, or an interop implementation run.",
    }
    report_path = args.out_dir / "results.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"report": str(report_path.resolve()), "passed": report["passed"],
                      "expected_rejections_observed": report["expected_rejections_observed"],
                      "cases_total": len(observations)}))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
