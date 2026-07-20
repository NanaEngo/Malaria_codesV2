"""
prepare_7F3Y.py
===============
Préparation de 7F3Y (PfDHFR-TS Wild-type) pour simulation GROMACS.

Ce script effectue :
  1. Suppression de MTX (inhibiteur — remplacé par tes ligands)
  2. Suppression de GOL (glycérol cryoprotectant)
  3. Conservation de NDP (NADPH) et UMP (dUMP) — cofacteurs essentiels
  4. Extraction séparée de NDP et UMP pour paramétrisation CGenFF
  5. Reconstruction de la boucle 86–95 (10 résidus, faisable)
  6. Gestion du linker 232–283 (52 résidus) — deux options disponibles
  7. Reconstruction de ASP B284 (chaîne latérale incomplète)
  8. Ajout des hydrogènes à pH 7.4

Dépendances : pdbfixer, openmm
Installation : mamba install pdbfixer openmm -c conda-forge

Usage :
  python prepare_7F3Y.py             # reconstruit le linker avec PDBFixer
  python prepare_7F3Y.py --no-linker # tronque le linker (recommandé)

Sortie :
  - 7F3Y_protein.pdb  → protéine + eaux, prête pour pdb2gmx
  - 7F3Y_NDP.pdb      → NADPH chaînes A+B pour CGenFF 
  - 7F3Y_UMP.pdb      → dUMP chaînes A+B pour CGenFF
"""

import sys
import os
from pdbfixer import PDBFixer
from openmm.app import PDBFile

INPUT       = "./protein_prep/7F3Y.pdb"
OUT_PROTEIN = "./protein_prep/7F3Y_protein.pdb"
OUT_NDP     = "./protein_prep/7F3Y_NDP.pdb"
OUT_UMP     = "./protein_prep/7F3Y_UMP.pdb"

# Option : tronquer le linker désordonnée 232–283 au lieu de le reconstruire
TRUNCATE_LINKER = "--no-linker" in sys.argv
LINKER_START = 232
LINKER_END   = 283

LIGANDS_TO_REMOVE = {"MTX", "GOL"}
COFACTORS_TO_KEEP = {"NDP", "UMP"}


# ════════════════════════════════════════════════════════════════════════════════
# ÉTAPE 1 — Extraire NDP et UMP avant PDBFixer (qui supprimerait les HETATM)
# ════════════════════════════════════════════════════════════════════════════════
print("[1/6] Extraction des cofacteurs NDP (NADPH) et UMP (dUMP)...")

ndp_lines, ump_lines = [], []
with open(INPUT, "r") as f:
    for line in f:
        if not line.startswith("HETATM"):
            continue
        resname = line[17:20].strip()
        if resname == "NDP":
            ndp_lines.append(line)
        elif resname == "UMP":
            ump_lines.append(line)

for fname, lines, name in [(OUT_NDP, ndp_lines, "NDP"), (OUT_UMP, ump_lines, "UMP")]:
    if lines:
        with open(fname, "w") as f:
            f.writelines(lines)
            f.write("END\n")
        print(f"  → {len(lines)} atomes {name} sauvegardés dans {fname}")
    else:
        print(f"  ATTENTION : aucun atome {name} trouvé")


# ════════════════════════════════════════════════════════════════════════════════
# ÉTAPE 2 — Nettoyage manuel : retirer MTX et GOL, garder NDP/UMP/HOH
# On réécrit le fichier source proprement avant de passer à PDBFixer
# ════════════════════════════════════════════════════════════════════════════════
print("[2/6] Suppression de MTX et GOL, conservation NDP/UMP/HOH...")

TMP_CLEAN = "7F3Y_clean_tmp.pdb"
removed = {k: 0 for k in LIGANDS_TO_REMOVE}

with open(INPUT, "r") as fin, open(TMP_CLEAN, "w") as fout:
    for line in fin:
        if line.startswith("HETATM"):
            resname = line[17:20].strip()
            if resname in LIGANDS_TO_REMOVE:
                removed[resname] += 1
                continue  # supprimer cette ligne
        fout.write(line)

for mol, count in removed.items():
    print(f"  {mol} supprimé : {count} atomes")


