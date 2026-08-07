# Malaria Codes - Docking Experiments

This directory contains scripts, configuration files, and results for molecular docking experiments carried out as part of the antimalarial drug discovery project. Two complementary docking methodologies are employed: standard structure-based molecular docking utilizing **AutoDock Vina 1.2.7** and deep learning-based blind docking via **DiffDock-L**.

## Key Statistics

| Metric | Value | Description |
|--------|-------|-------------|
| **Docking targets** | **4** | PfDHFR (7F3Y), PfCRT (6UKJ), PfATP4 (9N10), PfClpR (4GM2; not PfClpP) |
| **Centroids docked** | **~469** | K-Means cluster representatives |
| **Total docking poses** | **~18,760** | 469 × 4 targets × 10 poses/ligand |
| **Polypharmacological candidates** | **>70** | Engaging ≥2 targets simultaneously |
| **DiffDock-Vina orthogonality** | **r = -0.049** | Pooled (confirms independence) |

## Directory Structure

### AutoDock Vina Docking (`Docking_*`)
Folders named `Docking_<TargetID>` contain target-specific AutoDock Vina experiments:

| Directory | Target | PDB ID | Description | Success Rate |
|-----------|--------|--------|-------------|--------------|
| `Docking_7F3Y/` | PfDHFR | 7F3Y | Dihydrofolate reductase | 37.2% (8 EXCELLENT, 160 GOOD) |
| `Docking_6UKJ/` | PfCRT | 6UKJ | Chloroquine resistance transporter | 85.3% (91 EXCELLENT, 294 GOOD) |
| `Docking_9N10/` | PfATP4 | 9N10 | Sodium efflux pump | 0.2% (1 GOOD: Ligand 438) |
| `Docking_4GM2/` | PfClpR | 4GM2 | ClpR paralog/subunit; not PfClpP | 0.0% (historical negative control) |

Each folder typically includes:
- Target structure in `.pdbqt` format
- Grid box constraints configuration file (`config.txt`)
- Job submission scripts (`submit_dock_*.sh`)
- A `results_consensus` subdirectory, which categorizes docked ligands into `EXCELLENT`, `GOOD`, and `OTHERS` based on binding affinity

### DiffDock Inference (`results_inference`)
This directory contains output from the **DiffDock-L** deep learning model.
- Subdirectories generated for each ligand-target pair (e.g., `7F3Y_mol_201`)
- 10 poses per ligand with confidence scores
- Rank1 poses extracted for consensus scoring

## Named Consensus Hits

| Ligand | Target | Vina (kcal/mol) | DiffDock conf. | Notes |
|--------|--------|-----------------|----------------|-------|
| 201 | PfDHFR | −8.49 | −0.30 | Primary consensus lead |
| 214 | PfDHFR | — | — | Primary consensus lead |
| 87 | PfDHFR | — | — | Primary consensus lead |
| 438 | PfATP4 | −5.86 | −0.95 | Single GOOD hit; highest-priority for PfATP4 |
| 164 | PfClpP | −6.19 | −0.40 | Polypharmacological (multi-target) |
| 440, 169, 161 | Multi-target | < −6.0 | > −1.0 | Polypharmacological candidates |

## Key Scripts

- **`consensus_scoring_vina.sh`**
  A robust workflow script for AutoDock Vina (version 1.2.7) that runs a consensus scoring mechanism. It evaluates each ligand against a target using both the standard `vina` scoring function and the `vinardo` scoring function. It extracts the best binding affinity and categorizes the results into `EXCELLENT` (<= -9.0 kcal/mol), `GOOD` (<= -7.0 kcal/mol), and `OTHERS`. Results are logged progressively to a summary CSV file.

## Docking Pipeline

### Dual-Filter Consensus Approach

```
K-Means Centroids (n=469)
      ↓
┌─────────────────────────────────────┐
│  DiffDock-L                         │
│  - 10 poses/ligand                  │
│  - Confidence score (c)             │
│  - Geometric scoring                │
└─────────────────────────────────────┘
      ↓
┌─────────────────────────────────────┐
│  AutoDock Vina 1.2.7                │
│  - vina + vinardo scoring           │
│  - Thermodynamic scoring            │
│  - Pearson r ≈ 0.1-0.4 vs DiffDock  │
└─────────────────────────────────────┘
      ↓
┌─────────────────────────────────────┐
│  5-Component MPO Scorer             │
│  - Vina: 35%                        │
│  - DiffDock: 25%                    │
│  - QED: 20%                         │
│  - ADMET: 15%                       │
│  - Ro5 penalty: 5%                  │
└─────────────────────────────────────┘
      ↓
Primary Leads (MPO ≥ 0.70): 20,466
Secondary Hits (0.50 ≤ MPO < 0.70): 37,138
```

### DiffDock-Vina Orthogonality

Per-target Pearson correlations confirm scoring function independence:

| Target | r | p-value | n | Interpretation |
|--------|---|---------|---|----------------|
| PfDHFR (7F3Y) | 0.327 | 2.11×10⁻⁸ | 280 | Weak correlation |
| PfCRT (6UKJ) | 0.129 | 3.08×10⁻¹ | 64 | Not significant |
| PfATP4 (9N10) | 0.113 | 1.67×10⁻² | 447 | Weak correlation |
| PfClpR (4GM2) | 0.361 | 3.58×10⁻¹⁵ | 447 | Weak correlation |
| **Pooled** | **-0.049** | **8.19×10⁻²** | **1,238** | **Not significant** |

> **Identity caveat:** PDB 4GM2 is PfClpR rather than PfClpP; these historical 4GM2 records must not be used as PfClpP validation.\n\n> **Conclusion:** Low correlations (all < 0.5) confirm DiffDock (geometric) and Vina (thermodynamic) capture independent aspects of protein-ligand interaction, validating the dual-filter consensus approach.

## Data & Results CSV Files

The root level of this directory contains consolidated datasets:

| File | Description |
|------|-------------|
| `diffdock_summary.csv` | DiffDock confidence scores and estimated affinities |
| `combined_docking_results.csv` | Aggregated AutoDock Vina + DiffDock results |
| `docking_results_with_smiles.csv` | Docking results with SMILES for ML/cheminformatics |
| `smiles_with_scores.csv` | SMILES → docking scores mapping |
| `smiles_with_scores_prop.csv` | SMILES → scores + physicochemical properties |
| `ANP_MPO_Ranked_Final.csv` | MPO-ranked African Natural Products and SD derivatives |

## Usage Remarks
These files are tightly integrated with the python scripts found in the `../src/malaria_explorer/scripts/` directory, which handle the extraction of SMILES, combining results matrices, running MPO scoring, and generating 2D interaction diagrams.

---

**Last Updated:** April 8, 2026
**Docking Status:** ✅ Complete (469 centroids × 4 targets)
**Manuscript Integration:** §3.4 Dual-Filter Consensus Docking
