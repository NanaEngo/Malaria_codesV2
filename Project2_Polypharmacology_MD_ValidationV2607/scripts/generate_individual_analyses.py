#!/usr/bin/env python3
"""
Generate individual analysis files (01-05) for 214_PfCRT
Output: production_analysis/01_*.png, 01_*.txt, etc.
"""

import MDAnalysis as mda
from MDAnalysis.analysis import rms, align, distances
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 11

# Paths
PROJECT_DIR = Path(__file__).parent.parent
SYSTEM_DIR = PROJECT_DIR / "MD_systems" / "214_PfCRT"
OUTPUT_DIR = SYSTEM_DIR / "production_analysis"
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

print("="*80)
print("GENERATING INDIVIDUAL ANALYSIS FILES: 214_PfCRT")
print("="*80)
print(f"Output: {OUTPUT_DIR}\n")

# Load trajectory
topology = SYSTEM_DIR / "production.gro"
trajectory = SYSTEM_DIR / "production.xtc"

u = mda.Universe(str(topology), str(trajectory))
print(f"Loaded: {u.atoms.n_atoms} atoms, {u.trajectory.n_frames} frames\n")

protein = u.select_atoms("protein")
ligand_names = ['LIG', 'UNL', 'MOL', 'DRG']
ligand = None
for name in ligand_names:
    try:
        ligand = u.select_atoms(f"resname {name}")
        if ligand.n_atoms > 0:
            break
    except:
        pass
if ligand is None or ligand.n_atoms == 0:
    ligand = u.select_atoms("not protein and not resname WAT SOL TIP3 HOH NA CL K")

ligand_resname = ligand.resnames[0]
print(f"Protein: {protein.n_residues} residues")
print(f"Ligand: {ligand_resname} ({ligand.n_atoms} atoms)\n")


# ============================================================================
# 01 - BACKBONE RMSD
# ============================================================================
print("="*80)
print("01. Backbone RMSD")
print("="*80)

print("  Aligning trajectory...")
aligner = align.AlignTraj(u, u, select="backbone", in_memory=False)
aligner.run()

print("  Computing RMSD...")
rmsd_bb = rms.RMSD(u, select="backbone", ref_frame=0)
rmsd_bb.run()
bb_data = rmsd_bb.results.rmsd  # [frame, time(ps), rmsd(A)]

# Save data
time_ns = bb_data[:, 1] / 1000
rmsd_A = bb_data[:, 2]

with open(OUTPUT_DIR / "01_backbone_rmsd.txt", 'w') as f:
    f.write("# Backbone RMSD Analysis\n")
    f.write("# System: 214_PfCRT\n")
    f.write(f"# Frames: {len(bb_data)}\n")
    f.write(f"# Time range: 0 - {time_ns[-1]:.1f} ns\n")
    f.write("#\n")
    f.write(f"# Mean RMSD: {rmsd_A.mean():.3f} ± {rmsd_A.std():.3f} Å\n")
    f.write(f"# Min RMSD:  {rmsd_A.min():.3f} Å\n")
    f.write(f"# Max RMSD:  {rmsd_A.max():.3f} Å\n")
    f.write(f"# Median:    {np.median(rmsd_A):.3f} Å\n")
    f.write("#\n")
    f.write("# Time(ns) RMSD(A)\n")
    for t, r in zip(time_ns, rmsd_A):
        f.write(f"{t:.3f} {r:.3f}\n")

# Plot
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(time_ns, rmsd_A, 'b-', linewidth=1.5, alpha=0.8, label='Backbone RMSD')
ax.axhline(rmsd_A.mean(), color='r', linestyle='--', linewidth=2,
           label=f'Mean: {rmsd_A.mean():.2f} Å')
ax.fill_between(time_ns, 
                 rmsd_A.mean() - rmsd_A.std(),
                 rmsd_A.mean() + rmsd_A.std(),
                 alpha=0.2, color='red', label=f'±1σ: {rmsd_A.std():.2f} Å')
ax.set_xlabel('Time (ns)', fontweight='bold', fontsize=12)
ax.set_ylabel('RMSD (Å)', fontweight='bold', fontsize=12)
ax.set_title('214_PfCRT: Protein Backbone RMSD', fontweight='bold', fontsize=14)
ax.legend(loc='best', frameon=True, fontsize=11)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "01_backbone_rmsd.png", dpi=300, bbox_inches='tight')
plt.close()

print(f"  ✓ Saved: 01_backbone_rmsd.txt and .png")
print(f"    Mean: {rmsd_A.mean():.2f} ± {rmsd_A.std():.2f} Å\n")


