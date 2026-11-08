# Read the saved evidence or repeat the appraisal

## Read-only collection checks

From the collection root, with the pinned verification dependencies and Python 3.12:

```sh
python -B scripts/catalog.py --check
python -B scripts/verify_collection.py
python -B scripts/verify_scitt_receipt_boundary.py
python -B -m unittest discover -s scripts -p 'test_scitt_receipt_boundary_catalog.py'
```

These check the card, the generated catalog, the package manifest, the payload inventory against its reviewed pin, the archive against the payload, the Receipt and Signed Statement digests, the frozen expectations against their delivered digest list, and the recorded comparison results. They run no appraiser, emulator or Transparency Service.

## Repeat the appraisal (a new run, recorded separately)

From `payload/`, with Python 3.12, a public checkout of `WEXP-dev/wexp-ref` at `56289024c9ee748111f1f1d4f42728ffe04d8d69` and a checkout of `WEXP-dev/wexp-check` at `25ec856e053d8ab40ed60bb88b70c84768d45e34` (at the time of this card that commit exists only in the author's local repository and on no public branch; until it is pushed, the second appraiser's revision is not publicly retrievable):

```sh
git clone https://github.com/WEXP-dev/wexp-ref.git /path/to/wexp-ref
git -C /path/to/wexp-ref checkout 56289024c9ee748111f1f1d4f42728ffe04d8d69
git clone https://github.com/WEXP-dev/wexp-check.git /path/to/wexp-check
git -C /path/to/wexp-check checkout 25ec856e053d8ab40ed60bb88b70c84768d45e34
python3.12 -B run_case.py --wexp-ref /path/to/wexp-ref --wexp-check /path/to/wexp-check --output /path/outside/the/package/comparison.json
```

Both appraisers are standard-library Python; no installation step is needed, the script puts one
checkout at a time on `PYTHONPATH`. The second clone succeeds only once the named `wexp-check`
commit has been pushed (see the limitations in the card).

The script runs each appraiser in its own interpreter process on the four inputs and compares every result component with the frozen expectations under the harness set semantics. Write the output outside the package; a repeated run is a new record, not a change to this one.

## Repeat the SCITT registration (optional; different bytes)

`payload/harness/run_emulator.sh <new-dir>` clones the pinned emulator revision, installs its PyPI dependencies into a new virtual environment, starts the CCF emulator with error injection disabled, creates and registers the same statement, retrieves the Receipt twice and verifies it. Keys are generated ad hoc, so the resulting bytes differ from `payload/artifacts/`; the structure and the "Receipt verified" outcome repeat. The emulator source is not installed as a package; it runs from its checkout with a documented import shim for an SDK that is no longer on PyPI. Concretely, the script puts the emulator checkout and `harness/shim` on `PYTHONPATH` and runs `python -m scitt_emulator.cli`; `harness/shim/archivist/` is a two-file placeholder for the `archivist` module that the pinned source imports at load time (RKVST backend), which is never used with the CCF tree algorithm. Python 3.12 or newer, `git`, network access to GitHub and PyPI, and a free local port 8765 are required; the run takes well under a minute. Expected final lines: `receipt bytes identical on retrieve`, `Receipt verified`, then the digests of the new artifacts. This procedure was followed literally from a copy of the package in a fresh directory before the card was finalized.
