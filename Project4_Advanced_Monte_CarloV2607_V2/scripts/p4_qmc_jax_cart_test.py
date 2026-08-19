#!/usr/bin/env python3
"""DIAGNOSTIC — not production. See session notes (July 31, 2026).

Test PyQMC 0.8.1's JAX backend (freshly-jitted kernels) on H2O.

Context (July 31, 2026): the numba JastrowSpin in this env is deterministically
broken — the default e-N cusp gives VMC -99.6 (vs SCF -76.3), a manually
cusp-satisfying coefficient (-Z*rcut) still gives -19.9 (+56 off), and even the
default e-e Jastrow raises VMC above the bare Slater (-74.5 vs -75.09), which
is impossible variationally. The JAX backend previously failed only with
"Only cartesian basis supported" — this test builds H2O with mol.cart = True
and runs JAX Slater+Jastrow VMC and DMC.
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


def build_h2o_rks(cart=True):
    mol = gto.Mole()
    mol.atom = H2O
    mol.basis = "cc-pvdz"
    mol.cart = cart  # JAX needs cartesian orbitals
    mol.build()
    mf = scf.RKS(mol)
    mf.xc = "pbe"
    mf.chkfile = "jaxcart_h2o.chk"
    mf.kernel()
    return mol, mf


def main():
    mol, mf = build_h2o_rks(cart=True)
    e_scf = mf.e_tot
    rmol, rmf = recover_pyscf("jaxcart_h2o.chk")
    print(f"[SCF] PBE/cc-pvdz(cart) H2O = {e_scf:.6f} Eh (nelec={rmol.nelec}, nao={rmol.nao})")

    print("\n--- JAX Slater-only VMC ---")
    try:
        wf_s, _ = generate_slater(rmol, rmf, jax=True)
        configs = initial_guess(rmol, 200)
        acc = generate_accumulators(rmol, rmf)
        t0 = time.perf_counter()
        vmc(wf_s, configs, tstep=0.5, nblocks=6, nsteps_per_block=10,
            accumulators=acc, hdf_file="jaxcart_slater_vmc.hdf5", verbose=False)
        data = read_mc_output("jaxcart_slater_vmc.hdf5", warmup=1)
        key = "energy/total" if "energy/total" in data else "energytotal"
        e, err = float(data[key]), float(data[key + "_err"])
        print(f"    VMC = {e:.4f} +/- {err:.4f} (dE vs SCF {e - e_scf:+.4f}) "
              f"[{time.perf_counter() - t0:.0f}s]")
    except Exception as exc:  # noqa: BLE001
        print(f"    FAILED: {exc}")

    print("\n--- JAX Slater+Jastrow VMC (default cusp) ---")
    try:
        from pyqmc.wftools import generate_wf
        wf_j, _ = generate_wf(rmol, rmf, jax=True)
        configs = initial_guess(rmol, 200)
        acc = generate_accumulators(rmol, rmf)
        t0 = time.perf_counter()
        vmc(wf_j, configs, tstep=0.5, nblocks=6, nsteps_per_block=10,
            accumulators=acc, hdf_file="jaxcart_j_vmc.hdf5", verbose=False)
        data = read_mc_output("jaxcart_j_vmc.hdf5", warmup=1)
        key = "energy/total" if "energy/total" in data else "energytotal"
        e, err = float(data[key]), float(data[key + "_err"])
        print(f"    VMC = {e:.4f} +/- {err:.4f} (dE vs SCF {e - e_scf:+.4f}) "
              f"[{time.perf_counter() - t0:.0f}s]")
    except Exception as exc:  # noqa: BLE001
        print(f"    FAILED: {exc}")

    print("\n--- JAX Slater+Jastrow DMC (default cusp) ---")
    try:
        from pyqmc.wftools import generate_wf
        wf_j, _ = generate_wf(rmol, rmf, jax=True)
        configs = initial_guess(rmol, 200)
        acc = generate_accumulators(rmol, rmf)
        t0 = time.perf_counter()
        rundmc(wf_j, configs, tstep=0.005, nblocks=8, nsteps_per_block=5,
               accumulators=acc, hdf_file="jaxcart_j_dmc.hdf5", verbose=False,
               vmc_warmup=5, branchcut_start=5)
        data = read_mc_output("jaxcart_j_dmc.hdf5", warmup=1)
        key = "energy/total" if "energy/total" in data else "energytotal"
        e, err = float(data[key]), float(data[key + "_err"])
        print(f"    DMC = {e:.4f} +/- {err:.4f} (dE vs SCF {e - e_scf:+.4f}) "
              f"[{time.perf_counter() - t0:.0f}s]")
    except Exception as exc:  # noqa: BLE001
        print(f"    FAILED: {exc}")

    print("\n=== REFERENCE ===")
    print(f"  SCF PBE: {e_scf:.3f} Eh | Slater-only numba VMC: -75.09 | "
          f"numba DMC(no cusp): -76.50 | FCI/cc-pvdz ~ -76.44")


if __name__ == "__main__":
    main()
