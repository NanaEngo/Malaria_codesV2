# Recent runs — expected versus observed evidence

**Date:** 9 August 2026  
**Scope:** P1 V4/V5/V6, P2, P3, P4, and P5  
**Mode:** author-controlled pre-submission development (`development_execution_authorized=true`; editorial/review restrictions inactive)

This register separates scheduler/run completion from scientific promotion. A file on disk is not treated as a manuscript result unless its provenance, denominator, QC status, and interpretation boundary are explicit.

## P1 — V4, V5, and V6

| Work package | Expected | Observed | Manuscript status |
|---|---|---|---|
| V4 2F6I replacement | Complete 484-centroid panel with fail-closed accounting and independent review | **Targeted remediation COMPLETED (array 15016 + aggregate 15044, 9 Aug):** 35/35 records, 0 missing. Final classification: **10 `PASS_RAW_VINA`** (recovered: cid 237 multi-fragment cleanup, 43/195/228/340 multi-seed embedding, 339 zero-charge fallback, 136/170 re-docked, plus rescue 125/258 confirmed), **15 `UNSUPPORTED_ELEMENT_FOR_AD4`** (boron — AutoDock Vina cannot type B; explicit protocol exclusion), **5 `DOCKED_GATE_FAILED`** (Vina succeeded, rank-1 pose outside catalytic triad; affinities retained −2.4…−6.1), **5 `EMBED_FAILURE_ALL_STRATEGIES`** (exotic VAE SMILES). Net gain vs historical 449/484: +7 new PASS. Provenance: `results/pfclpp_2f6i_484_remediation_20260809/c_v4_2f6i_remediation_provenance.json` + summary CSV. | **Do not update V4 numerical results or promote the panel** (independent review still pending). The remediation gives a complete 35/35 accounting and is documented as exploratory evidence; the 15 boron exclusions and 5 gate-failures are honest protocol-bound results, not pipeline failures. |
| V5 four-target Vina | 17 candidates × 4 target-specific anchored runs | **68/68 finite raw records**, 17/17 per target for PfDHFR, PfCRT, PfClpP, and PfATP4; consolidated 17×4 table is internally consistent. | May be described as **raw target-specific docking evidence**. It is not experimental affinity, MD validation, or independently reviewed consensus. |
| V5 docking-RRS pilot | 136 mutant/WT docking records | Archived pilot: **136/136 finite raw scores**. **Isolated V5-protocol reproduction COMPLETED (jobs 15013 PfDHFR, 15014 PfCRT, 15015 post-processing):** 136/136 Vina rows (85 PfDHFR + 51 PfCRT), 34 RRS rows (17 per target), **0 failure.json**, status `VINA_GRID_DOCK_MUTANT_PANEL_RANK1_VERIFIED` (seed 0, exhaustiveness 16, num_modes 9). Class distribution **A*:12 / A:5 per target — identical to the archived pilot**, confirming internal V5-protocol reproducibility. Outputs isolated under `results/exploratory/rrs_reproduction_20260809/`; provenance records `canonical_outputs_modified=false`, `canonical_p2_rrs_overwritten=false`. This is **not** a common-protocol replication of canonical P2 (V5 RRS ≈ 99.9% vs P2 82.8% mean, as documented in the reconciliation). | Exploratory only; do not replace canonical P2 RRS classes or correlations. May be cited as an internal V5-protocol reproducibility check. |
| V6 integration | Exact-SMILES join of V5 and P2 Set-C sources | **17/17 candidate identities**, **68/68 target-wise records**, **204 Vina values with zero raw-table mismatches**, complete 136-row mutant panel, and **82 RRS values recomputed with zero mean/class/value mismatches**. Main/SM/cover compile at 13/5/1 pages. | Descriptive/exploratory figures are allowed in development; independent structural review remains pending and no submission-facing promotion is claimed. |

**P1 identity boundary:** PDB 4GM2 is PfClpR, not PfClpP. The genuine PfClpP receptor used in V5 is 2F6I. The V5 17×4 panel does not replace the V4 484-centroid panel.

## P2 — parent MD and Set-C MD

