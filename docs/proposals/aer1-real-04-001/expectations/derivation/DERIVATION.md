# Derivation record: five AER-1 interop inputs appraised under draft-sergeev-wexp-core-02

Isolated derivation. The expected values follow only from `spec/draft-sergeev-wexp-core-02.txt`
applied to the input values as given, with `profiles.json` as the applied profile catalog,
`REPRESENTATION.md` for the local JSON encoding and `FORMAT-REFERENCE-C01.json` for the result
format. I read `MAPPING.md` as background on where the inputs come from. No expected value depends
on it. In particular, its statements about what the two trust configurations accept are not used,
because Core treats `trust_configuration` as an opaque atom (Q6.1-a, Q6.1-c below).

Results:

- a: accept. Substantive reasons {}. Gaps {P_AER1_ANCHOR_NOT_CHECKED}.
- b: downgrade. Substantive reasons {E_BOUNDARY_NOT_SUPPORTED}. Gaps {P_AER1_ANCHOR_NOT_CHECKED}.
- c: downgrade. Substantive reasons {}. Gaps {E_PROV_NOT_EVALUATED, P_AER1_ANCHOR_NOT_CHECKED}.
- d: downgrade. Substantive reasons {E_IV_NOT_SUPPORTED, P_AER1_RECOMPUTE_COMMITMENT_ONLY}.
  Gaps {P_AER1_ANCHOR_NOT_CHECKED}.
- e: accept. Substantive reasons {}. Gaps {}.

Ambiguities: A1 (Core semantics, affects a, c, d, e; primary kept) and A2 (representation only,
member names of gap entries). Both are in section 9 and in `AMBIGUITIES.json`.

## 0. Conventions

### 0.1 Abbreviations

- M1 = `wexp-work/interop/aer1-real-04-001/mapping-1` (the only applied profile identifier)
- T = `aer1:c17b436d-0d9e-48a1-a5de-08dc80a9767e` (top-level target)
- C = `C-aer1-real-04-001` (evaluation-context identifier)
- bdR = (M1, `real-04.json@sha256:45c6af65806ad125d9ac33da9e13c737d89e1f2efde5c662cd7baa2db3ab51f8`):
  boundary basis reference; also the basis of the profile gap entry in a to d
- exR = (M1, `real-04/canonical_bytes@sha256:c92e4cfdc2a00d2914d6d5c596d0936e6bfdba522a125467a08ef6ebce5974ca`):
  basis of the execution finding; also the basis of the PROV finding in c
- ivR = (M1, `recompute-2026-11-22:sha256(canonical_bytes)=output_hash`): basis of the IV finding in d
- Lu = (M1, `L-aer1-unsigned`); Ln = (M1, `L-aer1-no-anchor`)
- E = (execution, {}); E+P = (execution, {PROV}); E+V = (execution, {IV})
- G-anchor = the input profile gap entry of a to d: token `P_AER1_ANCHOR_NOT_CHECKED`, target T,
  evaluation_context_ref C, affected_claims {E}, basis_refs {bdR}, limitations {}, no
  current_scope_capability

### 0.2 Quotations

Every line of the form `> **label** (section): "..."` is a verbatim quotation of the spec text,
after removing page headers and footers, rejoining words that the text breaks after an existing
hyphen at a line end, and collapsing runs of white space. Quotations from Table 2 (section 13) are
verbatim text of the named row and column, joined across the table's lines in the same way. All
quotations were checked mechanically against `spec/draft-sergeev-wexp-core-02.txt`.

### 0.3 Encoding choices (REPRESENTATION.md, not Core semantics)

- `null` encodes unavailable. REPRESENTATION.md: "Null represents unavailable, not an absent
  component."
- Sets are arrays and their order carries no meaning:

> **Q8.4-order** (8.4): "Set and token ordering in a serialized result is defined by the result carrier. The logical sets produced by Core are order-independent."

  The order I wrote: basis references and limitations of a support entry in premise order
  (boundary, then base finding), as in the C01 format reference (`bd` before `I`); reasons and
  gaps in the order of the 8.4 pseudocode (matrix rows, then finding reasons or profile gaps);
  carried members in input order.
- Evaluation-gap entries use the member names of the input `profile_evaluation_gaps` entries
  (`token`, `target`, `evaluation_context_ref`, `affected_claims`, `basis_refs`, `limitations`),
  because profile entries are copied exactly (Q8.4-copy). The one Core-derived entry (case c) uses
  the same six members and has no `current_scope_capability`, which only a profile gap can supply
  (Q8.5-b). This is ambiguity A2 (representation only).
- Expected files: 1-space indent, sorted keys, ASCII, trailing newline, exactly the twenty members
  of the C01 reference.

## 1. Common ingress analysis (section 6.2, checks 1 to 6)

> **Q1.2-a** (1.2): "A Core invocation begins only after an upstream mapper has produced one complete logical AppraisalInput."

> **Q6.2-pre** (6.2): "Core receives one complete logical AppraisalInput."

All five files parse as JSON without duplicate object members. Each is `{"id", "input"}`; `input`
is the logical record appraised below.

### Check 1

> **Q6.2-1** (6.2): "If the outer value is not an input record, or semantics_version is absent or is not a text atom, Core returns E_MALFORMED_NORMALIZED_INPUT."

All five inputs are records with `semantics_version` = "wexp-core-2", a text atom. Passed by a to e.

### Check 2

> **Q6.2-2** (6.2): "If that readable value is not wexp-core-2, Core returns E_UNSUPPORTED_SEMANTICS_VERSION without applying the version-specific member rules below."

The value is wexp-core-2 in all five. Passed by a to e.

### Check 3 (structural)

> **Q6.2-3** (6.2): "For wexp-core-2, a missing required member, unknown member, wrong logical type, unknown closed-enum value, or malformed set, entry, claim, token, or recorder relation returns E_MALFORMED_NORMALIZED_INPUT."

> **Q6-a** (6): "Every displayed top-level component is REQUIRED. The only semantics version defined by this document is wexp-core-2."

> **Q6.1-b** (6.1): "A basis reference or limitation is a profile-scoped atom logically equivalent to the pair (profile_identifier, local_value)."

> **Q6.1-d** (6.1): "Every collection described as a set, including qualifier, profile-identifier, basis-reference, reason, limitation, fatal-condition, affected-claim, supported-claim, and maximal-claim collections, is an unordered mathematical set. Equal members occur once."

> **Q12-a** (12): "evaluation_scope is an unordered map from capability names to exactly one of evaluated or not-evaluated."

> **Q12-b** (12): "Every initial name MUST appear exactly once."

> **Q15-a** (15): "Tokens begin with an uppercase ASCII letter and contain only uppercase ASCII letters, digits, and underscores. Token comparison is case-sensitive."

What was checked, the same for all five unless a case is named:

