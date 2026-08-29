#!/usr/bin/env python3
"""DIAGNOSTIC — not production. See session notes (July 31, 2026).

Finite-difference audit of PyQMC 0.8.1's CutoffCuspFunction kernel.

Goal: isolate the exact broken kernel. The VMC evidence (deterministic -23 Eh
at default cusp; cusp-satisfying coefficient -Z*rcut still +56 Eh off with LOW
variance) is consistent with a sign/formula error in the ONE-BODY cusp
gradient/laplacian kernels (value right -> density right -> low variance;
derivatives wrong -> kinetic energy systematically wrong).

Checks:
  1. mol._atom count vs acoeff[:,0,:] shape (the fix test printed [8,8] for a
     3-atom H2O — expect [8,1,1]; a mismatch would be a reconstruction bug).
  2. Numeric vs analytic radial gradient d/dr of the cusp function at several r
     (does the implemented slope have the documented sign -1/rcut?).
  3. Numeric vs analytic 3D laplacian  (db2/dr2 + 2/r db/dr).
"""
import sys

import numpy as np
from pyscf import gto, scf
from pyqmc.pyscftools import recover_pyscf
from pyqmc.wftools import generate_jastrow

H2O = "O 0 0 0; H 0 0 0.957; H 0.957 0 0"


def build_h2o_rks():
    mol = gto.Mole()
    mol.atom = H2O
    mol.basis = "cc-pvdz"
    mol.build()
    mf = scf.RKS(mol)
    mf.xc = "pbe"
    mf.chkfile = "kern_h2o.chk"
    mf.kernel()
    return mol, mf


def fd_check(basis_fn, r):
    """Compare analytic gradient_laplacian to central finite differences."""
    h = 1e-4
    # central differences of value() along the radial direction
    def val(rr):
        rvec = np.array([rr, 0.0, 0.0])
        rvec = np.broadcast_to(rvec, (1, 3)).astype(float)
        rr = np.array([rr])
        return float(np.asarray(basis_fn.value(rvec, rr))[0])

    dv = (val(r + h) - val(r - h)) / (2 * h)
    d2v = (val(r + h) - 2 * val(r) + val(r - h)) / h ** 2
    lap_num = d2v + 2.0 * dv / r  # spherically symmetric 3D laplacian

    rvec = np.broadcast_to(np.array([r, 0.0, 0.0]), (1, 3)).astype(float)
    rr = np.array([r])
    grad, lap = basis_fn.gradient_laplacian(rvec, rr)
    grad_x = float(np.asarray(grad)[0, 0])  # radial component along x
    lap_an = float(np.asarray(lap)[0])
    return dv, grad_x, d2v, lap_num, lap_an


def main():
    mol, mf = build_h2o_rks()
    rmol, rmf = recover_pyscf("kern_h2o.chk")
    print(f"[mol] _atom count = {len(rmol._atom)} (expect 3: O,H,H)")
    print(f"[mol] charges = {rmol.atom_charges()}")

    jastrow, _ = generate_jastrow(rmol, ion_cusp=None)
    acoeff = np.asarray(jastrow.parameters["acoeff"])
    # acoeff layout is (natm, na, nspin) — NOT (nelec, na, nion)
    print(f"[acoeff] shape = {acoeff.shape} (natm, na, nspin)")
    print(f"[acoeff] cusp slice [:,0,:] = {acoeff[:, 0, :].tolist()}")
    print(f"[acoeff] spin dim = {acoeff.shape[-1]} (nspin=2); "
          f"natm dim = {acoeff.shape[0]} vs natom = {len(rmol._atom)}")

    # a_basis is a CutoffFunc3dEvaluator wrapping the list of func3d objects
    abasis = jastrow.a_basis if hasattr(jastrow, "a_basis") else None
    print(f"[basis] a_basis present: {abasis is not None}")
    if abasis is None or not hasattr(abasis, "basis_functions"):
        print(f"[basis] jastrow attrs: {[a for a in dir(jastrow) if not a.startswith('_')][:30]}")
        sys.exit("no a_basis.basis_functions; cannot run kernel audit")

    cusp = abasis.basis_functions[0]
    rc = float(np.asarray(cusp.parameters["rcut"]).ravel()[0])
    print(f"[basis] a-basis[0] fn: {type(cusp).__name__}, rcut = {rc}, nbas = {abasis.nbas}")

    print("\n=== cusp kernel: analytic vs finite-difference (r in Bohr) ===")
    print(f"{'r':>6} {'fd_d/dr':>12} {'an_d/dr':>12} {'fd_lap':>12} {'an_lap':>12} {'match?':>8}")
    for r in (0.05, 0.1, 0.3, 0.7, 1.5, 3.0, 5.0):
        dv, gx, d2v, lap_num, lap_an = fd_check(cusp, r)
        ok = "OK" if abs(gx - dv) < 1e-3 and abs(lap_an - lap_num) < 1e-2 else "DIFF"
        print(f"{r:6.2f} {dv:12.5f} {gx:12.5f} {lap_num:12.5f} {lap_an:12.5f} {ok:>8}")

    # Same for the first b-basis (e-e cusp) function
    bbasis = jastrow.b_basis if hasattr(jastrow, "b_basis") else None
    if bbasis is not None and hasattr(bbasis, "basis_functions"):
        print("\n=== e-e cusp (b_basis[0]) kernel check ===")
        for r in (0.05, 0.1, 0.5):
            dv, gx, d2v, lap_num, lap_an = fd_check(bbasis.basis_functions[0], r)
            ok = "OK" if abs(gx - dv) < 1e-3 and abs(lap_an - lap_num) < 1e-2 else "DIFF"
            print(f"{r:6.2f} {dv:12.5f} {gx:12.5f} {lap_num:12.5f} {lap_an:12.5f} {ok:>8}")


if __name__ == "__main__":
    main()
