# WIMSE / Core-02 bounded migration trial

Read [the pre-run protocol](PROTOCOL.md) and [the exact profile](profile.json).
This directory contains a prospective contract and executable trial, not a
replacement for the historical WIMSE package or a completed collection card.

The trial re-verifies the same 130 raw AAR inputs under the historical native
readers and policies, maps admitted evidence into an explicit Core-02 context,
and checks the complete output with a separately staged source-aware receiver.
Native and WEXP routes share the native reader and recipient policy. Neither
route is called independently implemented or independently operated.

Expected results are specified before the run. A CI definition is not execution
evidence: actual outcomes require the identified run and retained observations.
No two-world operations, Coverage evaluation or AAC integration are performed.
The [observations record](RESULTS.md) identifies the executed runs and retained
archives without rewriting the pre-run contract or the historical package.

## Observations

[Run-001 results and reproduction](RESULTS.md) record 130/130 passing case
checks, 35 complete Core-02 appraisals and 95 cases with no Core appraisal.
Native and WEXP recipient decisions agree for all 130 inputs. Two workflow
runs, each on Python 3.12/3.13 and in normal/optimized modes, produced identical
full observations. Exact original archives and a read-only verifier are included.

These are bounded same-project observations, not independent interoperability
or a new result for the historical two-world experiment. The initial pre-run
commit remains available separately; its no-run statement describes its own
point in the chronology, before execution.

## Licensing

The new trial code is supplied under the collection's Apache-2.0 license.
Referenced historical and third-party inputs keep their existing scoped terms.
The public Core appraiser remains in its own pinned repository; it is not
relicensed or copied into this directory.