- Top level: exactly the thirteen components of the section 6 contract (semantics_version,
  target, asserted_claim, evaluation_context, boundary_finding, base_findings,
  qualifier_findings, recorder_relations, counter_evidence, evaluation_scope,
  profile_evaluation_gaps, inherited_limitations, fatal_conditions). None missing, none unknown.
- evaluation_context: id, evaluated_at, trust_configuration, profile_identifiers {M1}.
- boundary_finding: target, evaluation_context_ref, ceiling_base, status, target_binding,
  grounding, basis_refs, reasons, limitations.
- base_findings: one entry with target, evaluation_context_ref, base, target_binding,
  semantic_validation, basis_refs, reasons, limitations.
- qualifier_findings: empty in a, b and e. One entry in c (PROV) and one in d (IV), each with
  all ten members of the contract.
- profile_evaluation_gaps: one entry in a to d with target, evaluation_context_ref, token,
  affected_claims, basis_refs, limitations. The optional current_scope_capability is absent.
  Empty in e.
- counter_evidence: one entry with status, affected_claims, basis_refs, reasons, limitations.
- Closed enumerations hold only defined members: bases `execution`; qualifiers `PROV` (c) and
  `IV` (d); boundary status `supported` (a, c, d, e) and `unsupported` (b); target_binding
  `supported`; grounding `asserted-only`; semantic_validation `supported`, `not-evaluated`
  (c, PROV) and `unsupported` (d, IV); independence_validation `not-applicable` (c) and
  `supported` (d); counter status `not-supplied`; scope statuses `evaluated` and
  `not-evaluated`.
- Claims are well-formed (base, qualifier set): asserted E (a, b, e), E+P (c), E+V (d); the
  affected claim of G-anchor is E.
- Tokens follow the Q15-a syntax: `P_AER1_ANCHOR_NOT_CHECKED` and
  `P_AER1_RECOMPUTE_COMMITMENT_ONLY`.
- Every basis reference and limitation is a two-element pair of non-empty text atoms whose first
  element is M1. No set contains a repeated member: the two limitations of the execution finding
  in e, Lu and Ln, are distinct.
- evaluation_scope holds the twelve initial names, each exactly once, and no extension key.

Passed by a to e.

### Check 4 (cross-field)

> **Q6.2-4** (6.2): "A well-typed wexp-core-2 input that violates a cross-field invariant returns E_PROFILE_MAPPING_INVALID. Cross-field invariants include aggregate cardinality and keys, exact target and context scope, the counter-evidence sentinel, qualifier combinations, conditional ceiling_base, evaluation-scope consistency and extension-key binding, and profile or registry identity and token category."

**4.1 Aggregate cardinality and keys.**

> **Q6-e** (6): "A normalized input contains exactly one aggregated boundary finding, at most one aggregated base finding for each (target, base, evaluation_context) key, and at most one aggregated qualifier finding for each (target, qualifier, qualified_base, evaluation_context) key."

Each input has one boundary finding and one base finding (execution). c has one qualifier
aggregate (PROV, execution) and d has one (IV, execution). No duplicate keys. Passed by a to e.

**4.2 Exact target and context scope.**

> **Q6-d** (6): "All findings are explicitly scoped. The boundary finding, every base and qualifier aggregate, and every profile-gap entry have a target equal to the top-level target and an evaluation_context_ref equal to the top-level evaluation-context identifier."

Every aggregate and every profile gap entry has target T and evaluation_context_ref C, and C is
evaluation_context.id. Passed by a to e.

**4.3 Counter-evidence sentinel.**

> **Q6-i** (6): "When no counter-evidence was supplied it contains exactly one not-supplied entry with empty affected claims, basis references, reasons, and limitations."

Each input has exactly one entry: status not-supplied, all four sets empty. Passed by a to e.

**4.4 Qualifier combinations.**

> **Q6-g** (6): "A PROV aggregate is valid only when qualified_base = execution and independence_validation = not-applicable. An IV aggregate is valid only when qualified_base is one of the four content bases and independence_validation is supported, unsupported, or not-evaluated."

- c: PROV with qualified_base execution and independence_validation not-applicable. Valid.
- d: IV with qualified_base execution and independence_validation supported. Valid.
- a, b, e: no qualifier aggregate.

Passed by a to e.

**4.5 Conditional ceiling_base and the grounding/status pairing.**

> **Q6-f** (6): "A boundary finding with status = supported MUST contain ceiling_base. Its absence is a profile-mapping failure and produces E_PROFILE_MAPPING_INVALID. A supported boundary has a grounding value of asserted-only, attributed, or attested that the evaluation context accepts. grounding = not-evaluated is valid only with status = not-evaluated; either field paired differently produces E_PROFILE_MAPPING_INVALID. When boundary status is unsupported or not-evaluated, a present ceiling_base is diagnostic carrier metadata only and is ignored by the Core algorithm."

- a, c, d, e: status supported and ceiling_base execution is present. Grounding asserted-only is
  one of the three permitted classes. Neither field is not-evaluated.
- b: status unsupported, so the present ceiling_base (execution) is ignored. Grounding
  asserted-only. Neither field is not-evaluated.

Passed by a to e. One clause, "that the evaluation context accepts", cannot be tested by Core,
because the trust configuration is an opaque atom:

> **Q6.1-a** (6.1): "The target, evaluation-context identifier, evaluation time, and trust configuration are opaque logical atoms."

> **Q6.1-c** (6.1): "Core does not interpret an opaque atom; it only compares, copies, and set-unions it using that equality."

Section 7 places acceptance in the meaning of status = supported, that is, on the profile and the
evaluation context:

> **Q7-e** (7): "boundary_finding.status = supported means that the boundary predicate required by the named evaluation context passed. The evaluation context MUST identify the minimum acceptable grounding."

> **Q7-f** (7): "An asserted-only or attributed finding can be supported only when the evaluation context explicitly accepts that grounding class; the result still reports the weaker grounding and its limitations."

Primary reading: Core takes status = supported as the profile's statement that the context
accepted the grounding, and checks only the not-evaluated pairing, which carries a stated
consequence. Under the alternative, acceptance is a Core-checked invariant that cannot be
established from these inputs, and a, c, d and e are rejected with E_PROFILE_MAPPING_INVALID.
This is ambiguity A1 (section 9).

**4.6 Evaluation-scope consistency (section 12).**

> **Q12-c** (12): "carrier-mapping is evaluated for every complete Core input. A structurally valid input with carrier-mapping = not-evaluated violates this cross-field invariant and produces E_PROFILE_MAPPING_INVALID."

> **Q12-d** (12): "For finding-backed capabilities, evaluated means discovery of applicable material in that declared domain completed and every supplied assessment governed by the capability has a status other than not-evaluated. Absence of an aggregate under that value means the discovery found no candidate for that role. not-evaluated records an applicable unperformed assessment or an unexercised role."

