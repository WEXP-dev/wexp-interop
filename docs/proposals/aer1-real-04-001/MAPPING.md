# Mapping: AER-1 receipt real-04 as a Core-02 input

One page. The appraisal is `draft-sergeev-wexp-core-02` (semantics `wexp-core-2`). The external
format is `draft-zambo-aer1-26` (archived text SHA-256
`7e000d80f00ad29b8e01431de562e98956f86e426b2695a34c8a215e689e53d4`, 139,318 bytes). The record is
vector `real-04` of corpus kit 1.5.7 (`real-04.json`, SHA-256
`45c6af65806ad125d9ac33da9e13c737d89e1f2efde5c662cd7baa2db3ab51f8`, 994 bytes). This mapping is
local to this case: profile identity `wexp-work/interop/aer1-real-04-001/mapping-1`, not an AER-1
profile and not a registered WEXP mapping profile.

## Revision 1 (before any appraiser run)

### What the receipt establishes

Recomputed here on 2026-11-22: `canonical_bytes` decode to 337 bytes, and their SHA-256 equals
`output_hash` (`sha256:c92e4cfd…974ca`).

AER-1, Section 6: the verification steps, "applied to a presented record alone, therefore
establish the integrity of the presented bytes only." `output_hash` travels in the same unsigned
file as the bytes. The recompute shows that these are the bytes the stated commitment names. When
that commitment was recorded, and by whom, needs an anchor or another independent record of
`output_hash`.

There is no signature. Every statement in the receipt, including `provenance_class`
("EXECUTED BY ZAMBO"), `verification_status` ("verified"), the caller, the tool, the inputs and
the outputs, is asserted by the producer. Core-02, Section 7: "A string or structural descriptor asserted by a producer is at most
asserted-only."

### Target

The target atom is `aer1:c17b436d-0d9e-48a1-a5de-08dc80a9767e`, the receipt id. AER-1, Section 6:
the id "is not a committed field of the output commitment"; a verifier binds it only against an
independently obtained expected id, or by resolution with a matching `output_hash`. The issue
states that the record is resolvable from the corpus. A verifier that resolves it under Section 9
and finds a matching `output_hash` reports "resolved"; one that performs neither comparison
reports the id as unverified.

| AER-1 id verdict | `target_binding` |
|---|---|
| matched, resolved | supported |
| unverified, absent | not-evaluated |
| mismatched | unsupported |

### Where it goes

| field | value | why |
|---|---|---|
| `boundary_finding.grounding` | `asserted-only` | no signature; Section 7, quoted above |
| `boundary_finding.status` | `supported` under trust configuration `aer1-real-04-trust-asserted`, which accepts asserted-only grounding; `unsupported` under `aer1-real-04-trust-attributed`, which requires attributed | Section 7: an asserted-only finding "can be supported only when the evaluation context explicitly accepts that grounding class; the result still reports the weaker grounding and its limitations" |
| `boundary_finding.ceiling_base` | `execution` | the receipt is written by the party that executed the call, at its own execution boundary. That the boundary was under its control is not established: asserted-only is weaker than attribution, and "Attribution is not proof of actual boundary control" (Section 7) |
| `base_findings` | one `execution` finding: `semantic_validation` supported when the record is well-formed under AER-1 and the recompute matches; `basis_refs` `(mapping-1, real-04 canonical bytes by digest)`; limitation `(mapping-1, L-aer1-unsigned)` | Section 4.2: each base predicate is evaluated independently. This mapping evaluates the execution predicate only; observation, intent and invocation support are marked not-evaluated |
| `qualifier_findings` | PROV and IV, as in cases c and d below | Section 4.3 |
| anchor outcome | "not checked": profile evaluation gap `(mapping-1, G-aer1-anchor-not-checked)`. "absent": limitation `(mapping-1, L-aer1-no-anchor)`, no gap | below, question 2 |

### The two questions in the issue

1. **Provenance inside the hashed payload.** A complete input can be built. `basis_refs` point
   into the canonical bytes by digest, so where the provenance travels does not matter to Core.
   PROV turns on Section 4.3: provenance "semantically validated and accepted in the evaluation
   context", on top of separately established execution. Unsigned, the caller and
   `issuer_claims` remain producer assertions, and no accepted AER-1 provenance profile exists.
   The PROV finding is therefore `semantic_validation = not-evaluated` (case c).
