"""Regenerate LOCAL extensions, never modify either published corpus.

Optional generation dependency: cryptography. Normal replay is Python stdlib.
The fixed seed is a deliberately public TEST KEY, unrelated to any deployment.
Expectations below are selected from draft text before running the verifier.
"""
from __future__ import annotations
import base64
import copy
import hashlib
import json
from pathlib import Path
import sys

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'vendor/aar02/packaging'))
from agent_evidence_vectors import auditrecord

SEED = hashlib.sha256(b'PUBLIC TEST KEY ONLY: WEXP AAR 02 pilot 0.1.0').digest()
KEY = Ed25519PrivateKey.from_private_bytes(SEED)
PUBLIC = KEY.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw).hex()
KEYID = hashlib.sha256(bytes.fromhex(PUBLIC)).hexdigest()[:32]


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + '\n')


def load_vector(draft_id):
    corpus = ROOT / 'vendor/aar02/vectors-agent-audit-record'
    manifest = json.loads((corpus / 'MANIFEST.json').read_bytes())
    entry = next(e for e in manifest['vectors'] if e['draftId'] == draft_id)
    envelope = json.loads((corpus / entry['file']).read_bytes())
    return json.loads(base64.b64decode(envelope['payload']))


def seal(statement):
    payload = auditrecord.canonical_bytes(statement)
    signature = KEY.sign(auditrecord.pae(auditrecord.PAYLOAD_TYPE, payload))
    return {'payloadType': auditrecord.PAYLOAD_TYPE,
            'payload': base64.b64encode(payload).decode(),
            'signatures': [{'keyid': KEYID, 'sig': base64.b64encode(signature).decode()}]}


