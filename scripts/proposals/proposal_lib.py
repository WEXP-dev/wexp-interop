"""Shared pieces of the proposal tooling: identifiers, digests, pinned fetch, logical comparison.

A proposal is a directory under docs/proposals/ that takes one external evidence format through the
same steps every time: pin the exact public bytes, write the mapping and the expected results, freeze
them, then run both appraisers and compare. Nothing here decides a mapping; it only keeps the order
and the bytes honest. Standard library only.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PROPOSALS = REPO_ROOT / 'docs' / 'proposals'
SLUG_RE = re.compile(r'^[a-z0-9][a-z0-9-]{1,46}-[0-9]{3}$')
CASE_RE = re.compile(r'^[A-Za-z0-9][A-Za-z0-9-]{0,31}$')
SHA_RE = re.compile(r'^[0-9a-f]{40}$')
NAME = r'[A-Za-z0-9](?:[A-Za-z0-9._-]{0,98}[A-Za-z0-9_])?'
PIN_RE = re.compile(rf'^({NAME})/({NAME})@([0-9a-f]{{40}}):([A-Za-z0-9._-]+(?:/[A-Za-z0-9._-]+)*)$')
RESULT_ROW = 'RESULT-ROW.json'
RAW_HOST = 'raw.githubusercontent.com'
MAX_FILE_BYTES = 2 * 1024 * 1024
CORE02_XML_SHA256 = 'de983051a1c6ea51ea9b7f965fe9eabf2d97af92ab2f074781bd44e3f99c8782'
WEXP_REF_COMMIT = '56289024c9ee748111f1f1d4f42728ffe04d8d69'
WEXP_CHECK_COMMIT = '63bde685c54fd6329f1217708d1c211b80c3712e'
SET_FIELDS = {'qualifiers', 'profile_identifiers', 'basis_refs', 'reasons', 'limitations', 'base_findings',
              'qualifier_findings', 'recorder_relations', 'counter_evidence', 'evaluation_scope',
              'profile_evaluation_gaps', 'inherited_limitations', 'fatal_conditions', 'affected_claims',
              'fatal_reasons', 'substantive_reasons', 'evaluation_gaps', 'evaluation_gap_entries',
              'supported_claims', 'maximal_supported_claims', 'support_entries', 'support_relations'}


class ProposalError(Exception):
    """A refusal with a reason a person can act on."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def proposal_dir(slug: str, root: Path = PROPOSALS) -> Path:
    if not SLUG_RE.match(slug):
        raise ProposalError('slug must look like "format-topic-001": lowercase letters, digits, hyphens, '
                            'and a three-digit number at the end')
    return root / slug


def parse_pin(text: str) -> dict:
    m = PIN_RE.match(text.strip())
    if not m or any(part in ('.', '..') for part in m.group(4).split('/')):
        raise ProposalError(f'pin must be owner/repo@<40-hex commit>:path, got {text[:80]!r}')
    return {'repository': f'{m.group(1)}/{m.group(2)}', 'commit': m.group(3), 'path': m.group(4)}


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def fetch_pinned(pin: dict) -> bytes:
    """Bytes of one public file at an exact commit, from the raw-content host only."""
    url = f"https://{RAW_HOST}/{pin['repository']}/{pin['commit']}/{pin['path']}"
    try:
        opener = urllib.request.build_opener(_NoRedirect)
        with opener.open(urllib.request.Request(url, headers={'User-Agent': 'wexp-interop-proposals'}),
                         timeout=20) as response:
            data = response.read(MAX_FILE_BYTES + 1)
    except (urllib.error.URLError, OSError) as error:
        raise ProposalError(f'cannot read {pin["repository"]}@{pin["commit"][:8]}:{pin["path"]}: {error}')
    if len(data) > MAX_FILE_BYTES:
        raise ProposalError(f'{pin["path"]} is larger than {MAX_FILE_BYTES} bytes')
    return data


def enc(value) -> str:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(',', ':'), allow_nan=False)


def logical(value, field=None):
    if type(value) is dict:
        return {k: logical(v, k) for k, v in value.items()}
    if type(value) is list:
        items = [logical(v) for v in value]
        return sorted(items, key=enc) if field in SET_FIELDS else items
    return value


def same(a, b) -> bool:
    return enc(logical(a)) == enc(logical(b))


def case_ids(directory: Path) -> list[str]:
    ids = sorted(p.stem for p in (directory / 'inputs').glob('*.json'))
    for cid in ids:
        if not CASE_RE.match(cid):
            raise ProposalError(f'case identifier {cid!r} is not letters, digits and hyphens')
        if not (directory / 'expectations' / f'{cid}.json').is_file():
            raise ProposalError(f'case {cid} has an input and no expectation')
    extra = sorted(p.stem for p in (directory / 'expectations').glob('*.json') if p.stem not in ids)
    if extra:
        raise ProposalError(f'expectation without an input: {", ".join(extra)}')
    if not ids:
        raise ProposalError('no cases: inputs/ holds no .json file')
    return ids


def frozen_files(directory: Path) -> dict[str, str]:
    """Everything a run depends on: all files except the freeze record, the evidence of runs, and the
    result row, which is written after a run and agreed with the author."""
    out = {}
    for path in sorted(directory.rglob('*')):
        rel = path.relative_to(directory)
        if not path.is_file() or path.is_symlink() or rel.parts[0] == 'evidence' or rel.name == 'FREEZE.json':
            continue
        if rel.as_posix() == RESULT_ROW:
            continue
        if '__pycache__' in rel.parts:
            continue
        out[rel.as_posix()] = sha256(path.read_bytes())
    return out


def git(root: Path, *args: str) -> str:
    result = subprocess.run(['git', '-C', str(root), *args], capture_output=True, text=True)
    if result.returncode != 0:
        raise ProposalError(f'git {" ".join(args[:3])} failed: {result.stderr.strip()[:200]}')
    return result.stdout.strip()
