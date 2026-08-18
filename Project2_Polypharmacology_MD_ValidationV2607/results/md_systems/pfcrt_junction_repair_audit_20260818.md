# PfCRT 114–122 junction repair audit — 18 August 2026

## Context

The 6UKJ crystallographic reference (chain A, residues 47–405) has an internal
sequence gap at residues 114–122 (REMARK 465; UniProt W7FI62 maps
`NKKGNSKER` there). The rigid Kabsch graft
(`scripts/p2_pfcrt_graft_colabfold_loop.py`) superimposed each ColabFold
prediction's 113–123 anchor/loop interval onto the experimental core, but a
single rigid transform cannot satisfy both peptide junctions: the predicted
backbone has its own geometry, so `C(113)-N(114)` and `C(122)-N(123)` came out
of the 1.0–1.8 Å gate while the loop interior was fine.

- `pfcrt_loop_reconstruction_preflight_20260811.json` → `BLOCKED_NO_LOOP_MODELING_BACKEND` (no Modeller/Rosetta).
- `pfcrt_colabfold_gpu_ensemble_grafted_20260811/graft_audit.json` → 16 records, **0/16 PASS_GEOMETRY** (junction breaks at 113–114: 0.85–3.26 Å; at 122–123: 3.5–5.5 Å).
- `pfcrt_colabfold_gpu_retry_grafted_20260811_v2/graft_audit.json` → 1 record, **0/1 PASS_GEOMETRY**.

## Resolution: restrained OpenMM junction repair

New script `scripts/p2_pfcrt_junction_repair_openmm.py` (fail-closed, provenance-hashed):

1. Preprocess the grafted candidate: keep chain A only, drop HETATM (crystallographic ligand Y01), append OXT to the truncated C-terminus ASN 405 (required for the Amber terminal patch).
2. PDBFixer: complete partial sidechains and add hydrogens **without ever rebuilding missing residues** (`fixer.missingResidues = {}` — same rule as `scripts/preparation/fix_pdb_missing_atoms.py`); the loop is never re-modeled.
3. OpenMM Amber14 (implicit OBC2), `NoCutoff`, `HBonds` constraints.
4. **Position restraints** (k = 1000 kJ/mol/nm²) on every core atom outside the 114–122 loop — the experimental core is fixed.
5. **Harmonic distance restraints** (k = 1000 kJ/mol/nm², r0 = 1.33 Å) on the two junction bonds `C(113)-N(114)` and `C(122)-N(123)`.
6. L-BFGS minimization (≤1000 iterations) + 2000 steps of Langevin dynamics at 10 K (quasi-static relaxation).
7. Re-audit with the **identical** graft geometry gate (`audit_geometry` from the graft script; B-factors transferred back so loop pLDDT remains the ColabFold value), write `junction_repair_audit.json`.

## Results

| Metric | Before (graft) | After (repair) |
|---|---|---|
| Passing candidates | 0/16 | **15/15 unique PASS_GEOMETRY** |
| C(113)-N(114) | 0.85–3.26 Å | 1.32–1.37 Å |
| C(122)-N(123) | 3.5–5.5 Å | 1.32–1.35 Å |
| Loop interior (114–115…121–122) | 1.23–1.49 Å (already OK) | 1.32–1.36 Å |
| Core clash screen | mixed | **pass (min loop-core distance ≥ 2.7 Å)** |
| Loop sequence 114–122 | NKKGNSKER | NKKGNSKER (unchanged) |

Selected candidate (rule: highest mean loop pLDDT among geometry-passing
candidates): **`candidate_model_03_seed_001`**, loop pLDDT = 55.17 (heavy-only),
min loop-core distance 2.76 Å, all 10 peptide bonds in [1.0, 1.8] Å.

Machine-readable summary: `results/md_systems/pfcrt_junction_repair_ensemble_20260818/junction_repair_ensemble_manifest.json`
(`JUNCTION_REPAIR_ENSEMBLE_COMPLETED`).

## Boundaries (unchanged)

- **`GEOMETRY_REPAIR_WITNESS_ONLY`**: this resolves the *geometric* junction
  gate, not a biological validation. It is not a Set-C system, not a
  ligand/affinity calculation, not a mutation-resilience study, and not MD-RRS.
- Amber14/TIP3P-implicit is a repair force field; the P2 canonical policy
  (CHARMM36m + OpenFF/CGenFF) is untouched.
- The repaired model with the loop built in is a candidate for the next stage
  (e.g., full-model OpenMM/GROMACS relaxation and structure validation), which
  remains outside the scope of this witness.

## Scripts

- `scripts/p2_pfcrt_junction_repair_openmm.py` — single-candidate repair + audit.
- `scripts/p2_pfcrt_junction_repair_batch.sh` — batch over all graft records (maps candidate → source ColabFold model via the graft audit; `set +u` around `conda activate` per the GMXRC nounset fix).

## GROMACS canonical-policy check (selected model) - 18 Aug 2026

`results/md_systems/pfcrt_gromacs_check_20260818/gromacs_check_manifest.json` - **GROMACS_CANONICAL_POLICY_CHECK_PASS**

