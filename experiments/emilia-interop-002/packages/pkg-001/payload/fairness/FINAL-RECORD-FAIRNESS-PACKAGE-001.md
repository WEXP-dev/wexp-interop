# WEXP × EMILIA INTEROP-002 — final-record fairness review

**For:** Iman Schrock, EMILIA-side contributor
**From:** the WEXP side, via the Founder
**Status:** PREPARED — NOT SENT. No publication authorized.
**Charter basis:** DRAFT-004 §16, contribution 3 — *"verify the exact final record
and whether it represents the native EMILIA result fairly."*

---

## What this is, and what it is not

This is a **fairness and factual review**. You are being asked whether the record
is accurate and fair, not whether you approve of the outcome.

- It is **not** permission to rewrite results, and I will not rewrite them to
  accommodate a disagreement.
- **Disagreement is allowed and will be recorded** — including disagreement that
  makes the WEXP side look worse. If you hold that something here misreads
  EMILIA, that becomes a recorded finding about the bridge or the record, and
  the frozen result stands as measured.
- **No publication has been authorized.** Nothing here is public and nothing
  goes public without a separate decision that requires your review first.
- **No new execution is requested** of you.
- **No repair of the experiment is requested**, and none is being offered.

Everything below was produced under a frozen procedure. The freezes, the bridge,
the case bytes and both precommitted expectations are unchanged and were
re-verified by digest immediately before and immediately after execution.

---

## 1. The execution result, exactly as measured

**B-01 — your blind case**

| | |
|---|---|
| typed outcome | `INDETERMINATE` |
| CC-1 supported | `false` |
| ceiling base | `null` |
| IV | `not-evaluated` |
| rejection reason set | `{exact_binding_mismatch:operation_id}` — exactly one reason |
| I-01 | **PRESERVED** |
| I-03a | **PRESERVED** |

**The WEXP precommitted expectation: 23 of 23 fields reproduced, 0 differences.**
It was written from the frozen design while reading your revealed bytes, before
the bridge was ever run against them, and it was not edited afterwards.

**H-MIN: 15 of 17 elements SUPPORTED.** `BE-03` and `BE-06` remain
NOT_ESTABLISHED and were **not** deleted to improve the number.

**BE-04 necessity on B-01: SUPPORTED.** This is the sharpest result of the run,
and it is yours. Remove BE-04 alone and B-01 flips from `INDETERMINATE` to
`CONSTRUCTED_CLAIM_SUPPORTED` — a supported claim about
`operation:plant-7:002` carried by evidence attesting `operation:plant-7:001`.
Nothing else in the bridge refuses it, because you left the action digest and
the CAID matching. The six open cases could not show this: H-01-b rebinds three
fields at once, so BE-06 alone still catches it. Your case rebinds the operation
identifier only. It tested something the open set structurally could not.

---

## 2. Two findings we are explicitly not resolving without you

### F-01 — the EMILIA native output

The execution record stated: *"No EMILIA native output exists in this contour,
for any case."* **That wording was overstated, and I am correcting it before you
review rather than letting you find it.**

Searching afterwards, I found that the INTEROP-001 final-candidate package
(191735 b, `973d671d…`, digest verified) contains real EMILIA native outputs
produced by your verifier — `packages/verify/src/outcome-binding.ts` at commit
`9a04bea7`, the same commit every INTEROP-002 fixture pins:

| INTEROP-001 fixture | is byte-identical to | EMILIA native `actual` |
|---|---|---|
| `WE-EP-P` | INTEROP-002 **C-00** (`b552da51…`, 7255 b) | valid `true`, `reconciled`, `in_bounds`, no errors |
| `WE-EP-P-1` | INTEROP-002 **H-01-a** (`67556d28…`, 7152 b) | valid `false`, `indeterminate`, outcome `null`, `outcome_observations_not_exactly_bound` |

So the corrected finding is narrower and still real: **no EMILIA native output
exists for H-01-b, H-01-c, H-02, H-03 or B-01**, and no frozen INTEROP-002
procedure defines how to produce one. That matters because the charter
presupposes one — §10 step 5 says *"preserve each system's native output before
comparison"*, §11.1 describes the boundary such an output would cross, and §16
asks you to verify the record against *"the native EMILIA result"* — yet §16
never asks you to produce one, and no procedure produces one for these cases.

**B-01 has no EMILIA native output and no defined way to obtain one.**

### F-02 — how H-SUFF should be read

