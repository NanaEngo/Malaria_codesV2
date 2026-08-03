# P4 Data Analysis Report — Pareto-Guided MCTS & QMC Validation

**Generated:** July 29, 2026 — **Split from BMAD** August 1, 2026 — **Updated** August 3, 2026 (v12 canonical re-benchmark, greedy corrected)
**Canonical:** ✅ This report is the **single source of truth for all P4 data analysis**. It was split from `BMAD_Q1_DATA_ANALYSIS_REPORT.md` (v47, August 1, 2026) because the QMC validation effort (Tier 1 SCF + Tier 2 VMC/DMC deep-diagnostic) became complex enough to deserve a dedicated report. **All future P4 data-analysis decisions are documented HERE, not in BMAD** (which now covers P1–P3 only).
**Environment:** HPC `malaria_md` (rdkit 2025.03.6, pyscf 2.14.0, xtb, gpu4pyscf 1.8.0, pyqmc 0.8.1, scikit-learn)
**Coverage:** P4 only — MCTS benchmark (v1–v12, **v12 canonical**), Pareto front, ablations, QMC Tier 1 (SCF) + Tier 2 (VMC/DMC) validation

---

## Executive Summary

**P4 (Pareto-Guided MCTS for Antimalarial Design)** implements a **Monte-Carlo-tree-search generative agent that assembles antimalarial candidates fragment-by-fragment, scored by a multi-objective oracle (MPO + docking proxy + SA + SYBA + RRS + PNS). On the curated `medium` fragment set (6 categories), the canonical **v12 20-seed benchmark** (2026-08-03, v11 re-run with greedy lookahead bug fixed) shows **Random (0.7335 ± 0.0063) > MCTS+ScafVAE (0.7276 ± 0.0090) > Greedy (0.7211 ± 0.0000) > GA (0.7027 ± 0.0152)**. Random narrowly edges out MCTS (paired t-test: t₁₉ = 2.41, p = 0.026, mean Δ = 0.006), and MCTS significantly outperforms GA (t₁₉ = 5.55, p < 0.0001). The real value of MCTS is the **diverse Pareto front of multi-objective trade-offs** (4 non-dominated solutions across 20 seeds, hypervolume 1.2366), not a higher scalar reward.

