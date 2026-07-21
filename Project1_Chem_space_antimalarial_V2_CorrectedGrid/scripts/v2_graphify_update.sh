#!/bin/bash
# Update knowledge graph after code changes
# Usage: bash scripts/v2_graphify_update.sh
V2DIR="/home/nanaengo/Malaria_codesV2/Project1_Chem_space_antimalarial_V2_CorrectedGrid"
echo "Updating graphify for V2 Corrected Grid..."
graphify "$V2DIR/scripts" --code-only 2>&1 | grep -E "(wrote|error|found)"
echo "Done."
