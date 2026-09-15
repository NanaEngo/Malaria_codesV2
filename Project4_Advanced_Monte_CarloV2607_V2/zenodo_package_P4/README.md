# P4 Reproducibility Package — JCAMD Submission

**DOI**: https://doi.org/10.5281/zenodo.[TBD] (to be reserved)  
**License**: CC BY 4.0  
**Manuscript**: "Pareto-guided Monte Carlo tree search for multi-objective de novo antimalarial drug design"  
**Journal**: *Journal of Computer-Aided Molecular Design* (JCAMD)  
**Version**: V2 (submitted 2026-08-30)  
**Authors**: Sao Temgoua, M. V.; Tchapet Njafa, J.-P.; Samafou, P.; Fon Mbacham, W.; Nana Engo, S. G.

---

## Purpose

This deposit provides complete reproducibility records for Project 4 (P4), evaluating Pareto-guided Monte Carlo Tree Search (MCTS) with ScafVAE for multi-objective de novo molecular generation targeting antimalarial drug discovery.

**Key finding (honest-negative)**: MCTS does not outperform random exploration in scalar reward (Random: 0.6724 vs MCTS: 0.6649, p<0.001), but Pareto analysis provides transparent trade-off visualization across competing objectives.

All files are sha256-verified. The checksum manifest is in `sha256sums.txt`.

---

## Contents

### 1. `data/` — Input oracles and fragments

| File | Description |
|------|-------------|
| `fragment_library_medium.csv` | Medium-sized fragment set for MCTS |
| `scafvae_vocabulary.txt` | ScafVAE vocabulary (SMILES fragments) |
| `oracle_specifications.json` | MPO, SYBA, RRS, PNS oracle configurations |

### 2. `results/` — Benchmark and Pareto results

#### Core benchmark (v12, canonical)
- `benchmark_molecules_opt_v12/` — 20-seed scalar benchmark (MCTS, Random, GA, Greedy)
  - `p4_benchmark_merged.csv` — Merged results across all seeds
  - `p4_benchmark_seed_*.csv` — Per-seed outputs (20 files)
  - `p4_benchmark_statistics.json` — Summary statistics, paired t-tests

#### Pareto optimization
- `pareto/` — Multi-objective Pareto front
  - `pareto_front_4points.csv` — Non-dominated solutions (HV=1.2366)
  - `pareto_hypervolume.json` — Hypervolume calculation details
  - `pareto_tradeoffs.csv` — Objective trade-off analysis

#### Ablation study
- `ablation_2exp5/` — 2^5 factorial design (32 configurations × 5 replicates)
  - `ablation_effects.csv` — Main effects: ScafVAE (+0.148), Pareto (+0.108)
  - `ablation_full_results.csv` — Complete 160-run dataset

### 3. `scripts/` — Core pipeline

| Script | Purpose |
|--------|---------|
| `p4_mcts_agent.py` | MCTS agent with PUCT and temperature annealing |
| `p4_mcts_policy.py` | ScafVAE policy with Morgan+MACCS fingerprints |
| `p4_mcts_oracles.py` | Oracle aggregator (MPO, SYBA, RRS, PNS) with medchem filters |
| `p4_mcts_rl_env.py` | Molecular RL environment (fragment attachment) |
| `p4_mcts_benchmark.py` | 4-method benchmark (MCTS, Random, GA, Greedy) |
| `p4_mcts_pareto.py` | Pareto optimization and hypervolume (pymoo) |
| `p4_mcts_baselines.py` | Random, GA, Greedy baseline implementations |
| `p4_mcts_ablation.py` | 2^5 factorial ablation study |
| `environment.yml` | Conda environment specification |

### 4. `documentation/` — Supporting documents

| File | Description |
|------|-------------|
| `P4_DATA_ANALYSIS_REPORT.md` | Complete data provenance and analysis record |
| `P4_METHODS_SUPPLEMENT.md` | Detailed computational methods |
| `P4_RESULTS_SUMMARY.md` | Executive summary of key findings |

---

## How to Use This Deposit

### Verify Integrity

Before using any data, verify the checksums:

```bash
cd zenodo_package_P4
sha256sum -c sha256sums.txt
```

**Expected output**: All files OK (no mismatches).

### Reproduce Key Results

#### 1. Verify scalar benchmark (Table 1 in manuscript)

```bash
python scripts/p4_mcts_benchmark.py \
  --n-iterations 2000 \
  --n-seeds 20 \
  --output results/benchmark_reproduced.csv
```

**Expected** (mean reward ± SD):
- Random: 0.6724 ± 0.0056
- MCTS+ScafVAE: 0.6649 ± 0.0068
- GA: 0.6453 ± 0.0124
- Greedy: 0.4278 ± 0.0000

**Statistical tests**:
- MCTS vs Random: t₁₉ = -4.97, p = 0.000085 (MCTS significantly *worse*)
- MCTS vs GA: t₁₉ = 6.95, p < 0.0001 (MCTS better than GA)

#### 2. Reproduce Pareto front (Figure 3)

