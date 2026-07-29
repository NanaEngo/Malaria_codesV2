#!/usr/bin/env python3
"""V2 Corrected Grid - Post-processing with provenance.

Parses docked PDBQTs into per-target CSVs and a consolidated CSV, recording the
EXHAUSTIVITY used for each row so that EXHAUSTIVITY=32 rerun tasks are
distinguishable from the original EXHAUSTIVITY=64 set.

Provenance
----------
- ``v2_submit_all.sh`` launched four pf* target arrays (pfDHFR/pfCRT/pfATP4/pfClpP)
  with EXHAUSTIVITY=64. Job 30 (v2_pfatp4) hit TIME LIMIT on 16 of 484 pfATP4
  tasks. Those 16 were resubmitted as job 2669 with EXHAUSTIVITY=32 (and a
  2-hour time-limit).
- DEKOIS outputs (``results/v2_dekois/``) are not processed here - the dekois
  pipeline has its own downstream aggregator.

Outputs
-------
- Per-target CSVs: ``results/v2_docking/{target}/scores_{target}.csv`` with
  columns ``centroid_id, vina_score, exhaustiveness, tag``.
- Consolidated CSV: ``results/v2_centroid_scores.csv`` with columns
  ``centroid_id, best_target, best_score, best_exhaustiveness, best_tag, tag,
  pfDHFR, pfCRT, pfATP4, pfClpP``.
- Versioned copy: ``results/v2_centroid_scores_v2_<YYYYMMDD>_<jobid>.csv``
  where ``<jobid>`` is ``$SLURM_JOB_ID`` (validated) when running under SLURM,
  otherwise ``local``.

Per-row provenance logic
------------------------
For ``(target_name, i)``:
- ``(RERUN_EX, 'rerun')`` if ``target_name == 'pfATP4'`` and ``i`` is in
  ``RERUN_TASK_IDS``.
- ``(ORIGINAL_EX, 'original')`` otherwise (every pfDHFR/pfCRT/pfClpP row, plus
  the 468 pfATP4 rows not in the rerun set).

Per-centroid rollup (``tag`` column in consolidated CSV): ``'mixed'`` if any
scored target within that centroid row is a rerun, else ``'original'``.

AUDIT FIX 2026-07-17 — A1+A2+A4+A5+A6:
  - parse_vina_score: try/except + line.startswith("VINA RESULT") anchor
  - wrap module-level I/O in main(); import is now side-effect-free
  - V2DIR via _find_project_root() walker with PROJECT1_BASE_DIR env-var fallback
  - explicit encoding="utf-8" on all csv.open calls
  - validate SLURM_JOB_ID default ('local' instead of literal 'None' catch)
"""

import csv
import datetime as dt
import os
from pathlib import Path


# ============================================================
# Project root resolution (depth-invariant; honours env override)
# ============================================================
def _find_project_root(start=None):
    """Walk up from ``start`` (default: this script's directory) until a
    directory whose name matches the V2 project marker is found. Returns the
    absolute Path. Raises RuntimeError if no marker is found within the
    filesystem root.

    AUDIT FIX 2026-07-17 — A4 (depth-invariant, replaces hardcoded
    ``Path("/home/nanaengo/...")``).
    """
    start = Path(__file__).resolve().parent if start is None else Path(start)
    cur = start.resolve()
    while cur != cur.parent:
        if cur.name in {
            "Project1_Chem_space_antimalarial_V2_CorrectedGrid",
            "Project1_Chem_space_antimalarialV2607",
        }:
            return cur
        cur = cur.parent
    raise RuntimeError(
        f"V2 project root not found above {start!r}. "
        f"Walked up to filesystem root without finding a "
        f"Project1_Chem_space_antimalarial_V2_CorrectedGrid directory."
    )


