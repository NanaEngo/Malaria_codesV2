#!/bin/bash
# MD Simulation: NPT Equilibration (500 ps)
# Usage: bash scripts/md_run_npt.sh [complex_name]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
MD_DIR="${PROJECT_DIR}/MD_systems"

COMPLEX=${1:-"all"}

npt_equilibrate() {
    local complex_name=$1
    local system_dir="${MD_DIR}/${complex_name}"

    echo "=========================================="
    echo "NPT Equilibration: ${complex_name}"
    echo "=========================================="

    cd "${system_dir}"

    # Check required files exist
    if [[ ! -f nvt.gro ]]; then
        echo "  Error: nvt.gro not found in ${system_dir}"
        echo "  Run NVT equilibration step first"
        return 1
    fi
    if [[ ! -f nvt.cpt ]]; then
        echo "  Error: nvt.cpt not found in ${system_dir}"
        return 1
    fi

    # Create NPT mdp file
    cat > npt.mdp <<EOF
; NPT equilibration
integrator               = md
nsteps                   = 250000   ; 500 ps with 2 fs timestep
dt                       = 0.002
nstxout                  = 1000     ; Save every 2 ps
nstvout                  = 1000
nstenergy                = 1000
nstlog                   = 1000
continuation             = yes
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
pcoupl                   = Parrinello-Rahman
pcoupltype               = isotropic
tau_p                    = 2.0
compressibility          = 4.5e-5
ref_p                    = 1.0
gen_vel                  = no
EOF

    # Run NPT equilibration
    gmx grompp -f npt.mdp -c nvt.gro -r nvt.gro -t nvt.cpt -p topol.top -o npt.tpr -maxwarn 1
    gmx mdrun -deffnm npt -v

    echo "  NPT equilibration complete: ${complex_name}"
}

if [ "$COMPLEX" = "all" ]; then
    for complex in 201_DHFR 438_ATP4 164_ClpP 214_CRT; do
        if [ -d "${MD_DIR}/${complex}" ]; then
            npt_equilibrate "$complex" || echo "  Warning: ${complex} NPT equilibration failed"
        else
            echo "  Warning: ${complex} directory not found, skipping"
        fi
    done
else
    if [ -d "${MD_DIR}/${COMPLEX}" ]; then
        npt_equilibrate "$COMPLEX"
    else
        echo "Error: ${COMPLEX} directory not found"
        exit 1
    fi
fi

echo ""
echo "=========================================="
echo "NPT equilibration complete!"
echo "=========================================="
