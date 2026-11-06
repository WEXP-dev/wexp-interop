# Derivation of the expected appraisals for inputs a, b1, b2, c

Source of every expectation: `spec/draft-sergeev-wexp-core-02.txt` (the "text"). Section numbers
refer to that text. Quotations are verbatim. `MAPPING.md` was read as background only; nothing
below depends on it. Notation: P = `wexp-work/interop/scitt-receipt-boundary-001/mapping-1`,
T = `wexp-interop:scitt-receipt-boundary-001`, C = `C-scitt-001`, LIM = (P, `L-ts-no-issuer-signature-check`),
BD = (P, `receipt-510a7148`), O = (observation, {}), E = (execution, {}).

## 0. Common ingress analysis (all four inputs)

Ordered rejection checks, section 6.2:

> 1.  If the outer value is not an input record, or semantics_version is absent or is not a text atom, Core returns E_MALFORMED_NORMALIZED_INPUT.
> 2.  If that readable value is not wexp-core-2, Core returns E_UNSUPPORTED_SEMANTICS_VERSION without applying the version-specific member rules below.
> 3.  For wexp-core-2, a missing required member, unknown member, wrong logical type, unknown closed-enum value, or malformed set, entry, claim, token, or recorder relation returns E_MALFORMED_NORMALIZED_INPUT.
> 4.  A well-typed wexp-core-2 input that violates a cross-field invariant returns E_PROFILE_MAPPING_INVALID.  Cross-field invariants include aggregate cardinality and keys, exact target and context scope, the counter-evidence sentinel, qualifier combinations, conditional ceiling_base, evaluation-scope consistency and extension-key binding, and profile or registry identity and token category.
> 5.  If the structurally usable input has a non-empty valid fatal_conditions set, Core returns that complete set through the fixed rejection projection.
> 6.  Otherwise an inadmissible asserted claim returns E_CLAIM_OUT_OF_DOMAIN.

Applied to the four inputs:

- Check 1-2: `semantics_version` is the text atom `wexp-core-2` in all four. Pass.
- Check 3: every top-level member of the section 6 `AppraisalInput` record is present
  (`semantics_version, target, asserted_claim, evaluation_context, boundary_finding, base_findings,
  qualifier_findings, recorder_relations, counter_evidence, evaluation_scope, profile_evaluation_gaps,
  inherited_limitations, fatal_conditions`); every closed-enum value used (`supported`, `not-evaluated`,
  `attributed`, `not-supplied`, `evaluated`, bases `observation`/`execution`) is a defined member. Pass.
- Check 4, invariant by invariant:
  - aggregate cardinality: at most one base finding per (target, base, context) key in each input; exactly one boundary finding. Section 6: "A normalized input contains exactly one aggregated boundary finding, at most one aggregated base finding for each (target, base, evaluation_context) key". Pass.
  - exact scope: every finding has `target` = T and `evaluation_context_ref` = C = `evaluation_context.id`. Section 6: "The boundary finding, every base and qualifier aggregate, and every profile-gap entry have a target equal to the top-level target and an evaluation_context_ref equal to the top-level evaluation-context identifier." Pass.
  - counter-evidence sentinel: section 6: "When no counter-evidence was supplied it contains exactly one not-supplied entry with empty affected claims, basis references, reasons, and limitations." All four carry exactly that entry. Pass.
  - qualifier combinations: `qualifier_findings` is empty in all four. Pass.
  - conditional ceiling_base: section 6: "A boundary finding with status = supported MUST contain ceiling_base." (a, b1, b2: status supported, ceiling_base present.) "grounding = not-evaluated is valid only with status = not-evaluated; either field paired differently produces E_PROFILE_MAPPING_INVALID." (c: status not-evaluated AND grounding not-evaluated: the valid pairing.) "When boundary status is unsupported or not-evaluated, a present ceiling_base is diagnostic carrier metadata only and is ignored by the Core algorithm." (c: the present `ceiling_base` is ignored, not an error.) Pass.
  - evaluation-scope consistency: section 12: "Every initial name MUST appear exactly once." All twelve initial names appear exactly once in each input. "carrier-mapping is evaluated for every complete Core input." It is. Governed fields: "The governed status fields are: every finding's target_binding for target-binding; boundary status, binding, and grounding for boundary-grounding; the corresponding base aggregate's binding and semantic status for each base-support capability". In a, b1, b2 every governed field is a non-not-evaluated status and every capability is `evaluated`: consistent. In c, `boundary-grounding` = `not-evaluated` and the boundary's status and grounding are `not-evaluated`: consistent; `target-binding` = `evaluated` and every finding's target_binding is `supported`: consistent; `observation-support` = `evaluated` and the observation aggregate is wholly supported: consistent. No extension keys. Pass.
  - profile/registry identity and token category: no reason, fatal, or gap tokens occur anywhere in the inputs; `profiles.json` declares P with no tokens, which is consistent with none being used. Basis references and limitations are opaque profile-scoped atoms under the applied P (P occurs in `evaluation_context.profile_identifiers`): section 6.1: "A basis reference or limitation is a profile-scoped atom logically equivalent to the pair (profile_identifier, local_value). ... Core does not interpret an opaque atom; it only compares, copies, and set-unions it using that equality." Pass.
