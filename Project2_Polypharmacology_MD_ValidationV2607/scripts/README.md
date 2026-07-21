# Scripts Directory

## 📁 Directory Structure

```
scripts/
├── analysis/          # Data analysis and visualization scripts
├── maintenance/       # Project maintenance and utility scripts
├── md/               # Molecular dynamics simulation pipeline
├── paper3/           # Future work and Paper 3 preparation
├── pipeline/         # Core computational pipeline (from Project 1)
└── revision/         # JCIM revision scripts (refined versions)
```

## 🎯 Script Categories

### 🔬 Analysis Scripts (`analysis/`)
**Purpose**: Data analysis, visualization, and manuscript calculations

**Key Scripts**:
- `manuscript_calculations_c1_c8.py`: Core manuscript calculations
- `manuscript_calculations_c9_c12.py`: Extended calculations
- `compute_tanimoto_novelty.py`: Structural novelty analysis
- `r8b_polypharmacology_analysis.py`: Polypharmacology assessment
- `generate_2d_interaction_diagrams.py`: Molecular interaction plots

**Usage**:
```bash
# Run manuscript calculations
python scripts/analysis/manuscript_calculations_c1_c8.py

# Generate interaction diagrams
python scripts/analysis/generate_2d_interaction_diagrams.py --input results/md_systems/
```

### 🛠️ Maintenance Scripts (`maintenance/`)
**Purpose**: Project maintenance, auditing, and quality control

**Key Scripts**:
- `consistency_audit.py`: Comprehensive project validation
- `final_consistency_audit.py`: Pre-submission validation
- `roadmap_audit.py`: Progress tracking against roadmap
- `clean_notebooks.py`: Jupyter notebook cleanup

**Usage**:
```bash
# Run full project audit
python scripts/maintenance/consistency_audit.py

# Clean notebook outputs
python scripts/maintenance/clean_notebooks.py
```

### 🧬 MD Scripts (`md/`)
**Purpose**: Molecular dynamics simulation pipeline

**Key Scripts**:
- `md_run_em_nvt_npt.py`: **Active production run script** — EM → NVT → NPT for all 4 complexes
- `md_full_pipeline.sh`: Complete MD workflow (wrapper)
- `md_prepare_ligands.py`: Ligand preparation and parameterization
- `md_prepare_proteins.py`: Protein structure preparation
- `md_build_complexes.py`: Protein-ligand complex assembly
- `md_homology_mutants.py`: Generate resistance mutant structures
- `md_calculate_rrs_acsi_pns.py`: Calculate novel metrics

**HPC usage** (Tailscale node `nanaengo@100.73.21.40`):
```bash
# Transfer script
rsync -avz -e "ssh -i ~/.ssh/taiscale_key" scripts/md_run_em_nvt_npt.py \
  nanaengo@100.73.21.40:~/Malaria_codesV2/Project2_.../scripts/

# Launch
ssh -i ~/.ssh/taiscale_key nanaengo@100.73.21.40 bash << 'EOF'
source ~/miniforge3/etc/profile.d/conda.sh && conda activate malaria_md
cd ~/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607
nohup python -u scripts/md_run_em_nvt_npt.py --complex all \
  > logs/md_run_em_nvt_npt.log 2>&1 &
EOF

# Monitor
ssh -i ~/.ssh/taiscale_key nanaengo@100.73.21.40 \
  "tail -f ~/Malaria_codesV2/.../logs/md_run_em_nvt_npt.log"
```

> **Note:** Always use `gmx_mpi` (full path), set `GMXLIB`, and omit `-ntmpi`.
> See `md_simulation_protocol.md` §Known Issues for details.

### 🔄 Pipeline Scripts (`pipeline/`)
**Purpose**: Core computational pipeline inherited from Project 1

**Key Scripts**:
- `MPO_scorer_refined.py`: Refined MPO scoring (10x performance)
- `MPO_scorer.py`: Original MPO scorer
- `combine_docking_results.py`: Aggregate docking outputs
- Various clustering and similarity search scripts

**Usage**:
```bash
# Run refined MPO scorer
python scripts/pipeline/MPO_scorer_refined.py --config scripts/pipeline/mpo_config.yaml
```

### ✨ Revision Scripts (`revision/`)
**Purpose**: JCIM-compliant refined scripts addressing reviewer concerns

**Key Scripts**:
- `md_select_top20_refined.py`: Advanced candidate selection with sensitivity analysis
- `demo_refined_scripts.py`: Demonstration of improvements
- Configuration files: `selection_config.yaml`, `config.yaml`

**Usage**:
```bash
# Select candidates with sensitivity analysis (JCIM R2 compliance)
python scripts/revision/md_select_top20_refined.py --n 20 --sensitivity

# Run demonstration
python scripts/revision/demo_refined_scripts.py
```

