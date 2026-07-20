#!/usr/bin/env python3
"""
Comprehensive MDAnalysis trajectory analysis for 214_PfCRT
Output directory: MD_systems/214_PfCRT/production_analysis/
"""

import MDAnalysis as mda
from MDAnalysis.analysis import rms, align, distances, hydrogenbonds
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Publication style
plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['legend.fontsize'] = 9

# Paths
PROJECT_DIR = Path(__file__).parent.parent
SYSTEM_DIR = PROJECT_DIR / "MD_systems" / "214_PfCRT"
OUTPUT_DIR = SYSTEM_DIR / "production_analysis"
FIGURES_DIR = OUTPUT_DIR / "figures"
DATA_DIR = OUTPUT_DIR / "data"

# Create directories
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)
FIGURES_DIR.mkdir(exist_ok=True, parents=True)
DATA_DIR.mkdir(exist_ok=True, parents=True)

print("="*80)
print("COMPREHENSIVE MD ANALYSIS: 214_PfCRT Production Trajectory")
print("="*80)
print(f"\nSystem directory: {SYSTEM_DIR}")
print(f"Output directory: {OUTPUT_DIR}")
print(f"Figures: {FIGURES_DIR}")
print(f"Data: {DATA_DIR}\n")

# Load trajectory
print("Loading trajectory...")
topology = SYSTEM_DIR / "production.gro"
trajectory = SYSTEM_DIR / "production.xtc"

if not topology.exists() or not trajectory.exists():
    print(f"ERROR: Files not found!")
    print(f"  Topology: {topology} (exists: {topology.exists()})")
    print(f"  Trajectory: {trajectory} (exists: {trajectory.exists()})")
    exit(1)

u = mda.Universe(str(topology), str(trajectory))
print(f"✓ Loaded: {u.atoms.n_atoms} atoms, {u.trajectory.n_frames} frames")
print(f"  Time: {u.trajectory[0].time:.1f} - {u.trajectory[-1].time:.1f} ps")
print(f"  Timestep: {u.trajectory.dt:.1f} ps")


# Identify protein and ligand
protein = u.select_atoms("protein")
print(f"\n✓ Protein: {protein.n_atoms} atoms, {protein.n_residues} residues")

# Find ligand
ligand_names = ['LIG', 'UNL', 'MOL', 'DRG', 'INH']
ligand = None
for name in ligand_names:
    try:
        ligand = u.select_atoms(f"resname {name}")
        if ligand.n_atoms > 0:
            print(f"✓ Ligand: resname {name}, {ligand.n_atoms} atoms")
            break
    except:
        pass

if ligand is None or ligand.n_atoms == 0:
    ligand = u.select_atoms("not protein and not resname WAT SOL TIP3 HOH NA CL K")
    if ligand.n_atoms > 0:
        print(f"✓ Ligand: {ligand.resnames[0]}, {ligand.n_atoms} atoms")

if ligand is None or ligand.n_atoms == 0:
    print("ERROR: Could not identify ligand!")
    exit(1)

ligand_resname = ligand.resnames[0]

print("\n" + "="*80)
print("1. RMSD Analysis")
print("="*80)

print("  Aligning trajectory...")
aligner = align.AlignTraj(u, u, select="backbone", in_memory=False)
aligner.run()
print("  ✓ Alignment complete")

print("  Computing backbone RMSD...")
rmsd_bb = rms.RMSD(u, select="backbone", ref_frame=0)
rmsd_bb.run()
bb_data = rmsd_bb.results.rmsd
print(f"    Mean: {bb_data[:, 2].mean():.2f} ± {bb_data[:, 2].std():.2f} Å")

print("  Computing ligand RMSD...")
rmsd_lig = rms.RMSD(u, select=f"resname {ligand_resname}", ref_frame=0)
rmsd_lig.run()
lig_data = rmsd_lig.results.rmsd
print(f"    Mean: {lig_data[:, 2].mean():.2f} ± {lig_data[:, 2].std():.2f} Å")

np.savetxt(DATA_DIR / "rmsd_backbone.dat", bb_data, 
           header="Frame Time(ps) RMSD(Angstrom)", fmt="%.3f")
