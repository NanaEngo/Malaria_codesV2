#!/usr/bin/env python3
"""
Re-analyze P2 MD trajectories using PBC-unwrapped (nojump) files.

Loads md_production.gro + md_production_nojump.xtc for each system,
computes RMSD, RMSF, Rg, ligand RMSD, contacts, and H-bonds, and
writes production_analysis/summary_unwrapped.txt in the same format
as the original summary.txt files.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

import MDAnalysis as mda
from MDAnalysis.analysis import distances, hydrogenbonds, rms


PROJECT_DIR = Path(__file__).parent.parent
SYSTEMS = ["164_PfClpP", "201_PfDHFR", "214_PfCRT", "438_PfATP4"]
LIGAND_RESNAMES = ["LIG", "UNL", "MOL", "DRG"]
CONTACT_CUTOFF = 4.5  # Å
HBOND_D_A_CUTOFF = 3.5  # Å
HBOND_ANGLE_CUTOFF = 150.0  # degrees
BOUND_CUTOFF = 5.0  # Å, heavy-atom minimum distance threshold for "bound"


def find_ligand(u: mda.Universe) -> mda.AtomGroup:
    """Return the first non-empty ligand selection, or the largest non-protein/non-solvent residue."""
    for name in LIGAND_RESNAMES:
        lig = u.select_atoms(f"resname {name}")
        if lig.n_atoms > 0:
            return lig
    # Fallback: largest non-protein/non-solvent residue by atom count
    fallback = u.select_atoms("not protein and not resname WAT SOL TIP3 HOH NA CL K CA MG ZN")
    if fallback.n_atoms == 0:
        return fallback
    # Group by residue and pick the largest
    residues = fallback.residues
    if len(residues) == 0:
        return fallback
    largest = max(residues, key=lambda r: r.atoms.n_atoms)
    return largest.atoms


def compute_rmsd(u: mda.Universe, selection: str, ref_frame: int = 0) -> np.ndarray:
    """Compute RMSD for a given selection."""
    r = rms.RMSD(u, select=selection, ref_frame=ref_frame).run()
    return r.results.rmsd[:, 2]


def compute_rmsf(u: mda.Universe, ca: mda.AtomGroup, start_frame: int, step: int = 10) -> np.ndarray:
    """Compute per-residue RMSF over the second half of the trajectory (sampled)."""
    traj_slice = u.trajectory[start_frame::step]
    n_frames = len(traj_slice)
    if n_frames <= 0:
        return np.zeros(ca.n_atoms)

    avg_pos = np.zeros((ca.n_atoms, 3))
    for ts in traj_slice:
        avg_pos += ca.positions
    avg_pos /= n_frames

    rmsf_vals = np.zeros(ca.n_atoms)
    for ts in traj_slice:
        rmsf_vals += np.sqrt(np.sum((ca.positions - avg_pos) ** 2, axis=1))
    rmsf_vals /= n_frames
    return rmsf_vals


def compute_contacts(u: mda.Universe, protein: mda.AtomGroup, ligand: mda.AtomGroup, step: int = 10) -> tuple[np.ndarray, np.ndarray]:
    """Return number of protein-ligand contacts (< CONTACT_CUTOFF Å) per sampled frame and min distances."""
    prot_heavy = protein.select_atoms("not name H*")
    lig_heavy = ligand.select_atoms("not name H*")
    if prot_heavy.n_atoms == 0 or lig_heavy.n_atoms == 0:
        n_sampled = max(1, len(u.trajectory[::step]))
        return np.zeros(n_sampled, dtype=float), np.full(n_sampled, np.inf, dtype=float)
    counts = []
    min_dists = []
    # Use unwrapped nojump trajectory; no PBC math needed
    for _ts in u.trajectory[::step]:
        dist_arr = distances.distance_array(prot_heavy.positions, lig_heavy.positions)
        counts.append(np.sum(dist_arr < CONTACT_CUTOFF))
        min_dists.append(dist_arr.min())
    return np.array(counts, dtype=float), np.array(min_dists, dtype=float)


def compute_hbonds(u: mda.Universe, protein: mda.AtomGroup, ligand: mda.AtomGroup, step: int = 10) -> np.ndarray:
    """Return number of protein-ligand hydrogen bonds per sampled frame."""
    if ligand.n_atoms == 0:
        return np.zeros(max(1, len(u.trajectory[::step])))

    lig_resname = ligand.resnames[0]
    selection = f"protein or resname {lig_resname}"
    hb_kwargs = dict(
        universe=u,
        donors_sel=selection,
        hydrogens_sel=selection,
        acceptors_sel=selection,
        d_a_cutoff=HBOND_D_A_CUTOFF,
        d_h_a_angle_cutoff=HBOND_ANGLE_CUTOFF,
    )
    # `between` is only available in MDAnalysis >= 2.0; fall back to selection + post-filter.
    between_used = False
    try:
        hb = hydrogenbonds.HydrogenBondAnalysis(**hb_kwargs, between=["protein", f"resname {lig_resname}"])
        between_used = True
    except TypeError:
        hb = hydrogenbonds.HydrogenBondAnalysis(**hb_kwargs)
    try:
        hb.run(step=step)
    except Exception as exc:
        print(f"    Warning: H-bond analysis failed: {exc}")
        return np.zeros(max(1, len(u.trajectory[::step])))

    # If `between` was used, the results are already restricted to protein--ligand H-bonds.
    if between_used:
        return hb.count_by_time()

    # Post-filter for older MDAnalysis versions: keep only H-bonds where one partner is in the
    # protein and the other is in the ligand. Atom indices in results.hbonds are global indices.
    if hb.results.hbonds.size == 0:
        return hb.count_by_time()
    protein_idx = set(protein.indices)
    ligand_idx = set(ligand.indices)
    donor_idx = hb.results.hbonds[:, 1].astype(int)
    acceptor_idx = hb.results.hbonds[:, 3].astype(int)
    donor_in_protein = np.array([idx in protein_idx for idx in donor_idx])
    donor_in_ligand = np.array([idx in ligand_idx for idx in donor_idx])
    acceptor_in_protein = np.array([idx in protein_idx for idx in acceptor_idx])
    acceptor_in_ligand = np.array([idx in ligand_idx for idx in acceptor_idx])
    pl_mask = (donor_in_protein & acceptor_in_ligand) | (donor_in_ligand & acceptor_in_protein)
    # results.hbonds[:, 0] stores original frame numbers (0, step, 2*step, ...).
    # Map them to sampled-frame indices before counting.
    frames = hb.results.hbonds[:, 0].astype(int)
    n_sampled = len(u.trajectory[::step])
    frame_to_idx = {f: i for i, f in enumerate(range(0, len(u.trajectory), step))}
    counts = np.zeros(n_sampled, dtype=float)
    for f, mask_val in zip(frames, pl_mask):
        if mask_val and f in frame_to_idx:
            counts[frame_to_idx[f]] += 1
    return counts


def analyze_system(system_name: str) -> None:
    """Analyze a single system and write summary_unwrapped.txt."""
    print(f"Processing {system_name}...")
    sys_dir = PROJECT_DIR / "MD_systems" / system_name
    xtc_file = sys_dir / "md_production_nojump.xtc"
    # Try several topology sources; some systems were rebuilt under rebuild_test/
    gro_candidates = [
        sys_dir / "md_production.gro",
        sys_dir / "production.gro",
        sys_dir / "rebuild_test" / "md_production.gro",
        sys_dir / "rebuild_test" / "complex.gro",
        sys_dir / "rebuild_test" / "ions.gro",
    ]
    gro_file = next((p for p in gro_candidates if p.exists()), None)
    out_file = sys_dir / "production_analysis" / "summary_unwrapped.txt"

    if gro_file is None:
        print(f"  Skipping {system_name}: no topology (.gro) found.")
        return
    if not xtc_file.exists():
        print(f"  Skipping {system_name}: {xtc_file} not found.")
        return

    u = mda.Universe(str(gro_file), str(xtc_file))
    protein = u.select_atoms("protein")
    prot_bb = u.select_atoms("protein and backbone")
    prot_ca = u.select_atoms("protein and name CA")
    ligand = find_ligand(u)
    lig_resname_info = ligand.resnames[0] if ligand.n_atoms > 0 else "NONE"
    print(f"  Ligand selection: resname={lig_resname_info}, atoms={ligand.n_atoms}")

    n_frames = len(u.trajectory)
    half = n_frames // 2

    # 1. Backbone RMSD
    rmsd_bb = compute_rmsd(u, "backbone")
    rmsd_mean = float(rmsd_bb.mean())
    rmsd_std = float(rmsd_bb.std())
    rmsd_max = float(rmsd_bb.max())
    rmsd_drift = float(rmsd_bb[half:].mean() - rmsd_bb[:half].mean())
    equilibration = "EQUILIBRATED" if abs(rmsd_drift) < 2.0 else "DRIFTING"

    # 2. RMSF
    rmsf_vals = compute_rmsf(u, prot_ca, half)

    # 3. Radius of gyration (sampled)
    rgyr = np.array([protein.radius_of_gyration() for _ in u.trajectory[::10]])

    # 4. Ligand RMSD
    if ligand.n_atoms > 0:
        lig_resname = ligand.resnames[0]
        rmsd_lig = compute_rmsd(u, f"resname {lig_resname}")
    else:
        rmsd_lig = np.zeros(n_frames)

    # 5. Contacts (sampled)
    contacts, min_dists = compute_contacts(u, protein, ligand)
    bound = "BOUND" if min_dists.mean() < BOUND_CUTOFF else "UNBOUND"

    # 6. Hydrogen bonds (sampled)
    hbonds = compute_hbonds(u, protein, ligand)

    # Write summary
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w") as f:
        f.write(f"system: {system_name}\n")
        f.write(f"frames: {n_frames}\n")
        f.write(f"protein_atoms: {protein.n_atoms}\n")
        f.write(f"ligand_atoms: {ligand.n_atoms}\n")
        f.write(f"rmsd_mean_A: {rmsd_mean:.2f}\n")
        f.write(f"rmsd_std_A: {rmsd_std:.2f}\n")
        f.write(f"rmsd_max_A: {rmsd_max:.2f}\n")
        f.write(f"rmsd_drift_A: {rmsd_drift:.2f}\n")
        f.write(f"equilibration: {equilibration}\n")
        f.write(f"rmsf_mean_A: {rmsf_vals.mean():.2f}\n")
        f.write(f"rmsf_max_A: {rmsf_vals.max():.2f}\n")
        f.write(f"rgyr_mean_A: {rgyr.mean():.2f}\n")
        f.write(f"lig_rmsd_mean_A: {rmsd_lig.mean():.2f}\n")
        f.write(f"lig_rmsd_std_A: {rmsd_lig.std():.2f}\n")
        f.write(f"lig_rmsd_max_A: {rmsd_lig.max():.2f}\n")
        f.write(f"contacts_mean: {contacts.mean():.1f}\n")
        f.write(f"hbonds_mean: {hbonds.mean():.1f}\n")
        f.write(f"min_dist_protein_ligand_A: {min_dists.mean():.2f}\n")
        f.write(f"ligand_bound: {bound}\n")
        f.write(f"note: contacts, hbonds, rmsf and rgyr sampled every 10 frames (RMSD uses all frames)\n")

    print(f"  --> Saved {out_file}")


def main() -> None:
    print("=" * 60)
    print("P2 MD Re-analysis using PBC-unwrapped trajectories")
    print("=" * 60)
    for sys in SYSTEMS:
        analyze_system(sys)
    print("\nDone!")


if __name__ == "__main__":
    main()
