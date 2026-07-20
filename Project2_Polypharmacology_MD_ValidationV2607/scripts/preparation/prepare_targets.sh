#!/bin/bash
# =============================================================================
# PIPELINE DE PRÉPARATION — 6UKJ (PfCRT) et 7F3Y (PfDHFR-TS)
# À exécuter dans l'environnement conda : malaria_md
# =============================================================================
# Usage : bash prepare_targets.sh
# Ou étape par étape en copiant les blocs ci-dessous
# =============================================================================

#conda activate malaria_md
#cd ~/Tuto_MD_MC   # adapter selon ton répertoire de travail


# ─────────────────────────────────────────────────────────────────────────────
# BLOC 0 — Vérifications préalables
# ─────────────────────────────────────────────────────────────────────────────

echo "=== Vérification des fichiers source ==="
ls -lh ./protein_prep/6UKJ.pdb ./protein_prep/7F3Y.pdb

echo "=== Vérification des dépendances ==="
python3 -c "import pdbfixer, openmm; print('pdbfixer', pdbfixer.__version__, '| openmm OK')"


# ─────────────────────────────────────────────────────────────────────────────
# BLOC 1 — Préparation 6UKJ (PfCRT 7G8)
# ─────────────────────────────────────────────────────────────────────────────

echo ""
echo "=== PRÉPARATION 6UKJ ==="
python3 prepare_6UKJ.py

# Vérifications post-script
echo "--- Vérification 6UKJ_protein.pdb ---"
grep "^ATOM" ./protein_prep/6UKJ_protein.pdb | wc -l        # nombre d'atomes protéine
grep "^HETATM" ./protein_prep/6UKJ_protein.pdb | awk '{print $4}' | sort | uniq -c
                                               # ne doit PAS contenir Y01
grep "CHAIN H\|CHAIN L" ./protein_prep/6UKJ_protein.pdb || echo "OK — chaînes FAB absentes"
grep " 501 " ./protein_prep/6UKJ_protein.pdb | head -2 || echo "OK — résidu Y01 (501) absent"

echo "--- Vérification 6UKJ_Y01.pdb ---"
wc -l ./protein_prep/6UKJ_Y01.pdb                            # doit être 10 lignes + END

# Convertir Y01 en mol2 pour CGenFF
obabel ./protein_prep/6UKJ_Y01.pdb -O ./protein_prep/6UKJ_Y01.mol2 --gen3d -h
echo "Y01.mol2 prêt pour upload sur https://cgenff.com"


# ─────────────────────────────────────────────────────────────────────────────
# BLOC 2 — Préparation 7F3Y (PfDHFR-TS WT)
# ─────────────────────────────────────────────────────────────────────────────

echo ""
echo "=== PRÉPARATION 7F3Y — option recommandée : linker tronqué ==="
python3 prepare_7F3Y.py --no-linker

# Si tu préfères reconstruire le linker avec PDBFixer (moins fiable) :
# python3 prepare_7F3Y.py

# Vérifications post-script
echo "--- Vérification 7F3Y_protein.pdb ---"
grep "^ATOM" ./protein_prep/7F3Y_protein.pdb | awk '{print substr($0,22,1)}' | sort | uniq -c
                                               # doit montrer A et B
grep "^HETATM" ./protein_prep/7F3Y_protein.pdb | awk '{print $4}' | sort | uniq -c
                                               # NDP, UMP, HOH — PAS MTX ni GOL
grep "MTX\|GOL" ./protein_prep/7F3Y_protein.pdb || echo "OK — MTX et GOL absents"

echo "--- Vérification cofacteurs extraits ---"
wc -l ./protein_prep/7F3Y_NDP.pdb ./protein_prep/7F3Y_UMP.pdb              # NDP ~96 lignes, UMP ~40 lignes

# Convertir cofacteurs en mol2 pour CGenFF
obabel ./protein_prep/7F3Y_NDP.pdb -O ./protein_prep/7F3Y_NDP.mol2 --gen3d -h
obabel ./protein_prep/7F3Y_UMP.pdb -O ./protein_prep/7F3Y_UMP.mol2 --gen3d -h
echo "NDP.mol2 et UMP.mol2 prêts pour upload sur https://cgenff.com"


