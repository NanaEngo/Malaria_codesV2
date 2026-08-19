#!/usr/bin/env python3
"""Isolated Set-C chain-gap remediation pilot.

This pilot does not modify the canonical preparation root.  It copies one
prepared system, inserts an explicit TER at a documented unresolved internal
chain gap, regenerates the CHARMM36m protein topology, re-merges the existing
OpenFF ligand, re-solvates/ionizes, and requires ``grompp -maxwarn 0``.

It is intentionally limited to one system until the structural policy is
accepted for the target construct.  It must not be used as a silent global
repair: splitting an unresolved internal loop creates additional termini and
requires biological/force-field review.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shlex
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
PREP_SCRIPT = PROJECT / "scripts" / "p2_setc_prepare_openff.py"
DEFAULT_INPUT = PROJECT / "results" / "md_systems" / "set_c_preparation_20260811_v7" / "PP-01_PfCRT_K76A"
DEFAULT_OUTPUT = PROJECT / "results" / "md_systems" / "set_c_gap_pilot_20260811_v1"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def insert_ter_at_gap(src: Path, dst: Path, chain: str, after_residue: int) -> dict:
    """Insert TER only for the exact documented transition A:113 -> A:123."""
    lines = src.read_text(encoding="utf-8", errors="replace").splitlines()
    unique: list[tuple[str, int]] = []
    first_line: dict[tuple[str, int], int] = {}
    for lineno, line in enumerate(lines):
        if not line.startswith(("ATOM  ", "HETATM")):
            continue
        key = (line[21:22].strip(), int(line[22:26]))
        if not unique or unique[-1] != key:
            unique.append(key)
            first_line[key] = lineno
    expected = (chain, after_residue), (chain, after_residue + 10)
    transitions = list(zip(unique, unique[1:]))
    if expected not in transitions:
        nearby = [pair for pair in transitions if pair[0][0] == chain and pair[0][1] >= after_residue - 2 and pair[0][1] <= after_residue + 2]
        raise RuntimeError(
            f"Could not verify exact {chain}:{after_residue} -> {chain}:{after_residue + 10} "
            f"transition in {src}; nearby={nearby}"
        )
    insert_at = first_line[expected[1]]
    if insert_at > 0 and lines[insert_at - 1].strip() == "TER":
        raise RuntimeError("TER already present at the requested gap")
    out = lines[:insert_at] + ["TER"] + lines[insert_at:]
    dst.write_text("\n".join(out) + "\n", encoding="utf-8")
    transition = (after_residue, after_residue + 10)
    dst.write_text("\n".join(out) + "\n", encoding="utf-8")
    return {
        "source_sha256": sha256(src),
        "remediated_sha256": sha256(dst),
        "chain": chain,
        "after_residue": after_residue,
        "before_residue": after_residue + 10,
        "ter_inserted": True,
    }


def fragment_count(pdb: Path) -> int:
    """Count coordinate fragments separated by TER or chain transitions."""
    fragments = 0
    previous_chain = None
    previous_residue = None
    for line in pdb.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("TER"):
            previous_chain = None
            previous_residue = None
            continue
        if not line.startswith(("ATOM  ", "HETATM")):
            continue
        chain = line[21:22].strip()
        residue = int(line[22:26])
        if previous_chain is None or chain != previous_chain:
            fragments += 1
        previous_chain = chain
        previous_residue = residue
    return fragments


def molecule_entries(topol: Path) -> list[tuple[str, int]]:
    entries: list[tuple[str, int]] = []
    inside = False
    for line in topol.read_text(encoding="utf-8", errors="replace").splitlines():
        stripped = line.split(";", 1)[0].strip()
        if stripped.lower() == "[ molecules ]":
            inside = True
            continue
        if inside and stripped.startswith("["):
            break
        if inside and stripped:
            fields = stripped.split()
            if len(fields) >= 2 and fields[1].isdigit():
                entries.append((fields[0], int(fields[1])))
    return entries


def run(cmd: list[str], cwd: Path, label: str) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(
            f"{label} failed (rc={result.returncode})\n"
            f"$ {' '.join(cmd)}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input-system", type=Path, default=DEFAULT_INPUT)
    ap.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT)
    ap.add_argument("--chain", default="A")
    ap.add_argument("--after-residue", type=int, default=113)
    ap.add_argument("--system-name", default="PP-01_PfCRT_K76A_gap_split")
    args = ap.parse_args()

    if args.output_root.exists() and any(args.output_root.iterdir()):
        raise RuntimeError(f"Refusing non-empty output root: {args.output_root}")
    if not args.input_system.is_dir():
        raise FileNotFoundError(args.input_system)
    args.output_root.mkdir(parents=True, exist_ok=False)
    work = args.output_root / "system"
    shutil.copytree(args.input_system, work)
    source_system_manifest = json.loads((work / "system_manifest.json").read_text())
    source_forcefield_manifest = json.loads((work / "forcefield_manifest.json").read_text())

    # Import the canonical solvation/audit helpers only after the isolated copy
    # exists.  No canonical system directory is passed to any helper.
    os.environ.setdefault("P2_GMX_BIN", "/home/nanaengo/miniforge3/envs/malaria_md/bin/gmx")
    sys.path.insert(0, str(PREP_SCRIPT.parent))
    import p2_setc_prepare_openff as prep  # noqa: E402

    gmx = os.environ["P2_GMX_BIN"]
    receptor = work / "receptor_fixed.pdb"
    if not receptor.is_file():
        raise FileNotFoundError(receptor)
    original_fragments = fragment_count(receptor)
    provenance = insert_ter_at_gap(receptor, work / "receptor_gap_split.pdb", args.chain, args.after_residue)
    receptor.unlink()
    (work / "receptor_gap_split.pdb").rename(receptor)
    remediated_fragments = fragment_count(receptor)
    if remediated_fragments != original_fragments + 1:
        raise RuntimeError(
            f"Unexpected fragment count after TER insertion: {original_fragments} -> "
            f"{remediated_fragments}"
        )
    provenance.update({
        "original_fragment_count": original_fragments,
        "remediated_fragment_count": remediated_fragments,
    })

    # Remove only regenerated protein/system outputs.  Ligand files and the
    # force-field directory remain the audited inputs from the prepared witness.
    patterns = (
        "topol.top", "topol_*.itp", "posre*.itp", "protein_processed.gro",
        "complex_unsolv.gro", "boxed.gro", "solvated.gro", "complex.gro",
        "ions.gro", "ions.tpr", "ions.mdp", "pre_equilibration_audit.json",
        "pre_equilibration_audit.tpr", "equilibration_failure.json",
        "system_manifest.json", "forcefield_manifest.json",
    )
    for pattern in patterns:
        for p in work.glob(pattern):
            if p.is_file():
                p.unlink()

    # Four chain blocks become eight terminal prompts.  Capture the complete
    # pdb2gmx output in provenance; never suppress a topology warning.
    cmd = (
        f"printf '1\\n1\\n1\\n1\\n1\\n1\\n1\\n1\\n' | "
        f"{shlex.quote(gmx)} pdb2gmx -f receptor_fixed.pdb -o protein_processed.gro "
        f"-p topol.top -i posre_Protein_chain_A.itp -water tip3p "
        f"-ff charmm36-jul2022 -ignh -ter"
    )
    pdb2gmx = subprocess.run(["bash", "-lc", cmd], cwd=work, text=True, capture_output=True)
    (work / "pdb2gmx.stdout").write_text(pdb2gmx.stdout, encoding="utf-8")
    (work / "pdb2gmx.stderr").write_text(pdb2gmx.stderr, encoding="utf-8")
    if pdb2gmx.returncode:
        raise RuntimeError(f"pdb2gmx failed (rc={pdb2gmx.returncode}); see pdb2gmx.stdout/stderr")

    expected_protein_fragments = remediated_fragments
    entries_after_pdb2gmx = molecule_entries(work / "topol.top")
    protein_entries = [name for name, count in entries_after_pdb2gmx if name.startswith("Protein_") for _ in range(count)]
    if len(protein_entries) != expected_protein_fragments:
        raise RuntimeError(
            f"pdb2gmx protein molecule count {len(protein_entries)} != "
            f"expected fragments {expected_protein_fragments}: {entries_after_pdb2gmx}"
        )

    lig_name = prep.ligand_moleculetype(work / "ligand_openff.itp")
    prep.add_ligand_to_topol(work, lig_name)
    prep.merge_gro(work / "protein_processed.gro", work / "ligand_openff.gro",
                   work / "complex_unsolv.gro", lig_name)
    prep.solvate_and_ions(work, gmx)

    # Copied manifests are invalid after topology regeneration.  Rebuild them
    # with fresh hashes so the audit certifies the remediated system, not the
    # pre-remediation preparation.
    source_system_manifest.update({
        "schema_version": 2,
        "system_name": args.system_name,
        "remediation": "explicit_TER_at_unresolved_internal_gap",
        "receptor_fixed_sha256": sha256(receptor),
        "topology_sha256_at_prep": sha256(work / "topol.top"),
        "coordinates_sha256_at_prep": sha256(work / "complex.gro"),
        "preparation_script": "p2_setc_gap_remediation_pilot.py",
        "preparation_script_sha256": sha256(Path(__file__).resolve()),
        "gromacs_executable": gmx,
        "gromacs_executable_sha256": sha256(Path(gmx)),
        "provenance_status": "REBUILT_PILOT_NOT_BIOLOGICALLY_VALIDATED",
    })
    source_forcefield_manifest.update({
        "schema_version": 2,
        "system_name": args.system_name,
        "topology_sha256": sha256(work / "topol.top"),
        "coordinates_sha256": sha256(work / "complex.gro"),
        "finalized_by_equilibration": False,
        "remediation": "explicit_TER_at_unresolved_internal_gap",
        "provenance_status": "REBUILT_PILOT_NOT_BIOLOGICALLY_VALIDATED",
    })
    (work / "system_manifest.json").write_text(json.dumps(source_system_manifest, indent=2) + "\n")
    (work / "forcefield_manifest.json").write_text(json.dumps(source_forcefield_manifest, indent=2) + "\n")
    audit = prep.audit_pre_equilibration(work, lig_name, gmx, system_name=args.system_name)

    result = {
        "schema_version": 1,
        "status": "PASS",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "input_system": str(args.input_system),
        "output_root": str(args.output_root),
        "system_name": args.system_name,
        "remediation": "explicit_TER_at_unresolved_internal_gap",
        "scientific_status": "TECHNICAL_TOPOLOGY_PILOT_ONLY",
        "biological_validation": "PENDING_LOOP_OR_CHAIN_POLICY_REVIEW",
        "source_manifests_superseded": True,
        "provenance": provenance,
        "pdb2gmx_command": cmd,
        "pdb2gmx_stdout_sha256": sha256(work / "pdb2gmx.stdout"),
        "pdb2gmx_stderr_sha256": sha256(work / "pdb2gmx.stderr"),
        "audit": audit,
    }
    (args.output_root / "gap_remediation_pilot.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"status": "PASS", "output_root": str(args.output_root), "audit": audit}, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise
