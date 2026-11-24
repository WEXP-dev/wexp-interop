# Derivation of the expected appraisals for fifteen interop inputs (draft-sergeev-wexp-core-02)

Source of every expectation: `spec/draft-sergeev-wexp-core-02.txt` only. Quotes are verbatim, tagged
`(Snn) [section]` for prose and `(Tnn) [13, Table 2, row, column]` for table cells. In a quote, line
breaks are joined with one space, a line ending in a hyphen is joined without a space (the text
breaks lines only at existing hyphens), and page headers and footers are dropped. MAPPING.md was read
as background only; it is never cited as a source of an expected value.

Abbreviations used below:

- PID = `wexp-work/interop/aer1-must-fail-001/mapping-1`, the one applied profile.
- E = the typed claim (execution, {}), encoded `{"base": "execution", "qualifiers": []}`.
- L-u, L-lb, L-na = the limitation atoms (PID, `L-aer1-unsigned`), (PID, `L-aer1-legacy-unbound`),
  (PID, `L-aer1-no-anchor`).
- C = `C-aer1-must-fail-001`, the evaluation-context identifier of every input.
- CTX = the evaluation_context record of every input: evaluated_at `2026-11-23T00:00:00Z`, id C,
  profile_identifiers {PID}, trust_configuration `aer1-must-fail-trust-asserted`.
- SCOPE-STD = carrier-mapping, authenticity, target-binding, boundary-grounding, execution-support,
  composition and counter-evidence evaluated; observation-support, intent-support,
  invocation-support, provenance-support and independent-verification not-evaluated.
- SCOPE-UNV = SCOPE-STD with target-binding, boundary-grounding and execution-support not-evaluated.
- CE-NS = the single counter entry with status not-supplied and empty affected-claim, basis,
  reason and limitation sets.
- bd = the boundary finding's basis set, eb = the execution finding's basis set, Lb = the boundary
  finding's limitation set, Le = the execution finding's limitation set.

---

## 1. Common ingress analysis (Section 6.2, checks 1 to 6), all fifteen inputs

What Core receives:

- (S01) [1.2] "A Core invocation begins only after an upstream mapper has produced one complete logical AppraisalInput."
- (S02) [6.2] "Core receives one complete logical AppraisalInput."

Each file's `input` member is taken as that logical AppraisalInput. All fifteen files were checked as
JSON first: each parses, has no duplicate object member and is ASCII, so nothing fails before the
logical representation (REPRESENTATION.md).

### Check 1

- (S03) [6.2] "If the outer value is not an input record, or semantics_version is absent or is not a text atom, Core returns E_MALFORMED_NORMALIZED_INPUT."

All fifteen: the input is a record and semantics_version is the text atom `wexp-core-2`. Pass.

### Check 2

- (S04) [6.2] "If that readable value is not wexp-core-2, Core returns E_UNSUPPORTED_SEMANTICS_VERSION without applying the version-specific member rules below."

All fifteen carry `wexp-core-2`. Pass.

### Check 3 (structure)

- (S05) [6.2] "For wexp-core-2, a missing required member, unknown member, wrong logical type, unknown closed-enum value, or malformed set, entry, claim, token, or recorder relation returns E_MALFORMED_NORMALIZED_INPUT."
- (S06) [6] "Every displayed top-level component is REQUIRED."
- (S07) [6.1] "Equal members occur once."
- (S08) [15] "Tokens begin with an uppercase ASCII letter and contain only uppercase ASCII letters, digits, and underscores."

Findings, the same for all fifteen inputs:

- Top level: exactly the thirteen members of the Section 6 contract (semantics_version, target,
  asserted_claim, evaluation_context, boundary_finding, base_findings, qualifier_findings,
  recorder_relations, counter_evidence, evaluation_scope, profile_evaluation_gaps,
  inherited_limitations, fatal_conditions); none missing, none unknown.
- evaluation_context: id, evaluated_at, trust_configuration (text atoms) and profile_identifiers
  (a one-member set of text).
- boundary_finding: exactly target, evaluation_context_ref, ceiling_base, status, target_binding,
  grounding, basis_refs, reasons, limitations. Enum values used: status supported; target_binding
  supported, unsupported or not-evaluated; grounding asserted-only; ceiling_base execution. All are
  members of the closed enumerations of Section 6.
- base_findings: one entry with exactly target, evaluation_context_ref, base (execution),
  target_binding, semantic_validation, basis_refs, reasons, limitations; enum values within
  {supported, unsupported, not-evaluated}.
- qualifier_findings, recorder_relations, inherited_limitations: empty sets.
- asserted_claim: the well-formed claim E (recognized base, qualifier set empty).
- counter_evidence entries: exactly status, affected_claims, basis_refs, reasons, limitations, with
  status not-supplied or (anchor-verification-failed) unresolved-material.
- profile_evaluation_gaps entries (anchor-not-checked, anchor-unresolvable): exactly target,
  evaluation_context_ref, token, affected_claims, basis_refs, limitations; the optional
  current_scope_capability is absent.
- evaluation_scope: twelve entries of capability and status, statuses evaluated or not-evaluated,
  no extension keys.
- Every basis reference and limitation is a two-element pair of non-empty text whose first member is
  PID; no set repeats a member (S07).
- Tokens P_AER1_ANCHOR_NOT_CHECKED, P_AER1_ANCHOR_UNRESOLVABLE, P_AER1_ANCHOR_DIGEST_MISMATCH,
  E_INTEGRITY_INVALID and E_BINDING_MISMATCH all satisfy S08.

All fifteen pass check 3.

### Check 4 (cross-field invariants)

- (S09) [6.2] "A well-typed wexp-core-2 input that violates a cross-field invariant returns E_PROFILE_MAPPING_INVALID."
- (S10) [6.2] "Cross-field invariants include aggregate cardinality and keys, exact target and context scope, the counter-evidence sentinel, qualifier combinations, conditional ceiling_base, evaluation-scope consistency and extension-key binding, and profile or registry identity and token category."

Each invariant in turn:

Aggregate cardinality and keys.

- (S11) [6] "A normalized input contains exactly one aggregated boundary finding, at most one aggregated base finding for each (target, base, evaluation_context) key, and at most one aggregated qualifier finding for each (target, qualifier, qualified_base, evaluation_context) key."

All fifteen: one boundary finding, one execution base finding, no qualifier finding. Pass.

Exact target and context scope.

- (S12) [6] "The boundary finding, every base and qualifier aggregate, and every profile-gap entry have a target equal to the top-level target and an evaluation_context_ref equal to the top-level evaluation-context identifier."

Every boundary finding, base finding and profile-gap entry carries the input's own target and
evaluation_context_ref C. This holds also in id-resolution-disagreement, whose top-level target is
the donor id `aer1:42fc3298-b1e7-4087-bb1c-f80ef9f12c7c` and whose findings name that same target. Pass.

Counter-evidence sentinel.

- (S13) [6] "When no counter-evidence was supplied it contains exactly one not-supplied entry with empty affected claims, basis references, reasons, and limitations."
- (S14) [6] "Otherwise not-supplied is absent and every entry names at least one admissible affected claim or all-admissible-claims."

Fourteen inputs carry exactly CE-NS. anchor-verification-failed carries one unresolved-material
entry naming E (admissible) and no not-supplied entry. Pass.

Qualifier combinations: no qualifier findings. Pass.

Conditional ceiling_base and boundary pairing.

- (S15) [6] "A boundary finding with status = supported MUST contain ceiling_base."
- (S16) [6] "grounding = not-evaluated is valid only with status = not-evaluated; either field paired differently produces E_PROFILE_MAPPING_INVALID."

All fifteen: status supported with ceiling_base execution present, grounding asserted-only (not
not-evaluated). Pass. (Whether Core must itself confirm that the evaluation context accepts
asserted-only grounding is discussed in Section 5, X1: it does not.)

