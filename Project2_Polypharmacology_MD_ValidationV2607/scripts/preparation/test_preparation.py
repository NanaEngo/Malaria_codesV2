#!/usr/bin/env python
"""
Script de test pour valider la préparation des structures
Vérifie que tous les fichiers nécessaires sont présents et valides
"""

import sys
from pathlib import Path

# Configuration
TARGETS = ["7F3Y", "6UKJ", "4GM2", "9N10"]
OUTPUT_BASE = Path("prepared_structures")

def test_file_exists(filepath):
    """Teste si un fichier existe"""
    if filepath.exists():
        size_kb = filepath.stat().st_size / 1024
        return True, size_kb
    return False, 0

def test_pdb_content(filepath):
    """Vérifie le contenu d'un fichier PDB"""
    if not filepath.exists():
        return False, "Fichier n'existe pas"
    
    try:
        atom_count = 0
        has_nucleic_atoms = False
        residues = set()
        
        with open(filepath, 'r') as f:
            for line in f:
                if line.startswith('ATOM'):
                    atom_count += 1
                    resname = line[17:20].strip()
                    residues.add(resname)
                    
                    # Vérifier atomes nucléiques
                    atomname = line[12:16].strip()
                    if atomname in ["O3'", "O5'", "P", "OP1", "OP2"]:
                        has_nucleic_atoms = True
        
        if atom_count == 0:
            return False, "Aucun atome ATOM trouvé"
        
        if has_nucleic_atoms:
            return False, "Contient des atomes nucléiques (O3', O5', etc.)"
        
        # Vérifier que tous les résidus sont standards
        STANDARD = {'ALA', 'ARG', 'ASN', 'ASP', 'CYS', 'GLN', 'GLU', 'GLY', 
                   'HIS', 'ILE', 'LEU', 'LYS', 'MET', 'PHE', 'PRO', 'SER', 
                   'THR', 'TRP', 'TYR', 'VAL', 'HIE', 'HID', 'HIP'}
        
        non_standard = residues - STANDARD
        if non_standard:
            return False, f"Résidus non-standards: {non_standard}"
        
        return True, f"{atom_count} atomes, {len(residues)} types de résidus"
        
    except Exception as e:
        return False, f"Erreur lecture: {e}"

def main():
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 20 + "TEST DE VALIDATION" + " " * 28 + "║")
    print("║" + " " * 17 + "Structures préparées MD" + " " * 26 + "║")
    print("╚" + "═" * 68 + "╝")
    print()
    
    if not OUTPUT_BASE.exists():
        print(f"✗ ERREUR: Dossier {OUTPUT_BASE} n'existe pas")
        print("Exécutez d'abord: python prepare_all_targets.py")
        return 1
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    
    for pdb_id in TARGETS:
        print("=" * 70)
        print(f"TEST: {pdb_id}")
        print("=" * 70)
        
        target_dir = OUTPUT_BASE / pdb_id
        
        # Test 1: Dossier existe
        total_tests += 1
        if target_dir.exists():
            print(f"✓ Dossier existe: {target_dir}")
            passed_tests += 1
        else:
            print(f"✗ Dossier manquant: {target_dir}")
            failed_tests += 1
            print()
            continue
        
        # Test 2-5: Fichiers requis
        files_to_check = [
            (f"{pdb_id}_raw.pdb", "Structure originale"),
            (f"{pdb_id}_chainA_fixed.pdb", "Structure avec H"),
            (f"{pdb_id}_chainA_clean.pdb", "Structure nettoyée"),
            (f"{pdb_id}_chainA_noH.pdb", "Structure pour GROMACS"),
        ]
        
        for filename, description in files_to_check:
            total_tests += 1
            filepath = target_dir / filename
            exists, size_or_msg = test_file_exists(filepath)
            
            if exists:
                print(f"✓ {description}: {filename} ({size_or_msg:.1f} KB)")
                passed_tests += 1
            else:
                print(f"✗ {description} manquant: {filename}")
                failed_tests += 1
        
        # Test 6: Contenu du fichier noH (le plus important)
        total_tests += 1
        noH_file = target_dir / f"{pdb_id}_chainA_noH.pdb"
        is_valid, msg = test_pdb_content(noH_file)
        
        if is_valid:
            print(f"✓ Contenu valide: {msg}")
            passed_tests += 1
        else:
            print(f"✗ Problème contenu: {msg}")
            failed_tests += 1
        
        print()
    
    # Résumé final
    print("=" * 70)
    print("RÉSUMÉ DES TESTS")
    print("=" * 70)
    print(f"Total:   {total_tests}")
    print(f"Réussis: {passed_tests} ✓")
    print(f"Échoués: {failed_tests} ✗")
    
    if failed_tests == 0:
        print("\n🎉 SUCCÈS: Toutes les structures sont valides!")
        print("\nProchaines étapes:")
        print("1. Upload vers serveur: scp -r prepared_structures/ user@server:/path/")
        print("2. Génération topologies: python step2b_topology_generation.py")
        return 0
    else:
        print("\n⚠ ATTENTION: Certains tests ont échoué")
        print("Vérifiez les messages ci-dessus et relancez la préparation si nécessaire")
        return 1

if __name__ == "__main__":
    sys.exit(main())
