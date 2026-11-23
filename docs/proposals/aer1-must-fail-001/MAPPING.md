# Mapping: AER-1 must-fail vectors (draft-zambo-aer1-26) as Core-02 inputs

Core-02 line numbers refer to the published XML of draft-sergeev-wexp-core-02 (SHA-256
`de983051a1c6ea51ea9b7f965fe9eabf2d97af92ab2f074781bd44e3f99c8782`). The external format is
`draft-zambo-aer1-26` (archived text SHA-256
`7e000d80f00ad29b8e01431de562e98956f86e426b2695a34c8a215e689e53d4`, 139,318 bytes). The vectors are
from AER-1 corpus kit 1.5.7 (evaluated set digest
`sha256:60bf73f325793e16843370cfa24903bb0d017525cb297e42bebc35857e2db0d2`); see
[Pinning](#pinning). The profile identity `wexp-work/interop/aer1-must-fail-001/mapping-1` is local
to this proposal: it is not an AER-1 profile and not a registered WEXP mapping profile.

## Revision 1 (before any appraiser run)

### The question

Issue WEXP-dev/interop-test-lab#40 asks whether the corpus is useful beyond AER-1, and names three
kinds of fixture: the id-binding swap, anchors that must be reported absent, and records that must
come back "not checked". In this pull request the author adds that the must-fail set is the
corpus's invalid vectors, whose expected outcome is a failure, and that a must-fail vector that
comes back accepted is a divergence.

This proposal accounts for all 36 invalid vectors of the kit and for the id and anchor vectors that
#40 names. It tests one rule: Core must not accept where an AER-1 verifier must not pass, and must
keep apart the states that AER-1 keeps apart. Where Core lands softer than AER-1, the case shows
that gap.

### What AER-1 reports

AER-1, Section 6, reports three layers for every record: a structural verdict (a pass,
"verification failed", or "rejected: <reason>"), an id verdict (matched, resolved, mismatched,
unverified, absent) and a per-anchor outcome (verified, verification failed, rejected:
unresolvable record, not checked, absent). "The structural verdict governs the presented bytes and
is never upgraded or downgraded by the id verdict", and the anchor outcome "does not alter it".

Each input is built from the outcome the kit pins for the vector (`expected_verdict`,
`expected_id_verdict`, `expected_anchor_outcome`, or the invalid directory and the vector's
`rejected_by` member), not from a new verifier run.

### What reaches Core

A Core input is built only from a record whose members can all be read. Where they can be read and
contradict each other (a digest against the bytes it commits to, an outer member against the value
committed in the canonical bytes), the profile supplies the fatal condition that line 393 names for
it. Where a member cannot be read, or a member the format requires is missing, there is no complete
input: line 73, failure to interpret a carrier well enough to construct the input "produces no Core
appraisal". The failure stays with the mapping profile, and nothing is accepted.

Of the 36 invalid vectors, 5 become cases and 31 never reach Core:

| rule the vector fails (its `rejected_by`, or the kit's runner where it has none) | vectors |
|---|---|
| `created_at` is not RFC 3339, or not a valid calendar date and time (leap second included) | ax-feb29-1900, ax-feb29-non-leap, bad-created-at, bad-offset-range, feb29-1900, feb29-non-leap, impossible-date, leap-second-created-at, lowercase-timestamp, timestamp-no-timezone |
| `id` is not a lowercase UUID, or is the nil UUID | bad-id, id-trailing-newline, uppercase-id, nil-uuid |
| `canonical_bytes` is not valid base64, not the canonical spelling, or not UTF-8 | ax-base64-unpadded, base64-pad-bit, base64-unpadded, bytes-not-base64, non-utf8-bytes |
| `tool` is not an object with name, version and scope strings | ax-tool-empty-scope, tool-empty-name, tool-not-object |
| `provenance_class` is not a known class | bad-provenance, provenance-control-char, provenance-trailing-newline |
| `output_hash` is missing or malformed | hash-bad-format, missing-output-hash |
| a duplicate member name | duplicate-member-name |
| `verification_status` is not "verified" | bad-verification-status |
| a member that a schema 0.4 payload must commit is missing (the kit's checks 9a and 9c; missing, not contradictory) | payload-is-array, payload-omits-issuer-claims |

### How each layer is carried

| AER-1 | Core-02 input |
|---|---|
| id verdict matched or resolved | `target_binding` supported on the boundary and execution findings |
| id verdict mismatched | `target_binding` unsupported. Line 393: "Ordinary negative or unevaluated exact-target binding is represented by a correctly scoped aggregate and is non-fatal." |
| id verdict unverified | `target_binding` not-evaluated, and the `target-binding` capability not evaluated |
| anchor verified | nothing added |
| anchor not checked | profile gap `P_AER1_ANCHOR_NOT_CHECKED` on `(execution, {})`, as in aer1-real-04-001 |
| anchor rejected: unresolvable record | profile gap `P_AER1_ANCHOR_UNRESOLVABLE`. A separate token: Section 6, the two "are different states and MUST NOT be conflated" |
| anchor verification failed | counter-evidence `unresolved-material` on `(execution, {})`, reason `P_AER1_ANCHOR_DIGEST_MISMATCH` (reading choice 1) |
| anchor absent | limitation `L-aer1-no-anchor` on the execution finding, as in aer1-real-04-001 |
| `output_hash` or `input_hash` does not match what it commits to | supplied fatal `E_INTEGRITY_INVALID` (line 393), and the execution finding unsupported |
| an outer member contradicts the value committed in the canonical bytes | supplied fatal `E_BINDING_MISMATCH`: "protected fields or mandatory mapping bindings are internally contradictory" (line 393) |
| schema 0.3 without `metadata_hash` (legacy acceptance) | limitation `L-aer1-legacy-unbound` on the boundary and execution findings. Section 6, step 4: the id, tool, creation time and provenance class "are NOT bound to the output commitment", and a legacy acceptance "MUST NOT be reported as a plain pass under the current schema" |

An anchor that was not checked is a check that was not attempted; an anchor whose record could not
be resolved is a check that was attempted and could not be completed. Neither concludes anything,
so both are gaps, under different tokens. A failed anchor is a check that was completed and found a
contradiction, so it is counter-evidence. An absent anchor leaves the time of the commitment
resting on the file alone, so it is a limitation.

Line 393 makes a failed id comparison non-fatal: it is carried as a finding about the target, not
as a reason to reject the input. Where AER-1 fails the record (id-expected-mismatch,
id-resolution-disagreement), the case shows whether Core lands softer.

Common to all cases. There is no signature, so the boundary grounding is `asserted-only` (line
405: "A string or structural descriptor asserted by a producer is at most asserted-only"), with
limitation `L-aer1-unsigned`. The boundary is `supported` with ceiling `execution` under trust
configuration `aer1-must-fail-trust-asserted`, which accepts asserted-only grounding (line 406).
The execution finding is semantically validated where every commitment over the record verifies.
Observation, intent, invocation, PROV and IV are not evaluated. Counter-evidence is `not-supplied`
unless a case says otherwise. `evaluated_at` is 2026-11-23T00:00:00Z.

### Target

The target atom is `aer1:<id>` of the execution the check asks about: the expected id where one is
supplied (`id-expected-*`), otherwise the id the presented record carries. The id cases share the
Section 3 fixture of `id-binding-vectors.json` (`130da435-e157-498e-af90-605866a86a27`); in the two
swap vectors the record carries the donor id `42fc3298-b1e7-4087-bb1c-f80ef9f12c7c`. The anchor and
invalid vectors carry no expected id. These cases supply one equal to the record's id (id verdict
matched), so that only the anchor or the failure varies; without it, each would also carry the
unverified id state.

### Cases

| case | file | what varies |
|---|---|---|
| id-expected-match | id-binding-vectors.json | control: matched |
| id-expected-mismatch | id-binding-vectors.json | mismatched against the fixture's true id |
| id-resolution-agreement | id-binding-vectors.json | control: resolved |
| id-resolution-disagreement | id-binding-vectors.json | mismatched at resolution; the target is the donor id the record carries |
| id-alone-unverified | id-binding-vectors.json | unverified |
| anchor-resolves | anchored-valid.json | control: anchor verified |
| anchor-not-checked | anchored-unresolvable-anchor.json | anchor present, not evaluated |
| anchor-unresolvable | anchored-unresolvable-anchor.json | rejected: unresolvable record |
| anchor-verification-failed | anchored-bad-leaf-hash.json | verification failed |
| anchor-absent | receipt-01.json | absent |
| hash-mismatch | hash-mismatch.json | `output_hash` all zeros |
| input-hash-mismatch | input-hash-mismatch.json | `input_hash` does not match the recorded inputs |
| input-hash-key-order-20 | input-hash-key-order-20.json | `input_hash` over a different member order |
| tampered-provenance | tampered-provenance.json | outer `provenance_class` "LOGGED BY AGENT", committed `issuer_claims.provenance_class` "EXECUTED BY ZAMBO" |
| version-downgrade | version-downgrade.json | outer `receipt_schema_version` "0.3", committed "0.4" |

The five anchor cases and hash-mismatch are one record (`b6c63ac5-f324-4fa7-ad58-c4bf83faa86a`,
schema 0.3) with different anchors or a zeroed `output_hash`. The last four commit a schema 0.4
payload and carry no `metadata_hash`. The inputs are in [inputs/](inputs/), and the local profile catalog in
[profiles.json](profiles.json).

The expected results are derived from the Core-02 text before the freeze, by a session that sees
only the text, this mapping, the inputs and the representation note, as in aer1-real-04-001. They
are not stated here, so that the mapping is not fitted to an answer.

### Left out

- `id-absent`: no receipt id, so no target and no complete input (line 73).
- `anchor-other-profile`, `anchor-unresolvable-bad-leaf`, `anchor-partial-profile`, and the anchored
  fixtures `anchored-bad-id-version`, `anchored-bad-timestamp` and `anchored-missing-proof`: they
  test how a verifier recognises an anchor shape, or reach an outcome already covered by another
  cause. They can be added later.
- `invalid-profile/missing-inputs`: valid at the core tier by design; it fails only the
  reference-producer profile.

### Reading choices

1. **A failed anchor.** AER-1 does not let it fail the receipt's output commitment check. Core can
   still withhold the execution claim: a stored anchor that names a digest other than the record's
   means that either the anchor is wrong or the commitment changed after anchoring, and nothing here
   resolves which. This revision carries it as `unresolved-material` (line 364: "material but
   unresolved"). The other reading is a limitation only; under it, anchor-verification-failed
   changes.
2. **A digest mismatch** could be carried as a non-fatal execution finding that is unsupported. This
   revision supplies `E_INTEGRITY_INVALID`, the condition line 393 names.
3. **version-downgrade.** Section 6, step 4, keys the metadata check to `receipt_schema_version`.
   Read as the outer member ("0.3", no `metadata_hash`), the record gets a legacy acceptance;
   Section 13 describes this move: "A forger can also strip metadata_hash and rewrite the schema
   version to "0.3"." The kit fails the vector by comparing the outer version with the version
   committed in the canonical bytes ("0.4"; its check 9a), a comparison Section 6 does not state,
   and Section 2 requires the vector to fail. This revision follows the kit.
4. **The anchor vectors.** The anchored fixtures carry the kit's anchor shape (`log`, `leaf_hash`,
   `anchored_at`, `proof`), not the anchor of Section 10, Table 4. Under Section 6, a verifier that
   implements only Table 4 would report them absent. In the kit's runner, anchored-valid is
   "verified" by construction: the leaf hash equals the output digest, and a log host outside
   `.invalid` counts as resolvable; the proof (`{"type": "opaque"}`) is not checked, while Section
   10.1 reports an anchor as verified only after its proof is verified. These inputs carry the
   outcomes the kit pins.

### Questions for the author

1. A failed anchor: material and unresolved for the execution claim, or a limitation only?
2. version-downgrade: in Section 6, step 4, is `receipt_schema_version` the outer member or the
   committed one? Is the kit's check 9a meant to be in the text?
3. The kit's valid directory carries ten schema 0.4 receipts without `metadata_hash`: bound-04,
   deep-nesting, edge-numbers, empty-members, input-hash-multikey-20, large-payload,
   maximum-offset-timestamp, optional-members-18, typographic-unicode, uuid-v1-core. Section 6,
   step 4: "A "0.4" receipt without metadata_hash MUST fail." Which governs, the text or the kit?
   None of these vectors is a case here.
4. The anchored fixtures: is the kit's anchor shape meant to be covered by the text, and is
   "verified" meant to require a checked proof?
5. The split above: contradictions carried to Core as fatal conditions, unreadable or missing
   members left to the mapping. Does it match how AER-1 sees the invalid vectors?

### What the vectors do not establish

That any implementation conforms to AER-1, or that AER-1 conforms or does not conform to WEXP Core.
The records are corpus fixtures; nothing here is about a real execution.

### What was read to write the inputs

`draft-zambo-aer1-26` (pinned in [SOURCE-PINS.json](SOURCE-PINS.json)); the kit files below; the
kit's runner `base/conformance.py` (SHA-256
`af30138281da5c843e5a75559cc21122805b1f3419ff986a55f656ac3e7012dc`, 77,029 bytes), read as text and
not run; issue WEXP-dev/interop-test-lab#40 and this pull request; `draft-sergeev-wexp-core-02`. No
appraiser has run on these inputs, and none runs before FREEZE.json is committed.

### Pinning

The files are served from zambo.dev under <https://zambo.dev/aer1/corpus/v1.5.7/>, a host the
skeleton did not fetch. `corpus.json` (15,706 bytes, SHA-256
`dd3fbcd52ff7ba18536925b2700e4c38171d988acc335dbc240b3090f83a4bf0`) lists a digest for every vector
file; each file named in this mapping was fetched and matches it. The files the cases are built
from:

| path under `base/` | bytes | SHA-256 |
|---|---|---|
| `id-binding-vectors.json` | 11382 | `78cb42cbc8be1306458f63e90e01f0e9201504ff5bf5d455a659631f21237009` |
| `anchor-vectors.json` | 6301 | `15fe803468cc54a0bbddf04f592ac42fcbdb71d9353b91c8ef0b903557578fb8` |
| `test-vectors/anchored/anchored-valid.json` | 682 | `03dcdc8be19340ce91ddc6f6fc6c98f2b8b2bc183b350c6c3f2b849bd0f52daf` |
| `test-vectors/anchored/anchored-unresolvable-anchor.json` | 682 | `7060532c55c6d01a9d420433f5578810993f428597edfcd1612996e140647473` |
| `test-vectors/anchored/anchored-bad-leaf-hash.json` | 682 | `5e8ea1918e69be2f26dfa2da6707ad6868797f9114d6d19a3c19189662e377e2` |
| `test-vectors/valid/receipt-01.json` | 540 | `f6f2b532a70c1969a0e70a8342ad5a9fefa5810f163b930560b4bfffb9a24931` |
| `test-vectors/invalid/hash-mismatch.json` | 611 | `6037f4dd7abe55c8fcf88224e7fe02ef0ea7eccbde462d4f16263dc8557f9228` |
| `test-vectors/invalid/input-hash-mismatch.json` | 1852 | `5c745d87db58d21ab577759eb83976988b59aa17830fb10eec2709e5603281a6` |
| `test-vectors/invalid/input-hash-key-order-20.json` | 1884 | `d1f0809e01a7f6d79100400083c13c935fece85695492f7a52373c6c381e9b54` |
| `test-vectors/invalid/tampered-provenance.json` | 630 | `60fe34e381b33b58150479dcd990943d86c26e9c05aec39f7bd0567f982772cd` |
| `test-vectors/invalid/version-downgrade.json` | 632 | `228160b1c6fa8985df13a11342fae58844dc05bd34a3017f344c8d08deb1d3b9` |

### Who initiated the check

Issue #40 was opened from the AER-1 project account `zambodotdev`. In this pull request the account
answered "Name me as: Brennan Zambo, an author of Internet-Draft draft-zambo-aer1-26"; that
authorship was confirmed with him directly for aer1-real-04-001. The result row names him when it
is written after the run.
