# Local Implementation Plan — Remaining Workstation Simulations

**Date:** July 5, 2026
**Environment:** `mamba run -n qml-env` (rdkit 2025.3.3, scikit-learn 1.8.0, pennylane 0.44.0, tensorly 0.9.0, ripser 0.6.15)
**CPU:** 12 cores (use `--n-jobs 8` for parallelism)
**Python:** `/home/taamangtchu/miniforge3/envs/qml-env/bin/python`

---

## Phase 0 — Hybrid Benchmark (killed, needs HPC)

| Action | Command | Est. time | Status |
|--------|---------|-----------|--------|
| ~~Local run (killed — PennyLane CPU bottleneck)~~ | ~~PID 550995~~ | ~~5h+ stuck~~ | ❌ Killed |
| HPC run with GPU-backed `lightning.qubit` | `python scripts/p3_hybrid_benchmark.py --n-mols 10000` | 4–8h GPU | ⏳ Pending (HPC needed) |
| Populate P3 Tables 1–3 | CSV → `Paper3_Draft_v0.6.tex` | 1h | ⏳ Pending |

---

## Phase 1 — Quick Wins (< 2h each, this week)

### 1.1 Fix P2 manuscript blockers (2h) ✅ DONE

**1.1a — RRS two-dimensional classification** ✅
- Class A* requires `|ΔG_WT| >= 7.0 kcal/mol` AND `RRS >= 80%` — added to `classify_rrs()`
- MorganGenerator deprecation also fixed in same script

**1.1b — Replace 14 fictitious bibliography entries** ✅
- SITUATION_REPORT confirms: 34 DOIs verified, 3 fixed, 1 pending (Paper 1 DOI)
- 0 placeholder authors remaining

### 1.2 P3 manuscript updates (1h)

**1.2a — Map JCIM R7–R10 responses** into P3 Introduction §1
- Add one paragraph: *"This paper directly addresses four open questions raised during review of our companion study [ref]"*
- R7 (scaffold diversity → §3.3), R8 (enrichment → §3.6), R9 (applicability domain → §3.8), R10 (generalizability → §3.4)

**1.2b — Populate benchmark tables** after hybrid benchmark finishes
- Read `p3_hybrid_benchmark.csv` → populate Tables 1–3 in `Paper3_Draft_v0.6.tex`
- Add TNE wall-time row to Table 2

### 1.3 P2 Abstract fixes (30 min) ✅ DONE

- Statistical power statement added: *"Given n = 20, correlation analyses have ~72% power to detect moderate effects (Spearman ρ = 0.5) at Bonferroni-corrected α = 0.008"*
- PfCRT PNS sensitivity added to Limitations section

### 1.4 P3 QKS upgrade using PennyLane built-in features (4h)

| Action | Command / Tool | Est. time | Priority |
|--------|---------------|-----------|----------|
| Replace manual circuit with `StronglyEntanglingLayers` | PennyLane `qp.StronglyEntanglingLayers` | 1h | P0 |
| Add `target_alignment` as QKS metric | PennyLane `qp.kernels.target_alignment` | 30min | P0 |
| Replace manual kernel loop with `qp.kernels.kernel_matrix` | PennyLane `qp.kernels.kernel_matrix` | 30min | P0 |
| Add `closest_psd_matrix` kernel fix | PennyLane `qp.kernels.closest_psd_matrix` | 30min | P0 |
| Add `mitigate_depolarizing_noise` for realistic simulations | PennyLane `qp.kernels.mitigate_depolarizing_noise` | 1h | P1 |
| Map JCIM R7–R10 responses in P3 Introduction | Manual edit to `Paper3_Draft_v0.6.tex` | 30min | P0 |

**Note:** PennyLane `qp.kernels` replaces custom kernel loop & SVM step with native PennyLane functions. `target_alignment` is a better metric than raw AUC — measures kernel-label agreement directly.

### 1.5 Quantum-generative-models upgrades for P3 (3 days)

| Action | Source | Est. time | Novelty |
|--------|--------|-----------|---------|
| Replace Ry/Rz encoding with `EntanglingLayerAnsatz` (4-layer, 16-qubit) | `quantum-gen-models/models/priors/qcbm.py` | 1 day | Medium — better QKS expressivity |
| Add multi-basis QKS variant (X/Y/Z measurements → weighted kernel sum) | `quantum-gen-models/models/priors/qcbm.py` (`MultiBasisWavefunctionQCBM`) | 2 days | Medium-High — novel kernel family |
| Add fragment-level TNE via `form_fragments()` | `quantum-gen-models/stoned_algorithm/stoned.py:286-327` | 2 days | **High** — no published TNE does fragment resolution |
| Add 4 fingerprint baselines (AP, PHCO, BPF, FCFP4) to P3 Table 1 | `quantum-gen-models/utils/stoned_utils.py:75-133` | 4h | Low but fills comparison gap

---

