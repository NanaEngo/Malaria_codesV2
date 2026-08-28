#!/usr/bin/env python3
"""Bounded QKS gate for P6.

No QKS result is inferred from other models. This entry point records an
explicit NOT_COMPUTED status until a frozen cohort, kernel parameters, and
prediction-level output contract are supplied.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

def main()->int:
 ap=argparse.ArgumentParser(); ap.add_argument('--output',type=Path,required=True); ap.add_argument('--max-compounds',type=int,default=5000)
 a=ap.parse_args(); r={"status":"NOT_COMPUTED_BOUNDED_QKS_NOT_AUTHORIZED","max_compounds":a.max_compounds,"reason":"QKS requires a separately frozen kernel protocol and bounded cohort; no result is inferred from GIN, fingerprint, or ChemBERTa outputs."}; a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(r,indent=2)+'\n'); print(json.dumps(r,indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
