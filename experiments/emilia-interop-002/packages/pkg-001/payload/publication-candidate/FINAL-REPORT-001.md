# WEXP × EMILIA INTEROP-002 — final report

**Status:** publication candidate. **Not published.** Awaiting counterparty
exact-byte review, then a separate Founder PUBLICATION GO.

**Charter:** DRAFT-004, `INTEROP-002-CHARTER.md`, sha256 `814cd13f…eae61`,
never modified after freeze.

---

## What was tested

Whether a frozen, declared bridge can carry **one** narrow WEXP claim from
EMILIA outcome-binding evidence — and, more importantly, whether it *refuses*
when it should.

The claim under test, **CC-1**, is `(observation, {IV})`. Its positive ceiling,
fixed in advance, reads verbatim:

> Under the frozen evaluation context, an independently verified observation
> that an event concerning the exact action instance `operation:plant-7:001`
> was recorded — and nothing above the observation base.

Seven cases: one positive control, five open hostile cases, and **B-01** — a
blind hostile case committed by the EMILIA-side contributor by SHA-256 before
the bridge was authored, revealed only after the Execution Freeze.

## Headline results

| | |
|---|---|
| **WEXP bridge sufficiency** | **SUPPORTED** |
| **Joint WEXP × EMILIA comparison** | **INCONCLUSIVE** for every case lacking a native EMILIA output |
| **Local minimality (H-MIN)** | **NOT_ESTABLISHED** — 15 of 17 elements shown necessary |
| **Counterparty fairness review** | **PASS_WITH_PRECISIONS** |
| **H-03 IV divergence** | **RESOLVED_BY_SCOPE_SEPARATION** |

**These two scopes are not one verdict and must not be collapsed into one.**
The bridge did its job. The two-party comparison mostly could not be completed.
Both statements are true at once.

> **This is a claim ceiling, not a failed experiment.**

The charter anticipated exactly this: *"A negative, rejected, underdetermined,
or inconclusive result remains publishable if the procedure and evidence trail
are valid."*

---

## B-01 — the blind case

The contributor changed **one field** from the positive control:
`options.expectedOperationId`, `operation:plant-7:001` → `:002`. The action
digest and the CAID were left **matching**. Both observations still attest
`:001`.

| | |
|---|---|
| typed outcome | `INDETERMINATE` |
| CC-1 supported | `false` |
| ceiling base | `null` |
| IV | `not-evaluated` |
| rejection reason set | `{exact_binding_mismatch:operation_id}` — exactly one |
| I-01 | **PRESERVED** |
| I-03a | **PRESERVED** |

The WEXP side committed a written expectation before running anything against
these bytes. It **reproduced on all 23 compared fields, zero differences** —
including the terminal state, the single-token reason set, both invariant
verdicts, and a prediction about minimality that had been reasoned but not
measured.

### Why this case mattered more than the five open ones

**BE-04 is necessary, and only B-01 could prove it.**

Remove bridge element BE-04 alone and B-01 flips from `INDETERMINATE` to
`CONSTRUCTED_CLAIM_SUPPORTED`: a *supported* claim about `operation:plant-7:002`
carried by evidence attesting `:001`. Nothing else in the bridge catches it,
because the action digest and the CAID both still match.

The open hostile set could not have shown this. H-01-b rebinds three fields at
once, so another element always covered for BE-04 and it looked dispensable.
B-01 rebinds the operation identifier **only**. Local minimality moved from
14/17 to 15/17 on this case alone.

This is the value of committing a blind case by digest to someone who has not
seen your implementation.

## Local minimality: NOT_ESTABLISHED, and not massaged

15 of 17 elements are shown individually necessary. **BE-03** and **BE-06** are
not, and they were **not deleted to improve the number**:

- **BE-03** — no frozen case carries a stale, compromised, not-yet-valid or
  expired source pin. Nothing in the case set can discriminate it. It stays
  because EMILIA outcome-binding §§4 and 6 require refusing such sources.
  Removing it to score better would trade a normative requirement for a number.
- **BE-06** — B-01 leaves the CAID matching, so BE-06 never fires on it, and it
  still masks with BE-04 on H-01-b.

A two-element diagnostic (removing BE-04 *and* BE-06 together breaks H-01-b) is
recorded but **not counted**, because the frozen method admits single-element
ablation only.

