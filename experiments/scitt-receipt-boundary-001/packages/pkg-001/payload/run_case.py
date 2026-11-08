#!/usr/bin/env python3
"""Re-run both appraisers on the four inputs of this case and compare every result component with the
frozen expectations. Engines run in separate interpreter processes with only their own code on the path.

usage: python3.12 run_case.py --wexp-ref <wexp-ref checkout> --wexp-check <wexp-check checkout> [--output comparison.json]
"""
import argparse, json, platform, subprocess, sys, tempfile
from pathlib import Path
HERE = Path(__file__).resolve().parent
SET_FIELDS = {'qualifiers', 'profile_identifiers', 'basis_refs', 'reasons', 'limitations', 'base_findings',
              'qualifier_findings', 'recorder_relations', 'counter_evidence', 'evaluation_scope',
              'profile_evaluation_gaps', 'inherited_limitations', 'fatal_conditions', 'affected_claims',
              'fatal_reasons', 'substantive_reasons', 'evaluation_gaps', 'evaluation_gap_entries',
              'supported_claims', 'maximal_supported_claims', 'support_entries', 'support_relations'}
DRIVER = r'''
import json, sys
mod, inp, prof = sys.argv[1:4]
if mod == 'wexp_check':
    from wexp_check import appraise
else:
    from wexp_ref.core02.appraiser import appraise
print(json.dumps(appraise(json.load(open(inp)), json.load(open(prof)))))
'''
def enc(v): return json.dumps(v, ensure_ascii=True, sort_keys=True, separators=(',', ':'), allow_nan=False)
def logical(v, field=None):
    if type(v) is dict: return {k: logical(x, k) for k, x in v.items()}
    if type(v) is list:
        items = [logical(x) for x in v]
        return sorted(items, key=enc) if field in SET_FIELDS else items
    return v
def same(a, b): return enc(logical(a)) == enc(logical(b))
def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--wexp-ref', required=True, type=Path); ap.add_argument('--wexp-check', required=True, type=Path)
    ap.add_argument('--output', type=Path)
    a = ap.parse_args()
    paths = {'wexp_ref': a.wexp_ref.resolve() / 'src', 'wexp_check': a.wexp_check.resolve()}
    report = {'python': platform.python_version(), 'cases': {}}; ok = True
    with tempfile.TemporaryDirectory() as tmp:
        for cid in ('a', 'b1', 'b2', 'c'):
            inp = Path(tmp) / f'{cid}.json'
            inp.write_text(json.dumps(json.loads((HERE / 'inputs' / f'{cid}.json').read_text())['input']))
            exp = json.loads((HERE / 'expectations' / f'{cid}.json').read_text())['expected']
            row = {}
            for mod, path in paths.items():
                r = subprocess.run([sys.executable, '-B', '-c', DRIVER, mod, str(inp), str(HERE / 'profiles.json')],
                                   env={'PYTHONPATH': str(path), 'PATH': '/usr/bin:/bin'}, capture_output=True, text=True)
                obs = json.loads(r.stdout) if r.returncode == 0 else {'error': r.stderr[-500:]}
                row[f'{mod}_equals_expected'] = same(obs, exp)
                if not row[f'{mod}_equals_expected']:
                    row[f'{mod}_differing_components'] = sorted(k for k in exp if not same({k: exp[k]}, {k: obs.get(k)}))
                row[f'{mod}_observed'] = obs
                ok = ok and row[f'{mod}_equals_expected']
            report['cases'][cid] = row
            print(cid, 'wexp_ref==expected', row['wexp_ref_equals_expected'], 'wexp_check==expected', row['wexp_check_equals_expected'])
    if a.output:
        a.output.write_text(json.dumps(report, indent=1, sort_keys=True) + '\n')
    return 0 if ok else 1
if __name__ == '__main__':
    raise SystemExit(main())
