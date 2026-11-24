# Derivation record

The fifteen expected results in [`../`](../) were derived in an isolated session that saw only the
files listed in [FILES-READ.txt](FILES-READ.txt): the brief and the two format notes in
[handoff/](handoff/), `profiles.json`, the fifteen inputs and `MAPPING.md` with revision 2 (SHA-256
`e9be700253a160ac7eb5ee53b30a7cac87d5f373869d74ae78a766daa5a8f33c`), and the text of
`draft-sergeev-wexp-core-02`. It did not see, import or run any appraiser.

- [DERIVATION.md](DERIVATION.md): the common ingress analysis (Section 6.2, checks 1 to 6), then for
  each case the Core-02 sentences relied on and the derivation of every member.
- [AMBIGUITIES.json](AMBIGUITIES.json): empty. The session recorded no place where the text allows
  two readings for these inputs.
- [DELIVERED-SHA256SUMS.txt](DELIVERED-SHA256SUMS.txt): SHA-256 of the session's deliverables as
  published here. The fifteen expected results are byte-identical to what it delivered.

In FILES-READ.txt and handoff/BRIEF.md the session's working directory is written as `<handoff>/`;
nothing else differs from what the session received or wrote.

An earlier isolated session, given the same brief and the inputs of revision 1, found that
`id-alone-unverified` broke the cross-field contract of Core-02 Section 12; MAPPING.md, revision 2,
describes the change. Its results were not used. For the fourteen inputs that revision 2 did not
change, its expected results are byte-identical to the ones here.
