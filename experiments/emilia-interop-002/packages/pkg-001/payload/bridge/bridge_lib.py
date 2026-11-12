"""WEXP x EMILIA INTEROP-002 experiment-specific bridge candidate.

Not a generic Bridge Framework. Not part of interop_core, which this file
changes by zero bytes. Every element here exists because BRIDGE-CANDIDATE.yaml
declares it, and the element identifiers match that file exactly.

The one thing worth knowing before reading: elements can be individually
disabled. That is not a feature of the mapping, it is how the frozen
single-element ablation plan is executed. A disabled element takes its
dependents down with it, fail-closed, rather than letting them run on evidence
nobody checked.
"""

from __future__ import annotations

import base64
import hashlib
import json
import re
from datetime import datetime, timezone

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PublicFormat,
    load_der_public_key,
)

BRIDGE_ID = "WEXP-EMILIA-INTEROP-002-BRIDGE-CANDIDATE-001"
BRIDGE_VERSION = 1
SEMANTICS_VERSION = "wexp-core-1"
OBSERVATION_DOMAIN = "EP-OUTCOME-OBSERVATION-v1\x00"
CAID_PATTERN = re.compile(r"^caid:sha256:[0-9a-f]{64}$")

ELEMENTS = [f"BE-{n:02d}" for n in range(1, 18)]

# Mirrors depends_on in BRIDGE-CANDIDATE.yaml. Kept as data so the test suite
# can assert the two agree instead of trusting that they do.
# Genuine OUTPUT dependence only. An entry here means the dependent literally
# cannot compute without the other element's result, so ablating the dependency
# fails it closed. Elements that merely run "before" another are NOT listed:
# treating ordering as dependence is how an ablation study accidentally proves
# that every element is necessary. BE-08 works over whatever observation set
# survives, so it depends on none of BE-01..BE-07; BE-12 computes an unsupported
# boundary when no signature was verified rather than refusing to compute.
DEPENDS = {
    "BE-01": [],
    "BE-02": [],
    "BE-03": ["BE-01"],            # currency of a pin nobody resolved is undefined
    "BE-04": [],
    "BE-05": [],
    "BE-06": [],
    "BE-07": [],
    "BE-08": [],
    "BE-09": ["BE-01"],            # control_domain_id comes from the pinned registry
    "BE-10": ["BE-08", "BE-09"],   # the IV predicate names quorum and distinctness
    "BE-11": [],
    "BE-12": [],
    "BE-13": [],
    "BE-14": [],
    "BE-15": [],
    "BE-16": [],
    "BE-17": ["BE-12", "BE-13", "BE-14"],  # Core 6 requires all three fields
}

# Carried on every finding this bridge produces. M-05 could not be resolved
# from the frozen evidence, and a limitation that is not carried is a limitation
# that quietly disappears.
STANDING_LIMITATIONS = [
    "caid_issuer_scope_not_evidenced",
    "boundary_grounding_attributed_not_attested",
    "common_dependencies_beyond_declared_control_domain_not_visible",
]


