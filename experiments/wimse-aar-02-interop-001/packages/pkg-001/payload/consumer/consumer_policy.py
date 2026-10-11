"""Native record verification and the recipient's record-only admission policy.

This module imports no WEXP mapper, WEXP evaluator, or WEXP output reader.
Both entry points use it so that the comparison has the same source evidence,
selected native reader, expected predicate type, trusted key, and local policy.
Run one carrier revision per fresh process; the two pinned upstream readers use
the same Python module names and must never be mixed in one interpreter.
"""

from __future__ import annotations

import base64
import hashlib
import importlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

SPECIFICATION_SHA256 = {
    "01": "93ca132dfa65a397a6e64a0ffc47fc69952f2f92ed6c8d3fed3861d47586e763",
    "02": "601ff41ff886d0bf603143d3a02ce382e58e2d780dfbba3351e0f16797d9a79b",
}
POLICY_ID = "aar-record-only-0.1.0"
PREDICATE_TYPE = "https://probityai.github.io/agent-evidence-vectors/predicate/v1/agent-audit-record"
RESULT_FORMAT = "wexp-aar-pilot-consumer-result/0.1.0"
_loaded_revision: str | None = None


class StrictJSONError(ValueError):
    """JSON outside the recipient's unambiguous decoding profile."""


class ConsumerRuntimeError(RuntimeError):
    """An operational failure, rather than an expected record refusal."""


def _unique_members(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for name, item in pairs:
        if name in value:
            raise StrictJSONError("duplicate-member")
        value[name] = item
    return value


def _no_nonfinite(value: str) -> Any:
    raise StrictJSONError("nonfinite-number")


def strict_json(raw: bytes) -> Any:
    """Decode UTF-8 JSON, rejecting repeated member names and NaN/Infinity."""
    try:
        return json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_unique_members,
            parse_constant=_no_nonfinite,
        )
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise StrictJSONError("invalid-json") from exc


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def emit(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False))


def _not_run() -> dict[str, Any]:
    return {"verdict": "not-run", "codes": [], "derived_tier": ""}


@dataclass
class VerifiedSource:
    record_sha256: str
    policy_sha256: str
    policy: dict[str, Any]
    requested_revision: Any
    selected_revision: str | None
    native: dict[str, Any]
    facts: dict[str, Any] | None = None
    request_digest: str | None = None
    source_limitations: list[str] | None = None
    failure: dict[str, str] | None = None
    detail: str | None = None


def _refuse(source: VerifiedSource, stage: str, code: str) -> VerifiedSource:
    source.failure = {"stage": stage, "code": code}
    return source


def _native_reader(revision: str) -> Any:
    global _loaded_revision
    if _loaded_revision not in (None, revision):
        raise ConsumerRuntimeError("one-native-revision-per-process-required")
    packaging = Path(__file__).resolve().parent.parent / "vendor" / f"aar{revision}" / "packaging"
    if not (packaging / "agent_evidence_vectors" / "auditrecord.py").is_file():
        raise ConsumerRuntimeError("pinned-native-reader-missing")
    if _loaded_revision is None:
        # Never accept a module preloaded from an unrelated installation.
        if "agent_evidence_vectors" in sys.modules:
            raise ConsumerRuntimeError("native-module-already-loaded")
        sys.path.insert(0, str(packaging))
        try:
            module = importlib.import_module("agent_evidence_vectors.auditrecord")
        except Exception as exc:
            raise ConsumerRuntimeError("native-reader-import-failed") from exc
        if Path(module.__file__).resolve() != (packaging / "agent_evidence_vectors" / "auditrecord.py").resolve():
            raise ConsumerRuntimeError("unexpected-native-reader-location")
        _loaded_revision = revision
        return module
    return importlib.import_module("agent_evidence_vectors.auditrecord")


def _facts(predicate: dict[str, Any], revision: str) -> dict[str, Any]:
    """Extract reported facets only after the full native verifier succeeds."""
    evaluation = predicate["evaluation"] if revision == "02" else None
    oversight = predicate.get("oversight")
    return {
        "evaluation": {
            "status": evaluation["status"] if evaluation is not None else "unknown-in-01",
            "unavailable_input": list(evaluation.get("unavailableInput", [])) if evaluation is not None else [],
            # Section 5.4 uses the decision field's evidence classification.
            # Classification is still a record claim; no world truth follows.
            "evidence_class": predicate["fieldEvidence"]["decision"],
        },
        "decision_reported": predicate["decision"]["reported"],
        "effect_observed": predicate["effect"]["observed"],
        "agreement": predicate["agreement"],
        "oversight": {
            "presence": "present" if oversight is not None else "absent",
            "act": oversight.get("act") if oversight is not None else None,
            "record_digest": oversight.get("recordDigest") if oversight is not None else None,
            "evidence_class": "producer-asserted",
            "human_participation": "not-established",
            "authority": "not-established",
        },
    }


