#!/usr/bin/env python
"""Phase 1 finalization: RDKit validation of the v2 mapping + frozen data contract.

Reads ``data/mappings/drugid_to_smiles_v2.csv`` (produced by p6_phase1_prism.py),
splits multi-component SMILES entries, keeps the largest fragment by heavy-atom
count (standard salt-stripping), validates and re-canonicalizes every molecule
with RDKit, assigns collision groups over identical canonical SMILES, and writes:

* ``data/mappings/drugid_to_smiles_v2_validated.csv``
* ``data/mappings/drugid_to_smiles_contract.json`` (frozen provenance contract)

Subcommands
-----------
validate
    Run the full validation pass and write both artifacts.
selftest
    Plant synthetic rows and assert the expected behaviour (no I/O to the
    real mapping files).

Notes
-----
All counts are printed as an audit block suitable for pasting into
``P6_DATA_ANALYSIS_REPORT.md``.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from rdkit import Chem, RDLogger

# Silence RDKit parse spam; failures are counted, not logged line-by-line.
RDLogger.DisableLog("rdApp.*")

PROJ = Path(__file__).resolve().parents[1]
MAPS = PROJ / "data" / "mappings"
SRC = MAPS / "drugid_to_smiles_v2.csv"
OUT_CSV = MAPS / "drugid_to_smiles_v2_validated.csv"
OUT_CONTRACT = MAPS / "drugid_to_smiles_contract.json"


def _sha256(path: Path) -> str:
    """Return the SHA-256 hex digest of a file.

    Args:
        path: File to hash.

    Returns:
        Lowercase hex digest string.
    """
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def _largest_fragment_smiles(raw: str) -> tuple[str | None, int]:
    """Split a raw SMILES field into components and return (best SMILES, n_components).

    The raw PRISM field may contain several comma-separated SMILES strings and/or
    dot-disconnected fragments (salts). Components are split on both ',' and '.',
    parsed with RDKit, and the fragment with the most heavy atoms wins.

    Args:
        raw: Raw SMILES cell (may be NaN).

    Returns:
        Tuple of (canonical SMILES of the largest valid fragment, or None when no
        fragment parses; number of dot/comma components found).
    """
    if not isinstance(raw, str) or not raw.strip():
        return None, 0
    comps = [c.strip() for c in raw.replace(",", ".").split(".") if c.strip()]
    best_mol, best_smiles = None, None
    for c in comps:
        mol = Chem.MolFromSmiles(c)
        if mol is None:
            continue
        if best_mol is None or mol.GetNumHeavyAtoms() > best_mol.GetNumHeavyAtoms():
            best_mol, best_smiles = mol, Chem.MolToSmiles(mol)
    return best_smiles, len(comps)


def cmd_validate(_args: argparse.Namespace) -> None:
    """Validate the v2 mapping, assign collision groups, freeze the data contract."""
    m = pd.read_csv(SRC)
    parsed = [_largest_fragment_smiles(s) for s in m["canonical_smiles"]]
    m["smiles_rdkit"] = [p[0] for p in parsed]
    m["n_components"] = [p[1] for p in parsed]
    m["is_valid"] = m["smiles_rdkit"].notna()

    # Collision groups: identical validated molecule shares one group id.
    # ponytail: factorize is O(n) and enough; full InChIKey grouping if Phase 2 needs it.
    grp = m["smiles_rdkit"].fillna("__invalid__")
    codes, _uniq = pd.factorize(grp)
    m["collision_group"] = np.where(m["is_valid"], codes, -1)

    n_dup_groups = int((pd.Series(codes).value_counts() > 1).sum())
    audit = {
        "rows": len(m),
        "coverage_source": float(m["canonical_smiles"].notna().mean()),
        "valid_fraction": float(m["is_valid"].mean()),
        "unique_molecules": int(m.loc[m.is_valid, "collision_group"].nunique()),
        "collision_groups_gt1": n_dup_groups,
        "multi_component_rows": int((m["n_components"] > 1).sum()),
        "max_components": int(m["n_components"].max()),
    }
    m.to_csv(OUT_CSV, index=False)

    import rdkit
    contract = {
        "artifact": OUT_CSV.name,
        "artifact_sha256": _sha256(OUT_CSV),
        "source": SRC.name,
        "source_sha256": _sha256(SRC),
        "script": Path(__file__).name,
        "rdkit_version": rdkit.__version__,
        "seed": 42,
        "salt_strategy": "largest fragment by heavy atoms",
        "collision_policy": "group id over identical canonical SMILES; groups must not cross train/test",
        "audit": audit,
        "frozen": True,
    }
    OUT_CONTRACT.write_text(json.dumps(contract, indent=2))
    print(json.dumps(audit, indent=2))
    print(f"[contract] {OUT_CONTRACT} sha256={_sha256(OUT_CONTRACT)}")


def cmd_selftest(_args: argparse.Namespace) -> None:
    """Assert parser behaviour on planted rows."""
    ok, n = _largest_fragment_smiles("CCO")
    assert ok == "CCO" and n == 1, f"simple failed: {ok}, {n}"
    ok, n = _largest_fragment_smiles("CC(=O)O.CN")  # acid bigger than amine
    assert ok == "CC(=O)O" and n == 2, f"salt failed: {ok}, {n}"
    ok, n = _largest_fragment_smiles("Oc1ccc2sc(=O)oc2c1, Oc1ccc2sc(=O)oc2c1")
    assert ok == "O=c1oc2cc(O)ccc2s1" and n == 2, f"comma failed: {ok}, {n}"
    ok, n = _largest_fragment_smiles("not_a_smiles")
    assert ok is None and n == 1, f"garbage failed: {ok}, {n}"
    ok, n = _largest_fragment_smiles(float("nan"))
    assert ok is None and n == 0, f"nan failed: {ok}, {n}"
    print("[selftest] OK")


def main(argv: list[str] | None = None) -> None:
    """CLI entry point.

    Args:
        argv: Optional argument vector override (for testing).
    """
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("validate").set_defaults(func=cmd_validate)
    sub.add_parser("selftest").set_defaults(func=cmd_selftest)
    args = ap.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
