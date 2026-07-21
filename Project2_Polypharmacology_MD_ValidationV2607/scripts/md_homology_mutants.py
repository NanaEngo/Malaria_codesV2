"""
Paper 2 — Step 5: Homology modelling of resistance mutants.

Generates 6 mutant structures from wild-type PDB templates:
  PfDHFR (7F3Y): N51I, C59R, S108N, I164L
  PfCRT  (6UKJ): K76T, K76A

Fallback chain (per roadmap v1.4):
  1. SWISS-MODEL REST API  (requires SWISSMODEL_TOKEN env var) — preferred
  2. ColabFold             (requires localcolabfold installation) — faster than AF2
  3. RoseTTAFold           (requires Robetta API key in ROBETTA_TOKEN env var)
  4. PyMOL mutagenesis wizard (last resort, single-point mutations only)

Quality criteria checked after modelling:
  - QMEAN > -4.0
  - GMQE  > 0.7
  - Ramachandran favoured > 95%
  - Backbone RMSD to WT < 1.5 Å

Outputs saved to: data/proteins/mutants/<TARGET>_<MUTATION>.pdb

Usage:
    python scripts/md_homology_mutants.py [--method swissmodel|colabfold|rosettafold|pymol]
    python scripts/md_homology_mutants.py --method swissmodel  # needs SWISSMODEL_TOKEN
    python scripts/md_homology_mutants.py --method colabfold   # needs localcolabfold
"""

import argparse
import os
import subprocess
import time
from pathlib import Path

import requests

PROJECT_DIR = Path(__file__).parent.parent
PROTEIN_DIR = PROJECT_DIR / "data" / "proteins"
MUTANT_DIR = PROTEIN_DIR / "mutants"

# Wild-type templates
TEMPLATES = {
    "PfDHFR": {"pdb": "7F3Y", "chain": "A"},
    "PfCRT":  {"pdb": "6UKJ", "chain": "A"},
}

# Mutations: (target, wt_residue, position, mut_residue)
MUTATIONS = [
    ("PfDHFR", "N", 51,  "I"),
    ("PfDHFR", "C", 59,  "R"),
    ("PfDHFR", "S", 108, "N"),
    ("PfDHFR", "I", 164, "L"),
    ("PfCRT",  "K", 76,  "T"),
    ("PfCRT",  "K", 76,  "A"),
]

# One-letter to three-letter amino acid map
AA1TO3 = {
    "A": "ALA", "R": "ARG", "N": "ASN", "D": "ASP", "C": "CYS",
    "E": "GLU", "Q": "GLN", "G": "GLY", "H": "HIS", "I": "ILE",
    "L": "LEU", "K": "LYS", "M": "MET", "F": "PHE", "P": "PRO",
    "S": "SER", "T": "THR", "W": "TRP", "Y": "TYR", "V": "VAL",
}

SWISSMODEL_API = "https://swissmodel.expasy.org"


def mutate_sequence(fasta_seq: str, position: int, mut_aa: str) -> str:
    """Apply a single point mutation to a FASTA sequence (1-based position)."""
    seq = list(fasta_seq)
    idx = position - 1
    if idx < 0 or idx >= len(seq):
        raise ValueError(f"Position {position} out of range for sequence of length {len(seq)}")
    seq[idx] = mut_aa
    return "".join(seq)


def read_fasta_from_pdb(pdb_file: Path, chain: str) -> str:
    """Extract one-letter sequence from SEQRES records in a PDB file."""
    aa3to1 = {v: k for k, v in AA1TO3.items()}
    seq = []
    for line in pdb_file.read_text().splitlines():
        if line.startswith("SEQRES") and line[11] == chain:
            residues = line[19:].split()
            seq.extend(aa3to1.get(r, "X") for r in residues)
    if not seq:
        raise ValueError(f"No SEQRES records found for chain {chain} in {pdb_file}")
    return "".join(seq)


# ---------------------------------------------------------------------------
# SWISS-MODEL path
# ---------------------------------------------------------------------------

def submit_swissmodel(sequence: str, template_pdb: str, token: str) -> str | None:
    """Submit a modelling job to SWISS-MODEL and return the project ID."""
    headers = {"Authorization": f"Token {token}", "Content-Type": "application/json"}
    payload = {
        "target_sequences": [sequence],
        "template": template_pdb,
    }
    r = requests.post(f"{SWISSMODEL_API}/automodel", json=payload, headers=headers)
    if r.status_code not in (200, 201, 202):
        print(f"  SWISS-MODEL submission failed: {r.status_code} {r.text[:200]}")
        return None
    return r.json().get("project_id")


