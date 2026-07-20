#!/bin/bash
################################################################################
# Comprehensive Analysis for 214_PfCRT MD Trajectory
# 
# This script performs complete trajectory analysis including:
# - RMSD (backbone, ligand)
# - RMSF (per-residue flexibility)
# - Minimum distance (protein-ligand)
# - Radius of gyration
# - Energy analysis
# - Contact analysis
################################################################################

set -e

SYSTEM_DIR="/home/vital/Documents/GitHub/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607/214_PfCRT"
cd "$SYSTEM_DIR"

echo "=============================================================================="
echo "MD Trajectory Analysis: 214_PfCRT"
echo "=============================================================================="
echo "Working directory: $(pwd)"
echo "Start time: $(date)"
echo ""

# Check files exist
if [ ! -f "production.xtc" ]; then
    echo "ERROR: production.xtc not found!"
    exit 1
fi

if [ ! -f "production.tpr" ]; then
    echo "ERROR: production.tpr not found!"
    exit 1
fi

mkdir -p analysis

echo "=============================================================================="
echo "1. Extracting protein and ligand trajectory (centered)"
echo "=============================================================================="

# Group 1 = Protein, Group 13 = Other (ligand UNL)
echo "1 13" | gmx trjconv -s production.tpr -f production.xtc \
    -o analysis/protein_ligand.xtc -pbc mol -center -ur compact

echo "✓ Centered trajectory created"
echo ""

echo "=============================================================================="
echo "2. RMSD Analysis"
echo "=============================================================================="

# Backbone RMSD (C-alpha atoms, group 4)
echo "4 4" | gmx rms -s production.tpr -f analysis/protein_ligand.xtc \
    -o analysis/rmsd_backbone.xvg -tu ns

echo "✓ Backbone RMSD computed"

# Ligand RMSD (group 13 = Other/UNL)
echo "13 13" | gmx rms -s production.tpr -f analysis/protein_ligand.xtc \
    -o analysis/rmsd_ligand.xvg -tu ns

echo "✓ Ligand RMSD computed"
echo ""

echo "=============================================================================="
echo "3. RMSF Analysis (Per-Residue Flexibility)"
echo "=============================================================================="

# Backbone RMSF
echo "4" | gmx rmsf -s production.tpr -f analysis/protein_ligand.xtc \
    -o analysis/rmsf_backbone.xvg -res

echo "✓ RMSF computed"
echo ""

echo "=============================================================================="
echo "4. Radius of Gyration"
echo "=============================================================================="

# Protein gyration
echo "1" | gmx gyrate -s production.tpr -f analysis/protein_ligand.xtc \
    -o analysis/gyration.xvg -tu ns

echo "✓ Gyration computed"
echo ""

echo "=============================================================================="
echo "5. Minimum Distance (Protein-Ligand)"
echo "=============================================================================="

# Group 1 = Protein, Group 13 = ligand
echo "1 13" | gmx mindist -s production.tpr -f analysis/protein_ligand.xtc \
    -od analysis/mindist.xvg -tu ns -on analysis/numcont.xvg -d 0.6

echo "✓ Minimum distance computed"
echo ""

echo "=============================================================================="
echo "6. Energy Analysis"
echo "=============================================================================="

# Temperature
echo "16" | gmx energy -f production.edr -o analysis/temperature.xvg

# Pressure
echo "18" | gmx energy -f production.edr -o analysis/pressure.xvg

# Potential energy
echo "11" | gmx energy -f production.edr -o analysis/potential.xvg

# Density
echo "24" | gmx energy -f production.edr -o analysis/density.xvg

# Total energy
echo "12" | gmx energy -f production.edr -o analysis/total_energy.xvg

echo "✓ Energy analysis complete"
echo ""

echo "=============================================================================="
echo "7. Contact Analysis (Hydrogen Bonds)"
echo "=============================================================================="

# Protein-ligand H-bonds
echo "1 13" | gmx hbond -s production.tpr -f analysis/protein_ligand.xtc \
    -num analysis/hbonds.xvg -tu ns 2>/dev/null || echo "  (H-bond analysis skipped - may require different groups)"

echo ""

echo "=============================================================================="
echo "8. Generating Analysis Summary"
echo "=============================================================================="

# Extract key statistics
python3 << 'PYEOF'
import numpy as np
import os

analysis_dir = "analysis"

def read_xvg(filename):
    """Read GROMACS .xvg file, skip comments"""
    data = []
    with open(filename, 'r') as f:
        for line in f:
            if not line.startswith(('#', '@')):
                data.append([float(x) for x in line.split()])
    return np.array(data)

def safe_read(filename, desc):
    """Safely read file with error handling"""
    filepath = os.path.join(analysis_dir, filename)
    try:
        if os.path.exists(filepath):
            data = read_xvg(filepath)
            return data, True
        else:
            print(f"  ⚠ {desc}: File not found")
            return None, False
    except Exception as e:
        print(f"  ⚠ {desc}: Error reading file - {e}")
        return None, False

print("\n" + "="*80)
print("ANALYSIS SUMMARY: 214_PfCRT")
print("="*80 + "\n")

# RMSD Backbone
data, success = safe_read("rmsd_backbone.xvg", "Backbone RMSD")
if success and data is not None:
    rmsd_bb = data[:, 1] * 10  # Convert nm to Angstrom
    print(f"Backbone RMSD:")
    print(f"  Mean:    {rmsd_bb.mean():.2f} Å")
    print(f"  Std Dev: {rmsd_bb.std():.2f} Å")
    print(f"  Min:     {rmsd_bb.min():.2f} Å")
    print(f"  Max:     {rmsd_bb.max():.2f} Å")
    print(f"  Final:   {rmsd_bb[-1]:.2f} Å")
    print()

