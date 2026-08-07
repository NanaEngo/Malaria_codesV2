#!/bin/bash
# ==============================================================================
# rebuild_438_complex_md.sh
#
# Rebuild the 438_PfATP4 MD complex using the new Vina pose from
# exhaustiveness=128 docking and run a full MD cycle to check if
# the +473 kcal/mol clash resolves.
#
# Usage:
#   sbatch rebuild_438_complex_md.sh
#   bash rebuild_438_complex_md.sh
# ==============================================================================

#SBATCH --job-name=rebuild_438
#SBATCH --output=rebuild_438_%j.out
#SBATCH --error=rebuild_438_%j.err
#SBATCH --mem=32G
#SBATCH --time=12:00:00
#SBATCH --cpus-per-task=8

# Note: deliberately avoiding -u because GROMACS GMXRC sources scripts
# that reference unbound variables, which would cause immediate exit with -u.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=md_execution_guard.sh
source "${SCRIPT_DIR}/md_execution_guard.sh"
md_guard_parse "$@" || { echo "Usage: $0 [--dry-run|--execute]" >&2; exit 64; }
if [[ "$MD_GUARD_EXECUTE" != "1" ]]; then
    md_guard_print_plan "rebuild_438_complex_md.sh" "rebuild 438-PfATP4 pose and run a fresh validation trajectory"
    exit 0
fi
md_guard_require_authorization || exit $?
md_guard_check_parent_system "438_ATP4"

# A fresh 438 rerun is permitted only after a validated, internally consistent
# force-field manifest exists. The historical GAFF2/CHARMM36 setup is not
# silently upgraded or treated as publication-grade.

# ===== Configuration =====
PROJECT_DIR="/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607"
SYS_DIR="$PROJECT_DIR/MD_systems/438_PfATP4"
RESULTS_DIR="$PROJECT_DIR/results/redock_438"
WORK_DIR="$SYS_DIR/rebuild_test"
GMX_BIN="${P2_GMX_BIN:-gmx}"
BINDING_CENTER="134.84,133.10,97.63"

# Source conda
if [ -z "${CONDA_DEFAULT_ENV:-}" ] || [ "$CONDA_DEFAULT_ENV" != "malaria_md" ]; then
    if [ -f /home/nanaengo/miniforge3/etc/profile.d/conda.sh ]; then
        source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
        conda activate malaria_md
    fi
fi
export LD_LIBRARY_PATH="/home/nanaengo/miniforge3/envs/malaria_md/lib:${LD_LIBRARY_PATH:-}"
# Suppress Open MPI warnings about fork()
export OMPI_MCA_mpi_warn_on_fork=0
export OMPI_MCA_orte_base_help_aggregate=0
export OMPI_MCA_plm=isolated

echo "=============================================="
echo "  Rebuild 438_PfATP4 MD Complex"
echo "  Date: $(date)"
echo "  Conda: ${CONDA_DEFAULT_ENV:-NONE}"
echo "=============================================="
echo ""

mkdir -p "$WORK_DIR"
md_guard_validate_forcefield_manifest "$SYS_DIR"

# ===== Step 1: Check new pose =====
echo "=== Step 1: Checking new Vina pose ==="
if [ ! -f "$RESULTS_DIR/best_pose1.pdb" ]; then
    echo "  ERROR: Vina best pose not found at $RESULTS_DIR/best_pose1.pdb"
    exit 1
fi
N_ATOMS=$(grep -c "^HETATM\|^ATOM" "$RESULTS_DIR/best_pose1.pdb" || echo 0)
echo "  ✅ Best pose PDB: $RESULTS_DIR/best_pose1.pdb ($N_ATOMS atoms)"
echo ""

# ===== Step 2: Create new ligand GRO at binding site =====
echo "=== Step 2: Creating new ligand GRO at binding site ==="

# Export paths for Python
export VINA_PDB="$RESULTS_DIR/best_pose1.pdb"
export LIGAND_GRO_OUT="$WORK_DIR/ligand_438_new.gro"
export ACPYPE_GRO="$SYS_DIR/ligand/ligand_438.acpype/ligand_438_GMX.gro"
export CX="134.84" CY="133.10" CZ="97.63"

