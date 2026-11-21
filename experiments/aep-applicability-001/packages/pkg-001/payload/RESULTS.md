# AEP applicability proposal — retained local observations

## Status and observed comparison

**PROPOSAL, level 1, request revision 4.** All six inputs were run locally
through both pinned appraisers. The complete ref/check comparison has zero
component mismatches. The complete expected/ref and expected/check comparisons
each have **six mismatches**: `boundary_ceiling` is the string `"unavailable"`
in B and JSON `null` in both implementations, in every case. The other 114
of 120 components agree with B for each implementation. H1 and H2 match B's
frozen component expectations in both contexts.

The discrepancy is preserved in [comparison.json](comparison.json); no input,
expectation or observed value was repaired or coerced. In particular, this
is not a report of complete expected-result agreement. B explicitly chose
the string representation in [AMBIGUITIES.json](AMBIGUITIES.json), B-RC-01.
Core defines a logical unavailable value while leaving its encoding to a
result carrier (Core XML line 581; output rule at line 611). This trial records
the carrier-value mismatch and does not adjudicate an implementation defect.

## Frozen chronology and role separation

| Role | Local commit | Commit time, UTC | Activity |
| --- | --- | --- | --- |
| A | `8af5aa6f74e8209866a87970ada87e5c3a57e14a` | `2026-11-09T13:54:51Z` | Profile, mapping, source checks and six inputs. |
| B | `6a519c75151da620920bb4308837c53be67b63c8` | `2026-11-09T14:05:26Z` | Twenty-component expectations and H1/H2, frozen before C. |
| C | The later commit containing this file and RUN-RECORD.json | Read the enclosing Git commit object | Native and Core runs, comparison, retained-package checks. |

C's native sequence ran from `2026-11-09T14:13:06.901218Z` to
`2026-11-09T14:13:07.899762Z`; Core runs followed. [RUN-RECORD.json](RUN-RECORD.json)
retains each command's actual start/end times. Thus B preceded every C run.
A and B did not import or execute either Core appraiser or read/use their
implementations or outputs. The role receipts and whitelist are in
[HANDOFF.md](HANDOFF.md), `evidence/A-SESSION.json` and
`evidence/B-SESSION.json`. B's read-only hash helper and C's checker helper
are disclosed as support within those roles. The coordinator reviewed A's
profile/input structure, reviewed C's runner and authored this report.
These are separate AI role contexts under one operator on a shared
filesystem; the separation is procedural, not an OS sandbox guarantee.

## Native verifier observations, separate from mapping and Core

Every native command used `--now 1750000100`; actual wall-clock times were
recorded separately. A fresh C checkout had a newly created empty
`state/consumed_nonces.txt`, independent of A. a and b ran sequentially with
`--consume`; c was the first submission of its sample and omitted `--consume`.
The state path is tied to the checkout by the retained source
[`verify.py`](evidence/basis/aep-sandbox/verify.py), lines 24–26, 29–38, 49–71.

| Case | Exact observed native verdict | Reason | Exit code | State transition |
| --- | --- | --- | --- | --- |
| a | ALLOW | none | 0 | empty → `aep-nonce-0001` |
| b | DENY | `replayed` | 2 | unchanged |
| c | DENY | `scope_violation` | 2 | unchanged |

[AEP-OUTCOMES.json](evidence/AEP-OUTCOMES.json) preserves stdout/stderr and
return codes; `evidence/aep/` preserves their exact raw bytes and six
before/after state snapshots. The return-code and consumption branches are
`verify.py` lines 62–71; the exact replay token is
[`aep/package.py`](evidence/basis/aep-sandbox/aep/package.py) lines 128–133;
the scope token is [`aep/mandate.py`](evidence/basis/aep-sandbox/aep/mandate.py)
lines 163–164. These are local observations of the pinned verifier, not
evidence that a refund occurred. The source draft distinguishes a success
assertion from observable effect evidence (AEP-06 text lines 346–348).

The separate mapping column records that the grounding gate fails in
C-strict and passes in C-attrib, while the profile's material-sufficiency
boundary gate fails in both. Mapping diagnostics were frozen in A in
[MAPPING-DIAGNOSTICS.json](evidence/MAPPING-DIAGNOSTICS.json). Admission of
attributed grounding is not sufficient for a supported boundary or a
ceiling (Core XML lines 404–407). The invocation-only
`evidence/PROFILE-CATALOG.json` represents A's empty registry in the
appraisers' API format; no semantic entry or normalized-input field was added.

## Core appraisal observations and all mismatches

