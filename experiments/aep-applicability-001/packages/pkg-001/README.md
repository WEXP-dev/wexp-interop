# WEXP × AEP · package 001

WEXP x AEP (Anton Sokolov): two aep-sandbox samples (signed record and mandate, no platform Evidence) mapped to Core-02 under two evaluation contexts; both appraisers agree; the execution claim stays not evaluated and the boundary unsupported, while the sandbox verifier checks authority and record authorship. Mapping checked by the AEP author against -06.

Mapping and appraisal: Mikhail Sergeev (WEXP). AEP draft and sandbox: Anton Sokolov (Tyche Institute). The AEP author reviewed the mapping against draft -06 and the pinned sandbox code and did not run the appraisers.

Mikhail Sergeev initiated this trial and ran it on the WEXP side on 9 November 2026. He froze the mapping and inputs, then the expectations, before running the two Core appraisers. He sent the material to Anton on 12 November for review. Anton replied on 17 November, after the run. Mikhail accepted his wording and citation corrections on 21 November. The historical trial predates the Interop Test Lab procedure for obtaining a submitter's agreement to a new mapping and its expectations before a run.

## Six assessments from two signed samples

The sandbox checks a signed action record against the mandate and its local consumed-nonce state at the fixed evaluation time. Core evaluates a different question for each normalized input. How much support does the material supply for the assertion that the specified refund took place?

| Case | Signed record | Sandbox verdict | Core-02 verdict in strict / attrib |
| --- | --- | --- | --- |
| a · first submission | `good`, EUR 250 | ALLOW (exit 0), nonce consumed | downgrade / downgrade |
| b · second submission | Same signed bytes as a | DENY (exit 2), replayed | downgrade / downgrade |
| c · first submission | `exceed-scope`, EUR 9,000 against a EUR 1,000 limit | DENY (exit 2), scope_violation | downgrade / downgrade |

The strict context admits attested boundary grounding. The attrib context also admits attributed grounding. For these samples, identity attribution passes the grounding gate only in attrib. The evidence needed to establish boundary control is absent in both contexts. Cases a and b produce identical normalized bytes within each context, giving four distinct byte sequences across six assessed inputs. [Inputs](payload/inputs/) · [Mapping diagnostics](payload/evidence/MAPPING-DIAGNOSTICS.json)

The signed records support observation of what the agent reported. Actual execution is `not-evaluated` and the observation boundary is `unsupported`. The substantive reason is `E_BOUNDARY_NOT_SUPPORTED` and the evaluation gap is `E_BASE_NOT_EVALUATED`. Neither sample contains platform Evidence or an independent observation of a refund. This result applies to the tested signed-record samples. A composition that includes appraised platform Evidence would require its own boundary assessment. [Scope of the AEP review](evidence/AEP-REVIEW.md)

## Agreement on the historical outputs

Both appraisers agreed on **120/120** result components across the six assessments. Each agreed with **114/120** frozen expectations under the recorded component comparison rules. All six differences concern `boundary_ceiling`. The frozen expectations use the string `"unavailable"`. Both appraisers returned JSON `null`. Both representations can be inspected directly. [Frozen expectations](payload/expectations/v1/) · [Reference outputs](payload/evidence/core/ref/) · [Second appraiser outputs](payload/evidence/core/check/) · [Historical results](payload/RESULTS.md)

Both appraisers originated in separate AI-assisted sessions under the same WEXP operator. The tested second implementation includes documented changes made after its first corpus comparison. Anton reviewed the interpretation of AEP. This experiment has no recorded independent reproduction. [History of the second appraiser at the tested revision](https://github.com/WEXP-dev/wexp-check/blob/a2fd1ffd68b234592979a8aa8965bd580ede4d76/CHANGES-AFTER-RUN.md)

## Verify the public package

- [Mapping](payload/MAPPING.md), [profile](payload/PROFILE.md) and [correction to the historical AEP citations](CITATION-CORRECTIONS.md)
- [Pinned sources](payload/SOURCE-PINS.json), [public source archive](source-archive/AEP-CORE02-PUBLIC.zip) and [inventory of exact files and public representations](evidence/PUBLIC-INVENTORY.json)
- [Verification and replay instructions](REPRODUCE.md), [package checksums](PACKAGE-MANIFEST.sha256) and [comparison baseline](EXPECTED-DELTA.json)
- [Collection card](record.json), [citation](CITATION.cff) and [license scope](LICENSE-SCOPE.md)

The public archive contains the selected evidence. The inventory documents which files retain their historical bytes and how the public versions of operator logs and metadata relate to their historical sources. Statements dated 9 November in the frozen material describe the state at the time of that run. The historical RESULTS.md describes the full 9 November record, including workstation-specific diagnostic streams. The public inventory identifies the observations available in this selection.
