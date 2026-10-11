# WEXP × EMILIA EP Five-Case Comparison 001

Status: **JOINT REVIEW READY**  
Comparison mode: read-only comparison of two frozen readings  
Comparison date: 2026-08-20  
Authority: Founder

This record compares the exact frozen EMILIA-side and WEXP-side readings of the
same five fixtures. It does not revise either reading, run an implementation,
create a conformance claim, or modify either system.

## 1. Source identities and reveal verification

### EMILIA reveal

- File: `emilia-reading.json`, received as the attachment to Iman Schrock's
  `Re: WEXP × EMILIA: joint technical work` message dated
  2026-08-20 12:23:14 -05:00.
- MIME size: 5,078 bytes; JSON parse: PASS; `frozen: true`.
- Prior commitment and revealed-file SHA-256:
  `b43f8ac6dce465258c75a42117d2750a6bafa163846251416e87cec371a4bad6`.
- Baseline:
  `emiliaprotocol/emilia-protocol@9a04bea7fe680345132f6f6251fdb9a63fd8aeb2`.
- The commitment was received before the WEXP reveal. The revealed bytes match
  the commitment, so no post-commit change is present.

### WEXP reveal

- File: `WEXP-EMILIA-INTEROP-001/wexp-reading.yaml`, 13,256 bytes;
  YAML parse: PASS; `freeze_state: FROZEN`.
- Prior commitment and revealed-file SHA-256:
  `a185e6760de149375e657b1429adc1ea329ed9f9705b9d1c2b505dcc8e3ea984`.
- The sent reveal package `WEXP-EMILIA-INTEROP-001.zip` is 8,375 bytes,
  SHA-256
  `fbfd3d7bc66033ae51af280970ab2129d39731a64169cc1178300c94ffffbe59`.
  Its manifest verifies `README.md`, `fixtures.yaml`, and
  `wexp-reading.yaml`; Iman independently reported the same WEXP file hash and
  successful manifest checks after receipt.
- Baseline:
  - Core: `draft-sergeev-wexp-core-01` / `CORE-01-FROZEN-001`, authoritative
    XML SHA-256
    `84c0a16467585c29925339a10dd287c2e67bfe21ed592826254bf424dc24f56d`.
  - `WEXP-dev/wexp-spec@b28a46e7764c2ef14decc35394f21278fca9c988`.
  - `WEXP-dev/wexp-vectors@c745e5abebddfd99cd62cdb3e40dddaf6582bdd9`.
  - `WEXP-dev/wexp-ref@d8f7e512a56b90b17377444c07cbc006ee76b7b5`
    (`0.2.0.dev0`, `PARTIAL`).
- The revealed bytes match the pre-reveal commitment, so no post-commit change
  is present.

### Fixture identity

- Artifact: `WEXP-EMILIA-INTEROP-001`.
- Exact `fixtures.yaml` SHA-256:
  `d972dbb549aaaa25e92c32a936acba4d9a686e9ca62fe6bd556b12be2962cfcc`.
- The EMILIA reveal records that hash and the exact shareable-package hash
  `0ec17bcf9b88af17016c7e05d465012af604292210a858df5fa8f9bcf00d57a0`.
- The WEXP manifest covers the same fixture bytes.
- Fixture, EMILIA reading, and WEXP reading each contain exactly one ordered
  instance of `WE-EP-001` through `WE-EP-005`.

**Commitment/reveal verification: PASS. Fixture identity: PASS.**

## 2. Comparison discipline

The following remain distinct throughout:

- EMILIA lifecycle state or outcome;
- WEXP asserted claim and appraisal;
- CAID/action correlation.

No mapping in this record treats `independent_observer` or a role label as WEXP
independent verification, `in_bounds` as execution support, EMILIA `EXECUTED`
as a WEXP verdict, or CAID/action correlation as WEXP semantic support.