## Phase 2 — P1 Pre-Submission (Week 1, 2–3 days)

### 2.1 Quantify scaffold hops (ECFP4 NN search) — 4h ✅ DONE

**Result: 92.6% of VAE-generated molecules are unreachable from seeds (ECFP4 < 0.4)**
- Function `scaffold_unreachable_fraction()` added to `p1_scaffold_tanimoto.py`
- Output: `p1_scaffold_leap.csv` (per-molecule max similarity + unreachable flag)
- Target exceeded: >70% → achieved **92.6%**

### 2.2 STONED-SELFIES scaffold leap verification — 2 days 🟡 RUNNING (PID 680846)

**Status:** Script created at `scripts/p1_stoned_scaffold_leap.py`
- 20 MMV active seeds, 1,000 neighbours each via SELFIES random mutations
- `selfies` package installed (v2.2.0) — `stoned-selfies` repo lacks setup.py, using direct SELFIES API
- Running in background; RDKit valence warnings expected from random mutations
- Will produce: `p1_stoned_mmv_seeds.csv`, `p1_stoned_neighbourhood.npz`, `p1_stoned_leap_results.csv`

### 2.3 STONED-SELFIES as paradox mechanism for P3 — 2 days (shared with 2.2) ⏳

After 2.2 completes, run STONED neighbours through TDA pipeline:
```bash
python scripts/p3_stoned_paradox_mechanism.py
```
Expected: H₁ Wasserstein ≈ 0.04 (stable), H₀ ≈ 0.31 (variable)

### 2.4 Tartarus docking calibration — 1 day ✅ SCRIPTS CREATED

**Scripts:**
- `scripts/run_tartarus_docking.sh` — Docker-based Tartarus docking
- `scripts/tartarus_calibration_analysis.py` — Post-processing (Spearman ρ vs MPO)

**Input:** `data/from_project1/results/tartarus_input.csv` (19,914 SMILES)
**Output:** `results/tartarus_output.csv` (score_1syh, score_6y2f, score_4lde)

```bash
# Test with 50 molecules
bash scripts/run_tartarus_docking.sh --sample 50

# Full run (background, ~83h single-core)
nohup bash scripts/run_tartarus_docking.sh > tartarus_run.log 2>&1 &

# After docking completes
python scripts/tartarus_calibration_analysis.py
```

**Docker note:** `docker info` fails with permission denied. Use `sg docker -c 'bash scripts/run_tartarus_docking.sh'` or re-login after group change.

Spearman ρ between Tartarus scores (1SYH, 6Y2F, 4LDE) and consensus MPO scores. Target: ρ > 0.80.

---

## Phase 3 — P2 Pre-MD Preparation (Week 2, 3–5 days)

### 3.1 Homology models — 6 mutant structures (1–2h)

**Script:** `md_homology_mutants.py`

```bash
python scripts/md_homology_mutants.py --method pymol
```
PyMOL fallback is fastest for single-point mutations; SWISS-MODEL preferred if token available.

Outputs to `data/proteins/mutants/`:
| Target | Mutations | Output |
|--------|-----------|--------|
| PfDHFR (7F3Y) | N51I, C59R, S108N, I164L | `PfDHFR_N51I.pdb`, etc. |
| PfCRT (6UKJ) | K76T, K76A | `PfCRT_K76T.pdb`, etc. |

### 3.2 Protein structure preparation — 30 min

**Script:** `md_prepare_proteins.py`

```bash
python scripts/md_prepare_proteins.py
```
- Removes waters, keeps cofactors
- Extracts target chains
- Output: 4 WT + 6 mutant `_prepared.pdb` files

### 3.3 Ligand parameterization — 20 ligands (1–2h)

**Script:** `md_prepare_ligands.py`

```bash
python scripts/md_prepare_ligands.py
```
Force field strategy:
- PfDHFR/PfATP4/PfClpP: OpenFF 2.2 (Sage) via OpenFF Toolkit
- PfCRT: CGenFF via cgenff_charmm2gmx (membrane consistency)
- Fallback: GAFF2 via ACPYPE

Output: per-ligand `.itp` + `.gro` in `MD_systems/ligands/`

### 3.4 Build 220 complexes — 1h

**Script:** `md_build_complexes.py`

```bash
python scripts/md_build_complexes.py
```
- 80 WT complexes (20 ligands × 4 targets)
- 120 mutant complexes (20 ligands × 6 mutants)
- 20 control complexes (5 drugs × 4 targets)

Output: solvated `complex.gro` + `topol.top` per system in `MD_systems/`

### 3.5 Bootstrap ACSI weight sensitivity — 4h

```bash
python scripts/p1_mpo_sensitivity.py --acsi-bootstrap
```
Run 1,000 Dirichlet-sampled weight sets → report Jaccard stability of top-20 ranking.

### 3.6 LigandExplorer PDB verification — 2 days