## H-03 — resolved by separating scopes, not by compromise

The open divergence was about IV. It is now resolved, and **no frozen artifact
moved** to resolve it:

1. An EMILIA role label alone does **not** establish independent verification.
2. WEXP **may** derive IV from its frozen four-part predicate where satisfied.
3. That IV is a **WEXP conclusion**.
4. It does **not** establish independent verification of EMILIA semantics.

Both parties were already right about different questions. The fixture's ground
— that a registry role label is not evidence — was correct, and the bridge never
used a role label. The bridge's ground — that its own four-part predicate can
support a WEXP-side finding — was also correct, and it never claimed to speak
for EMILIA. Separating the scopes dissolves the disagreement without either
predicate changing.

Charter §14 already prohibited *"WEXP independent verification merely from an
EMILIA role label."* This resolution states a ceiling the charter always had.

## The honest gap: EMILIA native outputs

A joint comparison needs both parties' native outputs. **For five of seven cases,
only one exists.**

The final record originally said no EMILIA native output existed *for any* case.
**That was overstated, and the WEXP side corrected it before the contributor
reviewed it** — additively, leaving the original record byte-identical rather
than quietly editing it. The INTEROP-001 final-candidate package contains real
outputs from EMILIA's verifier at commit `9a04bea7` — the same commit every
INTEROP-002 fixture pins.

The contributor's precision, bound here: those outputs support **C-00** and
**H-01-a** *only because the corresponding inputs are byte-identical*.

**No native EMILIA output is established for H-01-b, H-01-c, H-02, H-03 or
B-01.** And a standing prohibition applies:

> **An available verifier implementation is NOT a frozen execution procedure.**
> It was not run. Results were not backfilled.

The gap is a genuine experiment-design finding, and it is published as one: the
charter presupposes a native output from each system (§10 step 5, §11.1 item 3,
§16) yet never asks the contributor for one and defines no procedure that
produces one for the INTEROP-002-specific cases.

## Anti-tuning evidence

The contributor's four precommitted B-01 expectation fields are field-for-field
EMILIA's own recorded native result for `P-1`, from 2026-08-21 — before the
bridge existed in reviewable form and without his seeing the bridge bytes.

- **ANTI_TUNING_EVIDENCE: SUPPORTED.** The expectation was not reverse-engineered
  from the bridge, and the bridge — authored blind to B-01 — was not tuned to the
  case. Neither side was fitted to the other.
- **SEMANTIC_PRECEDENT: SUPPORTED.** EMILIA's refusal token for a not-exactly-
  bound observation was not invented for this experiment.
- **Limitation: it does NOT constitute an EMILIA execution of B-01.** B-01 stays
  INCONCLUSIVE at the joint scope.

One caveat is not withdrawn: the two sides' agreement on *cause* is partly **by
construction**, because BE-04 was deliberately built on EP §6. That was recorded
before execution, not after the result was known.

---

## What this does NOT establish

- Not physical truth of any execution or effect.
- Not correctness, security or completeness of WEXP or EMILIA.
- Not global minimality of the bridge. **H-MIN is NOT_ESTABLISHED.**
- Not universal EP↔WEXP interoperability.
- Not conformance, certification, adoption or IETF endorsement.
- Not WEXP independent verification from an EMILIA role label.
- Not that any EP receipt or mapped appraisal grants reusable permission, local
  authorization, Gate admission, delegated authority, or approval for a future
  action.
- Not a generic Bridge Framework.
- Nothing beyond the frozen authorities, bridge, cases and verdict rules.

No claim above the **observation** base is supported on any case. §13
no-generalization governs; nothing here is promoted to a generic interop core.

## Procedure integrity

- Every frozen identity was re-measured by digest immediately **before** and
  **after** execution: 18 frozen path+digest pairs, **0 mismatches**.
- B-01 was verified against its prior commitment before admission
  (`COMMITMENT_MATCH`, 7276 bytes) and its earlier `NOT_RECEIVED` state is
  preserved in history rather than erased.
- Both expectations are byte-identical to their sealing commits. Neither was
  edited to agree with the other or with the result.
- The six open cases reproduced their pre-execution results exactly — the
  regression control on the execution driver itself.
- Two comparison-script errors were made and corrected **in the checker**, never
  in a frozen artifact or a result, and both are recorded in the execution record.