> **Q12-e** (12): "If the asserted claim requires an unevaluated base or qualifier role, its exact aggregate is present; a base or PROV aggregate has a governed not-evaluated field."

> **Q12-g** (12): "For each base-support capability and for provenance-support, if the corresponding aggregate is present and the capability is not-evaluated, at least one governed status field in that aggregate MUST be not-evaluated, independently of whether the role is asserted. A present wholly assessed single-role aggregate paired with not-evaluated violates the cross-field contract and produces E_PROFILE_MAPPING_INVALID. An absent unasserted aggregate can represent an unexercised capability without creating a claim-specific gap."

> **Q12-h** (12): "A claim-required IV aggregate is present when the shared IV capability is not-evaluated, but its passing statuses need not be changed merely because another role was not assessed. Claim-specific gaps are derived from the exact required aggregate, not from the shared summary alone."

> **Q12-i** (12): "The external authenticity and composition capabilities use a fully syntactic rule: their scope value is not-evaluated if and only if at least one profile-gap entry names that capability in current_scope_capability, and is evaluated if and only if no entry names it."

> **Q12-j** (12): "The governed status fields are: every finding's target_binding for target-binding; boundary status, binding, and grounding for boundary-grounding; the corresponding base aggregate's binding and semantic status for each base-support capability; PROV binding and semantic status for provenance-support; IV binding, semantic, and independence status for independent-verification."

> **Q12-k** (12): "A scope value of evaluated with a governed not-evaluated status, a claim-required finding-backed not-evaluated capability without its aggregate, a current-scope marker whose capability is not not-evaluated, or an external capability value without the required marker presence or absence violates the cross-field contract and produces E_PROFILE_MAPPING_INVALID."

> **Q12-f** (12): "The capability value alone MUST NOT create an ingress rejection, substantive finding, or evaluation gap for counter-evidence."

Each capability, for all five inputs unless a case is named:

- carrier-mapping: evaluated (Q12-c holds).
- authenticity: evaluated. No profile gap entry carries current_scope_capability, so the
  syntactic rule (Q12-i) requires evaluated, and it is.
- composition: evaluated. Same rule: no entry names composition.
- target-binding: evaluated. Governed fields are every finding's target_binding: the boundary,
  the execution finding, and the PROV (c) or IV (d) finding. All are supported; none is
  not-evaluated.
- boundary-grounding: evaluated. Governed fields: boundary status (supported, or unsupported in
  b), target_binding (supported) and grounding (asserted-only). None is not-evaluated.
- observation-support, intent-support, invocation-support: not-evaluated, with no aggregate.
  No asserted claim requires these bases, so the Q12-g allowance for "An absent unasserted
  aggregate" applies.
- execution-support: evaluated. The execution aggregate's binding and semantic status are both
  supported.
- provenance-support: not-evaluated.
  - a, b, d, e: no PROV aggregate and PROV is not asserted. Allowed (Q12-g).
  - c: PROV is asserted and its aggregate is present. Its governed semantic status is
    not-evaluated, which satisfies Q12-e and Q12-g. The aggregate is present, so the
    claim-required not-evaluated capability is not "without its aggregate" (Q12-k).
- independent-verification:
  - a, b, c, e: not-evaluated, no IV aggregate, IV not asserted.
  - d: evaluated. The IV aggregate's governed fields are binding supported, semantic unsupported
    and independence supported; none is not-evaluated (Q12-d, Q12-k).
- counter-evidence: evaluated. By Q12-f this value cannot by itself create a rejection, reason
  or gap.

Passed by a to e.

**4.7 Profile or registry identity and token category.**

> **Q6-j** (6): "Likewise, every token in reasons[] on a boundary, base, or qualifier finding MUST be registered in the substantive category and apply to that finding. A non-Core token resolves uniquely through an immutable registry revision identified by an applied profile_identifier."

> **Q6-k** (6): "Every member of fatal_conditions MUST be a token registered in the fatal category by the Core registry or a registry applicable to the mapping profile."

> **Q6-l** (6): "profile_evaluation_gaps carries structured gaps supplied by a mapping or composition profile that are not otherwise recoverable from a Core finding status. Every entry is scoped to the exact target and evaluation context and contains a token registered in the evaluation-gap category, at least one admissible affected claim or all-admissible-claims, basis references, and limitations."

> **Q6-o** (6): "For a structurally valid entry, an empty affected-claim set, an absent, ambiguous, unregistered, or non-evaluation-gap token binding, an incorrect target or evaluation-context scope, a disallowed or mismatched current-scope marker, or an unbound profile-scoped atom produces E_PROFILE_MAPPING_INVALID at the cross-field check."

> **Q15-c** (15): "The current-scope capability column is part of the immutable registration semantics resolved under Section 6. Its value is none for every fatal or substantive token, and for an evaluation-gap token that is not permitted with current_scope_capability."

- Applied profile identifiers: {M1}. M1 is the one profile in the applied catalog
  (`profiles.json`).
- `P_AER1_ANCHOR_NOT_CHECKED` (G-anchor, a to d) resolves uniquely under M1 in the evaluation-gap
  category, with no current-scope capability. G-anchor carries no marker, so there is no marker
  mismatch. Its affected-claim set {E} is non-empty and admissible. Its scope is T and C. Its
  basis bdR is bound to M1. Its limitations set is empty, which Q6-o does not list as a
  failure.
- `P_AER1_RECOMPUTE_COMMITMENT_ONLY` (reasons of the IV finding in d) resolves uniquely under M1
  in the substantive category, the category Q6-j requires. The further Q6-j condition that the
  token "apply to that finding" is a profile fact that Core cannot inspect.
- The boundary and base findings, the PROV finding in c and the counter entry have empty
  reasons. fatal_conditions is empty. recorder_relations is empty.
- Every basis reference and limitation names M1, an applied profile.

Passed by a to e.

### Check 5

> **Q6.2-5** (6.2): "If the structurally usable input has a non-empty valid fatal_conditions set, Core returns that complete set through the fixed rejection projection."

fatal_conditions is empty in all five, so this branch is not taken.

### Check 6

> **Q6.2-6** (6.2): "Otherwise an inadmissible asserted claim returns E_CLAIM_OUT_OF_DOMAIN."

> **Q4.4-a** (4.4): "A typed claim is a pair (base, qualifiers), where base is a content base and qualifiers is a subset of {PROV, IV}. The claim is admissible only if PROV is absent or the base is execution."

E, E+P and E+V are admissible: PROV appears only with execution. Passed by a to e.

### Ingress result

No input fails any ingress check, so no rejection is produced and the fixed rejection projection is
not used, except under the alternative reading of A1. All five go on to sections 8.1 to 8.6.

## 2. Appraisal sentences used in every case

Supported bases:

