# WEXP × EMILIA P/P-1 comparison 001

Status: **COMPLETE FOR FINAL-CANDIDATE REVIEW — BRANCH A**  
Mode: frozen-reading and receipt comparison; no WEXP implementation execution.

## Source identities

| Source | Exact identity |
| --- | --- |
| Pair archive | SHA-256 `ae237263c86ee0b5c2b6387159d81957efe47e20161b74dd363da5a530705282` |
| P | SHA-256 `b552da51858d0256a562e800a81a870435d6e136c9bc28833b962b6d3723fb3e` |
| P-1 | SHA-256 `67556d28d272b4b01a73e1c1465248644dd7a05460fc149aa77df92cf36403a0` |
| Frozen WEXP expectation | SHA-256 `42eeecaba33238d8c94bbb9d5bb22ab46721de6de74cff455b8115c17892088a` |
| Frozen EMILIA expectation | 885 bytes; SHA-256 `6e0dc6c87f853cacdeeb676b27690e54bdb8a7a7aa86611c5ffe233387e256a4` |
| EMILIA execution receipt | 1,963 bytes; SHA-256 `2d61071712ef4424d1b308afb6a3b8752b4effcf2525c0c08c97cff16617b77f` |
| EMILIA baseline | `emiliaprotocol/emilia-protocol@9a04bea7fe680345132f6f6251fdb9a63fd8aeb2` |
| WEXP baseline | `WEXP-dev/wexp-spec@b28a46e7764c2ef14decc35394f21278fca9c988` plus the frozen public surfaces named by the WEXP derivation |

The expectation and receipt hashes, precedence, receipt linkage, public EMILIA
baseline artifacts, and expectation reproduction are recorded in
`records/EMILIA-EXPECTATION-EXECUTION-VERIFICATION-001.md`.

## Controlled fixture fact

P-1 differs semantically from P only by removal of the meter observation's
`action_caid`. Its meter signature changes only as the cryptographic derivative
needed to keep that modified observation valid. Restoring the removed member
and P's meter signature reproduces P's exact bytes.

This fact establishes a controlled correlation ablation. It does not by itself
assign the relation a WEXP semantic role.

## Case comparison

### P

| Plane | Frozen or observed result |
| --- | --- |
| Fixture facts | Authenticated controller and independently keyed meter observations are present; the meter observation contains the exact `action_caid` relation fixed by the pair. |
| EMILIA expectation | `valid: true`; `lifecycle_state: reconciled`; `outcome: in_bounds`; `errors: []`. |
| EMILIA actual | Exact reproduction of the expectation; result class `EXPECTED RESULT REPRODUCED`; receipt result digest field `sha256:4ea90a5cf398ad77fe21bd5933ae85c2970cb55d1b5cd929c0f097bb9efc50b3`. |
| WEXP expectation | Determination `UNDERDETERMINED`; asserted claim, verdict, boundary, ceiling, and grounding `UNDETERMINED`. |
| WEXP implementation | Not invoked. Input is `NOT CONSTRUCTIBLE UNDER FROZEN PUBLIC MAPPING SURFACE`. |
| CAID/action correlation | The signed meter observation contains the fixture's `action_caid` relation. This is correlation within the fixture, not automatically WEXP semantic support. |
| Primary relation | **COMPATIBLE / DIFFERENT SEMANTIC SURFACE**. |

Why: EMILIA supplies a determinate lifecycle/outcome result under its frozen
semantics. WEXP cannot construct a determinate Core appraisal from the same
fixture without a public EP→WEXP mapping. The results do not contradict one
another, and the EMILIA label is not converted into a WEXP verdict.

### P-1

