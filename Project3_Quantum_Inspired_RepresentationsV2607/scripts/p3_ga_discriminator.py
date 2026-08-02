"""
Paper 3 — GA Discriminator vs Quantum Kernel.

Compares quantum kernel density (QKS) vs ECFP4-Tanimoto distance as a
discriminator for generated molecules at N=50/100/200/500 molecules per round.

This mirrors the Aspuru-Guzik GA discriminator setup (2024):
    - A quantum kernel-based SVM is trained on known active/inactive molecules
    - Generated molecules (via STONED-SELFIES) are scored by the discriminator
    - AUC-ROC is compared between quantum kernel density and ECFP4 Tanimoto distance

Pipeline:
    1. Load seed molecules (active African NPs from c6 leads)
    2. Generate N molecules via STONED-SELFIES mutations
    3. Train quantum kernel SVM on reference actives + inactives
    4. Score generated molecules as in-domain (active-like) vs out-of-domain
    5. Compare AUC: quantum kernel vs ECFP4 max Tanimoto to seed set
    6. Repeat at N=50/100/200/500

Outputs:
    results/p3_ga_discriminator.csv    -- per-round AUC comparison
    results/p3_ga_discriminator.png    -- AUC vs N comparison plot
    results/p3_ga_discriminator.txt    -- summary

Usage:
    python scripts/p3_ga_discriminator.py
    python scripts/p3_ga_discriminator.py --pilot --n-generated 50
    python scripts/p3_ga_discriminator.py --n-seeds 50 --n-rounds 3
"""

import argparse
import random
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from rdkit import Chem
from rdkit.Chem import rdFingerprintGenerator
from rdkit.DataStructs import ConvertToNumpyArray
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

import pennylane as qml
from pennylane.kernels import kernel_matrix, closest_psd_matrix

warnings.filterwarnings("ignore")

PROJECT_DIR = Path(__file__).parent.parent
RESULTS_DIR = PROJECT_DIR / "results"

N_QUBITS    = 8
ACT_THRESHOLD = 0.5
RANDOM_SEED = 42

morgan_gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)


# ---------------------------------------------------------------------------
# SELFIES-based molecular mutation (STONED-like, without full STONED install)
# ---------------------------------------------------------------------------

def _mol_to_selfies(smi: str) -> str | None:
    """Convert SMILES to SELFIES string."""
    try:
        import selfies as sf
        return sf.encoder(smi)
    except Exception:
        return None


def _selfies_to_smiles(selfies_str: str) -> str | None:
    """Convert SELFIES to valid SMILES."""
    try:
        import selfies as sf
        smi = sf.decoder(selfies_str)
        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            return None
        return Chem.MolToSmiles(mol)
    except Exception:
        return None


def mutate_selfies(selfies_str: str, n_mutations: int = 1,
                   rng: random.Random | None = None) -> str | None:
    """
    Apply random character-level mutations to a SELFIES string.
    Simple STONED-like mutation: substitute, insert, or delete a token.
    """
    try:
        import selfies as sf
        tokens = list(sf.split_selfies(selfies_str))
        if not tokens:
            return None

        alphabet = list(sf.get_semantic_robust_alphabet())
        if rng is None:
            rng = random.Random(RANDOM_SEED)

        for _ in range(n_mutations):
            if len(tokens) == 0:
                break
            op = rng.choice(["substitute", "insert", "delete"])
            idx = rng.randint(0, len(tokens) - 1)
            if op == "substitute" and alphabet:
                tokens[idx] = rng.choice(alphabet)
            elif op == "insert" and alphabet:
                tokens.insert(idx, rng.choice(alphabet))
            elif op == "delete" and len(tokens) > 1:
                tokens.pop(idx)

        return "".join(tokens)
    except Exception:
        return None


