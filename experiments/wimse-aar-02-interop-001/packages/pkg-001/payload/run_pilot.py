"""Replay pinned AAR corpora, bounded mapping, staged receiver and baseline.

No network or installation. Expects Python >=3.10. Output is new evidence:
--out must point outside the package's retained results directory on replays.
--compare compares semantic results with a previously retained run.
"""
from __future__ import annotations
import argparse
import base64
from concurrent.futures import ThreadPoolExecutor
import copy
import datetime
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parent
ENV = {k: v for k, v in os.environ.items() if k not in {'PYTHONPATH', 'PYTHONHOME'}}
ENV.update(PYTHONDONTWRITEBYTECODE='1', PYTHONNOUSERSITE='1')
OBS = {'base': 'observation', 'qualifiers': []}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encode(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encode(value))


def invoke(arguments, cwd):
    started = time.monotonic()
    completed = subprocess.run([sys.executable] + [str(x) for x in arguments], cwd=cwd,
        env=ENV, capture_output=True, timeout=30)
    if completed.returncode != 0:
        raise RuntimeError('command failed: ' + str(arguments[0]) + '\n' + completed.stderr.decode(errors='replace') + completed.stdout.decode(errors='replace'))
    value = json.loads(completed.stdout)
    return value, completed.stdout, {'returncode': completed.returncode,
        'stdout_sha256': sha(completed.stdout), 'stderr': completed.stderr.decode(),
        'elapsed_seconds': round(time.monotonic() - started, 6)}


