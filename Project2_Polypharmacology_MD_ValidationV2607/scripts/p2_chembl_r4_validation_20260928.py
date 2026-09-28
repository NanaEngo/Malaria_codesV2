#!/usr/bin/env python3
"""R4 external anchor — ChEMBL PfDHFR genotype IC50 fold-shifts vs in-silico Vina ddG.

Stages: build | ligands | dock | analyze | all
Frozen inputs, versioned outputs (AGENTS.md §4). No canonical result is overwritten.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "chembl_r4_validation_20260928"
IN = OUT / "inputs"
REC = OUT / "receptors"
LIG = OUT / "ligands"
DOCK = OUT / "docking"
ANA = OUT / "analysis"

WT_PDB = ROOT / "results/md_systems/set_c_preparation_20260812_v1/PP-01_PfDHFR_WT/receptor_fixed.pdb"
OBABEL = "/home/nanaengo/miniforge3/envs/malaria_md/bin/obabel"
PY = "/home/nanaengo/miniforge3/envs/malaria_md/bin/python"
VINA = "/usr/local/bin/vina"

# V2 grid of PfDHFR (manifest pp01_multiseed_pfdhfr_wt, 2026-08-29) — same frame as mutants
BOX = {"center_x": -1.696, "center_y": -6.841, "center_z": -62.139,
       "size_x": 25.0, "size_y": 25.0, "size_z": 25.0}
EXHAUSTIVENESS = 64   # paper Methods (L210)
SEED = 42

# genotype -> (chain mutations, source residue names)
STATES = {
    "WT": {},
    "DOUBLE": {"A": ["CYS-59-ARG", "SER-108-ASN"], "B": ["CYS-59-ARG", "SER-108-ASN"]},
    "TRIPLE": {"A": ["CYS-59-ARG", "SER-108-ASN", "ILE-164-LEU"],
               "B": ["CYS-59-ARG", "SER-108-ASN", "ILE-164-LEU"]},
    "QUAD": {"A": ["ASN-51-ILE", "CYS-59-ARG", "SER-108-ASN", "ILE-164-LEU"],
             "B": ["ASN-51-ILE", "CYS-59-ARG", "SER-108-ASN", "ILE-164-LEU"]},
}


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        raise RuntimeError(f"{' '.join(map(str, cmd[:6]))}... rc={r.returncode}\n{r.stderr[-800:]}")
    return r


def write_manifest(stage: str, extra: dict):
    OUT.mkdir(parents=True, exist_ok=True)
    mf = OUT / "manifest.json"
    data = json.loads(mf.read_text()) if mf.exists() else {"stages": {}}
    data["stages"][stage] = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "script_sha256": sha256(Path(__file__)),
        **extra,
    }
    mf.write_text(json.dumps(data, indent=2))


# ── Stage: build combo mutant receptors ───────────────────────────────────────
def build():
    REC.mkdir(parents=True, exist_ok=True)
    for state, muts in STATES.items():
        pdb = REC / f"PfDHFR_{state}.pdb"
        pdbqt = REC / f"PfDHFR_{state}.pdbqt"
        if not pdb.exists():
            script = f"""
from pdbfixer import PDBFixer
from openmm.app import PDBFile
f = PDBFixer(filename={str(WT_PDB)!r})
muts = {muts!r}
for chain, mlist in muts.items():
    if mlist:
        f.applyMutations(mlist, chain)
f.findMissingResidues()
f.missingResidues = dict()   # ponytail: no loop rebuilding, keep crystal gaps as-is
f.findMissingAtoms()
f.addMissingAtoms()
f.addMissingHydrogens(7.0)
with open({str(pdb)!r}, 'w') as fh:
    PDBFile.writeFile(f.topology, f.positions, fh)
print("wrote", {str(pdb)!r})
"""
            run([PY, "-c", script])
        if not pdbqt.exists():
            run([OBABEL, str(pdb), "-opdbqt", "-O", str(pdbqt), "--partialcharge", "gasteiger"])
            # Vina 1.2.7 rigid receptor must be a plain atom list (no flex tree)
            txt = pdbqt.read_text().splitlines(True)
            skip = ("ROOT", "ENDROOT", "BRANCH", "ENDBRANCH", "TORSDOF")
            pdbqt.write_text("".join(l for l in txt if not l.startswith(skip)))
        print(f"  receptor {state}: {pdb.stat().st_size} B pdb / {pdbqt.stat().st_size} B pdbqt")
    write_manifest("build", {"wt_input": str(WT_PDB), "wt_sha256": sha256(WT_PDB),
                             "box": BOX, "exhaustiveness": EXHAUSTIVENESS, "seed": SEED,
                             "note": "combo mutants built from the paper's WT receptor (chains A+B) by side-chain substitution; no loop modelling, no minimization (ponytail: docking-level model)"})
    print("build OK")


# ── Stage: ligand preparation (same recipe as paper: RDKit embed + MMFF94 + Meeko)
def ligands():
    LIG.mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader(open(IN / "paired_set.csv")))
    script = """
