# WEXP × EMILIA INTEROP-001 — pkg-001

**Recorded result: Branch A — Explicit Bridge Required.** The historical controlled-fixture experiment reproduced EMILIA's P/P-1 distinction; the frozen WEXP surface did not supply a sufficient EP-to-WEXP mapping. The [archived result record](payload/records/TERMINAL-BRANCH-SELECTION-001.json) remains unchanged.

This card locates the existing publication in the common collection. The migration checks archive bindings, file bytes and recorded relationships. It does not add an implementation execution or a new interoperability result.

| Dimension | Value | Scope |
|---|---|---|
| Integrity | `verified` | Selected archive, freeze, extraction and retained evidence identities. |
| Execution | `archived-evidence-replayed` | `implementation_execution_performed: false` for the migration checks. |
| Independent reproduction | `not-performed` | No separate external reproduction of the complete collection package is claimed. |
| Comparison | `explicit-bridge-required` | Historical Branch A, not semantic equivalence or conformance. |
| Publication | `published` | Existing GitHub release and Zenodo version record dated 22 August 2026. |

The [machine-readable card](record.json) uses the [collection's fixed definitions](../../../../docs/COLLECTION.md). The narrower historical contributor roles, separately frozen readings and EMILIA-side execution evidence are preserved in [the commitment record](payload/records/COMMIT-REVEAL-RECORD.md) and [execution verification record](payload/records/EMILIA-EXPECTATION-EXECUTION-VERIFICATION-001.md). Those records are not promoted into a new external reproduction claim.

## Exact published object and extracted view

The selected authoritative object is the [original ZIP](source-archive/WEXP-EMILIA-INTEROP-001-PUBLICATION-CANDIDATE.zip) from [Zenodo version record 22056151](https://zenodo.org/records/22056151):

```text
Bytes:   200140
SHA-256: f27b4ffc4259a91cdb11dd28424946612b723b0cffe62e588d1740c6a15c951f
MD5:     b1bc67411d64ff80f5f1a19823a68fe0
```

[SOURCES.json](evidence/SOURCES.json) identifies the named Zenodo file, its checksum, the copied GitHub asset comparison and the separate source of the expected SHA-256. The public SHA-256 source is [commit 4075939](https://github.com/WEXP-dev/wexp-interop/blob/4075939139d56b40e6e08788959de169559919af/PUBLICATION-METADATA.yaml), dated **23 August 2026**, after publication. Matching it establishes correspondence with that public pin; it does not independently establish the release-day bytes or exclude intermediate asset replacement.

`payload/` contains the 68 unmodified regular-file byte sequences extracted from that ZIP, with the outer container directory removed. It is an extraction, not the original ZIP byte stream. The source archive preserves ordering, timestamps, explicit directory entries and other container metadata.

The root `MANIFEST.sha256` has archive permissions `0600`; Git represents it as `100644`. An ordinary POSIX checkout under `umask 0022` yields `0644`. The other 67 regular files also use Git mode `100644`. [Reproduction instructions](REPRODUCE.md) cover both byte checks and the separate fresh-clone mode check.

## Freeze and migration evidence

[FREEZE-002](source-archive/WEXP-EMILIA-INTEROP-001-PUBLICATION-CANDIDATE-FREEZE-002.yaml) is an **unsigned inventory and transcription-correction record**. Its archive, manifest and corrected-digest bindings are checked by the [published verifier](../../../../scripts/emilia/verify_freeze_bindings.py). It contains no signature or trusted timestamp; a PASS does not establish authorship, historical review or factual truth.

The [evidence guide](evidence/README.md) exposes source acquisition, the public hash anchor, archive inspection, freeze replay, negative controls and extraction results. Account settings and private correspondence are not dependencies of this card.

The original [verify_final.py](payload/reproduction/verify_final.py) is unmodified. It checks 67 root-manifest entries, 15 frozen identities and recorded relationships, preserving Branch A. It does not check all POSIX permissions or execute a WEXP/EMILIA implementation. Fresh-clone reports identify the exact tested Git commit and stay outside that commit to avoid a circular hash reference.

## Publication state and preserved history

Use [CITATION.cff](CITATION.cff) and version DOI [10.5281/zenodo.22056151](https://doi.org/10.5281/zenodo.22056151). Concept DOI `10.5281/zenodo.22056150` describes this EMILIA record's version family, not the collection or another experiment. The original `wexp-emilia-interop-001` tag and release are retained.

The payload's pre-publication fields, including `publication_performed: false`, are preserved as historical bytes. Four later publication documents from [the previous public main](publication-history/d951b0b4170c3b169deb3cfe5ced85232a0a4f88/) remain byte-for-byte in `publication-history/`. Their old root paths and intermediate checksum table are historical, not current navigation or a current checksum ledger. All 69 files from that prior main are retained: 65 in payload and those four in publication history.

The archive establishes composition and original recorded results; publication-system metadata establishes the identified publication event; this external card records location and checked relationships. Neither the archive nor the card establishes the truth of a claim merely by containing it.

## License and boundaries

See [LICENSE-SCOPE.md](LICENSE-SCOPE.md). The archive's Apache-2.0 contribution terms and background-material qualifications remain in force. The surrounding collection license does not override them.

The publication establishes no physical-truth claim, semantic equivalence, full interoperability, positive WEXP appraisal, conformance, IETF adoption or endorsement. These boundaries survive the repository migration.
