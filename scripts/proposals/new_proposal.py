#!/usr/bin/env python3
"""Create the skeleton of a proposal: pinned public bytes with digests, and templates to fill in.

usage: python3 -B scripts/proposals/new_proposal.py --slug atx-boundary-001 --title "..." \
           [--issue 26] --pin owner/repo@<commit>:path [--pin ...]

It fetches each pinned file once to record its SHA-256 and size. It writes no mapping and no
expectation: those are the work a person does next.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import proposal_lib as lib  # noqa: E402

README = '''# {title}: local proposal

**Status: PROPOSAL. Not a published package.** The result row and the attribution are agreed with the
author of the external format before anything here is described as a result. Nothing here states
that the external format conforms or does not conform to WEXP Core.

{origin}
## Steps, in order

1. **Pinned bytes.** [SOURCE-PINS.json](SOURCE-PINS.json) names the exact public files this proposal
   refers to, with SHA-256 and size, and the revisions of both appraisers.
2. **Mapping and expectations.** [MAPPING.md](MAPPING.md) says how the external record maps to a
   normalized Core-02 input. `inputs/<case>.json` holds `{{"id": ..., "input": ...}}` and
   `expectations/<case>.json` holds `{{"id": ..., "expected": ...}}` with all twenty result components.
   Corrections from the author go in as a new revision section of MAPPING.md.
3. **Freeze.** `python3 -B scripts/proposals/freeze_proposal.py freeze docs/proposals/{slug}` writes
   FREEZE.json. Commit it before any appraiser runs.
4. **Run.** `python3 -B scripts/proposals/run_proposal.py docs/proposals/{slug} --wexp-ref <checkout>
   --wexp-check <checkout> --write` runs both appraisers and writes `evidence/`. Commit it after the
   freeze. A difference from an expectation is recorded as it is; expectations are not edited after a run.

Both appraisers are operated by one person. A run here is not an independent reproduction.
'''

MAPPING = '''# Mapping: {title}

Core-02 line numbers refer to the published XML of draft-sergeev-wexp-core-02 (SHA-256
`{core02}`).

## Revision 1 (before any appraiser run)

1. **What the external record establishes, in its author's terms.** _To write._
2. **What it does not name or bind** (target, action, actor). _To write._
3. **How each part is carried into a Core-02 input,** and what is deliberately not mapped. _To write._
4. **What is left to the mapping and never reaches Core** (for example an upstream rejection). _To write._

## Cases and pre-run expectations

| Case | What differs | Expected verdict | Expected non-fatal tokens |
|---|---|---|---|
| _id_ | _one variable_ | _accept, downgrade or reject_ | _tokens, with the Core-02 line each comes from_ |

## Reading choices

_Where the text allowed two readings, name both and say which one each case takes._

## What was read to write the inputs

_Sources, with revisions. State that no appraiser ran on these inputs before FREEZE.json was committed._
'''


def build(slug: str, title: str, pins: list[str], issue: int | None, root: Path, fetch=lib.fetch_pinned) -> Path:
    directory = lib.proposal_dir(slug, root)
    if directory.exists():
        raise lib.ProposalError(f'{directory.name} already exists; a proposal is never overwritten')
    if not title.strip() or len(title) > 120 or any(c in title for c in '\r\n`<>[]'):
        raise lib.ProposalError('title must be one plain line of at most 120 characters')
    parsed = [lib.parse_pin(p) for p in pins]
    if not parsed:
        raise lib.ProposalError('at least one --pin is required: a proposal is about exact bytes')
    files = []
    for pin in parsed:
        data = fetch(pin)
        files.append({**pin, 'sha256': lib.sha256(data), 'bytes': len(data)})
    origin = ''
    if issue is not None:
        origin = (f'Opened from interoperability check '
                  f'[WEXP-dev/interop-test-lab#{issue}](https://github.com/WEXP-dev/interop-test-lab/issues/{issue}).\n\n')
    (directory / 'inputs').mkdir(parents=True)
    (directory / 'expectations').mkdir()
    (directory / 'README.md').write_text(README.format(title=title.strip(), slug=slug, origin=origin), encoding='utf-8')
    (directory / 'MAPPING.md').write_text(MAPPING.format(title=title.strip(), core02=lib.CORE02_XML_SHA256), encoding='utf-8')
    pins_record = {'core02_xml_sha256': lib.CORE02_XML_SHA256, 'external_files': files,
                   'wexp_ref': {'repository': 'WEXP-dev/wexp-ref', 'commit': lib.WEXP_REF_COMMIT},
                   'wexp_check': {'repository': 'WEXP-dev/wexp-check', 'commit': lib.WEXP_CHECK_COMMIT}}
    if issue is not None:
        pins_record['interop_check_issue'] = issue
    (directory / 'SOURCE-PINS.json').write_text(json.dumps(pins_record, indent=1, sort_keys=True) + '\n', encoding='utf-8')
    profile = f'wexp-work/interop/{slug}/mapping-1'
    (directory / 'profiles.json').write_text(json.dumps(
        {profile: {'tokens': {}, 'relation_tokens': [], 'scope_names': []}}, indent=1, sort_keys=True) + '\n', encoding='utf-8')
    for sub in ('inputs', 'expectations'):
        (directory / sub / 'README.md').write_text(
            f'One `<case>.json` per case. See [../README.md](../README.md).\n', encoding='utf-8')
    return directory


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--slug', required=True)
    ap.add_argument('--title', required=True)
    ap.add_argument('--pin', action='append', default=[])
    ap.add_argument('--issue', type=int)
    ap.add_argument('--root', type=Path, default=lib.PROPOSALS)
    a = ap.parse_args()
    try:
        directory = build(a.slug, a.title, a.pin, a.issue, a.root)
    except lib.ProposalError as error:
        print(f'refused: {error}', file=sys.stderr)
        return 2
    print(f'created {directory}')
    for f in json.loads((directory / 'SOURCE-PINS.json').read_text())['external_files']:
        print(f"  {f['repository']}@{f['commit'][:8]}:{f['path']}  sha256 {f['sha256']}  {f['bytes']} bytes")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
