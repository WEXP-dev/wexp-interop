# Separate Zenodo record — prepared content, no deposit performed

This package has **no created Zenodo record, reserved DOI or Zenodo
publication**. ZENODO-RECORD-CONTENT.json is a concrete content descriptor for
a later manual upload. It is not an API request body or a response from
Zenodo. The current GitHub carrier is described independently by the outer
PUBLICATION.json and record.json.

## Upload procedure when account access is available

1. Use a **new separate record** for `wimse-aar-02-interop-001 / pkg-001`.
   Do not select a new version of the EMILIA record or reuse its concept DOI.
2. Select the exact ZIP identified in the descriptor and verify its size,
   SHA-256 and MD5 against the final freeze. The archive contains root
   PREPARATION.md plus the complete payload/ subtree. Keep that layout: the
   frozen input verifier reads its parent preparation file. Current outer
   card/publication metadata are maintained separately.
3. Transfer the title, description, creators, keywords, actual source links and
   scoped license notice from the content descriptor. Confirm the deposit
   interface's supported resource-type and license entries at upload time.
   Do not describe the multi-license package as having one overriding license.
4. If a DOI is reserved, record the actual returned record ID and DOI in a new
   external publication observation. A reservation is not publication.
5. Before publication, compare the preview's exact file and metadata with the
   selected archive and descriptor. Preserve applicable native Apache and IETF
   notices and the separate WEXP MIT/CC BY grants.
6. After publication, retrieve the deposited file and compare its bytes/hash
   with the selected ZIP. Record the actual version record, DOI, publication
   observation and file checksum in a subsequent external metadata revision.
   Do not modify the frozen payload or retrospectively claim an earlier DOI.

A GitHub Release is a separate optional carrier and has not been created for
this package. Follow the collection's current release procedure, including a
fresh repository/organization integration check, before any such release.
This pending Zenodo workflow does not expand the experiment's result or its
independence claims.
