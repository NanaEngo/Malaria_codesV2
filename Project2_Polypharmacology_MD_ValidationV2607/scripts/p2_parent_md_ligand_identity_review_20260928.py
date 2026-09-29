#!/usr/bin/env python3
"""Parent-MD ligand identity review (2026-09-28).

Question: do the four parent-study production-MD systems
(201_PfDHFR, 214_PfCRT, 438_PfATP4, 164_PfClpP) contain the molecules
named by the manuscript claim "parent-study consensus leads
(Ligands 201, 214, 438, 164)"?

Checks (all asserted):
  1. Production ground truth = UNL composition of complex_boxed.gro,
     cross-checked against a second per-system ligand PDB artifact.
  2. Ground-truth formula == all_molecules.csv row formula at the
     dir-claimed index (scheme B, 0-based) -- and the known off-by-one
     for the 438-labelled system (content = index 437, Temefos).
  3. Docking/consensus universe (scheme A, data/pdb_ligands) formulas
     for the same labels differ from production content.
  4. Set-C disjointness: production molecules not among PP-01..17.
  5. Receptor correspondence: prepared receptor CA counts == chain-A
     CA counts of the named PDB reference structures.

Outputs -> results/parent_md_ligand_identity_review_20260928/
  REVIEW.md, ligand_identity_review.csv, receptor_correspondence.csv,
  summary.json
ponytail: re-runnable audit; asserts fire if any identity drifts.
"""
import csv
import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from rdkit import Chem, RDLogger
from rdkit.Chem import rdMolDescriptors

RDLogger.DisableLog("rdApp.*")

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "parent_md_ligand_identity_review_20260928"
ALL_MOL = ROOT / "data/from_project1/data/raw/all_molecules.csv"
A_LIGDIR = ROOT / "data/from_project1/data/pdb_ligands"
PROTEINS = ROOT / "data/proteins"
SETC_CSV = ROOT / "results/c_rrs_classification.csv"

# system dir -> (PDB id, dir-claimed label, expected production formula,
#                scheme-B index expected, cross-check file,
#                scheme-A label formula (heavy), prepared receptor file, ref chain-A CA)
SYSTEMS = {
    "201_PfDHFR": dict(pdb="7F3Y", label=201, formula="C42H38O23",
                       b_index=201, cross="_MMPBSA_ligand.pdb",
                       a_label=201, a_heavy="C22N2O2",
                       prepared="7F3Y_prepared.pdb", ca=549),
    "214_PfCRT": dict(pdb="6UKJ", label=214, formula="C13H12O4",
                      b_index=214, cross="complex_214.pdb",
                      a_label=214, a_heavy="C20N4O3S",
                      prepared="6UKJ_prepared.pdb", ca=350),
    "438_PfATP4": dict(pdb="9N10", label=438, formula="C16H20O6P2S3",
                       b_index=437, cross="_MMPBSA_ligand.pdb",
                       a_label=438, a_heavy="C15ClN4O",
                       prepared="9N10_prepared.pdb", ca=985),
    "164_PfClpP": dict(pdb="4GM2", label=164, formula="C15H10O7",
                       b_index=164, cross="_MMPBSA_ligand.pdb",
                       a_label=164, a_heavy="C20O6",
                       prepared="4GM2_prepared.pdb", ca=183),
}
# off-by-one: content of 438-labelled system must equal B-437, not B-438
B_438_FORMULA = "C14H12F7N5S"  # DSM-265
AA3 = {"ALA", "ARG", "ASN", "ASP", "CYS", "GLN", "GLU", "GLY", "HIS", "ILE",
       "LEU", "LYS", "MET", "PHE", "PRO", "SER", "THR", "TRP", "TYR", "VAL",
       "HID", "HIE", "HIP", "CYX", "ASH", "GLH", "LYN"}


def _elem_from_name(name: str):
    n = name.strip().lstrip("0123456789")
    if not n:
        return None
    if n[:2].upper() in ("CL", "BR"):
        return n[:2].upper().capitalize()
    return n[0].upper()


