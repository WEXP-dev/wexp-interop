#!/usr/bin/env python3
"""Compare recorded public-run data with the frozen, known private reference.

SPDX-License-Identifier: MIT
This program checks data equality and declared accounting. It does not execute
the pilot or authenticate the fact that an execution observation occurred.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
REFERENCE_SHA256 = "1a97015e506db61bbf481cfac3ff3c2e53186cb935b491cb190bc370a1c62ef2"
REFERENCE_PATH = ROOT / "reference/private-pilot-semantic-results.json"


class ComparisonError(ValueError):
    pass


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def unique_members(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ComparisonError("duplicate JSON member: " + key)
        result[key] = value
    return result


def reject_constant(value):
    raise ComparisonError("non-finite JSON number: " + value)


def finite_float(value):
    parsed = float(value)
    if not math.isfinite(parsed):
        raise ComparisonError("non-finite JSON number after parsing: " + value)
    return parsed


def strict_json(raw: bytes):
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=unique_members,
                          parse_constant=reject_constant, parse_float=finite_float)
    except ComparisonError:
        raise
    except (UnicodeError, ValueError, RecursionError) as error:
        raise ComparisonError("invalid UTF-8 JSON: " + str(error)) from error


def same_types_and_values(left, right) -> bool:
    """Keep booleans, integers, floats, arrays and objects distinct."""
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return left.keys() == right.keys() and all(
            same_types_and_values(left[key], right[key]) for key in left)
    if isinstance(left, list):
        return len(left) == len(right) and all(
            same_types_and_values(a, b) for a, b in zip(left, right))
    return left == right


def require(condition: bool, message: str):
    if not condition:
        raise ComparisonError(message)


def compare_semantic_bytes(actual: bytes, reference: bytes,
                           known_reference_sha: str = REFERENCE_SHA256):
    # The optional argument is for isolated toy controls. The CLI has no
    # reference-pin override and always supplies the published constant.
    require(sha(reference) == known_reference_sha, "reference SHA-256 differs from the fixed pin")
    expected = strict_json(reference)
    observed = strict_json(actual)
    require(same_types_and_values(observed, expected), "full semantic JSON differs, including JSON types")
    require(sha(actual) == known_reference_sha, "semantic serialized bytes differ from the fixed reference")
    return observed


def compare_run(results: Path, reference_path: Path = REFERENCE_PATH):
    expected_delta = strict_json((ROOT / "pre-run/EXPECTED-DELTA.json").read_bytes())
    require(expected_delta["reference_sha256"] == REFERENCE_SHA256, "expected-delta reference pin changed")
    for key in ["removed_test_cases", "added_test_cases", "replaced_fixtures",
                "runtime_or_profile_changes", "allowed_semantic_result_differences"]:
        require(same_types_and_values(expected_delta[key], []), "nonempty permitted delta: " + key)
    semantic_raw = (results / "semantic-results.json").read_bytes()
    semantic = compare_semantic_bytes(semantic_raw, reference_path.read_bytes())
    expectations = strict_json((ROOT / "pre-run/EXPECTATIONS.json").read_bytes())
    require([row["id"] for row in semantic["cases"]] ==
            [row["id"] for row in expectations["cases"]], "case identities or order differ")
    require(len(semantic["cases"]) == 130, "expected exactly 130 pipeline cases")
    for row in semantic["cases"]:
        require(all(value is True for value in row["checks"].values()), "non-true pipeline check: " + row["id"])
    for section, expected_keys in [
        ("distinctions", expectations["distinction_checks_required_true"]),
        ("trusted_producer", expectations["trusted_producer_checks_required_true"])]:
        require(sorted(semantic[section]) == expected_keys, section + " check set differs")
        require(all(value is True for value in semantic[section].values()), "non-true " + section + " check")

    negative_plan = strict_json((ROOT / "pre-run/OUTPUT-MUTATION-INPUTS.json").read_bytes())["inputs"]
    negative_run = strict_json((results / "output-mutation-results.json").read_bytes())
    require(len(negative_plan) == len(negative_run) == 16, "expected exactly 16 output mutations")
    require([row["id"] for row in negative_plan] == [row["id"] for row in negative_run],
            "output-mutation identities/order differ")
    for expected, actual in zip(negative_plan, negative_run):
        for key in ["id", "base_case", "input_utf8", "input_sha256"]:
            require(same_types_and_values(actual[key], expected[key]), "mutation input differs: " + expected["id"] + "/" + key)
        require(sha(actual["input_utf8"].encode("utf-8")) == expected["input_sha256"],
                "mutation input byte/hash mismatch: " + expected["id"])
        require(actual["passed"] is True, "mutation did not pass: " + expected["id"])
        require(actual["recipient_result"]["output_validation"] == "rejected" and
                actual["recipient_result"]["decision"]["admission"] == "quarantine",
                "mutation refusal differs: " + expected["id"])

    for case in expectations["cases"]:
        if "runtime_generated_policy_path" in case:
            raw = (results / case["runtime_generated_policy_path"]).read_bytes()
            require(sha(raw) == case["policy"]["sha256"] and len(raw) == case["policy"]["bytes"],
                    "runtime-generated dispatch policy differs: " + case["id"])
    observation = strict_json((results / "execution-observation.json").read_bytes())
    counts = {"pipeline_cases": 130, "pipeline_passed": 130, "published_native_vectors": 102,
              "local_fixtures": 19, "output_mutations": 16, "output_mutations_rejected": 16,
              "controlled_worlds": 2}
    require(same_types_and_values(observation["counts"], counts), "execution counts differ")
    require(observation["passed"] is True and observation["compare_equal"] is True,
            "runner success/comparison was not recorded as true")
    require(observation["semantic_results_sha256"] == REFERENCE_SHA256, "observation/semantic fingerprint differs")
    return {
        "format": "wexp-aar-public-reference-comparison/0.1.0",
        "status": "PASS", "semantic_sha256": sha(semantic_raw), "reference_sha256": REFERENCE_SHA256,
        "comparison": "full strict typed JSON and exact semantic bytes; zero permitted semantic delta",
        "pipeline_cases": 130, "output_mutation_inputs_compared": 16, "controlled_worlds": 2,
        "implementation_execution_performed_by_comparator": False,
        "limitations": ["This checks the supplied run data; it does not authenticate execution or its timestamp.",
                        "The private reference was known before the public run; this is not blind or external-team reproduction.",
                        "WEXP/native-baseline comparison is performed by the retained runner, separately from this reference comparison."]
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", required=True, type=Path)
    parser.add_argument("--reference", type=Path, default=REFERENCE_PATH)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    try:
        result = compare_run(args.results.resolve(), args.reference.resolve())
        code = 0
    except (OSError, KeyError, TypeError, ComparisonError) as error:
        result = {"format": "wexp-aar-public-reference-comparison/0.1.0", "status": "FAIL",
                  "error": str(error), "implementation_execution_performed_by_comparator": False}
        code = 1
    output = (json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode()
    if args.report:
        # Store a new observation. Never replace a retained result.
        try:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            with args.report.open("xb") as stream:
                stream.write(output)
        except OSError as error:
            print("Could not create new comparison report: " + str(error), file=sys.stderr)
            return 1
    sys.stdout.buffer.write(output)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
