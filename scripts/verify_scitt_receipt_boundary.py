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
RUN_RECORD_SHA256 = '3c83c3b2925c723a38780893b39e387320fdcf2de27d18e078e4f23ea0109b63'
PACKAGE_COMPARISON_SHA256 = 'd6b39595efb3a989d4faafc04045563e9f47e59c6595f10359a7f9f92fa7b5cd'
WEXP_REF_COMMIT = '56289024c9ee748111f1f1d4f42728ffe04d8d69'
WEXP_CHECK_COMMIT = '25ec856e053d8ab40ed60bb88b70c84768d45e34'
# External reproduction of the mandatory route (read-only checks and repeated appraisal), card revision 6.
# `performed` is admitted only while every one of these files is present and byte-identical.
EXTERNAL_REPRODUCTION_DIR = 'evidence/external-reproduction-20261110-lemonnier'
EXTERNAL_REPRODUCTION_FILES = {
    'EVIDENCE-INDEX.json': 'da5523fed01302f52cb42e219d3db9497ebf879e3f4d97d0006cf7ec7b0ee5c8',
    'NOTE.md': 'bfa975d5bdbd44bd3e79c8f48d4ad4c89ee75a19ab0c9068e465ffb03b0a82ed',
    'artifacts-42801235872.json': '244563f989470892c537c9a4622920af0d228ee4528f7d00c64a06d6cd95856c',
    'artifacts-42801386609.json': '244563f989470892c537c9a4622920af0d228ee4528f7d00c64a06d6cd95856c',
    'corpus-comparison.extracted-from-log.json': '294f4cdc047994b838ede57d655beab8ec8ef3c05342903cc62d8884e1a0c9ab',
    'extract_comparison_from_log.py': 'c22c8beed29e122e48f77a6a2aa103a1c0ba041be3d64097af96e12d37b25374',
    'job-129778987815.log': '657b3160c2632ab5d88b887e81d333d6d6b61b24b3f4a162f465495d86cebd87',
    'job-129778988112.log': '1322da7a4757251d73e5a999baebd1c46510be2c4448086a4f4f26da3cb9eb71',
    'job-129779506135.log': 'd694dd4a39e2d5dc782b6b27d8e7297d881e0fdca1a2f3d38c7f08ab3028adc4',
    'job-129779506462.log': '4032761fc7b17acace6599d7dbd0fd57b2cbc3474e8f1e7cd0c6ca1a19f406f7',
    'pkg-001-comparison.extracted-from-log.json': '166dd11e838d93799a1a3c501b6d97698477f5a955796a4e0a68af6a48f82907',
    'run-42801235872.json': '50d36d7bfbe3e42fac2eed51560a7c2897cb936ba0209842d2b0f7a651a2c701',
    'run-42801386609.json': 'e3628df1cf9d12a823c4b1d7dfc3afac5e5fdb9ff8203e8fd564cce2bea5d865',
    'workflow-f57ea8bf30b88a4f6d8628d6ed9e7588561830ac.yml': '4c31d99b316e53cddcc16f6fc6d19361376ab85ca05ddc5273b910c39add92cc',
    'workflow-f661d39f7d9191f536ea09b7f7c4bbcc70af6128.yml': 'a1d7f50d18694887748ab832bda2d65a37cb4b89b8959b3ba03936f9df682d04',
}
EXTERNAL_REPRODUCTION_COMPARISON = 'pkg-001-comparison.extracted-from-log.json'
SET_FIELDS = {'qualifiers', 'profile_identifiers', 'basis_refs', 'reasons', 'limitations', 'base_findings',
              'qualifier_findings', 'recorder_relations', 'counter_evidence', 'evaluation_scope',
              'profile_evaluation_gaps', 'inherited_limitations', 'fatal_conditions', 'affected_claims',
              'fatal_reasons', 'substantive_reasons', 'evaluation_gaps', 'evaluation_gap_entries',
              'supported_claims', 'maximal_supported_claims', 'support_entries', 'support_relations'}
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


def encoded(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(',', ':'), allow_nan=False)


def logical(value, field=None):
    if type(value) is dict:
        return {key: logical(item, key) for key, item in value.items()}
    if type(value) is list:
        items = [logical(item) for item in value]
        return sorted(items, key=encoded) if field in SET_FIELDS else items
    return value


def same(left, right):
    # Harness set semantics: pure data comparison, Booleans distinct from numbers, null distinct from absent.
    return encoded(logical(left)) == encoded(logical(right))


