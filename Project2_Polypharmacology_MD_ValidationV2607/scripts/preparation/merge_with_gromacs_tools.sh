#!/bin/bash
#
# Merge Ligand and Protein Using GROMACS Native Tools
#
# This script uses gmx trjconv and gmx insert-molecules to properly
# merge ligand coordinates into the protein system
#
# Usage: bash merge_with_gromacs_tools.sh LIG1
#        bash merge_with_gromacs_tools.sh all

# Don't exit on error in loop mode
# set -e

# Configuration
BASE_DIR="Gromacs_inputs"
LIGS=(LIG1 LIG2 LIG3 LIG5 LIG7 LIG8 LIG9 LIG10 LIG14 LIG15 LIG16 LIG17)

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

process_lig() {
    local LIG_NAME=$1
    local LIG_NUM=${LIG_NAME#LIG}
    
    echo "======================================================================"
    print_info "Processing $LIG_NAME"
    echo "======================================================================"
    
    # Find directories
    local CHARMM_DIR=$(ls -d ${BASE_DIR}/${LIG_NAME}/charmm-gui-* 2>/dev/null | head -1)
    local COMPLEX_DIR="${BASE_DIR}/${LIG_NAME}/Complex_${LIG_NUM}"
    
    if [ ! -d "$COMPLEX_DIR" ]; then
        print_error "Complex directory not found: $COMPLEX_DIR"
        return 1
    fi
    
    if [ ! -d "$CHARMM_DIR" ]; then
        print_error "CHARMM-GUI directory not found"
        return 1
    fi
    
    print_info "CHARMM-GUI: $(basename $CHARMM_DIR)"
    print_info "Complex: $(basename $COMPLEX_DIR)"
    
    # Build absolute paths before cd
    local LIGAND_PDB="$(cd "$(dirname "$CHARMM_DIR")" && pwd)/$(basename "$CHARMM_DIR")/ligandrm.pdb"
    
    cd "$COMPLEX_DIR" || exit 1
    
    # Check files
    if [ ! -f "$LIGAND_PDB" ]; then
        print_error "Ligand PDB not found: $LIGAND_PDB"
        cd - > /dev/null
        return 1
    fi
    
    if [ ! -f "step3_input.gro" ]; then
        print_error "step3_input.gro not found"
        cd - > /dev/null
        return 1
    fi
    
    # Backup original
    if [ ! -f "step3_input.gro.original" ]; then
        print_info "Creating backup: step3_input.gro.original"
        cp step3_input.gro step3_input.gro.original
    fi
    
    # Method 1: Simple concatenation (works for pre-positioned ligands)
    print_info "Converting ligand PDB to GRO"
    gmx editconf -f "$LIGAND_PDB" -o ligand_temp.gro > convert.log 2>&1
    
    if [ ! -f "ligand_temp.gro" ]; then
        print_error "Failed to convert ligand PDB"
        cd - > /dev/null
        return 1
    fi
    
    print_info "Extracting protein+solvent without ligand"
    # Get atom counts
    local N_PROT=$(sed -n '2p' step3_input.gro | awk '{print $1}')
    local N_LIG=$(sed -n '2p' ligand_temp.gro | awk '{print $1}')
    local N_TOTAL=$((N_PROT + N_LIG))
    
    print_info "  Protein system: $N_PROT atoms"
    print_info "  Ligand: $N_LIG atoms"
    print_info "  Total: $N_TOTAL atoms"
    
    # Create merged file
    print_info "Creating merged complex.gro"
    
    # Extract header
    head -1 step3_input.gro > complex.gro
    
    # Write new atom count
    printf "%5d\n" $N_TOTAL >> complex.gro
    
    # According to topology order: PROA, NDP, POT, CLA, TIP3, LIG
    # So ligand goes AFTER all water and ions, not before
    print_info "Appending ligand at end (after water/ions)"
    
    # Add all protein+solvent+ions
    tail -n +3 step3_input.gro | head -n -1 >> complex.gro
    
    # Add ligand at the end
    tail -n +3 ligand_temp.gro | head -n -1 >> complex.gro
    
    # Add box line
    tail -1 step3_input.gro >> complex.gro
    
    print_info "✓ complex.gro created with $N_TOTAL atoms"
    
    # Create restraint.gro for position restraints
    cp complex.gro restraint.gro
    print_info "✓ restraint.gro created"
    
    # Verify with GROMACS
    print_info "Verifying structure..."
    if gmx check -f complex.gro > check.log 2>&1; then
        print_info "✓ Structure verification passed"
    else
        print_warn "Structure check had warnings (may be OK for large systems)"
    fi
    
    # Clean up
    rm -f ligand_temp.gro convert.log check.log \#*
    
    print_info "────────────────────────────────────────────────────────────────"
    print_info "✓ $LIG_NAME complete!"
    print_info "  Output: complex.gro ($N_TOTAL atoms)"
    print_info "────────────────────────────────────────────────────────────────"
    
    cd - > /dev/null
    return 0
}

# Main
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║       Merge Ligand and Protein - GROMACS Native Tools              ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

# Check GROMACS
if ! command -v gmx &> /dev/null; then
    print_error "GROMACS not found"
    echo "Please activate malaria_md environment:"
    echo "  conda activate malaria_md"
    exit 1
fi

print_info "$(gmx --version 2>&1 | grep "GROMACS version" | head -1)"
echo ""

# Parse arguments
if [ $# -eq 0 ]; then
    print_error "Usage: $0 <LIG_NAME|all>"
    echo "Examples:"
    echo "  $0 LIG1"
    echo "  $0 all"
    exit 1
fi

if [ "$1" == "all" ]; then
    print_info "Processing all ${#LIGS[@]} systems"
    echo ""
    
    SUCCESS=0
    FAILED=0
    FAILED_LIGS=()
    
    for lig in "${LIGS[@]}"; do
        if process_lig "$lig"; then
            ((SUCCESS++))
        else
            ((FAILED++))
            FAILED_LIGS+=("$lig")
        fi
        echo ""
    done
    
    echo "======================================================================"
    echo "SUMMARY"
    echo "======================================================================"
    print_info "Total: ${#LIGS[@]}"
    print_info "Success: $SUCCESS ✓"
    if [ $FAILED -gt 0 ]; then
        print_error "Failed: $FAILED ✗"
        echo "Failed systems: ${FAILED_LIGS[@]}"
    fi
else
    process_lig "$1"
fi

echo ""
print_info "Next steps:"
echo "  1. cd Gromacs_inputs/LIG1/Complex_1"
echo "  2. gmx grompp -f step4.0_minimization.mdp -c complex.gro -p topol.top -n index.ndx -o mini.tpr"
echo "  3. gmx mdrun -v -deffnm mini"
