#!/usr/bin/env python3
"""P7 chirality probe: two falsifiable checks that any stereochemistry claim must pass.

Why this exists
---------------
The P7 audit (rev 2, §3.1 and §6.2) makes two claims that are checkable in seconds and
must not be asserted in a manuscript before they are measured:

  CHECK A -- a *default* Morgan/ECFP4-class fingerprint is constitution-only, so it cannot
             rank enantiomers; a chirality-aware fingerprint can. Any stereo benchmark
             whose classical comparator is the default fingerprint is therefore not a
             result, and the comparator must be the chirality-aware generator.

  CHECK B -- the CIP descriptor returned by `Chem.FindMolChiralCenters` is invariant to
             SMILES atom ordering, while `atom.GetChiralTag()` encodes traversal parity and
             is not. `scripts/qmse_lib/processing.py::find_rs_stereoisomers` uses the tag,
             so the encoded R/S labels of a molecule depend on where its SMILES starts,
             which propagates into the sign of the QMSE matrix diagonal.

Read-only: no files are written, no models are trained, no quantum circuit is executed.

Usage
-----
    python3 scripts/p7_chirality_fingerprint_probe.py
    python3 scripts/p7_chirality_fingerprint_probe.py --json

Exit status is 0 when both checks behave as expected -- default fingerprints cannot
separate enantiomers, chirality-aware ones can, the CIP label survives re-rooting, and at
least one raw chiral tag does not -- and 1 otherwise, so the script doubles as a
regression test for the encoder's stereochemistry path.
"""

from __future__ import annotations

import argparse
import json
import sys

from rdkit import Chem, DataStructs, rdBase
from rdkit.Chem import rdFingerprintGenerator

# Enantiomer pairs: the two entries differ only by inversion at every stereocentre.
ENANTIOMER_PAIRS = [
    ("alanine", "N[C@@H](C)C(=O)O", "N[C@H](C)C(=O)O"),
    ("threonine", "C[C@H](O)[C@@H](N)C(=O)O", "C[C@@H](O)[C@H](N)C(=O)O"),
    ("lactic acid", "C[C@H](O)C(=O)O", "C[C@@H](O)C(=O)O"),
]

# Molecules for the ordering-invariance check. Artemisinin is included because it is the
# flagship African-natural-product-like polycyclic case: 7 stereocentres in a fused,
# bridged peroxide-bearing cage.
ORDERING_MOLECULES = [
    ("alanine", "N[C@@H](C)C(=O)O"),
    ("threonine", "C[C@H](O)[C@@H](N)C(=O)O"),
    ("glucose (open chain)", "O=C[C@H](O)[C@@H](O)[C@H](O)[C@H](O)CO"),
    ("quinine", "COC1=CC2=C(C=C1)C(C3=CC=NC4=CC=CC=C34)[C@@H](O)C[C@H]2C=C"),
    ("artemisinin", "C[C@@H]1CC[C@H]2[C@@H](C)C(=O)O[C@H]3CC[C@@]4(C)OO[C@]23[C@H]1O4"),
]

UNSPECIFIED = Chem.rdchem.ChiralType.CHI_UNSPECIFIED


def _stereochemistry(mol: Chem.Mol) -> Chem.Mol:
    m = Chem.Mol(mol)
    Chem.AssignStereochemistry(m, cleanIt=True, force=True, flagPossibleStereoCenters=True)
    return m


def _cip_map(mol: Chem.Mol) -> dict[int, str]:
    return {idx: cip for idx, cip in Chem.FindMolChiralCenters(_stereochemistry(mol), includeUnassigned=True)}


def _tag_map(mol: Chem.Mol) -> dict[int, str]:
    m = _stereochemistry(mol)
    return {
        atom.GetIdx(): str(atom.GetChiralTag()).replace("CHI_TETRAHEDRAL_", "")
        for atom in m.GetAtoms()
        if atom.GetChiralTag() != UNSPECIFIED
    }


def check_a(fp_size: int = 2048, radius: int = 2) -> list[dict]:
    """Default vs chirality-aware Morgan similarity on enantiomer pairs."""
    gen_default = rdFingerprintGenerator.GetMorganGenerator(radius=radius, fpSize=fp_size)
    gen_chiral = rdFingerprintGenerator.GetMorganGenerator(
        radius=radius, fpSize=fp_size, includeChirality=True
    )
    rows = []
    for name, smi_a, smi_b in ENANTIOMER_PAIRS:
        mol_a, mol_b = Chem.MolFromSmiles(smi_a), Chem.MolFromSmiles(smi_b)
        if mol_a is None or mol_b is None:
            raise ValueError(f"unparsable SMILES for {name}")
        default_tan = float(
            DataStructs.TanimotoSimilarity(
                gen_default.GetCountFingerprint(mol_a), gen_default.GetCountFingerprint(mol_b)
            )
        )
        chiral_tan = float(
            DataStructs.TanimotoSimilarity(
                gen_chiral.GetCountFingerprint(mol_a), gen_chiral.GetCountFingerprint(mol_b)
            )
        )
        rows.append(
            {
                "pair": name,
                "default_morgan_tanimoto": round(default_tan, 4),
                "default_identical": default_tan == 1.0,
                "chirality_aware_tanimoto": round(chiral_tan, 4),
                "chirality_aware_identical": chiral_tan == 1.0,
            }
        )
    return rows


