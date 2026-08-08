#!/usr/bin/env python3
"""P1 V5 — Correct the 68-pair input manifest: replace 4GM2 (PfClpR) with 2F6I (PfClpP).

Scientific justification (verified against RCSB/UniProt on 2026-08-08):
  - 4GM2 = "Structural Insights into the Inactive Subunit of the Apicoplast-localized
    Caseinolytic Protease Complex" (El Bakkouri et al. 2013), UniProt Q8IL98 -> PfClpR.
  - 2F6I = "Crystal structure of the ClpP protease catalytic domain from Plasmodium
    falciparum" (El Bakkouri et al. 2010), EC 3.4.21.92, UniProt O97252 -> PfClpP.
The 17 PfClpP rows must point to the genuine receptor. Original manifest is backed up.
"""
from __future__ import annotations

import csv
import shutil
from pathlib import Path

V5 = Path("/home/nanaengo/Malaria_codesV2/Project1_Chem_space_antimalarial_V5_CorrectedGrid")
MANIFEST = V5 / "results/diffdock_polypharm/diffdock_input_manifest.csv"
BACKUP = V5 / "results/diffdock_polypharm/diffdock_input_manifest_4GM2_legacy.csv"

NEW_PDB_ID = "2F6I"
NEW_PATH = "/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607/data/proteins/2F6I.pdb"
NEW_SHA = "12d02a92e72ab52267fcfb2f7fad2520271b7b311d7f538c16f6395d9f9f62d6"
OLD_SHA = "2130e9fdde2a56b5c31eef94a620624679af009f06bbd5e145e6053a82117fcc"


def main() -> int:
    if not MANIFEST.is_file():
        raise SystemExit(f"FAIL-CLOSED missing manifest: {MANIFEST}")
    # Backup the legacy manifest once (never overwrite existing backup).
    if not BACKUP.is_file():
        shutil.copy2(MANIFEST, BACKUP)
        print(f"backup written: {BACKUP.name}")
    with MANIFEST.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 68:
        raise SystemExit(f"FAIL-CLOSED expected 68 rows, found {len(rows)}")
    n_clpp = 0
    for r in rows:
        if r["target"] == "PfClpP":
            n_clpp += 1
            if r["pdb_id"] != "4GM2" or r["protein_sha256"] != OLD_SHA:
                raise SystemExit(f"FAIL-CLOSED unexpected PfClpP row state: {r}")
            r["pdb_id"] = NEW_PDB_ID
            r["protein_path"] = NEW_PATH
            r["protein_sha256"] = NEW_SHA
    if n_clpp != 17:
        raise SystemExit(f"FAIL-CLOSED expected 17 PfClpP rows, found {n_clpp}")
    fields = list(rows[0].keys())
    with MANIFEST.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    # Verify no 4GM2 remains
    with MANIFEST.open(encoding="utf-8") as f:
        content = f.read()
    if "4GM2" in content:
        raise SystemExit("FAIL-CLOSED 4GM2 still present after correction")
    print(f"manifest corrected: {n_clpp} PfClpP rows -> 2F6I (PfClpP, UniProt O97252, EC 3.4.21.92)")
    print(f"backup preserved: {BACKUP.name} (4GM2 legacy)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
