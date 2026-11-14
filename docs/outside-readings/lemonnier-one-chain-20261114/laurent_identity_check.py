import sys, hashlib, json, importlib.util, os
from cryptography.hazmat.primitives.serialization import load_pem_public_key
demo, regdir, out = sys.argv[1], sys.argv[2], sys.argv[3]
spec = importlib.util.spec_from_file_location("run_demo", demo)
rd = importlib.util.module_from_spec(spec); spec.loader.exec_module(rd)
key = load_pem_public_key(open(os.path.join(regdir, "issuer-ed25519.pub.pem"), "rb").read())
stated = {
 "action-binding-attachment-a1.signed-statement.cose": ("67e8c6a5163b866b02413e12f084477b4edb186a73775ccf6c642669c4857323","03cabe49ce79f40b50e4b0744469dede7fc19123c998474f2fc1d7419634fda8"),
 "action-binding-attachment-a2.signed-statement.cose": ("8d55eb43663529ec45cc9d1a8409bf9d30373032e019c52aa379c1373b3d1cb9","f5b4486b9ad95bd74cc68e6cb58df3955d8b024cfd584efb0703b78bf5f36aad"),
 "verdict-record.signed-statement.cose": ("0f4686fdc4bcaa44b05bc4b88f8c0f6f90522c44d2ccb051689fd50fbe3d2e32","52bf19f55d61278e5baff38d487878c31e93da07f222c3f9e2ecada6fcf68880"),
 "dispute-packet.signed-statement.cose": ("73c98d14e0d05d7d3d9672582d3fb6dac5d8ea7525556806820ed646c97e25d3","13bbf54e2c1d93bb25a1efb2ef6f52b3f13b4cb3f648dda42fe413b6fc9f286e"),
 "dispute-packet.2026-11-08.signed-statement.cose": ("d328894f075a7241380ae18e44fb84f046c047b0def4d4836f22e3645886a3ea","5f0fac2384f13bc571f60254ca7e21c74f1ef6c763b04e465cb07c23154da57f"),
}
rows = []
for name, (s_raw, s_entry) in stated.items():
    b = open(os.path.join(regdir, name), "rb").read()
    row = {"file": name, "bytes": len(b)}
    raw = hashlib.sha256(b).hexdigest()
    leaf = hashlib.sha256(b"\x00" + b).hexdigest()
    row["raw_sha256"] = raw; row["raw_equals_readme"] = raw == s_raw
    row["leaf_sha256"] = leaf; row["leaf_equals_readme_entry"] = leaf == s_entry
    try:
        protected, unprotected, payload, signature = rd.fields(b)
        row["unprotected_empty"] = unprotected == {}
        tbs = rd.encode(["Signature1", protected, b"", payload])
        row["tobesigned_sha256"] = hashlib.sha256(tbs).hexdigest()
        try:
            key.verify(signature, tbs); row["signature_verifies"] = True
        except Exception as e:
            row["signature_verifies"] = False
        proj = rd.projection(b)
        row["projection_equals_file_bytes"] = proj == b
        row["pr5_statement_id"] = rd.statement_id(b)
        row["reencode_roundtrip_equal"] = rd.encode(rd.decode(b)) == b
        row["protected_header"] = repr(rd.decode(protected))
    except Exception as e:
        row["error"] = type(e).__name__ + ": " + str(e)
    rows.append(row)
json.dump(rows, open(out, "w"), indent=1)
for r in rows:
    print(json.dumps(r, indent=1))