> **Q8.1-a** (8.1): "Let B be the set of exact supported bases. A base b is in B if and only if all of the following hold:"

> **Q8.1-a1** (8.1): "the unique aggregate base finding for b has supported target binding and supported semantic validation;"

> **Q8.1-a2** (8.1): "the finding names the same target and evaluation context as the appraisal input;"

> **Q8.1-a3** (8.1): "the boundary finding is supported, target-bound, and scoped to that same target and context; and"

> **Q8.1-a4** (8.1): "the accepted Boundary Ceiling is at least b."

> **Q4.2-a** (4.2): "observation < intent < invocation < execution"

> **Q7-g** (7): "The boundary status has deterministic precedence. When status = not-evaluated, no base is added and the appraiser records E_BOUNDARY_NOT_EVALUATED. When status = unsupported, no base is added and it records E_BOUNDARY_NOT_SUPPORTED. Only status = supported with target_binding = supported and matching target and context makes ceiling_base usable."

Qualifiers and the supported set:

> **Q8.1-b1** (8.1): "PROV only when b is execution and a PROV finding for execution has target_binding = supported and semantic_validation = supported for the exact target and evaluation context; and"

> **Q8.1-b2** (8.1): "IV only when an IV finding for b has target_binding = supported, semantic_validation = supported, and independence_validation = supported for the exact target and evaluation context."

> **Q8.1-c** (8.1): "SupportedClaims = { (b, A) | b is in B, A is a subset of Q(b), and (PROV in A implies b == execution) }"

> **Q8.1-d** (8.1): "The procedure evaluates all findings independently of the asserted claim. It does not restrict B or Q(b) to the asserted base or qualifiers."

> **Q8.1-e** (8.1): "MaximalSupportedClaims is the set of members of SupportedClaims that are not structurally dominated by another member under Section 4.5."

> **Q8.3-c** (8.3): "The separate Boolean asserted_claim_supported reports exact membership in SupportedClaims."

Support entries:

> **Q8.1-f** (8.1): "For every member of SupportedClaims, the appraiser also produces a support entry containing the exact claim, the union of basis references used for its base, boundary, and qualifiers, and the limitations attached to those same premises. Limitations from failed or unrelated findings are not attached to that support entry, but remain available as evaluation diagnostics where applicable."

> **Q13-a** (13): "For each member of S, support_entries contains exactly one entry whose basis-reference set is the union of bd, its base finding's basis references, and any qualifier findings' basis references; its limitations are the union of those premises."

Support relations:

> **Q8.3-a** (8.3): "For each maximal supported claim, the appraisal reports a pair {supported_claim, relation}, where relation is one of equal, support-below-claim, support-above-claim, or incomparable. If no claim is supported, the relation array is empty."

> **Q4.5-a** (4.5): "(b1, A1) <= (b2, A2) iff b1 <= b2 and A1 is a subset of A2"

> **Q8.3-b** (8.3): "The support relation compares typed claims structurally."

Boundary members of the result:

> **Q8.5-d** (8.5): "For an accept or downgrade result, boundary_ceiling is the accepted ceiling only when the boundary finding, its target binding, target, and context all pass; otherwise it is unavailable. boundary_grounding preserves the input grounding even when the boundary is unsupported."

> **Q7-c** (7): "An accept or downgrade result MUST preserve the boundary grounding status and its limitations."

Diagnostics (the claim-required matrix):

> **Q8.6-b** (8.6): "The following claim-required matrix is exhaustive for Core-derived non-fatal diagnostics."

> **Q8.6-c** (8.6): "An absent aggregate triggers only its absence row; status rows require that aggregate to be present. A present non-passing aggregate MUST NOT be reported as missing evidence merely because it contributes no supported claim. No catch-all fallback adds E_MISSING_REQUIRED_EVIDENCE or E_EXACT_CLAIM_NOT_SUPPORTED beyond their stated row predicates. A boundary-exceeded row requires a usable boundary and a present asserted-base aggregate whose base is deeper than the ceiling."

> **Q8.6-d** (8.6): "All simultaneously applicable distinct tokens are emitted. No condition outside this matrix creates a Core-derived non-fatal token."

> **Q8.4-matrix** (8.4): "The matrix is exhaustive: Core emits no other status-derived substantive token or Core gap entry."

> **Q8.4-coregap** (8.4): "Every Core-derived finding gap entry has the row's token, the input target and evaluation-context identifier, affected_claims={input.asserted_claim}, and the basis-reference and limitation sets of the aggregate that made the row true."

The rows are quoted where a case evaluates them (sections 3 to 7).

Finding reasons:

> **Q8.4-reasons** (8.4): "for every boundary, base, or qualifier finding that is the asserted role or an exact premise of a SupportEntry: add its registered substantive reasons to reasons"

> **Q8.6-e** (8.6): "A profile can add more specific registered tokens. It MUST NOT suppress a Core-required token. A finding reason is projected only from the boundary when it determines the asserted claim or a reported support entry, from an asserted-base or asserted-qualifier finding, or from a finding that is an exact premise of a reported support entry."

Profile gaps:

> **Q8.4-pgaps** (8.4): "for every profile gap entry whose affected claims include the asserted claim, a member of SupportedClaims, or all-admissible-claims: add that exact entry to GapEntries"

> **Q8.4-copy** (8.4): "Profile gap entries are already validated by the cross-field check and are copied exactly only under the affected-claim predicate shown above."

> **Q6-p** (6): "A valid entry is unrelated to this appraisal and is not projected only when its affected claims include none of the asserted claim, a member of SupportedClaims, or all-admissible-claims."

> **Q8.6-f** (8.6): "Profile-supplied gap entries, including E_COMPOSITION_NOT_EVALUATED, are included only when their affected claims contain the asserted claim, a member of SupportedClaims, or all-admissible-claims. A supplied profile gap does not by itself block acceptance."

> **Q15-b** (15): "The default effect describes the condition that generates the diagnostic, not a verdict computed from token presence alone. The verdict procedure in Section 8.4 is authoritative. In particular, a reason carried by a finding or a profile-supplied evaluation gap can coexist with accept; its presence does not negate a passing exact predicate."

> **Q8.5-b** (8.5): "Each support entry contains claim, basis_refs[], and limitations[]. Each support relation contains supported_claim and relation. Each evaluation-gap entry contains token, target and context scope, affected claims, basis references, limitations, and the optional current_scope_capability supplied on a profile gap; evaluation_gaps is its set-valued token projection."

Counter-evidence. All five carry only the not-supplied sentinel, so no counter entry is
applicable in any case:

> **Q8.2-b** (8.2): "Counter-evidence blocks a claim when at least one entry has status not-evaluated, unresolved-material, or defeating and that entry's affected_claims contains the claim or all-admissible-claims. not-supplied and resolved-no-defeat entries do not block by themselves."

