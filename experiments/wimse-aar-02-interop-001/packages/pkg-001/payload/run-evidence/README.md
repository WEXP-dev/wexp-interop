# New public-run observations

All 16 files generated in the new result directory and all 14 journal files
are copied without transformations. EXPORT.json identifies each copy. The
exact observation driver is run_public_replay.py; its SHA-256 is also recorded
in EXECUTION-START.json and EXECUTION-FINISH.json.

The journal preserves exact top-level command arguments, raw stdout/stderr,
exit codes and start/finish observations for the input verifier, retained
pilot and strict comparator. The retained pilot stores structured participant
results and per-process stdout hashes, stderr, timings and return codes. It
does not preserve every participant's complete raw stdout transcript.

Absolute clone, output and journal paths are ordinary observations of the
publisher-controlled runtime. They are retained as observed and are not
required reproduction paths. Current reproduction commands choose new local
paths and are described by the outer REPRODUCE.md.

execution_source_files is a packaged Python-file inventory, not a dynamic
import trace. The wrapper driver was outside that payload at execution time;
it is separately preserved and hash-bound here. Neither local clocks, file
hashes nor this log independently authenticate execution, authorship or the
truth of a source claim.
