# WIMSE AAR-02 INTEROP-001 — public replay result

The frozen public composition completed its local replay on **11 October
2026**: **130/130 pipeline cases passed, all 16 output mutations were rejected,
and both controlled trusted-producer worlds behaved as prospectively fixed**.
The WEXP recipient and strong native baseline made the same local decisions.
The complete semantic result also matched the known private reference in JSON
types, values and serialized bytes. These are two different comparisons.

This is a bounded, publisher-coordinated execution with a separately staged
recipient implementation. It is not a blind trial, an external-team
reproduction, general AAR interoperability or full Core conformance.

## Commitment and actual execution

| Item | Exact identity or observation |
|---|---|
| Public preparation commit | `70b4491a1ec8aab5af61f31510220067e3e5cfba` |
| Preparation tree | `feaec7ce219ba8aea944d3a8e8fcf0079f6932b9` |
| Public commit time | 2026-10-11 02:50:58 UTC |
| Driver start, written before runner invocation | 2026-10-11 02:53:02.228134 UTC |
| Retained runner observation | 02:53:02.278896–02:53:18.157024 UTC |
| Driver finish after strict comparison | 2026-10-11 02:53:18.208784 UTC |
| Python | CPython 3.12.14 |
| Runner and strict comparator exit codes | 0 and 0 |
| Fresh public clone after execution | Clean |
| Semantic SHA-256 | `1a97015e506db61bbf481cfac3ff3c2e53186cb935b491cb190bc370a1c62ef2` |

