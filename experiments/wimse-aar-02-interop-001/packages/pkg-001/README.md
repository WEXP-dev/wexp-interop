# WIMSE AAR-02 INTEROP-001 — pkg-001

The public composition completed its **11 October 2026 local replay** from an
earlier public preparation commit. **130/130 pipeline cases passed, 16/16
output mutations were rejected, and two controlled worlds preserved the
declared support limits.** WEXP and the strong native baseline made the same
local decisions. The full semantic result matched the known private reference
with strict JSON types and exact serialized bytes.

| Dimension | State and scope |
|---|---|
| Integrity | Frozen inputs and completed payload have exact byte inventories; see the verification evidence and archive identity. |
| Execution | Local run completed from public preparation commit `70b4491a1ec8aab5af61f31510220067e3e5cfba`. |
| Independent reproduction | Not performed by an external team; shared native reader, consumer policy and coordinated environment. |
| Comparison | No local decision difference from the strong native baseline; zero permitted semantic delta from the separate private reference. |
| Publication | The current carrier and publication state are in [record.json](record.json) and [PUBLICATION.json](PUBLICATION.json). No DOI is asserted. |

The **102 published native records are included in the 130 cases**, alongside
19 local cases and nine compatibility/dispatch cases. The separate native
corpus check is not an independent sample. Sixteen output mutations concern
the additional WEXP contract, not extra truth detection over the baseline.

## Read the evidence

- [Actual results and interpretation](payload/reports/RESULTS.md)
- [Reproduce and verify](REPRODUCE.md)
- [Historical pre-run statement](PREPARATION.md), [input freeze](payload/pre-run/FREEZE.json) and [prospective expected delta](payload/pre-run/EXPECTED-DELTA.json)
- [Full new results](payload/results/public-run-001/semantic-results.json), [strict comparison](payload/results/public-run-001/reference-comparison.json) and [execution export identities](payload/run-evidence/EXPORT.json)
- [Source identities](payload/SOURCES.lock.json), [known reference provenance](payload/reference/PROVENANCE.json) and [limitations](payload/docs/LIMITATIONS.md)
- [License scope](LICENSE-SCOPE.md) and [citation](CITATION.cff)

A2's evaluated deny and A10's not-evaluated deny remain distinct. EV3 is
malformed under the new revision even though its exact bytes are the older
A1. Declared oversight does not establish human participation or authority.
Both trusted-producer worlds yield `record-only` admission and no execution
establishment from their identical signed inputs; only the harness's extra
oracle distinguishes the controlled endpoint outcomes.

The pre-run profile, policy time, README and preparation documents are
unchanged historical inputs. The new result is added at separate paths. The
package does not update published Core-01, replace the private reference,
alter EMILIA, standardize an internal mapper interface or establish general
carrier interoperability.