Evaluation-scope consistency.

- (S17) [12] "Every initial name MUST appear exactly once."
- (S18) [12] "A structurally valid input with carrier-mapping = not-evaluated violates this cross-field invariant and produces E_PROFILE_MAPPING_INVALID."
- (S19) [12] "The governed status fields are: every finding's target_binding for target-binding; boundary status, binding, and grounding for boundary-grounding; the corresponding base aggregate's binding and semantic status for each base-support capability; PROV binding and semantic status for provenance-support; IV binding, semantic, and independence status for independent-verification."
- (S20) [12] "A scope value of evaluated with a governed not-evaluated status, a claim-required finding-backed not-evaluated capability without its aggregate, a current-scope marker whose capability is not not-evaluated, or an external capability value without the required marker presence or absence violates the cross-field contract and produces E_PROFILE_MAPPING_INVALID."
- (S21) [12] "For each base-support capability and for provenance-support, if the corresponding aggregate is present and the capability is not-evaluated, at least one governed status field in that aggregate MUST be not-evaluated, independently of whether the role is asserted."
- (S22) [12] "An absent unasserted aggregate can represent an unexercised capability without creating a claim-specific gap."
- (S23) [12] "The external authenticity and composition capabilities use a fully syntactic rule: their scope value is not-evaluated if and only if at least one profile-gap entry names that capability in current_scope_capability, and is evaluated if and only if no entry names it."
- (S24) [12] "If the asserted claim requires an unevaluated base or qualifier role, its exact aggregate is present; a base or PROV aggregate has a governed not-evaluated field."
- (S25) [12] "not-evaluated records an applicable unperformed assessment or an unexercised role."

The fourteen inputs with SCOPE-STD (all except id-alone-unverified):

- All twelve initial names appear once; carrier-mapping is evaluated (S17, S18).
- target-binding evaluated: the governed fields are the boundary and execution target_binding
  values, which are supported (or unsupported in id-expected-mismatch and id-resolution-disagreement);
  none is not-evaluated (S19, S20).
- boundary-grounding evaluated: boundary status supported, binding supported or unsupported,
  grounding asserted-only; none not-evaluated.
- execution-support evaluated: the execution aggregate's binding and semantic status are supported
  or unsupported (unsupported semantic status in the three integrity inputs); none not-evaluated.
- observation-, intent-, invocation-, provenance-support and independent-verification
  not-evaluated: their aggregates are absent and the asserted claim E requires none of those roles
  (S22, S24); S21 binds only present aggregates.
- authenticity and composition evaluated, and no profile-gap entry carries current_scope_capability
  (S23).
- counter-evidence evaluated; by S26 the capability value alone has no ingress effect.

- (S26) [12] "The capability value alone MUST NOT create an ingress rejection, substantive finding, or evaluation gap for counter-evidence."

id-alone-unverified (SCOPE-UNV), the input whose scope differs:

- Boundary target_binding = not-evaluated is governed by target-binding and by boundary-grounding
  (S19); both are not-evaluated, so S20's "evaluated with a governed not-evaluated status" does not
  occur.
- Execution target_binding = not-evaluated is governed by target-binding and by execution-support
  (S19); both are not-evaluated.
- execution-support is not-evaluated with its aggregate present, and that aggregate has a governed
  not-evaluated field (target_binding), as S21 and S24 require. The aggregate is present, so S20's
  "claim-required finding-backed not-evaluated capability without its aggregate" does not occur.
- boundary-grounding not-evaluated with status supported and grounding asserted-only is consistent
  with S25 (one governed assessment, the binding, was not performed); no sentence requires every
  governed field to be not-evaluated.
- Every capability still marked evaluated (carrier-mapping, authenticity, composition,
  counter-evidence) has no governed not-evaluated field.

All fifteen pass the scope invariants.

Profile or registry identity and token category.

- (S27) [6] "A non-Core token resolves uniquely, including category, through exactly one immutable registry revision identified by an applied profile_identifier; absence, ambiguity, or category disagreement produces E_PROFILE_MAPPING_INVALID."
- (S28) [6] "Every member of a counter entry's reasons set MUST be a token registered in the substantive category by a registry applicable to the mapping profile and MUST apply to that entry's affected claims."
- (S29) [6] "Every entry is scoped to the exact target and evaluation context and contains a token registered in the evaluation-gap category, at least one admissible affected claim or all-admissible-claims, basis references, and limitations."
- (S30) [6] "Absence of the marker means that the entry is inherited or otherwise diagnostic and does not determine a current capability status."
- (S31) [6] "Every member of fatal_conditions MUST be a token registered in the fatal category by the Core registry or a registry applicable to the mapping profile."
- (S32) [6.2] "The Core-defined supplied fatal members are E_UNKNOWN_CRITICAL_SEMANTIC, E_INTEGRITY_INVALID, E_BINDING_MISMATCH, and E_CHAIN_DESCRIPTION_INVALID."
- (S33) [6.2] "If any supplied member is appraiser-derived, unbound, ambiguous, or in the wrong category, the cross-field check returns only E_PROFILE_MAPPING_INVALID."
- (S34) [6.1] "A basis reference or limitation is a profile-scoped atom logically equivalent to the pair (profile_identifier, local_value)."