# ============================================================================
# 02 - RMSF (Per-residue flexibility)
# ============================================================================
print("="*80)
print("02. RMSF (Per-residue Flexibility)")
print("="*80)

start_frame = len(u.trajectory) // 2
print(f"  Using equilibrated frames: {start_frame}-{len(u.trajectory)}")

calphas = u.select_atoms("protein and name CA")
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

# Save data
with open(OUTPUT_DIR / "02_rmsf.txt", 'w') as f:
    f.write("# Per-Residue Flexibility (RMSF)\n")
    f.write("# System: 214_PfCRT\n")
    f.write(f"# Residues: {len(resids)}\n")
    f.write(f"# Frames used: {len(u.trajectory) - start_frame} (equilibrated portion)\n")
    f.write("#\n")
    f.write(f"# Mean RMSF: {rmsf_values.mean():.3f} ± {rmsf_values.std():.3f} Å\n")
    f.write(f"# Min RMSF:  {rmsf_values.min():.3f} Å (residue {resids[np.argmin(rmsf_values)]})\n")
    f.write(f"# Max RMSF:  {rmsf_values.max():.3f} Å (residue {resids[np.argmax(rmsf_values)]})\n")
    f.write("#\n")
    f.write("# ResID RMSF(A)\n")
    for rid, rmsf in zip(resids, rmsf_values):
        f.write(f"{rid:4d} {rmsf:.3f}\n")

# Plot
fig, ax = plt.subplots(figsize=(14, 6))
ax.plot(resids, rmsf_values, 'b-', linewidth=1.5)
ax.axhline(rmsf_values.mean(), color='r', linestyle='--', linewidth=2,
           label=f'Mean: {rmsf_values.mean():.2f} Å')
threshold = rmsf_values.mean() + 2 * rmsf_values.std()
ax.axhline(threshold, color='orange', linestyle=':', linewidth=1.5,
           label=f'Mean + 2σ: {threshold:.2f} Å')
ax.fill_between(resids, 0, rmsf_values, alpha=0.3, color='blue')
ax.set_xlabel('Residue Number', fontweight='bold', fontsize=12)
ax.set_ylabel('RMSF (Å)', fontweight='bold', fontsize=12)
ax.set_title('214_PfCRT: Per-Residue Flexibility', fontweight='bold', fontsize=14)
ax.legend(loc='best', frameon=True, fontsize=11)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "02_rmsf.png", dpi=300, bbox_inches='tight')
plt.close()

print(f"  ✓ Saved: 02_rmsf.txt and .png")
print(f"    Mean: {rmsf_values.mean():.2f} Å, Max: {rmsf_values.max():.2f} Å\n")


# ============================================================================
# 03 - LIGAND RMSD
# ============================================================================
print("="*80)
print("03. Ligand RMSD")
print("="*80)

print("  Computing ligand RMSD...")
rmsd_lig = rms.RMSD(u, select=f"resname {ligand_resname}", ref_frame=0)
rmsd_lig.run()
lig_data = rmsd_lig.results.rmsd

time_ns_lig = lig_data[:, 1] / 1000
rmsd_lig_A = lig_data[:, 2]

# Save data
with open(OUTPUT_DIR / "03_ligand_rmsd.txt", 'w') as f:
    f.write("# Ligand RMSD Analysis\n")
    f.write("# System: 214_PfCRT\n")
    f.write(f"# Ligand: {ligand_resname}\n")
    f.write(f"# Frames: {len(lig_data)}\n")
    f.write(f"# Time range: 0 - {time_ns_lig[-1]:.1f} ns\n")
    f.write("#\n")
    f.write(f"# Mean RMSD: {rmsd_lig_A.mean():.3f} ± {rmsd_lig_A.std():.3f} Å\n")
    f.write(f"# Min RMSD:  {rmsd_lig_A.min():.3f} Å\n")
    f.write(f"# Max RMSD:  {rmsd_lig_A.max():.3f} Å\n")
    f.write(f"# Median:    {np.median(rmsd_lig_A):.3f} Å\n")
    f.write("#\n")
    f.write("# Time(ns) RMSD(A)\n")
    for t, r in zip(time_ns_lig, rmsd_lig_A):
        f.write(f"{t:.3f} {r:.3f}\n")

# Plot
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(time_ns_lig, rmsd_lig_A, 'g-', linewidth=1.5, alpha=0.8, label='Ligand RMSD')
ax.axhline(rmsd_lig_A.mean(), color='r', linestyle='--', linewidth=2,
           label=f'Mean: {rmsd_lig_A.mean():.2f} Å')
