# WEXP × EMILIA commit/reveal record 001

Status: **COMPLETE FOR FINAL-CANDIDATE REVIEW — PUBLICATION NOT AUTHORIZED**  
Authority: Founder  
Purpose: preserve the actual commitment/reveal chronology without revising any
frozen reading or expectation.

## Frozen identities

| Item | Exact identity |
| --- | --- |
| Neutral five-case fixtures | `fixtures.yaml`, SHA-256 `d972dbb549aaaa25e92c32a936acba4d9a686e9ca62fe6bd556b12be2962cfcc` |
| Pre-reveal WEXP commitment carrier | `WEXP-EMILIA-INTEROP-001-SHAREABLE-v2.zip`, 2,809 bytes, SHA-256 `0ec17bcf9b88af17016c7e05d465012af604292210a858df5fa8f9bcf00d57a0`; ZIP and internal manifest PASS |
| Frozen WEXP five-case reading | `wexp-reading.yaml`, SHA-256 `a185e6760de149375e657b1429adc1ea329ed9f9705b9d1c2b505dcc8e3ea984` |
| Frozen EMILIA five-case reading | `emilia-reading.json`, SHA-256 `b43f8ac6dce465258c75a42117d2750a6bafa163846251416e87cec371a4bad6` |
| Five-case comparison | `WEXP-EMILIA-EP-COMPARISON-001.md`, SHA-256 `272a9b08a213702ee2156438b7736b954c7a32bc4a190cce92d3d82226266934` |
| Pair freeze archive | `WEXP-EMILIA-PAIR-FREEZE-001.zip`, 18,158 bytes, SHA-256 `ae237263c86ee0b5c2b6387159d81957efe47e20161b74dd363da5a530705282` |
| P | `WE-EP-P.json`, SHA-256 `b552da51858d0256a562e800a81a870435d6e136c9bc28833b962b6d3723fb3e` |
| P-1 | `WE-EP-P-1.json`, SHA-256 `67556d28d272b4b01a73e1c1465248644dd7a05460fc149aa77df92cf36403a0` |
| Frozen WEXP pair expectation | `wexp-expectation.yaml`, SHA-256 `42eeecaba33238d8c94bbb9d5bb22ab46721de6de74cff455b8115c17892088a` |
| Frozen EMILIA pair expectation | `emilia-expectation.freeze.json`, 885 bytes, SHA-256 `6e0dc6c87f853cacdeeb676b27690e54bdb8a7a7aa86611c5ffe233387e256a4` |
| EMILIA execution receipt | `emilia-execution-receipt.json`, 1,963 bytes, SHA-256 `2d61071712ef4424d1b308afb6a3b8752b4effcf2525c0c08c97cff16617b77f` |
| EMILIA semantic baseline | `emiliaprotocol/emilia-protocol@9a04bea7fe680345132f6f6251fdb9a63fd8aeb2` |
| WEXP publication baseline | `WEXP-dev/wexp-spec@b28a46e7764c2ef14decc35394f21278fca9c988` |
| WEXP reading-time vector context | `WEXP-dev/wexp-vectors@c745e5abebddfd99cd62cdb3e40dddaf6582bdd9` |
| WEXP reading-time reference context | `WEXP-dev/wexp-ref@d8f7e512a56b90b17377444c07cbc006ee76b7b5` (`PARTIAL`) |

Later public heads may be recorded as current-head metadata. They do not replace
these frozen experiment identities.

## Actual chronology

The order below preserves the established process. An absent exact timestamp is
shown as such rather than reconstructed from filesystem metadata or email
formatting.

| Order | Event | Time evidence | Evidentiary status |
| ---: | --- | --- | --- |
| 1 | Neutral five-case fixture freeze | Exact freeze communication time not retained in this local record | The byte identity above is established and common to both readings. |
| 2 | WEXP five-case reading commitment | WEXP artifact freeze time `2026-08-20T03:09:46-07:00`; exact commitment-message time not retained here | The pre-reveal carrier above disclosed the neutral fixture and WEXP reading hash, not the reading itself. Commitment preceded reveal. |
| 3 | EMILIA five-case reading commitment | Exact commitment-message time not retained here | Commitment preceded both reveals required for comparison; committed SHA-256 is recorded above. |
| 4 | WEXP five-case reveal | Exact reveal-message time not retained here | Revealed `wexp-reading.yaml` matched its commitment. The sent reveal ZIP was 8,375 bytes, SHA-256 `fbfd3d7bc66033ae51af280970ab2129d39731a64169cc1178300c94ffffbe59`; Iman reported the same file hash and successful manifest checks after receipt. |
| 5 | EMILIA five-case reveal | Attachment message dated `2026-08-20T12:23:14-05:00` | Revealed 5,078-byte `emilia-reading.json` matched its commitment; the exact bytes are retained under `source/original/`. |
| 6 | Five-case comparison | Record date `2026-08-20` | Read-only comparison completed; record hash is pinned above. |
| 7 | P/P-1 construction | Fixture creation time `2026-08-21T00:31:23Z` | Exact fixture bytes and controlled delta were frozen. |
| 8 | WEXP P/P-1 expectation freeze | `2026-08-21T00:32:35Z` | WEXP expectation was frozen before any WEXP or EMILIA implementation execution. |
| 9 | Pair package sent to Iman | `2026-08-21T00:58:41Z` | Authenticated Gmail message `1a021d3e03807dc2`, RFC Message-ID `<CAC-beJ6LsOw5EMWJj+JS4OQare+6OKV4egvNkO4sMuL6LXy-hA@mail.gmail.com>`. |
| 10 | EMILIA P/P-1 expectation freeze | Before `2026-08-21T02:41:04Z`; exact freeze instant not declared | The 885-byte source declares `fixed_before_emilia_execution`; the receipt binds its exact SHA-256. No intrinsic timestamp is added to the source. |
| 11 | EMILIA implementation execution | `2026-08-21T02:41:04Z` | Exact receipt links the pair package, EMILIA expectation, P, P-1, and frozen baseline; both actual results reproduce the expectation. |
| 12 | EMILIA expectation and receipt reveal | `2026-08-21T02:48:33Z` | Iman's authenticated Gmail reply `1a02238850e8d049`, RFC Message-ID `<CAOfgHgopYf29ydongKvjJMT2mh4hEmNyz6-OeL-AqaPxmyHMyg@mail.gmail.com>`; DKIM, SPF, and DMARC PASS. |
| 13 | WEXP implementation execution | Not performed | Input is not constructible under the frozen public mapping surface; no WEXP engine output is invented. |
| 14 | Final joint review | Future action | Final candidate is returned for Founder and Iman review. |
| 15 | Publication | Not authorized | No publication has occurred. |

## History qualification

The WEXP-side five-case freeze followed a Founder correction clarifying that the
two readings were to be frozen independently before comparison. No EMILIA
per-case outcome was used to create the WEXP reading. The correction is retained
because it explains the operative independence protocol; superseded formatting
or ordinary email-staging mistakes are not part of the scientific record.

## Commitment/reveal conclusion

- Both original reading commitments were fixed before the first reveal.
- Both revealed readings matched their commitments byte-for-byte by SHA-256.
- The five-case comparison did not rewrite either reading.
- The WEXP P/P-1 expectation was frozen before implementation execution.
- The EMILIA P/P-1 expectation was independently frozen before EMILIA
  execution; its exact hash is bound by the receipt.
- The receipt reproduces the frozen EMILIA expectation for P and P-1.
- No WEXP implementation was invoked because no frozen public EP→WEXP mapping
  constructs the required Core `AppraisalInput`.