> **Q8.4-ace** (8.4): "applicable_counter_entries returns only entries whose affected claims include the asserted claim or all-admissible-claims and whose status blocks that claim under the same predicate; it preserves per-entry scope."

> **Q8.5-c** (8.5): "counter_evidence preserves every status, affected-claim set, basis-reference set, reason set, and limitation set from the normalized input without cross-claim status or reason collapse."

Inherited limitations:

> **Q8.1-g** (8.1): "The result's inherited_limitations is the set union of the input's inherited limitations; limitations from each counter-evidence or profile-gap entry whose affected claims include the asserted claim, a member of SupportedClaims, or all-admissible-claims; boundary limitations; every support-entry limitation; and limitations attached to findings that determine a reason or gap for the asserted claim. Limitations on unrelated failed findings are excluded."

In the case sections, the five terms of this union are (i) input inherited limitations,
(ii) applicable counter or profile-gap entries, (iii) boundary limitations, (iv) support-entry
limitations, and (v) limitations of findings that determine a reason or gap for the asserted
claim.

Verdict:

> **Q8.2-accept** (8.2): "The asserted claim is an exact member of SupportedClaims and counter-evidence does not block that exact claim."

> **Q8.2-downgrade** (8.2): "The input is safely interpretable and the asserted claim is admissible, but it is not exactly supported, or counter-evidence blocks acceptance."

> **Q8.5-a** (8.5): "Every component shown above is REQUIRED; arrays and sets are empty when they have no members. fatal_reasons is non-empty if and only if the verdict is reject."

Members carried from the input (all five; none rejected):

> **Q13-b** (13): "For accept and downgrade rows, fields not varied by a row equal the common input values and carry through to the output. A reject row instead uses the complete fixed projection in Section 8.4."

> **Q14-b** (14): "An accept or downgrade appraisal carries the evaluation context so that the result is not detached from those dependencies."

So in every case semantics_version, target, asserted_claim, recorder_relations ({}),
counter_evidence (the not-supplied sentinel, by Q8.5-c), evaluation_context and evaluation_scope
are the input values, and fatal_reasons = {}.

## 3. Case a

**Input in one line.** Assert E. Boundary supported, target-bound, scoped to T and C, grounding
asserted-only, ceiling execution, basis {bdR}, limitations {Lu}. Execution finding with binding
and semantic validation supported, basis {exR}, limitations {Lu}, no reasons. No qualifier
findings. Profile gap G-anchor. Counter: not-supplied sentinel. Trust configuration
aer1-real-04-trust-asserted. Scope: observation, intent, invocation, provenance and IV support
not-evaluated; everything else evaluated.

**Sentences relied on.** Section 2 machinery: Q8.1-a to Q8.1-g, Q8.3-a to Q8.3-c, Q4.5-a, Q8.5-d,
Q7-c, Q8.6-b to Q8.6-f, Q8.4-reasons, Q8.4-pgaps, Q8.4-copy, Q6-p, Q15-b, Q8.2-b, Q8.4-ace,
Q8.2-accept, Q13-b. Specific to this case:

> **Q8.6-row-bns** (8.6): "E_BOUNDARY_NOT_SUPPORTED (substantive) Boundary status = unsupported; source: boundary finding."

> **Q8.6-row-bee** (8.6): "E_BASE_EXCEEDS_BOUNDARY (substantive) Usable boundary with asserted base deeper than its ceiling; sources: boundary and asserted-base findings."

> **Q13-C13i** (13, Table 2, C13 input column): "Assert E; execution supported; ceiling execution. A profile gap entry for target T and context C has token E_IV_NOT_EVALUATED, affects E, basis u1, and limitation L-upstream."

> **Q13-C13o** (13, Table 2, C13 output column): "S=M={E}; A=true; relations={E:equal}; accept; gaps={E_IV_NOT_EVALUATED}; fatal/reasons={}; inherited_limitations={L-upstream}. evaluation_gap_entries contains exactly the supplied entry."

C13 is the normative fixture with the same shape as a: a supplied profile gap affecting the
asserted exact claim, with an accept verdict.

**Derivation.**

- B. The execution finding has target T and context C with binding and semantic validation
  supported (Q8.1-a1, Q8.1-a2). The boundary is supported, target-bound and scoped to T and C
  (Q8.1-a3). execution <= ceiling execution (Q8.1-a4, Q4.2-a). So B = {execution}.
- Q(execution) = {}: there is no PROV finding and no IV finding (Q8.1-b1, Q8.1-b2).
- supported_claims = {E} (Q8.1-c). maximal_supported_claims = {E} (Q8.1-e).
- asserted_claim_supported = true: E is in SupportedClaims (Q8.3-c).
- support_entries: one entry for E. basis_refs = boundary basis ∪ base basis = {bdR, exR}.
  limitations = boundary limitations ∪ base limitations = {Lu} ∪ {Lu} = {Lu} (Q8.1-f, Q13-a;
  equal members occur once, Q6.1-d).
- support_relations: E compared with E is equal (Q8.3-a, Q4.5-a).
- boundary_ceiling = execution: the boundary finding, its target binding, target and context all
  pass (Q8.5-d). boundary_grounding = asserted-only, the input value (Q8.5-d, Q7-c).
- Matrix rows. The boundary is not unsupported and not not-evaluated, and its target_binding is
  supported, so no boundary row is true (Q8.6-row-bns and its siblings). The boundary is usable,
  but the asserted base execution is not deeper than the ceiling execution, so
  E_BASE_EXCEEDS_BOUNDARY is false (Q8.6-row-bee). The asserted-base aggregate is present with
  binding and semantic validation supported, so no asserted-base row is true. PROV and IV are
  not asserted, so no PROV or IV row applies. No row is true.
- Finding reasons: the boundary and the execution finding have empty reasons (Q8.4-reasons).
- Profile gaps: G-anchor affects {E}, which contains the asserted claim (and a member of
  SupportedClaims), so it is copied exactly (Q8.4-pgaps, Q8.4-copy, Q6-p).
- Counter: no applicable entry (Q8.2-b, Q8.4-ace).
- substantive_reasons = {}. evaluation_gaps = {P_AER1_ANCHOR_NOT_CHECKED}.
  evaluation_gap_entries = {G-anchor}, copied exactly (Q8.5-b).
- inherited_limitations = {Lu}: (i) {}; (ii) G-anchor's limitations {} (the not-supplied
  counter entry affects no claim); (iii) {Lu}; (iv) {Lu}; (v) no Core row fired, and the only
  gap-determining item is G-anchor, already covered by (ii) (Q8.1-g).
- verdict = accept: E is exactly supported and no counter entry blocks it (Q8.2-accept, Q8.2-b).
  The supplied profile gap does not block acceptance (Q8.6-f, Q15-b), as in C13 (Q13-C13o).