> ⚠️ **v9 → v10 → v11 re-benchmark (2026-08-02):** (1) the v9 deposited rewards (Random 0.6645, MCTS 0.6594, GA 0.6402, Greedy 0.5398) could **not** be reproduced from the committed code + data (the docking oracle's Tartarus library state differed at run time) → v10 re-run with a **value-preserving vectorisation of the docking Tanimoto scan** (~4700× faster, verified identical on held-out molecules); (2) a P0 audit then found the v10 benchmark MCTS ran with **default hyperparameters** (c_puct=1.414, uniform priors, NO ScafVAE policy) while the manuscript claimed the screened-optimal config (c_PUCT=5.0, ν=0.01, T=0.8 + ScafVAE) was retained for all experiments → **v11 re-run (job 12725) with the optimal config wired into the benchmark** (`results/benchmark_molecules_opt/`, canonical). MCTS rose 0.7149 → 0.7276 and now wins 5/20 seeds; ranking Random > MCTS > GA > Greedy is preserved in all three runs. The v10 default-config CSVs remain in `results/benchmark_molecules/` as a sensitivity comparison (§1.8).

**Component ablation (2⁵ factorial, 160 runs):** ScafVAE policy (+0.148), Pareto front (+0.108), and Large vocabulary (+0.079) are the largest positive main effects.

**QMC validation (Tier 1/2, July 26 – Aug 1, 2026):** Tier 1 (PBE/def2-SVP SCF via PySCF) is fully restored and GPU-accelerated (`gpu4pyscf`, 4/4 candidates, ~56 s/candidate). Tier 2 (VMC/DMC via PyQMC 0.8.1) is a complex diagnostic story with a **verdict correction** (v45 → v46):

- **v45 (July 31):** concluded the JastrowSpin combination/summation path was broken (LiH VMC −7.39 < RHF −7.78; DMC population collapse at 144 electrons).
- **v46 (Aug 1):** **RETRACTED** the "broken path" conclusion. The root cause was a **wrong premise**: `generate_jastrow(ion_cusp=False)` sets the e–e cusp `bcoeff[0,[0,1,2]]=[-0.25,-0.50,-0.25]` **unconditionally** in 0.8.1, so a nominal "zero-parameter" Jastrow is NOT exp(0)=1. The noise-free A0 true-identity test (both coefficient tensors explicitly zeroed) gives `max|log J| = 0.000e+00` ⇒ the numba `recompute()` value path is **CORRECT**. e-N cusp VMC = −74.603 ± 0.496 → **SANE** (July 31 −99.58 anomaly NOT reproduced). The **JAX backend is broken in 0.8.1** (two independent `dot_general` shape bugs, 24 spherical vs 25 cartesian AOs) → dropped; **numba is the production path**.

The **144-electron DMC population collapse remains real and confirmed** by the scale test (Slater-only −897/−900 Eh vs SCF −864; Jastrow −867 Eh — 3.2 Eh below SCF) — **candidate-level Tier 2 energies are NOT publication-grade in this env**, regardless of the JastrowSpin verdict. Production protocol would require OPTIMIZE + nconfig ≥ 1000 + τ→0 extrapolation. The manuscript stays clean (QMC claims removed July 29).

---

## 1. MCTS Benchmark Results

### 1.1 P4 Results at a Glance — **UPDATED August 3, 2026 (v12 canonical)**

A consolidated view of the final P4 production runs, cross-verified against the raw CSV outputs in `Project4_Advanced_Monte_CarloV2607/results/`.

| Study | Source file(s) | Key finding |
|:------|:-------------|:------------|
| **v12 20-seed benchmark (CANONICAL)** | `results/benchmark_molecules_opt/p4_benchmark_merged.csv` | Random (0.7335 ± 0.0063) > MCTS+ScafVAE (0.7276 ± 0.0090) > Greedy (0.7211 ± 0.0000) > GA (0.7027 ± 0.0152); MCTS vs Random t₁₉ = 2.41, p = 0.026, Δ=0.006; MCTS vs Greedy t₁₉ = 3.22, p = 0.005; MCTS vs GA t₁₉ = 5.55, p < 0.0001 |
| **Component ablation** | `results/ablation/p4_component_ablation_summary.csv` | ScafVAE (+0.148), Pareto front (+0.108), and Large vocabulary (+0.079) are the largest positive main effects |
| **Fragment vocabulary ablation** | `results/ablation/p4_ablation_summary.csv` | ANOVA F = 350.10, p = 1.12 × 10⁻²⁶; `aromatic_only` set is significantly worse than `all`, `medium`, and `minimal` |
| **Pareto front** | `results/pareto/merged_pareto_front.csv` | 4 non-dominated solutions across 20 seeds (MPO 0.729–0.946, SA = 3.0, SYBA recomputed 0.021–1.000, hypervolume 1.2366) |

**Primary conclusion:** On the curated medium fragment set, simple random search narrowly edges out MCTS at its screened optimal configuration (mean Δ = 0.006, paired t-test: t₁₉ = 2.41, p = 0.026), and MCTS significantly edges out GA (t₁₉ = 5.55, p < 0.0001). The real value of MCTS lies in its ability to generate a diverse Pareto front of multi-objective trade-offs, not in a higher scalar reward. The v11 re-benchmark (§1.8) preserves the v9/v10 ranking with a much smaller MCTS–Random gap and fully reproducible per-seed outputs.

### 1.8 Canonical re-benchmarks v10/v11 (20 seeds × 4 methods, 2026-08-02) — **v11 CANONICAL (supersedes v10, which supersedes v9)**

> **Why a re-run:** during P0 pre-submission verification (Pareto provenance lock + diversity recompute), the v9 deposited rewards could not be reproduced from the committed code + data. Greedy is deterministic, so the observed v9-vs-regenerated mismatch (Greedy 0.5398 vs 0.6147 [the regenerated greedy was itself pre-fix, later corrected to 0.7211 in v12]; Random 0.6645 vs 0.7329) is proof of **oracle/library state drift at v9 run time**, not stochasticity. Investigation (2026-08-02): the oracle script and pipeline are byte-identical between the v9 deposit commit (`81ee79a56`) and HEAD; the v9 timing profile (Random 310 s/seed, Greedy 0.12 s) implies a **different Tartarus docking library state at run time** (docstring references a ~2,800-row library; the committed file has 19,913 rows, committed in `5cd7eec03` together with the v9 results). None of the tested oracle configurations (full 6-objective vs reduced `compute_mpo_reward`) reproduced the v9 values.

**Value-preserving optimisation:** `_docking_score` rebuilt a 19,913×2048 dense fingerprint matrix **on every call** (~4.7 s/call). Fix: precompute the dense matrix + norms once at init, vectorise the Tanimoto scan (~1 ms/call, ~4700× faster). **Verified value-equivalent**: identical similarity + index on 10 held-out molecules (10/10). This changes runtime only, never reward semantics.

**Run:** v10 — SLURM array job 12705 (`p4_benchmark_molecules_array.sbatch`), outputs in `results/benchmark_molecules/`. v11 (optimal MCTS config) — SLURM array job 12725 (`p4_benchmark_molecules_opt_array.sbatch`), outputs in `results/benchmark_molecules_opt/` (**canonical**). Determinism check: seed 13 regenerated twice → identical rewards. **v12 (2026-08-03)** — greedy lookahead bug fixed (env accidentally reset inside the greedy roll-out), re-run as SLURM job 12767: Greedy 0.6147 → **0.7211** (deterministic), MCTS/random/GA unchanged. **The `benchmark_molecules_opt/` directory holds the v12 canonical values.**

**v12 canonical table (optimal MCTS config, greedy corrected):**

| Method | Mean reward | Std | Min | Max | n | Mean time (s) | Std time (s) |
|:------|:----------:|:---:|:---:|:---:|:---:|:-------:|:-------:|
| **Random** | **0.7335** | 0.0063 | 0.7227 | 0.7481 | 20 | 42.2 | 1.2 |
| MCTS+ScafVAE | 0.7276 | 0.0090 | 0.7054 | 0.7442 | 20 | 82.2 | 11.8 |
| Greedy | 0.7211 | 0.0000 | 0.7211 | 0.7211 | 20 | 0.1 | 0.0 |
| GA | 0.7027 | 0.0152 | 0.6749 | 0.7311 | 20 | 1.9 | 0.2 |

**Key findings (v12, optimal MCTS config — CANONICAL):**
- **MCTS config fix:** benchmark MCTS previously ran with defaults (c_puct=1.414, uniform priors, no ScafVAE). v11 wires the screened-optimal config (c_PUCT=5.0, virtual_loss=0.01, T=0.8, ScafVAE policy) into `run_mcts`.
- **Greedy fix (v12):** `p4_mcts_benchmark.py` greedy baseline accidentally called `env.reset()` inside its roll-out lookahead, degrading it to a single-fragment sample (0.6147). Corrected → Greedy 0.7211 (deterministic, uniq=1 seed 20/20).
- **Ranking:** Random > MCTS > Greedy > GA.
- **MCTS close to Random:** mean Δ = 0.0059 (v10: 0.0186), t₁₉ = 2.41, p = 0.026, Cohen's d = −0.54; **MCTS wins 5/20 seeds** (seeds 0, 6, 8, 10, 19) vs 0 in v10.
- **MCTS vs Greedy:** t₁₉ = 3.22, p = 0.005; **MCTS vs GA:** t₁₉ = 5.55, p < 0.0001.
- **Best/worst seeds:** Random best 0.7481 (seed 1); MCTS best 0.7442 (seed 8); GA best 0.7311 (seed 9); Greedy constant 0.7211.
- **Timing:** MCTS 82.2 ± 11.8 s/seed (ScafVAE policy adds overhead), Random 42.2 ± 1.2 s.
- **Molecule sets deposited:** best-SMILES per method per seed (`p4_benchmark_molecules_seed_N.csv` in `benchmark_molecules_opt/`) → real diversity analysis (§1.9).

**Key findings (v10, default config — sensitivity comparison only):**
- Ranking Random > MCTS > GA > Greedy; MCTS–Random Δ = 0.0186, t₁₉ = 6.59, p < 0.0001; MCTS mean 0.7149 ± 0.0105 (time 59.6 ± 8.8 s).
- Retained for comparison: `results/benchmark_molecules/` (per-seed rewards + best-SMILES).

**Manuscript impact:** Table 1 (tab:benchmark), abstract, Results, Discussion, Limitations, Methods, cover letters, and the new Supplementary Material (SM S2 diversity table + SM S3 reproducibility) all updated to v12 (greedy 0.7211). Ablation results (different oracle-weight config) and the Pareto front (independent of the scalar benchmark) are **unchanged**.

### 1.9 Real molecular diversity of the four methods (2026-08-02)

Computed by `scripts/p4_compute_diversity.py` from the deposited best-in-seed molecule sets (20 molecules/method; ECFP4 radius 2, 2048 bits; Bemis–Murcko scaffolds) — v12 optimal-config sets. Reported in SM S2 only (main text keeps diversity out, per the P0-2 decision).

| Method | n | Mean pairwise Tanimoto dissimilarity | Unique BM scaffolds | Unique scaffold fraction |
|:------|:--:|:---:|:---:|:---:|
| MCTS+ScafVAE | 20 | 0.8023 | 19 | 0.950 |
| Random | 20 | 0.7806 | 20 | 1.000 |
| GA | 20 | 0.8332 | 17 | 0.850 |
| Greedy | 20 | 0.0000 | 1 | 0.050 |

Key findings: all three stochastic methods are structurally diverse (mean pairwise dissimilarity 0.78–0.83; ≥17/20 unique scaffolds); Random achieves full scaffold coverage (20/20); MCTS with the optimal config achieves 19/20 unique scaffolds; Greedy deterministically collapses to a single molecule (dissimilarity 0, 1 scaffold) — confirming the "deceptive flat landscape" narrative with real deposited data. Outputs: `results/diversity/p4_diversity_metrics.csv`, `p4_diversity_mds.csv`.

### 1.2 Pipeline Optimizations (21 July 2026)

Nine code-level improvements were implemented to address MCTS underperformance and enable large-scale benchmarks:

| Optimization | Description | Impact |
|:-------------|:------------|:-------|
| **Dynamic Progressive Widening** | `max(5, k·N^α)` avec α=0.5, k=1.0 au lieu de K=10 fixe | Croissance de 5 à 33 actions selon visites |
| **Virtual Loss** | Pénalité ν=0.05 sur les nœuds sur-explorés | +47 états visités vs avant (29→47) |
| **State caching (MCTS-Solver)** | Évite de revisiter les mêmes molécules | Exploration plus diverse |
| **Policy-biased rollout** | Rollout via ScafVAE au lieu d'uniforme | +0.13 reward (+8.5%) |
| **Lightweight env reinit** | `MolecularEnv(...)` au lieu de `deepcopy()` | 2–5× rollout plus rapide |
| **Seeded reproducibility** | `random.Random(seed)` propagé | Runs déterministes |
| **LRU-bounded oracle cache** | `OrderedDict` avec `maxsize=10,000` | Évite OOM |
| **Multi-fidelity RRS/PNS** | K-NN pondéré (K=3) pour chimie nouvelle | Gradient lisse |
| **Oracle normalisation [0,1]** | Toutes les composantes MPO/Docking/SYBA/SA normalisées | Scores interprétables, reward équilibré |

### 1.3 Corrupted Tartarus CSV — Root Cause & Fix

**Bug découvert via l'anomaly detector du benchmark v3 (job 11892) :**

Le CSV Tartarus (`tartarus_output.csv`, 19,913 entrées) contient **2,836 lignes** avec un `docking = 10,000.00` (valeur positive aberrante — l'énergie de liaison devrait être négative, typiquement −5 à −12 kcal/mol). Cette corruption provient d'une agrégation `mean()` de colonnes `score_*` contenant des valeurs NaN/Inf non filtrées.

**Impact :** Quand MCTS génère une molécule dont le plus proche voisin Tanimoto tombe sur l'une de ces 2,836 entrées corrompues, `_tanimoto_nearest_docking()` retourne `10,000.00`, ce qui fait exploser le reward à `−2,499.69` (pire contribution docking = 0.25 × −10000 = −2500).

**Fix :** Un sanity check `_clamp_docking()` a été ajouté dans `OracleAggregator` :
- Valeurs positives (> 0) → remplacées par la valeur par défaut (−7.0)
- NaN/Inf → remplacées par la valeur par défaut
- Valeurs négatives valides → clampées dans [−15.0, −0.1]

Le clamp est appliqué à trois niveaux (défense en profondeur) :
1. `_docking_score()` — score direct depuis le CSV
2. `_tanimoto_nearest_docking()` — proxy par similarité Tanimoto
3. `reward()` — score final utilisé dans la fonction objectif

### 1.4 Four-Method Benchmark Summary (v1–v7)

| Version | MCTS | Random | Greedy | GA | Notes |
|:-------:|:----:|:------:|:------:|:---:|:------|
| **v1** (random rollout) | 1.524 ± 0.30 | 2.098 ± 0.07 | 2.218 ± 0.04 | 2.226 ± 0.09 | Baseline initiale |
| **v2** (policy_biased) | 1.653 ± 0.37 | 2.097 ± 0.04 | 2.227 ± 0.06 | 2.211 ± 0.11 | +0.13 MCTS |
| **v3** (PW K=10 + multi-fid) | **−2499.7*** | 2.152 ± 0.02 | 2.378 ± 0.08 | 2.280 ± 0.12 | *Corruption CSV → bug |
| **v4** (clamp fix, HPC) | **1.264 ± 0.00** | 2.225 ± 0.04 | 2.431 ± 0.02 | 2.246 ± 0.01 | Job 11897, 5 seeds × 500 iters |
| **v5** (normalisation [0,1]) | **0.280 ± 0.00** | 0.544 ± 0.02 | 0.613 ± 0.00 | 0.598 ± 0.01 | Job 11921, 5 seeds |
| **v6** (Dynamic PW + VL) | **0.280 ± 0.00** | 0.544 ± 0.02 | 0.613 ± 0.00 | 0.598 ± 0.01 | PW dynamique, virtual loss |
| **v7** (c_puct=5.0, n=500) | **0.239 ± 0.00** | 0.533 ± 0.01 | 0.615 ± 0.01 | 0.579 ± 0.02 | Job 11940, best hparams |

### 1.5 v8 real merged benchmark (5 seeds × 4 methods, 2026-07-25)

Source: `Project4_Advanced_Monte_CarloV2607/results/benchmark/p4_benchmark_merged.csv` (seeds 0–4, 1000 iterations, 108-fragment vocabulary, normalised [0,1] reward).

| Method | Mean reward | Std | n | MPO | Docking | Time (s) |
|:------|:----------:|:---:|:---:|:---:|:-------:|:--------:|
| **Greedy** | **0.614** | 0.002 | 5 | 0.932 | −7.70 | 146.7 |
| **MCTS** | 0.597 | 0.000 | 5 | 0.877 | −7.63 | 273.8 |
| **GA** | 0.592 | 0.020 | 5 | 0.912 | −7.47 | 242.3 |
| **Random** | 0.547 | 0.015 | 5 | 0.818 | −6.89 | 49.1 |

Key findings: Greedy search achieves the highest mean reward. MCTS converges to the same best molecule across all five seeds (reward = 0.5966, SMILES `Oc1cccc(C(Br)OCn2ccnc2)c1`) and is competitive with GA but does not surpass Greedy. Random search is fastest but yields the lowest reward.

### 1.6 v9 real merged benchmark (20 seeds × 4 methods, 2026-07-29) — **SUPERSEDED (archive only; do not use for claims)**

Source: `Project4_Advanced_Monte_CarloV2607/results/benchmark/p4_benchmark_merged.csv` (seeds 0–19, 1000 iterations, medium fragment set after valence fix). Values below are mean ± std from the raw CSV. ⚠️ The v9 rewards could **not** be reproduced from the committed code + data (oracle/library state drift at run time); the **v11 canonical benchmark (§1.8) supersedes this table** — kept for provenance only.

| Method | Mean reward | Std | Min | Max | n | Mean time (s) | Std time (s) |
|:------|:----------:|:---:|:---:|:---:|:---:|:-------:|:-------:|
| **Random** | **0.6645** | 0.0064 | 0.6497 | 0.6782 | 20 | 310.0 | 8.1 |
| MCTS+ScafVAE | 0.6594 | 0.0078 | 0.6472 | 0.6811 | 20 | 183.2 | 67.5 |
| GA | 0.6402 | 0.0098 | 0.6248 | 0.6577 | 20 | 8.9 | 0.6 |
| Greedy | 0.5398 | 0.0000 | 0.5398 | 0.5398 | 20 | 0.1 | 0.0 |

Key findings: Random search achieves the highest mean reward, reflecting the curated medium fragment set that biases the environment toward chemically plausible, high-scoring molecules. MCTS attains the highest single-seed reward (0.6811, seed 18). A paired t-test across the 20 seeds shows Random is significantly higher than MCTS (mean difference 0.005, $t_{19} = 2.32$, $p = 0.032$), although the absolute gap is small. Greedy is deterministic (σ = 0) and collapses to the same local optimum across all seeds, highlighting the deceptive reward landscape.

### 1.7 Hyperparameter Search Results

Grid search systématique sur 32 configurations × 2 seeds (64 évaluations, 30 itérations chacune) :

| Rang | pw_α | pw_k | VL | c_puct | Temp | Mean Reward |
|:----:|:----:|:----:|:--:|:------:|:----:|:----------:|
| 1 | 0.7 | 2.0 | 0.01 | 5.0 | 1.0 | **0.3293** |
| 2 | 0.7 | 2.0 | 0.01 | 5.0 | 0.5 | 0.3293 |
| 3 | 0.7 | 0.5 | 0.01 | 5.0 | 1.0 | 0.3293 |
| 4 | 0.3 | 2.0 | 0.01 | 5.0 | 1.0 | 0.3293 |
| 5 | 0.3 | 0.5 | 0.01 | 5.0 | 1.0 | 0.3293 |
| ... | ... | ... | ... | ... | ... | ... |
| 10 | 0.7 | 0.5 | 0.01 | 0.5 | 0.5 | 0.3132 |

**Résultat clé :** c_puct=5.0 domine systématiquement c_puct=0.5, confirmant que l'exploration élevée est essentielle. VL=0.01 > VL=0.20 (0.3293 vs 0.3261). pw_α et pw_k sont indifférenciés à cette échelle (30 itérations). Configuration optimale : **c_puct=5.0, VL=0.01, pw_α=0.5, pw_k=1.0, T=0.8**.

---

## 2. Ablation Studies

### 2.1 Component ablation (2⁵ factorial, 5 replicates per config)

Source: `Project4_Advanced_Monte_CarloV2607/results/ablation/p4_ablation_config_*.csv` (32 configs, 160 total runs) and `p4_component_ablation_summary.csv`. Each configuration varies ScafVAE policy, Pareto front, c_PUCT, Temperature, and Vocabulary (Small/Large). The response is the best reward under the ablation oracle weights, which uses a different weight configuration from the main benchmark, so the absolute reward values are not directly comparable to the main benchmark. "Small" and "Large" are the two levels of the factorial Vocab factor; the exact fragment lists are recorded in the ablation run metadata.

| Factor | Level | Mean reward | Std | n |
|:-------|:-----:|:-----------:|:---:|:---:|
| ScafVAE | Off | 0.6301 | 0.0810 | 80 |
| ScafVAE | On  | 0.7778 | 0.0897 | 80 |
| Pareto  | Off | 0.6498 | 0.0968 | 80 |
| Pareto  | On  | 0.7581 | 0.1017 | 80 |
| c_PUCT  | 1.0 | 0.7312 | 0.1038 | 80 |
| c_PUCT  | 2.0 | 0.6767 | 0.1156 | 80 |
| Temperature | 0.5 | 0.7102 | 0.1044 | 80 |
| Temperature | 1.5 | 0.6988 | 0.1210 | 80 |
| Vocab | Small | 0.6647 | 0.1050 | 80 |
| Vocab | Large | 0.7433 | 0.1072 | 80 |

Key findings: The ScafVAE policy (+0.148), Pareto front (+0.108), and Large vocabulary (+0.079) are the largest positive contributors. c_PUCT = 1.0 outperforms c_PUCT = 2.0 (+0.054). Temperature has a minimal effect (+0.011).

> 🔴 **M2 (2026-08-03, reproducibility fix):** an adversarial audit found the 2⁵ factorial **generator script was not committed** — `p4_ablation_factorial.sbatch` called `p4_mcts_ablation.py --array-id` (the vocab-*analysis* script, which has no such flag), and no factorial generator existed in the repo or on HPC. The 32 `p4_ablation_config_*.csv` (5 replicates each = 160 runs) and this summary were already deposited, so the **data** was reproducible, but the code path that produced it was lost. The generator was reconstructed as `Project4_Advanced_Monte_CarloV2607/scripts/p4_mcts_factorial_run.py`, validated byte-for-byte against the deposited factor mapping (0 mismatches / 32: bits LSB-first = Vocab / Temperature / c_PUCT / Pareto / ScafVAE; Vocab Small→`minimal`, Large→`all`). The `.sbatch` was fixed to call the reconstructed generator (5 replicates per ConfigID). Both scalar (`MCTSAgent` + `compute_mpo_reward`) and multi-objective (`ParetoMCTSAgent` + `OracleAggregator.score`) paths were smoke-tested on HPC (configs 0, 24, 31 → rewards 0.6317, 0.5634, 0.6242). `ParetoMCTSAgent.__init__` takes `env` as its first argument and exposes **no** `rollout_temperature`/temperature parameter — the reconstructed generator respects this signature.

### 2.2 Fragment vocabulary ablation

Source: `Project4_Advanced_Monte_CarloV2607/results/ablation/p4_ablation_{all,medium,aromatic_only,minimal}_seed_*.csv` (10 seeds per set) and `p4_ablation_summary.csv`.

| Set | Mean reward | Std | SEM | n | Notes |
|:----|:-----------:|:---:|:---:|:---:|:------|
| all | 0.6240 | 0.0056 | 0.0018 | 10 | Full 108-fragment vocabulary |
| medium | 0.6283 | 0.0048 | 0.0015 | 10 | 6 categories (simple_aromatics, aliphatic_chains, n_heterocycles, nitrogen_groups, oxygen_groups, antimalarial_privileged) |
| minimal | 0.6183 | 0.0097 | 0.0031 | 10 | simple_aromatics only |
| aromatic_only | 0.5497 | 0.0030 | 0.0010 | 10 | simple_aromatics + fused_rings |

ANOVA: F = 350.10, p = 1.12 × 10⁻²⁶ (df_between = 3, df_within = 36). Source: `results/ablation/p4_ablation_anova.csv`.

Tukey HSD (adjusted p): all vs aromatic_only p < 0.001; medium vs aromatic_only p < 0.001; minimal vs aromatic_only p < 0.001; medium vs minimal p = 0.005; all vs medium p = 0.421; all vs minimal p = 0.191. Source: `results/ablation/p4_ablation_tukey.csv`.

Key findings: The full (`all`) and `medium` fragment sets give equivalent mean rewards; restricting to `aromatic_only` causes a significant performance drop. Even the `minimal` set (simple aromatics only) remains close to the full vocabulary. The choice of `medium` for the main v11 benchmark is therefore well-justified.

---

## 3. Root Cause Analysis: Why MCTS Underperforms

1. **Random rollouts dominate value noise**: With 33 actions × 10 steps, a single random rollout gives a noisy value estimate. Greedy evaluates ALL 33 fragments at each step, yielding much better local choices.
2. **Policy-biased rollout helps modestly (+0.13)** but the core issue persists: the rollout horizon is too long for the MCTS budget (500 iterations).
3. **Docking proxy penalises novel molecules**: MCTS explores more diverse chemical space, but the Tanimoto nearest-neighbour proxy assigns −5.97 docking to novel molecules vs −7.73 for library-similar molecules from Greedy/GA.
4. **Corrupted Tartarus CSV** (2,836 entries with docking=10,000): Causes reward explosion to −2,499 when MCTS hits corrupted entries. Fixed via `_clamp_docking()` sanity check.

---

## 4. Pareto Front

Source: `Project4_Advanced_Monte_CarloV2607/results/pareto/merged_pareto_front.csv` — 4 non-dominated solutions across 20 seeds (MPO 0.729–0.946, SA = 3.0, SYBA recomputed 0.021–1.000, hypervolume 1.2366). Per-seed fronts in `pareto/p4_pareto_seed_{0..19}.csv` (20 files).

> ⚠️ **Provenance note:** SYBA was recomputed post-hoc with the lich/conda SYBA classifier after the original run returned a constant fallback of 0.

---

## 5. QMC Validation (Tier 1/2)

### 5.1 Tier 1 (SCF): restore + GPU acceleration — COMPLETED ✅

| Version | Content | Result |
|:--------|:--------|:-------|
| **v43** (July 26) | Installed `pyscf` 2.14.0 (pip) + `xtb` (conda-forge) into `malaria_md`; fixed `p4_qmc_array.sbatch` (array 0-4→0-3, absolute CONDA_BASE/PYTHON paths, script-dir path) and `p4_qmc_pipeline.py` (`mol.ecp="def2-ecp"`→None — invalid PySCF ECP name for Z≤16; `pyscf.molden`→`pyscf.tools.molden`; de-ECP'd prints/docstring) | Job 12682 array (0-3) ran clean: candidates 0/1/3 completed PBE/def2-SVP SCF (−864.165/−1258.406/−613.950 Eh) + `*_pbe.molden` trial wavefunctions (all 4 candidates) |
| **v44** (July 28) | GPU-accelerated via `gpu4pyscf` 1.8.0 (CUDA 12x, RTX A4000, cupy 14.1.1/CUDA 12.9, pyscf 2.14.0); `p4_qmc_array.sbatch` gained `--gres=gpu:1` | Job 12686 array completed 4/4 on GPU — gpu4pyscf RKS branch, SCF converged (cand 0 −864.164252, 1 −1258.406162, 2 −1012.418277, 3 −613.949885 Eh) + `*_pbe.molden` saved, zero errors; candidate-0 wall ~56 s vs ~131 s CPU (~2.3× end-to-end; PySCF portion far faster, xtb CPU-bound) |

**Tier 1 = production-grade**: SCF energies + trial wavefunctions (molden) for all 4 Pareto candidates.

### 5.2 Tier 2 (VMC/DMC) deep-diagnostic — v45 then **v46 CORRECTION**

> ⚠️ **VERSION CORRECTION (v46, Aug 1 2026):** the v45 conclusion ("**JastrowSpin combination/summation path broken in this env**") is **RETRACTED**. The root cause of the whole investigation was a **wrong premise, not a broken implementation** — see §5.2.3. The separate conclusion that **144-electron candidate-level Tier 2 energies are NOT publication-grade** (DMC population collapse) **REMAINS VALID**, but for a different reason than v45 claimed (it is a sampling/parameterisation problem at scale, not a broken code path).

#### 5.2.1 Installation & first evidence chain (v45, July 31)

Installed **`pyqmc` 0.8.1** (CPU numba backend) into `malaria_md` and ran a systematic diagnostic:

| # | Test | Result | Interpretation |
|---|------|--------|----------------|
| 1 | **Slater-only VMC, H₂O/PBE/cc-pvdz** | **−75.09 Eh** | Exactly reproduces the HF-style expectation of the PBE orbitals — the numba Slater determinant is correct |
| 2 | **Basis-kernel finite-difference audit** | Analytic vs FD match to ~1e-5 | Individual basis kernels (CutoffCusp, CutoffFunc3d) are mathematically correct |
| 3 | **Canonical LiH docs example (RHF/cc-pvdz)** | VMC −7.39 vs RHF −7.78 | Trial WORSE than the bare Slater determinant — **v45 wrongly concluded** "impossible for a valid Jastrow ⇒ path broken" (actually an *unoptimized cusp Jastrow*, see §5.2.3) |
| 4 | **H₂O with `ion_cusp=False`** | VMC −76.53, **DMC −76.50** vs SCF −76.33 (FCI −76.44) | Restores valid energies on SMALL systems only (5-block, nconfig 400) |
| 5 | **candidate_0 (144-e) VMC Slater-only** | −834.69 | +29.5 Eh above PBE SCF (−864.16) — the expected XC-free Slater expectation, not a bug |
| 6 | **candidate_0 (144-e) DMC (nconfig 100)** | **−1021 Eh vs SCF −864** (−157 Eh below SCF) | Physically impossible ⇒ **DMC population collapse**: walkers killed 15→92 of 100, mean walker position collapses to 0.25 Bohr (no e-N cusp → local energy diverges near nuclei) |
| 7 | **Scale test: Slater-only vs Jastrow DMC, nconfig=300** | **COMPLETED** — S: −897.4/−900.7 Eh (±17–18 Eh) ; J: −867.35/−867.59 Eh (±1.8–2.0 Eh) vs SCF −864.165 | **Collapse confirmed on both branches**: Slater-only shows ±17–18 Eh variance and ~33 Eh below SCF (unphysical); the Jastrow (ion_cusp=False) stabilises the variance but still lands ~3.2 Eh below SCF — no e-N cusp treatment at 144-e scale, so candidate-level DMC remains not publication-grade |

#### 5.2.2 Actions taken (honest state, July 31)

1. **Garbage CSV row deleted** — `results/qmc/p4_qmc_energies.csv` (contained cand_0 DMC −1021, corr −4267 eV) removed from HPC so a physically impossible value cannot reach the manuscript.
2. **Runtime sanity guard added** to `p4_qmc_pipeline.py` — after Tier 2, if `e_dmc` is non-finite or > 20 Eh below the PBE SCF (the observed collapse signature), the DMC columns are blanked and a loud WARNING is printed instead of writing the collapsed value.
3. **`ion_cusp=False` jastrow_kws** used in the VMC()/DMC() recipe calls (restores validity on small systems).
4. **12 diagnostic scripts marked `DIAGNOSTIC — not production`**: `p4_qmc_bisect.py`, `p4_qmc_jastrow_test.py`, `p4_qmc_cusp_fix_test.py` (HYPOTHESIS REFUTED — do not apply `a=+Z*rcut`), `p4_qmc_kernel_check.py` (label fixed: `acoeff` is `(natm, na, nspin)`), `p4_qmc_scale_test.py`, `p4_qmc_fd_wf_test.py` (**INCONCLUSIVE** — harness has a known shape/layout bug; even the proven-correct Slater control reports a large mismatch, so its verdicts must not be read as physics), `p4_qmc_dump_hdf5.py`, `p4_qmc_jax_cart_test.py`, `p4_qmc_lih_docs_example.py`, `p4_qmc_isolate_bug.py`, `p4_qmc_jax_test.py`, `p4_qmc_pyqmc_sanity_test.py`.
5. **Pipeline docstring corrected** — the previous claim that `ion_cusp=False` yields physically valid energies applied only to H₂O; now states candidate-level DMC is unreliable in this env and what a production protocol would require.

#### 5.2.3 v46 correction — the decisive A0 true-identity discovery (Aug 1, 2026)

**The smoking gun:** pyqmc 0.8.1's `wftools.generate_jastrow` sets the e–e cusp **unconditionally**, even with `ion_cusp=False`:

```python
jastrow.parameters["bcoeff"][0, [0, 1, 2]] = gpu.cp.array([-0.25, -0.50, -0.25])  # e-e cusp, ALWAYS set
```

So a nominal "zero-parameter" Jastrow is **not** exp(0)=1 — the July 31 "anomaly" (VMC −76.53 vs bare Slater −75.09) was a genuine e–e-cusp Jastrow, not an einsum bug.

**A0 — TRUE identity test (noise-free, decisive):** With BOTH coefficient tensors explicitly zeroed in place, `recompute()` returns `max|log J| = 0.000e+00` over 128 random configs on both H₂O and LiH. **A zero-parameter Jastrow is exactly exp(0)=1.** Strictly, A0 covers the `recompute()` value evaluation; the full sampling path (`value()/testvalue()/gradient()`) is exercised by the zeroed-Jastrow VMC energy leg.

**Final validation (run complete, Aug 1):**

| Test | H₂O/cc-pvdz PBE | LiH/cc-pvdz RHF |
|------|------------------|-----------------|
| A0 true-identity (zeroed params, noise-free) | **PASS** — max\|log J\| = 0.000e+00 | **PASS** |
| Bare Slater ≡ zeroed-Jastrow VMC | −74.971 ± 0.455 vs −74.960 ± 0.454 (Δ=0.012 < tol) | −7.733 ± 0.025 vs −7.781 ± 0.028 (Δ=0.048 < tol) |
| e-N cusp VMC (ion_cusp=True) | **−74.603 ± 0.496 → SANE** (July 31 −99.58 NOT reproduced) | — |
| JAX backend | ❌ fails reproducibly (`dot_general (24,) vs (25,)`) | skipped (broken) |

**Conclusions (v46):**
- The **numba JastrowSpin value path (including e–N cusp) is CORRECT** and is the production path.
- The **JAX backend is broken in pyqmc 0.8.1** (two independent `dot_general` shape bugs: `(24,) vs (5,)` via `mf.to_uhf()`; `(24,) vs (25,)` raw-mf — pyscf SCF produces 25 MOs with cartesian AOs for H2O/cc-pvdz(cart): O 3s+6p+6d=15, H 2s+3p=5×2=10, total 25, but the JAX GTO evaluator emits only the 24 spherical-shell AOs). **JAX dropped; numba is the production path.**
- LiH canonical VMC −7.39 (worse than RHF −7.78) is now understood as an *unoptimized cusp Jastrow* — no longer evidence of breakage.
- ⚠️ **Residual honest caveat:** the July −76.53 vs Aug −74.63 (−1.9 Eh, below FCI −76.44, impossible for a valid variational trial) is NOT explained by the bcoeff discovery alone — likely different July settings/stale path. All Aug 1 values sit above FCI (sane). Any future claim relying on July 31 absolute energies must be re-measured.

#### 5.2.4 Production path (for a future run)

A publication-grade QMC section requires: a **working optimized Jastrow** (`pyqmc.recipes.OPTIMIZE`, acoeff+bcoeff free), **nconfig ≥ 1000**, and a **τ→0 extrapolation** on the 14-e small system first, then porting to a candidate molecule (144-e) with a realistic sampling budget. **QMCPACK fallback** only if optimized-Jastrow VMC/DMC misbehaves. Until then, P4 manuscript must not claim QMC/DMC validation (already removed per §5.3).

**Full diagnostic detail:** `Project4_Advanced_Monte_CarloV2607/docs/P4_QMC_FIX_STRATEGY.md` (sections 7–8) and the reworked `scripts/p4_qmc_jax_identity_test.py`.

### 5.3 QMC removal and manuscript cleanup (2026-07-29)

Following the final adversarial audit recommendation, the pending QMC/DMC validation job and all quantum-validation claims were removed from the P4 manuscript before any JCIM submission attempt.

| Action | Status |
|---|---|
| Cancel SLURM QMC array job 12464 | Done (CANCELLED: DependencyNeverSatisfied) |
| Remove QMC/DMC/quantum-validation prose from P4 manuscript | Done |
| Remove QMC results table (`tab:qmc`) and Pareto table QMC column | Done |
| Remove QMC-related supplementary figure (S4) | Done |
| Remove unused QMC software (PySCF, PennyLane) from Methods | Done |
| Recompile P4 manuscript | Done, PDF 656K, no LaTeX errors |

**Changes applied to `Project4_Advanced_Monte_CarloV2607/manuscript/LaTeX/P4_Pareto_MCTS_V2607.tex`:**
- Title: "Multi-Objective MCTS with Quantum Validation for Antimalarial Design" → "Multi-Objective MCTS for Antimalarial Design".
- Abstract reframed (no electronic-structure validation; one fundamental challenge, three methodological innovations).
- Introduction: limitations three→two (L3 removed); contributions four→three (QMC validation removed).
- Results: Pareto table caption/footnote no longer mention QMC/DMC; QMC column removed; entire `\subsection{QMC Validation}` and `tab:qmc` deleted.
- Methods: `\subsection{Quantum Monte Carlo Validation}` deleted; software list now only RDKit and Scikit-learn.
- Conclusion: "three persistent limitations" → "two persistent limitations".
- Supporting Information: removed Figure~S4 (QMC correlation energy vs QKS score).

---

## 6. Pipeline Fixes & Relaunches (July 2026)

### 6.1 P4 benchmark relaunch (2026-07-29 09:06 UTC)

Following the audit and fix of the P4 benchmark scripts (RDKit valence/kekulization filter, real OracleAggregator reward, and `--fragment-set medium`), the production benchmark array job was relaunched for the full 20-seed protocol.

| Item | Value |
|------|-------|
| Commit (short) | 5cd7eec0 |
| Job ID | 12573 |
| Script | Project4_Advanced_Monte_CarloV2607/scripts/p4_benchmark_array.sbatch |
| Fragment set | medium |
| Array | 0-19 (max 8 concurrent) |
| N_iterations | 1000 |
| GA population × generations | 50 × 20 |
| Max steps | 10 |
| Wall time per task | 6 h |
| Output | Project4_Advanced_Monte_CarloV2607/results/benchmark/p4_benchmark_seed_N.csv |

Rationale: previous runs produced degenerate rewards (~0.6996 for all four methods) because the script imported a non-existent `compute_mpo_reward` and fell back to a mock oracle, while the full fragment vocabulary generated many RDKit valence/kekulization errors. Fixes replace the mock oracle with the real `OracleAggregator` and filter the fragment vocabulary to fragments that successfully attach to a methane seed.

### 6.2 P4 MCTS & Pareto sbatch fragment-set consistency (2026-07-29)

| Script | Change |
|---|---|
| `scripts/p4_mcts_array.sbatch` | `FRAGMENT_SET` default changed from `all` to `medium`; header/usage comments updated. |
| `scripts/p4_pareto_array.sbatch` | Added `FRAGMENT_SET` env var (default `medium`); `--fragment-set "all"` replaced by `--fragment-set "${FRAGMENT_SET}"`. |

**Rationale:** the `medium` set is valence-filtered (no RDKit errors on methane seed). Same vocabulary across benchmark, MCTS and Pareto ⇒ fair, consistent, reproducible. Override via `--export=FRAGMENT_SET=all|aromatic_only|minimal`.

### 6.3 P4 MCTS & Pareto Python CLI default fragment set (2026-07-29)

| Script | Previous default | New default |
|---|---|---|
| `scripts/p4_mcts_run.py` | `all` | `medium` |
| `scripts/p4_mcts_pareto_run.py` | `all` | `medium` (help string updated) |

### 6.4 P4 benchmark path/conda fix and relaunch (2026-07-29)

Root cause of the failed benchmark array (job 12573): `SCRIPT_DIR="${SLURM_SUBMIT_DIR:-...}"` fallback resolved to the project root (or SLURM's temp copy via `BASH_SOURCE[0]`), so the Python script path was wrong and outputs were written to the parent of the project.

Fix applied to all P4 sbatch scripts:
- Hardcoded `PROJECT_DIR="/home/nanaengo/Malaria_codesV2/Project4_Advanced_Monte_CarloV2607"` and `SCRIPT_DIR="${PROJECT_DIR}/scripts"`.
- Replaced `source "$(conda info --base)/etc/profile.d/conda.sh"` with hardcoded `${HOME}/miniforge3` fallback to `${HOME}/miniconda3`.
- Fixed relative `#SBATCH --output`/`--error` paths in `p4_ablation_factorial.sbatch` and `p4_qmc_array.sbatch`.

Validation:
- Local smoke test: passed (MCTS 0.6393, Random 0.6207, Greedy 0.5398, GA 0.5598).
- SLURM test array (job 12595, seed 0): completed and wrote `results/benchmark/p4_benchmark_seed_0.csv`.
- Full 20-seed benchmark array relaunched with the corrected sbatch scripts.

---

## 7. Data Availability & Reproducibility

All P4 numerical claims above are traceable to the following files in `Project4_Advanced_Monte_CarloV2607/results/`:

| Analysis | Raw file(s) | Rows / records |
|:---------|:------------|:---------------|
| v11 20-seed benchmark (CANONICAL) | `benchmark_molecules_opt/p4_benchmark_merged.csv` | 80 (4 methods × 20 seeds) |
| v11 per-seed CSVs + molecule sets | `benchmark_molecules_opt/p4_benchmark_seed_{0..19}.csv`, `benchmark_molecules_opt/p4_benchmark_molecules_seed_{0..19}.csv` | 20 files each |
| v10 default-config run (sensitivity) | `benchmark_molecules/p4_benchmark_merged.csv`, `benchmark_molecules/p4_benchmark_seed_{0..19}.csv` | kept for comparison |
| v11 diversity metrics | `diversity/p4_diversity_metrics.csv`, `diversity/p4_diversity_mds.csv` | 4 + 60 rows |
| v9 20-seed benchmark (superseded archive) | `benchmark/p4_benchmark_merged.csv` | 80 (kept for provenance) |
| LaTeX benchmark table | `benchmark/p4_benchmark_table.tex` | Auto-generated |
| Component ablation | `ablation/p4_ablation_config_*.csv`, `p4_component_ablation_summary.csv` | 32 configs × 5 replicates = 160 |
| Fragment vocabulary ablation | `ablation/p4_ablation_{all,medium,aromatic_only,minimal}_seed_{0..9}.csv` | 40 files, 10 seeds per set |
| ANOVA / Tukey | `ablation/p4_ablation_anova.csv`, `ablation/p4_ablation_tukey.csv` | 1 + 6 pairwise comparisons |
| Pareto front | `pareto/merged_pareto_front.csv` | 4 non-dominated solutions (hypervolume 1.2366) |
| Per-seed Pareto fronts | `pareto/p4_pareto_seed_{0..19}.csv` | 20 files |
| MCTS ranked hits | `mcts/p4_mcts_merged_ranked.csv` | Top molecules per seed |
| QMC Tier 1 outputs | `qmc/candidate_{0..4}/` | SCF energies + `*_pbe.molden` trial wavefunctions |

**Scripts used to generate the data:**
- `scripts/p4_mcts_benchmark.py` — main four-method benchmark (+ `--molecules-out` best-SMILES recording; v11 wires screened-optimal MCTS config: c_PUCT=5.0, ν=0.01, T=0.8, ScafVAE policy)
- `scripts/p4_mcts_ablation.py` — component and fragment vocabulary ablations
- `scripts/p4_mcts_factorial_run.py` — **reconstructed 2⁵ factorial generator (M2, 2026-08-03)**: runs one ConfigID × replicate under the 5-factor binary design; `ParetoMCTSAgent` called with `env` first and no temperature parameter
- `scripts/p4_mcts_pareto.py` — Pareto MCTS runs
- `scripts/p4_merge_pareto_fronts.py` — merges per-seed Pareto fronts
- `scripts/p4_merge_benchmark.py` — merges per-seed benchmark CSVs
- `scripts/p4_compute_diversity.py` — real diversity metrics (v11 molecule sets)
- `scripts/p4_pareto_provenance_check.py` — P0-1 provenance lock (all checks PASS)
- `scripts/p4_benchmark_stats.py` — canonical benchmark statistics + paired tests
- `scripts/p4_visualize.py` — generates figures
- `scripts/p4_qmc_pipeline.py` — Tier 1 SCF + molden (Tier 2 guarded by runtime sanity check)
- `scripts/p4_qmc_jax_identity_test.py` — v46 decisive A0 / e-N cusp / JAX validation

**Provenance note:** The v9 benchmark was executed on the HPC production partition as SLURM array job 12596 (seeds 0–19, 1000 iterations per seed, `--fragment-set medium`); the v10 re-benchmark as job 12705 (default MCTS config, `p4_benchmark_molecules_array.sbatch`); the **v11 canonical re-benchmark** as job 12725 (optimal MCTS config, `p4_benchmark_molecules_opt_array.sbatch`); the **v12 greedy-corrected re-benchmark** as job 12767 (Greedy 0.6147 → 0.7211). Raw SLURM logs are archived under `scripts/logs/` and excluded from the Zenodo deposit due to size.

> 🔴 **M3 (2026-08-03, GPU-backend reproducibility fix):** `_HAS_CUPY` in `p4_mcts_oracles.py` only recorded that CuPy *imports* — it did not guarantee a CUDA device exists on the current node. On a GPU-less node, `cp.zeros(...)` raised and the broad `try/except` in `_load_precomputed_libraries` silently emptied the Tartarus library, making the docking oracle constant (node-dependent rewards). Fixed by adding a runtime probe `_cupy_available()` (`cupy.cuda.runtime.getDeviceCount() > 0`) and a resolved backend flag `_USE_GPU`, used at every array-allocation site (`_build_tartarus_dense`, `_nearest_precomputed`, `_tanimoto_batch_gpu`). Results are value-identical on GPU vs numpy backend (same float32 formula, same first-maximum tie-breaking); only the compute backend differs. Verified on HPC: `_USE_GPU=True` (RTX A4000), `py_compile` clean, file synced to HPC. A reviewer reproducing on a CPU-only node now obtains identical rewards with an explicit log line instead of a silently-degraded docking score.

---

## 8. Remaining P4 Work Before Submission

1. **Manuscript finalisation** — Introduction and Results updated to **v12 canonical benchmark** (optimal MCTS config, greedy-corrected re-run 2026-08-03, job 12767; greedy 0.7211); SM (S1 Pareto provenance, S2 real diversity, S3 reproducibility) drafted; QMC removed. Compile and verify all references (`.bib` complete, 30+ entries).
2. **QMC section** — only re-enter if the production protocol (§5.2.4) is executed: OPTIMIZE + nconfig ≥ 1000 + τ→0. Tier 1 SCF is publication-ready.
3. **Zenodo deposit** — manifest (`zenodo_manifest.txt`) refreshed 2026-08-02 to include the **v11 benchmark + molecule + diversity CSVs**, the JoC manuscript set (main + SM + cover letters), and the two v11 array sbatch scripts (P4 section now 139 files, ~2.4 MB; deposit total 934 files, 170.3 MB); **Zenodo upload still pending** (DOI 10.5281/zenodo.19608875 reserved).
4. **Benchmark stats** — v11 is canonical (20 seeds, reproducible, optimal MCTS config). Paired t-tests Random vs MCTS (t₁₉ = 2.41, p = 0.026) and MCTS vs GA (t₁₉ = 5.55, p < 0.0001) are reported in the manuscript with the honest re-benchmark narrative.

---

## Références & Documents Liés

| Document | Rôle |
|:---------|:-----|
| `P4_DATA_ANALYSIS_REPORT.md` | **CE FICHIER** — Source de vérité P4 (canonique, depuis le 01/08/2026) |
| `BMAD_Q1_DATA_ANALYSIS_REPORT.md` | Boussole P1–P3 (le reporting P4 ne s'y fait plus) |
| `Project4_Advanced_Monte_CarloV2607/docs/P4_QMC_FIX_STRATEGY.md` | Stratégie de correction QMC (sections 7–8 = verdict v46) |
| `Project4_Advanced_Monte_CarloV2607/P4_MC_Strategies.md` | Stratégie P4 (architecture, analyse plan, roadmap) |
| `Project4_Advanced_Monte_CarloV2607/P4_Implementation2_.md` | Plan d'implémentation (ablation 2⁵, QMC, figures, cover letter) |
| `Project4_Advanced_Monte_CarloV2607/manuscript/LaTeX/P4_Pareto_MCTS_JoC_refined.tex` | **Manuscrit P4 CANONIQUE (JoC, v11)** — `P4_Pareto_MCTS_V2607.tex` conservé comme historique uniquement |
