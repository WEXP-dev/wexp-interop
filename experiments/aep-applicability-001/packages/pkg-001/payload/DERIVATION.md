# Session B — specification-derived expectations, v1

This is a local proposal expectation derivation for profile
`urn:wexp:proposal:aep-applicability-001:profile:1:r4`. It is not a conformance
claim or an external reproduction. B used a separate AI context under the same
operator and shared filesystem; exclusion of implementations was procedural,
not enforced by a sandbox. The read-only hash helper is disclosed in
`evidence/B-SESSION.json` and `evidence/B-HASH-HELPER.json`.

Every Core citation below is a one-based line reference into retained
`evidence/basis/specifications/draft-sergeev-wexp-core-02.xml`, SHA-256
`de983051a1c6ea51ea9b7f965fe9eabf2d97af92ab2f074781bd44e3f99c8782`.
`AEP draft` is retained
`evidence/basis/specifications/draft-sokolov-rats-aep-composition-06.txt`,
SHA-256 `a2561d39ddd1707d04df100137bdbff2bcde367a477e06e6068efe45572e1431`.
AEP code and samples mean retained paths below `evidence/basis/aep-sandbox/`
at `f6c88be63c5aa12b8e8f6bf35a378a6a5fca9cd4`. Text line numbers count LF
separators; a form-feed page-break line does not create an extra line.

## Integrity and scope of derivation

B independently re-read and SHA-256 hashed all 33 files named by
`HANDOFF.json`, its two control files, and all six inputs against
`INPUT-HASHES.json`. The staged inventory contained exactly 35 regular files,
no symlinks and no extra file. All applicable A-FREEZE entries matched;
entries outside the whitelist were not opened. The helper separately reached
the same integrity findings. `evidence/B-VALIDATION.json` retains B's repeatable
checks, input hashes, logical comparisons and complete-component validation.

B read HANDOFF, PROFILE, MAPPING and Core before the raw inputs, then inspected
the admitted AEP text, sample fields and necessary code ranges. A's permitted
preparation observations were reviewed as upstream preparation evidence; B did
not repeat cryptographic checks or execute retained AEP code. No native verdict,
Core output or appraiser implementation supplied an expectation.

The six inputs use the same JSON line layout: semantics at line 2; target at
3; assertion at 4–7; context at 8–15; boundary at 16–39; observation at 41–60;
execution at 61–84; empty qualifiers and recorder relations at 86–87; counter
sentinel at 88–96; scope at 97–146; empty profile gaps at 147; inherited domain
limitation at 148–153; empty fatal conditions at 154. These are concrete input
facts, not assumptions about an implementation.

## Admission before support

For all six inputs, the ordered ingress checks pass. The outer value is a
record and the version is the recognized text atom (Core XML 385–387). Every
required top-level and finding member has the stipulated logical shape
(269–356); there are no extra members, duplicate set members, unknown enums or
unbound scoped atoms (373–388). The profile identifier is the r4 immutable
revision and its own-token registries are empty; no supplied reason/gap/fatal
token requires an additional registry binding (366–374).

Each input has exactly one boundary, one observation aggregate and one
execution aggregate; every target/context reference matches its top-level
scope (360–361). An unsupported boundary may omit its ceiling. Attributed
grounding with unsupported status is allowed; the rule requiring acceptance
of grounding is conditional on a supported boundary (362, 406). No qualifier
aggregate needs validation. The sole counter entry is the exact empty
`not-supplied` sentinel (363–364).

All twelve scope keys occur once. `carrier-mapping` is evaluated;
`execution-support` is not-evaluated and its present execution finding has
not-evaluated semantic validation. Other supplied governed fields are
assessed; absent intent, invocation, provenance and IV aggregates accompany
evaluated searches. No authenticity/composition marker gaps are present, so
those two external capabilities are evaluated (Core XML 758–780). The map is
preserved, not used to manufacture support (782). The fatal set is empty and
the asserted `(execution,{})` is admissible (172–180, 389–390). Thus no rejection
branch applies. If one did apply, every component would instead follow the
fixed unavailable projection, not retain a partial input (560–576, 612).

## Independent reading of the mapping's evidentiary choices

Both samples report `issue_refund` on `ORD-4471` in EUR; their amounts are 250
and 9000, and their reported outcomes are `ok`, with different refund IDs
(each retained sample, lines 4–20). Both embed the same 1000-cap mandate
(each sample 36–52). The source calls that mandate a capability grant rather
than an exact-action approval (`aep/mandate.py` 80–88). The historical execution
assertion selected by this profile is therefore distinct from authority
validity, consistent with Core XML 145 and 149.