- Check 5: `fatal_conditions` = {} in all four. Pass.
- Check 6: section 4.4 admissible domain lists `(observation, {})` and `(execution, {})`. Asserted claims: a = E, b1 = b2 = c = O. All admissible. Pass.

Therefore none of the four is a reject; each verdict is `accept` or `downgrade` (section 8.2:
"A conforming Core appraiser MUST return exactly one of accept, downgrade, or reject.") and
`fatal_reasons` = {} in each (section 8.5: "fatal_reasons is non-empty if and only if the verdict is reject.").

Carried-through members. Section 13: "For accept and downgrade rows, fields not varied by a row equal
the common input values and carry through to the output." Section 8.5: "counter_evidence preserves every
status, affected-claim set, basis-reference set, reason set, and limitation set from the normalized input".
Section 12: "Core ignores an extension status for support and gap derivation but preserves the exact
pair and status in the result." Hence for every case: `semantics_version`, `target`, `asserted_claim`,
`recorder_relations` (= []), `counter_evidence` (the single not-supplied entry), `evaluation_context`,
`evaluation_scope` equal the input values. `BRIEF.md`/`REPRESENTATION.md` fix the same rule for the local encoding.

Support-set rule, section 8.1:

> A base b is in B if and only if all of the following hold:
> 1.  the unique aggregate base finding for b has supported target binding and supported semantic validation;
> 2.  the finding names the same target and evaluation context as the appraisal input;
> 3.  the boundary finding is supported, target-bound, and scoped to that same target and context; and
> 4.  the accepted Boundary Ceiling is at least b.

Section 7: "The Boundary Ceiling is an exclusion rule, not an evidence source.  A boundary finding can
prevent a base from being supported; it MUST NOT create a positive base finding.  Observation itself
requires a positive exact observation finding."

Section 4.2 order: "observation < intent < invocation < execution".

