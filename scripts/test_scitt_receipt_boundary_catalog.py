"""Read-only regressions for the SCITT receipt boundary package; no experiment execution.
SPDX-License-Identifier: MIT
"""
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from verify_scitt_receipt_boundary import ROOT, REL, verify_package


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
        self.edit_json('record.json', lambda d: d['status'].update(independent_reproduction='performed'))
        with self.assertRaisesRegex(ValueError, 'independence scope'):
            verify_package(self.package)

    def test_relabelled_comparison_refused(self):
        self.edit_json('payload/comparison.json', lambda d: d['cases']['a'].update(wexp_check_equals_expected=False))
        with self.assertRaisesRegex(ValueError, 'source bytes differ'):
            verify_package(self.package)


if __name__ == '__main__':
    unittest.main()