The fixture leaves these common fields `UNSPECIFIED`: exact action target,
WEXP asserted claim, immutable mapping profile, evaluation context, CAID/action
correlation, and WEXP arguments-hash identity. Consequently, every WEXP case
lacks a complete Core AppraisalInput. Common missing WEXP information includes
exact target binding, an asserted claim, immutable evidence/mapping profiles,
an accepted boundary with ceiling and grounding, complete base and qualifier
findings, counter-evidence treatment, evaluation scope, and trust context.

No WEXP or EMILIA engine was run. Engine output was not needed to verify either
frozen reading and could not override it.

## 3. Five-case summary

| Case | EMILIA determination and lifecycle | WEXP determination/appraisal | Primary relation |
| --- | --- | --- | --- |
| WE-EP-001 | `UNDERDETERMINED` / `UNRESOLVED_FROM_FIXTURE` | `UNDERDETERMINED`; asserted claim `UNSPECIFIED`; no verdict | **UNDERDETERMINED ON BOTH SIDES** |
| WE-EP-002 | `UNDERDETERMINED` / `UNRESOLVED_FROM_FIXTURE` | `UNDERDETERMINED`; asserted claim `UNSPECIFIED`; no verdict | **UNDERDETERMINED ON BOTH SIDES** |
| WE-EP-003 | `UNDERDETERMINED` / `UNRESOLVED_FROM_FIXTURE` | `UNDERDETERMINED`; asserted claim `UNSPECIFIED`; no verdict | **UNDERDETERMINED ON BOTH SIDES** |
| WE-EP-004 | `UNDERDETERMINED` / `UNRESOLVED_FROM_FIXTURE` | `UNDERDETERMINED`; asserted claim `UNSPECIFIED`; no verdict | **UNDERDETERMINED ON BOTH SIDES** |
| WE-EP-005 | `DETERMINED` / `INDETERMINATE` | `UNDERDETERMINED`; asserted claim `UNSPECIFIED`; no verdict | **UNDERDETERMINED ON WEXP SIDE ONLY** |

The first four cases refuse related stronger inferences, often for overlapping
evidence gaps, but this is claim-boundary compatibility rather than a generic
pass.
WE-EP-005 is secondarily compatible at the uncertainty boundary while using a
different abstraction; that secondary note does not replace its required
primary class.

## 4. Case records and claim-boundary tests

### WE-EP-001

- **Fixture facts:** executor self-report; valid signature; `in_bounds`.
- **EMILIA reading:** `UNDERDETERMINED` /
  `UNRESOLVED_FROM_FIXTURE`. The signed `in_bounds` self-report establishes an
  actor claim, not accepted current pinning, exact action binding, executor
  admission, one-time consumption, or authoritative evidence of the effect.
  Missing: accepted current executor pin; exact authorized-action and
  admitted-operation binding; Gate admission and consumption state;
  authenticated authoritative outcome evidence.
- **WEXP reading:** `UNDERDETERMINED`; asserted claim and appraisal are not
  constructible. A signature can authenticate bytes and may contribute
  attribution, while the self-report is at most candidate evidence of what the
  actor asserted. Neither the signature nor `in_bounds` establishes content
  truth, execution, a WEXP base, or a supported claim. No accepted ceiling or
  grounding finding is present. Case-specific missing information:
  self-report-to-exact-observation predicate, accepted boundary and grounding
  class, and exact target binding, in addition to the common WEXP gaps.
- **Relation:** **UNDERDETERMINED ON BOTH SIDES**. EMILIA does not determine a
  lifecycle or effect outcome, while WEXP cannot construct execution support.
  The readings are compatible only at the non-inference and claim-boundary
  level, with system-specific additional prerequisites.
- **CAID/action correlation:** `UNSPECIFIED`; it establishes no target identity
  or semantic support. `in_bounds` is not a substitute.
- **A — EMILIA establishes:** only the actor claim described above;
  no lifecycle outcome.
- **B — WEXP establishes:** only the non-inference constraints above; no
  appraisal or verdict.
- **C — Correlation establishes:** nothing beyond the absence of an established
  correlation.
