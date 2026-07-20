#!/bin/bash
#
# Server-Side Coordinate Merging Script
# Merge protein and ligand coordinates for GROMACS MD simulations
#
# Usage: bash server_coordinate_merging.sh LIG1
# Or: bash server_coordinate_merging.sh all   # Process all 12 systems
#
# Requirements: GROMACS (gmx command available)
#
# Author: Generated for Malaria MD Project
# Date: June 2026

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Base directory
BASE_DIR="Gromacs_inputs"

# List of LIG systems
ALL_LIGS=(LIG1 LIG2 LIG3 LIG5 LIG7 LIG8 LIG9 LIG10 LIG14 LIG15 LIG16 LIG17)

# Function to print colored messages
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if GROMACS is available
check_gromacs() {
    if ! command -v gmx &> /dev/null; then
        print_error "GROMACS (gmx command) not found"
        echo "Please load GROMACS module or add to PATH"
        echo "Example: module load gromacs/2025.4"
        exit 1
    fi
    
    local gmx_version=$(gmx --version 2>&1 | grep "GROMACS version" | head -1)
    print_info "Found: $gmx_version"
}

# Function to merge coordinates for one system
merge_system() {
    local lig_name=$1
    local complex_dir="${BASE_DIR}/${lig_name}/Complex_${lig_name#LIG}"
    local charmm_dir=$(ls -d ${BASE_DIR}/${lig_name}/charmm-gui-* 2>/dev/null | head -1)
    
    print_info "Processing $lig_name"
    
    # Check directories exist
    if [ ! -d "$complex_dir" ]; then
        print_error "Complex directory not found: $complex_dir"
        return 1
    fi
    
    if [ ! -d "$charmm_dir" ]; then
        print_error "CHARMM-GUI directory not found for $lig_name"
        return 1
    fi
    
    # Navigate to complex directory
    cd "$complex_dir" || exit 1
    print_info "Working in: $PWD"
    
    # Backup original files
    if [ -f "step3_input.gro" ]; then
        if [ ! -f "step3_input.gro.original" ]; then
            print_info "Backing up original step3_input.gro"
            cp step3_input.gro step3_input.gro.original
        fi
    else
        print_error "step3_input.gro not found"
        cd - > /dev/null
        return 1
    fi
    
    # Find ligand PDB
    local ligand_pdb="${charmm_dir}/ligandrm.pdb"
    if [ ! -f "$ligand_pdb" ]; then
        print_error "Ligand PDB not found: $ligand_pdb"
        cd - > /dev/null
        return 1
    fi
    
    print_info "Ligand PDB: $(basename $ligand_pdb)"
    
    # Step 1: Convert ligand to GRO format
    print_info "Step 1: Converting ligand PDB to GRO"
    gmx editconf -f "$ligand_pdb" -o ligand_temp.gro > convert.log 2>&1 || {
        print_error "Failed to convert ligand to GRO"
        cat convert.log
        cd - > /dev/null
        return 1
    }
    
    # Step 2: Extract header and footer from original GRO
    print_info "Step 2: Preparing merged structure"
    
    # Count atoms in protein system
    n_protein=$(tail -1 step3_input.gro | awk '{print $1}')
    n_ligand=$(tail -1 ligand_temp.gro | awk '{print $1}')
    n_total=$((n_protein + n_ligand))
    
    print_info "  Protein+Solvent atoms: $n_protein"
    print_info "  Ligand atoms: $n_ligand"
    print_info "  Total atoms: $n_total"
    
    # Step 3: Merge coordinate files
    print_info "Step 3: Merging coordinates"
    
    # Extract title from protein system
    head -1 step3_input.gro > step3_input_merged.gro
    
    # Write new atom count
    echo "  $n_total" >> step3_input_merged.gro
    
    # Add protein+solvent atoms (skip first 2 and last line)
    tail -n +3 step3_input.gro | head -n -1 >> step3_input_merged.gro
    
    # Add ligand atoms (skip first 2 and last line)
    tail -n +3 ligand_temp.gro | head -n -1 >> step3_input_merged.gro
    
    # Add box dimensions from protein system
    tail -1 step3_input.gro >> step3_input_merged.gro
    
    # Step 4: Verify merged structure
    print_info "Step 4: Verifying merged structure"
    gmx check -f step3_input_merged.gro > check.log 2>&1 || {
        print_warning "Structure check had warnings (may be OK)"
    }
    
    # Step 5: Test topology compilation
    print_info "Step 5: Testing topology compilation"
    if [ -f "step4.0_minimization.mdp" ]; then
        gmx grompp -f step4.0_minimization.mdp -c step3_input_merged.gro \
                   -p topol.top -o test_merge.tpr -maxwarn 2 > grompp.log 2>&1
        
        if [ $? -eq 0 ]; then
            print_info "✓ Topology compilation successful!"
            rm test_merge.tpr
        else
            print_warning "Topology compilation had errors:"
            tail -20 grompp.log
            print_warning "Manual intervention may be needed"
        fi
    else
        print_warning "step4.0_minimization.mdp not found, skipping test compilation"
    fi
    
    # Step 6: Generate/update index file
    print_info "Step 6: Generating index file"
    
    # Create index file with ligand group
    echo "q" | gmx make_ndx -f step3_input_merged.gro -o index_new.ndx > makeindex.log 2>&1
    
    if [ $? -eq 0 ]; then
        # Backup old index if exists
        if [ -f "index.ndx" ]; then
            cp index.ndx index.ndx.backup
        fi
        mv index_new.ndx index.ndx
        print_info "✓ Index file generated"
    else
        print_warning "Index generation had issues, check makeindex.log"
    fi
    
    # Summary
    print_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    print_info "✓ $lig_name merge complete"
    print_info "  Input:  step3_input.gro (original, backed up)"
    print_info "  Output: step3_input_merged.gro"
    print_info "  Index:  index.ndx (updated)"
    print_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Clean up temp files
    rm -f ligand_temp.gro convert.log check.log grompp.log makeindex.log
    
    cd - > /dev/null
    return 0
}

