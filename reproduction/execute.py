#!/usr/bin/env python3
"""Controlled future execution entry point for INTEROP-001.

The verifier runs to completion before this program creates result directories,
captures an environment, or invokes an implementation.  The current scaffold
must refuse because the EMILIA expectation is not yet frozen.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, Iterable

# The package manifest is an exact-coverage identity boundary.  Importing the
# local verifier must therefore never create an unmanifested __pycache__ entry
# before that boundary has been checked.
sys.dont_write_bytecode = True

import verify
from exact_json import canonical_json_bytes, parse_decimal, validate_json_limits


ACKNOWLEDGEMENT = "EXECUTE-P-P1-AFTER-BOTH-EXPECTATIONS-FROZEN"
RESULT_CLASSES = {
    "EXPECTED RESULT REPRODUCED",
    "EXPECTED RESULT NOT REPRODUCED",
    "IMPLEMENTATION INPUT NOT CONSTRUCTIBLE",
    "IMPLEMENTATION SURFACE NOT IMPLEMENTED",
    "INFRASTRUCTURE EXECUTION UNAVAILABLE",
    "IDENTITY FAILURE",
    "EXPECTATION MISSING / NOT FROZEN",
}


def _canonical_json_bytes(value: Any) -> bytes:
    return canonical_json_bytes(value)


def _emit_json(value: Any) -> None:
    sys.stdout.buffer.write(_canonical_json_bytes(value))


def _json_structurally_equal(left: Any, right: Any) -> bool:
    left_is_number = isinstance(left, (int, Decimal)) and not isinstance(left, bool)
    right_is_number = isinstance(right, (int, Decimal)) and not isinstance(right, bool)
    if left_is_number or right_is_number:
        return left_is_number and right_is_number and Decimal(left) == Decimal(right)
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return left.keys() == right.keys() and all(
            _json_structurally_equal(left[key], right[key]) for key in left
        )
    if isinstance(left, list):
        return len(left) == len(right) and all(
            _json_structurally_equal(left_item, right_item)
            for left_item, right_item in zip(left, right)
        )
    return left == right


def _write_bytes(path: Path, data: bytes) -> str:
    expected_sha256 = hashlib.sha256(data).hexdigest()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".tmp-{os.getpid()}")
    with temporary.open("xb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    try:
        os.link(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)
    verify._require_identity(
        path,
        expected_sha256,
        expected_bytes=len(data),
        gate="OUTPUT_CAPTURE",
    )
    return expected_sha256


def _record_output(
    root: Path,
    ledger: dict[str, str],
    path: Path,
    data: bytes,
) -> None:
    relative = path.relative_to(root).as_posix()
    if relative in ledger:
        raise verify.GateFailure(
            verify.IDENTITY_FAILURE,
            "OUTPUT_CAPTURE",
            f"output identity already recorded: {relative}",
        )
    ledger[relative] = _write_bytes(path, data)


def _verify_output_ledger(root: Path, ledger: dict[str, str]) -> None:
    for relative, expected_sha256 in ledger.items():
        verify._require_identity(
            root / relative,
            expected_sha256,
            gate="OUTPUT_CAPTURE",
        )


def _read_frozen_bytes(
    path: Path,
    expected_sha256: str,
    gate: str,
) -> tuple[dict[str, Any], bytes]:
    identity = verify._require_identity(path, expected_sha256, gate=gate)
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise verify.GateFailure(
            verify.IDENTITY_FAILURE,
            gate,
            f"cannot read frozen bytes from {path}: {exc}",
        ) from exc
    actual_sha256 = hashlib.sha256(data).hexdigest()
    if actual_sha256 != expected_sha256 or len(data) != identity["bytes"]:
        raise verify.GateFailure(
            verify.IDENTITY_FAILURE,
            gate,
            f"frozen bytes changed during identity read: {path}",
        )
    return identity, data


def _verify_runtime_package_coverage(
    root: Path,
    ledger: dict[str, str],
    additional_members: set[str] | None = None,
) -> None:
    """Allow only pre-run manifest members plus ledgered execution outputs."""
    manifest = verify._require_file(root, "MANIFEST.sha256")
    try:
        manifest_bytes = manifest.read_bytes()
    except OSError as exc:
        raise verify.GateFailure(
            verify.IDENTITY_FAILURE,
            "PACKAGE_COVERAGE",
            f"cannot read package manifest during execution: {exc}",
        ) from exc
    manifest_entries = verify._parse_manifest_bytes(manifest_bytes, str(manifest))
    expected = (
        {relative for _, relative in manifest_entries}
        | set(ledger)
        | (additional_members or set())
    )
    actual: set[str] = set()
    try:
        for entry in root.rglob("*"):
            relative = entry.relative_to(root).as_posix()
            if entry.is_symlink():
                raise verify.GateFailure(
                    verify.IDENTITY_FAILURE,
                    "PACKAGE_COVERAGE",
                    f"symlink appeared during execution: {relative}",
                )
            if entry.is_file():
                if relative != "MANIFEST.sha256":
                    actual.add(relative)
            elif not entry.is_dir():
                raise verify.GateFailure(
                    verify.IDENTITY_FAILURE,
                    "PACKAGE_COVERAGE",
                    f"special filesystem entry appeared during execution: {relative}",
                )
    except verify.GateFailure:
        raise
    except OSError as exc:
        raise verify.GateFailure(
            verify.IDENTITY_FAILURE,
            "PACKAGE_COVERAGE",
            f"cannot enumerate package during execution: {exc}",
        ) from exc
    if actual != expected:
        raise verify.GateFailure(
            verify.IDENTITY_FAILURE,
            "PACKAGE_COVERAGE",
            "runtime package coverage changed; "
            f"unexpected={sorted(actual - expected)}, missing={sorted(expected - actual)}",
        )


def _planned_output_paths(root: Path) -> list[Path]:
    paths = [
        root / "execution" / "RUN-START.json",
        root / "execution" / "PRE-RUN-MANIFEST.sha256",
        root / "execution" / "VERIFICATION-REPORT.json",
        root / "execution" / "EXECUTION-MANIFEST.sha256",
        root / "reproduction" / "environment" / "EXECUTION-ENVIRONMENT.json",
    ]
    for fixture_id in ("P", "P-1"):
        raw_root = root / "execution" / "raw" / "emilia" / fixture_id
        paths.extend(raw_root / name for name in ("stdout.bin", "stderr.bin", "invocation.json"))
        paths.append(root / "execution" / "normalized" / "wexp" / f"{fixture_id}.json")
        paths.append(root / "execution" / "normalized" / "emilia" / f"{fixture_id}.json")
    paths.append(root / "execution" / "normalized" / "summary.json")
    return paths


def _capture_environment(
    control: dict[str, Any],
    execution_identity: dict[str, Any],
    verified_emilia_baseline: dict[str, Any],
    adapter_executable: dict[str, Any],
    adapter_entrypoint: dict[str, Any],
    verified_runtime_versions: list[dict[str, Any]],
) -> dict[str, Any]:
    implementation = control["emilia"]["implementation"]
    adapter_environment = dict(implementation["environment"])
    container_runtime = implementation["container_runtime"]
    return {
        "schema_version": "wexp-emilia-execution-environment-1",
        "captured_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "execution_identity": execution_identity,
        "os": platform.platform(),
        "system": platform.system(),
        "release": platform.release(),
        "architecture": platform.machine(),
        "python": sys.version,
        "git": {
            "executable": verified_emilia_baseline["git_executable"],
            "executable_sha256": verified_emilia_baseline["git_executable_sha256"],
            "version": verified_emilia_baseline["git_version"],
        },
        "adapter_environment": adapter_environment,
        "adapter_executable": adapter_executable,
        "adapter_entrypoint": adapter_entrypoint,
        "parent_environment_inherited": False,
        "adapter_runtime_versions": verified_runtime_versions,
        "container_runtime": {
            "declared": container_runtime,
            "declared_for_adapter": container_runtime != "NONE",
            "image_reference": implementation["container_image_reference"],
            "image_digest": implementation["container_image_digest"],
            "identity_source": "reviewed adapter executable, runtime-version checks, and immutable image digest",
        },
        "verified_implementation_baselines": {
            "wexp": control["wexp"]["execution_baseline"],
            "emilia": verified_emilia_baseline,
        },
    }


def _replace_tokens(argv: list[str], fixture_path: Path, fixture_id: str) -> list[str]:
    replacements = {"{fixture_path}": str(fixture_path), "{fixture_id}": fixture_id}
    result: list[str] = []
    for value in argv:
        rendered = value
        for token, replacement in replacements.items():
            rendered = rendered.replace(token, replacement)
        if "{" in rendered or "}" in rendered:
            raise verify.GateFailure(verify.IDENTITY_FAILURE, "CONTROL", f"unsupported command token: {value}")
        result.append(rendered)
    return result


def _parse_adapter_stdout(data: bytes, fixture_id: str) -> dict[str, Any]:
    def reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        value: dict[str, Any] = {}
        for key, member in pairs:
            if key in value:
                raise ValueError(f"duplicate JSON member: {key}")
            value[key] = member
        return value

    def reject_constant(value: str) -> None:
        raise ValueError(f"non-standard JSON constant: {value}")

    try:
        decoded = data.decode("utf-8")
        value = json.loads(
            decoded,
            object_pairs_hook=reject_duplicate_pairs,
            parse_constant=reject_constant,
            parse_float=parse_decimal,
        )
        validate_json_limits(value)
    except (UnicodeError, json.JSONDecodeError, RecursionError, ValueError) as exc:
        raise ValueError(f"adapter stdout is not one JSON object: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError("adapter stdout is not a JSON object")
    if value.get("schema_version") != "wexp-emilia-observed-result-1":
        raise ValueError("adapter stdout schema_version mismatch")
    if value.get("fixture_id") != fixture_id:
        raise ValueError("adapter fixture_id mismatch")
    adapter_status = value.get("adapter_status")
    if adapter_status not in {"OBSERVED RESULT", "IMPLEMENTATION SURFACE NOT IMPLEMENTED"}:
        raise ValueError("adapter_status is absent or unknown")
    if adapter_status == "OBSERVED RESULT":
        required = {"schema_version", "fixture_id", "adapter_status", "observed_result"}
        if set(value) != required:
            raise ValueError("observed-result contract fields are incomplete or unknown")
    else:
        required = {"schema_version", "fixture_id", "adapter_status", "diagnostic"}
        if set(value) != required:
            raise ValueError("surface-not-implemented contract fields are incomplete or unknown")
        if not isinstance(value.get("diagnostic"), str) or not value["diagnostic"].strip():
            raise ValueError("surface-not-implemented diagnostic is absent")
    return value


def _captured_stream_bytes(value: bytes | str | None) -> bytes:
    """Preserve subprocess streams, including partial TimeoutExpired output."""
    if value is None:
        return b""
    if isinstance(value, bytes):
        return value
    return value.encode("utf-8")


def _runtime_identity_gate(
    root: Path,
    implementation: dict[str, Any],
    execution_identity: dict[str, Any],
) -> dict[str, Any]:
    """Recheck immutable package members and the implementation checkout."""
    manifest = verify._require_file(root, "MANIFEST.sha256")
    verify._require_identity(
        manifest,
        execution_identity["pre_run_package_manifest_sha256"],
        gate="PACKAGE_MANIFEST",
    )
    verify._verify_manifest(manifest, root)
    baseline = verify._verify_git_baseline(
        implementation, required_head=verify.EXPECTED_EMILIA_AUTHORITY
    )
    if baseline["repository_path"] != execution_identity["emilia_repository_path"]:
        raise verify.GateFailure(
            verify.IDENTITY_FAILURE,
            "BASELINE",
            "resolved EMILIA repository path changed after the reviewed pre-run gate",
        )
    executable = verify._resolve_executable(
        implementation["command_argv"][0],
        Path(baseline["repository_path"]),
        implementation["environment"],
    )
    if (
        executable["sha256"] != execution_identity["adapter_executable_sha256"]
        or executable["path"] != execution_identity["adapter_executable_path"]
    ):
        raise verify.GateFailure(
            verify.IDENTITY_FAILURE,
            "BASELINE",
            "adapter executable changed after the reviewed pre-run gate",
        )
    entrypoint = verify._verify_adapter_entrypoint(
        implementation,
        Path(baseline["repository_path"]),
        executable,
    )
    if entrypoint != execution_identity["adapter_entrypoint"]:
        raise verify.GateFailure(
            verify.IDENTITY_FAILURE,
            "BASELINE",
            "adapter entrypoint changed after the reviewed pre-run gate",
        )
    verify._verify_runtime_versions(
        implementation["runtime_version_checks"],
        Path(baseline["repository_path"]),
        implementation["environment"],
    )
    post_baseline = verify._verify_git_baseline(
        implementation,
        required_head=verify.EXPECTED_EMILIA_AUTHORITY,
    )
    post_executable = verify._resolve_executable(
        implementation["command_argv"][0],
        Path(post_baseline["repository_path"]),
        implementation["environment"],
    )
    post_entrypoint = verify._verify_adapter_entrypoint(
        implementation,
        Path(post_baseline["repository_path"]),
        post_executable,
    )
    if (
        post_baseline != baseline
        or post_executable != executable
        or post_entrypoint != entrypoint
    ):
        raise verify.GateFailure(
            verify.IDENTITY_FAILURE,
            "RUNTIME_BASELINE",
            "runtime-version checks changed a reviewed implementation identity",
        )
    verify._require_identity(
        manifest,
        execution_identity["pre_run_package_manifest_sha256"],
        gate="PACKAGE_MANIFEST",
    )
    verify._verify_manifest(manifest, root)
    return post_baseline


def _invoke_emilia(
    root: Path,
    control: dict[str, Any],
    fixture_id: str,
    fixture_source: Path,
    fixture_sha256: str,
    expected_result: Any,
    execution_identity: dict[str, Any],
    output_ledger: dict[str, str],
) -> dict[str, Any]:
    implementation = control["emilia"]["implementation"]
    repository = Path(execution_identity["emilia_repository_path"])
    adapter_environment = dict(implementation["environment"])
    timeout = implementation["timeout_seconds"]
    started = datetime.now(timezone.utc)
    monotonic_start = time.monotonic()
    argv: list[str] = []
    stdout = b""
    stderr = b""
    exit_code: int | None = None
    timed_out = False
    invocation_attempted = False
    implementation_invoked = False
    result_class: str
    detail: str
    parsed: dict[str, Any] | None = None
    staged_identity: dict[str, Any] = {
        "sha256": fixture_sha256,
        "status": "NOT STAGED",
    }
    with tempfile.TemporaryDirectory(
        prefix=f"wexp-emilia-{fixture_id}-",
        ignore_cleanup_errors=True,
    ) as temporary:
        staged_fixture = Path(temporary) / fixture_source.name
        try:
            _verify_output_ledger(root, output_ledger)
            _verify_runtime_package_coverage(root, output_ledger)
            _runtime_identity_gate(root, implementation, execution_identity)
            _verify_output_ledger(root, output_ledger)
            _verify_runtime_package_coverage(root, output_ledger)
            source_identity, source_bytes = _read_frozen_bytes(
                fixture_source,
                fixture_sha256,
                gate=f"{fixture_id}_SOURCE",
            )
            staged_fixture.write_bytes(source_bytes)
            staged_fixture.chmod(0o444)
            staged_identity = verify._require_identity(
                staged_fixture, fixture_sha256, gate=f"{fixture_id}_STAGE"
            )
            argv = _replace_tokens(
                implementation["command_argv"], staged_fixture, fixture_id
            )
            argv[0] = execution_identity["adapter_executable_path"]
            adapter_entrypoint = execution_identity["adapter_entrypoint"]
            if adapter_entrypoint["mode"] == "REPOSITORY_FILE":
                argv[adapter_entrypoint["argv_index"]] = adapter_entrypoint["path"]
            invocation_attempted = True
            try:
                completed = subprocess.run(
                    argv,
                    cwd=repository,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=timeout,
                    check=False,
                    env=adapter_environment,
                )
                implementation_invoked = True
                stdout = completed.stdout
                stderr = completed.stderr
                exit_code = completed.returncode
                if exit_code != 0:
                    result_class = "INFRASTRUCTURE EXECUTION UNAVAILABLE"
                    detail = f"implementation adapter exited {exit_code} without a successful contract exchange"
                else:
                    try:
                        parsed = _parse_adapter_stdout(stdout, fixture_id)
                    except ValueError as exc:
                        result_class = "INFRASTRUCTURE EXECUTION UNAVAILABLE"
                        detail = f"adapter contract unavailable: {exc}"
                    else:
                        if parsed["adapter_status"] == "IMPLEMENTATION SURFACE NOT IMPLEMENTED":
                            result_class = "IMPLEMENTATION SURFACE NOT IMPLEMENTED"
                            detail = parsed["diagnostic"]
                        else:
                            try:
                                reproduced = _json_structurally_equal(
                                    parsed["observed_result"], expected_result
                                )
                            except RecursionError as exc:
                                result_class = "INFRASTRUCTURE EXECUTION UNAVAILABLE"
                                detail = f"adapter contract comparison unavailable: {exc}"
                            else:
                                if reproduced:
                                    result_class = "EXPECTED RESULT REPRODUCED"
                                    detail = "observed_result is structurally identical to the independently frozen normalized expectation"
                                else:
                                    result_class = "EXPECTED RESULT NOT REPRODUCED"
                                    detail = "observed_result differs from the independently frozen normalized expectation"
            except subprocess.TimeoutExpired as exc:
                implementation_invoked = True
                stdout = _captured_stream_bytes(exc.stdout)
                stderr = _captured_stream_bytes(exc.stderr)
                timed_out = True
                result_class = "INFRASTRUCTURE EXECUTION UNAVAILABLE"
                detail = f"TimeoutExpired: {exc}"
            except OSError as exc:
                result_class = "INFRASTRUCTURE EXECUTION UNAVAILABLE"
                detail = f"OSError: {exc}"

            try:
                _verify_output_ledger(root, output_ledger)
                _verify_runtime_package_coverage(root, output_ledger)
                _runtime_identity_gate(root, implementation, execution_identity)
                _verify_output_ledger(root, output_ledger)
                _verify_runtime_package_coverage(root, output_ledger)
                verify._require_identity(
                    fixture_source, fixture_sha256, gate=f"{fixture_id}_SOURCE_POST"
                )
                verify._require_identity(
                    staged_fixture, fixture_sha256, gate=f"{fixture_id}_STAGE_POST"
                )
            except verify.GateFailure as exc:
                result_class = "IDENTITY FAILURE"
                detail = f"post-invocation {exc.gate}: {exc.detail}"
        except verify.GateFailure as exc:
            result_class = "IDENTITY FAILURE"
            detail = f"pre-invocation {exc.gate}: {exc.detail}"
            source_identity = {
                "path": str(fixture_source),
                "sha256": fixture_sha256,
                "status": "NOT VERIFIED",
            }
        except OSError as exc:
            result_class = "INFRASTRUCTURE EXECUTION UNAVAILABLE"
            detail = f"fixture staging unavailable: {exc}"
            source_identity = {
                "path": str(fixture_source),
                "sha256": fixture_sha256,
                "status": "NOT STAGED",
            }
    assert result_class in RESULT_CLASSES
    ended = datetime.now(timezone.utc)
    raw_root = root / "execution" / "raw" / "emilia" / fixture_id
    _record_output(root, output_ledger, raw_root / "stdout.bin", stdout)
    _record_output(root, output_ledger, raw_root / "stderr.bin", stderr)
    invocation = {
        "schema_version": "wexp-emilia-raw-invocation-1",
        "system": "EMILIA",
        "fixture_id": fixture_id,
        "fixture_source": source_identity,
        "staged_fixture": staged_identity,
        "command_argv_template": implementation["command_argv"],
        "argv": argv,
        "cwd": str(repository),
        "invocation_attempted": invocation_attempted,
        "implementation_invoked": implementation_invoked,
        "started_at_utc": started.isoformat().replace("+00:00", "Z"),
        "ended_at_utc": ended.isoformat().replace("+00:00", "Z"),
        "duration_seconds": time.monotonic() - monotonic_start,
        "exit_code": exit_code,
        "timed_out": timed_out,
        "timeout_seconds": timeout,
        "execution_identity": execution_identity,
        "stdout_bytes": len(stdout),
        "stdout_sha256": hashlib.sha256(stdout).hexdigest(),
        "stderr_bytes": len(stderr),
        "stderr_sha256": hashlib.sha256(stderr).hexdigest(),
    }
    _record_output(
        root,
        output_ledger,
        raw_root / "invocation.json",
        _canonical_json_bytes(invocation),
    )
    normalized = {
        "schema_version": "wexp-emilia-normalized-execution-result-1",
        "system": "EMILIA",
        "fixture_id": fixture_id,
        "result_class": result_class,
        "detail": detail,
        "expected_result": expected_result,
        "observed_result": None if parsed is None else parsed.get("observed_result"),
        "implementation_invoked": implementation_invoked,
        "execution_identity": execution_identity,
        "raw": {
            "stdout": f"execution/raw/emilia/{fixture_id}/stdout.bin",
            "stderr": f"execution/raw/emilia/{fixture_id}/stderr.bin",
            "invocation": f"execution/raw/emilia/{fixture_id}/invocation.json",
        },
    }
    _record_output(
        root,
        output_ledger,
        root / "execution" / "normalized" / "emilia" / f"{fixture_id}.json",
        _canonical_json_bytes(normalized),
    )
    return normalized


def _record_wexp_nonconstructibility(
    root: Path,
    fixture_id: str,
    reason: str,
    execution_identity: dict[str, Any],
    output_ledger: dict[str, str],
) -> dict[str, Any]:
    normalized = {
        "schema_version": "wexp-emilia-normalized-execution-result-1",
        "system": "WEXP",
        "fixture_id": fixture_id,
        "result_class": "IMPLEMENTATION INPUT NOT CONSTRUCTIBLE",
        "detail": reason,
        "implementation_invoked": False,
        "not_equivalent_to": "FAIL",
        "execution_identity": execution_identity,
    }
    _record_output(
        root,
        output_ledger,
        root / "execution" / "normalized" / "wexp" / f"{fixture_id}.json",
        _canonical_json_bytes(normalized),
    )
    return normalized


def _execution_manifest_bytes(root: Path, ledger: dict[str, str]) -> bytes:
    manifest_path = root / "execution" / "EXECUTION-MANIFEST.sha256"
    members = {
        path.relative_to(root).as_posix()
        for path in _planned_output_paths(root)
        if path != manifest_path
    }
    if set(ledger) != members:
        raise RuntimeError(
            "completed execution ledger is incomplete or contains unknown paths: "
            f"missing={sorted(members - set(ledger))}, "
            f"unknown={sorted(set(ledger) - members)}"
        )
    _verify_output_ledger(root, ledger)
    lines = [
        f"{ledger[relative]}  {relative}\n"
        for relative in sorted(members)
    ]
    return "".join(lines).encode("utf-8")


def _default_root() -> Path:
    return Path(__file__).resolve().parents[1]


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-root", type=Path, default=_default_root())
    parser.add_argument("--package-manifest-sha256")
    parser.add_argument("--emilia-expectation-sha256")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--preflight", action="store_true", help="verify only; this is the default and never invokes an implementation")
    mode.add_argument("--execute", action="store_true", help="future use only after both freezes and joint control review")
    parser.add_argument("--acknowledge", help="required exact execution acknowledgement")
    args = parser.parse_args(list(argv) if argv is not None else None)

    # FIRST IDENTITY/LIFECYCLE OPERATION: refuse any preserved prior capture
    # before a fresh-ready statement. This path-presence guard makes no claim
    # that a pre-existing capture is authentic; it only makes rerun impossible.
    try:
        root = args.package_root.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        _emit_json({
            "schema_version": "wexp-emilia-execution-refusal-1",
            "status": "REFUSED BEFORE IMPLEMENTATION EXECUTION",
            "result_class": "IDENTITY FAILURE",
            "gate": "PACKAGE_ROOT",
            "detail": f"package root cannot be resolved: {exc}",
            "execution_started_this_invocation": False,
        })
        return 21
    existing_outputs = [
        str(path.relative_to(root))
        for path in _planned_output_paths(root)
        if path.exists() or path.is_symlink()
    ]
    if existing_outputs:
        _emit_json({
            "schema_version": "wexp-emilia-execution-refusal-1",
            "status": "REFUSED; PRESERVED EXECUTION PATHS EXIST",
            "result_class": "IDENTITY FAILURE",
            "gate": "IMMUTABLE_OUTPUTS",
            "detail": f"planned output paths already exist: {existing_outputs}",
            "capture_authenticity_reverified": False,
            "execution_started_this_invocation": False,
            "rerun_permitted": False,
        })
        return 25
    if (
        (args.execute or args.emilia_expectation_sha256 is not None)
        and not args.package_manifest_sha256
    ):
        _emit_json({
            "schema_version": "wexp-emilia-execution-refusal-1",
            "status": "REFUSED BEFORE IMPLEMENTATION EXECUTION",
            "result_class": "IDENTITY FAILURE",
            "gate": "PACKAGE_MANIFEST",
            "detail": "an externally authenticated package-manifest SHA-256 is required before future expectation/control verification",
            "execution_started_this_invocation": False,
        })
        return 23

    # FULL IDENTITY OPERATION: verify every frozen identity, the supplied
    # EMILIA expectation pin, both declared baselines, and the package manifest.
    # No output directory or environment record is created before this returns.
    try:
        verification = verify.verify_package(
            args.package_root,
            package_manifest_sha256=args.package_manifest_sha256,
            emilia_expectation_sha256=args.emilia_expectation_sha256,
            require_future=True,
        )
    except verify.GateFailure as exc:
        _emit_json({
            "schema_version": "wexp-emilia-execution-refusal-1",
            "status": "REFUSED BEFORE IMPLEMENTATION EXECUTION",
            "result_class": exc.result_class,
            "gate": exc.gate,
            "detail": exc.detail,
            "execution_started_this_invocation": False,
        })
        return 20 if exc.result_class == verify.EXPECTATION_MISSING else 21
    except Exception as exc:
        _emit_json({
            "schema_version": "wexp-emilia-execution-refusal-1",
            "status": "REFUSED BEFORE IMPLEMENTATION EXECUTION",
            "result_class": "IDENTITY FAILURE",
            "gate": "HARNESS",
            "detail": f"unexpected verifier failure: {type(exc).__name__}: {exc}",
            "execution_started_this_invocation": False,
        })
        return 22

    if not args.package_manifest_sha256 or not args.emilia_expectation_sha256:
        _emit_json({
            "schema_version": "wexp-emilia-execution-refusal-1",
            "status": "REFUSED BEFORE IMPLEMENTATION EXECUTION",
            "result_class": "IDENTITY FAILURE",
            "detail": "external package-manifest and EMILIA-expectation SHA-256 pins are mandatory for a ready preflight or execution",
            "execution_started_this_invocation": False,
        })
        return 23
    if not args.execute:
        _emit_json({
            "schema_version": "wexp-emilia-execution-preflight-1",
            "status": "READY; EXECUTION NOT STARTED",
            "identity_gates": "PASS",
            "execution_started_this_invocation": False,
            "verification": verification,
        })
        return 0
    if args.acknowledge != ACKNOWLEDGEMENT:
        _emit_json({
            "schema_version": "wexp-emilia-execution-refusal-1",
            "status": "REFUSED BEFORE IMPLEMENTATION EXECUTION",
            "result_class": "IDENTITY FAILURE",
            "detail": "execution acknowledgement absent or incorrect",
            "execution_started_this_invocation": False,
        })
        return 24

    control_gate = next(
        gate for gate in verification["gates"] if gate["gate"] == "BASELINES_AND_CONTROL"
    )
    emilia_gate = next(
        gate for gate in verification["gates"] if gate["gate"] == "EMILIA_EXPECTATION"
    )
    control = control_gate["validated_control"]
    verification_bytes = _canonical_json_bytes(verification)
    try:
        _, pre_run_manifest_bytes = _read_frozen_bytes(
            root / "MANIFEST.sha256",
            args.package_manifest_sha256,
            "PACKAGE_MANIFEST",
        )
    except verify.GateFailure as exc:
        _emit_json({
            "schema_version": "wexp-emilia-execution-refusal-1",
            "status": "REFUSED BEFORE IMPLEMENTATION EXECUTION",
            "result_class": "IDENTITY FAILURE",
            "gate": exc.gate,
            "detail": exc.detail,
            "execution_started_this_invocation": False,
        })
        return 25
    execution_identity = {
        "pre_run_package_manifest_sha256": args.package_manifest_sha256,
        "emilia_expectation_sha256": args.emilia_expectation_sha256,
        "emilia_commitment_identity": emilia_gate["commitment_identity"],
        "execution_control_sha256": control_gate["control_sha256"],
        "verification_report_sha256": hashlib.sha256(verification_bytes).hexdigest(),
        "P_sha256": verify.EXPECTED_P_SHA256,
        "P-1_sha256": verify.EXPECTED_P1_SHA256,
        "wexp_expectation_sha256": verify.EXPECTED_WEXP_EXPECTATION_SHA256,
        "wexp_semantic_authority": verify.EXPECTED_WEXP_AUTHORITY,
        "emilia_semantic_authority": verify.EXPECTED_EMILIA_AUTHORITY,
        "adapter_executable_sha256": control_gate["adapter_executable"]["sha256"],
        "adapter_executable_path": control_gate["adapter_executable"]["path"],
        "adapter_entrypoint": control_gate["adapter_entrypoint"],
        "emilia_repository_path": control_gate["emilia_baseline"]["repository_path"],
    }
    run_start = {
        "schema_version": "wexp-emilia-run-start-1",
        "started_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "single_use": True,
        "execution_identity": execution_identity,
    }
    output_ledger: dict[str, str] = {}
    try:
        _record_output(
            root,
            output_ledger,
            root / "execution" / "RUN-START.json",
            _canonical_json_bytes(run_start),
        )
    except FileExistsError:
        _emit_json({
            "schema_version": "wexp-emilia-execution-refusal-1",
            "status": "REFUSED BEFORE IMPLEMENTATION EXECUTION",
            "result_class": "IDENTITY FAILURE",
            "gate": "RUN_LOCK",
            "detail": "another or prior execution already acquired the single-use run lock",
            "execution_started_this_invocation": False,
        })
        return 25
    _record_output(
        root,
        output_ledger,
        root / "execution" / "VERIFICATION-REPORT.json",
        verification_bytes,
    )
    _record_output(
        root,
        output_ledger,
        root / "execution" / "PRE-RUN-MANIFEST.sha256",
        pre_run_manifest_bytes,
    )
    environment = _capture_environment(
        control,
        execution_identity,
        control_gate["emilia_baseline"],
        control_gate["adapter_executable"],
        control_gate["adapter_entrypoint"],
        control_gate["runtime_versions"],
    )
    _record_output(
        root,
        output_ledger,
        root / "reproduction" / "environment" / "EXECUTION-ENVIRONMENT.json",
        _canonical_json_bytes(environment),
    )

    results: list[dict[str, Any]] = []
    wexp_reason = control["wexp"]["reason"]
    for fixture_id in ("P", "P-1"):
        results.append(
            _record_wexp_nonconstructibility(
                root,
                fixture_id,
                wexp_reason,
                execution_identity,
                output_ledger,
            )
        )
    _verify_output_ledger(root, output_ledger)
    _verify_runtime_package_coverage(root, output_ledger)

    fixture_paths = {
        "P": (
            root / "source" / "pair-freeze" / "fixtures" / "WE-EP-P.json",
            verify.EXPECTED_P_SHA256,
        ),
        "P-1": (
            root / "source" / "pair-freeze" / "fixtures" / "WE-EP-P-1.json",
            verify.EXPECTED_P1_SHA256,
        ),
    }
    expected_results = control["normalization"]["expected_results"]
    for fixture_id in ("P", "P-1"):
        fixture_path, fixture_sha256 = fixture_paths[fixture_id]
        emilia_result = _invoke_emilia(
            root,
            control,
            fixture_id,
            fixture_path,
            fixture_sha256,
            expected_results[fixture_id],
            execution_identity,
            output_ledger,
        )
        results.append(emilia_result)
        if emilia_result["result_class"] == "IDENTITY FAILURE":
            _emit_json({
                "schema_version": "wexp-emilia-partial-execution-1",
                "status": "STOPPED ON IDENTITY FAILURE; PARTIAL CAPTURE MUST BE FROZEN",
                "result_class": "IDENTITY FAILURE",
                "fixture_id": fixture_id,
                "P_P-1_further_execution_stopped": True,
                "execution_identity": execution_identity,
            })
            return 26
        _verify_output_ledger(root, output_ledger)
        _verify_runtime_package_coverage(root, output_ledger)

    summary = {
        "schema_version": "wexp-emilia-execution-summary-1",
        "completed_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "pre_run_identity_gates": "PASS",
        "per_invocation_runtime_identity_gates": "PASS",
        "execution_identity": execution_identity,
        "capture_status": "CAPTURE FILE SET COMPLETE; FINALIZATION DETERMINED BY EXECUTION-MANIFEST PRESENCE",
        "result_classes_preserved": True,
        "terminal_branch_selected": None,
        "note": "Terminal branch selection requires comparison and joint review; it is not performed by this runner.",
        "results": results,
    }
    _record_output(
        root,
        output_ledger,
        root / "execution" / "normalized" / "summary.json",
        _canonical_json_bytes(summary),
    )
    _verify_output_ledger(root, output_ledger)
    _verify_runtime_package_coverage(root, output_ledger)
    execution_manifest_path = root / "execution" / "EXECUTION-MANIFEST.sha256"
    _write_bytes(
        execution_manifest_path,
        _execution_manifest_bytes(root, output_ledger),
    )
    verify._verify_manifest(execution_manifest_path, root)
    _verify_runtime_package_coverage(
        root,
        output_ledger,
        {"execution/EXECUTION-MANIFEST.sha256"},
    )
    _emit_json(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