np.savetxt(DATA_DIR / "rmsd_ligand.dat", lig_data,
           header="Frame Time(ps) RMSD(Angstrom)", fmt="%.3f")


print("\n" + "="*80)
print("2. RMSF Analysis")
print("="*80)

start_frame = len(u.trajectory) // 2
print(f"  Using equilibrated portion: frames {start_frame}-{len(u.trajectory)}")

calphas = u.select_atoms("protein and name CA")
print(f"  Computing RMSF for {calphas.n_atoms} Cα atoms...")

u.trajectory[start_frame]
avg_pos = np.zeros((calphas.n_atoms, 3))
for ts in u.trajectory[start_frame:]:
    avg_pos += calphas.positions
avg_pos /= (len(u.trajectory) - start_frame)

rmsf_values = np.zeros(calphas.n_atoms)
for ts in u.trajectory[start_frame:]:
    rmsf_values += np.sqrt(np.sum((calphas.positions - avg_pos)**2, axis=1))
rmsf_values /= (len(u.trajectory) - start_frame)

resids = calphas.resids
rmsf_data = np.column_stack([resids, rmsf_values])
np.savetxt(DATA_DIR / "rmsf_calpha.dat", rmsf_data,
           header="ResID RMSF(Angstrom)", fmt="%d %.3f")

print(f"  Mean: {rmsf_values.mean():.2f} Å, Max: {rmsf_values.max():.2f} Å")

print("\n" + "="*80)
print("3. Distance Analysis")
print("="*80)

min_dists = []
com_dists = []
times = []

protein_heavy = protein.select_atoms("not name H*")
ligand_heavy = ligand.select_atoms("not name H*")

print(f"  Computing distances for {len(u.trajectory)} frames...")
for ts in u.trajectory:
    times.append(ts.time)
    
    dist_array = distances.distance_array(
        protein_heavy.positions, 
        ligand_heavy.positions
    )
    min_dists.append(dist_array.min())
    
    com_dist = np.linalg.norm(
        protein.center_of_mass() - ligand.center_of_mass()
    )
    com_dists.append(com_dist)

min_dists = np.array(min_dists)
com_dists = np.array(com_dists)
times = np.array(times)

print(f"  Min distance: {min_dists.mean():.2f} ± {min_dists.std():.2f} Å")
print(f"  COM distance: {com_dists.mean():.2f} ± {com_dists.std():.2f} Å")
print(f"  Time < 5 Å: {100*np.sum(min_dists < 5)/len(min_dists):.1f}%")

dist_data = np.column_stack([times, min_dists, com_dists])
np.savetxt(DATA_DIR / "distances.dat", dist_data,
           header="Time(ps) MinDist(Angstrom) COMDist(Angstrom)", fmt="%.3f")


print("\n" + "="*80)
print("4. Contact Analysis")
print("="*80)

contact_cutoff = 4.5
print(f"  Contact cutoff: {contact_cutoff} Å")

contact_counts = {}
total_frames = len(u.trajectory)

for ts in u.trajectory:
    dist_array = distances.distance_array(
        protein_heavy.positions,
        ligand_heavy.positions
    )
    
    in_contact_idx = np.where(dist_array < contact_cutoff)[0]
    contact_atoms = protein_heavy[in_contact_idx]
    
    for atom in contact_atoms:
        key = f"{atom.resname}{atom.resid}"
        contact_counts[key] = contact_counts.get(key, 0) + 1

contact_persistence = {k: v/total_frames for k, v in contact_counts.items()}
sorted_contacts = sorted(contact_persistence.items(), key=lambda x: x[1], reverse=True)

print(f"  Unique contact residues: {len(sorted_contacts)}")
print(f"\n  Top 10 contacts:")
for res, persistence in sorted_contacts[:10]:
    print(f"    {res:8s}: {persistence*100:5.1f}%")

with open(DATA_DIR / "contact_persistence.dat", 'w') as f:
    f.write("# Residue Persistence(%) Frames\n")
    for res, persistence in sorted_contacts:
        f.write(f"{res:8s} {persistence*100:6.2f} {int(persistence*total_frames):5d}\n")

print("\n" + "="*80)
print("5. Hydrogen Bonds")
print("="*80)

