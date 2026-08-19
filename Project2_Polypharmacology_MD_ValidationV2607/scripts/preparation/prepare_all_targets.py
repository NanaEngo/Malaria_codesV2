#!/usr/bin/env python
"""
Prépare automatiquement toutes les cibles pour les simulations MD
Utilise PDBFixer pour réparer les structures
"""

import sys
import urllib.request
from pathlib import Path

try:
    from pdbfixer import PDBFixer
    from openmm.app import PDBFile
except ImportError:
    print("ERROR: PDBFixer not found!")
    print("Install with: mamba install -c conda-forge pdbfixer openmm")
    sys.exit(1)

# ──────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────────────────────────────────────────

TARGETS = [
    {"pdb": "7F3Y", "chain": "A", "name": "PfDHFR-TS 7F3Y"},
    {"pdb": "6UKJ", "chain": "A", "name": "PfCRT 6UKJ"},
    {"pdb": "4GM2", "chain": "A", "name": "PfClpR 4GM2 (not PfClpP)"},
    {"pdb": "9N10", "chain": "A", "name": "PfATP4 9N10"},
]

OUTPUT_BASE = "prepared_structures"
PH = 7.4
REMOVE_HETEROGENS = True
FIX_MISSING_RESIDUES = True
FIX_MISSING_ATOMS = True

# ──────────────────────────────────────────────────────────────────────────────

