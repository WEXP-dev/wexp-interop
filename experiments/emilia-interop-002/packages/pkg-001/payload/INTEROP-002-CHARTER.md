---
artifact_id: WEXP-EMILIA-INTEROP-002-CHARTER-DRAFT-004
experiment_id: WEXP-EMILIA-INTEROP-002
status: DRAFT_FOR_JOINT_DESIGN_REVIEW
date: 2026-08-23
supersedes: WEXP-EMILIA-INTEROP-002-CHARTER-DRAFT-003
predecessor: WEXP-EMILIA-INTEROP-001
framework: WEXP_INTEROP_PROTOTYPE-000
successor_reason: VOLATILE_HOSTED_BASELINE_MOVED_TO_EXECUTION_FREEZE
scientific_design_changed: false
sent_for_joint_review:
  artifact_id: WEXP-EMILIA-INTEROP-002-CHARTER-DRAFT-002
  bytes: 21663
  sha256: e8653a1e8a6f632f7c18522566f73fe2151ddf1846f87a5b62352af7e77b47da
  git_commit: bcb607290425550f28a641b3007ee4dcf6683cca
  git_blob: a3c3434eb81170ce38ec2ce51f8d131eee47baa2
  status: SENT — NOT WITHDRAWN, NOT RETRACTED, NOT SUPERSEDED SCIENTIFICALLY
  role: scientific-design artifact reviewed and accepted by the EMILIA-side contributor
historical_successor:
  artifact_id: WEXP-EMILIA-INTEROP-002-CHARTER-DRAFT-003
  bytes: 30178
  sha256: 2dac498480dd99a5cfb04fcc47467452f41ef8b89a5f9f9e184eabe4869c78db
  git_blob: 9aed5e5bf954ee7e099ecb01b13dab60b171aafb
  role: historical infrastructure and security-contract successor
  status: PRESERVED — NOT REJECTED; its hosted commit and tree baseline became
    historical after the HL-001 remediation, so it is not the current freeze
    candidate
execution_authorized: false
publication_authorized: false
design_frozen: false
bridge_authorized: false
blind_case_commitment_authorized: false
---

# WEXP × EMILIA INTEROP-002 Charter

## 1. Decision sought

This draft seeks **joint design review only**. It does not authorize bridge
implementation, fixture execution, publication, a change to WEXP Core, a change
to EMILIA, or a change to the generic Prototype-000 core.

DRAFT-002 incorporates two EMILIA-side review points: causal provenance and
evaluation context remain separately testable, and evidence is explicitly
prohibited from becoming permission, local authorization, or Gate admission.
The draft is still not a Design Freeze.

DRAFT-003 succeeded DRAFT-002 by adding the hosted trust-boundary invariants
and the B-01 admission discipline, and by recording the then-current public lab
identity. DRAFT-004 succeeds DRAFT-003 by correcting where a hosted identity
belongs. A charter that names a public lab commit as *current* is wrong the
moment that lab advances, and it advanced: the HL-001 harness defect was
corrected and the hosted baseline moved. The fix is architectural rather than
factual — the charter states the properties hosted execution must satisfy, and
the **Execution Freeze** binds the exact infrastructure that will satisfy them.

**The scientific design is unchanged.** Research question, hypotheses, safety
invariants, case architecture, blind-case semantics, verdict model, freeze
architecture, claim ceilings and bridge semantics are carried from DRAFT-002
without substantive alteration, and every security property DRAFT-003 added is
preserved. Neither predecessor was erroneous. What DRAFT-004 changes is
confined to Sections 9.2, 18 and 19 and the frontmatter.

Within this charter, `MUST`, `MUST NOT`, `SHOULD`, and `MAY` govern this
experiment only. They are not normative requirements on WEXP, EMILIA, or any
external specification.

## 2. Starting point and authority boundary

WEXP × EMILIA INTEROP-001 established a bounded result:

