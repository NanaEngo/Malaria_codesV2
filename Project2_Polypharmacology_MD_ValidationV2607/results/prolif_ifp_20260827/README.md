# ProLIF interaction-fingerprint occupancy — Set-C pilot (27 August 2026)

**Tool:** ProLIF 2.2.1 (`pip install prolif` in the `malaria_md` env).
**Script:** `Project2_Polypharmacology_MD_ValidationV2607/scripts/p2_prolif_ifp_pilot.py`.
**Inputs:** the 16 QC-PASS pilot trajectories (PP-01/PP-02 × PfDHFR/PfCRT mutation states), 10 ns each, loaded via `production.tpr` + `production.xtc` from the canonical preparation root (same sources as the QC chain).
**Sampling:** 100 frames per system (step 10 of 1001 frames) for interaction-occupancy estimation.
**Interactions:** Hydrophobic, HBDonor, HBAcceptor, PiCation, PiStacking, CationPi, Anionic, Cationic, VdWContact (ProLIF v2 names).

## Results — 16/16 systems computed

All systems retain persistent ligand–protein contacts. Per-system `ifp_<system>.csv` lists residue-level interaction occupancy (fraction of sampled frames with the interaction present); `prolif_summary.json` summarizes the number of contacts with occupancy ≥ 50 %.

| System | n_contacts ≥50 % | Top contacts (occupancy) |
|---|---|---|
| PP-01 PfCRT K76A | 5 | ASN12, TYR16, LEU330 (100 %) |
| PP-01 PfCRT K76T | 4 | ILE15, TYR16, LEU330 (100 %) |
| PP-01 PfCRT WT | 5 | ILE15, TYR16, THR289 (100 %) |
| PP-01 PfDHFR C59R | 8 | VAL45, LEU46, CYS50 (100 %) |
| PP-01 PfDHFR I164L | 6 | GLY44, VAL45, SER98 (100 %) |
| PP-01 PfDHFR N51I | 6 | LEU46, MET55, PHE58 (100 %) |
| PP-01 PfDHFR S108N | 7 | LEU46, CYS50, MET55 (100 %) |
| PP-01 PfDHFR WT | 6 | LEU46, LYS49, CYS50 (100 %) |
| PP-02 PfCRT K76A | 6 | TYR16, LEU23, VAL293 (100 %) |
| PP-02 PfCRT K76T | 6 | GLU8, TYR16, SER19 (100 %) |
| PP-02 PfCRT WT | 4 | TYR16, SER19, LEU23 (100 %) |
| PP-02 PfDHFR C59R | 9 | CYS15, ALA16, LEU40 (100 %) |
| PP-02 PfDHFR I164L | 11 | ILE14, CYS15, LEU40 (100 %) |
| PP-02 PfDHFR N51I | 5 | MET55, PHE58, SER98 (100 %) |
| PP-02 PfDHFR S108N | 7 | ILE14, LEU40, ASP54 (100 %) |
| PP-02 PfDHFR WT | 8 | LEU40, LEU46, MET55 (100 %) |

Notable observations (descriptive only):
- **PfCRT TYR16** participates in hydrophobic/aromatic contacts at 100 % occupancy in 5 of 6 PfCRT systems (both PP-01 and PP-02), consistent with a conserved binding-site aromatic residue.
- **PfDHFR LEU46/MET55** recur at 100 % occupancy across PP-01 PfDHFR states; PP-02 PfDHFR favors LEU40/ILE14.
- Contact counts are 4–11 per system; no system shows dissociation-like loss of contacts.

## Interpretation boundary

- These are **descriptive trajectory-interaction occupancies**, not binding affinities, free energies, or biological resistance evidence.
- They complement the MD-RRS/MM-GBSA secondary analyses (retention-not-gain reading) by showing that the ligand stays in contact with conserved binding-site residues in every QC-PASS system.
- No canonical docking score, RRS classification, or manuscript claim is modified.

**Status:** `COMPUTED_SECONDARY_POST_PROCESSING` (16/16). Scripts and outputs versioned under `results/prolif_ifp_20260827/`.