def comparison_equal(comparison, package):
    # Re-derive every equality from the saved observed results and the frozen expectations; flags are not trusted.
    for cid in CASES:
        expected = load((package / f'payload/expectations/{cid}.json').read_bytes())['expected']
        row = comparison['cases'][cid]
        for engine in ('wexp_ref', 'wexp_check'):
            require(row[f'{engine}_equals_expected'] is True and same(row[f'{engine}_observed'], expected),
                    f'saved {engine} result for {cid} does not equal the frozen expectation')


def checked_path(root, name):
    parts = name.split('/')
    require(bool(name) and not name.startswith('/') and '\\' not in name
            and all(p not in ('', '.', '..') for p in parts), 'noncanonical path')
    path = root.joinpath(*parts)
    require(path.resolve().is_relative_to(root.resolve()) and path.is_file() and not path.is_symlink(), 'unsafe source path')
    return path


def verify_external_reproduction(package):
    # The status may say `performed` only with the pinned external evidence; a bare label is refused.
    directory = package / EXTERNAL_REPRODUCTION_DIR
    require(directory.is_dir() and not directory.is_symlink(), 'independence scope changed: external reproduction evidence absent')
    present = {p.name for p in directory.iterdir()}
    for name, digest in EXTERNAL_REPRODUCTION_FILES.items():
        require(name in present, 'independence scope changed: external reproduction evidence absent: ' + name)
        path = checked_path(package, EXTERNAL_REPRODUCTION_DIR + '/' + name)
        require(sha(path.read_bytes()) == digest, 'independence scope changed: external reproduction evidence differs: ' + name)
    require(present == set(EXTERNAL_REPRODUCTION_FILES), 'independence scope changed: external reproduction file set')
    external = load((directory / EXTERNAL_REPRODUCTION_COMPARISON).read_bytes())
    require(set(external['cases']) == set(CASES), 'external reproduction comparison case set')
    comparison_equal(external, package)


def verify_package(package, card=None):
    package = Path(package).resolve()
    card = load((package / 'record.json').read_bytes()) if card is None else card
    require((card['schema_version'], card['experiment_id'], card['package_id'], card['verification']['profile'])
            == ('0.3.0', 'scitt-receipt-boundary-001', 'pkg-001', 'scitt-receipt-boundary-v1'), 'profile/card identity')
    external = card['status']['independent_reproduction']
    require(external in ('not-performed', 'performed'), 'independence scope changed')
    if external == 'performed':
        verify_external_reproduction(package)
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
    require(set(comparison['cases']) == set(CASES), 'recorded workspace comparison case set')
    comparison_equal(comparison, package)
    result = {'status': 'PASS_PACKAGE_EVIDENCE', 'payload_files': 31, 'archive_members': len(names),
              'cases': 4, 'workspace_run_equal_both_engines': True, 'package_run_checked': False,
              'new_experiment_execution_performed': False, 'independent_authentication_of_execution': False}
    if card['status']['execution'] == 'local-run-completed':
        record_raw = (package / 'evidence/RUN-RECORD.json').read_bytes()
        comparison_raw = (package / 'evidence/comparison.json').read_bytes()
        require(sha(record_raw) == RUN_RECORD_SHA256, 'package run record differs from reviewed pin')
        require(sha(comparison_raw) == PACKAGE_COMPARISON_SHA256, 'package run comparison differs from reviewed pin')
        record = load(record_raw)
        package_comparison = load(comparison_raw)
        require(record['payload_archive_sha256'] == ARCHIVE_SHA256 and record['new_experiment_execution_performed'] is True
                and record['comparison_output_sha256'] == PACKAGE_COMPARISON_SHA256
                and record['engines']['wexp_ref']['commit'] == WEXP_REF_COMMIT
                and record['engines']['wexp_check']['commit'] == WEXP_CHECK_COMMIT, 'package run record scope')
        require({'git-commit:' + WEXP_REF_COMMIT, 'git-commit:' + WEXP_CHECK_COMMIT}.issubset({p['identity'] for p in card['source_pins']}), 'appraiser pins absent from card')
        require(set(package_comparison['cases']) == set(CASES), 'package run comparison case set')
        comparison_equal(package_comparison, package)
        require(card['status']['comparison'] == 'no-local-decision-difference' and card['verification']['implementation_execution_performed'] is True, 'card status/run disagreement')
        result.update(package_run_checked=True, package_run_equal_both_engines=True)
    else:
        require(card['status']['execution'] == 'not-run' and card['status']['comparison'] == 'not-evaluated', 'card status before the package run')
    result['external_reproduction_checked'] = card['status']['independent_reproduction'] == 'performed'
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
