#!/usr/bin/env python3
"""Read-only verifier for the INTEROP-001 final candidate.

This program verifies recorded bytes and relationships. It never imports or
invokes WEXP or EMILIA implementation code.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import zipfile

sys.dont_write_bytecode = True

SHA_RE = re.compile(r"^[0-9a-f]{64}$")
ROOT = Path(__file__).resolve().parents[1]

FROZEN = {
    "source/original/WEXP-EMILIA-INTEROP-001/fixtures.yaml": (2218, "d972dbb549aaaa25e92c32a936acba4d9a686e9ca62fe6bd556b12be2962cfcc"),
    "source/original/WEXP-EMILIA-INTEROP-001/MANIFEST.sha256": (240, "c914330b502a48f669381bad763952365da8db64b078445cea6ba5bfb7209d46"),
    "source/original/commitment/WEXP-EMILIA-INTEROP-001-SHAREABLE-v2.zip": (2809, "0ec17bcf9b88af17016c7e05d465012af604292210a858df5fa8f9bcf00d57a0"),
    "records/WEXP-EMILIA-EP-COMPARISON-001.md": (19327, "272a9b08a213702ee2156438b7736b954c7a32bc4a190cce92d3d82226266934"),
    "source/original/WEXP-EMILIA-INTEROP-001/wexp-reading.yaml": (13256, "a185e6760de149375e657b1429adc1ea329ed9f9705b9d1c2b505dcc8e3ea984"),
    "source/original/emilia-reading.json": (5078, "b43f8ac6dce465258c75a42117d2750a6bafa163846251416e87cec371a4bad6"),
    "source/original/WEXP-EMILIA-PAIR-FREEZE-001.zip": (18158, "ae237263c86ee0b5c2b6387159d81957efe47e20161b74dd363da5a530705282"),
    "source/pair-freeze/WEXP-EMILIA-PAIR-FREEZE-001.zip": (18158, "ae237263c86ee0b5c2b6387159d81957efe47e20161b74dd363da5a530705282"),
    "source/pair-freeze/fixtures/WE-EP-P.json": (7255, "b552da51858d0256a562e800a81a870435d6e136c9bc28833b962b6d3723fb3e"),
    "source/pair-freeze/fixtures/WE-EP-P-1.json": (7152, "67556d28d272b4b01a73e1c1465248644dd7a05460fc149aa77df92cf36403a0"),
    "source/pair-freeze/PAIR-MANIFEST.sha256": (178, "5375841c5c7d550d1dcbb3ac31e73ab6c5d68a2bc1eb4fea5249dec9dbdce604"),
    "source/pair-freeze/MANIFEST.sha256": (686, "ae6e2345e51cd32aad6e1aa7ce3d4ffeb7b4b005ebcbc19dc067ee22c6b52022"),
    "expectations/wexp/wexp-expectation.yaml": (8226, "42eeecaba33238d8c94bbb9d5bb22ab46721de6de74cff455b8115c17892088a"),
    "expectations/emilia/emilia-expectation.freeze.json": (885, "6e0dc6c87f853cacdeeb676b27690e54bdb8a7a7aa86611c5ffe233387e256a4"),
    "execution/raw/emilia/emilia-execution-receipt.json": (1963, "2d61071712ef4424d1b308afb6a3b8752b4effcf2525c0c08c97cff16617b77f"),
}

PAIR_MEMBERS = {
    "WEXP-EMILIA-PAIR-FREEZE-001/EXPERIMENT-PROPOSITION.md",
    "WEXP-EMILIA-PAIR-FREEZE-001/MANIFEST.sha256",
    "WEXP-EMILIA-PAIR-FREEZE-001/PAIR-DELTA.md",
    "WEXP-EMILIA-PAIR-FREEZE-001/PAIR-MANIFEST.sha256",
    "WEXP-EMILIA-PAIR-FREEZE-001/README.md",
    "WEXP-EMILIA-PAIR-FREEZE-001/WEXP-DERIVATION.md",
    "WEXP-EMILIA-PAIR-FREEZE-001/fixtures/WE-EP-P-1.json",
    "WEXP-EMILIA-PAIR-FREEZE-001/fixtures/WE-EP-P.json",
    "WEXP-EMILIA-PAIR-FREEZE-001/wexp-expectation.yaml",
}


class Failure(RuntimeError):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_regular(relative: str) -> bytes:
    path = ROOT / relative
    if path.is_symlink() or not path.is_file():
        raise Failure(f"not a regular non-symlink file: {relative}")
    try:
        return path.read_bytes()
    except OSError as exc:
        raise Failure(f"cannot read {relative}: {exc}") from exc


def verify_frozen() -> None:
    for relative, (expected_size, expected_hash) in FROZEN.items():
        data = read_regular(relative)
        if len(data) != expected_size or sha256(data) != expected_hash:
            raise Failure(f"frozen identity mismatch: {relative}")


def parse_manifest(data: bytes) -> dict[str, str]:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise Failure("manifest is not UTF-8") from exc
    entries: dict[str, str] = {}
    for line in text.splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        if not match:
            raise Failure(f"invalid manifest line: {line!r}")
        digest, relative = match.groups()
        if relative in entries or relative.startswith("/") or ".." in Path(relative).parts:
            raise Failure(f"unsafe or duplicate manifest path: {relative}")
        entries[relative] = digest
    return entries


def verify_root_manifest(external_hash: str | None) -> int:
    data = read_regular("MANIFEST.sha256")
    actual_manifest_hash = sha256(data)
    if external_hash is not None:
        if not SHA_RE.fullmatch(external_hash) or actual_manifest_hash != external_hash:
            raise Failure("root manifest external identity mismatch")
    entries = parse_manifest(data)
    actual_files: set[str] = set()
    for path in ROOT.rglob("*"):
        if path.is_symlink():
            raise Failure(f"symlink in candidate: {path.relative_to(ROOT)}")
        if path.is_file():
            relative = path.relative_to(ROOT).as_posix()
            if relative != "MANIFEST.sha256":
                actual_files.add(relative)
        elif not path.is_dir():
            raise Failure(f"special filesystem entry: {path.relative_to(ROOT)}")
    if set(entries) != actual_files:
        raise Failure("root manifest does not exactly cover candidate payload files")
    for relative, expected_hash in entries.items():
        if sha256(read_regular(relative)) != expected_hash:
            raise Failure(f"root manifest member mismatch: {relative}")
    return len(entries)


def verify_nested_manifest(directory: str, manifest_name: str) -> None:
    base = ROOT / directory
    entries = parse_manifest(read_regular(f"{directory}/{manifest_name}"))
    for relative, expected_hash in entries.items():
        path = base / relative
        if path.is_symlink() or not path.is_file() or sha256(path.read_bytes()) != expected_hash:
            raise Failure(f"nested manifest mismatch: {directory}/{relative}")


def verify_pair_archive() -> None:
    archive_path = ROOT / "source/original/WEXP-EMILIA-PAIR-FREEZE-001.zip"
    with zipfile.ZipFile(archive_path) as archive:
        infos = archive.infolist()
        names = [info.filename for info in infos]
        if len(names) != 9 or len(set(names)) != 9 or set(names) != PAIR_MEMBERS:
            raise Failure("pair archive member set mismatch")
        if any(info.is_dir() or info.flag_bits & 0x1 for info in infos):
            raise Failure("pair archive contains directory or encrypted entry")
        if archive.testzip() is not None:
            raise Failure("pair archive CRC failure")
        for name in names:
            relative = name.removeprefix("WEXP-EMILIA-PAIR-FREEZE-001/")
            direct = read_regular(f"source/pair-freeze/{relative}")
            nested = read_regular(f"source/pair-freeze/WEXP-EMILIA-PAIR-FREEZE-001/{relative}")
            if archive.read(name) != direct or direct != nested:
                raise Failure(f"pair archive/direct/nested byte mismatch: {name}")


def recursive_diff(left: object, right: object, path: str = "") -> list[tuple[str, str]]:
    if type(left) is not type(right):
        return [("CHANGE", path)]
    if isinstance(left, dict):
        changes: list[tuple[str, str]] = []
        for key in left.keys() - right.keys():
            changes.append(("REMOVE", f"{path}/{key}"))
        for key in right.keys() - left.keys():
            changes.append(("ADD", f"{path}/{key}"))
        for key in left.keys() & right.keys():
            changes.extend(recursive_diff(left[key], right[key], f"{path}/{key}"))
        return changes
    if isinstance(left, list):
        if len(left) != len(right):
            return [("CHANGE", path)]
        changes = []
        for index, (a, b) in enumerate(zip(left, right)):
            changes.extend(recursive_diff(a, b, f"{path}/{index}"))
        return changes
    return [] if left == right else [("CHANGE", path)]


def verify_pair_delta() -> None:
    p_bytes = read_regular("source/pair-freeze/fixtures/WE-EP-P.json")
    p1_bytes = read_regular("source/pair-freeze/fixtures/WE-EP-P-1.json")
    p = json.loads(p_bytes)
    p1 = json.loads(p1_bytes)
    expected = {
        ("REMOVE", "/emilia_input/observations/1/action_caid"),
        ("CHANGE", "/emilia_input/observations/1/proof/signature_b64u"),
    }
    if set(recursive_diff(p, p1)) != expected:
        raise Failure("P to P-1 parsed delta is not the declared two-path delta")

    original_signature = p["emilia_input"]["observations"][1]["proof"]["signature_b64u"]
    hostile_signature = p1["emilia_input"]["observations"][1]["proof"]["signature_b64u"]
    caid = p["emilia_input"]["observations"][1]["action_caid"]
    restored = p1_bytes.replace(hostile_signature.encode(), original_signature.encode(), 1)
    action_hash_line = b'        "action_hash": "sha256:d5332018e3e0caa454b9a5391a33fa57f58fcbb645ff443e112236caee4bf51a",\n'
    action_caid_line = f'        "action_caid": "{caid}",\n'.encode()
    first = restored.find(action_hash_line)
    second = restored.find(action_hash_line, first + len(action_hash_line))
    if first < 0 or second < 0:
        raise Failure("cannot locate exact meter action_hash line for byte restoration")
    insert_at = second + len(action_hash_line)
    restored = restored[:insert_at] + action_caid_line + restored[insert_at:]
    if restored != p_bytes:
        raise Failure("restoring action_caid and the original meter signature does not reproduce P bytes")


def verify_expectation_and_receipt() -> None:
    expectation = json.loads(read_regular("expectations/emilia/emilia-expectation.freeze.json"))
    receipt = json.loads(read_regular("execution/raw/emilia/emilia-execution-receipt.json"))
    if expectation.get("freeze_status") != "fixed_before_emilia_execution":
        raise Failure("EMILIA expectation freeze status mismatch")
    if receipt.get("expectation_freeze_sha256") != FROZEN["expectations/emilia/emilia-expectation.freeze.json"][1]:
        raise Failure("receipt-to-expectation hash linkage mismatch")
    if receipt.get("package_sha256") != FROZEN["source/original/WEXP-EMILIA-PAIR-FREEZE-001.zip"][1]:
        raise Failure("receipt-to-pair-package hash linkage mismatch")
    if expectation.get("emilia_baseline_commit") != "9a04bea7fe680345132f6f6251fdb9a63fd8aeb2":
        raise Failure("expectation EMILIA baseline mismatch")
    if receipt.get("emilia_baseline", {}).get("commit") != expectation["emilia_baseline_commit"]:
        raise Failure("receipt EMILIA baseline mismatch")
    if receipt["emilia_baseline"].get("verifier_source_sha256") != "9a674113122f23001567eaeb673190ac4658b5273f7433e234c8ecbb5be704b0":
        raise Failure("receipt verifier source identity mismatch")
    if receipt["emilia_baseline"].get("package_entry_sha256") != "f386e365a9998f08ea4947ffd415ca353c0a82766677a8e0cf3117909cccee24":
        raise Failure("receipt package entry identity mismatch")

    result_digests = {
        "P": "sha256:4ea90a5cf398ad77fe21bd5933ae85c2970cb55d1b5cd929c0f097bb9efc50b3",
        "P-1": "sha256:7bfe5b1ba465546787d0ed31fa7aabd00ddd30b755b1c028230a5796d0160aca",
    }
    for fixture_id in ("P", "P-1"):
        expected = expectation["pair"][fixture_id]["expect"]
        actual = receipt["results"][fixture_id]
        if actual["input_sha256"] != expectation["pair"][fixture_id]["sha256"]:
            raise Failure(f"{fixture_id} input identity mismatch")
        expected_errors = expected.get("errors", [expected["required_error"]] if "required_error" in expected else [])
        for field in ("valid", "lifecycle_state", "outcome"):
            if actual[field] != expected[field]:
                raise Failure(f"{fixture_id} expectation not reproduced: {field}")
        if actual["errors"] != expected_errors:
            raise Failure(f"{fixture_id} expectation not reproduced: errors")
        if actual.get("result_digest") != result_digests[fixture_id]:
            raise Failure(f"{fixture_id} recorded result digest mismatch")
    if set(receipt.get("shared_checks", {})) != {
        "predictions_valid", "observations_verified", "required_sources_present",
        "source_independence", "source_requirements", "observation_windows",
    } or not all(receipt["shared_checks"].values()):
        raise Failure("shared checks are not exactly six true values")


def verify_branch() -> None:
    selection = json.loads(read_regular("records/TERMINAL-BRANCH-SELECTION-001.json"))
    if selection.get("selected") != "A — EXPLICIT BRIDGE REQUIRED" or selection.get("selection_count") != 1:
        raise Failure("terminal Branch A is not uniquely selected")
    if not selection["branch_A_criteria"].get("all_criteria_met"):
        raise Failure("Branch A criteria are not all met")
    if selection["branch_B_criteria"].get("all_criteria_met") or selection["branch_C_criteria"].get("all_criteria_met"):
        raise Failure("Branch B or C is incorrectly selected")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest-sha256", help="externally pinned final MANIFEST.sha256 identity")
    args = parser.parse_args()
    try:
        count = verify_root_manifest(args.manifest_sha256)
        verify_frozen()
        verify_nested_manifest("source/original/WEXP-EMILIA-INTEROP-001", "MANIFEST.sha256")
        verify_nested_manifest("source/pair-freeze", "PAIR-MANIFEST.sha256")
        verify_nested_manifest("source/pair-freeze", "MANIFEST.sha256")
        verify_pair_archive()
        verify_pair_delta()
        verify_expectation_and_receipt()
        verify_branch()
    except (Failure, OSError, KeyError, TypeError, ValueError, json.JSONDecodeError, zipfile.BadZipFile) as exc:
        print(json.dumps({"status": "FAIL", "reason": str(exc)}, sort_keys=True))
        return 1
    print(json.dumps({
        "status": "PASS",
        "payload_entries_verified": count,
        "frozen_identities_verified": len(FROZEN),
        "pair_delta": "PASS",
        "emilia_expectation_reproduced": {"P": "PASS", "P-1": "PASS"},
        "terminal_branch": "A — EXPLICIT BRIDGE REQUIRED",
        "implementation_execution_performed": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
