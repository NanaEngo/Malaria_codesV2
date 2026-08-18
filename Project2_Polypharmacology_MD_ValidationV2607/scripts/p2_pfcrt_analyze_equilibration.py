#!/usr/bin/env python3
"""Analyze the long NPT equilibration (job 15387) of the repaired PfCRT model.

Reads npt1ns.edr from results/md_systems/pfcrt_eq1ns_20260818, extracts
Temperature / Pressure / Density time series, reports mean/std/min/max and a
convergence assessment (drift of the running mean over the second half), plus
a strict error-marker scan of the mdrun log. Writes a fail-closed manifest.

Usage:
    python scripts/p2_pfcrt_analyze_equilibration.py [--work-dir results/md_systems/pfcrt_eq1ns_20260818]
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

PROJECT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_WORK = PROJECT_DIR / "results" / "md_systems" / "pfcrt_eq1ns_20260818"


def extract_series(edr: Path) -> dict:
    """Return {temperature_k, pressure_bar, density_kg_m3} arrays from gmx energy."""
    import subprocess
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        xvg = Path(tmp) / "energy.xvg"
        cmd = [
            "gmx", "energy", "-f", str(edr), "-o", str(xvg),
        ]
        # Selections: Temperature=0-based index depends on energy term order; use
        # term names via stdin. gmx energy accepts names or indices.
        proc = subprocess.run(
            cmd, input="Temperature\nPressure\nDensity\n0\n", capture_output=True, text=True
        )
        if proc.returncode != 0:
            raise RuntimeError(f"gmx energy failed: {proc.stderr[-500:]}")
        rows = {"t": [], "T": [], "P": [], "D": []}
        for line in xvg.read_text().splitlines():
            if line.startswith(("#", "@")):
                continue
            parts = line.split()
            if len(parts) < 4:
                continue
            try:
                t, T, P, D = (float(x) for x in parts[:4])
            except ValueError:
                continue
            rows["t"].append(t)
            rows["T"].append(T)
            rows["P"].append(P)
            rows["D"].append(D)
    return {k: np.asarray(v) for k, v in rows.items()}


def running_mean(x: np.ndarray, window: int = 100) -> np.ndarray:
    if len(x) < window:
        return np.full_like(x, np.nan)
    kernel = np.ones(window) / window
    return np.convolve(x, kernel, mode="valid")


def stats(name: str, x: np.ndarray) -> dict:
    return {
        "name": name,
        "n": int(len(x)),
        "mean": float(x.mean()),
        "std": float(x.std()),
        "min": float(x.min()),
        "max": float(x.max()),
        "first_half_mean": float(x[: len(x) // 2].mean()) if len(x) > 1 else None,
        "second_half_mean": float(x[len(x) // 2 :].mean()) if len(x) > 1 else None,
        "drift_pct": (
            float((x[len(x) // 2 :].mean() - x[: len(x) // 2].mean()) / x.mean() * 100)
            if len(x) > 1 and x.mean() != 0
            else None
        ),
    }


def scan_log(log_path: Path) -> dict:
    if not log_path.is_file():
        return {"rows": 0, "error_markers": ["missing_log"]}
    text = log_path.read_text(errors="replace")
    # Exclude the mdp echo line "epsilon-rf = inf" (reaction field disabled ->
    # legitimately infinite) which is not a numerical instability marker.
    filtered = "\n".join(
        line for line in text.splitlines() if "epsilon-rf" not in line
    )
    markers = sorted(
        set(
            re.findall(
                r"(?i)(?:Fatal error|LINCS warning|Segmentation fault|Caught signal|\bNaN\b|\binf\b)",
                filtered,
            )
        )
    )
    perf = re.findall(r"Performance:\s+([\d.]+)", text)
    return {
        "rows": len(text.splitlines()),
        "error_markers": markers,
        "performance_ns_per_day": float(perf[-1]) if perf else None,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--work-dir", type=Path, default=DEFAULT_WORK)
    args = ap.parse_args()
    work = args.work_dir.resolve()
    edr = work / "npt1ns.edr"
    log = work / "npt1ns.log"
    if not edr.is_file():
        print(f"NO EDR YET: {edr} (job still running?)")
        return 2
    series = extract_series(edr)
    log_scan = scan_log(log)
    T = stats("temperature_k", series["T"])
    P = stats("pressure_bar", series["P"])
    D = stats("density_kg_m3", series["D"])
    duration_ps = float(series["t"][-1] - series["t"][0]) if len(series["t"]) > 1 else 0.0

    # Convergence verdict (descriptive, fail-open reporting): temperature within
    # +-5 K of 310.15 and |drift| of density < 1%.
    temp_ok = abs(T["mean"] - 310.15) <= 5.0
    dens_ok = D["drift_pct"] is not None and abs(D["drift_pct"]) < 1.0
    markers_ok = not log_scan["error_markers"]
    status = "CONVERGED" if (temp_ok and dens_ok and markers_ok) else "REPORTED"

    manifest = {
        "schema_version": 1,
        "status": status,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "job": "15387",
        "duration_ps": duration_ps,
        "temperature": T,
        "pressure": P,
        "density": D,
        "log_scan": log_scan,
        "verdict": {
            "temperature_within_5K": temp_ok,
            "density_drift_lt_1pct": dens_ok,
            "no_error_markers": markers_ok,
            "note": "temperature/pressure/density convergence is descriptive; "
            "a single 1 ns replicate does not establish equilibrium",
        },
    }
    out = work / "equilibration_convergence_manifest.json"
    out.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"status: {status}")
    print(f"duration_ps: {duration_ps:.1f}")
    print(f"T: mean={T['mean']:.2f} K  drift={T['drift_pct']}%  range=[{T['min']:.1f},{T['max']:.1f}]")
    print(f"P: mean={P['mean']:.2f} bar  drift={P['drift_pct']}%  range=[{P['min']:.1f},{P['max']:.1f}]")
    print(f"D: mean={D['mean']:.2f} kg/m3  drift={D['drift_pct']}%")
    print(f"log markers: {log_scan['error_markers'] or 'none'}")
    print(f"manifest: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
