#!/usr/bin/env python3
"""R-P5 light runs: paired permutation tests + ChEMBL spec extraction.
Seed 42, B=10000. Outputs results/rp5_summary.json (+csv). No fabrication: missing data => 'deferred'."""
import json, glob, os, csv
import numpy as np
np.random.seed(42)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))          # V2 dir
OLD  = os.path.join(os.path.dirname(ROOT), 'Project5_GNN_Transformer_DrugDiscovery', 'results')
V2R  = os.path.join(ROOT, 'results')
B = 10000

def load_json(p):
    with open(p) as f: return json.load(f)

def seed_array_from(obj, hint=('seed_means','per_seed','seeds')):
    """Extract a list of per-seed AUC floats from heterogeneous JSON."""
    if isinstance(obj, dict):
        for k in obj:
            if any(h.lower() in k.lower() for h in hint):
                v = obj[k]
                if isinstance(v, list) and all(isinstance(x,(int,float)) for x in v) and len(v)>=3:
                    return [float(x) for x in v]
        # nested search
        for k,v in sorted(obj.items()):
            r = seed_array_from(v, hint)
            if r: return r
    return None

def find_one(patterns, roots=(V2R, OLD)):
    for root in roots:
        for pat in patterns:
            hits = glob.glob(os.path.join(root, '**', pat), recursive=True)
            if hits: return hits[0]
    return None

summary = {'seed':42,'permutations':B}

# ---- collect per-seed arrays per arm/split ----
arms = {}
arms['ECFP4-RF'] = {sp: seed_array_from(load_json(find_one([f'p5_ecfp4rf_{sp}_baseline.json'])))
                    for sp in ('random','scaffold')}
for arm,pats in {
  'GIN':      ['p5_GIN_{s}_ckpt_replic.json','p5_GIN_{s}_results_replic.csv','p5_GIN_{s}_ckpt.json'],
  'ChemBERTa':['p5_chemberta_{s}_ckpt_metrics.json'],
  'GIN-TFP':  ['p5_GIN-TFP_{s}*.json'],
}.items():
    arms[arm] = {}
    for sp in ('random','scaffold'):
        p = find_one([p_.format(s=sp) for p_ in pats])
        if not p: continue
        arr = None
        if p.endswith('.json'):
            try: arr = seed_array_from(load_json(p))
            except Exception: pass
        if not arr and p.endswith('.csv'):
            rows=list(csv.DictReader(open(p))); col=None
            for c in rows[0]:
                lc=c.lower()
                if 'auc' in lc and ('mean' in lc or 'seed' in lc): col=c; break
            if col is None:
                for c in rows[0]:
                    if 'auc' in c.lower(): col=c; break
            if col: arr=[float(r[col]) for r in rows][:10] or None
            else:   arr=[float(r[list(rows[0])[-1]]) for r in rows][:10] or None
        arms[arm][sp]=arr

def paired_perm(a,b,B=B):
    d=np.asarray(a,float)-np.asarray(b,float); obs=d.mean()
    pool=np.concatenate([d,-d]); rng=np.random.default_rng(42)
    null=np.array([rng.choice(pool,size=d.size,replace=False).mean() for _ in range(B)])
    p=float((np.abs(null)>=abs(obs)).mean())
    boots=np.array([np.mean(rng.choice(d,size=d.size,replace=True)) for _ in range(B)])
    return {'n':d.size,'mean_delta':round(obs,4),'ci95':[round(float(q),4) for q in np.percentile(boots,[2.5,97.5])],'p_two_sided':round(p,4)}

tests={}
base=arms['ECFP4-RF']
for arm in arms:
    if arm=='ECFP4-RF': continue
    for sp in ('random','scaffold'):
        a,b_=arms[arm].get(sp), base.get(sp)
        key=f'{arm}_{sp}'
        if a is None:
            tests[key]='NO_PER_SEED_DATA'
        elif b_ is None:
            tests[key]='BASELINE_MISSING'
        elif len(a)!=len(b_):
            tests[key]=f'SIZE_MISMATCH {len(a)} vs {len(b_)}'
        else:
            tests[key]=paired_perm(a,b_)
summary['paired_tests']=tests

# ---- ChEMBL transfer spec (R5/R-P5-04) ----
chem=[]
for root in (OLD,V2R):
    chem+=glob.glob(os.path.join(root,'public_chembl*'))
spec={}
for p in sorted(set(chem)):
    try:
        if p.endswith(('.json',)):
            j=load_json(p)
            spec[os.path.basename(p)]={k:v for k,v in j.items() if isinstance(v,(str,int,float))}
        elif p.endswith('.csv'):
            rows=list(csv.DictReader(open(p)))
            spec[os.path.basename(p)]={'rows':len(rows),'columns':list(rows[0])[:12]}
    except Exception as e:
        spec[os.path.basename(p)]=f'READ_ERROR {e}'
summary['chembl_files']=spec

# ---- RF mini-grid feasibility probe (R-P5-02) ----
feat=glob.glob(os.path.join(V2R,'**','*features*'),recursive=True)+glob.glob(os.path.join(OLD,'**','*features*'),recursive=True)+glob.glob(os.path.join(V2R,'**','*.npz'),recursive=True)
summary['rf_minigrid']='DEFERRED_NO_FEATURE_MATRIX' if not feat else f'CANDIDATE_{feat[:2]}'

os.makedirs(os.path.join(V2R,'lightweight_robustness'),exist_ok=True)
out=os.path.join(V2R,'lightweight_robustness')
json.dump(summary,open(os.path.join(out,'rp5_summary.json'),'w'),indent=2)
with open(os.path.join(out,'rp5_paired_tests.csv'),'w',newline='') as f:
    w=csv.writer(f); w.writerow(['test','result']); [w.writerow([k,json.dumps(v) if isinstance(v,dict) else v]) for k,v in tests.items()]
print(json.dumps(summary,indent=2))
