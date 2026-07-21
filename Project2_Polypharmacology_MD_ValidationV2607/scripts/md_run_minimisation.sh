#!/bin/bash
# MD Simulation: Energy Minimisation
# Usage: bash scripts/md_run_minimisation.sh [complex_name]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
MD_DIR="${PROJECT_DIR}/MD_systems"

COMPLEX=${1:-"all"}

minimise_system() {
    local complex_name=$1
    local system_dir="${MD_DIR}/${complex_name}"

    echo "==========================================" 
    echo "Minimising: ${complex_name}"
    echo "=========================================="

    cd "${system_dir}"

    # Accept ions.gro (post-neutralisation) or solvated.gro (pre-ion addition)
    local input_gro
    if [[ -f ions.gro ]]; then
        input_gro="ions.gro"
    elif [[ -f solvated.gro ]]; then
        input_gro="solvated.gro"
    else
        echo "  Error: neither ions.gro nor solvated.gro found in ${system_dir}"
        echo "  Run complex building step (including add_ions.sh) first"
        return 1
    fi
    echo "  Using input structure: ${input_gro}"

    if [[ ! -f topol.top ]]; then
        echo "  Error: topol.top not found in ${system_dir}"
        return 1
    fi

    # Two-stage minimisation: 25000 steep + 25000 CG = 50000 total steps
    # Roadmap Step 9: 50000 steps, Fmax < 1000 kJ/mol/nm
    cat > minim.mdp <<EOF
; Energy minimisation - Stage 1: Steepest Descent
integrator  = steep
emtol       = 1000.0
emstep      = 0.01
nsteps      = 25000
nstlist     = 1
cutoff-scheme = Verlet
ns_type     = grid
coulombtype = PME
rcoulomb    = 1.0
rvdw        = 1.0
constraints = h-bonds
EOF

    # Run stage 1
    echo "  Stage 1: Steepest descent minimisation..."
    gmx grompp -f minim.mdp -c "${input_gro}" -p topol.top -o em_steep.tpr -maxwarn 1
    gmx mdrun -deffnm em_steep -v

    # Create stage 2 mdp file
    cat > minim_cg.mdp <<EOF
; Energy minimisation - Stage 2: Conjugate Gradient
integrator  = cg
emtol       = 100.0
emstep      = 0.01
nsteps      = 25000
nstlist     = 1
cutoff-scheme = Verlet
ns_type     = grid
coulombtype = PME
rcoulomb    = 1.0
rvdw        = 1.0
constraints = h-bonds
EOF

    # Run stage 2
    echo "  Stage 2: Conjugate gradient minimisation..."
    gmx grompp -f minim_cg.mdp -c em_steep.gro -p topol.top -o em.tpr -maxwarn 1
    gmx mdrun -deffnm em -v

    # Clean up intermediate files
    rm -f em_steep.tpr em_steep.trr em_steep.edr em_steep.log
    rm -f minim_cg.mdp

    echo "  Minimisation complete: ${complex_name}"
}

if [ "$COMPLEX" = "all" ]; then
    for complex in 201_DHFR 438_ATP4 164_ClpP 214_CRT; do
        if [ -d "${MD_DIR}/${complex}" ]; then
            minimise_system "$complex" || echo "  Warning: ${complex} minimisation failed"
        else
            echo "  Warning: ${complex} directory not found, skipping"
        fi
    done
else
    if [ -d "${MD_DIR}/${COMPLEX}" ]; then
        minimise_system "$COMPLEX"
    else
        echo "Error: ${COMPLEX} directory not found"
        exit 1
    fi
fi

echo ""
echo "=========================================="
echo "Minimisation complete!"
echo "=========================================="
