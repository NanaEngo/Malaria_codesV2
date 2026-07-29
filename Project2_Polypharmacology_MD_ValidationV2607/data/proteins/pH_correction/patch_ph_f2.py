#!/usr/bin/env python3
"""
Patch script to re-run the 32 timed-out PfCRT ligands with a longer timeout (1200 seconds).
Updates the results and recomputes the Spearman correlation.
"""
import sys, os, csv, json, subprocess, multiprocessing as mp

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

LOG_PATH = os.path.join(OUT_DIR, "f2_redock_log.csv")

def dock_one(task):
    lig_name, orig_score, rank = task
    lig_pdbqt = os.path.join(LIGAND_DIR, f"{lig_name}.pdbqt")
    out_pdbqt = os.path.join(OUT_DIR, f"{lig_name}_out.pdbqt")

    print(f"Starting {lig_name} (rank {rank}, orig {orig_score})...")
    cmd = ["vina",
        "--receptor", RECEPTOR, "--ligand", lig_pdbqt, "--out", out_pdbqt,
        "--center_x", str(CONFIG["center_x"]), "--center_y", str(CONFIG["center_y"]),
        "--center_z", str(CONFIG["center_z"]),
        "--size_x", str(CONFIG["size_x"]), "--size_y", str(CONFIG["size_y"]),
        "--size_z", str(CONFIG["size_z"]),
        "--exhaustiveness", str(CONFIG["exhaustiveness"]),
    ]
    try:
        # Long timeout: 1200s (20 minutes)
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=1200)
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
            print(f"  Finished {lig_name}: {new_score}")
            return (lig_name, orig_score, new_score, "OK", rank)
        print(f"  Failed {lig_name}: PARSE_FAIL")
        return (lig_name, orig_score, None, f"PARSE_FAIL: {r.stderr[:80]}", rank)
    except subprocess.TimeoutExpired:
        print(f"  Failed {lig_name}: TIMEOUT (20m)")
        return (lig_name, orig_score, None, "TIMEOUT", rank)
    except Exception as e:
        print(f"  Failed {lig_name}: ERROR {e}")
        return (lig_name, orig_score, None, f"ERROR: {e}", rank)

def main():
    # Identify timed-out ligands
    timed_out = []
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH) as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["Status"] == "TIMEOUT":
                    timed_out.append((row["Ligand"], float(row["Orig_Score"]), int(row["Orig_Rank"])))
    
    if not timed_out:
        print("No TIMEOUT ligands found in f2_redock_log.csv!")
        return

    print(f"Found {len(timed_out)} timed-out ligands. Re-running with 1200s timeout, 8 workers...")
    
    # Run in parallel with 8 workers (less contention)
    with mp.Pool(8) as pool:
        patched_results = pool.map(dock_one, timed_out)

    # Load existing results to update
    existing = {}
    with open(LOG_PATH) as f:
        reader = csv.DictReader(f)
        for row in reader:
            existing[row["Ligand"]] = {
                "Orig_Score": float(row["Orig_Score"]),
                "New_Score": row["New_Score"],
                "Orig_Rank": int(row["Orig_Rank"]),
                "Status": row["Status"]
            }

    # Apply patches
    for lig_name, orig_score, new_score, status, rank in patched_results:
        existing[lig_name] = {
            "Orig_Score": orig_score,
            "New_Score": f"{new_score:.3f}" if new_score else "",
            "Orig_Rank": rank,
            "Status": status
        }

    # Write back the full log
    with open(LOG_PATH, "w") as f:
        w = csv.writer(f)
        w.writerow(["Ligand", "Orig_Score", "New_Score", "Orig_Rank", "Status"])
        # Sort by original rank
        sorted_keys = sorted(existing.keys(), key=lambda x: existing[x]["Orig_Rank"])
        for k in sorted_keys:
            v = existing[k]
            w.writerow([k, v["Orig_Score"], v["New_Score"], v["Orig_Rank"], v["Status"]])

    # Recompute correlation
    success = []
    for k, v in existing.items():
        if v["Status"] == "OK" and v["New_Score"] != "":
            success.append((k, v["Orig_Score"], float(v["New_Score"]), v["Orig_Rank"]))

    print(f"\nFinal Success: {len(success)}/100")
    
    if len(success) >= 2:
        from scipy.stats import spearmanr
        orig_vals = [s[1] for s in success]
        new_vals  = [s[2] for s in success]
        rho, pval = spearmanr(orig_vals, new_vals)
        
        analysis = {
            "n_docked": len(success),
            "n_total": 100,
            "spearman_rho": round(rho, 4),
            "spearman_p": round(pval, 6),
            "mean_orig": round(sum(orig_vals)/len(orig_vals), 3),
            "mean_new":  round(sum(new_vals)/len(new_vals), 3),
        }
        with open(os.path.join(OUT_DIR, "f2_analysis.json"), "w") as f:
            json.dump(analysis, f, indent=2)
            
        print(f"\n=== Patched F2 Analysis ===")
        print(f"Spearman ρ = {rho:.4f} (p = {pval:.6f})")
        print(f"Mean orig: {analysis['mean_orig']:.2f}  Mean new: {analysis['mean_new']:.2f}")

        # Write clean summary
        with open(os.path.join(OUT_DIR, "f2_manuscript_summary.txt"), "w") as f:
            f.write(f"F2 pH Correction: PfCRT re-docked at pH 5.2 (Patched)\n")
            f.write(f"  Receptor: 6UKJ chain A (residues 47-405), PROPKA-informed pH 5.2\n")
            f.write(f"  Docking: Vina exhaustiveness=16, box 25Å\n")
            f.write(f"  N re-docked: {analysis['n_docked']}/100\n")
            f.write(f"  Spearman ρ (pH 7.4 vs pH 5.2): {analysis['spearman_rho']:.3f} (p={analysis['spearman_p']:.6e})\n")
            f.write(f"  Mean Δ (new - orig): {analysis['mean_new'] - analysis['mean_orig']:.2f} kcal/mol\n")

if __name__ == "__main__":
    main()
