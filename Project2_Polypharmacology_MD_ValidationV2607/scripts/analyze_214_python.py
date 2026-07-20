#!/usr/bin/env python3
"""
Comprehensive MD Trajectory Analysis for 214_PfCRT
Analyzes GROMACS output files and generates publication-quality figures
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pathlib import Path
import sys

# Set publication style
plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 11
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 13
plt.rcParams['legend.fontsize'] = 10

# Paths
PROJECT_DIR = Path(__file__).parent.parent
SYSTEM_DIR = PROJECT_DIR / "214_PfCRT"
ANALYSIS_DIR = SYSTEM_DIR / "analysis"
FIGURES_DIR = SYSTEM_DIR / "figures"

# Create figures directory
FIGURES_DIR.mkdir(exist_ok=True)

def read_xvg(filename):
    """Read GROMACS .xvg file, return time and data arrays"""
    filepath = ANALYSIS_DIR / filename
    if not filepath.exists():
        print(f"⚠ Warning: {filename} not found")
        return None, None
    
    time_data = []
    values = []
    
    with open(filepath, 'r') as f:
        for line in f:
            if line.startswith(('#', '@')):
                continue
            parts = line.split()
            if len(parts) >= 2:
                time_data.append(float(parts[0]))
                # Handle multiple columns
                if len(parts) == 2:
                    values.append(float(parts[1]))
                else:
                    values.append([float(x) for x in parts[1:]])
    
    return np.array(time_data), np.array(values)

def compute_statistics(data, label="Metric"):
    """Compute and print statistics"""
    if data is None or len(data) == 0:
        return None
    
    stats = {
        'mean': np.mean(data),
        'std': np.std(data),
        'min': np.min(data),
        'max': np.max(data),
        'median': np.median(data),
    }
    
    print(f"\n{label}:")
    print(f"  Mean:   {stats['mean']:.2f}")
    print(f"  Std:    {stats['std']:.2f}")
    print(f"  Min:    {stats['min']:.2f}")
    print(f"  Max:    {stats['max']:.2f}")
    print(f"  Median: {stats['median']:.2f}")
    
    return stats

def plot_rmsd_analysis():
    """Plot RMSD for backbone and ligand"""
    print("\n" + "="*80)
    print("1. RMSD Analysis")
    print("="*80)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Backbone RMSD
    time, rmsd_bb = read_xvg("rmsd_backbone.xvg")
    if time is not None:
        rmsd_bb_ang = rmsd_bb * 10  # nm to Angstrom
        ax1.plot(time, rmsd_bb_ang, 'b-', linewidth=1.5, label='Backbone RMSD')
        ax1.axhline(y=rmsd_bb_ang.mean(), color='r', linestyle='--', 
                    label=f'Mean: {rmsd_bb_ang.mean():.2f} Å')
        ax1.set_xlabel('Time (ns)')
        ax1.set_ylabel('RMSD (Å)')
        ax1.set_title('214_PfCRT: Backbone RMSD')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        stats = compute_statistics(rmsd_bb_ang, "Backbone RMSD (Å)")
    
    # Ligand RMSD
    time, rmsd_lig = read_xvg("rmsd_ligand.xvg")
    if time is not None:
        rmsd_lig_ang = rmsd_lig * 10  # nm to Angstrom
        ax2.plot(time, rmsd_lig_ang, 'g-', linewidth=1.5, label='Ligand RMSD')
        ax2.axhline(y=rmsd_lig_ang.mean(), color='r', linestyle='--',
                    label=f'Mean: {rmsd_lig_ang.mean():.2f} Å')
        ax2.set_xlabel('Time (ns)')
        ax2.set_ylabel('RMSD (Å)')
        ax2.set_title('214_PfCRT: Ligand RMSD')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        stats = compute_statistics(rmsd_lig_ang, "Ligand RMSD (Å)")
    
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "rmsd_analysis.png", dpi=300, bbox_inches='tight')
    print(f"\n✓ Saved: {FIGURES_DIR / 'rmsd_analysis.png'}")
    plt.close()

def plot_binding_stability():
    """Plot minimum distance (binding stability)"""
    print("\n" + "="*80)
    print("2. Binding Stability Analysis")
    print("="*80)
    
    time, mindist = read_xvg("mindist.xvg")
    if time is None:
        print("⚠ No minimum distance data found")
        return
    
    mindist_ang = mindist * 10  # nm to Angstrom
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.plot(time, mindist_ang, 'purple', linewidth=1.5, label='Min Distance')
    ax.axhline(y=mindist_ang.mean(), color='r', linestyle='--',
               label=f'Mean: {mindist_ang.mean():.2f} Å')
    ax.axhline(y=5.0, color='orange', linestyle=':', alpha=0.7,
               label='Binding threshold (5 Å)')
    
    ax.set_xlabel('Time (ns)')
    ax.set_ylabel('Minimum Distance (Å)')
    ax.set_title('214_PfCRT: Protein-Ligand Minimum Distance')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "binding_stability.png", dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {FIGURES_DIR / 'binding_stability.png'}")
    plt.close()
    
    stats = compute_statistics(mindist_ang, "Minimum Distance (Å)")
    
    # Binding assessment
    if stats['mean'] < 5.0:
        status = "✅ STABLE BINDING"
        color = "green"
    elif stats['mean'] < 8.0:
        status = "⚠ WEAK BINDING"
        color = "orange"
    else:
        status = "❌ DISSOCIATED"
        color = "red"
    
    print(f"\nBinding Status: {status}")
    print(f"  Time < 5 Å: {np.sum(mindist_ang < 5.0) / len(mindist_ang) * 100:.1f}%")
    print(f"  Time < 8 Å: {np.sum(mindist_ang < 8.0) / len(mindist_ang) * 100:.1f}%")

def plot_rmsf():
    """Plot per-residue flexibility (RMSF)"""
    print("\n" + "="*80)
    print("3. Per-Residue Flexibility (RMSF)")
    print("="*80)
    
    time, rmsf = read_xvg("rmsf_backbone.xvg")
    if time is None:
        print("⚠ No RMSF data found")
        return
    
    rmsf_ang = rmsf * 10  # nm to Angstrom
    residues = np.arange(1, len(rmsf) + 1)
    
    fig, ax = plt.subplots(figsize=(14, 6))
    
    ax.plot(residues, rmsf_ang, 'b-', linewidth=1.0)
    ax.axhline(y=rmsf_ang.mean(), color='r', linestyle='--',
               label=f'Mean: {rmsf_ang.mean():.2f} Å')
    
    ax.set_xlabel('Residue Number')
    ax.set_ylabel('RMSF (Å)')
    ax.set_title('214_PfCRT: Per-Residue Flexibility')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "rmsf_analysis.png", dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {FIGURES_DIR / 'rmsf_analysis.png'}")
    plt.close()
    
    stats = compute_statistics(rmsf_ang, "RMSF (Å)")
    
    # Identify highly flexible regions (> mean + 2*std)
    threshold = stats['mean'] + 2 * stats['std']
    flexible_residues = residues[rmsf_ang > threshold]
    if len(flexible_residues) > 0:
        print(f"\nHighly flexible residues (RMSF > {threshold:.2f} Å):")
        print(f"  {flexible_residues[:20]}...")  # Print first 20

def plot_energy_analysis():
    """Plot energy components"""
    print("\n" + "="*80)
    print("4. Energy Analysis")
    print("="*80)
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    
    # Temperature
    time, temp = read_xvg("temperature.xvg")
    if time is not None:
        ax1.plot(time, temp, 'r-', linewidth=1.0)
        ax1.axhline(y=310.15, color='b', linestyle='--', label='Target: 310.15 K')
        ax1.set_xlabel('Time (ps)')
        ax1.set_ylabel('Temperature (K)')
        ax1.set_title('Temperature')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        compute_statistics(temp, "Temperature (K)")
    
    # Pressure
    time, press = read_xvg("pressure.xvg")
    if time is not None:
        ax2.plot(time, press, 'g-', linewidth=1.0, alpha=0.7)
        ax2.axhline(y=1.0, color='b', linestyle='--', label='Target: 1 bar')
        ax2.set_xlabel('Time (ps)')
        ax2.set_ylabel('Pressure (bar)')
        ax2.set_title('Pressure')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        compute_statistics(press, "Pressure (bar)")
    
    # Potential Energy
    time, pot = read_xvg("potential.xvg")
    if time is not None:
        ax3.plot(time, pot, 'b-', linewidth=1.0)
        ax3.set_xlabel('Time (ps)')
        ax3.set_ylabel('Potential Energy (kJ/mol)')
        ax3.set_title('Potential Energy')
        ax3.grid(True, alpha=0.3)
        compute_statistics(pot, "Potential Energy (kJ/mol)")
    
    # Density
    time, dens = read_xvg("density.xvg")
    if time is not None:
        ax4.plot(time, dens, 'purple', linewidth=1.0)
        ax4.axhline(y=1.0, color='b', linestyle='--', label='Expected: 1.0 g/cm³')
        ax4.set_xlabel('Time (ps)')
        ax4.set_ylabel('Density (g/cm³)')
        ax4.set_title('Density')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        compute_statistics(dens, "Density (g/cm³)")
    
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "energy_analysis.png", dpi=300, bbox_inches='tight')
    print(f"\n✓ Saved: {FIGURES_DIR / 'energy_analysis.png'}")
    plt.close()

def plot_gyration():
    """Plot radius of gyration"""
    print("\n" + "="*80)
    print("5. Radius of Gyration")
    print("="*80)
    
    time, rg = read_xvg("gyration.xvg")
    if time is None:
        print("⚠ No gyration data found")
        return
    
    rg_ang = rg * 10  # nm to Angstrom
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.plot(time, rg_ang, 'orange', linewidth=1.5)
    ax.axhline(y=rg_ang.mean(), color='r', linestyle='--',
               label=f'Mean: {rg_ang.mean():.2f} Å')
    
    ax.set_xlabel('Time (ns)')
    ax.set_ylabel('Radius of Gyration (Å)')
    ax.set_title('214_PfCRT: Protein Compactness')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "gyration.png", dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {FIGURES_DIR / 'gyration.png'}")
    plt.close()
    
    stats = compute_statistics(rg_ang, "Radius of Gyration (Å)")

def create_summary_figure():
    """Create comprehensive summary figure with all key metrics"""
    print("\n" + "="*80)
    print("6. Creating Summary Figure")
    print("="*80)
    
    fig = plt.figure(figsize=(16, 12))
    gs = gridspec.GridSpec(3, 2, figure=fig, hspace=0.3, wspace=0.3)
    
    # 1. Backbone RMSD
    ax1 = fig.add_subplot(gs[0, 0])
    time, rmsd_bb = read_xvg("rmsd_backbone.xvg")
    if time is not None:
        rmsd_bb_ang = rmsd_bb * 10
        ax1.plot(time, rmsd_bb_ang, 'b-', linewidth=1.5)
        ax1.set_xlabel('Time (ns)')
        ax1.set_ylabel('RMSD (Å)')
        ax1.set_title('A. Backbone RMSD')
        ax1.grid(True, alpha=0.3)
    
    # 2. Ligand RMSD
    ax2 = fig.add_subplot(gs[0, 1])
    time, rmsd_lig = read_xvg("rmsd_ligand.xvg")
    if time is not None:
        rmsd_lig_ang = rmsd_lig * 10
        ax2.plot(time, rmsd_lig_ang, 'g-', linewidth=1.5)
        ax2.set_xlabel('Time (ns)')
        ax2.set_ylabel('RMSD (Å)')
        ax2.set_title('B. Ligand RMSD')
        ax2.grid(True, alpha=0.3)
    
    # 3. Minimum Distance
    ax3 = fig.add_subplot(gs[1, 0])
    time, mindist = read_xvg("mindist.xvg")
    if time is not None:
        mindist_ang = mindist * 10
        ax3.plot(time, mindist_ang, 'purple', linewidth=1.5)
        ax3.axhline(y=5.0, color='r', linestyle='--', alpha=0.5, label='5 Å threshold')
        ax3.set_xlabel('Time (ns)')
        ax3.set_ylabel('Distance (Å)')
        ax3.set_title('C. Protein-Ligand Distance')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
    
    # 4. Temperature
    ax4 = fig.add_subplot(gs[1, 1])
    time, temp = read_xvg("temperature.xvg")
    if time is not None:
        ax4.plot(time, temp, 'r-', linewidth=1.0, alpha=0.7)
        ax4.axhline(y=310.15, color='b', linestyle='--', alpha=0.5, label='Target')
        ax4.set_xlabel('Time (ps)')
        ax4.set_ylabel('Temperature (K)')
        ax4.set_title('D. Temperature')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
    
    # 5. RMSF
    ax5 = fig.add_subplot(gs[2, :])
    time, rmsf = read_xvg("rmsf_backbone.xvg")
    if time is not None:
        rmsf_ang = rmsf * 10
        residues = np.arange(1, len(rmsf) + 1)
        ax5.plot(residues, rmsf_ang, 'b-', linewidth=1.0)
        ax5.set_xlabel('Residue Number')
        ax5.set_ylabel('RMSF (Å)')
        ax5.set_title('E. Per-Residue Flexibility (RMSF)')
        ax5.grid(True, alpha=0.3)
    
    plt.suptitle('214_PfCRT MD Trajectory Analysis Summary', fontsize=16, y=0.995)
    plt.savefig(FIGURES_DIR / "summary_figure.png", dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {FIGURES_DIR / 'summary_figure.png'}")
    plt.close()

def write_summary_report():
    """Write comprehensive text summary"""
    print("\n" + "="*80)
    print("7. Writing Summary Report")
    print("="*80)
    
    report_file = ANALYSIS_DIR / "ANALYSIS_SUMMARY.txt"
    
    with open(report_file, 'w') as f:
        f.write("="*80 + "\n")
        f.write("MD TRAJECTORY ANALYSIS SUMMARY: 214_PfCRT\n")
        f.write("="*80 + "\n\n")
        f.write(f"System: PfCRT + Ligand 214\n")
        f.write(f"Trajectory: production.xtc\n")
        f.write(f"Analysis directory: {ANALYSIS_DIR}\n")
        f.write(f"Figures directory: {FIGURES_DIR}\n\n")
        
        # Analyze each metric
        metrics = [
            ("Backbone RMSD", "rmsd_backbone.xvg", 10, "Å"),
            ("Ligand RMSD", "rmsd_ligand.xvg", 10, "Å"),
            ("Min Distance", "mindist.xvg", 10, "Å"),
            ("Gyration", "gyration.xvg", 10, "Å"),
            ("Temperature", "temperature.xvg", 1, "K"),
            ("Density", "density.xvg", 1, "g/cm³"),
        ]
        
        for name, file, scale, unit in metrics:
            time, data = read_xvg(file)
            if data is not None:
                data_scaled = data * scale
                f.write(f"{name}:\n")
                f.write(f"  Mean:   {np.mean(data_scaled):.2f} {unit}\n")
                f.write(f"  Std:    {np.std(data_scaled):.2f} {unit}\n")
                f.write(f"  Min:    {np.min(data_scaled):.2f} {unit}\n")
                f.write(f"  Max:    {np.max(data_scaled):.2f} {unit}\n")
                f.write(f"  Median: {np.median(data_scaled):.2f} {unit}\n\n")
        
        # Binding assessment
        time, mindist = read_xvg("mindist.xvg")
        if mindist is not None:
            mindist_ang = mindist * 10
            mean_dist = np.mean(mindist_ang)
            f.write("Binding Assessment:\n")
            if mean_dist < 5.0:
                f.write("  Status: ✅ STABLE BINDING\n")
            elif mean_dist < 8.0:
                f.write("  Status: ⚠ WEAK BINDING\n")
            else:
                f.write("  Status: ❌ DISSOCIATED\n")
            f.write(f"  Time < 5 Å: {np.sum(mindist_ang < 5.0) / len(mindist_ang) * 100:.1f}%\n")
            f.write(f"  Time < 8 Å: {np.sum(mindist_ang < 8.0) / len(mindist_ang) * 100:.1f}%\n\n")
        
        f.write("="*80 + "\n")
        f.write("Generated Figures:\n")
        f.write("  - summary_figure.png      : Comprehensive overview\n")
        f.write("  - rmsd_analysis.png       : RMSD plots\n")
        f.write("  - binding_stability.png   : Protein-ligand distance\n")
        f.write("  - rmsf_analysis.png       : Per-residue flexibility\n")
        f.write("  - energy_analysis.png     : Energy components\n")
        f.write("  - gyration.png            : Protein compactness\n")
        f.write("="*80 + "\n")
    
    print(f"✓ Saved: {report_file}")

def main():
    """Main analysis pipeline"""
    print("\n" + "="*80)
    print("MD TRAJECTORY ANALYSIS: 214_PfCRT")
    print("="*80)
    print(f"\nWorking directory: {SYSTEM_DIR}")
    print(f"Analysis directory: {ANALYSIS_DIR}")
    print(f"Figures directory: {FIGURES_DIR}")
    
    # Check if analysis files exist
    if not ANALYSIS_DIR.exists():
        print(f"\n❌ ERROR: Analysis directory not found: {ANALYSIS_DIR}")
        print("Please run GROMACS analysis first (bash scripts/analyze_214_trajectory.sh)")
        sys.exit(1)
    
    # Run analysis
    plot_rmsd_analysis()
    plot_binding_stability()
    plot_rmsf()
    plot_energy_analysis()
    plot_gyration()
    create_summary_figure()
    write_summary_report()
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE!")
    print("="*80)
    print(f"\nAll figures saved in: {FIGURES_DIR}")
    print(f"Summary report: {ANALYSIS_DIR / 'ANALYSIS_SUMMARY.txt'}")
    print("\nNext steps:")
    print("  1. Review summary_figure.png for overview")
    print("  2. Read ANALYSIS_SUMMARY.txt for detailed metrics")
    print("  3. Use figures for manuscript")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()

