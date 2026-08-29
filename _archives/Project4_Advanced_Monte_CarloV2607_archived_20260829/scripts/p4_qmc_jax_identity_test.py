#!/usr/bin/env python3
"""DIAGNOSTIC v2 — numba JastrowSpin TRUE-identity + e-N cusp retest (Aug 1, 2026).

DISCOVERY (run 1 of this script): pyqmc 0.8.1 `wftools.generate_jastrow` sets
the e-e cusp coefficients UNCONDITIONALLY:

    jastrow.parameters["bcoeff"][0, [0, 1, 2]] = [-0.25, -0.50, -0.25]

even when `ion_cusp=False` (verified against the installed source). So a
"zero-parameter" Jastrow is NOT exp(0)=1. The July 31 anomaly (H2O/cc-pvdz:
VMC(Slater) = -75.09 vs VMC(Slater x Jastrow ion_cusp=False) = -76.53) is
therefore explained by a genuine (intentional, cusp-satisfying) e-e Jastrow —
NOT by a broken value path. Run 1 measured VMC(Slater) = -74.95 +/- 0.45 and
VMC(J0) = -74.63 +/- 0.48 for the same nominal configs: both sane (above the
exact ground state ~ -76.44), consistent with a real non-identity Jastrow.

The numba JastrowSpin value path therefore needs to be validated with the
CORRECT identity test — explicitly zero BOTH coefficient tensors:

  A0. TRUE-identity direct check (noise-free, DECISIVE): build the Jastrow,
      zero acoeff AND bcoeff in place, then recompute() MUST return log J = 0
      on all configs. Isolates the recompute/value path with zero parameters.
  A.  Numba VMC: bare Slater vs Slater x (zeroed Jastrow) — must agree within
      3 sigma (secondary; A0 is decisive, MC noise at nconfig=400 is ~+/-0.45).
  B.  Numba VMC: e-N cusp Jastrow (ion_cusp=True) on H2O — retest of the July
      31 red flags (VMC = -99.58, and +56 Eh with explicit acoeff). A sane
      result for a cusp-only Jastrow (between Slater -75.09 and FCI -76.44)
      clears the numba path for production use.
  C.  JAX backend: DOCUMENTED BROKEN in pyqmc 0.8.1 (two independent bugs:
      (1) mf.to_uhf() mo_coeff shape mismatch — dot_general (24,) vs (5,);
      (2) cartesian GTO evaluator (24 AOs) vs spherical-basis mo_coeff (25
      rows) — dot_general (24,) vs (25,)). Legs are wrapped in try/except to
      record the exact failure without aborting the run.

References (H2O/cc-pvdz): PBE SCF = -76.33 Eh, FCI = -76.44 Eh,
Slater-only VMC (XC-free expectation of PBE orbitals) = -75.09 Eh.
References (LiH/cc-pvdz, RHF, Li-H = 1.6 bohr): RHF = -7.78 Eh.

Usage:
  python p4_qmc_jax_identity_test.py            # run all tests
  P4_QMC_TEST=H2O python p4_qmc_jax_identity_test.py   # H2O only
  P4_QMC_TEST=LIH python p4_qmc_jax_identity_test.py   # LiH only
"""
import os
import time

# JAX: enable float64 (pyqmc JAX code uses jnp.float64) + CPU for determinism
os.environ.setdefault("JAX_ENABLE_X64", "1")
import jax  # noqa: E402

jax.config.update("jax_enable_x64", True)
jax.config.update("jax_platform_name", "cpu")
import numpy as np  # noqa: E402
from pyscf import gto, dft, scf  # noqa: E402

import pyqmc.method.mc as mc  # noqa: E402
from pyqmc.wftools import generate_wf, generate_slater, generate_jastrow  # noqa: E402
from pyqmc.observables.accumulators import EnergyAccumulator  # noqa: E402

TEST = os.environ.get("P4_QMC_TEST", "ALL")


def run_vmc(wf, mol, mf, nconfig=400, nblocks=10, nsteps_per_block=10, tstep=0.5):
    """Run VMC and return (mean_energy, std_error, wall_s).
    nconfig=100/5 blocks gives +/-1 Eh error bars (seen empirically); 400/10x10
    gives ~+/-0.45 — too wide to be decisive on its own, which is why A0 (the
    direct value check) is the decisive instrument and A/B are sanity checks."""
    configs = mc.initial_guess(mol, nconfig)
    acc = {"energy": EnergyAccumulator(mol)}
    t0 = time.perf_counter()
    df, _ = mc.vmc(
        wf, configs, tstep=tstep, nblocks=nblocks,
        nsteps_per_block=nsteps_per_block, accumulators=acc, verbose=False,
    )
    wall = time.perf_counter() - t0
    e = np.mean(df["energytotal"])
    err = np.std(df["energytotal"]) / np.sqrt(len(df["energytotal"]))
    return float(e), float(err), wall


def identity_ok(e1, err1, e2, err2, hard_tol=0.02):
    """Noise-aware identity check: PASS if |dE| within max(hard_tol, 3 sigma).
    Secondary instrument only — A0 (jastrow_true_identity) is decisive."""
    delta = abs(e1 - e2)
    sigma = err1 + err2
    tol = max(hard_tol, 3.0 * sigma)
    return delta, tol


