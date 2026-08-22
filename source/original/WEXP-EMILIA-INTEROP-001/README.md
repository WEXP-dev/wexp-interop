# WEXP–EMILIA Interop 001 — independent WEXP-side freeze

Status: **FROZEN — WEXP SIDE ONLY**  
Freeze time: `2026-08-20T03:09:46-07:00`  
Artifact: `WEXP-EMILIA-INTEROP-001`

This package freezes the WEXP-side reading of the five case descriptions agreed
in the Mikhail × Iman correspondence. It was prepared before receipt or use of
Iman's per-case EMILIA lifecycle outcomes.

It contains no EMILIA lifecycle expectations, no comparison result, and no
interop record. No WEXP engine was run against these cases. The package stops at
the independent WEXP freeze.

## Pinned public authority

- `draft-sergeev-wexp-core-01` / `CORE-01-FROZEN-001`; authoritative XML
  SHA-256 `84c0a16467585c29925339a10dd287c2e67bfe21ed592826254bf424dc24f56d`,
  103095 bytes.
- `WEXP-dev/wexp-spec@b28a46e7764c2ef14decc35394f21278fca9c988`,
  including `CORE-01-KNOWN-ISSUES-001` and
  `CORE-01-REPRESENTATION-CONTRACT-001`.
- `WEXP-dev/wexp-vectors@c745e5abebddfd99cd62cdb3e40dddaf6582bdd9`,
  version `0.2.0`, containing public sets 001 and 002.
- `WEXP-dev/wexp-ref@d8f7e512a56b90b17377444c07cbc006ee76b7b5`,
  version `0.2.0.dev0`, with declared conformance inventory `PARTIAL`.

The specification is authoritative. The known-issues record is
project-maintained, the representation contract is non-normative carrier
detail, the vector sets are not conformance suites, and `wexp-ref` does not
define WEXP semantics.

## Result

| Case | Frozen WEXP status | Reason |
|---|---|---|
| `WE-EP-001` | `UNDERDETERMINED` | A signed executor self-report and `in_bounds` do not provide an asserted WEXP claim, exact target binding, or an accepted execution-relevant boundary. |
| `WE-EP-002` | `UNDERDETERMINED` | Signature and digest checks do not semantically support an exact content claim, and the verifier did not observe the effect boundary. |
| `WE-EP-003` | `UNDERDETERMINED` | Core does not itself define when a system-of-record confirmation satisfies the exact execution predicate or accepted-boundary requirements. |
| `WE-EP-004` | `UNDERDETERMINED` | Dispatch and measured-effect reports lack an established exact-target correlation, boundary mapping, and WEXP IV independence predicate. |
| `WE-EP-005` | `UNDERDETERMINED` | Meter unavailability does not determine which normalized role was unevaluated or whether the result is `unsupported` versus `not-evaluated`. |

`UNDERDETERMINED` is the frozen expectation for each case. It means the agreed
facts do not determine one complete logical Core `AppraisalInput` and therefore
do not determine an `accept`, `downgrade`, or `reject` appraisal. It is not a
guessed negative verdict.

## Boundaries preserved

- A signature or digest check does not establish content truth, boundary
  control, or semantic support.
- `in_bounds` does not establish invocation or execution.
- An EMILIA lifecycle state does not determine a WEXP verdict.
- The words `external` or `independent` do not establish WEXP IV without a
  profile-defined independence assessment for the exact base.
- Dispatch does not imply execution or effect.
- A missing record or unavailable meter does not establish nonoccurrence.
- CAID/action correlation does not define WEXP target equality or an
  arguments-hash identity.
- Case identifiers such as `WE-EP-001` identify fixtures only; they are not
  WEXP action targets or CAIDs.

## Gaps exposed

No new Core ambiguity was found. The decisive gap is the absence of a public,
immutable EP-to-WEXP mapping profile defining exact-target equality, evidence
to content-base predicates, accepted boundary grounding, meter/effect
semantics, and IV independence criteria. Durable external effect is
intentionally outside Core's four content bases and needs a profile-defined
relationship to an exact WEXP claim.

The current public reference tooling is also `PARTIAL`. In particular, later
execution of `WE-EP-005` will depend on whether a future profile maps meter
unavailability to a boundary, base, IV, or counter-evidence assessment; those
paths are not all inside the declared public tooling surface.

## Files

- `fixtures.yaml` — agreed facts only; no EMILIA outcomes or inferred mapping.
- `wexp-reading.yaml` — independent WEXP interpretation, required predicates,
  missing information, and frozen statuses.
- `MANIFEST.sha256` — SHA-256 checksums for the three payload files.

## Integrity and freeze identity

All files are UTF-8 with LF endings and a final newline. Verify the payload
manifest from this directory with:

```sh
shasum -a 256 -c MANIFEST.sha256
```

`MANIFEST.sha256` is excluded from its own checksum list to avoid a circular
self-hash. The artifact-set freeze identity is:

```text
WEXP-EMILIA-INTEROP-001@sha256:<SHA-256 of the exact MANIFEST.sha256 bytes>
```

The concrete identity is reported with the frozen package. Recomputing that
digest plus successfully checking the manifest verifies all four files.

## Stop point

The next phase may begin only after an independent EMILIA-side freeze exists.
That later phase may compare freezes; it must not rewrite this package to make
the results agree.
