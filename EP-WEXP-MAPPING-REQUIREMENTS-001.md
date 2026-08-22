# EP-WEXP-MAPPING-REQUIREMENTS-001

STATUS:

**FOLLOW-ON DESIGN INPUT MOTIVATED BY INTEROP-001**  
**NOT PART OF CURRENT EXPERIMENT**  
**NON-NORMATIVE**  
**NOT USED TO DERIVE THE RESULT OR P/P-1 EXPECTATIONS**

## Purpose and authority boundary

This note lists only the functions that a possible future EP-to-WEXP mapping
would have to define. It does not define that mapping, select normative values,
repair the frozen experiment, or supply evidence authority for INTEROP-001.

The current pair remains governed by its already frozen fixture bytes and WEXP
expectation. Nothing here may be used to turn either frozen `UNDETERMINED`
reading into a determinate appraisal.

## Required mapping functions

| ID | Function a future mapping must define |
| --- | --- |
| M-01 | **WEXP asserted target construction:** define how the eligible EP identity and evidence fields construct the exact typed WEXP asserted target, including a defined non-constructible outcome when construction prerequisites are absent. |
| M-02 | **CAID namespace:** identify the CAID namespace or namespaces admitted by the mapping and how their authority and version are pinned. |
| M-03 | **CAID normalization:** define whether normalization occurs, the exact normalization function if it does, and the disposition of values outside its domain. |
| M-04 | **CAID equality:** define the equality relation applied to CAIDs after any permitted normalization and the treatment of ambiguous or non-comparable identifiers. |
| M-05 | **CAID issuer scope:** define which issuer or authority scope makes a CAID usable for the mapped claim and how that scope is evidenced. |
| M-06 | **Action / operation / receipt relation:** define the required identity and correlation predicates among the action, operation, authorization or receipt, nonce, facility or resource, and any associated digests. |
| M-07 | **Authenticated meter observation role:** define which WEXP input, premise, qualifier, boundary fact, or other typed role an authenticated meter observation may occupy; authentication alone must not silently imply semantic truth. |
| M-08 | **Meter `action_caid` premise:** define whether the meter observation's `action_caid` is a required exact-binding premise and, if so, the exact predicate it must satisfy. |
| M-09 | **Effect-to-execution predicate:** define the evidence predicate, timing relation, and identity binding by which an observed effect may support a typed WEXP execution claim. |
| M-10 | **Accepted boundary:** define the accepted evidence or execution boundary against which the mapped claim is appraised. |
| M-11 | **Ceiling:** define how the mapped evidence and boundary determine the maximum supportable WEXP claim ceiling. |
| M-12 | **Grounding:** define the facts and validation predicates required to ground the mapped target and claim. |
| M-13 | **IV independence predicate:** define the exact WEXP independent-verification predicate and the evidence required to establish it; an EMILIA role label alone must not satisfy it. |
| M-14 | **Source/control-domain independence:** define how source identity, keys, operators, control domains, and relevant common dependencies establish or fail to establish the independence required by the selected WEXP claim. |
| M-15 | **Missing `action_caid` disposition:** define the typed treatment of a missing meter `action_caid`, distinguishing non-constructibility, a gap, counter-evidence, downgrade, rejection, or another already authorized WEXP result. |
| M-16 | **Counter-evidence treatment:** define which EP facts constitute WEXP counter-evidence, how conflicts are resolved, and how absence of evidence differs from evidence against the claim. |
| M-17 | **Evaluation scope:** define the exact evaluation scope, including time, facility or resource, operation, evidence set, and claim set. |
| M-18 | **Complete `AppraisalInput` construction:** define a total, versioned construction procedure for every required Core input field, together with fail-closed diagnostics for any field that cannot be constructed. |

## Non-selection statement

No normative value, mapping direction, verdict, profile identifier, or
implementation behavior is selected here. In particular, this note does not
establish that CAID correlation is WEXP semantic support, that an EMILIA
independent observer satisfies WEXP independent verification, or that measured
effect establishes a WEXP execution claim.

Status remains **FOLLOW-ON DESIGN INPUT MOTIVATED BY INTEROP-001** until
separately authorized. It is not part of the frozen experiment and was not
used to derive the result.
