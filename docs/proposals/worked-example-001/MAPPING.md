# Mapping: worked example of the proposal path

This proposal exists to show the path and to exercise the checks. It maps nothing: there is no
external format here. Its two cases are taken verbatim, input and expected result, from the public
corpus `WEXP-CORE-02-VECTORS-001` pinned in [SOURCE-PINS.json](SOURCE-PINS.json).

## Revision 1 (before any appraiser run)

1. **The external record.** None. The pinned file is this project's own corpus.
2. **The cases.** `R34` and `P14`, copied without change, with the corpus profile registry as
   `profiles.json`.

## Cases and pre-run expectations

| Case | What differs | Expected verdict | Expected non-fatal tokens |
|---|---|---|---|
| `R34` | PROV aggregate present, semantic assessment not evaluated | downgrade | gap `E_PROV_NOT_EVALUATED` |
| `P14` | PROV and IV aggregates supported | accept | none |

## Reading choices

None: the expectations are the corpus expectations.

## What was read to write the inputs

Only the pinned corpus file. Both appraisers have been run on these corpus cases before, in the
comparison record of `WEXP-dev/wexp-check`; this example therefore shows the mechanics of the path
and is not evidence that expectations preceded a first run.
