# Bounded AAC completeness: preparation for discussion

**Status: WEXP-side proposal; no jointly agreed AAC profile or AAC interop run.**
This page is separate from the collection's completed experimental records.

## The small contribution

[Proposed clarification and two examples](aac-clarification-and-examples.md)
address the distinction between consistency with a declared population and
verification against a checkpoint chosen before the response. The
[additive upstream patch](aac-examples.patch) adds one informative companion
file under `spec/`; it changes no executable AAC behavior. It is prepared
against AAC commit `1d1752bf3956a9800d66b13f129d419d7252fa6d`.

The [reviewed AAC Section 6.7](https://github.com/action-state-group/agent-action-capsule/blob/1d1752bf3956a9800d66b13f129d419d7252fa6d/spec/interop-profile-v0.md#67-coverage-declaration)
already separates declared kinds, per-property checks and completeness-dependent
requirements. `coverage_declaration_commitment` remains `NOT_CHECKED`. The
examples preserve that result and the native Evidence Result semantics.

The informative contribution is now proposed in [AAC PR #429](https://github.com/action-state-group/agent-action-capsule/pull/429),
opened on 28 October 2026 at head `c4d6179290d98530d6c139f5089a694435416b12`.
It adds one companion document; it is not an accepted verification method or an
executed AAC experiment. The frozen patch and reviewed source snapshot above
remain unchanged. Consult the upstream PR for its current review/merge status;
publication of a proposal does not establish joint agreement.

## First experiment to agree

One stream; `all_records`; from the stream's beginning to a receiver-selected
checkpoint; full bounded disclosure. The checkpoint must bind the exact stream
population, count and ordered occurrences. The central negative control omits
R3 **and** reduces the declared count while keeping that checkpoint unchanged.
A smaller response that is self-consistent must not acquire a positive
checkpoint-relative completeness result.

Secondary controls: substituted checkpoint, wrong stream, wrong position,
repeated or extra occurrence, unsupported material, missing material, and
resource-limit handling. An unavailable check is not evidence of a missing
real-world action. Full disclosure is not proof of fullness without the
commitment binding. The byte contract and implementation roles remain to be
agreed; no new cryptographic primitive is proposed here.

## Available WEXP materials

| Material | Public pinned entry | Established scope |
|---|---|---|
| Appraisal Core-02 | [Published specification](https://datatracker.ietf.org/doc/draft-sergeev-wexp-core/02/) | Carrier-neutral normalized-input appraisal contract |
| Core-02 corpus | [89 full cases, package revision 2](https://github.com/WEXP-dev/wexp-vectors/tree/a9e5cd5ad6083aff893d9303b9b6503a7f2e02f7/vectors/WEXP-CORE-02-VECTORS-001) | Frozen expectations, not a conformance suite |
| Core-02 appraiser | [Version-scoped implementation](https://github.com/WEXP-dev/wexp-ref/tree/56289024c9ee748111f1f1d4f42728ffe04d8d69) | Bounded same-project qualification, not an AAC mapper |
| Coverage-00 | [Published specification](https://datatracker.ietf.org/doc/draft-sergeev-wexp-coverage/00/) | Separate population and correspondence contract |
| Coverage model | [Finite-predicate package](https://github.com/WEXP-dev/wexp-vectors/tree/a9e5cd5ad6083aff893d9303b9b6503a7f2e02f7/vectors/WEXP-COVERAGE-00-LOGIC-001) | Test-world populations; not a full evaluator or PostgreSQL validation |

The appraiser's corpus lock intentionally stays on `d6827a5e08fdf0aabecee5c025c369273c438db5`;
adding Coverage to the vectors repository did not change those Core bytes.
See [source pins](sources.lock.json). These pins are a review inventory, not
proof that an AAC-to-WEXP binding has been implemented.

## Separate questions and outputs

First establish native AAC bounded completeness. A later Coverage mapping must
name exact populations and relations; `stream_interval` does not automatically
map to a Coverage claim. A Core mapping instead concerns exact claims about
particular actions: interval completeness is not a Core content base.

Retain native verification findings, evidence sufficiency, the native contract
verdict, exact claim support and the recipient's reliance decision as distinct
comparison dimensions. These are not five new fields imposed on either format.
Both comparison routes must receive the same evidence and trust context. Shared
code, control and known expectations are disclosed, not called independence.

A possible later research question is appraisal reproducibility under selective
disclosure, distinct from policy-authorized reliance on someone else's result.
It does not enlarge the first experiment or imply established scientific novelty.
