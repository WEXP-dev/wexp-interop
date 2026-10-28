"""Source-aware receiver template. Imports neither producer nor Core."""
from copy import deepcopy
from pathlib import Path
import argparse
from common import PROFILE, PROFILE_ID, PROFILE_SHA, sha, load, native_module, emit

SET_FIELDS = {'qualifiers', 'profile_identifiers', 'basis_refs', 'reasons', 'limitations',
    'recorder_relations', 'counter_evidence', 'evaluation_scope', 'inherited_limitations',
    'affected_claims', 'fatal_reasons', 'substantive_reasons', 'evaluation_gaps',
    'evaluation_gap_entries', 'supported_claims', 'maximal_supported_claims',
    'support_entries', 'support_relations'}


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False)


import json


def logical(value, key=None):
    if type(value) is dict:
        return {k: logical(v, k) for k, v in value.items()}
    if type(value) is list:
        items = [logical(v) for v in value]
        return sorted(items, key=encoded) if key in SET_FIELDS else items
    return value


def same(left, right):
    return encoded(logical(left)) == encoded(logical(right))


def expected_appraisal(s):
    # Explicit closed-profile result, not a second general Core algorithm.
    target = f'urn:aar-pilot:record:{s.record_sha256}:request:{s.request_digest}'
    context = {'id': 'urn:sha256:' + sha((s.policy_sha256 + '\n' + PROFILE_ID).encode('ascii')),
        'evaluated_at': s.policy['evaluated_at'], 'trust_configuration': 'urn:sha256:' + s.policy_sha256,
        'profile_identifiers': [PROFILE_ID]}
    texts = set(PROFILE['required_limitations'])
    texts.update('AAR_SOURCE_LIMITATION:' + str(x) for x in s.source_limitations)
    if s.selected_revision == '01':
        texts.add('AAR01_EVALUATION_NOT_RECORDED')
    limitations = [[PROFILE_ID, text] for text in sorted(texts)]
    basis = [[PROFILE_ID, 'urn:sha256:' + s.record_sha256]]
    observation = {'base': 'observation', 'qualifiers': []}
    assertion = {'base': 'execution', 'qualifiers': []}
    scope = [
      ('carrier-mapping', 'evaluated'), ('authenticity', 'evaluated'),
      ('target-binding', 'evaluated'), ('boundary-grounding', 'evaluated'),
      ('observation-support', 'evaluated'), ('intent-support', 'not-evaluated'),
      ('invocation-support', 'not-evaluated'), ('execution-support', 'not-evaluated'),
      ('provenance-support', 'not-evaluated'), ('independent-verification', 'not-evaluated'),
      ('composition', 'evaluated'), ('counter-evidence', 'evaluated')]
    return {
      'semantics_version': 'wexp-core-2', 'verdict': 'downgrade', 'fatal_reasons': [],
      'target': target, 'asserted_claim': assertion, 'asserted_claim_supported': False,
      'support_entries': [{'claim': observation, 'basis_refs': basis, 'limitations': limitations}],
      'supported_claims': [observation], 'maximal_supported_claims': [observation],
      'support_relations': [{'supported_claim': observation, 'relation': 'support-below-claim'}],
      'boundary_ceiling': 'observation', 'boundary_grounding': 'attributed', 'recorder_relations': [],
      'substantive_reasons': ['E_BASE_EXCEEDS_BOUNDARY'],
      'evaluation_gaps': ['E_BASE_NOT_EVALUATED'],
      'evaluation_gap_entries': [{'token': 'E_BASE_NOT_EVALUATED', 'target': target,
          'evaluation_context_ref': context['id'], 'affected_claims': [assertion],
          'basis_refs': basis, 'limitations': limitations}],
      'counter_evidence': [{'status': 'not-supplied', 'affected_claims': [],
          'basis_refs': [], 'reasons': [], 'limitations': []}],
      'inherited_limitations': limitations, 'evaluation_context': context,
      'evaluation_scope': [{'capability': k, 'status': v} for k, v in scope]}


def expected_delivery(source):
    return {'format': 'wexp-aar-core02-trial/1', 'profile_sha256': PROFILE_SHA,
      'source_sha256': source.record_sha256, 'policy_sha256': source.policy_sha256,
      'native': source.native, 'facts': source.facts, 'failure': source.failure,
      'appraisal': None if source.failure else expected_appraisal(source)}


def controls(value):
    trials = []
    if value['appraisal'] is not None:
        for key in value['appraisal']:
            x = deepcopy(value); del x['appraisal'][key]
            trials.append(('omit-' + key, not same(value, x)))
            x = deepcopy(value); x['appraisal'][key] = {'invalid': True}
            trials.append(('change-' + key, not same(value, x)))
        x = deepcopy(value); x['appraisal']['asserted_claim_supported'] = 0
        trials.append(('boolean-as-number', not same(value, x)))
        x = deepcopy(value); x['appraisal']['support_entries'][0]['basis_refs'][0].reverse()
        trials.append(('ordered-atom-reversal', not same(value, x)))
        x = deepcopy(value); x['appraisal']['evaluation_scope'].reverse()
        trials.append(('scope-order-permutation', same(value, x)))
        x = deepcopy(value); x['appraisal']['supported_claims'] *= 2
        trials.append(('duplicate-set-member', not same(value, x)))
    for field in ('source_sha256', 'profile_sha256', 'policy_sha256'):
        x = deepcopy(value); x[field] = '0' * 64
        trials.append(('change-' + field, not same(value, x)))
    return [{'id': name, 'passed': passed} for name, passed in trials]


def main():
    p = argparse.ArgumentParser()
    for key in ('legacy', 'source', 'policy', 'delivery'):
        p.add_argument('--' + key, type=Path, required=True)
    args = p.parse_args()
    native = native_module(args.legacy)
    s = native.verify_source(args.source.read_bytes(), args.policy.read_bytes())
    expected = expected_delivery(s)
    observed = load(args.delivery.read_bytes())
    accepted = same(expected, observed)
    result = native.result_for(s, 'core02-source-aware-receiver')
    result['output_validation'] = 'accepted' if accepted else 'rejected'
    if not accepted:
        result['decision'] = {'admission': 'quarantine', 'reason': 'delivered-result-mismatch'}
    result['expected_delivery'] = expected
    result['controls'] = controls(expected)
    emit(result)


if __name__ == '__main__':
    main()
