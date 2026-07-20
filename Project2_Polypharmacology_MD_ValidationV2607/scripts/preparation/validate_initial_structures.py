#!/usr/bin/env python3
"""
Quick Validation of Initial Structures for Production Systems

Checks:
1. Protein-ligand COM distance
2. Number of ligand atoms within 4.5 Å of protein
3. Basic structural integrity

Run BEFORE starting production MD to avoid test system failure!
"""

import MDAnalysis as mda
import numpy as np
from pathlib import Path
import sys

class StructureValidator:
    """Validate initial complex structures"""
    
    def __init__(self, structure_file):
        """
        Args:
            structure_file: Path to complex.gro file
        """
        self.structure = Path(structure_file)
        self.system_name = self.structure.parent.name
        
        # Load structure
        try:
            self.u = mda.Universe(str(self.structure))
        except Exception as e:
            print(f"❌ ERROR loading {self.system_name}: {e}")
            self.u = None
            return
        
        # Identify components
        self.protein = self.u.select_atoms("protein")
        
        # Find ligand
        ligand_names = ['LIG', 'LIG1', 'UNK', 'MOL', 'DRG']
        self.ligand = None
        for name in ligand_names:
            try:
                lig = self.u.select_atoms(f"resname {name}")
                if lig.n_atoms > 0:
                    self.ligand = lig
                    break
            except:
                continue
    
    def validate(self):
        """
        Run all validation checks
        
        Returns:
            tuple: (pass/fail status, dict of metrics)
        """
        if self.u is None:
            return False, {"error": "Failed to load structure"}
        
        if self.ligand is None:
            return False, {"error": "No ligand found"}
        
        results = {}
        
        # 1. Center-of-mass distance
        prot_com = self.protein.center_of_mass()
        lig_com = self.ligand.center_of_mass()
        com_distance = np.linalg.norm(prot_com - lig_com)
        results['com_distance'] = com_distance
        
        # 2. Number of close contacts
        close_protein = self.protein.select_atoms(
            f"around 4.5 resname {self.ligand.resnames[0]}"
        )
        results['contact_residues'] = len(close_protein.residues)
        
        # 3. Closest atom distance
        from MDAnalysis.lib.distances import distance_array
        distances = distance_array(
            self.protein.positions,
            self.ligand.positions,
            box=None
        )
        results['min_distance'] = distances.min()
        
        # 4. Ligand in reasonable space
        box_size = self.u.dimensions[:3]
        lig_pos = lig_com
        results['ligand_position'] = lig_pos
        results['box_center'] = box_size / 2
        
        # Decision criteria
        status = "PASS"
        warnings = []
        
        if com_distance > 30:
            status = "FAIL"
            warnings.append(f"COM distance {com_distance:.1f} Å is too large (test system had 125 Å!)")
        elif com_distance > 15:
            status = "WARNING"
            warnings.append(f"COM distance {com_distance:.1f} Å is concerning (should be <15 Å)")
        
        if results['contact_residues'] == 0:
            status = "FAIL"
            warnings.append("Zero contact residues (ligand not in binding site)")
        elif results['contact_residues'] < 3:
            if status != "FAIL":
                status = "WARNING"
            warnings.append(f"Only {results['contact_residues']} contact residues (expect 5-15)")
        
        results['status'] = status
        results['warnings'] = warnings
        
        return status == "PASS", results
    
    def print_report(self, results):
        """Print formatted validation report"""
        status = results.get('status', 'UNKNOWN')
        
        # Status emoji
        if status == "PASS":
            emoji = "✅"
            color = "green"
        elif status == "WARNING":
            emoji = "⚠️"
            color = "yellow"
        else:
            emoji = "❌"
            color = "red"
        
        print(f"\n{emoji} {self.system_name}: {status}")
        print("-" * 60)
        
        if 'error' in results:
            print(f"  Error: {results['error']}")
            return
        
        # Metrics
        print(f"  Protein-ligand COM distance: {results['com_distance']:.2f} Å")
        print(f"  Contact residues (< 4.5 Å): {results['contact_residues']}")
        print(f"  Closest atom distance: {results['min_distance']:.2f} Å")
        
        # Reference ranges
        print("\n  Reference ranges:")
        print("    COM distance: <15 Å (optimal), <30 Å (acceptable)")
        print("    Contact residues: 5-15 (good), >3 (minimal)")
        print("    Min distance: 2-4 Å (typical)")
        
        # Warnings
        if results['warnings']:
            print("\n  Issues detected:")
            for warning in results['warnings']:
                print(f"    • {warning}")
        
        # Recommendation
        print("\n  Recommendation:")
        if status == "PASS":
            print("    ✓ Structure looks good - proceed with MD")
        elif status == "WARNING":
            print("    ⚠️  Visual inspection recommended before MD")
        else:
            print("    ❌ DO NOT RUN MD - fix ligand placement first!")
            print("    This system may fail like the test system (125 Å distance)")

def main():
    """Main validation function"""
    
    print("="*80)
    print("INITIAL STRUCTURE VALIDATION FOR PRODUCTION SYSTEMS")
    print("="*80)
    print("\nValidating ligand placement before MD simulations...")
    print("(Prevents test system failure: ligand 125 Å from protein)\n")
    
    # Find all production systems
    base_dir = Path("Gromacs_inputs")
    ligands = ["LIG1", "LIG2", "LIG5", "LIG7", "LIG8", "LIG9", 
               "LIG10", "LIG14", "LIG15", "LIG16", "LIG17"]
    
    results_summary = {}
    
    for lig in ligands:
        structure_file = base_dir / lig / f"Complex_{lig}" / "complex.gro"
        
        if not structure_file.exists():
            print(f"\n⚠️  {lig}: Structure file not found: {structure_file}")
            results_summary[lig] = "NOT FOUND"
            continue
        
        # Validate
        validator = StructureValidator(structure_file)
        passed, results = validator.validate()
        validator.print_report(results)
        
        results_summary[lig] = results.get('status', 'UNKNOWN')
    
    # Overall summary
    print("\n" + "="*80)
    print("VALIDATION SUMMARY")
    print("="*80)
    
    pass_count = sum(1 for s in results_summary.values() if s == "PASS")
    warn_count = sum(1 for s in results_summary.values() if s == "WARNING")
    fail_count = sum(1 for s in results_summary.values() if s == "FAIL")
    
    print(f"\nResults: {pass_count} PASS | {warn_count} WARNING | {fail_count} FAIL\n")
    
    for lig, status in results_summary.items():
        if status == "PASS":
            print(f"  ✅ {lig}: {status}")
        elif status == "WARNING":
            print(f"  ⚠️  {lig}: {status} - Check visually")
        else:
            print(f"  ❌ {lig}: {status} - DO NOT RUN")
    
    print("\n" + "="*80)
    
    if fail_count > 0:
        print(f"\n⚠️  {fail_count} system(s) FAILED validation")
        print("   DO NOT proceed with MD for failed systems!")
        print("   Fix ligand placement and re-validate.\n")
        return 1
    
    if warn_count > 0:
        print(f"\n⚠️  {warn_count} system(s) need visual inspection")
        print("   Review in VMD/PyMOL before running MD.\n")
    
    if pass_count == len(ligands):
        print(f"\n✅ All {pass_count} systems PASSED validation!")
        print("   Ready to proceed with production MD.\n")
        return 0
    
    return 0

if __name__ == "__main__":
    import warnings
    warnings.filterwarnings('ignore')
    
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n❌ Validation script failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
