#!/usr/bin/env python
"""
Convert SMILES from CSV to 3D PDB structures
Generates optimized 3D conformers for MD simulations

Input:  md_top20_candidates.csv (SMILES strings)
Output: ligand_prep/*.pdb (3D structures)

Dependencies:
    mamba install -c conda-forge rdkit openbabel
"""

import os
import sys
import pandas as pd
from pathlib import Path

try:
    from rdkit import Chem
    from rdkit.Chem import AllChem
    from rdkit.Chem import Descriptors
except ImportError:
    print("ERROR: RDKit not found!")
    print("Install with: mamba install -c conda-forge rdkit")
    sys.exit(1)

# ──────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────────────────────────────────────────

CSV_FILE = "/home/vital/Documents/GitHub/Malaria_codes/Project2_Polypharmacology_MD_Validation/Tuto_MD_MC/md_top20_candidates.csv"
OUTPUT_DIR = "/home/vital/Documents/GitHub/Malaria_codes/Project2_Polypharmacology_MD_Validation/Tuto_MD_MC/ligand_prep"

# Paramètres génération 3D
NUM_CONFORMERS = 10          # Nombre de conformères à générer
OPTIMIZE_CONFORMERS = True   # Optimiser avec MMFF94
ENERGY_MINIMIZE = True       # Minimisation d'énergie finale
MAX_ITERATIONS = 500         # Itérations minimisation

# ──────────────────────────────────────────────────────────────────────────────
# FONCTIONS
# ──────────────────────────────────────────────────────────────────────────────

def sanitize_filename(name):
    """Nettoie le nom de fichier"""
    # Remplacer caractères spéciaux
    name = name.replace('/', '_')
    name = name.replace('\\', '_')
    name = name.replace(' ', '_')
    return name

