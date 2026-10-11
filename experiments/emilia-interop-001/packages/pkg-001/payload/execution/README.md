# Execution evidence and preserved envelope

Status: **EXTERNAL EMILIA RECEIPT INGESTED; NO LOCAL IMPLEMENTATION RERUN**  
WEXP route: **IMPLEMENTATION INPUT NOT CONSTRUCTIBLE**  
Terminal result: **BRANCH A — EXPLICIT BRIDGE REQUIRED**

## Canonical execution evidence

The canonical implementation evidence for INTEROP-001 is Iman's exact external
receipt:

`raw/emilia/emilia-execution-receipt.json`  
1,963 bytes  
SHA-256 `2d61071712ef4424d1b308afb6a3b8752b4effcf2525c0c08c97cff16617b77f`

It is linked to the exact 885-byte EMILIA expectation freeze at
`6e0dc6c87f853cacdeeb676b27690e54bdb8a7a7aa86611c5ffe233387e256a4`,
the pair-package hash `ae237263...`, both fixture hashes, and the public EMILIA
baseline `9a04bea7fe680345132f6f6251fdb9a63fd8aeb2`.

The receipt reproduces the frozen expectation:

- P: `valid=true`, `reconciled`, `in_bounds`, `errors=[]`; result digest
  `sha256:4ea90a5cf398ad77fe21bd5933ae85c2970cb55d1b5cd929c0f097bb9efc50b3`.
- P-1: `valid=false`, `indeterminate`, `outcome=null`, sole error
  `outcome_observations_not_exactly_bound`; result digest
  `sha256:7bfe5b1ba465546787d0ed31fa7aabd00ddd30b755b1c028230a5796d0160aca`.
- `predictions_valid`, `observations_verified`,
  `required_sources_present`, `source_independence`,
  `source_requirements`, and `observation_windows` are all `true`.

This completion executor did not run or rerun EMILIA. The receipt remains
Iman's source terminology and is not rewritten as a WEXP result.

## WEXP execution classification

The exact frozen WEXP determination is `UNDERDETERMINED` for P and P-1; each
asserted claim and expected verdict is `UNDETERMINED`. No frozen public
EP→WEXP mapping/profile constructs a complete Core `AppraisalInput` or assigns
the removed meter `action_caid` relation the required WEXP semantic role.

The operational classification is therefore:

`WEXP IMPLEMENTATION INPUT: NOT CONSTRUCTIBLE UNDER FROZEN PUBLIC MAPPING SURFACE`

No WEXP engine was invoked. There is no WEXP stdout, stderr, adapter output,
verdict, engine failure, implementation unavailability, or engine disagreement.
`raw/wexp/NOT-CONSTRUCTIBLE.md` records this boundary without fabricating an
implementation result.

## Historical preparation envelope

The following files are preserved scaffold evidence:

- `plan/EXECUTION-ENVELOPE.json`;
- `plan/EXECUTION-CONTROL.json`;
- `plan/EXECUTION-CONTROL.schema.json`;
- `plan/EXPECTATION-INGEST.schema.json`;
- `../reproduction/verify.py`;
- `../reproduction/execute.py`; and
- `../reproduction/exact_json.py`.

Their `PREPARED_HARD_STOP` and `PENDING` values describe the pre-reveal
preparation phase. They are intentionally byte-preserved historical state.
They are not the live experiment result, do not override the subsequently
ingested expectation or receipt, and must not be edited to make the old
scaffold appear retrospectively ready.

Those artifacts may inform a future optional local reproduction run only in a
separate derived working copy with a newly reviewed control and newly pinned
manifest. Such a rerun is additional evidence; it cannot replace the canonical
receipt. No optional local rerun was performed during final-candidate
completion.

## Result-class discipline

The preserved envelope distinguishes:

- `EXPECTED RESULT REPRODUCED`;
- `EXPECTED RESULT NOT REPRODUCED`;
- `IMPLEMENTATION INPUT NOT CONSTRUCTIBLE`;
- `IMPLEMENTATION SURFACE NOT IMPLEMENTED`;
- `INFRASTRUCTURE EXECUTION UNAVAILABLE`;
- `IDENTITY FAILURE`; and
- `EXPECTATION MISSING / NOT FROZEN`.

For the completed candidate:

- EMILIA canonical receipt: **expected result reproduced for P and P-1**.
- WEXP: **implementation input not constructible**.
- Infrastructure failure: **not reported**.
- Implementation-surface absence: **not reported**.
- Branch C disagreement: **not present**.

These classes must not be collapsed into a generic PASS/FAIL.

## Optional future rerun boundary

A reviewer may independently rerun EMILIA using the public repository at
`9a04bea7fe680345132f6f6251fdb9a63fd8aeb2`. The package does not claim that
the receipt's source-path hashes alone define a complete fixture adapter or CLI
invocation. Any rerun must use and record the exact public package API,
toolchain, invocation, clean tree, raw outputs, and hashes. It must not alter P,
P-1, either expectation, or the canonical receipt.

A WEXP run remains prohibited inside INTEROP-001 unless a separate experiment
first freezes an explicit EP→WEXP mapping/profile. Creating that bridge is
outside this candidate.

## Integrity and publication boundary

The exact expectation, receipt, P, P-1, frozen WEXP expectation, original
commitments, and reveals are immutable evidence. The final root manifest covers
all payload entries after completion.

No public repository was modified. No publication, release, PR, standards
submission, or interop-PASS claim was performed.