ax.axhline(2.0, color='orange', linestyle=':', linewidth=1.5,
           label='2 Å threshold', alpha=0.7)
ax.set_xlabel('Time (ns)', fontweight='bold', fontsize=12)
ax.set_ylabel('RMSD (Å)', fontweight='bold', fontsize=12)
ax.set_title(f'214_PfCRT: Ligand ({ligand_resname}) RMSD', fontweight='bold', fontsize=14)
ax.legend(loc='best', frameon=True, fontsize=11)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "03_ligand_rmsd.png", dpi=300, bbox_inches='tight')
plt.close()

print(f"  ✓ Saved: 03_ligand_rmsd.txt and .png")
print(f"    Mean: {rmsd_lig_A.mean():.2f} ± {rmsd_lig_A.std():.2f} Å\n")


# ============================================================================
# 04 - RADIUS OF GYRATION
# ============================================================================
print("="*80)
print("04. Radius of Gyration")
print("="*80)

print("  Computing radius of gyration...")
rg_values = []
times = []

for ts in u.trajectory:
    times.append(ts.time / 1000)  # Convert to ns
    rg = protein.radius_of_gyration()
    rg_values.append(rg)

rg_array = np.array(rg_values)
times_array = np.array(times)

# Save data
with open(OUTPUT_DIR / "04_radius_of_gyration.txt", 'w') as f:
    f.write("# Radius of Gyration\n")
    f.write("# System: 214_PfCRT\n")
    f.write(f"# Frames: {len(rg_array)}\n")
    f.write(f"# Time range: 0 - {times_array[-1]:.1f} ns\n")
    f.write("#\n")
    f.write(f"# Mean Rg: {rg_array.mean():.3f} ± {rg_array.std():.3f} Å\n")
    f.write(f"# Min Rg:  {rg_array.min():.3f} Å\n")
    f.write(f"# Max Rg:  {rg_array.max():.3f} Å\n")
    f.write(f"# Median:  {np.median(rg_array):.3f} Å\n")
    f.write("#\n")
    f.write("# Time(ns) Rg(A)\n")
    for t, rg in zip(times_array, rg_array):
        f.write(f"{t:.3f} {rg:.3f}\n")

# Plot
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(times_array, rg_array, 'orange', linewidth=1.5, alpha=0.8, label='Radius of Gyration')
ax.axhline(rg_array.mean(), color='r', linestyle='--', linewidth=2,
           label=f'Mean: {rg_array.mean():.2f} Å')
ax.fill_between(times_array,
                 rg_array.mean() - rg_array.std(),
                 rg_array.mean() + rg_array.std(),
                 alpha=0.2, color='red', label=f'±1σ: {rg_array.std():.2f} Å')
ax.set_xlabel('Time (ns)', fontweight='bold', fontsize=12)
ax.set_ylabel('Radius of Gyration (Å)', fontweight='bold', fontsize=12)
ax.set_title('214_PfCRT: Protein Compactness (Rg)', fontweight='bold', fontsize=14)
ax.legend(loc='best', frameon=True, fontsize=11)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "04_radius_of_gyration.png", dpi=300, bbox_inches='tight')
plt.close()

print(f"  ✓ Saved: 04_radius_of_gyration.txt and .png")
print(f"    Mean: {rg_array.mean():.2f} ± {rg_array.std():.2f} Å\n")


# ============================================================================
# 05 - PROTEIN-LIGAND CONTACTS
# ============================================================================
print("="*80)
print("05. Protein-Ligand Contacts")
print("="*80)

contact_cutoff = 4.5
print(f"  Contact cutoff: {contact_cutoff} Å")

protein_heavy = protein.select_atoms("not name H*")
ligand_heavy = ligand.select_atoms("not name H*")

# Contact analysis
contact_counts = {}
n_contacts_per_frame = []
min_dists = []
times_contact = []
total_frames = len(u.trajectory)

print(f"  Analyzing {total_frames} frames...")
for ts in u.trajectory:
    times_contact.append(ts.time / 1000)
    
    dist_array = distances.distance_array(
        protein_heavy.positions,
        ligand_heavy.positions
    )
    
    min_dists.append(dist_array.min())
    
    in_contact_idx = np.where(dist_array < contact_cutoff)[0]
    contact_atoms = protein_heavy[in_contact_idx]
    
    n_contacts_per_frame.append(len(contact_atoms))
    
    for atom in contact_atoms:
        key = f"{atom.resname}{atom.resid}"
        contact_counts[key] = contact_counts.get(key, 0) + 1