- EMILIA distinguished the action-bound pair P/P-1;
- WEXP remained `UNDETERMINED` because no frozen public EP→WEXP mapping
  constructed a complete Core `AppraisalInput` or assigned the missing
  `action_caid` relation a WEXP semantic role;
- the terminal result was **Branch A — Explicit Bridge Required**;
- neither system was made to claim more than its frozen evidence supported.

`EP-WEXP-MAPPING-REQUIREMENTS-001.md` records eighteen functions that a future
mapping may need to define. It is design input, not a bridge, not experiment
authority for INTEROP-001, and not a normative WEXP or EMILIA profile.

Prototype-000 has now produced the same semantic projection through local
manual, local assisted, local automated, and real GitHub-hosted orchestration.
That establishes orchestration invariance for its worked exercise. It does not
yet establish portability to an independently designed prospective experiment.

INTEROP-002 is intended to test that next boundary.

## 3. Research question

Can a versioned, explicit EP→WEXP bridge:

1. construct the complete WEXP appraisal input required for a declared
   action-bound positive control;
2. fail closed, remain underdetermined, or limit the resulting claim when a
   hostile case breaks a required binding; and
3. contain no declared bridge element that can be removed without losing the
   positive construction or one of the required safety properties?

The third question is **local minimality relative to the declared bridge
elements and frozen case set**. This experiment does not claim global
minimality across all possible representations, mappings, or protocols.

## 4. Hypotheses

### H-SUFF — bridge sufficiency

The frozen bridge candidate preserves every invariant and separately testable
sub-invariant in Section 5 over the positive control, every open hostile family,
and the independently committed blind case.

A hostile case may legitimately yield rejection, non-constructibility,
`UNDETERMINED`, a lower claim ceiling, or another pre-authorized fail-closed
result. A bridge does not fail merely because it refuses to construct an unsafe
claim.

### H-MIN — local minimality

Each declared atomic bridge element is necessary relative to the frozen case
set. Removing that element while holding all other bytes constant MUST cause at
least one of the following:

- the positive control can no longer construct the intended complete input;
- a precommitted result changes to a less informative fail-closed result; or
- at least one invariant is no longer preserved.

Single-element ablation is sufficient for this experiment. No claim is made
about interactions among multiple simultaneous removals or about a globally
minimal bridge.

## 5. Safety invariants

### I-01 — subject and action-instance binding

Evidence for one actor, action, operation, receipt, or action instance MUST NOT
be usable as evidence for another. Equality of action type alone is
insufficient when the claim concerns a particular execution instance.

### I-02 — phase integrity

The bridge MUST NOT silently promote one phase into another. In particular,
intent, authorization, invocation, transport acknowledgement, observation,
completion, external effect, and execution remain distinct unless the frozen
mapping explicitly supplies the predicates required for the selected WEXP
claim.

### I-03 — causal provenance and evaluation-context integrity

The two parts below are independently testable. A case that establishes one
does not establish the other.

#### I-03a — causal provenance

The bridge MUST preserve the provenance and bindings needed to distinguish an
observation attributable to the selected action instance from a coincident,
replayed, reordered, substituted, or rebound observation. The relevant action,
operation, receipt, resource or facility, evidence chain, and ordering
relations MUST be explicit enough for the selected claim. Missing or ambiguous
causal provenance MUST fail closed or remain explicitly underdetermined.

#### I-03b — evaluation context

The bridge MUST preserve the relying-party policy, trust set, time window,
evaluation scope, and evidence set under which the mapped appraisal is made. An
observation may be causally related to the action and still be inadmissible
under the wrong policy, trust set, time window, or scope. Missing or ambiguous
evaluation context MUST fail closed or remain explicitly underdetermined.

### I-04 — claim monotonicity and non-claim preservation

The mapped WEXP claim MUST NOT be stronger than the source evidence and frozen
mapping support. The bridge MUST NOT silently add completion, external effect,
semantic truth, independent verification, or a higher claim ceiling. Source
limitations and non-claims MUST remain visible.

### I-05 — evidence confers no authority