def verify_source(raw: bytes, policy_raw: bytes) -> VerifiedSource:
    """Verify native bytes before deriving any admitted source facts.

    WEXP-only metadata in the supplied policy is deliberately not consumed
    here. The native alternative needs no Core or output-profile dependency.
    """
    source = VerifiedSource(sha256(raw), sha256(policy_raw), {}, None, None, _not_run())
    try:
        policy = strict_json(policy_raw)
    except StrictJSONError:
        return _refuse(source, "receiver-policy", "policy-invalid")
    if not isinstance(policy, dict):
        return _refuse(source, "receiver-policy", "policy-invalid")
    source.policy = policy
    revision = policy.get("carrier_revision")
    source.requested_revision = revision
    if revision is None:
        return _refuse(source, "revision-selection", "carrier-revision-not-selected")
    if not isinstance(revision, str) or revision not in SPECIFICATION_SHA256:
        return _refuse(source, "revision-selection", "unsupported-carrier-revision")
    source.selected_revision = revision
    if policy.get("specification_sha256") != SPECIFICATION_SHA256[revision]:
        return _refuse(source, "revision-selection", "carrier-specification-mismatch")
    key = policy.get("observer_public_key")
    predicate_type = policy.get("predicate_type")
    if (
        policy.get("policy_id") != POLICY_ID
        or not isinstance(key, str)
        or re.fullmatch(r"[0-9a-fA-F]{64}", key) is None
        or predicate_type != PREDICATE_TYPE
    ):
        return _refuse(source, "receiver-policy", "policy-invalid")
    reader = _native_reader(revision)
    try:
        report = reader.verify(raw, reader.Policy(predicate_type=predicate_type, observer_public_key=key))
    except Exception as exc:
        # This is an execution failure of a verifier, not its malformed verdict
        # and not an execution-evidence appraisal. Preserve the error category.
        source.native = {"verdict": "error", "codes": [type(exc).__name__], "derived_tier": ""}
        source.detail = type(exc).__name__
        return _refuse(source, "native-validation", "native-verifier-error")
    source.native = {
        "verdict": report.verdict,
        "codes": list(report.codes),
        "derived_tier": report.derived_tier,
    }
    if report.verdict == "malformed":
        return _refuse(source, "native-validation", "native-record-malformed")
    if report.verdict != "valid":
        return _refuse(source, "native-validation", "native-verdict-not-admitted")
    try:
        envelope = strict_json(raw)
        statement = strict_json(base64.b64decode(envelope["payload"], validate=True))
        predicate = statement["predicate"]
        if revision == "01" and any(member in predicate for member in ("evaluation", "oversight")):
            # A closed local revision profile, NOT a normative claim that the
            # legacy reader declared the record malformed. Native verdict stays.
            return _refuse(source, "revision-selection", "revision02-members-in-01-profile")
        source.facts = _facts(predicate, revision)
        source.request_digest = reader.request_digest(predicate)
        source.source_limitations = list(predicate["doesNotAssert"])
    except (KeyError, TypeError, ValueError, AttributeError, RecursionError) as exc:
        source.detail = type(exc).__name__
        return _refuse(source, "native-validation", "validated-record-extraction-failed")
    return source


def decision_for(source: VerifiedSource) -> dict[str, Any]:
    """Local admission is about the report; truth of an action is never inferred."""
    classification = "source-invalid"
    evaluation_status = None
    unavailable_input: list[str] = []
    oversight_act = None
    if source.failure is not None:
        if source.failure["code"] in {"carrier-revision-not-selected", "unsupported-carrier-revision"}:
            classification = "revision-not-selected"
        elif source.failure["code"] in {"revision02-members-in-01-profile", "carrier-specification-mismatch"}:
            classification = "revision-policy-mismatch"
    else:
        assert source.facts is not None
        facts = source.facts
        evaluation_status = facts["evaluation"]["status"]
        unavailable_input = facts["evaluation"]["unavailable_input"]
        oversight_act = facts["oversight"]["act"]
        reported = facts["decision_reported"]
        if evaluation_status == "not-evaluated" and reported in {"permit", "permit-with-conditions"}:
            classification = "reported-not-evaluated-permit"
        elif facts["agreement"] == "disagree":
            classification = "reported-decision-effect-disagreement"
        elif reported == "deny":
            classification = {
                "evaluated": "reported-evaluated-deny",
                "not-evaluated": "reported-not-evaluated-deny",
                "unknown-in-01": "reported-deny-evaluation-unknown-in-01",
            }[evaluation_status]
        else:
            classification = "reported-permit"
    return {
        "admission": "record-only" if source.failure is None else "quarantine",
        "classification": classification,
        "execution_established": False,
        "authorization_established": False,
        "human_participation_established": False,
        "evaluation_status": evaluation_status,
        "unavailable_input": unavailable_input,
        "oversight_act": oversight_act,
    }


def result_for(source: VerifiedSource, route: str) -> dict[str, Any]:
    return {
        "format": RESULT_FORMAT,
        "route": route,
        "source_sha256": source.record_sha256,
        "policy_sha256": source.policy_sha256,
        "carrier_revision": source.requested_revision,
        "native": source.native,
        "output_validation": "not-applicable",
        "errors": [source.failure["code"]] if source.failure else [],
        "decision": decision_for(source),
    }
