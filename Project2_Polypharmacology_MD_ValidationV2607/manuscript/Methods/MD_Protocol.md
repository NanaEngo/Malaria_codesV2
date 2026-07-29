# MD Simulation Protocol: Polypharmacological Antimalarial Leads

## Version 1.0 - April 8, 2026

---

## 1. System Preparation

### 1.1 Protein Preparation

```bash
# Download PDB structure
wget https://files.rcsb.org/download/7F3Y.pdb

# Clean PDB file (remove waters, heteroatoms except ligand)
gmx pdb2gmx -f 7F3Y.pdb -o protein_processed.gro -water tip3p -ff charmm36-jul2022

# Check for missing residues
grep -i "missing" 7F3Y.pdb
```

**Force Field:** CHARMM36m (July 2022 release)  
**Water Model:** TIP3P  
**Protonation State:** pH 7.0 (HIS neutral)

### 1.2 Ligand Preparation

```bash
# Generate ligand coordinates from SMILES (using RDKit)
python -c "
from rdkit import Chem
from rdkit.Chem import AllChem

smiles = 'YOUR_LIGAND_SMILES'
mol = Chem.MolFromSmiles(smiles)
mol = Chem.AddHs(mol)
AllChem.EmbedMolecule(mol, randomSeed=42)
AllChem.MMFFOptimizeMolecule(mol)
Chem.MolToPDBFile(mol, 'ligand.pdb')
"

# Generate CGenFF topology
# Upload ligand.pdb to: https://cgenff.com
# Download: ligand.str, ligand.prm, ligand.rtf
```

**Ligand Parameters:** CGenFF (CHARMM General Force Field)  
**Charge Method:** CGenFF automatic assignment  
**Validation:** Check penalty score < 50 (if > 50, requires manual parameterization)

### 1.3 Complex Preparation

```bash
# Position ligand in binding site (use docking pose from Paper 1)
# Align protein-ligand complex
gmx editconf -f protein.gro -o complex.gro -center

# Merge protein and ligand
cat protein.gro ligand.gro | head -n -1 > complex_raw.gro

# Count atoms
grep -c "^" complex_raw.gro
```

### 1.4 Solvation

```bash
# Define simulation box (1.0 nm padding)
gmx editconf -f complex.gro -o complex_box.gro -c -d 1.0 -bt dodecahedron

# Solvate with TIP3P water
gmx solvate -cp complex_box.gro -cs tip3p.gro -o complex_solv.gro -p topol.top
```

**Box Type:** Dodecahedron (minimum volume)  
**Padding:** 1.0 nm (prevents self-interaction with periodic images)  
**Water Model:** TIP3P (compatible with CHARMM36m)

### 1.5 Ion Addition

```bash
# Generate topology for ions
gmx grompp -f ions.mdp -c complex_solv.gro -p topol.top -o ions.tpr -maxwarn 1

# Add ions (neutralize + 0.15 M NaCl)
gmx genion -s ions.tpr -o system.gro -p topol.top -pname NA -nname CL \
  -neutral -conc 0.15
```

**Ion Concentration:** 0.15 M NaCl (physiological)  
**Neutralization:** Yes (add counterions to neutralize system charge)

---

## 2. Energy Minimization

### 2.1 Minimization Parameters

**File:** `em.mdp`

```mdp
integrator               = steep
emtol                    = 1000.0
emstep                   = 0.01
nsteps                   = 50000

nstlist                    = 10
cutoff-scheme              = Verlet
ns_type                    = grid
coulombtype                = PME
rcoulomb                   = 1.2
rvdw                       = 1.2
pbc                        = xyz
```

### 2.2 Run Minimization

```bash
gmx grompp -f em.mdp -c system.gro -p topol.top -o em.tpr -maxwarn 2
gmx mdrun -deffnm em -v

# Check potential energy
gmx energy -f em.edr -o potential.xvg
```

**Convergence Criterion:** Fmax < 1000 kJ/mol/nm  
**Expected Steps:** 5,000-20,000

---

## 3. Equilibration

### 3.1 NVT Equilibration (Constant Volume)

**File:** `nvt.mdp`

