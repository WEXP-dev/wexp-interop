# Package publication procedure

Repository layout changes and package preparation are reviewable changes in Git. Creating a new release is a separate publication action.

## Prepare before execution

For a new executable package, commit its exact source pins, public file composition, policies, fixtures, expectations and baseline comparison rule before the first run of that public composition. If a private reference already exists, also commit `EXPECTED-DELTA.json`: the exact intended input/result differences, allowed transformations and unchanged comparison scope. Use an explicit empty list when no differences are expected.

Keep the comparison with a native baseline within the new run separate from comparison with a prior reference. A private reference hash without its readable contents is not publicly reproducible evidence. Unexpected differences are preserved and addressed by a new explanatory record or candidate; expectations are not silently rewritten after seeing the output.

Run the pinned procedure, save inputs, environment, dependencies, actual outputs and limitations, and identify the preceding preparation commit. A package without an executable component can publish fixtures and expectations with `execution: not-run` and an explicit unexecuted status. Public availability is not independent external reproduction.

## Check before every release

Record the repository, experiment/package, proposed tag, exact commit, observer, UTC time, evidence references, scope of access, any actions and remaining unknowns. Check close to the release, because configuration can change after an earlier observation.

| Surface | Record |
|---|---|
| Repository Webhooks | Relevant hook configuration and release-event delivery path, or an observed empty list. |
| Organization Webhooks | Relevant organization-level path, or the exact unobserved scope/blocker. |
| OAuth application policy and GitHub Apps | Relevant application access. A grant establishes capability, not active autoarchiving. |
| Zenodo GitHub integration | Selected account, repository presence and observed toggle state. Absence from a list is not an observed OFF toggle. |
| Publication target | A separate record/version lineage for the experiment, rather than the EMILIA concept DOI. |

The owner or an authorized agent may perform these checks through a permitted session. Record a `Sync now` operation as an action that requests an inventory refresh, together with the returned status and observed refresh age. A click alone does not establish completed refresh. Record grants, toggle changes or hook changes separately from observations. Do not create a test release to discover how autoarchiving is configured.

An unresolved path that could place a collection release in the EMILIA DOI lineage blocks that release until the observations and selected publication method resolve it. It does not block preparation of a repository PR. General code inspection or an old empty hook list is insufficient to state that every possible automation path is permanently disabled.

Official operational references: [Zenodo GitHub repository enablement](https://help.zenodo.org/docs/github/enable-repository/) and [GitHub webhook creation](https://docs.github.com/en/webhooks/using-webhooks/creating-webhooks). Account evidence stays private; a public release record may contain the minimal dated conclusion, checked scope, actions and limitations.

## Publish the reviewed bytes

1. Validate the card, generated catalog, package manifest, citations and license scope.
2. Verify a fresh clone of the exact candidate commit. Preserve the report outside that commit to avoid a self-referential identity; a CI run or later publication evidence record identifies the tested commit.
3. Review the new public surface. Historical payload and publication-history text remain visibly designated as historical; current cards must not inherit their stale publication state.
4. Merge the reviewed change and, if the exact merged commit differs, verify that commit before release. Create the namespaced package release only after the fresh release check passes.
5. Archive the package in its own Zenodo record when that publication path is available and authorized. An unavailable DOI is reported as unavailable, never guessed or borrowed from another record.
6. Read back the public carrier, file identities, citations and result claims. Retain prior artifacts and published Core source bytes.
