#!/usr/bin/env python3
"""
F2 pH Correction — HPC version.
Re-dock top 100 PfCRT ligands against pH 5.2 receptor on HPC.
Paths hardcoded for HPC filesystem.

Usage:
  python3 redock_pH_f2_hpc.py              # dry-run
  python3 redock_pH_f2_hpc.py --run         # actual docking
  python3 redock_pH_f2_hpc.py --run --parallel N
"""
import sys, os, csv, json, argparse, subprocess, multiprocessing as mp

BASE = "/home/nanaengo/Malaria_codesV2"
ORIG_RESULTS = os.path.join(BASE,
    "Project2_Polypharmacology_MD_ValidationV2607/data/from_project1/docking/Docking_6UKJ/results/summary_results_6ukj.csv")
LIGAND_DIR = os.path.join(BASE,
    "Project2_Polypharmacology_MD_ValidationV2607/data/from_project1/data/pdbqt_ligands")
RECEPTOR  = os.path.join(BASE,
    "Project2_Polypharmacology_MD_ValidationV2607/data/proteins/pH_correction/6UKJ_pH5.2_v2.pdbqt")
OUT_DIR   = os.path.join(BASE,
    "Project2_Polypharmacology_MD_ValidationV2607/data/proteins/pH_correction/redock_results")

CONFIG = {
    "center_x": 152.99, "center_y": 151.042, "center_z": 159.379,
    "size_x": 25, "size_y": 25, "size_z": 25,
    "exhaustiveness": 16,
}

os.makedirs(OUT_DIR, exist_ok=True)

def dock_one(task):
    lig_name, orig_score = task
    lig_pdbqt = os.path.join(LIGAND_DIR, f"{lig_name}.pdbqt")
    out_pdbqt = os.path.join(OUT_DIR, f"{lig_name}_out.pdbqt")

    if not os.path.exists(lig_pdbqt):
        return (lig_name, orig_score, None, "MISSING_LIGAND")

    cmd = ["vina",
        "--receptor", RECEPTOR, "--ligand", lig_pdbqt, "--out", out_pdbqt,
        "--center_x", str(CONFIG["center_x"]), "--center_y", str(CONFIG["center_y"]),
        "--center_z", str(CONFIG["center_z"]),
        "--size_x", str(CONFIG["size_x"]), "--size_y", str(CONFIG["size_y"]),
        "--size_z", str(CONFIG["size_z"]),
        "--exhaustiveness", str(CONFIG["exhaustiveness"]),
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        new_score = None
        if os.path.exists(out_pdbqt):
            with open(out_pdbqt) as f:
                for line in f:
                    if "REMARK VINA RESULT:" in line:
                        parts = line.split()
                        try:
                            new_score = float(parts[3])
                        except (IndexError, ValueError):
                            pass
                        break
        if new_score is not None:
            return (lig_name, orig_score, new_score, "OK")
        return (lig_name, orig_score, None, f"PARSE_FAIL: {r.stderr[:80]}")
    except subprocess.TimeoutExpired:
        return (lig_name, orig_score, None, "TIMEOUT")
    except Exception as e:
        return (lig_name, orig_score, None, f"ERROR: {e}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--parallel", type=int, default=32)
    args = parser.parse_args()

    orig = {}
    with open(ORIG_RESULTS) as f:
        for row in csv.DictReader(f):
            orig[row["Ligand"]] = float(row["Affinity_kcal_mol"])

    sorted_ligs = sorted(orig.items(), key=lambda x: x[1])
    top100 = sorted_ligs[:100]
    print(f"Top 100: {top100[0][0]} ({top100[0][1]:.2f}) → {top100[-1][0]} ({top100[-1][1]:.2f})")

    if not args.run:
        print("DRY-RUN:")
        missing = sum(1 for n, _ in top100 if not os.path.exists(os.path.join(LIGAND_DIR, f"{n}.pdbqt")))
        print(f"  Ligands:  {100 - missing}/100 available")
        print(f"  Receptor: {'OK' if os.path.exists(RECEPTOR) else 'MISSING'}")
        print(f"  Results:  {'OK' if os.path.exists(ORIG_RESULTS) else 'MISSING'}")
        print(f"  Vina:     {'OK' if subprocess.run(['which','vina'],capture_output=True).returncode==0 else 'MISSING'}")
        print("\nRun: python3 redock_pH_f2_hpc.py --run [--parallel N]")
        return

    print(f"Running (exhaustiveness={CONFIG['exhaustiveness']}, {args.parallel} workers)...")
    with mp.Pool(args.parallel) as pool:
        results = pool.map(dock_one, top100)

    log_path = os.path.join(OUT_DIR, "f2_redock_log.csv")
    with open(log_path, "w") as f:
        w = csv.writer(f)
        w.writerow(["Ligand", "Orig_Score", "New_Score", "Orig_Rank", "Status"])
        success = []
        for rank, (lig_name, orig_score, new_score, status) in enumerate(results, 1):
            w.writerow([lig_name, orig_score, f"{new_score:.3f}" if new_score else "", rank, status])
            if new_score is not None:
                success.append((lig_name, orig_score, new_score, rank))

    print(f"\nSuccess: {len(success)}/{len(top100)}")
    if len(success) >= 2:
        from scipy.stats import spearmanr
        orig_vals = [s[1] for s in success]
        new_vals  = [s[2] for s in success]
        rho, pval = spearmanr(orig_vals, new_vals)
        analysis = {
            "n_docked": len(success), "n_total": len(top100),
            "spearman_rho": round(rho, 4), "spearman_p": round(pval, 6),
            "mean_orig": round(sum(orig_vals)/len(orig_vals), 3),
            "mean_new":  round(sum(new_vals)/len(new_vals), 3),
        }
        with open(os.path.join(OUT_DIR, "f2_analysis.json"), "w") as f:
            json.dump(analysis, f, indent=2)
        print(f"\nSpearman ρ = {rho:.4f} (p = {pval:.6f})")
        print(f"Mean orig: {analysis['mean_orig']:.2f}  Mean new: {analysis['mean_new']:.2f}")

if __name__ == "__main__":
    main()
