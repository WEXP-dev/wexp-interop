# Collection structure and card contract

The collection uses one hierarchy for every experiment:

```text
experiments/<experiment-id>/packages/<package-id>/
  README.md
  record.json
  CITATION.cff
  LICENSE-SCOPE.md
  REPRODUCE.md
  PACKAGE-MANIFEST.sha256
  payload/
  source-archive/
  evidence/
```

An experiment-level README links its packages. Historical publications may also need `publication-history/<source-commit>/` to retain later publication documents without replacing the archive's original versions. Such exceptions preserve evidence; they do not create a separate root layout for an early experiment.

Implementations have their own development repositories. A package may contain a pinned implementation snapshot, adapter or verifier needed to reproduce its declared run. That copy is an experimental input, with its own source and license information; this collection is not its ongoing development repository.

## Source precedence depends on the fact

| Fact | Primary source |
|---|---|
| Selected archive's composition and original recorded results | Exact archive bytes, named digest and source record |
| DOI, record version and publication event | Identified publication-system record |
| Package location, preservation checks and current explanatory scope | Versioned external card and the corresponding verification report |
| A new execution or reproduction | Its separately preserved inputs, implementation identities, environment and actual outputs |

An archive's `publication_performed: false` can remain correct as a pre-publication statement while the publication system later records a release. A successful checksum comparison does not establish that an experimental conclusion is true. Neither source should be assigned authority outside the kind of fact it records.

## Five independent status dimensions

`schemas/record.schema.json` fixes the following vocabulary for the two historical use cases; see the separately versioned extension below. Do not add synonyms such as `partial`, `limited` or `bridge-needed`. Extend the schema deliberately when a real case requires a new meaning; preserve the older schema and explain the change.

| Dimension | Values | Meaning |
|---|---|---|
| `integrity` | `verified`, `not-verified` | Recorded byte/inventory checks have, or have not, been performed for the identified package material. This does not establish factual truth or source authorship. |
| `execution` | `archived-evidence-replayed`, `local-run-completed`, `not-run` | An archived-evidence replay checks saved material without a new implementation execution; a local run records an actual implementation execution; not-run carries expectations only. An archived-evidence replay must keep `implementation_execution_performed: false`. |
| `independent_reproduction` | `not-performed`, `performed` | A separate external reproduction of the complete packaged procedure is, or is not, supported by the card's scoped evidence. Narrower historical independent contributions do not automatically satisfy this field. |
| `comparison` | `explicit-bridge-required`, `no-local-decision-difference`, `not-evaluated` | The selected comparison required a missing explicit mapping; the tested local decisions did not differ from the stated baseline; or no comparison outcome is claimed. These are bounded results, not a ranking of systems. |
| `publication` | `prepared`, `published` | A package is prepared, or has a concrete identified public carrier. The carrier distinguishes GitHub from Zenodo; `published` alone does not mean that a DOI exists. |

Independence statements distinguish observable common code/dependencies from declarations about control of the environment and access to expected results. A second process, a different programming language or an AI reviewer in the same session does not by itself establish independent external reproduction. Known private reference results make a later public replay non-blind; that limitation remains explicit.

## Cards and generated catalog

Each `record.json` declares a supported schema version (`0.1.0` for historical cards, `0.2.0` or `0.3.0` below), has an integer `record_revision`, and resides outside `payload/`. Its identity must agree with its directory. Citations, reproduction instructions and evidence references are package-relative paths.

`catalog.json` is generated only by:

```sh
python3 -B scripts/catalog.py
```

The catalog includes each card's SHA-256 and selected fields. `scripts/catalog.py --check` fails if a manually edited or stale catalog differs. `scripts/verify_collection.py` additionally verifies package manifests, reference paths and local links in newly authored Markdown. For the bounded `aar-pilot-v1` package it also invokes `scripts/verify_aar.py` to check the pinned preparation inputs, saved complete results/journal and exact ZIP composition; for `wimse-core02-migration-v1` it invokes `scripts/verify_wimse_core02.py`, and for `scitt-receipt-boundary-v1` it invokes `scripts/verify_scitt_receipt_boundary.py`. Those read-only checks verify evidence of the separately recorded local AAR execution; they do not invoke its implementations or independently authenticate that execution. Schema validity and catalog consistency do not independently appraise a result.

