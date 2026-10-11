# Independent recipient and strong native alternative — pilot 0.1.0

## What these programs do

`receive_output.py` is a separately implemented recipient for the frozen local
`wexp-aar-pilot-output/0.1.0` interface. It independently verifies the input
record and checks the received output against the recipient's own policy.
It imports no producer, mapper, normalized-input module, or Core evaluator.
The comparison uses the complete closed-profile appraisal: bindings, supported
claims, reasons, gaps, context, limitations, and the source's `doesNotAssert`
strings must survive. It admits only the observation claim defined in
[`profile.json`](../profile.json), with reported execution explicitly not
established and the execution assessment recorded as not evaluated.

`native_baseline.py` is the strong alternative without WEXP processing. It runs
the same selected native signature/schema/recompute verifier and the same
recipient policy against exactly the same source and policy bytes. It does
not consume a WEXP result and does not import `receive_output.py`, a mapper,
or a Core evaluator. It ignores WEXP-only context metadata in the common
policy; the selected revision, expected predicate type, observer key and
record-only admission rule still apply.

Both programs share only `consumer_policy.py` and the pinned upstream native
reader. Sharing the native reader deliberately prevents a weak baseline. It
also means this experiment has common implementation dependencies: process
separation and separate recipient code do **not** establish interoperability
between external teams or independently implemented native verifiers.

## CLI and result

Run each invocation in a fresh Python process. Both upstream revisions use the
same Python package name; mixing their modules in one process is refused.

From the pilot directory:

```sh
python -B consumer/native_baseline.py \
  --source vendor/aar02/vectors-agent-audit-record/statements/v8a2e4c0327732290.json \
  --policy policies/aar02.json

python -B consumer/receive_output.py \
  --source vendor/aar02/vectors-agent-audit-record/statements/v8a2e4c0327732290.json \
  --policy policies/aar02.json \
  --output path/to/received-output.json
```

`--output` names received data to validate; it is not a destination. The only
program output is deterministic JSON on stdout. Expected malformed input,
revision refusal and recipient quarantine are successful executions with
exit status 0. Missing files or unavailable native code are operational
failures with nonzero exit status. An unexpected exception inside the native
verifier is recorded as `native-verifier-error`, preserving its exception
class. It is not fabricated into the native reader's `malformed` verdict or
into a Core `reject` appraisal.

The result contains `route`, input/policy hashes, native verdict and codes,
`output_validation`, diagnostic `errors`, and a `decision` projection.
Compare the two routes' entire `decision` objects for normal matching inputs.
`output_validation=accepted` means the received **output** matches the closed
profile. A correctly described mapping failure can have an accepted output
and a quarantined source. Output tampering changes admission to quarantine;
the independently read record classification is retained, and the output
error is reported separately.

## Admission and evidence boundaries

| Observed source situation | Recipient classification | Established claims |
| --- | --- | --- |
| Valid `evaluated` + `deny` + `none` | `reported-evaluated-deny` | Authenticated report of those fields |
| Valid `not-evaluated` + `deny` + `none`, including A10 | `reported-not-evaluated-deny` | Authenticated report including the named unavailable inputs |
| Valid `not-evaluated` + permit variant | `reported-not-evaluated-permit` | A separately marked incomplete-evaluation report |
| Valid legacy deny, revision 01 explicitly selected | `reported-deny-evaluation-unknown-in-01` | Evaluation status is unknown in that contract |
| Valid decision/effect disagreement | `reported-decision-effect-disagreement` | Reported disagreement; evaluation status remains separate |
| Other valid permit variant | `reported-permit` | Reported permit, regardless of whether an effect was reported |
| Malformed under the selected native reader | `source-invalid` | No admitted facts or appraisal |
| Missing or unsupported revision | `revision-not-selected` | No native verifier selected |
| Revision 02 fields in the closed 01 profile | `revision-policy-mismatch` | Local compatibility refusal, while the native verdict is preserved |

