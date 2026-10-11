#!/usr/bin/env python3
"""Verify an exact public AAR package commit without executing the pilot.

This external driver checks a new Git transport clone, previously published
inputs, retained result bytes and the package's read-only verification CLIs.
It does not establish independent-team reproduction or facts asserted by an
audit record. Derived in part from verify_public_migration.py, SHA-256
b2e7ef69a3f3f7aeafef21ee7d569664e116a9766ea69ad5ae79a25f58d73bff.
SPDX-License-Identifier: MIT
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import io
import json
import math
import os
from pathlib import Path
import platform
import re
import shutil
import stat
import subprocess
import sys
import unicodedata
import zipfile


REPOSITORY = "https://github.com/WEXP-dev/wexp-interop.git"
COLLECTION_BASE = "b368b807195bbff578191ce2e2a6ac64f13646ae"
EMILIA = "experiments/emilia-interop-001/"
AAR = "experiments/wimse-aar-02-interop-001/packages/pkg-001"
ENV = {key: value for key, value in os.environ.items()
       if not key.startswith("GIT_") and key not in {"PYTHONPATH", "PYTHONHOME"}}
ENV.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
           GIT_ATTR_NOSYSTEM="1", PYTHONDONTWRITEBYTECODE="1", PYTHONNOUSERSITE="1")
GIT = ["git", "-c", "core.autocrlf=true", "-c", "core.filemode=true",
       "-c", "core.attributesFile=" + os.devnull]


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def blob(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def strict_json(raw):
    def pairs(rows):
        result = {}
        for key, value in rows:
            require(key not in result, "duplicate JSON member: " + key)
            result[key] = value
        return result

    def invalid(value):
        raise ValueError("non-finite JSON constant: " + value)

    def finite(value):
        number = float(value)
        require(math.isfinite(number), "non-finite parsed JSON number: " + value)
        return number

    return json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid, parse_float=finite)


def path_checks(entries):
    """Check file paths and implicit directory components under four views."""
    files, directories = set(entries), set()
    for name, entry in entries.items():
        parts = name.split("/")
        require(not name.startswith("/") and "\\" not in name and ":" not in name
                and all(part not in {"", ".", ".."} for part in parts)
                and not any(ord(char) < 32 or ord(char) == 127 for char in name),
                "unsafe or noncanonical path: " + name)
        require(entry["kind"] == "blob" and entry["mode"] in {"100644", "100755"},
                "unsupported Git object kind/mode: " + name)
        directories.update("/".join(parts[:end]) for end in range(1, len(parts)))
    require(not files & directories, "file/directory path conflict")
    transforms = {"NFC": lambda s: unicodedata.normalize("NFC", s),
                  "NFD": lambda s: unicodedata.normalize("NFD", s),
                  "casefold": str.casefold,
                  "NFD-casefold-NFD": lambda s: unicodedata.normalize(
                      "NFD", unicodedata.normalize("NFD", s).casefold())}
    collisions = {}
    for label, transform in transforms.items():
        groups = defaultdict(list)
        for path in sorted(files | directories):
            groups["/".join(transform(part) for part in path.split("/"))].append(path)
        collisions[label] = [paths for paths in groups.values() if len(paths) > 1]
    require(not any(collisions.values()), "case/Unicode/component collision")
    return {"status": "PASS", "regular_files": len(files), "implicit_directories": len(directories),
            "collisions": collisions, "unicode_database": unicodedata.unidata_version,
            "scope": "Listed names only; not a claim of portability to all filesystems."}


class Verification:
    def __init__(self, args, report):
        self.args, self.report = args, report
        self.clone = args.destination.resolve()
        self.out = args.artifacts.resolve()
        (self.out / "raw").mkdir(parents=True)
        self.env = dict(ENV, PYTHONPATH=str(args.dependencies.resolve()))
        self.commands = report["commands"] = []

    def run(self, command, *, cwd=None, environment=None, data=None):
        number = len(self.commands) + 1
        item = {"number": number, "command": command, "cwd": str(cwd) if cwd else None,
                "started_at_utc": now()}
        self.commands.append(item)
        try:
            completed = subprocess.run(command, cwd=cwd, input=data, env=environment or ENV,
                                       capture_output=True, timeout=120,
                                       preexec_fn=lambda: os.umask(0o022))
            stdout, stderr, code = completed.stdout, completed.stderr, completed.returncode
        except subprocess.TimeoutExpired as error:
            stdout, stderr, code = error.stdout or b"", error.stderr or b"", None
            item["timeout_seconds"] = 120
        for name, raw in [("stdout", stdout), ("stderr", stderr)]:
            relative = f"raw/{number:03d}.{name}"
            (self.out / relative).write_bytes(raw)
            item[name + "_file"] = relative
            item[name + "_bytes"] = len(raw)
            item[name + "_sha256"] = sha(raw)
            item[name + "_utf8"] = raw.decode("utf-8", errors="replace")
        item.update(returncode=code, finished_at_utc=now())
        require(code == 0, f"command {number} failed: {command!r}; returncode={code}")
        return stdout

    def git(self, *args, data=None):
        return self.run(GIT + ["-C", str(self.clone), *args], data=data)

    def tree(self, ref):
        result = {}
        for row in self.git("ls-tree", "-r", "-z", ref).split(b"\0"):
            if row:
                metadata, path = row.split(b"\t", 1)
                mode, kind, oid = metadata.decode().split()
                name = path.decode("utf-8")
                require(name not in result, "duplicate tracked path")
                result[name] = {"kind": kind, "mode": mode, "git_blob_sha1": oid}
        return result

    def preserve(self, ref, prefix, final, *, allow_additions):
        previous = {path: row for path, row in self.tree(ref).items() if path.startswith(prefix)}
        require(previous, "preservation prefix has no source files: " + prefix)
        changed = [path for path, row in previous.items() if final.get(path) != row]
        require(not changed, "previously published file changed or was removed: " + repr(changed))
        additions = sorted(path for path in final if path.startswith(prefix) and path not in previous)
        require(allow_additions or not additions, "unexpected additions in historical package: " + repr(additions))
        return {"status": "PASS", "source_commit": ref, "prefix": prefix,
                "unchanged_files": len(previous), "changed_or_removed": changed,
                "additions_permitted": allow_additions, "added_files": additions}

    def check_json_command(self, command, cwd):
        value = strict_json(self.run(command, cwd=cwd, environment=self.env))
        require(isinstance(value, dict) and value.get("status") == "PASS",
                "verification CLI did not return an explicit PASS: " + repr(command))
        return value

    def dependencies(self):
        requirements = self.clone / "requirements-verification.txt"
        expected = {}
        for line in requirements.read_text().splitlines():
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            match = re.fullmatch(r"([A-Za-z0-9_.-]+)==([A-Za-z0-9_.+-]+)", line)
            require(match and match[1] not in expected, "non-pinned or repeated dependency")
            expected[match[1]] = match[2]
        code = """import hashlib, importlib.metadata as m, json, sys
