#!/usr/bin/env python3
"""Create the skeleton of a proposal: pinned public bytes with digests, and templates to fill in.

usage: python3 -B scripts/proposals/new_proposal.py --slug atx-boundary-001 --title "..." \
           [--issue 26] --pin owner/repo@<commit>:path [--pin ...]
           [--relation repository-owner]

It fetches each pinned file once to record its SHA-256 and size. It writes no mapping and no
expectation: those are the work a person does next. It also writes RESULT-ROW.json as a draft that
records who initiated the check and how that is known; nobody is named in it until they agree.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import proposal_lib as lib  # noqa: E402
import result_table  # noqa: E402

README = '''# {title}: local proposal

**Status: PROPOSAL. Not a published package.** The result row and the attribution are agreed with the
author of the external format before anything here is described as a result. Nothing here states
that the external format conforms or does not conform to WEXP Core.

{origin}
## Steps, in order

1. **Pinned bytes.** [SOURCE-PINS.json](SOURCE-PINS.json) names the exact public files this proposal
   refers to, with SHA-256 and size, and the revisions of both appraisers.
2. **Mapping and expectations.** [FIELDS.md](FIELDS.md) lists the fields of the pinned files, with
   nothing decided about them. [MAPPING.md](MAPPING.md) says how the external record maps to a
   normalized Core-02 input. `inputs/<case>.json` holds `{{"id": ..., "input": ...}}` and
   `expectations/<case>.json` holds `{{"id": ..., "expected": ...}}` with all twenty result components.
   Corrections from the author go in as a new revision section of MAPPING.md.
3. **Freeze.** `python3 -B scripts/proposals/freeze_proposal.py freeze docs/proposals/{slug}` writes
   FREEZE.json. Commit it before any appraiser runs.
4. **Run.** `python3 -B scripts/proposals/run_proposal.py docs/proposals/{slug} --wexp-ref <checkout>
   --wexp-check <checkout> --write` runs both appraisers and writes `evidence/`. Commit it after the
   freeze. A difference from an expectation is recorded as it is; expectations are not edited after a run.

5. **Result row.** [RESULT-ROW.json](RESULT-ROW.json) says what was examined, who initiated the check
   and how that is known, and whether the author of the format agreed the row. It starts as a draft
   that names nobody. `python3 -B scripts/proposals/result_table.py` rebuilds the results page from it.

## For the author of the format

You do not need to edit anything. Answer in the pull request with one line; copy whichever applies:

- `Mapping read: correct as written.`
- `Mapping read: wrong here: <what it misreads>.`
- `Name me as: <your name>.` or `Do not name me.`
- `Row agreed.`

Each of these is a separate answer. Agreeing that the mapping reads your format correctly is not
agreeing the result row, and neither says anything about WEXP as a whole.

Both appraisers are operated by one person. A run here is not an independent reproduction.
'''

MAPPING = '''# Mapping: {title}

Core-02 line numbers refer to the published XML of draft-sergeev-wexp-core-02 (SHA-256
`{core02}`).

## Revision 1 (before any appraiser run)

1. **What the external record establishes, in its author's terms.** _To write._
2. **What it does not name or bind** (target, action, actor). _To write._
3. **How each part is carried into a Core-02 input,** and what is deliberately not mapped. Every
   field listed in [FIELDS.md](FIELDS.md) is accounted for. _To write._
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


FIELD_KEY = re.compile(r'^[A-Za-z0-9_.:@/-]{1,80}$')
MAX_FIELD_ROWS = 300
MAX_FIELD_DEPTH = 12


def _unique(pairs):
    keys = [k for k, _ in pairs]
    if len(set(keys)) != len(keys):
        raise ValueError('repeated key')
    return dict(pairs)


def field_paths(value, prefix: str = '', depth: int = 0, out: dict | None = None) -> dict:
    """Paths of the fields of a JSON value with the kind of each. No value is copied."""
    out = {} if out is None else out
    if depth > MAX_FIELD_DEPTH or len(out) >= MAX_FIELD_ROWS:
        return out
    if type(value) is dict:
        for key, child in value.items():
            name = key if FIELD_KEY.match(key) else f'(a key of {len(key)} characters, not shown)'
            field_paths(child, f'{prefix}.{name}' if prefix else name, depth + 1, out)
    elif type(value) is list:
        if not value:
            out.setdefault(f'{prefix}[]', set()).add('empty list')
        for child in value[:50]:
            field_paths(child, f'{prefix}[]', depth + 1, out)
    else:
        kind = {str: 'string', bool: 'boolean', int: 'number', float: 'number', type(None): 'null'}[type(value)]
        if len(out) < MAX_FIELD_ROWS or prefix in out:
            out.setdefault(prefix or '(the whole value)', set()).add(kind)
    return out


def fields_page(title: str, files: list[tuple[dict, bytes]]) -> str:
    """The field inventory of the pinned files: every field once, with nothing decided about it.

    This is the mechanical half of a mapping. What each field means, and whether it is carried
    into a Core-02 input, is the work of MAPPING.md and is not attempted here.
    """
    out = [f'# Fields of the pinned files: {title}', '',
           'Generated from the pinned bytes when the skeleton was made. It lists the fields that are present, '
           'not what they mean. Fill the last column while writing [MAPPING.md](MAPPING.md); a field that is '
           'deliberately not carried is written as such, not left blank. Values are not shown here.', '']
    for pin, data in files:
        out += [f'## `{pin["repository"]}` at `{pin["commit"][:12]}`: `{pin["path"]}`', '']
        try:
            paths = field_paths(json.loads(data, object_pairs_hook=_unique))
        except (ValueError, RecursionError, KeyError):
            out += ['Not read as JSON, or it repeats a key. List its fields by hand.', '']
            continue
        out += ['| Field | Kind | Carried into a Core-02 input as |', '|---|---|---|']
        out += [f'| `{path}` | {", ".join(sorted(kinds))} | _to decide_ |' for path, kinds in paths.items()]
        if len(paths) >= MAX_FIELD_ROWS:
            out.append(f'| _more than {MAX_FIELD_ROWS} fields; the rest are not listed_ | | |')
        out.append('')
    return '\n'.join(out)


def build(slug: str, title: str, pins: list[str], issue: int | None, root: Path, fetch=lib.fetch_pinned,
          relation: str = 'not-established') -> Path:
    directory = lib.proposal_dir(slug, root)
    if directory.exists():
        raise lib.ProposalError(f'{directory.name} already exists; a proposal is never overwritten')
    if not title.strip() or len(title) > 120 or any(c in title for c in '\r\n`<>[]'):
        raise lib.ProposalError('title must be one plain line of at most 120 characters')
    parsed = [lib.parse_pin(p) for p in pins]
    if not parsed:
        raise lib.ProposalError('at least one --pin is required: a proposal is about exact bytes')
    files, contents = [], []
    for pin in parsed:
        data = fetch(pin)
        files.append({**pin, 'sha256': lib.sha256(data), 'bytes': len(data)})
        contents.append((pin, data))
    if relation not in result_table.RELATIONS:
        raise lib.ProposalError(f'relation is one of {tuple(result_table.RELATIONS)}')
    # The draft row names nobody and therefore no repository or draft either; both are added with
    # the name once the person agrees to be named.
    row = result_table.template(title.strip(), issue, relation)
    origin = ''
    if issue is not None:
        origin = (f'Opened from interoperability check '
                  f'[WEXP-dev/interop-test-lab#{issue}](https://github.com/WEXP-dev/interop-test-lab/issues/{issue}).\n\n')
    (directory / 'inputs').mkdir(parents=True)
    (directory / 'expectations').mkdir()
    (directory / 'README.md').write_text(README.format(title=title.strip(), slug=slug, origin=origin), encoding='utf-8')
    (directory / 'FIELDS.md').write_text(fields_page(title.strip(), contents), encoding='utf-8')
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
    (directory / lib.RESULT_ROW).write_text(json.dumps(row, indent=1, sort_keys=True) + '\n', encoding='utf-8')
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
    ap.add_argument('--relation', default='not-established')
    ap.add_argument('--root', type=Path, default=lib.PROPOSALS)
    a = ap.parse_args()
    try:
        directory = build(a.slug, a.title, a.pin, a.issue, a.root, relation=a.relation)
    except lib.ProposalError as error:
        print(f'refused: {error}', file=sys.stderr)
        return 2
    print(f'created {directory}')
    for f in json.loads((directory / 'SOURCE-PINS.json').read_text())['external_files']:
        print(f"  {f['repository']}@{f['commit'][:8]}:{f['path']}  sha256 {f['sha256']}  {f['bytes']} bytes")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
