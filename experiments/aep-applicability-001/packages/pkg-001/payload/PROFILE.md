# AEP applicability mapping profile — proposal, revision 4

The immutable `profile_identifier` is the exact text atom
`urn:wexp:proposal:aep-applicability-001:profile:1:r4`.
This file, MAPPING.md, `profile-registry.json`, the pinned basis materials and
`prepare_inputs.py` define that revision. Session A freezes their bytes before
session B. A changed predicate, domain, atom rule or registry requires a new
profile revision; this identifier never follows a branch. This is a local
mapping proposal, not a collection verification profile or a registered EAT
profile. Core profile identities bind equality and registry revisions
(Core XML lines 366–374).

All Core citations below refer to the byte-identical retained
[`draft-sergeev-wexp-core-02.xml`](evidence/basis/specifications/draft-sergeev-wexp-core-02.xml),
SHA-256 `de983051a1c6ea51ea9b7f965fe9eabf2d97af92ab2f074781bd44e3f99c8782`.
`AEP draft` means the retained
[`draft-sokolov-rats-aep-composition-06.txt`](evidence/basis/specifications/draft-sokolov-rats-aep-composition-06.txt),
SHA-256 `a2561d39ddd1707d04df100137bdbff2bcde367a477e06e6068efe45572e1431`.
`AEP code` and sample citations refer to
[`aep-sandbox`](evidence/basis/aep-sandbox/) at
`f6c88be63c5aa12b8e8f6bf35a378a6a5fca9cd4`.

## Domain and exact target

The evidence domain is precisely the two retained sample documents and their
embedded action, outcome, credential, mandate, measurements and signature,
plus the pinned public `keys/trusted_issuers.json` for authentication.
Source code and the draft explain interpretation; they are not observations
of these actions. No live payment service, event collector, platform quote,
runtime trace or additional independent observer is supplied in this domain.
This is a bounded reading of the sample fields (each sample lines 1–59), not
a claim that no such evidence exists elsewhere. Discovery means completed
search of this declared domain only (Core XML lines 774–778).

For a validated packet `p`, define the target text atom as `aep-action:` followed
by compact JSON encoding of the ordered tuple
`[p.agent_pub, p.action.method, p.action.args.order_id, p.action.args.amount,
p.action.args.currency]`. The JSON is UTF-8, `ensure_ascii=False`, no spaces;
the amount must have exact integer type (not Boolean). This is the exact
refund-action specification in this two-packet domain, scoped to its producer
key, not a globally unique execution-occurrence identifier. No other packets
or repeated real-world executions are admitted by this revision. Extending
the domain requires a new profile with an occurrence-disambiguation rule.

All five values are extracted from integrity-protected packet content and
checked by the binding predicate below. a and b reuse the same signed packet;
c carries a different amount (samples lines 3–10, 54–58). Thus a and b have
one target, while a and c differ because 250 differs from 9000. An order/ticket
alone would collapse distinct action parameters. The required argument
binding is an added profile obligation (Core XML lines 264–268), in addition
to exact-target binding (Core XML lines 134–135). Outcome, refund ID, nonce,
submission ordinal and consumed-state are not parts of this action tuple.
The nonce is a signed receipt identifier in the basis material; its
application-state role is separate (AEP code `aep/package.py` lines 26–31,
43–44, 58; MAPPING.md).

## Claim and contexts

The asserted claim is always the typed pair `(execution, {})`, carried as
`{"base":"execution","qualifiers":[]}`. Its content is the reported execution
of the exact target action. Separately, the packet's outcome fields are
self-reported result data: `status=ok`, refund ID `RF-22317` or `RF-90001`
(samples lines 17–20). Neither signature validity nor presence of these data
establishes the execution base (Core XML lines 148–149, 358; AEP draft lines
117–126, 346–348).

The evaluation-context identifiers are the exact strings
`urn:wexp:aep-applicability-001:context:strict:r4` and
`urn:wexp:aep-applicability-001:context:attrib:r4`.
Both use the logical evaluation-time atom `unix:1750000100` and the singleton
profile set above. Their trust atoms are respectively
`urn:wexp:aep-applicability-001:trust:strict:r4` and
`urn:wexp:aep-applicability-001:trust:attrib:r4`, binding this section and the
pinned public trust-store bytes. No wall-clock reading enters the input.

Both contexts accept the public issuer-key mapping in the retained trust
store for **record attribution only**, not for a claim that an external
refund occurred. This acceptance is a local proposal assumption, not an
endorsement of the source's issuer. C-strict accepts boundary grounding only
at `attested`; C-attrib accepts `attributed` or `attested`. Grounding
admissibility is one gate of the boundary predicate and does not supply a
ceiling or make the boundary supported (Core XML lines 405–407).

## Predicates, findings and completed searches

