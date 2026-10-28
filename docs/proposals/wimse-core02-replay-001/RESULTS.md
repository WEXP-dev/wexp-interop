# Recorded bounded WIMSE / Core-02 migration result

**Result: 130/130 case checks passed; no recipient-decision difference from the
strong native baseline in this bounded trial.** Thirty-five admitted inputs
produced a complete Core-02 appraisal. Ninety-five native or dispatch failures
produced no Core input or appraisal. These are cases per run, not distinct new
cases multiplied by the number of repeated runs.

## What was frozen and executed

The [pre-run source commit](https://github.com/WEXP-dev/wexp-interop/commit/70d6c5d1fca0843859008c98fd6a57e265ff3f68)
fixed the protocol, profile, source-authored full-result template, producer,
receiver and workflow before the actual AAR replay. The original historical
input package stays at `b3bce9abd047e41af06ff8aff1d9ead8c6b0ed93`; Core-02 code
stays at `56289024c9ee748111f1f1d4f42728ffe04d8d69`. Current upstream AAR inputs
were not substituted.

| Execution | Runtime and modes | Observed result |
|---|---|---|
| [Push run 40604969823](https://github.com/WEXP-dev/wexp-interop/actions/runs/40604969823) | CPython 3.12.15 and 3.13.16; normal and `-O` | All four runs: 130 completed, 130 passed, 35 mapped, zero process/case errors |
| [PR run 40604995949](https://github.com/WEXP-dev/wexp-interop/actions/runs/40604995949) | CPython 3.12.15 and 3.13.16; normal and `-O` | Same complete observations, byte-for-byte |

All eight `observed.json` files have SHA-256:

```text
882cb96cef3fb00192988396ac0ebe4f742070b1d55c2141afe7aebabcb390ae
```

Each run retained 392 process outcomes: three per case and two additional
recipient-entry-point corruption checks. Each mapped output was compared across
all twenty components. The 1,930 comparator assertions per run include positive
set-order controls as well as negative mutations; they are not 1,930 independent
security tests. Two actual modified deliveries, with wrong source/profile
bindings, were separately refused and quarantined by the recipient entry point.

## Meaning of the result

Native record validity and dispatch results, native evaluation/oversight facts,
and recipient decisions agree with the historical reference for the same raw
inputs and policies. On admitted inputs only observation is supported; requested
execution remains unsupported and the appraisal is downgrade. The result keeps
an observation ceiling, attributed grounding, the boundary-exceeded reason,
the execution-support evaluation gap, and the applicable limitations.

The new profile and evaluation-context identities make this a new result. This
is not byte equality with the old Core-01 appraisal and not a retrospective
upgrade of the historical package. The input bytes, native readers and recipient
policy remained fixed to isolate the mapping/result migration.

## Durable evidence and read-only checking

[RECORD.json](evidence/run-001/RECORD.json) binds four original GitHub Actions ZIP
archives, including their exact archive bytes, artifact IDs, runs and hashes.
They are retained in Git; reproduction does not depend on future availability
of the expiring Actions download links. The preservation commit is
[5f3e15a943114a36639309355b4e5a166f9f4d95](https://github.com/WEXP-dev/wexp-interop/commit/5f3e15a943114a36639309355b4e5a166f9f4d95).
Each archive includes normal and optimized summaries, all full observations,
process records, empty error lists and the recipient distribution declaration.

From this directory, with Python 3.12 or later:

```sh
python -B verify_evidence.py --record evidence/run-001/RECORD.json --expected-record-sha256 2a3a0f8a375f7f5eb01419f737502b9f6b35f426f2ee743307799e0cbbe67781
python -O -B verify_evidence.py --record evidence/run-001/RECORD.json --expected-record-sha256 2a3a0f8a375f7f5eb01419f737502b9f6b35f426f2ee743307799e0cbbe67781
python -B test_evidence.py
python -O -B test_evidence.py
```

This checker reads saved data; it does not execute Core or authenticate the
truth of a historical experiment. A fresh execution instead follows
[PROTOCOL.md](PROTOCOL.md) and writes to new external output paths. Retain failed
or interrupted attempts separately; do not edit run-001 to incorporate them.

## Limits and collection status

This is author-coordinated execution with known sources and expectations. Both
routes share the native verifier and recipient decision policy. A separately
staged receiver has no distributed producer/Core source, but no filesystem or
network sandbox was enforced. It is not external independent reproduction,
full Core conformance, validation of real action occurrence, or a blind trial.

No two-world operations, AAC experiment, Coverage evaluation, PostgreSQL
profile or general cross-carrier interoperability were executed. The frozen
historical WIMSE/EMILIA packages and their outcomes remain unchanged. This
bounded migration record is intentionally outside the collection catalog:
formal promotion requires a separately reviewed package card and verification
profile, not reuse of an incompatible historical profile identifier.