A `PACKAGE-MANIFEST.sha256` lists every file below that package except itself. It identifies the current external package metadata and payload without replacing any historical payload manifest. A later card correction increments `record_revision`, regenerates the package manifest/catalog and explains the correction in Git history. It must not rewrite a frozen archive, run or expectation file.

## Preservation and new packages

Once published, source archives and frozen run contents are retained byte-for-byte. A corrected or expanded experimental run receives a new package identifier. Previous results, failed runs and their source versions remain available; a later draft never silently replaces a historical experiment's source bytes.

`.gitattributes` disables text normalization for all shipped bytes, including cards and the generated catalog as well as payloads, source archives, evidence and preserved publication history. It does not preserve ZIP ordering, timestamps or all Unix permissions. A migration checks case-folding and Unicode normalization collisions, types, executable-bit projection and a fresh Git clone of the exact candidate commit.

New release tags use `<experiment-id>/<package-id>`, for example `wimse-aar-02-interop-001/pkg-001`. The legacy `wexp-emilia-interop-001` tag remains unchanged. Repository-wide release settings and any GitHub–Zenodo integration are considered before creating a new release. Each experiment gets its own publication lineage; the EMILIA concept DOI is never reused for the collection or another experiment.

## Card revision 0.2.0 and saved Core-02 migration admission

The original `schemas/record.schema.json` (0.1.0) and historical cards are preserved.
`schemas/record-0.2.0.schema.json` adds verification profile `wimse-core02-migration-v1`.
The loader selects a closed schema by the card's explicit version; catalog entry
shape remains 0.1.0. No historical vocabulary is relabeled.

For this profile, `local-run-completed` and `implementation_execution_performed: true`
refer to the identified original implementation runs. Catalog admission and its
checker execute no producer/appraiser/recipient. The primary artifact is an exact
existing Actions observations ZIP; the separate frozen source snapshot is not
its extraction. All four ZIPs are retained, with a pinned source inventory and
read-only result checks. Fresh execution additionally needs the two specified
public dependency checkouts. New package metadata does not change old observations,
create independence or turn a recorded migration into AAC/Coverage interoperability.

## Card revision 0.3.0 and the SCITT receipt boundary package

`schemas/record-0.3.0.schema.json` is 0.2.0 with one added verification profile,
`scitt-receipt-boundary-v1`; `$id`, title and the `schema_version` constant change, nothing
else. Schemas 0.1.0 and 0.2.0 and their cards are preserved and still loaded. Catalog entry
shape remains 0.1.0.

For this profile, `local-run-completed` and `implementation_execution_performed: true` refer to
the package run made from the committed composition with the two pinned appraisers named in the
card; the read-only verifier pins the payload inventory, the primary archive, the Receipt and
Signed Statement digests, the frozen expectations' delivered digest list, and the package run
record and comparison, and re-derives every recorded equality from the saved observed results
and the frozen expectations under the harness set semantics. It executes no appraiser, emulator
or Transparency Service. A passing check does not make the mapping a SCITT profile or the case
a vector of `wexp-vectors`.

## Card revision 0.4.0 and split verdicts

`schemas/record-0.4.0.schema.json` is 0.3.0 with three deliberate changes; `$id`, title and the
`schema_version` constant change accordingly. Schemas 0.1.0–0.3.0 and their cards are preserved
and still loaded. Catalog entry shape remains 0.1.0.

1. `comparison` gains `split-verdict`: the recorded result consists of separate verdicts at
   different scopes that the source record forbids collapsing into one. It is not a synonym for
   `not-evaluated` or any other value.
2. With `split-verdict`, `result.verdict_record` is required (and it is allowed only then). It
   names the package-relative record, its SHA-256, a JSON pointer to the object that holds the
   scopes, each scope with its verdict exactly as recorded, and `not_collapsible: true`.
   `scripts/verify_collection.py` checks the digest, resolves the pointer and compares every
   scope verdict with the record.
3. `license` may be absent while license terms are pending; an absent license is permitted only
   with `publication: prepared`. A package without a recorded license is not published.

The first use is `emilia-interop-002/pkg-001` (profile `emilia-archive-v1`). For it,
`scripts/verify_emilia.py --package emilia-interop-002/pkg-001` handles a ZIP without directory
entries, member modes without a file-type bit and the absence of a FREEZE record, by checking
the candidate's internal manifest and pinned verdict record instead. The default invocation
still checks INTEROP-001 unchanged.
