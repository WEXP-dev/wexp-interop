#!/usr/bin/env python3
"""Inspect a publication ZIP without extracting or modifying its members.

This bounded migration audit records names, file bytes and metadata separately.
It does not certify archive provenance, all-filesystem portability, or Git
preservation of permissions and other ZIP metadata.
"""

from __future__ import annotations

import argparse
import collections
import datetime
import hashlib
import io
import json
from pathlib import Path, PureWindowsPath
import platform
import stat
import struct
import sys
import unicodedata
import zipfile


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_casefold(value: str) -> str:
    return unicodedata.normalize("NFD", unicodedata.normalize("NFD", value).casefold())


def central_names(data: bytes, start: int, count: int) -> list[bytes]:
    """Read name bytes from each central-directory entry, in original order."""
    names = []
    offset = start
    for _ in range(count):
        values = struct.unpack_from("<4s6H3I5H2I", data, offset)
        if values[0] != b"PK\x01\x02":
            raise ValueError("unexpected ZIP central-directory signature")
        name_length, extra_length, comment_length = values[10:13]
        end = offset + 46 + name_length
        if end + extra_length + comment_length > len(data):
            raise ValueError("truncated ZIP central-directory entry")
        names.append(data[offset + 46:end])
        offset = end + extra_length + comment_length
    return names


