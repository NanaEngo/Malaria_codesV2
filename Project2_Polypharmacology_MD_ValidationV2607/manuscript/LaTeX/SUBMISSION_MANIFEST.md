# Submission Manifest — Project 2

**Journal:** *Journal of Chemical Information and Modeling* (ACS)
**Updated:** 27 August 2026 (final robustness and companion-context consolidation; P2Rank box audit + ProLIF interaction fingerprints + Figure S4)
**Package status:** The canonical P2 main manuscript, Supporting Information, and cover letter compile without fatal LaTeX errors or unresolved references. The manuscript is suitable for final author reading. No Zenodo DOI is recorded; archival deposit remains pending.

## Canonical evidence status

- Set-C docking cohort: 17 filtered candidates and 136 WT/mutant docking systems.
- Target-balanced primary RRS panel: 12 candidates with eligible PfDHFR and PfCRT WT scores.
- Coverage-limited sensitivity panel: 5 PfCRT-only candidates; not equivalent to the complete panel.
- Parent-study MD: 4 non-overlapping WT complexes × 10 ns; only PfCRT–214 yielded an interpretable MM-GBSA endpoint.
- Set-C MD pilot: 16 systems covering PP-01/PP-02; trajectory QC PASS, single replicate per system; secondary only.
- K76A replicate-1 MM-GBSA: `FAILED_NUMERICAL_QC` after receptor-minimization `BOND overflow`; endpoint excluded from reportable claims.
- Full-panel Set-C MD-RRS: `NOT_COMPUTED` by design.

## Lightweight robustness and transfer audit

Script:

```text
scripts/p2_robustness_transfer_audit.py
```

Versioned outputs:

```text
results/robustness_transfer_20260827/
```

Included analyses:

- leave-one-candidate-out correlations on the complete two-target set;
- target-stratified PfDHFR/PfCRT correlations;
- individual docking-score perturbations of ±1 kcal mol⁻¹;
- existing RRS threshold-sensitivity artifact;
- P1/P2 cohort identity audit;
- related-project ChEMBL transfer provenance audit;

Interpretation boundary: all outputs are post-selection diagnostics. They do not establish biochemical affinity, biological resistance, target engagement, or mechanism of action.

## Independent pocket and interaction audits (27 August 2026) — post-processing only

### P2Rank pocket audit

```text
results/p2rank_boxes_20260827/     # predictions/residues CSVs + README
```

- P2Rank 2.5.1 (JDK 17 via `conda env jdk17`; the system Java 8 cannot run class-61 bytecode).
- **PfCRT (6UKJ):** top pocket (score 162.7, prob 0.999) lies 5.7 Å from the Vina box center — independent corroboration.
- PfDHFR (7F3Y) and PfATP4 (9N10): 23–46 Å separations with documented receptor-frame caveats (provenance flags, not refutations).
- PfClpP (2F6I): weak P2Rank signals; frame-independent report only (ClpP docking ran in P1).
- Integrated as **Figure S4** in the Supporting Information; cited in the main text Methods (grid-box paragraph) with the P2Rank citation (Krivák & Hoksza 2018).

### ProLIF interaction-fingerprint occupancy

```text
results/prolif_ifp_20260827/       # 16 ifp_<system>.csv + prolif_summary.json + README
scripts/p2_prolif_ifp_pilot.py
```

- ProLIF 2.2.1 on the 16 QC-PASS pilot trajectories (100 frames each); **16/16 computed**.
- Every system retains 4–11 contacts at ≥ 50 % occupancy (most at 100 %); no contact loss. Descriptive highlights: PfCRT TYR16 at 100 % in 5/6 PfCRT systems; PfDHFR LEU46/MET55 (PP-01) and LEU40/ILE14 (PP-02).
- Descriptive trajectory-interaction evidence corroborating the retention-not-gain pilot reading; not binding affinities or resistance evidence.

Key results:

- PNS–RRS leave-one-out ρ: −0.3182 to +0.0273.
- ACSI–RRS leave-one-out ρ: −0.7636 to −0.3182.
- RRS class unchanged in 212/272 perturbation records (77.9%).
- PfDHFR PNS–RRS ρ: −0.3497; PfCRT PNS–RRS ρ: −0.0417.

## Companion P1 context

The P1 V7 artefacts are used only as upstream methodological and chemical-space context. The P1/P2 audit found 17/17 exact canonical-SMILES matches and shared provenance. P1 therefore is not an independent replication of P2 and does not validate P2 RRS, mutant affinity, biological resistance, or polypharmacology.

Relevant record:

```text
results/robustness_transfer_20260827/p1_p2_cohort_audit.json
results/robustness_transfer_20260827/step1_external_rRS_feasibility.md
results/robustness_transfer_20260827/external_transfer_audit.json
```

The permitted use is summarized in SI Table S16. The local ChEMBL feasibility audit found no paired target-state WT/mutant fields; ChEMBL itself is not an independent P2-RRS replication; the separate targeted docking replication is documented below as a bounded computational sensitivity analysis.

## SI tables added or updated

