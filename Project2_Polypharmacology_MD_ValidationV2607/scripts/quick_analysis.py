#!/usr/bin/env python3
"""
Quick MD Trajectory Analysis - Lightweight version
Analyzes key metrics without loading full trajectory into memory
"""

import MDAnalysis as mda
import numpy as np
from pathlib import Path
import sys

# Paths
PROJECT_DIR = Path(__file__).parent.parent
SYSTEM_DIR = PROJECT_DIR / "214_PfCRT"

def quick_analysis():
    """Quick trajectory analysis"""
    print(f"\n{'='*80}")
    print("QUICK MD ANALYSIS: 214_PfCRT")
    print(f"{'='*80}\n")
    
    # Load trajectory
    topology = SYSTEM_DIR / "production.gro"
    trajectory = SYSTEM_DIR / "production.xtc"
    
    print(f"Loading trajectory...")
    u = mda.Universe(str(topology), str(trajectory))
    
    print(f"✓ Loaded: {len(u.trajectory)} frames")
    print(f"  Time span: {u.trajectory.totaltime / 1000:.1f} ns")
    print(f"  Total atoms: {len(u.atoms):,}\n")
    
    # Selections
    protein = u.select_atoms("protein")
    backbone = u.select_atoms("protein and backbone")
    
    # Try to find ligand
    try:
        ligand = u.select_atoms("resname UNL or resname LIG or resname MOL")
        if len(ligand) == 0:
            ligand = u.select_atoms(f"resid {u.residues[-1].resid}")
    except:
        ligand = None
    
    print(f"Selections:")
    print(f"  Protein: {len(protein):,} atoms")
    print(f"  Backbone: {len(backbone):,} atoms")
    if ligand:
        print(f"  Ligand: {len(ligand)} atoms (resname: {ligand.resnames[0]})\n")
    else:
        print(f"  Ligand: NOT FOUND\n")
        return
    
    # Sample every 10 frames for speed
    sample_frames = list(range(0, len(u.trajectory), 10))
    print(f"Analyzing {len(sample_frames)} frames (every 10th frame)...\n")
    
    # Initialize lists
    times = []
    bb_rmsd = []
    lig_rmsd = []
    min_dist = []
    
    # Reference structures
    u.trajectory[0]
    bb_ref = backbone.positions.copy()
    lig_ref = ligand.positions.copy()
    
    # Loop through frames
    for i, frame in enumerate(sample_frames):
        u.trajectory[frame]
        
        # Time
        times.append(u.trajectory.time / 1000)
        
        # Backbone RMSD
        from MDAnalysis.analysis.rms import rmsd
        bb_rmsd.append(rmsd(backbone.positions, bb_ref, superposition=True))
        
        # Ligand RMSD
        lig_rmsd.append(rmsd(ligand.positions, lig_ref, superposition=True))
        
        # Minimum distance
        from MDAnalysis.lib.distances import distance_array
        dist_array = distance_array(protein.positions, ligand.positions, box=u.dimensions)
        min_dist.append(dist_array.min())
        
        if (i+1) % 10 == 0:
            print(f"  Processed {i+1}/{len(sample_frames)} frames...")
    
    # Convert to arrays
    times = np.array(times)
    bb_rmsd = np.array(bb_rmsd)
    lig_rmsd = np.array(lig_rmsd)
    min_dist = np.array(min_dist)
    
    # Print results
    print(f"\n{'='*80}")
    print("RESULTS")
    print(f"{'='*80}\n")
    
    print(f"Backbone RMSD:")
    print(f"  Mean: {bb_rmsd.mean():.2f} ± {bb_rmsd.std():.2f} Å")
    print(f"  Range: {bb_rmsd.min():.2f} - {bb_rmsd.max():.2f} Å\n")
    
    print(f"Ligand RMSD:")
    print(f"  Mean: {lig_rmsd.mean():.2f} ± {lig_rmsd.std():.2f} Å")
    print(f"  Range: {lig_rmsd.min():.2f} - {lig_rmsd.max():.2f} Å\n")
    
    print(f"Protein-Ligand Minimum Distance:")
    print(f"  Mean: {min_dist.mean():.2f} ± {min_dist.std():.2f} Å")
    print(f"  Range: {min_dist.min():.2f} - {min_dist.max():.2f} Å")
    
    pct_bound = (min_dist < 5.0).sum() / len(min_dist) * 100
    print(f"  Time < 5 Å: {pct_bound:.1f}%")
    
    if min_dist.mean() < 5.0:
        print(f"\n  Status: ✅ STABLE BINDING")
    elif min_dist.mean() < 8.0:
        print(f"\n  Status: ⚠ WEAK BINDING")
    else:
        print(f"\n  Status: ❌ DISSOCIATED")
    
    print(f"\n{'='*80}\n")
    
    # Save summary
    summary_file = SYSTEM_DIR / "analysis" / "QUICK_SUMMARY.txt"
    summary_file.parent.mkdir(exist_ok=True)
    
    with open(summary_file, 'w') as f:
        f.write("="*80 + "\n")
        f.write("QUICK MD ANALYSIS SUMMARY: 214_PfCRT\n")
        f.write("="*80 + "\n\n")
        f.write(f"Frames analyzed: {len(sample_frames)} (every 10th frame)\n")
        f.write(f"Time span: {times[0]:.1f} - {times[-1]:.1f} ns\n\n")
        f.write(f"Backbone RMSD: {bb_rmsd.mean():.2f} ± {bb_rmsd.std():.2f} Å\n")
        f.write(f"Ligand RMSD: {lig_rmsd.mean():.2f} ± {lig_rmsd.std():.2f} Å\n")
        f.write(f"Min Distance: {min_dist.mean():.2f} ± {min_dist.std():.2f} Å\n")
        f.write(f"Time < 5 Å: {pct_bound:.1f}%\n\n")
        
        if min_dist.mean() < 5.0:
            f.write("Status: ✅ STABLE BINDING\n")
        elif min_dist.mean() < 8.0:
            f.write("Status: ⚠ WEAK BINDING\n")
        else:
            f.write("Status: ❌ DISSOCIATED\n")
        
        f.write("="*80 + "\n")
    
    print(f"✓ Summary saved to: {summary_file}")

if __name__ == "__main__":
    quick_analysis()
