# WEXP interoperability records

This repository collects versioned experimental packages and their reproduction materials. Each experiment has the same location under `experiments/`; each package has an external card and a separately identified payload. The [generated catalog](catalog.json) is an index of those cards, not a second source of experimental results.

## Experimental records

| Experiment | Package | Recorded result | Scope |
|---|---|---|---|
| [WEXP × EMILIA INTEROP-001](experiments/emilia-interop-001/packages/pkg-001/README.md) | `pkg-001` · [version DOI](https://doi.org/10.5281/zenodo.22056151) | **Branch A — Explicit Bridge Required** | Historical controlled-fixture record; migration replays archived evidence. |
| [WEXP × WIMSE AAR-02 INTEROP-001](experiments/wimse-aar-02-interop-001/packages/pkg-001/README.md) | `pkg-001` · [exact carrier and archive](experiments/wimse-aar-02-interop-001/packages/pkg-001/record.json) | **No local decision difference from the strong native baseline** | 130 expected case outcomes, 16 output refusals and two controlled worlds; known reference, coordinated local execution. |
| [WIMSE AAR / Core-02 bounded migration](experiments/wimse-aar-02-interop-001/packages/pkg-002/README.md) | `pkg-002` · [retained run identities](experiments/wimse-aar-02-interop-001/packages/pkg-002/record.json) | **No local decision difference from the strong native baseline** | 130 original cases, 35 full appraisals; catalog admission adds no execution. |
| [SCITT Receipt as the Core-02 boundary finding](experiments/scitt-receipt-boundary-001/packages/pkg-001/README.md) | `pkg-001` · [card](experiments/scitt-receipt-boundary-001/packages/pkg-001/record.json) | **Both appraisers equal the frozen expectations on all four inputs**; replayed on 10 November 2026 by Laurent Lemonnier in GitHub Actions in his own repository with the same published code and public expectations, with the same result (not an independent implementation; SCITT registration not repeated) | One pinned-emulator Receipt mapped to the boundary finding, ceiling observation; four inputs; expectations derived in a separate same-project session before any appraiser ran; its recorded file list is in the payload, and that it saw no implementation or corpus is an operator declaration. |
| [WEXP × EMILIA INTEROP-002](experiments/emilia-interop-002/packages/pkg-001/README.md) | `pkg-001` · [version DOI](https://doi.org/10.5281/zenodo.24180793) · [card](experiments/emilia-interop-002/packages/pkg-001/record.json) | **Split verdict: bridge sufficiency SUPPORTED; joint comparison INCONCLUSIVE (5/7), NOT_DERIVED (2/7)** | Historical INTEROP-002 result (Candidate 003, Core-01 surface, EMILIA 9a04bea7); archived evidence replayed; exact archive published on Zenodo; Apache-2.0 confirmed for code and vectors. |

An experiment's presence in this collection does not establish conformance, semantic equivalence, full interoperability, or IETF adoption. The card states what was executed, how comparison was made, and what kind of independent reproduction is available. Use those dimensions separately.

## Proposals and bounded follow-on trials

[AAC completeness preparation](docs/proposals/aac-completeness-001/README.md)
contains the proposed clarification, two examples, an upstream patch and the
public tooling pins observed on 28 October 2026. No AAC integration or jointly agreed profile is claimed.

[WIMSE / Core-02 migration trial](docs/proposals/wimse-core02-replay-001/RESULTS.md)
preserves the original bounded 130-case replay and its complete observations.
That result is now represented by [package 002](experiments/wimse-aar-02-interop-001/packages/pkg-002/README.md)
in the catalog; admitting it adds no run and does not replace package 001.
AAC preparation remains outside the completed-results catalog.

## Find and verify a package

- Read the package `README.md`, `record.json` and reproduction instructions first.
- Use the exact source archive and its digest for the historical published object. Read the card's payload/archive relation: a payload may be a verified extraction or a separately pinned source snapshot; it does not reproduce ZIP container metadata.
- Keep the package identifier, source revisions, inputs and run identity when reporting a reproduction.
- [Cite the particular record](CITATION.md), including its version DOI or exact public carrier. The collection has no separate DOI.

## Collection maintenance

[Structure and status definitions](docs/COLLECTION.md) describe cards, generated metadata, append-only experimental packages and scoped evidence. [Release procedure](docs/RELEASE.md) separates repository maintenance from a new publication and requires a fresh integration check before each release. [License scope](LICENSES/README.md) preserves the terms embedded in historical and third-party materials.

Python 3.12 is the collection verification profile:

```sh
python3 -m venv /tmp/wexp-collection-venv
/tmp/wexp-collection-venv/bin/python -m pip install -r requirements-verification.txt
/tmp/wexp-collection-venv/bin/python -B scripts/catalog.py --check
/tmp/wexp-collection-venv/bin/python -B scripts/verify_collection.py
```

Use a new virtual environment path if that example path already exists. Package-specific commands are in each package's reproduction instructions. CI verifies all collection changes; its success applies to the exact checked commit and the executed checks.

The historical `wexp-emilia-interop-001` tag and release remain the identity of the EMILIA INTEROP-001 publication; EMILIA INTEROP-002 is identified by its Zenodo version DOI and has no GitHub release or tag. New experiments use their own namespaced package tags and publication records.