def jastrow_true_identity(mol, nconfig=128):
    """DECISIVE noise-free identity test.

    generate_jastrow(ion_cusp=False) still sets the e-e cusp bcoeff
    [-0.25, -0.50, -0.25] UNCONDITIONALLY in pyqmc 0.8.1 (wftools.py), so a
    nominal 'zero-parameter' Jastrow is NOT identity. The true identity test
    explicitly zeroes BOTH acoeff and bcoeff in place; recompute() must then
    return log J = 0 for all configs — isolating the recompute/value path.
    """
    jastrow, _ = generate_jastrow(mol, ion_cusp=False)
    amax_def = float(np.max(np.abs(np.asarray(jastrow.parameters["acoeff"]))))
    bmax_def = float(np.max(np.abs(np.asarray(jastrow.parameters["bcoeff"]))))
    print(f"  default max|acoeff| = {amax_def:.2e}  max|bcoeff| = {bmax_def:.2e} "
          f"(e-e cusp set unconditionally by generate_jastrow)", flush=True)
    # True zero-parameter Jastrow: zero BOTH tensors in place.
    jastrow.parameters["acoeff"][:] = 0.0
    jastrow.parameters["bcoeff"][:] = 0.0
    amax = float(np.max(np.abs(np.asarray(jastrow.parameters["acoeff"]))))
    bmax = float(np.max(np.abs(np.asarray(jastrow.parameters["bcoeff"]))))
    configs = mc.initial_guess(mol, nconfig)
    _, logval = jastrow.recompute(configs)
    maxlog = float(np.max(np.abs(np.asarray(logval))))
    print(f"  after zeroing: max|acoeff| = {amax:.2e}  max|bcoeff| = {bmax:.2e}", flush=True)
    print(f"  max|log J| over {nconfig} configs = {maxlog:.3e}  (must be 0)", flush=True)
    ok = maxlog < 1e-8
    verdict = ("PASS (zeroed Jastrow = exp(0) = 1 => JastrowSpin value path CORRECT)" if ok
               else "FAIL (non-zero log J at zero params => value path BROKEN)")
    print(f"[direct-verdict] {verdict}", flush=True)
    return ok


def zeroed_jastrow_wf(mol, mf):
    """Slater x Jastrow with BOTH coefficient tensors explicitly zeroed."""
    wf, _ = generate_wf(mol, mf, jax=False, jastrow_kws={"ion_cusp": False})
    # MultiplyWF stores factors in a list (pyqmc 0.8.1, no .wf1/.wf2 attrs):
    # factor[0] = Slater, factor[1] = Jastrow.
    jastrow = wf.wf_factors[1]
    jastrow.parameters["acoeff"][:] = 0.0
    jastrow.parameters["bcoeff"][:] = 0.0
    return wf


def build_h2o():
    # JAX GTO evaluator requires CARTESIAN basis (verified: ValueError
    # "Only cartesian basis functions are supported" with default spherical).
    mol = gto.Mole()
    mol.atom = "O 0 0 0; H 0 0 0.957; H 0.957 0 0"  # Angstrom
    mol.basis = "cc-pvdz"
    mol.cart = True
    mol.build()
    mf = dft.RKS(mol)
    mf.xc = "pbe"
    mf.chkfile = "h2o_pbe_ccpvdz.chk"
    mf.kernel()
    print(f"H2O PBE/cc-pvdz(cart) e_tot = {mf.e_tot:.6f} Eh (ref SCF -76.33, FCI -76.44)")
    return mol, mf


def build_lih():
    # JAX GTO evaluator requires CARTESIAN basis.
    mol = gto.M(atom="Li 0 0 0; H 0 0 1.6", basis="cc-pvdz", unit="bohr", cart=True)
    mf = scf.RHF(mol)
    mf.chkfile = "lih.chk"
    mf.kernel()
    print(f"LiH RHF/cc-pvdz(cart) e_tot = {mf.e_tot:.6f} Eh (ref -7.78)")
    return mol, mf


def jax_leg(label, fn, *args):
    """Run a JAX-path leg, capturing the expected 0.8.1 failure as documentation."""
    try:
        e, err, t = fn(*args)
        print(f"[jax]    {label} = {e:8.4f} +/- {err:.4f} Eh ({t:.0f}s)", flush=True)
        return e
    except Exception as exc:  # noqa: BLE001 — diagnostic capture
        msg = str(exc).replace("\n", " ")[:200]
        print(f"[jax]    {label}: {type(exc).__name__}: {msg}", flush=True)
        print(f"[jax]    => pyqmc 0.8.1 JAX-path bug (documented: mo_coeff / GTO "
              f"cartesian-spherical mismatch); numba path is the production path", flush=True)
        return None