Every admitted valid source has admission `record-only`. Every result has
`execution_established=false`, `authorization_established=false`, and
`human_participation_established=false`. A successful signature check
authenticates the canonical Statement under the supplied test key. A local
SHA-256 of the complete envelope binds the exact bytes consumed; it does not
mean every byte or member of the DSSE envelope is covered by that signature.

Evaluation is the decision point's **reported** evaluation status. Its
`evidence_class` is preserved from the source `fieldEvidence.decision`, as
required by the revision 02 contract; a value of `substrate-covered` does not
create independently accepted authorization evidence in this profile.

Oversight `act` and optional `recordDigest` are preserved. Oversight remains
`producer-asserted`; it cannot establish human participation, an authorized
human approval, IV, or PROV. An absent oversight member also cannot establish
that no person participated.

The source may be structurally consistent, have a valid trusted signature,
and be factually wrong. Both routes can reach `record-only` for exactly those
bytes because neither has an external execution or authorization source.
Controlled-world truth belongs to the test oracle unless it is explicitly
supplied as participant evidence. This recipient neither reads such an oracle
nor silently treats an oracle's result as evidence available to the verifier.
The recipient therefore makes no claim that WEXP detects a coordinated lie
that this equally strong native alternative cannot detect.

## Revision and integrity rules

The recipient-owned policy selects the exact reader before interpretation.
The shared `predicateType` URI never selects a revision. An 01-shaped source
checked under 02 is passed unchanged to the 02 reader, so EV3 becomes a native
malformed result with no Core appraisal. There is no default revision,
fallback, migration, insertion of `evaluation`, or rewrite of historical
results. Unknown requested revision strings remain diagnostic values in the
output binding, while the native result remains `not-run`.

The closed revision 01 profile additionally refuses the presence of
`evaluation` or `oversight`. This deliberately prevents a permissive old
reader from silently accepting new semantics. It is a **local profile rule**,
not an assertion that revision 01 normatively rejects unknown members.

The two source text hashes are independently pinned in `consumer_policy.py`.
The receiver additionally pins the published Core text and finalized local
profile hash in `receive_output.py`. The policy is a trusted local input; a
hash binding does not discover who should be trusted or authenticate a policy
delivered by an untrusted producer. The harness must provision the policy.

The output parser rejects duplicate JSON member names and nonfinite numbers.
It checks the complete source and context objects, exact native verdict/codes,
reported facets, and every field of the allowed appraisal. Core set-valued
collections are compared without imposing array order; duplicate members and
extra entries do not disappear during this comparison. In particular,
execution/IV/PROV support, an `accept` verdict, changed target or context,
removed limitation, false claim support, or removed evaluation gap is refused.
An unadmitted source must carry `facts=null`, `appraisal=null`, and the matching
typed mapping failure.

## Isolated recipient execution

An execution directory needs only:

```text
consumer/consumer_policy.py
consumer/native_baseline.py
consumer/receive_output.py
vendor/aar01/packaging/   (when revision 01 is exercised)
vendor/aar02/packaging/   (when revision 02 is exercised)
input record, recipient-owned policy, received output
```

The dependency paths are resolved relative to the consumer location. No
producer or Core code is looked up. The root harness inventories the staged
files to make this separation reviewable. This is filesystem staging and
process isolation for dependency testing; it is not a sandbox security claim
or a test with a separately administered organization.

## Scope of verification

The versioned source texts, published conformance manifest and vendored reader
define what was executed. Native library verdicts and first-refusal codes are
retained, not re-labelled as WEXP conformance. The reader's implementation
limits remain inherited: it does not verify `priorCommitment.sig`, and its
implemented numeric space is narrower than all of I-JSON/JCS. Neither route
resolves an oversight digest, queries live authorization inputs, proves
nonoccurrence, authenticates a physical execution boundary, audits retention,
or validates a supplied timestamp anchor against an external service.

This recipient checks only the frozen profile's one supported observation
with unqualified execution requested. It cannot validate arbitrary Core
inputs, arbitrary profiles, composition, IV/PROV, or positive counter-evidence.
Execution records and local corpus outcomes are in the root result artifacts;
this contract note makes no independent assertion that a listed test ran.