contact_persistence = {k: v/total_frames for k, v in contact_counts.items()}
sorted_contacts = sorted(contact_persistence.items(), key=lambda x: x[1], reverse=True)

min_dists = np.array(min_dists)
times_contact = np.array(times_contact)
n_contacts_per_frame = np.array(n_contacts_per_frame)

# Save data
with open(OUTPUT_DIR / "05_contacts.txt", 'w') as f:
    f.write("# Protein-Ligand Contact Analysis\n")
    f.write("# System: 214_PfCRT\n")
    f.write(f"# Contact cutoff: {contact_cutoff} Å\n")
    f.write(f"# Frames: {total_frames}\n")
    f.write("#\n")
    f.write(f"# Minimum Distance Statistics:\n")
    f.write(f"#   Mean: {min_dists.mean():.3f} ± {min_dists.std():.3f} Å\n")
    f.write(f"#   Min:  {min_dists.min():.3f} Å\n")
    f.write(f"#   Max:  {min_dists.max():.3f} Å\n")
    f.write(f"#   % time < 5 Å: {100*np.sum(min_dists < 5)/len(min_dists):.1f}%\n")
    f.write(f"#   % time < 3 Å: {100*np.sum(min_dists < 3)/len(min_dists):.1f}%\n")
    f.write("#\n")
    f.write(f"# Contact Statistics:\n")
    f.write(f"#   Mean contacts per frame: {n_contacts_per_frame.mean():.1f}\n")
    f.write(f"#   Unique contact residues: {len(sorted_contacts)}\n")
    f.write(f"#   Persistent contacts (>50%): {len([c for c in sorted_contacts if c[1] > 0.5])}\n")
    f.write("#\n")
    f.write("# Top Contact Residues (sorted by persistence):\n")
    f.write("# Residue  Persistence(%)  Frames\n")
    for res, pers in sorted_contacts:
        f.write(f"{res:8s}  {pers*100:6.2f}        {int(pers*total_frames):5d}\n")

# Plot
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

# Panel 1: Minimum distance over time
ax1.plot(times_contact, min_dists, 'purple', linewidth=1.5, alpha=0.8)
ax1.axhline(5.0, color='orange', linestyle=':', linewidth=2, label='5 Å binding threshold')
ax1.axhline(min_dists.mean(), color='r', linestyle='--', linewidth=2,
            label=f'Mean: {min_dists.mean():.2f} Å')
ax1.set_ylabel('Minimum Distance (Å)', fontweight='bold', fontsize=11)
ax1.set_title('A. Protein-Ligand Minimum Distance', fontweight='bold', fontsize=13, loc='left')
ax1.legend(loc='best', frameon=True)
ax1.grid(True, alpha=0.3)
ax1.set_xticklabels([])

# Panel 2: Contact persistence bar plot
ax2 = plt.subplot(2, 1, 2)
top20 = sorted_contacts[:20]
residues = [c[0] for c in top20]
persistence_pct = [c[1]*100 for c in top20]
colors = ['green' if p > 50 else 'orange' if p > 25 else 'gray' for p in persistence_pct]

y_pos = np.arange(len(residues))
ax2.barh(y_pos, persistence_pct, color=colors, alpha=0.7)
ax2.set_yticks(y_pos)
ax2.set_yticklabels(residues, fontsize=10)
ax2.set_xlabel('Persistence (%)', fontweight='bold', fontsize=11)
ax2.set_title('B. Top 20 Contact Residues', fontweight='bold', fontsize=13, loc='left')
ax2.axvline(50, color='red', linestyle='--', alpha=0.5, linewidth=1)
ax2.invert_yaxis()
ax2.grid(True, alpha=0.3, axis='x')

plt.suptitle('214_PfCRT: Protein-Ligand Contact Analysis', fontsize=15, fontweight='bold')
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "05_contacts.png", dpi=300, bbox_inches='tight')
plt.close()

print(f"  ✓ Saved: 05_contacts.txt and .png")
print(f"    Min dist: {min_dists.mean():.2f} Å, Unique contacts: {len(sorted_contacts)}\n")

print("="*80)
print("ALL INDIVIDUAL ANALYSES COMPLETE!")
print("="*80)
print(f"\nOutput directory: {OUTPUT_DIR}")
print("\nGenerated files:")
print("  01_backbone_rmsd.txt / .png")
print("  02_rmsf.txt / .png")
print("  03_ligand_rmsd.txt / .png")
print("  04_radius_of_gyration.txt / .png")
print("  05_contacts.txt / .png")
print("="*80 + "\n")
