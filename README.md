# WEXP interoperability records

This repository collects versioned experimental packages and their reproduction materials. Each experiment has the same location under `experiments/`; each package has an external card and a separately identified payload. The [generated catalog](catalog.json) is an index of those cards, not a second source of experimental results.

## Experimental records

| Experiment | Package | Recorded result | Scope |
|---|---|---|---|
| [WEXP × EMILIA INTEROP-001](experiments/emilia-interop-001/packages/pkg-001/README.md) | `pkg-001` · [version DOI](https://doi.org/10.5281/zenodo.22056151) | **Branch A — Explicit Bridge Required** | Historical controlled-fixture record; migration replays archived evidence. |
| [WEXP × WIMSE AAR-02 INTEROP-001](experiments/wimse-aar-02-interop-001/packages/pkg-001/README.md) | `pkg-001` · [exact carrier and archive](experiments/wimse-aar-02-interop-001/packages/pkg-001/record.json) | **No local decision difference from the strong native baseline** | 130 expected case outcomes, 16 output refusals and two controlled worlds; known reference, coordinated local execution. |

An experiment's presence in this collection does not establish conformance, semantic equivalence, full interoperability, or IETF adoption. The card states what was executed, how comparison was made, and what kind of independent reproduction is available. Use those dimensions separately.

## Find and verify a package

- Read the package `README.md`, `record.json` and reproduction instructions first.
- Use the exact source archive and its digest for the historical published object. An extracted `payload/` is a useful view of its file bytes; it does not reproduce ZIP container metadata.
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

The historical `wexp-emilia-interop-001` tag and release remain the identity of the existing EMILIA publication. New experiments use their own namespaced package tags and publication records.
