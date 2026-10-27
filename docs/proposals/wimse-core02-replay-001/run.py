"""Precommitted 130-case migration trial; outputs outside immutable inputs."""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from common import PROFILE, PROFILE_SHA, load

HERE = Path(__file__).resolve().parent
PAYLOAD = 'experiments/wimse-aar-02-interop-001/packages/pkg-001/payload'


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def write(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, sort_keys=True, ensure_ascii=True, indent=2, allow_nan=False)
        stream.write('\n')


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], text=True).strip()


def pinned(root, commit):
    if git(root, 'rev-parse', 'HEAD') != commit:
        raise ValueError('wrong checkout commit: ' + str(root))
    if git(root, 'status', '--porcelain', '--untracked-files=normal'):
        raise ValueError('unclean checkout: ' + str(root))


def within(root, name):
    path = (root / name).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError('unavailable or escaping pinned input: ' + name)
    return path


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--legacy', type=Path, required=True)
    p.add_argument('--ref', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    legacy, ref, out = a.legacy.resolve(), a.ref.resolve(), a.out.resolve()
    if any(out.is_relative_to(x) for x in (legacy, ref, HERE)):
        raise SystemExit('Output must be outside the input trees')
    out.mkdir(parents=True, exist_ok=False)
    write(out / 'START.json', {'time': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'python': platform.python_version(), 'optimized': bool(sys.flags.optimize),
        'profile_sha256': PROFILE_SHA, 'status': 'STARTED_NOT_A_RESULT'})
    pinned(legacy, PROFILE['legacy_commit']); pinned(ref, PROFILE['ref_commit'])
    code = ref / 'src/wexp_ref/core02/appraiser.py'
    if digest(code.read_bytes()) != PROFILE['appraiser_sha256']:
        raise ValueError('wrong appraiser bytes')
    payload = legacy / PAYLOAD
    saved = payload / 'results/public-run-001'
    rows = []
    for group in ('aar01', 'aar02', 'local', 'compatibility'):
        rows += load((saved / (group + '-results.json')).read_bytes())
    if len(rows) != PROFILE['expected_cases'] or len({r['id'] for r in rows}) != len(rows):
        raise ValueError('unexpected case inventory')
    env = {k: v for k, v in os.environ.items() if k not in ('PYTHONPATH', 'PYTHONHOME')}
    env.update(PYTHONDONTWRITEBYTECODE='1', PYTHONNOUSERSITE='1')
    observations, errors = [], []
    calls = []
    flags = ['-B'] + (['-O'] if sys.flags.optimize else [])
    def invoke(script, *args):
        command = [sys.executable, *flags, str(script), *map(str, args)]
        proc = subprocess.run(command, env=env, capture_output=True, timeout=40)
        calls.append({'script': Path(script).name, 'returncode': proc.returncode,
            'stdout_sha256': digest(proc.stdout), 'stderr': proc.stderr.decode('utf-8', errors='replace')})
        if proc.returncode:
            raise RuntimeError(f'{Path(script).name}: {proc.returncode}: ' + proc.stderr.decode(errors='replace'))
        return load(proc.stdout)
    with tempfile.TemporaryDirectory(prefix='wexp-core02-recipient-') as temp:
        receiver = Path(temp)
        for name in ('receiver.py', 'common.py', 'profile.json'):
            shutil.copy2(HERE / name, receiver / name)
        write(out / 'recipient-distribution.json', {'files': sorted(p.name for p in receiver.iterdir()),
            'core_present': False, 'producer_present': False,
            'raw_source_and_policy_supplied': True, 'normalized_input_supplied': False,
            'os_sandbox': False, 'external_independence': False})
        for row in rows:
            try:
                source = within(payload, row['source'])
                policy = payload / row['policy']
                policy = within(payload if policy.is_file() else saved, row['policy'])
                if digest(source.read_bytes()) != row['source_sha256'] or digest(policy.read_bytes()) != row['policy_sha256']:
                    raise ValueError('historical input digest differs')
                produced = invoke(HERE / 'producer.py', '--legacy', legacy, '--ref', ref,
                    '--source', source, '--policy', policy)
                delivery = receiver / 'delivery.json'
                delivery.write_text(json.dumps(produced['delivery'], sort_keys=True, allow_nan=False))
                native = invoke(payload / 'consumer/native_baseline.py', '--source', source, '--policy', policy)
                received = invoke(receiver / 'receiver.py', '--legacy', legacy, '--source', source,
                    '--policy', policy, '--delivery', delivery)
                original = row['native_baseline']
                checks = {
                    'native_result_unchanged': native == original,
                    'output_accepted': received['output_validation'] == 'accepted',
                    'same_recipient_decision': native['decision'] == received['decision'],
                    'native_facets_preserved': produced['delivery']['native'] == row['producer_output']['native'] and
                        produced['delivery']['facts'] == row['producer_output']['facts'],
                    'no_appraisal_on_failure': (produced['delivery']['appraisal'] is None) ==
                        (row['producer_output']['appraisal'] is None),
                    'comparator_controls': all(c['passed'] for c in received['controls']),
                    'no_execution_inference': received['decision'].get('execution_established') is False,
                }
                observations.append({'id': row['id'], 'source_sha256': row['source_sha256'],
                    'policy_sha256': row['policy_sha256'], 'producer': produced,
                    'baseline': native, 'receiver': received, 'checks': checks,
                    'passed': all(checks.values())})
            except Exception as exc:
                errors.append({'id': row['id'], 'error': type(exc).__name__ + ': ' + str(exc)})
        # Exercise the recipient entry point with an actual modified delivery.
        sample = next((x for x in observations if x['producer']['delivery']['appraisal'] is not None), None)
        entrypoint_controls = []
        if sample:
            source_row = next(r for r in rows if r['id'] == sample['id'])
            source = within(payload, source_row['source'])
            policy = within(payload, source_row['policy'])
            for label, field in (('source-binding', 'source_sha256'), ('profile-binding', 'profile_sha256')):
                modified = dict(sample['producer']['delivery']); modified[field] = '0' * 64
                (receiver / 'delivery.json').write_text(json.dumps(modified))
                result = invoke(receiver / 'receiver.py', '--legacy', legacy, '--source', source,
                    '--policy', policy, '--delivery', receiver / 'delivery.json')
                entrypoint_controls.append({'id': label, 'passed': result['output_validation'] == 'rejected' and
                    result['decision']['admission'] == 'quarantine'})
    write(out / 'observed.json', observations)
    write(out / 'processes.json', calls)
    write(out / 'errors.json', errors)
    success = (len(observations) == PROFILE['expected_cases'] and not errors and
               all(x['passed'] for x in observations) and len(entrypoint_controls) == 2 and
               all(x['passed'] for x in entrypoint_controls))
    summary = {'status': 'PASS_BOUNDED_MIGRATION' if success else 'FAIL',
      'cases': len(rows), 'completed': len(observations), 'passed': sum(x['passed'] for x in observations),
      'mapped': sum(x['producer']['delivery']['appraisal'] is not None for x in observations),
      'errors': len(errors), 'entrypoint_controls': entrypoint_controls,
      'python': platform.python_version(), 'platform': platform.platform(),
      'optimized': bool(sys.flags.optimize), 'profile_sha256': PROFILE_SHA,
      'legacy_commit': PROFILE['legacy_commit'], 'ref_commit': PROFILE['ref_commit'],
      'observed_sha256': digest((out / 'observed.json').read_bytes()),
      'scope': '130 historical input cases; new bounded Core-02 mapping and source-aware receiver',
      'two_world_operations_repeated': False, 'full_conformance': False,
      'external_independence': False, 'coverage_evaluated': False, 'aac_run': False}
    pinned(legacy, PROFILE['legacy_commit']); pinned(ref, PROFILE['ref_commit'])
    write(out / 'SUMMARY.json', summary)
    print(json.dumps(summary, sort_keys=True))
    return 0 if success else 1


if __name__ == '__main__':
    raise SystemExit(main())
