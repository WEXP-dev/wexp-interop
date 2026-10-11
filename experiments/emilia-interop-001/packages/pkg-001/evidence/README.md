# Public verification evidence

This directory provides the public sources required to assess the external package card. [SOURCES.json](SOURCES.json) identifies the ZIP, freeze and public SHA-256 anchor. [EXPORT-MANIFEST.json](EXPORT-MANIFEST.json) lists every explicitly selected historical preparation file with its original byte identity and `transformation: none`.

The retained logs sometimes contain local preparation paths. These are historical environment labels, not dependencies on private repository access. Full mail, mail-search records, account settings, screenshots, private repository snapshots and local candidate bundles are excluded.

| Question | Evidence |
|---|---|
| Which published files were retrieved? | [Zenodo record](historical-preparation/zenodo-record-22056151.json), [record retrieval](historical-preparation/zenodo-record-request.json), [asset download comparison](historical-preparation/asset-download-comparison.json) and the individual request records below `historical-preparation/zenodo/` and `historical-preparation/github/`. |
| Where was the expected SHA-256 already written? | [Exact metadata copy](historical-preparation/expected-sha-source-PUBLICATION-METADATA.yaml), [file identity](historical-preparation/expected-sha-source-identity.json), [public commit API observation](historical-preparation/expected-sha-source-commit.json). The commit is dated 23 August 2026, after the release. |
| What does the freeze establish? | [Initial binding observation](historical-preparation/freeze-binding-check.json), [actual standalone replay](historical-preparation/freeze-binding-replay-002.json), [exact commands](historical-preparation/freeze-verifier-commands-20261011.json). Eleven historical bindings and three additional consistency checks passed. No signature or trusted time was verified. |
| Are name/type/mode assumptions visible? | [ZIP inspection](historical-preparation/archive-inspection-001.json) and its [source](historical-preparation/inspect_archive.py). All 95 members were read; 68 files, 27 directories, no detected listed collisions or special types. |
| What did extraction and the old verifier check? | [Extraction report](historical-preparation/extraction-verification-001.json) and its [historical source](historical-preparation/extract_and_verify.py). This source is retained for provenance; use the current collection procedure for a new replay. |
| Are negative controls retained? | [Initial control set](historical-preparation/freeze-negative-controls-001/results.json) and [corrected control set](historical-preparation/freeze-negative-controls-002/results.json), with exact mutated inputs, harness and per-case reports. |

In negative set 001, all eight inputs were rejected, but N04's 64 zero characters were parsed by YAML as an integer and failed a type check before the intended digest comparison. Set 002 corrects that fixture to alphabetic hexadecimal characters; all eight rejections then matched their predeclared reasons. Both histories remain available; the earlier result is not overwritten.

The [historical release response](historical-preparation/github-release-374898832.json) reported `immutable: false`. The [tag response](historical-preparation/github-tag-eb4011bcfe65e11545ddb36ebf906637002aca4f.json) reported a valid tag signature over a Git object, not a signature over the ZIP or freeze. These are saved API observations, not a local PGP verification or a permanent claim about platform state.

## Current replay and exact commit reports

[REPRODUCE.md](../REPRODUCE.md) names the current public commands. New reports are written outside the repository. The collection's CI and publication record identify the exact tested commit. A report stored later must keep that original tested identity rather than claiming to verify its own containing commit.

The current `scripts/emilia/verify_clean_clone.py` derives from the retained [preparation source](historical-preparation/verify_clean_clone-003.py). It changes the archive directory name to `source-archive/` and requires the preserved old main to be an ancestor, allowing later collection commits. It still checks the requested exact commit, 68 extracted file bytes and modes, 69 retained earlier main blobs, `-text` under `core.autocrlf=true`, actual POSIX permissions under `umask 0022`, and the unmodified archived verifier.

Neither replay, manifest PASS nor a second process establishes independent external reproduction, authorship, human approval, physical truth or a new interop result.
