# Worked example of the proposal path (two cases from the public corpus): local proposal

**Status: WORKED EXAMPLE of the path. Synthetic; not a result about any external format.** The result row and the attribution are agreed with the
author of the external format before anything here is described as a result. Nothing here states
that the external format conforms or does not conform to WEXP Core.


## Steps, in order

1. **Pinned bytes.** [SOURCE-PINS.json](SOURCE-PINS.json) names the exact public files this proposal
   refers to, with SHA-256 and size, and the revisions of both appraisers.
2. **Mapping and expectations.** [MAPPING.md](MAPPING.md) says how the external record maps to a
   normalized Core-02 input. `inputs/<case>.json` holds `{"id": ..., "input": ...}` and
   `expectations/<case>.json` holds `{"id": ..., "expected": ...}` with all twenty result components.
   Corrections from the author go in as a new revision section of MAPPING.md.
3. **Freeze.** `python3 -B scripts/proposals/freeze_proposal.py freeze docs/proposals/worked-example-001` writes
   FREEZE.json. Commit it before any appraiser runs.
4. **Run.** `python3 -B scripts/proposals/run_proposal.py docs/proposals/worked-example-001 --wexp-ref <checkout>
   --wexp-check <checkout> --write` runs both appraisers and writes `evidence/`. Commit it after the
   freeze. A difference from an expectation is recorded as it is; expectations are not edited after a run.

Both appraisers are operated by one person. A run here is not an independent reproduction.
