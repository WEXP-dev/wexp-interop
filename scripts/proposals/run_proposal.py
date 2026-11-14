#!/usr/bin/env python3
"""Run both appraisers on the frozen inputs of a proposal and compare every result component.

usage: python3 -B scripts/proposals/run_proposal.py docs/proposals/<slug> --wexp-ref <checkout> \
           --wexp-check <checkout> [--write] [--compare-committed] [--summary file.md]

Each appraiser runs in its own interpreter process with only its own checkout on the path. The
checkouts must be clean and at the commits named in SOURCE-PINS.json. A result that differs from
its expectation is reported and recorded, and is not an error. An appraiser that fails to complete
a case is a refusal, never a result: exit status is 0 when the run completed, 2 when it was refused, 3 when --compare-committed finds that the committed evidence is
not what this run produced.
"""
from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import proposal_lib as lib  # noqa: E402

DRIVER = r'''
import json, sys
mod, inp, prof = sys.argv[1:4]
if mod == 'wexp_check':
    from wexp_check import appraise
else:
    from wexp_ref.core02.appraiser import appraise
print(json.dumps(appraise(json.load(open(inp)), json.load(open(prof)))))
'''
ENGINES = ('wexp_ref', 'wexp_check')


def pinned_checkout(path: Path, expected: str, name: str) -> None:
    head = lib.git(path, 'rev-parse', 'HEAD')
    if head != expected:
        raise lib.ProposalError(f'{name} checkout is at {head[:8]}, SOURCE-PINS.json names {expected[:8]}')
    if lib.git(path, 'status', '--porcelain', '--untracked-files=no'):
        raise lib.ProposalError(f'{name} checkout has local changes')


def run(directory: Path, wexp_ref: Path, wexp_check: Path) -> dict:
    directory = directory.resolve()
    ids = lib.case_ids(directory)
    pins = json.loads((directory / 'SOURCE-PINS.json').read_text(encoding='utf-8'))
    for key in ('wexp_ref', 'wexp_check'):
        if not lib.SHA_RE.match(pins[key]['commit']):
            raise lib.ProposalError(f'SOURCE-PINS.json: {key} commit is not a full commit id')
    pinned_checkout(wexp_ref, pins['wexp_ref']['commit'], 'wexp-ref')
    pinned_checkout(wexp_check, pins['wexp_check']['commit'], 'wexp-check')
    paths = {'wexp_ref': wexp_ref.resolve() / 'src', 'wexp_check': wexp_check.resolve()}
    report = {'python': platform.python_version(), 'wexp_ref': pins['wexp_ref']['commit'],
              'wexp_check': pins['wexp_check']['commit'], 'cases': {}}
    with tempfile.TemporaryDirectory() as tmp:
        for cid in ids:
            wrapper = json.loads((directory / 'inputs' / f'{cid}.json').read_text(encoding='utf-8'))
            expected = json.loads((directory / 'expectations' / f'{cid}.json').read_text(encoding='utf-8'))['expected']
            inp = Path(tmp) / f'{cid}.json'
            inp.write_text(json.dumps(wrapper['input']), encoding='utf-8')
            row = {}
            for mod in ENGINES:
                r = subprocess.run([sys.executable, '-I', '-B', '-c', 'import sys; sys.path.insert(0, sys.argv.pop(1)); exec(sys.argv.pop(1))',
                                    str(paths[mod]), DRIVER, mod, str(inp), str(directory / 'profiles.json')],
                                   capture_output=True, text=True, cwd=tmp)
                if r.returncode != 0:
                    raise lib.ProposalError(f'{mod} did not complete case {cid}: ' + r.stderr.strip()[-300:])
                observed = json.loads(r.stdout)
                row[f'{mod}_equals_expected'] = lib.same(observed, expected)
                if not row[f'{mod}_equals_expected']:
                    row[f'{mod}_differing_components'] = sorted(k for k in expected if not lib.same({k: expected[k]}, {k: observed.get(k)}))
                row[f'{mod}_observed'] = observed
            row['appraisers_equal'] = lib.same(row['wexp_ref_observed'], row['wexp_check_observed'])
            row['expected_verdict'] = expected.get('verdict')
            report['cases'][cid] = row
    return report


def summary(directory: Path, report: dict, committed: str) -> str:
    lines = [f'### Proposal `{directory.name}`', '',
             f'wexp-ref `{report["wexp_ref"][:8]}`, wexp-check `{report["wexp_check"][:8]}`, Python {report["python"]}. '
             f'Committed evidence: {committed}.', '',
             '| Case | Expected verdict | wexp-ref | wexp-check | Appraisers equal |', '|---|---|---|---|---|']
    def cell(row, mod):
        observed = row[f'{mod}_observed']
        verdict = observed.get('verdict') if observed.get('verdict') in ('accept', 'downgrade', 'reject') else 'other'
        if row[f'{mod}_equals_expected']:
            return f'{verdict}, equals expectation'
        return f'{verdict}, differs in {len(row[f"{mod}_differing_components"])} component(s)'
    for cid, row in report['cases'].items():
        expected = row['expected_verdict'] if row['expected_verdict'] in ('accept', 'downgrade', 'reject') else 'other'
        lines.append(f'| `{cid}` | {expected} | {cell(row, "wexp_ref")} | {cell(row, "wexp_check")} | '
                     f'{"yes" if row["appraisers_equal"] else "no"} |')
    lines += ['', 'Both appraisers are operated by one person; this is not an independent reproduction. '
              'A difference from an expectation is a recorded result, not a failure of the check.', '']
    return '\n'.join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('directory', type=Path)
    ap.add_argument('--wexp-ref', required=True, type=Path)
    ap.add_argument('--wexp-check', required=True, type=Path)
    ap.add_argument('--write', action='store_true', help='write evidence/comparison.json')
    ap.add_argument('--compare-committed', action='store_true')
    ap.add_argument('--summary', type=Path)
    a = ap.parse_args()
    try:
        report = run(a.directory, a.wexp_ref, a.wexp_check)
    except (lib.ProposalError, OSError, ValueError, KeyError) as error:
        print(f'refused: {error}', file=sys.stderr)
        return 2
    target = a.directory / 'evidence' / 'comparison.json'
    status, committed = 0, 'none yet'
    if a.compare_committed and target.is_file():
        saved = json.loads(target.read_text(encoding='utf-8'))
        if lib.same(saved.get('cases'), report['cases']):
            committed = 'equal to this run'
        else:
            committed, status = 'DIFFERS from this run', 3
    if a.write:
        target.parent.mkdir(exist_ok=True)
        target.write_text(json.dumps(report, indent=1, sort_keys=True) + '\n', encoding='utf-8')
    text = summary(a.directory, report, committed)
    if a.summary:
        with a.summary.open('a', encoding='utf-8') as handle:
            handle.write(text + '\n')
    print(text)
    return status


if __name__ == '__main__':
    raise SystemExit(main())
