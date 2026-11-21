# Corrections to the AEP-06 citations

Mikhail Sergeev accepted these corrections on 21 November 2026 after Anton Sokolov reviewed the mapping. Line numbers are one-based in the retained text of draft-sokolov-rats-aep-composition-06, SHA-256 `a2561d39ddd1707d04df100137bdbff2bcde367a477e06e6068efe45572e1431`. [Pinned draft text](payload/evidence/basis/specifications/draft-sokolov-rats-aep-composition-06.txt)

| Proposition | Support in AEP-06 |
| --- | --- |
| The sandbox nonce is the per-action identifier used in the replay check. | Lines 328–330 describe `aep_action_id`. |
| The relying party separately checks whether the action remains authorized, within scope and unconsumed. A signed record can remain cryptographically valid after the action identifier has been consumed. | Lines 526–530, vector V6 at lines 585–589 and §14.1 at lines 804–809. |
| The draft sets freshness requirements for the attestation exchange. | Lines 509–511 concern an expired result or a nonce mismatch (`eat_nonce`). Cite these lines only for the draft's freshness requirements. |
| Authority is carried by reference to the digest of the exact mandate. The relying party decides whether to act. | Line 332, lines 144–151 and lines 526–530. |

Read these corrections alongside the following three pre-run records. Their original text and line references are preserved.

- [MAPPING.md](payload/MAPPING.md), line 56, the row about consumed-state membership. Line 104 discusses the draft's freshness requirements.
- [DERIVATION.md](payload/DERIVATION.md), lines 94–95. The combined list of references covers both attestation freshness and consumption of an action identifier. The table above identifies which source supports each proposition.
- [AMBIGUITIES.json](payload/AMBIGUITIES.json), choice `B-RC-05`, `aep_sources`. Lines 509–511 in this list support attestation freshness only.

The general freshness caveat in the [historical results](payload/RESULTS.md) uses lines 509–511 for the draft's own freshness requirements. The component derivations also cite lines in the Core XML, which uses its own line numbering.
