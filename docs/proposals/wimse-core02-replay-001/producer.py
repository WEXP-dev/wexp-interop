"""Bounded record-only AAC-independent mapping to Core-02."""
from copy import deepcopy
from pathlib import Path
import argparse
import sys
from common import PROFILE, PROFILE_ID, PROFILE_SHA, sha, native_module, emit

BASES = ('observation', 'intent', 'invocation', 'execution')


def normalize(source):
    if source.failure is not None:
        raise ValueError('native or dispatch failure cannot produce Core input')
    target = 'urn:aar-pilot:record:' + source.record_sha256 + ':request:' + source.request_digest
    cid = 'urn:sha256:' + sha((source.policy_sha256 + '\n' + PROFILE_ID).encode('ascii'))
    limits = list(PROFILE['required_limitations'])
    if source.selected_revision == '01':
        limits.append('AAR01_EVALUATION_NOT_RECORDED')
    limits += ['AAR_SOURCE_LIMITATION:' + str(x) for x in source.source_limitations]
    limits = [[PROFILE_ID, value] for value in sorted(set(limits))]
    finding = {'target': target, 'evaluation_context_ref': cid,
               'target_binding': 'supported',
               'basis_refs': [[PROFILE_ID, 'urn:sha256:' + source.record_sha256]],
               'reasons': [], 'limitations': limits}
    boundary = dict(deepcopy(finding), status='supported', ceiling_base='observation', grounding='attributed')
    bases = [dict(deepcopy(finding), base=b, semantic_validation='supported' if b == 'observation' else 'not-evaluated') for b in BASES]
    qualifiers = [dict(deepcopy(finding), qualifier='IV', qualified_base=b,
                  semantic_validation='not-evaluated', independence_validation='not-evaluated') for b in BASES]
    qualifiers.append(dict(deepcopy(finding), qualifier='PROV', qualified_base='execution',
                      semantic_validation='not-evaluated', independence_validation='not-applicable'))
    assessed = ('carrier-mapping', 'authenticity', 'target-binding', 'boundary-grounding',
                'observation-support', 'composition', 'counter-evidence')
    unassessed = ('intent-support', 'invocation-support', 'execution-support',
                  'provenance-support', 'independent-verification')
    return {'semantics_version': 'wexp-core-2', 'target': target,
        'asserted_claim': deepcopy(PROFILE['requested_claim']),
        'evaluation_context': {'id': cid, 'evaluated_at': source.policy['evaluated_at'],
            'trust_configuration': 'urn:sha256:' + source.policy_sha256,
            'profile_identifiers': [PROFILE_ID]},
        'boundary_finding': boundary, 'base_findings': bases, 'qualifier_findings': qualifiers,
        'recorder_relations': [], 'counter_evidence': [{'status': 'not-supplied',
            'affected_claims': [], 'basis_refs': [], 'reasons': [], 'limitations': []}],
        'evaluation_scope': [{'capability': c, 'status': 'evaluated'} for c in assessed] +
                            [{'capability': c, 'status': 'not-evaluated'} for c in unassessed],
        'profile_evaluation_gaps': [], 'inherited_limitations': limits, 'fatal_conditions': []}


def main():
    p = argparse.ArgumentParser()
    for key in ('legacy', 'ref', 'source', 'policy'):
        p.add_argument('--' + key, type=Path, required=True)
    args = p.parse_args()
    native = native_module(args.legacy)
    s = native.verify_source(args.source.read_bytes(), args.policy.read_bytes())
    delivery = {'format': 'wexp-aar-core02-trial/1', 'profile_sha256': PROFILE_SHA,
        'source_sha256': s.record_sha256, 'policy_sha256': s.policy_sha256,
        'native': s.native, 'facts': s.facts, 'failure': s.failure, 'appraisal': None}
    normalized = None
    if s.failure is None:
        core_path = args.ref.resolve() / 'src/wexp_ref/core02/appraiser.py'
        if sha(core_path.read_bytes()) != PROFILE['appraiser_sha256']:
            raise ValueError('wrong appraiser bytes')
        sys.path.insert(0, str(args.ref.resolve() / 'src'))
        from wexp_ref.core02.appraiser import appraise
        normalized = normalize(s)
        before = deepcopy(normalized)
        delivery['appraisal'] = appraise(normalized, {PROFILE_ID: {
            'tokens': {}, 'relation_tokens': [], 'scope_names': []}})
        if normalized != before:
            raise ValueError('appraiser mutated input')
    emit({'delivery': delivery, 'normalized_input': normalized})


if __name__ == '__main__':
    main()
