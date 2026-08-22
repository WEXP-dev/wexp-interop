# Reproduction record

Status: **READY FOR FOUNDER AND JOINT REVIEW**  
Terminal result: **BRANCH A — EXPLICIT BRIDGE REQUIRED**  
Publication: **NOT PERFORMED**

This record separates two reproducible operations:

1. verifying the complete evidence package and the supplied canonical EMILIA
   execution receipt; and
2. optionally rerunning the public EMILIA implementation at its pinned commit.

The optional rerun is new reproduction evidence. It cannot replace, rewrite, or
improve the frozen expectation or Iman's canonical receipt. There is no WEXP
engine rerun because no frozen public EP→WEXP mapping/profile constructs the
required Core `AppraisalInput`.

Private dependencies required: **NONE**.

## Exact identities

| Item | Bytes | SHA-256 |
| --- | ---: | --- |
| Neutral fixtures (`fixtures.yaml`) | — | `d972dbb549aaaa25e92c32a936acba4d9a686e9ca62fe6bd556b12be2962cfcc` |
| WEXP commitment carrier | 2,809 | `0ec17bcf9b88af17016c7e05d465012af604292210a858df5fa8f9bcf00d57a0` |
| Frozen WEXP reading | — | `a185e6760de149375e657b1429adc1ea329ed9f9705b9d1c2b505dcc8e3ea984` |
| Frozen EMILIA reading | 5,078 | `b43f8ac6dce465258c75a42117d2750a6bafa163846251416e87cec371a4bad6` |
| Five-case comparison | — | `272a9b08a213702ee2156438b7736b954c7a32bc4a190cce92d3d82226266934` |
| Pair-freeze ZIP | 18,158 | `ae237263c86ee0b5c2b6387159d81957efe47e20161b74dd363da5a530705282` |
| P | 7,255 | `b552da51858d0256a562e800a81a870435d6e136c9bc28833b962b6d3723fb3e` |
| P-1 | 7,152 | `67556d28d272b4b01a73e1c1465248644dd7a05460fc149aa77df92cf36403a0` |
| Pair manifest | — | `5375841c5c7d550d1dcbb3ac31e73ab6c5d68a2bc1eb4fea5249dec9dbdce604` |
| Full pair-freeze manifest | — | `ae6e2345e51cd32aad6e1aa7ce3d4ffeb7b4b005ebcbc19dc067ee22c6b52022` |
| Frozen WEXP pair expectation | — | `42eeecaba33238d8c94bbb9d5bb22ab46721de6de74cff455b8115c17892088a` |
| Frozen EMILIA pair expectation | 885 | `6e0dc6c87f853cacdeeb676b27690e54bdb8a7a7aa86611c5ffe233387e256a4` |
| EMILIA execution receipt | 1,963 | `2d61071712ef4424d1b308afb6a3b8752b4effcf2525c0c08c97cff16617b77f` |

The distribution channel must supply the final root `MANIFEST.sha256` identity
separately from the candidate archive. The root manifest covers every regular
payload file except itself.

## Ten-step evidence verification

### 1. Verify the original fixtures

Verify
`source/original/WEXP-EMILIA-INTEROP-001/fixtures.yaml` at
`d972dbb549aaaa25e92c32a936acba4d9a686e9ca62fe6bd556b12be2962cfcc`.
Confirm the five IDs are exactly `WE-EP-001` through `WE-EP-005` and retain
neutral facts rather than imported per-system outcomes.

### 2. Verify both reading commitments

Inspect `records/COMMIT-REVEAL-RECORD.md` and the 2,809-byte pre-reveal carrier
`source/original/commitment/WEXP-EMILIA-INTEROP-001-SHAREABLE-v2.zip` at
`0ec17bcf9b88af17016c7e05d465012af604292210a858df5fa8f9bcf00d57a0`.
Its commitment binds the undisclosed WEXP reading at `a185e676...`. Confirm the
independent EMILIA commitment binds `b43f8ac6...` and preceded both reveals.
Do not treat a commitment hash as a semantic result.

### 3. Verify both reveals

Hash the exact WEXP reveal at
`source/original/WEXP-EMILIA-INTEROP-001/wexp-reading.yaml` and the exact
EMILIA reveal at `source/original/emilia-reading.json`. Require
`a185e6760de149375e657b1429adc1ea329ed9f9705b9d1c2b505dcc8e3ea984`
and
`b43f8ac6dce465258c75a42117d2750a6bafa163846251416e87cec371a4bad6`.
Confirm each reveal equals its commitment without rewriting either
terminology.