result={}
for name in sys.argv[1:]:
    dist=m.distribution(name)
    files=[]
    for entry in sorted(dist.files or [], key=str):
        path=dist.locate_file(entry)
        if path.is_file():
            raw=path.read_bytes()
            files.append({'listed_path':str(entry),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
        else:
            files.append({'listed_path':str(entry),'missing':True})
    result[name]={'version':dist.version,'declared_installed_files':files,
                  'inventory_sha256':hashlib.sha256(json.dumps(files,sort_keys=True,separators=(',',':')).encode()).hexdigest()}
print(json.dumps(result,sort_keys=True))
"""
        observed = strict_json(self.run([sys.executable, "-B", "-c", code, *expected],
                                        cwd=self.clone, environment=self.env))
        require({name: value["version"] for name, value in observed.items()} == expected,
                "installed dependencies differ from exact public pins")
        self.report["dependencies"] = {"requirements_sha256": sha(requirements.read_bytes()),
                                       "expected_versions": expected, "observed": observed,
                                       "inventory_scope": "Files declared by installed distribution metadata; file hashes do not authenticate their publisher."}

    def archive(self, final):
        package = self.clone / AAR
        card = strict_json((package / "record.json").read_bytes())
        relative = card["artifact"]["path"]
        require(isinstance(relative, str) and relative and not relative.startswith("/")
                and "\\" not in relative and all(p not in {"", ".", ".."} for p in relative.split("/")),
                "noncanonical AAR archive path")
        raw = (package / relative).read_bytes()
        require(sha(raw) == self.args.aar_zip_sha256 == card["artifact"]["sha256"]
                and type(card["artifact"]["bytes"]) is int and len(raw) == card["artifact"]["bytes"],
                "AAR ZIP differs from supplied hash or card")
        prefix = AAR + "/payload/"
        payload = {path[len(prefix):]: row for path, row in final.items() if path.startswith(prefix)}
        archive_files = {"PREPARATION.md": final[AAR + "/PREPARATION.md"],
                         **{"payload/" + name: row for name, row in payload.items()}}
        archived, rows = {}, []
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            require(archive.testzip() is None, "AAR ZIP CRC failure")
            for member in archive.infolist():
                name, mode = member.filename, member.external_attr >> 16
                require(name not in archived, "duplicate AAR ZIP member")
                if member.is_dir():
                    require(stat.S_ISDIR(mode), "AAR ZIP directory type differs")
                    require(name.endswith("/") and any(path.startswith(name) for path in archive_files),
                            "AAR ZIP contains an unexpected/empty directory")
                    archived[name] = None
                    continue
                require(member.create_system == 3 and stat.S_ISREG(mode)
                        and not (member.flag_bits & 1), "AAR ZIP special/encrypted/non-POSIX file")
                content = archive.read(member)
                projection = "100755" if mode & 0o111 else "100644"
                entry = {"kind": "blob", "mode": projection, "git_blob_sha1": blob(content)}
                require(archive_files.get(name) == entry, "AAR archive file differs from Git: " + name)
                archived[name] = entry
                rows.append({"path": name, "bytes": len(content), "sha256": sha(content),
                             "archive_permissions": f"{stat.S_IMODE(mode):04o}", "git_mode": projection})
        file_entries = {name: row for name, row in archived.items() if row is not None}
        require(set(file_entries) == set(archive_files), "AAR ZIP differs from the declared PREPARATION.md + payload/ inventory")
        return {"status": "PASS", "path": AAR + "/" + relative, "bytes": len(raw),
                "sha256": sha(raw), "md5": hashlib.md5(raw).hexdigest(),
                "regular_files": len(file_entries), "payload_regular_files": len(payload),
                "supporting_files": ["PREPARATION.md"], "path_checks": path_checks(file_entries), "files": rows,
                "archive_role": "Frozen public PREPARATION.md plus payload/; current outer card and publication state are outside this ZIP."}

    def execute(self):
        self.run(GIT + ["clone", "--no-local", "--no-checkout", REPOSITORY, str(self.clone)])
        self.git("checkout", "--detach", self.args.commit)
        observed = self.git("rev-parse", "HEAD", "HEAD^{tree}").decode().splitlines()
        require(observed == [self.args.commit, self.args.expected_tree], "public commit/tree identity differs")
        for ancestor in [COLLECTION_BASE, self.args.pre_run_commit]:
            self.git("merge-base", "--is-ancestor", ancestor, self.args.commit)
        require(self.git("rev-parse", "--show-object-format").decode().strip() == "sha1", "Git SHA-1 objects required")
        require(self.git("remote", "get-url", "origin").decode().strip() == REPOSITORY, "public origin differs")
        require(not self.git("status", "--porcelain=v1", "--untracked-files=all"), "fresh clone is not clean")
        self.report["git"] = {"version": self.git("--version").decode().strip(),
                              "commit": observed[0], "tree": observed[1],
                              "configuration": {"core.autocrlf": "true", "core.filemode": "true",
                                  "core.attributesFile": os.devnull, "GIT_CONFIG_NOSYSTEM": "1",
                                  "GIT_CONFIG_GLOBAL": os.devnull, "GIT_ATTR_NOSYSTEM": "1"}}
        final = self.tree(self.args.commit)
        self.report["tracked_path_checks"] = path_checks(final)
        rows = []
        for name, entry in sorted(final.items()):
            path = self.clone / name
            require(path.is_file() and not path.is_symlink(), "missing/symlinked tracked file: " + name)
            raw = path.read_bytes()
            mode = "0755" if entry["mode"] == "100755" else "0644"
            require(blob(raw) == entry["git_blob_sha1"] and f"{stat.S_IMODE(path.lstat().st_mode):04o}" == mode,
                    "checkout bytes or POSIX mode differ from Git: " + name)
            rows.append({"path": name, "bytes": len(raw), "sha256": sha(raw), **entry, "checkout_permissions": mode})
        self.report["tracked_files"] = rows
        attrs = self.git("check-attr", "-z", "--stdin", "text",
                         data=b"\0".join(name.encode() for name in sorted(final)) + b"\0").split(b"\0")[:-1]
        require(len(attrs) == len(final) * 3 and all(attrs[i+1:i+3] == [b"text", b"unset"]
                for i in range(0, len(attrs), 3)), "a tracked path lacks -text")
        self.report["emilia_preservation"] = self.preserve(COLLECTION_BASE, EMILIA, final, allow_additions=False)
        self.report["pre_run_preservation"] = self.preserve(self.args.pre_run_commit, AAR + "/", final, allow_additions=True)
        self.dependencies()
        self.report["aar_archive"] = self.archive(final)
        payload = self.clone / AAR / "payload"
        checks = [
            ("catalog", [sys.executable, "-B", "scripts/catalog.py", "--check"], self.clone),
            ("collection", [sys.executable, "-B", "scripts/verify_collection.py"], self.clone),
            ("emilia", [sys.executable, "-B", "scripts/verify_emilia.py", "--out", str(self.out / "emilia")], self.clone),
            ("aar", [sys.executable, "-B", "scripts/verify_aar.py"], self.clone),
            ("frozen_inputs", [sys.executable, "-B", "verify_inputs.py"], payload),
            ("strict_results", [sys.executable, "-B", "compare_results.py", "--results", "results/public-run-001"], payload),
        ]
        self.report["checks"] = {}
        for label, command, cwd in checks:
            self.report["checks"][label] = self.check_json_command(command, cwd)
        freeze = strict_json((self.out / "emilia/freeze.json").read_bytes())
        require(freeze.get("status") == "PASS" and freeze.get("all_byte_and_binding_checks_passed") is True
                and len(freeze.get("checks", {})) == 11 and all(value is True for value in freeze["checks"].values())
                and len(freeze.get("additional_checks", {})) == 3
                and all(value is True for value in freeze["additional_checks"].values())
                and freeze.get("wexp_or_emilia_implementation_executed") is False,
                "retained EMILIA freeze checks differ from their declared scope")
        self.report["emilia_freeze"] = freeze
        self.report["emilia_replay"] = strict_json((self.out / "emilia/verification.json").read_bytes())
        require(not self.git("status", "--porcelain=v1", "--untracked-files=all"), "verification changed the clone")
        self.report["auxiliary_artifact_inventory"] = [
            {"path": path.relative_to(self.out).as_posix(), "bytes": path.stat().st_size,
             "sha256": sha(path.read_bytes())}
            for path in sorted(self.out.rglob("*")) if path.is_file()]
        self.report["summary"] = {"fresh_public_clone_checked": True, "tracked_files_verified": len(final),
            "tracked_files_with_text_unset": len(final), "clean_before_and_after": True,
            "emilia_files_unchanged": self.report["emilia_preservation"]["unchanged_files"],
            "public_pre_run_files_unchanged": self.report["pre_run_preservation"]["unchanged_files"],
            "aar_zip_regular_files_verified": self.report["aar_archive"]["regular_files"],
            "aar_zip_payload_files_verified": self.report["aar_archive"]["payload_regular_files"],
            "saved_pipeline_cases_compared": self.report["checks"]["strict_results"]["pipeline_cases"],
            "saved_output_mutation_inputs_compared": self.report["checks"]["strict_results"]["output_mutation_inputs_compared"],
            "controlled_worlds_in_saved_results": self.report["checks"]["strict_results"]["controlled_worlds"],
            "checks": {name: value["status"] for name, value in self.report["checks"].items()},
            "pilot_implementation_execution_performed": False,
            "independent_external_reproduction_established": False,
            "remote_link_availability_checked": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ["commit", "expected-tree", "pre-run-commit", "aar-zip-sha256"]:
        parser.add_argument("--" + name, required=True)
    for name in ["destination", "artifacts", "report", "public-detail", "public-summary", "dependencies"]:
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    if os.name != "posix" or not all(re.fullmatch("[0-9a-f]{40}", value) for value in
                                    [args.commit, args.expected_tree, args.pre_run_commit]):
        parser.error("Requires a POSIX host and exact SHA-1 commit/tree identities.")
    if not re.fullmatch("[0-9a-f]{64}", args.aar_zip_sha256):
        parser.error("Requires the separately supplied exact AAR ZIP SHA-256.")
    new = [args.destination, args.artifacts, args.report, args.public_detail, args.public_summary]
    if any(path.exists() for path in new) or len({path.resolve() for path in new}) != len(new):
        parser.error("Every destination/output must be new and distinct; prior runs are never overwritten.")
    if any(path.resolve().is_relative_to(args.destination.resolve()) for path in new[1:]):
        parser.error("All outputs must be outside the clone.")
    if not args.dependencies.is_dir() or args.dependencies.resolve().is_relative_to(args.destination.resolve()):
        parser.error("Dependencies must already exist outside the clone; no installation is performed.")
    git_path = Path(shutil.which("git") or "")
    report = {"schema": "wexp-public-aar-verification-detail-001", "status": "FAIL",
              "repository": REPOSITORY, "tested_commit": args.commit, "expected_tree": args.expected_tree,
              "public_pre_run_commit": args.pre_run_commit, "collection_base_commit": COLLECTION_BASE,
              "expected_aar_zip_sha256": args.aar_zip_sha256, "started_at_utc": now(),
              "verification_script_sha256": sha(Path(__file__).read_bytes()),
              "environment": {"python": sys.version, "platform": platform.platform(),
                              "python_executable_sha256": sha(Path(sys.executable).read_bytes()),
                              "git_executable_sha256": sha(git_path.read_bytes()), "child_process_umask": "0022"},
              "limitations": [
                  "This observation applies only to the exact tested public commit and tree.",
                  "A later evidence-carrier commit is not verified by a report contained in that carrier.",
                  "This publisher-controlled check replays retained verification data; it does not rerun the pilot or establish external-team reproduction.",
                  "Hash, signature and recorded-result agreement do not establish the truth of producer assertions, human oversight, or execution beyond the declared observation boundary.",
                  "Git preserves bytes and an executable-bit projection, not every ZIP metadata field.",
                  "This driver does not verify release/DOI publication state, organization integration settings, or remote link availability."]}
    try:
        Verification(args, report).execute()
        report["status"] = "PASS"
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError, zipfile.BadZipFile) as error:
        report["error"] = str(error)
    report["finished_at_utc"] = now()
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + "\n")
    raw_hash = sha(args.report.read_bytes())
    replacements = [(str(args.destination.resolve()), "${CHECKOUT}"),
                    (str(args.artifacts.resolve()), "${AUXILIARY_OUTPUT}"),
                    (str(args.dependencies.resolve()), "${VERIFICATION_DEPENDENCIES}"),
                    (str(Path(sys.executable).resolve()), "${PYTHON}"), (sys.executable, "${PYTHON}")]
    replacements.sort(key=lambda pair: -len(pair[0]))
    text = json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False)
    for before, after in replacements:
        text = text.replace(before, after)
    detail = strict_json(text)
    detail["public_normalization"] = {"operation": "Replace only local checkout/output/dependency/Python paths.",
                                      "raw_result_sha256": raw_hash,
                                      "stream_hashes": "Hashes identify original command streams before displayed path replacement."}
    args.public_detail.parent.mkdir(parents=True, exist_ok=True)
    args.public_detail.write_text(json.dumps(detail, indent=2, ensure_ascii=False, allow_nan=False) + "\n")
    result = {key: report[key] for key in ["schema", "status", "repository", "tested_commit", "expected_tree",
              "public_pre_run_commit", "collection_base_commit", "expected_aar_zip_sha256", "started_at_utc",
              "finished_at_utc", "verification_script_sha256", "environment", "limitations"]}
    result.update(schema="wexp-public-aar-verification-001", checks=report.get("summary"),
                  raw_result_sha256=raw_hash, public_detail_sha256=sha(args.public_detail.read_bytes()))
    if "error" in report:
        result["error"] = report["error"]
    args.public_summary.parent.mkdir(parents=True, exist_ok=True)
    args.public_summary.write_text(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + "\n")
    print(json.dumps({"status": report["status"], "tested_commit": args.commit,
                      "checks": report.get("summary"), "error": report.get("error")}))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
