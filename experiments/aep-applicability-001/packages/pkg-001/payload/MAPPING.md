# Mapping rationale and exclusions — revision 4

This is the proposed mapping of two fixed sample records. The rules are in
[PROFILE.md](PROFILE.md); this file explains their evidentiary scope. Source
short names and pins are defined there and in [SOURCE-PINS.json](SOURCE-PINS.json).
Line citations mean one-based lines in the exact retained source bytes,
including blank lines and form-feed page breaks in the AEP text.

## What is asserted and what is established

The sample action is `issue_refund` on `ORD-4471`, with 250 EUR (good) or
9000 EUR (exceed-scope); their result fields say `ok` and respectively
`RF-22317` / `RF-90001` (each sample lines 5–20). Both use a mandate capped
at 1000 (each sample lines 36–52). These are source facts about the records,
not observations that refunds occurred.

The candidate execution assertion means the exact parameterized action
executed. The outcome is separate self-report content. The AEP draft calls
unsupported success an "application-layer claim" (lines 346–348), and says
platform anchoring does not independently observe the action or external
effect (lines 121–126). Therefore the local mapping authenticates the record
and its exact-action association without promoting signature or outcome into
execution support (Core XML lines 134–135, 148–149, 264–268, 358–359).

The signature covers the protected body, including action, outcome and nonce
(`aep/package.py` lines 26–31, 46–62); measurements are explicitly an internal
consistency check (`aep/package.py` lines 104–111). Session A rechecks those
facts and the identity chain with public keys. The resulting positive
observation finding means this exact action was reported (Core XML line 143).
It does not certify the report's world truth (AEP draft lines 103–126).

## Boundary: signed description is not control evidence

The profile reads the reported refund result as the agent's claim of an
effect in an external refund system, not an observation made by this trial.
The fields identify an order and refund, but do not identify a service
observer or its controlled vantage (samples lines 5–20). Authentication
supports attribution to the accepted signer. It does not supply an applied
boundary-grounding profile, whose absence is explicit here (Core XML lines
405–406; AEP draft lines 178–195).

The boundary aggregate is always present and target-bound (Core XML lines
360–361). The independently checked acceptance gates are: binding, accepted
grounding, and sufficient material establishing control/coverage and a
warranted depth. The last gate fails in both contexts. C-attrib accepts the
grounding but not the missing control proof; C-strict also refuses that
grounding class. No ceiling is supplied because this profile has not
justified one (Core XML lines 362, 404–407). The same unsupported status
does not hide the different grounding-admission diagnostics, which remain
outside the Core result in `evidence/MAPPING-DIAGNOSTICS.json`.

## Explicitly excluded propositions

| Material / proposition | AEP citation | Independent reason for its placement |
| --- | --- | --- |
| Consumed-state membership of the nonce | The draft states "Freshness is also separate" (lines 509–511); its V6 separates reused action identifiers from platform appraisal (lines 585–589). The sandbox checks `consumed` at `aep/package.py` lines 128–131 and writes it only after ALLOW with `--consume` at `verify.py` lines 62–71. | This is a verifier's stateful applicability predicate for a subsequent submission. In this profile the assertion is historical execution of the action described by the unchanged signed packet. Remembering receipt reuse neither observes that historical execution nor supplies evidence of its non-occurrence. Thus the evolving consumed set is retained with native runs, outside normalized historical content evidence. This argument is bounded to this claim and mapping; it says nothing universal about freshness of other claims. |
| The nonce as a signed evidence identifier | The source calls nonce the "per-action one-shot id" (`aep/package.py` lines 43–44), puts it in the signed body (lines 26–31, 58, 62), and the draft distinguishes identifier utility from proof of uniqueness (lines 328–330). | Its stable value is part of the authenticated basis file and helps identify which evidence was submitted. It is not treated as a world-unique execution ID or as a replacement for exact parameter binding. The file digest identifies evidence bytes; consumed-state is a separate mutable relation to those bytes. a/b use the same basis reference and target. |
| Scope / maximum amount | The draft says the "Relying Party separately checks" authority and scope (lines 526–530). The source's `scope_ok` compares method and amount to the grant (`aep/mandate.py` lines 104–129), and returns `scope_violation` after successful key binding (lines 158–163). | Whether the principal permitted an amount is a proposition about authority. An unauthorized action may still execute; an authorized action may fail to execute. The selected execution claim therefore neither includes nor negates authority validity. No failed execution aggregate or counter-evidence entry is inferred solely from exceeding the cap (Core XML lines 145, 149, 364–365). The actual native scope result is retained separately. |
| Mandate for agent identity binding | The source checks the credential and mandate signatures, principal linkage, and agent key/label before scope (`aep/mandate.py` lines 149–163); signing a mandate is not itself platform appraisal (AEP draft lines 173–176). | These verified links do enter BIND: they associate the protected action report with the accepted agent identity. This distinct use does not import the mandate's scope decision, grant general credibility to the agent's statements, or establish an execution boundary (Core XML lines 135, 358, 405). |
| `verify.py` ALLOW / DENY | `verify.py` prints the result and returns 0 or 2 (lines 60–71); the first failure determines the reason (`verify.py` lines 10–12; `aep/package.py` lines 76–78, 113–133). The draft separates application authorization decisions from trustworthiness claims (lines 144–151). | The native verdict combines several checks, including stateful replay and scope, under a different decision question. Importing that aggregate as execution evidence would conflate authorization/applicability with witnessed content. Core receives the underlying authenticated record predicates; the native verdict is an external observation in the comparison report. |

None of these exclusions is justified merely by implementation invisibility.
Each follows from the chosen assertion's content and from the distinct
proposition evaluated. Core itself leaves authorization validity outside its
execution content base (Core XML line 149), while requiring a profile to state
its extra input-binding obligations (Core XML lines 264–268).

## Role search and omitted aggregates

PROFILE.md records the independent domain search for all four bases, PROV
and IV. A broad capability grant is not an exact-action prior approval
(`aep/mandate.py` lines 81–88); credential/mandate signatures are not independent
observations of the reported refund (`aep/mandate.py` lines 45–97; samples
lines 26–52). No role-appropriate intent, observed-invocation, execution-
provenance or IV candidate is present in this bounded domain. Their
aggregates are absent, and the completed search is represented in
`evaluation_scope` (Core XML lines 775–778). The execution candidate is the
self-report; evaluation of actual execution lacks requisite measurement,
so its aggregate remains `not-evaluated` with a retained limitation and a
Core-derived gap (Core XML lines 359, 639–640).

Binding applies to the record's exact action content even where substantive
execution evaluation could not run. All findings retain top-level scope;
an absent or negative role is not manufactured at another target (Core XML
line 360). An empty IV finding set is not a claim of verified independence.
Were a candidate supplied, its independence would require a separate actual
assessment (Core XML lines 167, 363, 694).

## Scope of conclusions

The cases are a=first good submission, b=repeat good submission after consume,
c=first exceed-scope submission. The six inputs differ only by the two
selected contexts and two authenticated source records; case identities and
state-transition data remain outside Core. Session B will independently
derive all twenty required appraisal components from these frozen inputs
and Core XML lines 584–612. No appraiser result establishes this mapping's
correctness; this is a proposal about that mapping, not an AEP author review
or a collection experiment.

H1/H2 concern this selected mapping and its handling by two implementations.
Equal appraisals after excluding consumed-state do not establish that
freshness never affects support for other execution claims. The source
draft's own freshness requirements address different composition claims
(AEP draft lines 318–326, 509–511); those claims are not silently substituted
for the bounded historical action assertion here.
