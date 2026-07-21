#!/usr/bin/env python3
"""
Prepare PfDHFR System with Docked Pose and NADP+ Cofactor

This script prepares the 201_PfDHFR system for production MD by:
1. Verifying the docked ligand pose is properly positioned
2. Ensuring NADP+ cofactor is included
3. Setting up a minimal test run to validate binding
4. Preparing for HPC production MD launch

Usage:
    python scripts/prepare_pfdhfr_with_docked_pose.py
"""

import sys
from pathlib import Path
import subprocess
import MDAnalysis as mda
from MDAnalysis.analysis import distances
import numpy as np

PROJECT_DIR = Path(__file__).parent.parent
MD_DIR = PROJECT_DIR / "MD_systems" / "201_PfDHFR"


def check_system_components():
    """
    Check that all necessary components are present in the system.
    
    Checks for:
    - Protein (PfDHFR)
    - Ligand (compound 201)
    - Cofactor (NADP+/NDP)
    - Solvent and ions
    """
    print("\n" + "="*70)
    print("📋 System Component Check: 201_PfDHFR")
    print("="*70)
    
    gro_file = MD_DIR / "ions_docked.gro"
    
    if not gro_file.exists():
        print(f"❌ ERROR: {gro_file} not found")
        return False
    
    try:
        u = mda.Universe(str(gro_file))
        
        # Check components
        protein = u.select_atoms("protein")
        ligand = u.select_atoms("resname UNL")
        nadp = u.select_atoms("resname NDP or resname NAP or resname NADP")
        water = u.select_atoms("resname SOL or resname WAT or resname TIP3")
        ions = u.select_atoms("resname NA or resname CL")
        
        print(f"\n  System Overview:")
        print(f"    Total atoms:     {u.atoms.n_atoms:,}")
        print(f"    Protein atoms:   {len(protein):,} ({'✅' if len(protein) > 0 else '❌'})")
        print(f"    Ligand atoms:    {len(ligand):,} ({'✅' if len(ligand) == 37 else '⚠️'})")
        print(f"    NADP+ atoms:     {len(nadp):,} ({'✅' if len(nadp) > 0 else '❌ MISSING'})")
        print(f"    Water molecules: {len(water)//3:,}")
        print(f"    Ions:            {len(ions):,}")
        
        # Check ligand position relative to protein
        if len(ligand) > 0 and len(protein) > 0:
            protein_ca = u.select_atoms("protein and name CA")
            dist_array = distances.distance_array(
                protein_ca.positions, ligand.positions
            )
            min_dist = np.min(dist_array)
            
            print(f"\n  Ligand Position Check:")
            print(f"    Min CA distance: {min_dist:.2f} Å", end="")
            
            if min_dist < 5.0:
                print(" ✅ In binding pocket")
                status = "bound"
            elif min_dist < 10.0:
                print(" ⚠️  Near protein surface")
                status = "proximal"
            else:
                print(" ❌ Dissociated")
                status = "dissociated"
        else:
            status = "unknown"
        
        # Check NADP+ position
        if len(nadp) > 0 and len(protein) > 0:
            protein_ca = u.select_atoms("protein and name CA")
            dist_array_nadp = distances.distance_array(
                protein_ca.positions, nadp.positions
            )
            min_dist_nadp = np.min(dist_array_nadp)
            
            print(f"\n  NADP+ Position Check:")
            print(f"    Min CA distance: {min_dist_nadp:.2f} Å", end="")
            
            if min_dist_nadp < 5.0:
                print(" ✅ In active site")
            else:
                print(" ⚠️  May need repositioning")
        
        # Overall assessment
        print(f"\n  Overall Status:")
        components_ok = (len(protein) > 0 and len(ligand) == 37 and 
                        len(nadp) > 0 and len(water) > 0)
        geometry_ok = (status == "bound" or status == "proximal")
        
        if components_ok and geometry_ok:
            print("    ✅ System ready for MD")
            return True
        elif components_ok:
            print("    ⚠️  Components present but geometry may need adjustment")
            return True
        else:
            print("    ❌ System needs preparation")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def visualize_binding_site():
    """
    Generate PyMOL/VMD visualization script for manual inspection.
    """
    print("\n" + "="*70)
    print("🔬 Generating Visualization Script")
    print("="*70)
    
    pymol_script = MD_DIR / "visualize_binding_site.pml"
    
    script_content = """# PyMOL Visualization Script for 201_PfDHFR Binding Site
# Load this with: pymol visualize_binding_site.pml

# Load structure
load ions_docked.gro, pfdhfr

# Style protein
hide everything
show cartoon, polymer
color grey70, polymer

# Highlight binding site (5 Å around ligand)
select binding_site, polymer within 5 of resname UNL
show sticks, binding_site
color wheat, binding_site

# Show ligand
show sticks, resname UNL
color green, resname UNL
color red, resname UNL and name O*
color blue, resname UNL and name N*

# Show NADP+ cofactor
show sticks, resname NDP or resname NAP
color yellow, resname NDP or resname NAP
color red, (resname NDP or resname NAP) and name O*
color blue, (resname NDP or resname NAP) and name N*
color orange, (resname NDP or resname NAP) and name P*

# Label key residues
select key_residues, binding_site and polymer
label key_residues and name CA, "%s-%s" % (resn, resi)

# Zoom to binding site
zoom resname UNL, 8

# Measure distances
distance lig_nadp_dist, resname UNL, resname NDP, 5.0, mode=2

# Set background
bg_color white
set ray_trace_mode, 1
set antialias, 2

# Print instructions
print "="*70
print "Binding Site Visualization Loaded"
print "="*70
print "Green: Ligand 201"
print "Yellow: NADP+ cofactor"
print "Wheat: Binding site residues (5 Å)"
print ""
print "Commands:"
print "  - Rotate: drag with left mouse button"
print "  - Zoom: scroll wheel"
print "  - Ray trace: 'ray' then 'png output.png'"
print "="*70
"""
    
    with open(pymol_script, 'w') as f:
        f.write(script_content)
    
    print(f"  ✅ PyMOL script saved: {pymol_script.name}")
    print(f"  \n  To visualize:")
    print(f"    cd {MD_DIR}")
    print(f"    pymol visualize_binding_site.pml")
    
    return pymol_script