# RMSD Ligand
data, success = safe_read("rmsd_ligand.xvg", "Ligand RMSD")
if success and data is not None:
    rmsd_lig = data[:, 1] * 10  # Convert nm to Angstrom
    print(f"Ligand RMSD:")
    print(f"  Mean:    {rmsd_lig.mean():.2f} Å")
    print(f"  Std Dev: {rmsd_lig.std():.2f} Å")
    print(f"  Min:     {rmsd_lig.min():.2f} Å")
    print(f"  Max:     {rmsd_lig.max():.2f} Å")
    print(f"  Final:   {rmsd_lig[-1]:.2f} Å")
    print()

# Minimum Distance
data, success = safe_read("mindist.xvg", "Minimum Distance")
if success and data is not None:
    mindist = data[:, 1] * 10  # Convert nm to Angstrom
    print(f"Protein-Ligand Minimum Distance:")
    print(f"  Mean:    {mindist.mean():.2f} Å")
    print(f"  Std Dev: {mindist.std():.2f} Å")
    print(f"  Min:     {mindist.min():.2f} Å")
    print(f"  Max:     {mindist.max():.2f} Å")
    print(f"  Final:   {mindist[-1]:.2f} Å")
    
    # Check binding stability
    if mindist.mean() < 5.0:
        print(f"  Status:  ✅ STABLE BINDING (avg < 5 Å)")
    elif mindist.mean() < 8.0:
        print(f"  Status:  ⚠ WEAK BINDING (5-8 Å)")
    else:
        print(f"  Status:  ❌ DISSOCIATED (avg > 8 Å)")
    print()

# Gyration
data, success = safe_read("gyration.xvg", "Radius of Gyration")
if success and data is not None:
    rg = data[:, 1] * 10  # Convert nm to Angstrom
    print(f"Radius of Gyration:")
    print(f"  Mean:    {rg.mean():.2f} Å")
    print(f"  Std Dev: {rg.std():.2f} Å")
    print()

# Temperature
data, success = safe_read("temperature.xvg", "Temperature")
if success and data is not None:
    temp = data[:, 1]
    print(f"Temperature:")
    print(f"  Mean:    {temp.mean():.2f} K")
    print(f"  Std Dev: {temp.std():.2f} K")
    print(f"  Target:  310.15 K")
    print()

# Density
data, success = safe_read("density.xvg", "Density")
if success and data is not None:
    dens = data[:, 1]
    print(f"Density:")
    print(f"  Mean:    {dens.mean():.3f} g/cm³")
    print(f"  Std Dev: {dens.std():.3f} g/cm³")
    print(f"  Expected: ~1.0 g/cm³")
    print()

# H-bonds (if available)
data, success = safe_read("hbonds.xvg", "H-bonds")
if success and data is not None:
    hbonds = data[:, 1]
    print(f"Protein-Ligand Hydrogen Bonds:")
    print(f"  Mean:    {hbonds.mean():.1f}")
    print(f"  Max:     {int(hbonds.max())}")
    print()

print("="*80)
print("Analysis files saved in: analysis/")
print("="*80 + "\n")

# Save summary to file
with open(os.path.join(analysis_dir, "ANALYSIS_SUMMARY.txt"), 'w') as f:
    f.write("="*80 + "\n")
    f.write("MD TRAJECTORY ANALYSIS SUMMARY: 214_PfCRT\n")
    f.write("="*80 + "\n\n")
    f.write(f"Analysis Date: {os.popen('date').read()}\n")
    f.write(f"Trajectory: production.xtc\n")
    f.write(f"System: PfCRT + Ligand 214\n\n")
    
    # Recompute and write to file
    for metric, file, scale, unit in [
        ("Backbone RMSD", "rmsd_backbone.xvg", 10, "Å"),
        ("Ligand RMSD", "rmsd_ligand.xvg", 10, "Å"),
        ("Min Distance", "mindist.xvg", 10, "Å"),
        ("Gyration", "gyration.xvg", 10, "Å"),
        ("Temperature", "temperature.xvg", 1, "K"),
        ("Density", "density.xvg", 1, "g/cm³"),
    ]:
        filepath = os.path.join(analysis_dir, file)
        if os.path.exists(filepath):
            try:
                data = read_xvg(filepath)
                values = data[:, 1] * scale
                f.write(f"{metric}:\n")
                f.write(f"  Mean: {values.mean():.2f} {unit}\n")
                f.write(f"  SD:   {values.std():.2f} {unit}\n")
                f.write(f"  Range: {values.min():.2f} - {values.max():.2f} {unit}\n\n")
            except:
                pass

print("✓ Summary saved to: analysis/ANALYSIS_SUMMARY.txt\n")

PYEOF

echo "=============================================================================="
echo "ANALYSIS COMPLETE!"
echo "=============================================================================="
echo ""
echo "Output files in analysis/:"
ls -lh analysis/
echo ""
echo "Key files:"
echo "  - ANALYSIS_SUMMARY.txt    : Text summary of all metrics"
echo "  - rmsd_backbone.xvg       : Backbone RMSD over time"
echo "  - rmsd_ligand.xvg         : Ligand RMSD over time"
echo "  - mindist.xvg             : Protein-ligand distance"
echo "  - rmsf_backbone.xvg       : Per-residue flexibility"
echo "  - gyration.xvg            : Radius of gyration"
echo "  - temperature.xvg         : Temperature profile"
echo "  - density.xvg             : Density profile"
echo ""
echo "Next steps:"
echo "  1. Review ANALYSIS_SUMMARY.txt for key metrics"
echo "  2. Generate figures: python scripts/plot_md_analysis.py"
echo "  3. Visualize trajectory: pymol production.gro production.xtc"
echo ""
echo "End time: $(date)"
echo "=============================================================================="