```mdp
define                     = -DPOSRES
integrator                 = md
nsteps                     = 50000
dt                         = 0.002

nstxout                    = 500
nstvout                    = 500
nstenergy                  = 1000
nstlog                     = 1000

continuation               = no
constraint_algorithm       = lincs
constraints                = h-bonds
lincs_iter                 = 1
lincs_order                = 4

cutoff-scheme              = Verlet
ns_type                    = grid
nstlist                    = 10
coulombtype                = PME
rcoulomb                   = 1.2
rvdw                       = 1.2
pbc                        = xyz

tcoupl                     = V-rescale
tc-grps                    = Protein Non-Protein
tau_t                      = 0.1 0.1
ref_t                      = 300 300

gen_vel                    = yes
gen_temp                   = 300
gen_seed                   = -1
```

**Duration:** 100 ps (50,000 steps × 2 fs)  
**Temperature:** 300 K (V-rescale thermostat)  
**Position Restraints:** On protein heavy atoms  
**Output Frequency:** Every 1 ps (energy), 0.1 ps (trajectory)

```bash
gmx grompp -f nvt.mdp -c em.gro -p topol.top -o nvt.tpr -r em.gro
gmx mdrun -deffnm nvt -v

# Check temperature stability
gmx energy -f nvt.edr -o temperature.xvg
```

### 3.2 NPT Equilibration (Constant Pressure)

**File:** `npt.mdp`

```mdp
define                     = -DPOSRES
integrator                 = md
nsteps                     = 50000
dt                         = 0.002

nstxout                    = 500
nstvout                    = 500
nstenergy                  = 1000
nstlog                     = 1000

continuation               = yes
constraint_algorithm       = lincs
constraints                = h-bonds
lincs_iter                 = 1
lincs_order                = 4

cutoff-scheme              = Verlet
ns_type                    = grid
nstlist                    = 10
coulombtype                = PME
rcoulomb                   = 1.2
rvdw                       = 1.2
pbc                        = xyz

tcoupl                     = V-rescale
tc-grps                    = Protein Non-Protein
tau_t                      = 0.1 0.1
ref_t                      = 300 300

pcoupl                     = Parrinello-Rahman
pcoupltype                 = isotropic
tau_p                      = 2.0
ref_p                      = 1.0
compressibility_isotropic  = 4.5e-5

gen_vel                    = no
```

**Duration:** 100 ps (50,000 steps × 2 fs)  
**Pressure:** 1 bar (Parrinello-Rahman)  
**Compressibility:** 4.5 × 10⁻⁵ bar⁻¹ (water)  
**Position Restraints:** On protein heavy atoms

```bash
gmx grompp -f npt.mdp -c nvt.gro -p topol.top -o npt.tpr -t nvt.cpt -r nvt.gro
gmx mdrun -deffnm npt -v

# Check pressure and density stability
gmx energy -f npt.edr -o pressure.xvg
gmx energy -f npt.edr -o density.xvg
```

---

## 4. Production MD

### 4.1 Production Parameters

**File:** `md.mdp`

```mdp
integrator                 = md
nsteps                     = 100000000
dt                         = 0.002

nstxout                    = 5000
nstvout                    = 5000
nstenergy                  = 1000
nstlog                     = 1000
nstxout-compressed         = 5000

continuation               = yes
constraint_algorithm       = lincs
constraints                = h-bonds
lincs_iter                 = 1
lincs_order                = 4

cutoff-scheme              = Verlet
ns_type                    = grid
nstlist                    = 10
coulombtype                = PME
rcoulomb                   = 1.2
rvdw                       = 1.2
pbc                        = xyz

tcoupl                     = V-rescale
tc-grps                    = Protein Non-Protein
tau_t                      = 0.1 0.1
ref_t                      = 300 300

pcoupl                     = Parrinello-Rahman
pcoupltype                 = isotropic
tau_p                      = 2.0
ref_p                      = 1.0
compressibility_isotropic  = 4.5e-5

gen_vel                    = no
```

