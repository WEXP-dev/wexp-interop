# WEXP × EMILIA positive/hostile pair freeze 001

Status: **PRE-IMPLEMENTATION FREEZE — FOUNDER REVIEW**  
Artifact: `WEXP-EMILIA-PAIR-FREEZE-001`

This package contains the exact P/P-1 pair requested by Iman and the
independently derived WEXP expectation. It contains no WEXP engine output, no
EMILIA implementation output, no comparison execution, and no private WEXP
material.

## Identity gate

The construction gate passed before fixture creation:

| Input | Exact identity |
| --- | --- |
| Original common fixture | `WEXP-EMILIA-INTEROP-001/fixtures.yaml`, 2,218 bytes, SHA-256 `d972dbb549aaaa25e92c32a936acba4d9a686e9ca62fe6bd556b12be2962cfcc` |
| Original artifact-set freeze | `WEXP-EMILIA-INTEROP-001@sha256:c914330b502a48f669381bad763952365da8db64b078445cea6ba5bfb7209d46` |
| Exact WE-EP-004 block | source byte range `[1606,2054)`, 448 bytes including terminating LF, SHA-256 `be4019e2e6b587d2c2bab6f6d6bb54874b5e0fcae77f26a1a53dd10444d9ae08` |
| Existing comparison | `WEXP-EMILIA-EP-COMPARISON-001.md`, 19,327 bytes, SHA-256 `272a9b08a213702ee2156438b7736b954c7a32bc4a190cce92d3d82226266934` |
| Frozen WEXP reading | `wexp-reading.yaml`, 13,256 bytes, SHA-256 `a185e6760de149375e657b1429adc1ea329ed9f9705b9d1c2b505dcc8e3ea984` |
| Frozen EMILIA reading | Gmail attachment `emilia-reading.json`, 5,078 bytes, SHA-256 `b43f8ac6dce465258c75a42117d2750a6bafa163846251416e87cec371a4bad6` |
| EMILIA baseline | `emiliaprotocol/emilia-protocol@9a04bea7fe680345132f6f6251fdb9a63fd8aeb2` |
| Latest Iman construction guidance | Authenticated Gmail message `<CAOfgHgrcyJ4dNaqGUyQ7fiP7WuzQMr0ZXLwMBZUp1VaCTWaSgA@mail.gmail.com>`, `2026-08-20T17:50:58-05:00` |

At the gate, EMILIA `main` and WEXP specification `main` remained exactly at
their pins. `wexp-vectors` had advanced by one commit to
`2da7309d75762e4cf1e83b86bd606f4d473b1638`; `wexp-ref` had advanced by five
commits to `3738c6d7767e5fafb0a97fc28336e3236761b3e6`. Both earlier commits remain
ancestors. The advancements were recorded rather than silently imported; this
package retains the frozen WEXP baseline.

## Exact fixtures

| Filename | Bytes | SHA-256 | Media type / encoding | Schema | Creation time UTC |
| --- | ---: | --- | --- | --- | --- |
| `fixtures/WE-EP-P.json` | 7,255 | `b552da51858d0256a562e800a81a870435d6e136c9bc28833b962b6d3723fb3e` | `application/json; charset=utf-8` | `wexp-emilia-pair-fixture-1` | `2026-08-21T00:31:23Z` |
| `fixtures/WE-EP-P-1.json` | 7,152 | `67556d28d272b4b01a73e1c1465248644dd7a05460fc149aa77df92cf36403a0` | `application/json; charset=utf-8` | `wexp-emilia-pair-fixture-1` | `2026-08-21T00:31:23Z` |

Fixture serialization rule: UTF-8 without BOM; JSON object member order exactly
as authored; two-space indentation; LF line endings; one final LF; no
post-freeze normalization. These exact file bytes—not a reparsed or re-rendered
form—are the fixture identities.

Pair manifest identity: `PAIR-MANIFEST.sha256`, 178 bytes, SHA-256
`5375841c5c7d550d1dcbb3ac31e73ab6c5d68a2bc1eb4fea5249dec9dbdce604`.

Signed observation bodies use the separate frozen EMILIA signing rule:
`canonicalizeStrictJson` with lexicographically sorted object keys, prefixed by
`EP-OUTCOME-OBSERVATION-v1\0`, encoded as UTF-8, and signed directly with
Ed25519. Fixture formatting is not the signature canonicalization.

