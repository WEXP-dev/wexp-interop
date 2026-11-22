# Author review of the AEP mapping

Anton Sokolov reviewed the WEXP mapping against draft-sokolov-rats-aep-composition-06 and aep-sandbox at `f6c88be63c5aa12b8e8f6bf35a378a6a5fca9cd4`. His review was dated 14 November 2026 and received 17 November. He checked the digest of the draft, cited passages, and the bytes of five sandbox files covering the verifier, the package and mandate modules, and both samples. His review covered how the mapping read AEP. He did not examine the Core derivations or run the appraisers. [Retained AEP draft](../payload/evidence/basis/specifications/draft-sokolov-rats-aep-composition-06.txt) · [Sandbox revision](https://github.com/tyche-institute/aep-sandbox/tree/f6c88be63c5aa12b8e8f6bf35a378a6a5fca9cd4)

On 21 November Mikhail Sergeev accepted the following result row and attribution as proposed by Anton.

WEXP x AEP (Anton Sokolov): two aep-sandbox samples (signed record and mandate, no platform Evidence) mapped to Core-02 under two evaluation contexts; both appraisers agree; the execution claim stays not evaluated and the boundary unsupported, while the sandbox verifier checks authority and record authorship. Mapping checked by the AEP author against -06.

Mapping and appraisal: Mikhail Sergeev (WEXP). AEP draft and sandbox: Anton Sokolov (Tyche Institute). The AEP author reviewed the mapping against draft -06 and the pinned sandbox code and did not run the appraisers.

The sample packets carry the signed record and mandate from sandbox Layer 2. The reported boundary result applies to those samples. The trial leaves the boundary-grounding question for Layer 3, with appraised platform Evidence, open. The sandbox verifier performed the concrete authority and record-authorship checks. AEP-06 assigns the separate decision about whether the action remains authorized and applicable to the relying party. The citation correction identifies the passages supporting the treatment of consumed state. [Citation correction](../CITATION-CORRECTIONS.md)
