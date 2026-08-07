"""
MD Simulation: Trajectory Analysis

Analyses MD trajectories for:
- RMSD (protein backbone + ligand heavy atoms)
- RMSF (per-residue)
- Hydrogen bond occupancy
- MM-GBSA binding free energy via AMBERTools MMPBSA.py (igb=2, OBC model)
  gmx_MMPBSA is used only as the GROMACS->AMBER format converter.

Usage:
    python scripts/md_analyse_trajectories.py
"""

import argparse
import os
import shlex
import subprocess
import re
from pathlib import Path
import pandas as pd
import numpy as np

PROJECT_DIR = Path(__file__).parent.parent
MD_DIR = PROJECT_DIR / "MD_systems"
RESULTS_DIR = PROJECT_DIR / "results" / "md_results"

# MD parameters (must match production.mdp)
DT_PS = 0.002  # timestep in ps
NSTXOUT = 5000  # output frequency in steps
OUTPUT_INTERVAL_PS = DT_PS * NSTXOUT  # 10 ps
GMX_BIN = shlex.quote(os.environ.get("P2_GMX_BIN", "gmx"))
N_REPLICATES = int(os.environ.get("P2_MD_REPLICATES", "1"))

COMPLEXES = {
    '201_DHFR': {
        'ligand_resname': None,  # Auto-detect
        'key_residues': ['ASP54', 'ARG57', 'PHE34'],
    },
    '438_ATP4': {
        'ligand_resname': None,  # Auto-detect
        'key_residues': ['GLU328', 'PHE340', 'LEU331'],
    },
    '164_ClpP': {
        'ligand_resname': None,  # Auto-detect
        'key_residues': ['ASP171', 'SER99', 'THR100'],
    },
    '214_CRT': {
        'ligand_resname': None,  # Auto-detect
        'key_residues': ['LYS76', 'ALA220', 'ILE228'],  # PfCRT binding site
    },
}

def get_ligand_resname_from_topology(topology_file):
    """Auto-detect ligand residue name from GROMACS topology."""
    if not Path(topology_file).exists():
        return 'LIG'
    
    try:
        with open(topology_file, 'r') as f:
            in_atoms = False
            residues = {}
            for line in f:
                if '[ atoms ]' in line:
                    in_atoms = True
                    continue
                if in_atoms and line.startswith('['):
                    break
                if in_atoms and not line.startswith(';'):
                    parts = line.split()
                    if len(parts) >= 4:
                        resname = parts[3]
                        residues[resname] = residues.get(resname, 0) + 1
        
        known_non_ligands = {'Protein', 'Protein_chain', 'SOL', 'WAT', 'NA', 'CL'}
        ligand_candidates = {r: c for r, c in residues.items() if r not in known_non_ligands}
        
        if ligand_candidates:
            return max(ligand_candidates, key=ligand_candidates.get)
    except Exception as e:
        print(f"  Warning: Could not detect residue name: {e}")
    
    return 'LIG'

def run_gmx_command(cmd, input_text=None):
    """Run a GROMACS command with proper error handling."""
    result = subprocess.run(
        cmd, shell=True, input=input_text, capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"  Warning: Command failed: {cmd}")
        print(f"  Error: {result.stderr}")
        return False
    return True

def compute_rmsd(complex_name, replicate_dir, ligand_resname='LIG'):
    """Compute backbone and ligand RMSD."""
    tpr_file = replicate_dir / "production.tpr"
    xtc_file = replicate_dir / "production.xtc"

    if not tpr_file.exists() or not xtc_file.exists():
        print(f"  Warning: Trajectory files not found in {replicate_dir}")
        return None, None

    # Backbone RMSD
    bb_rmsd_file = replicate_dir / "rmsd_bb.xvg"
    cmd = f"{GMX_BIN} rms -s {tpr_file} -f {xtc_file} -o {bb_rmsd_file} -tu ns"
    if not run_gmx_command(cmd, b"Backbone\n"):
        return None, None

    # Ligand RMSD
    lig_rmsd_file = replicate_dir / "rmsd_lig.xvg"
    index_file = replicate_dir / "index.ndx"

    # Create index for ligand
    cmd = f"{GMX_BIN} make_ndx -f {tpr_file} -o {index_file}"
    run_gmx_command(cmd, f"r {ligand_resname}\nq\n".encode())

    # Calculate ligand RMSD
    cmd = f"{GMX_BIN} rms -s {tpr_file} -f {xtc_file} -n {index_file} -o {lig_rmsd_file} -tu ns"
    if not run_gmx_command(cmd, f"r {ligand_resname}\nr {ligand_resname}\n".encode()):
        return None, None

    # Parse RMSD files
    def parse_rmsd(file):
        if not file.exists():
            return None
        try:
            data = np.loadtxt(file, comments=['@', '#'])
            return data[:, 1]  # RMSD column
        except Exception as e:
            print(f"  Warning: Could not parse {file}: {e}")
            return None

    bb_rmsd = parse_rmsd(bb_rmsd_file)
    lig_rmsd = parse_rmsd(lig_rmsd_file)

    return bb_rmsd, lig_rmsd

