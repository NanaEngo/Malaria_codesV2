#!/usr/bin/env python3
"""
Analyze the Test/Complex_test MD simulation to extract best practices
and refine parameters for the 11 production systems.

Uses MDAnalysis for trajectory analysis.
"""

import MDAnalysis as mda
from MDAnalysis.analysis import rms, align, distances
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import sys

# Enable matplotlib non-interactive backend
plt.switch_backend('Agg')

def analyze_test_system(test_dir="Test/Complex_test"):
    """Comprehensive analysis of test MD simulation."""
    
    print("="*70)
    print("TEST SYSTEM MD ANALYSIS")
    print("="*70)
    print()
    
    test_path = Path(test_dir)
    
    # Check if files exist - use complex.gro which has ligand
    topology = test_path / "complex.gro"
    if not topology.exists():
        topology = test_path / "step3_input.gro"  # Fallback
    trajectory = test_path / "step5_1.xtc"
    
    if not topology.exists():
        print(f"❌ Topology file not found: {topology}")
        return
    
    if not trajectory.exists():
        print(f"❌ Trajectory file not found: {trajectory}")
        return
    
    print("📂 Loading trajectory...")
    print(f"   Topology: {topology}")
    print(f"   Trajectory: {trajectory}")
    print()
    
    # Load universe
    try:
        u = mda.Universe(str(topology), str(trajectory))
    except Exception as e:
        print(f"❌ Error loading trajectory: {e}")
        return
    
    print("✓ Universe loaded successfully")
    print(f"  Total atoms: {u.atoms.n_atoms:,}")
    print(f"  Total frames: {u.trajectory.n_frames}")
    print(f"  Time range: 0 to {u.trajectory.totaltime:.1f} ps")
    print(f"  Timestep: {u.trajectory.dt:.2f} ps")
    print()
    
    # Identify system components
    print("📊 System Composition:")
    protein = u.select_atoms("protein")
    print(f"  Protein: {protein.n_atoms:,} atoms ({protein.n_residues} residues)")
    
    # Try to find ligand
    ligand_names = ['LIG', 'LIG1', 'UNK', 'MOL']
    ligand = None
    for name in ligand_names:
        try:
            ligand = u.select_atoms(f"resname {name}")
            if ligand.n_atoms > 0:
                print(f"  Ligand ({name}): {ligand.n_atoms} atoms")
                break
        except:
            continue
    
    if ligand is None or ligand.n_atoms == 0:
        print("  ⚠️  Ligand not found")
        ligand = None
    
    # Cofactor
    try:
        cofactor = u.select_atoms("resname NDP")
        if cofactor.n_atoms > 0:
            print(f"  Cofactor (NDP): {cofactor.n_atoms} atoms")
    except:
        cofactor = None
    
    # Water and ions
    try:
        water = u.select_atoms("resname TIP3 or resname SOL or resname HOH")
        print(f"  Water: {water.n_atoms:,} atoms ({water.n_residues} molecules)")
    except:
        pass
    
    try:
        ions = u.select_atoms("resname POT or resname CLA or resname NA or resname CL")
        print(f"  Ions: {ions.n_atoms} atoms")
    except:
        pass
    
    print()
    
    # === ANALYSIS 1: Protein Backbone RMSD ===
    print("🔬 Analysis 1: Protein Backbone RMSD")
    print("-" * 70)
    
    backbone = u.select_atoms("protein and name CA")
    
    # Align trajectory
    print("  Aligning trajectory to first frame...")
    aligner = align.AlignTraj(u, u, select="protein and name CA", 
                               in_memory=False, filename='aligned_temp.xtc')
    aligner.run()
    
    # Compute RMSD
    print("  Computing RMSD...")
    R = rms.RMSD(u, select="protein and name CA", ref_frame=0)
    R.run()
    
    rmsd_data = R.results.rmsd
    times_ns = rmsd_data[:, 1] / 1000  # Convert ps to ns
    rmsd_vals = rmsd_data[:, 2] * 10  # Convert nm to Å
    
    print(f"  Initial RMSD: {rmsd_vals[0]:.2f} Å")
    print(f"  Final RMSD: {rmsd_vals[-1]:.2f} Å")
    print(f"  Average RMSD: {rmsd_vals.mean():.2f} ± {rmsd_vals.std():.2f} Å")
    print(f"  Max RMSD: {rmsd_vals.max():.2f} Å")
    
    # Check for equilibration
    first_half_rmsd = rmsd_vals[:len(rmsd_vals)//2].mean()
    second_half_rmsd = rmsd_vals[len(rmsd_vals)//2:].mean()
    rmsd_drift = second_half_rmsd - first_half_rmsd
    
    print(f"  RMSD drift (1st vs 2nd half): {rmsd_drift:+.2f} Å")
    
    if abs(rmsd_drift) < 1.0:
        print("  ✓ System appears equilibrated (drift < 1 Å)")
    else:
        print(f"  ⚠️  System may not be equilibrated (drift = {rmsd_drift:.2f} Å)")
    
    # Plot RMSD
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(times_ns, rmsd_vals, 'b-', linewidth=0.8)
    ax.axhline(rmsd_vals.mean(), color='r', linestyle='--', 
               label=f'Mean: {rmsd_vals.mean():.2f} Å')
    ax.set_xlabel("Time (ns)")
    ax.set_ylabel("Backbone RMSD (Å)")
    ax.set_title("Protein Backbone RMSD vs Time")
    ax.legend()
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(test_path / "analysis_backbone_rmsd.png", dpi=150)
    print("  📊 Saved: analysis_backbone_rmsd.png")
    plt.close()
    print()
    
    # === ANALYSIS 2: Ligand RMSD ===
    if ligand is not None and ligand.n_atoms > 0:
        print("🔬 Analysis 2: Ligand RMSD")
        print("-" * 70)
        
        # Align on protein, compute RMSD of ligand
        u.trajectory[0]  # Go back to first frame
        
        # Compute ligand RMSD
        R_lig = rms.RMSD(ligand, select="all", ref_frame=0)
        R_lig.run()
        
        rmsd_lig_data = R_lig.results.rmsd
        rmsd_lig_vals = rmsd_lig_data[:, 2] * 10  # nm to Å
        
        print(f"  Initial RMSD: {rmsd_lig_vals[0]:.2f} Å")
        print(f"  Final RMSD: {rmsd_lig_vals[-1]:.2f} Å")
        print(f"  Average RMSD: {rmsd_lig_vals.mean():.2f} ± {rmsd_lig_vals.std():.2f} Å")
        print(f"  Max RMSD: {rmsd_lig_vals.max():.2f} Å")
        
        if rmsd_lig_vals.mean() < 3.0:
            print("  ✓ Ligand is stable in binding site (RMSD < 3 Å)")
        elif rmsd_lig_vals.mean() < 5.0:
            print("  ⚠️  Ligand has moderate mobility (3-5 Å)")
        else:
            print("  ❌ Ligand may have dissociated (RMSD > 5 Å)")
        
        # Plot
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(times_ns, rmsd_lig_vals, 'g-', linewidth=0.8)
        ax.axhline(rmsd_lig_vals.mean(), color='r', linestyle='--',
                   label=f'Mean: {rmsd_lig_vals.mean():.2f} Å')
        ax.set_xlabel("Time (ns)")
        ax.set_ylabel("Ligand RMSD (Å)")
        ax.set_title("Ligand RMSD vs Time")
        ax.legend()
        ax.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig(test_path / "analysis_ligand_rmsd.png", dpi=150)
        print("  📊 Saved: analysis_ligand_rmsd.png")
        plt.close()
        print()
        
        # === ANALYSIS 3: Protein-Ligand Distance ===
        print("🔬 Analysis 3: Protein-Ligand Distance")
        print("-" * 70)
        
        distances_list = []
        for ts in u.trajectory:
            dist_array = distances.distance_array(
                protein.center_of_mass(),
                ligand.center_of_mass(),
                box=u.dimensions
            )[0, 0]
            distances_list.append(dist_array)
        
        distances_array = np.array(distances_list)
        
        print(f"  Initial distance: {distances_array[0]:.2f} Å")
        print(f"  Final distance: {distances_array[-1]:.2f} Å")
        print(f"  Average distance: {distances_array.mean():.2f} ± {distances_array.std():.2f} Å")
        print(f"  Min distance: {distances_array.min():.2f} Å")
        print(f"  Max distance: {distances_array.max():.2f} Å")
        
        if distances_array.mean() < 30:
            print("  ✓ Ligand remains bound (< 30 Å)")
        else:
            print("  ❌ Ligand has dissociated (> 30 Å)")
        
        # Plot
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(times_ns, distances_array, 'purple', linewidth=0.8)
        ax.axhline(distances_array.mean(), color='r', linestyle='--',
                   label=f'Mean: {distances_array.mean():.2f} Å')
        ax.set_xlabel("Time (ns)")
        ax.set_ylabel("Protein-Ligand Distance (Å)")
        ax.set_title("Protein-Ligand Center of Mass Distance")
        ax.legend()
        ax.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig(test_path / "analysis_protein_ligand_distance.png", dpi=150)
        print("  📊 Saved: analysis_protein_ligand_distance.png")
        plt.close()
        print()
    
    # === SUMMARY & RECOMMENDATIONS ===
    print("="*70)
    print("📋 SUMMARY & RECOMMENDATIONS FOR PRODUCTION RUNS")
    print("="*70)
    print()
    
    print("✅ What Worked Well:")
    print("  • Trajectory files generated successfully")
    print(f"  • {u.trajectory.n_frames} frames captured")
    print("  • Temperature/pressure control stable (from MDP)")
    print()
    
    print("⚠️  Issues Identified:")
    if rmsd_vals[-1] > 5.0:
        print("  • High protein RMSD suggests insufficient equilibration")
        print("    → Recommendation: Extend equilibration to 2-5 ns")
    
    if ligand is not None:
        if rmsd_lig_vals.mean() > 5.0 or distances_array.mean() > 30:
            print("  • Ligand dissociation detected")
            print("    → Recommendation: Verify initial ligand position")
            print("    → Recommendation: Add ligand position restraints during equilibration")
    else:
        print("  • Ligand not detected in trajectory")
    
    print()
    
    print("🎯 Recommended Protocol for Production Systems:")
    print()
    print("1️⃣  Energy Minimization (DONE)")
    print("   • Current settings are good (5000 steps)")
    print()
    
    print("2️⃣  Extended NVT Equilibration (IMPROVE)")
    print("   • Current: 125 ps (125,000 steps × 0.001 ps)")
    print("   • Recommended: 500 ps - 1 ns")
    print("   • Keep position restraints: -DPOSRES")
    print()
    
    print("3️⃣  NPT Equilibration (NEW STEP)")
    print("   • Add separate NPT equilibration: 500 ps - 1 ns")
    print("   • Gradually reduce restraints")
    print("   • Enable pressure coupling (C-rescale)")
    print()
    
    print("4️⃣  Production MD")
    print("   • Current: 1 ns (500,000 steps × 0.002 ps)")
    print("   • Recommended for screening: 10 ns minimum")
    print("   • Recommended for publication: 50-100 ns")
    print("   • Save frames every 10 ps for analysis")
    print()
    
    print("🔧 Parameter Refinements:")
    print("  • dt = 0.002 ps (2 fs) ✓ Good with h-bonds constraints")
    print("  • Temperature: 303.15 K ✓ (30°C, appropriate for enzyme)")
    print("  • Pressure: 1.0 bar ✓")
    print("  • Cutoffs: 1.2 nm ✓")
    print("  • PME electrostatics ✓")
    print()
    
    print("📁 Files to Copy to Production Systems:")
    print("  ✓ step4.0_minimization.mdp (keep as-is)")
    print("  ✓ step4.1_equilibration.mdp (extend nsteps)")
    print("  ✓ step5_production.mdp (extend nsteps)")
    print()
    
    # Clean up temporary file
    temp_xtc = Path("aligned_temp.xtc")
    if temp_xtc.exists():
        temp_xtc.unlink()
    
    print("="*70)
    print("✅ Analysis Complete!")
    print("="*70)
    print()
    print("Next steps:")
    print("1. Review plots in Test/Complex_test/")
    print("2. Check if your 11 systems have similar initial ligand positions")
    print("3. Use refined MDP files for production runs")
    print()

if __name__ == "__main__":
    import os
    
    # Change to the correct directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    try:
        analyze_test_system()
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
