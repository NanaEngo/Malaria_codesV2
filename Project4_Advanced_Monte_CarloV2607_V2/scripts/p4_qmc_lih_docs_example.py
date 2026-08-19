#!/usr/bin/env python3
"""DIAGNOSTIC — not production. See session notes (July 31, 2026).

Canonical PyQMC documented example: LiH with RHF/cc-pVDZ.

From the PyQMC docs (recipes tutorial). Expected VMC energy ~ -7.9 Eh
(RHF/cc-pVDZ LiH E0 = -7.986 Eh). If this produces ~ -7.9, the library
works in this environment and the pipeline's chkfile/mol path is the bug.
If it produces garbage (like -20 or -100), the library itself is broken
with the installed dependency stack.

SESSION OUTCOME (July 31, 2026): this canonical example gave VMC -7.39 vs
RHF -7.78 — a trial WORSE than the bare Slater determinant (impossible for a
valid Jastrow), confirming the JastrowSpin breakage in this env rather than a
pipeline/chkfile bug. Retained as diagnostic reference only.
"""
import time

from pyscf import gto, scf

# The exact documented example (unit='bohr' as in the docs)
mol = gto.M(atom="Li 0 0 0; H 0 0 1.6", basis="cc-pvdz", unit="bohr")
mf = scf.RHF(mol)
mf.chkfile = "lih.chk"
mf.kernel()
print(f"LiH RHF/cc-pVDZ e_tot = {mf.e_tot:.6f} Eh (expect ~ -7.986)")

from pyqmc.recipes import VMC, read_mc_output  # noqa: E402

t0 = time.perf_counter()
VMC(
    "lih.chk",
    "lih_vmc.hdf5",
    nconfig=1000,
    nblocks=25,
    nsteps_per_block=25,
    verbose=False,
)
print(f"VMC wall {time.perf_counter() - t0:.1f}s")
vmc = read_mc_output("lih_vmc.hdf5", warmup=5)
key = "energy/total" if "energy/total" in vmc else "energytotal"
print(f"VMC {key} = {vmc[key]:.4f} +/- {vmc[key+'_err']:.4f} Eh  (expect ~ -7.9)")
