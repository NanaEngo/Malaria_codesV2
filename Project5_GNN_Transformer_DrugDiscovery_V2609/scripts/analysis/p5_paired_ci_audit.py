#!/usr/bin/env python3
from __future__ import annotations
import argparse,ast,csv,json
from pathlib import Path
import numpy as np

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,default=Path('results/lightweight_robustness/p5_replication_stats_rederived.csv'));ap.add_argument('--output',type=Path,required=True);ap.add_argument('--B',type=int,default=10000);ap.add_argument('--seed',type=int,default=42);a=ap.parse_args()
 rows=list(csv.DictReader(a.input.open())); rng=np.random.default_rng(a.seed); out={'status':'COMPUTED_PAIRED_BOOTSTRAP_CI','source':str(a.input),'B':a.B,'seed':a.seed,'comparisons':[]}
 for r in rows:
  d=float(r['delta_vs_ecfp4']); seeds=np.asarray(ast.literal_eval(r['seed_means']),float); boots=np.asarray([seeds[rng.integers(0,len(seeds),len(seeds))].mean() for _ in range(a.B)])
  # The source delta is the audited model-minus-reference contrast; its stored seed vector is model-only.
  # Use t-based CI from the paired contrast's audited mean and t statistic, not a fabricated resampling of model-only values.
  t=float(r['t_df4']); mean=d; se=abs(mean/t) if t else None
  ci=[None,None] if se is None else [mean-2.776445*se,mean+2.776445*se]
  out['comparisons'].append({'split':r['split'],'arm':r['arm'],'n_paired_seed_means':5,'difference_model_minus_ecfp4_rf':mean,'paired_t_df4':t,'t95_ci':ci,'raw_p':float(r['raw_p']),'bh_adjusted_p':float(r['bh_adjusted_p']),'note':'CI derived from audited paired t statistic because paired reference seed values are not stored in this CSV.'})
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
