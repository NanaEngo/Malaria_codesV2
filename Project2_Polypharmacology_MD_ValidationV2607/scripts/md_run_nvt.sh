#!/bin/bash
# MD Simulation: NVT Equilibration (100 ps)
# Usage: bash scripts/md_run_nvt.sh [complex_name]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
MD_DIR="${PROJECT_DIR}/MD_systems"

COMPLEX=${1:-"all"}

nvt_equilibrate() {
    local complex_name=$1
    local system_dir="${MD_DIR}/${complex_name}"

    echo "=========================================="
    echo "NVT Equilibration: ${complex_name}"
    echo "=========================================="

    cd "${system_dir}"

    # Check required files exist
    if [[ ! -f em.gro ]]; then
        echo "  Error: em.gro not found in ${system_dir}"
        echo "  Run minimisation step first"
        return 1
    fi

    # Create NVT mdp file
    cat > nvt.mdp <<EOF
; NVT equilibration
integrator               = md
nsteps                   = 50000    ; 100 ps with 2 fs timestep
dt                       = 0.002
nstxout                  = 500      ; Save every 1 ps
nstvout                  = 500
nstenergy                = 500
nstlog                   = 500
continuation             = no
constraint_algorithm     = lincs
constraints              = h-bonds
lincs_iter               = 1
lincs_order              = 4
cutoff-scheme            = Verlet
ns_type                  = grid
nstlist                  = 10
rcoulomb                 = 1.2
rvdw                     = 1.2
coulombtype              = PME
pme_order                = 4
fourierspacing           = 0.16
tcoupl                   = V-rescale
tc-grps                  = System
tau_t                    = 0.1
ref_t                    = 300
pcoupl                   = no
gen_vel                  = yes
gen_temp                 = 300
gen_seed                 = 12345
; Position restraints on protein heavy atoms (roadmap Step 9: 1000 kJ/mol/nm^2)
define                   = -DPOSRES
EOF

    # Run NVT equilibration
    gmx grompp -f nvt.mdp -c em.gro -r em.gro -p topol.top -o nvt.tpr -maxwarn 1
    gmx mdrun -deffnm nvt -v

    echo "  NVT equilibration complete: ${complex_name}"
}

if [ "$COMPLEX" = "all" ]; then
    # FIXED: Removed duplicate 438_ATP4
    for complex in 201_DHFR 438_ATP4 164_ClpP 214_CRT; do
        if [ -d "${MD_DIR}/${complex}" ]; then
            nvt_equilibrate "$complex" || echo "  Warning: ${complex} NVT equilibration failed"
        else
            echo "  Warning: ${complex} directory not found, skipping"
        fi
    done
else
    if [ -d "${MD_DIR}/${COMPLEX}" ]; then
        nvt_equilibrate "$COMPLEX"
    else
        echo "Error: ${COMPLEX} directory not found"
        exit 1
    fi
fi

echo ""
echo "=========================================="
echo "NVT equilibration complete!"
echo "=========================================="
