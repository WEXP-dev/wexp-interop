# WEXP × EMILIA claim ledger 001

Status: **COMPLETE FOR FINAL-CANDIDATE REVIEW — BRANCH A**

This ledger separates established evidence from prohibited inferences. Only
numbered rows are included in the category counts. EMILIA lifecycle/outcome,
WEXP appraisal, and CAID/action correlation remain distinct planes.

## A. Established — 19 claims

| ID | Established claim | Evidence boundary |
| --- | --- | --- |
| AE-01 | Both original five-case reading commitments were in place before the first reading reveal. | Commitment/reveal record; this is ordering evidence, not semantic agreement. |
| AE-02 | Both original five-case reveals matched their commitments. | WEXP SHA-256 `a185e6760de149375e657b1429adc1ea329ed9f9705b9d1c2b505dcc8e3ea984`; EMILIA SHA-256 `b43f8ac6dce465258c75a42117d2750a6bafa163846251416e87cec371a4bad6`. |
| AE-03 | The two five-case readings address the same byte-identical common fixture and the same ordered IDs `WE-EP-001` through `WE-EP-005`. | `fixtures.yaml` SHA-256 `d972dbb549aaaa25e92c32a936acba4d9a686e9ca62fe6bd556b12be2962cfcc`. |
| AE-04 | The five-case comparison found no genuine semantic disagreement. | Frozen comparison SHA-256 `272a9b08a213702ee2156438b7736b954c7a32bc4a190cce92d3d82226266934`; this does not establish equivalence. |
| AE-05 | `WE-EP-001` through `WE-EP-004` were underdetermined on both sides. | Four primary relations: `UNDERDETERMINED ON BOTH SIDES`. |
| AE-06 | For `WE-EP-005`, EMILIA determined lifecycle `INDETERMINATE` while WEXP remained underdetermined. | Primary relation: `UNDERDETERMINED ON WEXP SIDE ONLY`; compatible uncertainty preservation at different abstractions, not verdict equivalence. |
| AE-07 | Exact P and P-1 bytes are frozen. | P SHA-256 `b552da51858d0256a562e800a81a870435d6e136c9bc28833b962b6d3723fb3e`; P-1 SHA-256 `67556d28d272b4b01a73e1c1465248644dd7a05460fc149aa77df92cf36403a0`. |
| AE-08 | The WEXP P/P-1 expectation was frozen before WEXP implementation execution. | Frozen expectation time `2026-08-21T00:32:35Z`; no reference or independent WEXP engine was run before or after the freeze in this experiment. |
| AE-09 | No frozen public EP→WEXP profile constructs the complete Core `AppraisalInput` for P or P-1. | Frozen WEXP derivation and expectation; no profile was invented during the experiment. |
| AE-10 | An explicit bridging rule is required for a determinate WEXP composition experiment over this pair. | Frozen finding `MISSING-BRIDGE-EP-WEXP-PAIR-001`; this is a profile requirement, not a completed or current normative profile. |
| AE-11 | The exact independent EMILIA expectation freeze is established. | `emilia-expectation.freeze.json`, 885 bytes, SHA-256 `6e0dc6c87f853cacdeeb676b27690e54bdb8a7a7aa86611c5ffe233387e256a4`; artifact `WEXP-EMILIA-PAIR-FREEZE-001`; baseline `9a04bea7fe680345132f6f6251fdb9a63fd8aeb2`. |
| AE-12 | Freeze ordering is established: P/P-1 preceded both expectations, WEXP was frozen before WEXP execution, and EMILIA was frozen before EMILIA execution. | Pair creation `2026-08-21T00:31:23Z`; WEXP freeze `2026-08-21T00:32:35Z`; pair send `2026-08-21T00:58:41Z`; EMILIA source declares `fixed_before_emilia_execution`; receipt links its exact hash and records execution at `2026-08-21T02:41:04Z`. |
| AE-13 | EMILIA's frozen expectation for P is `valid: true`, lifecycle `reconciled`, outcome `in_bounds`, with `errors: []`. | Exact EMILIA expectation bytes; this is an EMILIA expectation only. |
| AE-14 | EMILIA's frozen expectation for P-1 is `valid: false`, lifecycle `indeterminate`, outcome `null`, requiring `outcome_observations_not_exactly_bound`. | Exact EMILIA expectation bytes; this is an EMILIA expectation only. |
| AE-15 | The EMILIA execution receipt reproduces the frozen P expectation exactly. | Receipt SHA-256 `2d61071712ef4424d1b308afb6a3b8752b4effcf2525c0c08c97cff16617b77f`; result digest field `sha256:4ea90a5cf398ad77fe21bd5933ae85c2970cb55d1b5cd929c0f097bb9efc50b3`; class `EXPECTED RESULT REPRODUCED`. |
| AE-16 | The EMILIA execution receipt reproduces the frozen P-1 expectation exactly. | Same receipt; result digest field `sha256:7bfe5b1ba465546787d0ed31fa7aabd00ddd30b755b1c028230a5796d0160aca`; class `EXPECTED RESULT REPRODUCED`. |
| AE-17 | The exact hostile ablation changes the disclosed EMILIA result: P is `reconciled/in_bounds`, while P-1 is `indeterminate/null`. | Exact pair delta plus independently frozen expectation and linked execution receipt; this finding is bounded to this pair. |
| AE-18 | The named P-1 refusal is `outcome_observations_not_exactly_bound`. | It is required by the frozen expectation and reproduced in the receipt's P-1 `errors` array. |
| AE-19 | All six shared receipt checks are `true`: `predictions_valid`, `observations_verified`, `required_sources_present`, `source_independence`, `source_requirements`, and `observation_windows`. | Exact receipt fields; these checks do not establish physical truth or WEXP semantic support. |

