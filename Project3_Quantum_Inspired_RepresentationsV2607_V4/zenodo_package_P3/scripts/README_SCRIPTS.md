# P3 Scripts — Template/Reference Implementations

**Note**: These are template/reference scripts created for reproducibility documentation. The actual P3 computations that generated the results in the `data/` and `results/` directories were performed using the workflows described in `P3_DATA_ANALYSIS_REPORT.md`.

## Scripts Included

1. **`p3_tda_pipeline.py`** — Topological Data Analysis (TDA) fingerprint generation
   - Method: Persistent homology via Gudhi
   - Output: 84-dimensional TFP features (H0 + H1)
   - Usage: `python p3_tda_pipeline.py --input molecules.csv --output tda_features.csv`

2. **`p3_tne_pipeline.py`** — Tensor Network Embedding (TNE) generation
   - Method: Tucker decomposition (bond_dim=8, ranks=(8,8,3))
   - Output: 192-dimensional embeddings
   - Usage: `python p3_tne_pipeline.py --input molecules.csv --output tne_embeddings.csv`

3. **`p3_qks_kernel.py`** — Quantum Kernel Score (QKS) computation
   - Method: IQPEmbedding on 8 qubits (classical simulation)
   - Output: Quantum kernel matrix and benchmark results
   - Usage: `python p3_qks_kernel.py --input features.csv --labels labels.csv --output qks_results.csv`

4. **`p3_hybrid_benchmark.py`** — Hybrid benchmark (ECFP4, TFP, TNE, hybrid)
   - Method: 5-fold cross-validation with Random Forest
   - Output: Benchmark AUC scores for all representations
   - Usage: `python p3_hybrid_benchmark.py --labels labels.csv --tda tda.csv --tne tne.csv --output results.csv`

5. **`environment.yml`** — Conda environment specification
   - Install: `conda env create -f environment.yml`
   - Activate: `conda activate malaria_md_p3`

## Environment Setup

```bash
# Create conda environment
conda env create -f environment.yml

# Activate environment
conda activate malaria_md_p3

# Verify installation
python -c "import gudhi, tensorly, pennylane, rdkit; print('All libraries installed successfully')"
```

## Key Dependencies

- **RDKit** (2025.03.6): SMILES processing, ECFP4 fingerprints
- **Gudhi** (3.10.1): Persistent homology for TDA
- **TensorLy** (0.8.1): Tucker decomposition for TNE
- **PennyLane** (0.45.1): Quantum circuit simulation for QKS
- **scikit-learn** (1.6.1): Machine learning models and evaluation

## Data Flow

```
molecules.csv (SMILES)
    ↓
[p3_tda_pipeline.py] → tda_features.csv (84 TFP features)
[p3_tne_pipeline.py] → tne_embeddings.csv (192 TNE features)
[p3_qks_kernel.py]   → qks_kernel.npy (kernel matrix)
    ↓
[p3_hybrid_benchmark.py] → benchmark_results.csv (AUC scores)
```

## Expected Results

Based on P3 DAR, you should obtain approximately:

| Representation | Mean AUC | Std AUC |
|----------------|----------|---------|
| ECFP4-RF | 0.9475 | 0.0043 |
| Hybrid (TFP+TNE) | 0.8876 | 0.0072 |
| TFP-RF | 0.6300 | 0.1121 |
| TNE-RF | 0.6300 | 0.1121 |
| Quantum Kernel | 0.7512 | 0.0334 |
| RBF Kernel | 0.7007 | 0.0672 |

**Key Finding**: No quantum-inspired representation outperforms classical ECFP4 under the tested protocols.

## Computational Requirements

- **TDA**: ~1-2 seconds per molecule (serial)
- **TNE**: ~0.5-1 second per molecule (serial)
- **QKS**: ~10-100 seconds per molecule pair (kernel matrix computation)
- **Benchmark**: ~5-30 minutes depending on panel size

For large datasets (>10,000 molecules), consider parallelization.

## Notes

1. **Classical Simulation**: QKS uses classical simulation (no quantum hardware). No quantum advantage is claimed or observed.

2. **Reconstruction Errors**: TNE may fail for ~13 molecules out of 19,849 (0.07% failure rate). These are marked as NaN in the output.

3. **Computational Cost**: Quantum kernel matrix computation is O(N²), making it expensive for large N. The 5,000-molecule benchmark is recommended.

4. **Random Seeds**: For reproducibility, use `--random-state 42` in all scripts.

## References

- Gudhi: https://gudhi.inria.fr/
- TensorLy: http://tensorly.org/
- PennyLane: https://pennylane.ai/
- P3 Manuscript: Section 2 (Methods)

## Support

For questions about these scripts, see:
- `P3_DATA_ANALYSIS_REPORT.md` — Complete methodology
- `README.md` — Package overview
- Corresponding author: myke-vital.sao@facsciences-uy1.cm

---

**Created**: 2026-09-11  
**Purpose**: Template/reference implementations for reproducibility  
**Status**: Functional templates based on P3 DAR methodology