def jcs(value) -> str:
    """Canonical JSON for the EP signing preimage only, never for comparison."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _b64u(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _instant(text):
    try:
        return datetime.fromisoformat(str(text).replace("Z", "+00:00")).astimezone(timezone.utc)
    except (ValueError, TypeError):
        return None


def _canonical_key(spki_b64u: str):
    """Key identity is the DER SubjectPublicKeyInfo, not the key_id text.

    EMILIA Section 4 is explicit that re-encoding a key must not create a
    distinct source, which is only true if identity comes from these bytes.
    """
    try:
        key = load_der_public_key(_b64u(spki_b64u))
        return key.public_bytes(Encoding.DER, PublicFormat.SubjectPublicKeyInfo), key
    except Exception:
        return None, None


class Availability:
    """An element is available only if it and every dependency are enabled."""

    def __init__(self, disabled):
        self.disabled = frozenset(disabled)
        self._cache: dict[str, bool] = {}

    def __call__(self, element_id: str) -> bool:
        if element_id in self._cache:
            return self._cache[element_id]
        ok = element_id not in self.disabled and all(self(d) for d in DEPENDS[element_id])
        self._cache[element_id] = ok
        return ok


def _accept_observations(inp, have):
    """BE-01..BE-07 decide, per observation, whether it may be used at all."""
    keys = inp.get("options", {}).get("sourceKeys", {}) or {}
    options = inp.get("options", {})
    windows = options.get("observationWindows", []) or []
    now = _instant(options.get("now"))
    accepted, rejected = [], []

    for index, obs in enumerate(inp.get("observations", []) or []):
        reasons = []
        source = obs.get("source", {}) or {}
        pin = keys.get(source.get("source_id"))
        canonical = None

        if not have("BE-01"):
            # No pin resolution at all. The presented key stands unchallenged,
            # which is precisely the exposure BE-01 exists to close.
            canonical, _ = _canonical_key(obs.get("proof", {}).get("public_key", ""))
            pin = None
        elif pin is None:
            reasons.append("source_key_not_pinned")
        else:
            canonical, _ = _canonical_key(pin.get("public_key", ""))
            presented, _ = _canonical_key(obs.get("proof", {}).get("public_key", ""))
            if canonical is None or presented is None:
                reasons.append("source_key_malformed")
            elif canonical != presented:
                reasons.append("source_key_mismatch")
            for field in ("role", "source_class", "facility_id"):
                if source.get(field) != pin.get(field):
                    reasons.append(f"source_metadata_not_pinned:{field}")

        signature_verified = False
        if have("BE-02"):
            proof = obs.get("proof", {}) or {}
            body = {k: v for k, v in obs.items() if k != "proof"}
            message = (OBSERVATION_DOMAIN + jcs(body)).encode("utf-8")
            _, key = _canonical_key(proof.get("public_key", ""))
            if key is None:
                reasons.append("signature_key_malformed")
            else:
                try:
                    key.verify(_b64u(proof.get("signature_b64u", "")), message)
                    signature_verified = True
                except (InvalidSignature, Exception):  # noqa: BLE001 - fail closed either way
                    reasons.append("signature_invalid")

        attested = _instant(obs.get("attested_at"))
        if have("BE-03") and pin is not None:
            if True:
                valid_from, valid_to = _instant(pin.get("valid_from")), _instant(pin.get("valid_to"))
                compromised = _instant(pin.get("compromised_at")) if pin.get("compromised_at") else None
                if pin.get("status") != "active":
                    reasons.append("source_pin_not_current:status")
                if attested is None or valid_from is None or valid_to is None:
                    reasons.append("source_pin_not_current:unparsable")
                elif not (valid_from <= attested <= valid_to):
                    reasons.append("source_pin_not_current:interval")
                if compromised is not None and attested is not None and compromised <= attested:
                    reasons.append("source_pin_not_current:compromised")

        if have("BE-04"):
            for field, expected_key in (
                ("receipt_id", "expectedReceiptId"),
                ("receipt_digest", "expectedReceiptDigest"),
                ("action_hash", "expectedActionHash"),
                ("consumption_nonce", "expectedConsumptionNonce"),
                ("operation_id", "expectedOperationId"),
            ):
                if expected_key in options and obs.get(field) != options[expected_key]:
                    reasons.append(f"exact_binding_mismatch:{field}")
            if "expectedFacilityId" in options and source.get("facility_id") != options["expectedFacilityId"]:
                reasons.append("exact_binding_mismatch:facility")

        caid = obs.get("action_caid")
        if have("BE-05"):
            if caid is None:
                reasons.append("caid_premise_absent")
        if have("BE-06"):
            if caid is not None and not CAID_PATTERN.match(str(caid)):
                reasons.append("caid_out_of_domain")
            if caid is not None and "expectedActionCaid" in options and caid != options["expectedActionCaid"]:
                reasons.append("exact_binding_mismatch:action_caid")

        if have("BE-07"):
            observed_from = _instant(obs.get("observed_from"))
            observed_until = _instant(obs.get("observed_until"))
            if None in (observed_from, observed_until, attested):
                reasons.append("observation_time_invalid:unparsable")
            else:
                if not (observed_from <= observed_until <= attested):
                    reasons.append("observation_time_invalid:order")
                if now is not None and attested > now:
                    reasons.append("observation_time_invalid:attested_in_future")
            window = next(
                (
                    w
                    for w in windows
                    if w.get("role") == source.get("role")
                    and w.get("source_class") in (None, source.get("source_class"))
                ),
                None,
            )
            if window is not None and None not in (observed_from, observed_until):
                not_before, not_after = _instant(window.get("not_before")), _instant(window.get("not_after"))
                relation = window.get("relation")
                if None in (not_before, not_after):
                    reasons.append("window_mismatch:unparsable")
                elif relation == "exact":
                    if observed_from != not_before or observed_until != not_after:
                        reasons.append("window_mismatch:exact")
                elif relation == "within":
                    if not (not_before <= observed_from and observed_until <= not_after):
                        reasons.append("window_mismatch:within")
                elif relation == "covers":
                    if not (observed_from <= not_before and not_after <= observed_until):
                        reasons.append("window_mismatch:covers")
                else:
                    reasons.append("window_mismatch:unknown_relation")
                limit = window.get("max_attestation_delay_ms")
                if isinstance(limit, int) and attested is not None and observed_until is not None:
                    if limit > 86_400_000:
                        reasons.append("window_mismatch:delay_bound_out_of_range")
                    elif (attested - observed_until).total_seconds() * 1000 > limit:
                        reasons.append("attestation_delay_exceeded")

        record = {
            "index": index,
            "source_id": source.get("source_id"),
            "role": source.get("role"),
            "source_class": source.get("source_class"),
            "canonical_key_sha256": _sha256_hex(canonical) if canonical else None,
            "control_domain_id": (pin or {}).get("control_domain_id"),
            "observed_effects": obs.get("observed_effects", []),
            "signature_verified": signature_verified,
            "basis_ref": "sha256:" + _sha256_hex(jcs(obs).encode("utf-8")),
            "reasons": sorted(set(reasons)),
        }
        (accepted if not reasons else rejected).append(record)

    return accepted, rejected


def _predicate_holds(predicate, value):
    op, target = predicate.get("op"), predicate.get("value")
    try:
        if op == "eq":
            return value == target
        if op == "gte":
            return float(value) >= float(target)
        if op == "lte":
            return float(value) <= float(target)
    except (TypeError, ValueError):
        return False
    return False


def evaluate(fixture, disabled=frozenset()):
    """Run the bridge over one frozen fixture. Never mutates the fixture."""
    have = Availability(disabled)
    inp = fixture.get("emilia_input", {}) or {}
    options = inp.get("options", {}) or {}
    accepted, rejected = _accept_observations(inp, have)

    trace = {"disabled": sorted(disabled), "unavailable": [e for e in ELEMENTS if not have(e)]}
    gaps, fatal, limitations = [], [], list(STANDING_LIMITATIONS)

    # BE-08 relying-party requirements, quorum, and prediction coverage.
    requirement_results, group_indeterminate = [], False
    if have("BE-08"):
        for requirement in options.get("sourceRequirements", []) or []:
            matching = [
                a
                for a in accepted
                if a["role"] == requirement.get("role")
                and requirement.get("source_class") in (None, a["source_class"])
            ]
            dimensions = requirement.get("distinct_by") or ["key"]
            distinct = set()
            for a in matching:
                distinct.add(
                    tuple(
                        a["canonical_key_sha256"] if d == "key" else a["control_domain_id"]
                        for d in dimensions
                    )
                )
            minimum = requirement.get("min_distinct_sources", 1)
            met = isinstance(minimum, int) and 1 <= minimum <= 16 and len(distinct) >= minimum
            requirement_results.append(
                {
                    "role": requirement.get("role"),
                    "source_class": requirement.get("source_class"),
                    "min_distinct_sources": minimum,
                    "distinct_accepted_sources": len(distinct),
                    "met": met,
                }
            )
            if not met:
                group_indeterminate = True
                gaps.append(
                    {
                        "token": "source_requirement_unmet",
                        "detail": f"{requirement.get('role')}/{requirement.get('source_class')}",
                    }
                )
        for effect in inp.get("predicted_effects", []) or []:
            group = [
                a
                for a in accepted
                if a["role"] == effect.get("required_source_role")
                and effect.get("required_source_class") in (None, a["source_class"])
            ]
            if not group:
                group_indeterminate = True
                gaps.append(
                    {
                        "token": "prediction_group_unobserved",
                        "detail": f"{effect.get('effect_type')}@{effect.get('target')}",
                    }
                )
    quorum_computed = have("BE-08")

    # BE-09 independence, BE-10 the IV predicate.
    independence = {"evaluated": False, "distinct_key": None, "distinct_control_domain": None}
    if have("BE-09"):
        independent = [a for a in accepted if a["role"] == "independent_observer"]
        others = [a for a in accepted if a["role"] != "independent_observer"]
        if independent:
            independence["evaluated"] = True
            independence["distinct_key"] = all(
                i["canonical_key_sha256"] and i["canonical_key_sha256"] != o["canonical_key_sha256"]
                for i in independent
                for o in others
            )
            independence["distinct_control_domain"] = all(
                i["control_domain_id"] and i["control_domain_id"] != o["control_domain_id"]
                for i in independent
                for o in others
            )

    iv_reasons = []
    if not have("BE-10"):
        iv_validation = "not-evaluated"
        iv_reasons.append("BE-10_unavailable_iv_predicate_undefined")
    elif not (options.get("sourceRequirements")):
        iv_validation = "not-evaluated"
        iv_reasons.append("no_relying_party_independence_requirement")
    elif not quorum_computed:
        iv_validation = "not-evaluated"
        iv_reasons.append("relying_party_quorum_not_established")
    elif group_indeterminate or not independence["evaluated"]:
        iv_validation = "not-evaluated"
        iv_reasons.append("independence_evidence_absent")
    elif independence["distinct_key"] and independence["distinct_control_domain"]:
        iv_validation = "supported"
    else:
        iv_validation = "unsupported"
        iv_reasons.append("independence_not_distinct")

    target = {
        "operation_id": options.get("expectedOperationId"),
        "action_hash": options.get("expectedActionHash"),
        "action_caid": options.get("expectedActionCaid"),
        "facility_id": options.get("expectedFacilityId"),
        "receipt_id": options.get("expectedReceiptId"),
    }
    target_ref = "target:sha256:" + _sha256_hex(jcs(target).encode("utf-8"))

    # BE-13 evaluation context.
    if have("BE-13"):
        trust_material = {
            "sourceKeys": options.get("sourceKeys"),
            "sourceRequirements": options.get("sourceRequirements"),
            "observationWindows": options.get("observationWindows"),
        }
        context = {
            "id": "evalctx:sha256:" + _sha256_hex(jcs(trust_material).encode("utf-8")),
            "evaluated_at": options.get("now"),
            "trust_configuration": "sha256:" + _sha256_hex(jcs(trust_material).encode("utf-8")),
            "profile_identifiers": [
                f"{BRIDGE_ID}#v{BRIDGE_VERSION}",
                "draft-sergeev-wexp-core-01#84c0a164",
                "draft-schrock-ep-outcome-binding-00#7bb88cdc",
                "draft-schrock-canonical-action-identifier-02#777487b0",
            ],
            "accepted_grounding_classes": ["attributed", "attested"],
        }
    else:
        context = None
        fatal.append("E_EVALUATION_CONTEXT_NOT_CONSTRUCTIBLE")

    context_ref = context["id"] if context else None
    bound = [a for a in accepted if not a["reasons"]]

    # BE-11 the observation base finding.
    base_findings = []
    if have("BE-11") and context_ref:
        supported = bool(bound) and not group_indeterminate
        base_findings.append(
            {
                "target": target_ref,
                "evaluation_context_ref": context_ref,
                "base": "observation",
                "target_binding": "supported" if bound else "unsupported",
                "semantic_validation": "supported" if supported else ("unsupported" if bound else "not-evaluated"),
                "basis_refs": [a["basis_ref"] for a in bound],
                "reasons": [] if supported else sorted({r for a in rejected for r in a["reasons"]}),
                "limitations": list(limitations),
            }
        )
    elif context_ref:
        gaps.append({"token": "observation_base_not_constructed", "detail": "observation"})

    # Core 6 requires claim-independent mapping: the other three bases are
    # evaluated too, and every one of them is refused for a stated reason.
    for base, reason in (
        ("intent", "no_intent_predicate_defined_by_this_bridge"),
        ("invocation", "no_invocation_boundary_evidence_in_frozen_material"),
        ("execution", "M-09_effect_to_execution_predicate_non_constructible"),
    ):
        if context_ref:
            base_findings.append(
                {
                    "target": target_ref,
                    "evaluation_context_ref": context_ref,
                    "base": base,
                    "target_binding": "supported" if bound else "unsupported",
                    "semantic_validation": "unsupported",
                    "basis_refs": [],
                    "reasons": [reason],
                    "limitations": list(limitations),
                }
            )

    qualifier_findings = []
    if context_ref:
        qualifier_findings.append(
            {
                "target": target_ref,
                "evaluation_context_ref": context_ref,
                "qualifier": "IV",
                "qualified_base": "observation",
                "target_binding": "supported" if bound else "unsupported",
                "semantic_validation": "supported" if bound and not group_indeterminate else "not-evaluated",
                "independence_validation": iv_validation,
                "basis_refs": [a["basis_ref"] for a in bound if a["role"] == "independent_observer"],
                "reasons": iv_reasons,
                "limitations": list(limitations),
            }
        )

    # BE-12 boundary and ceiling.
    if have("BE-12") and context_ref:
        boundary_supported = bool(bound) and all(a["signature_verified"] for a in bound)
        boundary = {
            "target": target_ref,
            "evaluation_context_ref": context_ref,
            "ceiling_base": "observation" if boundary_supported else None,
            "status": "supported" if boundary_supported else "unsupported",
            "target_binding": "supported" if bound else "unsupported",
            "grounding": "attributed" if boundary_supported else "not-evaluated",
            "basis_refs": [a["basis_ref"] for a in bound],
            "reasons": []
            if boundary_supported
            else (
                ["no_accepted_bound_observation"]
                if not bound
                else ["grounding_insufficient_no_verified_signature"]
            ),
            "limitations": list(limitations),
        }
    else:
        boundary = None
        fatal.append("E_BOUNDARY_NOT_EVALUATED")

    # BE-14 counter-evidence.
    counter_evidence = []
    if have("BE-14"):
        by_effect: dict[tuple, set] = {}
        for a in bound:
            for effect in a["observed_effects"]:
                by_effect.setdefault((effect.get("effect_type"), effect.get("target")), set()).add(
                    str(effect.get("value"))
                )
        for (effect_type, tgt), values in sorted(by_effect.items()):
            if len(values) > 1:
                counter_evidence.append(
                    {
                        "status": "unresolved-material",
                        "affected_claims": ["(observation, {IV})"],
                        "basis_refs": [a["basis_ref"] for a in bound],
                        "reasons": ["conflicting_values_from_distinct_accepted_sources"],
                        "limitations": [f"{effect_type}@{tgt}"],
                    }
                )
        for effect in inp.get("predicted_effects", []) or []:
            group = [
                a
                for a in bound
                if a["role"] == effect.get("required_source_role")
                and effect.get("required_source_class") in (None, a["source_class"])
            ]
            for a in group:
                for observed in a["observed_effects"]:
                    if observed.get("effect_type") != effect.get("effect_type"):
                        continue
                    if not _predicate_holds(effect.get("predicate", {}), observed.get("value")):
                        counter_evidence.append(
                            {
                                "status": "resolved-no-defeat",
                                "affected_claims": ["(observation, {IV})"],
                                "basis_refs": [a["basis_ref"]],
                                "reasons": ["effect_predicate_failed_does_not_defeat_record_of_event"],
                                "limitations": [],
                            }
                        )
        if not counter_evidence:
            counter_evidence.append(
                {
                    "status": "not-supplied",
                    "affected_claims": [],
                    "basis_refs": [],
                    "reasons": [],
                    "limitations": [],
                }
            )
    else:
        fatal.append("E_COUNTER_EVIDENCE_NOT_CONSTRUCTIBLE")

    # BE-15 claim expansion refusal.
    expansion_refusals = []
    if have("BE-15"):
        for asserted in (fixture.get("attempted_expansion", {}) or {}).get("asserted_properties", []):
            expansion_refusals.append(
                {
                    "property": asserted.get("property"),
                    "disposition": "asserted_not_admitted",
                    "reason": "an assertion attached to a fixture is not evidence; "
                    "every finding is derived from the observation set and the relying-party policy",
                    "above_ceiling": asserted.get("property")
                    not in ("observation", "independent_verification"),
                }
            )
    admitted_expansions = []
    if not have("BE-15"):
        admitted_expansions = [
            a.get("property")
            for a in (fixture.get("attempted_expansion", {}) or {}).get("asserted_properties", [])
        ]

    # BE-16 authority conversion refusal.
    authority_refusals = []
    if have("BE-16"):
        for request in (fixture.get("attempted_authority_conversion", {}) or {}).get("requests", []):
            authority_refusals.append(
                {
                    "from": request.get("from"),
                    "to": request.get("to"),
                    "disposition": "refused",
                    "reason": "no_independent_authority_source",
                }
            )
    admitted_authority_conversions = []
    if not have("BE-16"):
        admitted_authority_conversions = [
            f"{r.get('from')}->{r.get('to')}"
            for r in (fixture.get("attempted_authority_conversion", {}) or {}).get("requests", [])
        ]

    # BE-17 assembly.
    appraisal_input = None
    if have("BE-17") and context is not None and boundary is not None and not fatal:
        appraisal_input = {
            "semantics_version": SEMANTICS_VERSION,
            "target": target_ref,
            "asserted_claim": "(observation, {IV})",
            "evaluation_context": context,
            "boundary_finding": boundary,
            "base_findings": base_findings,
            "qualifier_findings": qualifier_findings,
            "recorder_relations": [],
            "counter_evidence": counter_evidence,
            "evaluation_scope": {
                "time": {"now": options.get("now"), "windows": options.get("observationWindows")},
                "facility": options.get("expectedFacilityId"),
                "operation": options.get("expectedOperationId"),
                "evidence_set": [a["basis_ref"] for a in bound],
                "claim_set": ["(observation, {IV})"],
                "status": "evaluated",
            },
            "profile_evaluation_gaps": [
                {
                    "target": target_ref,
                    "evaluation_context_ref": context_ref,
                    "token": g["token"],
                    "affected_claims": ["(observation, {IV})"],
                    "basis_refs": [],
                    "limitations": [g["detail"]],
                }
                for g in gaps
            ],
            "inherited_limitations": list(limitations),
            "fatal_conditions": [],
        }
    elif not fatal:
        fatal.append("E_APPRAISAL_INPUT_NOT_ASSEMBLED")

    observation_supported = any(
        f["base"] == "observation"
        and f["target_binding"] == "supported"
        and f["semantic_validation"] == "supported"
        for f in base_findings
    )
    ceiling_ok = boundary is not None and boundary["status"] == "supported" and boundary["ceiling_base"] == "observation"
    cc1_supported = bool(appraisal_input) and observation_supported and iv_validation == "supported" and ceiling_ok

    if appraisal_input is None:
        outcome = "NON_CONSTRUCTIBLE"
    elif cc1_supported:
        outcome = "CONSTRUCTED_CLAIM_SUPPORTED"
    elif group_indeterminate or iv_validation == "not-evaluated":
        outcome = "INDETERMINATE"
    else:
        outcome = "CONSTRUCTED_CLAIM_UNSUPPORTED"

    return {
        "bridge": BRIDGE_ID,
        "bridge_version": BRIDGE_VERSION,
        "typed_outcome": outcome,
        "cc1_supported": cc1_supported,
        "ceiling_base": boundary["ceiling_base"] if boundary else None,
        "iv_independence_validation": iv_validation,
        "accepted_observations": [
            {k: a[k] for k in ("index", "source_id", "role", "basis_ref")} for a in accepted
        ],
        "rejected_observations": [
            {k: a[k] for k in ("index", "source_id", "role", "reasons")} for a in rejected
        ],
        "source_requirements": requirement_results,
        "independence": independence,
        "gaps": gaps,
        "fatal_conditions": fatal,
        "expansion_refusals": expansion_refusals,
        "authority_refusals": authority_refusals,
        "admitted_expansions": admitted_expansions,
        "admitted_authority_conversions": admitted_authority_conversions,
        "appraisal_input": appraisal_input,
        "trace": trace,
    }
