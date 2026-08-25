#!/usr/bin/env python3
"""Paired-permutation dAUC vs ECFP4-RF from p5_replication_stats.csv + ChEMBL spec extraction.
Seed 42, B=10000. Honest: missing data => 'deferred'. Output: results/rp5_summary.json."""
import json, csv, os, ast
import numpy as np

np.random.seed(42)
B = 10000
R = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'results')

base = {}
for sp in ('random', 'scaffold'):
    j = json.load(open(f'{R}/p5_ecfp4rf_{sp}_baseline.json'))
    base[sp] = [float(x) for x in j['seed_means']]

rows = list(csv.DictReader(open(f'{R}/p5_replication_stats.csv')))

def perm(a, b):
    d = np.array(a, float) - np.array(b, float)
    obs = float(d.mean())
    rng = np.random.default_rng(42)
    pool = np.concatenate([d, -d])
    null = np.fromiter((rng.choice(pool, d.size, replace=False).mean() for _ in range(B)), float, B)
    boot = np.fromiter((rng.choice(d, d.size, replace=True).mean() for _ in range(B)), float, B)
    lo, hi = np.percentile(boot, [2.5, 97.5])
    return {'n': int(d.size), 'mean_delta': round(obs, 4),
            'ci95': [round(float(lo), 4), round(float(hi), 4)],
            'p_two_sided': round(float((np.abs(null) >= abs(obs)).mean()), 4)}

tests = {}
for r in rows:
    arm, sp = r['arm'], r['split']
    a = ast.literal_eval(r['seed_means'])
    key = f'{arm}_{sp}'
    tests[key] = perm(a, base[sp])

chem = {}
pj = f'{R}/p5_public_chembl_malaria_provenance.json'
if os.path.exists(pj):
    chem['provenance'] = json.load(open(pj))
for name in ('p5_public_chembl_malaria.csv', 'p5_public_chembl_malaria_disjoint.csv'):
    p = f'{R}/{name}'
    if os.path.exists(p):
        rr = list(csv.DictReader(open(p)))
        chem[name] = {'rows': len(rr), 'columns': list(rr[0])[:12]}

summary = {'seed': 42, 'permutations': B,
           'note': 'paired permutation of per-seed mean AUC deltas vs ECFP4-RF; fold-level pairing unavailable (fold-wise AUCs archived separately)',
           'paired_tests': tests, 'chembl': chem,
           'rf_minigrid': 'DEFERRED_NO_FEATURE_MATRIX'}
out = f'{R}/rp5_summary.json'
json.dump(summary, open(out, 'w'), indent=2)
print(json.dumps({'paired_tests': tests, 'chembl_keys': list(chem)}, indent=2))
