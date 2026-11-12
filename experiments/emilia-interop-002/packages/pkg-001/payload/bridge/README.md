# INTEROP-002 bridge candidate

Status: **CANDIDATE / OPEN-CASE VALIDATED / BLIND CASE PENDING / NOT EXECUTED / NOT PUBLISHED**

Authored after the effective Design Freeze
(`WEXP-EMILIA-INTEROP-002-DESIGN-FREEZE-001`, sha256 `cd16600c…685f`), against
frozen authorities only. This is an **experiment-specific** bridge, not a
generic Bridge Framework, and §13 still prohibits promoting anything here.

## What is here

| File | What it is |
| --- | --- |
| `BRIDGE-CANDIDATE.yaml` | The bridge. 17 elements, all 18 mapping requirements classified, all 16 predicate classes defined. |
| `bridge_lib.py` | The executable form of exactly those elements. Changes zero bytes of `interop_core/`. |
| `run_open_cases.py` | Runs the frozen open cases and regenerates both records below. |
| `BRIDGE-VALIDATION-RECORD-001.json` | Element inventory, coverage, per-case results, invariant verdicts, H-SUFF and H-MIN status. |
| `ABLATION-PLAN-001.json` | The frozen single-element H-MIN plan and its executed result. |
| `tests/` | 46 bridge tests. |

## Element identifiers

Bridge elements are `BE-01 … BE-17`. They are deliberately **not** `B-01 …`,
because `B-01` in this experiment is the independently committed blind hostile
case. A shared namespace would make every later sentence ambiguous exactly where
ambiguity costs most. Representation only; no frozen semantics changed.

## The claim, and where it stops

CC-1 is `(observation, {IV})`. `ceiling_base` is `observation` on every case that
constructs, and it is fixed there by **M-09 being non-constructible**: this
bridge defines no effect-to-execution predicate, so no higher base can be
reached from this evidence. That is a real experimental output, not a gap to be
filled later under the same freeze.

Two of eighteen mapping requirements are `FAIL_CLOSED_NON_CONSTRUCTIBLE`:

- **M-05, CAID issuer scope.** Nothing in the frozen evidence says which issuer
  scope makes the CAID usable. The bridge therefore uses CAIDs for *equality*
  only, never as authority, and carries `caid_issuer_scope_not_evidenced` as a
  limitation on every finding.
- **M-09, effect-to-execution.** Not defined. See above.

## Open-case results

| Case | Outcome | CC-1 | Attacked invariants preserved |
| --- | --- | --- | --- |
| C-00 | `CONSTRUCTED_CLAIM_SUPPORTED` | supported | positive control |
| H-01-a | `INDETERMINATE` | refused | I-01, I-03a |
| H-01-b | `INDETERMINATE` | refused | I-01, I-03a |
| H-01-c | `INDETERMINATE` | refused | I-03b |
| H-02 | `INDETERMINATE` | refused | I-02, I-04 |
| H-03 | `CONSTRUCTED_CLAIM_SUPPORTED` | supported | I-04, I-05 |

H-01-b fails on **instance binding with its signatures intact**, and H-01-c
fails on **evaluation context with its causal binding intact**. That separation
is what makes I-03a and I-03b independently scored rather than jointly asserted.

H-03's `emilia_input` is byte-identical to C-00, so the same evidence supports
the same claim; the hostility is entirely in what is attached, and all seven
attached items — two expansions, five authority conversions — are refused.

**One divergence is recorded and not resolved locally.** H-03 states that
independent verification is unsupported because a role label is not independent
verification. The bridge agrees about role labels and does not use one; its IV
finding rests on BE-10's declared predicate instead. Whether that predicate *is*
WEXP independent verification is the question CC-1 exists to probe, so it goes
to EMILIA-side fairness review rather than being settled here. It does not
affect the H-03 verdict, which turns on refusal.

## H-MIN: 14 of 17, honestly

Single-element ablation means **the element is absent**, not that the bridge
notices a missing part and fails closed. A bridge that fails closed on its own
missing parts makes every element look necessary and measures the harness.

Three elements are `NOT_ESTABLISHED` by the frozen open set:

- **BE-04 and BE-06** mask each other. H-01-b mutates three fields at once;
  BE-04 catches two, BE-06 catches the third, so removing either alone still
  refuses the case. Removing *both* does break I-01 and I-03a — recorded as a
  diagnostic only, since DRAFT-004 admits single-element ablation and disclaims
  multi-element conclusions.
- **BE-03** checks source-pin currency, and no frozen open case carries a stale,
  compromised or expired pin. It stays, because EMILIA §§4 and 6 require
  refusing such sources. Deleting a normatively required check to improve a
  minimality score would be trading correctness for a number.

Global minimality, multi-element minimality, uniqueness and a generic minimal
mapping are **not** claimed.

## Not done here

No B-01 reveal or inference. No Execution Freeze. No execution. No publication.
No `interop_core/` change. No generic promotion.

## Reproducing

```
cd experiments/WEXP-EMILIA-INTEROP-002/bridge
PYTHONPATH=. python -m pytest tests
PYTHONPATH=. python run_open_cases.py
```

Requires `cryptography` and `pyyaml`. Signature verification is real: the EP
signing preimage is the literal domain string `EP-OUTCOME-OBSERVATION-v1`
followed by a zero octet, then canonical JSON of the observation with `proof`
removed. That construction was confirmed against the frozen C-00 signatures
before any case was scored.
