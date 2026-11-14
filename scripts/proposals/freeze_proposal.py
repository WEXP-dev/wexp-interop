#!/usr/bin/env python3
"""Freeze a proposal before its first run, and check that the order was kept.

usage: python3 -B scripts/proposals/freeze_proposal.py freeze docs/proposals/<slug>
       python3 -B scripts/proposals/freeze_proposal.py check  docs/proposals/<slug> [--git]

`freeze` writes FREEZE.json: the SHA-256 of every file a run depends on. `check` verifies those
digests against the files as they are now. With --git it also verifies, from the commit history,
that the freeze was committed before the evidence of the run and without it: the commit that last
changed FREEZE.json touches nothing under evidence/, and every commit that last changed an evidence
file is a later descendant of it. A mapping revised after a run therefore needs a new freeze and a
new run. What the history cannot show is a run that was never committed; that stays a declaration.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import proposal_lib as lib  # noqa: E402


def freeze(directory: Path) -> dict:
    lib.case_ids(directory)
    if (directory / 'evidence').exists() and any((directory / 'evidence').iterdir()):
        raise lib.ProposalError('evidence/ already holds a run; a freeze written now would post-date it')
    record = {'algorithm': 'sha256', 'note': 'committed before the first appraiser run on any input of this proposal',
              'files': lib.frozen_files(directory)}
    (directory / 'FREEZE.json').write_text(json.dumps(record, indent=1, sort_keys=True) + '\n', encoding='utf-8')
    return record


def check(directory: Path, use_git: bool) -> dict:
    lib.case_ids(directory)
    path = directory / 'FREEZE.json'
    if not path.is_file():
        raise lib.ProposalError('no FREEZE.json: the proposal has not been frozen')
    recorded = json.loads(path.read_text(encoding='utf-8'))['files']
    current = lib.frozen_files(directory)
    changed = sorted(f for f in recorded if current.get(f) != recorded[f])
    added = sorted(f for f in current if f not in recorded)
    if changed or added:
        raise lib.ProposalError('files differ from the freeze: changed or missing ' + (', '.join(changed) or 'none')
                                + '; not in the freeze ' + (', '.join(added) or 'none'))
    out = {'frozen_files': len(recorded), 'digests': 'match', 'order': 'not checked'}
    if not use_git:
        return out
    root = Path(lib.git(directory, 'rev-parse', '--show-toplevel'))
    rel = directory.resolve().relative_to(root.resolve()).as_posix()
    freeze_commit = lib.git(root, 'log', '-1', '--format=%H', '--', f'{rel}/FREEZE.json')
    if not freeze_commit:
        raise lib.ProposalError('FREEZE.json is not committed')
    touched = lib.git(root, 'show', '--name-only', '--format=', freeze_commit).split('\n')
    if any(name.startswith(f'{rel}/evidence/') for name in touched):
        raise lib.ProposalError(f'the freeze commit {freeze_commit[:8]} also changes evidence/: '
                                'the freeze must be committed before the run, not with it')
    evidence = [p for p in sorted((directory / 'evidence').rglob('*')) if p.is_file()] if (directory / 'evidence').is_dir() else []
    out.update({'freeze_commit': freeze_commit, 'evidence_files': len(evidence), 'order': 'kept'})
    for p in evidence:
        name = p.resolve().relative_to(root.resolve()).as_posix()
        commit = lib.git(root, 'log', '-1', '--format=%H', '--', name)
        if not commit:
            raise lib.ProposalError(f'{name} is not committed')
        if commit == freeze_commit or lib.git(root, 'merge-base', commit, freeze_commit) != freeze_commit:
            raise lib.ProposalError(f'{name} was last changed in {commit[:8]}, which does not come after '
                                    f'the freeze commit {freeze_commit[:8]}')
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('command', choices=('freeze', 'check'))
    ap.add_argument('directory', type=Path)
    ap.add_argument('--git', action='store_true')
    a = ap.parse_args()
    try:
        if a.command == 'freeze':
            record = freeze(a.directory)
            print(f'frozen {len(record["files"])} files; commit FREEZE.json before any run')
        else:
            print(json.dumps(check(a.directory, a.git), sort_keys=True))
    except (lib.ProposalError, OSError, ValueError, KeyError) as error:
        print(f'refused: {error}', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