python3 << 'PYEOF'
import os, sys
import numpy as np
from pathlib import Path

vina_pdb = Path(os.environ["VINA_PDB"])
output_gro = Path(os.environ["LIGAND_GRO_OUT"])
acpype_gro = Path(os.environ.get("ACPYPE_GRO", ""))
cx, cy, cz = float(os.environ["CX"]), float(os.environ["CY"]), float(os.environ["CZ"])
binding_center = np.array([cx, cy, cz])

# Read Vina coordinates
coords = []
with open(vina_pdb) as f:
    for line in f:
        if line.startswith(("HETATM", "ATOM")):
            x = float(line[30:38])
            y = float(line[38:46])
            z = float(line[46:54])
            coords.append([x, y, z])

coords = np.array(coords)
n_atoms = len(coords)
print(f"  Read {n_atoms} atoms from Vina pose")

# Compute centroid and shift to binding center
centroid = np.mean(coords, axis=0)
shift = binding_center - centroid
coords_shifted = coords + shift
print(f"  Centroid: [{centroid[0]:.3f}, {centroid[1]:.3f}, {centroid[2]:.3f}]")
print(f"  Shift:    [{shift[0]:.3f}, {shift[1]:.3f}, {shift[2]:.3f}]")

# Get atom names from ACPYPE reference GRO (preserves topology compatibility)
ref_atom_names = []
ref_resname = "LIG"
if acpype_gro.exists():
    with open(acpype_gro) as f:
        lines = f.read().splitlines()
    n_ref = int(lines[1].strip()) if len(lines) > 1 else 0
    ref_atom_lines = lines[2:2+n_ref] if n_ref > 0 else []
    if ref_atom_lines:
        ref_resname = ref_atom_lines[0][5:10].strip()
    for al in ref_atom_lines:
        ref_atom_names.append(al[10:15].strip())
    print(f"  Using {len(ref_atom_names)} atom names from {acpype_gro.name}")
    print(f"  Residue name: {ref_resname}")
else:
    print(f"  WARNING: ACPYPE GRO not found at {acpype_gro}")
    print(f"  Generating generic atom names")
    ref_atom_names = [f"C{i+1}" for i in range(n_atoms)]

# Pad/truncate atom names to match
while len(ref_atom_names) < n_atoms:
    ref_atom_names.append(f"C{len(ref_atom_names)+1}")
ref_atom_names = ref_atom_names[:n_atoms]

# Write corrected GRO file
with open(output_gro, "w") as f:
    f.write("Ligand 438 (Vina pose, shifted to binding site)\n")
    f.write(f"{n_atoms:5d}\n")
    for i, (x, y, z) in enumerate(coords_shifted):
        x_nm = x / 10.0
        y_nm = y / 10.0
        z_nm = z / 10.0
        f.write(f"{1:5d}{ref_resname:5s}{ref_atom_names[i]:>5s}{i+1:5d}{x_nm:8.3f}{y_nm:8.3f}{z_nm:8.3f}\n")
    f.write(f"{10.0:10.5f}{10.0:10.5f}{10.0:10.5f}\n")

print(f"  Written: {output_gro} ({n_atoms} atoms)")

# Verify RMSD vs old ACPYPE pose
old_gro = acpype_gro
if old_gro.exists():
    old_coords = []
    with open(old_gro) as f:
        lines = f.read().splitlines()
    n_old = int(lines[1].strip()) if len(lines) > 1 else 0
    old_lines = lines[2:2+n_old] if n_old > 0 else []
    for al in old_lines:
        try:
            x = float(al[20:28]) * 10.0
            y = float(al[28:36]) * 10.0
            z = float(al[36:44]) * 10.0
            old_coords.append([x, y, z])
        except (ValueError, IndexError):
            pass
    old_coords = np.array(old_coords)
    if len(old_coords) == len(coords_shifted):
        rmsd = np.sqrt(np.mean(np.sum((old_coords - coords_shifted)**2, axis=1)))
        print(f"  RMSD vs old ACPYPE pose: {rmsd:.3f} Angstrom")
