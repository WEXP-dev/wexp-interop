# WEXP × EMILIA INTEROP-001 — final report

Artifact: `WEXP-EMILIA-INTEROP-001`  
Status: **Experimental Interoperability Record**  
Contributors: **Mikhail Sergeev; Iman Schrock**  
License: **Apache License 2.0 (`SPDX-License-Identifier: Apache-2.0`)**  
Canonical venue: **`WEXP-dev/wexp-interop`**  
IETF status: **NONE — NO IETF ADOPTION OR ENDORSEMENT IMPLIED**  
Technical result: **BRANCH A — EXPLICIT BRIDGE REQUIRED**  
Publication status: **NOT AUTHORIZED**  
Selected terminal branch: **BRANCH A — EXPLICIT BRIDGE REQUIRED**  
Branch B: **NOT SELECTED**  
Branch C: **NOT SELECTED**

## 1. Scope

This bounded experiment compares independently frozen WEXP and EMILIA
readings and expectations over shared byte-identical fixtures. It preserves
EMILIA lifecycle/outcome, WEXP appraisal, and CAID/action correlation as
separate planes. It does not claim conformance, semantic equivalence, physical
truth, standards adoption, or general interoperability.

## 2. Research question

The controlled proposition was fixed before WEXP expectation derivation:

> The stronger result depends on the exact meter-observation-to-action CAID
> binding.

The pair tests whether EMILIA distinguishes P from P-1 when the meter
observation's `action_caid` is removed and only the derivative meter signature
is changed. Separately, it asks whether the frozen public WEXP surface can
construct a determinate Core appraisal for either exact fixture without a new
EP→WEXP rule.

## 3. Frozen authorities

- P: 7,255 bytes; SHA-256
  `b552da51858d0256a562e800a81a870435d6e136c9bc28833b962b6d3723fb3e`.
- P-1: 7,152 bytes; SHA-256
  `67556d28d272b4b01a73e1c1465248644dd7a05460fc149aa77df92cf36403a0`.
- Pair archive: 18,158 bytes; SHA-256
  `ae237263c86ee0b5c2b6387159d81957efe47e20161b74dd363da5a530705282`.
- Frozen WEXP expectation: SHA-256
  `42eeecaba33238d8c94bbb9d5bb22ab46721de6de74cff455b8115c17892088a`.
- Frozen EMILIA expectation: 885 bytes; SHA-256
  `6e0dc6c87f853cacdeeb676b27690e54bdb8a7a7aa86611c5ffe233387e256a4`.
- EMILIA execution receipt: 1,963 bytes; SHA-256
  `2d61071712ef4424d1b308afb6a3b8752b4effcf2525c0c08c97cff16617b77f`.
- WEXP semantic authority: `WEXP-dev/wexp-spec` commit
  `b28a46e7764c2ef14decc35394f21278fca9c988`, with the frozen public
  known-issue and representation surfaces recorded in the WEXP derivation.
- EMILIA semantic and execution baseline: `emiliaprotocol/emilia-protocol`
  commit `9a04bea7fe680345132f6f6251fdb9a63fd8aeb2`.

The public EMILIA commit and receipt-stated files were verified read-only.
`packages/verify/src/outcome-binding.ts` is 72,532 bytes and has SHA-256
`9a674113122f23001567eaeb673190ac4658b5273f7433e234c8ecbb5be704b0`.
The receipt's package-entry hash resolves, through the pinned package metadata
and exact hash match, to `packages/verify/index.js`: 138 bytes, SHA-256
`f386e365a9998f08ea4947ffd415ca353c0a82766677a8e0cf3117909cccee24`.

## 4. Commit/reveal protocol

The neutral five-case fixture was frozen before the two independent readings;
both reading commitments preceded reveal, and both reveals matched their
commitments. The five-case comparison did not revise either reading. P/P-1 and
the WEXP pair expectation were then frozen before any WEXP execution. The
EMILIA expectation declares `fixed_before_emilia_execution`; authenticated
correspondence establishes its pre-run commitment, and the later receipt binds
that exact expectation hash. The expectation file itself has no intrinsic
timestamp, so the ordering claim retains that provenance qualification.

## 5. Five-case boundary comparison

The initial comparison, SHA-256
`272a9b08a213702ee2156438b7736b954c7a32bc4a190cce92d3d82226266934`,
found no genuine semantic disagreement or material overclaim. WE-EP-001
through WE-EP-004 were underdetermined on both sides. For WE-EP-005, EMILIA
determined lifecycle `INDETERMINATE` while WEXP remained underdetermined. This
was compatible uncertainty preservation at different abstractions, not verdict
equivalence.

## 6. Construction of P/P-1

P-1 differs from P in exactly two JSON values:

1. `/emilia_input/observations/1/action_caid` is removed; and
2. `/emilia_input/observations/1/proof/signature_b64u` changes only to
   re-sign the modified meter observation.

No other semantic input changes. Restoring those two values reproduces P
exactly, and all four fixture signatures verify. These construction checks
establish controlled bytes and cryptographic validity, not lifecycle outcome,
physical truth, or WEXP support.

## 7. Independent expectation freezes