An EP receipt, outcome observation, correlation, or mapped WEXP appraisal MAY
support only the frozen appraisal claim for which it is admitted. It MUST NOT
become reusable permission, local authorization, Gate admission, delegated
authority, a capability for future action, or approval under another policy.
Any authority-bearing conclusion requires its own explicit authority source,
scope, and evidence. Missing authority MUST fail closed and MUST NOT be inferred
from successful execution or appraisal evidence.

## 6. Case architecture

The Design Freeze MUST bind exact bytes for one positive control and three open
hostile families. A separate blind case is committed independently before the
bridge is authored.

### C-00 — positive action-bound control

The positive control SHOULD reuse the published INTEROP-001 P fixture unless
joint design review identifies a concrete reason that it cannot exercise the
selected bridge claim. The bridge MUST construct the declared complete WEXP
input without inventing missing source facts. The WEXP and EMILIA expectations
for the resulting case MUST be committed before execution.

### H-01 — identity, causal-provenance, and evaluation-context family

This family MUST include the published P-1 missing-`action_caid` regression or a
byte-identical reuse of it. It MUST also contain independently scored variants
for:

- an identity, substitution, replay, or rebinding break affecting the selected
  action instance or causal provenance; and
- an evaluation-context break in which apparently related evidence is assessed
  under the wrong relying-party policy, trust set, time window, evidence set, or
  scope.

A single fixture MAY exercise both variants, but the frozen expectations MUST
score the two properties separately.

### H-02 — phase-confusion family

This family MUST present evidence sufficient for a lower or different phase but
insufficient for the selected execution claim. The bridge passes only if the
result preserves the phase boundary and the precommitted claim ceiling.

### H-03 — claim-expansion and authority-conversion family

This family MUST test an attempted addition of at least one unsupported
property, such as completion, external effect, semantic truth, or independent
verification. It MUST also test an attempted conversion of an EP receipt,
outcome observation, or mapped appraisal into reusable permission, local
authorization, Gate admission, delegated authority, or approval for a future
action. The bridge passes only if the unsupported expansion or authority
conversion is refused or remains explicit as unsupported.

### B-01 — independently committed blind hostile case

Iman Schrock, or another separately authorized EMILIA-side contributor, supplies
one exact hostile case after reviewing this charter but before seeing the
bridge candidate bytes.

The contributor MUST first provide only:

- the case identifier;
- the invariant or invariants the case is intended to attack;
- the exact byte count; and
- a SHA-256 commitment to the unrevealed case bytes.

The case bytes remain withheld until the bridge candidate and Execution Freeze
are fixed. Reveal is accepted only if the bytes match the prior commitment.
The revealed case MUST NOT be altered to accommodate the bridge result.

One blind case is sufficient for INTEROP-002. Additional blind cases require a
specific design rationale, not a desire to improve the final verdict.

#### B-01 admission discipline

The commitment above governs what B-01 *means*. This governs where its bytes
may exist, which is a separate question and an infrastructure one.

**Before reveal authorization:**

- B-01 bytes MUST NOT exist in any public publication staging path;
- B-01 MUST NOT have an entry in the publication allowlist;
- no wildcard may admit it, because the allowlist admits exact paths only and
  a wildcard is precisely how an unrevealed fixture reaches a bundle nobody
  meant to put it in;
- only the commitment metadata this charter permits — identifier, target
  invariant(s), byte count, SHA-256 — may exist in any staged or published
  material.

**At reveal authorization:**

- the exact revealed artifact identity and path are known;
- an explicit exact allowlist entry MAY then be created for that path;
- the revealed bytes and digest MUST be checked against the prior commitment
  **before** any semantic execution consumes them.

**Reveal authorization is an act, not an observation.** The experiment monitor,
the bridge author, the tooling and the workflow MUST NOT infer that reveal has
been authorized from the fact that bytes have become available. Availability is
not authorization, and a procedure that treats it as authorization has removed
the boundary the blind case exists to create.

No reveal authorization is issued by this charter.

