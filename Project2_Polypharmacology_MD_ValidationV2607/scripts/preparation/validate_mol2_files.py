#!/usr/bin/env python3
"""
Validate MOL2 files generated from ligand PDB files

Checks:
- File format validity
- Atom and bond counts
- Partial charges present
- SYBYL atom types
- Reasonable molecular properties

Usage:
    python validate_mol2_files.py
"""

import sys
from pathlib import Path

# ──────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────────────────────────────────────────

MOL2_DIR = "ligand_prep"

# ──────────────────────────────────────────────────────────────────────────────
# FUNCTIONS
# ──────────────────────────────────────────────────────────────────────────────

def validate_mol2(mol2_file):
    """
    Valider un fichier MOL2
    
    Returns:
        (is_valid, issues, info)
    """
    issues = []
    info = {
        'atoms': 0,
        'bonds': 0,
        'has_charges': False,
        'has_atom_types': False,
        'total_charge': 0.0,
        'sections': []
    }
    
    try:
        with open(mol2_file, 'r') as f:
            content = f.read()
        
        if not content.strip():
            issues.append("Fichier vide")
            return False, issues, info
        
        # Parser sections
        lines = content.split('\n')
        current_section = None
        atom_data = []
        bond_data = []
        
        for line in lines:
            line = line.strip()
            
            # Détecter sections
            if line.startswith('@<TRIPOS>'):
                current_section = line[9:]
                info['sections'].append(current_section)
                continue
            
            if not line:
                continue
            
            # Parser atomes
            if current_section == 'ATOM':
                parts = line.split()
                if len(parts) >= 9:
                    info['atoms'] += 1
                    atom_type = parts[5]  # SYBYL atom type
                    charge = float(parts[8])
                    
                    atom_data.append({
                        'id': int(parts[0]),
                        'name': parts[1],
                        'type': atom_type,
                        'charge': charge
                    })
                    
                    info['total_charge'] += charge
            
            # Parser liaisons
            elif current_section == 'BOND':
                parts = line.split()
                if len(parts) >= 4:
                    info['bonds'] += 1
                    bond_data.append({
                        'id': int(parts[0]),
                        'atom1': int(parts[1]),
                        'atom2': int(parts[2]),
                        'type': parts[3]
                    })
        
        # Vérifications
        
        # 1. Sections requises
        required_sections = ['MOLECULE', 'ATOM', 'BOND']
        for section in required_sections:
            if section not in info['sections']:
                issues.append(f"Section manquante: {section}")
        
        # 2. Nombre d'atomes
        if info['atoms'] == 0:
            issues.append("Aucun atome trouvé")
        
        # 3. Nombre de liaisons
        if info['bonds'] == 0:
            issues.append("Aucune liaison trouvée")
        elif info['bonds'] < info['atoms'] - 1:
            issues.append(f"Trop peu de liaisons ({info['bonds']} pour {info['atoms']} atomes)")
        
        # 4. Charges partielles
        if atom_data:
            info['has_charges'] = True
            # Vérifier que les charges ne sont pas toutes nulles
            non_zero_charges = sum(1 for a in atom_data if abs(a['charge']) > 0.001)
            if non_zero_charges == 0:
                issues.append("Toutes les charges sont nulles")
        else:
            issues.append("Pas de données de charges")
        
        # 5. Types d'atomes SYBYL
        if atom_data:
            info['has_atom_types'] = True
            # Vérifier types valides
            valid_types = set()
            for a in atom_data:
                if '.' in a['type'] or a['type'] in ['C', 'N', 'O', 'S', 'P', 'H']:
                    valid_types.add(a['type'])
            
            if len(valid_types) == 0:
                issues.append("Types d'atomes SYBYL invalides")
        else:
            issues.append("Pas de types d'atomes")
        
        # 6. Charge totale raisonnable
        total_charge = round(info['total_charge'])
        if abs(total_charge) > 3:
            issues.append(f"Charge totale inhabituelle: {total_charge:+d}")
        
        # 7. Consistance liaisons
        if bond_data:
            # Vérifier que les IDs d'atomes existent
            atom_ids = set(a['id'] for a in atom_data)
            for bond in bond_data:
                if bond['atom1'] not in atom_ids:
                    issues.append(f"Liaison réfère atome inexistant: {bond['atom1']}")
                    break
                if bond['atom2'] not in atom_ids:
                    issues.append(f"Liaison réfère atome inexistant: {bond['atom2']}")
                    break
        
        is_valid = len(issues) == 0
        return is_valid, issues, info
        
    except Exception as e:
        issues.append(f"Erreur lecture: {e}")
        return False, issues, info

# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────

def main():
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 20 + "VALIDATION MOL2 FILES" + " " * 27 + "║")
    print("╚" + "═" * 68 + "╝")
    print()
    
    # Vérifier dossier
    mol2_path = Path(MOL2_DIR)
    if not mol2_path.exists():
        print(f"✗ Dossier non trouvé: {MOL2_DIR}")
        return 1
    
    # Trouver fichiers MOL2
    mol2_files = sorted(mol2_path.glob("*.mol2"))
    if not mol2_files:
        print(f"✗ Aucun fichier MOL2 trouvé dans: {MOL2_DIR}")
        print("Exécutez d'abord: python convert_pdb_to_mol2.py")
        return 1
    
    print(f"Trouvé {len(mol2_files)} fichier(s) MOL2")
    print()
    
    # Statistiques
    valid_count = 0
    invalid_count = 0
    
    # Valider chaque fichier
    for mol2_file in mol2_files:
        is_valid, issues, info = validate_mol2(mol2_file)
        
        print(f"{mol2_file.name}")
        
        if is_valid:
            print("  ✓ Valide")
            print(f"    Atomes: {info['atoms']}, Liaisons: {info['bonds']}")
            print(f"    Charge totale: {info['total_charge']:+.2f}")
            valid_count += 1
        else:
            print("  ✗ Invalide")
            for issue in issues:
                print(f"    - {issue}")
            if info['atoms'] > 0:
                print(f"    Atomes: {info['atoms']}, Liaisons: {info['bonds']}")
            invalid_count += 1
        
        print()
    
    # Résumé
    print("=" * 70)
    total = len(mol2_files)
    
    if invalid_count == 0:
        print("✓ Tous les fichiers sont valides!")
    else:
        print(f"Validation: {valid_count}/{total} valides, {invalid_count}/{total} invalides")
    
    print()
    
    return 0 if invalid_count == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