## Construction

P is derived from WE-EP-004 and the frozen EMILIA source vector
`accept_executor_and_independent_observer`. It carries:

- exact expected receipt, receipt digest, action hash, action CAID, consumption
  nonce, operation, and facility identifiers;
- signed controller and meter observations covering those identifiers;
- current accepted source pins, distinct Ed25519 keys, and distinct declared
  control domains;
- pinned source requirements and exact observation windows;
- typed controller-acceptance and delivered-MW effect semantics;
- exact controller/action/operation and meter/action/CAID/operation/facility
  equality fields.

The frozen source's `sourceRequirements` objects have no native requirement-ID
member and the native shapes are closed. No requirement identifier is required
by that source; none was invented inside the native input.

P-1 is derived from P by removing exactly
`/emilia_input/observations/1/action_caid` and re-signing only that meter
observation. The new meter signature is valid. `PAIR-DELTA.md` records the exact
semantic and derivative byte differences.

The package preserves the EMILIA source vector's exact `expected*` action and
receipt commitments as construction inputs. It does not invent an action body,
recompute CAID semantics, or treat those equality tokens as WEXP target
identity. Authorization-format verification remains an EMILIA-side concern for
the later independent run.

## Field bases

| Fixture field group | Basis |
| --- | --- |
| WE-EP-004 seed description and controller/meter roles | Original common fixture vocabulary |
| Native observation field names, roles/classes, effects, pins, key status, control domains, requirements, windows, equality options, concrete IDs/times/values and positive signatures | Frozen EMILIA baseline vector |
| Meter re-signing domain, canonicalization, Ed25519 key encoding and key-ID derivation | Frozen EMILIA baseline source and deterministic public vector generator |
| Wrapper `schema`, artifact/source provenance, stable observation index, JSON Pointer and P/P-1 names | Explicit experiment glue |
| WEXP expectation, non-inference rules, missing bridge and Core references | Published Core-01 and frozen public WEXP reading |

No fixture field is based on a current engine preference. Iman's guidance was
used only for fixture structure and the predeclared ablation; his rehearsed
EMILIA result was not copied into the WEXP expectation.

## Frozen WEXP expectation

P and P-1 are both `UNDERDETERMINED` as WEXP appraisals. Both have asserted
claim and verdict `UNDETERMINED`. The removal's effect on WEXP semantic support
is also `UNDETERMINED`: no frozen public EP-to-WEXP profile assigns the meter's
`action_caid` relation an exact WEXP role.

**BRIDGING RULE REQUIRED: YES.** `WEXP-DERIVATION.md` and
`wexp-expectation.yaml` state the exact missing rule. This is a terminal finding
for this phase and requires stopping before implementation execution.

## Independence check

- REFERENCE ENGINE RUN BEFORE FREEZE: **NO**
- INDEPENDENT WEXP ENGINE RUN BEFORE FREEZE: **NO**
- EMILIA IMPLEMENTATION RUN BY THIS EXECUTOR BEFORE FREEZE: **NO**
- IMAN INTERNAL REHEARSAL USED AS WEXP EXPECTATION INPUT: **NO**
- FIXTURE CONSTRUCTION USED IMAN'S STRUCTURAL GUIDANCE: **YES**

Construction-only JSON parsing, SHA-256 calculation, object-delta checking, and
Ed25519 signing/verification were performed. These are not WEXP or EMILIA
semantic execution.

## Package contents and use

- `fixtures/WE-EP-P.json` — exact positive fixture bytes.
- `fixtures/WE-EP-P-1.json` — exact hostile twin bytes.
- `PAIR-MANIFEST.sha256` — pair-only fixture manifest.
- `PAIR-DELTA.md` — controlled-delta and cryptographic proof record.
- `EXPERIMENT-PROPOSITION.md` — proposition fixed before derivation.
- `wexp-expectation.yaml` — frozen WEXP expectations.
- `WEXP-DERIVATION.md` — normative derivation and bridge finding.
- `MANIFEST.sha256` — full package manifest, excluding itself.

This package is for Founder review and transmission to Iman. It is not a public
interop result, WEXP or EMILIA conformance, certification, standards adoption,
or a normative profile. Do not run either implementation until the package has
been reviewed.
