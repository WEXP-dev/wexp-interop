"""Local transport helpers only; no appraisal or mapping semantics."""
from pathlib import Path
import hashlib
import json
import math
import sys

HERE = Path(__file__).resolve().parent
PROFILE_RAW = (HERE / 'profile.json').read_bytes()
PROFILE = json.loads(PROFILE_RAW)
PROFILE_SHA = hashlib.sha256(PROFILE_RAW).hexdigest()
PROFILE_ID = PROFILE['id'] + ':sha256:' + PROFILE_SHA


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def unique(pairs):
    result = {}
    for name, value in pairs:
        if name in result:
            raise ValueError('duplicate JSON member')
        result[name] = value
    return result


def finite(text):
    value = float(text)
    if not math.isfinite(value):
        raise ValueError('nonfinite JSON number')
    return value


def forbidden(text):
    raise ValueError('nonfinite JSON constant')


def load(raw):
    return json.loads(raw, object_pairs_hook=unique, parse_float=finite,
                      parse_constant=forbidden)


def emit(value):
    print(json.dumps(value, ensure_ascii=True, sort_keys=True, allow_nan=False))


def native_module(legacy):
    consumer = Path(legacy).resolve() / 'experiments/wimse-aar-02-interop-001/packages/pkg-001/payload/consumer'
    sys.path.insert(0, str(consumer))
    import consumer_policy
    if Path(consumer_policy.__file__).resolve() != consumer / 'consumer_policy.py':
        raise RuntimeError('unexpected native policy import')
    return consumer_policy
