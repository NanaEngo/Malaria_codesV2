"""
Paper 3 — TNE Wall-Time Benchmark.

Measures TNE throughput across molecule counts and bond dimensions.
Reports mol/s, total seconds, and estimated time for full 19K run.

Usage:
    python scripts/p3_tne_benchmark.py
    python scripts/p3_tne_benchmark.py --n-jobs 8
    python scripts/p3_tne_benchmark.py --gpu

Outputs:
    results/p3_tne_walltime_benchmark.csv
    results/p3_tne_walltime_benchmark.txt
"""

import argparse
import time
import warnings
from pathlib import Path

import pandas as pd

warnings.filterwarnings("ignore")

PROJECT_DIR = Path(__file__).parent.parent
RESULTS_DIR = PROJECT_DIR / "results"

BENCHMARK_SIZES  = [50, 100, 500, 1000, 5000]   # molecules
BENCHMARK_BDIMS  = [4, 8, 16]                     # bond dimensions
FULL_DATASET_N   = 19849                          # for ETA projection


def _load_sample_smiles(n: int) -> list[str]:
    """Load n SMILES from the synthesisable leads CSV."""
    path = RESULTS_DIR / "c6_primary_leads_synthesisable.csv"
    df = pd.read_csv(path).rename(columns={"input": "smiles"})
    df = df[["smiles"]].drop_duplicates().reset_index(drop=True)
    return df["smiles"].head(n).tolist()


def _run_one(smiles_list: list[str], bond_dim: int,
             n_jobs: int = 1, use_gpu: bool = False) -> dict:
    """Run TNE on a list of SMILES and return timing stats."""
    # Import here so benchmark itself doesn't count import time
    from p3_tne_pipeline import _process_one

    n = len(smiles_list)
    job_args = [(smi, bond_dim, use_gpu) for smi in smiles_list]

    t0 = time.perf_counter()

    if n_jobs != 1 and not use_gpu:
        from joblib import Parallel, delayed
        raw = Parallel(n_jobs=n_jobs, verbose=0)(
            delayed(_process_one)(a) for a in job_args
        )
    else:
        raw = [_process_one(a) for a in job_args]

    elapsed = time.perf_counter() - t0
    valid = sum(1 for _, core, _ in raw if core is not None)
    mol_per_sec = valid / elapsed if elapsed > 0 else 0.0
    eta_full = FULL_DATASET_N / mol_per_sec if mol_per_sec > 0 else float("inf")

    return {
        "n_mols":      n,
        "bond_dim":    bond_dim,
        "valid":       valid,
        "failed":      n - valid,
        "wall_time_s": round(elapsed, 2),
        "mol_per_sec": round(mol_per_sec, 2),
        "eta_full_min": round(eta_full / 60, 1),
        "backend": ("GPU" if use_gpu
                    else (f"CPU_{n_jobs}workers" if n_jobs != 1 else "CPU_serial")),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-jobs", type=int, default=1,
                        help="Number of parallel CPU workers (default: 1)")
    parser.add_argument("--gpu", action="store_true",
                        help="Use GPU Tucker backend")
    parser.add_argument("--quick", action="store_true",
                        help="Quick mode: only sizes 50,100,500 and bond_dim 8")
    args = parser.parse_args()

    sizes = [50, 100, 500] if args.quick else BENCHMARK_SIZES
    bdims = [8] if args.quick else BENCHMARK_BDIMS

    print("=" * 60)
    print("Paper 3 — TNE Wall-Time Benchmark")
    backend_str = ("GPU" if args.gpu
                   else (f"CPU ({args.n_jobs} workers)" if args.n_jobs != 1
                         else "CPU serial"))
    print(f"  Backend: {backend_str}")
    print(f"  Sizes:   {sizes}")
    print(f"  BondDims: {bdims}")
    print("=" * 60)

    # Pre-load max required SMILES
    max_n = max(sizes)
    print(f"\n  Loading {max_n} SMILES...")
    all_smiles = _load_sample_smiles(max_n)

    records = []
    for bond_dim in bdims:
        for n in sizes:
            smiles = all_smiles[:n]
            print(f"\n  n={n:5d}, bond_dim={bond_dim} ... ", end="", flush=True)
            row = _run_one(smiles, bond_dim, n_jobs=args.n_jobs, use_gpu=args.gpu)
            print(f"{row['mol_per_sec']:.2f} mol/s  "
                  f"(wall={row['wall_time_s']:.1f}s, "
                  f"ETA full={row['eta_full_min']:.0f} min)")
            records.append(row)

    df = pd.DataFrame(records)

    # Save CSV
    out_csv = RESULTS_DIR / "p3_tne_walltime_benchmark.csv"
    df.to_csv(out_csv, index=False)
    print(f"\n  Saved: {out_csv}")

    # Summary table
    lines = [
        "TNE Wall-Time Benchmark",
        f"Backend: {backend_str}",
        f"Full dataset projection: {FULL_DATASET_N} molecules",
        "",
        f"{'n_mols':>8}  {'bond_dim':>9}  {'mol/s':>8}  {'wall_time_s':>12}  {'ETA_full_min':>14}",
        "-" * 60,
    ]
    for _, row in df.iterrows():
        lines.append(
            f"{int(row['n_mols']):>8}  {int(row['bond_dim']):>9}  "
            f"{row['mol_per_sec']:>8.2f}  {row['wall_time_s']:>12.1f}  "
            f"{row['eta_full_min']:>14.0f}"
        )

    summary = "\n".join(lines)
    print("\n" + summary)
    out_txt = RESULTS_DIR / "p3_tne_walltime_benchmark.txt"
    out_txt.write_text(summary)
    print(f"\n  Summary saved: {out_txt}")


if __name__ == "__main__":
    main()
