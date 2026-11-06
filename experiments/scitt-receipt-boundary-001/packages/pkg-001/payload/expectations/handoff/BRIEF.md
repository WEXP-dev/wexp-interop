# Clean derivation brief: four interop inputs (SCITT Receipt as boundary finding)

You are an isolated derivation session. Derive, from the published specification text alone, the
complete expected logical appraisal (exactly twenty result members) for each of the four inputs in
`inputs/` (`a`, `b1`, `b2`, `c`).

## Hard rules
1. Read only files inside this directory (`handoff/`). No network. Do not open any other directory,
   repository, package or module; do not use or look at any WEXP implementation or any test corpus.
   The only expected result you may look at is `FORMAT-REFERENCE-C01.json` (the published section 13
   fixture C01, transcribed), as a format reference.
2. Every expected value must be traceable to a quoted sentence of `spec/draft-sergeev-wexp-core-02.txt`.
   `MAPPING.md` explains where the inputs come from (a SCITT Receipt mapped to the boundary finding);
   it is background about the inputs, not a source of expectations: the expected result follows from
   the Core text applied to the input values as given.
3. If the text admits two readings for a case, give both and both results, choose a primary and say why.
4. Record in `FILES-READ.txt` every file you opened.

## Material
- `spec/draft-sergeev-wexp-core-02.txt`: the published text; sections 6, 6.1, 6.2, 7, 8.1-8.6, 12, 13.
- `inputs/a.json`, `b1.json`, `b2.json`, `c.json`: `{"id", "input"}`; the applied profile catalog for
  all four is `profiles.json` (one local profile with no registered tokens).
- `REPRESENTATION.md`: the local JSON encoding of logical values (sets as arrays, scoped atoms as
  two-element arrays, `null` = unavailable, Booleans are Booleans). Twenty members, as in the C01
  reference: semantics_version, verdict, fatal_reasons, target, asserted_claim,
  asserted_claim_supported, support_entries, supported_claims, maximal_supported_claims,
  support_relations, boundary_ceiling, boundary_grounding, recorder_relations, substantive_reasons,
  evaluation_gaps, evaluation_gap_entries, counter_evidence, inherited_limitations,
  evaluation_context, evaluation_scope. Input-derived members of an accept or downgrade are the input
  values carried through.

## Deliverables (write into this directory)
1. `expected/a.json`, `expected/b1.json`, `expected/b2.json`, `expected/c.json`: `{"id": ..., "expected": {...20 members...}}`,
   1-space indent, sorted keys, ASCII, trailing newline.
2. `DERIVATION.md`: per case, the input in one line, the verbatim sentences relied on with section
   numbers, the derivation of every non-trivial member, and any ambiguity with both readings.
3. `AMBIGUITIES.json`: array (possibly empty) of `{"id", "question", "primary_reading", "alternative_reading", "alternative_expected"}`.
4. `FILES-READ.txt`.
