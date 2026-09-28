# GROMACS Molecular Dynamics Simulation Protocol
## Paper 2: Resistance-Informed MD Validation

**Cohorts**: Canonical set C contains 17 polypharmacology candidates for docking/RRS/ACSI/PNS. Production MD was run separately on four named parent-study consensus leads (201-PfDHFR, 438-PfATP4, historical 164-PfClpP cohort label, 214-PfCRT); PDB 4GM2 is PfClpR rather than PfClpP.
**Cohort boundary**: 17 set-C candidates/136 docking states; four separate parent-study MD complexes (201-PfDHFR, 438-PfATP4, historical 164-PfClpP cohort label, 214-PfCRT).
**Observed MD**: four parent-study wild-type systems, 10 ns each (40 ns total); no set-C production MD.
**Force fields observed**: CHARMM36m protein + GAFF2/ACPYPE AM1-BCC ligand topologies + TIP3P; this heterogeneity limits absolute MM-GBSA interpretation.
**Temperature**: 310.15 K (physiological).
**Future execution**: guarded scripts default to dry-run; any future run requires `--execute` plus `P2_MD_EXECUTE_CONFIRM=I_UNDERSTAND`.

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

The canonical set-C file is `results/candidate_selection/md_top20_candidates_polypharm.csv` (17 rows). It is distinct from the historical set-B file `results/md_top20_candidates.csv` and from the four parent-study MD systems. Use `scripts/p2_setc_md_pilot.py` for a bounded, fail-closed future-MD preflight; it never launches GROMACS. Before a future system can pass preflight, its directory must contain non-empty `complex.gro`, `topol.top`, and `md.mdp` files plus `system_manifest.json` with exact `set_c_id`, `target`, `mutation`, and canonical `smiles` values matching the selected docking row. No current preparation script writes this manifest; implementing and validating that producer is a prerequisite for any future READY status.


```bash
python scripts/md_select_top20.py
# Output: historical candidate-selection artifacts only; do not treat them as the production-MD cohort.
# Canonical set-C metrics use results/candidate_selection/md_top20_candidates_polypharm.csv.
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

## 7. NVT Equilibration (100 ps, 310.15 K)

```bash
bash scripts/md_run_nvt.sh
```

Key settings: V-rescale thermostat, τ_T = 0.1 ps, ref_T = 310.15 K,
position restraints 1000 kJ/mol/nm² on protein heavy atoms.

---

## 8. NPT Equilibration (500 ps, 310.15 K, 1 bar)

```bash
bash scripts/md_run_npt.sh
```

Key settings: Parrinello-Rahman barostat, τ_P = 2.0 ps, ref_P = 1.0 bar,  
compressibility = 4.5×10⁻⁵ bar⁻¹.

---

## 9. Production MD (historical results and guarded future workflow)

```bash
bash scripts/md_run_production.sh            # all complexes, auto GPU
bash scripts/md_run_production.sh 201_DHFR 0 # single complex, GPU 0
```

- **Observed completed result:** four parent-study complexes, 10 ns each (40 ns total), at 310.15 K; no set-C production MD was completed.
- **Guarded future default:** 10 ns, one replicate, 2 fs timestep; this is a targeted diagnostic, not a convergence claim.
- A future publication-grade campaign would require pre-specified duration, independent replicates, force-field consistency, integrity checks, and a registered provenance manifest before execution.
- Output targets are every 10 ps (coordinates) and 2 ps (energies) for the guarded template.

**Hardware/storage note:** no future run is implied by this protocol. Large trajectories must be archived with checksums before being described as publicly available.

---

## 10. Trajectory Analysis

Only bound, topology-valid parent-study systems may receive an interpretable MM-GBSA endpoint estimate. In the canonical evidence set, this rule retains PfCRT--214 only (−18.25 ± 0.40 kcal/mol); the historically labelled 164--PfClpP cohort and PfDHFR--201 dissociated, and PfATP4--438 was excluded for a CHARMM36-to-AMBER conversion artifact. PDB 4GM2 is PfClpR rather than PfClpP, so the historical 164 label is not structural validation of PfClpP.

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

RRS, ACSI, PNS, and the cross-metric analysis are computed for set C and are docking/cheminformatics-based. They must not be described as MD-derived metrics for the four parent-study complexes.


```bash
python scripts/md_calculate_rrs_acsi_pns.py
```

Requires `results/docking_mutants.csv` (Vina scores vs WT + 6 mutants). The canonical set-C run enforces exactly 136 unique candidate/target/mutation rows (17 candidates × 8 PfDHFR/PfCRT states) and embeds the candidate-file path and SHA-256 in each output CSV and the provenance manifest. Explicit custom cohorts receive structural coverage checks but must supply their own expected target/mutation schema.

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