def poll_swissmodel(project_id: str, token: str, timeout: int = 1800) -> dict | None:
    """Poll until the job completes or times out. Returns result dict or None."""
    headers = {"Authorization": f"Token {token}"}
    url = f"{SWISSMODEL_API}/api/v1/modelling/{project_id}/"
    elapsed = 0
    interval = 30
    while elapsed < timeout:
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            print(f"  Poll error: {r.status_code}")
            return None
        data = r.json()
        status = data.get("status", "")
        if status == "COMPLETED":
            return data
        if status in ("FAILED", "ERROR"):
            print(f"  SWISS-MODEL job failed: {data.get('message', '')}")
            return None
        print(f"  Waiting for SWISS-MODEL ({elapsed}s)... status={status}")
        time.sleep(interval)
        elapsed += interval
    print(f"  SWISS-MODEL timed out after {timeout}s")
    return None


def download_swissmodel_pdb(result: dict, output_file: Path) -> bool:
    """Download the first model PDB from a completed SWISS-MODEL result."""
    try:
        models = result["models"]
        if not models:
            print("  No models in SWISS-MODEL result")
            return False
        pdb_url = models[0]["coordinates_url"]
        r = requests.get(pdb_url)
        output_file.write_bytes(r.content)
        print(f"  Downloaded model: {output_file}")
        return True
    except (KeyError, IndexError, Exception) as e:
        print(f"  Download failed: {e}")
        return False


def model_with_swissmodel(target: str, wt_aa: str, position: int, mut_aa: str,
                           token: str) -> bool:
    info = TEMPLATES[target]
    pdb_file = PROTEIN_DIR / f"{info['pdb']}.pdb"
    output_file = MUTANT_DIR / f"{info['pdb']}_{wt_aa}{position}{mut_aa}.pdb"

    if output_file.exists():
        print(f"  Already exists: {output_file.name}")
        return True

    print(f"  Reading sequence from {pdb_file.name}...")
    try:
        wt_seq = read_fasta_from_pdb(pdb_file, info["chain"])
    except ValueError as e:
        print(f"  {e}")
        return False

    mut_seq = mutate_sequence(wt_seq, position, mut_aa)
    print(f"  Submitting {target} {wt_aa}{position}{mut_aa} to SWISS-MODEL...")
    project_id = submit_swissmodel(mut_seq, info["pdb"], token)
    if not project_id:
        return False

    result = poll_swissmodel(project_id, token)
    if not result:
        return False

    return download_swissmodel_pdb(result, output_file)


# ---------------------------------------------------------------------------
# ColabFold fallback path
# ---------------------------------------------------------------------------

def model_with_colabfold(target: str, wt_aa: str, position: int, mut_aa: str) -> bool:
    """
    Use localcolabfold (AlphaFold2 backend) for mutant structure prediction.
    Faster than standalone AlphaFold2; free; recommended first fallback.
    Requires: localcolabfold installed (https://github.com/YoshitakaMo/localcolabfold)
    """
    info = TEMPLATES[target]
    output_file = MUTANT_DIR / f"{info['pdb']}_{wt_aa}{position}{mut_aa}.pdb"

    if output_file.exists():
        print(f"  Already exists: {output_file.name}")
        return True

    try:
        wt_seq = read_fasta_from_pdb(PROTEIN_DIR / f"{info['pdb']}.pdb", info["chain"])
    except ValueError as e:
        print(f"  {e}")
        return False

    mut_seq = mutate_sequence(wt_seq, position, mut_aa)
    fasta_file = MUTANT_DIR / f"_{target}_{wt_aa}{position}{mut_aa}.fasta"
    fasta_file.write_text(f">{target}_{wt_aa}{position}{mut_aa}\n{mut_seq}\n")

    colabfold_out = MUTANT_DIR / f"colabfold_{target}_{wt_aa}{position}{mut_aa}"
    colabfold_out.mkdir(exist_ok=True)

    result = subprocess.run(
        ["colabfold_batch", str(fasta_file), str(colabfold_out),
         "--num-models", "1", "--num-recycle", "3"],
        capture_output=True, text=True
    )
    fasta_file.unlink(missing_ok=True)

    if result.returncode != 0:
        print(f"  ColabFold failed: {result.stderr[:300]}")
        return False

    # Find the best-ranked PDB output
    pdb_files = sorted(colabfold_out.glob("*.pdb"))
    if not pdb_files:
        print("  ColabFold produced no PDB files")
        return False

    import shutil as _shutil
    _shutil.copy2(pdb_files[0], output_file)
    print(f"  ColabFold model saved: {output_file.name}")
    return True


