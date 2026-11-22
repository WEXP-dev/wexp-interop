#!/usr/bin/env python3
"""Session-A preparation only; never imports or runs a Core appraiser.

Run with python -I, an exact clean AEP checkout, and a NEW output directory.
This script independently checks the PROFILE predicates using public data.
It is not called during session C: C uses the committed inputs unchanged.
"""
import argparse
import copy
import datetime
import hashlib
import importlib.metadata
import json
from pathlib import Path
import subprocess
import sys

AEP_PIN = "f6c88be63c5aa12b8e8f6bf35a378a6a5fca9cd4"
PID = "urn:wexp:proposal:aep-applicability-001:profile:1:r4"
CAPS = ("carrier-mapping", "authenticity", "target-binding", "boundary-grounding",
        "observation-support", "intent-support", "invocation-support",
        "execution-support", "provenance-support", "independent-verification",
        "composition", "counter-evidence")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def atom(local):
    return [PID, local]


def target_for(packet):
    action = packet["action"]
    args = action["args"]
    assert type(args["amount"]) is int
    values = [packet["agent_pub"], action["method"], args["order_id"], args["amount"], args["currency"]]
    assert all(type(v) is str and v for i, v in enumerate(values) if i != 3)
    return "aep-action:" + json.dumps(values, ensure_ascii=False, separators=(",", ":"))