## B. Resolved evidence dependencies

The prior expectation-dependent and execution-dependent questions are resolved
by the exact EMILIA freeze and linked receipt. No WEXP implementation was run:
its operational classification is `IMPLEMENTATION INPUT NOT CONSTRUCTIBLE`
under the frozen public mapping surface, not failure or unavailability.

The receipt is the retained execution evidence. This ledger does not claim that
separate raw stdout or stderr streams exist, and the recorded result-digest
strings are not described as independently recomputed without a declared
serialization rule.

## C. Prohibited / not established — 11 claims

| ID | Prohibited or unestablished claim | Why it is not warranted |
| --- | --- | --- |
| PR-01 | WEXP and EMILIA are semantically equivalent. | They operate at distinct abstraction planes and no equivalence proof exists. |
| PR-02 | WEXP validates EMILIA. | WEXP appraisal is not an EMILIA validation authority. |
| PR-03 | EMILIA proves WEXP execution. | An EMILIA lifecycle outcome is not a WEXP content-base finding or verdict. |
| PR-04 | CAID equality is WEXP semantic support. | Correlation is separate from semantic support absent a frozen mapping rule and separate semantic validation. |
| PR-05 | WEXP and EMILIA fully interoperate. | One bounded pair and a non-constructible WEXP input do not establish full interoperability. |
| PR-06 | Either system is fully conformant. | No conformance determination is authorized or supported. |
| PR-07 | The experiment is a conformance suite. | The fixtures and records are a bounded interop experiment, not a released conformance corpus. |
| PR-08 | A standards body adopted the mapping. | No adoption, submission, or normative profile publication occurred. |
| PR-09 | A positive WEXP appraisal or positive WEXP composition was demonstrated. | No determinate public EP→WEXP composition is constructible; no WEXP implementation was invoked. |
| PR-10 | EMILIA verifies physical truth. | The receipt reports an EMILIA verifier result over supplied evidence; it does not prove physical truth. |
| PR-11 | The missing bridge is normative WEXP today. | The experiment identifies a missing composition contract; it neither creates nor adopts one as WEXP authority. |

## Count summary

- Established: **19**.
- Prohibited / not established: **11**.

Branch A follows from the established evidence and does not move any prohibited
claim into the established category.