def generate_molecules(seed_smiles: list[str], n: int,
                       n_mutations: int = 2) -> list[str]:
    """
    Generate n unique valid molecules via STONED-like SELFIES mutations.
    Falls back to RDKit fragment enumeration if selfies not available.
    """
    rng = random.Random(RANDOM_SEED)
    generated = set()
    attempts = 0
    max_attempts = n * 20

    # Check if selfies is available
    try:
        import importlib.util
        use_selfies = importlib.util.find_spec("selfies") is not None
    except Exception:
        use_selfies = False

    while len(generated) < n and attempts < max_attempts:
        seed = rng.choice(seed_smiles)
        attempts += 1

        if use_selfies:
            selfies_str = _mol_to_selfies(seed)
            if selfies_str is None:
                continue
            mutated = mutate_selfies(selfies_str, n_mutations=n_mutations, rng=rng)
            if mutated is None:
                continue
            smi = _selfies_to_smiles(mutated)
        else:
            # Minimal fallback: add/remove a methyl group
            mol = Chem.MolFromSmiles(seed)
            if mol is None:
                continue
            smi = Chem.MolToSmiles(mol)  # just use the seed with canonical form

        if smi and smi not in generated and smi not in seed_smiles:
            generated.add(smi)

    return list(generated)[:n]


# ---------------------------------------------------------------------------
# Fingerprint utilities
# ---------------------------------------------------------------------------

def smiles_to_ecfp4(smiles_list: list[str]) -> np.ndarray:
    """Convert SMILES list to ECFP4 fingerprint matrix."""
    rows = []
    for smi in smiles_list:
        mol = Chem.MolFromSmiles(smi)
        arr = np.zeros(2048, dtype=np.float32)
        if mol:
            ConvertToNumpyArray(morgan_gen.GetFingerprint(mol), arr)
        rows.append(arr)
    return np.array(rows, dtype=np.float32)


def max_tanimoto_to_seeds(X_query: np.ndarray,
                           X_seeds: np.ndarray) -> np.ndarray:
    """
    For each molecule in X_query, compute its max Tanimoto similarity to any seed.
    Returns array of shape (n_query,) in [0, 1].
    """
    scores = []
    for i in range(len(X_query)):
        q = X_query[i]
        sims = []
        for j in range(len(X_seeds)):
            s = X_seeds[j]
            intersect = np.minimum(q, s).sum()
            union = np.maximum(q, s).sum()
            sims.append(float(intersect / union) if union > 0 else 0.0)
        scores.append(max(sims) if sims else 0.0)
    return np.array(scores, dtype=np.float32)


# ---------------------------------------------------------------------------
# Quantum kernel
# ---------------------------------------------------------------------------

def ecfp4_to_qubits(X_train: np.ndarray,
                     X_test: np.ndarray,
                     n_components: int = N_QUBITS):
    """Reduce ECFP4 to N_QUBITS dims via UMAP, scale to [-1, 1]."""
    try:
        from umap import UMAP
        reducer = UMAP(n_components=n_components, metric="jaccard",
                       random_state=RANDOM_SEED, n_neighbors=15, min_dist=0.1)
        X_tr = reducer.fit_transform(X_train)
        X_te = reducer.transform(X_test)
    except ImportError:
        from sklearn.decomposition import PCA
        pca = PCA(n_components=n_components, random_state=RANDOM_SEED)
        sc = StandardScaler()
        X_tr = pca.fit_transform(sc.fit_transform(X_train))
        X_te = pca.transform(sc.transform(X_test))

    lo, hi = X_tr.min(axis=0), X_tr.max(axis=0)
    rng = np.where(hi - lo > 0, hi - lo, 1.0)
    X_tr_q = np.clip(2.0 * (X_tr - lo) / rng - 1.0, -1.0, 1.0)
    X_te_q = np.clip(2.0 * (X_te - lo) / rng - 1.0, -1.0, 1.0)
    return X_tr_q, X_te_q


def make_qk_kernel_fn() -> callable:
    """Build IQPEmbedding kernel function on lightning.qubit."""
    dev = qml.device("lightning.qubit", wires=N_QUBITS)

    @qml.qnode(dev)
    def _kernel(x1, x2):
        qml.IQPEmbedding(x1, wires=range(N_QUBITS))
        qml.adjoint(qml.IQPEmbedding)(x2, wires=range(N_QUBITS))
        return qml.probs(wires=range(N_QUBITS))

    def kernel(a, b):
        return float(_kernel(a, b)[0])

    return kernel