def hill(cnt: Counter) -> str:
    parts = []
    for e in ("C", "H"):
        if cnt.get(e):
            parts.append(e + (str(cnt[e]) if cnt[e] > 1 else ""))
    for e in sorted(k for k in cnt if k not in ("C", "H")):
        parts.append(e + (str(cnt[e]) if cnt[e] > 1 else ""))
    return "".join(parts)


def heavy(formula: str) -> str:
    cnt = Counter()
    for sym, n in re.findall(r"([A-Z][a-z]?)(\d*)", formula):
        if sym:
            cnt[sym] += int(n) if n else 1
    del cnt["H"]
    return hill(cnt)


def pdb_formula(path: Path, unl_only: bool = False) -> str:
    cnt = Counter()
    lig_res = None
    lines = path.read_text(errors="replace").splitlines()
    if unl_only:
        resnames = {ln[17:20].strip().upper() for ln in lines if len(ln) > 20}
        lig_res = ({"UNL"} if "UNL" in resnames
                   else {"LIG"} if "LIG" in resnames else None)
    for ln in lines:
        if not ln.startswith(("ATOM", "HETATM")):
            continue
        res = ln[17:20].strip().upper()
        if res in ("HOH", "WAT", "SOL"):
            continue
        if lig_res is not None and res not in lig_res:
            continue
        if lig_res is None and res in AA3:
            continue
        el = ln[76:78].strip().upper() if len(ln) >= 78 else ""
        if el:
            el = el.capitalize() if el in ("CL", "BR") else el[0]
        else:
            el = _elem_from_name(ln[12:16])
        if el:
            cnt[el] += 1
    return hill(cnt)


def gro_unl_formula(path: Path) -> str:
    cnt = Counter()
    for ln in path.read_text(errors="replace").splitlines():
        if len(ln) < 15 or ln[5:10].strip().upper() not in ("UNL", "LIG"):
            continue
        el = _elem_from_name(ln[10:15])
        if el:
            cnt[el] += 1
    return hill(cnt)


def ca_count(path: Path, chain=None) -> int:
    n = 0
    for ln in path.read_text(errors="replace").splitlines():
        if ln.startswith(("ATOM", "HETATM")) and ln[12:16].strip() == "CA":
            if chain is None or (len(ln) > 21 and ln[21] == chain):
                n += 1
    return n


