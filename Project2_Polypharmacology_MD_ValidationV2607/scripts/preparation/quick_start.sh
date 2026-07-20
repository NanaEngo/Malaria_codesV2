#!/bin/bash
################################################################################
# Quick Start Script - Préparation structures MD Anti-Malaria
################################################################################
#
# Ce script guide à travers le workflow complet de préparation
#
# Usage: ./quick_start.sh
#
################################################################################

set -e  # Arrêter en cas d'erreur

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo ""
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC}  $1"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_step() {
    echo -e "${GREEN}▶${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

ask_continue() {
    echo ""
    read -p "Continuer? [Y/n] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]] && [[ ! -z $REPLY ]]; then
        print_warning "Arrêt par l'utilisateur"
        exit 0
    fi
}

################################################################################
# HEADER
################################################################################

clear
print_header "Quick Start - Préparation MD Anti-Malaria"

echo "Ce script va vous guider à travers:"
echo "  1. Vérification des dépendances"
echo "  2. Préparation des structures (4 cibles)"
echo "  3. Validation et tests"
echo "  4. Instructions pour le serveur"
echo ""

ask_continue

################################################################################
# STEP 1: Vérification dépendances
################################################################################

print_header "ÉTAPE 1: Vérification des dépendances"

# Python
print_step "Vérification Python..."
if command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
    print_success "Python $PYTHON_VERSION"
else
    print_error "Python non trouvé"
    exit 1
fi

# PDBFixer
print_step "Vérification PDBFixer..."
if python -c "from pdbfixer import PDBFixer" 2>/dev/null; then
    print_success "PDBFixer installé"
else
    print_error "PDBFixer manquant"
    echo ""
    echo "Installez avec:"
    echo "  mamba install -c conda-forge pdbfixer openmm"
    echo ""
    exit 1
fi

# OpenMM
print_step "Vérification OpenMM..."
if python -c "from openmm.app import PDBFile" 2>/dev/null; then
    print_success "OpenMM installé"
else
    print_error "OpenMM manquant"
    echo ""
    echo "Installez avec:"
    echo "  mamba install -c conda-forge openmm"
    echo ""
    exit 1
fi

print_success "Toutes les dépendances sont installées!"

################################################################################
# STEP 2: Préparation structures
################################################################################

print_header "ÉTAPE 2: Préparation des structures"

echo "Cibles à préparer:"
echo "  • 7F3Y - PfDHFR-TS"
echo "  • 6UKJ - PfDHFR-TS"
echo "  • 4GM2 - PfDHFR-TS"
echo "  • 9N10 - PfDHFR-TS"
echo ""
echo "Durée estimée: 2-4 minutes"
echo ""

ask_continue

print_step "Lancement de prepare_all_targets.py..."
echo ""

if python prepare_all_targets.py; then
    print_success "Préparation terminée!"
else
    print_error "Erreur pendant la préparation"
    echo "Consultez TROUBLESHOOTING.md pour l'aide"
    exit 1
fi

################################################################################
# STEP 3: Validation
################################################################################

print_header "ÉTAPE 3: Validation"

print_step "Exécution des tests automatisés..."
echo ""

if python test_preparation.py; then
    print_success "Tous les tests sont passés!"
else
    print_warning "Certains tests ont échoué"
    echo "Vérifiez les messages ci-dessus"
    ask_continue
fi

################################################################################
# STEP 4: Vérification qualité (optionnel)
################################################################################

print_header "ÉTAPE 4: Vérification qualité détaillée (optionnel)"

echo "Voulez-vous exécuter une vérification détaillée de la qualité PDB?"
read -p "Cela peut prendre quelques minutes [y/N] " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_step "Vérification qualité PDB..."
    
    for PDB in 7F3Y 6UKJ 4GM2 9N10; do
        FILE="prepared_structures/${PDB}/${PDB}_chainA_noH.pdb"
        if [ -f "$FILE" ]; then
            echo ""
            echo "════════════════════════════════════════════════"
            echo "Vérification: $PDB"
            echo "════════════════════════════════════════════════"
            ./check_pdb_quality.sh "$FILE" || true
        fi
    done
    
    print_success "Vérification qualité terminée"
else
    print_step "Vérification qualité sautée"
fi

################################################################################
# STEP 5: Résumé et prochaines étapes
################################################################################

print_header "ÉTAPE 5: Résumé et prochaines étapes"

echo "✓ Structures préparées avec succès!"
echo ""
echo "Fichiers générés dans: prepared_structures/"
echo ""
ls -lh prepared_structures/*/___*_noH.pdb 2>/dev/null | awk '{print "  " $9 " (" $5 ")")' || echo "  (Fichiers listés ci-dessus)"
echo ""

print_header "PROCHAINES ÉTAPES"

echo "Sur votre machine locale:"
echo ""
echo "  1. Visualiser une structure (optionnel):"
echo "     pymol prepared_structures/7F3Y/7F3Y_chainA_noH.pdb"
echo ""
echo "  2. Uploader vers le serveur GROMACS:"
echo "     scp -r prepared_structures/ user@server:/path/to/project/"
echo "     scp step2b_topology_generation.py user@server:/path/to/project/"
echo "     scp batch_topology_generation.sh user@server:/path/to/project/"
echo ""

echo "Sur le serveur:"
echo ""
echo "  3. Se connecter au serveur:"
echo "     ssh user@server"
echo "     cd /path/to/project"
echo ""
echo "  4. Charger GROMACS:"
echo "     module load gromacs/2025"
echo ""
echo "  5. Générer les topologies:"
echo "     # Une cible:"
echo "     python step2b_topology_generation.py --pdb 7F3Y --chain A"
echo ""
echo "     # Toutes les cibles:"
echo "     bash batch_topology_generation.sh"
echo ""
echo "  6. Procéder à step3_complex_assembly.py"
echo ""

print_header "DOCUMENTATION"

echo "Guide rapide:       QUICKSTART_TOPOLOGY.md"
echo "Dépannage:          TROUBLESHOOTING.md"
echo "Batch processing:   README_PREPARE_ALL.md"
echo "Index complet:      INDEX.md"
echo ""

print_success "Quick Start terminé!"
echo ""
echo "Bon courage avec vos simulations MD anti-malaria! 🦟"
echo ""