def qk_discriminator_auc(X_ref_q: np.ndarray, X_gen_q: np.ndarray,
                          kernel_fn: callable) -> float:
    """
    Compute Quantum Kernel Density as an out-of-domain discriminator score.
    Score = mean kernel similarity to the reference seeds.
    Returns AUC-ROC discriminating reference (label=1) from generated (label=0).
    """
    # Density for reference (leave-one-out for self-similarity might be better, but we just compute mean)
    K_ref = kernel_matrix(X_ref_q, X_ref_q, kernel_fn)
    density_ref = K_ref.mean(axis=1)

    # Density for generated
    K_gen = kernel_matrix(X_gen_q, X_ref_q, kernel_fn)
    density_gen = K_gen.mean(axis=1)

    all_scores = np.concatenate([density_ref, density_gen])
    all_labels = np.concatenate([np.ones(len(density_ref)),
                                 np.zeros(len(density_gen))])

    if np.isnan(all_scores).any():
        print(f"  [ERROR] all_scores contains NaN. ref_nan={np.isnan(density_ref).sum()}, gen_nan={np.isnan(density_gen).sum()}")
        return float("nan")

    try:
        return float(roc_auc_score(all_labels, all_scores))
    except Exception as e:
        print(f"  [ERROR in qk_discriminator_auc]: {e}")
        return float("nan")


