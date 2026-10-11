# WIMSE AAR-02 INTEROP-001 — frozen public inputs

This is the prospective input snapshot for package **pkg-001**. It preserves a
bounded AAR-to-WEXP pilot and a strong native baseline for a new public replay.
At the pre-run freeze, this input snapshot contains **no result of that new
replay**. A subsequent results/ addition is identified by the outer package
card. The prior private semantic result is supplied in full as a known reference.
This README remains a historical, prospective preparation statement.

The experiment asks whether the recipient preserves the distinction between
evaluated denial and inability to evaluate, rejects incompatible revisions,
and limits inferences from declared human oversight and a trusted but wrong
producer. The earlier private pilot obtained the same local decisions through
WEXP and its strong native alternative. The new public composition expects
that parity to reproduce; success must be recorded by a subsequent execution.

## Fixed scope

| Input or procedure | Count |
|---|---:|
| Published AAR-01 corpus | 47 |
| Published AAR-02 corpus | 55 |
| Local signed extensions | 19 |
| Compatibility and dispatch cases | 9 |
| Total pipeline cases | 130 |
| Output mutation inputs | 16 |
| Controlled trusted-producer worlds | 2 |

The 102 published records are part of the 130 cases. The separate corpus judge
invokes the same native implementation again. These are not independent totals.

## Read and reproduce

1. [Experiment and baseline](docs/EXPERIMENT.md)
2. [Reproduction procedure](docs/REPRODUCE.md)
3. [Expected delta](docs/EXPECTED-DELTA.md)
4. [Limitations](docs/LIMITATIONS.md)
5. [Recipient contract](consumer/CONTRACT-NOTES.md)
6. [Public sources](SOURCES.lock.json) and [composition provenance](PROVENANCE.json)
7. [Readable prior reference](reference/private-pilot-semantic-results.json)
8. [Licenses](LICENSES/README.md)

Before a first run, verify the exact prospective inventory:

    python3 -B verify_inputs.py --pre-run

The complete command sequence, including strict typed JSON comparison and the
exact semantic-byte pin, is in [docs/REPRODUCE.md](docs/REPRODUCE.md). A
verification PASS at this step only checks input identities and prospective
conditions. It does not run the pilot.

## Publication and historical atoms

The source profile and policies remain byte-for-byte identical to the private
pilot. PRIVATE_EXPERIMENTAL_BOUNDED_MAPPING is the historical profile's status
atom. The outer package records the current public preparation/publication.
The fixed policy evaluated_at value is scenario context, not a claim that a
live authorization source was queried on the new replay date.

The native source snapshots are reproduction inputs; ongoing implementation
development belongs in its own repository. No internal mapper-to-evaluator
standard is introduced. No change to the published Core TXT, earlier private
results, or historical EMILIA publication is made by this package.