- `Table_S8_Cohort_Estimands.tex` — filtered cohort and estimand separation.
- `Table_S13_Evidence_Scope.tex` — supported interpretation and required next validation.
- `Table_S14_Panel_Scope.tex` — covered and uncovered biological dimensions.
- `Table_S15_Robustness_Transfer.tex` — 3A/3B audit summary.
- `Table_S16_P1_Context.tex` — permitted use and limits of P1 evidence.

## Source and compiled-file checksums

| File | SHA-256 |
|---|---|
| `manuscript/LaTeX/Polypharmacology_MD_Validation_V2607.tex` | `0c8a4d197874069baf009d0d429c99b1c17e9ecaa2444a97ab78430fb845630d` |
| `manuscript/LaTeX/Polypharmacology_MD_Validation_V2607.pdf` | `dfd51eec49f8fe7045760e6011f039560b7665492dde8f77110262397b6593e5` |
| `manuscript/LaTeX/Polypharmacology_MD_Validation_SM_V2607.tex` | `4579a9d1a446ab4837ca36a54ee95a410f02b3ce3135c05164ce1b64f9619e71` |
| `manuscript/LaTeX/Polypharmacology_MD_Validation_SM_V2607.pdf` | `a635abdeb2fe657be940e8127d7d0c7d667f2d54468d3c67b68384d4cf1241fb` |
| `manuscript/LaTeX/Table_S8_Cohort_Estimands.tex` | `5457d0a8daa95938ed617cbf6894683f78cd9a7d644e64778d167253c1d0aa90` |
| `manuscript/LaTeX/Table_S10_WT_Replicate_Consistency.tex` | `976fe5eaac72cde398be7699663f7572a80733923181a6dc44e7a246d8ce42e2` |
| `manuscript/LaTeX/Table_S11_RRS_Threshold_Sensitivity.tex` | `ee374838b421a214c40e3d661f3770f9150231faeeb5660e7b25013cdd0a075a` |
| `manuscript/LaTeX/Table_S12_RRS_By_Target.tex` | `2d29c29d05f59fc06839ac37c11be9293066e29807a0d27f35e0ef7c47ccc40e` |
| `manuscript/LaTeX/Table_S13_Evidence_Scope.tex` | `63562e6ceb28e017ee1e5108fe2c7c6f2de02bd45826722dc60407e1224fdd58` |
| `manuscript/LaTeX/Table_S14_Panel_Scope.tex` | `11a4495bb914c9e55dadc6958fe7b6165b4d535accf194490488e02323638d2a` |
| `manuscript/LaTeX/Table_S15_Robustness_Transfer.tex` | `7dbb3c283db2e2109cd690333c02cf2659e97e9a5744e89807b2411c1744f543` |
| `manuscript/LaTeX/Table_S16_P1_Context.tex` | `de33d0e66da4c2748a4bdf6fd8b045f29ef71c6c909e754d04ec6999af45dcb2` |
| `results/robustness_transfer_20260827/robustness_transfer_summary.json` | `6f10e75e23b67c2e11612198107643085ea91cb069b624ab0df34cb70650193d` |
| `results/robustness_transfer_20260827/external_transfer_audit.json` | `702e85877f4998ac0da510a6389672530e9435f3b00a473ad18cf71099d58865` |
| `results/robustness_transfer_20260827/p1_p2_cohort_audit.json
results/robustness_transfer_20260827/step1_external_rRS_feasibility.md` | `cab1dc367a7a3201ea6f48825e2adc43a21232d3ab3553397d32bddd186ff0a6` |

## External docking replication status

The targeted external docking replication is complete and audited at 312/312 records after the declared exclusion of EXT-039 (`EMBED_FAILURE`). It is computational sensitivity evidence only, not experimental validation or an MD estimate. See `results/robustness_transfer_20260827/external_docking_rrs_20260827.{csv,json}`.

## Frozen future replication plan

The targeted external docking replication has been executed and audited at 312/312 records after the declared EXT-039 embedding exclusion. Its frozen protocol, repair ledger, and go/no-go gates are recorded in:

results/robustness_transfer_20260827/targeted_external_docking_replication_plan.md
results/robustness_transfer_20260827/targeted_external_docking_replication_plan.json

## Verification record

```bash
python3 scripts/p2_robustness_transfer_audit.py
latexmk -pdf -interaction=nonstopmode -halt-on-error Polypharmacology_MD_Validation_V2607.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error Polypharmacology_MD_Validation_SM_V2607.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error Cover_Letter.tex
git diff --check
```

Observed:

- robustness/transfer audit: PASS;
- main manuscript: compiled successfully;
- Supporting Information: compiled successfully;
- cover letter: compiled successfully;
- fatal LaTeX errors: none;
- undefined references/citations: none;
- `Overfull \\hbox`: none;
- minor `Underfull \\hbox` warnings remain in dense paragraphs/tables;
- Zenodo DOI: pending.

## Submission boundary

The manuscript reports computational prioritization and targeted structural follow-up. It does not establish biological polypharmacology, target engagement, clinical efficacy, resistance circumvention, or converged mutant-state free energies. The Set-C cohort is filtered, the MD pilot is single-replicate, K76A MM-GBSA is non-reportable, and P1 evidence is contextual rather than independent validation.
