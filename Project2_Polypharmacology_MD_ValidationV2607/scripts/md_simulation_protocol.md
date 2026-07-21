# GROMACS Molecular Dynamics Simulation Protocol
## Paper 2: Resistance-Informed MD Validation

**Targets**: Top 20 candidates (MPO ≥ 0.70, SYBA > 0, SI > 10) from Paper 1  
**Receptors**: 4 WT targets + 6 resistance mutants = up to 120 systems  
**Duration**: WT baseline 200 ns; mutant systems 100 ns  
**Force fields**: CHARMM36m (protein) + CGenFF v4.4 (ligands) + TIP3P (water)  
**Temperature**: 300 K  
**Software**: GROMACS 2022.4, gmx_MMPBSA (igb=2, OBC model)  

> **Use the scripts** — this document describes the protocol; the scripts implement it.  
> Run `bash scripts/md_full_pipeline.sh --dry-run` to see all steps.

---

## 0. Pre-computation Setup

```bash
conda env create -f environment_md.yml
conda activate malaria_md

# CGenFF (required for ligand topology — must match CHARMM36m protein FF)
# Download cgenff_charmm2gmx from: https://mackerell.umaryland.edu/charmm_ff_params.shtml
# Place in PATH or conda env bin/

# SWISS-MODEL token (for automated mutant structure generation)
export SWISSMODEL_TOKEN=<your_token>
```

---

## 1. Candidate Selection

```bash
python scripts/md_select_top20.py
# Output: results/md_top20_candidates.csv
#         results/md_top20_smiles.smi
```

Filters: MPO ≥ 0.70 AND SYBA > 0 AND SI > 10.  
Sorted by MPO score descending; top 20 selected.

---

## 2. Resistance Mutant Structures

Six mutants modelled from WT crystal structures:

| Target | Mutation | WT PDB | Prevalence (Africa) |
|--------|----------|--------|---------------------|
| PfDHFR | N51I | 7F3Y | 50–70% |
| PfDHFR | C59R | 7F3Y | 60–80% |
| PfDHFR | S108N | 7F3Y | 70–90% |
| PfDHFR | I164L | 7F3Y | <5% |
| PfCRT  | K76T | 6UKJ | 40–60% |
| PfCRT  | K76A | 6UKJ | Emerging |

```bash
# SWISS-MODEL (preferred, requires token)
python scripts/md_homology_mutants.py --method swissmodel

# PyMOL fallback
python scripts/md_homology_mutants.py --method pymol

# Output: data/proteins/mutants/<PDB>_<MUTATION>.pdb
```

Quality criteria (all must pass):
- Backbone RMSD to WT < 1.5 Å
- QMEAN > −4.0, GMQE > 0.7, Ramachandran favoured > 95%

---

## 3. Protein Preparation

```bash
python scripts/md_prepare_proteins.py
# Removes waters/HETATM, preserves cofactors (NAD, ATP, COF, metals)
# Output: MD_systems/<complex>/<PDB>_prepared.pdb
```

---

## 4. Ligand Topology (CGenFF)

```bash
python scripts/md_prepare_ligands.py
```

Workflow per ligand:
1. SMILES → 3D PDB (RDKit ETKDGv3 + MMFF optimisation)
2. PDB → MOL2 (Open Babel)
3. MOL2 → `.str` (CGenFF / ParamChem)
4. `.str` → GROMACS `.itp` + `.gro` (cgenff_charmm2gmx)

> If CGenFF is unavailable, GAFF2/ACPYPE is used as a fallback with an explicit
> warning. **Do not use GAFF2 output for production runs** — it is incompatible
> with CHARMM36m. Obtain CGenFF parameters from https://cgenff.umaryland.edu

---

## 5. Complex Building & Solvation

```bash
python scripts/md_build_complexes.py
# Places ligand at binding site centre (auto-detected from reference ligand)
# Solvates in 1.2 nm TIP3P water box, 0.15 M NaCl

# Ion addition (interactive — select SOL group)
bash MD_systems/<complex>/add_ions.sh
```

---

## 6. Energy Minimisation

Two-stage: steepest descent (Fmax < 1000 kJ/mol/nm) → conjugate gradient.

```bash
bash scripts/md_run_minimisation.sh          # all complexes
bash scripts/md_run_minimisation.sh 201_DHFR # single complex
```

Accepts `ions.gro` (preferred) or `solvated.gro` as input.

---

## 7. NVT Equilibration (100 ps, 300 K)

```bash
bash scripts/md_run_nvt.sh
```

Key settings: V-rescale thermostat, τ_T = 0.1 ps, ref_T = 300 K,  
position restraints 1000 kJ/mol/nm² on protein heavy atoms.

---

## 8. NPT Equilibration (500 ps, 300 K, 1 bar)

```bash
bash scripts/md_run_npt.sh
```

Key settings: Parrinello-Rahman barostat, τ_P = 2.0 ps, ref_P = 1.0 bar,  
compressibility = 4.5×10⁻⁵ bar⁻¹.

---

## 9. Production MD

```bash
bash scripts/md_run_production.sh            # all complexes, auto GPU
bash scripts/md_run_production.sh 201_DHFR 0 # single complex, GPU 0
```

- 100 ns (mutants) or 200 ns (WT baseline), 2 fs timestep
- 3 replicates with unique seeds (12345, 24690, 36935)
- Output every 10 ps (coordinates), 2 ps (energies)
- Total: ~14,000 ns across 120 systems

**Hardware**: 4× A100 (80 GB), ~35 days.  
**Storage**: ~6 TB trajectories. Back up weekly with MD5 checksums.

---

## 10. Trajectory Analysis