def public_case(revision, entry):
    source = ROOT / 'vendor' / ('aar' + revision) / 'vectors-agent-audit-record' / entry['file']
    # N1/N2 have no mandatory verdict in the corpus; both readings stay open.
    allowed = [entry['expected']['verdict']] if entry.get('expected', {}).get('verdict') else ['valid', 'indeterminate']
    return {'id': 'aar' + revision + '-' + entry['draftId'], 'group': 'aar' + revision,
        'source': source, 'policy': ROOT / 'policies' / ('aar' + revision + '.json'),
        'allowed_native_verdicts': allowed, 'expected_dispatch_failure': None,
        'authority': {'kind': 'published-vector', 'draft_id': entry['draftId'], 'manifest_entry': entry}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--compare', type=Path)
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()
    out = args.out.resolve()
    if out.exists() and any(out.iterdir()):
        raise SystemExit('Refusing to overwrite nonempty evidence directory; choose a new --out.')
    out.mkdir(parents=True, exist_ok=True)
    observed_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    cases = []
    manifests = {}
    for rev in ['01', '02']:
        manifest = json.loads((ROOT / 'vendor' / ('aar' + rev) / 'vectors-agent-audit-record/MANIFEST.json').read_bytes())
        manifests[rev] = manifest
        cases.extend(public_case(rev, entry) for entry in manifest['vectors'])
    local_manifest = json.loads((ROOT / 'fixtures/local-manifest.json').read_bytes())
    for entry in local_manifest['cases']:
        cases.append({'id': entry['id'], 'group': 'local', 'source': ROOT / entry['source'],
            'policy': ROOT / entry['policy'], 'allowed_native_verdicts': [entry['expected_native_verdict']],
            'expected_dispatch_failure': None, 'authority': entry})
    def vector(rev, vector_id):
        entry = next(e for e in manifests[rev]['vectors'] if e['draftId'] == vector_id)
        return ROOT / 'vendor' / ('aar' + rev) / 'vectors-agent-audit-record' / entry['file']
    for source_rev, source_id, selected, verdict, dispatch in [
        ('01', 'A1', '02', 'malformed', None),
        ('01', 'A2', '02', 'malformed', None),
        ('02', 'A10', '01', 'valid', 'revision02-members-in-01-profile'),
        ('02', 'A11', '01', 'valid', 'revision02-members-in-01-profile'),
        ('02', 'EV1', '01', 'valid', 'revision02-members-in-01-profile'),
        ('02', 'OV1', '01', 'valid', 'revision02-members-in-01-profile'),
    ]:
        cases.append({'id': 'compat-' + source_rev + '-' + source_id + '-as-' + selected,
            'group': 'compatibility', 'source': vector(source_rev, source_id),
            'policy': ROOT / 'policies' / ('aar' + selected + '.json'),
            'allowed_native_verdicts': [verdict], 'expected_dispatch_failure': dispatch,
            'authority': {'kind': 'explicit-cross-revision-test', 'source_revision': source_rev,
                          'source_vector': source_id, 'selected_revision': selected}})
    template = json.loads((ROOT / 'policies/aar02.json').read_bytes())
    for ident, change, code in [
        ('missing-revision', {'carrier_revision': None}, 'carrier-revision-not-selected'),
        ('unknown-revision', {'carrier_revision': '03'}, 'unsupported-carrier-revision'),
        ('wrong-specification', {'specification_sha256': '0' * 64}, 'carrier-specification-mismatch'),
    ]:
        policy = dict(template, **change)
        path = out / 'test-inputs' / (ident + '-policy.json')
        save(path, policy)
        cases.append({'id': ident, 'group': 'compatibility', 'source': vector('02', 'A10'),
            'policy': path, 'allowed_native_verdicts': ['not-run'], 'expected_dispatch_failure': code,
            'authority': {'kind': 'receiver-owned-dispatch-policy'}})

    measurements = []
    with tempfile.TemporaryDirectory(prefix='aar-pilot-replay-') as tmp:
        temp = Path(tmp)
        stage = temp / 'recipient'
        shutil.copytree(ROOT / 'consumer', stage / 'consumer', ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        for rev in ['01', '02']:
            shutil.copytree(ROOT / 'vendor' / ('aar' + rev) / 'packaging',
                stage / 'vendor' / ('aar' + rev) / 'packaging',
                ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        runtime_files = sorted(p for p in stage.rglob('*') if p.is_file())
        runtime_manifest = [{'path': str(p.relative_to(stage)), 'sha256': sha(p.read_bytes()), 'bytes': p.stat().st_size} for p in runtime_files]
        isolation = {'method': 'Actual copied recipient distribution and fresh subprocess per call/revision',
            'files': runtime_manifest, 'producer_present': (stage / 'producer.py').exists(),
            'core_evaluator_present': (stage / 'vendor/core_hof').exists(),
            'normalized_inputs_delivered': False, 'corpus_manifests_delivered': False,
            'os_access_sandbox': False, 'network_enforcement': False,
            'scope': 'Process/dependency separation within this one assistant-coordinated experiment; not an external team, deployment or adversarial OS sandbox.'}
        assert not isolation['producer_present'] and not isolation['core_evaluator_present']
        save(out / 'recipient-distribution.json', isolation)

        def exercise(case):
            ident = case['id']
            # The two worlds run sequentially through the same delivery paths.
            # The descriptive world id stays in harness-only observations.
            delivery_id = 'trusted-producer-input' if case.get('blind_world') else ident
            folder = temp / 'work' / delivery_id
            folder.mkdir(parents=True, exist_ok=True)
            source_bytes, policy_bytes = case['source'].read_bytes(), case['policy'].read_bytes()
            normalized = folder / 'normalized.json'
            produced, raw_output, process_a = invoke([ROOT / 'producer.py', '--source', case['source'],
                '--policy', case['policy'], '--normalized-out', normalized], ROOT)
            incoming = stage / 'incoming' / delivery_id
            incoming.mkdir(parents=True, exist_ok=True)
            (incoming / 'source.json').write_bytes(source_bytes)
            (incoming / 'policy.json').write_bytes(policy_bytes)
            (incoming / 'output.json').write_bytes(raw_output)
            baseline, raw_baseline, process_b = invoke([stage / 'consumer/native_baseline.py',
                '--source', incoming / 'source.json', '--policy', incoming / 'policy.json'], stage)
            recipient, raw_recipient, process_c = invoke([stage / 'consumer/receive_output.py',
                '--source', incoming / 'source.json', '--policy', incoming / 'policy.json',
                '--output', incoming / 'output.json'], stage)
            checks = {
                'native_matches_source_expectation': produced['native']['verdict'] in case['allowed_native_verdicts'],
                'receiver_accepts_actual_output': recipient['output_validation'] == 'accepted',
                'receiver_and_native_decisions_equal': recipient['decision'] == baseline['decision'],
                'no_execution_inference': recipient['decision']['execution_established'] is False,
                'no_authorization_inference': recipient['decision']['authorization_established'] is False,
                'no_human_inference': recipient['decision']['human_participation_established'] is False,
            }
            inp = json.loads(normalized.read_bytes())
            if produced['native']['verdict'] != 'valid' or case['expected_dispatch_failure']:
                checks['no_appraisal_on_input_failure'] = produced['appraisal'] is None and inp is None and produced['status'] == 'mapping-failure'
                if case['expected_dispatch_failure']:
                    checks['exact_dispatch_failure'] = produced['mapping_failure']['code'] == case['expected_dispatch_failure']
            else:
                appraisal = produced['appraisal']
                checks['bounded_core_result'] = (produced['status'] == 'mapped' and appraisal['verdict'] == 'downgrade'
                    and appraisal['asserted_claim_supported'] is False and appraisal['supported_claims'] == [OBS]
                    and appraisal['maximal_supported_claims'] == [OBS] and appraisal['fatal_reasons'] == [])
            source_path = str(case['source'].relative_to(ROOT))
            policy_path = str(case['policy'].relative_to(ROOT)) if case['policy'].is_relative_to(ROOT) else 'test-inputs/' + case['policy'].name
            result = {'id': ident, 'group': case['group'], 'source': source_path, 'source_sha256': sha(source_bytes),
                'policy': policy_path, 'policy_sha256': sha(policy_bytes), 'authority': case['authority'],
                'producer_output': produced, 'normalized_input': inp,
                'native_baseline': baseline, 'wexp_recipient': recipient, 'checks': checks, 'passed': all(checks.values())}
            return result, {'id': ident, 'delivery_id': delivery_id,
                'producer': process_a, 'native_baseline': process_b, 'recipient': process_c}

        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            exercised = list(pool.map(exercise, cases))
        results = [r for r, _ in exercised]
        measurements.extend(m for _, m in exercised)
        by_id = {r['id']: r for r in results}
        save(out / 'input-expectations.json', [{k: v for k, v in row.items() if k in {'id', 'group', 'source', 'source_sha256', 'policy', 'policy_sha256', 'authority'}} for row in results])
        for group in ['aar01', 'aar02', 'local', 'compatibility']:
            save(out / (group + '-results.json'), [r for r in results if r['group'] == group])

        # Explicit differences the common binary native verdict cannot convey.
        a2, a10 = by_id['aar02-A2'], by_id['aar02-A10']
        pair_checks = {
            'same_decision_deny': a2['producer_output']['facts']['decision_reported'] == a10['producer_output']['facts']['decision_reported'] == 'deny',
            'same_agreement': a2['producer_output']['facts']['agreement'] == a10['producer_output']['facts']['agreement'] == 'agree',
            'different_evaluation_status': a2['wexp_recipient']['decision']['evaluation_status'] == 'evaluated' and a10['wexp_recipient']['decision']['evaluation_status'] == 'not-evaluated',
            'different_recipient_classification': a2['wexp_recipient']['decision']['classification'] != a10['wexp_recipient']['decision']['classification'],
            'unavailable_input_retained': a10['wexp_recipient']['decision']['unavailable_input'] == ['standing-source'],
            'carrier_and_mapper_evaluation_are_distinct': a10['producer_output']['appraisal']['evaluation_scope']['carrier-mapping'] == 'evaluated',
            'historical_A1_is_exact_new_EV3': vector('01', 'A1').read_bytes() == vector('02', 'EV3').read_bytes(),
        }
        save(out / 'distinction-checks.json', pair_checks)

        # Output-specific negative controls; native baseline has no such output
        # to trust. Rejection here is not claimed as extra truth detection.
        mutations = []
        def mutate(label, base_id, operation):
            value = copy.deepcopy(by_id[base_id]['producer_output'])
            operation(value)
            mutations.append((label, base_id, encode(value)))
        mutate('source-version', 'aar02-A10', lambda o: o['source'].update(carrier_revision='01'))
        mutate('source-digest', 'aar02-A10', lambda o: o['source'].update(record_sha256='0' * 64))
        mutate('policy-digest', 'aar02-A10', lambda o: o['context'].update(policy_sha256='0' * 64))
        mutate('profile-digest', 'aar02-A10', lambda o: o['context'].update(profile_sha256='0' * 64))
        mutate('evaluation-laundering', 'aar02-A10', lambda o: o['facts']['evaluation'].update(status='evaluated', unavailable_input=[]))
        mutate('lost-unavailable-input', 'aar02-A10', lambda o: o['facts']['evaluation'].update(unavailable_input=[]))
        mutate('oversight-human-upgrade', 'aar02-A11', lambda o: o['facts']['oversight'].update(human_participation='established'))
        mutate('oversight-authority-upgrade', 'aar02-A11', lambda o: o['facts']['oversight'].update(authority='established'))
        mutate('false-core-accept', 'L19-trusted-wrong-effect', lambda o: o['appraisal'].update(verdict='accept', asserted_claim_supported=True, supported_claims=[{'base': 'execution', 'qualifiers': ['IV']}]))
        mutate('lost-limitations', 'aar02-A11', lambda o: o['appraisal'].update(inherited_limitations=[]))
        mutate('lost-gap', 'aar02-A10', lambda o: o['appraisal'].update(evaluation_gaps=[], evaluation_gap_entries=[]))
        mutate('foreign-target', 'aar02-A10', lambda o: o['appraisal'].update(target='urn:foreign:target'))
        mutate('wrong-basis', 'aar02-A10', lambda o: o['appraisal']['support_entries'][0].update(basis_refs=['urn:sha256:' + '0' * 64]))
        mutate('fake-appraisal-on-EV3', 'aar02-EV3', lambda o: o.update(status='mapped', appraisal=by_id['aar02-A2']['producer_output']['appraisal']))
        valid_raw = encode(by_id['aar02-A10']['producer_output'])
        mutations.append(('duplicate-output-member', 'aar02-A10', valid_raw.replace(b'{', b'{"format":"duplicate",', 1)))
        mutations.append(('nonfinite-output-value', 'aar02-A10', valid_raw.replace(b'"status": "mapped"', b'"status": NaN')))
        mutation_results = []
        for label, base_id, raw in mutations:
            path = stage / 'incoming' / base_id
            output_file = path / ('mutation-' + label + '.json')
            output_file.write_bytes(raw)
            recipient, stdout, process = invoke([stage / 'consumer/receive_output.py', '--source', path / 'source.json',
                '--policy', path / 'policy.json', '--output', output_file], stage)
            passed = recipient['output_validation'] == 'rejected' and recipient['decision']['admission'] == 'quarantine'
            mutation_results.append({'id': label, 'base_case': base_id, 'input_utf8': raw.decode(),
                'input_sha256': sha(raw), 'recipient_result': recipient, 'passed': passed})
            measurements.append({'id': 'mutation-' + label, 'recipient': process})
        save(out / 'output-mutation-results.json', mutation_results)

        oracle = json.loads((ROOT / 'fixtures/trusted-producer-oracle.json').read_bytes())
        worlds = []
        for world in oracle['worlds']:
            file = temp / ('world-' + world['id']) / 'ledger.txt'
            file.parent.mkdir()
            file.write_bytes(oracle['before_utf8'].encode())
            before = file.read_bytes()
            # Closed test operation, not a production actor or safety boundary.
            if world['operation'] == 'write':
                file.write_bytes(oracle['claimed_after_utf8'].encode())
            elif world['operation'] != 'no-op':
                raise AssertionError('unknown test operation')
            after = file.read_bytes()
            # Repeat participant runs with the exact same inputs, withholding
            # world id and observed endpoint states from both paths.
            base_case = next(c for c in cases if c['id'] == 'L19-trusted-wrong-effect')
            copy_case = dict(base_case, id='world-' + world['id'], blind_world=True)
            observed, process = exercise(copy_case)
            measurements.append(process)
            worlds.append({'world': world['id'], 'operation_invoked': world['operation'],
                'participant_delivery_id': process['delivery_id'],
                'before_utf8': before.decode(), 'after_utf8': after.decode(),
                'before_sha256': sha(before), 'after_sha256': sha(after),
                'claimed_after_matches_local_endpoint': after.decode() == oracle['claimed_after_utf8'],
                'record_sha256': observed['source_sha256'], 'policy_sha256': observed['policy_sha256'],
                'producer_output': observed['producer_output'], 'wexp_recipient': observed['wexp_recipient'],
                'native_baseline': observed['native_baseline']})
        oracle_checks = {
            'control_endpoint_matches_reported_effect': worlds[0]['claimed_after_matches_local_endpoint'],
            'false_report_endpoint_does_not_match': not worlds[1]['claimed_after_matches_local_endpoint'],
            'both_signed_records_native_valid': all(w['producer_output']['native']['verdict'] == 'valid' for w in worlds),
            'same_participant_inputs': worlds[0]['record_sha256'] == worlds[1]['record_sha256'] and worlds[0]['policy_sha256'] == worlds[1]['policy_sha256'],
            'same_participant_delivery_id': worlds[0]['participant_delivery_id'] == worlds[1]['participant_delivery_id'] == 'trusted-producer-input',
            'same_wexp_output_in_both_worlds': worlds[0]['producer_output'] == worlds[1]['producer_output'],
            'same_wexp_receiver_decision': worlds[0]['wexp_recipient']['decision'] == worlds[1]['wexp_recipient']['decision'],
            'same_native_decision': worlds[0]['native_baseline']['decision'] == worlds[1]['native_baseline']['decision'],
            'no_execution_inference_in_either_route': all(not w[route]['decision']['execution_established'] for w in worlds for route in ['wexp_recipient', 'native_baseline']),
        }
        save(out / 'trusted-producer-results.json', {'oracle': oracle, 'worlds': worlds, 'checks': oracle_checks,
            'external_counter_evidence_supplied': False,
            'conclusion': 'Both routes preserve the support limit. Neither detects the coordinated false fact from identical signed bytes alone. No WEXP superiority in truth detection is established.'})

    native_runs = []
    for rev in ['01', '02']:
        result, raw, process = invoke([ROOT / 'probe_native.py', '--revision', rev], ROOT)
        native_runs.append(result)
        measurements.append({'id': 'native-corpus-' + rev, 'process': process})
    save(out / 'native-corpus-results.json', native_runs)
    # Semantic fingerprint excludes timestamps, paths and timing observations.
    summary = {
        'cases': [{'id': r['id'], 'source_sha256': r['source_sha256'], 'policy_sha256': r['policy_sha256'],
                   'checks': r['checks'], 'native': r['producer_output']['native'],
                   'mapping_status': r['producer_output']['status'],
                   'decision': r['wexp_recipient']['decision']} for r in results],
        'distinctions': pair_checks, 'output_mutations': [{'id': r['id'], 'passed': r['passed'], 'errors': r['recipient_result']['errors']} for r in mutation_results],
        'trusted_producer': oracle_checks,
        'native_corpora': [{'revision': r['revision'], 'count': len(r['vectors']), 'judge_ok': r['judge_ok'], 'corpus_digest': r['corpus_digest']} for r in native_runs],
    }
    save(out / 'semantic-results.json', summary)
    passed = (all(r['passed'] for r in results) and all(pair_checks.values()) and all(r['passed'] for r in mutation_results)
              and all(oracle_checks.values()) and all(r['judge_ok'] and all(v['verdict_matches'] for v in r['vectors']) for r in native_runs))
    comparison = None
    if args.compare:
        comparison = json.loads(args.compare.read_bytes()) == summary
        passed = passed and comparison
    execution_sources = [{'path': str(p.relative_to(ROOT)), 'sha256': sha(p.read_bytes())}
        for p in sorted(ROOT.rglob('*.py')) if '__pycache__' not in p.parts and 'sources' not in p.relative_to(ROOT).parts]
    observation = {'observed_at_utc': observed_at, 'finished_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'runtime': {'python': sys.version, 'platform': platform.platform()}, 'workers': args.workers,
        'execution_source_files': execution_sources, 'profile_sha256': sha((ROOT / 'profile.json').read_bytes()),
        'local_execution': True, 'external_team_reproduction': False, 'network_required': False,
        'semantic_results_sha256': sha((out / 'semantic-results.json').read_bytes()),
        'counts': {'pipeline_cases': len(results), 'pipeline_passed': sum(r['passed'] for r in results),
                   'published_native_vectors': sum(len(r['vectors']) for r in native_runs),
                   'local_fixtures': len(local_manifest['cases']), 'output_mutations': len(mutation_results),
                   'output_mutations_rejected': sum(r['passed'] for r in mutation_results), 'controlled_worlds': len(worlds)},
        'compare_equal': comparison, 'passed': passed,
        'measurements': measurements,
        'timing_limit': 'Per-process wall times are execution observations, not a performance benchmark or cost comparison.'}
    save(out / 'execution-observation.json', observation)
    print(json.dumps({'passed': passed, 'counts': observation['counts'], 'compare_equal': comparison,
                      'semantic_results_sha256': observation['semantic_results_sha256']}, indent=2))
    if not passed:
        for r in results:
            if not r['passed']:
                print('FAIL', r['id'], {k: v for k, v in r['checks'].items() if not v}, r['wexp_recipient'].get('errors'), file=sys.stderr)
        for r in mutation_results:
            if not r['passed']:
                print('FAIL mutation', r['id'], file=sys.stderr)
        raise SystemExit(1)


if __name__ == '__main__':
    main()