`BIND(packet,target)` checks all of: (1) SHA-256 of the protected receipt core
equals its receipt hash; (2) the agent signature verifies over that core;
(3) action and outcome measurement digests recompute exactly; (4) the issuer
ID/key is in the pinned trust store and its credential signature verifies;
(5) the credential's principal ID equals the mandate's principal ID and that
principal key verifies the mandate signature; (6) the mandate's agent key and
label equal the packet signer key and label; (7) the signed action fields
have the required types and yield precisely the target tuple above.
The source mechanisms are `aep/package.py` lines 26–35, 95–111,
`aep/mandate.py` lines 149–160, `aep/keys.py` lines 66–72 and
`aep/canonical.py` lines 16–29. Session A actually runs these individual
checks; retained results are in `evidence/A-PREPARATION.json`.
This is evidence-to-target binding, not equality of mapper-written IDs.
It establishes what action is reported by the authenticated packet; it does
not authenticate the truth of the report (AEP draft lines 117–126).

The mandate's amount-cap and expiry checks and the consumed-state lookup
are **not** conjuncts of BIND: the relevant source code separates key binding
from scope/expiry (`aep/mandate.py` lines 158–167) and replay
(`aep/package.py` lines 128–133). Their exclusion from this historical
content-mapping predicate is justified in MAPPING.md. A failure of any BIND
conjunct prevents preparation; this revision does not fabricate a complete
input after upstream authentication failure (Core XML line 382).

Every candidate role is searched independently of the asserted claim (Core
XML lines 155, 357). The findings and absences for both samples are:

| Role | Explicit predicate/search and result |
| --- | --- |
| observation | The validated signed record reports the exact action and a result; BIND passes and the report is present (samples lines 5–20; `aep/package.py` lines 26–31, 99–111). This satisfies the narrow recorded/reported-event predicate: `target_binding=supported`, `semantic_validation=supported` (Core XML line 143). No external effect is thereby established. |
| intent | Search for a specific prior intention, approval, plan or decision for this exact amount/action. None is supplied. The mandate grants a capability rather than exact-action approval (`aep/mandate.py` lines 81–88); the resulting-report fields do not assert a prior decision. Aggregate absent; completed search, capability `evaluated` (Core XML lines 145, 775). |
| invocation | Search for material of an exact invocation crossing an observed invocation boundary. None is supplied in samples lines 1–59; a reported method and result are not such a trace. Aggregate absent, search `evaluated` (Core XML lines 147, 775). |
| execution | The action/outcome report is a candidate execution assertion (samples lines 5–20). BIND passes. Assessing actual execution at a controlled execution-relevant boundary needs runtime/service measurement and its boundary-control context; none is supplied. That substantive occurrence assessment cannot run, so `semantic_validation=not-evaluated`, with the explicit unavailable-material limitation and Core-derived gap, not `unsupported` and not positive support (Core XML lines 149, 358–359, 639–640). |
| PROV(execution) | Search for execution-linked provenance whose execution association can be assessed. None is supplied. Credential/mandate identify authority and signer (`aep/mandate.py` lines 45–97, 149–160), not the runtime execution chain. Aggregate absent; discovery `evaluated` (Core XML lines 162, 775). |
| IV, each base | Search for a candidate independently produced assessment of this exact content. None is supplied in the packet domain (samples lines 1–59). Credential and mandate signers supply identity/authority, not an independent assessment of these refund actions (`aep/mandate.py` lines 45–97). All IV aggregates absent; `independent-verification=evaluated` records completed candidate search, not validated independence (Core XML lines 167, 363, 775–778). |

If a future domain supplies an IV candidate, a new profile revision must
specify and actually assess administrative, operational and technical
independence, and retain `supported`/`unsupported`/`not-evaluated` according
to the assessment performed (Core XML lines 167, 363, 694). This revision
does not manufacture an unevaluated IV aggregate solely because no source
was found (Core XML lines 775–778).

The external composition procedure completes by classifying this as one
uncomposed target, with no composition claim requested; `composition=evaluated`
and no composition marker gap are supplied. Authenticity was evaluated by
BIND. This is the scope encoding for these completed procedures, not evidence
of a chain or a capability-based support rule (Core XML lines 779–782).
Counter-evidence inspection of this domain finds no supplied allegation
against the truth of the exact execution assertion; use the exact
`not-supplied` sentinel with empty sets (Core XML lines 364–365, 776).
An amount beyond authority is not by itself proof of non-execution
(Core XML lines 149, 365; AEP code `aep/mandate.py` lines 162–167).

## Boundary finding: content, grounding, status and ceiling

Exactly one boundary aggregate is present for every input (Core XML line 361).
The **agent's claimed boundary content** is that `issue_refund` for the exact
order, amount and currency produced an external refund, represented in its
own report by `status=ok` and its `refund_id` (samples lines 5–20). The external
effect interpretation is the proposition under appraisal, not a witnessed
boundary. No explicit service endpoint, observer or controlled execution
boundary is identified by those fields. The draft explicitly says a success
assertion without effect evidence remains an application-layer claim
(AEP draft lines 346–348).

