#!/usr/bin/env python3
"""P5 DD screening-utility secondary analyses (post-hoc, no retraining).

Reads archived canonical-scaffold fold predictions (index,y,p) for the 5 arms,
computes per fold-seed record then aggregates as mean over 5 per-seed means
+/- population SD (DAR convention):
  B4: EF@1%, EF@5%, BEDROC(alpha=20), precision@1%/5% (pooled-screening view:
      folds concatenated per seed, mimicking one ranked library per seed).
  B5: split-conformal coverage at nominal 90% (even/odd deterministic split of
      each test fold into calib/eval halves; nonconformity s = 1 - p_true).
  B6: Platt + isotonic recalibration fit on calib half; ECE(15 bins) of
      raw/Platt/isotonic on eval half.
  B7: TFP-rescue molecule mining (pooled mean p over 25 records/arm).
Outputs: results/dd_screening_utility_20260916/
Deterministic; numpy+pandas+rdkit stdlib otherwise.
"""
import csv, json, math, os
from datetime import date

import numpy as np
import pandas as pd

P5 = "/home/taamangtchu/Documents/Malaria_codesV2/Project5_GNN_Transformer_DrugDiscovery_V2609"
TR = os.path.join(P5, "results/extended_campaign_20260825/training/canonical_scaffold")
CB = os.path.join(P5, "results/extended_campaign_20260825/chemberta/canonical_scaffold")
ARMS = {
    "ECFP4-RF": os.path.join(TR, "ECFP4-RF"),
    "GIN": os.path.join(TR, "GIN_native"),
    "GIN-TFP": os.path.join(TR, "GIN-TFP_native"),
    "GIN-TNE": os.path.join(TR, "GIN-TNE_native"),
    "ChemBERTa": CB,
}
SEEDS = range(5)
FOLDS = range(5)
OUT = os.path.join(P5, "results/dd_screening_utility_20260916")
os.makedirs(OUT, exist_ok=True)
ALPHA_BEDROC = 20.0
NOM_COV = 0.90


def load(arm, s, k):
    df = pd.read_csv(os.path.join(ARMS[arm], f"pred_seed{s}_fold{k}.csv"))
    assert list(df.columns) == ["index", "y", "p"], df.columns
    return df["index"].to_numpy(), df["y"].to_numpy(dtype=float), df["p"].to_numpy(dtype=float)


def bedroc(y, p, alpha=ALPHA_BEDROC):
    order = np.argsort(-p, kind="stable")
    ys = y[order]
    n = len(y)
    ra = ys.sum()
    if ra == 0 or ra == n:
        return float("nan")
    ranks = np.flatnonzero(ys == 1) + 1  # 1-based
    num = np.exp(-alpha * ranks / n).sum()
    den = ra * (1 - math.exp(-alpha)) / (math.exp(alpha / n) - 1)
    return float(num / den)


def ef_prec(y, p, frac):
    n = len(y)
    ntop = max(1, int(round(n * frac)))
    order = np.argsort(-p, kind="stable")[:ntop]
    a_top = y[order].sum()
    prec = a_top / ntop
    ef = prec / (y.sum() / n) if y.sum() > 0 else float("nan")
    return float(ef), float(prec)


def ece(y, p, bins=15):
    edges = np.linspace(0, 1, bins + 1)
    tot = 0.0
    for b in range(bins):
        m = (p > edges[b]) & (p <= edges[b + 1] if b + 1 < bins else p <= 1.0)
        if b == 0:
            m = (p >= 0.0) & (p <= edges[1])
        if m.sum() == 0:
            continue
        tot += m.sum() / len(y) * abs(y[m].mean() - p[m].mean())
    return float(tot)


