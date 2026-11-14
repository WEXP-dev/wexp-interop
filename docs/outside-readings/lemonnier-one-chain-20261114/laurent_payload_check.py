import sys, os, importlib.util
demo, regdir, posdir = sys.argv[1:4]
spec = importlib.util.spec_from_file_location("run_demo", demo)
rd = importlib.util.module_from_spec(spec); spec.loader.exec_module(rd)
for n in sorted(os.listdir(regdir)):
    if not n.endswith(".signed-statement.cose"): continue
    payload = rd.fields(open(os.path.join(regdir, n), "rb").read())[2]
    base = n.replace(".signed-statement.cose", "")
    cands = [f for f in os.listdir(posdir) if f.startswith(base.replace(".2026-11-08",""))]
    print(n, len(payload), [(f, open(os.path.join(posdir,f),"rb").read()==payload) for f in cands])