## 7. Bridge candidate requirements

The bridge candidate MUST be a versioned, machine-readable,
experiment-specific artifact, provisionally named `BRIDGE-CANDIDATE.yaml`.

It MUST:

1. enumerate atomic elements under stable identifiers such as `B-01`, `B-02`,
   and so on;
2. give each element one reviewable purpose;
3. trace each element to one or more relevant functions in
   `EP-WEXP-MAPPING-REQUIREMENTS-001.md`;
4. explicitly mark every mapping requirement used by the selected claim as
   resolved, not applicable, or fail-closed/non-constructible, with rationale;
5. define all normalization, equality, issuer, identity, correlation, timing,
   causal-provenance, relying-party-policy, trust-set, evaluation-scope,
   boundary, grounding, counter-evidence, independence, claim-ceiling, and
   non-authority predicates it relies on;
6. contain no hidden fallback to a floating branch, default value, inferred
   authority, or unpinned external semantics; and
7. produce either a complete typed construction or an explicit typed failure.

EMILIA-specific logic MUST remain in the experiment or adapter layer. Adding
INTEROP-002 MUST change zero bytes of `interop_core/`. WEXP Core and the EMILIA
specification remain unchanged by this experiment.

## 8. Verdict model

Existing Prototype-000 case statuses, relations, and terminal outcomes remain
unchanged and authoritative. INTEROP-002 adds only report-level axes; it does
not add a new generic core taxonomy.

### Execution status

- `EXECUTED`
- `INFRASTRUCTURE_UNAVAILABLE`
- `EXPERIMENT_INVALID`

### Bridge sufficiency

- `SUPPORTED` — C-00 is constructible as declared, all precommitted
  expectations relevant to the conclusion are reproduced, and every invariant
  is preserved across all frozen cases.
- `REJECTED` — the bridge cannot perform its declared positive construction, or
  at least one hostile case permits a prohibited rebinding, causal-provenance
  break, evaluation-context misuse, phase promotion, claim expansion, or
  authority conversion.
- `INCONCLUSIVE` — the frozen evidence cannot decide sufficiency without
  overclaiming, and no unsafe bridge behavior has been established.
- `NOT_EVALUATED` — execution did not reach a valid semantic evaluation.

### Local minimality

- `SUPPORTED` — every declared atomic element is shown necessary by the frozen
  single-element ablation set.
- `REJECTED` — at least one declared element can be removed while preserving
  all sufficiency conditions and precommitted results relevant to the claim.
- `NOT_ESTABLISHED` — the ablation set is incomplete or cannot decide necessity.
- `NOT_EVALUATED` — execution did not reach a valid ablation evaluation.

Infrastructure absence is never interpreted as bridge rejection. A procedure
defect is never interpreted as a semantic result.

## 9. Two freeze boundaries

### 9.1 Design Freeze

Before bridge authoring begins, the Design Freeze MUST bind:

- the exact charter bytes;
- exact identities of the WEXP and EMILIA source authorities;
- exact bytes of C-00 and all open hostile fixtures;
- the B-01 commitment, byte count, and declared target invariant(s);
- role assignments and any unavoidable role fusion;
- the intended WEXP claim and its claim ceiling;
- the evidence-publication allowlist; and
- the statement that any generalization remains prohibited by Section 13.

A change to any of these items invalidates the Design Freeze and requires an
explicitly identified successor, not a silent edit.

### 9.2 Execution Freeze

Before B-01 is revealed, the Execution Freeze MUST bind:

- the Design Freeze identity;
- exact `BRIDGE-CANDIDATE.yaml` bytes and element inventory;
- exact experiment policy and comparison policy;
- the exact execution-infrastructure manifest described below;
- the ablation plan;
- the B-01 commitment; and
- the permitted report-level verdicts.

#### 9.2.1 Execution-infrastructure manifest

Hosted identities are volatile. A public lab advances, a workflow is corrected,
an action is repinned — and a charter that named any of those as *current*
becomes false without anyone editing it. So this charter states the properties
hosted execution MUST satisfy, and the Execution Freeze binds the exact
infrastructure that will satisfy them.