import sys, csv, json
from rdkit import Chem
from rdkit.Chem import AllChem
from meeko import MoleculePreparation, PDBQTWriterLegacy
ligdir = sys.argv[1]
rows = list(csv.DictReader(open(sys.argv[2])))
ok, bad = [], []
for r in rows:
    cid, smi = r["chembl_id"], r["smiles"]
    out = f"{ligdir}/{cid}.pdbqt"
    if not smi:
        bad.append((cid, "no smiles")); continue
    mol = Chem.MolFromSmiles(smi)
    if mol is None:
        bad.append((cid, "smiles parse")); continue
    mol = Chem.AddHs(mol)
    if AllChem.EmbedMolecule(mol, randomSeed=42) != 0:
        bad.append((cid, "embed")); continue
    AllChem.MMFFOptimizeMolecule(mol, mmffVariant="MMFF94", maxIters=200)
    try:
        setups = MoleculePreparation()(mol)
    except Exception as e:
        bad.append((cid, f"meeko {e}")); continue
    wrote = False
    for setup in setups:
        s, is_ok, err = PDBQTWriterLegacy.write_string(setup)
        if is_ok:
            open(out, "w").write(s)
            wrote = True
            break
    (ok if wrote else bad).append(cid if wrote else (cid, err))
print(json.dumps({"ok": len(ok), "failed": bad}))
"""
    r = run([PY, "-c", script, str(LIG), str(IN / "paired_set.csv")])
    res = json.loads(r.stdout.strip().splitlines()[-1])
    print(f"  ligands ok={res['ok']} failed={res['failed']}")
    write_manifest("ligands", res)


# ── Stage: docking ────────────────────────────────────────────────────────────
def _dock_one(lig_id: str, state: str, cpu: int = 4) -> dict:
    rec = REC / f"PfDHFR_{state}.pdbqt"
    lig = LIG / f"{lig_id}.pdbqt"
    out = DOCK / f"{lig_id}__{state}.pdbqt"
    log = DOCK / f"{lig_id}__{state}.out.txt"
    if out.exists() and log.exists():
        aff = None
        for line in out.read_text().splitlines():
            m = re.search(r"REMARK VINA RESULT:\s+(-?\d+\.\d+)", line)
            if m:
                aff = float(m.group(1))
                break
        return {"lig": lig_id, "state": state, "status": "CACHED", "affinity": aff}
    cmd = [VINA, "--receptor", str(rec), "--ligand", str(lig),
           "--center_x", str(BOX["center_x"]), "--center_y", str(BOX["center_y"]),
           "--center_z", str(BOX["center_z"]),
           "--size_x", str(BOX["size_x"]), "--size_y", str(BOX["size_y"]),
           "--size_z", str(BOX["size_z"]),
           "--exhaustiveness", str(EXHAUSTIVENESS), "--num_modes", "1",
           "--seed", str(SEED), "--cpu", str(cpu), "--out", str(out)]
    try:
        r = run(cmd)
        log.write_text(r.stdout + r.stderr)
        aff = None
        for line in out.read_text().splitlines():
            m = re.search(r"REMARK VINA RESULT:\s+(-?\d+\.\d+)", line)
            if m:
                aff = float(m.group(1))
                break
        return {"lig": lig_id, "state": state, "status": "OK" if aff is not None else "NO_SCORE",
                "affinity": aff}
    except Exception as e:
        return {"lig": lig_id, "state": state, "status": "FAILED", "error": str(e)[:200]}


def dock(limit=None, workers=8, cpu=4):
    DOCK.mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader(open(IN / "paired_set.csv")))
    lig_ids = [r["chembl_id"] for r in rows][:limit]
    tasks = [(l, s) for l in lig_ids for s in STATES]
    print(f"  {len(tasks)} docking jobs ({len(lig_ids)} ligands x {len(STATES)} states)")
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=workers) as ex:
        res = list(ex.map(lambda t: _dock_one(t[0], t[1], cpu), tasks))
    scores = [r for r in res if r["status"] in ("OK", "CACHED") and r.get("affinity") is not None]
    fails = [r for r in res if r["status"] not in ("OK", "CACHED")]
    with open(OUT / "docking_scores.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["lig", "state", "affinity", "status"])
        w.writeheader()
        for r in res:
            if r.get("affinity") is not None:
                w.writerow({"lig": r["lig"], "state": r["state"],
                            "affinity": r["affinity"], "status": r["status"]})
    print(f"  done in {(time.time()-t0)/60:.1f} min  scores={len(scores)} fails={len(fails)}")
    for r in fails[:10]:
        print("   ", r)
    write_manifest("dock", {"n_jobs": len(tasks), "n_scores": len(scores),
                            "n_failed": len(fails), "wall_min": round((time.time()-t0)/60, 1)})


# ── Stage: analysis ───────────────────────────────────────────────────────────
def analyze():
    ANA.mkdir(parents=True, exist_ok=True)
    meta = {r["chembl_id"]: r for r in csv.DictReader(open(IN / "paired_set.csv"))}
    sc = {}
    for r in csv.DictReader(open(OUT / "docking_scores.csv")):
        sc.setdefault(r["lig"], {})[r["state"]] = float(r["affinity"])

    def ddg(lig, state):  # mutant weaker binding = positive ddG = predicted resistance
        if lig not in sc or "WT" not in sc[lig] or state not in sc[lig]:
            return None
        return sc[lig][state] - sc[lig]["WT"]

    def fnum(x):
        try:
            return float(x)
        except (TypeError, ValueError):
            return None

    from math import log2, comb
    from scipy.stats import spearmanr

    def _stats(rows):
        e = [r["exp_log2_fold"] for r in rows]
        p_ = [r["vina_ddG"] for r in rows]
        agree = [r["direction_agree"] for r in rows]
        n, n_agree = len(agree), sum(agree)
        rho, p = spearmanr(e, p_) if n > 2 else (None, None)
        k = max(n_agree, n - n_agree) if n else 0
        return {
            "n_paired": n,
            "spearman_rho_log2fold_vs_ddG": None if rho is None else round(float(rho), 4),
            "spearman_p": None if p is None else round(float(p), 4),
            "direction_agreement": f"{n_agree}/{n}",
            "direction_agreement_fraction": round(n_agree / n, 3) if n else None,
            "binomial_p_one_sided": round(sum(comb(n, i) for i in range(k, n + 1)) / 2 ** n, 4) if n else None,
        }

    all_rows, per_geno = [], {}
    for state in ("DOUBLE", "TRIPLE", "QUAD"):
        g = state.lower()
        rows = []
        for cid, m in sorted(meta.items()):
            wt, mut = fnum(m["wt"]), fnum(m.get(g))
            d = ddg(cid, state)
            if not wt or not mut or d is None:
                continue
            fold = mut / wt
            rows.append({"genotype": g, "chembl_id": cid, "name": m["name"],
                         "wt_nM": wt, f"{g}_nM": mut,
                         "exp_fold": round(fold, 3), "exp_log2_fold": round(log2(fold), 3),
                         "vina_WT": sc[cid]["WT"], f"vina_{state}": sc[cid][state],
                         "vina_ddG": round(d, 3),
                         "pred_resistant": int(d > 0), "exp_resistant": int(fold > 1.0),
                         "direction_agree": int((d > 0) == (fold > 1.0))})
        all_rows.extend(rows)
        st = _stats(rows)
        known = [t for t in rows if re.search(
            r"pyrimethamine|cycloguanil|trimethoprim|etoprine|fanotaprim|methotrexate|proguanil|chlorcyclo",
            t["name"] or "", re.I)]
        st["known_dhfr_inhibitors_subset"] = None
        if len(known) > 2:
            try:
                r2, p2 = spearmanr([t["exp_log2_fold"] for t in known],
                                   [t["vina_ddG"] for t in known])
                st["known_dhfr_inhibitors_subset"] = {
                    "n": len(known), "names": [t["name"] for t in known],
                    "rho": round(float(r2), 4), "p": round(float(p2), 4),
                    "direction_agreement": f"{sum(t['direction_agree'] for t in known)}/{len(known)}"}
            except Exception as e:
                st["known_dhfr_inhibitors_subset"] = {"n": len(known), "error": str(e)}
        elif known:
            st["known_dhfr_inhibitors_subset"] = {
                "n": len(known), "names": [t["name"] for t in known],
                "rho": None, "p": None,
                "direction_agreement": f"{sum(t['direction_agree'] for t in known)}/{len(known)}"}
        per_geno[g] = st

    if all_rows:
        fields = ["genotype", "chembl_id", "name", "wt_nM", "double_nM", "triple_nM", "quad_nM",
                  "exp_fold", "exp_log2_fold", "vina_WT", "vina_DOUBLE", "vina_TRIPLE",
                  "vina_QUAD", "vina_ddG", "pred_resistant", "exp_resistant", "direction_agree"]
        with open(ANA / "foldshift_comparison.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            w.writeheader()
            w.writerows(all_rows)

    summary = {
        "per_genotype": per_geno,
        "boundary": "ChEMBL whole-parasite growth IC50 in DHFR-genotyped strains (not enzyme IC50); "
                    "strains differ in genetic background; descriptive comparison only.",
    }
    (ANA / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["build", "ligands", "dock", "analyze", "all"])
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--cpu", type=int, default=4)
    a = ap.parse_args()
    if a.stage in ("build", "all"):
        build()
    if a.stage in ("ligands", "all"):
        ligands()
    if a.stage in ("dock", "all"):
        dock(a.limit, a.workers, a.cpu)
    if a.stage in ("analyze", "all"):
        analyze()


if __name__ == "__main__":
    main()
