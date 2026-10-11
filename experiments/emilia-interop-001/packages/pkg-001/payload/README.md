# WEXP × EMILIA INTEROP-001

Artifact: `WEXP-EMILIA-INTEROP-001`  
Status: **Experimental Interoperability Record**  
Candidate state: **PRIVATE/LOCAL — NOT PUBLISHED**  
Canonical venue: `WEXP-dev/wexp-interop`  
Proposed Git tag: `wexp-emilia-interop-001` (**NOT CREATED**)  
License: Apache License 2.0 (`SPDX-License-Identifier: Apache-2.0`)  
IETF status: **NONE — NO IETF ADOPTION OR ENDORSEMENT IMPLIED**  
Technical result: **BRANCH A — EXPLICIT BRIDGE REQUIRED**

This directory is the completed review candidate for the bounded WEXP × EMILIA
experiment. It preserves the independently frozen readings and expectations,
the byte-identical P/P-1 pair, Iman's exact EMILIA execution receipt, the
comparison, claim ledger, and reproduction path. It is not a release,
conformance suite, certification, adopted mapping, or standards submission.

To verify the candidate without invoking WEXP or EMILIA, obtain the detached
root-manifest hash supplied with the archive and run:

`python3 -B reproduction/verify_final.py --manifest-sha256 <ROOT_MANIFEST_SHA256>`

## Contributors

- **Mikhail Sergeev:** WEXP-side experiment design and analysis; frozen WEXP
  reading and P/P-1 expectation and derivation; controlled-pair and WEXP-side
  package construction; cross-system comparison and integration record; and
  publication-candidate assembly.
- **Iman Schrock:** independent EMILIA-side reading and P/P-1 expectation;
  EMILIA structural fixture guidance; EMILIA verifier execution and execution
  evidence; and end-to-end technical review of the approved baseline.

These are contribution-specific roles. They do not describe either person as
a joint author of the other person's pre-existing specification or system.

## Result

EMILIA reproduced its independently frozen expectation:

- P (`b552da51858d0256a562e800a81a870435d6e136c9bc28833b962b6d3723fb3e`):
  `valid=true`, `lifecycle_state=reconciled`, `outcome=in_bounds`,
  `errors=[]`.
- P-1 (`67556d28d272b4b01a73e1c1465248644dd7a05460fc149aa77df92cf36403a0`):
  `valid=false`, `lifecycle_state=indeterminate`, `outcome=null`, with the
  sole error `outcome_observations_not_exactly_bound`.

P-1 removes only the meter observation's `action_caid` relation and changes
only the derivative meter signature required to preserve cryptographic
validity. All six receipt-level shared checks are true.

The frozen WEXP determination remains `UNDERDETERMINED` for P and P-1; each
asserted claim and expected verdict is `UNDETERMINED`. No frozen public
EP→WEXP mapping/profile constructs a complete Core `AppraisalInput` or assigns
the meter `action_caid` relation the required WEXP semantic role.
Accordingly:

`WEXP IMPLEMENTATION INPUT: NOT CONSTRUCTIBLE UNDER FROZEN PUBLIC MAPPING SURFACE`

No WEXP engine was run on P or P-1, and no synthetic input, bridge, WEXP result,
engine disagreement, or implementation failure was created. The supplied
EMILIA receipt is canonical external execution evidence; this executor did not
rerun EMILIA.

These facts mechanically select **Branch A — Explicit Bridge Required**.
Branches B and C are not selected. This is a compatible boundary between
different semantic surfaces, not a genuine semantic disagreement.

## New frozen evidence

| Evidence | Exact identity |
| --- | --- |
| EMILIA expectation | 885 bytes; SHA-256 `6e0dc6c87f853cacdeeb676b27690e54bdb8a7a7aa86611c5ffe233387e256a4` |
| EMILIA execution receipt | 1,963 bytes; SHA-256 `2d61071712ef4424d1b308afb6a3b8752b4effcf2525c0c08c97cff16617b77f` |
| EMILIA result P | `sha256:4ea90a5cf398ad77fe21bd5933ae85c2970cb55d1b5cd929c0f097bb9efc50b3` |
| EMILIA result P-1 | `sha256:7bfe5b1ba465546787d0ed31fa7aabd00ddd30b755b1c028230a5796d0160aca` |

The receipt links the exact pair-package hash
`ae237263c86ee0b5c2b6387159d81957efe47e20161b74dd363da5a530705282`,
the exact EMILIA expectation hash, both fixture hashes, and
`emiliaprotocol/emilia-protocol@9a04bea7fe680345132f6f6251fdb9a63fd8aeb2`.
The expectation declares `fixed_before_emilia_execution`, and the authenticated
message chronology identifies the pair transmission before the receipt's
`executed_at` value. The evidence files are retained byte-for-byte.

## Frozen authorities

