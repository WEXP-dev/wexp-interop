# Verify and replay the AEP × WEXP package

## Verify the saved observations

From the collection root with Python 3.12 and the pinned collection dependencies installed:

```sh
python3 -B scripts/catalog.py --check
python3 -B scripts/verify_collection.py
python3 -B scripts/verify_aep_core02.py
```

The collection checker validates the public archive, its extraction, the recorded case results and the frozen expectation discrepancy. From this package directory, `sha256sum -c PACKAGE-MANIFEST.sha256` checks the hashes of the shipped files. This manifest excludes itself.

## Repeat the local verifiers

Use a clean checkout of the collection and fresh source checkouts. The original run used Python 3.14.6. The recorded dependency versions are pinned below. Network access is needed to acquire the repositories and dependencies. The runner then uses the local fixture files. Run this block from the collection root in a POSIX environment:

```sh
set -eu
collection_root="$PWD"
package="$collection_root/experiments/aep-applicability-001/packages/pkg-001"
trial_dir=$(mktemp -d)
git clone -q https://github.com/tyche-institute/aep-sandbox.git "$trial_dir/aep-sandbox"
git -C "$trial_dir/aep-sandbox" checkout --detach f6c88be63c5aa12b8e8f6bf35a378a6a5fca9cd4
git clone -q https://github.com/WEXP-dev/wexp-ref.git "$trial_dir/wexp-ref"
git -C "$trial_dir/wexp-ref" checkout --detach 56289024c9ee748111f1f1d4f42728ffe04d8d69
git clone -q https://github.com/WEXP-dev/wexp-check.git "$trial_dir/wexp-check"
git -C "$trial_dir/wexp-check" checkout --detach a2fd1ffd68b234592979a8aa8965bd580ede4d76
python3.14 -m venv "$trial_dir/venv"
"$trial_dir/venv/bin/python" -I -m pip install pip==26.1.2 cryptography==50.0.2 cffi==2.1.1 pycparser==3.12
"$trial_dir/venv/bin/python" -I -B "$package/tools/replay.py" \
  --source-root "$trial_dir" --output "$trial_dir/observations"
cat "$trial_dir/observations/RUN-RECORD.json"
```

The runner creates a nonce-state file exclusively. Each repeat needs a new sandbox checkout and an unused output directory. Cases in order are the good sample with consumption, the identical sample presented again, and the exceed-scope sample. The evaluation time is fixed at 1750000100. Two isolated appraiser processes per input read the six delivered Core inputs and the original profile catalog. Their original launchers verify that the code is imported from the pinned checkouts. The Core driver also checks for input and profile mutations.

The resulting directory contains 12 raw Core JSON outputs and their exit statuses, three native stdout streams, native exit statuses, and before/after nonce states. The new run record binds these files to the checked-out collection commit, three implementation pins, runtime, clock times and the exact component differences. It compares them with the historical observations in the public payload. Successful stderr streams and working directories are environment-dependent and outside this comparison. On a launcher failure, the runner prints its diagnostic and retains the partial output.

Expected results are ALLOW, DENY/replayed and DENY/scope_violation for the native verifier, agreement on all 120 Core components across the two implementations and 114/120 matches to the frozen expectations per implementation. For each case the expected `boundary_ceiling` is the string `"unavailable"` and the observed value is JSON `null`. An unexpected difference is recorded as `DIFFERENCE` with a nonzero exit status.
