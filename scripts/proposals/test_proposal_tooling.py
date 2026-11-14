"""The order and the bytes of a proposal, checked on throwaway repositories with stand-in appraisers."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import freeze_proposal  # noqa: E402
import new_proposal  # noqa: E402
import proposal_lib as lib  # noqa: E402
import run_proposal  # noqa: E402

SHA = 'e' * 40
PIN = f'acme/receipts@{SHA}:samples/r1.json'
RESULT = {'verdict': 'downgrade', 'substantive_reasons': ['B', 'A'], 'supported_claims': []}
ENGINE = "import json\ndef appraise(input, profiles=None):\n    return json.loads(%r)\n"


def git(cwd, *args):
    subprocess.run(['git', '-C', str(cwd), '-c', 'user.name=test', '-c', 'user.email=test@example.invalid',
                    '-c', 'commit.gpgsign=false', *args], check=True, capture_output=True)


def head(cwd):
    return subprocess.run(['git', '-C', str(cwd), 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()


class Workspace:
    """A repository with one proposal, and two stand-in appraiser checkouts."""

    def __init__(self, tmp: Path, ref_result=RESULT, check_result=RESULT):
        self.repo = tmp / 'repo'
        self.root = self.repo / 'docs' / 'proposals'
        self.root.mkdir(parents=True)
        git(self.repo, 'init', '-q')
        self.ref, self.check = tmp / 'ref', tmp / 'check'
        (self.ref / 'src' / 'wexp_ref' / 'core02').mkdir(parents=True)
        for pkg in ('src/wexp_ref', 'src/wexp_ref/core02'):
            (self.ref / pkg / '__init__.py').write_text('')
        (self.ref / 'src/wexp_ref/core02/appraiser.py').write_text(ENGINE % json.dumps(ref_result))
        (self.check / 'wexp_check').mkdir(parents=True)
        (self.check / 'wexp_check/__init__.py').write_text(ENGINE % json.dumps(check_result))
        for c in (self.ref, self.check):
            git(c, 'init', '-q'); git(c, 'add', '-A'); git(c, 'commit', '-q', '-m', 'engine')
        self.dir = new_proposal.build('sample-format-001', 'Sample format', [PIN], 7, self.root,
                                      fetch=lambda pin: b'{"record": 1}\n')
        pins = json.loads((self.dir / 'SOURCE-PINS.json').read_text())
        pins['wexp_ref']['commit'], pins['wexp_check']['commit'] = head(self.ref), head(self.check)
        (self.dir / 'SOURCE-PINS.json').write_text(json.dumps(pins))
        self.case('K1', {'verdict': 'downgrade', 'substantive_reasons': ['A', 'B'], 'supported_claims': []})

    def case(self, cid, expected):
        (self.dir / 'inputs' / f'{cid}.json').write_text(json.dumps({'id': cid, 'input': {'target': 'T'}}))
        (self.dir / 'expectations' / f'{cid}.json').write_text(json.dumps({'id': cid, 'expected': expected}))

    def commit(self, message):
        git(self.repo, 'add', '-A'); git(self.repo, 'commit', '-q', '-m', message)

    def run(self):
        return run_proposal.run(self.dir, self.ref, self.check)

    def write_evidence(self):
        (self.dir / 'evidence').mkdir(exist_ok=True)
        (self.dir / 'evidence' / 'comparison.json').write_text(json.dumps(self.run()))


class Case(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)


class ScaffoldTest(Case):
    def test_the_skeleton_records_the_pinned_bytes_and_writes_no_mapping(self):
        w = Workspace(self.tmp)
        pins = json.loads((w.dir / 'SOURCE-PINS.json').read_text())
        self.assertEqual(pins['external_files'][0]['sha256'], lib.sha256(b'{"record": 1}\n'))
        self.assertEqual(pins['external_files'][0]['bytes'], 14)
        self.assertEqual(pins['interop_check_issue'], 7)
        self.assertIn('_To write._', (w.dir / 'MAPPING.md').read_text())
        self.assertIn('PROPOSAL', (w.dir / 'README.md').read_text())

    def test_a_proposal_is_never_overwritten(self):
        w = Workspace(self.tmp)
        with self.assertRaises(lib.ProposalError):
            new_proposal.build('sample-format-001', 'Again', [PIN], None, w.root, fetch=lambda pin: b'x')

    def test_pins_that_are_not_exact_public_bytes_are_refused(self):
        for bad in ('acme/receipts@main:r1.json', f'acme/receipts@{SHA}:../../etc/passwd',
                    f'acme/receipts@{SHA}:a/./b', f'acme/receipts@{SHA}:$(id)', f'acme/receipts@{SHA}',
                    f'https://evil.example/@{SHA}:x', f'acme/rec eipts@{SHA}:x'):
            with self.subTest(pin=bad):
                with self.assertRaises(lib.ProposalError):
                    lib.parse_pin(bad)

    def test_slug_and_title_are_plain(self):
        for slug in ('Bad_Slug', 'x', 'no-number', '../up-001'):
            with self.subTest(slug=slug):
                with self.assertRaises(lib.ProposalError):
                    lib.proposal_dir(slug)
        with self.assertRaises(lib.ProposalError):
            new_proposal.build('other-format-001', 'line one\nline two', [PIN], None, self.tmp, fetch=lambda pin: b'x')

    def test_a_proposal_needs_at_least_one_pin(self):
        with self.assertRaises(lib.ProposalError):
            new_proposal.build('other-format-001', 'No bytes', [], None, self.tmp, fetch=lambda pin: b'x')


class OrderTest(Case):
    def test_freeze_then_run_in_two_commits_is_accepted(self):
        w = Workspace(self.tmp)
        freeze_proposal.freeze(w.dir); w.commit('freeze')
        w.write_evidence(); w.commit('run')
        self.assertEqual(freeze_proposal.check(w.dir, True)['order'], 'kept')

    def test_an_unfrozen_proposal_is_refused(self):
        w = Workspace(self.tmp)
        with self.assertRaisesRegex(lib.ProposalError, 'not been frozen'):
            freeze_proposal.check(w.dir, False)

    def test_an_expectation_edited_after_the_freeze_is_refused(self):
        w = Workspace(self.tmp)
        freeze_proposal.freeze(w.dir); w.commit('freeze')
        w.case('K1', {'verdict': 'accept'})
        with self.assertRaisesRegex(lib.ProposalError, 'expectations/K1.json'):
            freeze_proposal.check(w.dir, False)

    def test_a_case_added_after_the_freeze_is_refused(self):
        w = Workspace(self.tmp)
        freeze_proposal.freeze(w.dir); w.commit('freeze')
        w.case('K2', {'verdict': 'accept'})
        with self.assertRaisesRegex(lib.ProposalError, 'not in the freeze'):
            freeze_proposal.check(w.dir, False)

    def test_freeze_and_evidence_in_one_commit_is_refused(self):
        w = Workspace(self.tmp)
        freeze_proposal.freeze(w.dir); w.write_evidence(); w.commit('both')
        with self.assertRaisesRegex(lib.ProposalError, 'before the run, not with it'):
            freeze_proposal.check(w.dir, True)

    def test_a_freeze_written_after_a_run_is_refused(self):
        w = Workspace(self.tmp)
        w.commit('skeleton'); w.write_evidence(); w.commit('run first')
        with self.assertRaisesRegex(lib.ProposalError, 'post-date'):
            freeze_proposal.freeze(w.dir)

    def test_evidence_committed_before_the_freeze_is_refused(self):
        w = Workspace(self.tmp)
        w.write_evidence(); w.commit('run first')
        record = {'algorithm': 'sha256', 'files': lib.frozen_files(w.dir)}
        (w.dir / 'FREEZE.json').write_text(json.dumps(record)); w.commit('freeze later')
        with self.assertRaisesRegex(lib.ProposalError, 'does not come after'):
            freeze_proposal.check(w.dir, True)

    def test_an_input_without_an_expectation_is_refused(self):
        w = Workspace(self.tmp)
        (w.dir / 'expectations' / 'K1.json').unlink()
        with self.assertRaisesRegex(lib.ProposalError, 'no expectation'):
            freeze_proposal.freeze(w.dir)


class RunTest(Case):
    def test_set_valued_components_compare_as_sets(self):
        row = Workspace(self.tmp).run()['cases']['K1']
        self.assertTrue(row['wexp_ref_equals_expected'] and row['wexp_check_equals_expected'])
        self.assertTrue(row['appraisers_equal'])

    def test_a_difference_is_recorded_per_component_and_is_not_an_error(self):
        other = dict(RESULT, verdict='accept')
        row = Workspace(self.tmp, check_result=other).run()['cases']['K1']
        self.assertFalse(row['wexp_check_equals_expected'])
        self.assertEqual(row['wexp_check_differing_components'], ['verdict'])
        self.assertFalse(row['appraisers_equal'])

    def test_an_appraiser_that_does_not_complete_is_a_refusal_not_a_result(self):
        w = Workspace(self.tmp)
        (w.check / 'wexp_check/__init__.py').write_text('def appraise(i, p=None):\n    raise RuntimeError("boom")\n')
        git(w.check, 'commit', '-q', '-am', 'broken')
        pins = json.loads((w.dir / 'SOURCE-PINS.json').read_text())
        pins['wexp_check']['commit'] = head(w.check)
        (w.dir / 'SOURCE-PINS.json').write_text(json.dumps(pins))
        with self.assertRaisesRegex(lib.ProposalError, 'did not complete case K1'):
            w.run()

    def test_a_checkout_at_another_commit_or_with_local_changes_is_refused(self):
        w = Workspace(self.tmp)
        (w.ref / 'src/wexp_ref/core02/appraiser.py').write_text(ENGINE % json.dumps({'verdict': 'accept'}))
        with self.assertRaisesRegex(lib.ProposalError, 'local changes'):
            w.run()
        git(w.ref, 'commit', '-q', '-am', 'moved')
        with self.assertRaisesRegex(lib.ProposalError, 'SOURCE-PINS.json names'):
            w.run()

    def test_the_summary_is_built_from_fixed_words_only(self):
        w = Workspace(self.tmp, ref_result=dict(RESULT, verdict='<script>'))
        text = run_proposal.summary(w.dir, w.run(), 'none yet')
        self.assertNotIn('<script>', text)
        self.assertIn('not an independent reproduction', text)


if __name__ == '__main__':
    unittest.main()