| Input | Frozen identity |
| --- | --- |
| Common fixtures | SHA-256 `d972dbb549aaaa25e92c32a936acba4d9a686e9ca62fe6bd556b12be2962cfcc` |
| Five-case comparison | SHA-256 `272a9b08a213702ee2156438b7736b954c7a32bc4a190cce92d3d82226266934` |
| Frozen WEXP reading | SHA-256 `a185e6760de149375e657b1429adc1ea329ed9f9705b9d1c2b505dcc8e3ea984` |
| Frozen EMILIA reading | 5,078 bytes; SHA-256 `b43f8ac6dce465258c75a42117d2750a6bafa163846251416e87cec371a4bad6` |
| Pair-freeze archive | 18,158 bytes; SHA-256 `ae237263c86ee0b5c2b6387159d81957efe47e20161b74dd363da5a530705282` |
| P | SHA-256 `b552da51858d0256a562e800a81a870435d6e136c9bc28833b962b6d3723fb3e` |
| P-1 | SHA-256 `67556d28d272b4b01a73e1c1465248644dd7a05460fc149aa77df92cf36403a0` |
| Pair manifest | SHA-256 `5375841c5c7d550d1dcbb3ac31e73ab6c5d68a2bc1eb4fea5249dec9dbdce604` |
| Pair-freeze manifest | SHA-256 `ae6e2345e51cd32aad6e1aa7ce3d4ffeb7b4b005ebcbc19dc067ee22c6b52022` |
| Frozen WEXP pair expectation | SHA-256 `42eeecaba33238d8c94bbb9d5bb22ab46721de6de74cff455b8115c17892088a` |
| EMILIA semantic baseline | `emiliaprotocol/emilia-protocol@9a04bea7fe680345132f6f6251fdb9a63fd8aeb2` |
| WEXP semantic baseline | `WEXP-dev/wexp-spec@b28a46e7764c2ef14decc35394f21278fca9c988` |
| WEXP reading-time vectors | `WEXP-dev/wexp-vectors@c745e5abebddfd99cd62cdb3e40dddaf6582bdd9` |
| WEXP reading-time reference | `WEXP-dev/wexp-ref@d8f7e512a56b90b17377444c07cbc006ee76b7b5` (`PARTIAL`) |

Later repository heads do not replace these frozen authorities.

## Evidence boundary

The experiment establishes a bounded distinction on the EMILIA side and a
non-constructibility boundary on the WEXP side. It does not establish physical
truth, semantic equivalence, WEXP validation of EMILIA, EMILIA proof of a WEXP
claim, CAID equality as WEXP semantic support, full interoperability,
conformance, certification, adoption, or a positive WEXP appraisal.

`EP-WEXP-MAPPING-REQUIREMENTS-001.md` is follow-on, non-normative design input.
It was not used as experiment authority and is not a bridge/profile.

## Directory roles

- `source/original/` preserves the common fixtures, commitments, reveals, and
  original pair archive.
- `source/pair-freeze/` preserves the verified pair extraction, controlled
  delta, WEXP derivation, and exact frozen WEXP expectation.
- `expectations/emilia/` preserves Iman's exact 885-byte expectation freeze.
- `execution/raw/emilia/` preserves Iman's exact 1,963-byte external receipt.
- `execution/raw/wexp/` records that WEXP input is not constructible; it
  contains no engine output.
- `records/` preserves chronology, the initial comparison, and pair-freeze
  provenance.
- `comparison/` contains the completed P/P-1 cross-surface comparison.
- `claims/` separates established and prohibited claims.
- `publication/` contains the Branch-A final report, limitations, and bounded
  publication-claim candidate.
- `reproduction/` provides byte verification and an optional public
  implementation rerun path that cannot replace the canonical receipt;
  `verify_final.py` verifies the completed evidence and Branch-A selection
  without invoking either implementation.

## Review and publication state

All frozen evidence remains unchanged. No public repository, Core text, WEXP
vectors, wexp-ref, EMILIA source, or EXT-10 was modified. No bridge/profile was
created. No publication, PR, release, IETF submission, or message to Iman was
performed by this completion step.

The candidate is ready for Founder review and then Iman's final end-to-end
review. Publication remains a separate authorized action.

## License and release identity

Contributions to this joint artifact are made available under the Apache
License 2.0; see `LICENSE`. Independently owned pre-existing specifications,
code, trademarks, and other background work retain their existing ownership
and licensing. Inclusion or reference here does not relicense that background
work beyond rights contributed to this artifact, and Apache-2.0 grants no
trademark rights beyond its stated terms. No separate `NOTICE` is required for
this candidate.

The technically approved predecessor is the 191,735-byte archive with SHA-256
`973d671d5326d642a480b2f546aae9d9c71f07bc5ab6df9aed730c68db8338e3`.
The future published release will bind the artifact ID, Git commit, Git tree,
root-manifest SHA-256, and release-archive SHA-256. Git commit/tree and the
publication date remain pending until an actual authorized publication. The
new candidate manifest/archive hashes are recorded in the detached freeze
record delivered beside the ZIP; embedding either value inside the bytes it
identifies would create a circular self-reference.