def platt_fit(p_cal, y_cal, iters=100):
    # Newton for sigmoid(A*p+B); init A=0,B=logit(base rate)
    r = np.clip(y_cal.mean(), 1e-6, 1 - 1e-6)
    A, B = 0.0, math.log(r / (1 - r))
    pc = np.clip(p_cal, 1e-9, 1 - 1e-9)
    for _ in range(iters):
        z = A * pc + B
        q = 1 / (1 + np.exp(-z))
        q = np.clip(q, 1e-12, 1 - 1e-12)
        gA = ((q - y_cal) * pc).sum()
        gB = (q - y_cal).sum()
        w = q * (1 - q)
        Haa = (w * pc * pc).sum() + 1e-9
        Hab = (w * pc).sum()
        Hbb = w.sum() + 1e-9
        det = Haa * Hbb - Hab * Hab
        dA = (Hbb * gA - Hab * gB) / det
        dB = (Haa * gB - Hab * gA) / det
        A -= dA
        B -= dB
        if abs(dA) + abs(dB) < 1e-10:
            break
    return A, B


def platt_apply(p, A, B):
    pc = np.clip(p, 1e-9, 1 - 1e-9)
    return 1 / (1 + np.exp(-(A * pc + B)))


def isotonic_fit(p_cal, y_cal):
    o = np.argsort(p_cal, kind="stable")
    xs, ys = p_cal[o], y_cal[o]
    # PAVA: blocks with (sum, count)
    sums, cnts = [ys[0]], [1]
    xs_b = [xs[0]]
    for x, yv in zip(xs[1:], ys[1:]):
        sums.append(yv); cnts.append(1); xs_b.append(x)
        while len(sums) >= 2 and sums[-2] / cnts[-2] > sums[-1] / cnts[-1]:
            s = sums.pop() + sums.pop(); c = cnts.pop() + cnts.pop()
            sums.append(s); cnts.append(c); xs_b.pop()
    vals = np.array(sums) / np.array(cnts)
    return np.array(xs_b), vals


def isotonic_apply(p, xs_b, vals):
    return vals[np.clip(np.searchsorted(xs_b, p, side="right") - 1, 0, len(vals) - 1)]


screen_rows, conf_rows, rec_rows = [], [], []
for arm in ARMS:
    per_seed = {m: [] for m in ("ef1", "ef5", "bedroc", "p1", "p5", "cov", "ssize",
                                "ece_raw", "ece_platt", "ece_iso")}
    for s in SEEDS:
        pool_y, pool_p = [], []
        covs, ssizes, er, ep, ei = [], [], [], [], []
        for k in FOLDS:
            idx, y, p = load(arm, s, k)
            pool_y.append(y); pool_p.append(p)
            cal = np.arange(len(y)) % 2 == 0
            yc, pc = y[cal], p[cal]
            ye, pe = y[~cal], p[~cal]
            s_cal = np.where(yc == 1, 1 - pc, pc)
            qhat = np.quantile(s_cal, min(1.0, math.ceil((len(s_cal) + 1) * NOM_COV) / len(s_cal)),
                               method="higher")
            s0 = np.where(ye == 1, 1 - pe, pe)   # score of true label
            s1 = np.where(ye == 1, pe, 1 - pe)   # score of false label
            inset_true = s0 <= qhat
            inset_false = s1 <= qhat
            covs.append(inset_true.mean())
            ssizes.append((inset_true.astype(int) + inset_false.astype(int)).mean())
            A, B = platt_fit(pc, yc)
            xs_b, vals = isotonic_fit(pc, yc)
            er.append(ece(ye, pe)); ep.append(ece(ye, platt_apply(pe, A, B)))
            ei.append(ece(ye, isotonic_apply(pe, xs_b, vals)))
        Y = np.concatenate(pool_y); P = np.concatenate(pool_p)
        ef1, p1 = ef_prec(Y, P, 0.01); ef5, p5 = ef_prec(Y, P, 0.05)
        per_seed["ef1"].append(ef1); per_seed["ef5"].append(ef5)
        per_seed["bedroc"].append(bedroc(Y, P))
        per_seed["p1"].append(p1); per_seed["p5"].append(p5)
        per_seed["cov"].append(float(np.mean(covs))); per_seed["ssize"].append(float(np.mean(ssizes)))
        per_seed["ece_raw"].append(float(np.mean(er)))
        per_seed["ece_platt"].append(float(np.mean(ep)))
        per_seed["ece_iso"].append(float(np.mean(ei)))
    agg = {m: (float(np.mean(v)), float(np.std(v))) for m, v in per_seed.items()}
    screen_rows.append({"arm": arm, **{m: round(agg[m][0], 4) for m in ("ef1", "ef5", "bedroc", "p1", "p5")},
                        **{m + "_sd": round(agg[m][1], 4) for m in ("ef1", "ef5", "bedroc", "p1", "p5")}})
    conf_rows.append({"arm": arm, "coverage_mean": round(agg["cov"][0], 4),
                      "coverage_sd": round(agg["cov"][1], 4),
                      "setsize_mean": round(agg["ssize"][0], 3),
                      "setsize_sd": round(agg["ssize"][1], 3)})
    rec_rows.append({"arm": arm, "ece_raw": round(agg["ece_raw"][0], 4),
                     "ece_platt": round(agg["ece_platt"][0], 4),
                     "ece_iso": round(agg["ece_iso"][0], 4),
                     "ece_raw_sd": round(agg["ece_raw"][1], 4)})

