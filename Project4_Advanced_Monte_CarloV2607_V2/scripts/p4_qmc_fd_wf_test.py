#!/usr/bin/env python3
"""DIAGNOSTIC — not production. See session notes (July 31, 2026).

Full-wavefunction finite-difference audit for PyQMC 0.8.1.

STATUS (July 31, 2026): INCONCLUSIVE / KNOWN-ARTIFACT — do NOT trust the
verdict output. The Slater-only control (proven CORRECT by VMC: Slater-only
VMC = -75.09 exactly reproduces the HF-style expectation of the PBE orbitals)
reports a large mismatch in this harness, so the finite-difference harness
itself has a shape/layout bug (the gradient_laplacian return layout differs
from what the branch logic assumes). The authoritative evidence for the
JastrowSpin breakage is the direct VMC/DMC energy reproduction in the bisect,
jastrow-isolation and cusp-fix tests (default e-N cusp VMC = -99.58 vs SCF
-76.33; cusp-satisfying acoeff = -Z*rcut still +56 Eh off; DMC without cusp
collapses on 144-e molecules). Retained only as a diagnostic reference.
"""
import numpy as np
from pyscf import gto, scf
from pyqmc.pyscftools import recover_pyscf
from pyqmc.wftools import generate_slater, generate_wf
from pyqmc.method.mc import initial_guess
from pyqmc.configurations.coord import OpenConfigs

H2O = "O 0 0 0; H 0 0 0.957; H 0.957 0 0"
EIDX = 0
AXIS = 0
H = 1e-3


def build_h2o_rks():
    mol = gto.Mole()
    mol.atom = H2O
    mol.basis = "cc-pvdz"
    mol.build()
    mf = scf.RKS(mol)
    mf.xc = "pbe"
    mf.chkfile = "fdwf_h2o.chk"
    mf.kernel()
    return mol, mf


def _flat_value(v):
    """Normalize wf.value() output to (nconfig,) — PyQMC returns per-spin rows
    (2, nconfig) for some wavefunctions; take the product of spin blocks."""
    v = np.asarray(v)
    if v.ndim == 2 and v.shape[0] in (1, 2):
        return v.prod(axis=0)
    return v.ravel()


def check_wf(label, wf, rmol):
    try:
        configs = initial_guess(rmol, 64)
        wf.recompute(configs)

        # analytic — gradient shape varies (nconfig,3) or (3,nconfig)
        g_an, l_an = wf.gradient_laplacian(EIDX, configs.electron(EIDX))
        g_an = np.asarray(g_an)
        l_an = np.asarray(l_an)
        if g_an.ndim == 2 and g_an.shape[1] == 3:
            gcol = g_an[:, AXIS]      # (nconfig,)
        elif g_an.ndim == 2 and g_an.shape[0] == 3:
            gcol = g_an[AXIS, :]      # transposed (3, nconfig)
        else:
            gcol = np.asarray(g_an).ravel()
        l_an_flat = l_an.ravel()
        nconf = gcol.shape[0]

        def lnval(dx):
            c = OpenConfigs(np.array(configs.configs, copy=True))
            c.configs[:, EIDX, AXIS] += dx
            wf.recompute(c)
            return np.log(np.abs(_flat_value(wf.value())))

        f0 = lnval(0.0)
        fp = lnval(H)
        fm = lnval(-H)
        fpp = lnval(2 * H)
        fmm = lnval(-2 * H)

        d1 = (fp - fm) / (2 * H)
        d2 = (fpp - 2 * f0 + fmm) / (4 * H * H)
        d1 = d1[:nconf]
        d2 = d2[:nconf]

        # guard against nodal-surface crossings (ln|psi| -> -inf) and shape drift
        mask = (np.isfinite(d1) & np.isfinite(d2) & np.isfinite(gcol)
                & np.isfinite(l_an_flat))
        n_fin = int(mask.sum())
        if n_fin < max(4, nconf // 2):
            print(f"[warn] only {n_fin}/{nconf} finite walkers; verdict unreliable")
        gdiff = float(np.abs(gcol[mask] - d1[mask]).max())
        ld_ln = float(np.abs(l_an_flat[mask] - d2[mask]).max())
        ld_psipsi = float(np.abs(l_an_flat[mask] - (d2[mask] + d1[mask] ** 2)).max())
        nconf = int(n_fin)

        print(f"\n[{label}]")
        print(f"  max |grad_an - FD d/dx ln(psi)|  = {gdiff:.3e}")
        print(f"  max |lap_an - FD lap(ln psi)|    = {ld_ln:.3e}  (log-deriv convention)")
        print(f"  max |lap_an - FD lap(psi)/psi|   = {ld_psipsi:.3e}  (ratio convention)")
        verdict = []
        if gdiff < 1e-4:
            verdict.append("gradient: MATCH")
        else:
            verdict.append("gradient: MISMATCH")
        if ld_ln < 1e-3:
            verdict.append("lap: log-deriv convention MATCH")
        elif ld_psipsi < 1e-3:
            verdict.append("lap: ratio convention MATCH")
        else:
            verdict.append("lap: MISMATCH (both conventions)")
        print("  => " + " | ".join(verdict))
    except Exception as exc:  # noqa: BLE001
        print(f"\n[{label}] FAILED: {exc}")
        print(f"    g_an.shape={getattr(g_an, 'shape', None)} "
              f"l_an.shape={getattr(l_an, 'shape', None)} "
              f"value shape={getattr(wf.value(), 'shape', None)}")


def main():
    print("=" * 70)
    print("INCONCLUSIVE — this FD harness has a known shape/layout bug (even the")
    print("proven-correct Slater-only control mismatches). See module docstring.")
    print("Do NOT use the verdicts below as physics evidence.")
    print("=" * 70)
    mol, mf = build_h2o_rks()
    rmol, rmf = recover_pyscf("fdwf_h2o.chk")
    print(f"SCF PBE/cc-pvdz H2O = {mf.e_tot:.6f} Eh")

    wf_s, _ = generate_slater(rmol, rmf)
    check_wf("Slater-only (control, expect MATCH)", wf_s, rmol)

    wf_j, _ = generate_wf(rmol, rmf)  # default jastrow (cusp on) — broken case
    check_wf("Slater+Jastrow default cusp", wf_j, rmol)

    wf_nc, _ = generate_wf(rmol, rmf, jastrow_kws={"ion_cusp": False})
    check_wf("Slater+Jastrow ion_cusp=False", wf_nc, rmol)


if __name__ == "__main__":
    main()
