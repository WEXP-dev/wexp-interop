# Interop case 001: a SCITT Receipt as the Core-02 boundary finding

The first executable interoperability case in this workspace. One Signed Statement was registered
with the pinned SCITT API emulator (a community implementation used in IETF SCITT hackathons), its Receipt was
retrieved and verified, and the Receipt was mapped to the `boundary_finding` of a
`draft-sergeev-wexp-core-02` appraisal. Four normalized inputs exercise what the Receipt bounds
and what it does not supply. Expected results were derived by an isolated session that saw only the Core text, the mapping
(as background on the inputs), the inputs, the representation note and the section 13 fixture C01 as
a format reference; they were frozen before either appraiser ran.

| document | content |
|---|---|
| [`SOURCE-PIN.md`](SOURCE-PIN.md) | which implementation, which revision, how it was run, what its registration actually checks |
| [`MAPPING.md`](MAPPING.md) | the one-page mapping: what the Receipt establishes, how it fills `boundary_finding`, why the ceiling is `observation`, what it does not establish |
| [`artifacts/`](artifacts/) | the Signed Statement, the Receipt, the service parameters, their SHA-256 |
| [`inputs/`](inputs/), [`profiles.json`](profiles.json) | the four appraisal inputs and the local profile catalog |
| [`expectations/`](expectations/) | the frozen expected results, the derivation and the ambiguity record, verbatim from the isolated session; `expectations/handoff/` holds the brief, representation note and C01 format reference it received; the delivered digest list names the expected files under `expected/`, committed flat with unchanged bytes |
| [`RUN-RECORD.json`](RUN-RECORD.json), [`comparison.json`](comparison.json) | the engine runs and the component-wise comparison |

## Reproduce

From this directory, with Python 3.12 and both appraisers available as checkouts:

    python3.12 run_case.py --wexp-ref <wexp-ref checkout> --wexp-check <wexp-check checkout>

The recorded run used `WEXP-dev/wexp-ref` at `56289024` (the checkout root; the script appends
`src`) and `WEXP-dev/wexp-check` at `25ec856` (the checkout root).

This re-runs both appraisers on the four inputs and compares every result component with the
frozen expectations (set semantics for the collections the harness defines as sets). To repeat the
SCITT registration itself, `harness/run_emulator.sh <new-dir>` clones the pinned emulator revision
and registers the same statement; keys are generated ad hoc, so the bytes differ from
`artifacts/` while the structure and the verification outcome repeat.

## Results

| input | asserted | boundary | frozen expectation | wexp_ref | wexp_check |
|---|---|---|---|---|---|
| a | execution | verified Receipt, ceiling observation | downgrade, `E_BASE_EXCEEDS_BOUNDARY` | equal | equal |
| b1 | observation, positive observation finding | same | accept; support entry carries the Receipt basis and the limitation | equal | equal |
| b2 | observation, no base finding | same | downgrade, `E_MISSING_REQUIRED_EVIDENCE` (the Receipt adds nothing) | equal | equal |
| c | observation, positive observation finding | Receipt present, inclusion proof not checked (status and grounding not-evaluated) | downgrade, gap `E_BOUNDARY_NOT_EVALUATED`, ceiling unavailable, grounding not-evaluated preserved | equal | equal |

All four results carry the boundary limitation `L-ts-no-issuer-signature-check` in
`inherited_limitations`, and the two accept/downgrade results that use the boundary report
`boundary_grounding = attributed`. Both appraisers (`wexp_ref.core02` at `56289024`, `wexp_check`
at `25ec856`) equal the frozen expectations on all twenty components in all four cases; there is
no divergence to classify. The isolated session recorded one open reading (b2: whether a
supported boundary that is neither a support premise nor a reason source still contributes its
limitations to `inherited_limitations`; it chose yes from section 8.1 "boundary limitations" and
section 7 "MUST preserve ... its limitations"); both engines follow that reading and differ from
the alternative. It is new relative to the issues recorded for the section 7 matrix (A1-A6) and the
set 001 re-derivation (P08, P18, P19, R12, R47). Details: `RUN-RECORD.json`, `comparison.json`,
`expectations/DERIVATION.md`, `expectations/AMBIGUITIES.json`.

## Non-claims

- This is not a SCITT profile, not a WEXP mapping profile and not a registered anything. The
  profile identity in the inputs is local to this case.
- This is not a vector of `wexp-vectors`. It may become a candidate there only after the mapping is
  reviewed and the emulator revision is replaced or confirmed as the pinned source.
- The emulator revision is pinned (`cfebeee5`, tag `pre-archive`) and the repository is archived; its
  Receipt format predates RFC 9942 and its registration does not verify the issuer signature or apply
  a registration policy; its inclusion proof is over a synthetic one-shot tree, and its service
  identity is a self-signed certificate generated in the same run and accepted by fiat (see
  `SOURCE-PIN.md` and `MAPPING.md`). The case therefore shows the mapping discipline on a
  real receipt of a hackathon implementation, not interoperability with a production Transparency
  Service.
- Agreement of two appraisers with the frozen expectations is agreement with this case's reading of
  the text; the published specifications remain the authority.
- The Receipt establishes registration, bounded to `observation`; it does not establish execution,
  intent, invocation, PROV, IV, coverage, content truth or boundary control (Core-02 section 10).

## Next step

Coverage, the question whether the set of registered statements is complete for a scope, is the
separate specification `draft-sergeev-wexp-coverage-00`
(<https://datatracker.ietf.org/doc/draft-sergeev-wexp-coverage/00/>). A SCITT Transparency
Service's statement sequence is a natural population for a Coverage case; nothing here is a
Coverage result.