pd.DataFrame(screen_rows).to_csv(os.path.join(OUT, "screening_metrics.csv"), index=False)
pd.DataFrame(conf_rows).to_csv(os.path.join(OUT, "conformal_coverage.csv"), index=False)
pd.DataFrame(rec_rows).to_csv(os.path.join(OUT, "recalibration_ece.csv"), index=False)

# B7: pooled mean-p per molecule; rescue = active, GIN<0.5, TFP>=0.7 (and reverse)
pooled = {}
for arm in ("GIN", "GIN-TFP"):
    acc = {}
    for s in SEEDS:
        for k in FOLDS:
            idx, y, p = load(arm, s, k)
            for i, yv, pv in zip(idx, y, p):
                acc.setdefault(int(i), {}).setdefault("y", yv)
                acc[int(i)].setdefault("ps_" + arm, []).append(float(pv))
    for i, d in acc.items():
        pooled.setdefault(i, {"y": d["y"]})[arm] = float(np.mean(d["ps_" + arm]))
panel = pd.read_csv(os.path.join(P5, "results/canonical_panel/p5_canonical_panel.csv"),
                    usecols=["smiles", "activity"])
rescue, reverse = [], []
for i, d in pooled.items():
    if d["y"] != 1.0:
        continue
    row = {"index": i, "smiles": panel["smiles"].iloc[i],
           "GIN_p": round(d["GIN"], 3), "GIN-TFP_p": round(d["GIN-TFP"], 3)}
    if d["GIN"] < 0.5 and d["GIN-TFP"] >= 0.7:
        rescue.append(row)
    elif d["GIN-TFP"] < 0.5 and d["GIN"] >= 0.7:
        reverse.append(row)
rescue.sort(key=lambda r: r["GIN-TFP_p"] - r["GIN_p"], reverse=True)
reverse.sort(key=lambda r: r["GIN_p"] - r["GIN-TFP_p"], reverse=True)
with open(os.path.join(OUT, "tfp_rescue_examples.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["index", "smiles", "GIN_p", "GIN-TFP_p"])
    w.writeheader(); w.writerows(rescue[:12])
with open(os.path.join(OUT, "tfp_reverse_examples.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["index", "smiles", "GIN_p", "GIN-TFP_p"])
    w.writeheader(); w.writerows(reverse[:12])

summary = {"date": str(date.today()), "arms": list(ARMS), "records_per_arm": 25,
           "screening": screen_rows, "conformal_nominal": NOM_COV, "conformal": conf_rows,
           "recalibration": rec_rows, "n_rescue": len(rescue), "n_reverse": len(reverse),
           "n_molecules_pooled": len(pooled)}
with open(os.path.join(OUT, "dd_utility_summary.json"), "w") as f:
    json.dump(summary, f, indent=1)
with open(os.path.join(OUT, "audit.json"), "w") as f:
    json.dump({"script": "scripts/p5_dd_screening_utility.py", "protocol": "posthoc-no-retraining",
               "aggregation": "mean over 5 per-seed means +/- population SD",
               "conformal": "even/odd calib-eval split per test fold, s=1-p_true",
               "bedroc_alpha": ALPHA_BEDROC}, f, indent=1)
print(json.dumps({"screening": screen_rows, "conformal": conf_rows,
                  "recalibration": rec_rows, "n_rescue": len(rescue),
                  "n_reverse": len(reverse)}, indent=1))
