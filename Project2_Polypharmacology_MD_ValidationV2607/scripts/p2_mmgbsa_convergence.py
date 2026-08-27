#!/usr/bin/env python3
"""MM-GBSA endpoint summary + convergence analysis for Set-C reruns.

Two modes, both read-only on inputs:
  A) Parse every FINAL_RESULTS_MMPBSA.dat under the given roots:
     DELTA TOTAL mean / SD / SEM -> tidy CSV + SEM < 1 kcal/mol gate.
  B) If a per-frame energy CSV (gmx_MMPBSA -eo) exists next to the .dat,
     compute cumulative-average convergence + block-averaging SEM and plot.

Usage: python p2_mmgbsa_convergence.py [--root DIR ...] [--outdir DIR]
Default roots: canonical batch mmgbsa_20260819 + single_rerun_20260825/mmgbsa.
"""
import argparse
import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROOTS = [
    ROOT / "results" / "set_c_md" / "mmgbsa_20260819",
    ROOT / "results" / "set_c_md" / "single_rerun_20260825" / "mmgbsa",
]
SEM_GATE = 1.0  # kcal/mol, best-practice convergence target
N_BLOCKS = 5


def parse_final_results(dat: Path):
    """Return dict with DELTA rows: name -> (mean, sd_prop, sd, sem_prop, sem)."""
    rows = {}
    in_delta = False
    for line in dat.read_text(errors="replace").splitlines():
        if line.startswith("Delta ("):
            in_delta = True
            continue
        if not in_delta:
            continue
        m = re.match(r"^(\S+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)", line)
        if m:
            rows[m.group(1)] = tuple(float(x) for x in m.groups()[1:])
    return rows


def load_timeseries(csv_path: Path):
    """Parse gmx_MMPBSA -eo CSV; return list of frame indices and ΔTOTAL series."""
    lines = [l for l in csv_path.read_text(errors="replace").splitlines() if l.strip()]
    # find header line containing 'Frame'
    hdr_i = next((i for i, l in enumerate(lines) if "frame" in l.lower()), None)
    if hdr_i is None:
        return None
    rdr = csv.reader(lines[hdr_i:])
    header = next(rdr)
    # locate a DELTA TOTAL-like column
    col = next((j for j, h in enumerate(header)
                if re.search(r"(delta.*total|total)", h.strip().lower())), None)
    if col is None or not any("delta" in h.lower() for h in header):
        return None
    frames, vals = [], []
    for row in rdr:
        try:
            v = float(row[col])
        except (ValueError, IndexError):
            continue
        frames.append(len(vals))
        vals.append(v)
    return (frames, vals) if vals else None


def block_sem(vals):
    n = len(vals)
    size = max(1, n // N_BLOCKS)
    blocks = [vals[i:i + size] for i in range(0, n - size + 1, size)]
    means = [sum(b) / len(b) for b in blocks]
    if len(means) < 2:
        return None
    mu = sum(means) / len(means)
    var = sum((m - mu) ** 2 for m in means) / (len(means) - 1)
    return var ** 0.5 / len(means) ** 0.5


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", action="append", default=[])
    ap.add_argument("--outdir", default=None)
    args = ap.parse_args()
    roots = [Path(r) for r in args.root] or DEFAULT_ROOTS
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    outdir = Path(args.outdir) if args.outdir else ROOT / "results" / "set_c_md" / f"mmgbsa_convergence_{stamp}"
    outdir.mkdir(parents=True, exist_ok=True)

    records = []
    for root in roots:
        for dat in sorted(root.glob("*/FINAL_RESULTS_MMPBSA.dat")):
            sys_name = dat.parent.name
            delta = parse_final_results(dat)
            total = delta.get("ΔTOTAL") or delta.get("DTOTAL") or delta.get("TOTAL")
            if total is None:
                records.append({"system": sys_name, "source": str(dat), "status": "PARSE_FAILED"})
                continue
            mean, sd_prop, sd, sem_prop, sem = total
            rec = {
                "system": sys_name,
                "source": str(dat),
                "dg_mean_kcalmol": mean,
                "sd_prop": sd_prop, "sd": sd,
                "sem_prop": sem_prop, "sem": sem,
                "sem_lt_1_gate": "PASS" if sem < SEM_GATE else "FAIL",
            }
            ts_csv = dat.parent / "mmgbsa_timeseries.csv"
            if ts_csv.is_file():
                ts = load_timeseries(ts_csv)
                if ts:
                    frames, vals = ts
                    bsem = block_sem(vals)
                    rec["n_frames"] = len(vals)
                    rec["block_sem"] = bsem
                    rec["cum_plot"] = plot_cumulative(sys_name, vals, outdir)
            records.append(rec)

    out_csv = outdir / "mmgbsa_endpoints_summary.csv"
    if records:
        keys = sorted({k for r in records for k in r})
        with open(out_csv, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=keys)
            w.writeheader()
            w.writerows(records)

    ok = [r for r in records if r.get("sem_lt_1_gate") == "PASS"]
    report = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "roots": [str(r) for r in roots],
        "n_systems": len([r for r in records if "dg_mean_kcalmol" in r]),
        "sem_gate": {"threshold_kcalmol": SEM_GATE, "pass": len(ok)},
        "records": records,
    }
    (outdir / "convergence_report.json").write_text(json.dumps(report, indent=2) + "\n")

    md = ["# MM-GBSA endpoints & convergence", "",
          f"Généré : {report['generated_utc']}", "",
          "| Système | ΔG (kcal/mol) | SD | SEM | Gate SEM<1 |", "|---|---|---|---|---|"]
    for r in records:
        if "dg_mean_kcalmol" in r:
            md.append(f"| {r['system']} | {r['dg_mean_kcalmol']:.2f} | {r['sd']:.2f} "
                      f"| {r['sem']:.2f} | {r['sem_lt_1_gate']} |")
        else:
            md.append(f"| {r['system']} | PARSE_FAILED | | | FAIL |")
    md += ["", "Note : « score MM-GBSA » = enthalpie d'endpoint (entropie exclue), "
           "pas un ΔG_bind expérimental ; gate SEM < 1 kcal/mol = bonne pratique 2025-2026.", ""]
    (outdir / "convergence_report.md").write_text("\n".join(md))
    print(f"{len(ok)}/{report['n_systems']} systems pass SEM<{SEM_GATE}; out: {outdir}")


def plot_cumulative(name, vals, outdir):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return None
    csum, run = [], 0.0
    for i, v in enumerate(vals, 1):
        run += v
        csum.append(run / i)
    fig, ax = plt.subplots(figsize=(5, 3.2))
    ax.plot(range(1, len(csum) + 1), csum, lw=1.2)
    ax.axhline(sum(vals) / len(vals), ls="--", c="grey", lw=0.8)
    ax.set_xlabel("Frame")
    ax.set_ylabel("Cumulative mean ΔG (kcal/mol)")
    ax.set_title(f"{name} — MM-GBSA score convergence (entropy excluded)")
    fig.tight_layout()
    p = outdir / f"cumulative_{name}.png"
    fig.savefig(p, dpi=150)
    plt.close(fig)
    return str(p)


if __name__ == "__main__":
    main()