def compute_rmsf(complex_name, replicate_dir):
    """Compute per-residue RMSF."""
    tpr_file = replicate_dir / "production.tpr"
    xtc_file = replicate_dir / "production.xtc"
    rmsf_file = replicate_dir / "rmsf.xvg"

    cmd = f"{GMX_BIN} rmsf -s {tpr_file} -f {xtc_file} -o {rmsf_file} -res"
    if not run_gmx_command(cmd, b"Backbone\n"):
        return None

    if rmsf_file.exists():
        try:
            data = np.loadtxt(rmsf_file, comments=['@', '#'])
            return data[:, 1]  # RMSF values
        except Exception as e:
            print(f"  Warning: Could not parse RMSF: {e}")
            return None
    return None

def compute_hbonds(complex_name, replicate_dir, key_residues, ligand_resname='LIG'):
    """Compute hydrogen bond occupancy with key residues."""
    tpr_file = replicate_dir / "production.tpr"
    xtc_file = replicate_dir / "production.xtc"
    index_file = replicate_dir / "index.ndx"

    # Create index for ligand
    cmd = f"{GMX_BIN} make_ndx -f {tpr_file} -o {index_file}"
    run_gmx_command(cmd, f"r {ligand_resname}\nq\n".encode())

    # Compute H-bonds between protein and ligand
    hbond_file = replicate_dir / "hbonds.xvg"
    cmd = f"{GMX_BIN} hbond -s {tpr_file} -f {xtc_file} -n {index_file} -num {hbond_file}"
    if not run_gmx_command(cmd, b"Protein\nr LIG\n"):
        return None

    if hbond_file.exists():
        try:
            data = np.loadtxt(hbond_file, comments=['@', '#'])
            return data[:, 1]  # Number of H-bonds
        except Exception as e:
            print(f"  Warning: Could not parse H-bonds: {e}")
            return None
    return None

def parse_mmpbsa_energy(output_file):
    """
    Robustly parse gmx_MMPBSA energy output.
    
    Handles multiple output formats:
    - RESULTS TOTAL = -45.32 kcal/mol
    - TOTAL -45.32
    - Summary energy = -45.32
    - TOTAL pair format
    
    Args:
        output_file: Path to FINAL_RESULTS_MMPBSA.dat
        
    Returns:
        Energy value in kcal/mol or None if parsing fails
        
    Raises:
        FileNotFoundError: If output file doesn't exist
        ValueError: If energy cannot be reliably parsed
    """
    output_file = Path(output_file)
    
    if not output_file.exists():
        raise FileNotFoundError(f"MM-PBSA output not found: {output_file}")
    
    with open(output_file, 'r') as f:
        content = f.read()
    
    # Try multiple parsing strategies in order of specificity
    strategies = [
        # Strategy 1: RESULTS TOTAL = value kcal/mol
        (r'RESULTS.*?TOTAL.*?=\s*([-\d.e+]+)\s*kcal', 'RESULTS format'),
        # Strategy 2: TOTAL COMPLEX = value
        (r'TOTAL\s+COMPLEX\s+(\S+)\s+([-\d.e+]+)', 'COMPLEX pair'),
        # Strategy 3: Just "TOTAL" followed by numbers on same line
        (r'^TOTAL\s+([-\d.e+]+)', 'Simple TOTAL format'),
        # Strategy 4: Summary format
        (r'Summary.*?TOTAL.*?(\S+)\s+([-\d.e+]+)', 'Summary format'),
    ]
    
    for pattern, description in strategies:
        match = re.search(pattern, content, re.MULTILINE)
        if match:
            try:
                if len(match.groups()) == 1:
                    energy = float(match.group(1))
                else:
                    energy = float(match.group(2))
                
                # Validate energy is in reasonable range
                if -1000 < energy < 1000:  # Typical range in kcal/mol
                    return energy
                else:
                    print(f"  Warning: Energy {energy} outside expected range (-1000 to 1000 kcal/mol)")
            except (ValueError, IndexError) as e:
                print(f"  Warning: Error parsing with {description}: {e}")
                continue
    
    # If we get here, parsing failed
    raise ValueError(
        f"Could not parse MM-PBSA energy from {output_file}. "
        f"Tried strategies: {', '.join(s[1] for s in strategies)}"
    )

