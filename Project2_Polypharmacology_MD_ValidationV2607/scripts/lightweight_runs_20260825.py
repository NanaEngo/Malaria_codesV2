#!/usr/bin/env python3
"""Lightweight post-processing runs (R3/R8/R9 support) — deterministic, seed 42.

RUN1: per-mutant MM-GBSA DeltaDeltaG with propagated SD (mutant - WT, same compound+target).
RUN2: partial Spearman PNS~RRS controlling MW + Murcko-scaffold prevalence (NOT the companion TDA quantity).
RUN3: cohort-level bootstrap uncertainty (class proportions over n=17; >100%-ratio proportion over 12 mutants).
Outputs -> results/lightweight_robustness/*.csv + lightweight_runs_summary.json
"""
import json, os
import numpy as np, pandas as pd

np.random.seed(42)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results"); OUT = os.path.join(RES, "lightweight_robustness")
os.makedirs(OUT, exist_ok=True)
summary = {}

# ---------- RUN1: ΔΔG ± SD ----------
m = pd.read_csv(os.path.join(RES, "set_c_md", "mmgbsa_summary_pilot.csv"))
assert {"set_c_id","target","mutation","mmgbsa_dg_kcal_mol","mmgbsa_sd_kcal_mol"} <= set(m.columns)
rows = []
for (cid,tgt),g in m.groupby(["set_c_id","target"]):
    wt = g[g["mutation"].str.upper()=="WT"]
    assert len(wt)==1, f"missing WT for {cid}/{tgt}"
    wtd, wts = float(wt.mmgbsa_dg_kcal_mol.iloc[0]), float(wt.mmgbsa_sd_kcal_mol.iloc[0])
    for _,r in g[g["mutation"].str.upper()!="WT"].iterrows():
        dd  = float(r.mmgbsa_dg_kcal_mol) - wtd                      # >0 = mutant binds weaker
        sd  = float(np.hypot(float(r.mmgbsa_sd_kcal_mol), wts))      # independent propagation
        rows.append(dict(set_c_id=cid,target=tgt,mutation=r.mutation,
                         dG_wt=wtd,dG_mut=float(r.mmgbsa_dg_kcal_mol),
                         dDeltaG=round(dd,3),SD_prop=round(sd,3),
                         CI95_low=round(dd-1.96*sd,3),CI95_high=round(dd+1.96*sd,3)))
dd_df = pd.DataFrame(rows).sort_values(["set_c_id","target","mutation"])
assert len(dd_df)==12, f"expected 12 mutants, got {len(dd_df)}"
dd_df.to_csv(os.path.join(OUT,"mmgbsa_ddeltaG_pilot.csv"), index=False)
sig = int((dd_df.CI95_high < 0).sum())   # significantly tighter binding
summary["run1"] = {"n_mutants": len(dd_df), "weaker_binding_CI95": int((dd_df.CI95_low>0).sum()),
                   "tighter_binding_CI95": sig,
                   "max_abs_dDeltaG": float(dd_df.dDeltaG.abs().max()),
                   "n_significant_at_95": int(((dd_df.CI95_low>0)|(dd_df.CI95_high<0)).sum())}

# ---------- RUN2: partial Spearman PNS~RRS | MW + scaffold prevalence ----------
from rdkit import Chem, RDLogger
from rdkit.Chem import Descriptors
from rdkit.Chem.Scaffolds import MurckoScaffold
RDLogger.DisableLog("rdApp.*")
adm = pd.read_csv(os.path.join(RES,"admet_profile_setC_17.csv"))
pns = pd.read_csv(os.path.join(RES,"c_pns_ranking.csv"))
cls = pd.read_csv(os.path.join(RES,"c_rrs_classification.csv"))
smi2pp = dict(zip(adm.smiles.str.strip(), adm.candidate))
pns["PP"] = pns.smiles.str.strip().map(smi2pp)
assert pns.PP.notna().all(), "PNS↔PP join failed"
# RRS: prefer a single primary two-target ratio if present, else first numeric rrs-like column
cand_cols = [c for c in cls.columns if "rrs" in c.lower()]
assert cand_cols, cls.columns.tolist()
key = "candidate_id" if "candidate_id" in cls.columns else ("candidate" if "candidate" in cls.columns else cls.columns[0])
for _pref in ("RRS_mean_complete_two_target","RRS_mean_available","RRS_mean"):
    if _pref in cls.columns: rrs_col=_pref; break