try:
    print("  Computing H-bonds...")
    hbonds = hydrogenbonds.hbond_analysis.HydrogenBondAnalysis(
        universe=u,
        donors_sel="protein",
        hydrogens_sel="protein",
        acceptors_sel=f"resname {ligand_resname}",
        d_a_cutoff=3.5,
        d_h_a_angle_cutoff=150
    )
    hbonds.run(verbose=False)
    
    if hasattr(hbonds, 'results') and hasattr(hbonds.results, 'hbonds'):
        hb_data = hbonds.results.hbonds
        print(f"  H-bond occurrences: {len(hb_data)}")
        
        with open(DATA_DIR / "hbonds_summary.txt", 'w') as f:
            f.write(f"Total H-bond occurrences: {len(hb_data)}\n")
            f.write(f"Trajectory frames: {total_frames}\n")
            f.write(f"Average H-bonds per frame: {len(hb_data)/total_frames:.2f}\n")
    else:
        print("  No H-bonds detected")
except Exception as e:
    print(f"  H-bond analysis failed: {e}")


print("\n" + "="*80)
print("6. Generating Figures")
print("="*80)

# Figure 1: RMSD 3-panel
fig = plt.figure(figsize=(16, 5))
gs = gridspec.GridSpec(1, 3, figure=fig, wspace=0.3)

ax1 = fig.add_subplot(gs[0, 0])
ax1.plot(bb_data[:, 1]/1000, bb_data[:, 2], 'b-', linewidth=1.5, alpha=0.8)
ax1.axhline(bb_data[:, 2].mean(), color='r', linestyle='--', linewidth=2,
            label=f'Mean: {bb_data[:, 2].mean():.2f} Å')
ax1.set_xlabel('Time (ns)', fontweight='bold')
ax1.set_ylabel('RMSD (Å)', fontweight='bold')
ax1.set_title('A. Protein Backbone RMSD', fontweight='bold')
ax1.legend()
ax1.grid(True, alpha=0.3)

ax2 = fig.add_subplot(gs[0, 1])
ax2.plot(lig_data[:, 1]/1000, lig_data[:, 2], 'g-', linewidth=1.5, alpha=0.8)
ax2.axhline(lig_data[:, 2].mean(), color='r', linestyle='--', linewidth=2,
            label=f'Mean: {lig_data[:, 2].mean():.2f} Å')
ax2.set_xlabel('Time (ns)', fontweight='bold')
ax2.set_ylabel('RMSD (Å)', fontweight='bold')
ax2.set_title('B. Ligand RMSD', fontweight='bold')
ax2.legend()
ax2.grid(True, alpha=0.3)

ax3 = fig.add_subplot(gs[0, 2])
ax3.plot(times/1000, min_dists, 'purple', linewidth=1.5, alpha=0.8)
ax3.axhline(5.0, color='orange', linestyle=':', linewidth=2, label='5 Å threshold')
ax3.axhline(min_dists.mean(), color='r', linestyle='--', linewidth=2,
            label=f'Mean: {min_dists.mean():.2f} Å')
ax3.set_xlabel('Time (ns)', fontweight='bold')
ax3.set_ylabel('Min Distance (Å)', fontweight='bold')
ax3.set_title('C. Protein-Ligand Distance', fontweight='bold')
ax3.legend()
ax3.grid(True, alpha=0.3)

plt.suptitle('214_PfCRT: RMSD and Binding Stability', fontsize=15, fontweight='bold')
plt.savefig(FIGURES_DIR / "rmsd_panel.png", dpi=300, bbox_inches='tight')
print(f"  ✓ Saved: rmsd_panel.png")
plt.close()

# Figure 2: RMSF + Contacts
fig = plt.figure(figsize=(16, 6))
gs = gridspec.GridSpec(1, 2, figure=fig, wspace=0.3, width_ratios=[2, 1])

ax1 = fig.add_subplot(gs[0, 0])
ax1.plot(resids, rmsf_values, 'b-', linewidth=1.5)
ax1.axhline(rmsf_values.mean(), color='r', linestyle='--', linewidth=2,
            label=f'Mean: {rmsf_values.mean():.2f} Å')
