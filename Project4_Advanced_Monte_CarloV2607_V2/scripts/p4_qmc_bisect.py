#!/usr/bin/env python3
"""DIAGNOSTIC — not production. See session notes (July 31, 2026).

Bisect PyQMC's broken wavefunction evaluation on H2O.

Established: VMC gives -100.5 vs SCF -76.27 (variational violation — broken
wavefunction evaluation in PyQMC 0.8.1 in this env). Tests:

A) Slater-only VMC (no Jastrow). A bare Slater of the SCF orbitals MUST
   reproduce the SCF energy. If it does, the Jastrow is the culprit.
B) Full Slater-Jastrow VMC with explicit eval_gto_precision=1e-8 (tests the
   orbital-rcut truncation hypothesis: _estimate_rcut default 0.01 may
   truncate orbitals too aggressively).
C) Recovered-mf fidelity: RHF energy_elec() from the chkfile-recovered mf
   should reproduce the SCF energy.
"""
import time

from pyscf import gto, scf
from pyqmc.pyscftools import recover_pyscf
from pyqmc.wftools import generate_slater, generate_wf
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
    mf.chkfile = "bisect_h2o.chk"
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


def main():
    mol, mf = build_h2o_rks()
    e_scf = mf.e_tot
    print(f"[SCF] PBE/cc-pvdz H2O = {e_scf:.6f} Eh")

    # --- C: recovered mf fidelity ---
    rmol, rmf = recover_pyscf("bisect_h2o.chk")
    e_elec, e_coul = rmf.energy_elec()
    print(f"[C] recovered mf energy_elec = {e_elec + e_coul:.6f} Eh "
          f"(dE vs SCF = {e_elec + e_coul - e_scf:+.6f})")

    # --- A: Slater-only ---
    t0 = time.perf_counter()
    wf_s, to_opt_s = generate_slater(rmol, rmf)
    e_vmc_s, e_err_s = vmc_energy(wf_s, rmol, rmf, "h2o_slater_vmc.hdf5")
    print(f"[A] Slater-only VMC = {e_vmc_s:.4f} +/- {e_err_s:.4f} "
          f"(dE vs SCF = {e_vmc_s - e_scf:+.4f}) [{time.perf_counter() - t0:.0f}s]")

    # --- B: full Slater-Jastrow with tight eval_gto_precision ---
    t0 = time.perf_counter()
    wf_f, to_opt_f = generate_wf(rmol, rmf,
                                 slater_kws={"eval_gto_precision": 1e-8})
    e_vmc_f, e_err_f = vmc_energy(wf_f, rmol, rmf, "h2o_full_vmc.hdf5")
    print(f"[B] Slater+Jastrow (prec=1e-8) VMC = {e_vmc_f:.4f} +/- {e_err_f:.4f} "
          f"(dE vs SCF = {e_vmc_f - e_scf:+.4f}) [{time.perf_counter() - t0:.0f}s]")


if __name__ == "__main__":
    main()