The protected receipt includes action, outcome and nonce
(`aep/package.py` 26–31, 46–62); the measurement comparison is expressly a
self-consistency check (105–111). Key and identity checks precede amount scope
and expiry (`aep/mandate.py` 149–167). Replay membership is another predicate
(`aep/package.py` 128–133), and consume writes happen only after ALLOW with
consume requested (`verify.py` 62–68). These source predicates support the
profile's separation of authenticated report content, authority and evolving
submission state. B does not infer that a native run actually occurred.

The AEP draft states that platform binding does not independently observe
the action or effect (117–126), separates application authorization from
trustworthiness (144–151), and treats unsupported success as an application
claim (346–348). Its freshness and consumed-identifier discussion concerns
additional applicability checks (509–511, 526–530, 585–589). These passages do
not prove the mapping universally correct. They justify using this bounded
historical assertion without silently substituting a freshness-composition
claim, whose distinct challenge rule appears at AEP draft 318–326.

B accepts the profile's unsupported boundary in both contexts: identity
attribution does not establish control (Core XML 405), and merely admitting
attributed grounding in C-attrib does not make the missing control/coverage
predicate pass (406). The supplied sample field domain contains reported
action/outcome, credential, mandate, digests and signature, without a runtime
or service observation (each sample 1–59; AEP draft 178–195 describes the
additional platform roles). Thus the separate execution occurrence assessment
can remain not-evaluated while the sufficiency assessment of the available
boundary description is unsupported, as the status distinction requires
(Core XML 359). No unsupported execution finding or defeating counter entry
is inferred merely from 9000 exceeding the cap (Core XML 149, 364–365).

## All twenty components, for every case

The table is normative for the six B expectation files, not a statement of
any implementation's output. `expectations/v1/DERIVATIONS.json` expands these
twenty rows for each of the six cases with the complete expected component
value, exact XML lines and input pointers. `T`, `C`, and `R` below are the
case's input target, complete context and singleton execution basis-reference
set. Every non-rejection result has all twenty keys (Core XML 584–612).

| Component | Expected value in all six cases | XML derivation |
| --- | --- | --- |
| semantics_version | `wexp-core-2` | Recognized version and result contract: 356, 588. |
| verdict | `downgrade` | Safe admissible input without exact support: 448–451; algorithm 552–556. |
| fatal_reasons | empty set | No ingress branch; empty non-reject fatal set: 383–394, 515, 610. |
| target | `T`, copied exactly | Opaque identity and copy semantics: 374; result target: 591. |
| asserted_claim | `(execution,{})` | Typed claim 172–180; input assertion retained in result 592. |
| asserted_claim_supported | `false` | Empty SupportedClaims; exact membership: 459, 513–514. |
| support_entries | empty set | No supported claim has premises to emit: 436, 497–511. |
| supported_claims | empty set | Unsupported boundary fails the conjunct for every base, including positive observation: 407, 415–432. |
| maximal_supported_claims | empty set | Maximal members of an empty set: 435, 513. |
| support_relations | empty set | Explicit no-support rule: 457. |
| boundary_ceiling | `unavailable` | Unsupported boundary makes ceiling unusable: 407, 611. |
| boundary_grounding | `attributed` | Preserve grounding even for unsupported boundary: 405, 611. |
| recorder_relations | empty set | No input relation; descriptive relation preservation: 376, 600. |
| substantive_reasons | `{E_BOUNDARY_NOT_SUPPORTED}` | Unsupported boundary row 621–622; exhaustive diagnostic restrictions 619. No supplied finding reasons. |
| evaluation_gaps | `{E_BASE_NOT_EVALUATED}` | Execution semantic status row 639–640; token projection 549, 610. |
| evaluation_gap_entries | one exact execution gap, detailed below | Scope, affected claims and source premise copy: 579, 603, 610; trigger 639–640. |
| counter_evidence | exact input `not-supplied` sentinel with all four sets empty | Sentinel semantics 364; complete entry preservation 610; nonblocking 452. |
| inherited_limitations | exactly five profile-scoped atoms, detailed below | Applicable union 437; scoped equality 374–377. |
| evaluation_context | `C`, copied exactly | Opaque context and immutable profile identity 374; required result 606. |
| evaluation_scope | exact twelve-entry input map | Unordered map and closed keys 758–773; preserved scoped result 607, 773; non-evidentiary role 782. |

`B={}` because the boundary-status conjunct fails for every base. Observation's
positive validation cannot bypass that conjunct (Core XML 415–420). No
qualifier or lower structural claim appears by inference (155, 422–435).
The counter sentinel does not assert real-world absence of counter-evidence
(738), but does not block this assertion (452).

The sole structured gap has exactly these six components:

- `token = E_BASE_NOT_EVALUATED`;
- `target = T`;
- `evaluation_context_ref = C.id`;
- `affected_claims = {(execution,{})}`;
- `basis_refs = R` from the present execution aggregate;
- `limitations = {(P,self-report-is-not-external-effect),
  (P,execution-assessment-material-unavailable)}`, with P the applied r4 ID.

