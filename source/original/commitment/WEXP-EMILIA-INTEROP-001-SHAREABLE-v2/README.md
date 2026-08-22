# WEXP x EMILIA Interop 001 - neutral handoff

Status: WEXP-side reading frozen; reading withheld pending independent EMILIA freeze.

Source frozen artifact:
WEXP-EMILIA-INTEROP-001@sha256:c914330b502a48f669381bad763952365da8db64b078445cea6ba5bfb7209d46

Projection:
WEXP-EMILIA-INTEROP-001-SHAREABLE-v2

This projection contains the agreed neutral fixture file byte-for-byte and the
commitment to the frozen WEXP-side reading. It intentionally excludes
wexp-reading.yaml and all WEXP per-case results.

Source projection rules:
- fixtures.yaml is byte-identical to the source frozen artifact.
- wexp-reading.yaml is excluded.
- WEXP-COMMITMENT.sha256 commits to the excluded source wexp-reading.yaml.
- MANIFEST.sha256 covers only this shareable projection.

## WEXP baseline

- Core-01 / CORE-01-FROZEN-001
- wexp-spec@b28a46e7764c2ef14decc35394f21278fca9c988
- wexp-vectors@c745e5abebddfd99cd62cdb3e40dddaf6582bdd9
- wexp-ref@d8f7e512a56b90b17377444c07cbc006ee76b7b5 (PARTIAL)

## WEXP reading commitment

SHA-256:
a185e6760de149375e657b1429adc1ea329ed9f9705b9d1c2b505dcc8e3ea984

The committed WEXP reading was frozen before receipt or use of any per-case
EMILIA outcome. The reading itself is withheld until an independently frozen
EMILIA-side commitment exists.

## Procedure

1. Use fixtures.yaml as the common case input.
2. Freeze the EMILIA-side reading independently against a pinned EMILIA baseline.
3. Return only the EMILIA reading SHA-256 commitment and baseline.
4. Once both commitments are fixed, reveal both readings.
5. Compare without rewriting disagreement or underdetermination after the fact.

Agreement, disagreement, and underdetermination are all valid experimental
results. The purpose is to test whether the mapping preserves what the evidence
actually warrants, not to manufacture convergence.