PYEOF
echo ""

# ===== Step 3: Setup topology =====
echo "=== Step 3: Setting up topology ==="
cp "$SYS_DIR/topol.top" "$WORK_DIR/topol.top"
if [ -f "$SYS_DIR/ligand_438.itp" ]; then
    cp "$SYS_DIR/ligand_438.itp" "$WORK_DIR/"
    echo "  ✅ Copied topol.top and ligand_438.itp"
else
    echo "  ✅ Copied topol.top"
fi
echo ""

# ===== Step 4: Create complex =====
echo "=== Step 4: Merging protein + new ligand ==="
PROTEIN_GRO="$SYS_DIR/protein_processed.gro"
if [ ! -f "$PROTEIN_GRO" ]; then
    PROTEIN_GRO="$SYS_DIR/protein_processed_new.gro"
fi
if [ ! -f "$PROTEIN_GRO" ]; then
    echo "  ERROR: No protein GRO found"
    exit 1
fi
echo "  Protein: $PROTEIN_GRO"
echo "  Ligand:  $WORK_DIR/ligand_438_new.gro"

"$GMX_BIN" editconf -f "$PROTEIN_GRO" -o "$WORK_DIR/protein.pdb"
"$GMX_BIN" editconf -f "$WORK_DIR/ligand_438_new.gro" -o "$WORK_DIR/ligand.pdb"

# Combine
{
    cat "$WORK_DIR/protein.pdb"
    echo "TER"
    grep "^HETATM\|^ATOM" "$WORK_DIR/ligand.pdb"
    echo "END"
} > "$WORK_DIR/complex.pdb"
echo "  Complex PDB: $(wc -l < "$WORK_DIR/complex.pdb") lines"
echo ""

# ===== Step 5: Simulation box =====
echo "=== Step 5: Creating simulation box ==="
"$GMX_BIN" editconf -f "$WORK_DIR/complex.pdb" -o "$WORK_DIR/complex_boxed.gro" \
    -c -d 1.2 -bt dodecahedron
echo ""

# ===== Step 6: Solvate =====
echo "=== Step 6: Solvating ==="
"$GMX_BIN" solvate -cp "$WORK_DIR/complex_boxed.gro" -cs spc216.gro \
    -o "$WORK_DIR/solvated.gro" -p "$WORK_DIR/topol.top"
echo ""

# ===== Step 7: Add ions =====
echo "=== Step 7: Adding ions ==="
cat > "$WORK_DIR/ions.mdp" << 'EOF'
; Ions mdp
integrator = steep
emtol = 1000.0
emstep = 0.01
nsteps = 50000
EOF

"$GMX_BIN" grompp -f "$WORK_DIR/ions.mdp" -c "$WORK_DIR/solvated.gro" \
    -p "$WORK_DIR/topol.top" -o "$WORK_DIR/ions.tpr"

# Fix: use OMPI_MCA_plm=isolated to prevent Open MPI from killing genion
# Also backup topology before genion modifies it
cp "$WORK_DIR/topol.top" "$WORK_DIR/topol.top.bak"
echo "SOL" | "$GMX_BIN" genion -s "$WORK_DIR/ions.tpr" -o "$WORK_DIR/ions.gro" \
    -p "$WORK_DIR/topol.top" -pname NA -nname CL -conc 0.15 -neutral
echo ""

# ===== Step 8: Energy Minimisation =====
echo "=== Step 8: Energy Minimisation (50000 steps) ==="
cat > "$WORK_DIR/em.mdp" << 'EOF'
integrator = steep
nsteps = 50000
emtol = 1000.0
emstep = 0.01
nstxout = 100
nstenergy = 100
cutoff-scheme = Verlet
nstlist = 10
rlist = 1.0
coulombtype = PME
rcoulomb = 1.0
vdwtype = Cut-off
rvdw = 1.0
pme-order = 4
fourierspacing = 0.16
constraints = h-bonds
constraint-algorithm = LINCS
EOF

