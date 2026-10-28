"""Read-only checks of saved run-001 bytes; no experiment or Core execution."""
from pathlib import Path
import argparse
import hashlib
import io
import json
import math
import zipfile

FIELDS = {'semantics_version', 'verdict', 'fatal_reasons', 'target', 'asserted_claim',
 'asserted_claim_supported', 'support_entries', 'supported_claims', 'maximal_supported_claims',
 'support_relations', 'boundary_ceiling', 'boundary_grounding', 'recorder_relations',
 'substantive_reasons', 'evaluation_gaps', 'evaluation_gap_entries', 'counter_evidence',
 'inherited_limitations', 'evaluation_context', 'evaluation_scope'}
SETS = {'qualifiers', 'profile_identifiers', 'basis_refs', 'reasons', 'limitations',
 'recorder_relations', 'counter_evidence', 'evaluation_scope', 'inherited_limitations',
 'affected_claims', 'fatal_reasons', 'substantive_reasons', 'evaluation_gaps',
 'evaluation_gap_entries', 'supported_claims', 'maximal_supported_claims',
 'support_entries', 'support_relations'}
CHECKS = {'comparator_controls', 'native_facets_preserved', 'native_result_unchanged',
 'no_appraisal_on_failure', 'no_execution_inference', 'output_accepted', 'same_recipient_decision'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def unique(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'duplicate JSON member')
        result[key] = value
    return result


def finite(text):
    value = float(text)
    require(math.isfinite(value), 'nonfinite JSON number')
    return value


def invalid(text):
    raise ValueError('nonfinite JSON constant')


def load(raw):
    return json.loads(raw, object_pairs_hook=unique, parse_float=finite, parse_constant=invalid)


def encode(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(',', ':'), allow_nan=False)


def logical(value, key=None):
    if type(value) is dict:
        return {k: logical(v, k) for k, v in value.items()}
    if type(value) is list:
        result = [logical(v) for v in value]
        if key in SETS:
            require(len({encode(x) for x in result}) == len(result), 'duplicate set member')
            return sorted(result, key=encode)
        return result
    return value


def verify(record_path, expected_hash):
    raw = record_path.read_bytes()
    require(sha(raw) == expected_hash, 'record digest differs from external pin')
    record = load(raw)
    require(record['schema'] == 'wexp-bounded-migration-evidence/1', 'record schema')
    archives = record['archives']
    require(len(archives) == 4 and len({a['path'] for a in archives}) == 4, 'archive inventory')
    member_names = {'source-commit.txt'} | {m + '/' + n for m in ('normal', 'optimized')
        for n in ('START.json', 'SUMMARY.json', 'errors.json', 'observed.json',
                  'processes.json', 'recipient-distribution.json')}
    reports = []
    for a in archives:
        path = record_path.parent / a['path']
        require(Path(a['path']).name == a['path'] and not path.is_symlink(), 'archive path')
        data = path.read_bytes()
        require(len(data) == a['bytes'] and sha(data) == a['sha256'], 'archive identity')
        require(hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
                == a['git_blob'], 'archive Git blob')
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            require(len(z.namelist()) == 13 and set(z.namelist()) == member_names, 'ZIP member set')
            require(sum(i.file_size for i in z.infolist()) <= 8_000_000, 'ZIP expansion limit')
            require(z.testzip() is None, 'ZIP CRC')
            require(z.read('source-commit.txt').decode().strip() == record['source_commit'], 'source identity')
            require(z.read('normal/observed.json') == z.read('optimized/observed.json'), 'mode bytes')
            for mode in ('normal', 'optimized'):
                observed_raw = z.read(mode + '/observed.json')
                require(sha(observed_raw) == record['observed_sha256_all_eight_mode_runs'], 'observed digest')
                s = load(z.read(mode + '/SUMMARY.json'))
                require((s['status'], s['cases'], s['completed'], s['passed'], s['mapped'], s['errors'])
                    == ('PASS_BOUNDED_MIGRATION', 130, 130, 130, 35, 0), 'summary counts')
                require(s['optimized'] is (mode == 'optimized') and s['observed_sha256'] == sha(observed_raw), 'summary mode or digest')
                require(len(s['entrypoint_controls']) == 2 and all(x['passed'] is True for x in s['entrypoint_controls']), 'entrypoint controls')
                require(load(z.read(mode + '/errors.json')) == [], 'saved errors')
                processes = load(z.read(mode + '/processes.json'))
                require(len(processes) == 392 and all(x['returncode'] == 0 for x in processes), 'process outcomes')
                rows = load(observed_raw)
                require(len(rows) == 130 and len({r['id'] for r in rows}) == 130, 'case identities')
                mapped = controls = 0
                for r in rows:
                    require(r['passed'] is True and set(r['checks']) == CHECKS and all(v is True for v in r['checks'].values()), 'saved case check')
                    delivered, received = r['producer']['delivery'], r['receiver']
                    require(encode(logical(delivered)) == encode(logical(received['expected_delivery'])), 'full delivered result')
                    require(received['output_validation'] == 'accepted', 'receiver refusal')
                    require(encode(r['baseline']['decision']) == encode(received['decision']), 'decision parity')
                    require(received['decision']['execution_established'] is False, 'execution inference')
                    require(delivered['source_sha256'] == r['source_sha256'] and delivered['policy_sha256'] == r['policy_sha256'], 'input binding')
                    checks = received['controls']
                    require(all(x['passed'] is True for x in checks), 'comparator control')
                    controls += len(checks)
                    appraisal = delivered['appraisal']
                    require((appraisal is None) == (delivered['failure'] is not None), 'failure/appraisal separation')
                    if appraisal is None:
                        require(r['producer']['normalized_input'] is None and len(checks) == 3, 'unmapped input')
                        continue
                    mapped += 1
                    require(set(appraisal) == FIELDS and len(checks) == 47, 'complete result or controls')
                    require(appraisal['semantics_version'] == 'wexp-core-2' and appraisal['verdict'] == 'downgrade'
                        and appraisal['asserted_claim_supported'] is False, 'Core result boundary')
                    require(appraisal['supported_claims'] == [{'base': 'observation', 'qualifiers': []}]
                        and appraisal['boundary_ceiling'] == 'observation', 'unsupported stronger inference')
                require(mapped == 35 and controls == 1930, 'mapping/control totals')
                reports.append({'archive': a['path'], 'mode': mode, 'python': s['python'],
                    'cases': 130, 'mapped': mapped, 'comparison_controls': controls,
                    'entrypoint_controls': 2, 'observed_sha256': sha(observed_raw)})
    return {'status': 'PASS_SAVED_EVIDENCE', 'source_commit': record['source_commit'],
        'record_sha256': expected_hash, 'runs': reports, 'new_execution': False,
        'scope': 'Saved byte identities, complete results and recorded comparisons; not independent truth or conformance.'}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--record', type=Path, required=True)
    p.add_argument('--expected-record-sha256', required=True)
    args = p.parse_args()
    try:
        print(json.dumps(verify(args.record.resolve(), args.expected_record_sha256), sort_keys=True, indent=2))
    except (OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile) as exc:
        raise SystemExit('SAVED_EVIDENCE_REFUSED: ' + str(exc))
