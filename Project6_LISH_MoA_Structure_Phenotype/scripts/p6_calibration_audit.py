#!/usr/bin/env python3
"""Build bounded P6 calibration diagnostics from fold-level prediction files.

The current report files contain aggregate metrics, not per-drug predictions.
Therefore this script is fail-closed unless prediction CSVs are supplied. It
never reconstructs calibration from aggregate metrics.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--prediction-dir', type=Path, default=None)
    ap.add_argument('--output', type=Path, required=True)
    args=ap.parse_args()
    result={"status":"NOT_COMPUTED_MISSING_PREDICTION_RECORDS","reason":"Aggregate fold metrics cannot reconstruct per-label calibration; no prediction-level files were supplied.","per_label":[],"pooled":None}
    if args.prediction_dir is not None and args.prediction_dir.exists():
        files=sorted(args.prediction_dir.glob('*.csv'))
        if files:
            result={"status":"PENDING_IMPLEMENTATION_REQUIRES_SCHEMA_AUDIT","reason":"Prediction files exist but require explicit schema and fold-identity audit before calibration is computed.","files":[str(x) for x in files]}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    return 0
if __name__=='__main__': raise SystemExit(main())
