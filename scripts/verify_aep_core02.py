#!/usr/bin/env python3
"""Verify the AEP/Core-02 public export and compare saved results without running appraisers.

SPDX-License-Identifier: MIT
"""

import argparse
import hashlib
import json
from pathlib import Path
import zipfile


EXPERIMENT = "aep-applicability-001"
DEFAULT_PACKAGE = Path(__file__).resolve().parents[1] / "experiments" / EXPERIMENT / "packages/pkg-001"
ARCHIVE = "source-archive/AEP-CORE02-PUBLIC.zip"
ARCHIVE_SHA256 = "126cccbc0d19753846e4997a18641a0b7fc314f81c0fa530522e458d3a8daa4e"
INVENTORY_SHA256 = "4fb3fe4bcbca6d0fe9c9f1bfed24c644f9c85351d1875a06eb910ed6d9a11cac"
PUBLIC_RUN_SHA256 = "eee35c5431ed454765485b8ea2caf827657c6d0bd64461f1cf6600ad8f9bacf2"
CASES = tuple(f"{case}-{context}" for case in "abc" for context in ("strict", "attrib"))
COMPONENTS = {
    "semantics_version", "verdict", "fatal_reasons", "target", "asserted_claim",
    "asserted_claim_supported", "support_entries", "supported_claims", "maximal_supported_claims",
    "support_relations", "boundary_ceiling", "boundary_grounding", "recorder_relations",
    "substantive_reasons", "evaluation_gaps", "evaluation_gap_entries", "counter_evidence",
    "inherited_limitations", "evaluation_context", "evaluation_scope",
}
SET_FIELDS = {
    "qualifiers", "profile_identifiers", "basis_refs", "reasons", "limitations", "base_findings",
    "qualifier_findings", "recorder_relations", "counter_evidence", "profile_evaluation_gaps",
    "inherited_limitations", "fatal_conditions", "affected_claims", "fatal_reasons", "support_entries",
    "supported_claims", "maximal_supported_claims", "support_relations", "substantive_reasons",
    "evaluation_gaps", "evaluation_gap_entries",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def unique_object(pairs):
    obj = dict(pairs)
    require(len(obj) == len(pairs), "duplicate JSON key")
    return obj


def read_json(path):
    return json.loads(path.read_bytes(), object_pairs_hook=unique_object)


def logical(value, field=None):
    """Use the frozen comparison rules: typed scalars, declared sets, keyed scope and ordered atoms."""
    if isinstance(value, dict):
        return "object", frozenset((key, logical(item, key)) for key, item in value.items())
    if isinstance(value, list):
        if field == "evaluation_scope":
            require(all(isinstance(item, dict) and item.keys() == {"capability", "status"} for item in value),
                    "malformed scope")
            scope = {logical(item["capability"]): logical(item["status"]) for item in value}
            require(len(scope) == len(value), "duplicate scope capability")
            return "scope", frozenset(scope.items())
        members = tuple(logical(item) for item in value)
        if field in SET_FIELDS:
            require(len(members) == len(set(members)), f"duplicate member of {field}")
            return "set", frozenset(members)
        return "array", members
    if type(value) in (int, float):
        return "number", value
    return type(value).__name__, value


def compare_components(left, right):
    require(left.keys() == COMPONENTS and right.keys() == COMPONENTS, "twenty Core result components required")
    return sorted(key for key in COMPONENTS if logical(left[key], key) != logical(right[key], key))


def verify_export(package, record):
    payload = package / "payload"
    archive = package / ARCHIVE
    inventory = package / "evidence/PUBLIC-INVENTORY.json"
    for path in (payload, archive.parent, archive, inventory.parent, inventory):
        require(not path.is_symlink(), f"symlink at {path.name}")
    require(payload.is_dir(), "missing payload")
    require(sha(archive.read_bytes()) == ARCHIVE_SHA256, "public archive digest")
    require(sha(inventory.read_bytes()) == INVENTORY_SHA256, "public inventory digest")
    artifact = record["artifact"]
    require((artifact["path"], artifact["bytes"], artifact["sha256"]) ==
            (ARCHIVE, archive.stat().st_size, ARCHIVE_SHA256), "archive/card mismatch")
    files = read_json(inventory)["files"]
    extracted = set()
    for path in payload.rglob("*"):
        require(not path.is_symlink() and (path.is_file() or path.is_dir()), "non-regular payload entry")
        if path.is_file():
            extracted.add(path.relative_to(payload).as_posix())
    require(files.keys() == extracted, "public payload/inventory file set")
    prefix = EXPERIMENT + "/"
    with zipfile.ZipFile(archive) as source:
        members = source.namelist()
        require(len(members) == len(files) and set(members) == {prefix + name for name in files},
                "public archive/inventory file set")
        for name, entry in files.items():
            raw = (payload / name).read_bytes()
            require(source.read(prefix + name) == raw, f"extracted bytes: {name}")
            require(len(raw) == entry["bytes"] and sha(raw) == entry["sha256"], f"inventory entry: {name}")
            identical = entry["source_sha256"] == entry["sha256"]
            require(entry["treatment"] == ("exact" if identical else "projected"), f"export treatment: {name}")
    require(record["payload"]["path"] == "payload" and record["payload"]["regular_files"] == len(files),
            "payload/card mismatch")
    return files


def verify_source_pins(payload, record):
    source = read_json(payload / "SOURCE-PINS.json")
    expected = {}
    for repo in (source["aep_sandbox"], *source["appraisers_for_session_C_only"].values()):
        expected[repo["repository"] + "/tree/" + repo["commit"]] = "git-commit:" + repo["commit"]
    for spec in source["specifications"]:
        require(sha((payload / spec["path"]).read_bytes()) == spec["sha256"], "specification digest")
        expected[spec["url"]] = "sha256:" + spec["sha256"]
    declared = [(p["url"], p["identity"]) for p in record["source_pins"]]
    require(len(declared) == 5 and dict(declared) == expected, "source pins/card mismatch")


def check_freezes(payload, files):
    coverage = {}
    for name in ("A-FREEZE.json", "expectations/FREEZE.json"):
        bindings = read_json(payload / name)["files"]
        counts = {"bound_in_original": len(bindings), "exact": 0, "projected": 0, "omitted": 0}
        for path, original_sha in bindings.items():
            entry = files.get(path)
            if entry is None:
                counts["omitted"] += 1
            else:
                require(original_sha == entry["source_sha256"], "original freeze binding: " + path)
                counts[entry["treatment"]] += 1
        coverage[name] = counts
    return coverage


def check_native(payload):
    # Each native case comes from the sandbox verification transcript and its saved nonce state.
    # No observed refund or external service receipt appears in either signed sample.
    raw_dir = payload / "evidence/aep"
    samples = payload / "evidence/basis/aep-sandbox/samples"
    packet_fields = {
        "aep_version", "agent_id", "agent_pub", "action", "outcome", "measurements", "credential",
        "mandate", "nonce", "issued_at", "prev_hash", "aep_sig", "receipt_hash",
    }
    for sample in ("good", "exceed-scope"):
        packet = read_json(samples / f"{sample}.aep.json")
        require(set(packet) == packet_fields and set(packet["measurements"]) == {"action_sha256", "outcome_sha256"},
                f"signed sample fields: {sample}")
    consumed = read_json(samples / "good.aep.json")["nonce"] + "\n"
    native = {}
    saved = read_json(payload / "evidence/AEP-OUTCOMES.json")["cases"]
    require(saved.keys() == {"a", "b", "c"}, "native cases")
    for case, sample, decision, rc in (("a", "good", "ALLOW", 0), ("b", "good", "DENY  reason=replayed", 2),
                                       ("c", "exceed-scope", "DENY  reason=scope_violation", 2)):
        raw = (raw_dir / f"{case}.stdout.txt").read_bytes().decode("utf-8")
        lines = raw.splitlines()
        evidence = saved[case]
        require(evidence["stdout"] == raw and evidence["sample"] == sample and
                evidence["verdict"] == decision.split()[0] and evidence["consume"] is (case != "c") and
                evidence["reason"] == (None if rc == 0 else decision.split("=")[1]) and
                type(evidence["rc"]) is int and evidence["rc"] == rc == evidence["returncode"],
                f"native record: {case}")
        require([s for s in lines if s.startswith("VERDICT:")] == [f"VERDICT: {decision}  ({sample}.aep.json)"],
                f"sandbox verdict: {case}")
        require((raw_dir / f"{case}.rc.txt").read_bytes() == f"{rc}\n".encode(), f"sandbox exit: {case}")
        before = (raw_dir / f"{case}.state-before.txt").read_text(encoding="utf-8")
        after = (raw_dir / f"{case}.state-after.txt").read_text(encoding="utf-8")
        require(before == ("" if case == "a" else consumed) and after == consumed, f"sandbox nonce state: {case}")
        native[case] = {"verdict_line": f"VERDICT: {decision}  ({sample}.aep.json)", "exit": rc}
    return native


def compare_saved(payload):
    published = read_json(payload / "comparison.json")
    native = read_json(payload / "evidence/AEP-OUTCOMES.json")["cases"]
    require(published["cases"].keys() == set(CASES), "published comparison cases")
    inputs = read_json(payload / "INPUT-HASHES.json")["files"]
    require(inputs.keys() == {f"inputs/{case}.json" for case in CASES}, "frozen input names")
    require(len(set(inputs.values())) == 4, "distinct input byte strings")
    for context in ("strict", "attrib"):
        require(inputs[f"inputs/a-{context}.json"] == inputs[f"inputs/b-{context}.json"], "replay input identity")
    diagnostics = read_json(payload / "evidence/MAPPING-DIAGNOSTICS.json")
    require(diagnostics.keys() == set(CASES), "mapping diagnostic cases")
    case_results = {}
    for case in CASES:
        key = f"inputs/{case}.json"
        require(sha((payload / key).read_bytes()) == inputs[key], f"input digest: {case}")
        mapped = read_json(payload / key)
        roles = {item["base"]: item["semantic_validation"] for item in mapped["base_findings"]}
        diag = diagnostics[case]
        require(roles == {"observation": "supported", "execution": "not-evaluated"} and
                mapped["boundary_finding"]["status"] == "unsupported" and
                mapped["boundary_finding"]["grounding"] == "attributed", f"mapped roles and boundary: {case}")
        require(diag["grounding_admission_passed"] is case.endswith("-attrib") and
                diag["boundary_control_coverage_material_present"] is False and diag["boundary_status"] == "unsupported"
                and diag["execution_occurrence_assessment_performed"] is False, f"mapping diagnostic: {case}")
        expected = read_json(payload / f"expectations/v1/{case}.json")
        require(set(expected) == COMPONENTS and expected["boundary_ceiling"] == "unavailable", f"expectation: {case}")
        results = {}
        for engine in ("ref", "check"):
            directory = payload / "evidence/core" / engine
            require((directory / f"{case}.rc.txt").read_bytes() == b"0\n", f"appraiser exit: {engine}/{case}")
            output = read_json(directory / f"{case}.stdout.json")
            require(set(output) == COMPONENTS and output["asserted_claim_supported"] is False
                    and output["verdict"] == "downgrade" and output["boundary_grounding"] == "attributed"
                    and output["boundary_ceiling"] is None and output["substantive_reasons"] == ["E_BOUNDARY_NOT_SUPPORTED"]
                    and output["evaluation_gaps"] == ["E_BASE_NOT_EVALUATED"], f"Core appraisal: {engine}/{case}")
            results[engine] = output
        deltas = {}
        for left, right, name in ((results["ref"], results["check"], "ref_vs_check"),
                                  (expected, results["ref"], "expected_vs_ref"),
                                  (expected, results["check"], "expected_vs_check")):
            deltas[name] = compare_components(left, right)
        require(deltas == {"ref_vs_check": [], "expected_vs_ref": ["boundary_ceiling"],
                           "expected_vs_check": ["boundary_ceiling"]}, f"component comparisons: {case}")
        row = published["cases"][case]
        columns = row["columns"]
        originals = {"expected": expected, **results}
        require(columns["aep_verifier_outcome"] == native[case[0]] and columns["mapping_diagnostic"] == diag
                and columns["core_02_appraisal"] == originals, f"comparison columns: {case}")
        require(row["components"].keys() == COMPONENTS and row["all_twenty_components_match"] is False,
                f"published component set or agreement: {case}")
        for key, component in row["components"].items():
            for who, original in originals.items():
                require(logical(component[who], key) == logical(original[key], key), f"stored component: {case}/{key}")
            for flag, pair in (("expected_eq_ref", "expected_vs_ref"), ("expected_eq_check", "expected_vs_check"),
                               ("ref_eq_check", "ref_vs_check")):
                require(component[flag] is (key not in deltas[pair]), f"comparison flag: {case}/{key}/{flag}")
        case_results[case] = deltas
    summary = published["summary"]
    require(summary["case_count"] == len(CASES) and summary["component_count_per_case"] == len(COMPONENTS),
            "comparison summary counts")
    for key, pair in (("expected_ref_mismatches", "expected_vs_ref"), ("expected_check_mismatches", "expected_vs_check"),
                      ("ref_check_mismatches", "ref_vs_check")):
        require(summary[key] == sum(len(delta[pair]) for delta in case_results.values()), "comparison summary: " + key)
    return case_results


def check_public_repeat(package, record, historical_differences):
    relative = "evidence/public-run/RUN-RECORD.json"
    report = package / relative
    declared = relative in record["verification"]["evidence"]
    require(declared == report.parent.exists(), "public repeat presence/card mismatch")
    if not declared:
        return None

    raw = report.parent / "evidence"
    original = package / "payload/evidence"
    require(not report.is_symlink() and not report.parent.is_symlink(), "public repeat symlink")
    require(sha(report.read_bytes()) == PUBLIC_RUN_SHA256, "public repeat report digest")
    saved = read_json(report)
    commit = saved["preparation_commit"]
    pins = read_json(package / "payload/SOURCE-PINS.json")
    required = {"aep-sandbox": pins["aep_sandbox"]["commit"]}
    required.update({name: pin["commit"] for name, pin in pins["appraisers_for_session_C_only"].items()})
    require(saved["implementation_commits"] == required, "public repeat implementation pins")

    files = [f"core/{engine}/{case}.{suffix}" for engine in ("ref", "check") for case in CASES
             for suffix in ("stdout.json", "rc.txt")]
    files += [f"aep/{case}.{suffix}.txt" for case in "abc" for suffix in ("stdout", "rc", "state-before", "state-after")]
    actual = set()
    for item in raw.rglob("*"):
        require(not item.is_symlink() and (item.is_dir() or item.is_file()), "unsafe public repeat entry")
        if item.is_file():
            actual.add(item.relative_to(raw).as_posix())
    require(actual == set(files), "public repeat raw file set")
    hashes = {}
    for name in files:
        data = (raw / name).read_bytes()
        require(data == (original / name).read_bytes(), "public repeat output: " + name)
        hashes[name] = sha(data)
    require(saved["output_sha256"] == hashes and saved["changed_raw_files_vs_historical"] == []
            and saved["status"] == "PASS" and saved["logical_now"] == 1750000100, "public repeat result")
    require(saved["ref_check_differing_components"] ==
            {case: row["ref_vs_check"] for case, row in historical_differences.items()}, "public repeat ref/check")
    expected_deltas = {engine: {case: row["expected_vs_" + engine] for case, row in historical_differences.items()}
                       for engine in ("ref", "check")}
    require(saved["frozen_expectation_differing_components"] == expected_deltas, "public repeat ref/expectations")
    return {"historical_raw_files_matched": len(files), "preparation_commit_recorded": commit}


def verify_package(package, record=None):
    package = Path(package).resolve()
    if record is None:
        record = read_json(package / "record.json")
    require((record["experiment_id"], record["package_id"], record["verification"]["profile"]) ==
            (EXPERIMENT, "pkg-001", "aep-core02-applicability-v1"), "profile/card identity")
    status = record["status"]
    require(status["execution"] == "local-run-completed" and status["comparison"] == "no-local-decision-difference"
            and status["independent_reproduction"] == "not-performed"
            and record["verification"]["implementation_execution_performed"] is True, "trial scope/card mismatch")
    files = verify_export(package, record)
    payload = package / "payload"
    verify_source_pins(payload, record)
    coverage = check_freezes(payload, files)
    native = check_native(payload)
    comparison = compare_saved(payload)
    total = len(CASES) * len(COMPONENTS)
    agreements = {pair: total - sum(len(row[pair]) for row in comparison.values())
                  for pair in ("ref_vs_check", "expected_vs_ref", "expected_vs_check")}
    repeat = check_public_repeat(package, record, comparison)
    return {"status": "PASS", "public_repeat": repeat, "public_payload_files": len(files), "freeze_coverage": coverage,
            "saved_native_decisions": native, "case_contexts": len(CASES), "distinct_input_bytes": 4,
            "saved_core_appraisals": len(CASES) * 2, "component_comparisons_per_pair": total,
            "matching_components": agreements, "differences_by_case": comparison,
            "new_implementation_execution_performed": False, "independent_reproduction_performed": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, default=DEFAULT_PACKAGE)
    try:
        result = verify_package(parser.parse_args().package)
    except (OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile) as error:
        print(json.dumps({"status": "FAIL", "error": str(error)}))
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