def generate_hpc_submission_script():
    """
    Generate SLURM submission script for HPC production MD.
    """
    print("\n" + "="*70)
    print("🚀 Generating HPC Submission Script")
    print("="*70)
    
    slurm_script = MD_DIR / "submit_production_md.sh"
    
    script_content = """#!/bin/bash
#SBATCH --job-name=PfDHFR_201_prod
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=48:00:00
#SBATCH --output=production_md_%j.log
#SBATCH --error=production_md_%j.err

# Load modules (adjust for your HPC)
module purge
module load gromacs/2025.4-gpu
# or: module load gromacs/2024.3-gpu

# Set environment
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
cd $SLURM_SUBMIT_DIR

echo "=========================================="
echo "PfDHFR Production MD (10 ns)"
echo "=========================================="
echo "Start time: $(date)"
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $SLURM_NODELIST"
echo "GPU: $CUDA_VISIBLE_DEVICES"
echo ""

# Check if docked system exists
if [ ! -f "ions_docked.gro" ]; then
    echo "ERROR: ions_docked.gro not found!"
    exit 1
fi

# Production MDP parameters (10 ns)
cat > production.mdp << 'EOF'
; Production MD (10 ns, NPT)
title                   = PfDHFR Production MD
integrator              = md                ; Leap-frog MD
dt                      = 0.002             ; 2 fs timestep
nsteps                  = 5000000           ; 10 ns (5M steps)

; Output control
nstlog                  = 5000
nstxout-compressed      = 5000              ; Save every 10 ps
compressed-x-grps       = System
nstenergy               = 5000

; Neighbor searching
cutoff-scheme           = Verlet
nstlist                 = 10
ns_type                 = grid
pbc                     = xyz
rlist                   = 1.2

; Electrostatics
coulombtype             = PME
rcoulomb                = 1.2
pme_order               = 4
fourierspacing          = 0.12
ewald_rtol              = 1e-5

; Van der Waals
vdwtype                 = Cut-off
rvdw                    = 1.2
DispCorr                = EnerPres

; Temperature coupling (NPT)
tcoupl                  = V-rescale
tc-grps                 = System
tau_t                   = 0.1
ref_t                   = 310.15            ; 310 K (37°C)

; Pressure coupling (NPT)
pcoupl                  = C-rescale         ; Recommended for production
pcoupltype              = isotropic
tau_p                   = 2.0
ref_p                   = 1.0
compressibility         = 4.5e-5

; Velocity generation
gen_vel                 = no                ; Continue from equilibration
continuation            = yes

; Constraints
constraints             = h-bonds
constraint_algorithm    = lincs
lincs_order             = 4
lincs_iter              = 1
EOF

# Step 1: Create TPR from test run final frame
echo "Step 1: Preparing production TPR..."
gmx grompp -f production.mdp \
           -c test_100ps.gro \
           -p topol.top \
           -o production.tpr \
           -maxwarn 2

if [ $? -ne 0 ]; then
    echo "ERROR: grompp failed!"
    exit 1
fi

# Step 2: Run production MD on GPU
echo "Step 2: Running production MD (10 ns)..."
gmx mdrun -v \
          -deffnm production \
          -nb gpu \
          -pme gpu \
          -bonded cpu \
          -update gpu

if [ $? -ne 0 ]; then
    echo "ERROR: mdrun failed!"
    exit 1
fi

echo ""
echo "=========================================="
echo "Production MD Complete!"
echo "End time: $(date)"
echo "=========================================="
echo ""
echo "Output files:"
echo "  - production.gro     : Final structure"
echo "  - production.xtc     : Trajectory (10 ns)"
echo "  - production.edr     : Energies"
echo "  - production.log     : MD log"
echo ""
echo "Next: Run analysis with md_analyse_trajectories.py"
"""
    
    with open(slurm_script, 'w') as f:
        f.write(script_content)
    
    # Make executable
    slurm_script.chmod(0o755)
    
    print(f"  ✅ SLURM script saved: {slurm_script.name}")
    print(f"\n  To submit on HPC:")
    print(f"    cd {MD_DIR}")
    print(f"    sbatch submit_production_md.sh")
    
    return slurm_script