Grounding is derived as `attributed`: BIND validates the signed description
against an identity accepted for this purpose by the context. That is the
signer's description of the claimed effect boundary; it is not proof of
boundary control. There is no boundary-grounding profile or its supporting
platform/boundary material in the admitted sample domain, hence there is no
basis for `attested` (samples lines 1–59; Core XML line 405). The existence of
a general RATS composition discussion does not supply such material for
these packets (AEP draft lines 124–126, 178–195).

The boundary predicate has separate gates:

1. BIND binds this authenticated boundary description to the exact target.
2. The context accepts the derived grounding class.
3. The supplied material identifies an evidence-producing vantage, its
   control/coverage for the target, and why a particular content depth is
   warranted. Mere presence of a description is not sufficient.

Gate 3 is a **completed sufficiency assessment of the packet material**:
required control/vantage/coverage material is absent, so it fails in both
contexts. Gate 2 fails for C-strict and passes for C-attrib. Thus both
aggregates have `status=unsupported`, `target_binding=supported`,
`grounding=attributed` and **no `ceiling_base`** (Core XML lines 360–362,
404–407). This differs from execution's unperformed occurrence assessment:
we can determine that the available boundary description fails this
acceptance predicate, while we cannot assess the unobserved execution.
The unavailable observation of execution is recorded as its own gap.

This proposal deliberately makes no claim that an attributed reporting
boundary with observation ceiling has been accepted. Observation has its
own positive record predicate above, but a positive base cannot invent a
usable boundary (Core XML lines 404, 415–420). All aggregates, including the
unsupported boundary, are scoped to top-level target/context, and the basis
ref points to the actual authenticated record (Core XML lines 360–361).

## Logical identity, carrier and vocabularies

Targets, context IDs, time and trust atoms compare by exact Unicode scalar
text. There is no URI lookup, case-folding, Unicode normalization or aliasing.
The target's compact tuple-encoding rule produces that text before Core.
Applied profile IDs use the same text equality. A basis or limitation atom
is an ordered two-element array `[profile_identifier, local_value]`;
both components use exact text equality. This carrier represents the
profile-scoped logical pair, not an unordered set (Core XML lines 373–377).

The only basis local values are `aep-file:sha256:<lowercase hex>` for the
exact bytes of the retained good or exceed-scope sample. Resolution is by
the sample hashes in `SOURCE-PINS.json`. A reference includes the embedded
credential, mandate, protected nonce and outcome, but its identity does not
vary by submission, context, wall-clock or consumed-state. The reference
is not by itself proof of execution (Core XML line 358).

These are the complete limitation local values:

| Local value | Meaning and application |
| --- | --- |
| `bounded-two-packet-domain` | Only the declared two-packet evidence domain was searched; inherited on all inputs. |
| `self-report-is-not-external-effect` | Authenticated action/result content remains self-report; observation and execution findings. AEP draft lines 117–126, 346–348. |
| `boundary-control-not-established` | The available description supplies no accepted control/vantage/coverage proof; boundary finding. |
| `no-boundary-grounding-profile` | No applied profile and material establish attested boundary grounding in this domain; boundary finding. |
| `execution-assessment-material-unavailable` | No runtime/service measurement permits evaluation of actual exact execution; execution finding. |

All limitation atoms are scoped by the immutable profile ID. They are not
reason tokens and do not invent Core gaps. They are retained according to
the normative premise/diagnostic union rules (Core XML lines 436–437).

The exact registry revision is `profile-registry.json`. The own-token
registries are explicitly empty for **substantive**, **evaluation-gap** and
**fatal** categories: no custom reason/gap/fatal token is emitted. Only the
Core status-derived diagnostics are used; their registry is bound by
`semantics_version=wexp-core-2`. This avoids treating explanatory prose or
limitation atoms as unregistered tokens (Core XML lines 366–369, 374).
There are no custom relation tokens or evaluation-scope extension keys.

JSON objects carry records; all specification set collections are unordered,
duplicate-free arrays. Qualifier sets, findings, basis/limitation sets,
counter entries and evaluation-scope map entries compare by their logical
keys and members, not array order. An atom pair remains ordered. Claims use
`base` and a mathematical `qualifiers` set. `evaluation_scope` is carried as
an array of `{capability,status}` records (Core XML lines 373–377, 758–780).
No case ID, wall-clock, submission ordinal, native verdict or consumed-state
is inserted in `AppraisalInput` (complete shape: Core XML lines 269–356).

The non-normative carrier shape was checked against only the input-construction
function `normalize()` in the base repository's old proposal
`docs/proposals/wimse-core02-replay-001/producer.py`, lines 11–45.
Its semantic choices were not adopted. No Core appraiser or its results
were read or run by A.
