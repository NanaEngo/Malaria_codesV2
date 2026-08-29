# MM-GBSA Calculation Methodology

> **Active P2 boundary:** this document is a general/historical protocol note. The canonical evidence set retains only PfCRT--214 (−18.25 ± 0.40 kcal/mol) as interpretable. Dissociated systems, conversion-corrupted systems, and any unvalidated endpoint are N/A; the examples below must not be read as results for 20 candidates.


## Overview

Molecular Mechanics/Generalized Born Surface Area (MM-GBSA) calculations provide more accurate binding free energy estimates than docking scores by incorporating:
- Explicit solvation effects
- Entropic contributions (approximate)
- Conformational flexibility
- Ensemble averaging

**Expected Accuracy:** ±2-3 kcal/mol (vs. ±1-2 kcal/mol for FEP)

---

## 1. Theory

### Binding Free Energy Equation

ΔG_bind = G_complex - (G_protein + G_ligand)

Where:
G = E_MM + G_solv - TS

**Components:**
- **E_MM**: Molecular mechanics energy (bonded + non-bonded)
- **G_solv**: Solvation free energy (polar + non-polar)
- **TS**: Entropic contribution (often omitted due to computational cost)

### Energy Decomposition

ΔG_bind = Σ ΔG_residue (per-residue decomposition)

This identifies key binding residues and validates interaction mechanisms.

---

## 2. Methods

### 2.1 Software Options

| Software | License | Pros | Cons |
|----------|---------|------|------|
| **gmx_MMPBSA** | Open-source | Integrates with GROMACS, fast | Limited FEP support |
| **AMBER MMPBSA.py** | Free (AMBERTools) | Well-documented, robust | Requires AMBER format |
| **Schrödinger Prime MM-GBSA** | Commercial | User-friendly, accurate | Expensive |

**Selected Tool:** gmx_MMPBSA (open-source, GROMACS integration)

### 2.2 Installation

```bash
# Install via conda (recommended)
conda install -c conda-forge gmx_mmpbsa

# Or via pip
pip install gmx_MMPBSA

# Verify installation
gmx_MMPBSA --version
```

**Dependencies:**
- GROMACS 2020+
- AMBERTools (for MMPBSA.py backend)
- Python 3.7+

---

## 3. Snapshot Extraction

### 3.1 Select Frames

Extract snapshots from the equilibrated portion of a validated trajectory. The historical 50 ns/200 ns example below is not applicable to the canonical 10 ns P2 trajectories; the observed PfCRT--214 estimate used 101 snapshots across 10 ns.

```bash
# Extract every 100 ps from last 50 ns (500 frames total)
gmx trjconv -s md.tpr -f md.xtc -o mmgbsa_traj.xtc \
  -b 150 -e 200 -dt 100
```

**Rationale:**
- Last 50 ns ensures equilibration
- 100 ps interval reduces correlation between frames
- 500 frames provides good statistical sampling

### 3.2 Prepare Index File

```bash
# Create index groups for protein and ligand
gmx make_ndx -f md.tpr -o index.ndx

# In interactive mode:
> a CA          # Select protein C-alpha atoms
> name 1 Protein
> r LIG         # Select ligand (replace LIG with residue name)
> name 2 Ligand
> q
```

---

## 4. MM-GBSA Calculation

### 4.1 Input File

**File:** `mmpbsa.in`

```ini
[ General ]
startframe           = 1
endframe             = 500
interval             = 1
verbose              = 1

[ Energy ]
# Use GB model (faster than PB)
igb                  = 2    # OBC GB model (recommended)
saltcon              = 0.15 # Ionic strength (M)
extdiel              = 80.0 # Dielectric constant (solvent)
intdiel              = 1.0  # Dielectric constant (protein)

# Non-polar solvation
surften              = 0.0072 # Surface tension coefficient
surfoff              = 0.0    # Surface offset

# Decomposition (per-residue energy)
decomp               = 1    # Enable decomposition
dec_verbose          = 0

[ Trajectory ]
strip                = ":WAT:NA:CL" # Remove water and ions
```

### 4.2 Run Calculation

```bash
# Single system
gmx_MMPBSA -O -i mmpbsa.in \
  -cs md.tpr \
  -ci index.ndx \
  -cg 1 2 \
  -ct mmgbsa_traj.xtc \
  -n 500 \
  -o results.csv \
  -eo results.dat

# With decomposition
gmx_MMPBSA -O -i mmpbsa.in \
  -cs md.tpr \
  -ci index.ndx \
  -cg 1 2 \
  -ct mmgbsa_traj.xtc \
  -n 500 \
  -decomp \
  -o results.csv \
  -eo results.dat \
  -do decomp.csv
```