def inspect(path: Path, source_url: str | None, expected_hash: str | None) -> dict:
    data = path.read_bytes()
    errors = []
    members = []
    expected_matches = sha256(data) == expected_hash if expected_hash else None
    if expected_matches is False:
        errors.append({"kind": "archive-sha256-mismatch"})
    report = {
        "schema": "emilia-archive-inspection-001",
        "observed_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "archive": {
            "local_path": str(path.resolve()), "source_url": source_url,
            "bytes": len(data), "sha256": sha256(data),
            "md5": hashlib.md5(data).hexdigest(),
            "expected_sha256": expected_hash, "expected_sha256_matches": expected_matches,
            "hash_provenance": "Expected hash is a caller-supplied pin; its historical source must be established in the separate acquisition record.",
        },
        "runtime": {"python": sys.version, "platform": platform.platform(),
                    "unicode_database": unicodedata.unidata_version,
                    "audit_script_sha256": sha256(Path(__file__).read_bytes())},
        "scope": "Central-directory members and uncompressed member bytes of this exact ZIP; no extraction, Git import, or execution by this script.",
    }
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        infos = archive.infolist()
        raw_names = central_names(data, archive.start_dir, len(infos))
        files = set()
        explicit_dirs = set()
        all_dirs = set()
        exact_seen = collections.defaultdict(list)
        for index, (info, raw_name) in enumerate(zip(infos, raw_names)):
            name = info.orig_filename
            encoding = "utf-8" if info.flag_bits & 0x800 else "cp437"
            decoded_name = raw_name.decode(encoding)
            if decoded_name != name or info.filename != name:
                errors.append({"kind": "filename-decoding-or-truncation", "index": index})
            parts = name.rstrip("/").split("/")
            unsafe = (name.startswith(("/", "\\")) or bool(PureWindowsPath(name).drive)
                      or "\\" in name or ":" in name
                      or any(p in {"", ".", ".."} for p in parts)
                      or any(ord(c) < 32 or ord(c) == 127 for c in name))
            if unsafe:
                errors.append({"kind": "unsafe-or-noncanonical-relative-path", "name": name})
            exact_seen[name].append(index)
            directory_by_name = info.is_dir()
            node = name.rstrip("/")
            if directory_by_name:
                explicit_dirs.add(node)
                all_dirs.add(node)
            else:
                files.add(node)
            all_dirs.update("/".join(parts[:end]) for end in range(1, len(parts)))

            unix_mode = info.external_attr >> 16 if info.create_system == 3 else None
            unix_type = stat.S_IFMT(unix_mode) if unix_mode is not None else None
            type_names = {stat.S_IFREG: "regular", stat.S_IFDIR: "directory",
                          stat.S_IFLNK: "symlink", stat.S_IFCHR: "character-device",
                          stat.S_IFBLK: "block-device", stat.S_IFIFO: "fifo",
                          stat.S_IFSOCK: "socket", 0: "not-specified"}
            type_name = type_names.get(unix_type, "unknown") if unix_type is not None else "not-unix-metadata"
            permissions = stat.S_IMODE(unix_mode) if unix_mode is not None else None
            if unix_type not in {None, 0, stat.S_IFREG, stat.S_IFDIR}:
                errors.append({"kind": "unsupported-file-type", "name": name, "type": type_name})
            if (unix_type == stat.S_IFDIR and not directory_by_name
                    or unix_type == stat.S_IFREG and directory_by_name):
                errors.append({"kind": "directory-type-name-disagreement", "name": name})
            if permissions is not None and permissions & 0o7000:
                errors.append({"kind": "special-permission-bits-require-explicit-handling", "name": name,
                               "bits": oct(permissions & 0o7000)})
            if info.flag_bits & 1:
                errors.append({"kind": "encrypted-entry", "name": name})

            git_mode = None
            mode_limitation = None
            if directory_by_name:
                mode_limitation = "Git checkout does not preserve this explicit directory entry or its Unix permission metadata."
            elif unix_type == stat.S_IFREG and permissions is not None:
                git_mode = "100755" if permissions & 0o111 else "100644"
                git_permissions = 0o755 if git_mode == "100755" else 0o644
                if permissions != git_permissions:
                    mode_limitation = f"Git represents this regular file as {git_mode}; archive permissions {permissions:04o} are not preserved."
            else:
                mode_limitation = "Unix regular-file mode was not explicitly supplied; do not infer original permissions from extraction defaults."

            content = archive.read(info)
            members.append({
                "index": index, "name": name, "raw_name_hex": raw_name.hex(), "name_encoding": encoding,
                "name_ascii": name.isascii(), "name_nfc": unicodedata.normalize("NFC", name) == name,
                "name_nfd": unicodedata.normalize("NFD", name) == name,
                "directory_by_name": directory_by_name,
                "create_system": info.create_system, "external_attr": info.external_attr,
                "external_attr_hex": f"0x{info.external_attr:08x}",
                "unix_mode": f"{unix_mode:06o}" if unix_mode is not None else None,
                "unix_type": type_name,
                "unix_permissions": f"{permissions:04o}" if permissions is not None else None,
                "regular_file_execute_bits": f"{permissions & 0o111:03o}" if unix_type == stat.S_IFREG else None,
                "projected_git_mode": git_mode, "git_projection_limitation": mode_limitation,
                "bytes": info.file_size, "sha256": sha256(content), "crc32": f"{info.CRC:08x}",
                "compression": info.compress_type, "compressed_bytes": info.compress_size,
                "zip_datetime": list(info.date_time), "extra_hex": info.extra.hex(),
            })

        duplicates = [{"name": name, "indices": indices} for name, indices in exact_seen.items() if len(indices) > 1]
        conflicts = sorted(files & all_dirs)
        transforms = {"NFC": lambda s: unicodedata.normalize("NFC", s),
                      "NFD": lambda s: unicodedata.normalize("NFD", s),
                      "casefold": str.casefold, "NFD-casefold-NFD": canonical_casefold}
        collisions = {}
        # Include every implicit directory prefix: different leaf names must
        # not conceal a collision between parent directory components.
        for label, transform in transforms.items():
            grouped = collections.defaultdict(list)
            for node in sorted(files | all_dirs):
                key = "/".join(transform(component) for component in node.split("/"))
                grouped[key].append(node)
            collisions[label] = [{"comparison_key": key, "nodes": nodes}
                                 for key, nodes in grouped.items() if len(nodes) > 1]
        empty_dirs = sorted(d for d in explicit_dirs if not any(f.startswith(d + "/") for f in files))
        if duplicates:
            errors.append({"kind": "exact-duplicate-member-names", "details": duplicates})
        if conflicts:
            errors.append({"kind": "file-directory-prefix-conflicts", "paths": conflicts})
        if any(collisions.values()):
            errors.append({"kind": "normalized-or-casefold-component-collisions", "details": collisions})
        report["members"] = members
        report["checks"] = {"exact_duplicate_members": duplicates,
                            "file_directory_prefix_conflicts": conflicts,
                            "component_collisions": collisions,
                            "all_members_read_with_crc_check": True,
                            "explicit_empty_directories": empty_dirs}

    report["summary"] = {
        "members": len(members), "regular_files": sum(m["unix_type"] == "regular" for m in members),
        "explicit_directories": sum(m["directory_by_name"] for m in members),
        "all_names_ascii": all(m["name_ascii"] for m in members),
        "mode_counts": dict(collections.Counter(m["unix_mode"] or "unknown" for m in members)),
        "regular_files_with_execute_bits": [m["name"] for m in members if m["unix_type"] == "regular" and m["regular_file_execute_bits"] != "000"],
        "regular_files_with_projection_loss": [{"name": m["name"], "unix_permissions": m["unix_permissions"],
            "projected_git_mode": m["projected_git_mode"], "limitation": m["git_projection_limitation"]}
            for m in members if not m["directory_by_name"] and m["git_projection_limitation"]],
        "explicit_empty_directories": report["checks"]["explicit_empty_directories"],
        "errors": errors, "structural_inspection_passed": not errors,
        "full_zip_metadata_preserved_by_git": False,
        "scope_limit": "Passing covers only the listed checks and this source archive. Fresh-clone byte/mode checks and an explicit Git projection remain required before accepting a migration."
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--source-url")
    parser.add_argument("--expected-sha256")
    args = parser.parse_args()
    if args.out.exists():
        raise SystemExit("Refusing to overwrite an existing audit result.")
    report = inspect(args.archive, args.source_url, args.expected_sha256)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"report": str(args.out.resolve()), "archive": report["archive"], "summary": report["summary"]},
                     ensure_ascii=False, indent=2))
    return 0 if report["summary"]["structural_inspection_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