| Plane | Frozen or observed result |
| --- | --- |
| Fixture facts | The meter observation lacks `action_caid`; the derivative meter signature preserves cryptographic validity; all other frozen semantic facts remain unchanged. |
| EMILIA expectation | `valid: false`; `lifecycle_state: indeterminate`; `outcome: null`; required error `outcome_observations_not_exactly_bound`. |
| EMILIA actual | Exact reproduction of the expectation; result class `EXPECTED RESULT REPRODUCED`; receipt result digest field `sha256:7bfe5b1ba465546787d0ed31fa7aabd00ddd30b755b1c028230a5796d0160aca`. |
| WEXP expectation | Determination `UNDERDETERMINED`; asserted claim, verdict, boundary, ceiling, and grounding `UNDETERMINED`. |
| WEXP implementation | Not invoked. Input is `NOT CONSTRUCTIBLE UNDER FROZEN PUBLIC MAPPING SURFACE`. |
| CAID/action correlation | The meter observation's `action_caid` relation is absent. Absence removes a possible profile premise but does not select a WEXP finding or verdict. |
| Primary relation | **COMPATIBLE / DIFFERENT SEMANTIC SURFACE**. |

Why: EMILIA supplies the determinate lifecycle state `indeterminate` and its
named exact-binding refusal. The frozen WEXP surface supplies no rule for the
semantic disposition of missing meter `action_caid`, so WEXP remains
underdetermined. This difference of surface is not a semantic disagreement.

## Shared checks

For the receipt as a whole, `predictions_valid`, `observations_verified`,
`required_sources_present`, `source_independence`, `source_requirements`, and
`observation_windows` are all `true`. Those checks do not erase P-1's
`outcome_observations_not_exactly_bound` refusal and do not establish physical
truth, WEXP independent verification, or WEXP semantic support.

## Pair-level finding

EMILIA distinguishes P from P-1 under its independently frozen expectation and
the linked execution receipt:

- P reproduces `reconciled / in_bounds`;
- P-1 reproduces `indeterminate / null` with
  `outcome_observations_not_exactly_bound`.

WEXP does not produce a determinate appraisal or classify the semantic effect
of the ablation because no frozen public bridge/profile constructs a complete
Core `AppraisalInput` or assigns the changed relation a WEXP role. Both frozen
WEXP determinations remain `UNDERDETERMINED`.

This is **not a genuine semantic disagreement**. It is a bounded distinction on
the EMILIA surface paired with a WEXP composition boundary.

- Genuine semantic disagreement: **NO**.
- Material overclaim: **NO**.

## Claim-boundary test

### What EMILIA establishes

For these exact bytes and the pinned EMILIA baseline, the receipt reproduces
the independently frozen P and P-1 lifecycle/outcome expectations and the
named P-1 refusal.

### What WEXP establishes

For both fixtures, the frozen WEXP reading is `UNDERDETERMINED`. No complete
Core `AppraisalInput` is constructible under the frozen public mapping surface,
and no WEXP implementation was invoked.

### What correlation establishes

P contains and P-1 omits the exact meter-observation-to-action `action_caid`
relation while cryptographic validity is preserved. Correlation alone is not
WEXP semantic support.

### What remains unknown

No determinate WEXP appraisal, target binding, boundary, ceiling, grounding,
IV predicate, effect-to-execution predicate, or missing-`action_caid`
disposition is supplied by the frozen public WEXP surface. Physical truth and
general behavior outside this pair are not established.

### Stronger-than-evidence claim

Neither frozen reading nor the retained receipt is strengthened in this
comparison. **Material overclaim: NO.**

## Terminal branch

**SELECTED: BRANCH A — EXPLICIT BRIDGE REQUIRED.**

Branch A is selected because the EMILIA expectation was independently frozen,
both EMILIA results reproduce it, the exact controlled ablation produces the
frozen distinction, WEXP remains underdetermined/non-constructible, and no
bridging rule was inserted.

- Branch B — bounded composition demonstrated: **NOT SELECTED**. No determinate
  WEXP appraisal is constructible without a new mapping rule.
- Branch C — expectation/implementation disagreement: **NOT SELECTED**. Both
  applicable EMILIA results reproduced their own frozen expectations.

No sixth fixture is required. The existing pair classifies the question.