def prepare_target(pdb_id, chain, name):
    """Prépare une cible spécifique"""
    
    print("=" * 70)
    print(f"PRÉPARATION: {name} ({pdb_id}, chaîne {chain})")
    print("=" * 70)
    
    # Créer dossier de sortie
    output_dir = Path(OUTPUT_BASE) / pdb_id
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # ──────────────────────────────────────────────────────────────────────────
    # 1. TÉLÉCHARGEMENT
    # ──────────────────────────────────────────────────────────────────────────
    
    raw_pdb = output_dir / f"{pdb_id}_raw.pdb"
    url = f"https://files.rcsb.org/download/{pdb_id}.pdb"
    
    if raw_pdb.exists():
        print(f"✓ Déjà téléchargé: {raw_pdb}")
    else:
        print(f"Téléchargement depuis {url}...")
        try:
            urllib.request.urlretrieve(url, raw_pdb)
            print(f"✓ Sauvegardé: {raw_pdb}")
        except Exception as e:
            print(f"✗ Erreur téléchargement: {e}")
            return False
    
    # ──────────────────────────────────────────────────────────────────────────
    # 2. INSPECTION RAPIDE
    # ──────────────────────────────────────────────────────────────────────────
    
    print("\nInspection de la structure...")
    chains = set()
    residue_count = 0
    
    with open(raw_pdb) as f:
        for line in f:
            if line.startswith("ATOM"):
                chains.add(line[21])
                residue_count += 1
    
    print(f"  Chaînes trouvées: {sorted(chains)}")
    print(f"  Atomes: {residue_count}")
    
    # ──────────────────────────────────────────────────────────────────────────
    # 3. RÉPARATION AVEC PDBFIXER
    # ──────────────────────────────────────────────────────────────────────────
    
    print("\nRéparation avec PDBFixer...")
    
    try:
        fixer = PDBFixer(filename=str(raw_pdb))
        print("✓ Structure chargée")
        
        # Garder seulement la chaîne spécifiée
        if chain:
            chains_to_remove = []
            for ch in fixer.topology.chains():
                if ch.id != chain:
                    chains_to_remove.append(ch.index)
            
            if chains_to_remove:
                fixer.removeChains(chainIds=chains_to_remove)
                print(f"✓ Gardé chaîne {chain}, retiré {len(chains_to_remove)} chaîne(s)")
        
        # Trouver résidus manquants
        if FIX_MISSING_RESIDUES:
            fixer.findMissingResidues()
            if fixer.missingResidues:
                print(f"⚠ Trouvé {len(fixer.missingResidues)} région(s) de résidus manquants")
            else:
                print("✓ Pas de résidus manquants")
        
        # Retirer hétérogènes
        if REMOVE_HETEROGENS:
            fixer.removeHeterogens(keepWater=False)
            print("✓ Hétérogènes retirés")
        
        # Trouver atomes manquants
        if FIX_MISSING_ATOMS:
            fixer.findMissingAtoms()
            if fixer.missingAtoms or fixer.missingTerminals:
                fixer.addMissingAtoms()
                print("✓ Atomes manquants ajoutés")
            else:
                print("✓ Pas d'atomes manquants")
        
        # Ajouter hydrogènes
        print(f"Ajout d'hydrogènes à pH {PH}...")
        fixer.addMissingHydrogens(pH=PH)
        print("✓ Hydrogènes ajoutés")
        
        # Sauvegarder structure avec H
        fixed_pdb = output_dir / f"{pdb_id}_chain{chain}_fixed.pdb"
        with open(fixed_pdb, 'w') as f:
            PDBFile.writeFile(fixer.topology, fixer.positions, f, keepIds=True)
        print(f"✓ Structure avec H: {fixed_pdb.name}")
        
        # ──────────────────────────────────────────────────────────────────
        # NETTOYAGE POUR GROMACS
        # ──────────────────────────────────────────────────────────────────
        
        print("Nettoyage pour compatibilité GROMACS...")
        
        # Résidus standards
        STANDARD_RESIDUES = {
            'ALA', 'ARG', 'ASN', 'ASP', 'CYS', 'GLN', 'GLU', 'GLY', 'HIS', 'ILE',
            'LEU', 'LYS', 'MET', 'PHE', 'PRO', 'SER', 'THR', 'TRP', 'TYR', 'VAL',
            'HIE', 'HID', 'HIP', 'HSD', 'HSE', 'HSP', 'CYX', 'CYM', 'ASH', 'GLH', 'LYN',
        }
        
        # Atomes à sauter (artefacts nucléiques)
        SKIP_ATOMS = {"O3'", "O5'", "C3'", "C4'", "C5'", "P", "OP1", "OP2", "O2'", "C2'", "C1'"}
        
        clean_pdb = output_dir / f"{pdb_id}_chain{chain}_clean.pdb"
        kept = 0
        skipped = 0
        
        with open(fixed_pdb, 'r') as fin, open(clean_pdb, 'w') as fout:
            for line in fin:
                if line.startswith(('ATOM', 'HETATM')):
                    resname = line[17:20].strip()
                    atomname = line[12:16].strip()
                    
                    if resname not in STANDARD_RESIDUES or atomname in SKIP_ATOMS:
                        skipped += 1
                        continue
                    
                    fout.write(line)
                    kept += 1
                elif line.startswith(('MODEL', 'ENDMDL', 'TER', 'END', 'CRYST1', 'REMARK')):
                    fout.write(line)
        
        print(f"✓ Nettoyage: {kept} atomes gardés, {skipped} retirés")
        print(f"✓ Structure nettoyée: {clean_pdb.name}")
        
        # Créer version sans H pour GROMACS (depuis clean_pdb)
        no_h_pdb = output_dir / f"{pdb_id}_chain{chain}_noH.pdb"
        with open(clean_pdb, 'r') as fin, open(no_h_pdb, 'w') as fout:
            for line in fin:
                if line.startswith(('ATOM', 'HETATM')):
                    atomname = line[12:16].strip()
                    element = line[76:78].strip() if len(line) > 77 else atomname[0]
                    if element not in ['H', 'D']:
                        fout.write(line)
                else:
                    fout.write(line)
        
        print(f"✓ Structure sans H: {no_h_pdb.name}")
        
        # Statistiques finales
        atom_count = sum(1 for _ in fixer.topology.atoms())
        residue_count = sum(1 for _ in fixer.topology.residues())
        print(f"\nStructure finale: {residue_count} résidus, {atom_count} atomes")
        
        return True
        
    except Exception as e:
        print(f"✗ Erreur pendant la réparation: {e}")
        import traceback
        traceback.print_exc()
        return False

# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────

def main():
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "PRÉPARATION AUTOMATIQUE DES CIBLES" + " " * 19 + "║")
    print("║" + " " * 20 + "Projet Anti-Malaria MD" + " " * 25 + "║")
    print("╚" + "═" * 68 + "╝")
    print()
    
    # Vérifier les dépendances
    print("Vérification des dépendances...")
    try:
        from pdbfixer import PDBFixer
        from openmm.app import PDBFile
        print("✓ PDBFixer et OpenMM disponibles")
    except ImportError as e:
        print(f"✗ Erreur: {e}")
        print("Installez avec: mamba install -c conda-forge pdbfixer openmm")
        return 1
    print()
    
    # Créer dossier de base
    Path(OUTPUT_BASE).mkdir(exist_ok=True)
    
    # Statistiques
    success_count = 0
    fail_count = 0
    failed_targets = []
    
    # Traiter chaque cible
    for idx, target in enumerate(TARGETS, 1):
        print(f"[{idx}/{len(TARGETS)}] Traitement de {target['pdb']}...")
        print()
        
        success = prepare_target(
            target["pdb"],
            target["chain"],
            target["name"]
        )
        
        if success:
            success_count += 1
            print(f"\n✓ {target['pdb']} préparé avec succès!")
        else:
            fail_count += 1
            failed_targets.append(target["pdb"])
            print(f"\n✗ Échec de la préparation de {target['pdb']}")
        
        print()
    
    # Résumé final
    print("=" * 70)
    print("RÉSUMÉ")
    print("=" * 70)
    print(f"Total:      {len(TARGETS)}")
    print(f"Succès:     {success_count} ✓")
    print(f"Échecs:     {fail_count} ✗")
    
    if failed_targets:
        print(f"\nCibles échouées: {', '.join(failed_targets)}")
    
    if success_count > 0:
        print("\nCibles réussies:")
        for target in TARGETS:
            if target["pdb"] not in failed_targets:
                target_dir = Path(OUTPUT_BASE) / target["pdb"]
                noH_file = target_dir / f"{target['pdb']}_chain{target['chain']}_noH.pdb"
                if noH_file.exists():
                    size_mb = noH_file.stat().st_size / 1024 / 1024
                    print(f"  ✓ {target['pdb']}: {noH_file.name} ({size_mb:.2f} MB)")
    
    print(f"\nFichiers préparés dans: {OUTPUT_BASE}/")
    print("\nFichiers générés pour chaque cible:")
    print("  - {PDB}_raw.pdb             (structure originale)")
    print("  - {PDB}_chain{X}_fixed.pdb  (avec H, tous atomes)")
    print("  - {PDB}_chain{X}_clean.pdb  (protéine seule avec H)")
    print("  - {PDB}_chain{X}_noH.pdb    (protéine sans H, pour GROMACS) ← UTILISEZ")
    
    print("\n" + "=" * 70)
    print("PROCHAINES ÉTAPES")
    print("=" * 70)
    print("1. Vérifier les structures générées:")
    print(f"   ./check_pdb_quality.sh {OUTPUT_BASE}/{{PDB}}/{{PDB}}_chain{{X}}_noH.pdb")
    print()
    print(f"2. Uploader {OUTPUT_BASE}/ vers le serveur GROMACS:")
    print(f"   scp -r {OUTPUT_BASE}/ user@server:/path/to/md_project/")
    print()
    print("3. Sur le serveur, lancer la génération de topologie:")
    print("   python step2b_topology_generation.py --pdb {{PDB}} --chain {{X}}")
    print("   # Ou en batch:")
    print("   bash batch_topology_generation.sh")
    print()
    print("4. Puis procéder à step3_complex_assembly.py")
    
    return 0 if fail_count == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