def test_h2o():
    print("\n" + "=" * 72)
    print("TEST H2O/cc-pvdz PBE: numba true-identity + e-N cusp retest")
    print("=" * 72)
    mol, mf = build_h2o()

    # --- A0. DECISIVE direct value check (noise-free, ~10 s) ---
    print("\n[A0] True-identity direct Jastrow value check (zeroed params, no MC noise)")
    jastrow_true_identity(mol)

    # --- A. Numba path: bare Slater vs zeroed-Jastrow (energy identity) ---
    wf_slater, _ = generate_slater(mol, mf, jax=False)
    e_slater, err_slater, t = run_vmc(wf_slater, mol, mf)
    print(f"[numba] VMC(bare Slater)              = {e_slater:8.4f} +/- {err_slater:.4f} Eh ({t:.0f}s)", flush=True)

    wf_z = zeroed_jastrow_wf(mol, mf)
    e_z, err_z, t = run_vmc(wf_z, mol, mf)
    print(f"[numba] VMC(Slater x zeroed-J)        = {e_z:8.4f} +/- {err_z:.4f} Eh ({t:.0f}s)", flush=True)
    delta, tol = identity_ok(e_slater, err_slater, e_z, err_z)
    va = f"PASS (|dE| {delta:.4f} < tol {tol:.3f})" if delta < tol else \
        "FAIL (DIFFERENT => value path broken)"
    print(f"[A-verdict] bare Slater vs zeroed-Jastrow: -> {va} (secondary; A0 decisive)", flush=True)

    # --- B. Numba e-N cusp Jastrow (ion_cusp=True) — retest July 31 red flags ---
    wf_jc, _ = generate_wf(mol, mf, jax=False, jastrow_kws={"ion_cusp": True})
    e_jc, err_jc, t = run_vmc(wf_jc, mol, mf)
    print(f"[numba] VMC(Slater x e-N cusp J)      = {e_jc:8.4f} +/- {err_jc:.4f} Eh ({t:.0f}s)", flush=True)
    # Window is heuristic: -76.44 is the spherical-basis FCI reference (not
    # basis-matched to these cart=True runs); a cusp-only Jastrow should land
    # between the Slater (-75.09) and FCI, and must NOT reproduce -99.58/+56.
    vb = f"e-N cusp VMC {e_jc:.3f} vs Slater -75.09 / SCF -76.33 / FCI -76.44"
    if e_jc < -76.44 - 0.3 or e_jc > -74.5:
        vb += " => OUT OF RANGE (July 31 -99.58/+56Eh anomaly REPRODUCED?)"
    else:
        vb += " => SANE (between Slater and FCI; numba e-N cusp path CLEARED)"
    print(f"[B-verdict] {vb}", flush=True)

    # --- C. JAX legs — documented 0.8.1 bugs, expected failure ---
    print("\n[C] JAX backend legs (pyqmc 0.8.1: documented broken) — capturing exact failures")
    try:
        wf_jax_slater, _ = generate_slater(mol, mf, jax=True)
        jax_leg("VMC(bare Slater)         ", run_vmc, wf_jax_slater, mol, mf)
    except Exception as exc:  # noqa: BLE001
        print(f"[jax]    build JAXSlater: {type(exc).__name__}: {str(exc)[:150]}", flush=True)
    try:
        wf_jax_j0, _ = generate_wf(mol, mf, jax=True, jastrow_kws={"ion_cusp": False})
        jax_leg("VMC(Slater x J0)         ", run_vmc, wf_jax_j0, mol, mf)
    except Exception as exc:  # noqa: BLE001
        print(f"[jax]    build JAX-J0: {type(exc).__name__}: {str(exc)[:150]}", flush=True)


def test_lih():
    print("\n" + "=" * 72)
    print("TEST LiH/cc-pvdz RHF: numba true-identity (canonical docs example)")
    print("=" * 72)
    mol, mf = build_lih()

    print("\n[A0] True-identity direct Jastrow value check (zeroed params, no MC noise)")
    jastrow_true_identity(mol)

    wf_slater, _ = generate_slater(mol, mf, jax=False)
    e_slater, err_slater, t = run_vmc(wf_slater, mol, mf)
    print(f"[numba] VMC(bare Slater)              = {e_slater:8.4f} +/- {err_slater:.4f} Eh ({t:.0f}s)", flush=True)

    wf_z = zeroed_jastrow_wf(mol, mf)
    e_z, err_z, t = run_vmc(wf_z, mol, mf)
    print(f"[numba] VMC(Slater x zeroed-J)        = {e_z:8.4f} +/- {err_z:.4f} Eh ({t:.0f}s)", flush=True)
    delta, tol = identity_ok(e_slater, err_slater, e_z, err_z)
    va = f"PASS (|dE| {delta:.4f} < tol {tol:.3f})" if delta < tol else \
        "FAIL (DIFFERENT => value path broken)"
    print(f"[A-verdict] bare Slater vs zeroed-Jastrow: -> {va} (secondary; A0 decisive)", flush=True)

    print(f"[C-verdict] RHF = -7.78 (JAX path documented broken in 0.8.1; skipped)", flush=True)


if __name__ == "__main__":
    if TEST in ("ALL", "H2O"):
        test_h2o()
    if TEST in ("ALL", "LIH"):
        test_lih()
    print("\nDONE")
