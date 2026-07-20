"""
MD Simulation: EM → NVT → NPT Pipeline

Runs energy minimization, NVT, and NPT equilibration for all complexes.

Usage:
    python scripts/md_run_em_nvt_npt.py [--complex NAME]
"""

import os
import sys
import subprocess
from pathlib import Path
import argparse

# ── GROMACS paths ────────────────────────────────────────────────────────────
GMX_MPI = "/home/nanaengo/miniforge3/envs/malaria_md/bin.AVX2_256/gmx_mpi"
GMX_CMD = GMX_MPI  # alias kept for clarity; both point to the same binary

# Set GMXLIB so GROMACS can locate force-field files at runtime
os.environ["GMXLIB"] = "/home/nanaengo/miniforge3/envs/malaria_md/share/gromacs/top"

PROJECT_DIR = Path(__file__).parent.parent
MD_DIR = PROJECT_DIR / "MD_systems"

COMPLEXES = {
    "201_PfDHFR": {"solute_resnames": ["PROA", "LIG"]},
    "438_PfATP4": {"solute_resnames": ["PROA", "LIG"]},
    "164_PfClpP": {"solute_resnames": ["PROA", "LIG"]},
    "214_PfCRT":  {"solute_resnames": ["PROA", "LIG"]},
}


def run_cmd(cmd, cwd=None):
    print("  $ %s" % cmd)
    r = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        print("  STDERR: %s" % r.stderr[-500:])
        raise RuntimeError("Failed: %s" % cmd)
    return r


def create_em_mdp(complex_dir):
    mdp = complex_dir / "em.mdp"
    mdp.write_text("""; Energy Minimization
integrator              = steep
emtol                   = 1000.0
emstep                  = 0.01
nsteps                  = 50000
nstlist                 = 10
cutoff-scheme           = Verlet
rlist                   = 1.2
vdwtype                 = Cut-off
vdw-modifier            = Force-switch
rvdw_switch             = 1.0
rvdw                    = 1.2
coulombtype             = PME
rcoulomb                = 1.2
constraints             = none
""")
    return mdp


def create_nvt_mdp(complex_dir):
    mdp = complex_dir / "nvt.mdp"
    mdp.write_text("""; NVT Equilibration (1 ns)
define                  = -DPOSRES
integrator              = md
dt                      = 0.002
nsteps                  = 500000
nstxout-compressed      = 5000
nstxout                 = 0
nstvout                 = 0
nstfout                 = 0
nstcalcenergy           = 100
nstenergy               = 1000
nstlog                  = 1000
cutoff-scheme           = Verlet
nstlist                 = 20
rlist                   = 1.2
vdwtype                 = Cut-off
vdw-modifier            = Force-switch
rvdw_switch             = 1.0
rvdw                    = 1.2
coulombtype             = PME
rcoulomb                = 1.2
tcoupl                  = v-rescale
tc_grps                 = System
tau_t                   = 1.0
ref_t                   = 310.15
pcoupl                  = no
constraints             = h-bonds
constraint_algorithm    = LINCS
continuation            = no
nstcomm                 = 100
comm_mode               = linear
gen-vel                 = yes
gen-temp                = 310.15
gen-seed                = -1
""")
    return mdp


def create_npt_mdp(complex_dir):
    mdp = complex_dir / "npt.mdp"
    mdp.write_text("""; NPT Equilibration (1 ns)
define                  = -DPOSRES
integrator              = md
dt                      = 0.002
nsteps                  = 500000
nstxout-compressed      = 5000
nstxout                 = 0
nstvout                 = 0
nstfout                 = 0
nstcalcenergy           = 100
nstenergy               = 1000
nstlog                  = 1000
cutoff-scheme           = Verlet
nstlist                 = 20
rlist                   = 1.2
vdwtype                 = Cut-off
vdw-modifier            = Force-switch
rvdw_switch             = 1.0
rvdw                    = 1.2
coulombtype             = PME
rcoulomb                = 1.2
tcoupl                  = v-rescale
tc_grps                 = System
tau_t                   = 1.0
ref_t                   = 310.15
pcoupl                  = C-rescale
pcoupltype              = isotropic
tau_p                   = 5.0
compressibility         = 4.5e-5
ref_p                   = 1.0
constraints             = h-bonds
constraint_algorithm    = LINCS
continuation            = yes
nstcomm                 = 100
comm_mode               = linear
""")
    return mdp


def run_complex(complex_name):
    cdir = MD_DIR / complex_name
    print("\n%s" % ("=" * 60))
    print("Running EM → NVT → NPT for: %s" % complex_name)
    print("=" * 60)

    ions_gro = cdir / "ions.gro"

    if not ions_gro.exists():
        print("  SKIP: %s not found" % ions_gro)
        return False

    # Create MDP files
    em_mdp  = create_em_mdp(cdir)
    nvt_mdp = create_nvt_mdp(cdir)
    npt_mdp = create_npt_mdp(cdir)

    # === ENERGY MINIMIZATION ===
    print("\n--- Step 1: Energy Minimization ---")
    em_gro = cdir / "em.gro"

    run_cmd(
        "%s grompp -f em.mdp -c ions.gro -p topol.top -o em.tpr -maxwarn 5" % GMX_MPI,
        cwd=str(cdir),
    )
    run_cmd(
        "%s mdrun -deffnm em -v -ntomp 8" % GMX_MPI,
        cwd=str(cdir),
    )

    if not em_gro.exists():
        print("  ERROR: EM failed for %s" % complex_name)
        return False

    run_cmd(
        'echo "10" | %s energy -f em.edr -o em_potential.xvg' % GMX_MPI,
        cwd=str(cdir),
    )
    print("  EM completed successfully")

    # === NVT EQUILIBRATION ===
    print("\n--- Step 2: NVT Equilibration (1 ns) ---")
    nvt_gro = cdir / "nvt.gro"

    run_cmd(
        "%s grompp -f nvt.mdp -c em.gro -r em.gro -p topol.top -o nvt.tpr -maxwarn 5" % GMX_MPI,
        cwd=str(cdir),
    )
    run_cmd(
        "%s mdrun -deffnm nvt -v -ntomp 8" % GMX_MPI,
        cwd=str(cdir),
    )

    if not nvt_gro.exists():
        print("  ERROR: NVT failed for %s" % complex_name)
        return False
    print("  NVT completed successfully")

    # === NPT EQUILIBRATION ===
    print("\n--- Step 3: NPT Equilibration (1 ns) ---")
    npt_gro = cdir / "npt.gro"

    run_cmd(
        "%s grompp -f npt.mdp -c nvt.gro -r nvt.gro -t nvt.cpt -p topol.top -o npt.tpr -maxwarn 5" % GMX_MPI,
        cwd=str(cdir),
    )
    run_cmd(
        "%s mdrun -deffnm npt -v -ntomp 8 -nb gpu -pme gpu" % GMX_MPI,
        cwd=str(cdir),
    )

    if not npt_gro.exists():
        print("  ERROR: NPT failed for %s" % complex_name)
        return False
    print("  NPT completed successfully")

    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--complex", default="all")
    args = parser.parse_args()

    if args.complex == "all":
        results = {}
        for name in COMPLEXES:
            try:
                results[name] = run_complex(name)
            except Exception as e:
                print("  ERROR: %s" % e)
                results[name] = False

        print("\n%s" % ("=" * 60))
        print("Results:")
        for name, ok in results.items():
            print("  %s: %s" % (name, "OK" if ok else "FAILED"))
    else:
        run_complex(args.complex)


if __name__ == "__main__":
    main()
