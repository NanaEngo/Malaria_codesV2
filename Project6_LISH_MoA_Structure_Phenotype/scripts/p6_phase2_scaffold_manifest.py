#!/usr/bin/env python3
from __future__ import annotations
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'results'/'p6_phase2'
MODELS=('gin','gin-tfp','gin-tne','chemberta')
def main():
 rows=[]
 for m in MODELS:
  csvp=OUT/f'p6_lish_moa_{m}_scaffold_folds.csv'; jsonp=OUT/f'p6_lish_moa_{m}_scaffold_report.json'
  n=0
  if csvp.exists(): n=len(list(csv.DictReader(csvp.open())))
  rows.append({'model':m,'fold_csv':str(csvp.relative_to(ROOT)),'report_json':str(jsonp.relative_to(ROOT)),'exists':csvp.exists() and jsonp.exists(),'fold_records':n})
 status='COMPUTED_COMPLETE' if all(x['exists'] and x['fold_records']==25 for x in rows) else 'NOT_COMPUTED_MISSING_SCAFFOLD_MOLECULAR_ARMS'
 r={'status':status,'models':rows,'contract':'5 seeds x 5 scaffold-disjoint folds; no result inferred from collision-group metrics'}
 p=OUT/'p6_scaffold_molecular_arm_manifest.json'; p.write_text(json.dumps(r,indent=2)+'\n'); print(json.dumps(r,indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
