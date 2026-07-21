#!/bin/bash
# Verify all merged systems can compile with grompp

LIGS=(LIG1 LIG2 LIG3 LIG5 LIG7 LIG8 LIG9 LIG10 LIG14 LIG15 LIG16 LIG17)

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║              Verify All Systems with gmx grompp                    ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

SUCCESS=0
FAILED=0
FAILED_LIGS=()

for lig in "${LIGS[@]}"; do
    LIG_NUM=${lig#LIG}
    COMPLEX_DIR="Gromacs_inputs/${lig}/Complex_${LIG_NUM}"
    
    echo -n "Testing $lig... "
    
    cd "$COMPLEX_DIR" || continue
    
    if gmx grompp -f step4.0_minimization.mdp -c complex.gro -p topol.top -n index.ndx -o mini_test.tpr -maxwarn 100 > grompp_test.log 2>&1; then
        echo -e "${GREEN}✓${NC}"
        ((SUCCESS++))
        rm -f mini_test.tpr grompp_test.log
    else
        echo -e "${RED}✗${NC}"
        ((FAILED++))
        FAILED_LIGS+=("$lig")
        echo "  See $COMPLEX_DIR/grompp_test.log for details"
    fi
    
    cd - > /dev/null
done

echo ""
echo "======================================================================"
echo "SUMMARY"
echo "======================================================================"
echo "Total: ${#LIGS[@]}"
echo -e "${GREEN}Success: $SUCCESS ✓${NC}"
if [ $FAILED -gt 0 ]; then
    echo -e "${RED}Failed: $FAILED ✗${NC}"
    echo "Failed systems: ${FAILED_LIGS[@]}"
else
    echo ""
    echo "✓ All systems passed grompp verification!"
    echo "  Ready for energy minimization and MD simulations"
fi
