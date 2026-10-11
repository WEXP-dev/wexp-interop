"""Private AAR mapping/output experiment; no standardized internal interface.

An input failure never becomes a fabricated Core rejection. Native libraries
remain unmodified and are loaded in a fresh process for each selected revision.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
PROFILE_BYTES = (ROOT / 'profile.json').read_bytes()
PROFILE = json.loads(PROFILE_BYTES)
PROFILE_SHA = hashlib.sha256(PROFILE_BYTES).hexdigest()
EMPTY_NATIVE = {'verdict': 'not-run', 'codes': [], 'derived_tier': ''}
BASES = ['observation', 'intent', 'invocation', 'execution']


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def no_duplicates(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError('duplicate JSON member')
        obj[key] = value
    return obj


def strict(raw):
    return json.loads(raw, object_pairs_hook=no_duplicates,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))


def fact_projection(pred, revision):
    ev = pred.get('evaluation') if revision == '02' else None
    ov = pred.get('oversight')
    return {
        'evaluation': {
            'status': ev['status'] if ev is not None else 'unknown-in-01',
            'unavailable_input': list(ev.get('unavailableInput', [])) if ev is not None else [],
            'evidence_class': pred['fieldEvidence']['decision'],
        },
        'decision_reported': pred['decision']['reported'],
        'effect_observed': pred['effect']['observed'],
        'agreement': pred['agreement'],
        'oversight': {
            'presence': 'present' if ov is not None else 'absent',
            'act': ov['act'] if ov is not None else None,
            'record_digest': ov.get('recordDigest') if ov is not None else None,
            'evidence_class': 'producer-asserted',
            'human_participation': 'not-established',
            'authority': 'not-established',
        },
    }


def map_input(raw, pred, policy, policy_sha):
    """Closed input domain from profile.json, all available roles considered."""
    record_sha = sha(raw)
    target = 'urn:aar-pilot:record:' + record_sha + ':request:' + pred['decision']['requestDigest']
    context_id = 'urn:sha256:' + policy_sha
    limits = list(PROFILE['required_limitations'])
    if policy['carrier_revision'] == '01':
        limits.append('AAR01_EVALUATION_NOT_RECORDED')
    limits.extend('AAR_SOURCE_LIMITATION:' + str(x) for x in pred['doesNotAssert'])
    limits = sorted(set(limits))
    basis = ['urn:sha256:' + record_sha]
    common = {'target': target, 'evaluation_context_ref': context_id,
              'target_binding': 'supported', 'basis_refs': basis,
              'reasons': [], 'limitations': limits}
    boundary = dict(common, status='supported', ceiling_base='observation', grounding='attributed')
    bases = [dict(common, base=base,
                  semantic_validation='supported' if base == 'observation' else 'not-evaluated')
             for base in BASES]
    quals = [dict(common, qualifier='IV', qualified_base=base,
                  semantic_validation='not-evaluated', independence_validation='not-evaluated')
             for base in BASES]
    quals.append(dict(common, qualifier='PROV', qualified_base='execution',
                      semantic_validation='not-evaluated', independence_validation='not-applicable'))
    scope = {key: 'evaluated' for key in [
        'carrier-mapping', 'authenticity', 'target-binding', 'boundary-grounding',
        'observation-support', 'composition', 'counter-evidence']}
    scope.update({key: 'not-evaluated' for key in [
        'intent-support', 'invocation-support', 'execution-support',
        'provenance-support', 'independent-verification']})
    # Composition is outside the requested single-action claim: no required
    # composition predicate and no current-scope gap. This scope is not a claim
    # that any composition was proved (Core §12 external-capability rule).
    return {
        'semantics_version': 'wexp-core-1', 'target': target,
        'asserted_claim': dict(PROFILE['requested_claim']),
        'evaluation_context': {'id': context_id, 'evaluated_at': policy['evaluated_at'],
            'trust_configuration': 'urn:sha256:' + policy_sha,
            'profile_identifiers': [PROFILE['profile_id'] + ':sha256:' + PROFILE_SHA]},
        'boundary_finding': boundary, 'base_findings': bases,
        'qualifier_findings': quals, 'recorder_relations': [],
        'counter_evidence': [{'status': 'not-supplied', 'affected_claims': [],
                             'basis_refs': [], 'reasons': [], 'limitations': []}],
        'evaluation_scope': scope, 'profile_evaluation_gaps': [],
        'inherited_limitations': limits, 'fatal_conditions': [],
    }


def guard_closed_input(inp):
    """Necessary admission assertions for this profile, not a Core validator."""
    expected = set(['semantics_version', 'target', 'asserted_claim', 'evaluation_context',
        'boundary_finding', 'base_findings', 'qualifier_findings', 'recorder_relations',
        'counter_evidence', 'evaluation_scope', 'profile_evaluation_gaps',
        'inherited_limitations', 'fatal_conditions'])
    if set(inp) != expected or inp['semantics_version'] != 'wexp-core-1':
        raise ValueError('closed-input-shape')
    if inp['asserted_claim'] != PROFILE['requested_claim']:
        raise ValueError('closed-input-claim')
    if [f['base'] for f in inp['base_findings']] != BASES:
        raise ValueError('closed-input-bases')
    for f in [inp['boundary_finding']] + inp['base_findings'] + inp['qualifier_findings']:
        if f['target'] != inp['target'] or f['evaluation_context_ref'] != inp['evaluation_context']['id']:
            raise ValueError('closed-input-scope')
    passing = [f['base'] for f in inp['base_findings'] if f['semantic_validation'] == 'supported']
    if passing != ['observation'] or any(f['semantic_validation'] != 'not-evaluated' for f in inp['qualifier_findings']):
        raise ValueError('closed-input-support')
    if inp['boundary_finding']['ceiling_base'] != 'observation':
        raise ValueError('closed-input-boundary')


def run(raw, policy_raw):
    policy = strict(policy_raw)
    if not isinstance(policy, dict):
        raise ValueError('policy must be an object')
    revision = policy.get('carrier_revision')
    output = {
        'format': 'wexp-aar-pilot-output/0.1.0',
        'source': {'record_sha256': sha(raw), 'carrier_revision': revision,
            'specification_sha256': policy.get('specification_sha256'),
            'predicate_type': policy.get('predicate_type')},
        'context': {'profile_id': PROFILE['profile_id'], 'profile_sha256': PROFILE_SHA,
                    'policy_sha256': sha(policy_raw)},
        'status': 'mapping-failure', 'native': dict(EMPTY_NATIVE), 'facts': None,
        'appraisal': None, 'mapping_failure': None,
    }
    def fail(stage, code):
        output['mapping_failure'] = {'stage': stage, 'code': code}
        return output, None
    if revision is None:
        output['source']['specification_sha256'] = None
        return fail('revision-selection', 'carrier-revision-not-selected')
    if not isinstance(revision, str) or revision not in PROFILE['carrier_revisions']:
        output['source']['specification_sha256'] = None
        return fail('revision-selection', 'unsupported-carrier-revision')
    if policy.get('specification_sha256') != PROFILE['carrier_revisions'][revision]:
        return fail('revision-selection', 'carrier-specification-mismatch')
    if (policy.get('predicate_type') != PROFILE['predicate_type']
            or policy.get('policy_id') != 'aar-record-only-0.1.0'):
        return fail('receiver-policy', 'policy-invalid')
    if (policy.get('profile_id') != PROFILE['profile_id']
            or policy.get('profile_sha256') != PROFILE_SHA
            or policy.get('core_txt_sha256') != PROFILE['core_txt_sha256']
            or policy.get('requested_claim') != PROFILE['requested_claim']):
        return fail('policy-validation', 'policy-pin-mismatch')
    if (not isinstance(policy.get('observer_public_key'), str)
            or re.fullmatch(r'[0-9a-fA-F]{64}', policy['observer_public_key']) is None
            or not isinstance(policy.get('evaluated_at'), str)):
        return fail('receiver-policy', 'policy-invalid')
    sys.path.insert(0, str(ROOT / 'vendor' / ('aar' + revision) / 'packaging'))
    try:
        from agent_evidence_vectors import auditrecord
        report = auditrecord.verify(raw, auditrecord.Policy(PROFILE['predicate_type'], policy['observer_public_key']))
    except Exception as exc:
        output['native'] = {'verdict': 'error', 'codes': [type(exc).__name__], 'derived_tier': ''}
        return fail('native-validation', 'native-verifier-error')
    output['native'] = {'verdict': report.verdict, 'codes': report.codes,
                         'derived_tier': report.derived_tier}
    if report.verdict != 'valid':
        return fail('native-validation', 'native-record-malformed')
    pred = auditrecord.parse_statement(base64.b64decode(strict(raw)['payload'], validate=True))['predicate']
    if revision == '01' and any(key in pred for key in ('evaluation', 'oversight')):
        return fail('revision-selection', 'revision02-members-in-01-profile')
    try:
        inp = map_input(raw, pred, policy, sha(policy_raw))
        guard_closed_input(inp)
        spec = importlib.util.spec_from_file_location('pinned_hof_core', ROOT / 'vendor/core_hof/evaluator.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        appraisal = module.appraise(inp)
    except Exception:
        return fail('mapping', 'closed-profile-input-unavailable')
    output.update(status='mapped', facts=fact_projection(pred, revision),
                  appraisal=appraisal, mapping_failure=None)
    return output, inp


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--policy', type=Path, required=True)
    parser.add_argument('--normalized-out', type=Path)
    args = parser.parse_args()
    output, normalized = run(args.source.read_bytes(), args.policy.read_bytes())
    if args.normalized_out is not None:
        args.normalized_out.write_text(json.dumps(normalized, ensure_ascii=False, sort_keys=True, indent=2) + '\n')
    print(json.dumps(output, ensure_ascii=False, sort_keys=True, separators=(',', ':')))


if __name__ == '__main__':
    main()
