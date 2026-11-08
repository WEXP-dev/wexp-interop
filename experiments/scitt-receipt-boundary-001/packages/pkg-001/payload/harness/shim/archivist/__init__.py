"""Import shim for the harness only.

The pinned scitt-api-emulator revision imports the RKVST SDK ("rkvst-archivist") at module load
even when the CCF tree algorithm is selected. That distribution is no longer on PyPI. This shim
satisfies the import so the CCF emulator can run; the RKVST backend is never used here, and this
case makes no statement about it. The pinned emulator source is not modified.
"""
