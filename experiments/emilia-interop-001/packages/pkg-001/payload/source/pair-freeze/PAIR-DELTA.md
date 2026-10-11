# P → P-1 controlled delta

The only intended semantic intervention is removal of the meter observation's
action-to-CAID relation.

## Semantic patch

```json
[
  {
    "op": "remove",
    "path": "/emilia_input/observations/1/action_caid"
  }
]
```

After that removal, only the affected meter observation is re-signed. The
resulting derivative byte change is:

```text
/emilia_input/observations/1/proof/signature_b64u
```

No other JSON value changes. In particular, P-1 preserves the controller
observation and signature; meter payload and `observed_effects_digest`; receipt,
action hash, nonce, operation and facility identifiers; expected CAID; source
pins; public keys and key IDs; control domains; source requirements; observation
windows; effects; and evaluation time.

## Exact fixture identities

| Fixture | Bytes | SHA-256 |
| --- | ---: | --- |
| `fixtures/WE-EP-P.json` | 7,255 | `b552da51858d0256a562e800a81a870435d6e136c9bc28833b962b6d3723fb3e` |
| `fixtures/WE-EP-P-1.json` | 7,152 | `67556d28d272b4b01a73e1c1465248644dd7a05460fc149aa77df92cf36403a0` |

## Cryptographic construction and verification

The meter key is the pinned vector's deterministic **test-only** Ed25519 key:
32-byte seed filled with `0x65`, imported with PKCS#8 prefix
`302e020100300506032b657004220420`. It is public test material and must never be
used as a secret or production key.

For each meter observation, `proof` is removed, the remaining body is encoded
with the frozen EMILIA strict canonical JSON rule, and the Ed25519 signing input
is:

```text
UTF-8("EP-OUTCOME-OBSERVATION-v1\0" || canonical_body)
```

| Property | P | P-1 |
| --- | --- | --- |
| Meter signing-preimage SHA-256 | `f4b7a068b04c6030ec796dea0bc68d02558b01c8915363e71ed45a0dedd8bcfb` | `4249cb402df9a238c4ca2f8b97cbcb30aed80883313870a88b9e40e2612c438a` |
| Meter signature | `0Lfmjdqi0IhEhNxQjknPldAOgjjLYX10Hh0MBGlsqSnLD51YEfm2Krhki9EHX9_f8lLreWqw7_S2QxnvXLgDDw` | `BmqssjoR2v7_BUenBfZeGBBw0FEB3OOa0HuXb2f6XurASBRuxqQLS4ibUNufj-6XT1sT3AMpCq5rB4C6cuAxAQ` |
| New signature verifies | YES | YES |

Independent construction-only verification using the platform Ed25519
primitive established:

- all four carried signatures verify: P controller, P meter, P-1 controller,
  and P-1 meter;
- the original P meter signature does **not** verify over the P-1 body;
- both observed-effects digests verify and remain identical across the pair;
- controller objects are identical;
- after restoring the removed `action_caid` and original meter signature, the
  parsed P-1 object is exactly equal to P;
- controller and meter public keys are distinct;
- controller and meter control-domain pins are distinct.

This verification did not call the EMILIA implementation and did not evaluate
an EMILIA lifecycle outcome. It checked only canonical bytes, hashes, equality,
and Ed25519 validity needed to freeze the controlled pair.

## Delta conclusion

Semantic delta: exactly one removed relation,
`/emilia_input/observations/1/action_caid`.

Necessary derivative delta: exactly one re-created signature,
`/emilia_input/observations/1/proof/signature_b64u`.

Cryptographic validity preserved: **YES**.
