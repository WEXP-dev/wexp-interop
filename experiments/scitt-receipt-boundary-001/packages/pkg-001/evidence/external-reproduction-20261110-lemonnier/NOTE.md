# External reproduction by Laurent Lemonnier, 2026-11-10

Laurent Lemonnier ran the published checks and the repeated appraisal of this package in GitHub
Actions in his own repository, `Laurent-Lemonnier/dps-scitt-decision-layer`, workflow
`.github/workflows/wexp-reproduce.yml`, on a GitHub-hosted runner with Python 3.12.16. He reported
the result by email on 2026-11-10 and asked that it be recorded in this collection under his name.
Every fact below was re-read from the GitHub API and the job logs; `EVIDENCE-INDEX.json` gives the
source, retrieval time, run, attempt, job and SHA-256 of each file in this directory.

## What was repeated (run 42801386609, attempt 1, head `f661d39f7d9191f536ea09b7f7c4bbcc70af6128`, success)

Job 129779506462, at `WEXP-dev/wexp-interop` commit `a45c88e9e345978fa4392bfa0fd76a5e645b1751`:

- the four read-only commands of this package's `REPRODUCE.md`: `catalog.py --check` (PASS,
  4 packages), `verify_collection.py` (PASS), `verify_scitt_receipt_boundary.py`
  (`PASS_PACKAGE_EVIDENCE`), and the 9 catalog regression tests (OK);
- the repeated appraisal: `run_case.py` with `WEXP-dev/wexp-ref` at
  `56289024c9ee748111f1f1d4f42728ffe04d8d69` and `WEXP-dev/wexp-check` at
  `25ec856e053d8ab40ed60bb88b70c84768d45e34`. For cases a, b1, b2 and c both appraisers equal the
  frozen expectations. The output printed in the log has SHA-256
  `166dd11e838d93799a1a3c501b6d97698477f5a955796a4e0a68af6a48f82907`.

Job 129779506135 in the same run repeated the corpus comparison of `WEXP-dev/wexp-check`
(recorded in that repository); it is kept here because it is part of the same run.

The pinned verification dependencies were installed from `requirements-verification.txt` by a
workflow step before the checks. The environment preparation is the one in the saved workflow file.

## What was not repeated

- The optional SCITT registration (`REPRODUCE.md`, "Repeat the SCITT registration (optional;
  different bytes)") was not run. No new Receipt exists from this reproduction.
- No independent implementation was involved: the same published code and commands were run.
- The run was not blind: the frozen expectations are public in this package.

## First failure

An earlier run, 42801235872 (attempt 1, head `f57ea8bf30b88a4f6d8628d6ed9e7588561830ac`), failed in
job 129778988112 at the read-only collection checks with `ModuleNotFoundError: No module named
'jsonschema'`; the repeated appraisal step was skipped. The workflow at that head had no step
installing `requirements-verification.txt`; the workflow at `f661d39f` adds it (compare the two saved
workflow files). The corpus job of that run, 129778987815, succeeded with the same counts and the
same comparison digest as the later run.

## How the comparison files were obtained

The runs published no artifacts (`artifacts-*.json`, `total_count` 0). The two
`*.extracted-from-log.json` files were reconstructed from the job logs by
`extract_comparison_from_log.py`, which removes the runner's timestamp prefix from the lines printed
by `cat` and checks the result against the digest printed by `sha256sum` in the same log. They are
extracted from the log, not downloaded artifacts. The log files are kept byte for byte as served.
