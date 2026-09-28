#!/bin/bash
# Canonical-policy MD witness for the repaired PfCRT model (CHARMM36m/TIP3P).
# Solvates the repaired structure, adds ions, and runs EM + short NVT + short
# NPT to demonstrate technical stability under the P2 canonical protocol.
# This is a technical stability witness only: no production MD, no
# binding/affinity/RRS/Set-C claim.
set -eo pipefail
cd /home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607
set +u
source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate malaria_md
set -u
GMX=/home/nanaengo/miniforge3/envs/malaria_md/bin/gmx_mpi

ROOT=/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607
WORK="${1:-$ROOT/results/md_systems/pfcrt_md_witness_20260818}"
INPUT="${2:-$ROOT/results/md_systems/pfcrt_gromacs_check_20260818/model_repaired.pdb}"
mkdir -p "$WORK"
cd "$WORK"
cp -a "$ROOT/results/md_systems/pfcrt_gromacs_check_20260818/charmm36-jul2022.ff" . 2>/dev/null || cp -a "$ROOT/results/md_systems/set_c_preparation_20260812_v1/PP-01_PfDHFR_WT/charmm36-jul2022.ff" .

# ---- pdb2gmx (canonical flags) ----
echo "1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1" | "$GMX" pdb2gmx -f "$INPUT" -o protein.gro -p topol.top -i posre.itp -water tip3p -ff charmm36-jul2022 -ignh -ter > step1_pdb2gmx.out 2>&1

# ---- solvate ----
cp ../pfcrt_gromacs_check_20260818/em.mdp . 2>/dev/null || printf 'integrator = steep\nnsteps = 100\nemtol = 1000\nemstep = 0.01\nnstlist = 10\ncutoff-scheme = Verlet\nrlist = 1.2\nrcoulomb = 1.2\nrvdw = 1.2\ncoulombtype = PME\npme_order = 4\nfourierspacing = 0.16\nconstraints = none\n' > em.mdp
printf 'integrator = md\nnsteps = 50000\ndt = 0.002\nnstxout-compressed = 1000\nnstenergy = 500\nnstlog = 500\ncontinuation = no\nconstraints = h-bonds\nconstraint_algorithm = lincs\nlincs_iter = 1\nlincs_order = 4\ncutoff-scheme = Verlet\nnstlist = 10\nrlist = 1.2\nrcoulomb = 1.2\nrvdw = 1.2\ncoulombtype = PME\npme_order = 4\nfourierspacing = 0.16\ntcoupl = V-rescale\ntc-grps = System\ntau_t = 0.1\nref_t = 310.15\ngen_vel = yes\ngen_temp = 310.15\n' > nvt.mdp
printf 'integrator = md\nnsteps = 50000\ndt = 0.002\nnstxout-compressed = 1000\nnstenergy = 500\nnstlog = 500\ncontinuation = yes\nconstraints = h-bonds\nconstraint_algorithm = lincs\nlincs_iter = 1\nlincs_order = 4\ncutoff-scheme = Verlet\nnstlist = 10\nrlist = 1.2\nrcoulomb = 1.2\nrvdw = 1.2\ncoulombtype = PME\npme_order = 4\nfourierspacing = 0.16\ntcoupl = V-rescale\ntc-grps = System\ntau_t = 0.1\nref_t = 310.15\npcoupl = Parrinello-Rahman\npcoupltype = isotropic\ntau_p = 2.0\ncompressibility = 4.5e-5\nref_p = 1.0\ngen_vel = no\n' > npt.mdp

# ---- grompp + EM (in vacuo first? No: solvate first) ----
# Solvate the box
printf '1\n' | "$GMX" editconf -f protein.gro -o box.gro -c -d 1.0 -bt cubic > step2_editconf.out 2>&1
printf '1\n' | "$GMX" solvate -cp box.gro -cs spc216.gro -o solv.gro -p topol.top > step3_solvate.out 2>&1
# Add ions (neutralize)
printf '15\n' | "$GMX" grompp -f em.mdp -c solv.gro -p topol.top -o ions.tpr -maxwarn 2 > step4_grompp_ions.out 2>&1
printf '13\n' | "$GMX" genion -s ions.tpr -o solv_ions.gro -p topol.top -pname NA -nname CL -neutral -conc 0.15 > step5_genion.out 2>&1

# ---- EM ----
printf '1\n' | "$GMX" grompp -f em.mdp -c solv_ions.gro -p topol.top -o em.tpr -maxwarn 2 > step6_grompp_em.out 2>&1
"$GMX" mdrun -s em.tpr -deffnm em -nb cpu -pme cpu -bonded cpu -update cpu -ntomp 8 -pin off > step7_em.out 2>&1

# ---- NVT ----
printf '1\n' | "$GMX" grompp -f nvt.mdp -c em.gro -r em.gro -p topol.top -o nvt.tpr -maxwarn 2 > step8_grompp_nvt.out 2>&1
"$GMX" mdrun -s nvt.tpr -deffnm nvt -nb cpu -pme cpu -bonded cpu -update cpu -ntomp 8 -pin off > step9_nvt.out 2>&1

# ---- NPT ----
printf '1\n' | "$GMX" grompp -f npt.mdp -c nvt.gro -t nvt.cpt -r nvt.gro -p topol.top -o npt.tpr -maxwarn 2 > step10_grompp_npt.out 2>&1
"$GMX" mdrun -s npt.tpr -deffnm npt -nb cpu -pme cpu -bonded cpu -update cpu -ntomp 8 -pin off > step11_npt.out 2>&1

echo "=== WITNESS COMPLETE ==="
ls -la em.gro nvt.gro npt.gro npt.cpt npt.edr npt.log 2>/dev/null
