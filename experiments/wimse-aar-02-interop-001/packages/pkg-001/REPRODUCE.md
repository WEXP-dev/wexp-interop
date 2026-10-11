# Verify or reproduce the completed AAR package

Use an ordinary fresh clone of the exact public carrier identified in
[record.json](record.json). Python 3.12 is the retained execution profile;
the recorded run used CPython 3.12.14. The AAR replay and the AAR-specific
read-only verifier need no third-party Python installation. General collection
schema verification uses the pinned root `requirements-verification.txt`.

## Read-only checks of retained evidence

From the collection root:

```sh
python3 -B scripts/verify_aar.py
python3 -B scripts/catalog.py --check
python3 -B scripts/verify_collection.py
```

The AAR-specific command checks the fixed public preparation/freeze, every
frozen input, the complete final inventory and exact ZIP-to-payload file bytes,
paths and executable-bit projection. It checks the full strict result
comparison, case/output accounting and execution-journal bindings. It reads
saved evidence and invokes no retained producer, recipient, probe, generator
or two-world operation. A PASS is not independent authentication that the
recorded execution occurred.

The two underlying evidence checks can also be run from `payload/`:

```sh
python3 -B verify_inputs.py
python3 -B compare_results.py --results results/public-run-001
```

Do not use `verify_inputs.py --pre-run` on the completed payload: that option
deliberately requires the earlier inventory before result additions. The
default mode preserves the same frozen input identities while reporting later
files, whose complete inventory is checked by the final package verifier.

## A new implementation replay

This is a separate action from reading the saved results. From `payload/`,
choose a new empty external output directory and retain its observations:

```sh
python3 -B run_pilot.py --out /tmp/wexp-aar-new-replay --compare reference/private-pilot-semantic-results.json
python3 -B compare_results.py --results /tmp/wexp-aar-new-replay --report /tmp/wexp-aar-new-replay/reference-comparison.json
```

Use a different path if that directory already exists. Preserve stdout,
stderr, exit codes, runtime, exact checked commit/tree and freeze hash. A
different result fails the fixed comparison; keep it without replacing the
earlier observations or editing the source/expectations after the fact.

The original public run used a fresh clone of preparation commit
`70b4491a1ec8aab5af61f31510220067e3e5cfba`, tree
`feaec7ce219ba8aea944d3a8e8fcf0079f6932b9`, before results were added. Its
complete invocation driver and journal are under `payload/run-evidence/`.
Replaying from a completed package will additionally inventory later Python
helper files in the runner's execution observation; that is outside the fixed
semantic projection and is not a dynamic import trace.

## Archive, publication and independence

The final ZIP contains the exact historical `PREPARATION.md` at its root and
the complete `payload/` subtree. The frozen input verifier reads that parent
preparation file, so both must stay in this relative layout after extraction.
The ZIP excludes the current outer card/citation/publication metadata. The outer
package manifest includes both the archive and current card. The archive's
SHA-256 identifies its bytes; Git preserves each extracted regular file and
its executable-bit projection, not ZIP ordering or container metadata.

A fresh-clone verification report belongs outside the commit it verifies.
CI or a later evidence record can identify that exact checked commit without
claiming a commit contains its own subsequent verification result. A later
merge commit requires its own fresh check.

The known reference, oracle and shared dependencies remain visible to the
coordinated preparation team. A new local clone/process or a read-only CI PASS
does not create external-team independence, a blind experiment or a general
interoperability result.

For a standalone downloaded archive, extract the complete ZIP into a new
directory, enter its `payload/` directory and follow
[VERIFY-COMPLETED.md](payload/reports/VERIFY-COMPLETED.md). The two local input
and result verifiers work from this self-contained layout; collection-level
card/ZIP checks additionally require the collection checkout.
