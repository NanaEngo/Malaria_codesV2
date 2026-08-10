#!/usr/bin/env python3
"""Set-C MD preparation — OpenFF 2.2 + CHARMM36m documented workaround.

Contract deviation (recorded, never silent):
  * canonical requirement : ligand_force_field = "CGenFF" (licensed ParamChem tool)
  * implemented          : ligand_force_field = "OpenFF 2.2.0 (AM1-BCC)"
  * reason               : cgenff/cgenff_charmm2gmx is a licensed binary, not
                           installable via pip/conda (verified 2026-08-09); OpenFF
                           2.2.0 is a permissively licensed general force field
                           with AM1-BCC partial charges (AmberTools).
  * water model          : TIP3P (unchanged)
  * protein force field  : CHARMM36m (unchanged)

Every system directory carries a `forcefield_manifest.json` whose
`policy_deviation` block declares this deviation explicitly, and a
`system_manifest.json` binding candidate/target/mutation/SMILES/cohort to the
receptor, docking pose, and coordinates used.

Ligand placement: the rank-1 Vina pose from the V5 RRS pilot
(Project1 .../results/rrs_pilot/vina_scores/<TARGET_MUT>/<PP>_<TARGET>/vina_out.pdbqt)
is used as the 3D starting conformation.  RDKit distance-geometry embedding
with a coordMap pins every heavy atom exactly at the docked pose (Meeko's
`REMARK SMILES IDX` atom-mapping verified by element consistency), so the
OpenFF ligand topology and the protein share exactly the receptor coordinate
frame.

This script performs preparation only (topology + solvation + manifests).
Equilibration (EM/NVT/NPT) is a separate SLURM array that finalises the
force-field manifests with the npt.gro/npt.cpt hashes.

Usage:
    python scripts/p2_setc_prepare_openff.py --system PP-01_PfDHFR_WT
    python scripts/p2_setc_prepare_openff.py --all            # pilot 16 systems
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
RESULTS_DIR = PROJECT_DIR / "results"
SET_C_FILE = RESULTS_DIR / "candidate_selection" / "md_top20_candidates_polypharm.csv"
SYSTEM_ROOT = RESULTS_DIR / "md_systems" / "set_c"
V5_RRS = (
    Path("/home/nanaengo/Malaria_codesV2/Project1_Chem_space_antimalarial_V5_CorrectedGrid")
    / "results" / "rrs_pilot"
)
RECEPTORS = V5_RRS / "receptors"
VINA_SCORES = V5_RRS / "vina_scores"

GMX = os.environ.get("P2_GMX_BIN", "/home/nanaengo/miniforge3/envs/malaria_md/bin/gmx_mpi")
PY = sys.executable

# Receptor state -> (receptor pdb basename, vina score subdir)
RECEPTOR_MAP = {
    ("PfDHFR", "WT"): ("PfDHFR_WT.pdb", "PfDHFR_WT"),
    ("PfDHFR", "N51I"): ("PfDHFR_N51I.pdb", "PfDHFR_N51I"),
    ("PfDHFR", "C59R"): ("PfDHFR_C59R.pdb", "PfDHFR_C59R"),
    ("PfDHFR", "S108N"): ("PfDHFR_S108N.pdb", "PfDHFR_S108N"),
    ("PfDHFR", "I164L"): ("PfDHFR_I164L.pdb", "PfDHFR_I164L"),
    ("PfCRT", "WT"): ("PfCRT_WT_K76.pdb", "PfCRT_WT_K76"),
    ("PfCRT", "K76T"): ("PfCRT_K76T.pdb", "PfCRT_K76T"),
    ("PfCRT", "K76A"): ("PfCRT_K76A.pdb", "PfCRT_K76A"),
}

COHORT = "P2_SET_C_POLYPHARM_17"
PROTEIN_FF = "CHARMM36m"
LIGAND_FF = "OpenFF 2.2.0 (AM1-BCC)"
WATER_MODEL = "TIP3P"
DEVIATION = {
    "declared": True,
    "field": "ligand_force_field",
    "canonical_requirement": "CGenFF",
    "actual": LIGAND_FF,
    "reason": (
        "cgenff/cgenff_charmm2gmx is a licensed ParamChem binary not installable "
        "via pip/conda (verified 2026-08-09). OpenFF 2.2.0 (AM1-BCC via AmberTools) "
        "is used instead, with the deviation declared in every forcefield manifest. "
        "See results/set_c_md/set_c_preparation_remediation_20260809.md."
    ),
    "approved": True,
    "approval_context": "auto-approved documented workaround requested by PI 2026-08-09",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run(cmd: list[str], cwd: Path, label: str) -> None:
    result = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"{label} failed (rc={result.returncode}):\n"
            f"$ {' '.join(cmd)}\n{result.stdout[-2000:]}\n{result.stderr[-2000:]}"
        )
    return result


def parse_system_name(name: str) -> tuple[str, str, str]:
    """'PP-01_PfDHFR_WT' -> ('PP-01', 'PfDHFR', 'WT')."""
    m = re.match(r"^(PP-\d+)_(PfDHFR|PfCRT)_(.+)$", name)
    if not m:
        raise SystemExit(f"Invalid system name {name!r}; expected PP-XX_PfDHFR_<mut>")
    return m.group(1), m.group(2), m.group(3)


def load_set_c() -> dict[str, str]:
    import csv
    with SET_C_FILE.open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    out: dict[str, str] = {}
    for row in rows:
        rank = int(row["rank"])
        pid = f"PP-{rank:02d}"
        out[pid] = row["smiles"]
    return out


# --------------------------------------------------------------------------
# Ligand: OpenFF 2.2 + AM1-BCC, placed at the Vina rank-1 pose
# --------------------------------------------------------------------------
def parse_pdbqt_pose(pdbqt: Path) -> tuple[list[tuple[float, float, float]], list[str], dict[int, int]]:
    """MODEL 1 coordinates, elements, and Meeko SMILES->pdbqt atom map.

    Mapping convention (verified against real pose 2026-08-09): pairs are
    (rdkit_atom_idx_1based, pdbqt_atom_idx_1based); 24/24 element matches for
    PP-01.  Returns mapping as {rdkit_idx_0based: pdbqt_idx_0based}.
    """
    mapping: dict[int, int] = {}
    coords: list[tuple[float, float, float]] = []
    elements: list[str] = []
    in_model = False
    model_count = 0
    for line in pdbqt.read_text(errors="replace").splitlines():
        if line.startswith("MODEL"):
            model_count += 1
            in_model = model_count == 1
            continue
        if line.startswith("ENDMDL"):
            if in_model:
                break
            continue
        if line.startswith("REMARK SMILES IDX"):
            tokens = line.split()[3:]
            for i in range(0, len(tokens) - 1, 2):
                mapping[int(tokens[i]) - 1] = int(tokens[i + 1]) - 1
            continue
        if in_model and line.startswith(("ATOM", "HETATM")):
            coords.append((float(line[30:38]), float(line[38:46]), float(line[46:54])))
            name = line[12:16].strip()
            if not name:
                elements.append("?")
            elif len(name) > 1 and name[1].islower():
                elements.append(name[:2])
            else:
                elements.append(name[:1])
    if not coords:
        raise RuntimeError(f"No MODEL 1 coordinates in {pdbqt}")
    return coords, elements, mapping


def make_ligand_openff(system_dir: Path, smiles: str, pose_pdbqt: Path) -> dict:
    """Generate ligand_openff.itp/.gro at the docked pose (OpenFF 2.2 + AM1-BCC).

    The Vina docked pose contains only heavy atoms (+ a single polar H); the
    nonpolar H's were stripped during docking preparation.  Heavy atoms are
    placed EXACTLY at the rank-1 Vina pose coordinates (Meeko mapping verified
    by element consistency).  Hydrogens are then added ON the fixed heavy frame
    by Open Babel (-h, pH 7.4), which places them at geometry-consistent
    positions relative to the docked heavy atoms, and the result is written to
    an SDF (bond orders preserved).  The heavy frame is re-verified against the
    docked pose by element-matched nearest-neighbour matching (<= 0.001 nm).

    This replaces an earlier H-placement scheme that transferred bond vectors
    from an unrelated embedded conformer, which created 0.63 A intra-ligand
    overlaps and crashed EM (verified 2026-08-09).
    """
    import subprocess as _sub
    import tempfile
    import numpy as np
    from scipy.spatial import cKDTree as _cKDTree
    from openff.toolkit import Molecule
    from openff.units import unit
    from rdkit import Chem
    from rdkit.Chem import rdMolDescriptors

    pose_coords, elements, mapping = parse_pdbqt_pose(pose_pdbqt)

    ref_mol = Chem.MolFromSmiles(smiles)
    if ref_mol is None:
        raise RuntimeError(f"RDKit cannot parse SMILES: {smiles}")
    ref_mol_h = Chem.AddHs(ref_mol)
    expected_formula = rdMolDescriptors.CalcMolFormula(ref_mol_h)
    expected_heavy = sum(1 for a in ref_mol.GetAtoms() if a.GetAtomicNum() > 1)

    # element-consistency fail-fast: reject a wrong mapping before using it
    heavy_rdkit = [a.GetIdx() for a in ref_mol.GetAtoms() if a.GetAtomicNum() > 1]
    mismatches = 0
    for rk in heavy_rdkit:
        if rk in mapping and mapping[rk] < len(elements):
            if ref_mol.GetAtomWithIdx(rk).GetSymbol() != elements[mapping[rk]]:
                mismatches += 1
    if mismatches:
        raise RuntimeError(f"Meeko mapping element-mismatch for {smiles}: {mismatches} atoms")
    mapped_heavy = [rk for rk in heavy_rdkit if rk in mapping and mapping[rk] < len(pose_coords)]
    if len(mapped_heavy) < max(3, int(0.5 * len(heavy_rdkit))):
        raise RuntimeError(f"Too few mapped heavy atoms ({len(mapped_heavy)}/{len(heavy_rdkit)})")

    # 1. heavy-only PDB at the docked pose (PDBQT MODEL 1, non-H atoms)
    heavy_pdb = []
    serial = 1
    in_model, model_count = False, 0
    for line in pose_pdbqt.read_text(errors="replace").splitlines():
        if line.startswith("MODEL"):
            model_count += 1
            in_model = model_count == 1
            continue
        if line.startswith("ENDMDL"):
            if in_model:
                break
            continue
        if in_model and line.startswith(("ATOM", "HETATM")):
            name = line[12:16].strip()
            elem = name[:2] if len(name) > 1 and name[1].islower() else name[:1]
            if elem == "H":
                continue
            x, y, z = float(line[30:38]), float(line[38:46]), float(line[46:54])
            heavy_pdb.append(
                f"HETATM{serial:5d} {name:>4} LIG A   1    "
                f"{x:8.3f}{y:8.3f}{z:8.3f}{1.0:6.2f}{0.0:6.2f}          {elem:>2}")
            serial += 1
    heavy_pdb.append("END")
    heavy_path = system_dir / "ligand_heavy_dock.pdb"
    heavy_path.write_text("\n".join(heavy_pdb) + "\n", encoding="utf-8")
    if serial - 1 != expected_heavy:
        raise RuntimeError(
            f"docked heavy count {serial - 1} != SMILES heavy count {expected_heavy}")

    # 2. Open Babel: add hydrogens on the fixed heavy frame -> SDF
    sdf_path = system_dir / "ligand_docked_h.sdf"
    obabel = _sub.run(
        ["obabel", str(heavy_path), "-O", str(sdf_path), "-h", "-p", "7.4"],
        capture_output=True, text=True,
    )
    if obabel.returncode != 0:
        raise RuntimeError(f"obabel -h failed: {obabel.stderr[-500:]}")

    # 3. RDKit read SDF -> chemistry + heavy-frame verification
    rdmol = Chem.MolFromMolFile(str(sdf_path), removeHs=False)
    if rdmol is None:
        raise RuntimeError(f"RDKit cannot read obabel SDF for {smiles}")
    formula = rdMolDescriptors.CalcMolFormula(rdmol)
    if formula != expected_formula:
        raise RuntimeError(
            f"obabel H-addition formula {formula} != SMILES formula {expected_formula}")
    conf = rdmol.GetConformer()
    sdf_coords = np.array([list(conf.GetAtomPosition(i)) for i in range(rdmol.GetNumAtoms())])
    sdf_elements = [a.GetSymbol() for a in rdmol.GetAtoms()]
    heavy_mask = np.array([e != "H" for e in sdf_elements])
    sdf_heavy = sdf_coords[heavy_mask]
    sdf_heavy_elem = np.array(sdf_elements)[heavy_mask]
    pose_heavy = np.array([pose_coords[mapping[rk]] for rk in mapped_heavy])
    pose_heavy_elem = np.array([elements[mapping[rk]] for rk in mapped_heavy])

    # element-matched nearest-neighbour RMSD (obabel preserves input positions;
    # atom ORDER may differ from the PDBQT, so match by nearest same-element atom)
    deviations = []
    for xyz, elem in zip(sdf_heavy, sdf_heavy_elem):
        cand = pose_heavy[pose_heavy_elem == elem]
        if len(cand) == 0:
            raise RuntimeError(f"element {elem} present in SDF but not in pose")
        dmin = float(np.min(np.linalg.norm(cand - xyz, axis=1)))
        deviations.append(dmin)
    frame_rmsd = float(np.sqrt(np.mean(np.square(deviations))))
    if frame_rmsd > 0.001:
        raise RuntimeError(f"heavy frame drifted from docked pose: {frame_rmsd:.6f} nm")

    # 4. OpenFF molecule from the SDF-derived RDKit mol, pose preserved.
    #    The SDF title (a file path) would otherwise leak into the residue/
    #    moleculetype name ("1_tmp_...pdb", 46 chars) and corrupt the merged
    #    gro formatting; pin a short neutral name explicitly.
    rdmol.SetProp("_Name", "MOL0")
    off_mol = Molecule.from_rdkit(rdmol, allow_undefined_stereo=True)
    off_mol.name = "MOL0"
    off_mol.assign_partial_charges(partial_charge_method="am1bcc")

    # Interchange -> GROMACS top (prefix) then strip defaults/system/molecules
    from openff.interchange import Interchange
    from openff.toolkit import ForceField as OpenFFForceField

    ff = OpenFFForceField("openff-2.2.0.offxml")
    top = off_mol.to_topology()
    # GROMACS 2020+ requires box vectors even for a lone-molecule export
    box = np.eye(3) * 10.0 * unit.nanometer
    top.box_vectors = box
    inter = Interchange.from_smirnoff(force_field=ff, topology=top)
    inter.box = box
    inter.positions = off_mol.conformers[0]
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        inter.to_gromacs(prefix=str(tmp_path / "lig"))
        raw_top = (tmp_path / "lig.top").read_text(encoding="utf-8")
        raw_gro = (tmp_path / "lig.gro").read_text(encoding="utf-8")

    # keep [atomtypes]..[constraints]; drop [defaults]/[system]/[molecules] + includes
    sections: list[str] = []
    current: list[str] = []
    keep = {"[atomtypes]", "[moleculetype]", "[atoms]", "[bonds]", "[pairs]",
            "[angles]", "[dihedrals]", "[constraints]", "[settles]", "[virtual_sites2]"}
    for line in raw_top.splitlines():
        stripped = line.strip()
        if stripped.startswith("["):
            if current:
                sections.append("\n".join(current))
            current = [line]
        elif stripped.startswith("#include"):
            current = []
            continue
        else:
            if current:
                current.append(line)
    if current:
        sections.append("\n".join(current))
    kept = [s for s in sections if re.sub(r"\s+", "", s.splitlines()[0].strip()) in keep]
    if not kept:
        raise RuntimeError("No usable sections extracted from OpenFF ligand top")
    itp_text = "\n".join(kept) + "\n"

    (system_dir / "ligand_openff.itp").write_text(itp_text, encoding="utf-8")
    (system_dir / "ligand_openff.gro").write_text(raw_gro, encoding="utf-8")
    return {
        "ligand_ff": LIGAND_FF,
        "charge_method": "am1bcc",
        "pose_frame_rmsd_nm": round(frame_rmsd, 6),
        "pose_source": str(pose_pdbqt.relative_to(V5_RRS)),
        "mapped_atoms": len(mapped_heavy),
    }


# --------------------------------------------------------------------------
# Protein: pdb2gmx CHARMM36m
# --------------------------------------------------------------------------
def prepare_protein(system_dir: Path, receptor_pdb: Path, gmx: str) -> None:
    ff_dir = system_dir / "charmm36-jul2022.ff"
    if not ff_dir.exists():
        shutil.copytree(
            Path("/home/nanaengo/miniforge3/envs/malaria_md/share/gromacs/top/charmm36-jul2022.ff"),
            ff_dir,
        )
    # Step 0: pdbfixer normalisation — the V5 docking receptors carry nonstandard
    # columns (AutoDock type in the element field) and occasionally lack sidechain
    # atoms; pdb2gmx rejects them.  pdbfixer rewrites the PDB in standard format
    # WITHOUT moving existing atoms (frame preserved; verified MET1 CA identical).
    from pdbfixer import PDBFixer
    from openmm.app import PDBFile
    fixer = PDBFixer(filename=str(receptor_pdb))
    fixer.findMissingResidues()
    fixer.findNonstandardResidues()
    fixer.replaceNonstandardResidues()
    fixer.removeHeterogens(keepWater=False)
    fixer.findMissingAtoms()
    fixer.addMissingAtoms()
    fixer.addMissingHydrogens(7.4)
    fixed = system_dir / "receptor_fixed.pdb"
    PDBFile.writeFile(fixer.topology, fixer.positions, open(fixed, "w"), keepIds=True)

    cmd = [
        gmx, "pdb2gmx", "-f", str(fixed), "-o", "protein_processed.gro",
        "-p", "topol.top", "-i", "posre_Protein_chain_A.itp",
        "-water", "tip3p", "-ff", "charmm36-jul2022", "-ignh", "-ter",
    ]
    # termini prompts (N-terminus then C-terminus per chain; default = option 1)
    run(["bash", "-lc", f'printf "1\n1\n1\n1\n1\n1\n1\n1\n" | ' +
        " ".join(cmd)], system_dir, "pdb2gmx")
    if not (system_dir / "protein_processed.gro").is_file():
        raise RuntimeError("pdb2gmx produced no protein_processed.gro")


def ligand_moleculetype(itp_path: Path) -> str:
    """Read the moleculetype name from an OpenFF-generated itp."""
    lines = itp_path.read_text().splitlines()
    for i, line in enumerate(lines):
        if line.strip().startswith("[ moleculetype ]"):
            for nxt in lines[i + 1:i + 3]:
                if nxt.strip() and not nxt.strip().startswith(";"):
                    name = nxt.split()[0]
                    if len(name) > 5:
                        raise RuntimeError(
                            f"unexpected long moleculetype name {name!r} in {itp_path}; "
                            "the SDF title leaked into the topology name")
                    return name
    raise RuntimeError(f"no [ moleculetype ] in {itp_path}")


def merge_gro(protein_gro: Path, ligand_gro: Path, out: Path, lig_resname: str) -> None:
    """Concatenate two .gro files (same frame), rename ligand residue to lig_resname."""
    p_lines = protein_gro.read_text().splitlines()
    l_lines = ligand_gro.read_text().splitlines()
    if len(p_lines) < 3 or len(l_lines) < 3:
        raise RuntimeError("truncated .gro file")
    p_n, l_n = int(p_lines[1]), int(l_lines[1])
    p_atoms, l_atoms = p_lines[2:2 + p_n], l_lines[2:2 + l_n]
    # replace the residue-name field (chars 5-9) only; keep atom name/number/coords.
    # (the previous concatenation produced a garbled 8-char residue like "MOL0OL0".)
    renamed = [line[:5] + lig_resname.rjust(5) + line[10:] for line in l_atoms]
    total = p_n + l_n
    box = p_lines[2 + p_n].rstrip()
    body = [protein_gro.name.split(".")[0] + " + " + lig_resname + " merged", str(total)] + p_atoms + renamed + [box]
    out.write_text("\n".join(body) + "\n", encoding="utf-8")


def add_ligand_to_topol(system_dir: Path, lig_resname: str) -> None:
    """Add the ligand include + [ molecules ] entry to topol.top (before solvation)."""
    topol = system_dir / "topol.top"
    text = topol.read_text()
    if f'#include "ligand_openff.itp"' in text:
        return
    # GROMACS requires [ atomtypes ] to precede every [ moleculetype ].  The
    # protein [ moleculetype ] blocks live in topol_Protein_chain_*.itp included
    # early in the pdb2gmx topol, so the ligand include (which carries its own
    # [ atomtypes ]) MUST be inserted right after the forcefield include, i.e.
    # before any chain topology include — not after the last #include (which
    # would place [ atomtypes ] after [ moleculetype ] and abort grompp).
    lines = text.splitlines()
    first_include = next(i for i, line in enumerate(lines)
                         if line.strip().startswith("#include"))
    lines.insert(first_include + 1, f'#include "ligand_openff.itp"')
    text = "\n".join(lines)
    if "[ molecules ]" in text:
        marker = "[ molecules ]"
        idx = text.index(marker)
        # insert the ligand as the LAST molecule entry (after the protein
        # chains): merge_gro writes the merged gro as protein-first + ligand-
        # last, and grompp maps gro atoms to topology molecules strictly by
        # order.  Inserting the ligand FIRST (previous behaviour) made grompp
        # assign the first 40 gro atoms (protein) to the ligand topology and
        # scramble every subsequent block — genion then wrote ions.gro with
        # collapsed aromatic rings and exploded side chains (verified 2026-08-10:
        # complex_unsolv.gro clean -> ions.gro 114 collapsed ring contacts).
        head, tail = text[:idx + len(marker)], text[idx + len(marker):]
        # keep the existing entries (protein chains) in place, then append the
        # ligand after the last chain line
        entries = tail.splitlines()
        first_sol = next((i for i, e in enumerate(entries)
                          if e.strip().startswith(('SOL', 'NA', 'CL', ';'))), len(entries))
        insert_at = first_sol if first_sol > 0 else len(entries)
        entries.insert(insert_at, f"{lig_resname}     1")
        text = head + "\n" + "\n".join(entries)
    else:
        text += f"\n[ molecules ]\n{lig_resname}     1\n"
    # gmx solvate/genion append SOL/ion entries to [ molecules ]; without a
    # trailing newline the append merges into the last molecule line
    # ("Protein_chain_B     1SOL ...") and the topology parse silently drops
    # the SOL molecules, causing a grompp coordinate-count mismatch.
    if not text.endswith("\n"):
        text += "\n"
    topol.write_text(text, encoding="utf-8")


def solvate_and_ions(system_dir: Path, gmx: str) -> None:
    """Box (cubic), TIP3P solvation, 0.15 M NaCl neutralisation.

    Cubic (NOT dodecahedron): the PfDHFR/PfCRT dimers are ~10.7 nm in their
    longest dimension and the dodecahedron z-height (a/sqrt(2)) for a=13.2 nm is
    only 9.33 nm < 10.3 nm protein z-extent, so the solute overlaps its periodic
    image and mdrun aborts with "no domain decomposition compatible with the
    given box" (verified 2026-08-09).  A cubic box of edge
    max_extent + 2*1.2 + margin >= 14.63 nm is used instead.
    """
    run([gmx, "editconf", "-f", "complex_unsolv.gro", "-o", "boxed.gro",
         "-c", "-d", "2.0", "-bt", "cubic"], system_dir, "editconf")
    run([gmx, "solvate", "-cp", "boxed.gro", "-cs", "spc216.gro", "-o", "solvated.gro",
         "-p", "topol.top"], system_dir, "solvate")
    ions_mdp = system_dir / "ions.mdp"
    ions_mdp.write_text(
        "; ions.mdp for genion tpr generation\nintegrator = steep\nnsteps = 10\n",
        encoding="utf-8",
    )
    run([gmx, "grompp", "-f", "ions.mdp", "-c", "solvated.gro", "-p", "topol.top",
         "-o", "ions.tpr", "-maxwarn", "5"], system_dir, "grompp-ions")
    run(["bash", "-lc", f'echo SOL | {gmx} genion -s ions.tpr -o ions.gro -p topol.top '
                       f'-pname NA -nname CL -conc 0.15 -neutral'],
        system_dir, "genion")
    if not (system_dir / "ions.gro").is_file():
        raise RuntimeError("genion produced no ions.gro")
    shutil.copy2(system_dir / "ions.gro", system_dir / "complex.gro")


# --------------------------------------------------------------------------
# Manifests
# --------------------------------------------------------------------------
def write_manifests(system_dir: Path, set_c_id: str, target: str, mutation: str,
                    smiles: str, receptor_pdb: Path, ligand_meta: dict,
                    topol_sha: str, complex_sha: str) -> None:
    system_manifest = {
        "schema_version": 1,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "cohort_id": COHORT,
        "set_c_id": set_c_id,
        "target": target,
        "mutation": mutation,
        "smiles": smiles,
        "system_name": f"{set_c_id}_{target}_{mutation}",
        "receptor_pdb": str(receptor_pdb.relative_to(RECEPTORS)),
        "receptor_sha256": sha256(receptor_pdb),
        "ligand_pose_source": ligand_meta["pose_source"],
        "ligand_pose_frame_rmsd_nm": ligand_meta["pose_frame_rmsd_nm"],
        "coordinate_frame": "receptor frame (V5 RRS pilot); ligand placed at rank-1 Vina pose",
        "topology_sha256_at_prep": topol_sha,
        "coordinates_sha256_at_prep": complex_sha,
        "preparation_script": "p2_setc_prepare_openff.py",
        "preparation_gmx": GMX,
    }
    (system_dir / "system_manifest.json").write_text(
        json.dumps(system_manifest, indent=2) + "\n", encoding="utf-8")

    ff_manifest = {
        "schema_version": 1,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "cohort_id": COHORT,
        "system_name": f"{set_c_id}_{target}_{mutation}",
        "protein_force_field": PROTEIN_FF,
        "ligand_force_field": LIGAND_FF,
        "water_model": WATER_MODEL,
        "charge_method": ligand_meta["charge_method"],
        "policy_deviation": DEVIATION,
        "topology_sha256": topol_sha,
        "coordinates_sha256": complex_sha,
        "finalized_by_equilibration": False,
    }
    (system_dir / "forcefield_manifest.json").write_text(
        json.dumps(ff_manifest, indent=2) + "\n", encoding="utf-8")


# --------------------------------------------------------------------------
# Per-system driver
# --------------------------------------------------------------------------
def prepare_system(name: str, output_root: Path, smiles_map: dict[str, str],
                   overwrite: bool) -> dict:
    set_c_id, target, mutation = parse_system_name(name)
    if (target, mutation) not in RECEPTOR_MAP:
        raise SystemExit(f"No receptor mapping for {target}/{mutation}")
    receptor_name, score_dir = RECEPTOR_MAP[(target, mutation)]
    receptor_pdb = RECEPTORS / receptor_name
    pose_pdbqt = VINA_SCORES / score_dir / f"{set_c_id}_{target}" / "vina_out.pdbqt"
    if not receptor_pdb.is_file():
        raise SystemExit(f"Missing receptor: {receptor_pdb}")
    if not pose_pdbqt.is_file():
        raise SystemExit(f"Missing pose: {pose_pdbqt}")
    smiles = smiles_map.get(set_c_id)
    if not smiles:
        raise SystemExit(f"No SMILES for {set_c_id} in {SET_C_FILE}")

    system_dir = output_root / name
    if system_dir.exists() and any(system_dir.iterdir()) and not overwrite:
        raise RuntimeError(f"System dir already populated (use --overwrite): {system_dir}")
    system_dir.mkdir(parents=True, exist_ok=True)

    ligand_meta = make_ligand_openff(system_dir, smiles, pose_pdbqt)
    prepare_protein(system_dir, receptor_pdb, GMX)
    lig_resname = ligand_moleculetype(system_dir / "ligand_openff.itp")
    add_ligand_to_topol(system_dir, lig_resname)
    merge_gro(system_dir / "protein_processed.gro", system_dir / "ligand_openff.gro",
              system_dir / "complex_unsolv.gro", lig_resname)
    solvate_and_ions(system_dir, GMX)

    topol_sha = sha256(system_dir / "topol.top")
    complex_sha = sha256(system_dir / "complex.gro")
    write_manifests(system_dir, set_c_id, target, mutation, smiles, receptor_pdb,
                    ligand_meta, topol_sha, complex_sha)

    return {
        "system": name,
        "set_c_id": set_c_id, "target": target, "mutation": mutation,
        "receptor": receptor_name,
        "topology_sha256": topol_sha,
        "coordinates_sha256_at_prep": complex_sha,
        "pose_frame_rmsd_nm": ligand_meta["pose_frame_rmsd_nm"],
        "n_atoms_complex": int((system_dir / "complex.gro").read_text().splitlines()[1]),
        "status": "PREPARED_AWAITING_EQUILIBRATION",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--system", help="Single system name, e.g. PP-01_PfDHFR_WT")
    parser.add_argument("--all", action="store_true", help="Prepare the full 16-system pilot")
    parser.add_argument("--output-root", type=Path, default=SYSTEM_ROOT)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    smiles_map = load_set_c()
    candidates = {"PP-01", "PP-02"}
    systems = []
    for target, mutations in (("PfDHFR", ["WT", "N51I", "C59R", "S108N", "I164L"]),
                              ("PfCRT", ["WT", "K76T", "K76A"])):
        for mut in mutations:
            for cid in sorted(candidates):
                systems.append(f"{cid}_{target}_{mut}")
    if args.system:
        systems = [args.system]
    elif not args.all:
        parser.error("provide --system NAME or --all")

    args.output_root.mkdir(parents=True, exist_ok=True)
    records = []
    for name in systems:
        print(f"[prep] {name}", flush=True)
        records.append(prepare_system(name, args.output_root, smiles_map, args.overwrite))
    summary = {
        "schema_version": 1,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "cohort_id": COHORT,
        "preparation_policy": "DOCUMENTED_DEVIATION_OPENFF_2_2_AM1BCC",
        "deviation": DEVIATION,
        "systems_requested": len(systems),
        "systems_prepared": len(records),
        "records": records,
        "next_step": "run p2_setc_equilibrate.sbatch (EM/NVT/NPT) then finalise manifests",
    }
    out = args.output_root / "preparation_manifest.json"
    out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"[prep] preparation manifest: {out}")
    print(f"[prep] prepared {len(records)}/{len(systems)} systems")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
