#!/usr/bin/env python3
"""One unchanged input, one isolated appraiser process; no expected values loaded."""
# SPDX-License-Identifier: MIT
import argparse
import hashlib
import json
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine', choices=('ref', 'check'), required=True)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--profiles', type=Path, required=True)
    parser.add_argument('--metadata', type=Path, required=True)
    args = parser.parse_args()
    source = args.source.resolve(strict=True)
    if not args.source.is_absolute() or Path.cwd().resolve() != source:
        raise SystemExit('source and isolated cwd must be the absolute source root')
    sys.path.insert(0, str(source))
    if args.engine == 'ref':
        import wexp_ref.core02.appraiser as engine
    else:
        import wexp_check as engine
    actual = Path(engine.__file__).resolve(strict=True)
    print('CORE_MODULE_FILE=' + str(actual), file=sys.stderr, flush=True)
    if not actual.is_relative_to(source):
        raise SystemExit('engine imported from outside pinned checkout')
    input_bytes = args.input.read_bytes()
    profile_bytes = args.profiles.read_bytes()
    normalized = json.loads(input_bytes)
    profiles = json.loads(profile_bytes)
    before_input = json.dumps(normalized, sort_keys=True, allow_nan=False)
    before_profiles = json.dumps(profiles, sort_keys=True, allow_nan=False)
    result = engine.appraise(normalized, profiles)
    metadata = {
        'module_file': str(actual),
        'module_sha256': hashlib.sha256(actual.read_bytes()).hexdigest(),
        'input_sha256': hashlib.sha256(input_bytes).hexdigest(),
        'profiles_sha256': hashlib.sha256(profile_bytes).hexdigest(),
        'input_mutated': before_input != json.dumps(normalized, sort_keys=True, allow_nan=False),
        'profiles_mutated': before_profiles != json.dumps(profiles, sort_keys=True, allow_nan=False),
        'input_file_changed': input_bytes != args.input.read_bytes(),
        'profile_file_changed': profile_bytes != args.profiles.read_bytes(),
    }
    args.metadata.write_text(json.dumps(metadata, indent=2) + '\n')
    print(json.dumps(result, sort_keys=True, ensure_ascii=True, allow_nan=False))
    return 1 if any(metadata[k] for k in ('input_mutated', 'profiles_mutated', 'input_file_changed', 'profile_file_changed')) else 0


if __name__ == '__main__':
    raise SystemExit(main())