def compute_mm_gbsa(complex_name, replicate_dir, ligand_resname='LIG', timeout=3600):
    """
    Compute MM-GBSA binding free energy using AMBERTools MMPBSA.py.

    Strategy:
      1. Use gmx_MMPBSA as a GROMACS->AMBER format converter to produce
         AMBER-format topology and trajectory files.
      2. Run MMPBSA.py (AMBERTools 23) natively for the actual calculation.
         This gives the better-validated AMBER MM-GBSA implementation.

    igb=2 (OBC model), 500 snapshots from last 50 ns, per-residue decomposition.

    Args:
        complex_name: Name of complex
        replicate_dir: Path to replicate directory
        ligand_resname: Residue name of ligand
        timeout: Timeout in seconds (default 1 hour)

    Returns:
        Energy in kcal/mol or None if calculation fails
    """
    tpr_file = replicate_dir / "production.tpr"
    xtc_file = replicate_dir / "production.xtc"
    index_file = replicate_dir / "index.ndx"
    mmpbsa_out = replicate_dir / "FINAL_RESULTS_MMPBSA.dat"

    # Validate input files exist
    if not tpr_file.exists() or not xtc_file.exists():
        print("  Warning: Trajectory files not found for MM-GBSA calculation")
        return None

    # Create index file
    cmd = f"{GMX_BIN} make_ndx -f {tpr_file} -o {index_file}"
    if not run_gmx_command(cmd, f"r {ligand_resname}\nq\n".encode()):
        print("  Warning: Failed to create index file for MM-GBSA")
        return None

    # Calculate number of frames for MM-GBSA (use last 50 ns, roadmap Step 12)
    # Dynamically calculate frame indices based on trajectory
    startframe = 0
    interval = 10
    
    try:
        import MDAnalysis as mda
        u = mda.Universe(str(tpr_file), str(xtc_file))
        total_frames = u.trajectory.n_frames
        total_ns = total_frames * OUTPUT_INTERVAL_PS / 1000.0
        
        # Skip first 50% of trajectory, use last 50 ns (roadmap Step 12)
        if total_ns > 100:
            frames_to_skip = int((total_ns - 50) / OUTPUT_INTERVAL_PS)
            startframe = max(0, frames_to_skip)
        else:
            # Use last 50% of trajectory if < 100 ns
            startframe = max(0, int(0.5 * total_frames))
        
        interval = max(1, int(10 / OUTPUT_INTERVAL_PS))  # Sample every ~10 ps
    except Exception as e:
        print(f"  Warning: Could not calculate frames dynamically: {e}")
        # Safe fallback: skip first 20% rather than starting at frame 0
        # (avoids including non-equilibrated frames when trajectory length is unknown)
        startframe = 200  # ~20 ns at 10 ps/frame
        interval = 10
        print(f"  Using conservative fallback: startframe={startframe}, interval={interval}")

    # Create input file for MMPBSA.py (AMBERTools 23)
    # Check if this is a transmembrane protein (PfCRT/PfATP4)
    is_membrane = any(x in str(complex_name) for x in ["PfCRT", "PfATP4", "6UKJ", "9N10"])
    gb_model = 8 if is_membrane else 2
    memb_params = "\nmembrane=1,\nmemb_thickness=30.0," if is_membrane else ""

    mmpbsa_in = replicate_dir / "mmpbsa.in"
    with open(mmpbsa_in, 'w') as f:
        f.write(f"""&general
startframe={startframe}, endframe=0, interval={interval},
verbose=1, keep_files=0,
/
&gb
igb={gb_model}, saltcon=0.15,{memb_params}
/
""")

    # Step 1: Use gmx_MMPBSA as format converter (GROMACS -> AMBER)
    # This produces AMBER-format topology (.prmtop) and trajectory (.nc)
    print("  Step 1: Converting GROMACS files to AMBER format via gmx_MMPBSA...")
    convert_cmd = (
        f"gmx_MMPBSA -O -i {mmpbsa_in} -cs {tpr_file} -ci {index_file} "
        f"-cg 1 1 -ct {xtc_file} --rewrite-input"
    )

    # Step 2: Run MMPBSA.py natively if AMBER topology files were produced
    amber_top = replicate_dir / "_GMXMMPBSA_complex.prmtop"
    amber_traj = replicate_dir / "_GMXMMPBSA_complex_traj.nc"

    print(f"  Running MM-GBSA calculation via AMBERTools MMPBSA.py (timeout: {timeout}s)...")
    try:
        # Run gmx_MMPBSA (converter + calculation in one step if MMPBSA.py not separately available)
        result = subprocess.run(
            convert_cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(replicate_dir)
        )

        if result.returncode != 0:
            print(f"  Warning: gmx_MMPBSA returned non-zero exit code: {result.returncode}")
            if result.stderr:
                print(f"  Error: {result.stderr[:200]}")

        # If AMBER files exist, run MMPBSA.py directly for better-validated output
        if amber_top.exists() and amber_traj.exists():
            mmpbsa_direct_cmd = (
                f"MMPBSA.py -O -i {mmpbsa_in} "
                f"-cp {amber_top} -ct {amber_traj} "
                f"-o {replicate_dir / 'FINAL_RESULTS_MMPBSA.dat'} "
                f"-eo {replicate_dir / 'FINAL_RESULTS_MMPBSA.csv'}"
            )
            result = subprocess.run(
                mmpbsa_direct_cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(replicate_dir)
            )
            if result.returncode != 0:
                print(f"  Warning: MMPBSA.py direct run failed: {result.stderr[:200]}")

    except subprocess.TimeoutExpired:
        print(f"  Warning: MM-GBSA calculation timed out after {timeout}s")
        return None

    # Parse output
    if mmpbsa_out.exists():
        try:
            energy = parse_mmpbsa_energy(mmpbsa_out)
            print(f"  MM-GBSA energy: {energy:.1f} kcal/mol")
            return energy
        except (FileNotFoundError, ValueError) as e:
            print(f"  Warning: MM-GBSA parsing failed: {e}")
            return None
    else:
        print(f"  Warning: MM-GBSA output file not found: {mmpbsa_out}")
        return None

