# SCITT Receipt as the Core-02 boundary finding — package 001

**Recorded result (workspace run): both appraisers equal the four frozen expectations on all twenty result components.** The package run on this public composition is recorded in a later card revision; the card in this revision says `execution: not-run` because the composition is committed before that run, as the [release procedure](../../../../docs/RELEASE.md) requires.

One Signed Statement was registered with the pinned SCITT API emulator (`scitt-community/scitt-api-emulator`, tag `pre-archive`, commit `cfebeee5`), its Receipt was retrieved and verified, and the Receipt was mapped to the `boundary_finding` of a `draft-sergeev-wexp-core-02` appraisal with `ceiling_base = observation`. Four normalized inputs exercise what the Receipt bounds and what it does not supply: an asserted execution base exceeds the ceiling; an asserted observation base is accepted only with a positive observation finding; the Receipt alone adds nothing; a Receipt whose inclusion proof was not checked makes the ceiling unusable.

Read [the card](record.json), [reproduction instructions](REPRODUCE.md), the frozen [mapping](payload/MAPPING.md), [source pin](payload/SOURCE-PIN.md), [case README](payload/README.md), [source inventory](evidence/SOURCE-MANIFEST.json) and [license scope](LICENSE-SCOPE.md).

## Preserved material

`payload/` is the exact extraction of the primary artifact, a deterministic ZIP of the case directory frozen in the WEXP workspace at commit `428f0375`. It holds the Receipt and Signed Statement bytes with their digests, the mapping, the four inputs and the local profile catalog, the isolated session's expectations with its derivation, ambiguity record, digest list and file list, the workspace run record and comparison, and the harness that reproduces the registration. One line of `expectations/FILES-READ.txt` had a local directory prefix removed; the original digest is in the source inventory.

The order of evidence is in the workspace history and repeated here: inputs and mapping first, the isolated derivation second, the appraisers last. The isolated session saw the Core text, the mapping as background, the inputs, a representation note and the section 13 fixture C01; it saw no implementation and no corpus.

## Scope

The Receipt establishes that the emulator registered the statement bytes; for this emulator even that is weak, since its registration verifies no issuer signature, applies no registration policy, proves inclusion in a synthetic one-shot tree and signs with a self-signed same-run service identity. All of this is carried as the boundary limitation and appears in every result. The Receipt establishes nothing about execution, intent, invocation, PROV, IV, coverage, content truth or boundary control (Core-02 section 10).

This is same-project work with an isolated derivation step. It is not a SCITT profile, not a WEXP mapping profile, not a `wexp-vectors` vector, not interoperability with a production Transparency Service, not independent external reproduction and not a conformance result. No release, tag or DOI exists for this package. Coverage, whether a set of registered statements is complete for a scope, is the separate `draft-sergeev-wexp-coverage-00`; nothing here is a Coverage result.
