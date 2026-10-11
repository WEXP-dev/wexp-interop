# Attribution, modifications and new publication grants

The native readers, packaging modules, vector manifests and source envelopes
come from Sankalp Gilda's agent-evidence-vectors repository at the exact
revisions in SOURCES.lock.json. They retain the upstream Apache License 2.0
and copyright notice in vendor/aar01/LICENSE and vendor/aar02/LICENSE.

Local fixtures L01–L19 are modified and re-signed derivatives of AAR-02
vectors A1, A2 and A3. fixtures/local-manifest.json records each parent and the
changed scenario; generate_local_fixtures.py preserves the modification
procedure. These derived fixture envelopes retain Apache-2.0 treatment. All
keys are deliberately public experiment keys; they are not deployment keys.

The copied HOF evaluator originates in the WEXP private research commit
3a45ebb1272a7fceed672bca356c8861edf12630. The exact source identity is in
SOURCES.lock.json and the complete code is publicly supplied at
vendor/core_hof/evaluator.py. The earlier private file had no public license
declaration. WEXP-origin Python code, including this copy and the pilot,
consumer and preparation verification helpers, is granted MIT terms from this
new public distribution. This does not assert a previous MIT license.

WEXP-authored public prose and JSON manifest, oracle, profile, policy and
reference presentation are granted CC BY 4.0 terms from this publication.
Attribution: WEXP-dev pilot contributors, 2026. This scope excludes underlying
third-party content and the derived fixture envelopes addressed above.

The published IETF TXT files retain their original notices and exact bytes.
Neither the new MIT/CC BY grants nor the collection's root notices replace
their IETF Trust terms or any upstream rights. No trademark rights, endorsement,
IETF status or certification is implied. See LICENSES/SCOPE.json.