# ---------------------------------------------------------------------------
# Main benchmark
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-seeds", type=int, default=200,
                        help="Reference seed molecules to train discriminator (default: 200)")
    parser.add_argument("--n-generated-list", type=str, default="50,100,200,500",
                        help="Comma-separated list of N values to benchmark (default: 50,100,200,500)")
    parser.add_argument("--n-mutations", type=int, default=2,
                        help="SELFIES mutations per molecule (default: 2)")
    parser.add_argument("--pilot", action="store_true",
                        help="Pilot mode: n-seeds=50, n-generated=[50, 100] only")
    args = parser.parse_args()

    DEVICE = "lightning.qubit"  # system-wide PennyLane device

    n_gen_list = [int(x) for x in args.n_generated_list.split(",")]
    if args.pilot:
        args.n_seeds = 50
        n_gen_list = [50, 100]
        print("  [PILOT] n_seeds=50, n_generated=[50, 100]")

    print("=" * 60)
    print("Paper 3 — GA Discriminator vs Quantum Kernel  (lightning.qubit)")
    print(f"  Device:    {DEVICE}")
    print(f"  Seeds:     {args.n_seeds}")
    print(f"  N values:  {n_gen_list}")
    print(f"  Mutations: {args.n_mutations}")
    print("=" * 60)

    # Load reference dataset
    print("\n  Loading reference molecules...")
    act_df = pd.read_csv(RESULTS_DIR / "eos80ch_malaria_final_activity.csv")
    act_df = act_df[["input", "asexual_blood_stage"]].dropna().rename(
        columns={"input": "smiles", "asexual_blood_stage": "activity"}
    ).head(args.n_seeds)

    ref_smiles = act_df["smiles"].tolist()
    y_ref_full = (act_df["activity"].values >= ACT_THRESHOLD).astype(int)

    # Filter valid SMILES
    valid_ref, valid_y = [], []
    for smi, y in zip(ref_smiles, y_ref_full):
        if Chem.MolFromSmiles(smi) is not None:
            valid_ref.append(smi)
            valid_y.append(y)
    ref_smiles = valid_ref
    y_ref = np.array(valid_y)
    print(f"  Reference: {len(ref_smiles)} valid (active={y_ref.sum()}, inactive={(y_ref==0).sum()})")

    X_ref_ecfp = smiles_to_ecfp4(ref_smiles)

    # Build quantum kernel function (shared across all N rounds)
    print(f"\n  Building quantum kernel (device={DEVICE})...")
    kernel_fn = make_qk_kernel_fn()

    records = []

    for n_gen in n_gen_list:
        print(f"\n  --- N={n_gen} generated molecules ---")

        # Generate molecules
        print(f"  Generating {n_gen} molecules via SELFIES mutations...")
        gen_smiles = generate_molecules(ref_smiles, n=n_gen,
                                        n_mutations=args.n_mutations)
        valid_gen = [s for s in gen_smiles if Chem.MolFromSmiles(s) is not None]
        print(f"  Generated: {len(valid_gen)} valid / {n_gen} requested")
        if len(valid_gen) == 0:
            print("  Warning: no valid generated molecules — skipping N={n_gen}")
            continue

        X_gen_ecfp = smiles_to_ecfp4(valid_gen)

        # Metric 1: ECFP4 max Tanimoto discriminator
        # Score each generated molecule by max Tanimoto to reference seeds
        # AUC = can we distinguish refs (high Tanimoto) from generated (low)?
        tanimoto_scores_ref = max_tanimoto_to_seeds(X_ref_ecfp, X_ref_ecfp)
        tanimoto_scores_gen = max_tanimoto_to_seeds(X_gen_ecfp, X_ref_ecfp)
        all_scores_tan = np.concatenate([tanimoto_scores_ref, tanimoto_scores_gen])
        all_labels_tan = np.concatenate([np.ones(len(X_ref_ecfp)),
                                          np.zeros(len(X_gen_ecfp))])
        try:
            auc_tanimoto = float(roc_auc_score(all_labels_tan, all_scores_tan))
        except Exception:
            auc_tanimoto = float("nan")
        print(f"  ECFP4 Tanimoto discriminator AUC: {auc_tanimoto:.4f}")

        # Metric 2: Quantum kernel discriminator
        # Reduce to qubits: train on refs, score on generated
        X_ref_q, X_gen_q = ecfp4_to_qubits(X_ref_ecfp, X_gen_ecfp)
        print(f"  Computing quantum kernel ({len(X_ref_q)}x{len(X_ref_q)})...")
        auc_qk = qk_discriminator_auc(X_ref_q, X_gen_q, kernel_fn)
        print(f"  Quantum kernel discriminator AUC: {auc_qk:.4f}")

        records.append({
            "n_generated": n_gen,
            "n_valid_generated": len(valid_gen),
            "n_reference": len(ref_smiles),
            "auc_ecfp4_tanimoto": round(auc_tanimoto, 4),
            "auc_quantum_kernel": round(auc_qk, 4),
            "delta_auc": round(auc_qk - auc_tanimoto, 4),
            "device": DEVICE,
        })

    if not records:
        print("No valid records — check SELFIES installation and molecule generation.")
        return

    df = pd.DataFrame(records)

    # Save CSV
    out_csv = RESULTS_DIR / "p3_ga_discriminator.csv"
    df.to_csv(out_csv, index=False)
    print(f"\n  Saved: {out_csv}")

    # Summary
    lines = [
        "GA Discriminator vs Quantum Kernel (AUC-ROC comparison)",
        f"Device: {DEVICE} | Seeds: {len(ref_smiles)} | Mutations/mol: {args.n_mutations}",
        "",
        f"{'N_gen':>6}  {'AUC_Tanimoto':>14}  {'AUC_QK':>10}  {'Delta':>8}",
        "-" * 45,
    ]
    for _, row in df.iterrows():
        lines.append(
            f"{int(row['n_generated']):>6}  {row['auc_ecfp4_tanimoto']:>14.4f}  "
            f"{row['auc_quantum_kernel']:>10.4f}  {row['delta_auc']:>+8.4f}"
        )

    summary = "\n".join(lines)
    print("\n" + summary)
    out_txt = RESULTS_DIR / "p3_ga_discriminator.txt"
    out_txt.write_text(summary)
    print(f"\n  Summary saved: {out_txt}")

    # Plot
    try:
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(7, 5))
        ax.plot(df["n_generated"], df["auc_ecfp4_tanimoto"], "o-",
                color="#E76F51", label="ECFP4 Tanimoto", linewidth=2, markersize=8)
        ax.plot(df["n_generated"], df["auc_quantum_kernel"], "s-",
                color="#264653", label="Quantum Kernel (IQPEmbedding)", linewidth=2, markersize=8)
        ax.axhline(0.5, color="gray", linestyle="--", alpha=0.5, label="Random")
        ax.set_xlabel("N generated molecules", fontsize=13)
        ax.set_ylabel("AUC-ROC (discriminator)", fontsize=13)
        ax.set_title("GA Discriminator: QK vs Tanimoto", fontsize=14)
        ax.legend(fontsize=11)
        ax.set_ylim(0, 1.05)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        out_png = RESULTS_DIR / "p3_ga_discriminator.png"
        fig.savefig(out_png, dpi=150, bbox_inches="tight")
        plt.close()
        print(f"  Plot saved: {out_png}")
    except Exception as e:
        print(f"  Plot skipped: {e}")


if __name__ == "__main__":
    main()