- **D — Unknown:** accepted source pin, exact authorized/admitted operation,
  Gate state, authoritative outcome evidence, WEXP target, asserted claim, and
  accepted boundary.
- **E — Stronger claim than evidence permits:** **NO**. Both readings expressly
  refuse it.

### WE-EP-002

- **Fixture facts:** an external verifier checks signatures and digests; check
  results are `UNSPECIFIED`; it does not observe the effect boundary.
- **EMILIA reading:** `UNDERDETERMINED` /
  `UNRESOLVED_FROM_FIXTURE`. External cryptographic checks alone do not
  establish the effect boundary. Missing: verifier result; accepted current
  verifier pin; exact receipt/action/operation/nonce correlation; authenticated
  evidence at the relevant effect boundary.
- **WEXP reading:** `UNDERDETERMINED`; asserted claim and appraisal are not
  constructible. Authenticity and reference-integrity checks are not passing
  content-base findings; the external role label does not establish WEXP
  independence; the facts do not establish execution or `IV(execution)`. No
  accepted ceiling or grounding finding is present. Case-specific missing:
  check results, exact assessed content base, semantic-validation and
  exact-target predicates, profile-defined independence assessment, and an
  accepted boundary.
- **Relation:** **UNDERDETERMINED ON BOTH SIDES**. EMILIA does not infer an
  effect-boundary outcome from the cryptographic checks. Separately, WEXP does
  not derive content-base, execution, IV, or accepted-boundary support from
  those checks. The two refusals are compatible without identifying a shared
  formal boundary.
- **CAID/action correlation:** `UNSPECIFIED`; exact receipt/action/operation/
  nonce linkage is absent and no WEXP target binding follows.
- **A — EMILIA establishes:** no lifecycle outcome; the checks do not establish
  the effect boundary.
- **B — WEXP establishes:** no appraisal; no content-base, execution, or IV
  support follows from the stated checks and role label.
- **C — Correlation establishes:** nothing semantically.
- **D — Unknown:** verifier result and pin, exact linkage, effect observation,
  WEXP claim, exact target, accepted boundary, and independence predicate.
- **E — Stronger claim than evidence permits:** **NO**.

### WE-EP-003

- **Fixture facts:** a system of record confirms the exact committed operation.
- **EMILIA reading:** `UNDERDETERMINED` /
  `UNRESOLVED_FROM_FIXTURE`. A system of record is authoritative for a bounded
  digital state only conditionally; the fixture does not establish an
  authenticated receipt, current accepted pin/source policy, exact binding of
  action/operation/CAID/nonce/metadata, or whether the confirmed state denotes
  acceptance, application, or final effect.
- **WEXP reading:** `UNDERDETERMINED`; asserted claim and appraisal are not
  constructible. The confirmation is candidate execution evidence, not an
  automatic supported execution finding; the source label yields neither IV
  nor PROV, and a committed operation does not itself establish durable
  external effect. No accepted ceiling or grounding finding is present.
  Case-specific missing: commit-to-execution predicate, profile-defined exact
  target equality/binding, and accepted boundary status, ceiling, and
  grounding.
- **Relation:** **UNDERDETERMINED ON BOTH SIDES**. Neither reading warrants an
  automatic execution or final-effect inference. Their prerequisites overlap
  on exact binding and semantics; EMILIA additionally lacks authenticated and
  pinned source evidence, while WEXP additionally lacks profile-defined
  execution and accepted-boundary predicates.
- **CAID/action correlation:** not established. EMILIA explicitly lists exact
  CAID binding as missing; WEXP does not derive target equality or semantic
  support from correlation.
- **A — EMILIA establishes:** no lifecycle outcome; system-of-record authority
  remains conditional.
- **B — WEXP establishes:** no appraisal; only a conditional execution-evidence
  candidate and non-inference constraints.
- **C — Correlation establishes:** nothing because the required exact
  correlation is absent.
