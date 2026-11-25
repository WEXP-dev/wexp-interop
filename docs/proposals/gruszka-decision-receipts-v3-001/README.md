# Gruszka decision receipts -11: V3 mapping to Core-02: local proposal

**Track: open. Status: PROPOSAL, not a published package.** The mapping, the expectations, the runs and the result are public. The result row and the attribution are agreed with the author of the external format before anything here is described as a result. Nothing here states that the external format conforms or does not conform to WEXP Core.

Opened from interoperability check [WEXP-dev/interop-test-lab#43](https://github.com/WEXP-dev/interop-test-lab/issues/43).


## Steps, in order

1. **Pinned bytes.** [SOURCE-PINS.json](SOURCE-PINS.json) names the exact public files and
   Internet-Draft revisions this proposal refers to, with SHA-256 and size, and the revisions of both
   appraisers. It is part of the freeze.
2. **Mapping and expectations.** [FIELDS.md](FIELDS.md) lists the fields of the pinned files, with
   nothing decided about them. [MAPPING.md](MAPPING.md) says how the external record maps to a
   normalized Core-02 input. `inputs/<case>.json` holds `{"id": ..., "input": ...}` and
   `expectations/<case>.json` holds `{"id": ..., "expected": ...}` with all twenty result components.
   Corrections go in as a new revision section of MAPPING.md.
3. **Freeze.** `python3 -B scripts/proposals/freeze_proposal.py freeze docs/proposals/gruszka-decision-receipts-v3-001` writes
   FREEZE.json. Commit it before any appraiser runs.
4. **Run.** `python3 -B scripts/proposals/run_proposal.py docs/proposals/gruszka-decision-receipts-v3-001 --wexp-ref <checkout>
   --wexp-check <checkout> --write` runs both appraisers and writes `evidence/`. Commit it after the
   freeze. A difference from an expectation is recorded as it is; expectations are not edited after a run.

5. **Result row.** [RESULT-ROW.json](RESULT-ROW.json) says what was examined, who initiated the check
   and how that is known, and whether the author of the format agreed the row. It starts as a draft
   that names nobody. `python3 -B scripts/proposals/result_table.py` rebuilds the results page from it.

## Corrections

You do not need to edit anything. Corrections to the mapping, the inputs or the expectations are
welcome in the pull request, in any form, from anyone who has read the pinned material. They go in as
a new revision section of MAPPING.md before the freeze.

Naming and agreement of the result row are separate steps. They are asked directly, at the result-row
stage, of the person concerned, and nobody is named before they confirm it.

Both appraisers are operated by one person. A run here is not an independent reproduction.