### 4. Verify the five-case comparison

Hash `records/WEXP-EMILIA-EP-COMPARISON-001.md` at
`272a9b08a213702ee2156438b7736b954c7a32bc4a190cce92d3d82226266934`.
Check that it records four cases underdetermined on both sides, WE-EP-005 as
EMILIA-determined `INDETERMINATE` while WEXP remains underdetermined, and no
genuine semantic disagreement or material overclaim.

### 5. Verify the P/P-1 pair freeze

Verify the 18,158-byte
`source/pair-freeze/WEXP-EMILIA-PAIR-FREEZE-001.zip` at
`ae237263c86ee0b5c2b6387159d81957efe47e20161b74dd363da5a530705282`.
Run ZIP integrity checks and both nested manifests. Require P and P-1 at their
exact byte counts and hashes above. Confirm every archive member is
byte-identical to the isolated `source/pair-freeze/` copy.

### 6. Verify the WEXP expectation freeze

Hash `expectations/wexp/wexp-expectation.yaml` at
`42eeecaba33238d8c94bbb9d5bb22ab46721de6de74cff455b8115c17892088a`.
Confirm its freeze time is `2026-08-21T00:32:35Z` and both P and P-1 have
determination `UNDERDETERMINED`, with asserted claim and expected verdict
`UNDETERMINED`. The reason must remain the absence of a frozen public mapping
that supplies the asserted target, boundary, evidence roles, effect→execution
predicate, CAID role, IV mapping, counter-evidence semantics, evaluation scope,
and complete Core `AppraisalInput`. No engine output may override this freeze.

### 7. Verify the EMILIA expectation freeze

Hash
`expectations/emilia/emilia-expectation.freeze.json` as exactly 885 bytes at
`6e0dc6c87f853cacdeeb676b27690e54bdb8a7a7aa86611c5ffe233387e256a4`.
Require:

- artifact `WEXP-EMILIA-PAIR-FREEZE-001`;
- `freeze_status=fixed_before_emilia_execution`;
- baseline `9a04bea7fe680345132f6f6251fdb9a63fd8aeb2`;
- P expectation `true / reconciled / in_bounds / []`;
- P-1 expectation `false / indeterminate / null` with required error
  `outcome_observations_not_exactly_bound`; and
- the explicit EMILIA-only claim boundary.

Use the chronology record: pair bytes were frozen at
`2026-08-21T00:31:23Z`, the WEXP expectation at `00:32:35Z`, and the pair was
sent at `00:58:41Z`. The expectation has no invented intrinsic timestamp; its
pre-execution status, exact hash linkage, and authenticated correspondence
establish the declared ordering.

### 8. Verify the EMILIA execution receipt

Hash `execution/raw/emilia/emilia-execution-receipt.json` as exactly 1,963
bytes at
`2d61071712ef4424d1b308afb6a3b8752b4effcf2525c0c08c97cff16617b77f`.
Require its `executed_at` value `2026-08-21T02:41:04Z` and exact links to:

- pair package `ae237263...`;
- expectation `6e0dc6c8...`;
- P `b552da51...`;
- P-1 `67556d28...`; and
- EMILIA commit `9a04bea7...`.

Compare receipt actuals with Step 7. P must reproduce
`true / reconciled / in_bounds / []` with result digest
`sha256:4ea90a5cf398ad77fe21bd5933ae85c2970cb55d1b5cd929c0f097bb9efc50b3`.
P-1 must reproduce `false / indeterminate / null` with the sole error
`outcome_observations_not_exactly_bound` and result digest
`sha256:7bfe5b1ba465546787d0ed31fa7aabd00ddd30b755b1c028230a5796d0160aca`.
All six shared checks must be `true`.

### 9. Verify the exact hostile delta

Compare the exact P and P-1 JSON bytes. The only JSON-value differences must be:

1. removal of `/emilia_input/observations/1/action_caid`; and
2. replacement of `/emilia_input/observations/1/proof/signature_b64u`.

Restore the removed member at its original location and restore P's meter
signature. The resulting serialization must equal P byte-for-byte. This proves
the controlled fixture delta; it does not by itself assign `action_caid` a WEXP
semantic role.

### 10. Reproduce terminal-branch selection

Evaluate the branch predicates without preference:

- EMILIA expectation independently frozen: **true**.
- EMILIA actuals reproduce both frozen expectations: **true**.
- Pair isolates the declared exact-binding change: **true**.
- WEXP expectation determinate without a new bridge: **false**.
- New EP→WEXP bridge inserted after freeze: **false**.
- Either implementation failed to reproduce its own expectation: **false**.

