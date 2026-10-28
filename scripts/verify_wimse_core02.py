#!/usr/bin/env python3
"""Read-only catalog admission of retained WIMSE/Core-02 observations.

SPDX-License-Identifier: MIT
No producer, appraiser, recipient or original experiment is invoked.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REL = 'experiments/wimse-aar-02-interop-001/packages/pkg-002'
SOURCE_MANIFEST_SHA256 = '7c4ede32db16ce0251ef4216757402b3415dddff7c9f88b5bc90ce2f747dc28c'
CHECKER_SHA256 = '20e5e5b1cf6f2fa44706580eaf2b32f23b12f1cd78905e2573c435890880af74'
RECORD_SHA256 = '2a3a0f8a375f7f5eb01419f737502b9f6b35f426f2ee743307799e0cbbe67781'
PRE_RUN = '70d6c5d1fca0843859008c98fd6a57e265ff3f68'
SOURCE = 'c8e04e8959eb8f45fad0f7230b5b4c68e606d9c5'
REF = '56289024c9ee748111f1f1d4f42728ffe04d8d69'
LEGACY = 'b3bce9abd047e41af06ff8aff1d9ead8c6b0ed93'


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
    require(path.resolve().is_relative_to(root.resolve()) and path.is_file()
            and not any(p.is_symlink() for p in [path, *path.parents] if p != root.parent), 'unsafe source path')
    return path


def verify_package(package, card=None):
    package = Path(package).resolve()
    card = load((package / 'record.json').read_bytes()) if card is None else card
    require((card['schema_version'], card['experiment_id'], card['package_id'], card['verification']['profile'])
            == ('0.2.0', 'wimse-aar-02-interop-001', 'pkg-002', 'wimse-core02-migration-v1'), 'profile/card identity')
    require(card['status']['integrity'] == 'verified'
            and card['status']['execution'] == 'local-run-completed'
            and card['status']['comparison'] == 'no-local-decision-difference'
            and card['status']['independent_reproduction'] == 'not-performed'
            and card['verification']['implementation_execution_performed'] is True,
            'recorded-run scope changed')
    require({PRE_RUN, LEGACY, REF, 'sha256:' + RECORD_SHA256}.issubset(
        {p['identity'] for p in card['source_pins']}), 'required source pins absent')
    raw = (package / 'evidence/SOURCE-MANIFEST.json').read_bytes()
    require(sha(raw) == SOURCE_MANIFEST_SHA256, 'source inventory differs from reviewed pin')
    source = load(raw)
    files = source['files']
    expected = set()
    for row in files:
        path = checked_path(package, row['path'])
        require(row['path'] not in expected and row['path'].startswith('payload/'), 'source inventory path')
        expected.add(row['path'])
        data = path.read_bytes()
        require(len(data) == row['bytes'] and sha(data) == row['sha256'], 'source bytes differ: ' + row['path'])
        require(hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest() == row['git_blob'], 'source Git blob')
        require(row['source_commit'] == (SOURCE if row['path'].endswith('/verify_evidence.py') else PRE_RUN), 'source origin')
    actual = {p.relative_to(package).as_posix() for p in (package / 'payload').rglob('*') if p.is_file()}
    require(expected == actual and len(files) == 8, 'frozen source file set')
    require(card['payload']['regular_files'] == 8 and card['payload']['path'] == 'payload', 'payload/card mismatch')
    saved_path = package / 'source-archive/RECORD.json'
    require(sha(saved_path.read_bytes()) == RECORD_SHA256, 'saved record differs from reviewed pin')
    saved = load(saved_path.read_bytes())
    arc = saved['archives'][0]
    require(card['artifact']['path'] == 'source-archive/' + arc['path']
            and card['artifact']['bytes'] == arc['bytes']
            and card['artifact']['sha256'] == arc['sha256'], 'primary artifact/card mismatch')
    expected_archives = {'RECORD.json'} | {a['path'] for a in saved['archives']}
    require({p.name for p in saved_path.parent.iterdir()} == expected_archives, 'archive file set')
    require(not any(p.is_symlink() for p in package.rglob('*')), 'package contains symlink')
    adm = load((package / 'evidence/ADMISSION.json').read_bytes())
    require(adm['new_experiment_execution_performed'] is False
            and adm['case_count_per_run'] == 130 and adm['mapped'] == 35 and adm['unmapped'] == 95
            and adm['source_result_commit'] == SOURCE and adm['pre_run_commit'] == PRE_RUN
            and adm['source_manifest_sha256'] == SOURCE_MANIFEST_SHA256,
            'admission scope or counts')
    # No candidate module is imported until its external byte identity and the
    # entire source inventory have been checked. This module only reads data.
    checker = package / 'payload/verify_evidence.py'
    require(sha(checker.read_bytes()) == CHECKER_SHA256, 'saved-data checker differs from reviewed pin')
    spec = importlib.util.spec_from_file_location('pinned_wimse_saved_evidence', checker)
    require(spec is not None and spec.loader is not None, 'checker loader')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    observed = module.verify(saved_path, RECORD_SHA256)
    require(observed['new_execution'] is False and len(observed['runs']) == 8, 'read-only checker contract')
    return {'status': 'PASS_CATALOG_ADMISSION', 'original_source_commit': PRE_RUN,
            'source_files': 8, 'archives': 4, 'recorded_mode_runs': 8,
            'cases_per_original_run': 130, 'mapped_per_original_run': 35,
            'observed_sha256': saved['observed_sha256_all_eight_mode_runs'],
            'new_experiment_execution_performed': False,
            'independent_authentication_of_execution': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, default=ROOT / REL)
    args = parser.parse_args()
    try:
        print(json.dumps(verify_package(args.package), sort_keys=True, indent=2))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({'status': 'REFUSED', 'error': str(exc)}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
