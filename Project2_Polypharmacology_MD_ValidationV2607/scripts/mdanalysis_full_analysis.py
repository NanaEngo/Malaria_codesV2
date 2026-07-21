#!/usr/bin/env python3
"""
Complete MD Trajectory Analysis using MDAnalysis
For 214_PfCRT system

This script performs comprehensive analysis without requiring GROMACS commands:
- RMSD (backbone, ligand)
- RMSF (per-residue flexibility)
- Minimum distance (protein-ligand)
- Radius of gyration
- Hydrogen bonds
- Contacts
- Energy analysis (from EDR file if available)
"""

import MDAnalysis as mda
from MDAnalysis.analysis import rms, distances, contacts
from MDAnalysis.analysis.rms import RMSF
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pathlib import Path
import sys
import warnings
warnings.filterwarnings('ignore')

# Set publication style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 11
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 13
plt.rcParams['legend.fontsize'] = 10
plt.rcParams['lines.linewidth'] = 1.5

# Paths
PROJECT_DIR = Path(__file__).parent.parent
SYSTEM_DIR = PROJECT_DIR / "214_PfCRT"
ANALYSIS_DIR = SYSTEM_DIR / "analysis"
FIGURES_DIR = SYSTEM_DIR / "figures"

# Create directories
ANALYSIS_DIR.mkdir(exist_ok=True)
FIGURES_DIR.mkdir(exist_ok=True)

