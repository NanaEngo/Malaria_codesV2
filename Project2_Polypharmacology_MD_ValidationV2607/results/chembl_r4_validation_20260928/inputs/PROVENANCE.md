# Frozen inputs — R4 external anchor (2026-09-28)

- Source: ChEMBL API `https://www.ebi.ac.uk/chembl/api/data/activity.json?target_chembl_id=CHEMBL1939&standard_type=IC50&limit=1000`
  retrieved 2026-09-28 → `CHEMBL1939_ic50.json` (379 IC50 records, 108 molecules).
- Target CHEMBL1939 = Bifunctional dihydrofolate reductase-thymidylate synthase, *Plasmodium falciparum* K1.
- Curation → `paired_set.csv`: assays whose description encodes a DHFR genotype
  (`wt|wild`, `double|C59R`, `triple|I164L`, `quad|N51I`); assays marked
  "relative to trimethoprim" excluded (ratio readout, not IC50); value = min(standard_value) nM
  per genotype; requires WT **and** at least one genotype → n = 28, all with ChEMBL canonical SMILES.
- Measurement type: in vitro antiplasmodial (parasite growth) IC50 in DHFR-genotyped strains
  (TM4/8.2 wt, K1CB1 double, Csl-2 triple, Vl/S quad) — NOT recombinant-enzyme IC50.