def _resolve_v2_dir():
    """Returns the V2 project root, with env-var override first, walker second,
    graceful CWD fallback third.

    AUDIT FIX 2026-07-17 -- A4 + DIR-DEDUP-WALKER.
    The CWD fallback (instead of SystemExit) prevents the canonical V2
    pipeline from failing in environments where neither the depth-invariant
    walker nor PROJECT1_BASE_DIR resolve a known project root -- notably
    after the DIR-DEDUP-1 move (the OLD path is now a stub README inside
    Malaria_codesV2/, not a directory walker could match against). The
    fallback is safe: V2DIR is only used as the prefix for relative
    I/O paths in main(); resolving against CWD keeps adjacency.
    """
    env = os.environ.get("PROJECT1_BASE_DIR")
    if env and Path(env).is_dir():
        return Path(env).resolve()
    try:
        return _find_project_root()
    except RuntimeError:
        # Graceful fallback: use the script's CWD. Safe because main()
        # only builds relative Paths under V2DIR (e.g. "results/v2_docking/").
        # AUDIT FIX 2026-07-17 -- DIR-DEDUP-WALKER
        return Path.cwd().resolve()


V2DIR = _resolve_v2_dir()
RESULTS = V2DIR / "results" / "v2_docking"
OUT_CSV = V2DIR / "results" / "v2_centroid_scores.csv"
N_CENTROIDS = 484

TARGETS = {
    "pfDHFR": "7F3Y",
    "pfCRT": "6UKJ",
    "pfATP4": "9N10",
    "pfClpP": "4GM2",
}

# EXHAUSTIVITY values used by the launchers:
#   v2_submit_all.sh -> --export=EXHAUSTIVITY=64        (original)
#   rerun sbatch call (job 2669) -> --export=EXHAUSTIVITY=32  (rerun)
ORIGINAL_EX = 64
RERUN_EX = 32

# Task IDs of the pfATP4 rerun, sourced from /tmp/j_pfatp4_rerun_ids.txt
# if present (created by the rerun submit block), else hard-coded fallback
# matching the sbatch --array argument.
_RERUN_FALLBACK_PATH = Path("/tmp/j_pfatp4_rerun_ids.txt")
RERUN_TASK_IDS_FALLBACK = frozenset({
    201, 204, 210, 211, 220, 249,
    320, 340, 341, 346,
    374, 375, 376, 378,
    416, 434,
})


def load_rerun_task_ids():
    p = _RERUN_FALLBACK_PATH
    if p.is_file():
        ids = set()
        for line in p.read_text().splitlines():
            line = line.strip()
            if line.isdigit():
                ids.add(int(line))
        if ids:
            return ids
    return set(RERUN_TASK_IDS_FALLBACK)


# Single side-effect on import: load the rerun IDs. Cheap, well-protected.
RERUN_TASK_IDS = load_rerun_task_ids()


def parse_vina_score(pdbqt_path):
    """Extract the Vina docking score from a .pdbqt output file.

    Vina writes the score as a REMARK line: ``REMARK VINA RESULT:  <score> ...``
    The score is the first numeric token after ``VINA RESULT:``.

    AUDIT FIX 2026-07-17 — A1: anchored to ``'VINA RESULT' in line`` (not
    ``line.startswith``) because the actual format is ``REMARK VINA RESULT:``
    and the previous ``startswith("VINA RESULT")`` never matched, causing
    0/484 scores to be parsed. Protected by try/except so that any
    non-result context cannot crash the enclosing postprocess.
    Returns None on any parse error.
    """
    try:
        with open(pdbqt_path, encoding="utf-8") as f:
            for line in f:
                if "VINA RESULT" not in line:
                    continue
                parts = line.split()
                # Format: REMARK VINA RESULT:  -5.571  0.000  0.000
                # parts[0]='REMARK' parts[1]='VINA' parts[2]='RESULT:'
                # parts[3]=score  OR  parts[2]='VINA' parts[3]='RESULT' parts[4]=score
                # Robust: find the first token that parses as float after RESULT
                found_result = False
                for tok in parts:
                    if tok.startswith("RESULT"):
                        found_result = True
                        continue
                    if found_result:
                        try:
                            return float(tok)
                        except ValueError:
                            continue
                # Fallback: if no RESULT: marker pattern, try 3rd token
                if len(parts) >= 4:
                    try:
                        return float(parts[3])
                    except ValueError:
                        pass
        return None
    except (OSError, UnicodeDecodeError):
        return None


def provenance_for(target_name, i):
    """Return (exhaustiveness:int, tag:str) for an output (target_name, i)."""
    if target_name == "pfATP4" and i in RERUN_TASK_IDS:
        return RERUN_EX, "rerun"
    return ORIGINAL_EX, "original"


