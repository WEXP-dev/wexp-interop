# WEXP × EMILIA INTEROP-001 — limitations

Status: **REVIEW-READY PUBLICATION CANDIDATE — PUBLICATION NOT AUTHORIZED**

1. **Only one positive/hostile pair was tested.** The controlled intervention
   removes one meter-observation `action_caid` relation and updates only the
   derivative signature. The result cannot be generalized to other evidence,
   actions, facilities, mappings, or hostile changes.

2. **Positive WEXP semantic composition was not tested.** No frozen public
   EP→WEXP mapping constructs the complete Core `AppraisalInput`, so P and P-1
   remain `UNDERDETERMINED` and implementation input is `NOT CONSTRUCTIBLE`.
   This is not a WEXP rejection or implementation failure.

3. **The semantic planes remain distinct.** EMILIA lifecycle/outcome, WEXP
   appraisal, and CAID/action correlation are not interchangeable. The
   EMILIA distinction does not establish a WEXP verdict, and CAID equality or
   absence is not automatically WEXP semantic support.

4. **Physical truth is not established.** Authentication, exact binding,
   source checks, and a reproduced verifier result establish only their stated
   digital predicates. They do not prove that a physical effect occurred or
   that an observation was truthful.

5. **No conformance claim is made.** The pair is not a conformance suite, and
   neither WEXP nor EMILIA is certified or shown fully conformant by this work.

6. **No semantic-equivalence or full-interoperability claim is made.** The
   systems use different abstractions. Compatibility at a boundary does not
   establish equivalent meanings or general interoperability.

7. **No standardized mapping/profile exists in this experiment.** The missing
   bridge is a finding, not a current normative WEXP rule, adopted profile, or
   standards-body action.

8. **Future bridge design requires a separate experiment.** It must be
   independently authorized, specified, frozen, and tested. The non-normative
   requirements note is not evidence authority for INTEROP-001.

9. **EMILIA freeze timing has qualified provenance.** The expectation states
   `fixed_before_emilia_execution` and authenticated correspondence asserts
   the pre-run commitment. The expectation JSON has no intrinsic timestamp.
   The receipt, executed at `2026-08-21T02:41:04Z`, binds its exact hash; this
   supports ordering together with the correspondence, not from the
   expectation bytes alone.

10. **The EMILIA execution evidence is an external receipt.** Its hashes,
    linkages, results, shared checks, and public baseline files were verified,
    but this executor did not rerun EMILIA. Independent re-performance remains
    available from the pinned public repository.

11. **Raw process streams are absent.** The receipt supplies structured actual
    results and result digests but no raw stdout/stderr or invocation-level
    process capture. The candidate therefore preserves the receipt as the
    execution evidence and does not fabricate a local harness record.

12. **Later repository heads are not authority.** Reproduction must pin EMILIA
    commit `9a04bea7fe680345132f6f6251fdb9a63fd8aeb2` and the frozen WEXP semantic
    surface. Later heads may be recorded as metadata only.

13. **Public-only reproduction is required.** The current path requires no
    private WEXP or EMILIA dependency. Discovery of a private prerequisite
    would be a publication blocker and must be disclosed.

14. **Publication remains subject to review.** Branch A was selected from the
    frozen expectations and receipt, but no publication, public repository
    update, profile creation, release, or standards submission is authorized
    by this candidate.
