# Results Directory

## 📁 Directory Structure

```
results/
├── analysis/              # Analysis outputs and computed metrics
├── candidate_selection/   # Selected compounds for MD validation
├── figures/              # Generated plots and visualizations
├── md_systems/           # MD system setups and configurations
├── metrics/              # Calculated metrics (RRS, ACSI, PNS)
├── mutant_structures/    # Generated resistance mutant structures
├── tables/               # Data tables for manuscript
└── trajectories/         # MD trajectory files (LARGE - git-ignored)
```

## 📊 Result Categories

### 🎯 Candidate Selection (`candidate_selection/`)
**Purpose**: Selected compounds for MD validation studies

**Current Files**:
- `md_top20_candidates.csv`: Top 20 candidates with comprehensive scoring
- `md_top20_smiles.smi`: SMILES strings for structure generation
- `mpo_sensitivity_analysis.csv`: JCIM R2 compliance analysis

**Key Metrics**:
- **Success Rate**: 18.3% (17/93 molecules pass all filters)
- **MPO Score Range**: 0.514 - 0.550 (primary leads)
- **Synthesizability**: All candidates SYBA > 0
- **Selectivity**: Mean SI = 90.6

### 🧬 MD Systems (`md_systems/`)
**Purpose**: Prepared molecular dynamics systems

**Structure**:
```
md_systems/
├── system_001_compound001_4gm2_wt/
├── system_002_compound001_4gm2_mut/
├── system_003_compound001_6ukj_wt/
└── ... (160 total systems)
```

**System Naming**: `system_{ID}_{compound}_{target}_{variant}`
- **ID**: Sequential system identifier
- **compound**: Compound identifier (001-020)
- **target**: Protein target (4gm2, 6ukj, 7f3y, 9n10)
- **variant**: Wild-type (wt) or mutant (mut)

### 📈 Analysis (`analysis/`)
**Purpose**: Computed analysis results and derived data

**Expected Contents**:
- Binding affinity calculations
- Structural analysis results
- Statistical comparisons
- Cross-validation results

### 📊 Metrics (`metrics/`)
**Purpose**: Novel metrics for polypharmacology assessment

**Key Metrics**:
- **RRS (Resistance Resilience Score)**: Activity retention against mutants
- **ACSI (Activity Conservation Score Index)**: Multi-target activity preservation
- **PNS (Polypharmacology Network Score)**: Network-based polypharmacology assessment

### 🧪 Mutant Structures (`mutant_structures/`)
**Purpose**: Generated resistance mutant protein structures

**Targets and Mutations**:
- **4GM2 (PfClpP)**: [Specific mutations to be determined]
- **6UKJ (PfCRT)**: K76T, N75E, M74I, A220S
- **7F3Y (PfDHFR)**: S108N, N51I, C59R, I164L
- **9N10 (PfATP4)**: [Specific mutations to be determined]

### 📋 Tables (`tables/`)
**Purpose**: Formatted data tables for manuscript

**Expected Tables**:
- Candidate selection summary
- MD simulation parameters
- Binding affinity comparisons
- Statistical analysis results

### 📊 Figures (`figures/`)
**Purpose**: Generated plots and visualizations

**Figure Categories**:
- Candidate selection flowcharts
- MD trajectory analysis plots
- Binding mode comparisons
- Statistical distribution plots

### 🎬 Trajectories (`trajectories/`)
**Purpose**: MD simulation trajectory files

**⚠️ Important Notes**:
- **Git-ignored**: Files are too large for version control
- **Storage**: Use local/HPC storage or cloud solutions
- **Backup**: Implement separate backup strategy
- **Access**: Document location for collaborators

**Expected Size**: ~30 TB total (160 systems × ~187 GB each)

## 📋 File Naming Conventions

### Candidate Selection
```
candidate_selection/
├── md_top{N}_candidates.csv      # N = number of candidates
├── md_top{N}_smiles.smi          # SMILES for structure generation
└── mpo_sensitivity_analysis.csv  # Sensitivity analysis results
```

### MD Systems
```
md_systems/
└── system_{ID}_{compound}_{target}_{variant}/
    ├── system.gro                # Initial coordinates
    ├── system.top                # Topology file
    ├── md_params.mdp             # MD parameters
    └── analysis/                 # System-specific analysis
```

### Analysis Results
```
analysis/
├── binding_affinities_{date}.csv
├── structural_analysis_{date}.csv
└── statistical_comparisons_{date}.csv
```

### Figures
```
figures/
├── candidate_selection_flowchart.png
├── md_trajectory_analysis.png
├── binding_mode_comparison.png
└── manuscript_figures/
    ├── figure_1_candidate_selection.png
    ├── figure_2_md_overview.png
    └── figure_3_results_summary.png
```

## 📊 Data Management