def normalize(packet, file_sha, context):
    target = target_for(packet)
    cid = f"urn:wexp:aep-applicability-001:context:{context}:r4"
    ref = atom("aep-file:sha256:" + file_sha)
    report_limit = atom("self-report-is-not-external-effect")
    base = {"target": target, "evaluation_context_ref": cid,
            "target_binding": "supported", "basis_refs": [ref], "reasons": []}
    boundary = dict(copy.deepcopy(base), status="unsupported", grounding="attributed",
                    limitations=[atom("boundary-control-not-established"), atom("no-boundary-grounding-profile")])
    observation = dict(copy.deepcopy(base), base="observation", semantic_validation="supported",
                       limitations=[report_limit])
    execution = dict(copy.deepcopy(base), base="execution", semantic_validation="not-evaluated",
                     limitations=[report_limit, atom("execution-assessment-material-unavailable")])
    return {
        "semantics_version": "wexp-core-2", "target": target,
        "asserted_claim": {"base": "execution", "qualifiers": []},
        "evaluation_context": {"id": cid, "evaluated_at": "unix:1750000100",
            "trust_configuration": f"urn:wexp:aep-applicability-001:trust:{context}:r4",
            "profile_identifiers": [PID]},
        "boundary_finding": boundary, "base_findings": [observation, execution],
        "qualifier_findings": [], "recorder_relations": [],
        "counter_evidence": [{"status": "not-supplied", "affected_claims": [],
                              "basis_refs": [], "reasons": [], "limitations": []}],
        "evaluation_scope": [{"capability": c, "status": "not-evaluated" if c == "execution-support" else "evaluated"} for c in CAPS],
        "profile_evaluation_gaps": [],
        "inherited_limitations": [atom("bounded-two-packet-domain")],
        "fatal_conditions": []}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    source, out = args.source.resolve(), args.out.resolve()
    if out.exists():
        raise SystemExit("--out must be new; frozen inputs are never overwritten")
    actual = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
    assert actual == AEP_PIN
    assert subprocess.check_output(["git", "-C", str(source), "status", "--porcelain", "--untracked-files=no"], text=True) == ""
    sys.path.insert(0, str(source))
    import aep
    from aep import canonical, keys, package
    assert Path(aep.__file__).resolve() == source / "aep/__init__.py"
    trust = json.loads((source / "keys/trusted_issuers.json").read_text())["issuers"]
    preparations, packets, diagnostics = {}, {}, {}
    for name, amount, refund, nonce in (("good", 250, "RF-22317", "aep-nonce-0001"),
                                      ("exceed-scope", 9000, "RF-90001", "aep-nonce-0002")):
        path = source / f"samples/{name}.aep.json"
        raw = path.read_bytes()
        p = json.loads(raw)
        assert p["action"]["method"] == "issue_refund"
        assert p["action"]["args"] == {"order_id": "ORD-4471", "amount": amount, "currency": "EUR"}
        assert type(p["action"]["args"]["amount"]) is int
        assert p["outcome"]["status"] == "ok" and p["outcome"]["refund_id"] == refund
        assert p["nonce"] == nonce and p["mandate"]["body"]["scope"]["max_amount"] == 1000
        cb, mb = p["credential"]["body"], p["mandate"]["body"]
        checks = {
            "receipt_hash": package.receipt_hash(p) == p["receipt_hash"],
            "agent_signature": keys.verify(p["agent_pub"], package._receipt_core(p), p["aep_sig"]),
            "action_measurement": canonical.digest(p["action"]) == p["measurements"]["action_sha256"],
            "outcome_measurement": canonical.digest(p["outcome"]) == p["measurements"]["outcome_sha256"],
            "issuer_in_pinned_public_trust_store": trust.get(cb["issuer_id"]) == cb["issuer_pub"],
            "credential_signature": keys.verify(cb["issuer_pub"], cb, p["credential"]["sig"]),
            "principal_identity_link": cb["principal_id"] == mb["principal_id"],
            "mandate_signature": keys.verify(cb["principal_pub"], mb, p["mandate"]["sig"]),
            "agent_identity_link": mb["agent_pub"] == p["agent_pub"] and mb["agent_id"] == p["agent_id"],
            "target_tuple_extracted_from_verified_action": bool(target_for(p)),
        }
        assert all(checks.values()), checks
        packets[name] = (p, sha(raw))
        preparations[name] = {"file_sha256": sha(raw), "checked_values": {"action": p["action"],
            "outcome": p["outcome"], "nonce": p["nonce"], "max_amount": mb["scope"]["max_amount"]},
            "binding_predicates": checks,
            "source_lines": ["samples/" + name + ".aep.json:5-20,47,54", "aep/package.py:95-111", "aep/mandate.py:149-160"]}
    assert packets["good"][0]["mandate"] == packets["exceed-scope"][0]["mandate"]
    hashes = {}
    for case, source_name in (("a", "good"), ("b", "good"), ("c", "exceed-scope")):
        p, digest = packets[source_name]
        for context in ("strict", "attrib"):
            rel = f"inputs/{case}-{context}.json"
            normalized = normalize(p, digest, context)
            write(out / rel, normalized)
            hashes[rel] = sha((out / rel).read_bytes())
            diagnostics[f"{case}-{context}"] = {"source_sample": source_name, "target": normalized["target"],
                "claimed_effect": {"action": p["action"], "self_reported_outcome": p["outcome"]},
                "binding_predicate_passed": True, "grounding": "attributed",
                "grounding_admission_passed": context == "attrib",
                "boundary_control_coverage_material_present": False,
                "boundary_sufficiency_assessment_completed": True,
                "boundary_predicate_passed": False, "boundary_status": "unsupported",
                "ceiling_justified": False, "execution_occurrence_assessment_performed": False,
                "execution_gap": "execution-assessment-material-unavailable",
                "role_candidates": {"observation": True, "intent": False, "invocation": False,
                    "execution": True, "PROV(execution)": False, "IV(any base)": False},
                "candidate_search_completed": True,
                "source_lines": [f"samples/{source_name}.aep.json:1-59", "aep/mandate.py:81-88,149-160",
                    "draft-sokolov-rats-aep-composition-06.txt:117-126,346-348"],
                "core_xml_lines": [143, 149, 358, 359, 360, 361, 405, 406, 775, 778]}
    for context in ("strict", "attrib"):
        assert (out / f"inputs/a-{context}.json").read_bytes() == (out / f"inputs/b-{context}.json").read_bytes()
    write(out / "INPUT-HASHES.json", {"algorithm": "sha256", "files": hashes})
    write(out / "evidence/MAPPING-DIAGNOSTICS.json", diagnostics)
    write(out / "evidence/A-PREPARATION.json", {"session": "A", "wall_clock_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "logical_now": 1750000100, "argv": sys.argv, "python": sys.version, "executable": sys.executable,
        "packages": {x: importlib.metadata.version(x) for x in ("cryptography", "cffi", "pycparser")},
        "source_checkout": str(source), "source_commit": actual, "aep_file": aep.__file__,
        "source_tracked_clean": True, "same_mandate_confirmed": True,
        "sample_checks": preparations, "core_appraisers_imported": False, "core_appraisers_executed": False,
        "core_appraiser_outputs_used": False, "native_verify_py_executed": False,
        "consumed_state_read_or_written": False,
        "verification_scope": "Public-data cryptographic preparation and field checks only; no occurrence claim."})
    print(json.dumps({"prepared": len(hashes), "aep_file": aep.__file__, "all_binding_predicates": True}))


if __name__ == "__main__":
    main()
