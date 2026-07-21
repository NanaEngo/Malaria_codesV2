#!/bin/bash
# MD Simulation: Production MD (100 ns × 3 replicates)
# Usage: bash scripts/md_run_production.sh [complex_name] [GPU_ID]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
MD_DIR="${PROJECT_DIR}/MD_systems"

COMPLEX=${1:-"all"}
GPU_ID=${2:-"auto"}  # auto-detect GPU or specify ID
REPLICATES=3
# Duration: WT systems=200 ns, mutant systems=100 ns (roadmap Step 10)
PRODUCTION_NS_WT=200
PRODUCTION_NS_MUT=100
DT=0.002  # 2 fs timestep
NSTEPS_WT=$((PRODUCTION_NS_WT * 1000000 / 2))   # steps for 200 ns
NSTEPS_MUT=$((PRODUCTION_NS_MUT * 1000000 / 2)) # steps for 100 ns

run_production() {
    local complex_name=$1
    local system_dir="${MD_DIR}/${complex_name}"

    echo "=========================================="
    echo "Production MD: ${complex_name}"
    # WT systems run 200 ns; mutant systems run 100 ns
    if [[ "$complex_name" == *"WT"* ]] || [[ "$complex_name" == *"DHFR"* && "$complex_name" != *"N51I"* && "$complex_name" != *"C59R"* && "$complex_name" != *"S108N"* && "$complex_name" != *"I164L"* ]]; then
        local NSTEPS=$NSTEPS_WT; local PRODUCTION_NS=$PRODUCTION_NS_WT
    else
        local NSTEPS=$NSTEPS_MUT; local PRODUCTION_NS=$PRODUCTION_NS_MUT
    fi
    echo "Duration: ${PRODUCTION_NS} ns × ${REPLICATES} replicates"
    echo "GPU: ${GPU_ID}"
    echo "=========================================="

    cd "${system_dir}"

    # Check required files exist
    if [[ ! -f npt.gro ]]; then
        echo "  Error: npt.gro not found in ${system_dir}"
        echo "  Run NPT equilibration step first"
        return 1
    fi
    if [[ ! -f npt.cpt ]]; then
        echo "  Error: npt.cpt not found in ${system_dir}"
        return 1
    fi

    # Create production mdp file
    cat > production.mdp <<EOF
; Production MD
integrator               = md
nsteps                   = ${NSTEPS}
dt                       = ${DT}
nstxout                  = 5000     ; Save coordinates every 10 ps
nstvout                  = 5000
nstenergy                = 1000     ; Save energies every 2 ps
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

    # Run replicates with different seeds
    for rep in $(seq 1 ${REPLICATES}); do
        echo "  Running replicate ${rep}/${REPLICATES}..."

        # Create replicate directory
        rep_dir="replicate_${rep}"
        mkdir -p "${rep_dir}"
        cd "${rep_dir}"

        # Copy equilibration files
        cp ../npt.gro .
        cp ../npt.cpt .
        cp ../topol.top .
        cp ../production.mdp .

        # Inject unique seed per replicate (write a fresh mdp to avoid sed spacing issues)
        local seed=$((rep * 12345))
        sed -i "s/^gen_vel.*=.*/gen_vel                  = yes/" production.mdp
        # Remove any existing gen_seed line before appending
        sed -i "/^gen_seed/d" production.mdp
        echo "gen_seed                 = ${seed}" >> production.mdp

        # Prepare and run
        gmx grompp -f production.mdp -c npt.gro -r npt.gro -t npt.cpt -p topol.top -o production.tpr -maxwarn 1

        # Run with GPU (auto-detect if needed)
        if [ "$GPU_ID" = "auto" ]; then
            gmx mdrun -deffnm production -v -gpu_id auto 2>&1 | tee production.log
        else
            gmx mdrun -deffnm production -v -gpu_id ${GPU_ID} 2>&1 | tee production.log
        fi

        cd ..
        echo "  Replicate ${rep} complete"
    done

    echo "  Production MD complete: ${complex_name}"
}

if [ "$COMPLEX" = "all" ]; then
    for complex in 201_DHFR 438_ATP4 164_ClpP 214_CRT; do
        if [ -d "${MD_DIR}/${complex}" ]; then
            run_production "$complex" || echo "  Warning: ${complex} production MD failed"
        else
            echo "  Warning: ${complex} directory not found, skipping"
        fi
    done
else
    if [ -d "${MD_DIR}/${COMPLEX}" ]; then
        run_production "$COMPLEX"
    else
        echo "Error: ${COMPLEX} directory not found"
        exit 1
    fi
fi

echo ""
echo "=========================================="
echo "Production MD complete!"
echo "=========================================="