**Runtime:** ~1-2 hours per system (500 frames)  
**Total for 20 systems:** 20-40 hours

### 4.3 Parallel Execution (historical template; not used for canonical P2 results)

```bash
#!/bin/bash
# Run MM-GBSA on multiple systems in parallel

SYSTEMS=("Ligand_201" "Ligand_214" "Ligand_87" "Ligand_438" "Ligand_164")

for SYS in "${SYSTEMS[@]}"; do
  cd $SYS
  gmx_MMPBSA -O -i ../mmpbsa.in \
    -cs md.tpr -ci index.ndx -cg 1 2 \
    -ct mmgbsa_traj.xtc -n 500 \
    -o results.csv -eo results.dat &
  echo "Started $SYS (PID: $!)"
done

wait
echo "All calculations complete!"
```

---

## 5. Analysis

### 5.1 Parse Results

```python
import pandas as pd
import numpy as np

# Load results
df = pd.read_csv('results.csv')

# Calculate statistics
delta_g = df['G_bind']
mean_dg = delta_g.mean()
std_dg = delta_g.std()
sem_dg = std_dg / np.sqrt(len(delta_g))

print(f"ΔG_bind = {mean_dg:.2f} ± {std_dg:.2f} kcal/mol")
print(f"Standard error: {sem_dg:.2f} kcal/mol")
print(f"Frames: {len(delta_g)}")

# 95% confidence interval
ci_95 = 1.96 * sem_dg
print(f"95% CI: [{mean_dg - ci_95:.2f}, {mean_dg + ci_95:.2f}]")
```

### 5.2 Compare with Docking

```python
import matplotlib.pyplot as plt
from scipy.stats import pearsonr, spearmanr

# Docking scores (from Paper 1)
vina_scores = {'Ligand_201': -8.49, 'Ligand_214': -7.5, ...}

# MM-GBSA results
mmgbsa_scores = {'Ligand_201': -35.2, 'Ligand_214': -32.1, ...}

# Correlation
ligands = list(vina_scores.keys())
vina = [vina_scores[l] for l in ligands]
mmgbsa = [mmgbsa_scores[l] for l in ligands]

r_pearson, p_pearson = pearsonr(vina, mmgbsa)
r_spearman, p_spearman = spearmanr(vina, mmgbsa)

print(f"Pearson r = {r_pearson:.3f} (p = {p_pearson:.4f})")
print(f"Spearman ρ = {r_spearman:.3f} (p = {p_spearman:.4f})")

# Plot
plt.figure(figsize=(8, 6))
plt.scatter(vina, mmgbsa, s=100, alpha=0.7)
plt.xlabel('Vina Score (kcal/mol)', fontsize=14)
plt.ylabel('MM-GBSA ΔG_bind (kcal/mol)', fontsize=14)
plt.title(f'Vina vs. MM-GBSA (r = {r_pearson:.3f})', fontsize=16)
plt.tight_layout()
plt.savefig('vina_vs_mmgbsa.png', dpi=300)
plt.show()
```

### 5.3 Per-Residue Decomposition

```python
# Load decomposition data
decomp = pd.read_csv('decomp.csv')

# Top 20 contributing residues
top_residues = decomp.nsmallest(20, 'Total')

# Plot
plt.figure(figsize=(12, 8))
plt.barh(top_residues['Residue'], top_residues['Total'], color='red')
plt.xlabel('ΔG (kcal/mol)', fontsize=14)
plt.title('Top 20 Contributing Residues', fontsize=16)
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig('energy_decomposition.png', dpi=300)
plt.show()
```

---

## 6. Validation

### 6.1 Convergence Check

```python
# Block averaging analysis
def block_averaging(data, max_block_size=100):
    """Check convergence via block averaging"""
    means = []
    errors = []
    block_sizes = range(10, max_block_size, 10)
    
    for block_size in block_sizes:
        n_blocks = len(data) // block_size
        blocks = [data[i*block_size:(i+1)*block_size].mean() 
                  for i in range(n_blocks)]
        means.append(np.mean(blocks))
        errors.append(np.std(blocks) / np.sqrt(n_blocks))
    
    return block_sizes, means, errors

# Check convergence
block_sizes, means, errors = block_averaging(delta_g.values)

plt.figure(figsize=(8, 6))
plt.plot(block_sizes, means, 'o-', markersize=8)
plt.fill_between(block_sizes, 
                  [m - e for m, e in zip(means, errors)],
                  [m + e for m, e in zip(means, errors)],
                  alpha=0.3)
plt.xlabel('Block Size (frames)', fontsize=14)
plt.ylabel('Mean ΔG_bind (kcal/mol)', fontsize=14)
plt.title('Convergence Check', fontsize=16)
plt.tight_layout()
plt.savefig('convergence.png', dpi=300)
plt.show()
```