The WEXP expectation was frozen at `2026-08-21T00:32:35Z` without a reference
or independent WEXP engine run. It fixes both P and P-1 as `UNDERDETERMINED`
with asserted claim and verdict `UNDETERMINED`.

The independent EMILIA expectation fixes:

- P: `valid: true`, lifecycle `reconciled`, outcome `in_bounds`, errors `[]`.
- P-1: `valid: false`, lifecycle `indeterminate`, outcome `null`, required
  error `outcome_observations_not_exactly_bound`.

Its claim boundary expressly excludes WEXP semantics, equivalence,
conformance, and physical truth.

## 8. EMILIA execution result

The externally supplied receipt records execution at `2026-08-21T02:41:04Z`
and binds the exact pair archive, expectation freeze, P, P-1, and EMILIA
baseline hashes. It reproduces both frozen expectations:

| Fixture | Actual result | Result digest |
| --- | --- | --- |
| P | `valid: true`; lifecycle `reconciled`; outcome `in_bounds`; errors `[]` | `sha256:4ea90a5cf398ad77fe21bd5933ae85c2970cb55d1b5cd929c0f097bb9efc50b3` |
| P-1 | `valid: false`; lifecycle `indeterminate`; outcome `null`; errors `[outcome_observations_not_exactly_bound]` | `sha256:7bfe5b1ba465546787d0ed31fa7aabd00ddd30b755b1c028230a5796d0160aca` |

The receipt reports all six shared checks `true`: `predictions_valid`,
`observations_verified`, `required_sources_present`, `source_independence`,
`source_requirements`, and `observation_windows`. The receipt was verified
against the expectation and frozen identities; this executor did not rerun
EMILIA, and no raw stdout/stderr accompanied the receipt.

## 9. WEXP non-constructibility under the frozen mapping surface

P and P-1 remain `UNDERDETERMINED`. No frozen public EP→WEXP mapping/profile
constructs the complete Core `AppraisalInput` or assigns the meter
`action_caid` relation the required WEXP target-binding or support role.
Therefore the operational class is `IMPLEMENTATION INPUT NOT CONSTRUCTIBLE`,
not failure, engine disagreement, or infrastructure unavailability. No WEXP
engine was invoked and no asserted target, boundary, qualifier role,
effect-to-execution predicate, CAID/IV mapping, counter-evidence rule, or
evaluation scope was fabricated.

## 10. Pair comparison

| Fixture | EMILIA | WEXP | Relationship |
| --- | --- | --- | --- |
| P | `reconciled` / `in_bounds` | `UNDERDETERMINED` | Compatible / different semantic surface |
| P-1 | `indeterminate` / `null`; `outcome_observations_not_exactly_bound` | `UNDERDETERMINED` | Compatible / different semantic surface |

At pair level, EMILIA distinguishes P from P-1 under its frozen expectation
and receipt. WEXP does not classify the changed relation because the public
bridge/profile is absent. CAID/action correlation identifies the controlled
fixture difference only; it is not thereby WEXP semantic evidence. The result
is not a genuine semantic disagreement and contains no material overclaim.

## 11. Terminal result

**BRANCH A — EXPLICIT BRIDGE REQUIRED** is selected mechanically because:

- EMILIA's independent expectation distinguishes P and P-1;
- the receipt reproduces both expected results;
- the pair isolates the exact binding relation while preserving signature
  validity;
- WEXP remains underdetermined and non-constructible under the frozen public
  mapping surface; and
- no bridging rule was inserted.

Branch B is not selected because no determinate WEXP appraisal was
constructible. Branch C is not selected because the EMILIA implementation did
not disagree with its frozen expectation and no applicable WEXP execution was
constructed.

The bounded conclusion is: the EMILIA side reproduced sensitivity to exact
meter-observation-to-action binding, while positive WEXP×EMILIA semantic
composition requires an explicit bridging contract not supplied by the frozen
public surfaces. No such contract was invented or assumed here.

## 12. Limitations

This is one positive/hostile pair. WEXP positive semantic composition was not
tested because no frozen mapping exists. EMILIA lifecycle semantics and WEXP
appraisal semantics remain distinct; physical truth, semantic equivalence,
conformance, full interoperability, and standards adoption are not
established. The EMILIA result is preserved as an external receipt rather than
a local rerun, and its raw process streams are unavailable. Full qualifications
are in `LIMITATIONS.md`.

## 13. Reproduction

A third party can verify all package manifests, commitments, reveals, fixture
hashes, the exact P→P-1 delta, both expectation freezes, receipt linkages,
reported results, and Branch A predicates with the package's read-only
`reproduction/verify_final.py`. Re-running
the EMILIA implementation uses the public repository pinned to
`9a04bea7fe680345132f6f6251fdb9a63fd8aeb2`. No private WEXP or EMILIA
dependency is required. WEXP execution remains correctly classified as input
not constructible unless a separately governed mapping experiment is created.

## 14. Follow-on work

`EP-WEXP-MAPPING-REQUIREMENTS-001.md` is a non-normative follow-on design input
motivated by this result. It is not part of the frozen experiment and was not
used to derive it. Any bridge design, determinate WEXP composition test, or
additional pair requires a separate authorization, freeze, and experiment.
Publication of this candidate remains subject to Founder and joint review.
