# Verify this completed standalone archive

The complete ZIP contains the exact historical `PREPARATION.md` at its root
and the `payload/` directory. Extract both into a new empty directory and keep
that relative layout. The frozen input verifier reads its parent preparation
file. An isolated copy of `payload/` lacks this required binding.

From the extracted `payload/` directory, with Python 3.12:

```sh
python3 -B verify_inputs.py
python3 -B compare_results.py --results results/public-run-001
```

Both commands are read-only. They check the fixed input identities and strict
typed JSON plus exact semantic-byte comparison of the recorded result. They
do not run producer, recipient, native probe, generator or controlled world
operations. No third-party Python installation is required for these checks.

Do not pass `--pre-run` on a completed package: it would intentionally reject
the result/document additions that were absent from the earlier commitment.
The pre-run README and docs remain historical prospective statements; the
actual replay result is in [RESULTS.md](RESULTS.md).

Use the current external package card, final freeze and exact public carrier
to check the downloaded ZIP's identity. A full collection checkout also
provides `scripts/verify_aar.py` for complete archive, payload, card and journal
verification. The ZIP does not contain its own mutable publication/card
metadata or make a self-authenticating claim about its download origin.

A new implementation replay is a separate action. Preserve a new empty
external result directory, runtime/commit/freeze identity and all failures;
use the retained runner and comparator commands from the historical
docs/REPRODUCE.md. The known reference and shared dependencies remain known,
so a successful local replay does not establish external-team independence.