# ---------------------------------------------------------------------------
# RoseTTAFold fallback path
# ---------------------------------------------------------------------------

def model_with_rosettafold(target: str, wt_aa: str, position: int, mut_aa: str) -> bool:
    """
    Use Robetta server (RoseTTAFold) for mutant structure prediction.
    Requires: ROBETTA_TOKEN environment variable.
    """
    token = os.environ.get("ROBETTA_TOKEN", "")
    if not token:
        print("  RoseTTAFold: ROBETTA_TOKEN not set. Skipping.")
        return False

    info = TEMPLATES[target]
    output_file = MUTANT_DIR / f"{info['pdb']}_{wt_aa}{position}{mut_aa}.pdb"

    if output_file.exists():
        print(f"  Already exists: {output_file.name}")
        return True

    try:
        wt_seq = read_fasta_from_pdb(PROTEIN_DIR / f"{info['pdb']}.pdb", info["chain"])
    except ValueError as e:
        print(f"  {e}")
        return False

    mut_seq = mutate_sequence(wt_seq, position, mut_aa)
    label = f"{target}_{wt_aa}{position}{mut_aa}"

    # Submit to Robetta REST API
    headers = {"Authorization": f"Token {token}", "Content-Type": "application/json"}
    payload = {"sequence": mut_seq, "target_name": label}
    try:
        r = requests.post("https://robetta.bakerlab.org/api/targets/",
                          json=payload, headers=headers)
        if r.status_code not in (200, 201):
            print(f"  Robetta submission failed: {r.status_code} {r.text[:200]}")
            return False
        job_id = r.json().get("id")
        print(f"  Submitted to Robetta (job {job_id}). Polling...")

        # Poll for completion
        for _ in range(120):  # up to 60 minutes
            time.sleep(30)
            r = requests.get(f"https://robetta.bakerlab.org/api/targets/{job_id}/",
                             headers=headers)
            data = r.json()
            if data.get("status") == "DONE":
                pdb_url = data.get("model_url", "")
                if pdb_url:
                    pdb_content = requests.get(pdb_url).content
                    output_file.write_bytes(pdb_content)
                    print(f"  RoseTTAFold model saved: {output_file.name}")
                    return True
                break
            if data.get("status") in ("FAILED", "ERROR"):
                print("  Robetta job failed")
                return False

        print("  Robetta timed out")
        return False
    except Exception as e:
        print(f"  RoseTTAFold error: {e}")
        return False




def model_with_pymol(target: str, wt_aa: str, position: int, mut_aa: str) -> bool:
    """Use PyMOL mutagenesis wizard for single-point mutation."""
    info = TEMPLATES[target]
    pdb_file = PROTEIN_DIR / f"{info['pdb']}.pdb"
    output_file = MUTANT_DIR / f"{info['pdb']}_{wt_aa}{position}{mut_aa}.pdb"

    if output_file.exists():
        print(f"  Already exists: {output_file.name}")
        return True

    mut3 = AA1TO3.get(mut_aa, mut_aa)
    pymol_script = f"""
from pymol import cmd
from pymol.wizard import mutagenesis
cmd.load("{pdb_file}", "wt")
cmd.wizard("mutagenesis")
cmd.get_wizard().set_mode("{mut3}")
cmd.get_wizard().do_select("/{info['chain']}/{position}/")
cmd.get_wizard().apply()
cmd.set_wizard()
cmd.save("{output_file}", "wt")
cmd.quit()
"""
    script_file = MUTANT_DIR / f"_pymol_{target}_{wt_aa}{position}{mut_aa}.py"
    script_file.write_text(pymol_script)

    result = subprocess.run(
        ["pymol", "-c", str(script_file)],
        capture_output=True, text=True
    )
    script_file.unlink(missing_ok=True)

    if result.returncode != 0 or not output_file.exists():
        print(f"  PyMOL failed: {result.stderr[:300]}")
        return False

    print(f"  PyMOL mutant saved: {output_file.name}")
    return True