# ============================================================
# Main entry point (wraps module-level I/O)
# ============================================================
def main():
    # Build the per-row dataset
    rows = []
    for target_name, _ in TARGETS.items():
        target_dir = RESULTS / target_name
        for i in range(N_CENTROIDS):
            fname = f"ligand_{i:04d}_docked.pdbqt"
            fpath = target_dir / fname
            ex, tag = provenance_for(target_name, i)
            if fpath.exists():
                score = parse_vina_score(str(fpath))
                rows.append({"centroid_id": i, "target": target_name,
                             "vina_score": score,
                             "exhaustiveness": ex, "tag": tag})
            else:
                rows.append({"centroid_id": i, "target": target_name,
                             "vina_score": None,
                             "exhaustiveness": ex, "tag": tag})

    # Per-target CSVs (explicit encoding utf-8)
    per_target_fields = ["centroid_id", "vina_score", "exhaustiveness", "tag"]
    for target_name in TARGETS:
        target_rows = [r for r in rows if r["target"] == target_name]
        csv_path = RESULTS / target_name / f"scores_{target_name}.csv"
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=per_target_fields)
            w.writeheader()
            for r in target_rows:
                w.writerow({k: r[k] for k in per_target_fields})
        scored = sum(1 for r in target_rows if r["vina_score"] is not None)
        print(f"{target_name}: {scored}/{N_CENTROIDS} docked -> {csv_path}")

    # Consolidated CSV (explicit encoding utf-8)
    consolidated = []
    for i in range(N_CENTROIDS):
        centroid_rows = [r for r in rows if r["centroid_id"] == i]
        scores = {r["target"]: r["vina_score"] for r in centroid_rows}
        valid = {t: s for t, s in scores.items() if s is not None}
        ex_by_target = {r["target"]: r["exhaustiveness"]
                        for r in centroid_rows if r["vina_score"] is not None}
        tags_by_target = {r["target"]: r["tag"]
                          for r in centroid_rows if r["vina_score"] is not None}
        best_target = min(valid, key=valid.get) if valid else None
        best_score = valid.get(best_target) if best_target else None
        best_ex = ex_by_target.get(best_target) if best_target else None
        best_tag = tags_by_target.get(best_target) if best_target else None
        has_rerun = any(t == "rerun" for t in tags_by_target.values())
        cross_tag = "mixed" if has_rerun else "original"
        consolidated.append({
            "centroid_id": i,
            **scores,
            "best_target": best_target,
            "best_score": best_score,
            "best_exhaustiveness": best_ex,
            "best_tag": best_tag,
            "tag": cross_tag,
        })

    consolidated_fields = ["centroid_id", "best_target", "best_score",
                            "best_exhaustiveness", "best_tag", "tag",
                            "pfDHFR", "pfCRT", "pfATP4", "pfClpP"]
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=consolidated_fields)
        w.writeheader()
        w.writerows(consolidated)

    print(f"\nConsolidated: {OUT_CSV}")

    # AUDIT FIX 2026-07-17 — A6: validate SLURM_JOB_ID before stamp (avoid
    # a "jobNone" filename stamp when env is set but blank).
    raw_jid = os.environ.get("SLURM_JOB_ID", "").strip()
    job_id = raw_jid if raw_jid else "local"
    stamp = dt.date.today().isoformat().replace("-", "")
    versioned = OUT_CSV.parent / f"v2_centroid_scores_v2_{stamp}_job{job_id}.csv"
    with open(versioned, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=consolidated_fields)
        w.writeheader()
        w.writerows(consolidated)

    print(f"Versioned:   {versioned}")

    n_with_score = sum(1 for c in consolidated if c["best_score"] is not None)
    n_mixed = sum(1 for c in consolidated if c["tag"] == "mixed")
    print(f"Centroids with >=1 target score: {n_with_score}/{N_CENTROIDS}")
    print(f"Centroids tagged 'mixed' (any rerun target scored): {n_mixed}")
    print(f"pfATP4 rerun rows (i in RERUN_TASK_IDS): {len(RERUN_TASK_IDS)}")


# AUDIT FIX 2026-07-17 — A2: module I/O lives in main(), not at import time.
if __name__ == "__main__":
    main()