**Duration:** 200 ns (100,000,000 steps × 2 fs)  
**Trajectory Output:** Every 10 ps (5,000 steps)  
**Energy Output:** Every 2 ps (1,000 steps)  
**Total Frames:** 20,000 (for 200 ns simulation)

### 4.2 Run Production MD

```bash
# Generate TPR file
gmx grompp -f md.mdp -c npt.gro -p topol.top -o md.tpr -t npt.cpt -maxwarn 2

# Run on GPU
gmx mdrun -deffnm md -ntmpi 1 -ntomp 16 -gpu_id 0 -pin on

# Resume from checkpoint (if interrupted)
gmx mdrun -deffnm md -cpi md.cpt -noappend
```

**GPU Acceleration:** `-gpu_id 0` (use GPU 0)  
**Thread Pinning:** `-pin on` (improves performance)  
**Checkpointing:** Automatic (every 15 min)

### 4.3 Monitoring

```bash
# Monitor progress (in separate terminal)
tail -f md.log | grep "Progress"

# Check RMSD during simulation
echo "Backbone" | gmx rms -s md.tpr -f md.xtc -o rmsd.xvg -tu ns
```

**Expected Performance:**
- RTX 4090: ~50-100 ns/day (system-dependent)
- 200 ns simulation: 2-4 days
- 20 systems: 40-80 days total (parallelize on multiple GPUs)

---

## 5. Quality Checks

### 5.1 RMSD Analysis

```bash
# Backbone RMSD
echo "Backbone" | gmx rms -s md.tpr -f md.xtc -o rmsd_backbone.xvg -tu ns

# Ligand RMSD (relative to protein)
echo "Protein_Ligand" | gmx rms -s md.tpr -f md.xtc -o rmsd_ligand.xvg -tu ns -fit rot+trans
```

**Acceptance Criteria:**
- Protein backbone RMSD: < 2-3 Å (stable)
- Ligand RMSD: < 2 Å (remains in binding site)
- No large jumps (> 1 Å in 10 ns)

### 5.2 RMSF Analysis

```bash
# Per-residue RMSF
echo "Backbone" | gmx rmsf -s md.tpr -f md.xtc -o rmsf.xvg -res
```

**Interpretation:**
- RMSF < 1 Å: Rigid regions (stable)
- RMSF 1-2 Å: Flexible loops (normal)
- RMSF > 3 Å: Highly flexible (may indicate issues)

### 5.3 Radius of Gyration

```bash
echo "Protein" | gmx gyrate -s md.tpr -f md.xtc -o rgyr.xvg
```

**Expected:** Stable Rg (± 0.1 Å), no drift

### 5.4 Solvent Accessible Surface Area (SASA)

```bash
echo "Protein" | gmx sasa -s md.tpr -f md.xtc -o sasa.xvg
```

**Expected:** Stable SASA (± 5 nm²)

### 5.5 Hydrogen Bonds

```bash
# Protein-ligand H-bonds
gmx hbond -s md.tpr -f md.xtc -n index.ndx -num hbnum.xvg
```

**Expected:** Stable H-bond pattern (> 50% occupancy for key interactions)

---

## 6. Trajectory Processing

### 6.1 Remove Periodic Boundary Conditions

```bash
# Make molecules whole
gmx trjconv -s md.tpr -f md.xtc -o md_whole.xtc -pbc mol -center

# Fit to reference structure
gmx trjconv -s md.tpr -f md_whole.xtc -o md_fit.xtc -fit rot+trans -n index.ndx
```

### 6.2 Compress Trajectory (Optional)

```bash
# Reduce output frequency for analysis
gmx trjconv -s md.tpr -f md_fit.xtc -o md_compressed.xtc -dt 100
```

**Output:** 1 frame per 100 ps (2,000 frames for 200 ns)

---

## 7. Backup & Storage

### 7.1 Checksum Generation

```bash
# Generate MD5 checksums
md5sum md.tpr md.xtc md.edr md.log md.cpt > md_checksums.md5

# Verify integrity
md5sum -c md_checksums.md5
```

### 7.2 Storage Structure