The Execution Freeze MUST bind an exact manifest, provisionally
`HOSTED-INFRASTRUCTURE-BASELINE-001.json`, recording directly or by reference:

- the public lab repository identity;
- its exact commit;
- its exact tree;
- the exact workflow identity and content digest;
- the exact adapter identities;
- the exact action pins relevant to the execution;
- the exact public source pins;
- the private tooling identity **handling policy** — never the private
  identity itself;
- the exact hosted canary run identity;
- the canary execution status;
- the publication-gate status;
- the disclosure-scan status;
- the post-gate immutability status;
- the exact public evidence artifact identity and digest, where an artifact is
  retained as readiness evidence.

The manifest is bound at Execution Freeze and nowhere earlier. **No such
manifest is created by this charter**, and no hosted identity named anywhere in
this document is an execution authority.

After the Execution Freeze:

1. B-01 is revealed and verified against its commitment;
2. the revealed bytes are admitted as the frozen blind fixture;
3. each party commits expectations before any implementation execution;
4. the bridge, cases, authorities, policies, and verdict rules remain
   unchanged; and
5. execution proceeds through the existing framework state machine.

No third design freeze is required. The expectation commitments, reveal check,
and append-only execution record supply the remaining chronology.

## 10. Roles and separation

### Founder

- approves `DESIGN GO`, `EXECUTION GO`, and `PUBLICATION GO`;
- approves any successor to a failed freeze;
- decides whether post-result findings remain experiment-specific or become
  candidates for later external replication.

### WEXP-side design owner

- prepares the bridge candidate and WEXP-side expectations from frozen
  authorities;
- does not see B-01 bytes before the Execution Freeze;
- does not modify the bridge after B-01 reveal.

### EMILIA-side contributor

- confirms or corrects the EMILIA-side authority description;
- supplies the B-01 commitment and later exact reveal;
- commits the EMILIA-side expectation before execution; and
- reviews whether the final comparison represents the native EMILIA result
  fairly.

### Experiment operator / local verifier

- freezes bytes, computes manifests, executes the authorized procedure, and
  performs an independent disclosure scan;
- does not select the semantic verdict or rewrite expectations;
- records failures rather than tuning fixtures until they pass.

### GitHub Actions

- executes the frozen procedure;
- is not an epistemic authority, reviewer, witness of physical truth, or owner
  of the result.

Role separation follows the experiment policy. Any unavoidable fusion is
recorded as reduced assurance rather than hidden.

## 11. Hosted execution procedure

1. Run the unchanged X-001 hosted canary against the selected framework
   baseline.
2. If the canary cannot execute, record `INFRASTRUCTURE_UNAVAILABLE`; draw no
   semantic conclusion about INTEROP-002.
3. Verify B-01 reveal, all source pins, bridge identity, fixture identities,
   policy identity, and expectation chronology.
4. Run the positive, open hostile, blind, and ablation cases without changing
   their frozen bytes.
5. Preserve each system's native output before comparison.
6. Derive the existing case-level relations, then derive the report-level
   sufficiency and local-minimality verdicts.
7. Re-run only after an infrastructure failure, using the exact same frozen
   semantic inputs. A semantic failure is not repaired by redesigning the
   bridge under the same experiment identity.

The hosted path MUST remain within the free public GitHub Actions contour. Any
authorized private tooling fetch MUST use a short-lived, repository-scoped,
read-only credential minted at run time and never persisted. No personal access
token, and no long-lived credential of any kind, is permitted as a fallback.

### 11.1 Hosted trust-boundary invariants

These are the orchestration properties the hosted path has established and MUST
continue to satisfy. They are **experiment infrastructure requirements**. They
are not normative requirements on WEXP, on EMILIA, or on any external
specification, and nothing here may be cited as one.

1. Counterparty execution occurs in a **separate execution domain** — a
   distinct job, on a distinct runner, with a distinct filesystem.
