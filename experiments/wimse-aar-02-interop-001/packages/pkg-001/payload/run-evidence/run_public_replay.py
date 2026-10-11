#!/usr/bin/env python3
"""Record and execute one frozen AAR public replay from a fresh public clone.

SPDX-License-Identifier: MIT
The journal records a local execution observation, not an independently signed
attestation. No retained source or prior output is modified.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def save(path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def git(repository, *arguments):
    return subprocess.check_output(["git", *arguments], cwd=repository, text=True).strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", required=True, type=Path)
    parser.add_argument("--preparation-commit", required=True)
    parser.add_argument("--preparation-tree", required=True)
    parser.add_argument("--freeze-sha256", required=True)
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--journal-dir", required=True, type=Path)
    args = parser.parse_args()
    repository = args.repository.resolve()
    payload = repository / "experiments/wimse-aar-02-interop-001/packages/pkg-001/payload"
    results = args.run_dir.resolve()
    journal = args.journal_dir.resolve()
    if results.exists() or journal.exists():
        raise SystemExit("Refusing an existing result or journal directory.")
    if results.is_relative_to(repository) or journal.is_relative_to(repository):
        raise SystemExit("Results and journal must be outside the untouched clone.")
    head = git(repository, "rev-parse", "HEAD")
    tree = git(repository, "rev-parse", "HEAD^{tree}")
    if head != args.preparation_commit or tree != args.preparation_tree:
        raise SystemExit("Clone commit/tree differs from the published preparation pin.")
    if git(repository, "status", "--porcelain"):
        raise SystemExit("The fresh clone is not clean.")
    freeze = (payload / "pre-run/FREEZE.json").read_bytes()
    if sha(freeze) != args.freeze_sha256:
        raise SystemExit("Input freeze differs from the public preparation pin.")
    journal.mkdir(parents=True, exist_ok=False)
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"

    def invoke(name, arguments):
        command = [sys.executable, "-B", *arguments]
        start = {"command": command, "working_directory": str(payload), "started_at_utc": now()}
        save(journal / (name + ".start.json"), start)
        completed = subprocess.run(command, cwd=payload, env=environment, capture_output=True)
        for suffix, data in [("stdout", completed.stdout), ("stderr", completed.stderr)]:
            with (journal / (name + "." + suffix)).open("xb") as stream:
                stream.write(data)
        observation = {**start, "ended_at_utc": now(), "exit_code": completed.returncode,
                       "stdout_sha256": sha(completed.stdout), "stderr_sha256": sha(completed.stderr)}
        save(journal / (name + ".command.json"), observation)
        return completed

    pre = invoke("input-verification", ["verify_inputs.py", "--pre-run"])
    if pre.returncode:
        sys.stdout.buffer.write(pre.stdout)
        sys.stderr.buffer.write(pre.stderr)
        return pre.returncode
    pre_result = json.loads(pre.stdout)
    if pre_result.get("status") != "PASS" or pre_result.get("implementation_execution_performed") is not False:
        raise SystemExit("Pre-run identity verification did not have the required scope and success.")
    start = {"format": "wexp-aar-public-replay-start/0.1.0", "recorded_at_utc": now(),
             "public_repository": "https://github.com/WEXP-dev/wexp-interop",
             "preparation_commit": head, "preparation_tree": tree,
             "preparation_parent": git(repository, "rev-parse", "HEAD^"),
             "preparation_commit_date": git(repository, "show", "-s", "--format=%cI", "HEAD"),
             "freeze_sha256": sha(freeze), "input_lock_sha256": sha((payload / "pre-run/INPUTS.lock.json").read_bytes()),
             "input_verification_stdout_sha256": sha(pre.stdout),
             "clone_worktree_clean_before_execution": not bool(git(repository, "status", "--porcelain")),
             "python_version": sys.version, "python_implementation": platform.python_implementation(),
             "platform": platform.platform(), "machine": platform.machine(),
             "driver_sha256": sha(Path(__file__).read_bytes()),
             "result_directory": str(results), "journal_directory": str(journal),
             "coordination": "Same owner-controlled environment; known reference and oracle; no external-team independence.",
             "timing_limit": "This start was written before invoking the retained runner. Local clock and log are not independent timestamp attestations."}
    save(journal / "EXECUTION-START.json", start)
    run = invoke("retained-pilot", ["run_pilot.py", "--out", str(results), "--compare", "reference/private-pilot-semantic-results.json"])
    # Compare retained data even after a runner failure, preserving both outcomes.
    comparison = invoke("strict-comparison", ["compare_results.py", "--results", str(results),
                                               "--report", str(results / "reference-comparison.json")])
    finish = {"format": "wexp-aar-public-replay-finish/0.1.0", "recorded_at_utc": now(),
              "preparation_commit": head, "preparation_tree": tree, "freeze_sha256": sha(freeze),
              "runner_exit_code": run.returncode, "comparator_exit_code": comparison.returncode,
              "clone_worktree_clean_after_execution": not bool(git(repository, "status", "--porcelain")),
              "driver_sha256": sha(Path(__file__).read_bytes()), "pilot_implementation_execution_performed": True}
    save(journal / "EXECUTION-FINISH.json", finish)
    print(json.dumps(finish, indent=2, sort_keys=True), flush=True)
    sys.stdout.buffer.write(run.stdout)
    sys.stdout.buffer.write(comparison.stdout)
    sys.stderr.buffer.write(run.stderr)
    sys.stderr.buffer.write(comparison.stderr)
    return 0 if run.returncode == 0 and comparison.returncode == 0 and finish["clone_worktree_clean_after_execution"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
