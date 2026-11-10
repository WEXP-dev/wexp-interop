"""Read-only regressions for the SCITT receipt boundary package; no experiment execution.
SPDX-License-Identifier: MIT
"""
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from verify_scitt_receipt_boundary import EXTERNAL_REPRODUCTION_DIR, ROOT, REL, verify_package


class PackageEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='scitt-pkg-')
        self.addCleanup(self.tmp.cleanup)
        self.package = Path(self.tmp.name) / 'pkg-001'
        shutil.copytree(ROOT / REL, self.package)

    def edit_json(self, rel, fn):
        p = self.package / rel
        data = json.loads(p.read_bytes())
        fn(data)
        p.write_text(json.dumps(data) + '\n')

    def test_saved_evidence_only(self):
        result = verify_package(self.package)
        self.assertEqual(result['cases'], 4)
        self.assertFalse(result['new_experiment_execution_performed'])

    def test_payload_tampering_refused(self):
        p = self.package / 'payload/expectations/a.json'
        p.write_bytes(p.read_bytes() + b'\n')
        with self.assertRaisesRegex(ValueError, 'source bytes differ'):
            verify_package(self.package)

    def test_rehashed_inventory_not_trusted(self):
        self.edit_json('evidence/SOURCE-MANIFEST.json', lambda d: d.update(files=[]))
        with self.assertRaisesRegex(ValueError, 'reviewed pin'):
            verify_package(self.package)

    def test_archive_corruption(self):
        p = self.package / 'source-archive/scitt-receipt-boundary-001-run-materials.zip'
        p.write_bytes(p.read_bytes() + b'x')
        with self.assertRaisesRegex(ValueError, 'archive identity'):
            verify_package(self.package)

    def test_extra_payload(self):
        (self.package / 'payload/EXTRA').write_text('x')
        with self.assertRaisesRegex(ValueError, 'file set'):
            verify_package(self.package)

    def test_false_independence(self):
        # `performed` without the external reproduction evidence is refused.
        shutil.rmtree(self.package / EXTERNAL_REPRODUCTION_DIR)
        self.edit_json('record.json', lambda d: d['status'].update(independent_reproduction='performed'))
        with self.assertRaisesRegex(ValueError, 'independence scope changed: external reproduction evidence absent'):
            verify_package(self.package)

    def test_unknown_independence_value_refused(self):
        self.edit_json('record.json', lambda d: d['status'].update(independent_reproduction='partial'))
        with self.assertRaisesRegex(ValueError, 'independence scope changed'):
            verify_package(self.package)

    def test_external_reproduction_checked(self):
        result = verify_package(self.package)
        self.assertTrue(result['external_reproduction_checked'])

    def test_missing_external_evidence_refused(self):
        (self.package / EXTERNAL_REPRODUCTION_DIR / 'job-129779506462.log').unlink()
        with self.assertRaisesRegex(ValueError, 'evidence absent: job-129779506462.log'):
            verify_package(self.package)

    def test_changed_external_evidence_refused(self):
        p = self.package / EXTERNAL_REPRODUCTION_DIR / 'pkg-001-comparison.extracted-from-log.json'
        data = json.loads(p.read_bytes())
        data['cases']['a']['wexp_check_observed']['verdict'] = 'accept'
        p.write_text(json.dumps(data, indent=1, sort_keys=True) + '\n')
        with self.assertRaisesRegex(ValueError, 'evidence differs: pkg-001-comparison'):
            verify_package(self.package)

    def test_changed_external_note_refused(self):
        p = self.package / EXTERNAL_REPRODUCTION_DIR / 'NOTE.md'
        p.write_bytes(p.read_bytes() + b'x')
        with self.assertRaisesRegex(ValueError, 'evidence differs: NOTE.md'):
            verify_package(self.package)

    def test_extra_external_evidence_refused(self):
        (self.package / EXTERNAL_REPRODUCTION_DIR / 'EXTRA.txt').write_text('x')
        with self.assertRaisesRegex(ValueError, 'external reproduction file set'):
            verify_package(self.package)

    def test_relabelled_observed_result_refused(self):
        p = self.package / 'evidence/comparison.json'
        data = json.loads(p.read_bytes())
        data['cases']['a']['wexp_ref_observed']['verdict'] = 'accept'
        p.write_text(json.dumps(data, indent=1, sort_keys=True) + '\n')
        with self.assertRaisesRegex(ValueError, 'reviewed pin'):
            verify_package(self.package)

    def test_altered_run_record_refused(self):
        self.edit_json('evidence/RUN-RECORD.json', lambda d: d['engines']['wexp_ref'].update(commit='0' * 40))
        with self.assertRaisesRegex(ValueError, 'reviewed pin'):
            verify_package(self.package)

    def test_relabelled_comparison_refused(self):
        self.edit_json('payload/comparison.json', lambda d: d['cases']['a'].update(wexp_check_equals_expected=False))
        with self.assertRaisesRegex(ValueError, 'source bytes differ'):
            verify_package(self.package)


if __name__ == '__main__':
    unittest.main()
