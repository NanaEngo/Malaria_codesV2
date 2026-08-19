#!/usr/bin/env python3
"""P4 — QMC Tier 1/2 Execution Pipeline

Selects the Pareto candidates from results/pareto/ (array index 0..N-1).

Tier 1: GFN2-xTB 3D geometry optimization + PySCF PBE/def2-SVP trial wavefunctions.
        Saves both a molden file (visualisation) and a PySCF chkfile (QMC input).
Tier 2: Variational Monte Carlo (VMC) energy + Slater-Jastrow Diffusion Monte Carlo
        (DMC) energy, using the PyQMC recipes VMC()/DMC(). Outputs a per-candidate
        energies CSV (p4_qmc_energies.csv) with E_VMC, E_DMC and correlation energies.
        (See 'IMPORTANT' below — candidate-level DMC values are unreliable in this env.)

IMPORTANT — PyQMC 0.8.1 JastrowSpin is BROKEN in this environment (July 31, 2026):
PyQMC 0.8.1's DEFAULT Jastrow (ion_cusp=None -> acoeff = atom_charges) produces
non-variational garbage VMC energies (H2O VMC -99.58 vs SCF -76.33; reproduced
across pyscf 2.8/2.14 and numpy 1.x/2.x — an environment-level bug in the
JastrowSpin combination/summation path: the individual basis kernels are
verified correct (finite-difference audit), but the full-wavefunction
derivative evaluation is broken). Disabling the ion cusp
(jastrow_kws={'ion_cusp': False}) restores VALID variational energies on SMALL
systems only (H2O: DMC -76.50 vs SCF -76.33 vs FCI -76.44). However, WITHOUT a
correct electron-ion cusp the local energy diverges near nuclei -> infinite
variance -> DMC population collapse on drug-size molecules: candidate_0
(C12H17NO3, 144 e-) DMC at nconfig=100 gave -1021 vs SCF -864 with 15->92 of
100 walkers killed per block (walker positions collapse to 0.25 Bohr).

CONSEQUENCE: Tier 2 energies for the large Pareto candidates are NOT
publication-grade. The ion_cusp=False workaround is validated only on H2O;
candidate-level VMC/DMC values must be reported with this limitation or
recomputed with a fixed Jastrow (e.g. QMCPACK or a patched PyQMC).

Scope note (honest): the Jastrow factor is the PyQMC default Slater-Jastrow trial
from the PBE orbitals with the ion-cusp term disabled, Jastrow NOT optimised. Tier 2
produces real VMC/DMC energies on SMALL systems (H2O-validated: DMC -76.50 vs SCF
-76.33 vs FCI -76.44); candidate-level DMC values for the 144-electron Pareto
molecules are UNRELIABLE — without a correct electron-ion cusp the local energy
diverges near nuclei, driving DMC population collapse (walkers killed 15->92 of
100; mean walker position 0.25 Bohr). A production protocol would require a working
Jastrow (patched PyQMC or QMCPACK), Jastrow optimisation (pyqmc.recipes.OPTIMIZE),
nconfig >= 1000 and a tau->0 extrapolation.
"""

import argparse
import csv
import fcntl
import os
import subprocess
import time
from pathlib import Path

import numpy as np
import pandas as pd

try:
    from pyscf import gto, dft, scf
except ImportError:
    gto = None
    dft = None
    scf = None

try:
    import gpu4pyscf
    has_gpu4pyscf = True
except ImportError:
    has_gpu4pyscf = False

try:
    from rdkit import Chem
    from rdkit.Chem import AllChem
except ImportError:
    Chem = None
    AllChem = None

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PARETO_DIR = PROJECT_ROOT / "results" / "pareto"
QMC_DIR = PROJECT_ROOT / "results" / "qmc"
ENERGIES_CSV = QMC_DIR / "p4_qmc_energies.csv"

HARTREE_TO_EV = 27.211386245988


