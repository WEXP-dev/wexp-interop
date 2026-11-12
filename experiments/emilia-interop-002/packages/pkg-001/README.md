# WEXP × EMILIA INTEROP-002 — pkg-001

**Historical INTEROP-002 result. Split verdict: bridge sufficiency SUPPORTED; joint WEXP × EMILIA comparison INCONCLUSIVE for five of seven cases and NOT_DERIVED for two.** The archived record states that these "MUST NOT be collapsed into a single verdict". This card keeps them apart. The [verdict record](payload/publication-candidate/FINAL-RECORD-002.json) (member `TWO_SCOPES_NOT_ONE_VERDICT`) remains unchanged.

**Status: prepared, not published.** This card places Publication Candidate 003 in the common collection. The migration checks archive bytes, the candidate's internal manifest and the recorded verdicts. It adds no implementation execution and no new interoperability result.

| Dimension | Value | Scope |
|---|---|---|
| Integrity | `verified` | Selected archive, extraction, internal manifest and verdict-record identities. |
| Execution | `archived-evidence-replayed` | `implementation_execution_performed: false` for the migration checks. The historical execution status `EXECUTED` remains in [the execution record](payload/execution/EXECUTION-RECORD-001.json). |
| Independent reproduction | `not-performed` | No separate external reproduction of the complete package is claimed. |
| Comparison | `split-verdict` | Two scopes held in the pinned verdict record; neither is a combined verdict. |
| Publication | `prepared` | No public carrier, release tag or DOI. |

The [machine-readable card](record.json) uses card schema 0.4.0 and the [collection's fixed definitions](../../../../docs/COLLECTION.md).

## The two scopes

| Scope | Recorded verdict | Cases |
|---|---|---|
| WEXP bridge sufficiency | `SUPPORTED` | A property of this bridge over these seven frozen cases. |
| Joint WEXP × EMILIA comparison | `INCONCLUSIVE for every case lacking native EMILIA output` | H-01-b, H-01-c, H-02, H-03, B-01 |
| | `NOT_DERIVED_UNDER_THIS_ORDER` | C-00, H-01-a |

Local minimality is recorded as `NOT_ESTABLISHED` (15 of 17 elements shown necessary). The full narrative is the archived [final report](payload/publication-candidate/FINAL-REPORT-001.md).

## Original version pins

- WEXP surface: `draft-sergeev-wexp-core-01`, SHA-256 `84c0a16467585c29925339a10dd287c2e67bfe21ed592826254bf424dc24f56d`, semantics `wexp-core-1`. This is the surface the frozen bridge targets, as recorded in [BRIDGE-CANDIDATE.yaml](payload/bridge/BRIDGE-CANDIDATE.yaml).
- EMILIA: commit `9a04bea7fe680345132f6f6251fdb9a63fd8aeb2` of `emiliaprotocol/emilia-protocol`, pinned by every fixture. EMILIA was not run by this package.

These are the historical pins. Nothing here restates the result under a later WEXP version.

## Attribution

As recorded in the package. The charter, section 16:

> INTEROP-002 asks for only three substantive
> contributions from Iman Schrock:
>
> 1. review this charter and correct any unfair or inaccurate EMILIA-side
>    assumption;
> 2. provide one B-01 commitment and later the matching reveal; and
> 3. verify the exact final record and whether it represents the native EMILIA
>    result fairly.

The final report describes B-01 as "a blind hostile case committed by the EMILIA-side contributor by SHA-256 before the bridge was authored, revealed only after the Execution Freeze." The [commitment](payload/pre-freeze/B-01-COMMITMENT.json), [commitment verification](payload/reveal/B01-COMMITMENT-VERIFICATION-001.json) and [fairness review](payload/publication-candidate/COUNTERPARTY-FAIRNESS-REVIEW-002.json) are retained byte-for-byte. [CITATION.cff](CITATION.cff) names the two persons named in the package.

## Exact archive and extracted view

The selected object is the [Candidate 003 ZIP](source-archive/WEXP-EMILIA-INTEROP-002-PUBLICATION-CANDIDATE-003.zip):

```text
Bytes:   192089
SHA-256: 37412ba521b9bca9901b54142290356a0aedf8bc7cd635e731d7660916cf770e
```

`payload/` contains the 57 unmodified file byte sequences extracted from that ZIP, with the outer container directory removed. The ZIP has no directory entries; directories in Git are implicit. Every member records permissions `0644` without a Unix file-type bit; Git represents every file as `100644`. The candidate has no separate FREEZE record; its [internal manifest](payload/publication-candidate/PUBLICATION-CANDIDATE-MANIFEST-003.json) binds 56 files and excludes itself. See [evidence](evidence/README.md) and [reproduction instructions](REPRODUCE.md).

## Publication state

Prepared, not published. The candidate's own records state `publication_authorized: false` and that counterparty exact-byte review was not yet performed; those historical bytes are unchanged. **Zenodo fields (version DOI, concept DOI, record) are intentionally empty** pending a separate decision. No release tag exists.

## License

**Pending.** Candidate 003 contains no license statement. License terms for the archived content await the EMILIA-side contributor's confirmation. Until then this card declares no license, `LICENSE-SCOPE.md` is intentionally absent, and the package must not be published.

## Limitations

Package limitations:

- This migration does not rerun any WEXP, EMILIA or bridge implementation and executes no archived code.
- The two scopes are separate claims. `split-verdict` only points to the record that holds them.
- The ZIP is authoritative for archive composition; `payload/` is its verified extraction, not the container bytes.

Claim ceilings, verbatim from the archived [final record](payload/publication-candidate/FINAL-RECORD-002.json), `PUBLICATION_CLAIM_CEILINGS`. Prohibited claims (charter section 14):

- physical truth of an execution or effect
- correctness, security, or completeness of WEXP or EMILIA
- global minimality of the bridge
- universal EP-WEXP interoperability
- conformance, certification, adoption, or IETF endorsement
- WEXP independent verification merely from an EMILIA role label
- that an EP receipt, outcome observation, or mapped appraisal grants reusable permission, local authorization, Gate admission, delegated authority, or approval for a future action
- a generic Bridge Framework
- validity beyond the frozen authorities, bridge, cases, and verdict rules

Additional ceilings from this experiment:

- H-MIN is NOT_ESTABLISHED. The bridge is NOT shown to be minimal.
- The joint comparison is INCONCLUSIVE for five of seven cases.
- No claim above the observation base is supported on any case.
- The WEXP IV finding is a WEXP conclusion and says nothing about EMILIA's independence semantics.
- Section 13 no-generalization governs; nothing here is promoted to interop-core.
