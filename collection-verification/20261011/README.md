# Exact public migration commit: clean-clone verification

**PASS for commit [`15039dd52dce398a4ceb0ce74d67e947f9ea1e40`](https://github.com/WEXP-dev/wexp-interop/commit/15039dd52dce398a4ceb0ce74d67e947f9ea1e40).** The checked tree is `8bca460876b0fefbc48e90b9ffdce7d9fbf96583`. The historical public base is `d951b0b4170c3b169deb3cfe5ced85232a0a4f88`.

The run started at `2026-10-11T02:23:32.468359+00:00` and finished at `2026-10-11T02:23:37.932927+00:00`. It cloned the public repository through Git transport into a new directory. It did not copy an existing worktree or use a local bundle.

## Result and scope

| Check | Observed result |
| --- | --- |
| Every tracked file's checkout bytes, Git blob and mode projection | 193 passed |
| Archive payload file bytes, Git modes and POSIX permissions | 68 passed |
| Archive payload directories, including root | 27 checked |
| Earlier public main file blobs and Git modes retained | 69 passed |
| Payload paths with `text` unset | 68 |
| Declared archive permission projection | One: `MANIFEST.sha256` 0600 → Git 100644 → checkout 0644 |
| Original verifier | PASS; 67 manifest entries, 15 frozen identities, Branch A |
| Current catalog, collection, archive and freeze checks | PASS |
| Freeze bindings and additional checks | 11 + 3 passed |
| New local Markdown link targets | 51 checked |
| Whole-tree case/Unicode component collisions | None in the checked transforms |
| Working tree after checks | Clean |
| New WEXP or EMILIA implementation execution | False |
| New interoperability established | False |

The environment used Python 3.12.14 and Git 2.51.1. All Git commands explicitly used `core.autocrlf=true`, `core.filemode=true`, disabled system/global Git configuration and external attributes, and child-process umask `0022`. Installed dependency versions matched the checked commit's `requirements-verification.txt`; the exact versions are in [result.json](result.json).

The selected input was the [named ZIP from Zenodo record 22056151](https://zenodo.org/api/records/22056151/files/WEXP-EMILIA-INTEROP-001-PUBLICATION-CANDIDATE.zip/content): 200140 bytes, SHA-256 `f27b4ffc4259a91cdb11dd28424946612b723b0cffe62e588d1740c6a15c951f`. The expected SHA-256 is anchored in [public metadata at commit 4075939](https://github.com/WEXP-dev/wexp-interop/blob/4075939139d56b40e6e08788959de169559919af/PUBLICATION-METADATA.yaml), dated after the historical release. This check does not independently establish the release-day bytes or continuous non-replacement.

## Files

- [result.json](result.json) is the concise result, with the tested commit/tree, environment, checks, identities and limitations.
- [detail.json](detail.json) contains the complete listed checks, including per-file comparisons and validator outputs. Only execution-local paths have been replaced with named variables. Its SHA-256 is recorded in `result.json`.
- [verify_public_migration.py](verify_public_migration.py) is the exact driver executed. Its SHA-256 is `b2e7ef69a3f3f7aeafef21ee7d569664e116a9766ea69ad5ae79a25f58d73bff`.
- [MANIFEST.sha256](MANIFEST.sha256) covers the four other files in this directory; it excludes itself.

`detail.json` declares the path normalization operation. Hashes of stdout/stderr refer to the original streams before the displayed paths were normalized. The private raw journal's hash identifies that unnormalized counterpart; it supplies no additional authority or private evidence behind the public result. No mail, account screenshots or private research inputs are included in this verification carrier.

## Reproduce

Prepare the exact dependencies from [the checked requirements file](https://github.com/WEXP-dev/wexp-interop/blob/15039dd52dce398a4ceb0ce74d67e947f9ea1e40/requirements-verification.txt) in the selected Python environment, or in an external target passed with `--dependencies`. Download the named ZIP from the Zenodo link above. Use new output locations; the driver refuses to overwrite earlier runs.

```bash
python -B verify_public_migration.py \
  --commit 15039dd52dce398a4ceb0ce74d67e947f9ea1e40 \
  --expected-tree 8bca460876b0fefbc48e90b9ffdce7d9fbf96583 \
  --archive /absolute/path/to/WEXP-EMILIA-INTEROP-001-PUBLICATION-CANDIDATE.zip \
  --destination /absolute/path/to/new-clone \
  --report /absolute/path/to/new-run/raw-result.json \
  --artifacts /absolute/path/to/new-run/auxiliary \
  --public-summary /absolute/path/to/new-run/public/result.json \
  --public-detail /absolute/path/to/new-run/public/detail.json
```

## Evidence boundary and carrier

The result identifies the earlier commit it checked. A later evidence commit carries this directory; the result does not claim verification of its own carrier commit. A later changed source commit needs another check.

This is a publisher-controlled migration verification. It preserves and replays historical evidence; it is not a new implementation experiment, independent external reproduction, proof of interoperability, signature verification of the unsigned freeze, or validation of every historical claim. Remote URL availability was not checked by this driver. ZIP ordering, timestamps and full permission metadata remain properties of the authoritative ZIP, not the Git extraction.

The new driver is MIT-licensed; this new README is CC-BY-4.0. These declarations do not replace any historical payload, source archive or third-party license terms. See the collection's [license scope](../../LICENSES/README.md).
