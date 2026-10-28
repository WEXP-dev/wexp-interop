"""Negative controls for saved-evidence integrity; no producer execution."""
from pathlib import Path
import shutil
import tempfile
import unittest
import verify_evidence as v

ROOT = Path(__file__).resolve().parent
PIN = '2a3a0f8a375f7f5eb01419f737502b9f6b35f426f2ee743307799e0cbbe67781'


class EvidenceControls(unittest.TestCase):
    def test_wrong_record_pin(self):
        with self.assertRaisesRegex(ValueError, 'external pin'):
            v.verify(ROOT / 'evidence/run-001/RECORD.json', '0' * 64)

    def test_modified_archive(self):
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp) / 'evidence'
            shutil.copytree(ROOT / 'evidence/run-001', destination)
            path = destination / 'push-python312.zip'
            raw = bytearray(path.read_bytes()); raw[-1] ^= 1
            path.write_bytes(raw)
            with self.assertRaisesRegex(ValueError, 'archive identity'):
                v.verify(destination / 'RECORD.json', PIN)

    def test_strict_json(self):
        for text in ('{"a":1,"a":2}', '1e9999', '-1e9999', 'NaN'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                v.load(text)

    def test_duplicate_set_is_not_normalized_away(self):
        with self.assertRaisesRegex(ValueError, 'duplicate set'):
            v.logical({'supported_claims': [{'base':'observation'}, {'base':'observation'}]})

    def test_boolean_number_and_atom_order(self):
        self.assertNotEqual(v.encode(v.logical({'v':True})), v.encode(v.logical({'v':1})))
        self.assertNotEqual(v.logical({'basis_refs':[['p','x']]}), v.logical({'basis_refs':[['x','p']]}))
        self.assertEqual(v.logical({'reasons':['a','b']}), v.logical({'reasons':['b','a']}))


if __name__ == '__main__':
    unittest.main()
