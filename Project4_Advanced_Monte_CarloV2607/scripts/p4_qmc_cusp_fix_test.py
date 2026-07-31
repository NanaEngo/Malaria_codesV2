#!/usr/bin/env python3
"""DIAGNOSTIC — not production. See session notes (July 31, 2026).

Validate the electron-ion cusp coefficient fix for PyQMC 0.8.1.

STATUS (July 31, 2026): HYPOTHESIS REFUTED — do NOT apply a = +Z*rcut.
The empirical result was the OPPOSITE of the hypothesis: a = +Z*rcut gave
VMC -1209.7 (walkers collapse into nuclei), while a = -Z*rcut gave LOW
variance (cusp SATISFIED) but still a wrong energy (-19.88, +56 Eh off).
The numba kernel's cusp slope is opposite to the documented formula, and
even a cusp-satisfying coefficient cannot fix the energy -> the JastrowSpin
combination/summation path is broken in this env (see p4_qmc_kernel_check.py:
individual basis kernels are mathematically correct). Kept as diagnostic
reference only.

Original hypothesis (now refuted): the CutoffCuspFunction
b(r) = -p(z)/(1 + gamma*p(z)) + 1/(3+gamma), z = r/rcut, has b'(0) = -1/rcut,
so the cusp condition u'(0) = -Z requires a = +Z*rcut; generate_jastrow sets
a = Z (missing the x rcut factor), under-correcting the cusp ~7.5x and leaving
infinite-variance local energies near nuclei.

Tests on H2O (PBE/cc-pvdz, mirroring bisect geometry):
  1. default generate_jastrow (a = +Z):       broken VMC (~-99.6, non-var)
  2. a = +Z*rcut (hypothesised fix):           VMC -1209.7 (collapse) — REFUTED
  3. a = -Z*rcut (sign control):               VMC -19.88, LOW variance — cusp
                                               satisfied but energy still +56 Eh off
  4. DMC with a = +Z*rcut:                     garbage (collapse)
"""
import time

import numpy as np
from pyscf import gto, scf
from pyqmc.pyscftools import recover_pyscf
from pyqmc.wftools import generate_slater, generate_jastrow
from pyqmc.wf.multiplywf import MultiplyWF
from pyqmc.method.mc import initial_guess, vmc
from pyqmc.method.dmc import rundmc
from pyqmc.recipes import generate_accumulators, read_mc_output

H2O = "O 0 0 0; H 0 0 0.957; H 0.957 0 0"
RCUT_DEFAULT = 7.5  # non-periodic default in default_jastrow_basis


def build_h2o_rks():
    mol = gto.Mole()
    mol.atom = H2O
    mol.basis = "cc-pvdz"
    mol.build()
    mf = scf.RKS(mol)
    mf.xc = "pbe"
    mf.chkfile = "fix_h2o.chk"
    mf.kernel()
    return mol, mf


def make_wf(rmol, rmf, mode):
    """Build Slater x Jastrow with a chosen acoeff convention for the cusp.

    mode: "default" | "plus_rcut" | "minus_rcut"
    """
    slater, _ = generate_slater(rmol, rmf)
    jastrow, _ = generate_jastrow(rmol, ion_cusp=None)  # default: cusp on
    charges = rmol.atom_charges()
    # acoeff shape: (nelec, na, nion); index [:, 0, :] is the cusp function
    if mode == "default":
        pass  # generate_jastrow already set acoeff[:,0,:] = +Z
    elif mode == "plus_rcut":
        jastrow.parameters["acoeff"][:, 0, :] = charges[:, None] * RCUT_DEFAULT
    elif mode == "minus_rcut":
        jastrow.parameters["acoeff"][:, 0, :] = -charges[:, None] * RCUT_DEFAULT
    else:
        raise ValueError(mode)
    cusp = np.asarray(jastrow.parameters["acoeff"][:, 0, :])
    print(f"    acoeff[:,0,:] = {cusp[0].tolist()}")
    return MultiplyWF(slater, jastrow)


