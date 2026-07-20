"""
prepare_6UKJ.py
===============
Préparation de 6UKJ (PfCRT 7G8) pour simulation GROMACS.

Ce script effectue :
  1. Suppression des chaînes FAB (H, L) — artifacts cryo-EM
  2. Suppression des tags d'expression N- et C-terminaux (résidus ≤46 et ≥406)
  3. Extraction du ligand Y01 dans un fichier séparé
  4. Reconstruction des résidus manquants biologiques (boucle 114–122)
  5. Reconstruction des chaînes latérales tronquées (8 résidus)
  6. Ajout des hydrogènes à pH 7.4

Dépendances : pdbfixer, openmm
Installation : mamba install pdbfixer openmm -c conda-forge

Usage : python prepare_6UKJ.py
Sortie :
  - 6UKJ_protein.pdb  → protéine prête pour pdb2gmx
  - 6UKJ_Y01.pdb      → ligand Y01 pour CGenFF
"""

from pdbfixer import PDBFixer
from openmm.app import PDBFile

INPUT  = "./protein_prep/6UKJ.pdb"
OUT_PROTEIN = "./protein_prep/6UKJ_protein.pdb"
OUT_LIGAND  = "./protein_prep/6UKJ_Y01.pdb"

# ── Résidus tags à exclure de la reconstruction ───────────────────────────────
# N-terminal : résidus -2 à 46 (tags + résidus non résolus du début)
# C-terminal : résidus 406 à 461 (His-tag + linker)
# Ces intervalles sont confirmés par SEQADV et REMARK 465
TAG_RANGES = [range(-2, 47), range(406, 462)]

def is_tag_residue(chain_id, res_num):
    if chain_id != "A":
        return False
    return any(res_num in r for r in TAG_RANGES)


# ════════════════════════════════════════════════════════════════════════════════
# ÉTAPE 1 — Extraire Y01 manuellement (grep-style) avant PDBFixer
# PDBFixer supprime les HETATM non reconnus — on sauvegarde Y01 d'abord
# ════════════════════════════════════════════════════════════════════════════════
print("[1/5] Extraction du ligand Y01...")
y01_lines = []
with open(INPUT, "r") as f:
    for line in f:
        if line.startswith("HETATM") and "Y01" in line:
            y01_lines.append(line)

if not y01_lines:
    print("  ATTENTION : aucun atome Y01 trouvé dans", INPUT)
else:
    with open(OUT_LIGAND, "w") as f:
        f.writelines(y01_lines)
        f.write("END\n")
    print(f"  → {len(y01_lines)} atomes Y01 sauvegardés dans {OUT_LIGAND}")


# ════════════════════════════════════════════════════════════════════════════════
# ÉTAPE 2 — Charger avec PDBFixer et supprimer les chaînes FAB
# ════════════════════════════════════════════════════════════════════════════════
print("[2/5] Chargement et suppression des chaînes FAB (H, L)...")
fixer = PDBFixer(filename=INPUT)

# Identifier les indices des chaînes à supprimer
chains = list(fixer.topology.chains())
chain_ids = [c.id for c in chains]
print(f"  Chaînes détectées : {chain_ids}")

chains_to_remove = [i for i, c in enumerate(chains) if c.id in ("H", "L")]
if chains_to_remove:
    fixer.removeChains(chains_to_remove)
    print(f"  Chaînes supprimées : {[chain_ids[i] for i in chains_to_remove]}")
else:
    print("  Aucune chaîne FAB trouvée (déjà supprimées ?)")


# ════════════════════════════════════════════════════════════════════════════════
# ÉTAPE 3 — Supprimer les tags d'expression
# PDBFixer ne gère pas la suppression par numéro de résidu directement.
# On passe par une réécriture intermédiaire.
# ════════════════════════════════════════════════════════════════════════════════
print("[3/5] Suppression des tags d'expression (résidus ≤46 et ≥406)...")

# Sauvegarder l'état intermédiaire (chaîne A seule, sans FAB)
TMP = "6UKJ_tmp_chainA.pdb"
with open(TMP, "w") as f:
    PDBFile.writeFile(fixer.topology, fixer.positions, f)

# Réécrire en filtrant les tags
kept = 0
skipped = 0
with open(TMP, "r") as fin, open("6UKJ_notag.pdb", "w") as fout:
    for line in fin:
        if line.startswith(("ATOM", "HETATM")):
            chain = line[21]
            try:
                resnum = int(line[22:26].strip())
            except ValueError:
                fout.write(line)
                continue
            if is_tag_residue(chain, resnum):
                skipped += 1
                continue
        fout.write(line)
        kept += 1

print(f"  Lignes conservées : {kept} | Tags supprimés : {skipped} atomes")

import os
os.remove(TMP)


# ════════════════════════════════════════════════════════════════════════════════
# ÉTAPE 4 — Reconstruction des résidus manquants biologiques
# Boucle 114–122 (9 résidus) entre hélices transmembranaires
# ════════════════════════════════════════════════════════════════════════════════
print("[4/5] Reconstruction des résidus manquants et chaînes latérales...")
fixer2 = PDBFixer(filename="6UKJ_notag.pdb")

fixer2.findMissingResidues()

# Afficher ce que PDBFixer va reconstruire
missing = fixer2.missingResidues
if missing:
    print(f"  Résidus à reconstruire : {dict(list(missing.items())[:5])}...")
else:
    print("  Aucun résidu manquant détecté")

fixer2.findNonstandardResidues()
fixer2.replaceNonstandardResidues()
fixer2.findMissingAtoms()
fixer2.addMissingAtoms()

print("  Chaînes latérales tronquées reconstruites :")
print("  LYS56, ASP57, HIS123, ARG124, ARG178, ARG400, LYS401, ARG404")


# ════════════════════════════════════════════════════════════════════════════════
# ÉTAPE 5 — Ajout des hydrogènes à pH physiologique + sauvegarde
# ════════════════════════════════════════════════════════════════════════════════
print("[5/5] Ajout des hydrogènes (pH 7.4) et sauvegarde...")
fixer2.addMissingHydrogens(7.4)

with open(OUT_PROTEIN, "w") as f:
    PDBFile.writeFile(fixer2.topology, fixer2.positions, f)

os.remove("6UKJ_notag.pdb")

# ── Rapport final ─────────────────────────────────────────────────────────────
atom_count = sum(1 for line in open(OUT_PROTEIN) if line.startswith("ATOM"))
print("\n" + "="*60)
print("RAPPORT FINAL — 6UKJ")
print("="*60)
print(f"  Protéine : {OUT_PROTEIN}")
print(f"    → {atom_count} atomes ATOM")
print(f"  Ligand   : {OUT_LIGAND}")
print(f"    → {len(y01_lines)} atomes Y01")
print()
print("ÉTAPES SUIVANTES :")
print("  1. Vérifier visuellement dans ChimeraX :")
print("     open 6UKJ_protein.pdb")
print("  2. Paramétrer Y01 sur https://cgenff.com")
print("     → Upload 6UKJ_Y01.pdb (ou convertir en .mol2 d'abord)")
print("  3. Lancer pdb2gmx :")
print("     gmx pdb2gmx -f 6UKJ_protein.pdb -o 6UKJ_processed.gro \\")
print("                 -ff charmm36-feb2026_cgenff-5.0 -water tip3p -ter")
print("="*60)