The frozen policy makes bridge sufficiency conditional on *"every precommitted
expectation relevant to the conclusion reproduced."* That admits two readings:

- **Narrow** — sufficiency is a property of the WEXP bridge, so only the WEXP
  expectation is relevant. It reproduced 23/23. → **H-SUFF SUPPORTED**
- **Broad** — in a two-party experiment both expectations are relevant. Yours
  cannot be verified without an EMILIA native output for B-01. → **H-SUFF
  INCONCLUSIVE**

The record applies the narrow reading and says so in the open. I am not settling
this by picking the reading that yields the better verdict.

---

## 3. What I am asking you to review

**A.** Does the final record fairly represent your precommitted EMILIA
expectation? Your five fields are recorded verbatim as
`valid: false`, `lifecycle_state: indeterminate`, `outcome: null`,
`failed_check: exact_bindings`, `error: outcome_observations_not_exactly_bound`,
with the record stating plainly that they are **neither confirmed nor
contradicted**, because verifying them needs an EMILIA native output for B-01.

**B.** Is the corrected statement in F-01 accurate — that no EMILIA native
output exists in this contour for H-01-b, H-01-c, H-02, H-03 or B-01?

**C.** Is there an **already-defined, already-frozen** EMILIA-side native-output
procedure or artifact that the execution record overlooked?

> If yes, please **identify the pre-existing frozen authority or process only** —
> its name, location and digest. Do **not** run or generate anything on our
> account, and nothing will be generated or run on this side under this order.
> If no, the absence is recorded as a genuine experiment-design finding: the
> charter presupposed a native output it never arranged to obtain.

**D.** Does the final record fairly characterize the **H-03 IV-semantics
divergence**? In short: your fixture's stated ground is that a source labelled
`independent_observer` is a role label in the registry, not an independent
verification of the WEXP claim. The bridge agrees a role label cannot establish
IV and does not use one; its IV finding rests instead on BE-10's four-part
predicate — a relying-party-supplied requirement the presenter may not widen or
select, a met quorum, canonical DER key distinctness, and declared
control-domain distinctness, with every contributing observation independently
accepted. **This was recorded as NOT RESOLVED and neither the fixture nor the
predicate was altered.** H-03's I-04 and I-05 verdicts rest on refusal of
expansion and of authority conversion and do not depend on this question. If you
hold that BE-10 misreads EMILIA's independence semantics, that is recorded as a
finding about the bridge and the frozen result is not rewritten.

**E.** Does the final record characterize F-02 fairly **without overstating
bilateral interoperability**? Specifically: is it fair to report H-SUFF
SUPPORTED under the narrow reading, given that it is a claim about one bridge on
one frozen case set and not a claim that WEXP and EMILIA interoperate?

---

## DISCLOSURE — not a review question

One factual observation, disclosed because you would notice it and because
withholding it would be the wrong way to run this.

The four fields of your precommitted B-01 expectation are field-for-field the
frozen INTEROP-001 native result for `WE-EP-P-1`. **No conclusion is drawn from
this.** If your expectation was grounded in your own system's recorded behaviour
on a structurally similar rebinding case, that is a strength of the expectation,
not a defect. You are better placed to characterize it than I am; respond only
if you wish to.

---

## 4. What the record does not claim

- Not that WEXP proves execution.
- Not that EMILIA is certified, validated or correct.
- Not that the two specifications interoperate in general.
- Not that this bridge generalizes — §13 no-generalization governs.
- Not that the bridge is minimal. **H-MIN is NOT_ESTABLISHED.**
- No claim above the observation base is supported on any case.

H-SUFF SUPPORTED is a statement about **this bridge, on these seven frozen
cases**, and nothing wider.

---

## 5. Where the record is

All artifacts are in the private repository, unchanged since execution:

```
experiments/WEXP-EMILIA-INTEROP-002/
  execution/EXECUTION-RECORD-001.json          the final record
  execution/native/                            preserved native outputs, per case
  fairness/FINDINGS-STATUS-001.json            F-01 corrected additively, F-02 preserved
  fairness/EMILIA-NATIVE-OUTPUT-SEARCH-001.json  the search behind F-01, auditable
```

The execution record is preserved **byte-identical** and was not edited to
absorb the F-01 correction. A finding that turns out to be overstated is
corrected by a successor record, never by quietly rewriting the original.

**No publication is authorized. Your review is a precondition of the publication
gate, not a formality after it.**