### 📄 Paper 3 Scripts (`paper3/`)
**Purpose**: Future work preparation and Paper 3 development

**Contents**:
- Environment specifications for GNN and advanced ML methods
- Placeholder scripts for future development

## 🚀 Quick Start Guide

### 1. Environment Setup
```bash
# Create MD environment
conda env create -f ../environments/environment_md.yml
conda activate md_validation

# Verify installation
python maintenance/consistency_audit.py
```

### 2. Candidate Selection
```bash
# Run refined candidate selection
python revision/md_select_top20_refined.py --n 20 --sensitivity --log-level INFO
```

### 3. MD Pipeline
```bash
# Prepare ligands
python md/md_prepare_ligands.py

# Prepare proteins
python md/md_prepare_proteins.py

# Build complexes
python md/md_build_complexes.py

# Run MD simulations (requires HPC)
bash md/md_full_pipeline.sh
```

### 4. Analysis
```bash
# Calculate manuscript metrics
python analysis/manuscript_calculations_c1_c8.py

# Generate figures
python analysis/generate_2d_interaction_diagrams.py
```

## 📋 Script Standards

### Code Quality
- **Type hints**: All functions should include type annotations
- **Docstrings**: Comprehensive documentation for all modules
- **Error handling**: Graceful degradation with informative messages
- **Logging**: Use structured logging for debugging and monitoring

### Configuration Management
- **YAML/JSON configs**: Externalize parameters
- **Command-line interfaces**: Use argparse for user-friendly CLIs
- **Environment variables**: Support for different execution environments

### File Path Management
All scripts use **relative paths** from the Project2 root directory:
```python
# Good: Relative to Project2 root
input_file = "data/from_project1/docking/ANP_MPO_Ranked_Final.csv"
output_dir = "results/candidate_selection/"

# Avoid: Absolute paths
input_file = "../../data/docking/..."
```

## 🔧 Development Guidelines

### Adding New Scripts
1. **Choose appropriate directory** based on script purpose
2. **Follow naming conventions**: `verb_noun_description.py`
3. **Include comprehensive docstring** with usage examples
4. **Add to this README** with brief description
5. **Update relevant documentation**

### Script Template
```python
#!/usr/bin/env python3
"""
Brief description of script purpose.

Usage:
    python script_name.py --input data/input.csv --output results/output.csv

Author: [Name]
Date: [Date]
Project: Malaria Project 2 - MD Validation
"""

import argparse
import logging
from pathlib import Path
from typing import Optional

def setup_logging(level: str = "INFO") -> logging.Logger:
    """Configure logging."""
    logging.basicConfig(level=getattr(logging, level.upper()))
    return logging.getLogger(__name__)

def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description="Script description")
    parser.add_argument("--input", required=True, help="Input file path")
    parser.add_argument("--output", required=True, help="Output file path")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    
    args = parser.parse_args()
    logger = setup_logging(args.log_level)
    
    # Script logic here
    logger.info("Script completed successfully")

if __name__ == "__main__":
    main()
```

## 📊 Performance Considerations

### Refined Scripts Performance
- **MPO Scorer**: 10x improvement (1.3s vs 45s for 451 molecules)
- **Candidate Selection**: Vectorized operations for large datasets
- **Memory Efficiency**: Optimized for datasets >100k molecules

### HPC Integration
- **SLURM compatibility**: MD scripts include job submission templates
- **Parallel processing**: Multi-core support where applicable
- **Resource estimation**: Memory and time requirements documented

## 🔗 Dependencies

### Core Dependencies
```yaml
# From environment_md.yml
- python>=3.8
- rdkit
- pandas
- numpy
- scipy
- matplotlib
- seaborn
- jupyter
```

### Optional Dependencies
```yaml
# For advanced features
- openeye-toolkits  # Commercial license required
- schrodinger       # Academic license required
- gromacs          # MD simulations
- pymol            # Visualization
```

## 📋 Testing and Validation

### Unit Tests
```bash
# Run tests (when implemented)
pytest scripts/tests/

# Coverage report
pytest --cov=scripts/ scripts/tests/
```

### Integration Tests
```bash
# Test complete pipeline
python scripts/maintenance/consistency_audit.py

# Validate outputs
python scripts/maintenance/final_consistency_audit.py
```

## 🔗 Related Documentation

- [Project Overview](../docs/project_overview.md)
- [MD Simulation Protocol](../docs/md_simulation_protocol.md)
- [Script Refinement Summary](../docs/SCRIPT_REFINEMENT_SUMMARY.md)
- [JCIM Roadmap](../JCIM_COMPLIANT_ROADMAP.md)

---

**Note**: All scripts are designed to work from the Project2 root directory using relative paths. This ensures portability and collaboration-friendly file management.