2. That domain contains **no private WEXP checkout, no private WEXP credential,
   and no protected private tooling**.
3. Exchange into the coordination domain is **artifact-only** and limited to
   declared native outputs. Code does not cross the boundary; data does.
4. The coordination domain **does not execute externally controlled
   counterparty code**, before the publication gate or after it.
5. Publication uses an **exact, wildcard-free allowlist**. A staged file that
   no entry admits fails the run.
6. **All semantic execution completes before final publication staging
   begins.**
7. The final sequence is substantially:

       stage
       -> freeze
       -> allowlist validation
       -> disclosure scan
       -> manifest
       -> immutability verification
       -> upload

8. **No semantic transformation and no untrusted mutation occurs after the
   final disclosure gate.** Only deterministic, non-mutating upload mechanics
   may follow it.
9. The private tooling identity is **verified during execution and excluded
   from public evidence**. A published artifact carrying it is refused rather
   than published.
10. **Job separation is the claimed isolation boundary**, and the only one
    claimed.

**Explicit non-claim.** This is not an operating-system sandbox and not a
defence against compromise of the hosting platform. If a future counterparty
requires a stronger boundary than job separation, this topology is insufficient
and the correct response is to say so and stop — not to describe job separation
as isolation it does not provide.

## 12. Public evidence contract

The final Design and Execution Freezes MUST contain an explicit allowlist. That
allowlist admits **exact paths only**. Wildcards, prefixes and globs are
refused, and an unknown or unclassified staged file fails closed rather than
being published on the assumption that it is harmless.

Subject to contributor review and publication approval, the allowlist may
include:

- frozen charter and freeze manifests;
- public authority pins and authorized source artifacts;
- bridge candidate and element inventory;
- open and revealed blind cases;
- commitment and reveal verification records;
- party expectations and native outputs approved for publication;
- semantic bundle, comparison, outcome, claims registry, status, ablation
  results, manifests, and reproduction instructions; and
- a ledger-head commitment only when the Execution Freeze explicitly marks it
  publishable and states what it binds.

The public package MUST exclude:

- tokens, keys, secrets, and credential values;
- GitHub App operational identifiers not needed by the scientific record;
- the protected private tooling pin, private branch/ref names, and private
  tooling commit identity;
- local filesystem paths;
- private source bytes or private per-file digests not explicitly admitted by
  the publication contract;
- ledger bodies not explicitly approved for publication;
- unrelated repository, billing, or historical-run metadata; and
- B-01 bytes before reveal, which MUST NOT be present in any staging path and
  MUST NOT hold an allowlist entry until reveal is authorized (Section 6,
  B-01 admission discipline).

A ledger-head digest is a commitment to bytes, not proof that those bytes are
true or semantically correct.

## 13. Generalization rule

INTEROP-002 cannot by itself change WEXP Core, the EMILIA specification, or the
generic Prototype-000 core.

Any apparently reusable finding is labelled `CANDIDATE_GENERIC` only. Promotion
requires:

1. a separate Founder decision;
2. reproduction with at least one non-EMILIA external system; and
3. a change process independent of the INTEROP-002 publication decision.

A third exemplar inside the WEXP × EMILIA line is not external replication by
itself.

## 14. Claims that remain prohibited

INTEROP-002 MUST NOT be described as establishing:

- physical truth of an execution or effect;
- correctness, security, or completeness of WEXP or EMILIA;
- global minimality of the bridge;
- universal EP↔WEXP interoperability;
- conformance, certification, adoption, or IETF endorsement;
- WEXP independent verification merely from an EMILIA role label;
- that an EP receipt, outcome observation, or mapped appraisal grants reusable
  permission, local authorization, Gate admission, delegated authority, or
  approval for a future action;
- a generic Bridge Framework; or
- validity beyond the frozen authorities, bridge, cases, and verdict rules.

A negative, rejected, underdetermined, or inconclusive result remains
publishable if the procedure and evidence trail are valid.

