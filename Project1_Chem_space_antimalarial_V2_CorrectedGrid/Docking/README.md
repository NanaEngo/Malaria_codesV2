# Docking Configs — V2 Corrected Grid

## Grid Centers

| Target | PDB | V1 (broken) | V1 Status | V2 (corrected) |
|--------|-----|-------------|-----------|-----------------|
| PfDHFR | 7F3Y | (1.33, -1.73, -23.84) | BROKEN — 35.4Å décalé | TBD (après re-prep) |
| PfCRT | 6UKJ | (152.99, 151.04, 159.38) | RE-CENTER — 6Å décalé | (152.5, 148.0, 154.5) |
| PfATP4 | 9N10 | (134.84, 133.10, 97.63) | RE-CENTER — 8Å décalé | (129.3, 130.9, 92.4) |
| PfClpP | 4GM2 | (26.19, 35.09, 24.72) | OK | (26.19, 35.09, 24.72) |

## Usage

```bash
# Run Vina with corrected config:
vina --config Docking/Docking_6UKJ/config.txt --ligand ligand.pdbqt --out docked.pdbqt
```

## To Do
- [ ] Re-prepare 7F3Y with NADPH cofactor → define corrected PfDHFR grid
- [ ] Re-run centroid docking for PfDHFR on HPC
- [ ] Update DEKOIS config after PfDHFR validation