All twelve Core processes exited zero and returned all twenty components
(required components: Core XML lines 587–610). All six results from each
implementation report `downgrade`, `asserted_claim_supported=false`, empty
support/maximal/support-entry/relation sets, `boundary_grounding=attributed`,
the sole substantive reason `E_BOUNDARY_NOT_SUPPORTED`, and the sole gap token
`E_BASE_NOT_EVALUATED` with one exact scoped gap entry. The result rules are
Core XML lines 415–420, 448–451, 457, 579, 611, 621–622 and 639–640.
All five applicable limitation atoms are retained under the union rule
(Core XML line 437); exact values are in the saved results and B derivation.

| Input | B `boundary_ceiling` | ref | check | Other components agreeing with B |
| --- | --- | --- | --- | --- |
| a-strict | `"unavailable"` | `null` | `null` | 19/19 |
| b-strict | `"unavailable"` | `null` | `null` | 19/19 |
| c-strict | `"unavailable"` | `null` | `null` | 19/19 |
| a-attrib | `"unavailable"` | `null` | `null` | 19/19 |
| b-attrib | `"unavailable"` | `null` | `null` | 19/19 |
| c-attrib | `"unavailable"` | `null` | `null` | 19/19 |

This table enumerates every expected/ref/check mismatch. Ref and check agree
on 120/120 components. Their raw JSON, stderr, exit-code files and module
metadata remain under `evidence/core/{ref,check}/`. Comparison uses typed
set equality, retaining ordered scoped atom pairs and distinguishing Boolean
from number; it does not depend on JSON array ordering (Core XML lines
373–377, 581). It also keeps `null` distinct from the text `unavailable`.

## Six results, selected components

Values below are read from the saved outputs `evidence/core/ref/<input>.stdout.json` and
`evidence/core/check/<input>.stdout.json`; for every input and every column the two
implementations return identical values. `boundary_ceiling` is JSON `null` in both
implementations, which they use as the carrier encoding of the logical unavailable value
(see the mismatch table above). The last column is the `status` of the
`independent-verification` entry of `evaluation_scope`: it records that the candidate search
was completed, not that independence was validated (PROFILE.md, role table).

| Input | verdict | boundary_grounding | boundary_ceiling | substantive_reasons | evaluation_gaps | evaluation_scope[independent-verification] |
| --- | --- | --- | --- | --- | --- | --- |
| a-strict | `"downgrade"` | `"attributed"` | `null` | `["E_BOUNDARY_NOT_SUPPORTED"]` | `["E_BASE_NOT_EVALUATED"]` | `"evaluated"` |
| b-strict | `"downgrade"` | `"attributed"` | `null` | `["E_BOUNDARY_NOT_SUPPORTED"]` | `["E_BASE_NOT_EVALUATED"]` | `"evaluated"` |
| c-strict | `"downgrade"` | `"attributed"` | `null` | `["E_BOUNDARY_NOT_SUPPORTED"]` | `["E_BASE_NOT_EVALUATED"]` | `"evaluated"` |
| a-attrib | `"downgrade"` | `"attributed"` | `null` | `["E_BOUNDARY_NOT_SUPPORTED"]` | `["E_BASE_NOT_EVALUATED"]` | `"evaluated"` |
| b-attrib | `"downgrade"` | `"attributed"` | `null` | `["E_BOUNDARY_NOT_SUPPORTED"]` | `["E_BASE_NOT_EVALUATED"]` | `"evaluated"` |
| c-attrib | `"downgrade"` | `"attributed"` | `null` | `["E_BOUNDARY_NOT_SUPPORTED"]` | `["E_BASE_NOT_EVALUATED"]` | `"evaluated"` |

## H1 and H2 by component

Each row below holds separately in C-strict and C-attrib and for B, ref and
check. H1 compares a/b; H2 compares a/c. The input equalities were checked
from retained files, not assumed. The complete evidence and per-context
checks are in [HYPOTHESES.json](HYPOTHESES.json) and [comparison.json](comparison.json).
The complete-result identity requirement is Core XML lines 581 and 746;
opaque target/basis equality and scoped gaps are defined at lines 374 and 579.