It has no `current_scope_capability`: that optional field belongs to a supplied
profile gap, and this gap is Core-derived from the execution finding (Core XML
369, 579, 610). Boundary grounding and binding are assessed, so no boundary gap
exists (623–628). The asserted execution aggregate is present, so no missing
evidence reason exists (619, 631–632). Its semantic validation is not-evaluated,
not unsupported, so no `E_EXACT_CLAIM_NOT_SUPPORTED` exists (637–640). No usable
ceiling exists, so no base-exceeds-boundary reason exists (619, 629–630).
No qualifier is asserted, and the sentinel is nonblocking; no qualifier or
counter row applies (641–664). Empty profile gaps and finding reasons add
nothing (526–533, 667).

The inherited limitation set is exactly:

1. `(P,bounded-two-packet-domain)` from input inheritance;
2. `(P,boundary-control-not-established)` from boundary;
3. `(P,no-boundary-grounding-profile)` from boundary;
4. `(P,self-report-is-not-external-effect)` from asserted execution;
5. `(P,execution-assessment-material-unavailable)` from asserted execution.

Core XML 437 requires all five and no other member. Execution determines the
asserted-role gap, so both its limitations survive even though no claim is
supported. The same self-report atom on observation does not produce a sixth
member: equality and union are mathematical sets (374–377). Observation does
not supply a support entry here; its limitation is already independently
applicable through the execution finding.

## Case identities and hypotheses

| Cases | Target amount | Execution basis local value | Context suffix |
| --- | --- | --- | --- |
| a-strict, b-strict | 250 | `aep-file:sha256:305bc28083e99ae417a18ce35d042e2e2e66d2eaad9f840cbe34bde466a99437` | strict:r4 |
| c-strict | 9000 | `aep-file:sha256:3b7f18af3e8d5cc41f40f036282cd15afe49a68d381f1a5b0bdb8c30a24998ef` | strict:r4 |
| a-attrib, b-attrib | 250 | `aep-file:sha256:305bc28083e99ae417a18ce35d042e2e2e66d2eaad9f840cbe34bde466a99437` | attrib:r4 |
| c-attrib | 9000 | `aep-file:sha256:3b7f18af3e8d5cc41f40f036282cd15afe49a68d381f1a5b0bdb8c30a24998ef` | attrib:r4 |

The amounts are inside the exact opaque target text under PROFILE's tuple
rule; Core does not parse or weaken that target (Core XML 134–135, 374). The
asserted typed claim remains the same execution pair in every case.

H1 checks actual a/b files in each context, before reasoning from scenario
labels. They are byte-identical and logically equal under set-aware comparison.
Thus all twenty components must be equal (Core XML 581, 745–746).

H2 does **not** assert complete equality of a/c. Exactly `target` and
`evaluation_gap_entries` differ; the latter preserves both the changed target
and changed execution basis reference (Core XML 374, 579). Its token,
context reference, affected typed claim and limitation set are equal. All
remaining eighteen complete components are equal by the per-component
derivation above, including the asserted claim and empty support entries.
The target difference prevents complete Core equivalence; equality of eighteen
components is not target equality (Core XML 745–746). `HYPOTHESES.json` contains
all twenty component expectations for both hypotheses in both contexts.

Across strict and attrib contexts, the same case has a different
`evaluation_context` and a differently scoped `evaluation_gap_entries` value;
the shared downgrade is not equality of the complete appraisal. A changed
context yields a new scoped result (Core XML 783).

## Comparison and freeze

Sets are compared unordered, including qualifier sets and nested reference,
limitation and entry sets; evaluation scope compares as a map. A scoped atom is
an ordered two-element pair, not a set. Exact text is not normalized. Booleans
are distinct from numbers. The checker dispatches by the declared set field
and retains order for nested atom arrays, rather than sorting every array
(Core XML 373–377, 758; PROFILE's logical carrier rules).

The result carrier used by B encodes logical `unavailable` as the JSON string
`"unavailable"`, preserves Boolean false, and encodes empty sets as `[]`.
This choice is recorded in AMBIGUITIES; the Core leaves serialization to a
carrier (Core XML 581, 610). Set order in B's files is for readability only.

`expectations/FREEZE.json` hashes all new B files except itself. Its bytes are
bound by the B Git commit. The freeze manifest's own SHA-256, B's full commit
SHA and timestamp are reported together to the coordinator after committing;
the commit object is authoritative, avoiding a self-referential manifest or
commit identifier. No expectation is to be rewritten in reaction to C; a
revision requires a new expectation version and freeze. A's frozen files are
unchanged.
