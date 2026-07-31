#!/usr/bin/env python3
"""Minimal PyQMC 0.8.1 sanity test on H2O.

Isolates whether the garbage energies seen for candidate_0 are due to a
PyQMC<->PySCF 2.14 incompatibility (independent of our pipeline) or something
in our chkfile/mol handling. Uses the STANDARD PyQMC workflow: pyscf SCF with
mf.chkfile set, then pyqmc.recipes.VMC/DMC + read_mc_output.
"""
import time

from pyscf import gto, dft

# --- Build H2O and save a PySCF chkfile the standard way ---
mol = gto.Mole()
mol.atom = "O 0 0 0; H 0 0 0.957; H 0.957 0 0"  # Angstrom, pyscf converts
mol.basis = "def2-svp"
mol.build()

mf = dft.RKS(mol)
mf.xc = "pbe"
mf.chkfile = "h2o_pbe.chk"
mf.kernel()
print(f"H2O PBE e_tot = {mf.e_tot:.6f} Eh (reference ~ -76.4)")

# --- Standard PyQMC VMC + DMC ---
from pyqmc.recipes import VMC, DMC, read_mc_output  # noqa: E402

t0 = time.perf_counter()
VMC(
    "h2o_pbe.chk",
    "h2o_vmc.hdf5",
    nconfig=100,
    tstep=0.5,
    nblocks=5,
    nsteps_per_block=5,
    verbose=False,
)
print(f"VMC wall {time.perf_counter() - t0:.1f}s")
vmc = read_mc_output("h2o_vmc.hdf5", warmup=1)
key = "energy/total" if "energy/total" in vmc else "energytotal"
print(f"VMC {key} = {vmc[key]:.4f} +/- {vmc[key+'_err']:.4f} Eh")

t0 = time.perf_counter()
DMC(
    "h2o_pbe.chk",
    "h2o_dmc.hdf5",
    nconfig=100,
    tstep=0.005,
    nblocks=10,
    nsteps_per_block=5,
    vmc_warmup=10,
    branchcut_start=10,
    verbose=False,
)
print(f"DMC wall {time.perf_counter() - t0:.1f}s")
dmc = read_mc_output("h2o_dmc.hdf5", warmup=1)
key = "energy/total" if "energy/total" in dmc else "energytotal"
print(f"DMC {key} = {dmc[key]:.4f} +/- {dmc[key+'_err']:.4f} Eh")
