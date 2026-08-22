#!/usr/bin/env python3
"""Fail-closed identity verifier for WEXP × EMILIA INTEROP-001.

This module hashes and structurally compares frozen files.  It never invokes a
WEXP engine, the EMILIA implementation, or any semantic adapter.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

sys.dont_write_bytecode = True

from exact_json import canonical_json_bytes, parse_decimal, validate_json_limits


IDENTITY_FAILURE = "IDENTITY FAILURE"
EXPECTATION_MISSING = "EXPECTATION MISSING / NOT FROZEN"
CONFIGURATION_FAILURE = "IDENTITY FAILURE"

EXPECTED_P_SHA256 = "b552da51858d0256a562e800a81a870435d6e136c9bc28833b962b6d3723fb3e"
EXPECTED_P1_SHA256 = "67556d28d272b4b01a73e1c1465248644dd7a05460fc149aa77df92cf36403a0"
EXPECTED_P_BYTES = 7255
EXPECTED_P1_BYTES = 7152
EXPECTED_ORIGINAL_FIXTURES_SHA256 = "d972dbb549aaaa25e92c32a936acba4d9a686e9ca62fe6bd556b12be2962cfcc"
EXPECTED_COMPARISON_SHA256 = "272a9b08a213702ee2156438b7736b954c7a32bc4a190cce92d3d82226266934"
EXPECTED_WEXP_READING_SHA256 = "a185e6760de149375e657b1429adc1ea329ed9f9705b9d1c2b505dcc8e3ea984"
EXPECTED_EMILIA_READING_SHA256 = "b43f8ac6dce465258c75a42117d2750a6bafa163846251416e87cec371a4bad6"
EXPECTED_PAIR_ARCHIVE_SHA256 = "ae237263c86ee0b5c2b6387159d81957efe47e20161b74dd363da5a530705282"
EXPECTED_PAIR_ARCHIVE_BYTES = 18158
EXPECTED_PAIR_MANIFEST_SHA256 = "5375841c5c7d550d1dcbb3ac31e73ab6c5d68a2bc1eb4fea5249dec9dbdce604"
EXPECTED_PAIR_FULL_MANIFEST_SHA256 = "ae6e2345e51cd32aad6e1aa7ce3d4ffeb7b4b005ebcbc19dc067ee22c6b52022"
EXPECTED_WEXP_EXPECTATION_SHA256 = "42eeecaba33238d8c94bbb9d5bb22ab46721de6de74cff455b8115c17892088a"
EXPECTED_ENVELOPE_SHA256 = "d7dddd96ad6488433002c0f6206775ed68790d25d33bb0f316df07b7f1399f3f"
EXPECTED_WEXP_AUTHORITY = "b28a46e7764c2ef14decc35394f21278fca9c988"
EXPECTED_EMILIA_AUTHORITY = "9a04bea7fe680345132f6f6251fdb9a63fd8aeb2"
EXPECTED_WEXP_NONCONSTRUCTIBILITY_REASON = (
    "No frozen public EP-to-WEXP profile constructs the complete Core "
    "AppraisalInput for P or P-1."
)
EXPECTED_WEXP_EXECUTION_BASELINE = (
    "NOT APPLICABLE — INPUT NOT CONSTRUCTIBLE UNDER FROZEN PUBLIC MAPPING SURFACE"
)
READY_CONTROL_STATE = "READY — BOTH EXPECTATIONS FROZEN AND CONTROL REVIEWED"


class GateFailure(RuntimeError):
    def __init__(self, result_class: str, gate: str, detail: str) -> None:
        super().__init__(detail)
        self.result_class = result_class
        self.gate = gate
        self.detail = detail


def _json_no_duplicates(path: Path) -> Any:
    def hook(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON member: {key}")
            result[key] = value
        return result

    def reject_constant(value: str) -> None:
        raise ValueError(f"non-standard JSON constant: {value}")

    try:
        value = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=hook,
            parse_constant=reject_constant,
            parse_float=parse_decimal,
        )
        validate_json_limits(value)
        return value
    except (OSError, UnicodeError, json.JSONDecodeError, RecursionError, ValueError) as exc:
        raise GateFailure(IDENTITY_FAILURE, "JSON", f"cannot parse {path}: {exc}") from exc


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as exc:
        raise GateFailure(IDENTITY_FAILURE, "FILE", f"cannot read {path}: {exc}") from exc
    return digest.hexdigest()


def _emit_json(value: Any) -> None:
    sys.stdout.buffer.write(canonical_json_bytes(value))


def _safe_path(root: Path, relative: str) -> Path:
    candidate = root / relative
    try:
        resolved_root = root.resolve(strict=True)
        resolved_candidate = candidate.resolve(strict=False)
    except OSError as exc:
        raise GateFailure(IDENTITY_FAILURE, "PATH", f"cannot resolve {relative}: {exc}") from exc
    if resolved_candidate != resolved_root and resolved_root not in resolved_candidate.parents:
        raise GateFailure(IDENTITY_FAILURE, "PATH", f"path escapes package root: {relative}")
    return candidate


def _require_file(root: Path, relative: str) -> Path:
    path = _safe_path(root, relative)
    if path.is_symlink() or not path.is_file():
        raise GateFailure(IDENTITY_FAILURE, "FILE", f"required regular file absent: {relative}")
    return path


def _require_identity(
    path: Path,
    expected_sha256: str,
    *,
    expected_bytes: int | None = None,
    gate: str = "HASH",
) -> dict[str, Any]:
    try:
        if path.is_symlink() or not path.is_file():
            raise GateFailure(
                IDENTITY_FAILURE,
                gate,
                f"required identity is not a regular non-symlink file: {path}",
            )
        actual_bytes = path.stat().st_size
    except GateFailure:
        raise
    except OSError as exc:
        raise GateFailure(
            IDENTITY_FAILURE,
            gate,
            f"cannot inspect {path}: {exc}",
        ) from exc
    actual_sha256 = sha256_file(path)
    if actual_sha256 != expected_sha256:
        raise GateFailure(
            IDENTITY_FAILURE,
            gate,
            f"SHA-256 mismatch for {path}: expected {expected_sha256}, got {actual_sha256}",
        )
    if expected_bytes is not None and actual_bytes != expected_bytes:
        raise GateFailure(
            IDENTITY_FAILURE,
            gate,
            f"byte-count mismatch for {path}: expected {expected_bytes}, got {actual_bytes}",
        )
    return {"path": str(path), "bytes": actual_bytes, "sha256": actual_sha256}


_MANIFEST_LINE = re.compile(r"^([0-9a-f]{64})  ([^\r\n]+)$")


def _parse_manifest_bytes(data: bytes, identity: str) -> list[tuple[str, str]]:
    try:
        text = data.decode("utf-8")
    except UnicodeError as exc:
        raise GateFailure(IDENTITY_FAILURE, "MANIFEST", f"{identity} is not UTF-8") from exc
    entries: list[tuple[str, str]] = []
    seen: set[str] = set()
    for number, line in enumerate(text.splitlines(), start=1):
        match = _MANIFEST_LINE.fullmatch(line)
        if not match:
            raise GateFailure(IDENTITY_FAILURE, "MANIFEST", f"invalid line {number} in {identity}")
        expected, relative = match.groups()
        if relative in seen:
            raise GateFailure(IDENTITY_FAILURE, "MANIFEST", f"duplicate path in {identity}: {relative}")
        if relative.startswith("/") or ".." in Path(relative).parts:
            raise GateFailure(IDENTITY_FAILURE, "MANIFEST", f"unsafe path in {identity}: {relative}")
        seen.add(relative)
        entries.append((expected, relative))
    if not entries:
        raise GateFailure(IDENTITY_FAILURE, "MANIFEST", f"empty manifest: {identity}")
    return entries


def _verify_manifest(manifest: Path, content_root: Path) -> dict[str, Any]:
    try:
        manifest_bytes = manifest.read_bytes()
    except OSError as exc:
        raise GateFailure(
            IDENTITY_FAILURE,
            "MANIFEST",
            f"cannot read manifest {manifest}: {exc}",
        ) from exc
    entries = _parse_manifest_bytes(manifest_bytes, str(manifest))
    verified: list[dict[str, str]] = []
    for expected, relative in entries:
        member = _require_file(content_root, relative)
        actual = sha256_file(member)
        if actual != expected:
            raise GateFailure(
                IDENTITY_FAILURE,
                "MANIFEST",
                f"manifest mismatch for {relative}: expected {expected}, got {actual}",
            )
        verified.append({"path": relative, "sha256": actual})
    return {"manifest": str(manifest), "entries_verified": len(verified), "members": verified}


def _verify_root_manifest_coverage(root: Path, manifest_members: set[str]) -> dict[str, Any]:
    if "MANIFEST.sha256" in manifest_members:
        raise GateFailure(IDENTITY_FAILURE, "PACKAGE_MANIFEST", "root manifest must exclude itself")
    actual_members: set[str] = set()
    try:
        for entry in root.rglob("*"):
            relative = entry.relative_to(root).as_posix()
            if entry.is_symlink():
                raise GateFailure(IDENTITY_FAILURE, "PACKAGE_MANIFEST", f"symlink is not permitted: {relative}")
            if entry.is_file():
                if relative != "MANIFEST.sha256":
                    actual_members.add(relative)
            elif not entry.is_dir():
                raise GateFailure(IDENTITY_FAILURE, "PACKAGE_MANIFEST", f"special filesystem entry is not permitted: {relative}")
    except OSError as exc:
        raise GateFailure(IDENTITY_FAILURE, "PACKAGE_MANIFEST", f"cannot enumerate package tree: {exc}") from exc
    if actual_members != manifest_members:
        unpinned = sorted(actual_members - manifest_members)
        absent = sorted(manifest_members - actual_members)
        raise GateFailure(
            IDENTITY_FAILURE,
            "PACKAGE_MANIFEST",
            f"manifest coverage mismatch; unpinned={unpinned}, absent={absent}",
        )
    return {"coverage": "EXACT", "payload_files": len(actual_members), "symlinks": 0}


def _verify_pair_archive(archive: Path, unpacked: Path) -> dict[str, Any]:
    prefix = "WEXP-EMILIA-PAIR-FREEZE-001/"
    expected_relatives = {
        "EXPERIMENT-PROPOSITION.md",
        "MANIFEST.sha256",
        "PAIR-DELTA.md",
        "PAIR-MANIFEST.sha256",
        "README.md",
        "WEXP-DERIVATION.md",
        "fixtures/WE-EP-P-1.json",
        "fixtures/WE-EP-P.json",
        "wexp-expectation.yaml",
    }
    try:
        with zipfile.ZipFile(archive, "r") as bundle:
            corrupt = bundle.testzip()
            if corrupt is not None:
                raise GateFailure(IDENTITY_FAILURE, "ZIP", f"ZIP CRC failure: {corrupt}")
            names = bundle.namelist()
            if len(names) != 9 or set(names) != {prefix + item for item in expected_relatives}:
                raise GateFailure(IDENTITY_FAILURE, "ZIP", "archive member set is not the frozen nine-file set")
            if any(info.flag_bits & 0x1 for info in bundle.infolist()):
                raise GateFailure(IDENTITY_FAILURE, "ZIP", "encrypted archive member is not permitted")
            manifest_bytes = bundle.read(prefix + "MANIFEST.sha256")
            manifest_entries = _parse_manifest_bytes(manifest_bytes, "archive MANIFEST.sha256")
            for expected, relative in manifest_entries:
                member_bytes = bundle.read(prefix + relative)
                actual = hashlib.sha256(member_bytes).hexdigest()
                if actual != expected:
                    raise GateFailure(IDENTITY_FAILURE, "ZIP", f"archive manifest mismatch: {relative}")
            for relative in expected_relatives:
                archived = bundle.read(prefix + relative)
                local = _require_file(unpacked, relative).read_bytes()
                if archived != local:
                    raise GateFailure(IDENTITY_FAILURE, "ZIP", f"archive/unpacked byte mismatch: {relative}")
    except zipfile.BadZipFile as exc:
        raise GateFailure(IDENTITY_FAILURE, "ZIP", f"invalid ZIP: {exc}") from exc
    return {"integrity": "PASS", "members_verified": 9, "unpacked_byte_identity": "PASS"}


def _pointer_escape(value: str) -> str:
    return value.replace("~", "~0").replace("/", "~1")


def _diff_json(left: Any, right: Any, pointer: str = "") -> list[dict[str, Any]]:
    differences: list[dict[str, Any]] = []
    if type(left) is not type(right):
        return [{"path": pointer or "/", "kind": "type_or_value", "left": left, "right": right}]
    if isinstance(left, dict):
        for key in left:
            child = pointer + "/" + _pointer_escape(key)
            if key not in right:
                differences.append({"path": child, "kind": "removed", "left": left[key]})
            else:
                differences.extend(_diff_json(left[key], right[key], child))
        for key in right:
            if key not in left:
                child = pointer + "/" + _pointer_escape(key)
                differences.append({"path": child, "kind": "added", "right": right[key]})
        return differences
    if isinstance(left, list):
        if len(left) != len(right):
            differences.append({"path": pointer or "/", "kind": "length", "left": len(left), "right": len(right)})
            return differences
        for index, (left_item, right_item) in enumerate(zip(left, right)):
            differences.extend(_diff_json(left_item, right_item, pointer + f"/{index}"))
        return differences
    if left != right:
        differences.append({"path": pointer or "/", "kind": "changed", "left": left, "right": right})
    return differences


def _verify_pair_delta(p_path: Path, p1_path: Path) -> dict[str, Any]:
    p = _json_no_duplicates(p_path)
    p1 = _json_no_duplicates(p1_path)
    differences = _diff_json(p, p1)
    observed = {(item["path"], item["kind"]) for item in differences}
    expected = {
        ("/emilia_input/observations/1/action_caid", "removed"),
        ("/emilia_input/observations/1/proof/signature_b64u", "changed"),
    }
    if observed != expected or len(differences) != 2:
        raise GateFailure(IDENTITY_FAILURE, "PAIR_DELTA", f"unexpected JSON delta: {differences!r}")

    restored = copy.deepcopy(p1)
    p_meter = p["emilia_input"]["observations"][1]
    restored_meter = restored["emilia_input"]["observations"][1]
    ordered_meter: dict[str, Any] = {}
    for key in p_meter:
        if key == "action_caid":
            ordered_meter[key] = p_meter[key]
        else:
            ordered_meter[key] = restored_meter[key]
    ordered_meter["proof"]["signature_b64u"] = p_meter["proof"]["signature_b64u"]
    restored["emilia_input"]["observations"][1] = ordered_meter
    restored_bytes = canonical_json_bytes(restored, sort_keys=False)
    if restored_bytes != p_path.read_bytes():
        raise GateFailure(IDENTITY_FAILURE, "PAIR_DELTA", "restoring the field and signature does not reproduce exact P bytes")
    return {
        "status": "PASS",
        "removed": "/emilia_input/observations/1/action_caid",
        "derivative_change": "/emilia_input/observations/1/proof/signature_b64u",
        "exact_p_bytes_restored": True,
    }


def _verify_git_baseline(implementation: dict[str, Any], required_head: str | None = None) -> dict[str, Any]:
    import subprocess

    try:
        repo = Path(str(implementation.get("repository_path", ""))).expanduser().resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise GateFailure(IDENTITY_FAILURE, "BASELINE", f"repository path cannot be resolved: {exc}") from exc
    expected_head = implementation.get("expected_head")
    expected_tree = implementation.get("expected_tree")
    if required_head is not None and expected_head != required_head:
        raise GateFailure(IDENTITY_FAILURE, "BASELINE", "declared implementation HEAD differs from frozen semantic baseline")
    if not repo.is_dir():
        raise GateFailure(IDENTITY_FAILURE, "BASELINE", f"repository unavailable: {repo}")

    git_executable = shutil.which("git")
    if git_executable is None:
        raise GateFailure(IDENTITY_FAILURE, "BASELINE", "git executable is unavailable")
    git_environment = {
        "PATH": os.path.dirname(git_executable),
        "LANG": "C",
        "LC_ALL": "C",
        "TZ": "UTC",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_OPTIONAL_LOCKS": "0",
    }

    def git(*args: str) -> str:
        try:
            completed = subprocess.run(
                [git_executable, "-C", str(repo), *args],
                check=True,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=30,
                env=git_environment,
            )
        except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            raise GateFailure(IDENTITY_FAILURE, "BASELINE", f"git identity check failed for {repo}: {exc}") from exc
        return completed.stdout.strip()

    actual_head = git("rev-parse", "HEAD")
    actual_tree = git("rev-parse", "HEAD^{tree}")
    dirty = git(
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
        "--ignore-submodules=none",
    )
    git_version = git("--version")
    if actual_head != expected_head or actual_tree != expected_tree:
        raise GateFailure(IDENTITY_FAILURE, "BASELINE", f"repository HEAD/TREE mismatch: {repo}")
    if implementation.get("require_clean") is not True or dirty:
        raise GateFailure(IDENTITY_FAILURE, "BASELINE", f"repository is dirty or clean-state gate disabled: {repo}")
    return {
        "repository_path": str(repo),
        "head": actual_head,
        "tree": actual_tree,
        "dirty": False,
        "git_executable": str(Path(git_executable).resolve(strict=True)),
        "git_executable_sha256": sha256_file(Path(git_executable).resolve(strict=True)),
        "git_version": git_version,
    }


def _command_uses_shell(argv: list[str]) -> bool:
    shell_names = {"sh", "bash", "zsh", "dash", "fish", "cmd", "cmd.exe", "powershell", "powershell.exe", "pwsh", "pwsh.exe"}

    def basename(value: str) -> str:
        return value.replace("\\", "/").rsplit("/", 1)[-1].lower()

    if not argv:
        return False
    first = basename(argv[0])
    if first in shell_names:
        return True
    return first in {"env", "env.exe"}


def _read_tracked_head_blob(repository: Path, relative: str) -> bytes:
    import subprocess

    git_executable = shutil.which("git")
    if git_executable is None:
        raise GateFailure(IDENTITY_FAILURE, "ADAPTER_ENTRYPOINT", "git executable is unavailable")
    environment = {
        "PATH": os.path.dirname(git_executable),
        "LANG": "C",
        "LC_ALL": "C",
        "TZ": "UTC",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_OPTIONAL_LOCKS": "0",
    }
    try:
        completed = subprocess.run(
            [git_executable, "-C", str(repository), "cat-file", "blob", f"HEAD:{relative}"],
            check=True,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30,
            env=environment,
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        raise GateFailure(
            IDENTITY_FAILURE,
            "ADAPTER_ENTRYPOINT",
            f"adapter entrypoint is not a tracked blob at pinned HEAD: {relative}: {exc}",
        ) from exc
    return completed.stdout


def _resolve_executable(
    argv0: str, repository: Path, environment: dict[str, str]
) -> dict[str, Any]:
    try:
        candidate = Path(argv0).expanduser()
        if candidate.is_absolute():
            resolved = candidate.resolve(strict=False)
        elif "/" in argv0 or "\\" in argv0:
            resolved = (repository / candidate).resolve(strict=False)
        else:
            normalized_entries = [
                str(
                    Path(entry).expanduser().resolve(strict=False)
                    if Path(entry).expanduser().is_absolute()
                    else (repository / Path(entry).expanduser()).resolve(strict=False)
                )
                for entry in environment.get("PATH", "").split(os.pathsep)
                if entry
            ]
            if not normalized_entries:
                raise GateFailure(
                    IDENTITY_FAILURE,
                    "CONTROL",
                    "adapter PATH contains no explicit search directory",
                )
            normalized_path = os.pathsep.join(normalized_entries)
            located = shutil.which(argv0, path=normalized_path)
            if located is None:
                raise GateFailure(IDENTITY_FAILURE, "CONTROL", f"adapter executable is unavailable: {argv0}")
            resolved = Path(located).resolve(strict=False)
    except GateFailure:
        raise
    except (OSError, RuntimeError) as exc:
        raise GateFailure(
            IDENTITY_FAILURE,
            "CONTROL",
            f"adapter executable path cannot be resolved: {exc}",
        ) from exc
    if not resolved.is_file() or not os.access(resolved, os.X_OK):
        raise GateFailure(IDENTITY_FAILURE, "CONTROL", f"adapter executable is absent, non-regular, or non-executable: {resolved}")
    return {"path": str(resolved), "sha256": sha256_file(resolved)}


def _verify_adapter_entrypoint(
    implementation: dict[str, Any],
    repository: Path,
    adapter_executable: dict[str, Any],
) -> dict[str, Any]:
    descriptor = implementation.get("adapter_entrypoint")
    if not isinstance(descriptor, dict) or set(descriptor) != {
        "mode",
        "argv_index",
        "repository_relative_path",
        "expected_sha256",
    }:
        raise GateFailure(
            IDENTITY_FAILURE,
            "CONTROL",
            "adapter_entrypoint descriptor is incomplete or unknown",
        )
    mode = descriptor.get("mode")
    argv_index = descriptor.get("argv_index")
    relative = descriptor.get("repository_relative_path")
    expected_sha256 = descriptor.get("expected_sha256")
    argv = implementation["command_argv"]
    if type(argv_index) is not int or not 0 <= argv_index < len(argv):
        raise GateFailure(
            IDENTITY_FAILURE,
            "CONTROL",
            "adapter_entrypoint argv_index is outside command_argv",
        )

    if mode == "EXECUTABLE_IS_ADAPTER":
        if (
            argv_index != 0
            or implementation.get("container_runtime") != "NONE"
            or relative is not None
            or expected_sha256 != adapter_executable["sha256"]
        ):
            raise GateFailure(
                IDENTITY_FAILURE,
                "CONTROL",
                "executable adapter entrypoint is not bound to reviewed argv[0]",
            )
        return {
            "mode": mode,
            "argv_index": 0,
            "path": adapter_executable["path"],
            "sha256": adapter_executable["sha256"],
        }

    if mode == "REPOSITORY_FILE":
        relative_parts = relative.split("/") if isinstance(relative, str) else []
        if (
            argv_index == 0
            or implementation.get("container_runtime") != "NONE"
            or not isinstance(relative, str)
            or not relative
            or relative.startswith("/")
            or "\\" in relative
            or ":" in relative
            or any(ord(character) < 32 for character in relative)
            or any(part in {"", ".", ".."} for part in relative_parts)
            or "{" in relative
            or "}" in relative
            or argv[argv_index] != relative
            or not isinstance(expected_sha256, str)
            or not re.fullmatch(r"[0-9a-f]{64}", expected_sha256)
        ):
            raise GateFailure(
                IDENTITY_FAILURE,
                "CONTROL",
                "repository adapter entrypoint is unsafe or not an exact argv member",
            )
        try:
            resolved_repository = repository.resolve(strict=True)
            resolved = (resolved_repository / relative).resolve(strict=True)
        except (OSError, RuntimeError) as exc:
            raise GateFailure(
                IDENTITY_FAILURE,
                "CONTROL",
                f"repository adapter entrypoint cannot be resolved: {exc}",
            ) from exc
        if resolved_repository not in resolved.parents:
            raise GateFailure(
                IDENTITY_FAILURE,
                "CONTROL",
                "repository adapter entrypoint escapes the pinned checkout",
            )
        identity = _require_identity(
            resolved,
            expected_sha256,
            gate="ADAPTER_ENTRYPOINT",
        )
        head_blob = _read_tracked_head_blob(resolved_repository, relative)
        head_blob_sha256 = hashlib.sha256(head_blob).hexdigest()
        if head_blob_sha256 != expected_sha256:
            raise GateFailure(
                IDENTITY_FAILURE,
                "ADAPTER_ENTRYPOINT",
                "worktree adapter entrypoint does not equal its tracked blob at pinned HEAD",
            )
        _require_identity(
            resolved,
            expected_sha256,
            gate="ADAPTER_ENTRYPOINT",
        )
        return {
            "mode": mode,
            "argv_index": argv_index,
            "path": str(resolved),
            "sha256": identity["sha256"],
            "head_blob_sha256": head_blob_sha256,
            "repository_relative_path": relative,
        }

    if mode == "CONTAINER_IMAGE":
        reference = implementation.get("container_image_reference")
        if (
            implementation.get("container_runtime") == "NONE"
            or relative is not None
            or expected_sha256 is not None
            or argv[argv_index] != reference
        ):
            raise GateFailure(
                IDENTITY_FAILURE,
                "CONTROL",
                "container adapter entrypoint is not bound to the immutable image reference",
            )
        return {
            "mode": mode,
            "argv_index": argv_index,
            "image_reference": reference,
            "image_digest": implementation["container_image_digest"],
        }

    raise GateFailure(
        IDENTITY_FAILURE,
        "CONTROL",
        "adapter_entrypoint mode is absent or unknown",
    )


def _verify_runtime_versions(
    checks: list[dict[str, Any]],
    repository: Path,
    environment: dict[str, str],
) -> list[dict[str, Any]]:
    import subprocess

    verified: list[dict[str, Any]] = []
    for check in checks:
        argv = check["argv"]
        try:
            completed = subprocess.run(
                argv,
                cwd=repository,
                env=environment,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=10,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise GateFailure(
                IDENTITY_FAILURE,
                "RUNTIME_BASELINE",
                f"runtime-version command unavailable: {argv!r}: {exc}",
            ) from exc
        output_sha256 = hashlib.sha256(completed.stdout).hexdigest()
        if (
            completed.returncode != check["expected_exit_code"]
            or output_sha256 != check["expected_output_sha256"]
        ):
            raise GateFailure(
                IDENTITY_FAILURE,
                "RUNTIME_BASELINE",
                f"runtime-version identity mismatch: {argv!r}",
            )
        verified.append({
            "argv": argv,
            "exit_code": completed.returncode,
            "output_bytes": len(completed.stdout),
            "output_sha256": output_sha256,
            "output": completed.stdout.decode("utf-8", errors="replace").strip(),
        })
    return verified


def _verify_emilia_expectation(
    root: Path,
    envelope: dict[str, Any],
    external_sha256: str | None,
    root_manifest_members: set[str],
) -> dict[str, Any]:
    future = envelope["future_emilia_expectation"]
    source_relative = future["exact_source_path"]
    ingest_relative = future["ingest_record_path"]
    source = _safe_path(root, source_relative)
    ingest_path = _safe_path(root, ingest_relative)
    pending_marker = _safe_path(root, "expectations/emilia/PENDING")
    if external_sha256 is None or not re.fullmatch(r"[0-9a-f]{64}", external_sha256):
        raise GateFailure(EXPECTATION_MISSING, "EMILIA_EXPECTATION", "authenticated external EMILIA expectation SHA-256 was not supplied")
    if not source.is_file() or not ingest_path.is_file():
        raise GateFailure(EXPECTATION_MISSING, "EMILIA_EXPECTATION", "exact EMILIA expectation or ingest record is absent")
    if pending_marker.exists() or pending_marker.is_symlink():
        raise GateFailure(EXPECTATION_MISSING, "EMILIA_EXPECTATION", "EMILIA expectation PENDING marker was not retired")
    if source_relative not in root_manifest_members or ingest_relative not in root_manifest_members:
        raise GateFailure(IDENTITY_FAILURE, "EMILIA_EXPECTATION", "future expectation files are not pinned by the package manifest")
    ingest = _json_no_duplicates(ingest_path)
    if not isinstance(ingest, dict):
        raise GateFailure(IDENTITY_FAILURE, "EMILIA_EXPECTATION", "ingest record is not a JSON object")
    required_keys = {
        "schema_version",
        "freeze_state",
        "source_identity",
        "source_path",
        "source_sha256",
        "semantic_baseline",
        "fixtures",
        "commitment_identity",
        "committed_at_utc",
        "revealed_at_utc",
    }
    if set(ingest) != required_keys:
        raise GateFailure(
            IDENTITY_FAILURE,
            "EMILIA_EXPECTATION",
            "ingest record fields are incomplete or unknown",
        )
    required = {
        "schema_version": "wexp-emilia-expectation-ingest-1",
        "freeze_state": "FROZEN",
        "source_path": source_relative,
        "source_sha256": external_sha256,
        "semantic_baseline": EXPECTED_EMILIA_AUTHORITY,
        "fixtures": {
            "P": EXPECTED_P_SHA256,
            "P-1": EXPECTED_P1_SHA256,
        },
    }
    for key, expected in required.items():
        if ingest.get(key) != expected:
            raise GateFailure(IDENTITY_FAILURE, "EMILIA_EXPECTATION", f"invalid ingest field: {key}")
    actual = sha256_file(source)
    if actual != external_sha256:
        raise GateFailure(IDENTITY_FAILURE, "EMILIA_EXPECTATION", f"EMILIA expectation hash mismatch: {actual}")
    if not isinstance(ingest.get("source_identity"), str) or not ingest["source_identity"].strip():
        raise GateFailure(IDENTITY_FAILURE, "EMILIA_EXPECTATION", "source_identity is absent")
    if not isinstance(ingest.get("commitment_identity"), str) or not ingest["commitment_identity"].strip():
        raise GateFailure(IDENTITY_FAILURE, "EMILIA_EXPECTATION", "commitment_identity is absent")
    chronology: dict[str, datetime] = {}
    for field in ("committed_at_utc", "revealed_at_utc"):
        value = ingest.get(field)
        if not isinstance(value, str) or not value.strip():
            raise GateFailure(IDENTITY_FAILURE, "EMILIA_EXPECTATION", f"{field} is absent")
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise GateFailure(IDENTITY_FAILURE, "EMILIA_EXPECTATION", f"{field} is not ISO-8601") from exc
        if parsed.tzinfo is None or parsed.utcoffset() is None or parsed.utcoffset().total_seconds() != 0:
            raise GateFailure(IDENTITY_FAILURE, "EMILIA_EXPECTATION", f"{field} is not UTC")
        chronology[field] = parsed
    if chronology["committed_at_utc"] > chronology["revealed_at_utc"]:
        raise GateFailure(IDENTITY_FAILURE, "EMILIA_EXPECTATION", "commitment follows reveal")
    return {
        "state": "FROZEN",
        "source_identity": ingest["source_identity"],
        "commitment_identity": ingest["commitment_identity"],
        "committed_at_utc": ingest["committed_at_utc"],
        "revealed_at_utc": ingest["revealed_at_utc"],
        "path": source_relative,
        "sha256": actual,
        "semantic_baseline": EXPECTED_EMILIA_AUTHORITY,
    }


def _verify_control(root: Path, root_manifest_members: set[str], emilia_expectation_sha256: str) -> dict[str, Any]:
    relative = "execution/plan/EXECUTION-CONTROL.json"
    if relative not in root_manifest_members:
        raise GateFailure(IDENTITY_FAILURE, "CONTROL", "execution control is not pinned by package manifest")
    pending_markers = (
        "execution/raw/wexp/PENDING",
        "execution/raw/emilia/PENDING",
        "execution/normalized/PENDING",
    )
    active_markers = [
        marker
        for marker in pending_markers
        if (_safe_path(root, marker).exists() or _safe_path(root, marker).is_symlink())
    ]
    if active_markers:
        raise GateFailure(EXPECTATION_MISSING, "CONTROL", f"execution PENDING markers were not retired: {active_markers}")
    control = _json_no_duplicates(_require_file(root, relative))
    if not isinstance(control, dict):
        raise GateFailure(IDENTITY_FAILURE, "CONTROL", "execution control is not a JSON object")
    control_keys = {"schema_version", "state", "wexp", "emilia", "normalization"}
    if set(control) != control_keys:
        raise GateFailure(IDENTITY_FAILURE, "CONTROL", "execution-control fields are incomplete or unknown")
    if control.get("schema_version") != "wexp-emilia-execution-control-1":
        raise GateFailure(IDENTITY_FAILURE, "CONTROL", "execution-control schema_version mismatch")
    if control.get("state") != READY_CONTROL_STATE:
        raise GateFailure(EXPECTATION_MISSING, "CONTROL", "execution control remains PENDING")
    wexp = control.get("wexp", {})
    emilia = control.get("emilia", {})
    normalization = control.get("normalization", {})
    if not isinstance(wexp, dict) or not isinstance(emilia, dict) or not isinstance(normalization, dict):
        raise GateFailure(IDENTITY_FAILURE, "CONTROL", "execution-control planes must be JSON objects")
    wexp_keys = {
        "semantic_authority_commit",
        "route",
        "reason",
        "invoke_implementation",
        "execution_baseline",
    }
    emilia_keys = {"semantic_authority_commit", "route", "invoke_implementation", "implementation"}
    normalization_keys = {
        "state",
        "adapter_stdout_contract",
        "source_expectation_sha256",
        "projection_record",
        "expected_results",
    }
    if set(wexp) != wexp_keys or set(emilia) != emilia_keys or set(normalization) != normalization_keys:
        raise GateFailure(IDENTITY_FAILURE, "CONTROL", "execution-control plane fields are incomplete or unknown")
    if wexp.get("semantic_authority_commit") != EXPECTED_WEXP_AUTHORITY:
        raise GateFailure(IDENTITY_FAILURE, "BASELINE", "WEXP semantic-authority pin mismatch")
    if emilia.get("semantic_authority_commit") != EXPECTED_EMILIA_AUTHORITY:
        raise GateFailure(IDENTITY_FAILURE, "BASELINE", "EMILIA semantic-authority pin mismatch")
    if wexp.get("reason") != EXPECTED_WEXP_NONCONSTRUCTIBILITY_REASON:
        raise GateFailure(
            IDENTITY_FAILURE,
            "CONTROL",
            "WEXP nonconstructibility reason differs from the frozen scaffold boundary",
        )
    if wexp.get("execution_baseline") != EXPECTED_WEXP_EXECUTION_BASELINE:
        raise GateFailure(
            IDENTITY_FAILURE,
            "CONTROL",
            "WEXP execution_baseline differs from the frozen scaffold boundary",
        )
    if wexp.get("route") != "IMPLEMENTATION INPUT NOT CONSTRUCTIBLE" or wexp.get("invoke_implementation") is not False:
        raise GateFailure(IDENTITY_FAILURE, "CONTROL", "this frozen scaffold cannot invoke WEXP without the prohibited bridge")
    if emilia.get("route") != "INVOKE" or emilia.get("invoke_implementation") is not True:
        raise GateFailure(IDENTITY_FAILURE, "CONTROL", "EMILIA execution route is not explicitly ready")
    implementation = emilia.get("implementation")
    if not isinstance(implementation, dict):
        raise GateFailure(IDENTITY_FAILURE, "CONTROL", "EMILIA implementation descriptor is absent")
    implementation_keys = {
        "repository_path",
        "expected_head",
        "expected_tree",
        "require_clean",
        "command_argv",
        "expected_executable_sha256",
        "adapter_entrypoint",
        "timeout_seconds",
        "environment",
        "inherit_parent_environment",
        "runtime_version_checks",
        "container_runtime",
        "container_image_reference",
        "container_image_digest",
    }
    if set(implementation) != implementation_keys:
        raise GateFailure(IDENTITY_FAILURE, "CONTROL", "EMILIA implementation descriptor fields are incomplete or unknown")
    if not isinstance(implementation.get("repository_path"), str) or not implementation["repository_path"].strip():
        raise GateFailure(IDENTITY_FAILURE, "CONTROL", "EMILIA repository_path is absent")
    if not isinstance(implementation.get("expected_tree"), str) or not re.fullmatch(r"[0-9a-f]{40}", implementation["expected_tree"]):
        raise GateFailure(IDENTITY_FAILURE, "CONTROL", "EMILIA expected_tree is not an exact Git tree identity")
    argv = implementation.get("command_argv")
    if not isinstance(argv, list) or not argv or any(
        not isinstance(item, str) or not item or "\x00" in item for item in argv
    ):
        raise GateFailure(IDENTITY_FAILURE, "CONTROL", "EMILIA command_argv must be a non-empty string array")
    if not any("{fixture_path}" in item for item in argv):
        raise GateFailure(IDENTITY_FAILURE, "CONTROL", "EMILIA command_argv does not consume the identity-gated fixture path")
    if _command_uses_shell(argv):
        raise GateFailure(IDENTITY_FAILURE, "CONTROL", "shell and env wrappers are prohibited in EMILIA command_argv")
    for item in argv:
        residue = re.sub(r"\{(?:fixture_path|fixture_id)\}", "", item)
        if "{" in residue or "}" in residue:
            raise GateFailure(IDENTITY_FAILURE, "CONTROL", f"unsupported command token in argv: {item}")
    timeout = implementation.get("timeout_seconds")
    if type(timeout) is not int or not 1 <= timeout <= 3600:
        raise GateFailure(IDENTITY_FAILURE, "CONTROL", "EMILIA timeout_seconds is outside the reviewed range")
    environment = implementation.get("environment")
    if not isinstance(environment, dict) or any(
        not isinstance(key, str)
        or not key
        or "=" in key
        or "\x00" in key
        or not isinstance(value, str)
        or "\x00" in value
        for key, value in environment.items()
    ):
        raise GateFailure(IDENTITY_FAILURE, "CONTROL", "EMILIA adapter environment is not a string map")
    required_environment = {
        "PATH": None,
        "LANG": "C",
        "LC_ALL": "C",
        "TZ": "UTC",
        "PYTHONHASHSEED": "0",
    }
    for key, expected in required_environment.items():
        value = environment.get(key)
        if not isinstance(value, str) or not value or (expected is not None and value != expected):
            raise GateFailure(IDENTITY_FAILURE, "CONTROL", f"invalid deterministic environment field: {key}")
    if implementation.get("inherit_parent_environment") is not False:
        raise GateFailure(IDENTITY_FAILURE, "CONTROL", "parent environment inheritance is not disabled")
    version_checks = implementation.get("runtime_version_checks")
    if (
        not isinstance(version_checks, list)
        or not version_checks
        or any(
            not isinstance(check, dict)
            or set(check) != {"argv", "expected_exit_code", "expected_output_sha256"}
            or not isinstance(check.get("argv"), list)
            or not check["argv"]
            or any(
                not isinstance(item, str)
                or not item
                or "{" in item
                or "}" in item
                or "\x00" in item
                for item in check["argv"]
            )
            or type(check.get("expected_exit_code")) is not int
            or check["expected_exit_code"] != 0
            or not isinstance(check.get("expected_output_sha256"), str)
            or not re.fullmatch(r"[0-9a-f]{64}", check["expected_output_sha256"])
            for check in version_checks
        )
    ):
        raise GateFailure(IDENTITY_FAILURE, "CONTROL", "runtime_version_checks are incomplete or unsafe")
    if any(_command_uses_shell(check["argv"]) for check in version_checks):
        raise GateFailure(IDENTITY_FAILURE, "CONTROL", "shell and env wrappers are prohibited in runtime_version_checks")
    container_runtime = implementation.get("container_runtime")
    container_reference = implementation.get("container_image_reference")
    container_digest = implementation.get("container_image_digest")
    if container_runtime not in {"NONE", "DOCKER", "PODMAN", "OTHER"}:
        raise GateFailure(IDENTITY_FAILURE, "CONTROL", "container_runtime declaration is absent or unknown")
    if container_runtime == "NONE":
        if container_digest is not None or container_reference is not None:
            raise GateFailure(
                IDENTITY_FAILURE,
                "CONTROL",
                "container image reference/digest must be null when no container is used",
            )
    elif (
        not isinstance(container_digest, str)
        or not re.fullmatch(r"sha256:[0-9a-f]{64}", container_digest)
        or not isinstance(container_reference, str)
        or not re.fullmatch(r"[^\s@]+@sha256:[0-9a-f]{64}", container_reference)
        or not container_reference.endswith("@" + container_digest)
    ):
        raise GateFailure(
            IDENTITY_FAILURE,
            "CONTROL",
            "container image reference/digest is absent, inconsistent, or not immutable",
        )
    baseline = _verify_git_baseline(implementation, required_head=EXPECTED_EMILIA_AUTHORITY)
    adapter_executable = _resolve_executable(
        argv[0], Path(baseline["repository_path"]), environment
    )
    executable_name = Path(adapter_executable["path"]).name.lower()
    if container_runtime == "DOCKER" and executable_name not in {"docker", "docker.exe"}:
        raise GateFailure(IDENTITY_FAILURE, "CONTROL", "DOCKER declaration does not use the Docker executable directly")
    if container_runtime == "PODMAN" and executable_name not in {"podman", "podman.exe"}:
        raise GateFailure(IDENTITY_FAILURE, "CONTROL", "PODMAN declaration does not use the Podman executable directly")
    if container_runtime != "NONE" and container_reference not in argv:
        raise GateFailure(
            IDENTITY_FAILURE,
            "CONTROL",
            "container command does not include the reviewed immutable image reference",
        )
    if container_runtime == "NONE" and executable_name in {"docker", "docker.exe", "podman", "podman.exe"}:
        raise GateFailure(IDENTITY_FAILURE, "CONTROL", "container executable conflicts with NONE declaration")
    expected_executable_sha256 = implementation.get("expected_executable_sha256")
    if (
        not isinstance(expected_executable_sha256, str)
        or not re.fullmatch(r"[0-9a-f]{64}", expected_executable_sha256)
        or adapter_executable["sha256"] != expected_executable_sha256
    ):
        raise GateFailure(IDENTITY_FAILURE, "CONTROL", "adapter executable identity mismatch")
    adapter_entrypoint = _verify_adapter_entrypoint(
        implementation,
        Path(baseline["repository_path"]),
        adapter_executable,
    )
    runtime_versions = _verify_runtime_versions(
        version_checks, Path(baseline["repository_path"]), environment
    )
    post_runtime_baseline = _verify_git_baseline(
        implementation,
        required_head=EXPECTED_EMILIA_AUTHORITY,
    )
    post_runtime_executable = _resolve_executable(
        argv[0],
        Path(post_runtime_baseline["repository_path"]),
        environment,
    )
    post_runtime_entrypoint = _verify_adapter_entrypoint(
        implementation,
        Path(post_runtime_baseline["repository_path"]),
        post_runtime_executable,
    )
    if (
        post_runtime_baseline != baseline
        or post_runtime_executable != adapter_executable
        or post_runtime_entrypoint != adapter_entrypoint
    ):
        raise GateFailure(
            IDENTITY_FAILURE,
            "RUNTIME_BASELINE",
            "runtime-version checks changed a reviewed implementation identity",
        )
    if normalization.get("state") != "FROZEN BEFORE EXECUTION":
        raise GateFailure(EXPECTATION_MISSING, "CONTROL", "result normalization was not frozen before execution")
    if normalization.get("adapter_stdout_contract") != "wexp-emilia-observed-result-1":
        raise GateFailure(IDENTITY_FAILURE, "CONTROL", "unknown adapter output contract")
    if normalization.get("source_expectation_sha256") != emilia_expectation_sha256:
        raise GateFailure(IDENTITY_FAILURE, "CONTROL", "normalized expectations are not bound to Iman's exact frozen source hash")
    if not isinstance(normalization.get("projection_record"), str) or not normalization["projection_record"].strip():
        raise GateFailure(EXPECTATION_MISSING, "CONTROL", "reviewable expectation projection record is absent")
    expected_results = normalization.get("expected_results")
    if not isinstance(expected_results, dict) or set(expected_results) != {"P", "P-1"}:
        raise GateFailure(EXPECTATION_MISSING, "CONTROL", "both normalized EMILIA expectations are required")
    control_path = _require_file(root, relative)
    return {
        "state": READY_CONTROL_STATE,
        "wexp_route": wexp["route"],
        "emilia_baseline": baseline,
        "adapter_executable": adapter_executable,
        "adapter_entrypoint": adapter_entrypoint,
        "runtime_versions": runtime_versions,
        "control_sha256": sha256_file(control_path),
        "validated_control": control,
    }


def verify_package(
    package_root: Path,
    *,
    package_manifest_sha256: str | None = None,
    emilia_expectation_sha256: str | None = None,
    require_future: bool = True,
) -> dict[str, Any]:
    root = package_root.resolve(strict=True)
    report: dict[str, Any] = {"schema_version": "wexp-emilia-verification-report-1", "package_root": str(root), "gates": []}

    # Gate 1: the package manifest and every path it pins.  No fixture parsing,
    # environment capture, output creation, or implementation call precedes it.
    manifest = _require_file(root, "MANIFEST.sha256")
    manifest_sha = sha256_file(manifest)
    if package_manifest_sha256 is not None and manifest_sha != package_manifest_sha256:
        raise GateFailure(IDENTITY_FAILURE, "PACKAGE_MANIFEST", f"package manifest pin mismatch: {manifest_sha}")
    manifest_report = _verify_manifest(manifest, root)
    manifest_members = {member["path"] for member in manifest_report["members"]}
    coverage_report = _verify_root_manifest_coverage(root, manifest_members)
    critical_members = {
        "execution/plan/EXECUTION-ENVELOPE.json",
        "execution/plan/EXECUTION-CONTROL.json",
        "source/original/WEXP-EMILIA-INTEROP-001/fixtures.yaml",
        "records/WEXP-EMILIA-EP-COMPARISON-001.md",
        "source/original/WEXP-EMILIA-INTEROP-001/wexp-reading.yaml",
        "source/original/emilia-reading.json",
        "source/pair-freeze/MANIFEST.sha256",
        "source/pair-freeze/PAIR-MANIFEST.sha256",
        "source/pair-freeze/fixtures/WE-EP-P.json",
        "source/pair-freeze/fixtures/WE-EP-P-1.json",
        "expectations/wexp/wexp-expectation.yaml",
    }
    missing_pins = sorted(critical_members - manifest_members)
    if missing_pins:
        raise GateFailure(IDENTITY_FAILURE, "PACKAGE_MANIFEST", f"critical members not pinned: {missing_pins}")
    report["gates"].append({
        "gate": "PACKAGE_MANIFEST",
        "status": "PASS",
        "sha256": manifest_sha,
        **manifest_report,
        **coverage_report,
    })

    envelope_path = _require_file(root, "execution/plan/EXECUTION-ENVELOPE.json")
    _require_identity(envelope_path, EXPECTED_ENVELOPE_SHA256, gate="EXECUTION_ENVELOPE")
    envelope = _json_no_duplicates(envelope_path)
    frozen = envelope["frozen_inputs"]
    unpacked = _safe_path(root, frozen["pair_freeze_directory"])

    source_identities: dict[str, Any] = {}
    frozen_source_hashes = {
        "original_common_fixtures": EXPECTED_ORIGINAL_FIXTURES_SHA256,
        "five_case_comparison": EXPECTED_COMPARISON_SHA256,
        "frozen_wexp_reading": EXPECTED_WEXP_READING_SHA256,
        "frozen_emilia_reading": EXPECTED_EMILIA_READING_SHA256,
    }
    for name, immutable_sha256 in frozen_source_hashes.items():
        specification = frozen[name]
        if specification.get("sha256") != immutable_sha256:
            raise GateFailure(IDENTITY_FAILURE, "SOURCE_IDENTITIES", f"envelope repins frozen input: {name}")
        source_path = _require_file(root, specification["path"])
        source_identities[name] = _require_identity(source_path, immutable_sha256, gate="SOURCE_IDENTITIES")
    report["gates"].append({"gate": "SOURCE_IDENTITIES", "status": "PASS", "inputs": source_identities})

    archive_spec = frozen["pair_archive"]
    if archive_spec.get("sha256") != EXPECTED_PAIR_ARCHIVE_SHA256 or archive_spec.get("bytes") != EXPECTED_PAIR_ARCHIVE_BYTES:
        raise GateFailure(IDENTITY_FAILURE, "PAIR_ARCHIVE", "envelope repins the frozen pair archive")
    archive = _require_file(root, archive_spec["source_path"])
    archive_identity = _require_identity(
        archive,
        EXPECTED_PAIR_ARCHIVE_SHA256,
        expected_bytes=EXPECTED_PAIR_ARCHIVE_BYTES,
        gate="PAIR_ARCHIVE",
    )
    archive_report = _verify_pair_archive(archive, unpacked)
    report["gates"].append({"gate": "PAIR_ARCHIVE", "status": "PASS", **archive_identity, **archive_report})

    full_manifest_spec = frozen["pair_freeze_manifest"]
    if full_manifest_spec.get("sha256") != EXPECTED_PAIR_FULL_MANIFEST_SHA256:
        raise GateFailure(IDENTITY_FAILURE, "PAIR_FREEZE_MANIFEST", "envelope repins the full pair manifest")
    full_manifest = _require_file(root, full_manifest_spec["path"])
    _require_identity(full_manifest, EXPECTED_PAIR_FULL_MANIFEST_SHA256, gate="PAIR_FREEZE_MANIFEST")
    full_report = _verify_manifest(full_manifest, unpacked)
    pair_manifest_spec = frozen["pair_manifest"]
    if pair_manifest_spec.get("sha256") != EXPECTED_PAIR_MANIFEST_SHA256:
        raise GateFailure(IDENTITY_FAILURE, "PAIR_MANIFEST", "envelope repins the pair manifest")
    pair_manifest = _require_file(root, pair_manifest_spec["path"])
    _require_identity(pair_manifest, EXPECTED_PAIR_MANIFEST_SHA256, gate="PAIR_MANIFEST")
    pair_report = _verify_manifest(pair_manifest, unpacked)
    report["gates"].append({"gate": "PAIR_MANIFESTS", "status": "PASS", "full": full_report, "pair": pair_report})

    p_spec = frozen["p"]
    p1_spec = frozen["p_minus_1"]
    if p_spec.get("sha256") != EXPECTED_P_SHA256 or p_spec.get("bytes") != EXPECTED_P_BYTES:
        raise GateFailure(IDENTITY_FAILURE, "P", "envelope repins frozen P")
    if p1_spec.get("sha256") != EXPECTED_P1_SHA256 or p1_spec.get("bytes") != EXPECTED_P1_BYTES:
        raise GateFailure(IDENTITY_FAILURE, "P-1", "envelope repins frozen P-1")
    p_path = _require_file(root, p_spec["path"])
    p1_path = _require_file(root, p1_spec["path"])
    p_identity = _require_identity(p_path, EXPECTED_P_SHA256, expected_bytes=EXPECTED_P_BYTES, gate="P")
    p1_identity = _require_identity(p1_path, EXPECTED_P1_SHA256, expected_bytes=EXPECTED_P1_BYTES, gate="P-1")
    delta = _verify_pair_delta(p_path, p1_path)
    report["gates"].append({"gate": "P_AND_P-1", "status": "PASS", "P": p_identity, "P-1": p1_identity, "delta": delta})

    wexp_spec = frozen["wexp_expectation"]
    if wexp_spec.get("sha256") != EXPECTED_WEXP_EXPECTATION_SHA256:
        raise GateFailure(IDENTITY_FAILURE, "WEXP_EXPECTATION", "envelope repins the WEXP expectation")
    wexp = _require_file(root, wexp_spec["path"])
    wexp_identity = _require_identity(wexp, EXPECTED_WEXP_EXPECTATION_SHA256, gate="WEXP_EXPECTATION")
    report["gates"].append({"gate": "WEXP_EXPECTATION", "status": "PASS", **wexp_identity})

    if require_future:
        emilia = _verify_emilia_expectation(root, envelope, emilia_expectation_sha256, manifest_members)
        report["gates"].append({"gate": "EMILIA_EXPECTATION", "status": "PASS", **emilia})
        # Control verification may execute reviewed, read-only baseline and
        # runtime-version probes. Authenticate the package snapshot externally
        # before any such package-derived command can be considered. Keeping
        # this immediately after the expectation gate preserves the deliberate
        # missing-expectation refusal without permitting an unpinned control.
        if (
            not isinstance(package_manifest_sha256, str)
            or not re.fullmatch(r"[0-9a-f]{64}", package_manifest_sha256)
        ):
            raise GateFailure(
                IDENTITY_FAILURE,
                "PACKAGE_MANIFEST",
                "an externally authenticated package-manifest SHA-256 is required before future expectation/control verification",
            )
        assert emilia_expectation_sha256 is not None
        control = _verify_control(root, manifest_members, emilia_expectation_sha256)
        report["gates"].append({"gate": "BASELINES_AND_CONTROL", "status": "PASS", **control})
        if sha256_file(manifest) != manifest_sha:
            raise GateFailure(
                IDENTITY_FAILURE,
                "POST_CONTROL_IDENTITY",
                "package manifest changed during control/runtime verification",
            )
        post_control_manifest = _verify_manifest(manifest, root)
        post_control_members = {
            member["path"] for member in post_control_manifest["members"]
        }
        post_control_coverage = _verify_root_manifest_coverage(
            root,
            post_control_members,
        )
        report["gates"].append({
            "gate": "POST_CONTROL_IDENTITY",
            "status": "PASS",
            **post_control_manifest,
            **post_control_coverage,
        })
    else:
        report["gates"].append({"gate": "FUTURE_INPUTS", "status": "NOT_REQUESTED"})

    report["status"] = "PASS"
    return report


def _self_test() -> dict[str, Any]:
    tests: list[dict[str, str]] = []
    with tempfile.TemporaryDirectory(prefix="wexp-emilia-harness-selftest-") as temp_name:
        root = Path(temp_name)
        payload = root / "dummy.txt"
        payload.write_bytes(b"dummy-not-P-or-P-1\n")
        expected = hashlib.sha256(payload.read_bytes()).hexdigest()
        _require_identity(payload, expected)
        tests.append({"name": "dummy hash accepted", "status": "PASS"})

        payload.write_bytes(b"mutated-dummy\n")
        try:
            _require_identity(payload, expected)
        except GateFailure as exc:
            if exc.result_class != IDENTITY_FAILURE:
                raise
            tests.append({"name": "dummy mismatch fails closed", "status": "PASS"})
        else:
            raise RuntimeError("dummy mismatch did not fail closed")

        unsafe_manifest = root / "unsafe.sha256"
        unsafe_manifest.write_text(f"{expected}  ../escape\n", encoding="utf-8")
        try:
            _verify_manifest(unsafe_manifest, root)
        except GateFailure:
            tests.append({"name": "unsafe manifest path rejected", "status": "PASS"})
        else:
            raise RuntimeError("unsafe manifest path was accepted")

        coverage_root = root / "coverage"
        coverage_root.mkdir()
        (coverage_root / "tracked.txt").write_bytes(b"tracked-dummy\n")
        _verify_root_manifest_coverage(coverage_root, {"tracked.txt"})
        (coverage_root / "unmanifested.txt").write_bytes(b"unmanifested-dummy\n")
        try:
            _verify_root_manifest_coverage(coverage_root, {"tracked.txt"})
        except GateFailure:
            tests.append({"name": "unmanifested dummy file rejected", "status": "PASS"})
        else:
            raise RuntimeError("unmanifested dummy file was accepted")

        envelope = {
            "future_emilia_expectation": {
                "exact_source_path": "expectations/emilia/emilia-expectation.json",
                "ingest_record_path": "expectations/emilia/EXPECTATION-INGEST.json",
            }
        }
        try:
            _verify_emilia_expectation(root, envelope, None, set())
        except GateFailure as exc:
            if exc.result_class != EXPECTATION_MISSING:
                raise
            tests.append({"name": "missing EMILIA expectation refused", "status": "PASS"})
        else:
            raise RuntimeError("missing expectation was accepted")
    return {"schema_version": "wexp-emilia-harness-self-test-1", "status": "PASS", "semantic_inputs_used": False, "tests": tests}


def _default_root() -> Path:
    return Path(__file__).resolve().parents[1]


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-root", type=Path, default=_default_root())
    parser.add_argument("--package-manifest-sha256")
    parser.add_argument("--emilia-expectation-sha256")
    parser.add_argument("--static-only", action="store_true", help="verify only already-frozen static inputs; never sufficient to execute")
    parser.add_argument("--self-test", action="store_true", help="exercise fail-closed primitives using dummy files only")
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        if args.self_test:
            report = _self_test()
        else:
            report = verify_package(
                args.package_root,
                package_manifest_sha256=args.package_manifest_sha256,
                emilia_expectation_sha256=args.emilia_expectation_sha256,
                require_future=not args.static_only,
            )
    except GateFailure as exc:
        _emit_json({
            "schema_version": "wexp-emilia-verification-report-1",
            "status": "REFUSED",
            "result_class": exc.result_class,
            "gate": exc.gate,
            "detail": exc.detail,
            "implementation_execution_started": False,
        })
        return 20 if exc.result_class == EXPECTATION_MISSING else 21
    except Exception as exc:  # keep unexpected preflight defects fail-closed
        _emit_json({
            "schema_version": "wexp-emilia-verification-report-1",
            "status": "REFUSED",
            "result_class": IDENTITY_FAILURE,
            "gate": "HARNESS",
            "detail": f"unexpected verifier failure: {type(exc).__name__}: {exc}",
            "implementation_execution_started": False,
        })
        return 22
    _emit_json(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