Applied to the inputs, with the catalog of `profiles.json` (one profile, PID, listed in every
input's profile_identifiers):

- P_AER1_ANCHOR_DIGEST_MISMATCH (counter reason in anchor-verification-failed) resolves uniquely
  through PID to the substantive category (S27, S28).
- P_AER1_ANCHOR_NOT_CHECKED and P_AER1_ANCHOR_UNRESOLVABLE (profile gaps) resolve uniquely through
  PID to the evaluation-gap category with no current-scope capability; the entries carry no marker,
  so there is no marker-token mismatch (S29, S30). Each names one admissible affected claim (E) and
  the input's target and context.
- E_INTEGRITY_INVALID and E_BINDING_MISMATCH are Core-defined supplied fatal members (S31, S32);
  neither is appraiser-derived (S33).
- Every basis reference and limitation is bound to PID, an applied profile (S34).
- Every finding's reasons set is empty, so the finding-reason registration rule has nothing to check.

All fifteen pass check 4.

### Check 5 (supplied fatal conditions)

- (S35) [6.2] "If the structurally usable input has a non-empty valid fatal_conditions set, Core returns that complete set through the fixed rejection projection."

Five inputs carry a non-empty valid set and fail check 5:

- hash-mismatch: {E_INTEGRITY_INVALID}
- input-hash-key-order-20: {E_INTEGRITY_INVALID}
- input-hash-mismatch: {E_INTEGRITY_INVALID}
- tampered-provenance: {E_BINDING_MISMATCH}
- version-downgrade: {E_BINDING_MISMATCH}

Their rejection is derived in Section 2. The other ten have empty fatal_conditions.

### Check 6 (admissibility)

- (S36) [6.2] "Otherwise an inadmissible asserted claim returns E_CLAIM_OUT_OF_DOMAIN."
- (S37) [4.4] "The claim is admissible only if PROV is absent or the base is execution."

The ten remaining inputs assert E, which has no PROV: admissible. Pass. These ten go on to the
appraisal procedure (Section 3).

Summary of ingress: no input fails checks 1 to 4 or check 6; five fail check 5; ten are appraised.

---

## 2. The rejection projection (the five inputs that fail check 5)

- (S38) [6.2] "No later check or diagnostic is added after any earlier rejection branch wins."
- (S39) [6.2] "The fixed projection in Section 8.4 is the only Core result for every rejection branch."
- (S40) [8.4] "if input.fatal_conditions is not empty: return rejected_result(input.fatal_conditions)"
- (S41) [8.4] "rejected_result(fatal_tokens): return Appraisal with verdict = reject, semantics_version = "wexp-core-2", fatal_reasons = fatal_tokens, substantive_reasons = {}, evaluation_gaps = {}, evaluation_gap_entries = {}, supported_claims = {}, maximal_supported_claims = {}, support_entries = {}, support_relations = {}, asserted_claim_supported = false, boundary_ceiling = unavailable, boundary_grounding = unavailable, target = unavailable, asserted_claim = unavailable, recorder_relations = unavailable, counter_evidence = unavailable, inherited_limitations = unavailable, evaluation_context = unavailable, evaluation_scope = unavailable"
- (S42) [8.5] "fatal_reasons is non-empty if and only if the verdict is reject."
- (S43) [8.5] "Its semantics_version identifies this result contract; all input-derived appraisal components are unavailable, and all derived support, relation, substantive-reason, and gap sets are empty."
- (S44) [8.4] "All twenty result components are present even in the fixed rejection projection."
- (S45) [8.4] "The logical value unavailable is distinct from an omitted component; its encoding is defined by a result carrier."
- (S46) [6.2] "A supplied E_INTEGRITY_INVALID means that an integrity or authentication failure affecting normalized interpretation was identified while enough structurally usable logical input remains to report that Core condition."
- (S47) [6.2] "A supplied E_BINDING_MISMATCH means protected fields or mandatory mapping bindings are internally contradictory while the same minimum remains available."
- (T01) [13, Table 2, row C09, right column] "reject; semantics_version=wexp-core-2; fatal={E_CLAIM_OUT_OF_DOMAIN}; S=M={}; A=false; support entries/relations/reasons/gaps={}; target/asserted claim/boundary ceiling/ boundary grounding/recorder relations/ counter evidence/inherited limitations/ evaluation context/evaluation scope=unavailable."

Derivation (all twenty members, from S41; unavailable is encoded `null` per REPRESENTATION.md, empty
sets as `[]`):

- semantics_version: "wexp-core-2"
- verdict: reject
- fatal_reasons: the complete supplied set (S35, S41)
- substantive_reasons, evaluation_gaps, evaluation_gap_entries, supported_claims,
  maximal_supported_claims, support_entries, support_relations: []
- asserted_claim_supported: false
- boundary_ceiling, boundary_grounding, target, asserted_claim, recorder_relations,
  counter_evidence, inherited_limitations, evaluation_context, evaluation_scope: null

The finding statuses in these inputs (for example the unsupported execution semantic status in the
three integrity inputs) are not consulted: S38. The five results are identical except for
fatal_reasons, because every input-derived member is unavailable and every derived set is empty
(S43).

---

## 3. Appraisal of the ten admitted inputs

### 3.1 Members carried through in every accept or downgrade

- (S48) [13] "For accept and downgrade rows, fields not varied by a row equal the common input values and carry through to the output."
- (S49) [8.5] "counter_evidence preserves every status, affected-claim set, basis-reference set, reason set, and limitation set from the normalized input without cross-claim status or reason collapse."
- (S50) [8.5] "boundary_grounding preserves the input grounding even when the boundary is unsupported."
- (S51) [7] "An accept or downgrade result MUST preserve the boundary grounding status and its limitations."
- (S52) [14] "An accept or downgrade appraisal carries the evaluation context so that the result is not detached from those dependencies."
- (S53) [6.1] "Recorder relations are descriptive carried facts."
- (S54) [12] "evaluation_scope is an unordered map from capability names to exactly one of evaluated or not-evaluated."
- (T02) [13, Table 2, row C12, right column] "The unexercised IV capability remains visible in evaluation_scope but creates no claim-unrelated gap token."
- (S55) [8.5] "Every component shown above is REQUIRED; arrays and sets are empty when they have no members."
- (S56) [8.5] "fatal_reasons is non-empty if and only if the verdict is reject."

S56 is the sentence of S42, quoted again here for the non-reject direction.

Hence, in all ten: semantics_version "wexp-core-2"; target, asserted_claim (E), evaluation_context
(CTX), evaluation_scope, counter_evidence and recorder_relations (empty) equal the input values;
boundary_grounding "asserted-only"; fatal_reasons [] (S56).

### 3.2 Template A: bound, supported, nothing else applies

Applies to anchor-absent, anchor-resolves, id-expected-match, id-resolution-agreement, and is the
base of Templates B and C. Input shape: boundary status supported, target_binding supported, the
input's target and context, ceiling execution; execution finding target_binding supported and
semantic_validation supported; no qualifier findings; CE-NS; no profile gaps.

Supported bases:

- (S57) [8.1] "Let B be the set of exact supported bases."
- (S58) [8.1] "A base b is in B if and only if all of the following hold:"
- (S59) [8.1] "the unique aggregate base finding for b has supported target binding and supported semantic validation;"
- (S60) [8.1] "the finding names the same target and evaluation context as the appraisal input;"
- (S61) [8.1] "the boundary finding is supported, target-bound, and scoped to that same target and context; and"
- (S62) [8.1] "the accepted Boundary Ceiling is at least b."
- (S63) [4.2] "observation < intent < invocation < execution"

All four conditions hold for execution (the ceiling execution is at least execution), so
B = {execution}.

Qualifiers:

- (S64) [8.1] "PROV only when b is execution and a PROV finding for execution has target_binding = supported and semantic_validation = supported for the exact target and evaluation context; and"
- (S65) [8.1] "IV only when an IV finding for b has target_binding = supported, semantic_validation = supported, and independence_validation = supported for the exact target and evaluation context."

There is no PROV or IV finding, so Q(execution) = {}.

Supported and maximal claims, exact membership:

- (S66) [8.1] "SupportedClaims = { (b, A) | b is in B, A is a subset of Q(b), and (PROV in A implies b == execution) }"
- (S67) [8.1] "MaximalSupportedClaims is the set of members of SupportedClaims that are not structurally dominated by another member under Section 4.5."
- (S68) [8.3] "The separate Boolean asserted_claim_supported reports exact membership in SupportedClaims."

supported_claims = [E]; maximal_supported_claims = [E] (one member, undominated);
asserted_claim_supported = true.

Support entry:

- (S69) [8.1] "For every member of SupportedClaims, the appraiser also produces a support entry containing the exact claim, the union of basis references used for its base, boundary, and qualifiers, and the limitations attached to those same premises."
- (S70) [13] "For each member of S, support_entries contains exactly one entry whose basis-reference set is the union of bd, its base finding's basis references, and any qualifier findings' basis references; its limitations are the union of those premises."
- (S71) [8.5] "Each support entry contains claim, basis_refs[], and limitations[]."

support_entries = [{claim E, basis_refs bd union eb, limitations Lb union Le}].

Support relation:

- (S72) [8.3] "For each maximal supported claim, the appraisal reports a pair {supported_claim, relation}, where relation is one of equal, support-below-claim, support-above-claim, or incomparable."
- (S73) [4.5] "(b1, A1) <= (b2, A2) iff b1 <= b2 and A1 is a subset of A2"

The one maximal claim E compared with the asserted E holds in both directions: relation equal.
support_relations = [{supported_claim E, relation equal}].

Boundary ceiling:

- (S74) [8.5] "For an accept or downgrade result, boundary_ceiling is the accepted ceiling only when the boundary finding, its target binding, target, and context all pass; otherwise it is unavailable."
- (S75) [7] "Only status = supported with target_binding = supported and matching target and context makes ceiling_base usable."

All four pass: boundary_ceiling = "execution".

Diagnostics:

- (S76) [8.6] "The following claim-required matrix is exhaustive for Core-derived non-fatal diagnostics."
- (S77) [8.6] "An absent aggregate triggers only its absence row; status rows require that aggregate to be present."
- (S78) [8.6] "All simultaneously applicable distinct tokens are emitted."
- (S79) [8.6] "No condition outside this matrix creates a Core-derived non-fatal token."

The finding and boundary rows, evaluated for every template:

- (R1) [8.6] "E_BOUNDARY_NOT_SUPPORTED (substantive) Boundary status = unsupported; source: boundary finding."
- (R2) [8.6] "E_BOUNDARY_NOT_EVALUATED (gap) Boundary status = not-evaluated; source: boundary finding."
- (R3) [8.6] "E_EVIDENCE_NOT_BOUND (substantive) Boundary target_binding = unsupported; source: boundary finding."
- (R4) [8.6] "E_BOUNDARY_NOT_EVALUATED (gap) Boundary target_binding = not-evaluated; source: boundary finding."
- (R5) [8.6] "E_BASE_EXCEEDS_BOUNDARY (substantive) Usable boundary with asserted base deeper than its ceiling; sources: boundary and asserted-base findings."
- (R6) [8.6] "E_MISSING_REQUIRED_EVIDENCE (substantive) Asserted-base aggregate absent; source: none."
- (R7) [8.6] "E_EVIDENCE_NOT_BOUND (substantive) Asserted-base target_binding = unsupported; source: asserted-base finding."
- (R8) [8.6] "E_BASE_NOT_EVALUATED (gap) Asserted-base target_binding = not-evaluated; source: asserted-base finding."
- (R9) [8.6] "E_EXACT_CLAIM_NOT_SUPPORTED (substantive) Asserted-base semantic_validation = unsupported; source: asserted-base finding."
- (R10) [8.6] "E_BASE_NOT_EVALUATED (gap) Asserted-base semantic_validation = not-evaluated; source: asserted-base finding."
- (R11) [8.6] "E_MISSING_REQUIRED_EVIDENCE (substantive) Asserted PROV aggregate absent; source: none."
- (R12) [8.6] "E_MISSING_REQUIRED_EVIDENCE (substantive) Asserted IV aggregate absent; source: none."

The PROV rows (R11 and the three after it in the matrix) and the IV rows (R12 and the four after
it) concern the asserted PROV or IV role. E asserts neither qualifier, so no PROV or IV row is applicable in any
of the ten inputs.

For Template A: status supported (R1, R2 false); binding supported (R3, R4 false); execution is not
deeper than the ceiling execution (R5 false); the asserted-base aggregate is present (R6 false); its
binding and semantic status are supported (R7 to R10 false). No row is true.

Finding reasons:

- (S80) [8.4] "for every boundary, base, or qualifier finding that is the asserted role or an exact premise of a SupportEntry: add its registered substantive reasons to reasons"

Every finding's reasons set is empty in all ten inputs: nothing is added in any template.

Counter-evidence:

- (S81) [8.2] "Counter-evidence blocks a claim when at least one entry has status not-evaluated, unresolved-material, or defeating and that entry's affected_claims contains the claim or all-admissible-claims."
- (S82) [8.2] "not-supplied and resolved-no-defeat entries do not block by themselves."

CE-NS does not block and is not an applicable blocking entry. Hence substantive_reasons = [],
evaluation_gap_entries = [], evaluation_gaps = [].

Verdict:

- (S83) [8.4] "if asserted_claim_supported and not counter_blocks( input.counter_evidence, input.asserted_claim): verdict = accept else: verdict = downgrade"
- (S84) [8.2] "accept The asserted claim is an exact member of SupportedClaims and counter-evidence does not block that exact claim."

asserted_claim_supported is true and nothing blocks E: verdict accept.

Inherited limitations:

- (S85) [8.1] "The result's inherited_limitations is the set union of the input's inherited limitations; limitations from each counter-evidence or profile-gap entry whose affected claims include the asserted claim, a member of SupportedClaims, or all-admissible-claims; boundary limitations; every support-entry limitation; and limitations attached to findings that determine a reason or gap for the asserted claim."
- (S86) [8.1] "Limitations on unrelated failed findings are excluded."

Input inherited limitations: {}. CE-NS names no affected claim (and has no limitations). Boundary
limitations: Lb. Support-entry limitations: Lb union Le. No finding determines a reason or gap.
inherited_limitations = Lb union Le.

### 3.3 Template B: Template A plus one profile-gap entry affecting E

Applies to anchor-not-checked and anchor-unresolvable. Everything in Template A holds unchanged
(the gap entry is not a finding and does not touch B, Q, the matrix rows or counter-evidence). In
addition:

- (S87) [8.4] "for every profile gap entry whose affected claims include the asserted claim, a member of SupportedClaims, or all-admissible-claims: add that exact entry to GapEntries"
- (S88) [8.4] "Profile gap entries are already validated by the cross-field check and are copied exactly only under the affected-claim predicate shown above."
- (S89) [6] "A valid entry is unrelated to this appraisal and is not projected only when its affected claims include none of the asserted claim, a member of SupportedClaims, or all-admissible-claims."
- (S90) [8.4] "gaps = token projection of GapEntries"
- (S91) [8.5] "Each evaluation-gap entry contains token, target and context scope, affected claims, basis references, limitations, and the optional current_scope_capability supplied on a profile gap; evaluation_gaps is its set-valued token projection."
- (S92) [8.6] "A supplied profile gap does not by itself block acceptance."
- (S93) [15] "In particular, a reason carried by a finding or a profile-supplied evaluation gap can coexist with accept; its presence does not negate a passing exact predicate."
- (T03) [13, Table 2, row C13, left column] "Assert E; execution supported; ceiling execution. A profile gap entry for target T and context C has token E_IV_NOT_EVALUATED, affects E, basis u1, and limitation L-upstream."
- (T04) [13, Table 2, row C13, right column] "S=M={E}; A=true; relations={E:equal}; accept; gaps={E_IV_NOT_EVALUATED}; fatal/reasons={}; inherited_limitations={L-upstream}. evaluation_gap_entries contains exactly the supplied entry."

The entry's affected claims {E} include the asserted claim (and a member of SupportedClaims), so
evaluation_gap_entries = [the supplied entry, copied exactly] and evaluation_gaps = [its token].
The verdict stays accept (S92, S93; the C13 pattern T03/T04). inherited_limitations adds the entry's
limitations under S85; they are empty here, so inherited_limitations = Lb union Le as in Template A.

### 3.4 Template C: Template A plus one blocking counter entry affecting E

Applies to anchor-verification-failed. B, Q, SupportedClaims, the support entry, the relation, the
ceiling and the finding rows are as in Template A. In addition:

- (S94) [8.4] "reasons = reasons union c.reasons"
- (S95) [8.4] "if c.status == unresolved-material: add E_COUNTER_EVIDENCE_UNRESOLVED to reasons"
- (R13) [8.6] "E_COUNTER_EVIDENCE_UNRESOLVED (substantive) Applicable counter entry status = unresolved-material; source: that counter entry."
- (S96) [8.6] "For every blocking counter-evidence entry applicable to the asserted claim, the appraiser MUST add every token in that entry's reasons set to substantive_reasons, in addition to the Core token determined by the entry status."
- (S97) [8.2] "downgrade The input is safely interpretable and the asserted claim is admissible, but it is not exactly supported, or counter-evidence blocks acceptance."
- (S98) [8.2] "In the latter case asserted_claim_supported remains true."
- (S99) [8.3] "The support relation compares typed claims structurally."
- (T05) [13, Table 2, row C15, left column] "Assert E; execution supported; ceiling execution. One counter entry has status unresolved-material, affects E, has reason P_COUNTER_FAIL, basis p1, and no limitations."
- (T06) [13, Table 2, row C15, right column] "S=M={E}; A=true; relations={E:equal}; downgrade; reasons={E_COUNTER_EVIDENCE_UNRESOLVED, P_COUNTER_FAIL}; gaps={}; fatal={}. The copied counter entry retains its scoped reason."

The entry has status unresolved-material and affected claims {E}: it blocks E (S81) and is
applicable. substantive_reasons = {E_COUNTER_EVIDENCE_UNRESOLVED} union the entry's reasons. No gap
arises (the not-evaluated counter row is not triggered). The verdict is downgrade (S83, S97) while
asserted_claim_supported stays true (S98) and the relation stays equal (S99). counter_evidence
carries the entry unchanged (S49). The entry's limitations enter inherited_limitations (S85); they are
empty, so inherited_limitations = Lb union Le. This is the C15 pattern (T05/T06).

### 3.5 Template D: failed target binding on boundary and execution finding

Applies to id-expected-mismatch and id-resolution-disagreement. Input shape: boundary status
supported, target_binding unsupported; execution finding target_binding unsupported,
semantic_validation supported; everything else as Template A.

- (S100) [7] "A failed target binding prevents use of the ceiling and adds the Core substantive reason E_EVIDENCE_NOT_BOUND; an unevaluated target binding prevents use of the ceiling and adds the Core gap E_BOUNDARY_NOT_EVALUATED, as specified by Section 8.6."
- (S101) [6.2] "Ordinary negative or unevaluated exact-target binding is represented by a correctly scoped aggregate and is non-fatal."
- (S102) [8.3] "If no claim is supported, the relation array is empty."
- (S103) [8.6] "A boundary-exceeded row requires a usable boundary and a present asserted-base aggregate whose base is deeper than the ceiling."
- (S104) [8.6] "A present non-passing aggregate MUST NOT be reported as missing evidence merely because it contributes no supported claim."
- (S105) [8.6] "No catch-all fallback adds E_MISSING_REQUIRED_EVIDENCE or E_EXACT_CLAIM_NOT_SUPPORTED beyond their stated row predicates."
- (S106) [8.4] "Substantive reason tokens are a set, so simultaneous causes of the same token produce one token without suppressing any distinct token."

Derivation:

- B: S59 fails (execution binding unsupported) and S61 fails (boundary not target-bound): B = {}.
- supported_claims = [], maximal_supported_claims = [], support_entries = [],
  asserted_claim_supported = false, support_relations = [] (S102).
- boundary_ceiling: the target binding does not pass, so null (unavailable) (S74, S75, S100).
- Rows: R3 true (boundary binding unsupported) and R7 true (asserted-base binding unsupported),
  both E_EVIDENCE_NOT_BOUND, one token (S106). R1, R2, R4 false (status supported, binding not
  not-evaluated). R5 false: no usable boundary (S103). R6 false: the aggregate is present (S104).
  R8, R10 false. R9 false: semantic_validation is supported. No fallback token (S105).
  substantive_reasons = [E_EVIDENCE_NOT_BOUND]; no gap rows: evaluation_gaps = [],
  evaluation_gap_entries = [].
- Verdict: asserted_claim_supported is false: downgrade (S83, S97); non-fatal by S101.
- inherited_limitations: boundary limitations Lb (S85; also S51), plus Le because the execution
  finding determines the R7 reason for the asserted claim (S85); the finding is failed but not
  unrelated, so S86 does not exclude it. No support entry, no applicable counter or gap entry.
  inherited_limitations = Lb union Le.
- boundary_grounding "asserted-only" is preserved although the ceiling is unusable (S50, S51).

### 3.6 Template E: unevaluated target binding on boundary and execution finding

Applies to id-alone-unverified. Input shape: boundary status supported, target_binding
not-evaluated; execution finding target_binding not-evaluated, semantic_validation supported;
scope SCOPE-UNV; everything else as Template A.

- (S107) [8.4] "Every Core-derived finding gap entry has the row's token, the input target and evaluation-context identifier, affected_claims={input.asserted_claim}, and the basis-reference and limitation sets of the aggregate that made the row true."
- (S108) [8.6] "Evaluation gaps describe assessments that were not performed."
- (S109) [12] "A role-specific Core gap entry is emitted only by the claim-required matrix when its aggregate is required by the asserted claim."
- (S110) [12] "Otherwise the scope map alone records the unexercised capability and does not become a reason, gap, or substantive finding."

Derivation:

- B = {} (S59 and S61 fail: neither binding is supported); supported_claims,
  maximal_supported_claims, support_entries, support_relations = []; asserted_claim_supported =
  false; boundary_ceiling null (S74, S75, S100).
- Rows: R4 true (boundary binding not-evaluated): gap entry {token E_BOUNDARY_NOT_EVALUATED,
  target, evaluation_context_ref C, affected_claims {E}, basis_refs bd, limitations Lb} (S100,
  S107). R8 true (asserted-base binding not-evaluated): gap entry {token E_BASE_NOT_EVALUATED,
  target, C, {E}, basis_refs eb, limitations Le} (S107). R1, R2, R3, R7 false (status supported,
  bindings not unsupported). R5 false (no usable boundary). R6 false (present). R9, R10 false
  (semantic_validation supported). The two entries differ in token, basis and limitations, so both
  remain (S78).
- substantive_reasons = []; evaluation_gaps = [E_BOUNDARY_NOT_EVALUATED, E_BASE_NOT_EVALUATED]
  (S90, S91).
- The not-evaluated scope values add nothing further (S109, S110, T02).
- Verdict: downgrade (S83, S97).
- inherited_limitations: Lb (boundary limitations, and the boundary determines the R4 gap) union Le
  (the execution finding determines the R8 gap) = Lb union Le (S85).
- Core-derived gap entries carry no current_scope_capability: that member is only "supplied on a
  profile gap" (S91).

---

## 4. Per-case derivations

Each case: the input in one line, its atoms, the sentences relied on, all twenty members, and every
difference from its template. Sentences of Section 1 (ingress) apply to every case and are not
repeated.

### 4.1 anchor-absent

Input: target `aer1:b6c63ac5-f324-4fa7-ad58-c4bf83faa86a`; assert E; boundary supported, bound,
ceiling execution, asserted-only, Lb = {L-u, L-lb}; execution finding bound and supported,
Le = {L-u, L-lb, L-na}; no qualifier findings; CE-NS; no profile gaps; fatal {}; SCOPE-STD.

Atoms: bd = {(PID, `receipt-01.json@sha256:f6f2b532a70c1969a0e70a8342ad5a9fefa5810f163b930560b4bfffb9a24931`)};
eb = {(PID, `receipt-01/canonical_bytes@sha256:c2258bdf9c34813a70166bc0e2d79b167f22f51a0adb67e218b5c868b911dca7`)}.

Ingress: passes 1 to 6. Template A. Sentences: S48 to S86 as used in 3.1 and 3.2.

Expected:

- semantics_version: "wexp-core-2"
- verdict: accept
- fatal_reasons: []
- target: `aer1:b6c63ac5-f324-4fa7-ad58-c4bf83faa86a`
- asserted_claim: E
- asserted_claim_supported: true
- support_entries: [{claim E, basis_refs [bd, eb], limitations [L-u, L-lb, L-na]}]
- supported_claims: [E]
- maximal_supported_claims: [E]
- support_relations: [{E, equal}]
- boundary_ceiling: "execution"
- boundary_grounding: "asserted-only"
- recorder_relations: []
- substantive_reasons: []
- evaluation_gaps: []
- evaluation_gap_entries: []
- counter_evidence: CE-NS
- inherited_limitations: [L-u, L-lb, L-na]
- evaluation_context: CTX
- evaluation_scope: SCOPE-STD

Differences from Template A: none. The limitation L-na comes from Le and therefore appears in the
support entry (S69) and in inherited_limitations (S85). Ambiguity: none.

### 4.2 anchor-not-checked

Input: as anchor-absent, but Le = {L-u, L-lb} (no L-na), and one profile-gap entry: token
P_AER1_ANCHOR_NOT_CHECKED, target and context of the input, affected_claims {E}, two basis
references, empty limitations, no current_scope_capability.

Atoms: bd = {(PID, `anchored-unresolvable-anchor.json@sha256:7060532c55c6d01a9d420433f5578810993f428597edfcd1612996e140647473`)};
eb = {(PID, `anchored-unresolvable-anchor/canonical_bytes@sha256:c2258bdf9c34813a70166bc0e2d79b167f22f51a0adb67e218b5c868b911dca7`)};
gap basis = {(PID, `anchor-vectors.json@sha256:15fe803468cc54a0bbddf04f592ac42fcbdb71d9353b91c8ef0b903557578fb8#anchor-not-checked`),
(PID, `anchored-unresolvable-anchor.json@sha256:7060532c55c6d01a9d420433f5578810993f428597edfcd1612996e140647473`)}.

Ingress: passes 1 to 6 (the gap token resolves to the evaluation-gap category, S27, S29). Template B.
Sentences: as Template A plus S87 to S93, T03, T04.

Expected:

- semantics_version "wexp-core-2"; verdict accept; fatal_reasons []
- target `aer1:b6c63ac5-f324-4fa7-ad58-c4bf83faa86a`; asserted_claim E; asserted_claim_supported true
- support_entries: [{claim E, basis_refs [bd, eb], limitations [L-u, L-lb]}]
- supported_claims [E]; maximal_supported_claims [E]; support_relations [{E, equal}]
- boundary_ceiling "execution"; boundary_grounding "asserted-only"; recorder_relations []
- substantive_reasons: []
- evaluation_gaps: [P_AER1_ANCHOR_NOT_CHECKED]
- evaluation_gap_entries: [the supplied entry exactly: token P_AER1_ANCHOR_NOT_CHECKED, target,
  evaluation_context_ref C, affected_claims [E], basis_refs [gap basis], limitations []]
- counter_evidence: CE-NS
- inherited_limitations: [L-u, L-lb]
- evaluation_context CTX; evaluation_scope SCOPE-STD

Differences from Template A: the projected gap entry and its token (S87, S90); the verdict does not
change (S92). Le lacks L-na, so neither the support entry nor inherited_limitations has it.
Ambiguity: none.

### 4.3 anchor-resolves

Input: as anchor-absent, but Le = {L-u, L-lb}.

Atoms: bd = {(PID, `anchored-valid.json@sha256:03dcdc8be19340ce91ddc6f6fc6c98f2b8b2bc183b350c6c3f2b849bd0f52daf`)};
eb = {(PID, `anchored-valid/canonical_bytes@sha256:c2258bdf9c34813a70166bc0e2d79b167f22f51a0adb67e218b5c868b911dca7`)}.

Ingress: passes 1 to 6. Template A. Sentences: as anchor-absent.

Expected:

- semantics_version "wexp-core-2"; verdict accept; fatal_reasons []
- target `aer1:b6c63ac5-f324-4fa7-ad58-c4bf83faa86a`; asserted_claim E; asserted_claim_supported true
- support_entries: [{claim E, basis_refs [bd, eb], limitations [L-u, L-lb]}]
- supported_claims [E]; maximal_supported_claims [E]; support_relations [{E, equal}]
- boundary_ceiling "execution"; boundary_grounding "asserted-only"; recorder_relations []
- substantive_reasons []; evaluation_gaps []; evaluation_gap_entries []
- counter_evidence CE-NS
- inherited_limitations: [L-u, L-lb]
- evaluation_context CTX; evaluation_scope SCOPE-STD

Differences from anchor-absent: the basis atoms, and no L-na in Le, hence none in the support entry
or inherited_limitations. Ambiguity: none.

### 4.4 anchor-unresolvable

Input: as anchor-not-checked, with the gap token P_AER1_ANCHOR_UNRESOLVABLE and the first gap basis
reference ending `#anchor-unresolvable`.

Atoms: bd and eb as anchor-not-checked; gap basis =
{(PID, `anchor-vectors.json@sha256:15fe803468cc54a0bbddf04f592ac42fcbdb71d9353b91c8ef0b903557578fb8#anchor-unresolvable`),
(PID, `anchored-unresolvable-anchor.json@sha256:7060532c55c6d01a9d420433f5578810993f428597edfcd1612996e140647473`)}.

Ingress: passes 1 to 6. Template B. Sentences: as anchor-not-checked.

Expected: identical to anchor-not-checked except

- evaluation_gaps: [P_AER1_ANCHOR_UNRESOLVABLE]
- evaluation_gap_entries: [the supplied entry exactly, with token P_AER1_ANCHOR_UNRESOLVABLE and the
  gap basis above]

Differences from anchor-not-checked: the token and one basis atom of the copied entry; every other
member is equal. The two anchor states stay distinct in the result because the entry is copied
exactly (S88) and the token projection keeps the token (S90). Ambiguity: none.

### 4.5 anchor-verification-failed

Input: as anchor-resolves (Le = {L-u, L-lb}), but counter_evidence is one entry: status
unresolved-material, affected_claims {E}, reasons {P_AER1_ANCHOR_DIGEST_MISMATCH}, two basis
references, empty limitations.

Atoms: bd = {(PID, `anchored-bad-leaf-hash.json@sha256:5e8ea1918e69be2f26dfa2da6707ad6868797f9114d6d19a3c19189662e377e2`)};
eb = {(PID, `anchored-bad-leaf-hash/canonical_bytes@sha256:c2258bdf9c34813a70166bc0e2d79b167f22f51a0adb67e218b5c868b911dca7`)};
counter basis = {(PID, `anchor-vectors.json@sha256:15fe803468cc54a0bbddf04f592ac42fcbdb71d9353b91c8ef0b903557578fb8#anchor-verification-failed`),
(PID, `anchored-bad-leaf-hash.json@sha256:5e8ea1918e69be2f26dfa2da6707ad6868797f9114d6d19a3c19189662e377e2`)}.

Ingress: passes 1 to 6 (sentinel absent with a named admissible claim, S14; reason substantive,
S27, S28). Template C. Sentences: as Template A plus S81, S82, S94 to S99, R13, T05, T06.

Expected:

- semantics_version "wexp-core-2"; verdict downgrade; fatal_reasons []
- target `aer1:b6c63ac5-f324-4fa7-ad58-c4bf83faa86a`; asserted_claim E
- asserted_claim_supported: true (S98)
- support_entries: [{claim E, basis_refs [bd, eb], limitations [L-u, L-lb]}]
- supported_claims [E]; maximal_supported_claims [E]; support_relations [{E, equal}] (S99)
- boundary_ceiling "execution"; boundary_grounding "asserted-only"; recorder_relations []
- substantive_reasons: [E_COUNTER_EVIDENCE_UNRESOLVED, P_AER1_ANCHOR_DIGEST_MISMATCH] (S94 to S96)
- evaluation_gaps []; evaluation_gap_entries []
- counter_evidence: the input entry, unchanged (S49)
- inherited_limitations: [L-u, L-lb]
- evaluation_context CTX; evaluation_scope SCOPE-STD

Differences from anchor-resolves: the blocking counter entry gives the two reasons and the verdict
downgrade; the support set, the relation and asserted_claim_supported do not change. Ambiguity: none.

### 4.6 hash-mismatch

Input: target `aer1:b6c63ac5-f324-4fa7-ad58-c4bf83faa86a`; assert E; boundary supported and bound;
execution finding bound, semantic_validation unsupported, Le = {L-u, L-lb, L-na}; CE-NS; SCOPE-STD;
fatal_conditions {E_INTEGRITY_INVALID}.

Ingress: passes 1 to 4; fails check 5 with the valid supplied set {E_INTEGRITY_INVALID} (S32, S35,
S46). Sentences: S35, S38 to S47, T01.

Expected: the fixed projection of Section 2 with fatal_reasons [E_INTEGRITY_INVALID]; every other
member as listed there (unavailable members null, derived sets empty, asserted_claim_supported
false, verdict reject). Ambiguity: none.

### 4.7 id-alone-unverified

Input: target `aer1:130da435-e157-498e-af90-605866a86a27`; assert E; boundary supported, ceiling
execution, target_binding not-evaluated, asserted-only, Lb = {L-u, L-lb}; execution finding
target_binding not-evaluated, semantic_validation supported, Le = {L-u, L-lb, L-na}; CE-NS; no
profile gaps; fatal {}; SCOPE-UNV.

Atoms: bd = {(PID, `id-binding-vectors.json@sha256:78cb42cbc8be1306458f63e90e01f0e9201504ff5bf5d455a659631f21237009#id-alone-unverified`)};
eb = {(PID, `id-binding-fixture/canonical_bytes@sha256:0492c18e09059aa2e30ba0864f6aada2ef08475a5b35944cbf2a9ce46d12b9f1`)}.

Ingress: passes 1 to 6; its scope was checked in detail under check 4 (S19 to S25). Template E.
Sentences: S48 to S79, S83, S85, S86, S90, S91, S97, S100, S107 to S110, T02.

Expected:

- semantics_version "wexp-core-2"; verdict downgrade; fatal_reasons []
- target `aer1:130da435-e157-498e-af90-605866a86a27`; asserted_claim E
- asserted_claim_supported: false
- support_entries []; supported_claims []; maximal_supported_claims []; support_relations []
- boundary_ceiling: null
- boundary_grounding: "asserted-only"
- recorder_relations: []
- substantive_reasons: []
- evaluation_gaps: [E_BOUNDARY_NOT_EVALUATED, E_BASE_NOT_EVALUATED]
- evaluation_gap_entries:
  - {token E_BOUNDARY_NOT_EVALUATED, target `aer1:130da435-e157-498e-af90-605866a86a27`,
    evaluation_context_ref C, affected_claims [E], basis_refs [bd], limitations [L-u, L-lb]}
  - {token E_BASE_NOT_EVALUATED, target `aer1:130da435-e157-498e-af90-605866a86a27`,
    evaluation_context_ref C, affected_claims [E], basis_refs [eb], limitations [L-u, L-lb, L-na]}
- counter_evidence: CE-NS
- inherited_limitations: [L-u, L-lb, L-na]
- evaluation_context: CTX
- evaluation_scope: SCOPE-UNV (carried, S48, S54)

Differences from Template E: none (this case is the template's only instance). Ambiguity: none.

### 4.8 id-expected-match

Input: as anchor-absent in shape (bound and supported, Le = {L-u, L-lb, L-na}), with target
`aer1:130da435-e157-498e-af90-605866a86a27`.

Atoms: bd = {(PID, `id-binding-vectors.json@sha256:78cb42cbc8be1306458f63e90e01f0e9201504ff5bf5d455a659631f21237009#id-expected-match`)};
eb = {(PID, `id-binding-fixture/canonical_bytes@sha256:0492c18e09059aa2e30ba0864f6aada2ef08475a5b35944cbf2a9ce46d12b9f1`)}.

Ingress: passes 1 to 6. Template A. Sentences: as anchor-absent.

Expected:

- semantics_version "wexp-core-2"; verdict accept; fatal_reasons []
- target `aer1:130da435-e157-498e-af90-605866a86a27`; asserted_claim E; asserted_claim_supported true
- support_entries: [{claim E, basis_refs [bd, eb], limitations [L-u, L-lb, L-na]}]
- supported_claims [E]; maximal_supported_claims [E]; support_relations [{E, equal}]
- boundary_ceiling "execution"; boundary_grounding "asserted-only"; recorder_relations []
- substantive_reasons []; evaluation_gaps []; evaluation_gap_entries []
- counter_evidence CE-NS
- inherited_limitations: [L-u, L-lb, L-na]
- evaluation_context CTX; evaluation_scope SCOPE-STD

Differences from anchor-absent: target and basis atoms only. Ambiguity: none.

### 4.9 id-expected-mismatch

Input: target `aer1:130da435-e157-498e-af90-605866a86a27`; assert E; boundary supported, ceiling
execution, target_binding unsupported, asserted-only, Lb = {L-u, L-lb}; execution finding
target_binding unsupported, semantic_validation supported, Le = {L-u, L-lb, L-na}; CE-NS; no profile
gaps; fatal {}; SCOPE-STD.

Atoms: bd = {(PID, `id-binding-vectors.json@sha256:78cb42cbc8be1306458f63e90e01f0e9201504ff5bf5d455a659631f21237009#id-expected-mismatch`)};
eb = {(PID, `id-binding-fixture/canonical_bytes@sha256:0492c18e09059aa2e30ba0864f6aada2ef08475a5b35944cbf2a9ce46d12b9f1`)}.
Neither appears in the result: there is no support entry and no gap entry.

Ingress: passes 1 to 6; the failed binding is non-fatal (S101). Template D. Sentences: S48 to S79,
S83, S85, S86, S97, S100 to S106.

Expected:

- semantics_version "wexp-core-2"; verdict downgrade; fatal_reasons []
- target `aer1:130da435-e157-498e-af90-605866a86a27`; asserted_claim E
- asserted_claim_supported: false
- support_entries []; supported_claims []; maximal_supported_claims []; support_relations []
- boundary_ceiling: null
- boundary_grounding: "asserted-only"
- recorder_relations: []
- substantive_reasons: [E_EVIDENCE_NOT_BOUND]
- evaluation_gaps []; evaluation_gap_entries []
- counter_evidence: CE-NS
- inherited_limitations: [L-u, L-lb, L-na]
- evaluation_context CTX; evaluation_scope SCOPE-STD

Differences from Template D: none. Ambiguity: none.

### 4.10 id-resolution-agreement

Input: identical to id-expected-match except the boundary basis reference, which ends
`#id-resolution-agreement`.

Atoms: bd = {(PID, `id-binding-vectors.json@sha256:78cb42cbc8be1306458f63e90e01f0e9201504ff5bf5d455a659631f21237009#id-resolution-agreement`)};
eb as id-expected-match.

Ingress: passes 1 to 6. Template A. Sentences: as anchor-absent, plus

- (S111) [11] "Inputs that differ only in opaque basis-reference identifiers are not completely Core-equivalent; when all other normalized components are equal, their appraisals MUST nevertheless be identical except for those carried basis references and any carrier metadata that the result profile explicitly preserves."

Expected: identical to id-expected-match except support_entries[0].basis_refs = [bd, eb] with the bd
above (S111). Ambiguity: none.

### 4.11 id-resolution-disagreement

Input: identical in shape to id-expected-mismatch (both bindings unsupported, semantic_validation
supported, same Lb and Le), with target `aer1:42fc3298-b1e7-4087-bb1c-f80ef9f12c7c` on the input,
the boundary and the execution finding, and the boundary basis reference ending
`#id-resolution-disagreement`.

Ingress: passes 1 to 6 (scope equality holds for the donor target, S12). Template D. Sentences: as
id-expected-mismatch.

Expected: identical to id-expected-mismatch except target = `aer1:42fc3298-b1e7-4087-bb1c-f80ef9f12c7c`.
The different boundary basis atom does not appear in the result (no support or gap entry carries
it). Ambiguity: none.

### 4.12 input-hash-key-order-20

Input: target `aer1:8b2d0f53-6c4e-45b7-bf9c-2d3e4f5a6b7c`; assert E; boundary supported and bound,
Lb = {L-u}; execution finding bound, semantic_validation unsupported, Le = {L-u, L-na}; CE-NS;
SCOPE-STD; fatal_conditions {E_INTEGRITY_INVALID}.

Ingress: passes 1 to 4; fails check 5 with {E_INTEGRITY_INVALID}. Expected: the fixed projection of
Section 2 with fatal_reasons [E_INTEGRITY_INVALID]. Identical to hash-mismatch: the differing target,
limitations and basis atoms are all unavailable in a rejection (S43). Ambiguity: none.

### 4.13 input-hash-mismatch

Input: target `aer1:22c64420-500f-498a-be52-d7011647bb2b`; otherwise the same shape as
input-hash-key-order-20 (semantic_validation unsupported, Lb = {L-u}, Le = {L-u, L-na}); fatal_conditions
{E_INTEGRITY_INVALID}.

Ingress: fails check 5. Expected: the fixed projection with fatal_reasons [E_INTEGRITY_INVALID];
identical to hash-mismatch. Ambiguity: none.

### 4.14 tampered-provenance

Input: target `aer1:231c3cb5-1e6c-4d29-8125-e38472b679b6`; assert E; boundary supported and bound,
Lb = {L-u}; execution finding bound and supported, Le = {L-u, L-na}; CE-NS; SCOPE-STD;
fatal_conditions {E_BINDING_MISMATCH}.

Ingress: passes 1 to 4; fails check 5 with the valid supplied set {E_BINDING_MISMATCH} (S32, S35,
S47). Expected: the fixed projection of Section 2 with fatal_reasons [E_BINDING_MISMATCH]. The
supported execution finding is not consulted (S38). Ambiguity: none.

### 4.15 version-downgrade

Input: target `aer1:62e028e2-9bc0-4d70-9762-17d1a84b411f`; same shape as tampered-provenance;
fatal_conditions {E_BINDING_MISMATCH}.

Ingress: fails check 5. Expected: the fixed projection with fatal_reasons [E_BINDING_MISMATCH];
identical to tampered-provenance. Ambiguity: none.

---

## 5. Readings considered and rejected

Each item below is an alternative I tested against the text. None is admitted by the text, so none
is recorded as an ambiguity.

X1. Core must itself confirm that the evaluation context accepts asserted-only grounding, and
return E_PROFILE_MAPPING_INVALID when it cannot. Under this reading all fifteen inputs would be
rejected at check 4 (before the five supplied fatal sets are reached). Rejected:

- (S112) [6] "A supported boundary has a grounding value of asserted-only, attributed, or attested that the evaluation context accepts."
- (S113) [7] "boundary_finding.status = supported means that the boundary predicate required by the named evaluation context passed."
- (S114) [6.1] "The target, evaluation-context identifier, evaluation time, and trust configuration are opaque logical atoms."
- (S115) [6.1] "Core does not interpret an opaque atom; it only compares, copies, and set-unions it using that equality."
- (S116) [13] "trust-configuration atom core02-fixture-trust-1, which accepts attributed boundary grounding"

S112 attaches no consequence; the consequence in the same paragraph (S16) covers only the pairing of
not-evaluated with another value. Acceptance is part of the boundary predicate that status =
supported already reports as passed (S113), and Core cannot read acceptance from the opaque
trust-configuration atom (S114, S115). The normative fixtures state acceptance as a property of the
fixture's trust atom (S116), not as an input value Core checks; C01 is an accept under an attributed
boundary on that basis.

X2. A projected profile gap blocks acceptance (anchor-not-checked and anchor-unresolvable would be
downgrade, because an evaluation-gap token's registered default effect is "downgrade if needed by
claim"). Rejected by S92, S93, by the C13 pattern (T03, T04), and by:

- (S117) [15] "The default effect describes the condition that generates the diagnostic, not a verdict computed from token presence alone."
- (S118) [15] "The verdict procedure in Section 8.4 is authoritative."

X3. id-alone-unverified is rejected at check 4 for scope inconsistency. Rejected: the walk-through
under check 4 shows every governing capability of its two not-evaluated binding fields is
not-evaluated, and the claim-required execution aggregate is present with a governed not-evaluated
field (S19 to S25).

X4. The two failed-binding downgrades also carry E_MISSING_REQUIRED_EVIDENCE or
E_EXACT_CLAIM_NOT_SUPPORTED, because no claim is supported. Rejected by S77, S104 and S105:
the aggregate is present and its semantic status is supported.

X5. boundary_ceiling is carried as "execution" in the three binding downgrades. Rejected by S74,
S75 and S100: the ceiling is reported only when the target binding passes.

X6. The execution finding's limitations (with L-na) are left out of inherited_limitations in the
three binding downgrades, because the finding failed. Rejected: S85 includes "limitations attached
to findings that determine a reason or gap for the asserted claim", and the execution finding
determines R7 or R8; S86 excludes only unrelated failed findings.

X7. The not-evaluated scope values (target-binding, boundary-grounding, execution-support in
id-alone-unverified; observation-, intent-, invocation-, provenance-support and
independent-verification everywhere) create further gaps. Rejected by S22, S109, S110 and T02, and:

- (S119) [3] "It MUST NOT be used as positive evidence, as a structural ceiling on claims, or as a sort key over claims."

X8. A rejected input reports a different set because its findings are also non-passing (for example
an added E_EXACT_CLAIM_NOT_SUPPORTED with E_INTEGRITY_INVALID), or is E_PROFILE_MAPPING_INVALID
because a supplied fatal and an unsupported finding are redundant. Rejected: no cross-field invariant
relates fatal_conditions to finding statuses (S10), and after a rejection branch wins nothing is
added (S38, S39, S43).

X9. MAPPING.md's reading choices 1 to 3 (a failed anchor as unresolved-material counter-evidence, a
digest mismatch as a supplied fatal, the version-downgrade comparison) decide how AER-1 outcomes were
turned into inputs. They are choices about input construction, not readings of the Core text; the
expectations here follow from the inputs as given, as the brief requires.

---

## 6. Ambiguities

None found. For every case and every member, the quoted text admits one result; the alternatives
tested in Section 5 are each excluded by a quoted sentence. `out/AMBIGUITIES.json` is therefore an
empty array.

---

## 7. Encoding notes (REPRESENTATION.md, FORMAT-REFERENCE-C01.json)

- unavailable is encoded `null`; sets are arrays with set semantics, so member order is not
  significant. The orders written are: support-entry basis references boundary first, then the base
  finding (as in C01, whose entry lists bd before I); limitations in order of first occurrence
  (boundary, then execution finding); substantive_reasons with the Core token before the profile
  token (as C15 lists them); evaluation_gaps and evaluation_gap_entries in matrix row order
  (boundary row, then asserted-base row); evaluation_scope and counter_evidence in input order.
- A support entry is encoded with the members claim, basis_refs and limitations; a support relation
  with supported_claim and relation (S71, S72; C01).
- An evaluation-gap entry is encoded with the member names of the input's profile_evaluation_gaps
  entries: token, target, evaluation_context_ref, affected_claims, basis_refs, limitations; and
  current_scope_capability only when supplied on a profile gap (S91). This is required for the
  profile entries, which must equal the supplied entry (S88, T04), and the same names are used for
  the Core-derived entries of id-alone-unverified. REPRESENTATION.md names no members for gap
  entries; this is an encoding choice, not a reading of the text.
- Files are serialized with 1-space indent, sorted keys, ASCII only and a trailing newline, the same
  convention as FORMAT-REFERENCE-C01.json (confirmed by byte comparison).

---

## 8. Checks run on the deliverables (none implements an appraiser)

- Every input file parses as JSON with no duplicate object member.
- Every expected file parses, has exactly the members `expected` and `id`, its id equals its file
  name, `expected` has exactly the twenty members, and the bytes equal the 1-space-indent,
  sorted-key, ASCII serialization with a trailing newline.
- Transcription: in each accept or downgrade, target, asserted_claim, evaluation_context,
  evaluation_scope, counter_evidence, recorder_relations and boundary_grounding equal the input
  values; every opaque atom written occurs in the corresponding input aggregate; each copied profile
  gap entry equals the supplied entry.
- Every quote tagged (Snn) or (Rnn) above occurs verbatim in the normalized specification text, and
  every (Tnn) quote occurs in the joined cell text of the named Table 2 row and column (138 quotes,
  0 failures).
- Labels: (R1) to (R13) are quoted matrix rows of Section 8.6; X1 to X9 are the rejected readings of
  Section 5.