```
/storage/MD_Trajectories/
├── PfDHFR_7F3Y/
│   ├── Ligand_201/
│   │   ├── replicate_1/
│   │   │   ├── md.tpr
│   │   │   ├── md.xtc (200 ns)
│   │   │   ├── md.edr
│   │   │   ├── md.log
│   │   │   └── md_checksums.md5
│   │   ├── replicate_2/
│   │   └── replicate_3/
│   ├── Ligand_214/
│   └── ...
├── PfCRT_6UKJ/
├── PfATP4_9N10/
└── PfClpP_4GM2/
```

### 7.3 Storage Requirements

| System Type | Trajectory Size (200 ns) | Checkpoint | Total |
|-------------|--------------------------|------------|-------|
| Small (< 50k atoms) | ~20 GB | ~500 MB | ~21 GB |
| Medium (50-100k atoms) | ~40 GB | ~1 GB | ~41 GB |
| Large (> 100k atoms) | ~80 GB | ~2 GB | ~82 GB |

**Total for 20 systems:** ~400-800 GB (compressed: ~200-400 GB)

---

## 8. Troubleshooting

### Issue: Simulation Crashes

**Possible Causes:**
- Bad contacts in initial structure
- Insufficient energy minimization
- Timestep too large

**Solutions:**
- Re-minimize with more steps (100,000)
- Check for atom clashes: `gmx check -f system.gro`
- Reduce timestep to 1 fs for first 10 ns

### Issue: RMSD Drift

**Possible Causes:**
- Insufficient equilibration
- Ligand unbinding
- Protein unfolding

**Solutions:**
- Extend equilibration (200 ps NPT)
- Check ligand position visually (VMD/PyMOL)
- Verify force field parameters

### Issue: GPU Memory Error

**Solutions:**
- Reduce nstxout (less frequent output)
- Use `-update gpu -bonded gpu` flags
- Switch to mixed precision: `-mixed yes`

---

## 9. Performance Optimization

### GPU Acceleration

```bash
# Optimal settings for RTX 4090
gmx mdrun -deffnm md -ntmpi 1 -ntomp 16 -gpu_id 0 -pin on \
  -update gpu -bonded gpu -pme gpu -dlb yes
```

**Expected Performance:**

| GPU | ns/day | 200 ns Time |
|-----|--------|-------------|
| RTX 4090 | 50-100 | 2-4 days |
| A100 (80 GB) | 100-200 | 1-2 days |
| V100 | 30-60 | 3-7 days |

### Multi-GPU Scaling

```bash
# Run on 4 GPUs
gmx mdrun -deffnm md -ntmpi 4 -ntomp 8 -gpu_id 0,1,2,3 -pin on
```

**Scaling Efficiency:**
- 2 GPUs: ~80% efficiency
- 4 GPUs: ~60% efficiency

---

## 10. Analysis Pipeline

### Quick Analysis Script

```bash
#!/bin/bash
# analyze_md.sh - Quick quality check

SYSTEM=$1
TRAJ=md.xtc
TPR=md.tpr

echo "=== Analyzing $SYSTEM ==="

# RMSD
echo "Protein" | gmx rms -s $TPR -f $TRAJ -o rmsd.xvg -tu ns
echo "✓ RMSD calculated"

# RMSF
echo "Backbone" | gmx rmsf -s $TPR -f $TRAJ -o rmsf.xvg -res
echo "✓ RMSF calculated"

# Rg
echo "Protein" | gmx gyrate -s $TPR -f $TRAJ -o rgyr.xvg
echo "✓ Radius of gyration calculated"

# SASA
echo "Protein" | gmx sasa -s $TPR -f $TRAJ -o sasa.xvg
echo "✓ SASA calculated"

echo "=== Analysis Complete ==="
```

---

## References

1. **GROMACS Manual:** https://manual.gromacs.org
2. **CHARMM36m Force Field:** Huang et al., Nat. Methods, 2017
3. **CGenFF:** Vanommeslaeghe & MacKerell Jr., J. Chem. Inf. Model., 2012
4. **Best Practices:** Lindorff-Larsen et al., Proteins, 2012

---

**Protocol Version:** 1.0  
**Created:** April 8, 2026  
**Last Updated:** April 8, 2026  
**Author:** Myke Vital Sao Temgoua
