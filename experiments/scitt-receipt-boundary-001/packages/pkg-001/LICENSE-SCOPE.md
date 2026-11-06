# License and attribution scope

The external card, reproduction instructions and metadata of this package follow the collection's [license scope](../../../../LICENSES/README.md): newly authored collection verification code is MIT; new collection prose is CC BY 4.0.

`payload/` is the frozen case directory from the WEXP workspace. Its harness and comparison code (`run_case.py`, `harness/run_emulator.sh`, `harness/shim/`) were written for the case under Apache-2.0; its prose (mapping, source pin, README, derivation) is CC BY 4.0. The Signed Statement and Receipt bytes under `payload/artifacts/` were produced by running the pinned `scitt-community/scitt-api-emulator` (MIT) and carry no license text of their own; the emulator source is not copied here, only pinned. Quotations from RFC 9943 and from `draft-sergeev-wexp-core-02` retain the IETF Trust terms of those documents; no specification text is included beyond short quotations.

Attribution: WEXP-dev contributors. The SCITT API emulator retains its upstream authorship (scitt-community; principal contributor John Andersen). No independent review, IETF endorsement or certification is implied.
