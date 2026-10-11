#!/usr/bin/env python3
"""Strong native alternative: pinned AAR verifier plus recipient policy."""

import argparse
from pathlib import Path

from consumer_policy import ConsumerRuntimeError, emit, result_for, verify_source


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--policy", type=Path, required=True)
    args = parser.parse_args()
    try:
        source = verify_source(args.source.read_bytes(), args.policy.read_bytes())
    except (OSError, ConsumerRuntimeError) as exc:
        emit({"route": "native-library", "runtime_error": str(exc)})
        return 1
    emit(result_for(source, "native-library"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
