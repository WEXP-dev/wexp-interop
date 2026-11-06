#!/usr/bin/env python3
"""Read-only checks for the SCITT Receipt boundary-finding package (profile scitt-receipt-boundary-v1).

SPDX-License-Identifier: MIT
Checks the frozen payload inventory against its reviewed pin, the source archive against
the payload, the frozen expectations against their delivered digest list, and the recorded
comparison results. No appraiser, emulator or Transparency Service is executed.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
REL = 'experiments/scitt-receipt-boundary-001/packages/pkg-001'
SOURCE_MANIFEST_SHA256 = 'af579564fa959780e21c6da578f4e56d01da9a092c6cf786638fd7f7f33a872a'
ARCHIVE_SHA256 = 'ab8441e581c903288e9a115736482ffab684391bc73ccc283f82bfbb07d9dc29'
WORKSPACE_COMMIT = '428f03752bce590b221ea053c361d48a714e7702'
EMULATOR_COMMIT = 'cfebeee5bb3da7d5a9a13d319aaaab17c1348641'
RECEIPT_SHA256 = '510a71486c25d7e8ac2814af268b705b156444ca5ec896d0da176dc8911e7dde'
STATEMENT_SHA256 = '18df0c526cbebabb192f1a8f8bb0ba2cfded48266984cc76f73c2cd4a8d866d9'
CASES = ('a', 'b1', 'b2', 'c')


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def unique(pairs):
    out = {}
    for key, value in pairs:
        require(key not in out, 'duplicate JSON key')
        out[key] = value
    return out


def load(raw):
    return json.loads(raw, object_pairs_hook=unique,
                      parse_constant=lambda text: (_ for _ in ()).throw(ValueError('non-JSON constant')))


def checked_path(root, name):
    parts = name.split('/')
    require(bool(name) and not name.startswith('/') and '\\' not in name
            and all(p not in ('', '.', '..') for p in parts), 'noncanonical path')
    path = root.joinpath(*parts)
    require(path.resolve().is_relative_to(root.resolve()) and path.is_file() and not path.is_symlink(), 'unsafe source path')
    return path


def verify_package(package, card=None):
    package = Path(package).resolve()
    card = load((package / 'record.json').read_bytes()) if card is None else card
    require((card['schema_version'], card['experiment_id'], card['package_id'], card['verification']['profile'])
            == ('0.3.0', 'scitt-receipt-boundary-001', 'pkg-001', 'scitt-receipt-boundary-v1'), 'profile/card identity')
    require(card['status']['independent_reproduction'] == 'not-performed', 'independence scope changed')
    require({'git-commit:' + WORKSPACE_COMMIT, 'git-commit:' + EMULATOR_COMMIT, 'sha256:' + RECEIPT_SHA256}.issubset(
        {p['identity'] for p in card['source_pins']}), 'required source pins absent')
    raw = (package / 'evidence/SOURCE-MANIFEST.json').read_bytes()
    require(sha(raw) == SOURCE_MANIFEST_SHA256, 'source inventory differs from reviewed pin')
    source = load(raw)
    require(source['source']['commit'] == WORKSPACE_COMMIT, 'source commit')
    expected = {}
    for row in source['files']:
        path = checked_path(package, row['path'])
        require(row['path'] not in expected and row['path'].startswith('payload/'), 'source inventory path')
        data = path.read_bytes()
        require(len(data) == row['bytes'] and sha(data) == row['sha256'], 'source bytes differ: ' + row['path'])
        expected[row['path']] = row['sha256']
    actual = {p.relative_to(package).as_posix() for p in (package / 'payload').rglob('*') if p.is_file()}
    require(set(expected) == actual and len(expected) == 31, 'frozen payload file set')
    require(card['payload']['regular_files'] == 31 and card['payload']['path'] == 'payload', 'payload/card mismatch')
    archive = checked_path(package, card['artifact']['path'])
    raw = archive.read_bytes()
    require(sha(raw) == ARCHIVE_SHA256 == source['archive']['sha256'] == card['artifact']['sha256']
            and len(raw) == card['artifact']['bytes'] == source['archive']['bytes'], 'archive identity')
    with zipfile.ZipFile(archive) as z:
        names = sorted(z.namelist())
        require(names == sorted(p[len('payload/'):] for p in expected), 'archive member set')
        for name in names:
            require(sha(z.read(name)) == expected['payload/' + name], 'archive member differs from payload: ' + name)
    require({p.name for p in archive.parent.iterdir()} == {archive.name}, 'archive directory file set')
    # Receipt material and expectations, all read-only.
    sums = dict(line.split('  ', 1)[::-1] for line in (package / 'payload/artifacts/SHA256SUMS.txt').read_text().splitlines() if line.strip())
    require(sums.get('receipt.cbor') == RECEIPT_SHA256 == sha((package / 'payload/artifacts/receipt.cbor').read_bytes())
            and sums.get('signed-statement.cose') == STATEMENT_SHA256 == sha((package / 'payload/artifacts/signed-statement.cose').read_bytes()),
            'receipt or statement bytes differ from the recorded digests')
    delivered = dict(line.split('  ', 1)[::-1] for line in (package / 'payload/expectations/DELIVERED-SHA256SUMS.txt').read_text().splitlines() if line.strip())
    for cid in CASES:
        require(delivered.get(f'expected/{cid}.json') == sha((package / f'payload/expectations/{cid}.json').read_bytes()), 'frozen expectation differs from delivered digest: ' + cid)
        exp = load((package / f'payload/expectations/{cid}.json').read_bytes())
        require(exp['id'] == cid and len(exp['expected']) == 20, 'expectation shape: ' + cid)
    for name in ('DERIVATION.md', 'AMBIGUITIES.json'):
        require(delivered.get(name) == sha((package / 'payload/expectations' / name).read_bytes()), 'delivered file differs: ' + name)
    comparison = load((package / 'payload/comparison.json').read_bytes())
    require(set(comparison['cases']) == set(CASES) and all(
        comparison['cases'][c]['wexp_ref_equals_expected'] is True and comparison['cases'][c]['wexp_check_equals_expected'] is True for c in CASES),
        'recorded workspace comparison is not 4/4 for both appraisers')
    result = {'status': 'PASS_PACKAGE_EVIDENCE', 'payload_files': 31, 'archive_members': len(names),
              'cases': 4, 'workspace_run_equal_both_engines': True, 'package_run_checked': False,
              'new_experiment_execution_performed': False, 'independent_authentication_of_execution': False}
    if card['status']['execution'] == 'local-run-completed':
        record = load((package / 'evidence/RUN-RECORD.json').read_bytes())
        package_comparison = load((package / 'evidence/comparison.json').read_bytes())
        require(record['payload_archive_sha256'] == ARCHIVE_SHA256 and record['new_experiment_execution_performed'] is True, 'package run record scope')
        require(set(package_comparison['cases']) == set(CASES) and all(
            package_comparison['cases'][c]['wexp_ref_equals_expected'] is True and package_comparison['cases'][c]['wexp_check_equals_expected'] is True for c in CASES),
            'package run comparison is not 4/4 for both appraisers')
        require(card['status']['comparison'] == 'no-local-decision-difference' and card['verification']['implementation_execution_performed'] is True, 'card status/run disagreement')
        result.update(package_run_checked=True, package_run_equal_both_engines=True)
    else:
        require(card['status']['execution'] == 'not-run' and card['status']['comparison'] == 'not-evaluated', 'card status before the package run')
    require(not any(p.is_symlink() for p in package.rglob('*')), 'package contains symlink')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, default=ROOT / REL)
    args = parser.parse_args()
    try:
        print(json.dumps(verify_package(args.package), sort_keys=True, indent=2))
        return 0
    except (OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile) as exc:
        print(json.dumps({'status': 'REFUSED', 'error': str(exc)}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
