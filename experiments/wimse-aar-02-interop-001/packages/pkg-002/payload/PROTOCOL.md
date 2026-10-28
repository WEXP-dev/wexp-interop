# WIMSE record-only mapping to Core-02: pre-run contract

This is a new bounded migration trial, not a relabeling of the historical
WIMSE AAR-02 package or its two-world execution. The commit containing this
protocol, code and profile is the pre-run commitment. Results belong outside
that commit and identify its exact SHA. The original package remains unchanged.

## Question and fixed comparison

Does the explicitly versioned Core-02 record-only mapping preserve the native
facts and recipient decisions for the historical 130 input cases while
returning the complete Core-02 result required by the new context?

Read [profile.json](profile.json) for immutable external pins. Native AAR-01
and AAR-02 readers, raw records, observer keys, selected revisions, timestamps
and record-admission policy remain those in historical `pkg-001`. The current
upstream AAR revision is deliberately not substituted. The first trial changes
only the mapping/result layer; changing both source and appraiser would
confound this comparison.

## New normalized-input contract

Use the record-scoped target of the earlier profile, not a global action ID.
The native verifier must succeed before any finding is constructed. A valid
but locally disallowed cross-revision record is still not mapped. Preserve
native evaluation status, unavailable inputs and producer-asserted oversight.

The exact profile identity is its `id` followed by `:sha256:` and the SHA-256
of the exact profile bytes. Logical target, time and trust atoms use exact
Unicode scalar text. Scoped atoms are ordered [profile_identity, local_value]
pairs; no Unicode normalization, URI dereference or aliases are introduced.
The context identifier hashes the ASCII policy digest, a newline, and the
profile identity. The original policy bytes are not rewritten; WEXP-specific
legacy fields are historical provenance, not Core-02 configuration. The new
profile and pinned appraiser are selected explicitly outside that policy.

After native validation, the reporting boundary is attributed and accepted
with observation ceiling. Observation alone is supported; intent, invocation,
execution, PROV(execution), and all four IV assessments remain not-evaluated.
Binding to the signed report's exact action reference passes, but is not proof
of an executed business action. Native derived tier is not execution evidence.
A complete capability map retains these distinctions. Counter-evidence is the
not-supplied sentinel for this packet-only evidence domain. No composition
predicate is requested. Existing source limitations are retained in the new
profile scope, not erased by renaming the profile.

## Expectations fixed before execution

For each admitted case, the receiver constructs a source-authored full-result
template without importing the producer mapping or Core appraiser:

- S = M = {observation}; requested execution is not supported; verdict downgrade.
- The observation support entry retains exact record basis and all applicable
  limitations; relation is support-below-claim.
- Boundary ceiling is observation and grounding is attributed.
- `E_BASE_EXCEEDS_BOUNDARY` and the claim-scoped `E_BASE_NOT_EVALUATED` gap both
  occur: an execution aggregate exists, is above the ceiling and is unevaluated.
- All twenty components, including context, scope, counter sentinel, empty sets
  and limitations, are compared as typed logical values, not just verdicts.

On native or dispatch failure, no Core input or appraisal is produced. The
native result and recipient decision are compared against the retained
historical result for the same exact raw input/policy. The historical result
is a known reference, not an independent oracle or a new Core-02 expectation.

Mutation controls omit and change every result component, substitute Boolean
with number, reverse an ordered atom, and alter source/profile bindings. All
must be refused by the source-aware receiver. Reversing mathematical set order
must remain equivalent; duplicate members are not silently deleted.

## Execution and independence

[run.py](run.py) requires exact clean legacy and ref checkouts. Every case uses
fresh processes for native-baseline, producer, and receiver; two AAR reader
revisions must never coexist in one process. The receiver is staged without
the producer or Core code and receives raw source, policy and delivered result,
not the normalized input. Filesystem/network access is not sandboxed.

Both routes reuse the pinned native verifier and recipient decision policy.
The author knows the source, old results and expectations. This is same-project
bounded validation, not an external independent reproduction or a blind trial.
A second runtime or green CI does not change that. Parity is a permitted result;
no superiority of WEXP is presupposed.

## Commands and evidence

Python 3.12/3.13 are the requested run environments. From this directory:

```sh
python -B run.py --legacy /path/to/pinned-interop --ref /path/to/pinned-ref --out /path/to/new-results
python -O -B run.py --legacy /path/to/pinned-interop --ref /path/to/pinned-ref --out /path/to/another-new-results
```

Use new absolute external output paths. The report retains runtime, source pins,
complete observed outputs, expected results, process errors and failed cases.
A failed or interrupted run is preserved, not counted as PASS. Reports are
not included in the frozen protocol's own hash. Hosted observations require
actual run and job IDs. Promotion to a versioned collection experiment requires
its own card, manifest, durable evidence, reproduction review and publication
record; this pre-run directory is not added to the results catalog by itself.
