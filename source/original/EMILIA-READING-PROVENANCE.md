# Frozen EMILIA reading provenance

Status: **EXACT SOURCE BYTES STAGED AND VERIFIED**

The frozen reveal is identified as:

- filename: `emilia-reading.json`
- bytes: `5,078`
- SHA-256: `b43f8ac6dce465258c75a42117d2750a6bafa163846251416e87cec371a4bad6`
- baseline: `emiliaprotocol/emilia-protocol@9a04bea7fe680345132f6f6251fdb9a63fd8aeb2`

The exact attachment payload was recovered mechanically from the existing
local Codex session log:

```text
/Users/pai/.codex/sessions/2026/08/19/
rollout-2026-08-19T21-07-15-01a01d5a-0cf8-7c93-8d50-ddc9116f8058.jsonl
line 1004
$.payload.result.Ok.structuredContent.content[0].text
```

That log entry is the recorded result of the earlier attachment reveal. The
originating session contains six connector-serialization occurrences of the
same payload; all have one unique 5,078-byte UTF-8 value at the expected hash.
Forked local session logs contain further byte-identical copies and no variant
with that schema, size, and expected hash.

The selected string value was UTF-8 encoded directly to
`source/original/emilia-reading.json`. It was not reparsed and reserialized,
and no newline or encoding normalization was applied. Post-extraction checks
established:

- byte count: `5,078`;
- SHA-256: `b43f8ac6dce465258c75a42117d2750a6bafa163846251416e87cec371a4bad6`;
- valid JSON;
- schema: `wexp-emilia-interop-emilia-reading-1`;
- `frozen`: `true`;
- baseline repository: `https://github.com/emiliaprotocol/emilia-protocol`;
- baseline commit: `9a04bea7fe680345132f6f6251fdb9a63fd8aeb2`.

No Gmail connector was invoked during this recovery. This provenance note is
metadata; the adjacent exact `emilia-reading.json` is the frozen source.