ax1.fill_between(resids, 0, rmsf_values, alpha=0.3, color='blue')
ax1.set_xlabel('Residue Number', fontweight='bold')
ax1.set_ylabel('RMSF (Å)', fontweight='bold')
ax1.set_title('A. Per-Residue Flexibility', fontweight='bold')
ax1.legend()
ax1.grid(True, alpha=0.3)

ax2 = fig.add_subplot(gs[0, 1])
top15 = sorted_contacts[:15]
residues = [c[0] for c in top15]
persistence_pct = [c[1]*100 for c in top15]
colors = ['green' if p > 50 else 'orange' if p > 25 else 'gray' for p in persistence_pct]
ax2.barh(range(len(residues)), persistence_pct, color=colors, alpha=0.7)
ax2.set_yticks(range(len(residues)))
ax2.set_yticklabels(residues, fontsize=9)
ax2.set_xlabel('Persistence (%)', fontweight='bold')
ax2.set_title('B. Top Contact Residues', fontweight='bold')
ax2.axvline(50, color='red', linestyle='--', alpha=0.5)
ax2.invert_yaxis()
ax2.grid(True, alpha=0.3, axis='x')

plt.suptitle('214_PfCRT: Flexibility and Ligand Contacts', fontsize=15, fontweight='bold')
plt.savefig(FIGURES_DIR / "rmsf_contacts.png", dpi=300, bbox_inches='tight')
print(f"  ✓ Saved: rmsf_contacts.png")
plt.close()


# Figure 3: Timeline
fig = plt.figure(figsize=(16, 10))
gs = gridspec.GridSpec(4, 1, figure=fig, hspace=0.4)

ax1 = fig.add_subplot(gs[0, 0])
ax1.plot(bb_data[:, 1]/1000, bb_data[:, 2], 'b-', linewidth=1.2)
ax1.set_ylabel('Backbone RMSD (Å)', fontweight='bold')
ax1.set_title('A. Protein Stability', fontweight='bold', loc='left')
ax1.grid(True, alpha=0.3)
ax1.set_xticklabels([])

ax2 = fig.add_subplot(gs[1, 0])
ax2.plot(lig_data[:, 1]/1000, lig_data[:, 2], 'g-', linewidth=1.2)
ax2.set_ylabel('Ligand RMSD (Å)', fontweight='bold')
ax2.set_title('B. Ligand Position', fontweight='bold', loc='left')
ax2.grid(True, alpha=0.3)
ax2.set_xticklabels([])

ax3 = fig.add_subplot(gs[2, 0])
ax3.plot(times/1000, min_dists, 'purple', linewidth=1.2)
ax3.axhline(5.0, color='red', linestyle='--', alpha=0.5)
ax3.set_ylabel('Min Distance (Å)', fontweight='bold')
ax3.set_title('C. Protein-Ligand Proximity', fontweight='bold', loc='left')
ax3.grid(True, alpha=0.3)
ax3.set_xticklabels([])

ax4 = fig.add_subplot(gs[3, 0])
ax4.plot(times/1000, com_dists, 'orange', linewidth=1.2)
ax4.set_ylabel('COM Distance (Å)', fontweight='bold')
ax4.set_xlabel('Time (ns)', fontweight='bold')
ax4.set_title('D. Center-of-Mass Distance', fontweight='bold', loc='left')
ax4.grid(True, alpha=0.3)

plt.suptitle('214_PfCRT: Complete Trajectory Timeline', fontsize=16, fontweight='bold')
plt.savefig(FIGURES_DIR / "timeline.png", dpi=300, bbox_inches='tight')
print(f"  ✓ Saved: timeline.png")
plt.close()

print("\n" + "="*80)
print("7. Writing Summary Report")
print("="*80)