def create_analysis_checklist():
    """Create checklist for post-production analysis."""
    print("\n" + "="*70)
    print("📊 Analysis Checklist")
    print("="*70)
    
    checklist = MD_DIR / "ANALYSIS_CHECKLIST.md"
    
    content = """# PfDHFR Production MD Analysis Checklist

**System:** 201_PfDHFR + Ligand 201 + NADP+ cofactor  
**Simulation:** 10 ns NPT production MD  
**Temperature:** 310 K (37°C)  
**Pressure:** 1 bar

---

## Pre-Production Validation ✅

- [ ] Visual inspection of docked pose (PyMOL/VMD)
- [ ] Ligand in binding pocket (< 5 Å from protein)
- [ ] NADP+ cofactor present and positioned correctly
- [ ] Test run (100 ps) completed without crashes
- [ ] No significant drift in test run

---

## Production MD Monitoring

**During Run:**
- [ ] Check log file for errors every 2-4 hours
- [ ] Monitor temperature stability (310 ± 5 K)
- [ ] Monitor pressure (1 ± 100 bar fluctuations normal)
- [ ] Monitor energy drift (should plateau after equilibration)
- [ ] Verify trajectory file growing (~10 MB per ns)

**Red Flags:**
- ❌ Temperature > 320 K or < 300 K
- ❌ Pressure > 500 bar or < -500 bar
- ❌ Energy continuously increasing
- ❌ Simulation crashes or stalls

---

## Post-Production Analysis

### 1. Structural Stability
- [ ] **Protein Backbone RMSD** (target: < 3 Å)
  - Use first frame after equilibration as reference
  - Should plateau within 1-2 ns
- [ ] **Radius of Gyration** (should be stable)
- [ ] **RMSF per residue** (identify flexible loops)

### 2. Ligand Binding Analysis
- [ ] **Ligand RMSD** (target: < 3 Å for stable binding)
- [ ] **Minimum protein-ligand distance** (should stay < 6 Å)
- [ ] **Protein-ligand contacts** (should be > 5 consistently)
- [ ] **Hydrogen bonds** (identify stable H-bonds)
- [ ] **Binding pocket volume** (should be stable)

### 3. Cofactor Interactions
- [ ] **NADP+ RMSD** (should be stable)
- [ ] **Ligand-NADP+ distance** (may influence activity)
- [ ] **NADP+-protein contacts**

### 4. Binding Free Energy (Optional)
- [ ] **MM-GBSA** calculation on trajectory
- [ ] **MM-PBSA** calculation (more accurate, slower)
- [ ] **Per-residue decomposition** (identify key residues)

### 5. Comparison to Successful Systems
- [ ] Compare to PfCRT (214) metrics
- [ ] Compare to PfATP4 (438) metrics
- [ ] Identify differences if any

---

## Success Criteria

**Minimum Requirements:**
- ✅ Protein RMSD < 4 Å (stable fold)
- ✅ Ligand RMSD < 5 Å (bound)
- ✅ Min CA-ligand distance < 6 Å (in pocket)
- ✅ Contacts > 5 (stable interactions)

**Ideal Results:**
- ✅ Protein RMSD 2-3 Å
- ✅ Ligand RMSD < 2 Å
- ✅ Min distance 3-5 Å
- ✅ Contacts 10-15
- ✅ 2-4 stable H-bonds

---

## Manuscript Reporting

**Include:**
1. System composition (atoms, waters, ions)
2. Force field (CHARMM36/GAFF2)
3. Simulation protocol (EM → NVT → NPT → Production)
4. Equilibration criteria met
5. RMSD plot (protein + ligand)
6. Contact analysis
7. Binding mode figure (PyMOL)
8. Key interactions identified

**Transparency:**
- Report ligand dissociation fix (used docked pose)
- Compare to initial generic placement failure
- Justify docked pose as starting structure

---

## Files to Generate

### Figures:
- [ ] `rmsd_protein_ligand.pdf` — RMSD over time
- [ ] `rmsf_per_residue.pdf` — Per-residue flexibility
- [ ] `contacts_over_time.pdf` — Protein-ligand contacts
- [ ] `binding_mode_snapshot.png` — Representative structure
- [ ] `ligand_trajectory_overlay.png` — Ligand pose evolution

### Data Tables:
- [ ] `md_metrics_summary.csv` — All metrics
- [ ] `key_interactions.csv` — Persistent H-bonds/contacts
- [ ] `comparison_to_other_systems.csv` — Cross-system comparison

### Supplementary:
- [ ] `production.xtc` — Full trajectory (deposit or make available)
- [ ] `final_structure.pdb` — Final frame for visualization
- [ ] `analysis_scripts/` — Reproducible analysis code

---

**Next Steps:**
1. ✅ Submit production MD on HPC
2. ⏳ Monitor for 24-48 hours
3. ✅ Run analysis pipeline
4. ✅ Generate figures
5. ✅ Update manuscript
"""
    
    with open(checklist, 'w') as f:
        f.write(content)
    
    print(f"  ✅ Checklist saved: {checklist.name}")
    
    return checklist