### Size Guidelines
| Directory | Typical Size | Max Size | Git Tracked |
|-----------|-------------|----------|-------------|
| analysis/ | 10-100 MB | 1 GB | Yes |
| candidate_selection/ | 1-10 MB | 50 MB | Yes |
| figures/ | 10-100 MB | 500 MB | Yes (selective) |
| md_systems/ | 100 MB - 1 GB | 10 GB | Yes |
| metrics/ | 1-10 MB | 100 MB | Yes |
| mutant_structures/ | 10-50 MB | 200 MB | Yes |
| tables/ | 1-10 MB | 50 MB | Yes |
| trajectories/ | **10-30 TB** | **50 TB** | **NO** |

### Backup Strategy
- **Small files** (<1 GB): Git version control
- **Medium files** (1-10 GB): Cloud storage (Google Drive, Dropbox)
- **Large files** (>10 GB): HPC storage with backup policy
- **Critical results**: Multiple backup locations

## 🔄 Result Generation Workflow

### Phase 1: Candidate Selection
```bash
# Generate candidates
python scripts/revision/md_select_top20_refined.py --n 20 --sensitivity

# Results → candidate_selection/
```

### Phase 2: System Preparation
```bash
# Prepare MD systems
python scripts/md/md_prepare_ligands.py
python scripts/md/md_prepare_proteins.py
python scripts/md/md_build_complexes.py

# Results → md_systems/
```

### Phase 3: MD Simulations
```bash
# Run simulations (HPC)
bash scripts/md/md_full_pipeline.sh

# Results → trajectories/ (git-ignored)
```

### Phase 4: Analysis
```bash
# Calculate metrics
python scripts/md/md_calculate_rrs_acsi_pns.py

# Results → analysis/, metrics/
```

### Phase 5: Visualization
```bash
# Generate figures
python scripts/analysis/generate_2d_interaction_diagrams.py

# Results → figures/
```

## 📋 Quality Control

### Data Validation
- **Completeness**: All expected files present
- **Format consistency**: Standardized file formats
- **Size validation**: Files within expected size ranges
- **Content validation**: Data integrity checks

### Validation Scripts
```bash
# Check result completeness
python scripts/maintenance/consistency_audit.py

# Validate specific results
python scripts/maintenance/final_consistency_audit.py --results-only
```

## 📊 Current Status

### ✅ Completed
- **Candidate Selection**: 17+5 compounds (MPO-ranked + named consensus hits 201,214,87,438,164)
- **Sensitivity Analysis**: JCIM R2 compliance demonstrated
- **RRS Classification**: 14 polypharm scaffolds classified (A*:1, A:3, B:2, C:7, D:1) — see `c_rrs_classification.csv`
- **PP-11 C59R Investigation**: Complete mechanistic analysis in `analysis/PP11_C59R_investigation.md`
- **Named Ligand Docking**: 5 ligands × 6 mutants pending (job 7948)
- **Mutant Structures**: All 6 homology models generated (QMEAN -0.15 to -1.52, GMQE 0.78–0.98)

### 🔄 In Progress
- **MD System Preparation**: Setting up 160 simulation systems
- **P3 QI Optimization**: 5K molecules, n_repeats=2, n_kpca=20 (job 7943, running)
- **TNE bond_dim=16**: 768 features (job 7945, pending)

### 📅 Planned
- **MD Simulations**: 30,000 ns total simulation time
- **RRS/ACSI/PNS Integration**: Cross-metric correlation analysis
- **Manuscript Figures**: Publication-ready visualizations

## 🔗 Integration with Manuscript

### Table References
- **Table 1**: Candidate selection summary → `tables/candidate_summary.csv`
- **Table 2**: MD simulation parameters → `tables/md_parameters.csv`
- **Table 3**: Binding affinity results → `tables/binding_affinities.csv`

### Figure References
- **Figure 1**: Candidate selection workflow → `figures/candidate_selection_flowchart.png`
- **Figure 2**: MD simulation overview → `figures/md_overview.png`
- **Figure 3**: Results summary → `figures/results_summary.png`

## 🛠️ Maintenance

### Regular Tasks
- **Weekly**: Check disk usage, especially trajectories/
- **Monthly**: Validate result integrity
- **Before submission**: Run final consistency audit

### Cleanup Commands
```bash
# Clean temporary files
find results/ -name "*.tmp" -delete
find results/ -name "*.log" -delete

# Compress old results
tar -czf results_backup_$(date +%Y%m%d).tar.gz results/analysis/
```

## 🔗 Related Documentation

- [Project Overview](../docs/project_overview.md)
- [MD Simulation Protocol](../docs/md_simulation_protocol.md)
- [JCIM Roadmap](../JCIM_COMPLIANT_ROADMAP.md)
- [Script Documentation](../scripts/README.md)

---

**Note**: The trajectories/ directory contains very large files (>10 TB total) and is git-ignored. Implement appropriate backup and sharing strategies for these critical simulation results.