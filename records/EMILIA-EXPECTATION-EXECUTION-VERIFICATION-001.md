# EMILIA expectation and execution verification 001

Status: **VERIFIED — REVIEW EVIDENCE**  
Authority: Founder  
Scope: byte identity, precedence, receipt linkage, expectation reproduction,
and the public EMILIA baseline artifacts named by the receipt.

This record preserves EMILIA terminology as disclosed. It does not translate an
EMILIA lifecycle state or outcome into a WEXP appraisal and does not establish
semantic equivalence, conformance, physical truth, or a WEXP execution claim.

## Gmail provenance

The correspondence subject was `Re: WEXP × EMILIA: joint technical work`.
The pair package was sent to Iman at `2026-08-21T00:58:41Z` in Gmail message
`1a021d3e03807dc2`, RFC Message-ID
`<CAC-beJ6LsOw5EMWJj+JS4OQare+6OKV4egvNkO4sMuL6LXy-hA@mail.gmail.com>`.
Iman's reply at `2026-08-21T02:48:33Z`, Gmail message
`1a02238850e8d049`, RFC Message-ID
`<CAOfgHgopYf29ydongKvjJMT2mh4hEmNyz6-OeL-AqaPxmyHMyg@mail.gmail.com>`,
supplied the exact attachments `emilia-expectation.freeze.json` and
`emilia-execution-receipt.json`. The received headers report DKIM, SPF, and
DMARC as PASS.

## Exact input identities

| Input | Bytes | SHA-256 | Verification |
| --- | ---: | --- | --- |
| `expectations/emilia/emilia-expectation.freeze.json` | 885 | `6e0dc6c87f853cacdeeb676b27690e54bdb8a7a7aa86611c5ffe233387e256a4` | PASS |
| `execution/raw/emilia/emilia-execution-receipt.json` | 1,963 | `2d61071712ef4424d1b308afb6a3b8752b4effcf2525c0c08c97cff16617b77f` | PASS |

Both source JSON files are retained byte-for-byte. This record is derived
verification metadata and does not replace either source.

## Freeze and execution chronology

| Order | Event | Time evidence | Result |
| ---: | --- | --- | --- |
| 1 | P/P-1 creation and byte freeze | `2026-08-21T00:31:23Z` | P and P-1 preceded both expectation freezes. |
| 2 | WEXP P/P-1 expectation freeze | `2026-08-21T00:32:35Z` | Preceded any WEXP execution; no WEXP implementation was run. |
| 3 | Exact pair package sent to Iman | `2026-08-21T00:58:41Z` | The sent package carried the frozen P/P-1 bytes and WEXP expectation. |
| 4 | EMILIA expectation freeze | Before EMILIA execution; exact freeze instant is not separately declared | The source declares `fixed_before_emilia_execution`; the receipt binds its exact hash before reporting execution. |
| 5 | EMILIA execution | `2026-08-21T02:41:04Z` | Receipt records the execution over the exact pair. |
| 6 | Iman reply and reveal | `2026-08-21T02:48:33Z` | Exact expectation and receipt attachments revealed after execution. |

Freeze precedence: **PASS**. The evidence establishes ordering without
reconstructing an undeclared EMILIA expectation-freeze timestamp.

## Receipt linkage

The receipt binds all required frozen identities:

| Receipt member | Exact value | Result |
| --- | --- | --- |
| `artifact` | `WEXP-EMILIA-PAIR-FREEZE-001` | PASS |
| `package_sha256` | `ae237263c86ee0b5c2b6387159d81957efe47e20161b74dd363da5a530705282` | PASS |
| `expectation_freeze_sha256` | `6e0dc6c87f853cacdeeb676b27690e54bdb8a7a7aa86611c5ffe233387e256a4` | PASS |
| P `input_sha256` | `b552da51858d0256a562e800a81a870435d6e136c9bc28833b962b6d3723fb3e` | PASS |
| P-1 `input_sha256` | `67556d28d272b4b01a73e1c1465248644dd7a05460fc149aa77df92cf36403a0` | PASS |
| EMILIA baseline commit | `9a04bea7fe680345132f6f6251fdb9a63fd8aeb2` | PASS |

## Frozen expectation versus actual result

| Fixture | Frozen EMILIA expectation | Receipt actual | Result digest | Reproduction |
| --- | --- | --- | --- | --- |
| P | `valid: true`; `lifecycle_state: reconciled`; `outcome: in_bounds`; `errors: []` | `valid: true`; `lifecycle_state: reconciled`; `outcome: in_bounds`; `errors: []` | `sha256:4ea90a5cf398ad77fe21bd5933ae85c2970cb55d1b5cd929c0f097bb9efc50b3` | `EXPECTED RESULT REPRODUCED` |
| P-1 | `valid: false`; `lifecycle_state: indeterminate`; `outcome: null`; required error `outcome_observations_not_exactly_bound` | `valid: false`; `lifecycle_state: indeterminate`; `outcome: null`; `errors: [outcome_observations_not_exactly_bound]` | `sha256:7bfe5b1ba465546787d0ed31fa7aabd00ddd30b755b1c028230a5796d0160aca` | `EXPECTED RESULT REPRODUCED` |

The result-digest strings above are verified as exact receipt fields. This
record does not claim to recompute them under an unstated serialization rule.

## Shared checks

Every shared check disclosed by the receipt is `true`:

| Check | Value |
| --- | --- |
| `predictions_valid` | `true` |
| `observations_verified` | `true` |
| `required_sources_present` | `true` |
| `source_independence` | `true` |
| `source_requirements` | `true` |
| `observation_windows` | `true` |

These checks do not erase P-1's exact-binding refusal and do not establish
physical truth or WEXP semantic support.

## Controlled difference

The frozen pair record establishes that P-1 removes only the meter
observation's `action_caid` relation and changes only the derivative meter
signature needed to preserve cryptographic validity. Restoring those two
values reproduces P exactly. The receipt binds the same fixture hashes and
states the same controlled difference.

Controlled-difference verification: **PASS**.

## Public EMILIA baseline artifacts

Read-only verification against
`https://github.com/emiliaprotocol/emilia-protocol` at commit
`9a04bea7fe680345132f6f6251fdb9a63fd8aeb2` established:

| Public artifact | Bytes | SHA-256 | Result |
| --- | ---: | --- | --- |
| `packages/verify/src/outcome-binding.ts` | 72,532 | `9a674113122f23001567eaeb673190ac4658b5273f7433e234c8ecbb5be704b0` | PASS |
| `packages/verify/index.js` | 138 | `f386e365a9998f08ea4947ffd415ca353c0a82766677a8e0cf3117909cccee24` | PASS |

These identities verify the public baseline artifacts named by the receipt.
They are not a fresh EMILIA execution and do not expand the receipt's claim
boundary.

## Terminal implication

The EMILIA implementation reproduced both independently frozen expectations,
including the positive/hostile distinction. The frozen WEXP reading remains
`UNDERDETERMINED` for both fixtures because no frozen public EP→WEXP mapping
constructs a complete Core `AppraisalInput` or assigns meter `action_caid` the
required WEXP role. No bridge was inserted.

The evidence therefore selects **BRANCH A — EXPLICIT BRIDGE REQUIRED**.
Branch B is not selected because no determinate WEXP appraisal is constructible
under the frozen public surface. Branch C is not selected because both
applicable EMILIA results reproduced their frozen expectations.
