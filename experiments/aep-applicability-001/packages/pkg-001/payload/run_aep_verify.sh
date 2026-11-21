#!/bin/sh
# SPDX-License-Identifier: MIT
# Usage: run_aep_verify.sh /absolute/venv/bin/python /absolute/aep-checkout [verify arguments]
set -eu
test "$#" -ge 3
proposal_python=$1
proposal_source=$2
shift 2
exec "$proposal_python" -I -B - "$proposal_source" "$@" <<'PY'
import pathlib
import runpy
import sys

source = pathlib.Path(sys.argv[1])
if not source.is_absolute():
    raise SystemExit('AEP checkout must be absolute')
source = source.resolve(strict=True)
sys.path.insert(0, str(source))
import aep
actual = pathlib.Path(aep.__file__).resolve(strict=True)
print('AEP_MODULE_FILE=' + str(actual), file=sys.stderr, flush=True)
if not actual.is_relative_to(source):
    raise SystemExit('aep imported from outside pinned checkout')
sys.argv = [str(source / 'verify.py'), *sys.argv[2:]]
runpy.run_path(sys.argv[0], run_name='__main__')
PY
