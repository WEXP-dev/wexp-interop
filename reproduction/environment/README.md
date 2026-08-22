# Environment records

`PREPARATION-ENVIRONMENT.json` is a factual snapshot of the host used to build
and dry-validate this scaffold. It is not an implementation execution record.

`EXECUTION-ENVIRONMENT.json` does not exist yet. The controlled runner creates
it only after every identity and baseline gate passes, immediately before any
future implementation call. The absence of that file is evidence that this
runner has not crossed its execution barrier.

The future record includes the externally supplied pre-run manifest and
expectation pins, exact control and adapter-executable hashes, clean repository
HEAD/tree, the complete reviewed adapter environment, declared container use,
and all reviewed runtime-version command results. The adapter never inherits
the ambient parent environment.
