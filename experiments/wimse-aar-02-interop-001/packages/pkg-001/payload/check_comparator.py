#!/usr/bin/env python3
"""Isolated synthetic comparator controls. Never execute AAR implementations.

SPDX-License-Identifier: MIT
"""
from __future__ import annotations

import datetime
import hashlib
import json
from pathlib import Path

from compare_results import ComparisonError, compare_semantic_bytes, same_types_and_values, strict_json


def check():
    base = b'{"x":false,"nested":{"values":[1,"1",null]}}\n'
    digest = hashlib.sha256(base).hexdigest()
    observations = []

    def control(name, raw, expected, pin=digest):
        try:
            compare_semantic_bytes(raw, base, pin)
            actual = "accepted"
            error = None
        except ComparisonError as exc:
            actual = "rejected"
            error = str(exc)
        observations.append({"id": name, "input_utf8": raw.decode(), "input_sha256": hashlib.sha256(raw).hexdigest(),
                             "expected": expected, "observed": actual, "error": error, "passed": actual == expected})

    control("equal-bytes", base, "accepted")
    control("false-versus-zero", base.replace(b"false", b"0"), "rejected")
    control("integer-versus-float", base.replace(b'[1,"1"', b'[1.0,"1"'), "rejected")
    control("duplicate-root-member", b'{"x":false,"x":false}\n', "rejected")
    control("duplicate-nested-member", b'{"nested":{"x":1,"x":1}}\n', "rejected")
    control("nan", b'{"x":NaN}\n', "rejected")
    control("infinity", b'{"x":Infinity}\n', "rejected")
    control("finite-spelling-overflow", b'{"x":1e400}\n', "rejected")
    control("extra-member", base.replace(b'{"x"', b'{"extra":1,"x"'), "rejected")
    control("same-value-different-serialization", b" " + base, "rejected")
    control("wrong-reference-pin", base, "rejected", "0" * 64)
    # Directly exercise the concrete False == 0 risk, without relying on
    # the additional exact-byte comparison to reject it first.
    type_controls = {
        "false_is_not_zero": not same_types_and_values(False, 0),
        "true_is_not_one": not same_types_and_values(True, 1),
        "nested_boolean_is_not_integer": not same_types_and_values({"x": [False]}, {"x": [0]}),
        "same_document_is_equal": same_types_and_values(strict_json(base), strict_json(base)),
    }
    source = Path(__file__).read_bytes()
    return {"format": "wexp-aar-comparator-toy-controls/0.1.0",
            "observed_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "status": "PASS" if all(row["passed"] for row in observations) and all(type_controls.values()) else "FAIL",
            "controls": observations, "type_controls": type_controls,
            "source_sha256": hashlib.sha256(source).hexdigest(),
            "comparator_sha256": hashlib.sha256(Path(__file__).with_name("compare_results.py").read_bytes()).hexdigest(),
            "pilot_implementation_execution_performed": False,
            "scope": "Synthetic JSON equality/refusal controls only; no AAR source, producer, recipient, oracle or generator was executed."}


if __name__ == "__main__":
    result = check()
    print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
    raise SystemExit(0 if result["status"] == "PASS" else 1)