| Step | Result |
|---|---|
| pdb2gmx (charmm36-jul2022, TIP3P, -ignh -ter) | RC=0, **1 chain**, 359 residues, 5936 atoms |
| Termini | VAL47 NH2, ASN405 COOH - **no internal split** |
| grompp (-maxwarn 0) | 1 warning only: net charge +11 e (ions added at solvation) |
| grompp (-maxwarn 1) | RC=0, em.tpr written |
| mdrun steepest descent | RC=0, converged in 48 steps, E = -8.74e3 kJ/mol, no error markers |

This confirms the repaired loop is processable under the **canonical P2 policy** (CHARMM36m + TIP3P): the former internal COOH/NH2 split at the 114-122 gap is gone (single continuous chain), and the topology passes the standard gates. Still a **technical** check: no production MD, no binding/affinity, no RRS.

## Canonical MD stability witness (selected model) - 18 Aug 2026

`results/md_systems/pfcrt_md_witness_20260818/md_witness_manifest.json` - **CANONICAL_MD_WITNESS_PASS**

Pipeline (CHARMM36m/TIP3P, NA/CL 0.15 M): pdb2gmx -> editconf -> solvate -> genion (neutral) -> EM -> NVT 100 ps -> NPT 100 ps.

| Stage | Result |
|---|---|
| EM | converged (steepest descent, RC=0) |
| NVT 100 ps | RC=0, 9.92 ns/day, T target 310.15 K |
| NPT 100 ps | RC=0, 9.69 ns/day, T mean 310.18 K (308.2-312.2), density 1020.8 kg/m^3 (TIP3P-typical), 0 error markers |
| Pressure | mean -7.24 bar over 100 ps (short window, fluctuations expected; no divergence) |

The repaired PfCRT model is technically stable under the **canonical P2 MD policy** through EM + NVT + NPT. Pressure equilibration is not fully converged in 100 ps (expected for a witness; a longer equilibration would be needed before any production run).

## Long equilibration (1 ns NPT) - submitted 18 Aug 2026

Job `15387` (`scripts/p2_pfcrt_long_equilibration.sbatch`, partition production):
resumes from the 100 ps canonical witness checkpoint and runs **1 ns NPT**
(500,000 steps, Parrinello-Rahman, 310.15 K) on the repaired model. Purpose:
test whether pressure/density converge beyond the 100 ps window (which showed
P mean -7.24 bar and TIP3P-typical density ~1021 kg/m^3). Still a technical
stability witness: no production MD, no binding/affinity/RRS, no Set-C.

## Discriminative MD-RRS (multi-threshold) - 18 Aug 2026

See `results/set_c_md/setc_md_rrs_execution_runbook.md` (section
"Discriminative MD-RRS") and `results/set_c_md/md_rrs_discriminative_manifest.json`.
Re-analysis of the 16 existing Set-C pilot trajectories with continuous
metrics (bound fractions at 2.0-5.0 A, mean/p5 min distance, MD_RRS_d ratios).
The binary 5 A ceiling is lifted, but **no mutant shows a weaker-binding
signature** within 10 ns (several bind tighter, e.g. PP-02 PfDHFR N51I
mean_min 1.82 A vs WT 2.52 A). This does not demonstrate resistance.

## Superseded historical artefacts (reclassified 18 Aug 2026)

The following PfCRT reconstruction jobs from the 11-12 Aug chain are **superseded**
by the completed junction-repair + canonical-MD chain and are retained as
non-canonical provenance only (do not use as current status):

| Job | Historical status | Why superseded |
|---|---|---|
| 15227 | failed (`--msa-mode mmseqs2`) | ensemble now uses `mmseqs2_uniref_env` (15241 OK) |
| 15238 / 15243 | `BLOCKED_INSUFFICIENT_PASSING_ENSEMBLE` | geometry gate now passed 15/15 by junction repair |
| 15239 | `pdbfixer` missing in env | `pdbfixer` now installed in `pfcrt_colabfold` |
| 15242 | FAIL-CLOSED (ColabFold provenance absent) | ensemble provenance `COLABFOLD_ENSEMBLE_COMPLETED` now recorded |
| 15244 / 15237 | GMXRC unbound variable | fixed by `set +u` in all wrappers |
| 15245 | `FileExistsError` (retry dir existed) | superseded by fresh output roots |
| 15247 | `witness_provenance_requested.json` absent | witness retry4 completed `TECHNICAL_MODEL_STABILITY_PASS` |
| 15246 / 15248 / 15249 | `TECHNICAL_MODEL_STABILITY_PASS` (OpenMM) | stability evidence only, superseded by canonical GROMACS chain |

## Provenance chain

```
ColabFold ensemble (W7FI62, 16 models, COLABFOLD_ENSEMBLE_COMPLETED)
  → graft (Kabsch, 0/16 passing geometry)
    → junction repair (OpenMM restraints, 15/15 unique PASS_GEOMETRY)
      → junction_repair_ensemble_manifest.json (selected: model_03_seed_001)
        → GROMACS canonical check (PASS)
          → canonical MD witness (PASS)
            → long equilibration job 15387 (running)
```