def main():
    """Main workflow."""
    print("="*70)
    print("🧬 PfDHFR System Preparation for Production MD")
    print("="*70)
    print("\nThis script will:")
    print("  1. Verify system components (protein, ligand, NADP+)")
    print("  2. Check ligand binding geometry")
    print("  3. Generate visualization script")
    print("  4. Create HPC submission script")
    print("  5. Provide analysis checklist")
    
    # Step 1: Check system
    system_ok = check_system_components()
    
    if not system_ok:
        print("\n❌ System check failed. Please review the issues above.")
        return False
    
    # Step 2: Generate visualization
    visualize_binding_site()
    
    # Step 3: Generate HPC script
    generate_hpc_submission_script()
    
    # Step 4: Create analysis checklist
    create_analysis_checklist()
    
    # Final summary
    print("\n" + "="*70)
    print("✅ PfDHFR System Preparation Complete!")
    print("="*70)
    print("\nNext Steps:")
    print("  1. Visually inspect binding site:")
    print(f"     cd {MD_DIR}")
    print("     pymol visualize_binding_site.pml")
    print("")
    print("  2. If geometry looks good, run final test:")
    print("     python scripts/md_fix_dissociated_ligands.py \\")
    print("         --complex 201_PfDHFR \\")
    print("         --input ions_docked.gro")
    print("")
    print("  3. If test passes, submit to HPC:")
    print("     sbatch MD_systems/201_PfDHFR/submit_production_md.sh")
    print("")
    print("  4. Monitor production MD (24-48 hours)")
    print("")
    print("  5. Run analysis pipeline")
    print("")
    print(f"📋 See {MD_DIR}/ANALYSIS_CHECKLIST.md for full workflow")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
