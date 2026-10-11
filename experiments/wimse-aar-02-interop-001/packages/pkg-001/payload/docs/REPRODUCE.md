# Reproduce the prospective public composition

Use an ordinary fresh clone of the identified actual public preparation commit
and Python 3.12. Check out that exact remote commit before invoking any retained
implementation. The exact selected preparation runtime is in pre-run/RUNTIME.json; the
actual execution must record its own runtime. There is no required network or
package installation for the replay. Existing private runs do not validate
other Python versions or operating systems.

## Before the first run

From this payload directory:

    python3 -B verify_inputs.py --pre-run

The first public-composition run must follow publication of the preparation
commit containing the input lock, freeze, expectations, expected delta and
comparator. Before invoking the runner, record that remote commit, its Git tree,
the freeze's SHA-256 and the fresh clone's verified input check in the new
execution journal. The local preparation commit may have different metadata
from the public commit. A commit cannot hash itself into its own contents.

The pre-run verifier validates inputs and does not invoke producer, recipient,
native probe, generator or the two-world test.

## Execute and compare

Choose a new empty output directory:

    python3 -B run_pilot.py --out /tmp/wexp-aar-public-run-001 --compare reference/private-pilot-semantic-results.json
    python3 -B compare_results.py --results /tmp/wexp-aar-public-run-001 --report /tmp/wexp-aar-public-run-001/reference-comparison.json

Both commands must succeed. The second command compares complete strict typed
semantic JSON and the exact semantic-byte pin, all 16 negative input bytes,
three generated dispatch policies and recorded accounting.

Do not overwrite a prior output directory or replace failed results. Preserve
stdout, stderr, exit codes, input/implementation hashes, runtime and the exact
preparation commit alongside the new result. Existing pre-run files remain
unchanged. A subsequent completed package may add results, verification logs,
a result report and a final package lock at new paths.

For a completed package, verify its frozen inputs without demanding that the
payload still has the original pre-run-only file set:

    python3 -B verify_inputs.py

This reports additions; the outer collection package manifest verifies the
completed package inventory. Neither command authenticates execution simply
because a log says it occurred.

## Fixed dependencies and limitations

Native revision 01 and 02 use the same Python module names. Keep fresh processes
as the retained runner does; do not load both revisions in a shared interpreter.
The runner stages consumer code and native packaging without producer/Core
files. This is dependency separation, not an OS access-control sandbox.

generate_local_fixtures.py is preserved for provenance and optional development.
Do not execute it during replay or publication assembly. It uses a deliberately
public deterministic test key and the optional cryptography library; the
normal replay consumes the 19 retained exact signed inputs.

check_comparator.py exercises synthetic JSON controls only. Its pre-run result
is not counted among the 130 pilot cases or the 16 recipient output mutations.
No test here makes the known reference blind or externally independent.
