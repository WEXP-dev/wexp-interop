# WEXP derivation for positive/hostile pair 001

This record derives the WEXP expectation before any WEXP or EMILIA
implementation is run. It does not import Iman's rehearsed EMILIA lifecycle
outcomes and does not use an engine as an oracle.

## Frozen inputs

- Published Core: `draft-sergeev-wexp-core-01` / `CORE-01-FROZEN-001`,
  authoritative XML SHA-256
  `84c0a16467585c29925339a10dd287c2e67bfe21ed592826254bf424dc24f56d`,
  at `WEXP-dev/wexp-spec@b28a46e7764c2ef14decc35394f21278fca9c988`.
- Known issues: `CORE-01-KNOWN-ISSUES-001`, SHA-256
  `25c703dd876f717163e1919e71ccab7e11ba8c90152756bf8933852ea3c5b60f`.
- Representation contract: `CORE-01-REPRESENTATION-CONTRACT-001`, SHA-256
  `2da2245065ceced20ebd741b2e718935181dbc2958c95f338874e4f2bc79a38f`.
- Frozen WEXP reading: SHA-256
  `a185e6760de149375e657b1429adc1ea329ed9f9705b9d1c2b505dcc8e3ea984`.
- P fixture: SHA-256
  `b552da51858d0256a562e800a81a870435d6e136c9bc28833b962b6d3723fb3e`.
- P-1 fixture: SHA-256
  `67556d28d272b4b01a73e1c1465248644dd7a05460fc149aa77df92cf36403a0`.

The WEXP specification head remained at the frozen commit. Public
`wexp-vectors` and `wexp-ref` advanced after the prior freeze to
`2da7309d75762e4cf1e83b86bd606f4d473b1638` and
`3738c6d7767e5fafb0a97fc28336e3236761b3e6`, respectively. Those successors
are tooling/corpus state, not the source of this expectation. They were observed
and excluded; the frozen authority was not silently repinned.

## Authority order and rules applied

1. Core §1.2 places evidence parsing, authentication, semantic validation, and
   exact-target binding in an applicable profile. Core appraisal begins only
   after those steps produce one complete logical AppraisalInput.
2. Core §4.1 makes the exact action target opaque to Core. Correlation hints,
   record identifiers, timestamps, common payloads, and common signers do not
   establish target equality unless a profile defines and validates that rule.
3. Core §4.2 keeps observation, intent, invocation, and execution independent.
   Invocation or dispatch is not execution; a durable external effect is not a
   fifth Core content base.
4. Core §4.3 makes IV exact-base and trust/profile-relative. A separate key,
   role label, or control-domain label alone does not establish WEXP IV.
5. Core §6 requires the complete normalized input, including target, asserted
   claim, evaluation context, boundary, base and qualifier findings,
   counter-evidence, scope, gaps, limitations, and fatal conditions. Presence of
   evidence, a signature, or a digest is insufficient for a passing finding.
6. Core §7 makes a boundary ceiling exclusion-only. A ceiling cannot create
   semantic support.
7. Core §§8.1–8.2 derive supported claims and the verdict from the complete
   normalized findings and explicit asserted claim.
8. Core §§10 and 14 prohibit promoting signatures, digests, actor reports,
   recorder relations, or absence into semantic truth, boundary control,
   execution, independence, or nonoccurrence.

These rules preserve three distinct planes: EMILIA lifecycle/outcome, WEXP
appraisal, and CAID/action correlation.

## P

P supplies a materially richer evidence chain than the original WE-EP-004
description: exact equality tokens for receipt, action hash, CAID, nonce,
operation and facility; signed controller and meter observations; current
source pins; distinct keys and declared control domains; exact windows; source
requirements; and typed effect predicates.

That does not complete the WEXP input. No frozen public profile:

- constructs the opaque WEXP target from the EP action identity;
- defines CAID syntax, issuer scope, normalization, equality, or its role in
  exact WEXP target binding;