Therefore select **Branch A — Explicit Bridge Required**. Branch B is not
selected because no determinate WEXP appraisal is constructible. Branch C is
not selected because the supplied EMILIA receipt reproduces its expectation and
there was no WEXP implementation execution to disagree with a result. The pair
is `COMPATIBLE / DIFFERENT SEMANTIC SURFACE`, not a genuine semantic
disagreement.

## Public EMILIA baseline verification

The receipt pins the public repository:

`https://github.com/emiliaprotocol/emilia-protocol`  
commit `9a04bea7fe680345132f6f6251fdb9a63fd8aeb2`

At that exact commit verify:

| Role | Tracked path | SHA-256 |
| --- | --- | --- |
| Outcome-binding verifier source | `packages/verify/src/outcome-binding.ts` | `9a674113122f23001567eaeb673190ac4658b5273f7433e234c8ecbb5be704b0` |
| Public package entry | `packages/verify/index.js` | `f386e365a9998f08ea4947ffd415ca353c0a82766677a8e0cf3117909cccee24` |

The verified Git blob identity for `packages/verify/index.js` is
`ad9f7ec812711cbc0a13f3a06b3fe1528ab8eaa3`. The repository `package.json`
selects that file as the package `main`/root import entry.

A public checkout can verify exact tracked bytes without running either
fixture:

`git show 9a04bea7fe680345132f6f6251fdb9a63fd8aeb2:packages/verify/src/outcome-binding.ts | shasum -a 256`

`git show 9a04bea7fe680345132f6f6251fdb9a63fd8aeb2:packages/verify/index.js | shasum -a 256`

If the public repository cannot be obtained, report
`UNVERIFIED EXTERNAL REFERENCE`. Do not convert absence of network access into
an implementation failure.

## Canonical receipt versus optional implementation rerun

The exact supplied receipt is the canonical external execution evidence for
INTEROP-001. Package verification requires no EMILIA rerun. A reviewer may
optionally reproduce the public implementation behavior from a clean checkout
at the pinned commit, using only the public package API and the exact
`emilia_input` values carried by P and P-1. Preserve raw output and compare it
against the frozen expectation and canonical receipt.

No exact fixture-adapter or CLI invocation was established by this completion
pass, and the two verified source paths alone do not define one. An optional
rerun must therefore use the pinned public package API's documented invocation
at that commit and record the exact command/API call before execution; this
record does not invent a command after seeing the receipt.

An optional rerun:

- must use the exact public commit and record the clean tree;
- must not change P, P-1, either expectation, or the canonical receipt;
- must not use current repository head as semantic authority;
- must report its invocation, toolchain, raw bytes, and hashes separately; and
- must be classified as additional reproduction evidence, never replacement
  evidence.

No private EMILIA material is required. No WEXP implementation may be invoked
unless a separately frozen, reviewed EP→WEXP profile first makes the input
constructible; such a profile would be a new experiment and is outside
INTEROP-001.

## Package-level checks

`verify_final.py` performs the complete package-byte, nested-manifest,
pair-delta, expectation/receipt-linkage, reproduction, and Branch-A checks
without importing or invoking either implementation. Obtain the final root
manifest identity from a channel independent of the archive, then run from the
candidate root:

`python3 -B reproduction/verify_final.py --manifest-sha256 <FINAL_MANIFEST_SHA256>`

The command reports the number of manifest payload entries verified and
`implementation_execution_performed: false`. Supplementary read-only checks
include:

`shasum -a 256 -c MANIFEST.sha256`

`unzip -t source/pair-freeze/WEXP-EMILIA-PAIR-FREEZE-001.zip`

`python3 -m json.tool expectations/emilia/emilia-expectation.freeze.json >/dev/null`

`python3 -m json.tool execution/raw/emilia/emilia-execution-receipt.json >/dev/null`

Verify that the manifest covers every regular payload file except itself, with
no unlisted files, symlinks, or special files. Independently unpack the final
candidate ZIP and repeat the root and nested manifest checks.

`reproduction/verify.py`, `reproduction/execute.py`, their schemas, and the
immutable `PREPARED_HARD_STOP` envelope are preserved preparation artifacts.
They document and test an identity-first optional local rerun workflow; they
are not the source of the supplied EMILIA result and were not run on P/P-1 in
this completion phase.

A zero process exit from a future optional capture means only that capture
finalization succeeded. It is never an interop PASS, semantic-equivalence
claim, or conformance result.