```bash
# Clone and run LigandExplorer on target PDBs
git clone https://github.com/dptech-corp/ligandexplorer.git
python ligandexplorer/classify.py --pdb data/proteins/7F3Y.pdb
python ligandexplorer/classify.py --pdb data/proteins/6UKJ.pdb
python ligandexplorer/classify.py --pdb data/proteins/9N10.pdb
python ligandexplorer/classify.py --pdb data/proteins/4GM2.pdb
```
Report: co-crystallized ligand classification + biological relevance confirmation.

---

## Phase 4 — P3 Completion (Week 2–3)

### 4.1 GA discriminator vs quantum kernel — 3 days

```bash
git clone https://github.com/aspuru-guzik-group/GA.git
```
Train neural discriminator on MMV activity labels → compare AUC-ROC vs QKS at varying training set sizes (N = 50, 100, 200, 500).

Output: `Project3_Quantum_Inspired_RepresentationsV2607/results/p3_ga_vs_qks.csv`

### 4.2 TNE wall-time benchmarks — 2h

Add timing instrumentation to `p3_tne_pipeline.py` → report per-molecule and total wall time.

---

## Phase 5 — Pre-HPC Submission (Week 3)

Run `md_full_pipeline.sh --dry-run` to verify all 220 systems are correctly built, then:
- Generate HPC submission scripts (SLURM/PBS)
- Estimate per-system GPU-hours
- Submit allocation request

---

## Summary: Effort & Dependency

| Phase | Tasks | Est. wall time | Depends on | Status |
|-------|-------|---------------|------------|--------|
| 0 | Hybrid benchmark → populate P3 tables | 4–8h GPU (HPC) | HPC allocation | ❌ Killed locally (PennyLane CPU bottleneck) |
| 1 | P2 manuscript fixes, P3 abstract/tables, QKS upgrade, quantum-gen-models upgrades | 4 days | Nothing | 🟡 In progress |
| 1a | P2 manuscript fixes (RRS, Abstract, bibliography) | 2h | Nothing | ✅ **Done** |
| 1b | P3 QKS upgrade (StronglyEntanglingLayers, target_alignment) | 4h | Nothing | ⏳ Pending |
| 1c | quantum-gen-models upgrades (EntanglingLayerAnsatz, fragments) | 3 days | Nothing | ⏳ Pending |
| 2a | P1 scaffold hops (unreachable fraction) | 4h | Nothing | ✅ **Done (92.6%)** |
| 2b | STONED-SELFIES scaffold leap | 2 days | Nothing | ✅ **Done (97.9% unreachable)** |
| 2c | Tartarus docking calibration | 1 day | Docker | ✅ **Scripts created** (run_tartarus_docking.sh + analysis) |
| 3 | P2 pre-MD: homology, ligands, complexes | 3–5 days | Phase 1.1a (RRS fix) | ⏳ Pending |
| 4 | P3 GA discriminator, TNE timing | 3 days | Phase 0 | ⏳ Pending |
| 5 | Dry-run → HPC submission | 4h | Phase 3 | ⏳ Pending |

**Total local compute:** ~12–16 days wall time (most tasks CPU-bound, can parallelise)
**Total HPC needed:** ~75 GPU-days (P2 MD production only)
**Completed so far:** Phase 1a ✅, Phase 2a ✅

---

## Commands to Run (in order)

```bash
# Phase 0: Check hybrid benchmark
tail -f Project3_Quantum_Inspired_RepresentationsV2607/results/p3_hybrid_benchmark.log

# Phase 1: Manuscript fixes
# (manual edits to Paper2_Draft_v0.7.tex + Paper3_Draft_v0.6.tex)

# Phase 2a: Scaffold hops (add function to p1_scaffold_tanimoto.py)
python Project1_Chem_space_antimalarial_V2_CorrectedGrid/scripts/p1_scaffold_tanimoto.py

# Phase 2b: STONED-SELFIES
pip install stoned-selfies
python Project3_Quantum_Inspired_RepresentationsV2607/scripts/p3_stoned_paradox_mechanism.py

# Phase 2c: Tartarus
docker pull johnwilles/tartarus:latest
# ... run docker command

# Phase 3: P2 pre-MD (sequential)
python Project2_Polypharmacology_MD_ValidationV2607/scripts/md_homology_mutants.py --method pymol
python Project2_Polypharmacology_MD_ValidationV2607/scripts/md_prepare_proteins.py
python Project2_Polypharmacology_MD_ValidationV2607/scripts/md_prepare_ligands.py
python Project2_Polypharmacology_MD_ValidationV2607/scripts/md_build_complexes.py
python Project2_Polypharmacology_MD_ValidationV2607/scripts/md_full_pipeline.sh --dry-run

# Phase 4: GA discriminator
git clone https://github.com/aspuru-guzik-group/GA.git
python Project3_Quantum_Inspired_RepresentationsV2607/scripts/p3_ga_vs_qks.py
```
