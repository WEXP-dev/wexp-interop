#!/usr/bin/env python3
"""Read a frozen pilot output using independently recomputed native evidence.

This is a recipient for one closed local profile, not a general Core evaluator.
It does not import producer code, normalized input, or a Core implementation.
The policy is supplied by the recipient, never selected from the output.
"""

from __future__ import annotations

import argparse
import datetime
import json
from pathlib import Path
from typing import Any

from consumer_policy import (
    ConsumerRuntimeError,
    StrictJSONError,
    VerifiedSource,
    emit,
    result_for,
    strict_json,
    verify_source,
)

OUTPUT_FORMAT = "wexp-aar-pilot-output/0.1.0"
PROFILE_ID = "urn:wexp:aar-pilot:0.1.0"
PROFILE_SHA256 = "3e75e47f77f620793223d4b05785cf576e065f9834da5a667f027eee1dc8b2ca"
CORE_TXT_SHA256 = "50c137713a08ebba7c7b284f97107a2259c9a2d3e0eaefdaede3a77d09fa902b"
REQUIRED_LIMITATIONS = {
    "AAR_RECORD_ASSERTIONS_NOT_WORLD_TRUTH",
    "AAR_BOUNDARY_VANTAGE_NOT_EXTERNALLY_ESTABLISHED",
    "AAR_EVALUATION_IS_DECISION_POINT_REPORT",
    "AAR_OVERSIGHT_IS_PRODUCER_ASSERTED",
    "AAR_NONOCCURRENCE_NOT_ESTABLISHED",
    "AAR_AUTHORIZATION_VALIDITY_NOT_ESTABLISHED",
    "AAR_PRIOR_COMMITMENT_SIGNATURE_NOT_VERIFIED",
}
REQUESTED_CLAIM = {"base": "execution", "qualifiers": []}
OBSERVATION_CLAIM = {"base": "observation", "qualifiers": []}
EVALUATION_SCOPE = {
    "authenticity": "evaluated",
    "boundary-grounding": "evaluated",
    "carrier-mapping": "evaluated",
    "composition": "evaluated",
    "counter-evidence": "evaluated",
    "execution-support": "not-evaluated",
    "independent-verification": "not-evaluated",
    "intent-support": "not-evaluated",
    "invocation-support": "not-evaluated",
    "observation-support": "evaluated",
    "provenance-support": "not-evaluated",
    "target-binding": "evaluated",
}
OUTPUT_KEYS = {"format", "source", "context", "status", "native", "facts", "appraisal", "mapping_failure"}