**Convergence Criteria:**
- Mean ΔG_bind stable within ±1 kcal/mol for block sizes > 200 frames
- Error bars plateau

### 6.2 Replicate Consistency

Compare 3 independent replicates:

```python
# Load replicates
rep1 = pd.read_csv('replicate_1/results.csv')['G_bind']
rep2 = pd.read_csv('replicate_2/results.csv')['G_bind']
rep3 = pd.read_csv('replicate_3/results.csv')['G_bind']

# ANOVA
from scipy.stats import f_oneway
f_stat, p_value = f_oneway(rep1, rep2, rep3)
print(f"ANOVA: F = {f_stat:.3f}, p = {p_value:.4f}")

# Expected: p > 0.05 (no significant difference between replicates)
```

---

## 7. Expected Results

### Typical MM-GBSA Values

| System Type | ΔG_bind (kcal/mol) | Interpretation |
|-------------|-------------------|----------------|
| Strong binder | < −35 | Excellent affinity |
| Moderate binder | −35 to −25 | Good affinity |
| Weak binder | −25 to −15 | Moderate affinity |
| Non-binder | > −15 | Poor affinity |

### Correlation with Experiment

| Method | Typical R² | Notes |
|--------|-----------|-------|
| Docking (Vina) | 0.3-0.5 | Qualitative ranking |
| MM-GBSA | 0.5-0.7 | Semi-quantitative |
| FEP | 0.7-0.9 | Quantitative (±1 kcal/mol) |

---

## 8. Troubleshooting

### Issue: Positive ΔG_bind (Unfavorable)

**Possible Causes:**
- Ligand not properly positioned
- Insufficient sampling
- Force field issues

**Solutions:**
- Check initial pose (visualize trajectory)
- Extend simulation (use full 200 ns)
- Verify ligand parameters (CGenFF penalty)

### Issue: Large Standard Deviation (> 5 kcal/mol)

**Causes:**
- High flexibility
- Insufficient sampling
- Ligand partially unbinding

**Solutions:**
- Increase snapshot interval (every 200 ps instead of 100 ps)
- Use longer trajectory (full 200 ns)
- Check RMSD for instability

### Issue: Decomposition Fails

**Solutions:**
- Use `decomp = 2` (pairwise instead of full)
- Reduce number of frames
- Check for missing atoms in topology

---

## 9. Reporting

### Table Format for Manuscript

| Ligand | Target | ΔG_bind (kcal/mol) | Std Dev | SEM | 95% CI |
|--------|--------|-------------------|---------|-----|--------|
| 201 | PfDHFR | −35.2 | 4.3 | 0.19 | [−35.6, −34.8] |
| 214 | PfDHFR | −32.1 | 3.8 | 0.17 | [−32.4, −31.8] |
| 438 | PfATP4 | −28.5 | 5.1 | 0.23 | [−29.0, −28.0] |

### Figure Panel

Create multi-panel figure:
- **Panel A:** MM-GBSA ΔG_bind for all 20 ligands (bar chart with error bars)
- **Panel B:** Correlation with Vina scores (scatter plot)
- **Panel C:** Per-residue energy decomposition (top 10 residues)
- **Panel D:** Convergence plot (block averaging)

---

## 10. Advanced: Free Energy Perturbation (Optional)

### When to Use FEP

- Need quantitative accuracy (±1 kcal/mol)
- Comparing congeneric series (similar scaffolds)
- Top 3-5 candidates only (expensive)

### Software Options

| Software | License | Cost |
|----------|---------|------|
| **Schrödinger FEP+** | Commercial | $$$$ |
| **AMBER TI** | Academic | ~$500 |
| **GROMACS FEP** | Open-source | Free |
| **alchemistry-tools** | Open-source | Free |

### Expected Timeline

- Top 5 ligands × 20 windows × 5 ns = 500 ns total
- Runtime: ~5-10 days (GPU)
- Analysis: 1-2 weeks

---

## References

1. **gmx_MMPBSA:** Valdés-Tresanco et al., J. Chem. Theory Comput., 2021
2. **MM-GBSA Theory:** Genheden & Ryde, Expert Opin. Drug Discov., 2015
3. **Best Practices:** Wang et al., J. Chem. Inf. Model., 2024
4. **FEP Review:** RSC Advances, 2026 (d5cp04452a)

---

**Document Version:** 1.0  
**Created:** April 8, 2026  
**Author:** Myke Vital Sao Temgoua