- maps controller acceptance to invocation or meter effect to execution;
- establishes an accepted execution-relevant boundary, ceiling, grounding, or
  grounding acceptance;
- validates the meter as IV of an exact execution base under WEXP independence
  predicates;
- fixes an asserted WEXP claim, counter-evidence treatment, evaluation scope,
  or the remaining normalized findings.

Therefore P has no constructible complete AppraisalInput, supported-claims set,
or WEXP verdict. Its frozen expectation is `UNDERDETERMINED`, with asserted
claim and verdict both `UNDETERMINED`. This is not a WEXP rejection.

## P-1

P-1 removes only the signed meter observation's `action_caid` relation and
re-signs that observation. The signature remains valid, so an integrity failure
does not explain any later difference.

Core assigns no intrinsic WEXP meaning to the removed field. Without a public
mapping profile, Core cannot choose among at least four possibilities:

- the missing member prevents construction of a complete logical AppraisalInput;
- it produces an evaluated unsupported exact-target binding;
- it produces a not-evaluated binding, base, boundary, or qualifier assessment;
- another profile-defined exact-binding premise substitutes for it.

Therefore P-1 also has no constructible complete AppraisalInput, supported-claims
set, or WEXP verdict. Its frozen expectation is `UNDERDETERMINED`, with asserted
claim and verdict both `UNDETERMINED`. Absence of the field does not establish
nonoccurrence, failure, counter-evidence, or a Core rejection.

## Does action_caid removal change WEXP semantic support?

**UNDETERMINED.** No frozen public mapping rule assigns the meter's
`action_caid` relation a WEXP semantic role. Both fixture expectations remain
underdetermined, but that shared meta-status does not establish that the removed
relation is semantically irrelevant under a future profile.

CAID correlation is not WEXP semantic support unless a frozen mapping rule makes
it an exact premise and separately validates the relevant semantic predicate.

## Required bridge

**BRIDGING RULE REQUIRED: YES.** A determinate expectation would require one
named, immutable EP-to-WEXP profile that:

1. constructs the exact WEXP target `T`;
2. defines CAID namespace, normalization, issuer scope, equality, and whether
   authenticated meter `action_caid` presence/equality is necessary, sufficient,
   or only one premise for binding to `T`;
3. states whether an alternate exact-binding mechanism can substitute;
4. validates operation, facility, nonce, window, and effect semantics as a
   separate effect-to-execution predicate rather than treating CAID equality as
   execution support;
5. establishes the accepted boundary, ceiling, grounding, and grounding
   acceptance;
6. if IV is asserted, validates the exact execution base and administrative,
   operational, and technical independence under the named trust context;
7. fixes the asserted claim and every remaining AppraisalInput component; and
8. defines the P-1 missing-field disposition.

Until that bridge exists, the terminal technical result is to stop before any
implementation run. No normative WEXP × EMILIA profile is created by this
package.

## Independence record

- Reference engine run before freeze: **NO**.
- Independent WEXP engine run before freeze: **NO**.
- EMILIA implementation run by this executor before freeze: **NO**.
- Iman internal rehearsal used as WEXP expectation input: **NO**.
- Fixture construction used Iman's structural guidance: **YES**.

Public authority links:

- [Core-01 at the frozen WEXP commit](https://github.com/WEXP-dev/wexp-spec/blob/b28a46e7764c2ef14decc35394f21278fca9c988/drafts/core/01/draft-sergeev-wexp-core-01.xml)
- [EMILIA outcome-observation vector at the frozen baseline](https://github.com/emiliaprotocol/emilia-protocol/blob/9a04bea7fe680345132f6f6251fdb9a63fd8aeb2/conformance/vectors/outcome-binding.sources.v1.json)
- [EMILIA signing and binding source at the frozen baseline](https://github.com/emiliaprotocol/emilia-protocol/blob/9a04bea7fe680345132f6f6251fdb9a63fd8aeb2/packages/verify/src/outcome-binding.ts)
