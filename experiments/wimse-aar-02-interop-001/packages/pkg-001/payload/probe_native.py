"""Fresh-process access to a pinned native reader; never interprets WEXP."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.dont_write_bytecode = True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True, choices=['01', '02'])
    parser.add_argument('--source', type=Path)
    args = parser.parse_args()
    native = ROOT / 'vendor' / ('aar' + args.revision)
    sys.path.insert(0, str(native / 'packaging'))
    from agent_evidence_vectors import auditrecord
    corpus = native / 'vectors-agent-audit-record'
    manifest = json.loads((corpus / 'MANIFEST.json').read_bytes())
    policy = auditrecord.policy_for(manifest)
    if args.source:
        report = auditrecord.verify(args.source.read_bytes(), policy)
        result = {'verdict': report.verdict, 'codes': report.codes, 'derived_tier': report.derived_tier}
    else:
        results = []
        for entry in manifest['vectors']:
            report = auditrecord.verify((corpus / entry['file']).read_bytes(), policy)
            results.append({'draft_id': entry['draftId'], 'source': entry['file'],
                'verdict': report.verdict, 'codes': report.codes, 'derived_tier': report.derived_tier,
                'allowed_verdicts': sorted(auditrecord.conforming_verdicts(entry)),
                'verdict_matches': report.verdict in auditrecord.conforming_verdicts(entry)})
        judged = auditrecord.judge(str(corpus))
        result = {'revision': args.revision, 'corpus_digest': auditrecord.corpus_digest(manifest, str(corpus)),
            'declared_corpus_digest': manifest['corpusDigest'], 'judge_ok': judged.ok(),
            'judge_stdout': auditrecord.render(judged, auditrecord.SUITE), 'vectors': results}
    print(json.dumps(result, sort_keys=True, separators=(',', ':')))


if __name__ == '__main__':
    main()
