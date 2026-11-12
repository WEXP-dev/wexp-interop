"""Bridge-specific tests. Open cases only; B-01 is never read or inferred."""

from __future__ import annotations

import copy
import hashlib
import json
import pathlib
import sys

import pytest
import yaml

HERE = pathlib.Path(__file__).resolve().parent
BRIDGE = HERE.parent
FIXTURES = BRIDGE.parent / "fixtures"
sys.path.insert(0, str(BRIDGE))

import bridge_lib  # noqa: E402

SPEC = yaml.safe_load((BRIDGE / "BRIDGE-CANDIDATE.yaml").read_text())
CASES = ["C-00", "H-01-a", "H-01-b", "H-01-c", "H-02", "H-03"]

FROZEN_FIXTURE_SHA256 = {
    "C-00": "b552da51858d0256a562e800a81a870435d6e136c9bc28833b962b6d3723fb3e",
    "H-01-a": "67556d28d272b4b01a73e1c1465248644dd7a05460fc149aa77df92cf36403a0",
    "H-01-b": "fbfb2046305ca6e9a8a3bbaf2e15c7acc30b8929d7625a3d90643c882276fe47",
    "H-01-c": "4737ed60826f981beed70a34303a3a79ea40207858e55c62f1ab81fe48271aa5",
    "H-02": "18350d7511035c0debd3ea5c7f02cabd3a095ba03be910dc10fa2b3b1cf314aa",
    "H-03": "ec7904648898cf8f6590cc7d1d223516ec38dde7365e4c96168061bb2192c7fb",
}


def load(case):
    return json.loads((FIXTURES / f"{case}.json").read_text())


@pytest.mark.parametrize("case", CASES)
def test_frozen_fixture_bytes_unchanged(case):
    """The bridge is validated against the frozen bytes or against nothing."""
    digest = hashlib.sha256((FIXTURES / f"{case}.json").read_bytes()).hexdigest()
    assert digest == FROZEN_FIXTURE_SHA256[case]


def test_spec_and_implementation_agree_on_elements():
    assert [e["element_id"] for e in SPEC["elements"]] == bridge_lib.ELEMENTS


def test_spec_and_implementation_agree_on_dependencies():
    """A drifting dependency graph would silently change what ablation means."""
    assert {e["element_id"]: list(e["depends_on"]) for e in SPEC["elements"]} == bridge_lib.DEPENDS


def test_all_eighteen_mapping_requirements_classified_exactly_once():
    reqs = SPEC["mapping_coverage"]["requirements"]
    assert [r["id"] for r in reqs] == [f"M-{n:02d}" for n in range(1, 19)]
    allowed = {"RESOLVED", "NOT_APPLICABLE", "FAIL_CLOSED_NON_CONSTRUCTIBLE"}
    assert all(r["classification"] in allowed for r in reqs)
    assert all(r["rationale"].strip() for r in reqs)


def test_all_sixteen_predicate_classes_defined():
    expected = {
        "normalization", "equality", "issuer", "identity", "correlation", "timing",
        "causal-provenance", "relying-party-policy", "trust-set", "evaluation-scope",
        "boundary", "grounding", "counter-evidence", "independence", "claim-ceiling",
        "non-authority",
    }
    assert set(SPEC["predicate_classes"]) == expected
    assert all(v["this_bridge"].strip() for v in SPEC["predicate_classes"].values())


def test_positive_control_constructs_the_claim():
    result = bridge_lib.evaluate(load("C-00"))
    assert result["typed_outcome"] == "CONSTRUCTED_CLAIM_SUPPORTED"
    assert result["cc1_supported"] is True
    assert result["ceiling_base"] == "observation"


@pytest.mark.parametrize("case", ["H-01-a", "H-01-b", "H-01-c", "H-02"])
def test_hostile_cases_refuse_the_claim(case):
    result = bridge_lib.evaluate(load(case))
    assert result["cc1_supported"] is False
    assert result["typed_outcome"] in {"INDETERMINATE", "CONSTRUCTED_CLAIM_UNSUPPORTED", "NON_CONSTRUCTIBLE"}


def test_h01a_fails_on_the_caid_premise_and_not_on_cryptography():
    result = bridge_lib.evaluate(load("H-01-a"))
    reasons = {r for o in result["rejected_observations"] for r in o["reasons"]}
    assert reasons == {"caid_premise_absent"}


def test_h01b_fails_on_instance_binding_with_signatures_intact():
    """If it failed on a signature it would be testing cryptography, not I-01."""
    result = bridge_lib.evaluate(load("H-01-b"))
    reasons = {r for o in result["rejected_observations"] for r in o["reasons"]}
    assert reasons and all(r.startswith("exact_binding_mismatch") for r in reasons)
    assert "signature_invalid" not in reasons


