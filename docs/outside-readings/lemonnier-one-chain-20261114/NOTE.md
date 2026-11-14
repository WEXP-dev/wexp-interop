# A reading of the one-chain Signed Statements of dps-scitt-decision-layer

Reader: Mikhail Sergeev. Date: 14 November 2026 (IETF 127 Hackathon).
Records: github.com/Laurent-Lemonnier/dps-scitt-decision-layer at
21cf862c1ed6c70349cf7ad29654b56b839abb46, folder `interop/one-chain/registration/`.

## What is here

- `laurent_identity_check.py`: for each of the five Signed Statements, the SHA-256 of the file, the entry id
  SHA-256(0x00 || file), the SHA-256 of the Sig_structure (RFC 9052 Section 4.4), the Ed25519 signature check under
  the published issuer key, and the identifier of the audit-coverage fixture.
- `laurent_payload_check.py`: each payload compared with the files of `interop/one-chain/out/positive/`.
- `identity-check.json`: the output of the first script.
- `run.log`, `run-tail.log`: an outside run of `interop/run.sh` at the same commit (Linux, Python 3.13.18).

Both scripts load the CBOR decoder, the encoder and `statement_id` from `run_demo.py` of ietf-wg-scitt/examples
pull request 5 at c6bcf5c2b7a28cc8df7640d1814e9b1409d32add. They use none of the code of the repository read.

## Commands

    python3 -I laurent_identity_check.py <run_demo.py> <registration folder> identity-check.json
    python3 -I laurent_payload_check.py <run_demo.py> <registration folder> <out/positive folder>

Needs the `cryptography` package (50.0.1 here).

## Limits

The README of the registration folder was read before the scripts were written: the reading is not blind.
No receipt was fetched or checked. This is not a verifier of draft-lemonnier-scitt-decision-provenance-01.
The run of `interop/run.sh` is a replay of the author's procedure, not an independent implementation; it stopped
at the Izmaylov step because the reader's environment refused one download (HTTP 403), and the sections after
that step were run separately (`run-tail.log`).

AI assistance was used to prepare the scripts and this note.

In the two logs the path of the reader's clone is replaced by `<clone>`; nothing else in them is edited.
