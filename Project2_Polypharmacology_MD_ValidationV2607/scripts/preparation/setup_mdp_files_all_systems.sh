#!/bin/bash
# Copy refined MDP files to all 11 working systems

# Don't exit on error - we want to process all systems
# set -e

LIGS=(LIG1 LIG2 LIG5 LIG7 LIG8 LIG9 LIG10 LIG14 LIG15 LIG16 LIG17)

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║         Setup Refined MDP Files for All Production Systems        ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if mdp_templates directory exists
if [ ! -d "mdp_templates" ]; then
    echo "❌ mdp_templates directory not found!"
    echo "   Expected: mdp_templates/step4.1_equilibration_nvt.mdp"
    echo "             mdp_templates/step4.2_equilibration_npt.mdp"
    echo "             mdp_templates/step5_production_10ns.mdp"
    exit 1
fi

echo "📋 MDP files to deploy:"
echo "  • step4.0_minimization.mdp (already exists)"
echo "  • step4.1_equilibration_nvt.mdp (NEW - extended to 1 ns)"
echo "  • step4.2_equilibration_npt.mdp (NEW - pressure equilibration)"
echo "  • step5_production_10ns.mdp (NEW - 10 ns production)"
echo ""

SUCCESS=0
TOTAL=${#LIGS[@]}

for lig in "${LIGS[@]}"; do
    LIG_NUM=${lig#LIG}
    COMPLEX_DIR="Gromacs_inputs/${lig}/Complex_${LIG_NUM}"
    
    echo -n "Setting up $lig... "
    
    if [ ! -d "$COMPLEX_DIR" ]; then
        echo -e "${YELLOW}SKIP${NC} (directory not found)"
        continue
    fi
    
    # Backup old equilibration file if it exists
    if [ -f "$COMPLEX_DIR/step4.1_equilibration.mdp" ]; then
        mv "$COMPLEX_DIR/step4.1_equilibration.mdp" \
           "$COMPLEX_DIR/step4.1_equilibration.mdp.old"
    fi
    
    # Copy new MDP files
    cp mdp_templates/step4.1_equilibration_nvt.mdp "$COMPLEX_DIR/"
    cp mdp_templates/step4.2_equilibration_npt.mdp "$COMPLEX_DIR/"
    cp mdp_templates/step5_production_10ns.mdp "$COMPLEX_DIR/"
    
    echo -e "${GREEN}✓${NC}"
    ((SUCCESS++))
done

echo ""
echo "════════════════════════════════════════════════════════════════════"
echo "SUMMARY"
echo "════════════════════════════════════════════════════════════════════"
echo -e "${GREEN}Successfully updated: $SUCCESS / $TOTAL systems${NC}"
echo ""

if [ $SUCCESS -eq $TOTAL ]; then
    echo "✓ All systems ready for MD!"
    echo ""
    echo "Next steps:"
    echo "  1. Test with one system first:"
    echo "     cd Gromacs_inputs/LIG1/Complex_1"
    echo "     bash ~/path/to/run_md_system.sh"
    echo ""
    echo "  2. If successful, run all systems:"
    echo "     bash run_all_systems.sh"
    echo ""
else
    echo "⚠️  Some systems were not updated"
    echo "   Check that all Complex_* directories exist"
fi

echo "════════════════════════════════════════════════════════════════════"