Verdict rule, section 8.2: "accept  The asserted claim is an exact member of SupportedClaims and
counter-evidence does not block that exact claim." / "downgrade  The input is safely interpretable and
the asserted claim is admissible, but it is not exactly supported, or counter-evidence blocks acceptance."
Section 8.2 on blocking: "Counter-evidence blocks a claim when at least one entry has status
not-evaluated, unresolved-material, or defeating and that entry's affected_claims contains the claim or
all-admissible-claims. not-supplied and resolved-no-defeat entries do not block by themselves." The only
entry in every input is `not-supplied` with empty affected claims: it never blocks and is never an
applicable counter entry (section 8.4: "applicable_counter_entries returns only entries whose affected
claims include the asserted claim or all-admissible-claims and whose status blocks that claim"). So the
three counter-status rows never fire and no counter-derived reason or gap is produced in any case.

Boundary members in an accept/downgrade result, section 8.5: "For an accept or downgrade result,
boundary_ceiling is the accepted ceiling only when the boundary finding, its target binding, target, and
context all pass; otherwise it is unavailable. boundary_grounding preserves the input grounding even
when the boundary is unsupported." Section 7: "An accept or downgrade result MUST preserve the boundary
grounding status and its limitations."

inherited_limitations, section 8.1: "The result's inherited_limitations is the set union of the input's
inherited limitations; limitations from each counter-evidence or profile-gap entry whose affected claims
include the asserted claim, a member of SupportedClaims, or all-admissible-claims; boundary limitations;
every support-entry limitation; and limitations attached to findings that determine a reason or gap for
the asserted claim.  Limitations on unrelated failed findings are excluded." In all four inputs the
input `inherited_limitations` is {}, no profile gap exists, the counter entry has empty affected claims
and empty limitations, every base finding has empty limitations, and the boundary carries exactly LIM.

Diagnostic matrix, section 8.6 (rows relevant here):

> E_BOUNDARY_NOT_EVALUATED (gap)  Boundary status = not-evaluated; source: boundary finding.
> E_BASE_EXCEEDS_BOUNDARY (substantive)  Usable boundary with asserted base deeper than its ceiling; sources: boundary and asserted-base findings.
> E_MISSING_REQUIRED_EVIDENCE (substantive)  Asserted-base aggregate absent; source: none.

and: "An absent aggregate triggers only its absence row; status rows require that aggregate to be
present. ... A boundary-exceeded row requires a usable boundary and a present asserted-base aggregate
whose base is deeper than the ceiling.  Consequently a present supported base excluded by the ceiling
produces E_BASE_EXCEEDS_BOUNDARY, not E_MISSING_REQUIRED_EVIDENCE.  All simultaneously applicable
distinct tokens are emitted.  No condition outside this matrix creates a Core-derived non-fatal token."
The PROV/IV rows are "Asserted PROV ..." / "Asserted IV ..." rows; no qualifier is asserted in any of the
four inputs, so none applies (confirmed by C07 and C08, which assert unqualified claims and emit only one
token each). Finding reasons: all `reasons[]` sets in the inputs are empty, so the finding-reason
projection ("add its registered substantive reasons to reasons") adds nothing.

## 1. Case a

Input (one line): assert E; one base finding (execution; target T; context C; target_binding supported;
semantic_validation supported; basis (P, exec-log-1); no limitations); boundary supported, target-bound,
attributed, ceiling_base observation, basis BD, limitations {LIM}; counter not-supplied; all scope
capabilities evaluated; no gaps, no inherited limitations, no fatal conditions.

Derivation:
- B: the execution finding satisfies 8.1 conditions 1-3, but condition 4 fails: the accepted ceiling is
  observation and "observation < intent < invocation < execution" (4.2), so execution exceeds it.
  Section 7: "For every supported claim (b, A), b MUST NOT exceed the accepted boundary_finding.ceiling_base."
  No observation finding exists and the boundary "MUST NOT create a positive base finding" (7). B = {}.
- supported_claims = maximal_supported_claims = {} ; support_entries = {} (one entry per member of
  SupportedClaims, 8.1); support_relations = {} (8.3: "If no claim is supported, the relation array is empty.").
- asserted_claim_supported = false (8.3: "reports exact membership in SupportedClaims").
- verdict = downgrade (8.2: not exactly supported; input safely interpretable; claim admissible).
- substantive_reasons = {E_BASE_EXCEEDS_BOUNDARY}: the boundary is usable (7: "Only status = supported
  with target_binding = supported and matching target and context makes ceiling_base usable."), the
  asserted-base aggregate (execution) is present, and execution is deeper than observation. The
  E_MISSING_REQUIRED_EVIDENCE row does not fire (aggregate present); no other row predicate is true.
  This is the exact pattern of fixture C07: "Assert E; execution finding supported; ceiling invocation." ->
  "reasons={E_BASE_EXCEEDS_BOUNDARY}; fatal/gaps={}."
- evaluation_gaps = evaluation_gap_entries = {} (no gap row true, no profile gaps, no blocking counter entry).
- boundary_ceiling = observation (8.5: boundary, binding, target and context all pass).
- boundary_grounding = attributed (8.5 / 7: preserved).
- inherited_limitations = {LIM}: "boundary limitations" (8.1), and also the boundary is a source of the
  reason E_BASE_EXCEEDS_BOUNDARY ("sources: boundary and asserted-base findings", 8.6), so LIM is included
  under either clause; the execution finding's limitations are empty.
- Carried through: semantics_version, target, asserted_claim = E, recorder_relations = [],
  counter_evidence, evaluation_context, evaluation_scope; fatal_reasons = {}.

## 2. Case b1

Input: assert O; one base finding (observation; T; C; binding supported; semantic supported; basis
(P, observer-1); no limitations); boundary supported, target-bound, attributed, ceiling observation,
basis BD, limitations {LIM}; counter not-supplied; all capabilities evaluated; no gaps/inherited/fatal.

Derivation:
- B = {observation}: conditions 1-3 hold; condition 4: observation <= observation.
- Q(observation) = {}: no qualifier findings (8.1: PROV/IV only with a passing qualifier finding).
  SupportedClaims = {(observation, {})} = {O}. MaximalSupportedClaims = {O}.
- support_entries: one entry for O. 8.1: "a support entry containing the exact claim, the union of basis
  references used for its base, boundary, and qualifiers, and the limitations attached to those same
  premises." Section 13: "support_entries contains exactly one entry whose basis-reference set is the
  union of bd, its base finding's basis references, and any qualifier findings' basis references; its
  limitations are the union of those premises." Basis = {BD, (P, observer-1)}; limitations = {LIM}
  (boundary limitation) union {} (base) = {LIM}. (Compare C12: "The support entry also carries L-boundary.")
- asserted_claim_supported = true; counter does not block; verdict = accept (8.2).
- support_relations = {O: equal} (8.3: for each maximal supported claim, relation to the asserted claim;
  O is structurally equal to O; compare C01 "relations={I:equal}").
- substantive_reasons = {}; evaluation_gaps = evaluation_gap_entries = {}: no matrix row is true (boundary
  supported and bound; asserted-base aggregate present, bound, supported; no asserted qualifiers), no
  profile gaps, no blocking counter entry. Compare C01: "accept; fatal/reasons/gaps={}."
- boundary_ceiling = observation; boundary_grounding = attributed (8.5).
- inherited_limitations = {LIM}: "boundary limitations" and "every support-entry limitation" (8.1) both
  yield LIM. Compare C12: "inherited_limitations={L-boundary}".
- Carried through as in case a, with asserted_claim = O.

## 3. Case b2

Input: assert O; no base findings; boundary supported, target-bound, attributed, ceiling observation,
basis BD, limitations {LIM}; counter not-supplied; all capabilities evaluated; no gaps/inherited/fatal.

Derivation:
- B = {}: there is no aggregate base finding for any base (8.1 condition 1 cannot hold), and the
  boundary "MUST NOT create a positive base finding.  Observation itself requires a positive exact
  observation finding." (7). SupportedClaims = Maximal = support_entries = support_relations = {}.
- asserted_claim_supported = false; verdict = downgrade.
- substantive_reasons = {E_MISSING_REQUIRED_EVIDENCE}: "Asserted-base aggregate absent; source: none."
  The E_BASE_EXCEEDS_BOUNDARY row requires "a present asserted-base aggregate" and so does not fire; the
  boundary rows are false (supported, bound). Exact pattern of fixture C08: "Assert O; no base findings;
  ceiling observation." -> "downgrade; reasons={E_MISSING_REQUIRED_EVIDENCE}; fatal/gaps={}."
- evaluation_gaps = evaluation_gap_entries = {}.
- boundary_ceiling = observation; boundary_grounding = attributed (8.5: all boundary conditions pass).
- inherited_limitations = {LIM}, by the unconditional "boundary limitations" term of 8.1 and section 7's
  "An accept or downgrade result MUST preserve the boundary grounding status and its limitations."
  See AMBIGUITIES.json (b2): an alternative reading that ties boundary limitations to premise or
  reason-source status would give {} here; it is not adopted because the text lists boundary
  limitations as a standalone union term and restricts the exclusion to "unrelated failed findings".
- Carried through as in case b1.

## 4. Case c

Input: assert O; one base finding (observation; T; C; binding supported; semantic supported; basis
(P, observer-1); no limitations); boundary with status not-evaluated, grounding not-evaluated,
target_binding supported, ceiling_base observation (present), basis BD, limitations {LIM}; counter
not-supplied; evaluation_scope: boundary-grounding = not-evaluated, all other capabilities evaluated;
no gaps/inherited/fatal.

Derivation:
- Ingress: the status/grounding pairing is the valid one (section 6, quoted in 0); the present
  ceiling_base "is diagnostic carrier metadata only and is ignored by the Core algorithm" (6); the scope
  map is consistent (12, see 0). Not a reject.
- B = {}: 8.1 condition 3 fails ("the boundary finding is supported"). Section 7: "When status =
  not-evaluated, no base is added and the appraiser records E_BOUNDARY_NOT_EVALUATED." The observation
  finding, although positive, cannot enter B without a supported boundary.
  SupportedClaims = Maximal = support_entries = support_relations = {}.
- asserted_claim_supported = false; verdict = downgrade (8.2: safely interpretable, admissible, not
  exactly supported). Note 8.6: "Substantive reasons describe why evidence does not support the asserted
  claim.  Evaluation gaps describe assessments that were not performed." The boundary not-evaluated
  condition is a gap, not a substantive reason.
- substantive_reasons = {}: E_BOUNDARY_NOT_SUPPORTED requires status unsupported (false);
  E_EVIDENCE_NOT_BOUND (boundary) requires binding unsupported (false); E_BASE_EXCEEDS_BOUNDARY requires a
  usable boundary (false: 7 "Only status = supported ... makes ceiling_base usable"); the asserted-base
  rows are false (present, bound, supported); E_MISSING_REQUIRED_EVIDENCE false (present). No finding reasons.
- evaluation_gaps = {E_BOUNDARY_NOT_EVALUATED}: row "E_BOUNDARY_NOT_EVALUATED (gap)  Boundary status =
  not-evaluated; source: boundary finding." The second E_BOUNDARY_NOT_EVALUATED row (binding
  not-evaluated) is false (binding supported); it would in any case produce the same token.
- evaluation_gap_entries = one entry. 8.4: "Every Core-derived finding gap entry has the row's token, the
  input target and evaluation-context identifier, affected_claims={input.asserted_claim}, and the
  basis-reference and limitation sets of the aggregate that made the row true." Hence: token
  E_BOUNDARY_NOT_EVALUATED; target T; evaluation_context_ref C; affected_claims {O}; basis_refs {BD};
  limitations {LIM}; no current_scope_capability (8.5: "the optional current_scope_capability supplied
  on a profile gap"; this is a Core-derived entry, not a profile gap, so the component is absent).
  Representation note: the entry's member names follow the section 6 `profile_evaluation_gaps` record
  (`target, evaluation_context_ref, token, affected_claims, basis_refs, limitations`), since 8.5 states a
  gap entry "contains token, target and context scope, affected claims, basis references, limitations";
  the absent optional component is omitted, not null (REPRESENTATION.md: "Null represents unavailable,
  not an absent component").
- boundary_ceiling = unavailable (null): 8.5 "boundary_ceiling is the accepted ceiling only when the
  boundary finding, its target binding, target, and context all pass; otherwise it is unavailable."
  The input's ceiling_base is ignored (6).
- boundary_grounding = not-evaluated: 8.5 "boundary_grounding preserves the input grounding even when the
  boundary is unsupported." and 7 "MUST preserve the boundary grounding status". `not-evaluated` is a
  defined grounding class (section 2: "asserted-only, attributed, attested, or not-evaluated"); the value
  `unavailable` is reserved for the fixed rejection result (section 2: "The fixed rejection result uses
  unavailable, as specified in Section 8.4.").
- inherited_limitations = {LIM}: "boundary limitations" (8.1) and "limitations attached to findings
  that determine a reason or gap for the asserted claim" (8.1; the boundary determines the gap) both
  yield LIM. The observation finding's limitations are empty.
- Carried through: semantics_version, target, asserted_claim = O, recorder_relations = [],
  counter_evidence, evaluation_context, evaluation_scope (with boundary-grounding = not-evaluated
  preserved as supplied; 12: the capability value "MUST NOT create an ingress rejection, substantive
  finding, or evaluation gap" by itself, and the gap here comes from the boundary status row, not from
  the scope map); fatal_reasons = {}.

## 5. Summary table

| id | verdict | fatal | substantive_reasons | gaps | boundary_ceiling | boundary_grounding | inherited_limitations | supported_claims |
|----|---------|-------|---------------------|------|------------------|--------------------|-----------------------|------------------|
| a  | downgrade | {} | {E_BASE_EXCEEDS_BOUNDARY} | {} | observation | attributed | {LIM} | {} |
| b1 | accept | {} | {} | {} | observation | attributed | {LIM} | {O} (support entry basis {BD, (P, observer-1)}, limitations {LIM}; relation O:equal) |
| b2 | downgrade | {} | {E_MISSING_REQUIRED_EVIDENCE} | {} | observation | attributed | {LIM} | {} |
| c  | downgrade | {} | {} | {E_BOUNDARY_NOT_EVALUATED} (entry: affected {O}, basis {BD}, limitations {LIM}) | unavailable | not-evaluated | {LIM} | {} |

Set ordering in the emitted JSON is a representation choice (8.4: "The logical sets produced by Core are
order-independent."); support-entry basis references are listed boundary first, then base, following the
C01 format reference.
