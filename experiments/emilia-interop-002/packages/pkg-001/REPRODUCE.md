# Reproduce the INTEROP-002 preservation checks

Run from the collection root on a POSIX host with Python 3.12. Install the exact dependencies in `requirements-verification.txt` into a fresh virtual environment as shown in the root README. Commands below assume that environment is active. Report directories must be new; existing observations are never overwritten.

```sh
python3 -B scripts/catalog.py --check
python3 -B scripts/verify_collection.py
emilia002_output_root=$(mktemp -d)
python3 -B scripts/verify_emilia.py --package emilia-interop-002/pkg-001 --out "$emilia002_output_root/replay"
```

The third command checks:

- the archive identity (192089 bytes, SHA-256 `37412ba5…770e`) and a structural inspection of all 57 members: names, collisions, no directory entries, and every mode `0644` without a file-type bit;
- all 57 extracted file bytes, the file set and the implicit directory set of `payload/`;
- the candidate's internal manifest: 56 entries by bytes and SHA-256; the manifest is the only file it excludes;
- the pinned verdict record and its two scopes: bridge sufficiency `SUPPORTED`; joint comparison `INCONCLUSIVE` for H-01-b, H-01-c, H-02, H-03 and B-01, `NOT_DERIVED_UNDER_THIS_ORDER` for C-00 and H-01-a; and their agreement with the internal manifest;
- that the historical execution record still reads `EXECUTED`.

It executes no archived code. Expected summary: `payload_files_identical: 57`, `internal_manifest_entries_verified: 56`, `split_verdict_checked: true`, `implementation_execution_performed: false`.

`scripts/verify_collection.py` separately checks that the card's `verdict_record` digest, JSON pointer and both scope verdicts match the archived record.

Without `--package`, `scripts/verify_emilia.py` checks INTEROP-001 exactly as before. A PASS concerns preserved bytes and recorded relationships only. It is not a new run, an external reproduction or a statement about the truth of the result.