```bash
python scripts/md_analyse_trajectories.py
```

Per system per replicate:
- Backbone RMSD (pass: < 0.30 nm)
- Ligand RMSD (pass: < 0.25 nm)
- Per-residue RMSF
- Protein-ligand H-bonds (3.5 Å, 30°)
- MM-GBSA: igb=2 (OBC), 500 snapshots from last 50 ns, 0.15 M ionic strength

Output: `results/md_results/md_analysis_summary.csv`

---

## 11. Paper 2 Metrics

```bash
python scripts/md_calculate_rrs_acsi_pns.py
```

Requires `results/docking_mutants.csv` (Vina scores vs WT + 6 mutants).

| Metric | Formula | Output |
|--------|---------|--------|
| RRS | mean(ΔG_mut / ΔG_WT × 100) | Classes A–D |
| ACSI | 0.40×D_DB + 0.25×D_ANPDB + 0.20×fsp³ + 0.15×NPL | [0,1] |
| PNS | Σ(C_D,j × \|ΔG_j\|) / n | Ranked list |

---

## Stability Criteria Summary

| Metric | Pass | Flag |
|--------|------|------|
| Backbone RMSD | < 0.30 nm | > 0.35 nm |
| Ligand RMSD | < 0.25 nm | > 0.40 nm |
| Rg drift | < 0.05 nm | > 0.10 nm |
| H-bond occupancy (key) | > 30% | < 10% |

Expected: 80–90% systems stable; unstable systems reported as negative controls.

---

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `Fatal error: Atom not found in rtp` | CGenFF penalty > 50 | Re-parameterise; check `.str` file |
| `Particle moved > minimum distance` | Clash in initial structure | Reduce timestep; check ligand placement |
| `LINCS warning` | Constraint failure | Increase `lincs_iter`; check H-bond constraints |
| MM-GBSA parsing fails | Non-standard output format | Check `FINAL_RESULTS_MMPBSA.dat`; update regex in `parse_mmpbsa_energy()` |
| ACPYPE timeout | Large/complex ligand | Use `-c gas` instead of `-c bcc`; or obtain CGenFF parameters manually |

---

## Known Issues & Fixes (July 7, 2026 HPC Run)

The following problems were encountered and resolved during the first production run on
`nanaengo@100.73.21.40`. Document here to avoid repeating debugging.

### 1. GROMACS binary: use `gmx_mpi`, never bare `gmx`

The HPC conda env (`malaria_md`) provides only the MPI build:
```
/home/nanaengo/miniforge3/envs/malaria_md/bin.AVX2_256/gmx_mpi
```
There is no `gmx` (thread-MPI) binary. All scripts must use the full path above.
Set once at the top of any run script:
```python
GMX = "/home/nanaengo/miniforge3/envs/malaria_md/bin.AVX2_256/gmx_mpi"
```

### 2. GMXLIB must be set explicitly

Non-interactive SSH sessions do not source `~/.bashrc`, so GROMACS cannot find
force-field files. Set at script launch:
```python
import os
os.environ["GMXLIB"] = "/home/nanaengo/miniforge3/envs/malaria_md/share/gromacs/top"
```

### 3. Remove `-ntmpi` from all `mdrun` calls

`-ntmpi N` is a **thread-MPI** flag. Using it with the MPI build (`gmx_mpi`) causes
an immediate `MPI_ABORT`:
```
Fatal error: Setting the number of thread-MPI ranks is only supported with
thread-MPI and GROMACS was compiled without thread-MPI
```
Use `-ntomp 8` (OpenMP threads per rank) only. Let MPI handle rank count via
`mpirun` or the scheduler.

### 4. 438_PfATP4: chain break at residues 66–67

The crystal structure has residues 66 (GLU) and 67 (LYS) separated by 20 Å — two
disconnected structural domains with no `TER` record between them. `pdb2gmx` creates
a spurious peptide bond across this gap, causing an "excluded atoms 2.096 nm apart"
error at NVT `grompp`.

**Fix:**
1. Insert `TER` between res 66 and 67 in `protein_fixed.pdb`
2. Re-run `pdb2gmx` → produces two chains: `Protein_chain_A` + `Protein_chain_A2`
3. Rebuild `topol.top` with correct directive order:
   `forcefield.itp` → ligand atomtypes → ligand moleculetype → chain A itp → chain A2 itp → water → ions
4. Re-run `solvate` + `genion`

### 5. Energy minimization with bad starting geometry

After a fresh `solvate`, water molecules may be placed inside protein cavities,
causing initial LJ energies of ~10¹⁵ kJ/mol. Standard `constraints = h-bonds`
will immediately crash with LINCS/SETTLE errors.

**Fix for `em.mdp`:**
```
; Allow water to flex and protein H-bonds unconstrained during EM
define                  = -DFLEXIBLE
constraints             = none
emstep                  = 0.001   ; smaller step for bad geometries (default 0.01)
nsteps                  = 100000  ; more steps needed
```
The `-DFLEXIBLE` flag activates the flexible TIP3P water model defined in
`charmm36-jul2022.ff/tip3p.itp`, removing SETTLE constraints during EM.
Switch back to `constraints = h-bonds` for NVT/NPT (already set in those mdps).

### 6. Conda activation in non-interactive SSH

`conda` is not in PATH for non-interactive SSH sessions. Source the init script:
```bash
source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate malaria_md
```
Or use `nohup python -u script.py` after activation in the same shell block.

---

*Protocol version 2.1 — July 7, 2026*  
*Updated: GROMACS HPC fixes, 438_PfATP4 chain-break resolution, flexible EM procedure*  
*Supersedes: md_simulation_protocol.md v2.0 (April 2026)*
