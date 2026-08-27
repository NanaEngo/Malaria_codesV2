#!/usr/bin/env python3
"""
P2 — ProLIF interaction-fingerprint occupancy on the Set-C pilot trajectories.

Post-processing only (no new MD). For each of the 16 QC-PASS pilot systems
(PP-01/PP-02 x PfDHFR/PfCRT mutation states) it:
  1. loads the production trajectory (topol.top + production.xtc) with MDAnalysis,
  2. computes ProLIF interaction fingerprints (HBA, HBD, hydrophobic, aromatic,
     ionic, etc.) ligand-vs-protein on a 100-frame subsample,
  3. writes per-residue interaction occupancy CSV + a system-level summary JSON.

Inputs are read from the canonical preparation root (same sources as the QC
chain). Outputs are written under results/prolif_ifp_20260827/ and never
overwrite any canonical file.

Usage (conda env malaria_md):
    python scripts/p2_prolif_ifp_pilot.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

import MDAnalysis as mda
import prolif as plf

P2_ROOT = Path(__file__).resolve().parent.parent
QC = P2_ROOT / "results" / "set_c_md" / "set_c_trajectory_qc_pilot.csv"
OUT = P2_ROOT / "results" / "prolif_ifp_20260827"
N_FRAMES = 100  # subsample for occupancy (10 ns trajectory, 1001 frames)


def main() -> int:
    qc = pd.read_csv(QC)
    qc = qc[qc["qc_status"] == "PASS"]
    if len(qc) != 16:
        print(f"[WARN] expected 16 QC-PASS rows, found {len(qc)}; continuing", file=sys.stderr)

    OUT.mkdir(parents=True, exist_ok=True)
    summaries = []

    for _, row in qc.iterrows():
        set_c_id, target, mut = row["set_c_id"], row["target"], row["mutation"]
        xtc = Path(row["trajectory_path"])
        tpr = Path(row["tpr_path"])
        if not xtc.exists() or not tpr.exists():
            print(f"[FAIL] missing xtc/tpr for {set_c_id} {target} {mut}", file=sys.stderr)
            summaries.append({"set_c_id": set_c_id, "target": target,
                              "mutation": mut, "status": "FAIL_MISSING_FILES"})
            continue

        key = f"{set_c_id}_{target}_{mut}"
        print(f"[RUN] {key}: loading {xtc.name} (tpr topology) ...")
        try:
            u = mda.Universe(str(tpr), str(xtc))
        except Exception as exc:  # noqa: BLE001 - fail closed per system
            print(f"[FAIL] {key}: MDAnalysis load error: {exc}", file=sys.stderr)
            summaries.append({"set_c_id": set_c_id, "target": target,
                              "mutation": mut, "status": "FAIL_LOAD"})
            continue

        # ligand = MOL0 residue; protein = all protein chains
        lig = u.select_atoms("resname MOL0")
        prot = u.select_atoms("protein")
        if len(lig) == 0 or len(prot) == 0:
            print(f"[FAIL] {key}: empty ligand ({len(lig)}) or protein ({len(prot)}) selection",
                  file=sys.stderr)
            summaries.append({"set_c_id": set_c_id, "target": target,
                              "mutation": mut, "status": "FAIL_SELECTION"})
            continue

        n_total = u.trajectory.n_frames
        step = max(1, n_total // N_FRAMES)
        frames = list(range(0, n_total, step))[:N_FRAMES]

        # ProLIF IFP (v2.x API: generate() runs on the current trajectory frame;
        # the Molecule keeps live coordinates from the AtomGroup)
        ifp = plf.Fingerprint(["Hydrophobic", "HBDonor", "HBAcceptor", "PiCation",
                               "PiStacking", "CationPi", "Anionic", "Cationic",
                               "VdWContact"])
        lig_plf = plf.Molecule.from_mda(lig)
        prot_plf = plf.Molecule.from_mda(prot)

        # accumulate per-frame interaction counts: {interaction: [0/1 per frame]}
        ifp_names = ["Hydrophobic", "HBDonor", "HBAcceptor", "PiCation",
                     "PiStacking", "CationPi", "Anionic", "Cationic", "VdWContact"]
        per_frame = {name: [] for name in ifp_names}
        pair_meta = []  # (protein_resnr, protein_resname, interaction, n_active_frames)
        pair_counts = {}
        n_sampled = 0
        for ts in u.trajectory:
            if ts.frame not in frames:
                continue
            n_sampled += 1
            bits = ifp.generate(lig_plf, prot_plf, metadata=False)
            # bits: {(lig_res, prot_res): np.ndarray} over ifp.interactions
            for (_, prot_res), vec in bits.items():
                for i, name in enumerate(ifp.interactions):
                    if vec[i]:
                        key_p = (prot_res, name)
                        pair_counts[key_p] = pair_counts.get(key_p, 0) + 1
        if n_sampled == 0:
            print(f"[FAIL] {key}: no frames sampled", file=sys.stderr)
            summaries.append({"set_c_id": set_c_id, "target": target,
                              "mutation": mut, "status": "FAIL_NO_FRAMES"})
            continue

        if not pair_counts:
            print(f"[WARN] {key}: no interactions detected over {n_sampled} frames",
                  file=sys.stderr)
            summaries.append({"set_c_id": set_c_id, "target": target,
                              "mutation": mut, "status": "EMPTY_IFP",
                              "n_frames_sampled": n_sampled})
            continue

        # occupancy table
        rows = []
        for (prot_res, interaction), n_act in pair_counts.items():
            # prot_res is a prolif ResidueId with .name/.number/.chain attributes
            rows.append({"protein_resnr": prot_res.number,
                         "protein_resname": prot_res.name,
                         "protein_chain": prot_res.chain,
                         "interaction": interaction,
                         "occupancy": n_act / n_sampled})
        occ = pd.DataFrame(rows)
        occ = occ.sort_values(["protein_resnr", "interaction"])
        occ.insert(0, "set_c_id", set_c_id)
        occ.insert(1, "target", target)
        occ.insert(2, "mutation", mut)

        occ_csv = OUT / f"ifp_{key}.csv"
        occ.to_csv(occ_csv, index=False)

        # top contacts: residues with any interaction in >= 50% of frames
        per_res = occ.groupby(["protein_resnr", "protein_resname"])["occupancy"].max()
        top_contacts = per_res[per_res >= 0.5].sort_values(ascending=False)
        summaries.append({
            "set_c_id": set_c_id, "target": target, "mutation": mut,
            "status": "COMPUTED",
            "n_frames_sampled": n_sampled,
            "n_interaction_types": len(ifp.interactions),
            "n_contacts_ge50pct": int(len(top_contacts)),
            "top_contacts_ge50pct": [
                {"residue": f"{resname}{resnr}", "max_occupancy": float(v)}
                for (resnr, resname), v in top_contacts.items()
            ],
        })
        print(f"[OK] {key}: {len(occ)} residue-interaction rows, "
              f"{len(top_contacts)} contacts >= 50% occupancy")

    with open(OUT / "prolif_summary.json", "w") as f:
        json.dump({"n_systems": len(summaries),
                   "n_computed": sum(1 for s in summaries if s["status"] == "COMPUTED"),
                   "systems": summaries}, f, indent=2)
    print(f"\nDONE: {sum(1 for s in summaries if s['status'] == 'COMPUTED')}/16 computed; "
          f"summary -> {OUT / 'prolif_summary.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
