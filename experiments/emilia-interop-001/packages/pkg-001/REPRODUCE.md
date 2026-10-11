# Reproduce the EMILIA preservation checks

Run from the collection root on a POSIX host with Git and Python 3.12. Install the exact dependencies in `requirements-verification.txt` into a fresh virtual environment as shown in the root README. Commands below assume that environment is active. Report directories must be new; existing observations are never overwritten.

## Collection and archived evidence

```sh
python3 -B scripts/catalog.py --check
python3 -B scripts/verify_collection.py
emilia_output_root=$(mktemp -d)
python3 -B scripts/verify_emilia.py --out "$emilia_output_root/replay"
```

This checks the independently pinned source identities, ZIP names/types/collisions, all 68 extracted file bytes, the freeze's 11 historical and three additional bindings, and the unchanged archived verifier. Expected scope: 67 manifest entries, 15 frozen identities, `A — EXPLICIT BRIDGE REQUIRED`, `implementation_execution_performed: false`.

The public expected SHA-256 source is [PUBLICATION-METADATA.yaml at commit 4075939](https://github.com/WEXP-dev/wexp-interop/blob/4075939139d56b40e6e08788959de169559919af/PUBLICATION-METADATA.yaml). The pinned copy has SHA-256 `45885e423193ebadb83f34c80e1941e38e13c7b01ea1f38c89ced69e4e10f73d` and Git blob `ae90a4ab9331d986d163c0f6db18cd9201ff5d61`. It is a public post-publication source, not a trusted timestamp or proof of continuous asset non-replacement.

## Fresh Git clone of the exact commit

```sh
emilia_clone_root=$(mktemp -d)
emilia_checked_commit=$(git rev-parse HEAD)
python3 -B scripts/emilia/verify_clean_clone.py \
  --repository "$PWD" \
  --commit "$emilia_checked_commit" \
  --archive experiments/emilia-interop-001/packages/pkg-001/source-archive/WEXP-EMILIA-INTEROP-001-PUBLICATION-CANDIDATE.zip \
  --destination "$emilia_clone_root/clone" \
  --report "$emilia_clone_root/clean-clone.json"
```

This uses an actual `git clone --no-local --no-checkout`, then checks out the exact requested commit. It avoids local object hardlink reuse and does not copy the working tree. For a remote publication check, replace `--repository "$PWD"` with `--repository https://github.com/WEXP-dev/wexp-interop.git` and supply the published exact commit. A branch or moving tag is not accepted as the requested commit.

The procedure checks that the preserved old main `d951b0b4170c3b169deb3cfe5ced85232a0a4f88` is an ancestor, verifies all 69 earlier file blobs and modes at their declared destinations, compares the 68 archive file bytes, checks 27 directories, enforces `text: unset` with `core.autocrlf=true`, and separately records actual POSIX modes with child-process `umask 0022`. It runs the pinned archived verifier only after its bytes and payload have matched.

A successful report is about that exact commit. A later commit, including a different merge commit, must be checked separately. The report belongs outside its tested commit; CI artifacts or a later evidence record can carry it without a circular identity claim.

## Freeze negative controls

```sh
emilia_controls_root=$(mktemp -d)
python3 -B scripts/emilia/run_freeze_negative_checks.py \
  --verifier scripts/emilia/verify_freeze_bindings.py \
  --archive experiments/emilia-interop-001/packages/pkg-001/source-archive/WEXP-EMILIA-INTEROP-001-PUBLICATION-CANDIDATE.zip \
  --freeze experiments/emilia-interop-001/packages/pkg-001/source-archive/WEXP-EMILIA-INTEROP-001-PUBLICATION-CANDIDATE-FREEZE-002.yaml \
  --metadata experiments/emilia-interop-001/packages/pkg-001/evidence/historical-preparation/expected-sha-source-PUBLICATION-METADATA.yaml \
  --metadata-sha256 45885e423193ebadb83f34c80e1941e38e13c7b01ea1f38c89ced69e4e10f73d \
  --metadata-git-blob ae90a4ab9331d986d163c0f6db18cd9201ff5d61 \
  --metadata-source-url https://github.com/WEXP-dev/wexp-interop/blob/4075939139d56b40e6e08788959de169559919af/PUBLICATION-METADATA.yaml \
  --manifest-member WEXP-EMILIA-INTEROP-001-PUBLICATION-CANDIDATE/MANIFEST.sha256 \
  --out-dir "$emilia_controls_root/controls"
```

Expected outcome: eight inputs rejected for the specified reasons. This is a bounded control set, not an exhaustive proof about every malformed ZIP/YAML input. The [historical evidence guide](evidence/README.md) retains the earlier fixture correction and both original control runs.