def parse_args():
    parser = argparse.ArgumentParser(description="P4 QMC Pipeline (Tier 1 + Tier 2)")
    parser.add_argument("--array-id", type=int, default=None, help="SLURM array ID (0-3)")
    parser.add_argument("--test-run", action="store_true", help="Run a fast mock test")
    parser.add_argument("--tier1-only", action="store_true", help="Skip Tier 2 (VMC/DMC)")
    parser.add_argument("--nconfig", type=int, default=300, help="PyQMC nconfig (default 300)")
    parser.add_argument("--vmc-blocks", type=int, default=20, help="VMC blocks (default 20)")
    parser.add_argument("--vmc-steps", type=int, default=20, help="VMC steps per block (default 20)")
    parser.add_argument("--dmc-blocks", type=int, default=50, help="DMC blocks (default 50)")
    parser.add_argument("--dmc-steps", type=int, default=10, help="DMC steps per block (default 10)")
    parser.add_argument("--dmc-tstep", type=float, default=0.005, help="DMC time step in a.u. (default 0.005)")
    return parser.parse_args()


def get_top_5_pareto_candidates():
    """Reads the merged Pareto front and returns top 5 SMILES."""
    merged_path = PARETO_DIR / "merged_pareto_front.csv"
    if not merged_path.exists():
        print(f"Warning: {merged_path} not found. Using mock candidates.")
        return ["CC(C)C1=CC=C(C=C1)C(C)C", "c1ccccc1", "CCO", "CCN", "CCC"]

    df = pd.read_csv(merged_path)
    # Sort by some surrogate metric of Pareto rank, here assuming arbitrary sort
    if "Reward" in df.columns:
        df = df.sort_values(by="Reward", ascending=False)

    top5_col = next((c for c in df.columns if c.lower() == "smiles"), None)
    if top5_col is None:
        raise KeyError(f"No 'smiles' column found in {merged_path}. Columns: {list(df.columns)}")
    top5 = df[top5_col].head(5).tolist()
    return top5


