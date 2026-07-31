#!/usr/bin/env python3
"""DIAGNOSTIC — not production. See session notes (July 31, 2026).

Test PyQMC 0.8.1 workarounds on H2O (PBE/cc-pvdz, chkfile auto-save).

Established: default Jastrow (ion cusp ON, acoeff=atom_charges) gives broken
VMC (-102 vs SCF -76.3); Slater-only (-75.09) and ion_cusp=False (-74.5) are
valid. Tests:
F) generate_wf(jax=True) VMC  — JAX backend avoids numba kernels entirely
G) DMC with ion_cusp=False (non-JAX)
H) DMC with jax=True
I) Slater-only DMC (baseline)
"""
import time

from pyscf import gto, scf
from pyqmc.pyscftools import recover_pyscf
from pyqmc.wftools import generate_wf, generate_slater
from pyqmc.method.mc import initial_guess, vmc
from pyqmc.method.dmc import rundmc
from pyqmc.recipes import generate_accumulators, read_mc_output

H2O = "O 0 0 0; H 0 0 0.957; H 0.957 0 0"


def build_h2o_rks():
    mol = gto.Mole()
    mol.atom = H2O
    mol.basis = "cc-pvdz"
    mol.build()
    mf = scf.RKS(mol)
    mf.xc = "pbe"
    mf.chkfile = "jax_h2o.chk"
    mf.kernel()
    return mol, mf


def run_vmc(wf, mol, mf, out):
    configs = initial_guess(mol, 200)
    acc = generate_accumulators(mol, mf)
    vmc(wf, configs, tstep=0.5, nblocks=5, nsteps_per_block=10,
        accumulators=acc, hdf_file=out, verbose=False)
    data = read_mc_output(out, warmup=1)
    key = "energy/total" if "energy/total" in data else "energytotal"
    return data[key], data[key + "_err"]


def run_dmc(wf, mol, mf, out):
    configs = initial_guess(mol, 200)
    acc = generate_accumulators(mol, mf)
    rundmc(wf, configs, tstep=0.005, nblocks=10, nsteps_per_block=5,
           vmc_warmup=5, branchcut_start=5, accumulators=acc,
           hdf_file=out, verbose=False)
    data = read_mc_output(out, warmup=1)
    key = "energy/total" if "energy/total" in data else "energytotal"
    return data[key], data[key + "_err"]


def main():
    mol, mf = build_h2o_rks()
    e_scf = mf.e_tot
    rmol, rmf = recover_pyscf("jax_h2o.chk")
    print(f"[SCF] PBE/cc-pvdz H2O = {e_scf:.6f} Eh")

    # F: JAX Slater-Jastrow VMC
    try:
        t0 = time.perf_counter()
        wf, _ = generate_wf(rmol, rmf, jax=True)
        e, eerr = run_vmc(wf, rmol, rmf, "jax_F_vmc.hdf5")
        print(f"[F jax=True VMC] {e:.4f} +/- {eerr:.4f} "
              f"(dE vs SCF = {e - e_scf:+.4f}) [{time.perf_counter() - t0:.0f}s]")
    except Exception as exc:  # noqa: BLE001
        print(f"[F jax=True VMC] FAILED: {type(exc).__name__}: {exc}")

    # G: DMC ion_cusp=False
    try:
        t0 = time.perf_counter()
        wf, _ = generate_wf(rmol, rmf, jastrow_kws={"ion_cusp": False})
        e, eerr = run_dmc(wf, rmol, rmf, "jax_G_dmc.hdf5")
        print(f"[G DMC ion_cusp=False] {e:.4f} +/- {eerr:.4f} "
              f"(dE vs SCF = {e - e_scf:+.4f}) [{time.perf_counter() - t0:.0f}s]")
    except Exception as exc:  # noqa: BLE001
        print(f"[G DMC ion_cusp=False] FAILED: {type(exc).__name__}: {exc}")

    # H: DMC jax=True
    try:
        t0 = time.perf_counter()
        wf, _ = generate_wf(rmol, rmf, jax=True)
        e, eerr = run_dmc(wf, rmol, rmf, "jax_H_dmc.hdf5")
        print(f"[H jax=True DMC] {e:.4f} +/- {eerr:.4f} "
              f"(dE vs SCF = {e - e_scf:+.4f}) [{time.perf_counter() - t0:.0f}s]")
    except Exception as exc:  # noqa: BLE001
        print(f"[H jax=True DMC] FAILED: {type(exc).__name__}: {exc}")

    # I: Slater-only DMC baseline
    try:
        t0 = time.perf_counter()
        wf, _ = generate_slater(rmol, rmf)
        e, eerr = run_dmc(wf, rmol, rmf, "jax_I_dmc.hdf5")
        print(f"[I Slater-only DMC] {e:.4f} +/- {eerr:.4f} "
              f"(dE vs SCF = {e - e_scf:+.4f}) [{time.perf_counter() - t0:.0f}s]")
    except Exception as exc:  # noqa: BLE001
        print(f"[I Slater-only DMC] FAILED: {type(exc).__name__}: {exc}")


if __name__ == "__main__":
    main()
