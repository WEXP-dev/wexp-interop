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

`schemas/record.schema.json` fixes the following vocabulary for the two current use cases. Do not add synonyms such as `partial`, `limited` or `bridge-needed`. Extend the schema deliberately when a real case requires a new meaning; preserve the older schema and explain the change.

| Dimension | Values | Meaning |
|---|---|---|
| `integrity` | `verified`, `not-verified` | Recorded byte/inventory checks have, or have not, been performed for the identified package material. This does not establish factual truth or source authorship. |
| `execution` | `archived-evidence-replayed`, `local-run-completed`, `not-run` | An archived-evidence replay checks saved material without a new implementation execution; a local run records an actual implementation execution; not-run carries expectations only. An archived-evidence replay must keep `implementation_execution_performed: false`. |
| `independent_reproduction` | `not-performed`, `performed` | A separate external reproduction of the complete packaged procedure is, or is not, supported by the card's scoped evidence. Narrower historical independent contributions do not automatically satisfy this field. |
| `comparison` | `explicit-bridge-required`, `no-local-decision-difference`, `not-evaluated` | The selected comparison required a missing explicit mapping; the tested local decisions did not differ from the stated baseline; or no comparison outcome is claimed. These are bounded results, not a ranking of systems. |
| `publication` | `prepared`, `published` | A package is prepared, or has a concrete identified public carrier. The carrier distinguishes GitHub from Zenodo; `published` alone does not mean that a DOI exists. |

Independence statements distinguish observable common code/dependencies from declarations about control of the environment and access to expected results. A second process, a different programming language or an AI reviewer in the same session does not by itself establish independent external reproduction. Known private reference results make a later public replay non-blind; that limitation remains explicit.

## Cards and generated catalog

Each `record.json` conforms to schema version `0.1.0`, has an integer `record_revision`, and resides outside `payload/`. Its identity must agree with its directory. Citations, reproduction instructions and evidence references are package-relative paths.

`catalog.json` is generated only by:

```sh
python3 -B scripts/catalog.py
```

The catalog includes each card's SHA-256 and selected fields. `scripts/catalog.py --check` fails if a manually edited or stale catalog differs. `scripts/verify_collection.py` additionally verifies package manifests, reference paths and local links in newly authored Markdown. For the bounded `aar-pilot-v1` package it also invokes `scripts/verify_aar.py` to check the pinned preparation inputs, saved complete results/journal and exact ZIP composition. Those read-only checks verify evidence of the separately recorded local AAR execution; they do not invoke its implementations or independently authenticate that execution. Schema validity and catalog consistency do not independently appraise a result.

A `PACKAGE-MANIFEST.sha256` lists every file below that package except itself. It identifies the current external package metadata and payload without replacing any historical payload manifest. A later card correction increments `record_revision`, regenerates the package manifest/catalog and explains the correction in Git history. It must not rewrite a frozen archive, run or expectation file.

## Preservation and new packages

Once published, source archives and frozen run contents are retained byte-for-byte. A corrected or expanded experimental run receives a new package identifier. Previous results, failed runs and their source versions remain available; a later draft never silently replaces a historical experiment's source bytes.

`.gitattributes` disables text normalization for all shipped bytes, including cards and the generated catalog as well as payloads, source archives, evidence and preserved publication history. It does not preserve ZIP ordering, timestamps or all Unix permissions. A migration checks case-folding and Unicode normalization collisions, types, executable-bit projection and a fresh Git clone of the exact candidate commit.

New release tags use `<experiment-id>/<package-id>`, for example `wimse-aar-02-interop-001/pkg-001`. The legacy `wexp-emilia-interop-001` tag remains unchanged. Repository-wide release settings and any GitHub–Zenodo integration are considered before creating a new release. Each experiment gets its own publication lineage; the EMILIA concept DOI is never reused for the collection or another experiment.
