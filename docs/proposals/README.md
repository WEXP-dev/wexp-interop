# Proposals: taking one external evidence format through Core-02

A proposal examines one question: what does a record from another system support as an input to
[draft-sergeev-wexp-core-02](https://datatracker.ietf.org/doc/draft-sergeev-wexp-core/02/)? It is
working material, not a published package. A proposal becomes a package under `experiments/` only
by the [publication procedure](../RELEASE.md), after its result row and attribution are agreed with
the author of the external format.

## The path

| Step | Who | How |
|---|---|---|
| 1. Ask | the author of the format | [Start an interoperability check](https://github.com/WEXP-dev/interop-test-lab/blob/main/START-HERE.md). An automatic reply pins the public files linked in the form: repository, commit, path, SHA-256, size. |
| 2. Skeleton | a maintainer | Run the "Proposal skeleton" workflow with the pins from that reply, or `python3 -B scripts/proposals/new_proposal.py` locally. It creates `docs/proposals/<slug>/` on a branch and opens a draft pull request. |
| 3. Mapping | a maintainer, then the author | Write `MAPPING.md`, `inputs/` and `expectations/`. The author reads the pull request and says where the mapping misreads the format; corrections go in as a new revision section. |
| 4. Freeze | a maintainer | `python3 -B scripts/proposals/freeze_proposal.py freeze docs/proposals/<slug>`, committed on its own. |
| 5. Run | automatic | On every push to the pull request, the "Proposal order check and appraisal run" workflow checks the freeze, runs both appraisers at the pinned revisions and posts the result table. To keep the evidence in the tree, run `run_proposal.py --write` locally and commit `evidence/` after the freeze. |
| 6. Result | both | The row and the attribution are agreed in the pull request before anything is published. |

## What the checks hold

- A frozen file that changes after the freeze is refused. A mapping revised after a run needs a new
  freeze and a new run.
- The freeze must be its own commit and come before any committed evidence. This is read from the
  commit history of the pull request, so merge with a merge commit, not a squash.
- Appraiser checkouts must be clean and at the commits in `SOURCE-PINS.json`.
- An appraiser that does not complete a case is a refusal, never a result.
- Committed evidence must equal a fresh run.
- A result that differs from its expectation is reported and kept. Expectations are not edited
  after a run.

## What they do not hold

The history cannot show a run that was never committed; that the expectations were written before
any run is a declaration by the person who wrote them. Both appraisers are operated by one person,
so a run here is not an independent reproduction. No check decides whether a mapping reads the
external format correctly; that is what the author's review is for.

## Existing proposals

- [AAC completeness preparation](aac-completeness-001/README.md)
- [WIMSE / Core-02 migration trial](wimse-core02-replay-001/RESULTS.md)

Both predate this path and are not frozen under it.
