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
| 2. Skeleton | a maintainer | Run the "Proposal skeleton" workflow with the pins from that reply, or `python3 -B scripts/proposals/new_proposal.py` locally. It creates `docs/proposals/<slug>/` on a branch and opens a draft pull request. The skeleton includes `FIELDS.md`, the list of fields in the pinned files with nothing decided about them, and ready one-line answers for the author of the format. When the repository secret `CHECK_COMMENT_TOKEN` is set (a token that can write issues in `WEXP-dev/interop-test-lab` and nothing else), the workflow also leaves a note in the check; without it the maintainer does. |
| 3. Mapping | a maintainer, then the author | Write `MAPPING.md`, `inputs/` and `expectations/`. The author reads the pull request and says where the mapping misreads the format; corrections go in as a new revision section. |
| 4. Freeze | a maintainer | `python3 -B scripts/proposals/freeze_proposal.py freeze docs/proposals/<slug>`, committed on its own. |
| 5. Run | automatic | On every push to the pull request, the "Proposal order check and appraisal run" workflow checks the freeze, runs both appraisers at the pinned revisions and posts the result table. To keep the evidence in the tree, run `run_proposal.py --write` locally and commit `evidence/` after the freeze. |
| 6. Result | both | `RESULT-ROW.json` holds the row: what was examined, a one-line summary, who initiated the check, and what the work left open. The row and the attribution are agreed in the pull request before anything is published. `python3 -B scripts/proposals/result_table.py` rebuilds [RESULTS.md](RESULTS.md) and [OPEN-READINGS.md](OPEN-READINGS.md). |

## Who initiated a check

Every result row states who asked for the check and how that is known, because a result reads
differently when the author of a format asked for it than when a stranger did.

| Relation to the format | How it is established |
|---|---|
| an author of a named Internet-Draft | confirmed with the person directly; an account name alone is never enough |
| the owner of a named repository | GitHub public record, or confirmed with the person |
| a public member of the organization that owns it | GitHub public record, or confirmed with the person |
| a contributor to it | GitHub public record, or confirmed with the person |
| a maintainer of this repository | the check maps no external format |
| no established link | stated as such; it is not an obstacle to a check |

The skeleton writes the row as a draft that names nobody. A name, and the repository or draft the
relation refers to, are added only when the person agrees. Until the person has answered, the row
says that naming is not yet agreed; a row cannot be marked agreed in that state. A party who asks
not to be named is recorded as such, with the kind of relation and no name, repository or draft.
The kind of relation is still published, and with few possible parties it can narrow down who it
was; say so to a party who asks not to be named.

The row records who asked for the check. Who read the mapping, who agreed the row, and who ran the
run are separate facts: the first two are kept in the pull request and in `author_review`, the
third in the evidence. A public member of an organization is not thereby speaking for it, and one
author of an Internet-Draft is not thereby speaking for the others.

A row also records two things that outlast the check: changes the author made to their own
specification afterwards, each with a public reference, and readings of the Core-02 text that the
mapping showed to be open. The second list is input to the next revision of the draft.

## Keeping the pinned bytes retrievable

`python3 -B scripts/proposals/request_archive.py docs/proposals/<slug> --send` asks the Software
Heritage archive to save the repositories a proposal pins. The skeleton workflow can do this on
request. It is a courtesy: no result depends on it.

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
- A result row must be well formed, must not carry a name together with "not named", and must not
  be marked agreed unless the author of the format agreed it. The counts on the results page come
  from the committed evidence, not from the row, and are published only for a proposal that has a
  freeze: evidence with no freeze is refused. The two pages must equal what the rows produce.
- A check asked for by a party with no established link to the format is not listed on the results
  pages, and its pull request cannot leave the draft state, until the author of the format has
  agreed the row. Anybody can ask about anybody's format; that alone publishes nothing about it.
- The summary comment on a pull request names the commit and the run it describes. When the check
  does not complete for a commit, the comment says so in place of the earlier result.

## What they do not hold

The history cannot show a run that was never committed; that the expectations were written before
any run is a declaration by the person who wrote them. Both appraisers are operated by one person,
so a run here is not an independent reproduction. No check decides whether a mapping reads the
external format correctly; that is what the author's review is for.

## Existing proposals

- [AAC completeness preparation](aac-completeness-001/README.md)
- [WIMSE / Core-02 migration trial](wimse-core02-replay-001/RESULTS.md)

Both predate this path and are not frozen under it.
- [Worked example of the path](worked-example-001/README.md): two cases from the public corpus, frozen and run
  under these checks. Synthetic; it maps no external format.