- Asserted-only grounding creates no token: no matrix row tests grounding (Q8.6-d,
  Q8.4-matrix). It is reported through boundary_grounding and the boundary limitations (Q7-f,
  Q7-c).
- Carried members: Q13-b.

**Ambiguity.** A1. The alternative is reject, E_PROFILE_MAPPING_INVALID.

## 4. Case b

**Input in one line.** As a, except boundary status = unsupported (target_binding still
supported, grounding asserted-only, ceiling_base execution present) and trust configuration
aer1-real-04-trust-attributed.

**Sentences relied on.** Section 2 machinery as in a, with Q8.2-downgrade in place of
Q8.2-accept. Specific to this case:

> **Q6-f** (6): "When boundary status is unsupported or not-evaluated, a present ceiling_base is diagnostic carrier metadata only and is ignored by the Core algorithm."

> **Q8.6-row-bns** (8.6): "E_BOUNDARY_NOT_SUPPORTED (substantive) Boundary status = unsupported; source: boundary finding."

> **Q8.6-row-ecns** (8.6): "E_EXACT_CLAIM_NOT_SUPPORTED (substantive) Asserted-base semantic_validation = unsupported; source: asserted-base finding."

> **Q8.6-row-mre** (8.6): "E_MISSING_REQUIRED_EVIDENCE (substantive) Asserted-base aggregate absent; source: none."

**Derivation.**

- B = {}: Q8.1-a3 fails because the boundary is not supported. Q7-g: "When status =
  unsupported, no base is added". The present ceiling_base is ignored (Q6-f).
- supported_claims = {}, maximal_supported_claims = {}, asserted_claim_supported = false
  (Q8.1-c, Q8.1-e, Q8.3-c).
- support_entries = {} (no member of SupportedClaims, Q8.1-f). support_relations = {}: "If no
  claim is supported, the relation array is empty." (Q8.3-a).
- boundary_ceiling = unavailable (null): the boundary finding does not pass (Q8.5-d).
- boundary_grounding = asserted-only: "boundary_grounding preserves the input grounding even when
  the boundary is unsupported." (Q8.5-d).
- Matrix rows:
  - E_BOUNDARY_NOT_SUPPORTED: true; boundary status = unsupported (Q8.6-row-bns, Q7-g).
  - Boundary binding rows: false; boundary target_binding = supported.
  - E_BASE_EXCEEDS_BOUNDARY: false; it requires a usable boundary (Q8.6-c, Q7-g).
  - E_MISSING_REQUIRED_EVIDENCE: false; the asserted-base aggregate is present (Q8.6-row-mre).
  - Asserted-base binding rows: false; binding supported.
  - E_EXACT_CLAIM_NOT_SUPPORTED: false; semantic_validation is supported (Q8.6-row-ecns). The
    text forbids a catch-all: "No catch-all fallback adds E_MISSING_REQUIRED_EVIDENCE or
    E_EXACT_CLAIM_NOT_SUPPORTED beyond their stated row predicates." (Q8.6-c).
  - PROV and IV rows: not asserted, so they do not apply.
- Finding reasons: the boundary determines the asserted claim's reason, so its reasons would be
  projected (Q8.6-e), but they are empty. The execution finding (asserted role) also has empty
  reasons.
- Profile gaps: G-anchor affects {E}, the asserted claim, so it is copied exactly although
  SupportedClaims is empty (Q8.4-pgaps, Q6-p).
- Counter: none.
- substantive_reasons = {E_BOUNDARY_NOT_SUPPORTED}. evaluation_gaps = {P_AER1_ANCHOR_NOT_CHECKED}.
  evaluation_gap_entries = {G-anchor}.
- inherited_limitations = {Lu}. Term (iii) puts boundary limitations into the union with no
  condition attached, and Q7-c separately requires the result to "preserve the boundary
  grounding status and its limitations"; the boundary is not an "unrelated failed finding",
  because it determines E_BOUNDARY_NOT_SUPPORTED. (ii) G-anchor contributes {}. (iv) there are no
  support entries. (v) the boundary again; the execution finding determines no reason or gap.
  Its limitations are also {Lu}, so the value is {Lu} however (v) is read (Q8.1-g).
- verdict = downgrade: E is admissible and the input safely interpretable, but E is not
  exactly supported (Q8.2-downgrade).
- Carried members: Q13-b. evaluation_context carries trust configuration
  aer1-real-04-trust-attributed.

**Ambiguity.** None with a value effect. A1 concerns supported boundaries only. A2 concerns only
member naming.

## 5. Case c

**Input in one line.** As a, but assert E+P, and one PROV(execution) finding with target_binding
supported, semantic_validation not-evaluated, independence_validation not-applicable, basis
{exR}, limitations {Lu}, no reasons. provenance-support = not-evaluated.

**Sentences relied on.** Section 2 machinery, with Q8.2-downgrade. Specific to this case:

> **Q6-h** (6): "A valid qualifier contributes support only when its exact qualified base is independently in B."

> **Q8.6-row-pne** (8.6): "E_PROV_NOT_EVALUATED (gap) Asserted PROV target-binding or semantic assessment not-evaluated; source: PROV finding."

> **Q8.6-row-pns** (8.6): "E_PROV_NOT_SUPPORTED (substantive) Asserted PROV semantic_validation = unsupported; source: PROV finding."

> **Q8.6-row-pmre** (8.6): "E_MISSING_REQUIRED_EVIDENCE (substantive) Asserted PROV aggregate absent; source: none."

> **Q8.6-row-pnb** (8.6): "E_EVIDENCE_NOT_BOUND (substantive) Asserted PROV target_binding = unsupported; source: PROV finding."

> **Q12-l** (12): "An evaluation capability MUST NOT be used as evidence and MUST NOT create or structurally cap a claim. A role-specific Core gap entry is emitted only by the claim-required matrix when its aggregate is required by the asserted claim. A valid profile-gap entry is projected under its affected-claim rule. Otherwise the scope map alone records the unexercised capability and does not become a reason, gap, or substantive finding."

> **Q13-C06o** (13, Table 2, C06 output column): "S={N,N+V,E}; M={N+V,E}; A=false; relations={N+V:support-below-claim,E:support-below-claim}; downgrade; reasons={E_MISSING_REQUIRED_EVIDENCE}; fatal/gaps={}."

C06 shows that E is reported as support-below-claim against a qualified execution assertion
(there E+V).

**Derivation.**

- B = {execution}, as in a.
- Q(execution) = {}: the PROV finding has semantic_validation not-evaluated, not supported, so
  PROV is not added (Q8.1-b1). There is no IV finding (Q8.1-b2).
- supported_claims = {E}; maximal_supported_claims = {E}.
- asserted_claim_supported = false: E+P is not in SupportedClaims (Q8.3-c).
- support_entries: one entry for E with basis_refs {bdR, exR} and limitations {Lu}. The PROV
  finding is not a premise of E, which carries no qualifier (Q8.1-f, Q13-a). (Its basis exR and
  limitation Lu would not change the entry anyway.)
