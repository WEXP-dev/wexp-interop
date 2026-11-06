#!/bin/sh
# Reproduce the Signed Statement registration and Receipt retrieval against the pinned emulator.
# Usage: harness/run_emulator.sh <work-dir>   (the work dir must not exist; everything is created inside it)
# Requires: python3.12, network access to clone the pinned revision, and PyPI for the dependencies.
set -eu
WORK="$1"; [ -e "$WORK" ] && { echo "work dir exists: $WORK" >&2; exit 1; }
HERE="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$WORK" && cd "$WORK"
git clone -q https://github.com/scitt-community/scitt-api-emulator.git emulator
git -C emulator checkout -q cfebeee5bb3da7d5a9a13d319aaaab17c1348641   # tag pre-archive, 2024-03-26
python3.12 -m venv venv
./venv/bin/python -m pip -q install cryptography cbor2 cwt jwcrypto pycose httpx flask   # the emulator itself is not pip-installed
export PYTHONPATH="$WORK/emulator:$HERE/shim"   # shim satisfies the RKVST SDK import; the CCF backend is used
mkdir -p workspace artifacts
./venv/bin/python -s -B -m scitt_emulator.cli server --workspace workspace --tree-alg CCF --port 8765 --error-rate 0 > server.log 2>&1 &
SERVER=$!; trap 'kill $SERVER' EXIT; sleep 4
P=./venv/bin/python
$P -s -B -m scitt_emulator.cli client create-claim --content-type application/json \
  --subject 'wexp-interop:scitt-receipt-boundary-001' \
  --payload '{"statement":"WEXP interop case 001: a Signed Statement registered for a Receipt to be mapped to a Core-02 boundary finding","target":"T"}' \
  --out artifacts/signed-statement.cose
$P -s -B -m scitt_emulator.cli client submit-claim --claim artifacts/signed-statement.cose --out artifacts/receipt.cbor --out-entry-id artifacts/entry-id.txt --url http://127.0.0.1:8765
$P -s -B -m scitt_emulator.cli client retrieve-receipt --entry-id "$(cat artifacts/entry-id.txt)" --out artifacts/receipt-retrieved.cbor --url http://127.0.0.1:8765
cmp artifacts/receipt.cbor artifacts/receipt-retrieved.cbor && echo "receipt bytes identical on retrieve"
$P -s -B -m scitt_emulator.cli client verify-receipt --claim artifacts/signed-statement.cose --receipt artifacts/receipt.cbor --service-parameters workspace/service_parameters.json
cp workspace/service_parameters.json artifacts/
(cd artifacts && shasum -a 256 *)
echo "Note: keys are generated ad hoc on every run, so the bytes and digests differ from the committed artifacts; the structure and the verification outcome are what reproduce."
