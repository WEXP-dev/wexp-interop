"""Read-only metadata and evidence regressions; no experiment execution.
SPDX-License-Identifier: MIT
"""
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from catalog import load_records
from verify_wimse_core02 import ROOT, REL, verify_package


class CatalogAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='wimse-catalog-')
        self.addCleanup(self.tmp.cleanup)
        self.package = Path(self.tmp.name) / 'pkg-002'
        shutil.copytree(ROOT / REL, self.package)

    def edit(self, rel, fn):
        p = self.package / rel
        data = json.loads(p.read_bytes())
        fn(data)
        p.write_text(json.dumps(data) + '\n')

    def test_saved_evidence_only(self):
        result = verify_package(self.package)
        self.assertEqual(result['cases_per_original_run'], 130)
        self.assertFalse(result['new_experiment_execution_performed'])

    def test_source_tampering_refused_before_import(self):
        marker = Path(self.tmp.name) / 'EXECUTED'
        (self.package / 'payload/verify_evidence.py').write_text(
            f'from pathlib import Path\nPath({str(marker)!r}).touch()\n')
        with self.assertRaisesRegex(ValueError, 'source bytes differ'):
            verify_package(self.package)
        self.assertFalse(marker.exists())

    def test_rehashed_inventory_not_trusted(self):
        self.edit('evidence/SOURCE-MANIFEST.json', lambda d: d.update(files=[]))
        with self.assertRaisesRegex(ValueError, 'reviewed pin'):
            verify_package(self.package)

    def test_archive_corruption(self):
        p = self.package / 'source-archive/push-python312.zip'
        p.write_bytes(p.read_bytes() + b'x')
        with self.assertRaisesRegex(ValueError, 'archive identity'):
            verify_package(self.package)

    def test_saved_record_relabeling(self):
        self.edit('source-archive/RECORD.json', lambda d: d.update(cases_per_run=131))
        with self.assertRaisesRegex(ValueError, 'reviewed pin'):
            verify_package(self.package)

    def test_false_new_execution(self):
        self.edit('evidence/ADMISSION.json', lambda d: d.update(new_experiment_execution_performed=True))
        with self.assertRaisesRegex(ValueError, 'admission scope'):
            verify_package(self.package)

    def test_false_independence(self):
        self.edit('record.json', lambda d: d['status'].update(independent_reproduction='performed'))
        with self.assertRaisesRegex(ValueError, 'scope'):
            verify_package(self.package)

    def test_extra_payload(self):
        (self.package / 'payload/EXTRA').write_text('x')
        with self.assertRaisesRegex(ValueError, 'file set'):
            verify_package(self.package)

    def test_old_and_new_card_versions(self):
        records = load_records(ROOT)
        self.assertEqual(len(records), 3)
        versions = {d['package_id'] + ':' + d['experiment_id']: d['schema_version'] for _, d in records}
        self.assertEqual(versions['pkg-001:emilia-interop-001'], '0.1.0')
        self.assertEqual(versions['pkg-001:wimse-aar-02-interop-001'], '0.1.0')
        self.assertEqual(versions['pkg-002:wimse-aar-02-interop-001'], '0.2.0')

    def test_unknown_schema_rejected(self):
        isolated = Path(self.tmp.name) / 'collection'
        shutil.copytree(ROOT / 'schemas', isolated / 'schemas')
        folder = isolated / REL
        folder.mkdir(parents=True)
        card = json.loads((self.package / 'record.json').read_bytes())
        card['schema_version'] = '999'
        (folder / 'record.json').write_text(json.dumps(card))
        with self.assertRaisesRegex(ValueError, 'unsupported package card'):
            load_records(isolated)


if __name__ == '__main__':
    unittest.main()