## 15. Decision gates

### DESIGN GO

Authorizes completion and freezing of the Design Freeze package. It does not
authorize execution.

### EXECUTION GO

Requires an exact Execution Freeze, successful pre-run disclosure review, and
verified readiness to receive B-01 reveal. It authorizes reveal and execution
only against the frozen identities.

### PUBLICATION GO

Requires independent byte verification, disclosure audit, WEXP-side claim
review, EMILIA-side fairness review, and an exact publication candidate. It may
approve any valid result or hold publication without rewriting the result.

## 16. Minimum contribution requested from the EMILIA side

To keep the collaboration bounded, INTEROP-002 asks for only three substantive
contributions from Iman Schrock:

1. review this charter and correct any unfair or inaccurate EMILIA-side
   assumption;
2. provide one B-01 commitment and later the matching reveal; and
3. verify the exact final record and whether it represents the native EMILIA
   result fairly.

Additional implementation or authorship work is optional and must be separately
agreed.

## 17. Definition of done

INTEROP-002 is complete when:

1. the charter and exact open cases were fixed before bridge authoring;
2. B-01 was committed before the bridge candidate was visible;
3. the bridge was frozen before B-01 reveal;
4. the reveal matched the prior commitment;
5. party expectations preceded execution;
6. hosted execution used unchanged generic core and exact frozen inputs;
7. bridge sufficiency and local minimality received explicit verdicts;
8. the result was independently checked for bytes, claims, and disclosure;
9. the exact result was approved for publication or explicitly held; and
10. no WEXP, EMILIA, or generic-core change was inferred automatically.

A third protocol, a universal bridge, a new specification, and promotion of any
generic finding are outside this Definition of Done.

## 18. Stable reference identities

These are stable scientific reference points. They are not the INTEROP-002
Design Freeze and they are not an execution baseline.

- INTEROP-001 P: `b552da51858d0256a562e800a81a870435d6e136c9bc28833b962b6d3723fb3e`
- INTEROP-001 P-1: `67556d28d272b4b01a73e1c1465248644dd7a05460fc149aa77df92cf36403a0`
- INTEROP-001 result: `BRANCH A — EXPLICIT BRIDGE REQUIRED`
- INTEROP-001 semantic projection observed for the X-001 worked example:
  `bc409c308491de92ffb2f7786c305f6c88c7785b10df9541b82a4b83c7644c5f`
- that worked example's outcome: `MAPPING_REQUIRED`

**No hosted execution identity is listed here, deliberately.** The properties
hosted execution must satisfy are defined by Sections 9, 11 and 12. The exact
hosted execution baseline — repository, commit, tree, workflow, adapters,
action pins, source pins, canary run and gate statuses — is selected and bound
only by the Execution Freeze infrastructure manifest of Section 9.2.1. A commit
named in a charter as *current* stops being current without anyone editing the
charter, which is how a document quietly starts asserting something false.

No private repository head, private branch name, or protected private tooling
identity is recorded in this charter, and none may be added to it. The private
tooling identity is verified at execution time and never written down here.

Historical hosted identities appear only in Section 19, explicitly labelled
historical. They are provenance, never execution authority.

This draft remains **not frozen and not executable** until exact-byte joint
design review and a separate Founder `DESIGN GO`.

## 19. Provenance: three layers, one scientific design

This charter has three predecessors on record. They differ in role, not in
science.

**DRAFT-002 — the scientific-design artifact.** Reviewed and accepted by the
EMILIA-side contributor. Its design is the reference against which every later
draft is checked, and it remains unchanged.

**DRAFT-003 — a historical infrastructure and security-contract successor.**
Created after the hosted interop infrastructure was security-hardened and
before the HL-001 defect was corrected. It added the hosted trust-boundary
invariants, the B-01 admission discipline, the exact wildcard-free publication
allowlist and the post-disclosure immutability requirement — **all preserved
here.** It also recorded a then-current public lab commit and tree. Those
became historical when the lab advanced, which is why DRAFT-003 is not the
current freeze candidate. It is preserved, not rejected.

    artifact_id  WEXP-EMILIA-INTEROP-002-CHARTER-DRAFT-003
    bytes        30178
    SHA-256      2dac498480dd99a5cfb04fcc47467452f41ef8b89a5f9f9e184eabe4869c78db
    git blob     9aed5e5bf954ee7e099ecb01b13dab60b171aafb