The public [preparation commit](https://github.com/WEXP-dev/wexp-interop/commit/70b4491a1ec8aab5af61f31510220067e3e5cfba)
preceded this execution. The exact inputs and expectations were checked in an
ordinary fresh clone before the retained runner was invoked. The
[start observation](../run-evidence/public-run-001/EXECUTION-START.json),
[finish observation](../run-evidence/public-run-001/EXECUTION-FINISH.json),
[runner observation](../results/public-run-001/execution-observation.json) and
[strict comparison](../results/public-run-001/reference-comparison.json)
retain the identities, runtime, commands and outcomes. The journal retains
the top-level verifier, runner and comparator stdout, stderr and exit codes.
Per-participant measurements retain stdout hashes, stderr, elapsed time and
return codes alongside the structured results; they are not full raw
subprocess stdout transcripts. Local clocks and logs are not independent
timestamp attestations or external authentication of execution.

## What was exercised

| Procedure | Recorded outcome |
|---|---|
| Published AAR-01 records | 47 cases; declared native expectations satisfied |
| Published AAR-02 records | 55 cases; declared native expectations satisfied |
| Local signed extensions | 19 cases; declared expectations satisfied |
| Cross-revision compatibility | 6 cases; intended validation/dispatch results |
| Missing, unknown or incorrectly bound revision selection | 3 cases; refused |
| Additional WEXP output mutations | 16/16 rejected and quarantined |
| Controlled trusted-producer worlds | 2/2; record-only decisions, differing oracle endpoints |

The **102 published records are included in the 130 pipeline cases**. The
separate corpus probe repeats the same native readers; its 102 records are not
an additional independent sample. The two worlds repeat a retained local
input with different harness operations. The 16 mutations test the additional
output contract and are counted separately. Exact case identities and
prospective requirements are in [EXPECTATIONS.json](../pre-run/EXPECTATIONS.json).
The 130 producer-native outcomes comprise 39 `valid`, 88 `malformed` and three
`not-run` dispatch refusals. Passing means matching the declared outcome;
it does not mean every input was valid.

## A2 and A10: equal deny labels, different evaluations

| Recipient field | A2 | A10 |
|---|---|---|
| Source `decision.reported` | `deny` | `deny` |
| Evaluation status | `evaluated` | `not-evaluated` |
| Local classification | `reported-evaluated-deny` | `reported-not-evaluated-deny` |
| Unavailable input | `[]` | `["standing-source"]` |
| Admission | `record-only` | `record-only` |
| Execution / authorization / human participation established | All false | All false |

Both source records were native-valid. Both paths retained the evaluation
distinction and A10's unavailable input. The mapper successfully evaluated
the supplied record while that record reported an evaluation it could not
complete; these are different evaluations. See [distinction checks](../results/public-run-001/distinction-checks.json)
and [full AAR-02 results](../results/public-run-001/aar02-results.json).

## Revision mismatch and EV3

The exact historical AAR-01 A1 envelope is the AAR-02 EV3 envelope. The old
revision's reader accepts it; the selected new reader returns `malformed`
with `member-missing`. The producer emits a mapping failure, no normalized
Core input or appraisal is fabricated, and the recipient quarantines the
invalid source. Its `output_validation: accepted` means that the **failure
output accurately represented the source failure**, not that EV3 became a
valid AAR-02 record.

The old reader also parses the tested newer envelopes, but the closed old
profile refuses their revision-02 members. Missing or unknown revision pins
and an incorrect specification digest are refused before native processing.
This demonstrates why the unchanged predicate URI is insufficient for
version selection. The detailed [compatibility results](../results/public-run-001/compatibility-results.json)
preserve every native verdict, dispatch code and recipient decision.

## Oversight and evidence classes

A11 and local oversight cases carried the declared act/digest without
establishing human participation or authority. An unresolved digest stayed
unresolved; absence of oversight did not establish absence of human activity.
Attempts to upgrade human participation or authority in the WEXP output were
rejected. See [local results](../results/public-run-001/local-results.json) and
[output-mutation results](../results/public-run-001/output-mutation-results.json).

L18 specifically retained `substrate-covered` from the source decision
partition at `facts.evaluation.evidence_class`. Its output
`facts.oversight.evidence_class` remained `producer-asserted`, the local trust
treatment. These locations must not be described as a verbatim re-export of
a separate source oversight evidence-class field.

## A trusted producer can sign the wrong fact

Both worlds received the same trusted signed L19 record and policy. The record
reports the effect corresponding to `balance=0`. The harness started with
`balance=100` in both worlds and invoked either a write or a no-op.

| Observable | Effect-consistent control | Trusted-producer-wrong |
|---|---|---|
| Operation invoked by harness | `write` | `no-op` |
| Observed final local bytes | `balance=0\n` | `balance=100\n` |
| Signed record native-valid | Yes | Yes |
| WEXP/native admission | `record-only` / `record-only` | `record-only` / `record-only` |
| WEXP/native execution established | false / false | false / false |

The recipient delivery path was the same neutral identifier in both worlds.
Neither recipient received the world label or before/after oracle. The
producer output and recipient decisions were equal across worlds. The harness
could distinguish its endpoints using the extra observation it held; neither
route detected the false world fact from the signed record alone. This
experiment therefore establishes **no WEXP advantage in truth detection**.
The [complete world record](../results/public-run-001/trusted-producer-results.json)
includes exact before/after bytes, hashes, operations and both participant
results. The endpoint check does not rule out transient effects outside this
closed operation.

## Meaning of the successful comparison

The native alternative received the same source bytes, receiver-owned
revision/specification pin and trust policy, and used the pinned native
verification library directly. It received no WEXP output and no extra oracle.
The WEXP recipient independently rechecked that same native source before
interpreting its bounded output. Both routes shared `consumer_policy.py` and
the native reader, as recorded in the prospective [dependency overlap](../pre-run/DEPENDENCY-OVERLAP.json).
Decision parity consequently measures these two compositions under their
shared local policy; it is not evidence of independent algorithm design.

The 16 mutations exercised binding, evaluation-gap preservation, oversight
overclaims, unsupported Core upgrades, fabricated appraisals on invalid input,
duplicate JSON members and non-finite values. Rejection protects the additional
exchange contract; the native baseline never receives that extra surface.

The separate reference comparator required **full strict typed JSON and exact
semantic bytes**, with no permitted semantic difference. All expected input
identities and 16 negative input bytes also matched. The new observations,
timestamps, environment details and public packaging are separate additions,
as fixed by [EXPECTED-DELTA.json](../pre-run/EXPECTED-DELTA.json). The known
private reference was not rewritten or relabeled as this new run.

## Remaining boundaries

- N1/N2 returned `valid` with these pinned readers. Their permitted hypothetical
  `indeterminate` branch was not exercised. The retained producer's generic
  non-valid failure code is broader than the recipient's treatment.
- The retained receiver sorts collection values without deduplication. The
  preserved profile sentence describing duplicate elimination is broader than
  the executed duplicate-free output shapes.
- The recipient was staged without producer/Core modules, but this was process
  and dependency separation in one coordinated environment. No OS sandbox,
  enforced network isolation or external-team reproduction was established.
- The partial HOF evaluator and closed mapping guard do not establish general
  Core conformance. Source hashes authenticate neither world facts nor people.
- Cost, performance, deployment behavior and multi-carrier advantages were not
  measured. Existing Core, EMILIA and private-run bytes remain historical.

The complete [prospective limitations](../docs/LIMITATIONS.md) still apply.
The useful publication is a reproducible record of revision handling, support
limits and output-contract refusals, together with a strong baseline that
made the same local decisions.
