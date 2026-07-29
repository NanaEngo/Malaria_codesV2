# Data Directory

**Last updated:** April 13, 2026 (restructured from 988 → 45 files)

---

## Structure

```
data/
├── README.md
├── cluster_representatives_smiles.smi     (484 K-Means centroids — used by R1)
├── cluster_representatives_nonsmiles.smi
│
├── proteins/                              (8 files — 4 targets × PDB+PDBQT)
│   ├── 4GM2.pdb / 4GM2.pdbqt             (PfClpP)
│   ├── 6UKJ.pdb / 6UKJ.pdbqt             (PfCRT)
│   ├── 7F3Y.pdb / 7F3Y.pdbqt             (PfDHFR)
│   └── 9N10.pdb / 9N10.pdbqt             (PfATP4)
│
├── external/                              (9 files — external datasets)
│   ├── ANPDB.csv                          (African NPs, 11,448 compounds)
│   ├── ANPDB.sdf
│   ├── anpdb_clean.csv
│   ├── DHFR_decoys.smi                    (DEKOIS 2.0, 1,200 decoys)
│   ├── DHFR_ligands.smi                   (DEKOIS 2.0, 40 ligands)
│   └── MalariaBox400compoundsDec2014.csv  (MMV Malaria Box, 400 compounds)
│
└── raw/                                   (16 files — pipeline inputs)
    ├── Afromalaria_DB.csv
    ├── All_mol_selfies.csv
    ├── All_molecules.csv
    ├── Antimalarial_NP.csv
    ├── Antimalarial_sp.csv
    ├── PAINS_hits_Malaria.txt
    ├── admet.csv
    ├── all_mol_cheese_prop.csv
    ├── all_mol_selfies_prop.csv
    ├── all_molecules.csv
    ├── all_molecules_inputs.csv
    ├── all_molecules_prop.csv
    ├── alphabet.txt
    ├── generated_data_filt_final.csv
    ├── malaria_final.csv
    ├── merged_cheese.csv
    └── merged_cheese_clean.csv
```

---

## What Was Removed

| Removed | Files | Reason |
|---------|-------|--------|
| `data/raw/ligands/pdb/` | 466 | Duplicates of `results/ligands/pdb/` |
| `data/raw/ligands/pdbqt/` | 465 | Duplicates of `results/ligands/pdbqt/` |
| `data/external/decoys_part_*.zip` | 3 | Unextracted archives (contents already in `external/`) |
| `data/external/ligands.zip` | 1 | Unextracted archive |
| `data/external/dekois/*.sdf` + `*.gz` | 2 | Raw source archives (extracted `.smi` files used by scripts) |
| `data/external/ligands/DHFR.sdf` + `*.gz` | 2 | Raw source archives |
| `data/pdbqt_ligands_test/` | 6 | Legacy test data |
| **Total removed** | **945** | |

---

## Data → Script Mapping

See [`DATA_SCRIPT_MAP.md`](./DATA_SCRIPT_MAP.md) for full mapping.

---

*988 → 45 files (−95.4%)*