def smiles_to_3d_mol(smiles, name="molecule"):
    """
    Convertit un SMILES en molécule 3D optimisée
    Version robuste avec multiples stratégies de fallback
    
    Args:
        smiles: String SMILES
        name: Nom de la molécule
    
    Returns:
        RDKit Mol object with 3D coordinates, or None if failed
    """
    try:
        # 1. Nettoyer le SMILES
        smiles = smiles.strip()
        
        # 2. Créer molécule depuis SMILES
        mol = Chem.MolFromSmiles(smiles)
        
        if mol is None:
            print("  ✗ Erreur: SMILES invalide")
            return None
        
        # 3. Ajouter hydrogènes explicites
        mol = Chem.AddHs(mol)
        
        num_atoms = mol.GetNumAtoms()
        print(f"  ✓ Molécule chargée: {num_atoms} atomes")
        
        # 4. STRATÉGIE 1: ETKDGv3 (moderne, robuste)
        print("  Tentative 1: ETKDGv3...")
        params = AllChem.ETKDGv3()
        params.randomSeed = 42
        params.numThreads = 0  # Use all available cores
        params.useRandomCoords = True
        params.maxIterations = 0  # Pas de pré-optimisation
        
        conf_ids = AllChem.EmbedMultipleConfs(
            mol, 
            numConfs=NUM_CONFORMERS,
            params=params
        )
        
        if len(conf_ids) == 0:
            # STRATÉGIE 2: ETKDG standard (moins strict)
            print("  Tentative 2: ETKDG standard...")
            params = AllChem.ETKDG()
            params.randomSeed = 42
            params.useRandomCoords = True
            
            conf_ids = AllChem.EmbedMultipleConfs(
                mol,
                numConfs=NUM_CONFORMERS,
                params=params
            )
        
        if len(conf_ids) == 0:
            # STRATÉGIE 3: Méthode basique sans distance geometry
            print("  Tentative 3: Méthode basique...")
            if AllChem.EmbedMolecule(mol, randomSeed=42, useRandomCoords=True) == -1:
                # STRATÉGIE 4: Forcer coordonnées aléatoires
                print("  Tentative 4: Coordonnées aléatoires...")
                AllChem.EmbedMolecule(
                    mol, 
                    randomSeed=42, 
                    useRandomCoords=True,
                    maxAttempts=1000
                )
            
            conf_ids = [0] if mol.GetNumConformers() > 0 else []
        
        if len(conf_ids) == 0:
            print("  ✗ Erreur: Impossible de générer géométrie 3D après 4 tentatives")
            return None
        
        print(f"  ✓ {len(conf_ids)} conformère(s) généré(s)")
        
        # 5. Optimiser avec MMFF94 (avec fallback UFF)
        if OPTIMIZE_CONFORMERS and len(conf_ids) > 0:
            energies = []
            best_conf_id = 0
            best_energy = float('inf')
            ff_type = None
            
            # Essayer MMFF94 d'abord
            for conf_id in conf_ids:
                try:
                    props = AllChem.MMFFGetMoleculeProperties(mol)
                    if props is not None:
                        ff = AllChem.MMFFGetMoleculeForceField(mol, props, confId=conf_id)
                        if ff is not None:
                            ff.Minimize(maxIts=MAX_ITERATIONS)
                            energy = ff.CalcEnergy()
                            if energy < best_energy:
                                best_energy = energy
                                best_conf_id = conf_id
                                ff_type = 'MMFF'
                except:
                    pass
            
            # Si MMFF échoue, essayer UFF (Universal Force Field)
            if ff_type is None:
                print("  ⚠ MMFF94 échoué, essai UFF...")
                for conf_id in conf_ids:
                    try:
                        ff = AllChem.UFFGetMoleculeForceField(mol, confId=conf_id)
                        if ff is not None:
                            ff.Minimize(maxIts=MAX_ITERATIONS)
                            energy = ff.CalcEnergy()
                            if energy < best_energy:
                                best_energy = energy
                                best_conf_id = conf_id
                                ff_type = 'UFF'
                    except:
                        pass
            
            if ff_type is not None:
                # Garder seulement le meilleur conformère et s'assurer qu'il a l'ID 0
                best_conf = mol.GetConformer(best_conf_id)
                
                # Créer une nouvelle molécule sans conformères
                new_mol = Chem.Mol(mol)
                new_mol.RemoveAllConformers()
                
                # Ajouter le meilleur conformère avec ID 0 explicite
                new_conf = Chem.Conformer(best_conf)
                new_conf.SetId(0)
                new_mol.AddConformer(new_conf, assignId=True)
                mol = new_mol
                
                print(f"  ✓ Optimisé avec {ff_type} (E = {best_energy:.2f} kcal/mol, conf {best_conf_id}→0)")
            else:
                print("  ⚠ Optimisation échouée, structure non optimisée utilisée")
        
        # 6. Minimisation finale (plus douce)
        if ENERGY_MINIMIZE and mol.GetNumConformers() > 0:
            try:
                # Essayer MMFF d'abord
                result = AllChem.MMFFOptimizeMolecule(mol, maxIters=MAX_ITERATIONS)
                if result == 0:
                    print("  ✓ Minimisation finale MMFF effectuée")
                else:
                    # Fallback UFF
                    result = AllChem.UFFOptimizeMolecule(mol, maxIters=MAX_ITERATIONS)
                    if result == 0:
                        print("  ✓ Minimisation finale UFF effectuée")
            except:
                print("  ⚠ Minimisation finale échouée")
        
        # Vérifier qu'on a bien des coordonnées 3D
        if mol.GetNumConformers() == 0:
            print("  ✗ Erreur: Aucun conformère final")
            return None
        
        return mol
        
    except Exception as e:
        print(f"  ✗ Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()
        return None

def write_pdb(mol, output_file, name="LIG"):
    """
    Écrit molécule en format PDB
    
    Args:
        mol: RDKit Mol object
        output_file: Chemin fichier sortie
        name: Nom résidu (3 lettres)
    """
    try:
        # Vérifier qu'on a au moins un conformère
        if mol.GetNumConformers() == 0:
            print("  ✗ Erreur: Molécule sans conformère 3D")
            return False
        
        # Écrire PDB en spécifiant explicitement le conformère 0
        # (qui contient toujours le meilleur conformère après optimisation)
        Chem.MolToPDBFile(mol, str(output_file), confId=0)
        
        # Modifier le nom du résidu si nécessaire
        if name != "UNL":
            with open(output_file, 'r') as f:
                content = f.read()
            
            # Remplacer le nom de résidu par défaut (UNL) par le nom personnalisé
            content = content.replace(' UNL ', f' {name.ljust(3)} ')
            
            with open(output_file, 'w') as f:
                f.write(content)
        
        return True
        
    except Exception as e:
        print(f"  ✗ Erreur écriture PDB: {e}")
        import traceback
        traceback.print_exc()
        return False

def get_molecule_info(mol):
    """Retourne informations sur la molécule"""
    info = {
        'num_atoms': mol.GetNumAtoms(),
        'num_heavy_atoms': mol.GetNumHeavyAtoms(),
        'mol_weight': Descriptors.MolWt(mol),
        'num_rings': Descriptors.RingCount(mol),
        'num_rotatable_bonds': Descriptors.NumRotatableBonds(mol),
    }
    return info

# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────

def main():
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "CONVERSION SMILES → PDB 3D" + " " * 27 + "║")
    print("║" + " " * 20 + "Ligands pour MD" + " " * 32 + "║")
    print("╚" + "═" * 68 + "╝")
    print()
    
    # Vérifier CSV existe
    if not os.path.exists(CSV_FILE):
        print(f"✗ Erreur: Fichier CSV non trouvé: {CSV_FILE}")
        return 1
    
    # Créer dossier sortie
    output_path = Path(OUTPUT_DIR)
    output_path.mkdir(parents=True, exist_ok=True)
    print(f"✓ Dossier sortie: {OUTPUT_DIR}")
    print()
    
    # Lire CSV
    print("Lecture du CSV...")
    try:
        df = pd.read_csv(CSV_FILE)
        print(f"✓ {len(df)} candidats trouvés")
    except Exception as e:
        print(f"✗ Erreur lecture CSV: {e}")
        return 1
    
    # Vérifier colonne SMILES existe
    if 'smiles' not in df.columns:
        print("✗ Erreur: Colonne 'smiles' non trouvée dans le CSV")
        print(f"Colonnes disponibles: {list(df.columns)}")
        return 1
    
    print()
    print("=" * 70)
    print("CONVERSION DES MOLÉCULES")
    print("=" * 70)
    print()
    
    # Statistiques
    success_count = 0
    fail_count = 0
    failed_molecules = []
    
    # Convertir chaque SMILES
    for idx, row in df.iterrows():
        rank = row.get('rank', idx + 1)
        smiles = row['smiles']
        
        # Nom du fichier
        mol_name = f"ligand_{rank:02d}"
        output_file = output_path / f"{mol_name}.pdb"
        
        print(f"[{rank}/20] {mol_name}")
        print(f"  SMILES: {smiles[:60]}{'...' if len(smiles) > 60 else ''}")
        
        # Convertir
        mol = smiles_to_3d_mol(smiles, mol_name)
        
        if mol is None:
            print("  ✗ ÉCHEC conversion")
            fail_count += 1
            failed_molecules.append((rank, mol_name))
            print()
            continue
        
        # Informations molécule
        info = get_molecule_info(mol)
        print(f"  Atomes: {info['num_atoms']} ({info['num_heavy_atoms']} lourds)")
        print(f"  MW: {info['mol_weight']:.2f} Da")
        print(f"  Cycles: {info['num_rings']}, Rot. bonds: {info['num_rotatable_bonds']}")
        
        # Écrire PDB
        if write_pdb(mol, output_file, "LIG"):
            print(f"  ✓ Sauvegardé: {output_file.name}")
            success_count += 1
        else:
            print("  ✗ ÉCHEC écriture PDB")
            fail_count += 1
            failed_molecules.append((rank, mol_name))
        
        print()
    
    # Résumé
    print("=" * 70)
    print("RÉSUMÉ")
    print("=" * 70)
    print(f"Total:      {len(df)}")
    print(f"Succès:     {success_count} ✓")
    print(f"Échecs:     {fail_count} ✗")
    
    if failed_molecules:
        print("\nMolécules échouées:")
        for rank, name in failed_molecules:
            print(f"  - Rang {rank}: {name}")
    
    print(f"\nFichiers PDB dans: {OUTPUT_DIR}")
    
    # Liste fichiers générés
    pdb_files = list(output_path.glob("*.pdb"))
    if pdb_files:
        print(f"\nFichiers générés ({len(pdb_files)}):")
        for pdb_file in sorted(pdb_files):
            size_kb = pdb_file.stat().st_size / 1024
            print(f"  {pdb_file.name} ({size_kb:.1f} KB)")
    
    print()
    print("=" * 70)
    print("PROCHAINES ÉTAPES")
    print("=" * 70)
    print("1. Visualiser les structures:")
    print(f"   pymol {OUTPUT_DIR}/ligand_01.pdb")
    print()
    print("2. Paramétrer pour GROMACS:")
    print("   - CGenFF (CHARMM)")
    print("   - ACPYPE (AMBER)")
    print("   - OpenFF (moderne)")
    print()
    print("3. Docking moléculaire (optionnel)")
    print()
    print("4. Complex assembly (step3)")
    
    return 0 if fail_count == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