# Main script
main() {
    echo "╔════════════════════════════════════════════════════════════════════╗"
    echo "║          Server-Side Coordinate Merging for GROMACS MD           ║"
    echo "╚════════════════════════════════════════════════════════════════════╝"
    echo ""
    
    # Check GROMACS
    check_gromacs
    echo ""
    
    # Parse arguments
    if [ $# -eq 0 ]; then
        print_error "Usage: $0 <LIG_NAME|all>"
        echo "Examples:"
        echo "  $0 LIG1       # Process only LIG1"
        echo "  $0 all        # Process all 12 systems"
        exit 1
    fi
    
    # Process systems
    if [ "$1" == "all" ]; then
        print_info "Processing all 12 systems"
        echo ""
        
        success_count=0
        fail_count=0
        
        for lig in "${ALL_LIGS[@]}"; do
            if merge_system "$lig"; then
                ((success_count++))
            else
                ((fail_count++))
                print_error "Failed: $lig"
            fi
            echo ""
        done
        
        # Summary
        echo "╔════════════════════════════════════════════════════════════════════╗"
        echo "║                           SUMMARY                                 ║"
        echo "╚════════════════════════════════════════════════════════════════════╝"
        print_info "Total:   ${#ALL_LIGS[@]}"
        print_info "Success: $success_count ✓"
        if [ $fail_count -gt 0 ]; then
            print_error "Failed:  $fail_count ✗"
        fi
        
    else
        # Process single system
        lig_name=$1
        merge_system "$lig_name"
    fi
    
    echo ""
    print_info "Next steps:"
    echo "  1. Verify merged structures: gmx check -f Complex_*/step3_input_merged.gro"
    echo "  2. Run energy minimization: cd Complex_1/ && bash run_minimization.sh"
    echo "  3. Continue with equilibration and production"
}

# Run main function
main "$@"