def run_vmc(wf, mol, mf, out, nblocks=6, nsteps=10, nconfig=200):
    configs = initial_guess(mol, nconfig)
    acc = generate_accumulators(mol, mf)
    t0 = time.perf_counter()
    vmc(wf, configs, tstep=0.5, nblocks=nblocks, nsteps_per_block=nsteps,
        accumulators=acc, hdf_file=out, verbose=False)
    wall = time.perf_counter() - t0
    data = read_mc_output(out, warmup=1)
    key = "energy/total" if "energy/total" in data else "energytotal"
    return float(data[key]), float(data[key + "_err"]), wall


def run_dmc(wf, mol, mf, out, nconfig=200, nblocks=8, nsteps=5):
    configs = initial_guess(mol, nconfig)
    acc = generate_accumulators(mol, mf)
    t0 = time.perf_counter()
    rundmc(wf, configs, tstep=0.005, nblocks=nblocks, nsteps_per_block=nsteps,
           accumulators=acc, hdf_file=out, verbose=False,
           vmc_warmup=5, branchcut_start=5)
    wall = time.perf_counter() - t0
    data = read_mc_output(out, warmup=1)
    key = "energy/total" if "energy/total" in data else "energytotal"
    return float(data[key]), float(data[key + "_err"]), wall


def main():
    mol, mf = build_h2o_rks()
    e_scf = mf.e_tot
    rmol, rmf = recover_pyscf("fix_h2o.chk")
    print(f"[SCF] PBE/cc-pvdz H2O = {e_scf:.6f} Eh (nelec={rmol.nelec})")

    print("\n--- 1. default cusp (a = +Z) ---")
    wf1 = make_wf(rmol, rmf, "default")
    e1, err1, w1 = run_vmc(wf1, rmol, rmf, "fix_1_default.hdf5")
    print(f"    VMC = {e1:.4f} +/- {err1:.4f} Eh  (dE vs SCF {e1 - e_scf:+.4f}) [{w1:.0f}s]")

    print("\n--- 2. fixed cusp (a = +Z*rcut) ---")
    wf2 = make_wf(rmol, rmf, "plus_rcut")
    e2, err2, w2 = run_vmc(wf2, rmol, rmf, "fix_2_plus.hdf5")
    print(f"    VMC = {e2:.4f} +/- {err2:.4f} Eh  (dE vs SCF {e2 - e_scf:+.4f}) [{w2:.0f}s]")

    print("\n--- 3. sign control (a = -Z*rcut) ---")
    wf3 = make_wf(rmol, rmf, "minus_rcut")
    e3, err3, w3 = run_vmc(wf3, rmol, rmf, "fix_3_minus.hdf5")
    print(f"    VMC = {e3:.4f} +/- {err3:.4f} Eh  (dE vs SCF {e3 - e_scf:+.4f}) [{w3:.0f}s]")

    print("\n--- 4. DMC with fixed cusp (a = +Z*rcut) ---")
    e4, err4, w4 = run_dmc(wf2, rmol, rmf, "fix_4_dmc.hdf5")
    print(f"    DMC = {e4:.4f} +/- {err4:.4f} Eh  (dE vs SCF {e4 - e_scf:+.4f}) [{w4:.0f}s]")

    print("\n=== VERDICT ===")
    print(f"  default(+Z):     VMC {e1:+.3f} (expect garbage, dE << -1)")
    print(f"  fixed(+Z*rcut):  VMC {e2:+.3f}, DMC {e4:+.3f} (expect dE ~ +1.2 VMC, "
          f"DMC near/above SCF, low stderr)")
    print(f"  sign(-Z*rcut):   VMC {e3:+.3f} (expect garbage)")
    print(f"  SCF reference: {e_scf:.3f} Eh")


if __name__ == "__main__":
    main()
