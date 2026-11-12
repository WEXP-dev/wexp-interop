"""B-01 reveal intake. Verification before anything else touches the bytes.

The ordering below is the whole point of this file, so it is worth stating
before the code says it: nothing here parses, decodes, normalizes, loads or
evaluates the payload. It measures bytes and compares digests. A verifier that
parsed first would have already trusted the thing it was supposed to check, and
a JSON round-trip alone is enough to turn a mismatching payload into a matching
one without anybody deciding to cheat.

Run:
    python3 verify_b01_commitment.py --carrier RECEIVED --payload CANDIDATE \
        --extraction identity --report OUT.json [--admit-to PATH]

The payload is admitted only on COMMITMENT_MATCH, and admission copies the
exact received bytes with no transformation of any kind.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import shutil
import sys

# The frozen commitment. Fixed before the bridge existed; not editable by
# anything that happens downstream of it.
CASE_ID = "WEXP-EMILIA-INTEROP-002-B01-OPERATION-REBIND-001"
EXPECTED_BYTE_COUNT = 7276
EXPECTED_SHA256 = "8a5164e1a5c3924be201b703a47be4882b09d1abe355128eb1ff7e02c9868e66"
COMMITMENT_RECORD = "experiments/WEXP-EMILIA-INTEROP-002/pre-freeze/B-01-COMMITMENT.json"

STATES = (
    "NOT_RECEIVED",
    "RECEIVED_UNVERIFIED",
    "COMMITMENT_MATCH",
    "COMMITMENT_MISMATCH",
    "CARRIER_AMBIGUOUS",
)

# Extraction is declared, not guessed. Anything outside this set is ambiguous by
# definition, because a verifier that invents an extraction has changed the
# bytes it is about to vouch for.
ADMISSIBLE_EXTRACTIONS = ("identity", "single-attachment-verbatim")


def sha256_of(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def verify(carrier: pathlib.Path, payload: pathlib.Path, extraction: str) -> dict:
    result = {
        "record_kind": "wexp-emilia-interop-002-b01-commitment-verification",
        "case_id": CASE_ID,
        "commitment_record": COMMITMENT_RECORD,
        "expected_byte_count": EXPECTED_BYTE_COUNT,
        "expected_sha256": EXPECTED_SHA256,
        "extraction_declared": extraction,
        "state": "NOT_RECEIVED",
        "admitted": False,
        "checks": {},
        "reasons": [],
        "non_claims": [
            "COMMITMENT_MATCH means the received bytes are the bytes committed to. "
            "It says nothing about what the case contains or what the bridge will do with it.",
            "This gate produces no semantic result and must not be read as one.",
        ],
    }

    if not carrier.exists():
        result["reasons"].append("carrier_absent")
        return result
    carrier_bytes = carrier.read_bytes()
    result["carrier"] = {
        "byte_count": len(carrier_bytes),
        "sha256": sha256_of(carrier_bytes),
        "preserved_verbatim": True,
    }

    if not payload.exists():
        result["state"] = "CARRIER_AMBIGUOUS"
        result["reasons"].append("no_candidate_payload_identified")
        return result

    if extraction not in ADMISSIBLE_EXTRACTIONS:
        result["state"] = "CARRIER_AMBIGUOUS"
        result["reasons"].append(f"extraction_not_admissible:{extraction}")
        return result

    payload_bytes = payload.read_bytes()
    if extraction == "identity" and payload_bytes != carrier_bytes:
        # The declaration and the bytes disagree. Do not pick a winner.
        result["state"] = "CARRIER_AMBIGUOUS"
        result["reasons"].append("declared_identity_extraction_but_payload_differs_from_carrier")
        return result

    result["state"] = "RECEIVED_UNVERIFIED"
    measured_count = len(payload_bytes)
    measured_digest = sha256_of(payload_bytes)
    result["received"] = {"byte_count": measured_count, "sha256": measured_digest}

    result["checks"]["byte_count_exact"] = measured_count == EXPECTED_BYTE_COUNT
    result["checks"]["sha256_exact"] = measured_digest == EXPECTED_SHA256
    result["checks"]["no_transformation_applied"] = True

    if all(result["checks"].values()):
        result["state"] = "COMMITMENT_MATCH"
        result["blind_case_status"] = "REVEALED_COMMITMENT_VERIFIED"
    else:
        result["state"] = "COMMITMENT_MISMATCH"
        result["blind_case_status"] = "NOT_ADMITTED"
        if not result["checks"]["byte_count_exact"]:
            result["reasons"].append(
                f"byte_count_mismatch:expected {EXPECTED_BYTE_COUNT}, received {measured_count}"
            )
        if not result["checks"]["sha256_exact"]:
            result["reasons"].append("sha256_mismatch")
        result["reasons"].append(
            "STOP. Do not repair, reformat, or ask for a silently regenerated case. "
            "Preserve both the commitment identity and the received carrier identity and escalate."
        )
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Verify received B-01 bytes against the frozen commitment.")
    parser.add_argument("--carrier", required=True, type=pathlib.Path)
    parser.add_argument("--payload", required=True, type=pathlib.Path)
    parser.add_argument("--extraction", default="identity")
    parser.add_argument("--report", required=True, type=pathlib.Path)
    parser.add_argument(
        "--admit-to",
        type=pathlib.Path,
        help="Write the exact received bytes here, and only on COMMITMENT_MATCH.",
    )
    args = parser.parse_args(argv)

    result = verify(args.carrier, args.payload, args.extraction)

    if args.admit_to is not None:
        if result["state"] == "COMMITMENT_MATCH":
            args.admit_to.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(args.payload, args.admit_to)  # byte-for-byte, no rewrite
            result["admitted"] = True
            result["admitted_path"] = str(args.admit_to)
        else:
            result["admitted"] = False
            result["reasons"].append("admission_refused_state_is_not_commitment_match")

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({k: result[k] for k in ("state", "admitted", "reasons")}, ensure_ascii=False))
    return 0 if result["state"] == "COMMITMENT_MATCH" else 1


if __name__ == "__main__":
    sys.exit(main())