"$GMX_BIN" grompp -f "$WORK_DIR/em.mdp" -c "$WORK_DIR/ions.gro" \
    -p "$WORK_DIR/topol.top" -o "$WORK_DIR/em.tpr"

# Use cd + relative -deffnm for reliable output paths
cd "$WORK_DIR"
"$GMX_BIN" mdrun -v -s em.tpr -deffnm em \
    -ntomp 8 -gpu_id 0
cd - > /dev/null

EM_ENERGY=$(grep "Potential" "$WORK_DIR/em.log" 2>/dev/null | tail -1 | awk '{print $NF}')
echo "  Final EM energy: ${EM_ENERGY:-N/A} kJ/mol"
echo ""

# ===== Step 9: NVT Equilibration (500 ps) =====
echo "=== Step 9: NVT Equilibration (500 ps) ==="
cat > "$WORK_DIR/nvt.mdp" << 'EOF'
integrator = md
nsteps = 250000
dt = 0.002
nstxout = 500
nstvout = 500
nstenergy = 500
nstlog = 500
cutoff-scheme = Verlet
nstlist = 10
rlist = 1.0
coulombtype = PME
rcoulomb = 1.0
vdwtype = Cut-off
rvdw = 1.0
pme-order = 4
fourierspacing = 0.16
constraints = h-bonds
constraint-algorithm = LINCS
continuation = no
tcoupl = V-rescale
tc-grps = Protein Non-Protein
tau_t = 0.1 0.1
ref_t = 310.15 310.15
pcoupl = no
gen_vel = yes
gen_temp = 310.15
gen_seed = -1
EOF

"$GMX_BIN" grompp -f "$WORK_DIR/nvt.mdp" -c "$WORK_DIR/em.gro" \
    -p "$WORK_DIR/topol.top" -o "$WORK_DIR/nvt.tpr"

cd "$WORK_DIR"
"$GMX_BIN" mdrun -v -s nvt.tpr -deffnm nvt \
    -ntomp 8 -gpu_id 0
cd - > /dev/null
echo ""

# ===== Step 10: NPT Equilibration (1 ns) =====
echo "=== Step 10: NPT Equilibration (1 ns) ==="
cat > "$WORK_DIR/npt.mdp" << 'EOF'
integrator = md
nsteps = 500000
dt = 0.002
nstxout = 500
nstvout = 500
nstenergy = 500
nstlog = 500
cutoff-scheme = Verlet
nstlist = 10
rlist = 1.0
coulombtype = PME
rcoulomb = 1.0
vdwtype = Cut-off
rvdw = 1.0
pme-order = 4
fourierspacing = 0.16
constraints = h-bonds
constraint-algorithm = LINCS
continuation = yes
tcoupl = V-rescale
tc-grps = Protein Non-Protein
tau_t = 0.1 0.1
ref_t = 310.15 310.15
pcoupl = Berendsen
pcoupltype = isotropic
tau_p = 2.0
ref_p = 1.0
compressibility = 4.5e-5
gen_vel = no
EOF

"$GMX_BIN" grompp -f "$WORK_DIR/npt.mdp" -c "$WORK_DIR/nvt.gro" \
    -t "$WORK_DIR/nvt.cpt" -p "$WORK_DIR/topol.top" \
    -o "$WORK_DIR/npt.tpr"

cd "$WORK_DIR"
"$GMX_BIN" mdrun -v -s npt.tpr -deffnm npt \
    -ntomp 8 -gpu_id 0
cd - > /dev/null
echo ""

# ===== Step 11: Production MD (2 ns diagnostic only) =====
echo "=== Step 11: Production MD (2 ns diagnostic only) ==="
cat > "$WORK_DIR/md_prod.mdp" << 'EOF'
integrator = md
nsteps = 1000000
dt = 0.002
nstxout = 1000
nstvout = 1000
nstenergy = 1000
nstlog = 1000
nstxout-compressed = 100
cutoff-scheme = Verlet
nstlist = 10
rlist = 1.0
coulombtype = PME
rcoulomb = 1.0
vdwtype = Cut-off
rvdw = 1.0
pme-order = 4
fourierspacing = 0.16
constraints = h-bonds
constraint-algorithm = LINCS
continuation = yes
tcoupl = V-rescale
tc-grps = Protein Non-Protein
tau_t = 0.1 0.1
ref_t = 310.15 310.15
pcoupl = Parrinello-Rahman
pcoupltype = isotropic
tau_p = 2.0
ref_p = 1.0
compressibility = 4.5e-5
gen_vel = no
EOF