def test_h01c_isolates_evaluation_context_from_causal_provenance():
    """I-03b must be able to fail while I-03a holds, or the two are not separable."""
    result = bridge_lib.evaluate(load("H-01-c"))
    reasons = {r for o in result["rejected_observations"] for r in o["reasons"]}
    assert reasons == {"window_mismatch:exact"}
    assert not any(r.startswith("exact_binding_mismatch") for r in reasons)


def test_h02_preserves_the_phase_boundary():
    result = bridge_lib.evaluate(load("H-02"))
    assert result["cc1_supported"] is False
    supported = [
        f["base"]
        for f in (result["appraisal_input"] or {}).get("base_findings", [])
        if f["semantic_validation"] == "supported"
    ]
    assert "execution" not in supported and "invocation" not in supported


def test_h03_refuses_every_expansion_and_every_authority_conversion():
    result = bridge_lib.evaluate(load("H-03"))
    assert [e["disposition"] for e in result["expansion_refusals"]] == ["asserted_not_admitted"] * 2
    assert len(result["authority_refusals"]) == 5
    assert all(r["disposition"] == "refused" for r in result["authority_refusals"])
    assert result["admitted_expansions"] == []
    assert result["admitted_authority_conversions"] == []


@pytest.mark.parametrize("case", CASES)
def test_no_base_above_observation_is_ever_supported(case):
    result = bridge_lib.evaluate(load(case))
    for finding in (result["appraisal_input"] or {}).get("base_findings", []):
        if finding["base"] != "observation":
            assert finding["semantic_validation"] == "unsupported"


@pytest.mark.parametrize("case", CASES)
def test_ceiling_never_exceeds_observation(case):
    assert bridge_lib.evaluate(load(case))["ceiling_base"] in (None, "observation")


@pytest.mark.parametrize("case", CASES)
def test_bridge_emits_no_authority_bearing_field(case):
    blob = json.dumps(bridge_lib.evaluate(load(case))["appraisal_input"] or {})
    for token in ("permission", "authorization", "gate_admission", "delegated", "approval"):
        assert token not in blob


def test_signature_verification_is_real():
    """Flip one byte of a signed field; the observation must stop being accepted."""
    fixture = copy.deepcopy(load("C-00"))
    obs = fixture["emilia_input"]["observations"][1]
    obs["observed_effects"][0]["value"] = "9.9"
    result = bridge_lib.evaluate(fixture)
    reasons = {r for o in result["rejected_observations"] for r in o["reasons"]}
    assert "signature_invalid" in reasons
    assert result["cc1_supported"] is False


def test_evaluation_does_not_mutate_the_fixture():
    fixture = load("C-00")
    before = json.dumps(fixture, sort_keys=True)
    bridge_lib.evaluate(fixture)
    assert json.dumps(fixture, sort_keys=True) == before


def test_ablation_is_deterministic():
    fixture = load("C-00")
    for element in bridge_lib.ELEMENTS:
        first = bridge_lib.evaluate(fixture, disabled={element})
        second = bridge_lib.evaluate(fixture, disabled={element})
        assert first["typed_outcome"] == second["typed_outcome"]
        assert first["cc1_supported"] == second["cc1_supported"]


def test_removing_the_binding_guards_together_would_break_i01():
    """Recorded as a diagnostic in the ablation plan; asserted here so it stays true."""
    result = bridge_lib.evaluate(load("H-01-b"), disabled={"BE-04", "BE-06"})
    assert result["cc1_supported"] is True


def test_removing_the_ceiling_guard_admits_the_expansion():
    result = bridge_lib.evaluate(load("H-03"), disabled={"BE-15"})
    assert result["admitted_expansions"] == ["completion", "independent_verification"]


def test_removing_the_non_authority_guard_admits_the_conversions():
    result = bridge_lib.evaluate(load("H-03"), disabled={"BE-16"})
    assert len(result["admitted_authority_conversions"]) == 5


def test_b01_fixture_is_packaged_post_reveal_but_not_loaded_by_open_case_tests():
    assert (FIXTURES / "B-01.json").is_file()
    assert "B-01" not in CASES


def test_no_bridge_source_mentions_a_committed_blind_digest():
    committed = "8a5164e1a5c3924be201b703a47be4882b09d1abe355128eb1ff7e02c9868e66"
    for path in list(BRIDGE.glob("*.py")) + list(BRIDGE.glob("*.yaml")):
        assert committed not in path.read_text()