| Work package | Expected | Observed | Manuscript status |
|---|---|---|---|
| Historical diagnostic continuation `14970_[0-1]` | 10 ns diagnostic continuation for 201–PfDHFR and 214–PfCRT at 310.15 K | Both output trees contain trajectories and analyses, but both `diagnostic_provenance.json` files report `status=FAILED`, `failed_stage=mdrun`, and `publication_grade_reconstruction=false`. | Do not call this a successful new MD validation or add a new MM-GBSA result. It is a failed diagnostic execution with retained analysis artifacts. |
| Historical parent-study MD | Four named systems, 10 ns each | Historical evidence remains 40 ns total; only PfCRT–214 has an interpretable MM-GBSA estimate (−18.25 ± 0.40 kcal mol⁻¹). 164/201 dissociated; 438 is conversion-corrupted; 4GM2 is PfClpR. | Keep current bounded manuscript interpretation. |
| Set-C MD pilot | 16 systems for PP-01/PP-02 across PfDHFR/PfCRT | `required_system_count=16`, `ready=0`, `blocked=16`, `gromacs_launched=false`, `md_rrs_status=NOT_COMPUTED`. Missing candidate-specific complexes/manifests; remediation contract recorded in `results/set_c_md/set_c_preparation_remediation_20260809.md`. **Dependency audit (9 Aug): `cgenff` is not installed** (CGenFF is a licensed tool), while the fail-closed workflow requires exactly `CHARMM36m + CGenFF + TIP3P`. OpenFF 2.2 (openff-toolkit 0.16.10) and ACPYPE/GAFF2 are available but are explicitly rejected by the protocol as non-conforming provenance. | State explicitly that no Set-C production MD or MD-RRS was performed; the blocker is a missing licensed force-field tool (CGenFF), not an editorial restriction. |

No P2 manuscript claim should imply that `14970` generated a publication-grade trajectory or that Set-C candidates underwent MD.

## P3 — quantum-inspired representations

The expected external descriptor and QKS validation work is present in the repository and is already integrated in the canonical manuscript package:

- descriptor ITT panel: 22,447 molecules, with 351 TNE failures retained as an explicit zero-vector penalty;
- complete-case sensitivity: 22,096 molecules, job 13997;
- descriptor ranking: ECFP4 0.9601, TFP 0.8645, TNE 0.6448, TFP+TNE 0.8000 (ITT); complete-case TFP 0.8611, TNE 0.6437, TFP+TNE 0.7981;
- QKS external: quantum 0.8172 versus RBF 0.8466; corrected-resampled p=0.021, exploratory;
- statistical audit artifacts are present, with failure-mask provenance.

**Decision:** no additional manuscript rewrite is required for these run results. Keep the ITT/complete-case distinction and the exploratory statistical qualification.

## P4 — activity-aware Pareto/MCTS

The expected v12 activity-aware scalar benchmark is present:

- 20 seeds × four methods in `results/benchmark_molecules_opt_v12/`;
- Random 0.6724 ± 0.0056;
- MCTS 0.6649 ± 0.0068;
- GA 0.6453 ± 0.0124;
- Greedy 0.4278 ± 0.0000;
- MCTS versus Random paired t-test: t₁₉ = −4.97, p = 0.000085.

The canonical Pareto front remains the **pre-activity** front with post-hoc SYBA recomputation; it must not be described as if the v12 activity term had been retroactively used to generate that front. QMC Tier-2 candidate validation remains diagnostic/non-publication-grade and is excluded from the manuscript.

**Decision:** the current P4 manuscript is aligned; no new numeric result is inserted.

## P5 — GNN/Transformer and external replication

The expected independent checks are present and integrated:

- leak-fixed internal random/scaffold benchmarks;
- ECFP4-RF and GIN replications;
- disjoint ChEMBL-derived benchmark: 22,267 molecules after exclusion of 180 overlaps;
- ECFP4-RF versus GIN: random 0.9547 ± 0.0033 versus 0.9237 ± 0.0040; scaffold 0.9190 ± 0.0004 versus 0.8843 ± 0.0021;
- Job 12889 scaffold ChemBERTa replication: 25/25 records, 0.7908 ± 0.0298; redundant random branch was cancelled and did not alter canonical random 0.9121 ± 0.0047.

**Decision:** no new P5 numerical manuscript update is required. Preserve the external-label and cancelled-redundant-run caveats.

## Global manuscript-update rule

Development execution is unrestricted before explicit author reactivation: calculations, reruns, exploratory consensus/RRS/PNS/ACSI analyses, figures, and manuscript drafting may proceed. This does not change evidence status or permit promotion of unreviewed outputs.

Only these statuses may enter primary Results claims:

1. complete finite output with verified denominator and provenance;
2. a declared analysis population and pre-specified interpretation;
3. no unresolved identity, geometry, or runtime failure affecting the claim.

Failed diagnostics, incomplete aggregates, exploratory consensus/RRS/PNS, and pending-review artifacts may be described in Methods, Limitations, or provenance notes, but not as validated biological results.