- **D — Unknown:** authentication and source acceptance, exact multi-field
  binding, state semantics, WEXP execution predicate, target mapping, and
  accepted boundary.
- **E — Stronger claim than evidence permits:** **NO**.

### WE-EP-004

- **Fixture facts:** controller reports dispatch; a source characterized as an
  independent meter reports measured effect; exact dispatch/effect correlation
  and the WEXP independence basis are `UNSPECIFIED`.
- **EMILIA reading:** `UNDERDETERMINED` /
  `UNRESOLVED_FROM_FIXTURE`. A controller record can evidence accepted dispatch
  and a pinned meter can evidence what it observed, but EMILIA does not infer
  the missing exact command-to-observation correlation or independence basis.
  Missing: exact dispatch-to-measurement correlation; accepted current
  controller/meter pins; declared source-policy independence basis;
  measurement window and effect semantics.
- **WEXP reading:** `UNDERDETERMINED`; asserted claim and appraisal are not
  constructible. Dispatch is candidate invocation evidence and measured effect
  can be premise evidence for a profile-defined execution finding, but neither
  mapping is automatic. The word `independent` does not establish IV. No
  accepted ceiling or grounding finding is present. Case-specific missing:
  dispatch-to-invocation, exact dispatch/effect and effect-to-execution
  predicates, meter boundary status/grounding, and exact-base IV independence
  criteria.
- **Relation:** **UNDERDETERMINED ON BOTH SIDES**. Both refuse linkage by
  proximity and independence by role label. Their non-inference boundaries for
  exact linkage and role-label independence are compatible, with
  system-specific prerequisites; no shared formal boundary identity is
  established.
- **CAID/action correlation:** `UNSPECIFIED`; neither dispatch-to-effect nor
  CAID/action correlation establishes WEXP semantic support.
- **A — EMILIA establishes:** the limited source claims above, not a lifecycle
  outcome or source-policy independence.
- **B — WEXP establishes:** no appraisal; only conditional invocation,
  execution, and IV mapping candidates plus non-inference constraints.
- **C — Correlation establishes:** nothing because exact correlation is absent.
- **D — Unknown:** pins, independence basis, measurement window/effect
  semantics, WEXP exact binding, boundary grounding, base predicates, and IV
  assessment.
- **E — Stronger claim than evidence permits:** **NO**.

### WE-EP-005

- **Fixture facts:** a required meter is unavailable.
- **EMILIA reading:** `DETERMINED` / `INDETERMINATE`. The required measurement
  evidence is unavailable, so EMILIA preserves the unknown and does not convert
  it to failure, success, settlement, or retry permission. Missing: required
  authenticated measurement evidence.
- **WEXP reading:** `UNDERDETERMINED`; asserted claim and appraisal are not
  constructible. Meter unavailability supplies no passing base, boundary, or
  qualifier finding; it does not establish nonoccurrence or evaluated failure
  and is not automatically counter-evidence. No boundary ceiling or grounding
  is reported. Without a public mapping profile WEXP cannot select whether the
  meter assesses the boundary, execution base, `IV(execution)`, or applicable
  counter-evidence, nor whether a future mapped result is `unsupported` or
  `not-evaluated`. Missing: affected exact claim, normalized meter role,
  attempted-assessment status, and evaluation-scope/profile classification.
- **Relation:** **UNDERDETERMINED ON WEXP SIDE ONLY**. The determinate side uses
  an EMILIA-specific lifecycle rule, not an injected fixture fact. At the pinned
  commit, the Outcome Binding draft explicitly maps an unavailable required
  meter to `indeterminate`, while WEXP has no public EP mapping predicate that
  selects a Core role or claim. This is compatible uncertainty preservation at
  different abstraction layers, not a semantic disagreement and not an
  equivalence between EMILIA `INDETERMINATE` and a WEXP verdict.
- **CAID/action correlation:** `UNSPECIFIED`; no affected exact claim or WEXP
  semantic link is established.
