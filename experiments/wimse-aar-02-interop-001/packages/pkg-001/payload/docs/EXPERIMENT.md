# Experiment, baseline and prospective conditions

## Question and comparison

Can a recipient retain AAR revision semantics, evaluation gaps and limits on
human-act claims through a bounded WEXP output, and does that change its local
decisions compared with a strong native-library route?

The mapping profile admits observation of an authenticated report while the
requested claim is execution. No independent invocation, execution-boundary,
authorization or human-record artifact is supplied. This is a fixed premise of
the experiment, not a conclusion inferred from a favorable result.

| Information or processing | WEXP route | Native baseline |
|---|---|---|
| Exact source envelope | Same input | Same input |
| Receiver-owned revision/specification pin | Same input | Same input |
| Trusted test signer key and admission policy | Same input | Same input |
| Native verification | Producer, then recipient recheck | Recipient |
| Additional ground truth delivered | None | None |
| Core/mapper/output-contract interpretation | Bounded implementation | None |
| Local decision code | Shared consumer_policy.py | Same file |

The within-run WEXP/native decision comparison is distinct from comparing the
new run to the supplied private reference. Neither reference matching nor
output-mutation rejection demonstrates a truth-detection advantage over the
native route.

## Prospective inputs and expectations

The exact file inventory, three published TXT sources, two native source
revisions, profile, policies, source records, oracle, expectations and comparator
are fixed by the pre-run input lock and freeze. All 130 case identities and
source/policy hashes are in [EXPECTATIONS.json](../pre-run/EXPECTATIONS.json).
All 16 exact negative output inputs are in
[OUTPUT-MUTATION-INPUTS.json](../pre-run/OUTPUT-MUTATION-INPUTS.json).

Published expected verdict sets come from the unchanged native manifests.
The 19 local expectations retain their requirement loci and parent vectors.
The six compatibility and three dispatch conditions are declared explicitly.
The private run already exists and is known to the preparation team. The
reference is a complete readable semantic projection, with its private-origin
commit, source hash and limits in [reference provenance](../reference/PROVENANCE.json).
This new commitment is prospective with respect to the public composition,
but the experiment is not blind.

The new run must preserve the full semantic projection byte-for-byte. The
[expected delta](../pre-run/EXPECTED-DELTA.json) allows no source, fixture,
policy, profile, implementation-source or semantic-result change. New observation timestamps,
runtime strings, process timings and packaging metadata are recorded separately.
Unexpected differences fail the comparison and remain in the history.

## Key distinctions

- A2 and A10 both report deny / none / agree. The recipient must distinguish
  reported-evaluated-deny from reported-not-evaluated-deny and retain A10's
  unavailable standing-source.
- The historical A1 envelope is exactly the new EV3. It remains native-valid
  under the old revision and malformed under the selected new revision, with
  no fabricated Core appraisal. A successful old parse cannot choose a version.
- Oversight act/digest is carried without establishing human participation or
  authority. A digest may be unresolved, and absent oversight does not prove
  absent human activity.
- L18 preserves the source decision evidence class in facts.evaluation.evidence_class.
  The output oversight evidence class is the local
  producer-asserted trust treatment, not a verbatim copy of that decision
  evidence partition.

## Trusted but wrong producer

The trusted public test key signs one coherent envelope reporting a write from
balance=100 to balance=0. The harness uses identical signed bytes and policy in
two controlled worlds: one performs the write, the other invokes a no-op.
It records before/after bytes and the selected operation. Recipients receive
neither the oracle nor the world identifier, and the retained runner uses the
same neutral participant delivery path in both worlds.

The expected record-alone decision is report-only in both routes and worlds,
with execution_established=false. The harness can distinguish its controlled
endpoint outcomes because it has the oracle. That extra harness observation is
not silently given to either recipient. Endpoint equality alone would not rule
out transient effects outside this closed operation.

## Dependence and control

[DEPENDENCY-OVERLAP.json](../pre-run/DEPENDENCY-OVERLAP.json) computes the
intersection of the conservative source-file closures for the two recipient
entry points. They share the selected native reader, its packaging imports and
consumer_policy.py. This inventory is not a dynamic import trace.

The [control declaration](../pre-run/CONTROL-DECLARATION.json) separately
records who controls the environment and who can read the expected results.
Both routes run in one coordinated environment. The staged directory and
fresh processes are not an OS sandbox, an independently governed team or an
independent external observer.

N1/N2 retain the native corpus's valid/indeterminate alternatives, but the
pinned private execution returned valid. General indeterminate producer
handling and duplicate-eliminating set comparison are not demonstrated by this
finite procedure; the exact boundaries are in [LIMITATIONS.md](LIMITATIONS.md).
