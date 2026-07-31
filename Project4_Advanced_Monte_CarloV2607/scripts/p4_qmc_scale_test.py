#!/usr/bin/env python3
"""DIAGNOSTIC — not production. See session notes (July 31, 2026).

P4 — QMC scaling diagnosis on candidate_0 (C12H17NO3, 144 e-).

Context (July 31, 2026): PyQMC 0.8.1 with jastrow_kws={'ion_cusp': False} is
physically valid on H2O (DMC -76.50 vs SCF -76.33), but the candidate_0 smoke
run at nconfig=100 produced garbage (DMC -1021 vs SCF -864, stderr 39 Eh) —
either too few walkers for a 144-e- system (population collapse) or a residual
Jastrow pathology in large systems.

This script runs two DMC tests on candidate_0 with nconfig=300:
  S: Slater-only DMC (bare PBE-orbitals determinant — no Jastrow at all)
  J: Slater+Jastrow DMC with ion_cusp=False (the H2O-validated config)
and prints per-block energies so we can see whether the mean drifts (population
collapse) or is stable. A Slater-only DMC that lands within a few Eh of SCF
(above it — fixed-node DMC from an uncorrelated trial should be near, not
far below, the VKS energy) is the decisive evidence.
"""

import os
import sys
import time

HARTREE_TO_EV = 27.211386245988


def main():
    chk = os.environ.get("CHK",
                         "../results/qmc/candidate_0/candidate_0_pbe.chk")
    if not os.path.exists(chk):
        sys.exit(f"ERROR: {chk} not found — run Tier 1 first")

    from pyqmc.pyscftools import recover_pyscf
    from pyqmc.wftools import generate_slater, generate_wf
    from pyqmc.method.dmc import rundmc
    from pyqmc.method.mc import initial_guess
    from pyqmc.recipes import generate_accumulators, read_mc_output

    nconfig = int(os.environ.get("NCFG", "300"))
    tstep = float(os.environ.get("TSTEP", "0.005"))
    nblocks = int(os.environ.get("NBLK", "6"))
    nsteps = int(os.environ.get("NSTEPS", "5"))

    mol, mf = recover_pyscf(chk)
    print(f"mol: nelec={mol.nelec} nao={mol.nao} nuc_charges={mol.atom_charges()}")
    print(f"SCF PBE energy (chkfile): {mf.e_tot:.6f} Eh")
    print(f"settings: nconfig={nconfig} tstep={tstep} nblocks={nblocks} nsteps={nsteps}")

    results = {}

    # --- S: Slater-only DMC ---
    print("\n=== S: Slater-only DMC ===")
    try:
        wf, _to_opt = generate_slater(mol, mf)
        configs = initial_guess(mol, nconfig)
        acc = generate_accumulators(mol, mf)
        out = "scale_S_slater.hdf5"
        for f in ("scale_S_slater.hdf5",):
            if os.path.exists(f):
                os.remove(f)
        t0 = time.perf_counter()
        rundmc(wf, configs, tstep=tstep, nblocks=nblocks, nsteps_per_block=nsteps,
               accumulators=acc, hdf_file=out, verbose=False,
               vmc_warmup=5, branchcut_start=5)
        wall = time.perf_counter() - t0
        data = read_mc_output(out, warmup=1)
        key = "energy/total" if "energy/total" in data else "energytotal"
        e, err = float(data[key]), float(data[key + "_err"])
        results["S_slater"] = (e, err, wall)
        print(f"  S Slater-only DMC: {e:.4f} +/- {err:.4f} Eh  (dE vs SCF "
              f"{(e - mf.e_tot) * HARTREE_TO_EV:+.1f} eV, {wall:.0f} s)")
    except Exception as exc:  # noqa: BLE001
        print(f"  S FAILED: {exc}")

    # --- J: Jastrow (ion_cusp=False) DMC ---
    print("\n=== J: Slater+Jastrow DMC (ion_cusp=False) ===")
    try:
        wf, _to_opt = generate_wf(mol, mf, jastrow_kws={"ion_cusp": False})
        configs = initial_guess(mol, nconfig)
        acc = generate_accumulators(mol, mf)
        out = "scale_J_jastrow.hdf5"
        if os.path.exists(out):
            os.remove(out)
        t0 = time.perf_counter()
        rundmc(wf, configs, tstep=tstep, nblocks=nblocks, nsteps_per_block=nsteps,
               accumulators=acc, hdf_file=out, verbose=False,
               vmc_warmup=5, branchcut_start=5)
        wall = time.perf_counter() - t0
        data = read_mc_output(out, warmup=1)
        key = "energy/total" if "energy/total" in data else "energytotal"
        e, err = float(data[key]), float(data[key + "_err"])
        results["J_jastrow"] = (e, err, wall)
        print(f"  J Jastrow DMC: {e:.4f} +/- {err:.4f} Eh  (dE vs SCF "
              f"{(e - mf.e_tot) * HARTREE_TO_EV:+.1f} eV, {wall:.0f} s)")
    except Exception as exc:  # noqa: BLE001
        print(f"  J FAILED: {exc}")

    print("\n=== VERDICT ===")
    for name, (e, err, wall) in results.items():
        print(f"  {name}: E={e:.4f} +/- {err:.4f} Eh, dE vs SCF "
              f"{(e - mf.e_tot) * HARTREE_TO_EV:+.1f} eV")


if __name__ == "__main__":
    main()
