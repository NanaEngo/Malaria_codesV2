#!/usr/bin/env python
"""
Validate generated ligand PDB files
Checks structure quality and 3D coordinates
"""

import sys
from pathlib import Path

try:
    from rdkit import Chem
    from rdkit.Chem import AllChem, Descriptors
except ImportError:
    print("ERROR: RDKit not found!")
    sys.exit(1)

LIGAND_DIR = Path("/home/vital/Documents/GitHub/Malaria_codes/Project2_Polypharmacology_MD_Validation/Tuto_MD_MC/ligand_prep")

def validate_pdb(pdb_file):
    """Valide un fichier PDB"""
    results = {
        'file_exists': False,
        'readable': False,
        'has_3d_coords': False,
        'num_atoms': 0,
        'num_heavy_atoms': 0,
        'mol_weight': 0.0,
        'issues': []
    }
    
    # Vérifier existence
    if not pdb_file.exists():
        results['issues'].append("Fichier n'existe pas")
        return results
    
    results['file_exists'] = True
    
    try:
        # Lire PDB
        mol = Chem.MolFromPDBFile(str(pdb_file), removeHs=False)
        
        if mol is None:
            results['issues'].append("PDB illisible par RDKit")
            return results
        
        results['readable'] = True
        
        # Statistiques
        results['num_atoms'] = mol.GetNumAtoms()
        results['num_heavy_atoms'] = mol.GetNumHeavyAtoms()
        results['mol_weight'] = Descriptors.MolWt(mol)
        
        # Vérifier coordonnées 3D
        conf = mol.GetConformer()
        if conf.Is3D():
            results['has_3d_coords'] = True
        else:
            results['issues'].append("Pas de coordonnées 3D")
        
        # Vérifier atomes
        if results['num_atoms'] == 0:
            results['issues'].append("Aucun atome")
        
        # Vérifier liaisons
        if mol.GetNumBonds() == 0:
            results['issues'].append("Aucune liaison")
        
    except Exception as e:
        results['issues'].append(f"Erreur: {e}")
    
    return results

def main():
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 20 + "VALIDATION LIGANDS PDB" + " " * 26 + "║")
    print("╚" + "═" * 68 + "╝")
    print()
    
    if not LIGAND_DIR.exists():
        print(f"✗ Dossier non trouvé: {LIGAND_DIR}")
        return 1
    
    # Trouver tous les PDB
    pdb_files = sorted(LIGAND_DIR.glob("*.pdb"))
    
    if not pdb_files:
        print(f"✗ Aucun fichier PDB dans: {LIGAND_DIR}")
        return 1
    
    print(f"Trouvé {len(pdb_files)} fichier(s) PDB\n")
    
    # Valider chaque fichier
    all_valid = True
    
    for pdb_file in pdb_files:
        print(f"{pdb_file.name}")
        results = validate_pdb(pdb_file)
        
        if results['file_exists'] and results['readable'] and results['has_3d_coords']:
            print("  ✓ Valide")
            print(f"    Atomes: {results['num_atoms']} ({results['num_heavy_atoms']} lourds)")
            print(f"    MW: {results['mol_weight']:.2f} Da")
        else:
            print("  ✗ Problème(s):")
            for issue in results['issues']:
                print(f"    - {issue}")
            all_valid = False
        
        print()
    
    # Résumé
    print("=" * 70)
    if all_valid:
        print("✓ Tous les fichiers sont valides!")
        return 0
    else:
        print("✗ Certains fichiers ont des problèmes")
        return 1

if __name__ == "__main__":
    sys.exit(main())