def main():
    OUT.mkdir(parents=True, exist_ok=True)

    # scheme B table
    b_rows = list(csv.DictReader(ALL_MOL.open()))
    b_formula = []
    for r in b_rows:
        smi = r.get("standard_smiles") or r.get("Smiles")
        m = Chem.MolFromSmiles(smi)
        assert m, f"bad SMILES row {r.get('Name')}"
        b_formula.append(rdMolDescriptors.CalcMolFormula(m))

    setc = [row["smiles"] for row in csv.DictReader(SETC_CSV.open())]
    setc_can = {Chem.MolToSmiles(Chem.MolFromSmiles(s)) for s in setc}

    lig_rows, rec_rows, findings = [], [], []
    for sysname, spec in SYSTEMS.items():
        sdir = ROOT / "MD_systems" / sysname
        box = sdir / "complex_boxed.gro"
        assert box.exists(), box
        f_box = gro_unl_formula(box)
        f_cross = pdb_formula(sdir / spec["cross"], unl_only=True)
        agree = f_box == f_cross
        assert agree, f"{sysname}: box {f_box} != cross {f_cross}"
        assert f_box == spec["formula"], f"{sysname}: {f_box} != {spec['formula']}"

        # scheme B identity
        f_b = b_formula[spec["b_index"]]
        b_ok = f_b == f_box
        assert b_ok, f"{sysname}: B-{spec['b_index']} {f_b} != {f_box}"
        b_name = b_rows[spec["b_index"]]["Name"][:60]
        off_by_one = spec["label"] != spec["b_index"]
        if off_by_one:
            assert b_formula[spec["label"]] == B_438_FORMULA
            assert b_formula[spec["label"]] != f_box

        # scheme A label content
        f_a = pdb_formula(A_LIGDIR / f"ligand_{spec['a_label']}.pdb")
        a_heavy_ok = heavy(f_a) == spec["a_heavy"]
        assert a_heavy_ok, f"A-{spec['a_label']}: {heavy(f_a)} != {spec['a_heavy']}"
        a_differs = heavy(f_a) != heavy(f_box)
        assert a_differs, f"{sysname}: scheme-A content unexpectedly == production"

        # Set-C disjointness
        smi_b = b_rows[spec["b_index"]].get("standard_smiles") or b_rows[spec["b_index"]]["Smiles"]
        can = Chem.MolToSmiles(Chem.MolFromSmiles(smi_b))
        disjoint = can not in setc_can
        assert disjoint, f"{sysname}: molecule present in Set-C"

        # receptor correspondence
        prep = sdir / spec["prepared"]
        assert prep.exists(), prep
        n_prep = ca_count(prep)
        n_ref = ca_count(PROTEINS / f"{spec['pdb']}.pdb", chain="A")
        rec_ok = n_prep == n_ref == spec["ca"]
        assert rec_ok, f"{sysname}: CA prep {n_prep} refA {n_ref} exp {spec['ca']}"

        lig_rows.append(dict(
            system=sysname, pdb=spec["pdb"], dir_label=spec["label"],
            production_formula=f_box, cross_check_file=spec["cross"],
            cross_check_formula=f_cross, box_cross_agree=agree,
            b_index=spec["b_index"], b_index_formula=f_b, b_name=b_name,
            off_by_one=off_by_one,
            a_label=spec["a_label"], a_formula=f_a,
            a_differs_from_production=a_differs,
            setc_disjoint=disjoint,
            verdict="CONTENT_MISMATCH_DIR_LABEL" if off_by_one
                    else "CONTENT_IS_B_INDEX_NOT_A_CONSENSUS_LEAD",
        ))
        rec_rows.append(dict(
            system=sysname, pdb=spec["pdb"], prepared_file=spec["prepared"],
            prepared_ca=n_prep, ref_chainA_ca=n_ref, match=rec_ok))

        findings.append(f"{sysname}: production {f_box} = B-{spec['b_index']} ({b_name}); "
                        f"dir label {spec['label']} claims A-{spec['a_label']} "
                        f"({f_a}) -> {'off-by-one; ' if off_by_one else ''}"
                        f"NOT the A-consensus-lead molecule; receptor {spec['pdb']} chain A {n_prep}/{n_ref} PASS")

    # verdict: every system fails the manuscript's consensus-lead claim
    n_fail = sum(1 for r in lig_rows if r["verdict"].startswith(("CONTENT_MISMATCH", "CONTENT_IS")))
    assert n_fail == 4

    def write_csv(path, rows):
        with path.open("w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)

    write_csv(OUT / "ligand_identity_review.csv", lig_rows)
    write_csv(OUT / "receptor_correspondence.csv", rec_rows)

    summary = {
        "review": "parent-MD ligand identity review",
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "status": "FAIL_MANUSCRIPT_CONSENSUS_LEAD_CLAIM_NOT_SUPPORTED",
        "receptor_correspondence": "PASS",
        "setc_disjointness": "PASS",
        "systems_reviewed": len(lig_rows),
        "systems_content_mismatch": n_fail,
        "findings": findings,
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    review = f"""# Parent-MD Ligand Identity Review
Date: {summary['date']} | Status: **{summary['status']}**

## Question
Do the four parent-study production-MD systems contain the molecules named by
the manuscript claim (main text): \"Four additional parent-study consensus
leads (Ligands 201, 214, 438, 164) were evaluated in production-MD wild-type
complexes\"?

## Method
- Production ground truth: UNL composition of `complex_boxed.gro`, cross-checked
  against a second per-system ligand artifact (MMPBSA/complex PDB); both must agree.
- Scheme B (seed-library 0-based index of `all_molecules.csv`, 850 rows) formula match.
- Scheme A (docking/consensus cluster-representative numbering,
  `data/pdb_ligands/`) label content compared against production.
- Set-C disjointness by canonical SMILES against the 17 Set-C candidates.
- Receptor correspondence: prepared-receptor CA counts vs chain A of the named PDB.
- All checks asserted; script re-run reproduces this file.

## Results
| System | Dir label | Production content (formula) | Scheme-B identity | Scheme-A label content | Verdict |
|---|---|---|---|---|---|
"""
    for r in lig_rows:
        review += (f"| {r['system']} | {r['dir_label']} | {r['production_formula']} | "
                   f"B-{r['b_index']} = {r['b_name'][:40]} | "
                   f"A-{r['a_label']} = {r['a_formula']} (differs) | "
                   f"{'off-by-one; ' if r['off_by_one'] else ''}"
                   f"not the named consensus lead |\n")
    review += """
## Numbering universes
- **Scheme A** = `data/pdb_ligands|pdbqt_ligands` (K-Means cluster representatives):
  the universe used by ALL docking runs and by the README \"Named Consensus Hits\"
  (201/214/87/438/164). Consensus scores in this numbering: 201 7F3Y -8.49 (GOOD).
- **Scheme B** = `data/ligands/pdb` 0-based index of `all_molecules.csv`
  (396 natural products + 454 synthetic). **Production MD content is scheme B.**
- **Scheme C** = `pdb_ligands_mmv` (MMV consensus) - not involved.

## Verdict
1. **NONE of the four production systems contains its named scheme-A
   consensus-lead molecule.** Production molecules are B-201 (pentaacetyl
   glycoside, C42H38O23), B-214 (C13H12O4), **B-437 (Temefos, C16H20O6P2S3)
   inside the 438-labelled directory - off-by-one**, B-164 (aurone acetate,
   C15H10O7).
2. The manuscript consensus-lead claim is therefore **not supported** under
   every consistent reading; scheme-B indices carry no consensus-lead status.
3. Stale preparation files contradict production (do not use for claims):
   201 `complex.pdb`/`ligand_201.mol2` (2026-07-10) contain a different
   molecule (oxindole, scheme-A index 307) vs the 2026-07-06 production box;
   214 `complex.pdb` (07-10) contains a third unidentified molecule;
   438 `ligand/ligand_438.mol2|pdb` contain DSM-265 (B-438) while production
   simulated Temefos (B-437). Production artifacts (box + MMPBSA) are internally
   consistent per system.
4. **Receptor correspondence PASS**: prepared receptors match chain A CA counts
   of 7F3Y (549), 6UKJ (350), 9N10 (985), 4GM2 (183) - supports \"the 164
   system represents PfClpR (PDB 4GM2)\".
5. Set-C disjointness PASS: none of the four production molecules is among the
   17 Set-C candidates.

## Recommended manuscript fix (author decision pending)
Replace the consensus-lead wording with an honest provenance statement, e.g.
\"four parent-study library complexes (upstream indices 201, 214, 437, 164; the
438-labelled system contains index 437) were evaluated in production-MD
wild-type complexes\" - or drop the labels entirely and cite the archived
identity review.

## Provenance
- Script: `scripts/p2_parent_md_ligand_identity_review_20260928.py`
  sha256 {summary['script_sha256'][:16]}...
- Outputs: this directory (versioned; nothing overwritten).
- `results/metrics/parent_md_source_inventory.json` remains FAIL_CLOSED
  untouched by this review.
"""
    (OUT / "REVIEW.md").write_text(review)
    print(f"OK: {n_fail}/4 systems content mismatch; receptor PASS; outputs in {OUT}")


if __name__ == "__main__":
    main()