| Component (Core XML declaration line) | H1 a/b | H2 a/c |
| --- | --- | --- |
| semantics_version (588) | equal | equal |
| verdict (589) | equal | equal |
| fatal_reasons (590) | equal | equal |
| target (591) | equal | different |
| asserted_claim (592) | equal | equal: `(execution,{})` |
| asserted_claim_supported (593) | equal | equal |
| support_entries (594) | equal | equal |
| supported_claims (595) | equal | equal |
| maximal_supported_claims (596) | equal | equal |
| support_relations (597) | equal | equal |
| boundary_ceiling (598) | equal | equal within each carrier |
| boundary_grounding (599) | equal | equal |
| recorder_relations (600) | equal | equal |
| substantive_reasons (601) | equal | equal |
| evaluation_gaps (602) | equal | equal |
| evaluation_gap_entries (603) | equal | different: exact target and basis reference |
| counter_evidence (604) | equal | equal |
| inherited_limitations (605) | equal | equal |
| evaluation_context (606) | equal | equal within the same context |
| evaluation_scope (607) | equal | equal |

H1 passes 20/20 components per context and result source. H2 matches the
predicted pattern of eighteen equal and two different components per context
and result source. No support-entry basis difference is present because those
sets are empty; the carried basis difference occurs in the structured gap.
H1/H2 matching does not remove the separate B/ref/check carrier discrepancy.

## Actually performed local checks

| Check | Observed result | Meaning |
| --- | --- | --- |
| A preparation | PASS | Exact sample fields and all ten binding checks per packet; same mandate. See `evidence/A-PREPARATION.json` and its source-line references. |
| B freeze validation | PASS | Whitelist/input hashes, six complete expected results and 120 component derivations; no Core execution. |
| C preflight and post-run freeze checks | PASS | A/B files match their original commit bytes; six input files were not rebuilt. |
| Native sequence | Three predictions matched | Exact preserved native outputs above; separate from Core support. |
| Saved ref/check outputs | 12 complete outputs, all process exit codes 0 | Ref/check agree on 120/120 components. |
| B expected/ref and expected/check | Six mismatches each | One `boundary_ceiling` carrier-value mismatch per input; full expected-result agreement is false. |
| `verify_proposal.py` | PASS | Full manifest integrity, A/B freezes and Git blobs, six inputs, six expectations, twelve saved outputs, exact three-column reports and component/H1/H2 comparisons. A PASS accurately retains the mismatches; it does not erase them. |
| `catalog.py --check` | PASS, exit 0; four packages | Existing collection preservation only. |
| `verify_collection.py` | PASS, exit 0; four packages and local links checked | Existing collection preservation only; `experiment_execution_performed=false`; exact link count is in the retained output. |

The collection checks first failed in system Python because its installed
`jsonschema` did not export `Draft202012Validator`; both exit-1 transcripts
are retained as `evidence/collection/attempt-1-system-*`. A dedicated
`collection-venv` then installed the unchanged repository's
`requirements-verification.txt`. The first dependency-equipped link check
found that the frozen source README's relative `LICENSE` link had no file
at that copied location; its failure is retained as
`evidence/collection/attempt-2-*`. C added a byte-identical copy of the
pinned source license at `evidence/basis/aep-sandbox/LICENSE`, documented in
`evidence/C-SOURCE-ADDITIONS.json`. No frozen A/B file or collection code was
changed. The final collection transcripts and exact commands are
`evidence/collection/{catalog,collection}.{stdout.json,stderr.txt,rc.txt}`
and `evidence/collection/commands.json`.

The separate proposal check is retained at
`evidence/verification/proposal.{stdout.json,stderr.txt,rc.txt}` and confirmed
read-only after final manifest sealing. Its summary explicitly reports
`expected_results_match=false`, mismatch counts 6/6/0 and matching H1/H2.
This distinguishes package integrity/reporting accuracy from agreement
with B. Neither collection PASS validates this proposal; neither the local
checks nor this bounded result assert full Core conformance (Core XML
lines 751–757). No historical collection experiment was rerun.

## Reproduction, publication and conclusion boundary

`independent_reproduction: not-performed`. Only the described local checks
were performed. Publication was not performed; `public_carrier: null`.
The local commits are not `github-commit` carriers. No push, PR, release or
email was made; no collection record or verification profile was assigned,
and the closed schema list and existing experiments were not extended.

H1/H2 test this selected mapping and its handling by two implementations.
Equality after excluding consumed-state does not establish that freshness
never affects support for other execution claims. This limit is consistent
with the AEP draft's separate composition freshness requirements (AEP-06
lines 318–326) and applicability statement (lines 509–511). The action tuple
is restricted to the profile's two-packet domain; no general occurrence
identity or complete-world discovery claim is made (Core XML lines 134–135,
774; PROFILE.md).

The AEP source and draft pins and their authorship are retained in
[SOURCE-PINS.json](SOURCE-PINS.json) and [LICENSES/](LICENSES/README.md).
AEP-author review was not performed; agreement to participate was not
requested. AI-assisted same-operator review is disclosed and is not attributed
to the AEP author.
