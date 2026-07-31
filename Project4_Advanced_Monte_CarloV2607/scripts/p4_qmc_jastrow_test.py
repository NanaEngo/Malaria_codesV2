#!/usr/bin/env python3
"""DIAGNOSTIC — not production. See session notes (July 31, 2026).

Isolate the broken Jastrow component in PyQMC 0.8.1 on H2O.

Established: Slater-only VMC = -75.09 (correct: PBE orbitals, HF expectation).
Slater+default-Jastrow VMC = -102.85 (broken, -26.5 Eh collapse).

Tests:
A) jastrow_kws={'ion_cusp': False}  — no electron-ion cusp terms
B) jastrow_kws={'ion_cusp': True}   — explicit ion cusp (should equal default)
C) Full Jastrow but with a-coeffs zeroed (ion part off) and b-coeffs zeroed
   (e-e part off) -> effectively no Jastrow; expect ~ -75.09
D) Default Jastrow with zeroed bcoeff only (ion cusp on, e-e off)
E) Default Jastrow with zeroed acoeff only (ion off, e-e on)
"""
import time

from pyscf import gto, scf
from pyqmc.pyscftools import recover_pyscf
from pyqmc.wftools import generate_wf
from pyqmc.method.mc import initial_guess, vmc
from pyqmc.recipes import generate_accumulators, read_mc_output

H2O = "O 0 0 0; H 0 0 0.957; H 0.957 0 0"


def build_h2o_rks():
    mol = gto.Mole()
    mol.atom = H2O
    mol.basis = "cc-pvdz"
    mol.build()
    mf = scf.RKS(mol)
    mf.xc = "pbe"
    mf.chkfile = "jast_h2o.chk"
    mf.kernel()
    return mol, mf


def vmc_energy(wf, mol, mf, out, nblocks=5, nsteps=10, nconfig=200):
    configs = initial_guess(mol, nconfig)
    acc = generate_accumulators(mol, mf)
    vmc(wf, configs, tstep=0.5, nblocks=nblocks, nsteps_per_block=nsteps,
        accumulators=acc, hdf_file=out, verbose=False)
    data = read_mc_output(out, warmup=1)
    key = "energy/total" if "energy/total" in data else "energytotal"
    return data[key], data[key + "_err"]


def zero_params(wf, a=True, b=True):
    """Zero out Jastrow coefficient arrays (in place)."""
    import numpy as np
    p = wf.parameters
    if a and "acoeff" in p:
        p["acoeff"] = p["acoeff"] * 0.0
    if b and "bcoeff" in p:
        p["bcoeff"] = p["bcoeff"] * 0.0
    return wf


def main():
    mol, mf = build_h2o_rks()
    e_scf = mf.e_tot
    rmol, rmf = recover_pyscf("jast_h2o.chk")
    print(f"[SCF] PBE/cc-pvdz H2O = {e_scf:.6f} Eh")

    tests = {
        "A ion_cusp=False": dict(jastrow_kws={"ion_cusp": False}),
        "B ion_cusp=True": dict(jastrow_kws={"ion_cusp": True}),
    }

    # Build once for each config since wf objects are stateful
    for label, kwargs in tests.items():
        t0 = time.perf_counter()
        wf, _ = generate_wf(rmol, rmf, **kwargs)
        e, eerr = vmc_energy(wf, rmol, rmf, f"jast_{label.split()[0]}.hdf5")
        print(f"[{label}] VMC = {e:.4f} +/- {eerr:.4f} "
              f"(dE vs SCF = {e - e_scf:+.4f}) [{time.perf_counter() - t0:.0f}s]")

    # C: full Jastrow, both a and b zeroed
    wf, _ = generate_wf(rmol, rmf)
    zero_params(wf, a=True, b=True)
    e, eerr = vmc_energy(wf, rmol, rmf, "jast_C_zero_both.hdf5")
    print(f"[C both zeroed] VMC = {e:.4f} +/- {eerr:.4f} "
          f"(dE vs SCF = {e - e_scf:+.4f})")

    # D: ion cusp on, e-e off
    wf, _ = generate_wf(rmol, rmf)
    zero_params(wf, a=False, b=True)
    e, eerr = vmc_energy(wf, rmol, rmf, "jast_D_a_only.hdf5")
    print(f"[D a only] VMC = {e:.4f} +/- {eerr:.4f} "
          f"(dE vs SCF = {e - e_scf:+.4f})")

    # E: ion off, e-e on
    wf, _ = generate_wf(rmol, rmf)
    zero_params(wf, a=True, b=False)
    e, eerr = vmc_energy(wf, rmol, rmf, "jast_E_b_only.hdf5")
    print(f"[E b only] VMC = {e:.4f} +/- {eerr:.4f} "
          f"(dE vs SCF = {e - e_scf:+.4f})")


if __name__ == "__main__":
    main()
