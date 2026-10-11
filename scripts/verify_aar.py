#!/usr/bin/env python3
"""Read-only verification of the completed, bounded AAR public package.

SPDX-License-Identifier: MIT
No retained AAR implementation, producer, recipient, generator or controlled
world operation is executed. This verifies supplied evidence, not its truth.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import stat
import sys
import unicodedata
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PREPARATION_COMMIT = "70b4491a1ec8aab5af61f31510220067e3e5cfba"
PREPARATION_TREE = "feaec7ce219ba8aea944d3a8e8fcf0079f6932b9"
FREEZE_SHA256 = "ab13055e8d65601eabdf1cb463d1ec92b2dc1ed5868914fd9af8bcf4fc19138f"
INPUT_LOCK_SHA256 = "a00401b781968a9f5aeb21313d1fc37bcd4513c2f98bc1b2c868e7fcb0004af0"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def unique(pairs):
    value = {}
    for key, item in pairs:
        require(key not in value, "duplicate JSON member: " + key)
        value[key] = item
    return value


def finite(value):
    result = float(value)
    require(math.isfinite(result), "non-finite JSON number")
    return result


def load(path):
    return json.loads(path.read_bytes().decode("utf-8"), object_pairs_hook=unique,
                      parse_float=finite,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError("non-finite JSON constant")))


def safe(root, relative):
    require(isinstance(relative, str) and relative and not relative.startswith("/") and
            "\\" not in relative and all(p not in {"", ".", ".."} for p in relative.split("/")),
            "noncanonical file path")
    result = root / relative
    require(result.resolve().is_relative_to(root.resolve()), "file escapes root")
    for part in [result, *result.parents]:
        if part == root:
            break
        require(not part.is_symlink(), "symlink in file path")
    return result


def identity(root, entry):
    path = safe(root, entry["path"])
    require(path.is_file(), "missing file: " + entry["path"])
    raw = path.read_bytes()
    require(type(entry["bytes"]) is int and len(raw) == entry["bytes"] and sha(raw) == entry["sha256"],
            "file identity differs: " + entry["path"])
    if "git_blob_sha1" in entry:
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        require(blob == entry["git_blob_sha1"], "Git blob identity differs: " + entry["path"])
    return raw


def inventory(root):
    result = {}
    for path in root.rglob("*"):
        require(not path.is_symlink(), "symlink in inventory")
        if path.is_file():
            require(stat.S_ISREG(path.stat().st_mode), "non-regular inventory entry")
            result[path.relative_to(root).as_posix()] = path
    return result


def check_collisions(paths):
    names = set()
    for path in paths:
        pieces = path.split("/")
        names.update("/".join(pieces[:i]) for i in range(1, len(pieces) + 1))
    for normalize in [lambda s: s.casefold(),
                      lambda s: unicodedata.normalize("NFC", s).casefold(),
                      lambda s: unicodedata.normalize("NFD", s).casefold()]:
        seen = {}
        for name in names:
            normalized = normalize(name)
            require(normalized not in seen or seen[normalized] == name, "case/Unicode path collision")
            seen[normalized] = name


def check_package_manifest(package):
    manifest = package / "PACKAGE-MANIFEST.sha256"
    rows = {}
    for line in manifest.read_text().splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        require(match is not None, "malformed outer package manifest")
        digest, relative = match.groups()
        require(relative != manifest.name and relative not in rows, "duplicate/self manifest entry")
        require(sha(safe(package, relative).read_bytes()) == digest, "outer manifest hash differs")
        rows[relative] = digest
    require(set(rows) == set(inventory(package)) - {manifest.name}, "outer package manifest inventory differs")
    return len(rows)


def import_helper(payload, name):
    spec = importlib.util.spec_from_file_location(name, payload / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def execute_package(package, record=None):
    record = load(package / "record.json") if record is None else record
    require((record["experiment_id"], record["package_id"]) == ("wimse-aar-02-interop-001", "pkg-001"),
            "this bounded verifier has no binding for that package")
    require(record["verification"]["profile"] == "aar-pilot-v1", "unexpected verification profile")
    payload = safe(package, record["payload"]["path"])
    require(sha((payload / "pre-run/FREEZE.json").read_bytes()) == FREEZE_SHA256, "published pre-run freeze changed")
    require(sha((payload / "pre-run/INPUTS.lock.json").read_bytes()) == INPUT_LOCK_SHA256, "published input lock changed")
    frozen = load(payload / "pre-run/INPUTS.lock.json")["files"]
    for entry in frozen:
        identity(payload, entry)
    # Import only the newly published data verifiers after their exact pre-run
    # source bytes have matched the immutable input lock. No runtime imports.
    comparator = import_helper(payload, "compare_results")
    input_verifier = import_helper(payload, "verify_inputs")
    inputs = input_verifier.verify(False)
    comparison = comparator.compare_run(payload / "results/public-run-001")
    same = comparator.same_types_and_values
    final = load(package / "evidence/FINAL-FREEZE.json")
    require(final["format"] == "wexp-aar-final-package-freeze/0.1.0", "unknown final freeze format")
    require(final["preparation_commit"] == PREPARATION_COMMIT and
            final["preparation_tree"] == PREPARATION_TREE and final["preparation_freeze_sha256"] == FREEZE_SHA256,
            "final/preparation binding differs")
    entries = final["payload_files"]
    paths = [entry["path"] for entry in entries]
    require(len(paths) == len(set(paths)), "duplicate final payload entry")
    actual_files = inventory(payload)
    require(set(paths) == set(actual_files) and len(paths) == record["payload"]["regular_files"],
            "final payload inventory differs")
    check_collisions(paths)
    for entry in entries:
        identity(payload, entry)
        require(entry["git_mode"] == "100644" and not (actual_files[entry["path"]].stat().st_mode & 0o111),
                "payload executable-bit projection differs")
    artifact = record["artifact"]
    require(all(same(final["archive"][key], artifact[key]) for key in ["path", "bytes", "sha256"]),
            "card/archive freeze binding differs")
    raw_archive = identity(package, final["archive"])
    require(hashlib.md5(raw_archive).hexdigest() == final["archive"]["md5"], "archive MD5 inventory differs")
    preparation = final["supporting_preparation_file"]
    require(preparation["path"] == "PREPARATION.md", "standalone parent preparation file is missing")
    identity(package, preparation)
    require(preparation["git_mode"] == "100644" and not ((package / "PREPARATION.md").stat().st_mode & 0o111),
            "supporting preparation executable-bit projection differs")
    zip_paths = {"PREPARATION.md": package / "PREPARATION.md"}
    zip_paths.update({"payload/" + name: path for name, path in actual_files.items()})
    check_collisions(zip_paths)
    archive = safe(package, artifact["path"])
    with zipfile.ZipFile(archive) as stream:
        members = stream.infolist()
        names = [member.filename for member in members]
        require(len(names) == len(set(names)) and set(names) == set(zip_paths), "ZIP/payload/supporting-preparation inventory differs")
        require(names == sorted(names), "ZIP member order differs from its declared sorted construction")
        for member in members:
            safe(package, member.filename)
            mode = member.external_attr >> 16
            require(not member.is_dir() and stat.S_ISREG(mode) and stat.S_IMODE(mode) == 0o644,
                    "unexpected ZIP entry type/mode")
            require(member.create_system == 3 and not (member.flag_bits & 1) and not member.extra and not member.comment,
                    "unexpected ZIP metadata")
            require(member.date_time == tuple(final["zip_construction"]["fixed_member_timestamp"]),
                    "ZIP construction timestamp differs")
            require(stream.read(member) == zip_paths[member.filename].read_bytes(), "ZIP/package file bytes differ")

    export = load(payload / "run-evidence/EXPORT.json")
    for entry in export["entries"]:
        require(entry["transformation"] == "none", "run export has an undeclared transformation")
        identity(payload, entry)
    require(len(export["entries"]) == 31, "run export accounting differs")
    journal = payload / "run-evidence/public-run-001"
    start, finish = load(journal / "EXECUTION-START.json"), load(journal / "EXECUTION-FINISH.json")
    driver_sha = sha((payload / "run-evidence/run_public_replay.py").read_bytes())
    for observation in [start, finish]:
        require(observation["preparation_commit"] == PREPARATION_COMMIT and
                observation["preparation_tree"] == PREPARATION_TREE and
                observation["freeze_sha256"] == FREEZE_SHA256 and observation["driver_sha256"] == driver_sha,
                "journal input/driver binding differs")
    require(start["clone_worktree_clean_before_execution"] is True and finish["clone_worktree_clean_after_execution"] is True,
            "run did not record a clean clone")
    require(finish["pilot_implementation_execution_performed"] is True and
            same(finish["runner_exit_code"], 0) and same(finish["comparator_exit_code"], 0),
            "journal execution completion differs")
    for label in ["input-verification", "retained-pilot", "strict-comparison"]:
        command = load(journal / (label + ".command.json"))
        began = load(journal / (label + ".start.json"))
        require(same(command["command"], began["command"]) and command["started_at_utc"] == began["started_at_utc"] and
                command["working_directory"] == began["working_directory"] and same(command["exit_code"], 0),
                "command journal binding differs")
        for suffix in ["stdout", "stderr"]:
            require(sha((journal / (label + "." + suffix)).read_bytes()) == command[suffix + "_sha256"],
                    "command stream digest differs")
    require(start["input_verification_stdout_sha256"] == sha((journal / "input-verification.stdout").read_bytes()),
            "pre-execution input observation differs")

    results = payload / "results/public-run-001"
    semantic = load(results / "semantic-results.json")
    cases = []
    for group in ["aar01", "aar02", "local", "compatibility"]:
        cases.extend(load(results / (group + "-results.json")))
    require(len(cases) == 130 and [row["id"] for row in cases] == [row["id"] for row in semantic["cases"]],
            "complete result/case projection differs")
    for row, projected in zip(cases, semantic["cases"]):
        require(same(row["wexp_recipient"]["decision"], row["native_baseline"]["decision"]),
                "strict WEXP/native decision parity differs")
        derived = {"id": row["id"], "source_sha256": row["source_sha256"], "policy_sha256": row["policy_sha256"],
                   "checks": row["checks"], "native": row["producer_output"]["native"],
                   "mapping_status": row["producer_output"]["status"], "decision": row["wexp_recipient"]["decision"]}
        require(same(derived, projected) and row["passed"] is True, "full case/result projection differs")
    worlds_record = load(results / "trusted-producer-results.json")
    worlds = worlds_record["worlds"]
    require(len(worlds) == 2 and [w["operation_invoked"] for w in worlds] == ["write", "no-op"], "world operations differ")
    for world in worlds:
        require(sha(world["before_utf8"].encode()) == world["before_sha256"] and
                sha(world["after_utf8"].encode()) == world["after_sha256"], "world endpoint identity differs")
        require(same(world["wexp_recipient"]["decision"], world["native_baseline"]["decision"]) and
                world["wexp_recipient"]["decision"]["execution_established"] is False,
                "world decision parity/support limit differs")
    require(worlds[0]["before_utf8"] == worlds[1]["before_utf8"] == "balance=100\n" and
            worlds[0]["after_utf8"] == "balance=0\n" and worlds[1]["after_utf8"] == "balance=100\n",
            "controlled oracle endpoints differ")
    require(worlds[0]["record_sha256"] == worlds[1]["record_sha256"] and
            worlds[0]["policy_sha256"] == worlds[1]["policy_sha256"] and
            worlds[0]["participant_delivery_id"] == worlds[1]["participant_delivery_id"] == "trusted-producer-input" and
            same(worlds[0]["producer_output"], worlds[1]["producer_output"]) and
            same(worlds[0]["wexp_recipient"]["decision"], worlds[1]["wexp_recipient"]["decision"]),
            "identical-input world controls differ")
    require(same(worlds_record["checks"], semantic["trusted_producer"]), "world checks/semantic projection differs")
    require(record["verification"]["implementation_execution_performed"] is True and
            record["status"]["execution"] == "local-run-completed" and
            record["status"]["independent_reproduction"] == "not-performed" and
            record["status"]["comparison"] == "no-local-decision-difference", "card's execution/comparison scope differs")
    manifest_count = check_package_manifest(package)
    return {"experiment_id": record["experiment_id"], "package_id": record["package_id"], "status": "PASS",
            "preparation_commit": PREPARATION_COMMIT, "preparation_tree": PREPARATION_TREE,
            "preparation_freeze_sha256": FREEZE_SHA256, "frozen_input_files": inputs["frozen_input_files"],
            "payload_files": len(paths), "zip_members": len(names), "archive_sha256": artifact["sha256"],
            "outer_manifest_entries": manifest_count, "full_strict_reference_comparison": comparison["status"],
            "pipeline_cases": len(cases), "output_mutations": 16, "controlled_worlds": len(worlds),
            "recorded_implementation_execution": True, "implementation_execution_performed_by_this_verifier": False}


def execute(root):
    reports = []
    for card in sorted(root.glob("experiments/*/packages/*/record.json")):
        record = load(card)
        if record.get("verification", {}).get("profile") == "aar-pilot-v1":
            reports.append(execute_package(card.parent, record))
    return {"status": "PASS", "scope": "Pinned AAR inputs, complete saved results and journal, exact ZIP/payload and outer inventory; no retained implementation execution or authentication of execution truth.",
            "packages": reports, "experiment_execution_performed": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        result = execute(args.root.resolve())
        code = 0
    except (OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile, UnicodeError) as error:
        result = {"status": "FAIL", "error": str(error), "experiment_execution_performed": False}
        code = 1
    print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
