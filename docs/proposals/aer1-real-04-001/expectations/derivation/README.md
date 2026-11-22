# Derivation record

The expected results in [`../a.json`](../a.json) to [`../e.json`](../e.json) were derived in an
isolated session that saw only the files listed in [FILES-READ.txt](FILES-READ.txt): the brief and
the two format notes in [handoff/](handoff/), `profiles.json`, `inputs/a.json` to `inputs/e.json`
and `MAPPING.md` as at commit `1de5f27` of this branch, and the text of `draft-sergeev-wexp-core-02`.
It did not see, import or run any appraiser.

- [DERIVATION.md](DERIVATION.md): for each case, the Core-02 sentences relied on and the derivation
  of every member.
- [AMBIGUITIES.json](AMBIGUITIES.json): two places where the text allows two readings. A1: is
  acceptance of the grounding class by the evaluation context a check that Core makes, or an
  obligation of the profile that Core takes as given? The expected results follow the second
  reading; under the first, cases a, c, d and e are rejected with `E_PROFILE_MAPPING_INVALID`. A2
  concerns member names only.
- [DELIVERED-SHA256SUMS.txt](DELIVERED-SHA256SUMS.txt): SHA-256 of the session's deliverables as
  published here. The five expected results are byte-identical to what it delivered.

In FILES-READ.txt and handoff/BRIEF.md the session's working directory is written as `<handoff>/`;
nothing else differs from what the session received or wrote. An earlier session, on inputs whose
profile tokens broke the token syntax of Core-02 Section 15, is described in MAPPING.md; its results
were not used.
