# Fresh public clone check — WIMSE AAR candidate B

**PASS for the exact public candidate B commit tested.** This is a read-only
verification of the supplied package and saved observations, performed in the
publisher-controlled environment after the package commit became public.

| Bound item | Identity |
|---|---|
| Repository | https://github.com/WEXP-dev/wexp-interop |
| Tested candidate B | `73ab5d5d6bfe5c2f61068be4d8245d31e968ee4e` |
| Tested tree | `ff1d7e8f12518895282740e20ad92bd52d054886` |
| Public pre-run commit | `70b4491a1ec8aab5af61f31510220067e3e5cfba` |
| Preserved collection migration | `b368b807195bbff578191ce2e2a6ac64f13646ae` |
| AAR ZIP SHA-256 | `fa42df4c859e744f199691a5f071f52a8e7102267dddeded95b68462843d2d20` |
| Driver SHA-256 | `8e6dc8acffe21b7745faa3a7d25859b886fcd5c8348e87bcb8b7b3cba99c7e10` |
| Started, UTC | 2026-10-11T03:22:57.884000+00:00 |
| Finished, UTC | 2026-10-11T03:23:05.365868+00:00 |

## What was checked

A new Git transport clone used isolated global/system Git configuration,
`core.autocrlf=true`, `core.filemode=true`, disabled global/system attributes,
and child-process umask `0022`. All **447** tracked
files matched their Git blob bytes and actual POSIX mode, and all had `text`
unset. The checkout was clean before and after verification. No file/directory,
casefold, NFC, NFD or combined normalization collision was found within the
checked path inventory.

All **172** files in the EMILIA subtree were
identical to the already published collection migration. All
**205** AAR files from the public pre-run
commit were preserved. The exact AAR archive contained
**240** regular files: the frozen
`PREPARATION.md` and **239** files under
`payload/`. ZIP content, inventory, CRCs and executable-bit projection matched
the public checkout.

The catalog, collection/package manifests/local links, EMILIA archive/freeze
and archived verifier, final AAR package verifier, frozen-input verifier and
strict saved-result comparator all passed. The comparator checked the saved
**130** pipeline cases,
**16** output-mutation inputs and
**2** controlled worlds against the
previously fixed reference. The original EMILIA verifier remained within its
archived-evidence scope. Runtime executable hashes, declared installed
dependency file inventories and all command observations are retained in the
detailed report.

## What this observation establishes

This check did **not** rerun the AAR pilot, producer, recipient, native verifier,
fixture generator, probes or controlled-world operations. The saved pilot run
and this later verification are different observations. A verification PASS
checks byte identities and the stated recorded relationships; it does not
authenticate the truth of producer assertions, execution timestamps or human
oversight. It does not establish external-team reproduction, a blind experiment,
certification or new interoperability.

This result applies to candidate B identified above. The later commit carrying
these five evidence files is a separate carrier and is **not** the commit this
report claims to verify. Any subsequent commit needs a separate observation
before it can be described as having passed this exact-commit check.

## Files and normalization

- [result.json](result.json): compact result, exact tested identities and limits.
- [detail.json](detail.json): complete checked inventories, command stdout/stderr,
  stream hashes, timestamps, exit codes and verification results.
- [verify_public_aar.py](verify_public_aar.py): the exact external driver used.
- [MANIFEST.sha256](MANIFEST.sha256): hashes of the other four files, excluding
  the manifest itself.

The public detail replaces only execution-local checkout, output, dependency
and Python paths with declared placeholders. Command stream hashes identify
the original retained bytes **before** those displayed paths were normalized.
The raw report SHA-256 is `5eacc37dc402d961f1974ae038bea353df9234890b9d39b9318651ffb84f0ec0`. The raw version adds
only those original execution paths; it supplies no private evidence or extra
authority. This procedure contains no account screenshots or private mail.

## Repeat this verification

Use Python 3.12 and install the exact versions from the tested repository's
`requirements-verification.txt` into a dependency directory outside the new
clone. The recorded runtime was CPython 3.12.14. Obtain this driver from its
identified evidence carrier, check its SHA-256 above, and use fresh output paths:

```sh
python3 -B verify_public_aar.py \
  --commit 73ab5d5d6bfe5c2f61068be4d8245d31e968ee4e \
  --expected-tree ff1d7e8f12518895282740e20ad92bd52d054886 \
  --pre-run-commit 70b4491a1ec8aab5af61f31510220067e3e5cfba \
  --aar-zip-sha256 fa42df4c859e744f199691a5f071f52a8e7102267dddeded95b68462843d2d20 \
  --destination ./aar-public-clone \
  --artifacts ./aar-check-artifacts \
  --report ./aar-check-raw.json \
  --public-detail ./aar-check-detail.json \
  --public-summary ./aar-check-result.json \
  --dependencies ./verification-dependencies
```

Every named destination/output must be new. The driver performs no dependency
installation and does not overwrite prior observations. It does not check
remote link availability, GitHub/Zenodo publication state or organization
integration settings; those are separate publication observations.