# ════════════════════════════════════════════════════════════════════════════════
# ÉTAPE 3 — Gestion du linker DHFR-TS (résidus 232–283)
# ════════════════════════════════════════════════════════════════════════════════
if TRUNCATE_LINKER:
    print(f"[3/6] Option --no-linker : troncature du linker {LINKER_START}–{LINKER_END}...")
    print("  (région intrinsèquement désordonnée — absente dans toutes les structures PDB)")
    TMP_NOLINKER = "7F3Y_nolinker_tmp.pdb"
    skipped_linker = 0
    with open(TMP_CLEAN, "r") as fin, open(TMP_NOLINKER, "w") as fout:
        for line in fin:
            if line.startswith(("ATOM", "HETATM")):
                try:
                    resnum = int(line[22:26].strip())
                except ValueError:
                    fout.write(line)
                    continue
                if LINKER_START <= resnum <= LINKER_END:
                    skipped_linker += 1
                    continue
            fout.write(line)
    os.remove(TMP_CLEAN)
    os.rename(TMP_NOLINKER, TMP_CLEAN)
    print(f"  Linker supprimé : {skipped_linker} atomes (dans A et B)")
else:
    print("[3/6] Linker 232–283 sera reconstruit par PDBFixer (52 résidus).")
    print("  AVERTISSEMENT : reconstruction de 52 résidus désordonnés = faible fiabilité.")
    print("  Utiliser --no-linker ou AlphaFold2 pour un modèle plus fiable.")


# ════════════════════════════════════════════════════════════════════════════════
# ÉTAPE 4 — PDBFixer : reconstruction des résidus manquants biologiques
# Boucle 86–95 + ASP B284 chaîne latérale
# ════════════════════════════════════════════════════════════════════════════════
print("[4/6] Reconstruction des résidus manquants (boucle 86–95, ASP B284)...")
fixer = PDBFixer(filename=TMP_CLEAN)

fixer.findMissingResidues()
missing = fixer.missingResidues

# Si on a tronqué le linker, s'assurer que PDBFixer ne tente pas de le reconstruire
if TRUNCATE_LINKER and missing:
    keys_to_remove = [
        k for k in missing.keys()
        if LINKER_START <= k[1] <= LINKER_END
    ]
    for k in keys_to_remove:
        del missing[k]
    if keys_to_remove:
        print(f"  Linker exclu de la reconstruction : {len(keys_to_remove)} segments")

remaining = {k: v for k, v in missing.items()}
if remaining:
    print(f"  Résidus à reconstruire : {remaining}")
else:
    print("  Aucun résidu manquant à reconstruire (hors linker)")

fixer.findNonstandardResidues()
fixer.replaceNonstandardResidues()
fixer.findMissingAtoms()
fixer.addMissingAtoms()
print("  ASP B284 chaîne latérale reconstruite (CG, OD1, OD2)")


# ════════════════════════════════════════════════════════════════════════════════
# ÉTAPE 5 — Ajout des hydrogènes à pH 7.4
# ════════════════════════════════════════════════════════════════════════════════
print("[5/6] Ajout des hydrogènes (pH 7.4)...")
fixer.addMissingHydrogens(7.4)


# ════════════════════════════════════════════════════════════════════════════════
# ÉTAPE 6 — Sauvegarde et nettoyage
# ════════════════════════════════════════════════════════════════════════════════
print("[6/6] Sauvegarde...")
with open(OUT_PROTEIN, "w") as f:
    PDBFile.writeFile(fixer.topology, fixer.positions, f)

os.remove(TMP_CLEAN)

# ── Rapport final ─────────────────────────────────────────────────────────────
atom_count  = sum(1 for l in open(OUT_PROTEIN) if l.startswith("ATOM"))
hetatm_count = sum(1 for l in open(OUT_PROTEIN) if l.startswith("HETATM"))

print("\n" + "="*60)
print("RAPPORT FINAL — 7F3Y")
print("="*60)
print(f"  Protéine + cofacteurs : {OUT_PROTEIN}")
print(f"    → {atom_count} atomes ATOM")
print(f"    → {hetatm_count} atomes HETATM (NDP + UMP + HOH)")
print(f"  NADPH extrait  : {OUT_NDP}  ({len(ndp_lines)} atomes)")
print(f"  dUMP extrait   : {OUT_UMP}  ({len(ump_lines)} atomes)")
linker_status = "TRONQUÉ" if TRUNCATE_LINKER else "RECONSTRUIT par PDBFixer"
print(f"  Linker 232–283 : {linker_status}")
print()
print("ÉTAPES SUIVANTES :")
print("  1. Vérifier visuellement dans ChimeraX :")
print("     open 7F3Y_protein.pdb")
print()
print("  2. Paramétrer les cofacteurs sur https://cgenff.com")
print("     → Upload 7F3Y_NDP.pdb  → télécharger NDP.itp")
print("     → Upload 7F3Y_UMP.pdb  → télécharger UMP.itp")
print()
print("  3. Lancer pdb2gmx :")
print("     gmx pdb2gmx -f 7F3Y_protein.pdb -o 7F3Y_processed.gro \\")
print("                 -ff charmm36-feb2026_cgenff-5.0 -water tip3p -ter")
print("="*60)