"$GMX_BIN" grompp -f "$WORK_DIR/md_prod.mdp" -c "$WORK_DIR/npt.gro" \
    -t "$WORK_DIR/npt.cpt" -p "$WORK_DIR/topol.top" \
    -o "$WORK_DIR/md_prod.tpr"

cd "$WORK_DIR"
"$GMX_BIN" mdrun -v -s md_prod.tpr -deffnm md_prod \
    -ntomp 8 -gpu_id 0
cd - > /dev/null
echo ""

# ===== Step 12: MM-GBSA Analysis =====
echo "=== Step 12: MM-GBSA Analysis ==="
if command -v gmx_MMPBSA >/dev/null 2>&1; then
    cat > "$WORK_DIR/mmpbsa.in" << 'EOF'
&general
  sys_name="438_PfATP4_rebuild"
  startframe=1
  endframe=10
  interval=10
/
&gb
  igb=2
  saltcon=0.150
/
EOF

    echo "  Running gmx_MMPBSA..."
    gmx_MMPBSA -O -i "$WORK_DIR/mmpbsa.in" \
        -o "$WORK_DIR/FINAL_RESULTS_MMPBSA_rebuild.dat" \
        -sp "$WORK_DIR/md_prod.tpr" \
        -cp "$WORK_DIR/topol.top" \
        -nogui
    [[ -s "$WORK_DIR/FINAL_RESULTS_MMPBSA_rebuild.dat" ]] || {
        echo "ERROR: gmx_MMPBSA returned no validated output; refusing interpretation." >&2
        exit 1
    }
else
    echo "  ERROR: gmx_MMPBSA is unavailable; no binding-energy proxy will be substituted." >&2
    exit 1
fi
echo ""

# ===== Summary =====
echo "=============================================="
echo "  Rebuild 438_PfATP4 — COMPLETE"
echo "=============================================="
echo "  Work dir: $WORK_DIR/"
echo ""
echo "  === Key Results ==="

EM_FINAL=$(grep "Potential" "$WORK_DIR/em.log" 2>/dev/null | tail -1 | awk '{print $NF}')
echo "  EM final energy:      ${EM_FINAL:-N/A} kJ/mol"

NPT_DENSITY=$(grep "Density" "$WORK_DIR/npt.log" 2>/dev/null | tail -1 | awk '{print $NF}')
echo "  NPT final density:    ${NPT_DENSITY:-N/A} kg/m^3"

if [ -f "$WORK_DIR/FINAL_RESULTS_MMPBSA_rebuild.dat" ]; then
    MMGBSA_TOTAL=$(grep "TOTAL" "$WORK_DIR/FINAL_RESULTS_MMPBSA_rebuild.dat" 2>/dev/null | head -1 | awk '{print $NF}')
    echo "  MM-GBSA TOTAL:        ${MMGBSA_TOTAL:-N/A} kcal/mol"
else
    echo "  MM-GBSA:             N/A (not computed)"
fi
echo "  OLD MM-GBSA (clash):  +473.0 kcal/mol"
echo ""

if [ -n "${MMGBSA_TOTAL:-}" ]; then
    if (( $(echo "$MMGBSA_TOTAL < 0" | bc -l) )); then
        echo "  RESULT: Negative endpoint reported; inspect topology and convergence before interpretation."
    else
        echo "  RESULT: Non-negative endpoint; clash or non-binding remains possible."
    fi
fi
echo ""
echo "  Next step: If clash persists, use ColabFold (AF2) for"
echo "  an alternate receptor conformation of PfATP4."
echo "=============================================="
