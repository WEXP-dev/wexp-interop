# SCITT Receipt as the Core-02 boundary finding — package 001

**Recorded result: both appraisers equal the four frozen expectations on all twenty result components, in the workspace run and in the package run.** The package composition was committed first (card revision 1, `execution: not-run`), the run was made from that committed payload with clean pinned appraiser checkouts, and card revision 2 records it in [`evidence/RUN-RECORD.json`](evidence/RUN-RECORD.json) and [`evidence/comparison.json`](evidence/comparison.json), as the [release procedure](../../../../docs/RELEASE.md) requires. Two honest gaps: no `EXPECTED-DELTA` file was committed before the package run (the preparation commit implied zero difference from the workspace run; `same_result_as_workspace_run` was recorded after it), and `evidence/comparison.json` is byte-identical to the workspace `payload/comparison.json` because the harness is deterministic, so the distinct evidence of the second run is the run record itself.

One Signed Statement was registered with the pinned SCITT API emulator (`scitt-community/scitt-api-emulator`, tag `pre-archive`, commit `cfebeee5`), its Receipt was retrieved and verified, and the Receipt was mapped to the `boundary_finding` of a `draft-sergeev-wexp-core-02` appraisal with `ceiling_base = observation`. Four normalized inputs exercise what the Receipt bounds and what it does not supply: an asserted execution base exceeds the ceiling; an asserted observation base is accepted only with a positive observation finding; the Receipt alone adds nothing; a Receipt whose inclusion proof was not checked makes the ceiling unusable.

Read [the card](record.json), [reproduction instructions](REPRODUCE.md), the frozen [mapping](payload/MAPPING.md), [source pin](payload/SOURCE-PIN.md), [case README](payload/README.md), [source inventory](evidence/SOURCE-MANIFEST.json), [pre-PR grounding check](evidence/GROUNDING-CHECK.md) and [license scope](LICENSE-SCOPE.md).

## Preserved material

`payload/` is the exact extraction of the primary artifact, a deterministic ZIP of the case directory frozen in the WEXP workspace at commit `428f0375`. It holds the Receipt and Signed Statement bytes with their digests, the mapping, the four inputs and the local profile catalog, the isolated session's expectations with its derivation, ambiguity record, digest list and file list, the workspace run record and comparison, and the harness that reproduces the registration. One line of `expectations/FILES-READ.txt` had a local directory prefix removed; the original digest is in the source inventory.

Labels such as A1-A6, P08 or R47 in the frozen payload refer to open-reading records kept in the author's other repositories: the section 7 matrix work (set 002) and the corpus re-derivation in `WEXP-dev/wexp-vectors`. At card revision 4 both were on branches; since 2026-11-08 they are on `main` of `WEXP-dev/wexp-vectors`, set 002 at `34b0b3516d0e717f7494b7c2697043bb318cc896` and the re-derivation at `edd67056873502a2c3cecf5dd2b8db71271c2f57`. The pins recorded in the frozen payload are unchanged. The labels are not needed to read this package.

The order of evidence is in the workspace history and repeated here: inputs and mapping first, the isolated derivation second, the appraisers last. The isolated session saw the Core text, the mapping as background, the inputs, a representation note and the section 13 fixture C01; it saw no implementation and no corpus.

## Next

Package 002 is intended to repeat the same mapping against the SCITT + SCRAPI reference
implementation presented by John Andersen at the IETF 127 hackathon (14-15 November 2026): one
Signed Statement registered through SCRAPI, the Receipt in the RFC 9942 COSE Receipts format with
RFC 9943 header labels, the same four inputs and the same `boundary_finding` mapping, a new source
pin recorded in its own `SOURCE-PIN.md`, and a fresh isolated derivation of the expectations before
any appraiser runs. The pinned revision is recorded when that package is prepared, not here. What
changes with a conformant Transparency Service is the strength of the limitation, not the ceiling:
the Receipt still bounds the appraisal to observation.

## Scope

The Receipt establishes that the emulator registered the statement bytes; for this emulator even that is weak, since its registration verifies no issuer signature, applies no registration policy, proves inclusion in a synthetic one-shot tree and signs with a self-signed same-run service identity. All of this is carried as the boundary limitation and appears in every result. The Receipt establishes nothing about execution, intent, invocation, PROV, IV, coverage, content truth or boundary control (Core-02 section 10).

This is same-project work with an isolated derivation step. It is not a SCITT profile, not a WEXP mapping profile, not a `wexp-vectors` vector, not interoperability with a production Transparency Service, not independent external reproduction and not a conformance result. No release, tag or DOI exists for this package. Coverage, whether a set of registered statements is complete for a scope, is the separate `draft-sergeev-wexp-coverage-00`; nothing here is a Coverage result.
