# Verification evidence

[SOURCES.json](SOURCES.json) identifies the selected Candidate 003 archive by size and SHA-256, the candidate's internal manifest, the record that holds the two-scope verdict, and the original version pins. No public carrier existed when this package was prepared, so the archive is named by a content-digest URI rather than a location.

Candidate 003 has no separate FREEZE record of the INTEROP-001 kind. The current check instead verifies the candidate's own internal manifest (56 entries; the manifest excludes itself) and pins the verdict record. Both are inside the unchanged payload.

The candidate's own preparation records remain in the payload, among them the [disclosure, privacy and reproducibility review](../payload/publication-candidate/CANDIDATE-CHECKS-002.json) and the [counterparty fairness review](../payload/publication-candidate/COUNTERPARTY-FAIRNESS-REVIEW-002.json). They are historical records of the WEXP-side preparation; this package does not promote them into an external reproduction.

New replay reports are written outside the repository by the commands in [REPRODUCE.md](../REPRODUCE.md).

[ZENODO-PUBLICATION.json](ZENODO-PUBLICATION.json) records the later archival publication on 12 November 2026: the version and concept DOIs, the published metadata, and the unauthenticated public download checked byte-for-byte against the original Candidate 003 ZIP. The earlier `public_carrier: null` in `SOURCES.json` remains as the preparation-time state. This publication check does not establish an independent reproduction or change the frozen payload.