2. **"absent" and "not checked".** They stay apart. "not checked" means an anchor is present and
   was not evaluated: nothing was concluded, so it is a profile evaluation gap. "absent" means
   there was no anchor to evaluate: the evaluation happened, and its result is a limitation (when
   the commitment was recorded rests on the file alone). It is not a gap, and it is not evidence
   that the bytes changed. Core-02, Section 10: "absence of a record does not establish
   nonoccurrence".

**A question back.** real-04 carries no anchor member, and none came with the issue. Under AER-1,
Section 6, "absent" means "no anchor is present for the verifier to evaluate", so this reads
"absent", not "not checked". Is there an external anchor for this receipt? If yes, please point to it, and case a
describes real-04. If not, case e does.

**Independent recompute.** Anyone can recompute `output_hash`, but the recompute checks the
commitment, which travels in the same unsigned file. It does not verify that the call executed.
An IV finding for execution therefore has `semantic_validation = unsupported`, with that reason
(`R-aer1-recompute-commitment-only`, case d).

### Cases

| id | asserted | boundary | findings | anchor |
|---|---|---|---|---|
| a | execution | asserted-only accepted: supported, ceiling execution | execution supported | not checked: gap |
| b | execution | attributed required: unsupported | execution supported | not checked: gap |
| c | execution, PROV | as a | as a, plus PROV not evaluated | not checked: gap |
| d | execution, IV | as a | as a, plus IV unsupported | not checked: gap |
| e | execution | as a | execution supported | absent: limitation |

The expected results are derived from the Core-02 text before the freeze, by a session that sees
only the text, this mapping, the inputs and the representation note, as in
`scitt-receipt-boundary-001`. They are not stated here, so that the mapping is not fitted to an
answer. The inputs are in [inputs/](inputs/), the local profile catalog in
[profiles.json](profiles.json), and the expected results, with the derivation record, in
[expectations/](expectations/).

### Reading choices

All five inputs take `target_binding = supported`: the id verdict "resolved", from the issue's
statement that the record is resolvable from the corpus. If the record does not resolve under
Section 9, `target_binding` is `not-evaluated` in every case and the inputs change.

The anchor gap affects the execution claim `(execution, {})`, and the limitation for an absent
anchor sits on the execution finding. Both concern when the commitment over the canonical bytes was
recorded.

### What was read to write the inputs

`draft-zambo-aer1-26` (pinned in [SOURCE-PINS.json](SOURCE-PINS.json)); `real-04.json` (URL,
SHA-256 and size above); issues WEXP-dev/interop-test-lab#40 and #42; `draft-sergeev-wexp-core-02`.
No appraiser has run on these inputs, and none runs before FREEZE.json is committed.

### What the receipt does not establish

- That the price was right, or that the call was authorized. Issue #40 says so itself: a receipt
  proves the saved result was not changed, "never that the result was right". AER-1, Section 1,
  states the question a receipt answers: "what did this system record for this execution?"
  Core-02, Section 10: execution does not imply correctness.
- That the bytes were not changed after the fact, without an anchor or an independent copy of
  `output_hash` (AER-1, Section 6, quoted above).
- That Zambo produced it: there is no signature, so the grounding is at most asserted-only. Even a
  signature "authenticates bytes under a key; it does not establish content truth or boundary
  control" (Core-02, Section 10).
- Anything about other calls: "presence of records does not establish completeness of coverage"
  (Core-02, Section 10).

### Pinning

`real-04.json` is served from zambo.dev, a host the intake did not fetch. It is recorded here by
URL, SHA-256 and size. A repository commit that carries the corpus would let the skeleton pin it
in the usual way.

### Who initiated the check

Both issues were opened from the AER-1 project account `zambodotdev`; #42 states that it was
submitted by "rambo, AI ops for Zambo", for Brennan Zambo. That he is an author of `draft-zambo-aer1-26` is confirmed with him
directly before any row names him. Until then the row says that naming is not yet agreed.