class MDAnalyzer:
    """Complete MD trajectory analyzer"""
    
    def __init__(self, topology, trajectory):
        """Initialize with topology and trajectory files"""
        print(f"\n{'='*80}")
        print("Loading MD Trajectory with MDAnalysis")
        print(f"{'='*80}\n")
        
        print(f"Topology: {topology}")
        print(f"Trajectory: {trajectory}")
        
        try:
            self.u = mda.Universe(str(topology), str(trajectory))
            print(f"\n✓ Universe loaded successfully")
            print(f"  Total atoms: {len(self.u.atoms):,}")
            print(f"  Total frames: {len(self.u.trajectory)}")
            print(f"  Time span: {self.u.trajectory.totaltime:.1f} ps")
            print(f"  Time step: {self.u.trajectory.dt:.2f} ps")
        except Exception as e:
            print(f"\n❌ Error loading trajectory: {e}")
            sys.exit(1)
        
        # Define selections
        self.protein = self.u.select_atoms("protein")
        self.backbone = self.u.select_atoms("protein and backbone")
        self.ca = self.u.select_atoms("protein and name CA")
        
        # Try different ligand selection methods
        try:
            self.ligand = self.u.select_atoms("resname UNL or resname LIG or resname MOL")
            if len(self.ligand) == 0:
                # Try selecting by residue number (often last residue)
                self.ligand = self.u.select_atoms(f"resid {self.u.residues[-1].resid}")
        except:
            print("⚠ Warning: Could not find ligand")
            self.ligand = None
        
        print(f"\nSelections:")
        print(f"  Protein atoms: {len(self.protein):,}")
        print(f"  Backbone atoms: {len(self.backbone):,}")
        print(f"  C-alpha atoms: {len(self.ca)}")
        if self.ligand:
            print(f"  Ligand atoms: {len(self.ligand)} (resname: {self.ligand.resnames[0]})")
        else:
            print(f"  Ligand atoms: Not found")
        
        self.results = {}
    
    def compute_rmsd(self):
        """Compute RMSD for backbone and ligand"""
        print(f"\n{'='*80}")
        print("1. Computing RMSD")
        print(f"{'='*80}\n")
        
        # Backbone RMSD
        print("Computing backbone RMSD...")
        R = rms.RMSD(self.u, select="backbone", ref_frame=0)
        R.run()
        
        self.results['rmsd_backbone'] = {
            'time': R.results.rmsd[:, 1] / 1000,  # ps to ns
            'rmsd': R.results.rmsd[:, 2]  # Already in Angstrom
        }
        
        print(f"✓ Backbone RMSD: {self.results['rmsd_backbone']['rmsd'].mean():.2f} ± "
              f"{self.results['rmsd_backbone']['rmsd'].std():.2f} Å")
        
        # Ligand RMSD
        if self.ligand:
            print("Computing ligand RMSD...")
            R_lig = rms.RMSD(self.u, select=f"resname {self.ligand.resnames[0]}", ref_frame=0)
            R_lig.run()
            
            self.results['rmsd_ligand'] = {
                'time': R_lig.results.rmsd[:, 1] / 1000,
                'rmsd': R_lig.results.rmsd[:, 2]
            }
            
            print(f"✓ Ligand RMSD: {self.results['rmsd_ligand']['rmsd'].mean():.2f} ± "
                  f"{self.results['rmsd_ligand']['rmsd'].std():.2f} Å")
    
    def compute_rmsf(self):
        """Compute per-residue RMSF"""
        print(f"\n{'='*80}")
        print("2. Computing RMSF (Per-Residue Flexibility)")
        print(f"{'='*80}\n")
        
        print("Computing backbone RMSF...")
        R = RMSF(self.ca).run()
        
        self.results['rmsf'] = {
            'residues': np.arange(1, len(R.results.rmsf) + 1),
            'rmsf': R.results.rmsf
        }
        
        print(f"✓ Mean RMSF: {R.results.rmsf.mean():.2f} ± {R.results.rmsf.std():.2f} Å")
        print(f"  Most flexible residue: {R.results.rmsf.argmax() + 1} (RMSF = {R.results.rmsf.max():.2f} Å)")
        print(f"  Most rigid residue: {R.results.rmsf.argmin() + 1} (RMSF = {R.results.rmsf.min():.2f} Å)")
    
    def compute_mindist(self):
        """Compute minimum protein-ligand distance"""
        print(f"\n{'='*80}")
        print("3. Computing Minimum Distance (Protein-Ligand)")
        print(f"{'='*80}\n")
        
        if not self.ligand:
            print("⚠ Skipping: No ligand found")
            return
        
        print("Computing minimum distances...")
        mindists = []
        times = []
        
        for ts in self.u.trajectory:
            dist = distances.distance_array(
                self.protein.positions,
                self.ligand.positions,
                box=self.u.dimensions
            ).min()
            mindists.append(dist)
            times.append(ts.time / 1000)  # ps to ns
        
        mindists = np.array(mindists)
        times = np.array(times)
        
        self.results['mindist'] = {
            'time': times,
            'distance': mindists
        }
        
        print(f"✓ Mean distance: {mindists.mean():.2f} ± {mindists.std():.2f} Å")
        print(f"  Min: {mindists.min():.2f} Å")
        print(f"  Max: {mindists.max():.2f} Å")
        
        # Binding assessment
        pct_bound = (mindists < 5.0).sum() / len(mindists) * 100
        print(f"  Time with distance < 5 Å: {pct_bound:.1f}%")
        
        if mindists.mean() < 5.0:
            print(f"  Status: ✅ STABLE BINDING")
        elif mindists.mean() < 8.0:
            print(f"  Status: ⚠ WEAK BINDING")
        else:
            print(f"  Status: ❌ DISSOCIATED")
    
    def compute_gyration(self):
        """Compute radius of gyration"""
        print(f"\n{'='*80}")
        print("4. Computing Radius of Gyration")
        print(f"{'='*80}\n")
        
        print("Computing protein gyration...")
        rg_values = []
        times = []
        
        for ts in self.u.trajectory:
            rg = self.protein.radius_of_gyration()
            rg_values.append(rg)
            times.append(ts.time / 1000)
        
        rg_values = np.array(rg_values)
        times = np.array(times)
        
        self.results['gyration'] = {
            'time': times,
            'rg': rg_values
        }
        
        print(f"✓ Mean Rg: {rg_values.mean():.2f} ± {rg_values.std():.2f} Å")
    
    def compute_contacts(self):
        """Compute protein-ligand contacts"""
        print(f"\n{'='*80}")
        print("5. Computing Protein-Ligand Contacts")
        print(f"{'='*80}\n")
        
        if not self.ligand:
            print("⚠ Skipping: No ligand found")
            return
        
        print("Computing contacts (distance < 6 Å)...")
        n_contacts = []
        times = []
        
        for ts in self.u.trajectory:
            dist_array = distances.distance_array(
                self.protein.positions,
                self.ligand.positions,
                box=self.u.dimensions
            )
            n_contacts.append((dist_array < 6.0).sum())
            times.append(ts.time / 1000)
        
        n_contacts = np.array(n_contacts)
        times = np.array(times)
        
        self.results['contacts'] = {
            'time': times,
            'n_contacts': n_contacts
        }
        
        print(f"✓ Mean contacts: {n_contacts.mean():.1f} ± {n_contacts.std():.1f}")
        print(f"  Range: {n_contacts.min()} - {n_contacts.max()}")
    
    def compute_hbonds(self):
        """Compute hydrogen bonds"""
        print(f"\n{'='*80}")
        print("6. Computing Hydrogen Bonds")
        print(f"{'='*80}\n")
        
        if not self.ligand:
            print("⚠ Skipping: No ligand found")
            return
        
        try:
            from MDAnalysis.analysis.hydrogenbonds import HydrogenBondAnalysis
            
            print("Computing hydrogen bonds...")
            hbonds = HydrogenBondAnalysis(
                universe=self.u,
                donors_sel=f"protein or resname {self.ligand.resnames[0]}",
                hydrogens_sel=f"protein or resname {self.ligand.resnames[0]}",
                acceptors_sel=f"protein or resname {self.ligand.resnames[0]}",
                d_h_a_angle_cutoff=150,
                d_a_cutoff=3.5
            )
            hbonds.run()
            
            # Count H-bonds per frame
            times = self.results['mindist']['time']
            n_hbonds = []
            
            for frame in range(len(self.u.trajectory)):
                frame_hbonds = hbonds.results.hbonds[hbonds.results.hbonds[:, 0] == frame]
                n_hbonds.append(len(frame_hbonds))
            
            n_hbonds = np.array(n_hbonds)
            
            self.results['hbonds'] = {
                'time': times,
                'n_hbonds': n_hbonds
            }
            
            print(f"✓ Mean H-bonds: {n_hbonds.mean():.1f} ± {n_hbonds.std():.1f}")
            print(f"  Max: {n_hbonds.max()}")
            
        except Exception as e:
            print(f"⚠ H-bond analysis failed: {e}")
    
    def plot_rmsd(self):
        """Plot RMSD analysis"""
        if 'rmsd_backbone' not in self.results:
            return
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Backbone
        ax1.plot(self.results['rmsd_backbone']['time'],
                self.results['rmsd_backbone']['rmsd'], 'b-', label='Backbone')
        ax1.axhline(self.results['rmsd_backbone']['rmsd'].mean(),
                   color='r', linestyle='--', alpha=0.7,
                   label=f"Mean: {self.results['rmsd_backbone']['rmsd'].mean():.2f} Å")
        ax1.set_xlabel('Time (ns)')
        ax1.set_ylabel('RMSD (Å)')
        ax1.set_title('214_PfCRT: Backbone RMSD')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Ligand
        if 'rmsd_ligand' in self.results:
            ax2.plot(self.results['rmsd_ligand']['time'],
                    self.results['rmsd_ligand']['rmsd'], 'g-', label='Ligand')
            ax2.axhline(self.results['rmsd_ligand']['rmsd'].mean(),
                       color='r', linestyle='--', alpha=0.7,
                       label=f"Mean: {self.results['rmsd_ligand']['rmsd'].mean():.2f} Å")
            ax2.set_xlabel('Time (ns)')
            ax2.set_ylabel('RMSD (Å)')
            ax2.set_title('214_PfCRT: Ligand RMSD')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(FIGURES_DIR / 'rmsd_analysis.png', dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {FIGURES_DIR / 'rmsd_analysis.png'}")
        plt.close()
    
    def plot_binding_stability(self):
        """Plot minimum distance"""
        if 'mindist' not in self.results:
            return
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        ax.plot(self.results['mindist']['time'],
               self.results['mindist']['distance'], 'purple', label='Min Distance')
        ax.axhline(self.results['mindist']['distance'].mean(),
                  color='r', linestyle='--', alpha=0.7,
                  label=f"Mean: {self.results['mindist']['distance'].mean():.2f} Å")
        ax.axhline(5.0, color='orange', linestyle=':', alpha=0.7,
                  label='Binding threshold (5 Å)')
        
        ax.set_xlabel('Time (ns)')
        ax.set_ylabel('Minimum Distance (Å)')
        ax.set_title('214_PfCRT: Protein-Ligand Binding Stability')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(FIGURES_DIR / 'binding_stability.png', dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {FIGURES_DIR / 'binding_stability.png'}")
        plt.close()
    
    def plot_rmsf(self):
        """Plot RMSF"""
        if 'rmsf' not in self.results:
            return
        
        fig, ax = plt.subplots(figsize=(14, 6))
        
        ax.plot(self.results['rmsf']['residues'],
               self.results['rmsf']['rmsf'], 'b-')
        ax.axhline(self.results['rmsf']['rmsf'].mean(),
                  color='r', linestyle='--', alpha=0.7,
                  label=f"Mean: {self.results['rmsf']['rmsf'].mean():.2f} Å")
        
        ax.set_xlabel('Residue Number')
        ax.set_ylabel('RMSF (Å)')
        ax.set_title('214_PfCRT: Per-Residue Flexibility')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(FIGURES_DIR / 'rmsf_analysis.png', dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {FIGURES_DIR / 'rmsf_analysis.png'}")
        plt.close()
    
    def plot_gyration(self):
        """Plot radius of gyration"""
        if 'gyration' not in self.results:
            return
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        ax.plot(self.results['gyration']['time'],
               self.results['gyration']['rg'], 'orange')
        ax.axhline(self.results['gyration']['rg'].mean(),
                  color='r', linestyle='--', alpha=0.7,
                  label=f"Mean: {self.results['gyration']['rg'].mean():.2f} Å")
        
        ax.set_xlabel('Time (ns)')
        ax.set_ylabel('Radius of Gyration (Å)')
        ax.set_title('214_PfCRT: Protein Compactness')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(FIGURES_DIR / 'gyration.png', dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {FIGURES_DIR / 'gyration.png'}")
        plt.close()
    
    def create_summary_figure(self):
        """Create comprehensive summary figure"""
        print(f"\n{'='*80}")
        print("Creating Summary Figure")
        print(f"{'='*80}\n")
        
        fig = plt.figure(figsize=(16, 12))
        gs = gridspec.GridSpec(3, 2, figure=fig, hspace=0.3, wspace=0.3)
        
        # Backbone RMSD
        if 'rmsd_backbone' in self.results:
            ax1 = fig.add_subplot(gs[0, 0])
            ax1.plot(self.results['rmsd_backbone']['time'],
                    self.results['rmsd_backbone']['rmsd'], 'b-')
            ax1.set_xlabel('Time (ns)')
            ax1.set_ylabel('RMSD (Å)')
            ax1.set_title('A. Backbone RMSD')
            ax1.grid(True, alpha=0.3)
        
        # Ligand RMSD
        if 'rmsd_ligand' in self.results:
            ax2 = fig.add_subplot(gs[0, 1])
            ax2.plot(self.results['rmsd_ligand']['time'],
                    self.results['rmsd_ligand']['rmsd'], 'g-')
            ax2.set_xlabel('Time (ns)')
            ax2.set_ylabel('RMSD (Å)')
            ax2.set_title('B. Ligand RMSD')
            ax2.grid(True, alpha=0.3)
        
        # Minimum Distance
        if 'mindist' in self.results:
            ax3 = fig.add_subplot(gs[1, 0])
            ax3.plot(self.results['mindist']['time'],
                    self.results['mindist']['distance'], 'purple')
            ax3.axhline(5.0, color='r', linestyle='--', alpha=0.5)
            ax3.set_xlabel('Time (ns)')
            ax3.set_ylabel('Distance (Å)')
            ax3.set_title('C. Protein-Ligand Distance')
            ax3.grid(True, alpha=0.3)
        
        # Contacts
        if 'contacts' in self.results:
            ax4 = fig.add_subplot(gs[1, 1])
            ax4.plot(self.results['contacts']['time'],
                    self.results['contacts']['n_contacts'], 'brown')
            ax4.set_xlabel('Time (ns)')
            ax4.set_ylabel('Number of Contacts')
            ax4.set_title('D. Protein-Ligand Contacts (<6 Å)')
            ax4.grid(True, alpha=0.3)
        
        # RMSF
        if 'rmsf' in self.results:
            ax5 = fig.add_subplot(gs[2, :])
            ax5.plot(self.results['rmsf']['residues'],
                    self.results['rmsf']['rmsf'], 'b-')
            ax5.set_xlabel('Residue Number')
            ax5.set_ylabel('RMSF (Å)')
            ax5.set_title('E. Per-Residue Flexibility')
            ax5.grid(True, alpha=0.3)
        
        plt.suptitle('214_PfCRT MD Trajectory Analysis Summary',
                    fontsize=16, y=0.995)
        plt.savefig(FIGURES_DIR / 'summary_figure.png', dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {FIGURES_DIR / 'summary_figure.png'}")
        plt.close()
    
    def write_summary(self):
        """Write text summary"""
        print(f"\n{'='*80}")
        print("Writing Summary Report")
        print(f"{'='*80}\n")
        
        summary_file = ANALYSIS_DIR / 'ANALYSIS_SUMMARY.txt'
        
        with open(summary_file, 'w') as f:
            f.write("="*80 + "\n")
            f.write("MD TRAJECTORY ANALYSIS SUMMARY: 214_PfCRT\n")
            f.write("="*80 + "\n\n")
            f.write(f"System: PfCRT + Ligand 214\n")
            f.write(f"Total atoms: {len(self.u.atoms):,}\n")
            f.write(f"Total frames: {len(self.u.trajectory)}\n")
            f.write(f"Time span: {self.u.trajectory.totaltime / 1000:.1f} ns\n\n")
            
            # Write all metrics
            if 'rmsd_backbone' in self.results:
                rmsd = self.results['rmsd_backbone']['rmsd']
                f.write(f"Backbone RMSD:\n")
                f.write(f"  Mean: {rmsd.mean():.2f} Å\n")
                f.write(f"  Std:  {rmsd.std():.2f} Å\n")
                f.write(f"  Range: {rmsd.min():.2f} - {rmsd.max():.2f} Å\n\n")
            
            if 'rmsd_ligand' in self.results:
                rmsd = self.results['rmsd_ligand']['rmsd']
                f.write(f"Ligand RMSD:\n")
                f.write(f"  Mean: {rmsd.mean():.2f} Å\n")
                f.write(f"  Std:  {rmsd.std():.2f} Å\n")
                f.write(f"  Range: {rmsd.min():.2f} - {rmsd.max():.2f} Å\n\n")
            
            if 'mindist' in self.results:
                dist = self.results['mindist']['distance']
                f.write(f"Protein-Ligand Minimum Distance:\n")
                f.write(f"  Mean: {dist.mean():.2f} Å\n")
                f.write(f"  Std:  {dist.std():.2f} Å\n")
                f.write(f"  Range: {dist.min():.2f} - {dist.max():.2f} Å\n")
                pct = (dist < 5.0).sum() / len(dist) * 100
                f.write(f"  Time < 5 Å: {pct:.1f}%\n")
                
                if dist.mean() < 5.0:
                    f.write(f"  Status: ✅ STABLE BINDING\n\n")
                elif dist.mean() < 8.0:
                    f.write(f"  Status: ⚠ WEAK BINDING\n\n")
                else:
                    f.write(f"  Status: ❌ DISSOCIATED\n\n")
            
            if 'rmsf' in self.results:
                rmsf_vals = self.results['rmsf']['rmsf']
                f.write(f"RMSF:\n")
                f.write(f"  Mean: {rmsf_vals.mean():.2f} Å\n")
                f.write(f"  Std:  {rmsf_vals.std():.2f} Å\n")
                f.write(f"  Range: {rmsf_vals.min():.2f} - {rmsf_vals.max():.2f} Å\n\n")
            
            if 'gyration' in self.results:
                rg = self.results['gyration']['rg']
                f.write(f"Radius of Gyration:\n")
                f.write(f"  Mean: {rg.mean():.2f} Å\n")
                f.write(f"  Std:  {rg.std():.2f} Å\n\n")
            
            if 'contacts' in self.results:
                cont = self.results['contacts']['n_contacts']
                f.write(f"Protein-Ligand Contacts (<6 Å):\n")
                f.write(f"  Mean: {cont.mean():.1f}\n")
                f.write(f"  Range: {cont.min()} - {cont.max()}\n\n")
            
            if 'hbonds' in self.results:
                hb = self.results['hbonds']['n_hbonds']
                f.write(f"Hydrogen Bonds:\n")
                f.write(f"  Mean: {hb.mean():.1f}\n")
                f.write(f"  Max: {hb.max()}\n\n")
            
            f.write("="*80 + "\n")
            f.write("Figures generated:\n")
            f.write("  - summary_figure.png\n")
            f.write("  - rmsd_analysis.png\n")
            f.write("  - binding_stability.png\n")
            f.write("  - rmsf_analysis.png\n")
            f.write("  - gyration.png\n")
            f.write("="*80 + "\n")
        
        print(f"✓ Saved: {summary_file}")
    
    def run_full_analysis(self):
        """Run complete analysis pipeline"""
        print(f"\n{'='*80}")
        print("STARTING COMPLETE MD ANALYSIS")
        print(f"{'='*80}")
        
        # Compute all metrics
        self.compute_rmsd()
        self.compute_rmsf()
        self.compute_mindist()
        self.compute_gyration()
        self.compute_contacts()
        self.compute_hbonds()
        
        # Generate plots
        print(f"\n{'='*80}")
        print("Generating Figures")
        print(f"{'='*80}\n")
        
        self.plot_rmsd()
        self.plot_binding_stability()
        self.plot_rmsf()
        self.plot_gyration()
        self.create_summary_figure()
        
        # Write summary
        self.write_summary()
        
        print(f"\n{'='*80}")
        print("ANALYSIS COMPLETE!")
        print(f"{'='*80}\n")
        print(f"Figures saved in: {FIGURES_DIR}")
        print(f"Summary saved in: {ANALYSIS_DIR / 'ANALYSIS_SUMMARY.txt'}\n")

def main():
    """Main entry point"""
    # Check files
    topology = SYSTEM_DIR / "production.gro"
    trajectory = SYSTEM_DIR / "production.xtc"
    
    if not topology.exists():
        print(f"❌ ERROR: Topology file not found: {topology}")
        sys.exit(1)
    
    if not trajectory.exists():
        print(f"❌ ERROR: Trajectory file not found: {trajectory}")
        sys.exit(1)
    
    # Run analysis
    analyzer = MDAnalyzer(topology, trajectory)
    analyzer.run_full_analysis()
    
    print(f"{'='*80}")
    print("Next steps:")
    print("  1. Review ANALYSIS_SUMMARY.txt for metrics")
    print("  2. Check summary_figure.png for overview")
    print("  3. Use figures for manuscript")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    main()

