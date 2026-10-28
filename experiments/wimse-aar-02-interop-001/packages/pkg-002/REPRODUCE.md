# Read saved evidence or execute a separate replay

## Read-only catalog checks

From the collection root, use the pinned root verification dependencies and Python 3.12 or 3.13:

```sh
python -B scripts/catalog.py --check
python -B scripts/verify_collection.py
python -B scripts/verify_wimse_core02.py
python -O -B scripts/verify_wimse_core02.py
python -B -m unittest discover -s scripts -p 'test_wimse_core02_catalog.py'
python -O -B -m unittest discover -s scripts -p 'test_wimse_core02_catalog.py'
```

These commands verify the exact archived outputs, source snapshot, profile/card bindings and stored comparisons. They do not run a producer, the Core appraiser, a recipient, or a two-world operation. They do not independently authenticate the recorded execution.

The primary ZIP contains only saved run observations. Keep the whole package for all four archives and the pinned source snapshot. Do not treat extracting one ZIP as installing the experiment.

## Optional fresh execution — NOT part of this catalog admission

A fresh replay is a distinct experiment with a new output directory. It additionally requires public checkouts of `WEXP-dev/wexp-interop@b3bce9abd047e41af06ff8aff1d9ead8c6b0ed93` (historical inputs) and `WEXP-dev/wexp-ref@56289024c9ee748111f1f1d4f42728ffe04d8d69` (Core-02 code). Follow the frozen [protocol](payload/PROTOCOL.md), verify both exact commits and use new external output paths:

```sh
python -B payload/run.py --legacy /path/to/pinned-legacy --ref /path/to/pinned-ref --out /path/to/new-external-output
```

Run from this package directory. Do not overwrite saved results, the package or a previous output directory. Preserve failures, exact invocation/environment and all outputs. No fresh replay was performed to add this catalog card; a later replay is not independent merely because its process or host differs.