def check_b(smiles: str) -> dict:
    """Re-root the SMILES at every atom: does the CIP label or the raw tag change?"""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"unparsable SMILES: {smiles}")
    mol = _stereochemistry(mol)
    canonical = Chem.MolToSmiles(mol)
    cip_ref, tag_ref = _cip_map(mol), _tag_map(mol)

    variants = cip_kept = tag_kept = tag_flip_variants = 0
    for root in range(mol.GetNumAtoms()):
        variant_smiles = Chem.MolToSmiles(mol, rootedAtAtom=root, canonical=False)
        variant = Chem.MolFromSmiles(variant_smiles)
        if variant is None or Chem.MolToSmiles(variant) != canonical:
            continue  # not the same molecule (should not happen); do not count it
        # match[variant index] = index in the reference molecule
        match = mol.GetSubstructMatch(variant, useChirality=True)
        if not match:
            continue
        variants += 1
        cip_v, tag_v = _cip_map(variant), _tag_map(variant)
        cip_kept += all(cip_v.get(i) == cip_ref.get(match[i]) for i in cip_ref)
        consistent = all(tag_v.get(i) == tag_ref.get(match[i]) for i in tag_ref)
        tag_kept += consistent
        if not consistent:
            tag_flip_variants += 1

    return {
        "molecule": smiles,
        "stereocentres": len(cip_ref),
        "smiles_variants": variants,
        "cip_preserved_variants": cip_kept,
        "chiraltag_preserved_variants": tag_kept,
        "chiraltag_flipped_variants": tag_flip_variants,
        "cip_ordering_invariant": cip_kept == variants,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    ap.add_argument("--fp-size", type=int, default=2048)
    ap.add_argument("--radius", type=int, default=2)
    args = ap.parse_args()

    rows_a = check_a(fp_size=args.fp_size, radius=args.radius)
    rows_b = [check_b(smi) for _, smi in ORDERING_MOLECULES]

    # A: the default fingerprint must fail to separate enantiomers and the chirality-aware
    #    one must separate them. B: the CIP label must survive re-rooting everywhere, and at
    #    least one raw chiral tag must be shown to change (otherwise the bug is not
    #    reproduced on this molecule set and the claim in the audit must be re-examined).
    ok_a = all(r["default_identical"] and not r["chirality_aware_identical"] for r in rows_a)
    cip_total = sum(r["cip_preserved_variants"] for r in rows_b)
    var_total = sum(r["smiles_variants"] for r in rows_b)
    flips_total = sum(r["chiraltag_flipped_variants"] for r in rows_b)
    ok_b = cip_total == var_total and flips_total > 0

    summary = {
        "rdkit": rdBase.rdkitVersion,
        "check_a_pass": ok_a,
        "check_b_pass": ok_b,
        "cip_preserved": f"{cip_total}/{var_total}",
        "chiraltag_flipped_variants": flips_total,
        "pass": ok_a and ok_b,
    }
    if args.json:
        print(json.dumps({"summary": summary, "check_a": rows_a, "check_b": rows_b}, indent=2))
        return 0 if summary["pass"] else 1

    print(f"RDKit {summary['rdkit']}")
    print(f"\nCHECK A - Morgan radius={args.radius}, {args.fp_size} bits, count fingerprints")
    print(f"{'pair':<14}{'default':>9}{'identical':>11}{'chirality-aware':>17}{'identical':>11}")
    for r in rows_a:
        print(
            f"{r['pair']:<14}{r['default_morgan_tanimoto']:>9.4f}"
            f"{str(r['default_identical']):>11}{r['chirality_aware_tanimoto']:>17.4f}"
            f"{str(r['chirality_aware_identical']):>11}"
        )
    print(
        "  => default fingerprint cannot separate enantiomers; chirality-aware can."
        if ok_a
        else "  => UNEXPECTED - do not cite CHECK A"
    )

    print("\nCHECK B - re-rooting the SMILES at every atom")
    print(f"{'molecule':<22}{'centres':>8}{'variants':>9}{'CIP kept':>10}{'tag kept':>10}{'tag flipped':>12}")
    for r in rows_b:
        print(
            f"{r['molecule']:<22}{r['stereocentres']:>8}{r['smiles_variants']:>9}"
            f"{r['cip_preserved_variants']:>10}{r['chiraltag_preserved_variants']:>10}"
            f"{r['chiraltag_flipped_variants']:>12}"
        )
    print(
        f"  => CIP preserved in {cip_total}/{var_total} variants; raw chiral tag flipped in "
        f"{flips_total} variants (the qmse_lib bug)."
        if ok_b
        else "  => UNEXPECTED - inspect before citing"
    )

    print(f"\nOVERALL: {'PASS' if summary['pass'] else 'FAIL'}")
    return 0 if summary["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