- support_relations: E <= E+P, since execution <= execution and {} is a subset of {PROV}, and
  E ≠ E+P, so the relation is support-below-claim (Q8.3-a, Q4.5-a, Q8.3-b; as for E in C06,
  Q13-C06o).
- boundary_ceiling = execution; boundary_grounding = asserted-only (Q8.5-d).
- Matrix rows:
  - Boundary and asserted-base rows: none true (as in a).
  - E_MISSING_REQUIRED_EVIDENCE (PROV): false; the PROV aggregate is present (Q8.6-row-pmre;
    "A present non-passing aggregate MUST NOT be reported as missing evidence", Q8.6-c).
  - E_EVIDENCE_NOT_BOUND (PROV): false; PROV target_binding is supported (Q8.6-row-pnb).
  - E_PROV_NOT_EVALUATED: true; the asserted PROV semantic assessment is not-evaluated
    (Q8.6-row-pne).
  - E_PROV_NOT_SUPPORTED: false; semantic is not-evaluated, not unsupported (Q8.6-row-pns).
  - IV rows: IV not asserted.
- Core-derived gap entry (Q8.4-coregap): token E_PROV_NOT_EVALUATED, target T,
  evaluation_context_ref C, affected_claims {E+P} (the asserted claim), basis_refs {exR} and
  limitations {Lu}, the sets of the PROV aggregate that made the row true. It has no
  current_scope_capability (Q8.5-b).
- The provenance-support capability value itself adds nothing; only the matrix row does
  (Q12-l, Q12-h last sentence).
- Finding reasons: the boundary and execution finding (premises of the E entry) and the PROV
  finding (asserted role) all have empty reasons (Q8.4-reasons, Q8.6-e).
- Profile gaps: G-anchor affects {E}. That does not contain the asserted claim E+P, but E is a
  member of SupportedClaims, so G-anchor is copied exactly (Q8.4-pgaps, Q6-p, Q8.6-f).