# ─────────────────────────────────────────────────────────────────────────────
# BLOC 3 — Vérification visuelle dans ChimeraX (commandes à taper dans ChimeraX)
# ─────────────────────────────────────────────────────────────────────────────

# Ouvrir ChimeraX et taper :
#   open 6UKJ_protein.pdb
#   open 6UKJ_Y01.pdb
#   open 7F3Y_protein.pdb
#
# Vérifier :
#   - Pas de chaînes FAB dans 6UKJ
#   - Boucle 114–122 reconstruite dans 6UKJ
#   - Dimère A+B intact dans 7F3Y
#   - Cofacteurs NDP et UMP présents dans 7F3Y
#   - Pas de MTX ni GOL dans 7F3Y


# ─────────────────────────────────────────────────────────────────────────────
# BLOC 4 — Génération des topologies protéines avec pdb2gmx
# ─────────────────────────────────────────────────────────────────────────────

echo ""
echo "=== pdb2gmx — 6UKJ ==="
gmx pdb2gmx -f ./protein_prep/6UKJ_protein.pdb \
            -o ./protein_prep/6UKJ_processed.gro \
            -p ./protein_prep/6UKJ_topol.top \
            -i ./protein_prep/6UKJ_posre.itp \
            -ff charmm36-feb2026_cgenff-5.0 \
            -water tip3p \
            -ter
# Aux questions termini : choisir "None" pour N-term et C-term
# (les tags ont été supprimés — les vrais termini sont 47 et 405)

echo ""
echo "=== pdb2gmx — 7F3Y ==="
gmx pdb2gmx -f ./protein_prep/7F3Y_protein.pdb \
            -o ./protein_prep/7F3Y_processed.gro \
            -p ./protein_prep/7F3Y_topol.top \
            -i ./protein_prep/7F3Y_posre.itp \
            -ff charmm36-feb2026_cgenff-5.0 \
            -water tip3p \
            -ter
# Aux questions termini : choisir selon le dimère (4 termini = A_N, A_C, B_N, B_C)


# ─────────────────────────────────────────────────────────────────────────────
# BLOC 5 — Paramétrisation des cofacteurs sur CGenFF (étape manuelle)
# ─────────────────────────────────────────────────────────────────────────────

# 1. Aller sur https://cgenff.com
# 2. Pour chaque molécule, uploader le .mol2 correspondant :
#    - 6UKJ_Y01.mol2   → télécharger Y01.itp  + Y01.prm
#    - 7F3Y_NDP.mol2   → télécharger NDP.itp  + NDP.prm
#    - 7F3Y_UMP.mol2   → télécharger UMP.itp  + UMP.prm
#    - tes 20 ligands  → télécharger LIG_XX.itp + LIG_XX.prm
#
# 3. Placer les .itp dans le même répertoire que les topologies


# ─────────────────────────────────────────────────────────────────────────────
# BLOC 6 — Vérifications finales avant MD
# ─────────────────────────────────────────────────────────────────────────────

echo ""
echo "=== Fichiers générés ==="
ls -lh 6UKJ_protein.pdb 6UKJ_Y01.pdb 6UKJ_Y01.mol2 \
        6UKJ_processed.gro 6UKJ_topol.top
echo ""
ls -lh 7F3Y_protein.pdb 7F3Y_NDP.pdb 7F3Y_UMP.pdb \
        7F3Y_NDP.mol2 7F3Y_UMP.mol2 \
        7F3Y_processed.gro 7F3Y_topol.top

echo ""
echo "=== RÉSUMÉ ==="
echo "6UKJ : protéine prête | Y01 extrait → paramétrer sur CGenFF"
echo "7F3Y : dimère prêt | NDP + UMP extraits → paramétrer sur CGenFF"
echo "Prochaine étape : assembler complexes protéine+ligand+cofacteurs"
