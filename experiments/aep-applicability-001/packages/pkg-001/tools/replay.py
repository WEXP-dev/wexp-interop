#!/usr/bin/env python3
"""Repeat the three local AEP verifier cases and twelve Core appraisals."""
# SPDX-License-Identifier: MIT
import argparse
from datetime import datetime, timezone
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import platform
import subprocess
import sys
import tempfile


PACKAGE = Path(__file__).resolve().parents[1]
COLLECTION = PACKAGE.parents[3]
PAYLOAD = PACKAGE / "payload"
sys.path.insert(0, str(COLLECTION / "scripts"))
from verify_aep_core02 import compare_components

PINS = {
    "aep-sandbox": "f6c88be63c5aa12b8e8f6bf35a378a6a5fca9cd4",
    "wexp-ref": "56289024c9ee748111f1f1d4f42728ffe04d8d69",
    "wexp-check": "a2fd1ffd68b234592979a8aa8965bd580ede4d76",
}
CASES = [f"{case}-{context}" for case in "abc" for context in ("strict", "attrib")]
NATIVE_CASES = (("a", "good", True), ("b", "good", True), ("c", "exceed-scope", False))
LOGICAL_NOW = "1750000100"


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def fingerprint(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def json_data(path):
    return json.loads(path.read_bytes())


def native_runs(source, evidence):
    state = source / "state" / "consumed_nonces.txt"
    if state.parent.is_symlink():
        raise ValueError("nonce-state directory is a symlink; use a fresh sandbox checkout")
    state.parent.mkdir(exist_ok=True)
    with state.open("xb"):
        pass
    destination = evidence / "aep"
    destination.mkdir()
    for case, sample, consume in NATIVE_CASES:
        packet = source / "samples" / f"{sample}.aep.json"
        cmd = ["/bin/sh", str(PAYLOAD / "run_aep_verify.sh"), sys.executable, str(source),
               str(packet), "--now", LOGICAL_NOW]
        if consume:
            cmd.append("--consume")
        (destination / f"{case}.state-before.txt").write_bytes(state.read_bytes())
        run = subprocess.run(cmd, cwd=source, capture_output=True,
                             env={"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8"})
        (destination / f"{case}.stdout.txt").write_bytes(run.stdout)
        (destination / f"{case}.rc.txt").write_text(f"{run.returncode}\n")
        (destination / f"{case}.state-after.txt").write_bytes(state.read_bytes())
        if run.returncode != (0 if case == "a" else 2):
            sys.stderr.buffer.write(run.stderr)
            raise RuntimeError(f"unexpected native return code for {case}; partial observations retained")


def core_runs(source_root, evidence):
    outputs = {}
    for engine in ("ref", "check"):
        source = source_root / f"wexp-{engine}"
        if engine == "ref":
            source = source / "src"
        destination = evidence / "core" / engine
        destination.mkdir(parents=True)
        for case in CASES:
            target = destination / f"{case}.stdout.json"
            with tempfile.TemporaryDirectory() as temp:
                metadata = Path(temp) / "metadata.json"
                cmd = [sys.executable, "-I", "-B", str(PAYLOAD / "run_core_appraiser.py"),
                       "--engine", engine, "--source", str(source),
                       "--input", str(PAYLOAD / "inputs" / f"{case}.json"),
                       "--profiles", str(PAYLOAD / "evidence/PROFILE-CATALOG.json"),
                       "--metadata", str(metadata)]
                run = subprocess.run(cmd, cwd=source, capture_output=True,
                                     env={"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8"})
                target.write_bytes(run.stdout)
                (destination / f"{case}.rc.txt").write_text(f"{run.returncode}\n")
                if run.returncode:
                    sys.stderr.buffer.write(run.stderr)
                    raise RuntimeError(f"appraiser {engine} failed on {case}; partial observations retained")
            outputs[engine, case] = json_data(target)
    return outputs


def replay(sources, output):
    preparation = git(COLLECTION, "rev-parse", "HEAD")
    if git(COLLECTION, "status", "--porcelain"):
        raise ValueError("use a clean collection checkout and keep the output outside it")
    for name, commit in PINS.items():
        repo = sources / name
        if git(repo, "rev-parse", "HEAD") != commit or git(repo, "status", "--porcelain"):
            raise ValueError(f"inexact or dirty checkout: {name}")
    if any(output.is_relative_to(repo) for repo in [COLLECTION, *(sources / name for name in PINS)]):
        raise ValueError("choose a new output path outside the checkouts")
    started = datetime.now(timezone.utc)
    output.mkdir()
    evidence = output / "evidence"
    evidence.mkdir()
    native_runs(sources / "aep-sandbox", evidence)
    outputs = core_runs(sources, evidence)

    deltas = {}
    for engine in ("ref", "check"):
        deltas[engine] = {
            case: compare_components(json_data(PAYLOAD / "expectations/v1" / f"{case}.json"), outputs[engine, case])
            for case in CASES
        }
    appraiser_deltas = {case: compare_components(outputs["ref", case], outputs["check", case]) for case in CASES}
    stream_hashes = {f.relative_to(evidence).as_posix(): fingerprint(f)
                     for f in sorted(evidence.rglob("*")) if f.is_file()}
    changed = [name for name, digest in stream_hashes.items() if fingerprint(PAYLOAD / "evidence" / name) != digest]
    result_matches = (not changed and not any(appraiser_deltas.values())
                      and all(row == ["boundary_ceiling"] for side in deltas.values() for row in side.values()))
    record = {
        "status": "PASS" if result_matches else "DIFFERENCE",
        "preparation_commit": preparation, "implementation_commits": PINS, "logical_now": int(LOGICAL_NOW),
        "started_utc": started.isoformat(), "finished_utc": datetime.now(timezone.utc).isoformat(),
        "runtime": {"python": platform.python_version(), "implementation": platform.python_implementation(),
                    "system": platform.system(), "architecture": platform.machine(),
                    "packages": {k: version(k) for k in ("pip", "cryptography", "cffi", "pycparser")}},
        "case_order": [row[0] for row in NATIVE_CASES], "core_case_order": CASES,
        "output_sha256": stream_hashes, "changed_raw_files_vs_historical": changed,
        "ref_check_differing_components": appraiser_deltas,
        "frozen_expectation_differing_components": deltas,
        "observation_scope": "Fresh execution of published code. Independent reproduction is not asserted.",
    }
    (output / "RUN-RECORD.json").write_text(json.dumps(record, indent=2) + "\n")
    return 0 if result_matches else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True, help="directory containing the three pinned checkouts")
    parser.add_argument("--output", type=Path, required=True, help="new output directory with an existing parent")
    args = parser.parse_args()
    try:
        sys.exit(replay(args.source_root.resolve(strict=True), args.output.resolve()))
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        sys.exit(str(error))