- **A — EMILIA establishes:** exactly the lifecycle classification
  `INDETERMINATE`, including the prohibition on treating it as success,
  failure, settlement, or retry permission.
- **B — WEXP establishes:** no complete appraisal, verdict, downgrade,
  rejection, or boundary ceiling; it does establish the non-inference
  constraints and preserves uncertainty.
- **C — Correlation establishes:** nothing semantically.
- **D — Unknown:** the missing authenticated measurement and, for WEXP, the
  affected claim, normalized role, assessment status, and applicable profile.
- **E — Stronger claim than evidence permits:** **NO**. EMILIA's determinate
  result is a lifecycle classification of uncertainty, not a positive effect
  claim; WEXP manufactures no verdict.

## 5. Relationship and assumption findings

Primary-class counts:

- Semantic agreement: **0**.
- Compatible / different abstraction: **0 primary**; WE-EP-005 carries this as
  a secondary note.
- Underdetermined: **5 total** — four on both sides and one on WEXP only.
- Genuine semantic disagreement: **0**.
- Correlation only / no semantic mapping: **0 primary**.
- Outside current WEXP surface: **0**.

**Shared-assumption findings: NONE.** Both readings explicitly refuse the
tempting assumptions: exact action binding from labels, accepted source pins
without proof, authority from unauthenticated observation, independence from
role descriptions, and semantic support from CAID. WE-EP-005 does not depend on
a hidden shared assumption: `required` and `unavailable` are fixture facts, the
EMILIA unavailable-meter rule is explicit in its pinned source, and WEXP does
not adopt that mapping.

**Material overclaims: NONE.** The frozen readings do not warrant, and do not
make, the material stronger claims exposed by the fixtures.

**Semantic disagreements: NONE.** WE-EP-005 is an abstraction/mapping
asymmetry: EMILIA can classify its own lifecycle uncertainty; WEXP cannot
construct an appraisal without an asserted claim and public mapping profile.

## 6. Gaps, distinguishing cases, and tooling

- The WEXP freeze's pre-existing `PROFILE-GAP-001` remains: no pinned public
  EP-to-WEXP profile defines exact-target equality, CAID relationship,
  evidence-to-base predicates, accepted boundary grounding, meter/effect
  semantics, IV independence criteria, or missing-meter handling.
- This comparison exposes no new Core ambiguity and no EMILIA ambiguity needed
  to classify the five cases. A semantic difference does not by itself create
  a normative requirement.
- **Distinguishing case required: NO.** Every result is classifiable from the
  five fixtures. A sixth fixture would not supply the absent mapping profile.
- Public WEXP tooling was not run: the sparse fixtures do not construct a
  complete AppraisalInput, and engine output was unnecessary for reveal
  reproducibility or comparison.
- EMILIA code was not run. Read-only inspection of the pinned source was enough
  to confirm that missing required evidence, including an unavailable required
  meter, maps to EMILIA `INDETERMINATE` rather than a positive or negative
  effect outcome.

Relevant pinned EMILIA sources:

- [Outcome Binding draft at the frozen commit](https://github.com/emiliaprotocol/emilia-protocol/blob/9a04bea7fe680345132f6f6251fdb9a63fd8aeb2/standards/posted/draft-schrock-ep-outcome-binding-00.xml#L185-L216)
- [Gate Enforcement Profile at the frozen commit](https://github.com/emiliaprotocol/emilia-protocol/blob/9a04bea7fe680345132f6f6251fdb9a63fd8aeb2/docs/architecture/GATE-ENFORCEMENT-PROFILE.md#L68-L79)

## 7. Publication recommendation

**JOINT REVIEW READY.**

The record is suitable for Mikhail and Iman to review together. It is not yet a
public interop record, a WEXP profile proposal, a conformance result, a
certification, a standards-adoption claim, or a normative change. Publication
should remain on hold until both reviewers confirm that this record preserves
their frozen terminology and claim boundaries.

No WEXP, EMILIA, vector, EXT-10, profile, or tooling artifact was modified. No
new public claim was made.