**DRAFT-004 — this document.** One architectural correction: volatile hosted
identities move out of the charter's current-state assertions and into the
Execution Freeze infrastructure manifest (Section 9.2.1). Every DRAFT-003
security property is preserved and the DRAFT-002 scientific design is
unchanged.

### HL-001, recorded only as far as succession requires

A defect in the **public** counterparty harness resolved a relative workspace
path from a changed working directory, so the counterparty was asked for a
request that was not where it had been told to look. Every case returned
unconstructible.

The fail-closed cross-check refused publication: nothing was staged, scanned,
manifested or uploaded, and **no semantic conclusion was drawn from that run**.
The correction was confined to the harness. A later hosted canary succeeded and
reproduced the frozen semantic projection exactly.

That is the whole of what this charter needs from HL-001. The engineering
record and the private tooling topology stay where they belong, which is not
here.

### The artifact already sent

DRAFT-002 is the exact artifact that was sent to the EMILIA-side contributor
for joint design review:

| | |
| --- | --- |
| Artifact | `WEXP-EMILIA-INTEROP-002-CHARTER-DRAFT-002` |
| Bytes | 21,663 |
| SHA-256 | `e8653a1e8a6f632f7c18522566f73fe2151ddf1846f87a5b62352af7e77b47da` |
| Git commit | `bcb607290425550f28a641b3007ee4dcf6683cca` |
| Git blob | `a3c3434eb81170ce38ec2ce51f8d131eee47baa2` |

That send stands. It is **not withdrawn and not retracted**, and its scientific
design is **not rejected**. DRAFT-002 remains recoverable byte-for-byte at the
commit and blob above; nothing in this successor rewrites it.

That send stands. DRAFT-002 was correct when written, and each successor was
occasioned by fact rather than by error.

The DRAFT-003 to DRAFT-004 changes are confined to:

| Section | Change | Class |
| --- | --- | --- |
| Frontmatter | artifact identity, successor reason, DRAFT-003 provenance layer, explicit authorization flags | status / provenance |
| §1 | why DRAFT-004 exists | provenance |
| §9.2 + new §9.2.1 | the Execution Freeze binds an exact execution-infrastructure manifest | architecture |
| §18 | volatile hosted identities removed; stable scientific references retained | factual baseline |
| §19 | this section, and HL-001 recorded at succession level | provenance |

The cumulative DRAFT-002 to DRAFT-004 change is the union of that table with
the DRAFT-003 additions preserved here: the B-01 admission discipline, the
hosted trust-boundary invariants, the short-lived repository-scoped read-only
private-tooling credential property, the exact wildcard-free publication
allowlist, the staged-file fail-closed rule, the post-disclosure immutability
requirement and the job-separation non-claim.

Every other section is carried from DRAFT-002 without substantive alteration.
The research question, H-SUFF, H-MIN, I-01 through I-05 with I-03a and I-03b
independently testable, C-00, H-01, H-02, H-03, blind-case semantics, local
minimality, single-element ablation, the case-level taxonomy, the report-level
sufficiency and minimality axes, permitted terminal outcomes, stance maps,
claim ceilings, bridge semantics, the no-repair-under-same-ID rule, the
two-freeze architecture, the prohibition on automatic generic promotion, EMILIA
semantics and WEXP semantics are unchanged.

Semantic diff classification:

    INFRASTRUCTURE BASELINE / SECURITY CONTRACT UPDATE ONLY

This draft is **not** a Design Freeze. No bridge is authorized, no blind-case
commitment is authorized, no execution is authorized, and no publication is
authorized.
