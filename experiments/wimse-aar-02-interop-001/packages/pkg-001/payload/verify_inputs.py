#!/usr/bin/env python3
"""Verify frozen public inputs and prospective conditions without execution.

SPDX-License-Identifier: MIT
The input lock is an identity declaration. Its integrity does not authenticate
its author, timestamp, the native source's truth or an implementation execution.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

from compare_results import REFERENCE_SHA256, ComparisonError, same_types_and_values, strict_json

ROOT = Path(__file__).resolve().parent


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def git_blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(relative):
    return strict_json(safe_path(relative).read_bytes())


def safe_path(relative):
    require(isinstance(relative, str) and relative != "" and not relative.startswith("/") and
            "\\" not in relative and all(part not in {"", ".", ".."} for part in relative.split("/")),
            "noncanonical path")
    path = ROOT / relative
    require(path.resolve().is_relative_to(ROOT), "path escapes the payload: " + relative)
    for parent in [path, *path.parents]:
        if parent == ROOT:
            break
        require(not parent.is_symlink(), "symlink in frozen path: " + relative)
    return path


def check_identity(item, path_key="path"):
    relative = item[path_key]
    path = safe_path(relative)
    require(path.is_file(), "missing input: " + relative)
    raw = path.read_bytes()
    require(type(item["bytes"]) is int and len(raw) == item["bytes"], "input size mismatch: " + relative)
    require(re.fullmatch("[0-9a-f]{64}", item["sha256"]) is not None and sha(raw) == item["sha256"],
            "input SHA-256 mismatch: " + relative)
    if "git_blob_sha1" in item:
        require(git_blob(raw) == item["git_blob_sha1"], "input Git blob mismatch: " + relative)
    return raw


def verify(pre_run=False):
    freeze = load("pre-run/FREEZE.json")
    require(freeze["format"] == "wexp-aar-public-prerun-freeze/0.1.0", "unknown freeze format")
    lock_raw = check_identity(freeze["input_lock"])
    lock = strict_json(lock_raw)
    require(lock["format"] == "wexp-aar-public-input-lock/0.1.0", "unknown input lock format")
    rows = lock["files"]
    names = [row["path"] for row in rows]
    require(len(names) == len(set(names)), "duplicate input-lock path")
    require("pre-run/INPUTS.lock.json" not in names and "pre-run/FREEZE.json" not in names,
            "self-referential freeze/input lock")
    require(len(rows) == freeze["frozen_input_files"], "freeze/input file count differs")
    for row in rows:
        check_identity(row)
    for item in freeze["critical_bindings"]:
        check_identity(item)
    require(sha((ROOT.parent / "PREPARATION.md").read_bytes()) == freeze["outer_preparation_sha256"],
            "outer preparation statement differs from freeze")
    actual = set()
    for path in ROOT.rglob("*"):
        require(not path.is_symlink(), "symlink in payload inventory")
        if path.is_file():
            actual.add(path.relative_to(ROOT).as_posix())
    frozen_inventory = set(names) | {"pre-run/INPUTS.lock.json", "pre-run/FREEZE.json"}
    require(frozen_inventory <= actual, "frozen input inventory incomplete")
    additions = sorted(actual - frozen_inventory)
    if pre_run:
        require(not additions, "pre-run payload has unregistered files: " + repr(additions))

    provenance = load("PROVENANCE.json")
    copies = provenance["copies"]
    require(len(copies) == 172 and len({row["path"] for row in copies}) == 172, "exact-copy accounting differs")
    for row in copies:
        require(row["transformation"] == "none", "retained input unexpectedly transformed")
        check_identity(row)
    sources = load("SOURCES.lock.json")
    require(len(sources["files"]) == 139, "retained-source accounting differs")
    for item in sources["files"]:
        check_identity(item, "package_path")
    profile_raw = (ROOT / "profile.json").read_bytes()
    profile = strict_json(profile_raw)
    require(profile["status"] == "PRIVATE_EXPERIMENTAL_BOUNDED_MAPPING", "historical profile atom changed")
    require(sha((ROOT / "sources/draft-sergeev-wexp-core-01.txt").read_bytes()) == profile["core_txt_sha256"],
            "published Core TXT binding differs")
    for revision, count in [("01", 47), ("02", 55)]:
        text = (ROOT / ("sources/draft-gilda-wimse-agent-audit-record-" + revision + ".txt")).read_bytes()
        require(sha(text) == profile["carrier_revisions"][revision], "carrier TXT binding differs")
        manifest = load("vendor/aar" + revision + "/vectors-agent-audit-record/MANIFEST.json")
        require(len(manifest["vectors"]) == count and manifest["draft"].endswith("-" + revision),
                "native corpus identity/count differs")
    for name in ["aar01", "aar02", "local-aar02"]:
        policy = load("policies/" + name + ".json")
        require(policy["profile_sha256"] == sha(profile_raw), "policy/profile binding differs")
        require(policy["core_txt_sha256"] == profile["core_txt_sha256"], "policy/Core binding differs")
        require(policy["specification_sha256"] == profile["carrier_revisions"][policy["carrier_revision"]],
                "policy/source revision binding differs")
        require(policy["evaluated_at"] == "2026-10-10T07:37:08Z", "fixed scenario context changed")
    delta = load("pre-run/EXPECTED-DELTA.json")
    require(delta["reference_sha256"] == REFERENCE_SHA256, "semantic reference pin differs")
    for name in ["removed_test_cases", "added_test_cases", "replaced_fixtures",
                 "runtime_or_profile_changes", "allowed_semantic_result_differences"]:
        require(same_types_and_values(delta[name], []), "nonzero prospective delta: " + name)
    reference_raw = (ROOT / "reference/private-pilot-semantic-results.json").read_bytes()
    require(sha(reference_raw) == REFERENCE_SHA256, "prior semantic reference differs")
    reference = strict_json(reference_raw)
    expectations = load("pre-run/EXPECTATIONS.json")
    cases = expectations["cases"]
    require(len(cases) == 130 and len({row["id"] for row in cases}) == 130, "prospective case accounting differs")
    require([row["id"] for row in cases] == [row["id"] for row in reference["cases"]],
            "prospective case identities/order differ from reference")
    for case, prior in zip(cases, reference["cases"]):
        check_identity(case["source"])
        check_identity(case["policy"])
        require(case["source"]["sha256"] == prior["source_sha256"] and
                case["policy"]["sha256"] == prior["policy_sha256"], "prospective case source/policy differs")
    mutations = load("pre-run/OUTPUT-MUTATION-INPUTS.json")["inputs"]
    require(len(mutations) == 16 and len({row["id"] for row in mutations}) == 16, "negative-input accounting differs")
    require([row["id"] for row in mutations] == [row["id"] for row in reference["output_mutations"]],
            "negative-input identities/order differ")
    for row in mutations:
        require(sha(row["input_utf8"].encode()) == row["input_sha256"], "negative-input hash differs")
        require(row["expected_output_validation"] == "rejected" and row["expected_admission"] == "quarantine",
                "negative-input expectation differs")
    return {"format": "wexp-aar-input-verification/0.1.0", "status": "PASS",
            "mode": "pre-run-exact-inventory" if pre_run else "frozen-input-identities",
            "frozen_input_files": len(rows), "exact_copied_files": 172, "retained_source_files": 139,
            "prospective_pipeline_cases": 130, "prospective_output_mutations": 16,
            "known_reference_sha256": REFERENCE_SHA256, "unfrozen_additions": additions,
            "implementation_execution_performed": False,
            "scope": "Input identities and prospective conditions relative to the freeze. No pilot/source/producer/recipient execution; no source authenticity or result-truth claim."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pre-run", action="store_true", help="Require the exact initial frozen payload inventory.")
    args = parser.parse_args()
    try:
        result = verify(args.pre_run)
        code = 0
    except (OSError, KeyError, TypeError, ValueError, ComparisonError) as error:
        result = {"format": "wexp-aar-input-verification/0.1.0", "status": "FAIL",
                  "error": str(error), "implementation_execution_performed": False}
        code = 1
    print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