report_file = OUTPUT_DIR / "ANALYSIS_REPORT.txt"
with open(report_file, 'w') as f:
    f.write("="*80 + "\n")
    f.write("MD TRAJECTORY ANALYSIS: 214_PfCRT\n")
    f.write("="*80 + "\n\n")
    
    f.write(f"System: PfCRT + Ligand {ligand_resname}\n")
    f.write(f"Total atoms: {u.atoms.n_atoms:,}\n")
    f.write(f"Protein: {protein.n_atoms} atoms, {protein.n_residues} residues\n")
    f.write(f"Ligand: {ligand.n_atoms} atoms\n")
    f.write(f"Frames: {len(u.trajectory)}\n")
    f.write(f"Time: {u.trajectory[0].time:.1f} - {u.trajectory[-1].time:.1f} ps\n\n")
    
    f.write("="*80 + "\n")
    f.write("RESULTS\n")
    f.write("="*80 + "\n\n")
    
    f.write("Backbone RMSD:\n")
    f.write(f"  Mean: {bb_data[:, 2].mean():.3f} ± {bb_data[:, 2].std():.3f} Å\n")
    f.write(f"  Range: {bb_data[:, 2].min():.3f} - {bb_data[:, 2].max():.3f} Å\n\n")
    
    f.write("Ligand RMSD:\n")
    f.write(f"  Mean: {lig_data[:, 2].mean():.3f} ± {lig_data[:, 2].std():.3f} Å\n")
    f.write(f"  Range: {lig_data[:, 2].min():.3f} - {lig_data[:, 2].max():.3f} Å\n\n")
    
    f.write("RMSF:\n")
    f.write(f"  Mean: {rmsf_values.mean():.3f} ± {rmsf_values.std():.3f} Å\n")
    f.write(f"  Max: {rmsf_values.max():.3f} Å\n\n")
    
    f.write("Distances:\n")
    f.write(f"  Min distance: {min_dists.mean():.3f} ± {min_dists.std():.3f} Å\n")
    f.write(f"  COM distance: {com_dists.mean():.3f} ± {com_dists.std():.3f} Å\n")
    f.write(f"  Time < 5 Å: {100*np.sum(min_dists < 5)/len(min_dists):.1f}%\n")
    f.write(f"  Time < 3 Å: {100*np.sum(min_dists < 3)/len(min_dists):.1f}%\n\n")
    
    f.write("Contacts:\n")
    f.write(f"  Unique residues: {len(sorted_contacts)}\n")
    f.write(f"  Persistent (>50%): {len([c for c in sorted_contacts if c[1] > 0.5])}\n\n")
    
    f.write("Top 10 Contact Residues:\n")
    for i, (res, pers) in enumerate(sorted_contacts[:10], 1):
        f.write(f"  {i:2d}. {res:8s}: {pers*100:5.1f}%\n")
    f.write("\n")
    
    # Binding status
    if min_dists.mean() < 3.0:
        status = "✅ EXCELLENT BINDING"
    elif min_dists.mean() < 5.0:
        status = "✅ STABLE BINDING"
    else:
        status = "⚠ WEAK BINDING"
    
    f.write("="*80 + "\n")
    f.write(f"BINDING STATUS: {status}\n")
    f.write("="*80 + "\n\n")
    
    f.write("Output Files:\n")
    f.write("  data/rmsd_backbone.dat\n")
    f.write("  data/rmsd_ligand.dat\n")
    f.write("  data/rmsf_calpha.dat\n")
    f.write("  data/distances.dat\n")
    f.write("  data/contact_persistence.dat\n")
    f.write("  figures/rmsd_panel.png\n")
    f.write("  figures/rmsf_contacts.png\n")
    f.write("  figures/timeline.png\n")

print(f"  ✓ Saved: ANALYSIS_REPORT.txt")

print("\n" + "="*80)
print("ANALYSIS COMPLETE!")
print("="*80)
print(f"\nOutput directory: {OUTPUT_DIR}")
print(f"  Data: {DATA_DIR}")
print(f"  Figures: {FIGURES_DIR}")
print(f"\nKey Results:")
print(f"  Backbone RMSD: {bb_data[:, 2].mean():.2f} ± {bb_data[:, 2].std():.2f} Å")
print(f"  Ligand RMSD: {lig_data[:, 2].mean():.2f} ± {lig_data[:, 2].std():.2f} Å")
print(f"  Min distance: {min_dists.mean():.2f} ± {min_dists.std():.2f} Å")
print(f"  Persistent contacts: {len([c for c in sorted_contacts if c[1] > 0.5])}")
print(f"  Status: {status}")
print("\n" + "="*80 + "\n")
