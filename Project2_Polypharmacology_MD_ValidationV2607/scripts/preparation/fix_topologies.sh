#!/bin/bash
# Fix all topology files to use cgenff_params.itp instead of charmm36.itp

LIGS=(LIG1 LIG2 LIG3 LIG5 LIG7 LIG8 LIG9 LIG10 LIG14 LIG15 LIG16 LIG17)

for lig in "${LIGS[@]}"; do
    LIG_NUM=${lig#LIG}
    TOPOL="Gromacs_inputs/${lig}/Complex_${LIG_NUM}/topol.top"
    
    if [ -f "$TOPOL" ]; then
        echo "Fixing $TOPOL..."
        sed -i 's|#include "toppar/charmm36.itp"|#include "toppar/cgenff_params.itp"|g' "$TOPOL"
        echo "  ✓ Fixed"
    fi
done

echo ""
echo "All topology files updated!"
