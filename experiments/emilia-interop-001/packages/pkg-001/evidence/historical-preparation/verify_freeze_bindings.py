#!/usr/bin/env python3
"""Reproduce EMILIA FREEZE-002's eleven recorded byte/binding checks.

This checks a YAML inventory against exact local files and an independently
selected, pinned metadata copy. It does not verify a signature, timestamp,
authorship, historical declaration, payload inventory, or implementation run.
The CLI accepts explicit paths and refuses to overwrite an existing report.
Requires exactly PyYAML 6.0.3; see requirements-freeze-verifier.txt.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import importlib.metadata
import io
import json
from pathlib import Path, PurePosixPath
import platform
import re
import stat
import sys
import zipfile


VERSION = "0.1.0"
YAML_VERSION = "6.0.3"
CHECK_IDS = (
    "freeze_bytes_match_preexisting_metadata",
    "freeze_sha256_match_preexisting_metadata",
    "archive_name_matches_metadata",
    "archive_size_binding_matches_bytes",
    "archive_sha256_binding_matches_bytes",
    "archive_sha256_binding_matches_preexisting_metadata",
    "manifest_size_binding_matches_bytes",
    "manifest_sha256_binding_matches_bytes",
    "manifest_sha256_binding_matches_preexisting_metadata",
    "manifest_nonempty_entry_count_matches_declared",
    "corrected_manifest_pin_matches_binding",
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def exact_map(value: object, label: str) -> dict:
    require(type(value) is dict, f"{label} must be a mapping")
    return value


def string_field(mapping: dict, key: str) -> str:
    value = mapping.get(key)
    require(type(value) is str and bool(value), f"{key} must be a nonempty string")
    return value


def integer_field(mapping: dict, key: str) -> int:
    value = mapping.get(key)
    require(type(value) is int and value >= 0, f"{key} must be a nonnegative integer, not a boolean")
    return value


def digest_field(mapping: dict, key: str) -> str:
    value = string_field(mapping, key)
    require(re.fullmatch(r"[0-9a-f]{64}", value) is not None, f"{key} must be a lowercase SHA-256")
    return value


def basename(value: str, label: str) -> str:
    require(PurePosixPath(value).name == value and value not in {".", ".."}
            and not any(c in value for c in "\\\x00\r\n:"), f"{label} must be a plain filename")
    return value


def load_strict_yaml(data: bytes, label: str, yaml) -> dict:
    """Use SafeLoader; additionally reject duplicate/non-string keys and aliases.

    These documents need no YAML anchors, aliases, merge keys, or multiple
    documents. Rejecting them avoids ambiguous or substituted identity fields.
    This is a bounded input policy, not a general YAML conformance validator.
    """
    for token in yaml.scan(data.decode("utf-8"), Loader=yaml.SafeLoader):
        require(not isinstance(token, (yaml.tokens.AnchorToken, yaml.tokens.AliasToken)),
                f"{label}: YAML anchors and aliases are outside the supported profile")

    class UniqueSafeLoader(yaml.SafeLoader):
        def construct_mapping(self, node, deep=False):
            require(isinstance(node, yaml.nodes.MappingNode), f"{label}: expected a mapping node")
            mapping = {}
            for key_node, value_node in node.value:
                require(key_node.tag != "tag:yaml.org,2002:merge", f"{label}: YAML merge keys are forbidden")
                key = self.construct_object(key_node, deep=deep)
                require(type(key) is str, f"{label}: mapping keys must be strings")
                require(key not in mapping, f"{label}: duplicate mapping key {key!r}")
                mapping[key] = self.construct_object(value_node, deep=deep)
            return mapping

    return exact_map(yaml.load(data.decode("utf-8"), Loader=UniqueSafeLoader), label)


def read_input(path: Path, maximum_bytes: int) -> tuple[bytes, dict]:
    require(path.is_file(), f"input is not a regular file: {path}")
    require(path.stat().st_size <= maximum_bytes, f"input exceeds bounded profile size: {path}")
    data = path.read_bytes()
    require(len(data) <= maximum_bytes, f"input grew beyond bounded profile size: {path}")
    return data, {"path": str(path.resolve()), "bytes": len(data), "sha256": sha256(data)}


def verify(args, report: dict) -> None:
    installed_yaml_version = importlib.metadata.version("PyYAML")
    report["runtime"]["PyYAML"] = installed_yaml_version
    require(installed_yaml_version == YAML_VERSION,
            f"requires PyYAML=={YAML_VERSION}; found {installed_yaml_version}")
    import yaml

    archive_bytes, archive_identity = read_input(args.archive, 10 * 1024 * 1024)
    freeze_bytes, freeze_identity = read_input(args.freeze, 64 * 1024)
    metadata_bytes, metadata_identity = read_input(args.metadata, 256 * 1024)
    metadata_identity.update({
        "git_blob_sha1": git_blob_sha1(metadata_bytes),
        "expected_sha256": args.metadata_sha256,
        "expected_git_blob_sha1": args.metadata_git_blob,
        "historical_source_url": args.metadata_source_url,
    })
    report["inputs"] = {"archive": archive_identity, "freeze": freeze_identity,
                        "metadata": metadata_identity}
    require(metadata_identity["sha256"] == args.metadata_sha256, "metadata SHA-256 pin mismatch")
    require(metadata_identity["git_blob_sha1"] == args.metadata_git_blob, "metadata Git blob pin mismatch")
    freeze = load_strict_yaml(freeze_bytes, "freeze", yaml)
    metadata = load_strict_yaml(metadata_bytes, "metadata", yaml)
    release = exact_map(metadata.get("release_identity"), "metadata.release_identity")
    correction = exact_map(freeze.get("correction"), "freeze.correction")
    require(freeze.get("schema_version") == "wexp-emilia-publication-candidate-freeze-2",
            "unsupported freeze schema_version")
    require(freeze.get("record_id") == "WEXP-EMILIA-INTEROP-001-PUBLICATION-CANDIDATE-FREEZE-002",
            "unsupported freeze record_id")
    require(freeze.get("artifact_id") == metadata.get("artifact_id") == "WEXP-EMILIA-INTEROP-001",
            "artifact_id mismatch or unsupported artifact")
    require(correction.get("field") == "root_manifest_sha256", "unexpected correction.field")

    archive_name = basename(string_field(release, "archive_filename"), "archive_filename")
    candidate_name = basename(string_field(freeze, "candidate_archive"), "candidate_archive")
    freeze_name = basename(string_field(release, "detached_record"), "detached_record")
    require(args.freeze.name == freeze_name, "supplied freeze filename differs from metadata.detached_record")
    manifest_name = basename(string_field(freeze, "root_manifest_filename"), "root_manifest_filename")
    require(archive_name.endswith(".zip"), "metadata archive_filename must end with .zip")
    expected_member = archive_name[:-4] + "/" + manifest_name
    require(args.manifest_member == expected_member,
            "explicit manifest member must select the declared root manifest, not a nested copy")

    # Validate scalar types before comparisons; Python otherwise equates True and 1.
    for key in ("archive_bytes", "root_manifest_bytes", "payload_entries_verified"):
        integer_field(freeze, key)
    for key in ("detached_record_bytes", "archive_bytes", "manifest_bytes", "manifest_payload_entries"):
        integer_field(release, key)
    for key in ("archive_sha256", "root_manifest_sha256"):
        digest_field(freeze, key)
    for key in ("detached_record_sha256", "archive_sha256", "manifest_sha256"):
        digest_field(release, key)
    digest_field(correction, "corrected_root_manifest_sha256")

    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        members = [member for member in archive.infolist() if member.orig_filename == args.manifest_member]
        require(len(members) == 1, "declared root manifest must occur exactly once in ZIP")
        member = members[0]
        require(member.filename == member.orig_filename and not member.is_dir(), "manifest is not an unambiguous file")
        require(member.create_system == 3 and stat.S_IFMT(member.external_attr >> 16) == stat.S_IFREG,
                "manifest must carry Unix regular-file type")
        require(not member.flag_bits & 1, "encrypted manifest is unsupported")
        require(member.file_size <= 1024 * 1024, "manifest exceeds bounded profile size")
        manifest_bytes = archive.read(member)  # Includes zipfile's CRC check for this member only.

    nonempty_lines = [line for line in manifest_bytes.decode("utf-8").splitlines() if line.strip()]
    manifest_paths = []
    for line in nonempty_lines:
        match = re.fullmatch(r"([0-9a-f]{64})  ([^\r\n\x00]+)", line)
        require(match is not None, "malformed root-manifest record")
        path = match.group(2)
        require(not path.startswith("/") and "\\" not in path
                and all(part not in {"", ".", ".."} for part in path.split("/")),
                "noncanonical relative path in root manifest")
        manifest_paths.append(path)
    require(len(manifest_paths) == len(set(manifest_paths)), "duplicate root-manifest paths")
    report["manifest_observation"] = {
        "member": args.manifest_member, "bytes": len(manifest_bytes),
        "sha256": sha256(manifest_bytes), "nonempty_entries": len(nonempty_lines),
        "syntax_and_unique_paths_checked": True, "listed_payload_hashes_verified": False,
    }

    report["checks"] = {
        "freeze_bytes_match_preexisting_metadata": len(freeze_bytes) == release["detached_record_bytes"],
        "freeze_sha256_match_preexisting_metadata": sha256(freeze_bytes) == release["detached_record_sha256"],
        "archive_name_matches_metadata": candidate_name == archive_name == args.archive.name,
        "archive_size_binding_matches_bytes": freeze["archive_bytes"] == len(archive_bytes),
        "archive_sha256_binding_matches_bytes": freeze["archive_sha256"] == sha256(archive_bytes),
        "archive_sha256_binding_matches_preexisting_metadata": freeze["archive_sha256"] == release["archive_sha256"],
        "manifest_size_binding_matches_bytes": freeze["root_manifest_bytes"] == len(manifest_bytes),
        "manifest_sha256_binding_matches_bytes": freeze["root_manifest_sha256"] == sha256(manifest_bytes),
        "manifest_sha256_binding_matches_preexisting_metadata": freeze["root_manifest_sha256"] == release["manifest_sha256"],
        "manifest_nonempty_entry_count_matches_declared": len(nonempty_lines) == freeze["payload_entries_verified"],
        "corrected_manifest_pin_matches_binding": correction["corrected_root_manifest_sha256"] == freeze["root_manifest_sha256"],
    }
    # These are extra consistency conditions, kept separate from the historical 11.
    report["additional_checks"] = {
        "archive_size_matches_preexisting_metadata": len(archive_bytes) == release["archive_bytes"],
        "manifest_size_matches_preexisting_metadata": len(manifest_bytes) == release["manifest_bytes"],
        "manifest_entry_count_matches_preexisting_metadata": len(nonempty_lines) == release["manifest_payload_entries"],
    }
    report["all_byte_and_binding_checks_passed"] = all(report["checks"].values())
    report["status"] = "PASS" if (report["all_byte_and_binding_checks_passed"]
                                  and all(report["additional_checks"].values())) else "FAIL"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--freeze", type=Path, required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--metadata-sha256", required=True)
    parser.add_argument("--metadata-git-blob", required=True)
    parser.add_argument("--metadata-source-url", required=True,
                        help="Recorded provenance only; this program performs no network access")
    parser.add_argument("--manifest-member", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    require(re.fullmatch(r"[0-9a-f]{64}", args.metadata_sha256) is not None, "invalid metadata SHA-256 argument")
    require(re.fullmatch(r"[0-9a-f]{40}", args.metadata_git_blob) is not None, "invalid metadata Git blob argument")
    if args.out.exists():
        parser.error("refusing to overwrite an existing report; select a new --out path")
    require(args.out.resolve() not in {args.archive.resolve(), args.freeze.resolve(), args.metadata.resolve(),
                                      Path(__file__).resolve()}, "output must not replace an input or script")
    report = {
        "schema": "emilia-freeze-bindings-verification-001", "verifier_version": VERSION,
        "started_at_utc": utc_now(), "status": "ERROR",
        "runtime": {"python": sys.version, "platform": platform.platform()},
        "command": [sys.executable, *sys.argv], "working_directory": str(Path.cwd()),
        "script_sha256": sha256(Path(__file__).read_bytes()),
        "checks": {key: None for key in CHECK_IDS}, "additional_checks": {},
        "all_byte_and_binding_checks_passed": False,
        "record_classification": "Unsigned YAML inventory and transcription-correction record.",
        "limits": [
            "Caller-supplied metadata pins select the comparison source; their historical provenance is not established by this script.",
            "The cited metadata source is postpublication. Matching observed bytes does not prove continuous non-modification or a publication-time commitment.",
            "No signature, trusted timestamp, authorship, human review, or Git tag is verified.",
            "No historical PASS, provenance, supersedes history, or unaffected-semantics declaration is revalidated.",
            "Only the root manifest member is read from the ZIP; payload hashes, extraction safety, modes, and fresh-clone behavior require separate checks.",
            "No WEXP or EMILIA implementation is executed. PASS establishes only the listed input and byte/binding conditions.",
        ],
        "wexp_or_emilia_implementation_executed": False,
    }
    try:
        verify(args, report)
    except Exception as error:
        report["status"] = "ERROR"
        report["error"] = {"type": type(error).__name__, "message": str(error)}
    report["finished_at_utc"] = utc_now()
    report["failed_checks"] = [key for key, passed in report["checks"].items() if passed is False]
    report["failed_additional_checks"] = [key for key, passed in report["additional_checks"].items() if passed is False]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x", encoding="utf-8", newline="\n") as output:
        output.write(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"report": str(args.out.resolve()), "status": report["status"],
                      "passed_checks": sum(value is True for value in report["checks"].values()),
                      "total_checks": len(CHECK_IDS), "failed_checks": report["failed_checks"],
                      "failed_additional_checks": report["failed_additional_checks"],
                      "error": report.get("error")}, ensure_ascii=False))
    return 0 if report["status"] == "PASS" else 1 if report["status"] == "FAIL" else 2


if __name__ == "__main__":
    raise SystemExit(main())
