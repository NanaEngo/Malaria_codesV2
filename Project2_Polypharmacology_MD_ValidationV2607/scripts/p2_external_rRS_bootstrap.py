#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json
from pathlib import Path
import numpy as np

def read(path):
 with Path(path).open() as f:return list(csv.DictReader(f))
def num(rows,key):
 out=[]
 for r in rows:
  try: out.append(float(r[key]))
  except (ValueError,KeyError): pass
 return np.asarray(out,float)
def ci(x,rng,B):
 if len(x)==0:return {'n':0,'estimate':None,'ci95':[None,None]}
 vals=np.asarray([x[rng.integers(0,len(x),len(x))].mean() for _ in range(B)])
 return {'n':int(len(x)),'estimate':float(x.mean()),'ci95':[float(np.quantile(vals,.025)),float(np.quantile(vals,.975))]}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--external',required=True);ap.add_argument('--primary',required=True);ap.add_argument('--output',required=True);ap.add_argument('--seed',type=int,default=42);ap.add_argument('--bootstrap',type=int,default=10000);a=ap.parse_args(); ext=read(a.external); pri=read(a.primary); rng=np.random.default_rng(a.seed)
 out={'status':'COMPUTED_DESCRIPTIVE_BOOTSTRAP','external_panel':{'n_rows':len(ext),'class_fraction':{},'rrs':{}},'primary_panel':{'n_rows':len(pri),'class_fraction':{},'rrs':{}},'comparison_boundary':'Descriptive comparison only: panels, receptor preparation, and provenance differ; no biological replication or equivalence claim.'}
 for label,rows in [('external_panel',ext),('primary_panel',pri)]:
  n=len(rows); counts={}
  key='RRS_class' if label=='external_panel' else 'RRS_class'
  for r in rows: counts[r.get(key,'UNDEFINED')]=counts.get(r.get(key,'UNDEFINED'),0)+1
  for k,v in counts.items():
   x=np.repeat(1.0,v); # bootstrap fraction via Bernoulli resampling
   vals=np.asarray([rng.binomial(n,v/n)/n for _ in range(a.bootstrap)])
   out[label]['class_fraction'][k]={'count':v,'fraction':v/n,'ci95':[float(np.quantile(vals,.025)),float(np.quantile(vals,.975))]}
  for k in ['RRS_mean','RRS_N51I','RRS_C59R','RRS_S108N','RRS_I164L','RRS_K76T','RRS_K76A']:
   vals=num(rows,k)
   out[label]['rrs'][k]=ci(vals,rng,a.bootstrap)
 Path(a.output).parent.mkdir(parents=True,exist_ok=True);Path(a.output).write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
