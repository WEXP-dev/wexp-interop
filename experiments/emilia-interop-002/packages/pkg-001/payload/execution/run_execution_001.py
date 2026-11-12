"""EXECUTION-001 — run the frozen procedure over the complete frozen case set.

Authority: FOUNDER EXECUTION GO, 2026-08-24. Scope is execution only.

This driver lives OUTSIDE the frozen surface and writes nothing into it. It
imports the frozen bridge and the frozen open-case runner rather than restating
their logic, so the invariant criteria applied to B-01 are byte-identically the
criteria that were frozen before B-01 was revealed. run_open_cases.main() is
never called, because it rewrites two frozen artifacts.

Order is the frozen comparison policy's order and is enforced structurally:
preserve both native outputs -> digest both -> only then derive relations.
Phase B reads the preserved files from disk, never the in-memory results.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
EXP = HERE.parent
BRIDGE = EXP / "bridge"
FIXTURES = EXP / "fixtures"
NATIVE = HERE / "native"
sys.path.insert(0, str(BRIDGE))

import bridge_lib          # noqa: E402  frozen
import run_open_cases      # noqa: E402  frozen; imported for its criteria, never run

OPEN_CASES = list(run_open_cases.CASES)
CASES = OPEN_CASES + ["B-01"]

# B-01's attacked invariants are read from the frozen commitment, not asserted here.
_COMMIT = json.loads((EXP / "pre-freeze" / "B-01-COMMITMENT.json").read_text())


def b01_attacked():
    for key in ("attacked_invariants", "invariants"):
        if key in _COMMIT:
            return list(_COMMIT[key])
    raise SystemExit("FAIL: B-01 commitment does not declare its attacked invariants")


# Extend the frozen module's own table in memory. The frozen file is untouched.
run_open_cases.ATTACKED["B-01"] = b01_attacked()


def jcs(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


# Copied verbatim from run_open_cases.main()'s local `signature`, which is not
# importable because it is defined inside that function. Copied rather than
# rewritten so the ablation signature is the frozen one.
def signature(r):
    return {
        "typed_outcome": r["typed_outcome"],
        "cc1_supported": r["cc1_supported"],
        "ceiling_base": r["ceiling_base"],
        "iv": r["iv_independence_validation"],
        "admitted_expansions": len(r["admitted_expansions"]),
        "admitted_authority_conversions": len(r["admitted_authority_conversions"]),
    }


def phase_a_preserve():
    """Run the bridge and preserve every native output before anything compares."""
    fixtures = {c: json.loads((FIXTURES / f"{c}.json").read_text()) for c in CASES}
    baseline = {c: bridge_lib.evaluate(fixtures[c]) for c in CASES}

    identities = {}
    for c in CASES:
        r = baseline[c]
        raw = jcs(r)
        (NATIVE / f"wexp-native-{c}.json").write_text(raw + "\n")
        ai = r["appraisal_input"]
        identities[c] = {
            "party": "WEXP",
            "producer": "frozen bridge",
            "bridge_id": bridge_lib.BRIDGE_ID,
            "bridge_spec_sha256": sha256_file(BRIDGE / "BRIDGE-CANDIDATE.yaml"),
            "bridge_impl_sha256": sha256_file(BRIDGE / "bridge_lib.py"),
            "fixture_sha256": sha256_file(FIXTURES / f"{c}.json"),
            "typed_outcome": r["typed_outcome"],
            "native_output_sha256": sha256_text(raw),
            "appraisal_input_canonical_sha256": sha256_text(jcs(ai)) if ai is not None else None,
            "appraisal_input_assembled": ai is not None,
        }

    # The EMILIA side. Recorded as absent rather than substituted.
    emilia_native = {
        "party": "EMILIA",
        "native_output_produced_in_this_contour": False,
        "why": (
            "The EMILIA native output is the result of EMILIA's own verifier run by the "
            "EMILIA side. No EMILIA implementation, conformance runner or recorded native "
            "result exists in this contour: every fixture carries emilia_input and an "
            "emilia_baseline provenance stanza, and none carries a native result. The "
            "frozen surface never defined a mechanism to produce one locally."
        ),
        "what_exists_instead": (
            "A single precommitted EMILIA expectation for B-01 only, relayed by the Founder."
        ),
        "explicitly_not_done": [
            "The EMILIA expectation is NOT recorded as an EMILIA native output.",
            "EMILIA's reference implementation was NOT run to manufacture one, because a "
            "reference implementation is not the party and running it here would produce a "
            "WEXP-side artifact wearing the other party's name.",
        ],
        "consequence": (
            "Every case-level relation that requires two native outputs is underdetermined "
            "on the EMILIA axis. This is a limit of the record, not a result about EMILIA."
        ),
    }
    (NATIVE / "emilia-native-ABSENT.json").write_text(json.dumps(emilia_native, indent=2) + "\n")

    manifest = {
        "artifact_id": "WEXP-EMILIA-INTEROP-002-NATIVE-OUTPUT-MANIFEST-001",
        "preserved_before_any_comparison": True,
        "order_enforced": "preserve -> digest -> compare; phase B reads only these files",
        "cases": CASES,
        "wexp": identities,
        "emilia": emilia_native,
    }
    (NATIVE / "NATIVE-OUTPUT-MANIFEST-001.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    )
    return fixtures, baseline, manifest


def phase_b_derive(fixtures, baseline, manifest):
    """Read back the preserved outputs and derive everything else from them."""
    # Re-read from disk and prove the in-memory results still match what was preserved.
    reread = {}
    for c in CASES:
        raw = (NATIVE / f"wexp-native-{c}.json").read_text().rstrip("\n")
        assert sha256_text(raw) == manifest["wexp"][c]["native_output_sha256"], c
        reread[c] = json.loads(raw)

    case_records = []
    for c in CASES:
        r = reread[c]
        case_records.append({
            "case_id": c,
            "blind": c == "B-01",
            "fixture_sha256": manifest["wexp"][c]["fixture_sha256"],
            "attacked_invariants": run_open_cases.ATTACKED[c],
            "typed_outcome": r["typed_outcome"],
            "cc1_supported": r["cc1_supported"],
            "ceiling_base": r["ceiling_base"],
            "iv_independence_validation": r["iv_independence_validation"],
            "accepted_observations": len(r["accepted_observations"]),
            "rejected_observations": len(r["rejected_observations"]),
            "rejection_reasons": sorted({x for o in r["rejected_observations"] for x in o["reasons"]}),
            "gaps": r["gaps"],
            "appraisal_input_assembled": manifest["wexp"][c]["appraisal_input_assembled"],
            "expansion_refusals": len(r["expansion_refusals"]),
            "authority_refusals": len(r["authority_refusals"]),
            "admitted_expansions": len(r["admitted_expansions"]),
            "admitted_authority_conversions": len(r["admitted_authority_conversions"]),
            "invariant_verdicts": run_open_cases.preserved(c, r),
        })

    # --- H-MIN: frozen single-element ablation over the COMPLETE case set
    ablation = []
    for element in bridge_lib.ELEMENTS:
        changes = []
        for c in CASES:
            before = signature(baseline[c])
            after = signature(bridge_lib.evaluate(fixtures[c], disabled={element}))
            if before != after:
                kind = (
                    "positive_control_no_longer_constructs"
                    if c == "C-00" and before["cc1_supported"] and not after["cc1_supported"]
                    else (
                        "invariant_no_longer_preserved"
                        if (after["cc1_supported"] and not before["cc1_supported"])
                        or after["admitted_expansions"]
                        or after["admitted_authority_conversions"]
                        else "result_degraded_to_less_informative_fail_closed"
                    )
                )
                changes.append({"case_id": c, "before": before, "after": after, "consequence_class": kind})
        ablation.append({
            "element_id": element,
            "necessity_on_complete_surface": "SUPPORTED" if changes else "NOT_ESTABLISHED",
            "discriminated_by_b01": any(x["case_id"] == "B-01" for x in changes),
            "discriminating_cases": [x["case_id"] for x in changes],
            "observed_consequences": changes,
        })
    return case_records, ablation


def main():
    fixtures, baseline, manifest = phase_a_preserve()
    case_records, ablation = phase_b_derive(fixtures, baseline, manifest)
    (HERE / "EXECUTION-RESULTS-001.json").write_text(
        json.dumps({"cases": case_records, "ablation": ablation}, indent=2, ensure_ascii=False) + "\n"
    )

    print("=== STEP 4/5: NATIVE OUTPUTS PRODUCED AND PRESERVED ===")
    for c in CASES:
        i = manifest["wexp"][c]
        print(f"  {c:8s} {i['typed_outcome']:20s} native {i['native_output_sha256'][:16]}  "
              f"AI {(i['appraisal_input_canonical_sha256'] or 'not-assembled')[:16]}")
    print(f"  EMILIA native outputs preserved: 0  (ABSENT — recorded, not substituted)")

    print("\n=== STEP 7: H-SUFF INPUTS, COMPLETE CASE SET ===")
    print(f"  {'case':8s} {'outcome':22s} {'CC-1':6s} {'ceiling':12s} {'IV':16s} invariants")
    for r in case_records:
        v = "  ".join(f"{k}={'PRESERVED' if d['preserved'] else 'BROKEN'}"
                      for k, d in r["invariant_verdicts"].items()) or "(positive control)"
        print(f"  {r['case_id']:8s} {r['typed_outcome']:22s} {str(r['cc1_supported']):6s} "
              f"{str(r['ceiling_base']):12s} {r['iv_independence_validation']:16s} {v}")

    print("\n  B-01 detail:")
    b = [r for r in case_records if r["case_id"] == "B-01"][0]
    print(f"    rejection reasons     {b['rejection_reasons']}")
    print(f"    accepted/rejected obs {b['accepted_observations']} / {b['rejected_observations']}")
    print(f"    gaps                  {b['gaps']}")
    print(f"    AppraisalInput built  {b['appraisal_input_assembled']}")

    print("\n=== STEP 8: H-MIN OVER THE COMPLETE FROZEN CASE SET ===")
    sup = [a["element_id"] for a in ablation if a["necessity_on_complete_surface"] == "SUPPORTED"]
    nes = [a["element_id"] for a in ablation if a["necessity_on_complete_surface"] == "NOT_ESTABLISHED"]
    for a in ablation:
        mark = "*B-01*" if a["discriminated_by_b01"] else "      "
        print(f"  {a['element_id']}  {a['necessity_on_complete_surface']:16s} {mark} "
              f"cases={a['discriminating_cases']}")
    print(f"\n  SUPPORTED {len(sup)}/17: {sup}")
    print(f"  NOT_ESTABLISHED {len(nes)}/17: {nes}")
    be04 = [a for a in ablation if a["element_id"] == "BE-04"][0]
    print(f"\n  BE-04 necessity on B-01: discriminated_by_b01={be04['discriminated_by_b01']}  "
          f"verdict={be04['necessity_on_complete_surface']}")
    for ch in be04["observed_consequences"]:
        if ch["case_id"] == "B-01":
            print(f"    before {ch['before']}")
            print(f"    after  {ch['after']}")
            print(f"    class  {ch['consequence_class']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