- Counter: none.
- substantive_reasons = {}. evaluation_gaps = {E_PROV_NOT_EVALUATED, P_AER1_ANCHOR_NOT_CHECKED}.
  evaluation_gap_entries = {the Core-derived E_PROV_NOT_EVALUATED entry, G-anchor}. The two
  differ in token, affected claims, basis and limitations, so they stay separate (8.4: "entries
  that differ in any component remain separate").
- inherited_limitations = {Lu}: (i) {}; (ii) G-anchor, applicable through member E, contributes
  {}; (iii) {Lu}; (iv) {Lu}; (v) the PROV finding determines E_PROV_NOT_EVALUATED for the
  asserted claim, so its limitations {Lu} count (Q8.1-g).
- verdict = downgrade: E+P is admissible but not exactly supported (Q8.2-downgrade).
- Carried members: Q13-b.

**Ambiguity.** A1. The alternative is reject. A2 applies to the Core-derived entry's member
names.

## 6. Case d

**Input in one line.** As a, but assert E+V and independent-verification = evaluated, with one
IV(execution) finding: target_binding supported, semantic_validation unsupported,
independence_validation supported, reasons {P_AER1_RECOMPUTE_COMMITMENT_ONLY}, basis {ivR},
limitations {Lu}.

**Sentences relied on.** Section 2 machinery, with Q8.2-downgrade. Specific to this case:

> **Q8.6-row-ivns** (8.6): "E_IV_NOT_SUPPORTED (substantive) Asserted IV semantic_validation = unsupported; source: IV finding."

> **Q8.6-row-ivne** (8.6): "E_IV_NOT_EVALUATED (gap) Asserted IV target-binding, semantic, or independence assessment not-evaluated; source: IV finding."

> **Q8.6-row-ine** (8.6): "E_INDEPENDENCE_NOT_ESTABLISHED (substantive) Asserted IV independence_validation = unsupported; source: IV finding."

> **Q8.6-row-ivmre** (8.6): "E_MISSING_REQUIRED_EVIDENCE (substantive) Asserted IV aggregate absent; source: none."

> **Q8.6-row-ivnb** (8.6): "E_EVIDENCE_NOT_BOUND (substantive) Asserted IV target_binding = unsupported; source: IV finding."

> **Q8.6-e** (8.6): "A finding reason is projected only from the boundary when it determines the asserted claim or a reported support entry, from an asserted-base or asserted-qualifier finding, or from a finding that is an exact premise of a reported support entry."

> **Q15-b** (15): "In particular, a reason carried by a finding or a profile-supplied evaluation gap can coexist with accept; its presence does not negate a passing exact predicate."

**Derivation.**

- B = {execution}, as in a.
- Q(execution) = {}: the IV finding has semantic_validation unsupported, so IV is not added
  (Q8.1-b2). There is no PROV finding (Q8.1-b1).
- supported_claims = {E}; maximal_supported_claims = {E}.
- asserted_claim_supported = false: E+V is not in SupportedClaims.
- support_entries: one entry for E with basis_refs {bdR, exR} and limitations {Lu}. The IV
  finding is not a premise of E, and it is a failed finding, so its basis ivR is not in the
  entry (Q8.1-f).
- support_relations: E <= E+V and E ≠ E+V, so support-below-claim (Q8.3-a, Q4.5-a; as for E in
  C06, Q13-C06o).
- boundary_ceiling = execution; boundary_grounding = asserted-only.
- Matrix rows:
  - Boundary and asserted-base rows: none true.
  - E_MISSING_REQUIRED_EVIDENCE (IV): false; the IV aggregate is present (Q8.6-row-ivmre).
  - E_EVIDENCE_NOT_BOUND (IV): false; binding supported (Q8.6-row-ivnb).
  - E_IV_NOT_EVALUATED: false; no IV assessment is not-evaluated (Q8.6-row-ivne).
  - E_IV_NOT_SUPPORTED: true; semantic_validation = unsupported (Q8.6-row-ivns).
  - E_INDEPENDENCE_NOT_ESTABLISHED: false; independence_validation = supported (Q8.6-row-ine).
  - PROV rows: PROV not asserted.
- Finding reasons: the IV finding is the asserted-qualifier finding, so its registered
  substantive reason P_AER1_RECOMPUTE_COMMITMENT_ONLY is projected (Q8.4-reasons, Q8.6-e). The
  boundary and execution finding have empty reasons.
- Profile gaps: G-anchor affects {E}, a member of SupportedClaims, so it is copied exactly.
- Counter: none.
- substantive_reasons = {E_IV_NOT_SUPPORTED, P_AER1_RECOMPUTE_COMMITMENT_ONLY} ("All
  simultaneously applicable distinct tokens are emitted", Q8.6-d; the profile token adds to the
  Core token and does not replace it, Q8.6-e). evaluation_gaps = {P_AER1_ANCHOR_NOT_CHECKED}.
  evaluation_gap_entries = {G-anchor}.
- inherited_limitations = {Lu}: (iii) {Lu}; (iv) {Lu}; (v) the IV finding determines
  E_IV_NOT_SUPPORTED for the asserted claim, so its limitations {Lu} count; (ii) G-anchor
  contributes {} (Q8.1-g).
- verdict = downgrade: E+V is admissible but not exactly supported (Q8.2-downgrade).
- Carried members: Q13-b. evaluation_scope shows independent-verification = evaluated.

**Ambiguity.** A1. The alternative is reject.

## 7. Case e

**Input in one line.** As a, but with no profile evaluation gap, and the execution finding's
limitations are {Lu, Ln}. The boundary limitations stay {Lu}.

**Sentences relied on.** Section 2 machinery, with Q8.2-accept. Specific to this case:

> **Q13-C12o** (13, Table 2, C12 output column): "S=M={E}; A=true; relations={E:equal}; accept; gaps={}; inherited_limitations={L-boundary}; fatal/reasons={}. The support entry also carries L-boundary. The unexercised IV capability remains visible in evaluation_scope but creates no claim-unrelated gap token."

C12 shows premise limitations carried into the support entry and into inherited_limitations, and
an unexercised capability creating no gap.

**Derivation.**

- B = {execution}; Q(execution) = {}; supported_claims = maximal_supported_claims = {E};
  asserted_claim_supported = true (as in a).
- support_entries: one entry for E. basis_refs {bdR, exR}. limitations = {Lu} ∪ {Lu, Ln} =
  {Lu, Ln} (Q8.1-f, Q13-a).
- support_relations: E is equal.
- boundary_ceiling = execution; boundary_grounding = asserted-only.
- Matrix rows: none true (as in a).
- Finding reasons: none.
- Profile gaps: none supplied. evaluation_gaps = {}; evaluation_gap_entries = {}.
- The not-evaluated capabilities (observation, intent, invocation, provenance and IV support)
  are unexercised roles and create no gap (Q12-l, Q12-g; as in C12, Q13-C12o).
- Counter: none.
- substantive_reasons = {}.
- inherited_limitations = {Lu, Ln}: (iii) {Lu}; (iv) {Lu, Ln}; (i), (ii) and (v) contribute
  nothing (Q8.1-g).
- verdict = accept: E is exactly supported and nothing blocks it (Q8.2-accept). Core emits no
  token for Ln: limitations are carried, not interpreted (Q6.1-c), and the matrix is exhaustive
  (Q8.6-d).
- Carried members: Q13-b.

**Ambiguity.** A1. The alternative is reject.

## 8. Cross-case notes (no effect on the expected values)

- **a against e.** The two encodings of the anchor outcome give the same verdict (accept) and the
  same supported set. They differ only in the gap members (a: G-anchor projected; e: none) and in
  the limitation sets (e adds Ln to the support entry and to inherited_limitations). This
  follows from Q8.6-f and Q15-b (a supplied profile gap does not block) and from Q8.1-f and
  Q8.1-g (premise limitations are carried).
- **The anchor gap without a marker.** G-anchor carries no current_scope_capability. Core
  therefore treats it as follows:

> **Q6-n** (6): "Absence of the marker means that the entry is inherited or otherwise diagnostic and does not determine a current capability status."

  By the syntactic rule (Q12-i), authenticity must then be evaluated, and it is. Core makes no
  judgement about whether checking the anchor belonged to the current appraiser's authenticity
  assessment. If the profile meant it to, the input would need a marker, an authenticity
  registration of the token and authenticity = not-evaluated. That would be a different input;
  under Q8.6-f the verdicts would not change.
- **b.** The fully passing execution finding contributes nothing because the boundary fails, and
  no reason is attached to it (Q8.6-c). E_BOUNDARY_NOT_SUPPORTED is the only substantive reason.
- **d.** The IV finding's basis ivR appears nowhere in the result: the IV finding is not a
  premise of any support entry and no gap entry derives from it. The finding reaches the result
  only through its two reason tokens and through its limitation Lu, which is already present.

## 9. Ambiguities (also in AMBIGUITIES.json)

### A1. Is "the evaluation context accepts" the grounding a Core-checked cross-field invariant?

Affects a, c, d and e: a supported boundary with grounding asserted-only under the opaque trust
configuration `aer1-real-04-trust-asserted`. b is unaffected because its boundary is
unsupported.

The Q6-f sentence "A supported boundary has a grounding value of asserted-only, attributed, or
attested that the evaluation context accepts." stands in the paragraph of boundary cross-field
rules.

**Primary reading (adopted): not Core-checked.**

- Q7-e and Q7-f define acceptance as part of what status = supported means under the named
  evaluation context, which the profile and context must ensure.
- Core treats the trust configuration as an opaque atom it does not interpret (Q6.1-a, Q6.1-c),
  and the applied catalog defines no trust configuration. Core has no material from which to
  evaluate acceptance.
- The sentence states no consequence. The next sentence (the not-evaluated pairing) states one
  explicitly.
- The Q6.2-4 enumeration of cross-field invariants does not name grounding acceptance.

Expected values: those in `out/expected/`.

**Alternative reading.** Acceptance is a cross-field invariant that Core must establish. These
inputs give no Core-visible means to establish it, so check 4 fails, and a, c, d and e are
rejected through the fixed projection with fatal_reasons {E_PROFILE_MAPPING_INVALID}. All
input-derived members are unavailable and all derived sets are empty (8.4 rejected_result,
Q8.5-e below). b is unchanged. If an appraiser instead learned out of band that
`aer1-real-04-trust-asserted` accepts asserted-only grounding, the results equal the primary
ones.

> **Q8.5-e** (8.5): "A reject result uses the fixed projection in Section 8.4. Its semantics_version identifies this result contract; all input-derived appraisal components are unavailable, and all derived support, relation, substantive-reason, and gap sets are empty."

### A2. Representation only: member names of evaluation-gap entries

Q8.5-b fixes the content of an evaluation-gap entry ("token, target and context scope, affected
claims, basis references, limitations, and the optional current_scope_capability supplied on a
profile gap"). REPRESENTATION.md and the C01 reference (whose gap set is empty) fix no member
names.

**Primary.** Use the input `profile_evaluation_gaps` member names for every gap entry: token,
target, evaluation_context_ref, affected_claims, basis_refs, limitations. Profile entries are
copied exactly (Q8.4-copy), and one encoding keeps the set homogeneous.
`current_scope_capability` is omitted where no profile gap supplies it.

**Alternative.** A result carrier names the context-scope member differently (for example
`evaluation_context_id`) for Core-derived entries, or for all entries. The logical value is
unchanged. Only case c has a Core-derived entry; a to d carry G-anchor; e has no gap entries.