def _json_key(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _same(value: Any, expected: Any) -> bool:
    # JSON comparison preserves types (Python would otherwise equate 0/False).
    return _json_key(value) == _json_key(expected)


def _set_order(value: Any) -> Any:
    """Core collections in this closed appraisal are set-valued, not ordered."""
    if isinstance(value, dict):
        return {key: _set_order(item) for key, item in value.items()}
    if isinstance(value, list):
        return sorted((_set_order(item) for item in value), key=_json_key)
    return value


def _appraisal_for_profile(source: VerifiedSource) -> dict[str, Any]:
    """The only admitted appraisal shape for this bounded reporting profile.

    This predicate is independently specified from the frozen public profile
    and Core result contract. It cannot appraise other evidence, claim bases,
    qualification roles, composition, or externally supplied counter-evidence.
    """
    target = f"urn:aar-pilot:record:{source.record_sha256}:request:{source.request_digest}"
    context_id = "urn:sha256:" + source.policy_sha256
    basis = ["urn:sha256:" + source.record_sha256]
    limitations = set(REQUIRED_LIMITATIONS)
    limitations.update("AAR_SOURCE_LIMITATION:" + item for item in source.source_limitations or [])
    if source.selected_revision == "01":
        limitations.add("AAR01_EVALUATION_NOT_RECORDED")
    inherited = sorted(limitations)
    return {
        "semantics_version": "wexp-core-1",
        "verdict": "downgrade",
        "fatal_reasons": [],
        "target": target,
        "asserted_claim": REQUESTED_CLAIM,
        "asserted_claim_supported": False,
        "support_entries": [{"claim": OBSERVATION_CLAIM, "basis_refs": basis, "limitations": inherited}],
        "supported_claims": [OBSERVATION_CLAIM],
        "maximal_supported_claims": [OBSERVATION_CLAIM],
        "support_relations": [{"supported_claim": OBSERVATION_CLAIM, "relation": "support-below-claim"}],
        "boundary_ceiling": "observation",
        "boundary_grounding": "attributed",
        "recorder_relations": [],
        "substantive_reasons": ["E_BASE_EXCEEDS_BOUNDARY"],
        "evaluation_gaps": ["E_BASE_NOT_EVALUATED"],
        "evaluation_gap_entries": [{
            "token": "E_BASE_NOT_EVALUATED",
            "target": target,
            "evaluation_context_ref": context_id,
            "affected_claims": [REQUESTED_CLAIM],
            "basis_refs": basis,
            "limitations": inherited,
        }],
        "counter_evidence": [{
            "status": "not-supplied", "affected_claims": [], "basis_refs": [], "reasons": [], "limitations": [],
        }],
        "inherited_limitations": inherited,
        "evaluation_context": {
            "id": context_id,
            "evaluated_at": source.policy["evaluated_at"],
            "trust_configuration": context_id,
            "profile_identifiers": [PROFILE_ID + ":sha256:" + PROFILE_SHA256],
        },
        "evaluation_scope": EVALUATION_SCOPE,
    }


def _profile_policy_valid(source: VerifiedSource) -> bool:
    policy = source.policy
    if (
        policy.get("profile_id") != PROFILE_ID
        or policy.get("profile_sha256") != PROFILE_SHA256
        or policy.get("core_txt_sha256") != CORE_TXT_SHA256
        or not _same(policy.get("requested_claim"), REQUESTED_CLAIM)
    ):
        return False
    timestamp = policy.get("evaluated_at")
    if not isinstance(timestamp, str):
        return False
    try:
        return datetime.datetime.fromisoformat(timestamp.replace("Z", "+00:00")).tzinfo is not None
    except ValueError:
        return False


def validate_output(source: VerifiedSource, raw: bytes) -> list[str]:
    errors: list[str] = []
    if not _profile_policy_valid(source):
        errors.append("policy-invalid")
    try:
        output = strict_json(raw)
    except StrictJSONError:
        return errors + ["output-json-invalid"]
    if not isinstance(output, dict) or set(output) != OUTPUT_KEYS:
        return errors + ["output-shape-invalid"]
    if output["format"] != OUTPUT_FORMAT:
        errors.append("output-format-mismatch")
    # The identifier is only compared after local revision dispatch. It is
    # never a selector, and no missing member is repaired from a later draft.
    expected_source = {
        "record_sha256": source.record_sha256,
        "carrier_revision": source.requested_revision,
        "specification_sha256": source.policy.get("specification_sha256") if source.selected_revision else None,
        "predicate_type": source.policy.get("predicate_type"),
    }
    expected_context = {
        "profile_id": source.policy.get("profile_id"),
        "profile_sha256": source.policy.get("profile_sha256"),
        "policy_sha256": source.policy_sha256,
    }
    if not _same(output["source"], expected_source):
        errors.append("output-source-binding-mismatch")
    if not _same(output["context"], expected_context):
        errors.append("output-policy-binding-mismatch")
    if not _same(output["native"], source.native):
        errors.append("output-native-result-mismatch")
    if source.failure is not None:
        if output["status"] != "mapping-failure":
            errors.append("output-status-mismatch")
        if not _same(output["mapping_failure"], source.failure):
            errors.append("output-mapping-failure-mismatch")
        if output["facts"] is not None or output["appraisal"] is not None:
            errors.append("output-appraises-unadmitted-source")
        return errors
    if output["status"] != "mapped" or output["mapping_failure"] is not None:
        errors.append("output-status-mismatch")
    if not _same(output["facts"], source.facts):
        errors.append("output-facts-mismatch")
    if "policy-invalid" not in errors:
        expected_appraisal = _appraisal_for_profile(source)
        appraisal = output["appraisal"]
        if not isinstance(appraisal, dict) or set(appraisal) != set(expected_appraisal):
            errors.append("output-appraisal-shape-invalid")
        else:
            for key in expected_appraisal:
                if not _same(_set_order(appraisal[key]), _set_order(expected_appraisal[key])):
                    errors.append("output-appraisal-mismatch:" + key)
    return errors


def receive(source_raw: bytes, policy_raw: bytes, output_raw: bytes) -> dict[str, Any]:
    source = verify_source(source_raw, policy_raw)
    result = result_for(source, "wexp-output")
    try:
        errors = validate_output(source, output_raw)
    except (ValueError, TypeError, KeyError, RecursionError):
        errors = ["output-shape-invalid"]
    result["output_validation"] = "rejected" if errors else "accepted"
    result["errors"] = sorted(set(result["errors"] + errors))
    if errors:
        result["decision"]["admission"] = "quarantine"
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True, help="received pilot output to validate")
    args = parser.parse_args()
    try:
        result = receive(args.source.read_bytes(), args.policy.read_bytes(), args.output.read_bytes())
    except (OSError, ConsumerRuntimeError) as exc:
        emit({"route": "wexp-output", "runtime_error": str(exc)})
        return 1
    emit(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
