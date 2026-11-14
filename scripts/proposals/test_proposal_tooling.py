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
import request_archive  # noqa: E402
import result_table  # noqa: E402
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


def row(**changes):
    base = result_table.template('Sample receipts', 26)
    base.update({k: v for k, v in changes.items() if k != 'initiation'})
    base['initiation'].update(changes.get('initiation', {}))
    return base


NAMED_OWNER = {'named': True, 'initiated_by': 'Dana Example', 'relation': 'repository-owner',
               'relation_subject': 'acme/receipts', 'established_by': 'github-public-record'}


class ResultRowTest(unittest.TestCase):

    def test_the_skeleton_row_is_a_draft_that_names_nobody(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = new_proposal.build('sample-topic-001', 'Sample receipts', [PIN], 26, Path(tmp),
                                           fetch=lambda pin: b'x', relation='repository-owner')
            saved = json.loads((directory / lib.RESULT_ROW).read_text())
        self.assertEqual((saved['status'], saved['initiation']['named'], saved['initiation']['initiated_by'],
                          saved['initiation']['relation_subject']), ('draft', False, None, None))
        self.assertEqual(saved['initiation']['relation'], 'repository-owner')
        self.assertEqual(result_table.initiated_by(saved['initiation']),
                         'A party who asked not to be named; the owner of a repository of the format '
                         '(GitHub public record)')

    def test_the_result_row_is_not_part_of_the_freeze(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = new_proposal.build('sample-topic-001', 'Sample receipts', [PIN], None, Path(tmp),
                                           fetch=lambda pin: b'x')
            self.assertNotIn(lib.RESULT_ROW, lib.frozen_files(directory))

    def test_each_kind_of_initiator_is_stated_with_how_it_is_known(self):
        said = result_table.initiated_by
        self.assertEqual(said(result_table.validate(row(initiation=NAMED_OWNER))['initiation']),
                         'Dana Example, the owner of repository `acme/receipts` (GitHub public record)')
        author = {**NAMED_OWNER, 'relation': 'internet-draft-author', 'relation_subject': 'draft-example-record-02',
                  'established_by': 'confirmed-with-the-person'}
        self.assertEqual(said(result_table.validate(row(initiation=author))['initiation']),
                         'Dana Example, an author of Internet-Draft `draft-example-record-02` '
                         '(confirmed with the person directly)')
        self.assertEqual(said(result_table.validate(row())['initiation']),
                         'A party who asked not to be named; no established link to the format')

    def test_authorship_of_a_draft_is_never_taken_from_a_public_record_of_an_account(self):
        claim = {**NAMED_OWNER, 'relation': 'internet-draft-author', 'relation_subject': 'draft-example-record-02'}
        with self.assertRaises(lib.ProposalError):
            result_table.validate(row(initiation=claim))

    def test_a_party_who_is_not_named_carries_no_name_and_no_repository(self):
        for leak in ({'initiated_by': 'Dana Example'}, {'relation_subject': 'acme/receipts'}):
            with self.subTest(leak=leak), self.assertRaises(lib.ProposalError):
                result_table.validate(row(initiation={'relation': 'repository-owner',
                                                      'established_by': 'github-public-record', **leak}))

    def test_a_row_is_agreed_only_when_the_author_agreed_it(self):
        with self.assertRaises(lib.ProposalError):
            result_table.validate(row(status='agreed', summary='Two cases.', initiation=NAMED_OWNER))
        with self.assertRaises(lib.ProposalError):
            result_table.validate(row(status='agreed', summary='Two cases.', author_review='not-applicable',
                                      initiation=NAMED_OWNER))
        result_table.validate(row(status='agreed', summary='Two cases.', author_review='row-agreed',
                                  initiation=NAMED_OWNER))

    def test_a_row_cannot_say_whether_a_format_meets_core_or_carry_markup(self):
        for text in ('The format conforms.', 'Certified.', 'An independent reproduction.',
                     'a | b', 'line\nbreak', '<b>x</b>', 'see `x`'):
            with self.subTest(text=text), self.assertRaises(lib.ProposalError):
                result_table.validate(row(summary=text))

    def test_the_pages_are_built_from_the_rows_and_the_committed_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            directory = new_proposal.build('sample-topic-001', 'Sample receipts', [PIN], 26, root, fetch=lambda pin: b'x')
            saved = row(summary='Two cases on one variable.', initiation=NAMED_OWNER,
                        author_spec_changes=[{'what': 'Clarified the binding rule.',
                                              'reference': 'https://github.com/acme/receipts/pull/7'}],
                        open_readings=[{'id': 'K2-scope', 'question': 'Does an excluded record count as supplied?',
                                        'core02_lines': [360, 642], 'cases': ['K2'], 'status': 'open'}])
            (directory / lib.RESULT_ROW).write_text(json.dumps(saved))
            pages = result_table.build(root)
            self.assertIn('No run committed', pages['RESULTS.md'])
            (directory / 'evidence').mkdir()
            (directory / 'evidence' / 'comparison.json').write_text(json.dumps({'cases': {
                'K1': {'expected_verdict': 'downgrade', 'wexp_ref_equals_expected': True, 'wexp_check_equals_expected': True},
                'K2': {'expected_verdict': 'accept', 'wexp_ref_equals_expected': True, 'wexp_check_equals_expected': False}}}))
            pages = result_table.build(root)
        results, readings = pages['RESULTS.md'], pages['OPEN-READINGS.md']
        self.assertIn('2 case(s); expected 1 accept, 1 downgrade; 1 of 2 equal the frozen expectation', results)
        self.assertIn('Dana Example, the owner of repository `acme/receipts` (GitHub public record); '
                      '[check 26](https://github.com/WEXP-dev/interop-test-lab/issues/26)', results)
        self.assertIn('| draft |', results)
        self.assertIn('Clarified the binding rule. ([reference](https://github.com/acme/receipts/pull/7))', results)
        self.assertIn('| `sample-topic-001/K2-scope` | Does an excluded record count as supplied? | 360, 642 |', readings)

    def test_the_committed_pages_of_this_repository_are_current(self):
        pages = result_table.build()
        for name, text in pages.items():
            self.assertEqual((lib.PROPOSALS / name).read_text(encoding='utf-8'), text)

    def test_archive_requests_go_to_one_host_for_validated_repository_names_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            (directory / 'SOURCE-PINS.json').write_text(json.dumps({'external_files': [
                {'repository': 'acme/receipts'}, {'repository': 'acme/receipts'}, {'repository': 'acme/other'}]}))
            self.assertEqual(request_archive.requests_for(directory), [
                'https://archive.softwareheritage.org/api/1/origin/save/git/url/https://github.com/acme/other/',
                'https://archive.softwareheritage.org/api/1/origin/save/git/url/https://github.com/acme/receipts/'])
            (directory / 'SOURCE-PINS.json').write_text(json.dumps({'external_files': [
                {'repository': 'acme/receipts/../../x?y=1'}]}))
            with self.assertRaises(lib.ProposalError):
                request_archive.requests_for(directory)


if __name__ == '__main__':
    unittest.main()