else: rrs_col=cand_cols[0]
assert key!="cohort_id", f"unexpected cls key cols {cls.columns.tolist()}"
d = pns[["PP","PNS"]].merge(cls[[key, rrs_col]].rename(columns={key:"PP"}), on="PP", how="inner")
def mw(s):
    mol = Chem.MolFromSmiles(s)
    return float(Descriptors.MolWt(mol)) if mol else np.nan
def scaff(s):
    mol = Chem.MolFromSmiles(s)
    return MurckoScaffold.MurckoScaffoldSmiles(mol=mol) if mol else ""
d["MW"]   = [mw(s) for s in adm.set_index("smiles").loc[d.PP.map(dict(zip(adm.candidate,adm.smiles)))].values] \
            if False else [mw(dict(zip(adm.candidate,adm.smiles))[p]) for p in d.PP]
scaf      = [scaff(dict(zip(adm.candidate,adm.smiles))[p]) for p in d.PP]
prev      = pd.Series(scaf).map(pd.Series(scaf).value_counts(normalize=True))
d["scaf_prev"] = prev.values
d = d.dropna(subset=["PNS",rrs_col,"MW"])
from scipy.stats import spearmanr
def partial_spearman(x,y,z):
    Z = np.atleast_2d(z)
    if Z.shape[0] != len(x): Z = Z.T
    rx = pd.Series(x).rank().values
    ry = pd.Series(y).rank().values
    rz = pd.DataFrame(Z).rank().values
    def resid(a,b):
        A=np.column_stack([np.ones(len(b)),b]); beta,*_=np.linalg.lstsq(A,a,rcond=None); return a-A@beta
    return spearmanr(resid(rx,rz), resid(ry,rz)).statistic
raw = spearmanr(d.PNS, d[rrs_col]).statistic
part = partial_spearman(d.PNS.values, d[rrs_col].values, d[["MW","scaf_prev"]].values)
d.to_csv(os.path.join(OUT,"partial_corr_input_table.csv"), index=False)
summary["run2"] = {"note":"PNS–RRS conditioning on MW+Murcko prevalence; TDA topology values NOT available locally",
                   "rrs_column":rrs_col,"n":len(d),"raw_spearman":round(float(raw),4),
                   "partial_spearman_given_MW_scaffold":round(float(part),4)}

# ---------- RUN3: cohort-level bootstrap (no replicate scores → no score-level σ) ----------
rng = np.random.default_rng(42)
klass = cls.set_index("candidate" if "candidate" in cls.columns else cls.columns[0]).get("class")
if klass is None:
    klass = cls.iloc[:, [i for i,c in enumerate(cls.columns) if c.lower() in ("class","rrs_class")][0]]
klass = klass.dropna()
B = 10000
props = {k: [] for k in sorted(klass.unique())}
idx = rng.integers(0, len(klass), size=(B, len(klass)))
for row in idx:
    vc = klass.iloc[row].value_counts(normalize=True)
    for k in props: props[k].append(vc.get(k, 0.0))
ci = {k: [round(float(np.percentile(v,2.5)),3), round(float(np.percentile(v,97.5)),3)] for k,v in props.items()}
mut = m[m.mutation.str.upper()!="WT"]
above = (mut.mmgbsa_rrs > 100).values
boot_above = [float(rng.choice(above, size=len(above), replace=True).mean()) for _ in range(B)]
summary["run3"] = {"note":"cohort-level bootstrap; docking CSV has single score/system → no score-level sigma",
                   "class_fraction_CI95": ci,
                   "frac_mutant_ratio_gt100_point": round(float(above.mean()),3),
                   "frac_mutant_ratio_gt100_CI95": [round(float(np.percentile(boot_above,2.5)),3),
                                                    round(float(np.percentile(boot_above,97.5)),3)]}

with open(os.path.join(OUT,"lightweight_runs_summary.json"),"w") as f:
    json.dump(summary,f,indent=2)
print(json.dumps(summary, indent=2))