```bash
python scripts/p4_mcts_pareto.py \
  --n-iterations 5000 \
  --objectives MPO,SYBA,RRS,PNS \
  --output results/pareto_reproduced.csv
```

**Expected**:
- 4 non-dominated solutions
- Hypervolume = 1.2366
- Trade-offs across competing objectives

**Note**: Pareto front is a historical pre-activity artifact with post-hoc SYBA recomputation; it is not an informative 4-way optimization result.

#### 3. Reproduce ablation study (Table 2)

```bash
python scripts/p4_mcts_ablation.py \
  --design 2exp5 \
  --n-replicates 5 \
  --output results/ablation_reproduced.csv
```

**Expected main effects**:
- ScafVAE policy: +0.148
- Pareto front: +0.108
- Large vocabulary: +0.079
- c_puct: +0.034
- Temperature: -0.012

---

## File Formats

### CSV files
- Comma-separated
- UTF-8 encoding
- First row = column headers
- SMILES strings are canonical (RDKit-generated)

### Oracle scores
- MPO: Multi-parameter optimization (0-1 scale)
- SYBA: Synthetic accessibility (0-10 scale)
- RRS: Resistance resilience score (% scale)
- PNS: Polypharmacology number score (integer count)
- SA: Synthetic accessibility (RDKit, constant in Pareto analysis)

### Benchmark protocol
- Budget: 2000 iterations per method per seed
- Seeds: 20 independent runs
- Statistical test: Paired t-test on per-seed means
- Multiplicity correction: Bonferroni (documented)

---

## Software Versions

| Software | Version | Purpose |
|----------|---------|---------|
| Python | 3.11.10 | Core environment |
| RDKit | 2025.03.6 | SMILES, descriptors, filters |
| NumPy | 2.2.1 | Array operations |
| pandas | 2.2.3 | Tabular data |
| SciPy | 1.15.1 | Statistics |
| PyTorch | 2.13.0 | ScafVAE neural network |
| pymoo | 0.6.1 | Pareto front and hypervolume |
| datamol | 0.12.4 | Molecular standardization |
| medchem | 2.0.5 | Drug-likeness filters (Lipinski, PAINS, Brenk) |

**Environment**: `malaria_md` conda environment (see `scripts/environment.yml` for complete package list).

---

## Evidence Boundaries

This deposit provides:
- ✅ 20-seed scalar benchmark with paired statistical tests
- ✅ Pareto front with documented hypervolume
- ✅ 2^5 factorial ablation study (160 runs)
- ✅ Honest-negative result (MCTS does not beat Random)
- ✅ Complete oracle specifications

This deposit **does NOT provide**:
- ❌ Claims of MCTS superiority in scalar optimization
- ❌ Experimental activity measurements
- ❌ QMC-validated electronic energies (Tier 2 diagnostics identified issues)
- ❌ Prospective wet-lab validation
- ❌ Universal claims about MCTS performance

**The Pareto analysis provides auditable candidate-set geometry for transparent trade-offs, not proof of superior scalar optimization.**

---

## Relation to Manuscript

This deposit corresponds to:
- **Main text**: Tables 1–2, Figures 1–4
- **Supporting Information**: Tables S1–S6, Figures S1–S4

**Manuscript sections directly supported**:
- §2 Methods (MCTS, ScafVAE, oracles, Pareto)
- §3.1 Scalar benchmark design
- §3.2 Benchmark results (honest-negative)
- §3.3 Pareto optimization
- §3.4 Ablation study
- §3.5 Chemical diversity and drug-likeness

---

## Citation

**Dataset**:
```
Sao Temgoua, M. V.; Tchapet Njafa, J.-P.; Samafou, P.; Fon Mbacham, W.; 
Nana Engo, S. G. (2026). P4 Reproducibility Package — JCAMD Submission [Data set]. 
Zenodo. https://doi.org/10.5281/zenodo.[TBD]
```

**Manuscript** (when published):
```
Sao Temgoua, M. V.; Tchapet Njafa, J.-P.; Samafou, P.; Fon Mbacham, W.; 
Nana Engo, S. G. Pareto-guided Monte Carlo tree search for multi-objective 
de novo antimalarial drug design. J. Comput. Aided Mol. Des. 2026, XX, XXXX–XXXX. 
DOI: [to be assigned]
```

---

## Contact

**Corresponding author**: Myke Vital Sao Temgoua  
**Email**: myke-vital.sao@facsciences-uy1.cm  
**ORCID**: 0009-0004-5170-2309  
**Institution**: Department of Physics, Faculty of Science, University of Yaoundé I, Cameroon

**Code repository** (to be made public upon publication): https://github.com/NanaEngo/Malaria_codesV2

---

## Acknowledgments

This work was supported by computational resources from the University of Yaoundé I.

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| V2 | 2026-08-30 | Initial Zenodo deposit for JCAMD submission |

---

**Last updated**: 2026-09-11  
**Package prepared by**: Kiro AI agent  
**Zenodo deposit ID**: [TBD] (to be reserved)
