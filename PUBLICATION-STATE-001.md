# Publication state on `main`

`MANIFEST.sha256` in this repository is the **frozen candidate manifest**. Its
own SHA-256, `4172c2d0d9f4cfaddaa4036a7d92e53d1ee6c2c290654daedaa5806e5281ad6a`,
is the externally pinned root-manifest identity recorded in
`WEXP-EMILIA-INTEROP-001-PUBLICATION-CANDIDATE-FREEZE-002.yaml` and deposited
with the archive at Zenodo under `10.5281/zenodo.22056151`.

That identity is not regenerated here, and it never will be. Regenerating it
would silently retire an identity that external records already cite.

## Why some files on `main` no longer match it

`README.md` and `PUBLICATION-METADATA.yaml` described the record as an
unpublished local candidate: no tag created, no release performed, publication
pending. Every one of those statements was true when the candidate was frozen
and false the moment the record was published. Leaving them in place would have
made this repository's landing surface contradict its own release.
`CITATION.cff` carried no DOI, version or release date, because there were none
to carry at freeze time.

All three were corrected forward. Their bytes therefore differ from the digests
the frozen manifest holds for them, and the divergence is recorded here rather
than absorbed into a new manifest.

| File | Digest in the frozen manifest | Digest on `main` |
| --- | --- | --- |
| `CITATION.cff` | `c1b3b19229acf910b1fa5a98ce5baf17b0b2a9a9090889abe86a2c6965de17e1` | `9e3bd73c531c4acc197300b5d3c391a950d2a5f5a65c36f37c6faf08a95776a3` |
| `PUBLICATION-METADATA.yaml` | `39eaec8f41c4631543871f3d1ae60a5aa8178d3e217e119a54f92418749abf0f` | `45885e423193ebadb83f34c80e1941e38e13c7b01ea1f38c89ced69e4e10f73d` |
| `README.md` | `1d1a02d5369f6d8c88ebf1c5f1ce06e07e62fabfb9408f11d305a4f2605f8065` | `deefb858cdb662e7eec0c936d1e105cda2cc94615a68cf8de5f9c32e4cbad43c` |

Nothing else diverges. Every other entry in `MANIFEST.sha256` still matches its
frozen digest on `main`.

## What this does not change

- **No evidence byte moved.** Every frozen reading, expectation, fixture,
  receipt, comparison and record is byte-identical to the published archive.
  The fifteen frozen identities `reproduction/verify_final.py` checks are
  untouched.
- **No claim changed.** The terminal result remains Branch A — Explicit Bridge
  Required. Every non-claim still holds: no certification, no WEXP validation
  of EMILIA, no semantic equivalence, no IETF adoption, no universal
  interoperability.
- **No external identity was invalidated.** The tag, the release assets, the
  root-manifest hash and the DOI all still resolve to exactly the bytes they
  always did.

## Where to verify

Against the published archive, not against a checkout of this repository:

```sh
python3 -B reproduction/verify_final.py \
  --manifest-sha256 4172c2d0d9f4cfaddaa4036a7d92e53d1ee6c2c290654daedaa5806e5281ad6a
```

A checkout was never the verification surface. The root manifest covers the
payload exactly, and a checkout carries `.git`, so the verifier refuses it —
before these corrections as well as after them.
