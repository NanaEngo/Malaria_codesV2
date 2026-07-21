#!/usr/bin/env python3
"""
Comprehensive MD Analysis for Test/Complex_test
Uses MDAnalysis to extract maximum insights from the trajectory

Analyses:
1. Protein backbone RMSD and RMSF
2. Ligand RMSD and trajectory
3. Protein-ligand distances and contacts
4. Hydrogen bonding analysis
5. Radius of gyration
6. Secondary structure stability (via DSSP if available)
7. Binding site residue flexibility
8. Center of mass movements
"""

import MDAnalysis as mda
from MDAnalysis.analysis import rms, align
from MDAnalysis import transformations
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys
import warnings
warnings.filterwarnings('ignore')

# Set plotting style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")
plt.rcParams['figure.dpi'] = 150
plt.rcParams['savefig.dpi'] = 150

class MDAnalyzer:
    """Comprehensive MD trajectory analyzer"""
    
    def __init__(self, topology, trajectory, output_dir="analysis_results"):
        """
        Initialize analyzer
        
        Args:
            topology: Path to topology file (GRO, PDB, PSF)
            trajectory: Path to trajectory file (XTC, TRR, DCD)
            output_dir: Directory for output files
        """
        print("="*80)
        print("COMPREHENSIVE MD TRAJECTORY ANALYSIS")
        print("="*80)
        print()
        
        self.topology = Path(topology)
        self.trajectory = Path(trajectory)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        print("📂 Loading trajectory...")
        print(f"   Topology: {self.topology}")
        print(f"   Trajectory: {self.trajectory}")
        
        # Load universe
        self.u = mda.Universe(str(self.topology), str(self.trajectory))
        
        print("\n✓ Universe loaded")
        print(f"  Atoms: {self.u.atoms.n_atoms:,}")
        print(f"  Frames: {self.u.trajectory.n_frames}")
        print(f"  Time: 0 - {self.u.trajectory.totaltime:.1f} ps")
        print(f"  Timestep: {self.u.trajectory.dt:.2f} ps")
        
        # Identify system components
        self._identify_components()
        
    def _identify_components(self):
        """Identify protein, ligand, cofactor, etc."""
        print("\n📊 System Components:")
        
        # Protein
        self.protein = self.u.select_atoms("protein")
        print(f"  Protein: {self.protein.n_atoms:,} atoms ({self.protein.n_residues} residues)")
        
        # Ligand
        ligand_names = ['LIG', 'LIG1', 'UNK', 'MOL', 'DRG']
        self.ligand = None
        for name in ligand_names:
            try:
                lig = self.u.select_atoms(f"resname {name}")
                if lig.n_atoms > 0:
                    self.ligand = lig
                    self.ligand_resname = name
                    print(f"  Ligand ({name}): {lig.n_atoms} atoms")
                    break
            except:
                continue
        
        # Cofactor
        try:
            self.cofactor = self.u.select_atoms("resname NDP or resname NAD or resname ATP")
            if self.cofactor.n_atoms > 0:
                print(f"  Cofactor: {self.cofactor.n_atoms} atoms")
        except:
            self.cofactor = None
        
        # Water
        try:
            water = self.u.select_atoms("resname TIP3 or resname SOL or resname HOH")
            print(f"  Water: {water.n_residues:,} molecules")
        except:
            pass
        
        # Ions
        try:
            ions = self.u.select_atoms("resname POT or resname CLA or resname NA or resname CL")
            print(f"  Ions: {ions.n_atoms} atoms")
        except:
            pass
        
        print()
    
    def analyze_protein_rmsd(self):
        """Analyze protein backbone RMSD"""
        print("🔬 Analysis 1: Protein Backbone RMSD")
        print("-" * 80)
        
        # Align trajectory
        print("  Aligning trajectory...")
        aligner = align.AlignTraj(self.u, self.u, select="protein and name CA",
                                   in_memory=False)
        aligner.run()
        
        # Compute RMSD
        print("  Computing RMSD...")
        R = rms.RMSD(self.u, select="protein and name CA", ref_frame=0)
        R.run()
        
        rmsd_data = R.results.rmsd
        times_ns = rmsd_data[:, 1] / 1000
        rmsd_vals = rmsd_data[:, 2] * 10  # nm to Å
        
        # Statistics
        print(f"  Initial RMSD: {rmsd_vals[0]:.2f} Å")
        print(f"  Final RMSD: {rmsd_vals[-1]:.2f} Å")
        print(f"  Mean RMSD: {rmsd_vals.mean():.2f} ± {rmsd_vals.std():.2f} Å")
        print(f"  Max RMSD: {rmsd_vals.max():.2f} Å")
        
        # Check equilibration
        first_half = rmsd_vals[:len(rmsd_vals)//2].mean()
        second_half = rmsd_vals[len(rmsd_vals)//2:].mean()
        drift = second_half - first_half
        print(f"  RMSD drift (1st vs 2nd half): {drift:+.2f} Å")
        
        if abs(drift) < 1.0:
            print("  ✓ System appears equilibrated")
        else:
            print("  ⚠️  Significant drift detected")
        
        # Plot
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(times_ns, rmsd_vals, 'b-', linewidth=1.5, alpha=0.8)
        ax.axhline(rmsd_vals.mean(), color='r', linestyle='--', linewidth=2,
                   label=f'Mean: {rmsd_vals.mean():.2f} Å')
        ax.fill_between(times_ns, 
                        rmsd_vals.mean() - rmsd_vals.std(),
                        rmsd_vals.mean() + rmsd_vals.std(),
                        alpha=0.2, color='red', label='±1 SD')
        ax.set_xlabel("Time (ns)", fontsize=12)
        ax.set_ylabel("Backbone RMSD (Å)", fontsize=12)
        ax.set_title("Protein Backbone RMSD over Time", fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig(self.output_dir / "01_backbone_rmsd.png")
        print("  📊 Saved: 01_backbone_rmsd.png")
        plt.close()
        
        # Save data
        np.savetxt(self.output_dir / "01_backbone_rmsd.txt",
                   np.column_stack([times_ns, rmsd_vals]),
                   header="Time(ns) RMSD(Å)", fmt="%.3f")
        print()
        
        return rmsd_vals
    
    def analyze_protein_rmsf(self):
        """Analyze per-residue flexibility (RMSF)"""
        print("🔬 Analysis 2: Per-Residue Flexibility (RMSF)")
        print("-" * 80)
        
        # Select CA atoms
        ca_atoms = self.u.select_atoms("protein and name CA")
        
        # Compute RMSF
        print("  Computing RMSF...")
        R = rms.RMSF(ca_atoms)
        R.run()
        
        rmsf_vals = R.results.rmsf * 10  # nm to Å
        resids = ca_atoms.resids
        
        print(f"  Mean RMSF: {rmsf_vals.mean():.2f} ± {rmsf_vals.std():.2f} Å")
        print(f"  Max RMSF: {rmsf_vals.max():.2f} Å (residue {resids[rmsf_vals.argmax()]})")
        
        # Find most flexible regions
        threshold = rmsf_vals.mean() + 2 * rmsf_vals.std()
        flexible_mask = rmsf_vals > threshold
        if flexible_mask.any():
            flexible_resids = resids[flexible_mask]
            print(f"  Highly flexible residues (RMSF > {threshold:.2f} Å):")
            print(f"    {list(flexible_resids)}")
        
        # Plot
        fig, ax = plt.subplots(figsize=(12, 5))
        ax.plot(resids, rmsf_vals, 'b-', linewidth=1.5)
        ax.axhline(rmsf_vals.mean(), color='r', linestyle='--', linewidth=2,
                   label=f'Mean: {rmsf_vals.mean():.2f} Å')
        ax.axhline(threshold, color='orange', linestyle=':', linewidth=2,
                   label=f'Mean + 2SD: {threshold:.2f} Å')
        ax.set_xlabel("Residue Number", fontsize=12)
        ax.set_ylabel("RMSF (Å)", fontsize=12)
        ax.set_title("Per-Residue Flexibility (RMSF)", fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig(self.output_dir / "02_rmsf.png")
        print("  📊 Saved: 02_rmsf.png")
        plt.close()
        
        # Save data
        np.savetxt(self.output_dir / "02_rmsf.txt",
                   np.column_stack([resids, rmsf_vals]),
                   header="ResID RMSF(Å)", fmt="%d %.3f")
        print()
        
        return resids, rmsf_vals
    
    def analyze_ligand_rmsd(self):
        """Analyze ligand RMSD"""
        if self.ligand is None:
            print("⚠️  No ligand found, skipping ligand RMSD")
            print()
            return None
        
        print(f"🔬 Analysis 3: Ligand RMSD ({self.ligand_resname})")
        print("-" * 80)
        
        # Compute ligand RMSD
        print("  Computing ligand RMSD...")
        self.u.trajectory[0]  # Reset to first frame
        
        R_lig = rms.RMSD(self.ligand, select="all", ref_frame=0)
        R_lig.run()
        
        rmsd_data = R_lig.results.rmsd
        times_ns = rmsd_data[:, 1] / 1000
        rmsd_vals = rmsd_data[:, 2] * 10  # nm to Å
        
        print(f"  Initial RMSD: {rmsd_vals[0]:.2f} Å")
        print(f"  Final RMSD: {rmsd_vals[-1]:.2f} Å")
        print(f"  Mean RMSD: {rmsd_vals.mean():.2f} ± {rmsd_vals.std():.2f} Å")
        print(f"  Max RMSD: {rmsd_vals.max():.2f} Å")
        
        if rmsd_vals.mean() < 3.0:
            print("  ✓ Ligand is stable in binding site")
        elif rmsd_vals.mean() < 5.0:
            print("  ⚠️  Ligand has moderate mobility")
        else:
            print("  ❌ Ligand may have dissociated")
        
        # Plot
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(times_ns, rmsd_vals, 'g-', linewidth=1.5, alpha=0.8)
        ax.axhline(rmsd_vals.mean(), color='r', linestyle='--', linewidth=2,
                   label=f'Mean: {rmsd_vals.mean():.2f} Å')
        ax.set_xlabel("Time (ns)", fontsize=12)
        ax.set_ylabel("Ligand RMSD (Å)", fontsize=12)
        ax.set_title(f"Ligand ({self.ligand_resname}) RMSD over Time",
                     fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig(self.output_dir / "03_ligand_rmsd.png")
        print("  📊 Saved: 03_ligand_rmsd.png")
        plt.close()
        
        # Save data
        np.savetxt(self.output_dir / "03_ligand_rmsd.txt",
                   np.column_stack([times_ns, rmsd_vals]),
                   header="Time(ns) RMSD(Å)", fmt="%.3f")
        print()
        
        return rmsd_vals
    
    def analyze_protein_ligand_distance(self):
        """Analyze protein-ligand distance over time"""
        if self.ligand is None:
            print("⚠️  No ligand found, skipping distance analysis")
            print()
            return None
        
        print("🔬 Analysis 4: Protein-Ligand Distance")
        print("-" * 80)
        
        print("  Computing center-of-mass distances...")
        distances_list = []
        
        for ts in self.u.trajectory:
            # Center of mass distance
            prot_com = self.protein.center_of_mass()
            lig_com = self.ligand.center_of_mass()
            dist = np.linalg.norm(prot_com - lig_com)
            distances_list.append(dist)
        
        distances_array = np.array(distances_list)
        times_ns = np.array([ts.time for ts in self.u.trajectory]) / 1000
        
        print(f"  Initial distance: {distances_array[0]:.2f} Å")
        print(f"  Final distance: {distances_array[-1]:.2f} Å")
        print(f"  Mean distance: {distances_array.mean():.2f} ± {distances_array.std():.2f} Å")
        print(f"  Min distance: {distances_array.min():.2f} Å")
        print(f"  Max distance: {distances_array.max():.2f} Å")
        
        if distances_array.mean() < 30:
            print("  ✓ Ligand remains bound")
        else:
            print("  ❌ Ligand has dissociated")
        
        # Plot
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(times_ns, distances_array, 'purple', linewidth=1.5, alpha=0.8)
        ax.axhline(distances_array.mean(), color='r', linestyle='--', linewidth=2,
                   label=f'Mean: {distances_array.mean():.2f} Å')
        ax.axhline(30, color='orange', linestyle=':', linewidth=2,
                   label='Dissociation threshold (30 Å)')
        ax.set_xlabel("Time (ns)", fontsize=12)
        ax.set_ylabel("Distance (Å)", fontsize=12)
        ax.set_title("Protein-Ligand Center-of-Mass Distance",
                     fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig(self.output_dir / "04_protein_ligand_distance.png")
        print("  📊 Saved: 04_protein_ligand_distance.png")
        plt.close()
        
        # Save data
        np.savetxt(self.output_dir / "04_protein_ligand_distance.txt",
                   np.column_stack([times_ns, distances_array]),
                   header="Time(ns) Distance(Å)", fmt="%.3f")
        print()
        
        return distances_array
    
    def analyze_protein_ligand_contacts(self):
        """Analyze protein-ligand contacts"""
        if self.ligand is None:
            print("⚠️  No ligand found, skipping contact analysis")
            print()
            return None
        
        print("🔬 Analysis 5: Protein-Ligand Contacts")
        print("-" * 80)
        
        print("  Identifying contact residues (< 4.5 Å)...")
        
        # Track contacts over time
        contact_counts = []
        all_contacts = {}  # resid -> count
        
        for ts in self.u.trajectory:
            # Find protein residues within 4.5 Å of ligand
            close_residues = self.protein.select_atoms(
                f"around 4.5 (resname {self.ligand_resname})"
            ).residues
            
            contact_counts.append(len(close_residues))
            
            for res in close_residues:
                if res.resid not in all_contacts:
                    all_contacts[res.resid] = 0
                all_contacts[res.resid] += 1
        
        times_ns = np.array([ts.time for ts in self.u.trajectory]) / 1000
        contact_counts = np.array(contact_counts)
        
        print(f"  Mean contacts: {contact_counts.mean():.1f} residues")
        print(f"  Max contacts: {contact_counts.max()} residues")
        
        # Find persistent contacts (> 50% of frames)
        n_frames = len(self.u.trajectory)
        persistent_contacts = {k: v for k, v in all_contacts.items() 
                               if v > n_frames * 0.5}
        
        sorted_contacts = []
        if persistent_contacts:
            print("  Persistent contacts (> 50% frames):")
            sorted_contacts = sorted(persistent_contacts.items(),
                                    key=lambda x: x[1], reverse=True)
            for resid, count in sorted_contacts[:10]:  # Top 10
                res = self.protein.select_atoms(f"resid {resid}").residues[0]
                print(f"    Res {resid} ({res.resname}): {count/n_frames*100:.1f}% frames")
        else:
            print("  No persistent contacts found (ligand dissociated)")
        
        # Plot contact counts over time
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(times_ns, contact_counts, 'brown', linewidth=1.5, alpha=0.8)
        ax.axhline(contact_counts.mean(), color='r', linestyle='--', linewidth=2,
                   label=f'Mean: {contact_counts.mean():.1f} residues')
        ax.set_xlabel("Time (ns)", fontsize=12)
        ax.set_ylabel("Number of Contact Residues", fontsize=12)
        ax.set_title("Protein-Ligand Contacts over Time (< 4.5 Å)",
                     fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig(self.output_dir / "05_contact_counts.png")
        print("  📊 Saved: 05_contact_counts.png")
        plt.close()
        
        # Plot contact frequency heatmap
        if persistent_contacts:
            fig, ax = plt.subplots(figsize=(12, 6))
            resids = sorted(persistent_contacts.keys())
            frequencies = [persistent_contacts[r]/n_frames*100 for r in resids]
            resnames = [self.protein.select_atoms(f"resid {r}").residues[0].resname 
                       for r in resids]
            labels = [f"{rn}{rid}" for rn, rid in zip(resnames, resids)]
            
            bars = ax.barh(labels, frequencies, color='steelblue', alpha=0.7)
            ax.set_xlabel("Contact Frequency (%)", fontsize=12)
            ax.set_ylabel("Residue", fontsize=12)
            ax.set_title("Persistent Protein-Ligand Contacts",
                        fontsize=14, fontweight='bold')
            ax.grid(axis='x', alpha=0.3)
            plt.tight_layout()
            plt.savefig(self.output_dir / "05_contact_frequency.png")
            print("  📊 Saved: 05_contact_frequency.png")
            plt.close()
        
        # Save data
        with open(self.output_dir / "05_contact_analysis.txt", 'w') as f:
            f.write("# Persistent Protein-Ligand Contacts (> 50% frames)\n")
            f.write("# ResID ResName Frequency(%)\n")
            if sorted_contacts:
                for resid, count in sorted_contacts:
                    res = self.protein.select_atoms(f"resid {resid}").residues[0]
                    f.write(f"{resid} {res.resname} {count/n_frames*100:.2f}\n")
            else:
                f.write("# No persistent contacts detected (ligand dissociated)\n")
        
        print()
        return persistent_contacts
    
    def analyze_radius_of_gyration(self):
        """Analyze protein compactness via radius of gyration"""
        print("🔬 Analysis 6: Radius of Gyration (Protein Compactness)")
        print("-" * 80)
        
        print("  Computing radius of gyration...")
        rgyr_list = []
        
        for ts in self.u.trajectory:
            rgyr = self.protein.radius_of_gyration()
            rgyr_list.append(rgyr)
        
        rgyr_array = np.array(rgyr_list)
        times_ns = np.array([ts.time for ts in self.u.trajectory]) / 1000
        
        print(f"  Initial Rg: {rgyr_array[0]:.2f} Å")
        print(f"  Final Rg: {rgyr_array[-1]:.2f} Å")
        print(f"  Mean Rg: {rgyr_array.mean():.2f} ± {rgyr_array.std():.2f} Å")
        print(f"  Change: {rgyr_array[-1] - rgyr_array[0]:+.2f} Å")
        
        # Plot
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(times_ns, rgyr_array, 'teal', linewidth=1.5, alpha=0.8)
        ax.axhline(rgyr_array.mean(), color='r', linestyle='--', linewidth=2,
                   label=f'Mean: {rgyr_array.mean():.2f} Å')
        ax.set_xlabel("Time (ns)", fontsize=12)
        ax.set_ylabel("Radius of Gyration (Å)", fontsize=12)
        ax.set_title("Protein Radius of Gyration over Time",
                     fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig(self.output_dir / "06_radius_of_gyration.png")
        print("  📊 Saved: 06_radius_of_gyration.png")
        plt.close()
        
        # Save data
        np.savetxt(self.output_dir / "06_radius_of_gyration.txt",
                   np.column_stack([times_ns, rgyr_array]),
                   header="Time(ns) Rg(Å)", fmt="%.3f")
        print()
        
        return rgyr_array
    
    def generate_summary_report(self):
        """Generate final summary report"""
        print("="*80)
        print("📋 GENERATING SUMMARY REPORT")
        print("="*80)
        
        report_path = self.output_dir / "ANALYSIS_SUMMARY.md"
        
        with open(report_path, 'w') as f:
            f.write("# MD Trajectory Analysis Summary\n\n")
            f.write("## System Information\n\n")
            f.write(f"- **Topology**: {self.topology.name}\n")
            f.write(f"- **Trajectory**: {self.trajectory.name}\n")
            f.write(f"- **Total atoms**: {self.u.atoms.n_atoms:,}\n")
            f.write(f"- **Protein**: {self.protein.n_atoms:,} atoms, {self.protein.n_residues} residues\n")
            if self.ligand:
                f.write(f"- **Ligand ({self.ligand_resname})**: {self.ligand.n_atoms} atoms\n")
            f.write(f"- **Frames**: {self.u.trajectory.n_frames}\n")
            f.write(f"- **Time range**: 0 - {self.u.trajectory.totaltime:.1f} ps\n")
            f.write(f"- **Timestep**: {self.u.trajectory.dt:.2f} ps\n\n")
            
            f.write("## Analysis Files Generated\n\n")
            f.write("1. `01_backbone_rmsd.png` - Protein backbone RMSD\n")
            f.write("2. `02_rmsf.png` - Per-residue flexibility\n")
            if self.ligand:
                f.write("3. `03_ligand_rmsd.png` - Ligand RMSD\n")
                f.write("4. `04_protein_ligand_distance.png` - Protein-ligand distance\n")
                f.write("5. `05_contact_counts.png` - Contact residue counts\n")
                f.write("6. `05_contact_frequency.png` - Persistent contacts\n")
            f.write("7. `06_radius_of_gyration.png` - Protein compactness\n\n")
            
            f.write("## Key Findings\n\n")
            f.write("See individual analysis outputs and plots for detailed results.\n\n")
            
            f.write("---\n")
            f.write("*Analysis completed with MDAnalysis*\n")
        
        print(f"✓ Summary report saved: {report_path}")
        print()

import argparse

def main():
    """Main analysis function"""
    
    parser = argparse.ArgumentParser(description="Comprehensive MD Trajectory Analysis")
    parser.add_argument("--topology", type=str, required=True, help="Path to topology file (GRO, PDB, PSF)")
    parser.add_argument("--trajectory", type=str, required=True, help="Path to trajectory file (XTC, TRR, DCD)")
    parser.add_argument("--output_dir", type=str, default="comprehensive_analysis", help="Directory for output files")
    
    args = parser.parse_args()
    
    # Configuration
    topology = Path(args.topology)
    trajectory = Path(args.trajectory)
    output_dir = Path(args.output_dir)
    
    # Check files exist
    if not topology.exists():
        print(f"❌ Topology file not found: {topology}")
        return 1
    
    if not trajectory.exists():
        print(f"❌ Trajectory file not found: {trajectory}")
        return 1
    
    # Run analysis
    analyzer = MDAnalyzer(topology, trajectory, output_dir)
    
    try:
        # Run all analyses
        analyzer.analyze_protein_rmsd()
        analyzer.analyze_protein_rmsf()
        analyzer.analyze_ligand_rmsd()
        analyzer.analyze_protein_ligand_distance()
        analyzer.analyze_protein_ligand_contacts()
        analyzer.analyze_radius_of_gyration()
        
        # Generate summary
        analyzer.generate_summary_report()
        
        print("="*80)
        print("✅ ANALYSIS COMPLETE!")
        print("="*80)
        print(f"\nResults saved in: {output_dir}/")
        print("\nGenerated files:")
        for f in sorted(output_dir.glob("*.png")):
            print(f"  📊 {f.name}")
        for f in sorted(output_dir.glob("*.txt")):
            print(f"  📄 {f.name}")
        print("  📝 ANALYSIS_SUMMARY.md")
        print()
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