def main():
    fixture_root = ROOT / 'fixtures/local'
    cases = []

    def add(case_id, parent, mutation, expected, why, locus):
        statement = load_vector(parent)
        mutation(statement['predicate'])
        path = fixture_root / (case_id + '.dsse.json')
        write_json(path, seal(statement))
        cases.append({'id': case_id, 'kind': 'local-extension', 'source': str(path.relative_to(ROOT)),
            'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'policy': 'policies/local-aar02.json', 'parent_draft_id': parent,
            'expected_native_verdict': expected, 'rationale': why, 'source_locus': locus})

    def evaluation(value):
        return lambda p: p.update(evaluation=copy.deepcopy(value))

    add('L01-fail-open-permit', 'A1', evaluation({'status': 'not-evaluated', 'unavailableInput': ['standing-source']}),
        'valid', 'Not-evaluated is representable even for permit.', 'AAR-02 §5.4 and §6.5')
    def conditional(p):
        p['decision']['reported'] = 'permit-with-conditions'
        p['evaluation'] = {'status': 'not-evaluated', 'unavailableInput': ['key-source', 'consumption-state']}
    add('L02-fail-open-conditional', 'A1', conditional, 'valid', 'The same rule covers permit-with-conditions.', 'AAR-02 §5.4')
    add('L03-outage-deny-effect', 'A3', evaluation({'status': 'not-evaluated', 'unavailableInput': ['standing-source']}),
        'valid', 'A leak during an outage remains disagreement, not malformed.', 'AAR-02 §5.4')
    bad = [
        ('L04-empty-unavailable', {'status': 'not-evaluated', 'unavailableInput': []}),
        ('L05-duplicate-unavailable', {'status': 'not-evaluated', 'unavailableInput': ['standing-source', 'standing-source']}),
        ('L06-scalar-unavailable', {'status': 'not-evaluated', 'unavailableInput': 'standing-source'}),
        ('L07-null-unavailable', {'status': 'not-evaluated', 'unavailableInput': None}),
        ('L08-evaluated-null-unavailable', {'status': 'evaluated', 'unavailableInput': None}),
        ('L09-evaluated-empty-unavailable', {'status': 'evaluated', 'unavailableInput': []}),
        ('L10-missing-evaluation-status', {}),
        ('L11-unknown-evaluation-status', {'status': 'unknown'}),
    ]
    for case_id, value in bad:
        add(case_id, 'A2', evaluation(value), 'malformed', 'Closed status and conditional nonempty unique array; no defaults.', 'AAR-02 §§4, 5.4; EV1–EV4')
    for index, act in enumerate(['observation', 'check', 'decision', 'release'], 12):
        add('L%02d-oversight-%s' % (index, act), 'A1', lambda p, act=act: p.update(oversight={'act': act}),
            'valid', 'Every defined act is representable without a digest; it remains producer asserted.', 'AAR-02 §5.5')
    add('L16-oversight-unresolved-digest', 'A1', lambda p: p.update(oversight={'act': 'release', 'recordDigest': 'f' * 64}),
        'valid', 'The reader does not resolve a well-shaped recordDigest.', 'AAR-02 §5.5')
    add('L17-oversight-absent', 'A1', lambda p: p.pop('oversight', None), 'valid',
        'Absence supplies no evidence that nobody acted.', 'AAR-02 §4')
    def substrate(p):
        p['fieldEvidence']['decision'] = 'substrate-covered'
        p['oversight'] = {'act': 'check'}
    add('L18-oversight-evidence-partition', 'A1', substrate, 'valid',
        'Preserve declared decision evidence class without making oversight independently verified.', 'AAR-02 §§5.4–5.5')

    before = b'balance=100\n'
    claimed_after = b'balance=0\n'
    def false_effect(p):
        p['recordId'] = 'urn:example:wexp-aar-pilot:trusted-wrong-effect'
        p['resource'] = {'kind': 'path', 'id': '/pilot/ledger.txt', 'binding': 'digest-bound',
                         'argumentsDigest': hashlib.sha256(claimed_after).hexdigest()}
        digest = auditrecord.request_digest(p)
        p['decision']['requestDigest'] = digest
        interval = p['effect']['interval']
        interval.update(beforeRoot=hashlib.sha256(before).hexdigest(), afterRoot=hashlib.sha256(claimed_after).hexdigest(), baseResolution='supplied')
        p['effect']['pathScope'] = ['/pilot/']
        p['effect']['writes'] = [{'path': '/pilot/ledger.txt', 'preStateDigest': interval['beforeRoot'],
            'postStateDigest': interval['afterRoot'], 'requestDigest': digest, 'inScope': True}]
        commitment = p['observation']['priorCommitment']
        commitment['keyid'] = KEYID
        commitment['commitmentDigest'] = auditrecord.commitment_digest(p, commitment)
        # This carried test signature is still outside native verification.
        commitment['sig'] = base64.b64encode(KEY.sign(commitment['commitmentDigest'].encode('ascii'))).decode()
    statement = load_vector('A1')
    false_effect(statement['predicate'])
    statement['subject'][0]['digest']['sha256'] = statement['predicate']['decision']['requestDigest']
    statement['subject'][1]['digest']['sha256'] = statement['predicate']['effect']['interval']['afterRoot']
    case_id = 'L19-trusted-wrong-effect'
    path = fixture_root / (case_id + '.dsse.json')
    write_json(path, seal(statement))
    cases.append({'id': case_id, 'kind': 'local-extension', 'source': str(path.relative_to(ROOT)),
        'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'policy': 'policies/local-aar02.json',
        'parent_draft_id': 'A1', 'expected_native_verdict': 'valid',
        'rationale': 'Coordinated false effect and all dependent bindings signed by the explicitly trusted TEST signer. Structural validity cannot establish the effect.',
        'source_locus': 'AAR-02 §§6.1–6.3; WEXP Core-01 §14'})
    oracle = {
        'kind': 'controlled-local-test-oracle-not-carried-to-participants',
        'record': str(path.relative_to(ROOT)), 'record_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'request_digest': statement['predicate']['decision']['requestDigest'],
        'logical_path': '/pilot/ledger.txt', 'before_utf8': before.decode(),
        'claimed_after_utf8': claimed_after.decode(),
        'worlds': [{'id': 'effect-consistent-control', 'operation': 'write'},
                   {'id': 'trusted-producer-wrong', 'operation': 'no-op'}],
        'scope': 'Only the reported effect is contrasted. Other fields are illustrative test assertions. A closed harness operation and local endpoint observations are not deployment-wide nonoccurrence evidence.',
        'participant_information': 'Both routes receive identical signed bytes and the same trusted public key/policy; neither receives this oracle or world id.',
    }
    write_json(ROOT / 'fixtures/trusted-producer-oracle.json', oracle)
    policy = json.loads((ROOT / 'policies/aar02.json').read_bytes())
    policy['observer_public_key'] = PUBLIC
    write_json(ROOT / 'policies/local-aar02.json', policy)
    write_json(ROOT / 'fixtures/local-manifest.json', {
        'format': 'aar-pilot-local-fixtures/0.1.0', 'test_key': {'note': 'DELIBERATELY PUBLIC TEST KEY; never deploy.',
            'seed_hex': SEED.hex(), 'public_key': PUBLIC, 'keyid': KEYID},
        'expectation_authority': 'The cited published requirements; expectations were not derived from verifier outcomes.',
        'cases': cases})
    print(json.dumps({'local_fixtures': len(cases), 'generator': 'cryptography Ed25519', 'public_test_key': PUBLIC}))


if __name__ == '__main__':
    main()
