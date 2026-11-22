# Clean derivation brief: five interop inputs (an AER-1 execution receipt mapped to a Core-02 input)

You are an isolated derivation session. Derive, from the published specification text alone, the
complete expected logical appraisal (exactly twenty result members) for each of the five inputs in
`inputs/` (`a`, `b`, `c`, `d`, `e`).

## Hard rules

1. Read only files inside this directory (`<handoff>/`). No network. Do not open,
   list or search any other directory, repository, package or module; do not use or look at any
   WEXP implementation (wexp-ref, wexp-check or any other) or any test corpus. The only expected
   result you may look at is `FORMAT-REFERENCE-C01.json` (the published section 13 fixture C01,
   transcribed), as a format reference.
2. Every expected value must be traceable to a quoted sentence of
   `spec/draft-sergeev-wexp-core-02.txt`. `MAPPING.md` explains where the inputs come from (an
   AER-1 receipt mapped to a Core-02 input); it is background about the inputs, not a source of
   expectations: the expected result follows from the Core text applied to the input values as given.
3. If the text admits two readings for a case, give both and both results, choose a primary and say why.
4. Do not run any program that implements an appraiser. Shell tools may be used only to read the
   files in this directory and to write and check your deliverables (for example JSON well-formedness).
5. Record in `out/FILES-READ.txt` every file you opened.

## Material

- `spec/draft-sergeev-wexp-core-02.txt`: the published text; sections 4, 6, 6.1, 6.2, 7, 8.1-8.6,
  12 and 13 carry the rules you need.
- `inputs/a.json` to `inputs/e.json`: `{"id", "input"}`. The applied profile catalog for all five is
  `profiles.json`: one local profile, `wexp-work/interop/aer1-real-04-001/mapping-1`, which registers
  `P_AER1_ANCHOR_NOT_CHECKED` in the evaluation-gap category (with no current-scope capability) and
  `P_AER1_RECOMPUTE_COMMITMENT_ONLY` in the substantive category.
- `REPRESENTATION.md`: the local JSON encoding of logical values (sets as arrays, scoped atoms as
  two-element arrays, `null` = unavailable, Booleans are Booleans). Twenty members, as in the C01
  reference: semantics_version, verdict, fatal_reasons, target, asserted_claim,
  asserted_claim_supported, support_entries, supported_claims, maximal_supported_claims,
  support_relations, boundary_ceiling, boundary_grounding, recorder_relations, substantive_reasons,
  evaluation_gaps, evaluation_gap_entries, counter_evidence, inherited_limitations,
  evaluation_context, evaluation_scope. Input-derived members of an accept or downgrade are the
  input values carried through.
- `FORMAT-REFERENCE-C01.json`: format reference only.
- `MAPPING.md`: background only.

## Deliverables (write into `out/`)

1. `out/expected/a.json` to `out/expected/e.json`: `{"id": ..., "expected": {...20 members...}}`,
   1-space indent, sorted keys, ASCII, trailing newline.
2. `out/DERIVATION.md`: per case, the input in one line, the verbatim sentences relied on with
   section numbers, the derivation of every non-trivial member, and any ambiguity with both readings.
   Begin with the common ingress analysis (section 6.2, checks 1 to 6) applied to all five inputs; if
   any input fails an ingress check, say which check and why, and derive the rejection it produces.
3. `out/AMBIGUITIES.json`: array (possibly empty) of
   `{"id", "question", "primary_reading", "alternative_reading", "alternative_expected"}`.
4. `out/FILES-READ.txt`.

When done, reply with one line per case (verdict and non-fatal tokens), the list of ambiguities, and
nothing else.