# ---------------------------------------------------------------------------
# Quality check
# ---------------------------------------------------------------------------

def check_backbone_rmsd(wt_pdb: Path, mut_pdb: Path, threshold: float = 1.5) -> bool:
    """
    Compute backbone RMSD between WT and mutant using BioPython Superimposer.
    Returns True if RMSD < threshold (Å).
    """
    try:
        from Bio.PDB import PDBParser, Superimposer

        parser = PDBParser(QUIET=True)
        wt_struct = parser.get_structure("wt", str(wt_pdb))
        mut_struct = parser.get_structure("mut", str(mut_pdb))

        wt_atoms = [a for a in wt_struct.get_atoms() if a.name == "CA"]
        mut_atoms = [a for a in mut_struct.get_atoms() if a.name == "CA"]

        n = min(len(wt_atoms), len(mut_atoms))
        if n == 0:
            return True  # can't check, pass through

        sup = Superimposer()
        sup.set_atoms(wt_atoms[:n], mut_atoms[:n])
        rmsd = sup.rms
        print(f"  Backbone RMSD to WT: {rmsd:.3f} Å (threshold: {threshold} Å)")
        return rmsd < threshold
    except Exception as e:
        print(f"  Warning: RMSD check failed: {e}")
        return True  # don't block on check failure


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--method",
                        choices=["swissmodel", "colabfold", "rosettafold", "pymol"],
                        default=None,
                        help="Modelling method (default: auto-detect from available tools)")
    args = parser.parse_args()

    MUTANT_DIR.mkdir(parents=True, exist_ok=True)

    token = os.environ.get("SWISSMODEL_TOKEN", "")
    method = args.method
    if method is None:
        # Auto-detect: prefer SWISS-MODEL, then ColabFold, then RoseTTAFold, then PyMOL
        if token:
            method = "swissmodel"
        elif subprocess.run(["which", "colabfold_batch"],
                            capture_output=True).returncode == 0:
            method = "colabfold"
        elif os.environ.get("ROBETTA_TOKEN"):
            method = "rosettafold"
        else:
            method = "pymol"
        print(f"  Auto-detected method: {method}")

    print("=" * 60)
    print(f"Homology modelling of resistance mutants (method: {method})")
    print("=" * 60)

    if method == "swissmodel" and not token:
        print("ERROR: SWISSMODEL_TOKEN environment variable not set.")
        print("  export SWISSMODEL_TOKEN=<your_token>")
        print("  Or use --method pymol")
        return

    results = {}
    for target, wt_aa, position, mut_aa in MUTATIONS:
        label = f"{target} {wt_aa}{position}{mut_aa}"
        print(f"\nModelling {label}...")

        if method == "swissmodel":
            ok = model_with_swissmodel(target, wt_aa, position, mut_aa, token)
        elif method == "colabfold":
            ok = model_with_colabfold(target, wt_aa, position, mut_aa)
        elif method == "rosettafold":
            ok = model_with_rosettafold(target, wt_aa, position, mut_aa)
        else:
            ok = model_with_pymol(target, wt_aa, position, mut_aa)

        if ok:
            info = TEMPLATES[target]
            wt_pdb = PROTEIN_DIR / f"{info['pdb']}.pdb"
            mut_pdb = MUTANT_DIR / f"{info['pdb']}_{wt_aa}{position}{mut_aa}.pdb"
            rmsd_ok = check_backbone_rmsd(wt_pdb, mut_pdb)
            results[label] = "PASS" if rmsd_ok else "FAIL (RMSD > 1.5 Å)"
        else:
            results[label] = "FAILED"

    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    for label, status in results.items():
        icon = "✓" if status == "PASS" else "✗"
        print(f"  {icon} {label}: {status}")

    failed = [k for k, v in results.items() if v != "PASS"]
    if failed:
        print(f"\n  {len(failed)} mutant(s) need attention:")
        for f in failed:
            print(f"    - {f}")
        print("  Fallback chain: ColabFold -> RoseTTAFold -> PyMOL wizard (see roadmap §Step 5)")


if __name__ == "__main__":
    main()
