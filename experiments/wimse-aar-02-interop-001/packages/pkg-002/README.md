# WIMSE AAR / Appraisal Core-02 — catalog package 002

**Recorded result: 130/130 case checks; no recipient-decision difference from the strong native baseline.**
Thirty-five admitted inputs produced all twenty Core-02 appraisal components; 95 native or dispatch failures produced none. These are cases per run, not new cases multiplied by repeated runs.

This package admits the [already published bounded migration](https://github.com/WEXP-dev/wexp-interop/blob/c8e04e8959eb8f45fad0f7230b5b4c68e606d9c5/docs/proposals/wimse-core02-replay-001/RESULTS.md) to the collection. **Catalog admission performs no new producer, appraiser, recipient or two-world experiment.** [Package 001](../pkg-001/README.md) and its results are unchanged.

Read [the card](record.json), [reproduction instructions](REPRODUCE.md), [source inventory](evidence/SOURCE-MANIFEST.json), [admission record](evidence/ADMISSION.json) and [license scope](LICENSE-SCOPE.md).

## Preserved material

The primary artifact is the original `push-python312.zip` from run 40604969823. It contains saved observations, not a standalone implementation distribution. All four original Actions ZIPs are retained under `source-archive/`, together with their unchanged [run record](source-archive/RECORD.json). `payload/` is a separate byte-identical source snapshot, not an extraction of that primary ZIP. Its README and protocol are historical pre-run material; this outer card states the completed result.

The original runs used CPython 3.12.15 and 3.13.16, normal and optimized modes. All eight complete observed data files share SHA-256 `882cb96cef3fb00192988396ac0ebe4f742070b1d55c2141afe7aebabcb390ae`. Each run retained 392 process outcomes, 1,930 comparator assertions (including positive order controls) and two actual recipient-entry-point binding corruptions. Those counts are not independent security tests.

## Scope

Admitted records support observation only; requested execution remains unsupported. Historical raw inputs, native readers and the recipient policy were held fixed. Mapping/profile/context identities changed for Core-02, so this is not byte equality with old Core-01 appraisals.

This is same-project execution with known sources and expectations, shared native verification and recipient policy, and no enforced OS/network isolation. It is not independent external reproduction, full Core conformance, proof of real action occurrence, AAC interoperability, Coverage evaluation or PostgreSQL validation. No new two-world operations were performed. No release, tag or DOI is created by this catalog entry.
