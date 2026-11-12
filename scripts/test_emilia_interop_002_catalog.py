"""Read-only regressions for card schema 0.4.0 and the EMILIA INTEROP-002 package; no experiment execution.
SPDX-License-Identifier: MIT
"""
import io
import json
from contextlib import redirect_stdout
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

from catalog import ROOT, load_records
from verify_collection import execute
import verify_emilia

REL = 'experiments/emilia-interop-002/packages/pkg-001'


class SplitVerdictCardTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='emilia-002-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'collection'
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns('.git', '__pycache__'))
        self.card = self.root / REL / 'record.json'

    def edit(self, fn):
        data = json.loads(self.card.read_bytes())
        fn(data)
        self.card.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')

    def test_card_loads_as_0_4_0(self):
        versions = {d['experiment_id']: d['schema_version'] for _, d in load_records(self.root)}
        self.assertEqual(versions['emilia-interop-002'], '0.4.0')

    def test_split_verdict_requires_verdict_record(self):
        self.edit(lambda d: d['result'].pop('verdict_record'))
        with self.assertRaisesRegex(ValueError, 'verdict_record'):
            load_records(self.root)

    def test_verdict_record_only_with_split_verdict(self):
        self.edit(lambda d: d['status'].update(comparison='not-evaluated'))
        with self.assertRaisesRegex(ValueError, 'split-verdict'):
            load_records(self.root)

    def test_split_verdict_absent_in_0_3_0(self):
        self.edit(lambda d: d.update(schema_version='0.3.0'))
        with self.assertRaises(ValueError):
            load_records(self.root)

    def test_missing_license_cannot_be_published(self):
        self.edit(lambda d: d['status'].update(publication='published'))
        with self.assertRaisesRegex(ValueError, 'prepared'):
            load_records(self.root)

    def test_card_verdict_must_match_record(self):
        def change(d):
            d['result']['verdict_record']['scopes'][1]['verdict'] = 'INCONCLUSIVE'
        self.edit(change)
        with self.assertRaisesRegex(ValueError, 'generated catalog drift|card verdict differs'):
            execute(self.root)

    def test_verdict_record_digest_pinned(self):
        self.edit(lambda d: d['result']['verdict_record'].update(sha256='0' * 64))
        with self.assertRaisesRegex(ValueError, 'generated catalog drift|digest mismatch'):
            execute(self.root)


class ReplayTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='emilia-002-replay-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'collection'
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns('.git', '__pycache__'))

    def replay(self):
        out = Path(self.tmp.name) / 'out'
        argv = sys.argv
        sys.argv = ['verify_emilia.py', '--root', str(self.root), '--out', str(out),
                    '--package', 'emilia-interop-002/pkg-001']
        try:
            with redirect_stdout(io.StringIO()):
                code = verify_emilia.main()
        finally:
            sys.argv = argv
        return code, json.loads((out / 'verification.json').read_text())

    def test_replay_passes(self):
        code, report = self.replay()
        self.assertEqual(code, 0, report.get('error'))
        self.assertFalse(report['summary']['implementation_execution_performed'])

    def test_payload_tampering_refused(self):
        p = self.root / REL / 'payload/fixtures/B-01.json'
        p.write_bytes(p.read_bytes() + b'\n')
        code, report = self.replay()
        self.assertEqual(code, 1)
        self.assertIn('mismatch', report['error'])

    def test_extra_payload_directory_refused(self):
        (self.root / REL / 'payload/extra').mkdir()
        code, report = self.replay()
        self.assertEqual(code, 1)
        self.assertIn('directory-set', report['error'])


if __name__ == '__main__':
    unittest.main()
