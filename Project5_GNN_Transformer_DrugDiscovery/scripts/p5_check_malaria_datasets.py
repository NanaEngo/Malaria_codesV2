#!/usr/bin/env python3
"""Check availability of public malaria datasets (TDC / MoleculeNet) for action 4."""
import importlib.util
import os

print("=== package availability ===")
for pkg in ["tdc", "deepchem"]:
    spec = importlib.util.find_spec(pkg)
    print(pkg, "->", "INSTALLED" if spec else "MISSING")
    if spec:
        try:
            mod = __import__(pkg)
            print("   version:", getattr(mod, "__version__", "?"))
        except Exception as e:
            print("   import error:", repr(e)[:200])

print()
print("=== deepchem molnet malaria scan ===")
try:
    import deepchem, os as _os
    base = _os.path.dirname(deepchem.__file__)
    molnet = _os.path.join(base, "molnet")
    hits = []
    for root, dirs, files in _os.walk(molnet):
        for f in files:
            if f.endswith(".py"):
                p = _os.path.join(root, f)
                try:
                    txt = open(p, encoding="utf-8", errors="ignore").read()
                except Exception:
                    continue
                if "malaria" in txt.lower():
                    hits.append(p)
    print("files referencing 'malaria':", hits[:10] or "NONE")
except Exception as e:
    print("scan failed:", repr(e)[:200])

print()
print("=== deepchemdata S3 candidate URLs ===")
urls = [
    "https://deepchemdata.s3-us-west-1.amazonaws.com/datasets/malaria.csv",
    "https://deepchemdata.s3.us-west-1.amazonaws.com/datasets/malaria.csv",
    "https://deepchemdata.s3-us-west-1.amazonaws.com/datasets/Malaria.csv",
    "https://raw.githubusercontent.com/deepchem/moleculenet/main/malaria.csv",
    "https://raw.githubusercontent.com/deepchem/deepchem/master/datasets/malaria.csv",
]
import urllib.request

for u in urls:
    try:
        req = urllib.request.Request(u, method="HEAD")
        with urllib.request.urlopen(req, timeout=10) as r:
            print("OK ", r.status, r.headers.get("Content-Length", "?"), u)
    except Exception as e:
        print("ERR", type(e).__name__, str(e)[:80], u)
