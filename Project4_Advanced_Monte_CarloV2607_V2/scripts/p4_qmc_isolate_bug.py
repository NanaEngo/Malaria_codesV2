#!/usr/bin/env python3
"""DIAGNOSTIC — not production. See session notes (July 31, 2026).

Isolation test: which factor (functional or basis) breaks PyQMC's
wavefunction evaluation?

Hypothesis: the canonical LiH example (RHF/cc-pVDZ) gives a plausible VMC
energy (-7.39 vs RHF -7.78), while H2O with RKS/def2-SVP gives an impossible
VMC (-100.5 vs SCF -76.27). This script runs H2O under 4 combinations to
isolate the trigger. A healthy VMC must land ABOVE SCF within ~1 Eh.
"""
import time

from pyscf import gto, dft, scf

from pyqmc.recipes import VMC, read_mc_output  # noqa: E402

CONFIGS = [
    ("hf_ccpvdz", "cc-pvdz", "HF"),
    ("hf_def2svp", "def2-svp", "HF"),
    ("rks_ccpvdz", "cc-pvdz", "PBE"),
    ("rks_def2svp", "def2-svp", "PBE"),
]

H2O = "O 0 0 0; H 0 0 0.957; H 0.957 0 0"  # Angstrom


def run_one(label, basis, method):
    mol = gto.Mole()
    mol.atom = H2O
    mol.basis = basis
    mol.build()

    if method == "HF":
        mf = scf.RHF(mol)
    else:
        mf = dft.RKS(mol)
        mf.xc = "pbe"
    mf.chkfile = f"iso_{label}.chk"
    mf.kernel()
    e_scf = mf.e_tot
    print(f"[{label}] {method}/{basis} SCF = {e_scf:.6f} Eh")

    t0 = time.perf_counter()
    VMC(
        f"iso_{label}.chk",
        f"iso_{label}_vmc.hdf5",
        nconfig=100,
        tstep=0.5,
        nblocks=5,
        nsteps_per_block=5,
        verbose=False,
    )
    dt = time.perf_counter() - t0
    vmc = read_mc_output(f"iso_{label}_vmc.hdf5", warmup=1)
    key = "energy/total" if "energy/total" in vmc else "energytotal"
    print(f"[{label}] VMC {key} = {vmc[key]:.4f} +/- {vmc[key + '_err']:.4f} "
          f"(dE = {vmc[key] - e_scf:+.4f} vs SCF) [{dt:.0f}s]")
    return e_scf, vmc[key]


if __name__ == "__main__":
    for label, basis, method in CONFIGS:
        try:
            run_one(label, basis, method)
        except Exception as exc:  # noqa: BLE001
            print(f"[{label}] FAILED: {type(exc).__name__}: {exc}")