def analyse_complex(complex_name):
    """
    Analyse all replicates for a complex.
    
    Auto-detects ligand residue name and calculates frame counts dynamically.
    """
    complex_dir = MD_DIR / complex_name
    if not complex_dir.exists():
        print(f"  Warning: {complex_name} directory not found")
        return None

    # Auto-detect ligand residue name if needed
    ligand_resname = COMPLEXES[complex_name]['ligand_resname']
    if ligand_resname is None:
        topology_file = complex_dir / "topol.top"
        if topology_file.exists():
            ligand_resname = get_ligand_resname_from_topology(str(topology_file))
            print(f"  Auto-detected ligand residue name: {ligand_resname}")
        else:
            ligand_resname = 'LIG'
            print(f"  Using default ligand residue name: {ligand_resname}")
    
    key_residues = COMPLEXES[complex_name]['key_residues']

    results = {
        'complex': complex_name,
        'bb_rmsd_means': [],
        'lig_rmsd_means': [],
        'rmsf_means': [],
        'hbond_means': [],
        'mm_gbsa_means': [],
    }

    for rep in range(1, N_REPLICATES + 1):
        rep_dir = complex_dir / f"replicate_{rep}"
        if not rep_dir.exists():
            print(f"  Warning: replicate {rep} not found for {complex_name}")
            continue

        print(f"  Analysing {complex_name} replicate {rep}...")

        # RMSD
        bb_rmsd, lig_rmsd = compute_rmsd(complex_name, rep_dir, ligand_resname)
        if bb_rmsd is not None:
            # Calculate frame count dynamically for last 50 ns (roadmap Step 12)
            frames_last_50ns = int(50 / OUTPUT_INTERVAL_PS)
            frames_last_50ns = min(frames_last_50ns, len(bb_rmsd))
            if frames_last_50ns > 0:
                results['bb_rmsd_means'].append(bb_rmsd[-frames_last_50ns:].mean())
                results['lig_rmsd_means'].append(lig_rmsd[-frames_last_50ns:].mean())
            else:
                print(f"    Warning: Not enough frames for {complex_name} replicate {rep}")

        # RMSF
        rmsf = compute_rmsf(complex_name, rep_dir)
        if rmsf is not None:
            results['rmsf_means'].append(rmsf)

        # H-bonds
        hbonds = compute_hbonds(complex_name, rep_dir, key_residues, ligand_resname)
        if hbonds is not None:
            results['hbond_means'].append(hbonds.mean())

        # MM-GBSA
        mm_gbsa = compute_mm_gbsa(complex_name, rep_dir, ligand_resname)
        if mm_gbsa is not None:
            results['mm_gbsa_means'].append(mm_gbsa)

    # Compute statistics
    stats = {
        'complex': complex_name,
        'bb_rmsd_mean': np.mean(results['bb_rmsd_means']) if results['bb_rmsd_means'] else None,
        'bb_rmsd_std': np.std(results['bb_rmsd_means']) if results['bb_rmsd_means'] else None,
        'lig_rmsd_mean': np.mean(results['lig_rmsd_means']) if results['lig_rmsd_means'] else None,
        'lig_rmsd_std': np.std(results['lig_rmsd_means']) if results['lig_rmsd_means'] else None,
        'hbond_mean': np.mean(results['hbond_means']) if results['hbond_means'] else None,
        'hbond_std': np.std(results['hbond_means']) if results['hbond_means'] else None,
        'mm_gbsa_mean': np.mean(results['mm_gbsa_means']) if results['mm_gbsa_means'] else None,
        'mm_gbsa_std': np.std(results['mm_gbsa_means']) if results['mm_gbsa_means'] else None,
    }

    return stats

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", help="Run trajectory analysis commands")
    parser.add_argument("--dry-run", action="store_true", help="Explicitly retain dry-run mode")
    args = parser.parse_args()
    if args.execute and args.dry_run:
        raise SystemExit("--execute and --dry-run cannot be combined")
    if N_REPLICATES < 1:
        raise SystemExit("P2_MD_REPLICATES must be a positive integer")
    if not args.execute:
        print("[DRY RUN] Trajectory analysis is disabled by default; no GROMACS command was launched.")
        print("Pass --execute and P2_MD_EXECUTE_CONFIRM=I_UNDERSTAND for an authorized future analysis.")
        return
    if os.environ.get("P2_MD_EXECUTE_CONFIRM") != "I_UNDERSTAND":
        raise SystemExit("--execute requires P2_MD_EXECUTE_CONFIRM=I_UNDERSTAND; no GROMACS command was launched.")
    provenance = PROJECT_DIR / "MD_systems" / "parent_md_run_manifest.json"
    if not provenance.is_file():
        raise SystemExit(f"FAIL-CLOSED: missing parent MD provenance manifest: {provenance}")
    print("=" * 60)
    print("MD Trajectory Analysis")
    print("=" * 60)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    all_stats = []

    for complex_name in COMPLEXES:
        print(f"\nAnalysing {complex_name}...")
        stats = analyse_complex(complex_name)
        if stats:
            all_stats.append(stats)

    # Save results
    if all_stats:
        df = pd.DataFrame(all_stats)
        df.to_csv(RESULTS_DIR / "md_analysis_summary.csv", index=False)
        print(f"\nSaved analysis summary to {RESULTS_DIR / 'md_analysis_summary.csv'}")

        # Print summary
        print("\n" + "=" * 60)
        print("Analysis Summary")
        print("=" * 60)
        for stats in all_stats:
            print(f"\n{stats['complex']}:")
            if stats['bb_rmsd_mean']:
                print(f"  Backbone RMSD: {stats['bb_rmsd_mean']:.2f} ± {stats['bb_rmsd_std']:.2f} Å")
            if stats['lig_rmsd_mean']:
                print(f"  Ligand RMSD: {stats['lig_rmsd_mean']:.2f} ± {stats['lig_rmsd_std']:.2f} Å")
            if stats['mm_gbsa_mean']:
                print(f"  MM-GBSA ΔG: {stats['mm_gbsa_mean']:.1f} ± {stats['mm_gbsa_std']:.1f} kcal/mol")

    print("\n" + "=" * 60)
    print("Analysis complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
