# WEXP × EMILIA P/P-1 pair freeze record 001

Status: **VERIFIED FROZEN INPUT — NOT EXECUTED**

This record identifies the exact pair package ingested into the final-candidate
scaffold. It does not revise the pair, derive an EMILIA expectation, or execute
either implementation.

## Archive and manifest verification

| Property | Verified value |
| --- | --- |
| Source archive | `WEXP-EMILIA-PAIR-FREEZE-001.zip` |
| Bytes | 18,158 |
| SHA-256 | `ae237263c86ee0b5c2b6387159d81957efe47e20161b74dd363da5a530705282` |
| ZIP integrity | **PASS** |
| Archive members | Exactly nine |
| Pair-manifest SHA-256 | `5375841c5c7d550d1dcbb3ac31e73ab6c5d68a2bc1eb4fea5249dec9dbdce604` |
| Full-manifest SHA-256 | `ae6e2345e51cd32aad6e1aa7ce3d4ffeb7b4b005ebcbc19dc067ee22c6b52022` |
| Archive-extracted pair manifest check | **PASS** |
| Archive-extracted full manifest check | **PASS** |

The exact staged archive is under `source/pair-freeze/`, beside an isolated
unpacked `WEXP-EMILIA-PAIR-FREEZE-001/` tree. Verification operated on the
archive bytes and extracted members; no member was normalized or rewritten.

## Nine governed members

| Member | SHA-256 |
| --- | --- |
| `EXPERIMENT-PROPOSITION.md` | `b26023018e2b7d9aa779c767d8f7c98f690fb9a71ee9a7f1af83abdbfaec5c6c` |
| `PAIR-DELTA.md` | `7e07c6457290d2c3e8854c60f44b45e5ea10095667c634a55083d60bd5a8210a` |
| `PAIR-MANIFEST.sha256` | `5375841c5c7d550d1dcbb3ac31e73ab6c5d68a2bc1eb4fea5249dec9dbdce604` |
| `README.md` | `888e12c4f4ee5fcc2e5c85d2cd6a2fb2a107d41ad9a9ba951ef88e32eadafaed` |
| `WEXP-DERIVATION.md` | `0249cfe81428edb3480c12e9d12ba06f51649719f8d544c4ecc066100d406983` |
| `fixtures/WE-EP-P-1.json` | `67556d28d272b4b01a73e1c1465248644dd7a05460fc149aa77df92cf36403a0` |
| `fixtures/WE-EP-P.json` | `b552da51858d0256a562e800a81a870435d6e136c9bc28833b962b6d3723fb3e` |
| `wexp-expectation.yaml` | `42eeecaba33238d8c94bbb9d5bb22ab46721de6de74cff455b8115c17892088a` |
| `MANIFEST.sha256` | Self-excluded from its contents; exact file SHA-256 `ae6e2345e51cd32aad6e1aa7ce3d4ffeb7b4b005ebcbc19dc067ee22c6b52022` |

## Exact pair and controlled delta

| Fixture | Bytes | SHA-256 |
| --- | ---: | --- |
| P — `fixtures/WE-EP-P.json` | 7,255 | `b552da51858d0256a562e800a81a870435d6e136c9bc28833b962b6d3723fb3e` |
| P-1 — `fixtures/WE-EP-P-1.json` | 7,152 | `67556d28d272b4b01a73e1c1465248644dd7a05460fc149aa77df92cf36403a0` |

The exact semantic intervention is removal of:

```text
/emilia_input/observations/1/action_caid
```

The only necessary derivative value change is:

```text
/emilia_input/observations/1/proof/signature_b64u
```

A byte-level diff found no other change. A construction-only check restored the
removed member at its original member position and restored the original meter
signature; the resulting bytes exactly equalled P and reproduced P's SHA-256.
All four carried Ed25519 signatures verify. These checks establish controlled
construction and cryptographic validity only; they do not evaluate an EMILIA
lifecycle outcome or a WEXP appraisal.

## Frozen experiment proposition

> The stronger result depends on the exact meter-observation-to-action CAID
> binding.

The proposition was fixed before WEXP expectation derivation. It does not make
CAID equality a WEXP target, WEXP semantic support, or WEXP arguments-hash
identity.

## Frozen WEXP expectation

- P: `UNDERDETERMINED`; asserted claim and verdict `UNDETERMINED`.
- P-1: `UNDERDETERMINED`; asserted claim and verdict `UNDETERMINED`.
- Effect of removing meter `action_caid` on WEXP support: `UNDETERMINED`.
- `BRIDGING RULE REQUIRED: YES` for a determinate WEXP composition experiment.
- The absent bridge was recorded; it was not created.

The WEXP expectation is frozen under SHA-256
`42eeecaba33238d8c94bbb9d5bb22ab46721de6de74cff455b8115c17892088a`.
It may be verified and copied byte-for-byte, but not edited.

## Independence and execution barrier

- Reference WEXP engine run before freeze: **NO**.
- Independent WEXP engine run before freeze: **NO**.
- EMILIA implementation run by the freeze executor before freeze: **NO**.
- Iman's internal rehearsal used as a WEXP oracle: **NO**.
- Iman's structural guidance used to construct the pair: **YES**.
- P/P-1 semantically executed during final-candidate staging: **NO**.

The pair remains behind the identity and expectation gates. If the frozen
public mapping cannot construct a WEXP input, the later result class is
`IMPLEMENTATION INPUT NOT CONSTRUCTIBLE`, not `FAIL` and not a synthetic WEXP
verdict.