def run_xtb_optimization(smiles, run_dir, name):
    """Tier 1: GFN2-xTB Geometry Optimization."""
    print(f"Running GFN2-xTB optimization for {name}...")
    if Chem is None:
        print("RDKit not installed. Skipping.")
        return None

    mol = Chem.MolFromSmiles(smiles)
    if not mol:
        return None

    mol = Chem.AddHs(mol)
    ret = AllChem.EmbedMolecule(mol, randomSeed=42)
    if ret == -1:
        print(f"  Warning: 3D embedding failed for {name}. Trying ETKDG with ETversion=2.")
        ret = AllChem.EmbedMolecule(mol, AllChem.ETKDGv3())
    if ret == -1:
        raise RuntimeError(f"3D embedding failed for {name} ({smiles}). Cannot continue.")
    AllChem.MMFFOptimizeMolecule(mol)

    xyz_path = run_dir / f"{name}_initial.xyz"
    Chem.rdmolfiles.MolToXYZFile(mol, str(xyz_path))

    opt_xyz_path = run_dir / f"{name}_xtbopt.xyz"

    # Run xTB via subprocess
    try:
        subprocess.run(
            ["xtb", str(xyz_path), "--opt", "tight"],
            cwd=run_dir,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        if (run_dir / "xtbopt.xyz").exists():
            (run_dir / "xtbopt.xyz").rename(opt_xyz_path)
            return opt_xyz_path
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("xTB command failed or not found. Using RDKit MMFF geometry as fallback.")
        return xyz_path

    return xyz_path


def _to_numpy(a):
    """Convert cupy (gpu4pyscf) arrays to numpy for chkfile/molden writers."""
    if hasattr(a, "get"):
        return a.get()
    return np.asarray(a)


def generate_trial_wavefunction(xyz_path, run_dir, name):
    """Tier 1: PySCF PBE/def2-SVP trial wavefunctions.

    Saves both a molden file (visualisation) and a PySCF chkfile (PyQMC input).
    Returns (mol, mf, e_tot) so Tier 2 can reuse the converged mean-field object.
    """
    print(f"Generating PBE/def2-SVP trial wavefunction for {name}...")
    if gto is None or dft is None:
        print("PySCF not installed. Skipping.")
        return None

    mol = gto.Mole()
    mol.fromfile(str(xyz_path))
    mol.basis = "def2-svp"
    # def2-ECP is only defined for atoms with Z > 36 (Rb and heavier). All P4
    # Pareto candidates are light organic molecules (C/H/N/O/S, Z <= 16), so no
    # ECP is required. Setting ecp=None avoids the 'Unable to parse ECP data'
    # RuntimeError that occurs with the invalid literal name "def2-ecp".
    mol.ecp = None
    mol.build()

    if has_gpu4pyscf:
        print("Using GPU-accelerated PySCF (gpu4pyscf)...")
        from gpu4pyscf.dft import rks as gpu_rks
        mf = gpu_rks.RKS(mol).to_gpu()
    else:
        print("Using CPU PySCF with Density Fitting (RI-J)...")
        mf = dft.RKS(mol).density_fit()

    mf.xc = "pbe"
    mf.kernel()

    e_tot = float(mf.e_tot)
    print(f"DFT Total Energy (PBE/def2-SVP): {e_tot:.6f} Eh")

    # Save molden file for visualisation
    # Note: pip-installed PySCF exposes molden under pyscf.tools, not pyscf.molden
    from pyscf.tools import molden
    molden_path = run_dir / f"{name}_pbe.molden"
    molden.from_mo(mol, str(molden_path), _to_numpy(mf.mo_coeff),
                   ene=_to_numpy(mf.mo_energy), occ=_to_numpy(mf.mo_occ))
    print(f"Saved trial wavefunction to {molden_path}")

    # Save PySCF chkfile for PyQMC (recover_pyscf reads scf/mo_coeff, mo_occ, mo_energy)
    # PySCF 2.14: save_mol(mol, chkfile) serializes the Mole via mol.dumps() JSON
    # (NOTE arg order: mol first), and dump(chkfile, key, value) stores one array
    # per call under h5 paths like 'scf/mo_coeff'.
    chk_path = run_dir / f"{name}_pbe.chk"
    try:
        scf.chkfile.save_mol(mol, str(chk_path))
        scf.chkfile.dump(str(chk_path), "scf/mo_energy", _to_numpy(mf.mo_energy))
        scf.chkfile.dump(str(chk_path), "scf/mo_coeff", _to_numpy(mf.mo_coeff))
        scf.chkfile.dump(str(chk_path), "scf/mo_occ", _to_numpy(mf.mo_occ))
        print(f"Saved PySCF chkfile to {chk_path}")
    except Exception as exc:  # noqa: BLE001
        print(f"WARNING: chkfile dump failed ({exc}); Tier 2 will be skipped for {name}.")
        chk_path = None

    return e_tot, chk_path


def run_qmc_tier2(chk_path, run_dir, name, args):
    """Tier 2: VMC + DMC energies via PyQMC recipes.

    Returns dict with e_vmc, e_vmc_err, e_dmc, e_dmc_err or None on failure.
    """
    print(f"Running Tier 2 (VMC/DMC) for {name}...")
    try:
        from pyqmc.recipes import DMC, VMC, read_mc_output
    except ImportError:
        print("PyQMC not installed. Skipping Tier 2.")
        return None

    vmc_out = run_dir / f"{name}_vmc.hdf5"
    dmc_out = run_dir / f"{name}_dmc.hdf5"

    # --- VMC ---
    # ion_cusp=False: PyQMC 0.8.1's default electron-ion cusp is broken in this
    # environment (non-variational energies); disabling it restores validity on
    # SMALL systems only (H2O-validated) — DMC collapses on 144-e molecules.
    t0 = time.perf_counter()
    print(f"  VMC: nconfig={args.nconfig}, blocks={args.vmc_blocks}, "
          f"steps/block={args.vmc_steps} (ion_cusp=False)")
    VMC(
        str(chk_path),
        str(vmc_out),
        nconfig=args.nconfig,
        jastrow_kws={"ion_cusp": False},
        tstep=0.5,
        nblocks=args.vmc_blocks,
        nsteps_per_block=args.vmc_steps,
        verbose=False,
    )
    vmc_wall = time.perf_counter() - t0
    vmc_warmup = max(1, min(args.vmc_blocks // 5, args.vmc_blocks - 1))
    vmc_data = read_mc_output(str(vmc_out), warmup=vmc_warmup)
    e_vmc, e_vmc_err = _extract_total_energy(vmc_data, "VMC", args.vmc_blocks)
    print(f"  VMC energy: {e_vmc:.6f} +/- {e_vmc_err:.6f} Eh ({vmc_wall:.1f} s)")

    # --- DMC ---
    # Note: DMC runs its OWN internal VMC warmup (vmc_warmup) from a fresh
    # initial_guess walker set; the VMC hdf output is NOT used to seed DMC.
    # VMC and DMC are therefore independent energy estimates.
    t0 = time.perf_counter()
    print(f"  DMC: nconfig={args.nconfig}, blocks={args.dmc_blocks}, "
          f"steps/block={args.dmc_steps}, tstep={args.dmc_tstep} (ion_cusp=False)")
    DMC(
        str(chk_path),
        str(dmc_out),
        nconfig=args.nconfig,
        jastrow_kws={"ion_cusp": False},
        tstep=args.dmc_tstep,
        nblocks=args.dmc_blocks,
        nsteps_per_block=args.dmc_steps,
        vmc_warmup=10,
        branchcut_start=10,
        verbose=False,
    )
    dmc_wall = time.perf_counter() - t0
    dmc_warmup = max(1, min(args.dmc_blocks // 10, args.dmc_blocks - 1))
    dmc_data = read_mc_output(str(dmc_out), warmup=dmc_warmup)
    e_dmc, e_dmc_err = _extract_total_energy(dmc_data, "DMC", args.dmc_blocks)
    print(f"  DMC energy: {e_dmc:.6f} +/- {e_dmc_err:.6f} Eh ({dmc_wall:.1f} s)")

    return {
        "e_vmc": e_vmc,
        "e_vmc_err": e_vmc_err,
        "e_dmc": e_dmc,
        "e_dmc_err": e_dmc_err,
        "vmc_wall_s": vmc_wall,
        "dmc_wall_s": dmc_wall,
    }


def _extract_total_energy(data, label, nblocks):
    """Extract the total energy (+ stderr) from a read_mc_output dict.

    PyQMC 0.8.1 stores the energy accumulator under flattened keys
    ('energytotal', 'energyee', ...) rather than 'energy/total'. Accept both
    spellings for forward compatibility.
    """
    for key in ("energy/total", "energytotal"):
        if key in data:
            return float(data[key]), float(data[key + "_err"])
    raise KeyError(f"No total-energy key found in {label} output "
                   f"(keys: {sorted(data.keys())}); nblocks={nblocks}")


def append_energies_csv(row):
    """Append one candidate row to the Tier-2 energies CSV.

    Uses an exclusive flock so concurrent SLURM array tasks (--array=0-3%2)
    cannot interleave rows or duplicate the header.
    """
    header = [
        "candidate", "smiles", "e_scf_pbe", "e_vmc", "e_vmc_err",
        "e_dmc", "e_dmc_err", "e_corr_vmc_eV", "e_corr_dmc_eV",
        "vmc_wall_s", "dmc_wall_s",
    ]
    with open(ENERGIES_CSV, "a+", newline="") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        fh.seek(0)
        empty = fh.read(1) == ""
        writer = csv.DictWriter(fh, fieldnames=header)
        if empty:
            writer.writeheader()
        writer.writerow(row)
        fh.flush()
        fcntl.flock(fh, fcntl.LOCK_UN)
    print(f"Appended to {ENERGIES_CSV}")


def main():
    args = parse_args()
    QMC_DIR.mkdir(parents=True, exist_ok=True)

    candidates = get_top_5_pareto_candidates()

    if args.array_id is not None:
        if args.array_id < 0 or args.array_id >= len(candidates):
            raise ValueError(f"Invalid array ID: {args.array_id}")
        idx = args.array_id
        cands_to_run = [(idx, candidates[idx])]
    else:
        cands_to_run = list(enumerate(candidates))

    for idx, smiles in cands_to_run:
        name = f"candidate_{idx}"
        run_dir = QMC_DIR / name
        run_dir.mkdir(exist_ok=True)

        print(f"--- Processing {name}: {smiles} ---")
        if args.test_run:
            print("Test run complete.")
            continue

        opt_xyz = run_xtb_optimization(smiles, run_dir, name)
        if not opt_xyz:
            print(f"No geometry for {name}; skipping.")
            continue

        tier1 = generate_trial_wavefunction(opt_xyz, run_dir, name)
        if tier1 is None:
            continue
        e_scf, chk_path = tier1

        row = {
            "candidate": name,
            "smiles": smiles,
            "e_scf_pbe": f"{e_scf:.6f}",
            "e_vmc": "",
            "e_vmc_err": "",
            "e_dmc": "",
            "e_dmc_err": "",
            "e_corr_vmc_eV": "",
            "e_corr_dmc_eV": "",
            "vmc_wall_s": "",
            "dmc_wall_s": "",
        }

        if not args.tier1_only and chk_path is not None:
            qmc = run_qmc_tier2(chk_path, run_dir, name, args)
            if qmc is not None:
                row.update({
                    "e_vmc": f"{qmc['e_vmc']:.6f}",
                    "e_vmc_err": f"{qmc['e_vmc_err']:.6f}",
                    "e_dmc": f"{qmc['e_dmc']:.6f}",
                    "e_dmc_err": f"{qmc['e_dmc_err']:.6f}",
                    "e_corr_vmc_eV": f"{(qmc['e_vmc'] - e_scf) * HARTREE_TO_EV:.4f}",
                    "e_corr_dmc_eV": f"{(qmc['e_dmc'] - e_scf) * HARTREE_TO_EV:.4f}",
                    "vmc_wall_s": f"{qmc['vmc_wall_s']:.1f}",
                    "dmc_wall_s": f"{qmc['dmc_wall_s']:.1f}",
                })
                # Sanity guard: without a correct e-N cusp the DMC local energy
                # diverges near nuclei -> population collapse gives physically
                # impossible values (observed: DMC 157 Eh BELOW SCF on a 144-e
                # candidate). Never let a collapsed value reach the CSV as a
                # result — blank the DMC columns and flag it instead.
                if (not np.isfinite(qmc["e_dmc"]) or
                        qmc["e_dmc"] < e_scf - 20.0):  # NaN or >20 Eh below SCF
                    if not np.isfinite(qmc["e_dmc"]):
                        print(f"  WARNING: {name} DMC non-finite — blanking DMC columns.")
                    else:
                        print(f"  WARNING: {name} DMC={qmc['e_dmc']:.2f} is "
                              f"{e_scf - qmc['e_dmc']:.1f} Eh BELOW SCF — population "
                              f"collapse; DMC columns blanked.")
                    row.update({
                        "e_dmc": "", "e_dmc_err": "",
                        "e_corr_dmc_eV": "", "dmc_wall_s": "",
                    })
        else:
            print("Tier 2 skipped (tier1-only or no chkfile).")

        append_energies_csv(row)
        print(f"Finished {name}.")


if __name__ == "__main__":
    main()
