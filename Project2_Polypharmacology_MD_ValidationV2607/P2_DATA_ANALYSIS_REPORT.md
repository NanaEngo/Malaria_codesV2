# P2 — Data Analysis Report (canonical)

**Project**: Project 2 — Polypharmacology MD validation (Set-C + parent-study cohort)
**Canonical directory**: `Project2_Polypharmacology_MD_ValidationV2607/`
**Manuscript target**: *J. Chem. Inf. Model.* (JCIM, ACS)
**Author**: Myke Vital Sao Temgoua
**Last refreshed**: 2026-08-30 (V2609 implementation checkpoint; canonical data unchanged)

**DAR update record — 29 Aug 2026:** Reconciled the editorial status to HOLD; added an explicit evidence-level/claim policy; preserved the PP-01 canonical multi-seed result with its PfCRT provenance limitation; and quarantined non-canonical ligand/grid runs from manuscript inference. No numerical result was changed by this update.

**M1 authorization and launch record — 29 Aug 2026:** A targeted replicated-MD extension was authorized before implementation: four PP-01 pillar states (PfDHFR WT, PfCRT WT, PfDHFR N51I, PfCRT K76T), three independent replicates per state, 100 ns per replicate, 12 trajectories total. This is a robustness analysis of inter-replicate variability, not a validation of affinity or resistance. The versioned launcher is `scripts/p2_m1_replicated_md.sbatch`; the runbook is `docs/P2_M1_RUNBOOK_20260829.md`; output root is `results/m1_replicated_md_20260829/`; environment is `malaria_md`; GPU concurrency is capped at one task (`%1`). SLURM job **15671** was submitted after shell, Python, input-presence, and `sbatch --test-only` preflight checks passed. Results remain `NOT_COMPUTED` until production and post-production QC complete. Earlier failed submissions 15671, 15683, and 15695 were fail-closed before production (GMXRC nounset or invalid source-run paths) and are excluded from analysis. Audit execution du 30 août 2026 : les tentatives 15671/15683/15695 ont échoué en préproduction (GMXRC nounset / chemins sources invalides). Les tâches 15707_0/1/2 ont échoué à `grompp` avec `-maxwarn 0` sur un mot-clé inconnu `tc-integrator` (production.mdp, ligne 34) — `MPI_ABORT` avant `mdrun` ; le journal 15710 rapporte `CANCELLED at 2026-08-29T19:51:45`. Le `mdrun` de `PP-01_PfDHFR_WT/replicate_1` a tourné du 29/08 19:52 au 30/08 15:31 (~1,2 ns/h ; SLURM accounting désactivé, le process survivait hors file). Débit observé ~1,2 ns/h : pour 100 ns il faut ~83 h, or `#SBATCH --time=2-00:00:00` ne couvrait que 48 h → la production ne pouvait pas atteindre 100 ns dans la fenêtre allouée. Voir `docs/P2_M1_EXECUTION_AUDIT_20260830.md` et §14-§15 ci-dessous pour le déroulé complet.

**M1 execution record — 30 Aug 2026 (afternoon):** job 15711_0 **arrêté par décision** à step 11,707,500 (**23,41 ns**) ; **QC post-kill PASS** sur l'intervalle atteint (`p2_m1_postkill_qc.py`, règle `setc_p2_minheavy_5A_ge10percent_v1` ; bound_fraction = 1,0000, mean_min = 2,78 Å, 2,342 frames) ; provenance corrigée `M1_PRODUCTION_INTERRUPTED_PARTIAL` (`achieved_ns = 23.41`, `termination = SLURM_TIME_LIMIT_KILL` — arrêt utilisateur, pas kill SLURM). **Continuation lancée (job 15715, `p2_m1_continue_100ns.sbatch`, 96 h)** — `mdrun -cpi` depuis le checkpoint 11,707,500. **Décision auteur (30 Aug PM, §17) : cible réduite 100 ns → 25 ns** (JCIM n'exige pas une longueur fixe ; 25 ns suffit pour le pilote structural secondaire, libère ~60 h GPU). Watcher SLURM **15716** (`p2_m1_stop_at_25ns.sbatch`) **a terminé (17:09Z)** : stop à step 12,579,600 (25,16 ns), **QC PASS final** (bound_fraction 1,0000, mean_min 2,753 Å, 2 517 frames, achieved 25,17 ns, `termination = USER_DECISION`). Résultat exploitable comme pilote structural secondaire court ; **non intégré à V2609** (décision §16 n°2 : artefact de robustesse archivé). ⚠️ *Superseded (30 Aug evening): décision §16 n°2 REVISED — M1 25.2 ns est désormais INTEGRATED dans le SM V2609 comme appendice `Extended structural stress test`, hors estimand Set-C, pas une campagne multi-réplicats (voir §0.4 M1 status et §17).*
**Status**: **V2609 implementation in progress — canonical data frozen; author review required before submission**. The computational record is substantial, but the current evidence supports computational prioritisation only; it does not establish target engagement, affinity, or resistance resilience.

> **Règle de workflow (permanente) : DAR avant manuscrit.** Toute modification de données, de résultats, de paramètres ou de protocole est tracée dans ce rapport AVANT toute édition du manuscrit ou du SM. Le manuscrit ne cite que des valeurs/statuts déjà reportés ici (source de vérité). En cas de divergence, le DAR fait foi et le manuscrit est corrigé ensuite. Cette règle s'applique à tous les projets (P1–P6) via leurs DAR respectifs et AGENTS.md.

## 0. Canonical-scope note

This is the only P2 DAR. The directory has no P2 V1/V2/.../Vn duplicates. **Version policy (30 Aug 2026):** P2 V2607 = canonical data/source release (immutable, not edited); **P2 V2609 = canonical manuscript release for submission** (see §0.4). Internal superseded artefacts (e.g. witness trajectories 15259/15260, failed QC wrappers 15384/15385) are referenced inline in §5bis. The `Project2_Polypharmacology_MD_ValidationV2607` directory at the root of the repo is the only P2 project.

The legacy `.archive_P2_V2607_20260720/` at the repo root is an early-archive copy retained only for `git log` continuity; do not use as a source for new claims.

## 0.1 Canonical directory inventory

```
Project2_Polypharmacology_MD_ValidationV2607/    ← canonical (this report)
├── README.md
├── P2_DATA_ANALYSIS_REPORT.md                    (this file, canonical DAR)
├── Polypharmacology_MD_Validation_V2607.{aux,bbl,blg,log,out,pdf}    (compiled main, root copy)
├── gmx_MMPBSA.log                                (root gmx_MMPBSA run, gitignored)
├── RESULTS_gmx_MMPBSA.h5                         (root MM-GBSA H5, gitignored)
├── analysis/                                     (PP-11 C59R investigation markdown)
├── data/                                         (external + from_project1 + proteins + README)
├── docs/                                         (P2-specific docs)
├── environments/                                 (environment files)
├── logs/                                         (job logs)
├── manuscript/
│   ├── README.md
│   ├── LaTeX/                                    (canonical LaTeX)
│   │   ├── Polypharmacology_MD_Validation_V2607.tex    (main, JCIM target)
│   │   ├── Polypharmacology_MD_Validation_SM_V2607.tex (SI)
│   │   ├── Secondary_Analyses_SI.tex
│   │   ├── Cover_Letter.{tex,pdf}
│   │   ├── Bibliography_P2.bib
│   │   ├── acs-Polypharmacology_MD_Validation_V2607.bib
│   │   ├── acs-Polypharmacology_MD_Validation_SM_V2607.bib
│   │   ├── Graphics/                              (PDFs referenced by LaTeX)
│   │   ├── Table_RRS_Primary.tex, Table_S*.tex   (12 SI tables)
│   │   └── SUBMISSION_MANIFEST.md                (canonical, refreshed 27 Aug)
├── MD_systems/                                   (6 receptor systems: 164_PfClpP, 201_DHFR, 201_PfDHFR, 214_PfCRT, 438_ATP4, 438_PfATP4)
├── results/                                      (55 top-level entries; see §0.2 below)
├── scripts/                                      (149 scripts; key entry points below)
└── tests/                                        (3 test modules)
    ├── test_lightweight_robustness.py
    ├── test_pfcrt_pipeline.py
    └── test_rigorous_audit.py
```

## 0.2 results/ layout (key entry points)

| Path | Purpose | Status (29 Aug) |
|---|---|---|
| `results/c_rrs_classification.csv` | Set-C RRS classes (target-balanced + available-target) | `COMPUTED` |
| `results/c_rrs_sensitivity.csv` | coverage / threshold sensitivity | `COMPUTED` |
| `results/c_acsi_scores.csv` | ACSI per candidate | `COMPUTED` |
| `results/c_acsi_weight_sensitivity.{csv,json}` | 8 perturbation weights | `COMPUTED` |
| `results/c_pns_ranking.csv` | PNS scores | `COMPUTED` |
| `results/cross_metric_statistical_audit.{csv,json}` | 100k perm + 10k boot | `COMPUTED` |
| `results/pns_imputation_sensitivity.{csv,json}` | zero-to-double PfCRT centrality | `COMPUTED` |
| `results/p2_rigorous_audit_manifest.json` | seed-42 manifest | `COMPUTED` |
| `results/p2_results_unlock_manifest.json` | provenance unlock audit | `COMPUTED` |
| `results/set_c_md/md_rrs_discriminative_manifest.json` | MD-RRS manifest (5Å gate lifted) | `COMPUTED` |
| `results/set_c_md/md_rrs_discriminative_pilot.csv` | per-system MD-RRS_d | `COMPUTED` |
| `results/set_c_md/md_vs_docking_comparison_pilot.csv` | MD-vs-docking direction | `COMPUTED` |
| `results/set_c_md/mmgbsa_20260819/` | Set-C MM-GBSA outputs (16 sys) | `MMGBSA_COMPUTED` (16/16) |
| `results/set_c_md/mmgbsa_summary_pilot.csv` | 16-row ΔG_bind summary | `COMPUTED` |
| `results/set_c_md/mmgbsa_manifest.json` | Set-C MM-GBSA manifest | `COMPUTED` |
| `results/set_c_md/md_systems/.../runs/20260815T185233Z/...` | canonical R1 (PP-01, PP-02) | production + QC + MM-GBSA COMPLETE |
| `results/set_c_md/single_rerun_20260825/...` | R2 PP-01 PfCRT WT + K76A + DHFR I164L | COMPLETE / BOND-overflow resolved |
| `results/pp15_docking_20260828/` | PP-15 Vina (2 WT poses) | `COMPLETE` |
| `results/pp15_md_20260828/` | PP-15 MD (2 WT, prep PASS) | `COMPLETE`, MM-GBSA FINAL 29 Aug 06:58Z |
| `results/robustness_transfer_20260827/` | LOO + perturbation + external replication | `COMPUTED` 27-28 Aug |
| `results/p2rank_boxes_20260827/` | P2Rank 2.5.1 binding-pocket audit | `COMPUTED_EXPLORATORY_BOUNDARY_AUDIT` |
| `results/prolif_ifp_20260827/` | ProLIF 2.2.1 IFP occupancy 16/16 | `COMPUTED_SECONDARY_POST_PROCESSING` |
| `results/rrs_polypharma_secondary_20260828/` | Set-C bootstrap CI95 + MD-filter gate | `COMPUTED_SECONDARY` 28 Aug |
| `results/lightweight_robustness/` | MM-GBSA ΔΔG + partial corr + bootstrap | `COMPUTED` 25 Aug |

## 0.3 Reproducibility runbook

```bash
cd Project2_Polypharmacology_MD_ValidationV2607
source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate malaria_md

# 1. Rigorous audit (regenerates c_rrs_*.csv, cross_metric_statistical_audit.*, pns_imputation_sensitivity.*, manifest)
python3 scripts/p2_rigorous_audit.py --seed 42

# 2. ACSI weight sensitivity (8 ±20% perturbations)
python3 scripts/p2_acsi_weight_sensitivity.py

# 3. Lightweight robustness (MM-GBSA ΔΔG, partial corr, bootstrap)
python3 scripts/lightweight_runs_20260825.py

# 4. External docking replication audit (replay manifest, recompute aggregate)
python3 scripts/p2_external_docking_aggregate_20260827.py

# 5. RRS/polypharma secondary (Set-C bootstrap + MD-filter gate)
python3 scripts/p2_rrs_polypharma_secondary_20260828.py

# 6. P2Rank + ProLIF audits (no new MD)
python3 scripts/p2_p2rank_audit_20260827.py
python3 scripts/p2_prolif_ifp_pilot.py

# 7. GNINA CNN consensus (rescoring, no new MD)
python3 scripts/p2_gnina_consensus_rescore.py
python3 scripts/p2_gnina_consensus_rrs.py

# 8. Unit tests
python3 -m pytest tests/ -q   # 19 passed, 1 skipped in malaria_md

# 9. LaTeX compile (V2609 release)
cd manuscript/LaTeX
pdflatex Polypharmacology_MD_Validation_SM_V2609.tex
pdflatex Polypharmacology_MD_Validation_V2609.tex
pdflatex Polypharmacology_MD_Validation_SM_V2609.tex
pdflatex Polypharmacology_MD_Validation_V2609.tex
pdflatex Cover_Letter_V2609.tex
# (V2607 canonical sources compile the same way with the V2607 names.)

# 10. M1 post-kill QC (partial replicate, real achieved duration)
python3 scripts/p2_m1_postkill_qc.py \
  --replicate results/m1_replicated_md_20260829/PP-01_PfDHFR_WT/replicate_1 \
  --target-ns 100.0
# 11. M1 continuation launcher (100 ns from latest checkpoint)
sbatch scripts/p2_m1_continue_100ns.sbatch
```

The current canonical Set-C pilot production was generated by the 15320 SLURM array (post-production manifest `results/set_c_md/post_production_manifest_pilot.json` v3, schema-fixed 2026-08-18T21:29:54Z). Trajectory QC rule: `setc_p2_minheavy_5A_ge10percent_v1`. The full-panel Set-C MD-RRS (17×8=136) is `NOT_COMPUTED` by design.

## 0.4 Manuscript status (cross-ref)

**Editorial gate (updated 30 Aug 2026): V2609 implementation in progress — canonical data frozen; AUTHOR REVIEW REQUIRED before submission.** The 29-Aug HOLD gate was lifted once the evidence-level/claim policy was added (DAR §7.0) and the V2609 narrative refinement (calibration-and-triage framing) was implemented and audited (checkpoints §11–§12; `docs/P2_V2609_NARRATIVE_PIVOT_PLAN.md`, `docs/P2_V2609_IMPLEMENTATION_PLAN.md`). No new manuscript claim, table, figure, or abstract wording may be added until every cited result has a single canonical provenance record below; PP-01 multi-seed redocking remains reportable only with the canonical ligand preparation and exact grid provenance (the earlier non-canonical runs remain explicitly excluded from inference).

**Release files:** V2607 = canonical data/source release (immutable, NOT to be edited); **V2609 = canonical manuscript release for submission** (`manuscript/LaTeX/Polypharmacology_MD_Validation_V2609.tex` + `_SM_V2609.tex` + `Cover_Letter_V2609.tex` + `SUBMISSION_MANIFEST_V2609.md`). **Decision (author, 30 Aug PM): work on V2609 only — one version; V2607.tex is left at its committed state and is not compiled or edited further.** V2609 recompile (30 Aug PM, after title/`??`/bib fixes; SM page count updated after the M1 stress-test appendix): main 32 p. / SM 20 p. / cover 1 p., 0 LaTeX error, 0 undefined reference, 0 `??` (build order: SM → main → SM → main, per the xr/`\externaldocument` policy). Title updated to *Calibrating the Interpretation of Docking-Derived Resistance-Retention Scores with a Short Molecular-Dynamics Structural Stress Test* (main, SM, cover letter); Conclusion strengthened with the PP-01/PP-02 pilot-gate statement; the fragile `\cref{sec:setc_pilot}` forward reference to an unnumbered section (rendered `??` on clean rebuild) was replaced by an explicit textual reference; `soares2023mdreport` was missing from all `.bib` files (DAR §12 claimed it was added but it was not) and has now been added to `Bibliography_P2.bib` with the correct DOI 10.1021/acs.jcim.3c00599 and regenerated `.bbl`s — citation renders as (21). All robustness outputs (GNINA CNN consensus, external docking replication, MD-filter gate, bootstrap CI95) are integrated; Vina-only remains the canonical docking estimand; the PBC-whole PP-15 MM-GBSA was added 29 Aug 06:58Z; the PP-01/PP-15 multi-seed table (S17) was updated 30 Aug with the honest PfCRT provenance caveat.

**M1 status (see §14–§17):** the 25 ns continuation (job 15715) is COMPLETE, QC PASS and reconciled; after the SM author review (30 Aug, decision §16 n°2 REVISED) it is INTEGRATED into the SM V2609 as an archival `Extended structural stress test` appendix (outside the Set-C estimand, not a multi-replicate campaign). **Decision (author, 30 Aug PM): M1 target reduced from 100 ns to 25 ns** — JCIM (Soares et al., DOI 10.1021/acs.jcim.3c00599) mandates ≥ 3 replicates with *adequate* duration, not a specific length; 25 ns is a round, defensible length for the secondary structural-stress pilot and frees ~60 h GPU. Watcher `scripts/p2_m1_stop_at_25ns.sh` stops job 15715 at step 12,500,000 (25 ns) and runs post-kill QC with `termination = USER_DECISION`; provenance will record the true achieved ns.

**SLURM jobs table (current, 30 Aug 2026):**

| Job | Script | State | Result |
|---|---|---|---|
| 15320 | Set-C 16-system production array | ✅ COMPLETE | 16/16 production runs, post-production chain v3 (see §5bis) |
| 15671 / 15683 / 15695 | M1 attempts | ❌ fail-closed (pre-production) | GMXRC nounset / invalid source paths; excluded from analysis |
| 15707 / 15710 | M1 attempts | ❌ fail-closed (`grompp` `tc-integrator`) | corrected in `production.mdp`; excluded |
| 15711 | M1 array 0-11 (task 0 = PP-01 PfDHFR WT rep1) | ⏹️ task 0 stopped by decision at 23.41 ns; tasks 1-11 cancelled (option A, §14) | partial trajectory 23.4 ns; QC PASS |
| 15714 | M1 continuation attempt | ❌ exit 141 (SIGPIPE in checkpoint selection) | pipe-free selection fix applied |
| 15715 | M1 continuation (`p2_m1_continue_100ns.sbatch`, 96 h) | ⏹️ stopped by watcher 15716 at step 12,579,600 (25.16 ns), QC PASS | achieved 25.17 ns, `termination = USER_DECISION` |
| 15716 | M1 watcher (`p2_m1_stop_at_25ns.sbatch`) | ✅ COMPLETE | scancel at 25 ns + post-kill QC; see §17 |

## 1. Central question

Does a resistance-aware, target-level computational workflow (docking-derived RRS + PNS + ACSI + targeted MD) distinguish predicted potency from predicted resilience in a chemically diverse antimalarial library — and what does a targeted MD pilot add beyond docking?

**Bounded answer:** the workflow supports *computational prioritisation* but does **not** establish biological target engagement, resistance circumvention, or pathway-level mechanism (as stated in the manuscript abstract).

## 2. Primary cohort: Set-C docking (17 candidates, 136 systems)

- **17 candidates** selected by MPO ≥ 0.70, SYBA > 0, SI > 10 from 19 913 primary leads.
- **136 Vina docking systems**: PfDHFR (WT + N51I, C59R, S108N, I164L) and PfCRT (WT + K76T, K76A).
- **Target-balanced primary RRS classification (12/17 complete panels):** 1 Class A*, 1 Class A, 4 Class B, 5 Class C, and 1 Class D.
- **Available-target sensitivity classification (17/17):** 5 Class A*, 1 Class A, 5 Class B, 5 Class C, and 1 Class D. The five PfCRT-only candidates are not evidence-equivalent to the complete two-target set.
- Primary PNS–RRS: Spearman **ρ = −0.2098**, two-sided permutation **p = 0.5144**, Bonferroni-adjusted **p = 1.0000**, bootstrap 95% interval [−0.7582, 0.5429] (**n = 12**).
- Coverage-sensitive PNS–RRS: **ρ = −0.5588**, permutation **p = 0.0222**, adjusted **p = 0.0667** (**n = 17**); this is exploratory because target coverage is unequal.
- Primary ACSI–RRS: **ρ = −0.4056**, permutation **p = 0.1922**, adjusted **p = 0.5766**; primary RRS–weakest-WT-score: **ρ = −0.1661**, permutation **p = 0.6038**, adjusted **p = 1.0000**.
- ACSI > 0.70 for **2/17** candidates; the coverage-sensitive ACSI–PNS association was ρ = −0.078 (p = 0.764), while the target-balanced value was ρ = −0.301 (p = 0.342).
- ACSI weight sensitivity (`results/c_acsi_weight_sensitivity.csv`, generated by `scripts/p2_acsi_weight_sensitivity.py`): eight ±20% one-at-a-time perturbations on the canonical 17-candidate cohort, with proportional rescaling of the other weights. Spearman ρ versus baseline = **0.9167–0.9804**; top-five Jaccard overlap = **0.6667–1.0000**. This is a local cohort stability check, not evidence for full-library top-20 robustness because the full-library component matrix is not in the committed source record.
- RRS versus the weakest eligible WT score: primary ρ = −0.1661 (permutation p = 0.6038; adjusted p = 1.0000; n = 12); the available-target sensitivity value is ρ = +0.1759 (p = 0.4947; n = 17).
- Tartarus calibration, independent-tool cross-docking comparison, and MPO sensitivity analysis are documented in the Supporting Information; the main manuscript retains only the concise interpretation and points to the corresponding SI tables.

## 3. Rigorous audit outputs and estimand controls

The canonical re-analysis is `scripts/p2_rigorous_audit.py` (seed 42). It regenerates `c_rrs_classification.csv`, `c_rrs_sensitivity.csv`, `cross_metric_statistical_audit.csv/json`, `pns_imputation_sensitivity.csv/json`, and the audit manifest. RRS classes are mutually exclusive: A*/A require all available mutant RRS values ≥80%, B requires all ≥70% but not all ≥80%, C requires at least one ≥80% but not all ≥70%, and D is the residual class in which no available mutant reaches 80%. The A*/A potency discriminator uses the **minimum eligible WT score magnitude**, not the strongest target. The primary class count is restricted to candidates with all six target-specific mutant ratios defined across PfDHFR and PfCRT.

The five PfCRT-only candidates are reported only in the available-target sensitivity analysis. Target-specific columns in `c_rrs_classification.csv` preserve the PfDHFR and PfCRT estimands, eligible-target count, mutant-state count, and both weakest/strongest WT anchors. This prevents unequal target coverage from being mistaken for pan-target resilience.

The cross-metric audit uses 100,000 seeded permutations and 10,000 bootstrap resamples. Its p-values and intervals are descriptive after candidate selection, not independent validation. PNS-imputation sensitivity gives Spearman rank correlations of 0.9632–1.0000 across zero-to-double canonical PfCRT centrality, but rank robustness does not validate the biological centrality assumption.

## 4. Parent-study targeted MD cohort (4 systems, 10 ns each)

| System | Outcome | MM-GBSA |
|---|---|---|
| PfCRT–214 | Bound (min dist 3.19 Å, 78 contacts, 23 H-bonds) | **−18.25 ± 0.40 kcal/mol** (101 snapshots, interpretable) |
| PfATP4–438 | Bound (min dist 2.25 Å, 178 contacts) | N/A — CHARMM36→AMBER conversion corrupted (+473 kcal/mol vdW inflation artifact) |
| PfClpR-labelled 164 | Unbound (67.4 Å) | N/A — dissociated |
| PfDHFR–201 | Unbound (78.2 Å) | N/A — dissociated |

## 5. Set-C MD pilot (16 systems, 10 ns each) — secondary analysis (NEW 19 Aug)

**Production:** 16 systems (PP-01, PP-02 × PfDHFR WT/N51I/C59R/S108N/I164L, PfCRT WT/K76T/K76A), 10 ns each, 310.15 K, GPU A4000 (job array 15320): CHARMM36m proteins with ligand parameters from OpenFF 2.2.0 AM1-BCC under the declared, PI-approved force-field policy deviation specific to this pilot (verified throughput witness job 15270 = 28.169 ns/day).
**Trajectory QC:** 16/16 PASS (authoritative post-production wrapper 15386; earlier attempts 15384/15385 are non-canonical and failed on an MDAnalysis API incompatibility; rule `setc_p2_minheavy_5A_ge10percent_v1`; hash-verified inputs/outputs).

### 4.1 Discriminative MD-RRS (multi-threshold, lifts the binary ceiling)

`results/set_c_md/md_rrs_discriminative_manifest.json` + `md_rrs_discriminative_pilot.csv`.
The 5 Å bound-fraction ceiling (all 16 systems = 1.000) is lifted with continuous metrics:
bound fractions at 2.0–4.0 Å, mean/p5 min heavy-atom distance, and MD_RRS_d = (mutant distance / WT distance) × 100 (>100 = looser).

**Key finding: no mutant shows a *reproducible* weaker-binding signature within 10 ns.** Verified per-system values (`set_c_trajectory_metrics_pilot.csv`, mean minimum heavy-atom distance):
- PP-02 PfDHFR N51I: 1.82 Å vs WT 2.52 Å — markedly tighter (85.0% of frames < 2 Å vs 0.9%); MD_RRS_d = 72.2
- PP-02 PfCRT K76T: 2.77 Å vs WT 3.17 Å — tighter; MD_RRS_d = 87.3
- PP-01 PfDHFR N51I: 2.67 Å vs WT 2.94 Å — tighter (90.0% frames < 3 Å vs 58.9%); MD_RRS_d = 91.0
- MD_RRS_d (mean-ratio) range across the 12 mutant states: **72.2–102.7**; two states marginally above 100 (PP-01 PfCRT K76T 102.7, PP-02 PfDHFR C59R 102.0), within ±3% of the WT reference — not a reproducible weakening signal within a single 10 ns replicate.

**Honest caveat:** 10 ns measures local geometry, not affinity; this does **not** demonstrate resistance.

### 4.2 MD vs docking direction comparison

`results/set_c_md/md_vs_docking_comparison_pilot.csv` — mapping by canonical SMILES.

| Candidate | Docking (RRS) | MD 10 ns (MD_RRS_d) | Direction |
|---|---|---|---|
| PP-01 (6 mutants) | 83.9–92.5 → **looser** | 91.0–102.7 → 5 tighter, 1 marginally looser (PfCRT K76T 102.7, concordant with docking) | **Divergent for 5/6** |
| PP-02 PfCRT (K76T/K76A) | 87.9–94.6 looser | 87.3–90.2 tighter | **Divergent** |
| PP-02 PfDHFR (4 mutants) | n/a (no pilot WT reference) | 72.2–102.0 (3 tighter, C59R 102.0 marginally looser) | n/a |

**Interpretation:** methodological divergence dominates (static docking energy vs local 10 ns geometry) — 7 of the 8 systems with both estimates diverge, with PP-01 PfCRT K76T the single concordant case. Neither method demonstrates resistance. Documented as a limitation, not a phenotype claim.

### 4.3 Set-C MM-GBSA (16 systems) — NEW 19 Aug

`results/set_c_md/mmgbsa_20260819/`, protocol identical to the parent cohort (gmx_MMPBSA v1.5.0.3, GB OBC2 igb=5, salt 0.15 M, ε 80/1, 100 ps snapshots = 100 frames, CHARMM36→AMBER).
Summary: `results/set_c_md/mmgbsa_summary_pilot.csv` + `mmgbsa_manifest.json` — **status `MMGBSA_COMPUTED` (16/16)**, regenerated 2026-08-19 after the two PBC-fixed reruns.

| System | ΔG_bind (kcal/mol) | MM-GBSA RRS | Docking RRS |
|---|---|---|---|
| PP-01 PfCRT K76A | −35.29 ± 1.17 | 115.3 | 90.86 |
| PP-01 PfCRT K76T | −29.51 ± 2.65 | 96.4 | 92.47 |
| PP-01 PfCRT WT | −30.61 ± 1.65 | 100.0 (ref) | — |
| PP-01 PfDHFR C59R | −26.56 ± 1.91 | 105.0 | 85.47 |
| PP-01 PfDHFR I164L | −26.13 ± 2.34 | 103.3 | 83.87 |
| PP-01 PfDHFR N51I | −29.83 ± 1.50 | 118.0 | 86.40 |
| PP-01 PfDHFR S108N | −30.21 ± 3.62 | 119.5 | 87.60 |
| PP-01 PfDHFR WT | −25.29 ± 2.94 | 100.0 (ref) | — |
| PP-02 PfCRT K76A | −24.53 ± 1.27 | 97.8 | 94.62 |
| PP-02 PfCRT K76T | −30.45 ± 1.38 | 121.4 | 87.91 |
| PP-02 PfCRT WT | −25.08 ± 2.56 | 100.0 (ref) | — |
| PP-02 PfDHFR C59R | −28.85 ± 1.88 | 95.7 | n/a |
| PP-02 PfDHFR I164L | −31.06 ± 1.52 | 103.0 | n/a |
| PP-02 PfDHFR N51I | −34.02 ± 2.68 | 112.8 | n/a |
| PP-02 PfDHFR S108N | −27.09 ± 1.55 | 89.8 | n/a |
| PP-02 PfDHFR WT | −30.16 ± 2.06 | 100.0 (ref) | — |

**Key findings:**
- All 16 systems yield finite negative ΔG_bind values (range −35.29 to −24.53 kcal/mol; mean −29.04 ± 3.00). Ligand retention is assessed from the declared geometric trajectory-QC gate, not from the sign of an endpoint estimate; all 16 systems passed that gate within the 10 ns pilot.
- 8/12 mutants show MM-GBSA RRS > 100 (tighter than WT); 4/12 below 100 (PP-01 PfCRT K76T 96.4, PP-02 PfCRT K76A 97.8, PP-02 PfDHFR C59R 95.7, PP-02 PfDHFR S108N 89.8).
- For the 8 mutant states with a docking WT reference, docking predicted looser binding (RRS 83.9–94.6); the 4 PP-02 PfDHFR states had no docking WT reference. MM-GBSA does not reproduce the docking direction among the comparable states. The four below-100 cases (89.8–97.8) do not support a robust ranking conclusion under this single-replicate endpoint protocol.
- **Conclusion: no mutant shows a reproducible weaker-binding signature within the pilot timescale**, consistent with the MD-RRS geometry result (§4.2). The docking-vs-MM-GBSA direction divergence remains methodological (static docking energy vs single-replicate endpoint estimate), not a phenotype claim.
- **PBC fix applied:** PP-02_PfCRT_K76A and PP-02_PfDHFR_WT failed the first pass (BOND/UB overflow, protein split across the periodic boundary) and were re-run on `production_whole.xtc` (`gmx trjconv -pbc whole`); both finalized 2026-08-19 12:02.

## 6. PfCRT 114–122 reconstruction chain (technical validation, 18–19 Aug)

`results/md_systems/pfcrt_junction_repair_audit_20260818.md` — full audit.

| Step | Verdict |
|---|---|
| Kabsch graft | 0/16 geometry (C–N junctions 0.85–5.5 Å) |
| OpenMM restrained junction repair | **15/15 unique PASS_GEOMETRY** (1.32–1.37 Å), selected `model_03_seed_001` (loop pLDDT 55.2) |
| Canonical GROMACS check | PASS — 1 continuous chain (VAL47→ASN405), pdb2gmx RC=0, EM converged |
| Canonical MD witness | PASS — EM + NVT 100 ps + NPT 100 ps |
| Long equilibration (jobs 15387+15388) | **CONVERGED** — 1 ns NPT, T 310.17 K (drift 0.03%), ρ 1021.12 kg/m³ (drift −0.017%), P half-window −7.52 → −0.38 bar, 0 error markers |

**Classification:** `GEOMETRY_REPAIR_WITNESS_ONLY` + `CANONICAL_POLICY_TOPOLOGY_CHECK_PASS` + `CANONICAL_MD_WITNESS_PASS` — technical validation only; no affinity/RRS/Set-C claim.

## 7. Interpretation and limitations

### 7.0 Audit boundary and claim policy (29 Aug 2026)

This report distinguishes four evidence levels:

1. **Primary computational estimand:** the prespecified docking-derived RRS/PNS/ACSI analysis on the Set-C cohort.
2. **Secondary computational diagnostics:** MD geometry, single-replicate MM-GBSA, GNINA, P2Rank, ProLIF, robustness, and external docking analyses.
3. **Technical validation:** topology repair, equilibration, file/hash checks, and software-execution checks.
4. **Unobserved biological quantities:** experimental affinity, target engagement, transport, cellular activity, and resistance phenotype.

Only levels 1–3 are available here. Results from levels 2–3 must not be described as validation of level-1 biological claims. A result is manuscript-eligible only when its input files, protocol, software/environment, output hash, and interpretation boundary are recorded in this DAR.

**PP-01 multi-seed reconciliation.** The definitive control used the canonical ligand file and the P1-V2 grid boxes. PfDHFR reproduced the canonical score within the observed seed range (mean −7.499; range −7.529 to −7.475; canonical −7.500). PfCRT gave mean −9.250; range −9.262 to −9.225, approximately 0.04 kcal/mol from the historical −9.300 value. Because the original PfCRT receptor preparation is not preserved, this supports low seed sensitivity of the reproduced protocol but does **not** prove exact reproduction of the historical PfCRT score. The earlier PP-15-grid and Meeko-prepared-ligand runs are non-canonical and excluded from the claim.

**Decision:** PP-01 multi-seed may be reported as a bounded reproducibility diagnostic, not as proof of score accuracy, affinity, or biological resilience.

### 7.1 Interpretation and limitations

- Docking-RRS is a hypothesis about relative mutant sensitivity, not a measurement of mutant free-energy difference.
- The 10 ns Set-C pilot cannot resolve partial affinity loss; the discriminative metrics lift the binary ceiling but show **no** mutant-weakening signal, and docking vs MD directions diverge for PP-01 — methodological, not biological.
- MM-GBSA is a cautious endpoint diagnostic, not a calibrated thermodynamic observable; within-trajectory standard deviations do not represent replicate uncertainty, and each system has a single 10 ns replicate.
- PfCRT reconstruction is a technical/stability witness: no production on the repaired model beyond 1 ns equilibration, no binding/affinity/RRS.
- The study is computational; experimental activity and resistance claims are not made.

## 8. Lightweight robustness and transfer audit (27 Aug 2026)

**Interpretation gate:** all analyses in this section are post-selection sensitivity or transfer diagnostics. They cannot be promoted to independent validation because the candidate set, source chemistry, and/or scoring protocol overlap with the primary analysis.

### Companion P1 context

P1 V7 was audited as an upstream companion source. Its redocking, DEKOIS/MMV enrichment, physicochemical, chemical-space, scaffold, and MPO-sensitivity outputs are usable in P2 only as methodological or chemical-space context. A cohort audit confirmed exact identity for all 17 PP-01--PP-17 SMILES; the overlap and shared workflow provenance preclude independent-replication claims. The source files, hashes, and permitted-use boundary are recorded in `results/robustness_transfer_20260827/external_transfer_audit.json` and `p1_p2_cohort_audit.json`; the boundary is summarized in the P1-context SI table.


A bounded post-processing audit was completed without new docking, MD, MM-GBSA, network extraction, or external data retrieval. Script: `scripts/p2_robustness_transfer_audit.py`; seed `20260827`; outputs: `results/robustness_transfer_20260827/`.

- Leave-one-candidate-out analysis on the complete two-target set (`n=12`) produced 12 records. PNS--RRS Spearman $\rho$ ranged from $-0.3182$ to $0.0273; ACSI--RRS ranged from $-0.7636$ to $-0.3182$; RRS versus weakest eligible WT anchor ranged from $-0.2805$ to $0.0876$. These are post-selection sensitivity diagnostics, not confirmatory tests.
- Target-stratified correlations were PfDHFR PNS--RRS $\rho=-0.3497$ (`n=12`) and PfCRT PNS--RRS $\rho=-0.0417$ (`n=17`), demonstrating that target-specific patterns should not be substituted for the pooled estimand.
- Bounded $\pm\qty{1}{\kcalmol}$ perturbations of individual docking scores generated 272 candidate--score records; the RRS class was unchanged in 212/272 (`\qty{77.9}{\percent}`). Stability was higher for a negative perturbation (`\qty{88.2}{\percent}`) than for a positive perturbation (`\qty{67.6}{\percent}`), and WT-score perturbation was more influential than most mutant-score perturbations. This documents operational threshold sensitivity rather than score uncertainty or biological resilience.
- The existing threshold-sensitivity output was copied into the versioned audit directory without recomputation. The related P5 ChEMBL artifacts were hash-audited as `RELATED_PROJECT_EXTERNAL_ARTIFACT`. A feasibility audit found that the local ChEMBL panel contains general *P. falciparum* activity labels but no paired PfDHFR/PfCRT WT--mutant scores or measurements; therefore ChEMBL itself is not an independent external P2-RRS replication. The panel remains usable only as related-project activity-transfer evidence, not as validation of P2 RRS or experimental biology. Details: `results/robustness_transfer_20260827/step1_external_rRS_feasibility.md`. The targeted docking replication plan and its completed execution record are in `results/robustness_transfer_20260827/targeted_external_docking_replication_plan.md` and `.json`.

**External docking replication — array 15605 and declared repair (27–28 Aug 2026):** the frozen 40-ligand × 8-state panel initially returned **243/320** valid poses. The missing states were attributable to four documented ligand-preparation/execution cases (not interpreted as docking failures), handled in `external_docking_repair_ledger.json` with the original panel provenance preserved:

- **(A) salt/counterion** → free base: EXT-019 (.Cl), EXT-021 (.2Cl), EXT-032 (.2Cl), EXT-033 (.Cl), EXT-036 (.2Cl), EXT-037 (.oxalate).
- **(B) RDKit distance-geometry failure** → Open Babel `--gen3d` fallback: EXT-008 (69 heavy atoms, 52 rotatable bonds), EXT-038.
- **(C) SLURM time-limit partial** → only the 5 missing states re-docked: EXT-007 (3/8 existed).
- **(D) declared EMBED_FAILURE** → **EXT-039** (folded cyclic ether macrocycle): no 3D coordinates under RDKit DG, RDKit random-coords, or OBabel `--gen3d` within reasonable compute; excluded **by declaration**, so the panel target is **39 ligands × 8 states = 312 records**.

The 9 repairable ligands (69 states) were re-docked by `p2_external_docking_repair.sh`. The fail-closed chain then completed the 312-record audit, aggregation, and external RRS calculation. The aggregate contains 312/312 finite, unique ligand–state records; the ligand-level RRS file contains 39 rows, with 38 Class A and 1 Class D. `EXT-039` remains a declared `EMBED_FAILURE` and contributes no score. Machine-readable outputs are `external_docking_aggregate_20260827/external_docking_scores.csv`, `external_docking_rrs_20260827.csv`, and `external_docking_rrs_20260827.json`; panel and aggregate hashes are recorded in their manifests. A bounded bootstrap summary (`external_vs_primary_bootstrap_20260828.json`, seed 42, B=10,000) gives an external mean RRS of 100.45 (95% bootstrap interval 99.59–101.32) and an external Class-A fraction of 0.974 (95% interval 0.923–1.000). The primary and external summaries are compared descriptively only because their cohorts and preparation provenance differ. This is docking-derived replication evidence only, not experimental validation or an MD estimate.

## 8bis. Independent pocket and interaction audits (27 Aug 2026) — post-processing only

Two post-processing audits were run without new MD or docking; both are exploratory boundary evidence and change no canonical score, RRS classification, or manuscript claim.

### P2Rank binding-pocket audit — `results/p2rank_boxes_20260827/`

P2Rank 2.5.1 (JDK 17 via `conda env jdk17`; Java 8 system JRE is too old for class-61 bytecode) predicted ligandable pockets on the four P2 receptors. Grid boxes came from `data/from_project1/docking/Docking_*/config.txt`.

- **PfCRT (6UKJ):** the top P2Rank pocket (score 162.7, probability 0.999 — far the most ligandable site, >5x the runner-up) lies **5.7 Å** from the Vina box center: independent corroboration of the docking box.
- **PfDHFR (7F3Y):** top pockets 25–40 Å from the box center; a receptor-frame caveat applies (the P1 `config.txt` may derive from a different preparation than `receptor_fixed.pdb`), so this is a provenance flag, not a refutation.
- **PfATP4 (9N10):** top pockets 23–46 Å from the box center; the input frame matches the docking PDBQT, so the separation warrants a manual recheck of the 9N10 pocket definition.
- **PfClpP (2F6I):** low scores (5–6) and probabilities (0.23–0.30); no P2 Vina grid exists for 2F6I (ClpP docking ran in P1 V4/V7), so this is a frame-independent report only.

Status: `COMPUTED_EXPLORATORY_BOUNDARY_AUDIT`. Details: `results/p2rank_boxes_20260827/README.md`.

### ProLIF interaction-fingerprint occupancy — `results/prolif_ifp_20260827/` (COMPLETE 16/16)

ProLIF 2.2.1 (`pip install prolif` in `malaria_md`; v2 API: `generate()` on the current trajectory frame, interaction names `HBDonor`/`HBAcceptor`/`VdWContact`, `ResidueId.name/.number/.chain`) computes ligand-protein interaction occupancy on the 16 QC-PASS pilot trajectories (100-frame subsample, ~10 min/system).

- Script: `scripts/p2_prolif_ifp_pilot.py`; per-system `ifp_<system>.csv` + `prolif_summary.json` + `README.md`.
- **All 16/16 systems computed**, each with 4–11 contacts at ≥ 50 % occupancy, most at 100 %; no system shows contact loss. Descriptive highlights: PfCRT TYR16 at 100 % occupancy in 5/6 PfCRT systems (conserved aromatic site residue); PfDHFR LEU46/MET55 recur across PP-01 states, LEU40/ILE14 across PP-02 states.

Status: `COMPUTED_SECONDARY_POST_PROCESSING`. These are descriptive trajectory-interaction occupancies that corroborate the retention-not-gain reading of the MD-RRS/MM-GBSA pilot (ligand stays in contact with conserved binding-site residues); they are not binding affinities, free energies, or biological resistance evidence, and no canonical value or manuscript claim is modified.

## 8ter. PP-15 single-ligand docking/MD — `results/pp15_docking_20260828/` + `results/pp15_md_20260828/` (28 Aug 2026)

Single-candidate pilot for PP-15 (outside the 17-member Set-C estimand). Docking (Vina) produced `PP-15_PfCRT_WT` and `PP-15_PfDHFR_WT` poses (`vina/*.pdbqt` + `metadata.json`); MD preparation completed two WT systems (`PP-15_PfCRT_WT`, `PP-15_PfDHFR_WT`) with `pre_equilibration_audit.json:PASS`, `forcefield_manifest.json`, and `system_manifest.json`. **State (28 Aug 19:50Z, corrected):** contrary to the earlier ``prepared-pending / no production`` note, **both WT systems have completed 10 ns production trajectories** — PfDHFR runs `20260825T063226Z` (finished 27 Aug 02:55Z, 5,000,000 steps) and `20260813T083606Z`; PfCRT runs `20260825T063226Z` (finished 25 Aug 13:08Z, 5,000,000 steps) and `20260815T052351Z`. The self-contained run directories carry the original valid ligand ITP (28,139 B, OpenFF 2.2.0 AM1-BCC); a regeneration attempt on 28 Aug 14:45Z wrote an inconsistent 40-atom ITP to the base directory that broke `grompp` against the 42-atom `npt.gro` — **reverted** by restoring the run-consistent ITP (28 Aug 19:46Z, `grompp` revalidated PASS). Trajectory QC (job 15653, rule `setc_p2_minheavy_5A_ge10percent_v1`) on the canonical `20260825T063226Z` runs: **both PASS** — PfDHFR bound_fraction 1.000, mean_min 2.77 Å, 10.0 ns; PfCRT bound_fraction 1.000, mean_min 3.20 Å, 10.0 ns (`results/pp15_md_20260828/pp15_trajectory_qc.csv`). **MM-GBSA (FINAL, job 15656 PBC-whole, 29 Aug 06:58Z):** after the `endframe=880`/`endframe=800` first-pass runs hit BOND-overflow frames (PBC artifact), the PBC-whole fix (gmx `trjconv -pbc whole` on the canonical `20260825T063226Z` runs → `production_whole.xtc`) re-ran both endpoints in a single pass with numerical QC: **PfDHFR ΔTOTAL = −29.52 ± 0.33 kcal/mol (100 frames, endframe=1000)**, **PfCRT ΔTOTAL = −27.79 ± 0.49 kcal/mol (80 frames, endframe=800)** — both `numerical QC PASS — reportable`, `Finalizing gmx_MMPBSA: [ERROR]=0 [WARNING]=0`. Both values lie within the pilot endpoint range and are now in the manuscript/SM. No mutant, no RRS — `EXPLORATORY_SINGLE_LIGAND_PILOT`. **Manuscript integration (28–29 Aug):** SM §7b updated with production + MM-GBSA state and Table S (Vina scores PfDHFR −8.62 / PfCRT −7.81 kcal/mol, audit PASS, 10 ns complete both, MM-GBSA −29.52 ± 0.33 / −27.79 ± 0.49, bound fraction 1.000); a main-text sentence in the Set-C pilot subsection (both systems completed 10 ns production with MM-GBSA estimates); explicitly outside the Set-C estimand. Not merged into Set-C tables. Root-cause note: the original PBC retry in `p2_setc_mmgbsa_single.py` triggered only on `rc != 0` — patched to also trigger on numerical-QC failure and to use `-pbc whole` (the `-mol` flag is invalid in GROMACS 2025.4).

## 8quater. RRS/polypharma impactful extensions — secondary, no new MD (28 Aug 2026)

Planned secondary audits that strengthen RRS+polypharma without new trajectories (ponytail: reuse existing 312-record external docking + 16-system pilot):

- **Per-target bootstrap RRS CI95** — bootstrap B=10k per-target on `c_rrs_classification.csv` (PfDHFR n=12, PfCRT n=17) and on `external_docking_rrs_20260827.csv` (39 ligands); report CI95 per RRS class (A*/A/B/C/D) and per-target retention fraction. Seed 42, same as `p2_robustness_transfer_audit.py`.
- **MD-filter retention gate** — intersect docking RRS ≥80% (Class A) with pilot MD-RRS_d retention (<100 = tighter/looser parity) for PP-01/PP-02; candidates passing both gates are polypharma-promoted (≥2 targets, retention-not-gain). No full-panel claim; uses existing `md_rrs_discriminative_pilot.csv` + `mmgbsa_ddeltaG_pilot.csv`.
- **Literature anchor** — Trends Parasitol 2026 SDMT MED6-189 (multi-target high barrier) + RSC Adv 2026 PfATP4/DHFR/DHODH/PfCRT mechanistic classes already in `docs/CENTRAL_QUESTIONS_PROJECTS.md:28`; cite in P2 Discussion to justify per-target WT denominator and polypharma ≥2-target threshold.

### 8quater.0 Bootstrap RRS CI95 + MD-filter retention gate — COMPUTED (28 Aug 2026)

Script: `scripts/p2_rrs_polypharma_secondary_20260828.py` (seed 42, B=10\u2074). Outputs: `results/rrs_polypharma_secondary_20260828/{secondary_summary.json, md_filter_gate.csv}`.

**RUN1 — Set-C bootstrap CI95 (n=17):** class fractions A* 0.294 [0.118, 0.529], A 0.059 [0.000, 0.176], B 0.294 [0.118, 0.529], C 0.294 [0.118, 0.529], D 0.059 [0.000, 0.176]. Per-mutant retention (pooled, WT=100): PfDHFR N51I 74.7 [67.2, 85.2], C59R 73.7 [67.4, 82.1], S108N 75.3 [67.7, 85.8], I164L 76.8 [68.9, 88.2] (n=12); PfCRT K76T 85.4 [81.0, 90.4], K76A 87.0 [83.1, 90.9] (n=17). The PfCRT retention CIs exclude 100, consistent with the retention-not-gain reading; the PfDHFR CIs are wide and overlap 100 for I164L.

**RUN1b — external panel bootstrap:** mean RRS 100.45 [99.59, 101.32], class-A fraction 0.974 [0.923, 1.000] (matches `external_vs_primary_bootstrap_20260828.json` and the robustness-transfer SI table).

**RUN2 — MD-filter retention gate (pilot scope PP-01/PP-02, 12 gate rows):** docking RRS \u2265 80 AND pilot MD-RRS < 100. 7/12 rows pass both gates. **PP-01 is polypharma-promoted at pilot scope** (PfCRT via K76A MD-RRS 97.8, PfDHFR 4/4 mutants 91.0\u201398.9; docking RRS 91.7 / 85.8). PP-02 is NOT promoted: its PfCRT rows pass (90.1/87.3) but PfDHFR has no eligible docking WT anchor under the 5.0 kcal/mol rule, so only one target is gate-eligible. K76T MD-RRS 102.7 for PP-01 PfCRT is the one >100 row and is read as within-noise retention, not gain.

Status: `COMPUTED_SECONDARY`; pilot-scope promotion only; full-panel (17\u00d78=136) MD-RRS remains `NOT_COMPUTED`; no canonical value replaced.

### 8quater.1 GNINA CNN consensus rescoring — COMPUTED (28 Aug 2026)

Post-processing only (no re-docking, no new MD). Script: `scripts/p2_gnina_consensus_rescore.py` (GNINA 1.3.2 `--score_only` on the MODEL 1 Vina pose of each of the 312 external states; non-AD Meeko/OpenBabel generic atom types `CG0/CG1/G0/G1` normalized to `C` in the type column; fail-closed at 312/312 finite scores). Outputs: `results/robustness_transfer_20260827/gnina_consensus_20260828/{gnina_consensus_scores.csv, manifest.json}`.

Consensus RRS analysis (script `scripts/p2_gnina_consensus_rrs.py`, same frozen estimand, target eligibility decided once on the canonical Vina scale):

- **312/312 poses rescored, 0 failures**; Vina scores −10.9…−3.25 (mean −7.03), CNN affinities 2.70…7.71 (mean 4.71).
- **RRS class agreement across scoring layers: 38/38 eligible ligands class A under both Vina and CNN; 0 discordances** (EXT-025 has no binding target under the 5.0 kcal/mol Vina eligibility rule and is unclassified under both layers).
- RRS mean: Vina 100.4 (95.1–106.0), CNN 103.6 (90.6–122.6). Spearman Vina-vs-CNN on ligand mean RRS = **0.558**; per-mutant ρ: K76T 0.644, K76A 0.486, N51I 0.271, S108N 0.204, I164L 0.040, C59R −0.076.

Status: `COMPUTED_CONSENSUS_RRS_SENSITIVITY`. Interpretation: the near-proportional mutant/WT retention observed in the Vina external panel is reproduced by an independent CNN scoring function on identical poses — the retention-not-gain pattern is not an artefact of one scoring function. The moderate ligand-level rank correlation (ρ=0.558) and near-zero C59R/I164L mutant-level correlations bound the interpretation: consensus supports class-level retention, not per-mutant rank transfer. Vina-only remains the canonical estimand; no manuscript value is replaced.

## 9. Manuscript status (updated 30 Aug 2026)

**Current release status:** V2607 canonical data FROZEN; **V2609 narrative release in author review** (`READING_FINAL_AUTHOR`). The primary Set-C docking analysis, the separate parent-study MD cohort, and the bounded Set-C MD pilot have completed their declared production and QC gates. K76A MM-GBSA retains the original canonical endpoint with an explicit Limitations caveat (author decision, 28 Aug). M1 is INTEGRATED into the SM V2609 as an archival `Extended structural stress test` appendix, outside the Set-C estimand and not a multi-replicate campaign (revised decision §16 n°2, 30 Aug evening; see §0.4 M1 status, §17). The optional witness job `15507_[0]` is not a prerequisite for the manuscript and remains non-blocking.

**28 Aug — robustness analyses integrated in manuscript (v2607 recompile clean: main 30 p., SM 16 p., 0 errors, 0 undefined refs):** (1) the pilot-scope MD-filter retention gate (7/12 gate rows pass docking RRS $\geq$ 80 % AND pilot MD-RRS < 100; PP-01 satisfies the two-target gate, PP-02 does not) was added to the Set-C MD pilot Results subsection and Discussion (role of structural follow-up), bounded by the saturated bound fraction and the 2.0 kcal/mol noise floor; (2) the Set-C bootstrap CI95 (class fractions A* 0.294 [0.118, 0.529], PfCRT retention CIs excluding 100, PfDHFR intervals wide) was added to the Discussion and as a new row in the robustness-transfer SI table; (3) SM Table S15 gained the MD-filter gate row. The GNINA CNN consensus (38/38 class A, 0 discordance, ρ=0.558) and external-docking replication were already integrated (Discussion + S15). No canonical value replaced; Vina-only remains the canonical estimand.

**K76A MM-GBSA resolution (author decision, 28 August 2026):** The PP-01 PfCRT K76A endpoint uses the original 19-Aug value (−35.29 ± 1.17 kcal/mol, SD_prop, SEM 0.50) from the canonical trajectory (`20260815T185233Z/replicate_1`, 100 frames). An independent second replicate on a different trajectory (`20260825T063226Z/replicate_1`) produced −27.54 ± 1.89 kcal/mol after PBC-whole correction. The 7.75 kcal/mol inter-replicate difference is documented in the manuscript Limitations section and treated as evidence of inter-replicate sensitivity for this mutant state. The `FAILED_NUMERICAL_QC` status (BOND overflow in sander parsing) applies to the 25–26 Aug diagnostic runs on the second trajectory, not to the original canonical endpoint. The Submission Manifest has been updated to reflect this resolution.

- **Manuscript**: `manuscript/LaTeX/Polypharmacology_MD_Validation_V2607.tex` (main) + `_SM_V2607.tex` (SI). Target: JCIM (ACS).
- **Scientific-article refinement:** the title, abstract and Introduction now foreground docking-derived RRS as the primary estimand; ACSI/PNS and MD are presented as secondary analyses. The Discussion separates primary inference, robustness and limitations. This is an editorial refinement only; no numerical result or analysis population was changed.
- 26 Aug revision: the main manuscript now foregrounds the primary docking-RRS estimand, presents ACSI/PNS and MD as secondary analyses, and keeps detailed tables in the SI. The Discussion separates primary inference, robustness, and limitations while retaining the primary RRS/MD evidence. The transferred material is included through `Secondary_Analyses_SI.tex` and the dedicated SI table sources. The current rigor pass separates target-balanced and coverage-sensitive RRS estimands, corrects the weakest-WT potency discriminator, and adds permutation/bootstrap uncertainty and PNS-imputation sensitivity.
- All numbers in text/tables trace to JSON/CSV data files (manifests listed above).
- Unit tests: `tests/` — **19 passed, 1 skipped** in `malaria_md` (verified 30 Aug 2026), including MD manifests, MM-GBSA aggregation, RRS class definitions, target coverage, regenerated statistical outputs, and lightweight robustness outputs.

## 9. Open items and 25 August reconciliation

> **Open-items inventory (confirmed 29 Aug 2026)** — exhaustive scan of P2 `.md` documents. **No BLOCKED item is active.** The four genuinely non-computed/pending items below are all either by-design limits, missing-input entries, or administrative; none blocks JCIM submission. Historical `NOT_COMPUTED`/`PENDING` wording in runbooks (pre-18 Aug) is superseded.
>
> | # | Item | Status | Blocker / reason |
> |---|------|--------|------------------|
> | 1 | Full-panel Set-C MD-RRS (17 cand., 136 sys) | `NOT_COMPUTED` **by design** | full-cohort production contract never prepared; pilot (PP-01/PP-02, 16 sys) is the only canonical MD-RRS |
> | 2 | STRING 400/900 threshold sensitivity | **`COMPUTED` (29 Aug 2026)** | closed by `scripts/p2_string_threshold_sensitivity.py` — see §9 update below |
> | 3 | PP-15 + PP-01 multi-seed redocking | **`COMPUTED` (29 Aug 2026)** | jobs 15668/15669 (PP-15, ±0.03 kcal/mol); PP-01 `COMPUTED` (29 Aug, canonical ligand + P1-V2 grids, ±0.05 kcal/mol) — see §9 update below |
> | 4 | Zenodo deposit / DOI | `pending` | archive deposit not yet made (see SUBMISSION_MANIFEST.md) |

- [x] Existing-results unlock audit: PfCRT pH 5.2 redocking verified 100/100; PNS imputation sensitivity verified 17/17; lightweight RRS thresholds, leave-one-mutant-out, and score perturbations regenerated.
- [x] Provenance manifest added: `results/p2_results_unlock_manifest.json`.
- [x] Short-MD execution was attempted under authorized array `15428`; tasks failed closed at `grompp` because the execution node lacked `charmm36-jul2022.ff/forcefield.itp`, and the remaining tasks were canceled. No new valid short-MD trajectory is promoted. Full details: `docs/P2_SHORT_MD_EXECUTION_STATUS_20260825.md`.
- [x] **STRING 400/900 threshold sensitivity — `COMPUTED` (29 Aug 2026).** `scripts/p2_string_threshold_sensitivity.py` recomputes the composite interactome centrality (degree/betweenness/closeness/eigenvector, 0.25 each, identical to the canonical `load_ppi_centrality()`) from `data/external/ppi_network.tsv` at thresholds 400/700/900, then re-derives the imputed PfCRT PNS on the canonical WT docking panel (`results/docking_mutants.csv`, 136 rows, 17 candidates). Outputs: `results/string_threshold_sensitivity_20260829/` (summary JSON + PNS ranking CSV + SI table `STRING_Threshold_Sensitivity.tex`). **Result:** PNS candidate ranking is threshold-robust — Spearman ρ = 0.9975 (400 vs 700, p<0.0001, top-5 Jaccard 1.0); ρ = 0.9681 (700 vs 900, top-5 Jaccard 0.67). The canonical 700 choice does not materially alter candidate ranking vs the neighbouring STRING confidence bands. Centrality-level ρ is lower (0.256 at 400 vs 700) because 400 admits 578 edges vs 145, but candidate-level PNS is dominated by the |ΔG| term.
- [x] **PP-15 multi-seed redocking — `COMPUTED` (29 Aug 2026).** `scripts/p2_targeted_redock_multiseed.sh` executed for both targets (jobs 15668 PfDHFR_WT, 15669 PfCRT_WT; 5 seeds each, exhaustiveness 32, Vina 1.2.7). Two script bugs fixed during execution: (1) `python - MANIFEST -c` consumed the manifest as script text leaving OUT empty (fixed to `python -c CODE MANIFEST`); (2) vina 1.2.7 has no `--log` flag (stdout redirected to log file). Outputs: `results/pp15_docking_20260828/multiseed_sensitivity/{PfDHFR_WT,PfCRT_WT}/seed_{101..505}.{pdbqt,log}` + `redock_sensitivity_manifest.json` (`COMPLETED_REQUIRES_POSE_QC`, input SHA-256) + `multiseed_sensitivity_summary.json`. **Result:** mode-1 affinity reproducible across seeds to ±0.03 kcal/mol (PfDHFR mean −8.590 ± 0.007, range 0.018; PfCRT mean −7.822 ± 0.011, range 0.030). Honest placement of the canonical single-run scores: PfCRT −7.810 lies at the edge of the seed range [−7.840, −7.810]; **PfDHFR −8.621 is 0.03 kcal/mol stronger than the seed range [−8.603, −8.585] (outside the spread, within the seed-noise floor)** — reported in Table S17 and the SM caveat. The docking prioritization is not seed-sensitive. **PP-01 multi-seed redocking — `COMPUTED` (29 Aug 2026, protocol error caught in deep relecture then RESOLVED).** Root cause of the intermediate `NOT INTERPRETABLE` verdict: the first attempt reused the PP-15 grid box **and** a Meeko-prepared ligand; the canonical inputs are the RRS-pilot ligand `results/docking/ligand_pdbqt/rank01_ligand.pdbqt` (MGLTools/Gasteiger prep; sha256 `bb61f5de…`) **plus** the P1-V2 WT grids (7F3Y 1.33/−1.733/−23.842; 6UKJ 152.99/151.042/159.379), exhaustiveness 128 — verified by exact reproduction of the canonical mutant scores (e.g. N51I −6.491 vs −6.48). 5 seeds × 2 WT targets: **PfDHFR WT** seeds −7.529/−7.504/−7.485/−7.504/−7.475, mean −7.499 ± 0.021, range 0.054 — **canonical −7.500 inside the spread**; **PfCRT WT** seeds −9.257/−9.262/−9.257/−9.225/−9.250, mean −9.250 ± 0.015, range 0.037 — canonical −9.300 is 0.04 kcal/mol above the spread (the original WT PfCRT receptor prep detail is not preserved on disk; within the 0.05 kcal/mol seed-noise floor). **Verdict: mode-1 affinity is reproducible across seeds to ≤0.05 kcal/mol on both WT targets; the PP-01 docking ranking is not seed-sensitive (same conclusion as PP-15).** Outputs: `results/pp01_docking_20260829/multiseed_canonical/{PfDHFR_WT,PfCRT_WT}/seed_{101..505}.{pdbqt,log}` + `multiseed_canonical_summary.json`. Table S17 now lists PP-15 and PP-01; the SM prose reports the PfCRT WT 0.04 kcal/mol grid-provenance caveat honestly. Lesson: seed-sensitivity controls must reuse the **exact canonical ligand preparation and grid box** of the score they purport to validate — changing either the grid *or* the ligand prep breaks the bracket.


- [x] MM-GBSA aggregation (16/16) → section 5.3 filled; manuscript `tab:mmmgbsa_setc` + Set-C pilot results subsection (`sec:setc_pilot`) added; abstract sentence already present (19 Aug revision).
- [x] Unit tests: `tests/` — current validation 19 passed, 1 skipped (incl. MM-GBSA aggregation, PBC-fix tests, rigorous audit, and lightweight robustness); historical 18/18 wording superseded.
- [x] Final LaTeX compile — main + SI compile with 0 errors, 0 undefined references.
- [x] Figure audit (25 Aug): retained figure set reduced to four main figures and three SI figures; duplicate workflow/PPI/RMSD/VAE displays removed; scatter is SI Figure S3 (`fig:s3_setc_rrs_scatter`); all graphics resolve from `manuscript/LaTeX/Graphics`.
- [x] **Manuscript audit & refinement (19 Aug)**: corrected intro WHO burden figures to WMR 2025 (282M cases / 610k deaths in 2024; artemisinin partial resistance ≥8 African countries) with new citation `letebo2026surveillance`; removed report-style hedging/meta-commentary (repeated ``does not establish X'' ×4, ``no primary claim'' ×4, ``(16/16)'' ×5, ``We explicitly state'', ``It should not be described as'', ``The appropriate conclusion is''); added literature-grounded Discussion passages (co-occurrence surveillance, end-point free-energy caveats via Wang et al. (2019; `wang2019_mmgbsa`)); **fixed SI numbering to sequential S1–S7 / S1–S4** (was rendering Table 1–7 / Figure 1–3 while prose cited S0/S3/S5…S9); renamed all SI labels to match; removed `\date{\today}`, fixed `margin=2.cm` typo, deduplicated keywords. Main + SI compile 0 errors / 0 undefined refs; test count at the time was 14/14 (superseded — current suite: 19 passed, 1 skipped in `malaria_md`, verified 30 Aug 2026).
- [x] Git commit + push (figure + manuscript updates) — pushed to origin/master (`930e40fbe`, `6f7b59b28`, `316f9b466`, `3d527398f`).
- [x] **siunitx/cleveref consistency pass (19 Aug)**: wrapped all remaining bare statistics (α, ρ, p, ΔG_bind, +473 kcal/mol, Bonferroni thresholds) in `\num{}`/`\SI{}`/`\qty{}`; enabled `retain-explicit-plus` so signed values keep their signs; verified all table numeric cells use S-columns and all cross-references use `\cref` (no bare `\ref`). The current rigor pass extends the statistical table with adjusted p-values and bootstrap intervals.
- [x] **DAR data-accuracy audit (19 Aug)**: verified the target-balanced and coverage-sensitive correlations by SMILES-merged recomputation (PNS–RRS ρ=−0.2098 / −0.5588; ACSI–PNS ρ=−0.3007 / −0.0784; ACSI–RRS ρ=−0.4056 / −0.1324); verified §4.3 all 16 MM-GBSA rows against `mmgbsa_summary_pilot.csv`; **corrected §4.1/§4.2** — the trajectory examples (PP-02 PfDHFR N51I 1.82 Å vs 2.52 Å; PP-02 PfCRT K76T 2.77 vs 3.17) were mis-attributed to PP-01, the MD_RRS_d range is 72.2–102.7 (not [91, 103]), and PP-01 PfCRT K76T (MD 102.7, exact source 102.7468) is the single concordant case (7/8 divergent).
- [x] **Deep web search + manuscript refinement (19 Aug)**: via PubMed/WHO (web_search tool unavailable) added three verified 2025–2026 references: `young2026artemisinin` (spatial-temporal mapping of Pfkelch13 ART-R in Africa; Lancet Infect Dis 2026, from medRxiv 2025) in the Intro; `okombo2026collateral` (PfCRT-mediated piperaquine efflux; Nat Commun 2026) in the mutant-panel Methods; `wicht2026chk1` (CHIR-124 dual PfArk1/hemozoin inhibition; ACS Chem Biol 2026) in the polypharmacology Discussion. Main + SI compile 0 errors / 0 undefined refs / 0 bibtex warnings; test count at the time was 14/14 (superseded — current suite: 19 passed, 1 skipped in `malaria_md`, verified 30 Aug 2026).
- [x] **ACSI sensitivity refinement (19 Aug)**: replaced the unpopulated SI sensitivity table with eight reproducible perturbation records generated from the committed 17-candidate component matrix; the script now verifies reconstruction of the baseline ACSI to numerical tolerance and records a project-relative input path in JSON. The manuscript reports the resulting local rank-stability range and explicitly avoids a full-library robustness claim.
- [x] **Desuet-file cleanup (19 Aug)**: removed 14 orphaned scripts with zero references (`quick_analysis.py`, `visualize_quick_results.py`, `analyze_214_python.py`, `analyze_214_trajectory.sh`, `custom_mmgbsa.py`, `extract_md_logs.py`, `md_convergence_check.py`, `mdanalysis_{214,438}_comprehensive.py`, `mdanalysis_full_analysis.py`, `p2_gap_{progressive_nvt,short_npt}.sbatch`, `p2_historical_diagnostic_md.sbatch`, `run_colabfold_pfatp4.sh`), the superseded `comprehensive_analysis/` result dirs (values differ from the manuscript's `production_analysis` source), the stray gitignored `gmx_MMPBSA.log`, caches (`.pytest_cache`, `__pycache__`), the leftover `MD_systems/164_ClpP/` dir, and `.xtc_offsets` runtime files. Kept all provenance-chain artifacts (ColabFold attempt dirs referenced by the repair audit, v2_top20, redock_438, mmgbsa outputs).


## 5bis. Post-production chain — CANONICAL (updated 25 August 2026)

- **All 16 production runs complete** (job array 15320); post-production chain COMPLETE at 2026-08-18T21:29:54Z (`results/set_c_md/post_production_manifest_pilot.json`, schema v3; QC exit code 0, MD-RRS exit code 0).
- **MD-RRS status:** `COMPUTED_WITH_COHORT_CONTRACT` (`md_rrs_pilot_PP01_PP02.csv` + provenance.json; rule `setc_p2_minheavy_5A_ge10percent_v1`, trajectory_count = 8).
- **MM-GBSA Set-C:** the historical summary contains 16/16 finite endpoint rows (`mmgbsa_summary_pilot.csv`, regenerated 2026-08-19; manifest `mmgbsa_manifest.json`). The PP-01 PfCRT K76A row retains the original 19-Aug value (−35.29 ± 1.17) as the canonical endpoint. A second replicate on an independent trajectory produced −27.54 ± 1.89 kcal/mol; this inter-replicate difference is documented in the manuscript Limitations. The `FAILED_NUMERICAL_QC` status applies to the 25–26 Aug diagnostic runs, not the canonical endpoint.
- **Pilot MD-RRS coverage:** the pilot MD-RRS covers **PP-01 and PP-02 only**, both classified **Class A over PfCRT;PfDHFR** under rule `setc_p2_minheavy_5A_ge10percent_v1` (`trajectory_count = 8`, i.e. both compounds × four mutant trajectories each). The full-panel 17 × 8 = 136-row MD-RRS remains `NOT_COMPUTED` by design.
- **MM-GBSA table composition:** the historical 16-row summary comprises **12 mutant systems plus 4 WT baselines**. The PP-01 PfCRT K76A row is retained (author decision, 28 Aug 2026) with an explicit Limitations caveat noting inter-replicate sensitivity. The remaining historical rows are interpreted, where retained, within the endpoint-method noise floor as **retention of binding, not gain** (same convention as the docking RRS caveat).
- **R2 traceability (replicate expectation):** the single-replicate pilot cannot establish replicate consistency or convergence; manuscript Limitations now require *replicated simulations of at least one pillar system (the PP-01 wild type)* before MM-GBSA-derived resilience statements enter routine use (pass 4bis, 24 Aug 2026).

### Traçabilité des mitigations R1–R10 (audit adversarial du 24 août 2026)

| # | Préoccupation | Mitigation appliquée (emplacement manuscrit V2607) |
|---|---|---|
| R1 | Circularité de sélection de la cohorte Set-C | ¶ gras *Cohort selection conditioning.* (Limitations) : fréquences de classe conditionnées à la cohorte MPO, distribution nulle non sélectionnée requise |
| R2 | Trajectoire unique vs attente éditoriale JCIM (réplicats) | Cadre honnête abstrait (« did not validate ») + phrase pilier PP-01 WT en Limitations (voir trace R2 ci-dessus) |
| R3 | Estimations RRS sans barre d'erreur | ¶ gras *Docking-score uncertainty.* : bruit Vina ≈ ±1 kcal/mol ; valeurs proches de 100 % = rétention complète dans le bruit |
| R4 | Absence d'ancrage expérimental | ¶ Discussion validation : IC50 enzymatiques PfDHFR quadruple N51I/C59R/S108N/I164L ; SPR/MST sur protéoliposomes PfCRT K76T vs WT pour PP-01/PP-15 |
| R5 | Seuil STRING 700 non justifié | Sensibilité par imputation PfCRT calculée (ρ de rang 0.9632–1.0000) ; matrices STRING 400/900 non disponibles, donc sensibilité de seuil explicitement NOT_COMPUTED |
| R6 | Arbitraire des poids ACSI | Phrase Méthodes : perturbations ±20 % par poids préservent l'ordre (ρ entre 0,9167 et 0,9804), cohérent avec le résumé |
| R7 | 5 candidats PfCRT-only | Clause de rattrapage : protonations alternatives / redocking en ensemble pour récupérer des scores PfDHFR éligibles |
| R8 | Bruit de fond MM-GBSA (ratios >100 %) | Captures tab:s8/tab:mmmgbsa : interprétation rétention-pas-gain + ΔΔG±SD dans la table source ; réconcilié contre le CSV (passe 4bis) |
| R9 | Confusion TDA (provenance partagée) | Clause corrélation partielle (masse molaire + prévalence de scaffold) |
| R10 | Dépôt de données | Nouvelle section *Data availability* : archives projet + dépôt Zenodo public accompagnant la publication |
- **Superseded / non-canonical artifacts:** witness trajectories 15259/15260 (partial 858 ps, witness-only); failed QC attempt logs `logs/p2_setc_qc_rrs_15384.log` / `15385.log` (MDAnalysis XTCReader.timespan API error) — authoritative wrapper output is job 15386.

## Lightweight robustness runs (25 August 2026)

Post-processing only (no new MD). Script: `Project2_Polypharmacology_MD_ValidationV2607/scripts/lightweight_runs_20260825.py` (numpy seed 42, self-check asserts); env `mamba run -n malaria_md`. Outputs: `results/lightweight_robustness/{mmgbsa_ddeltaG_pilot.csv, partial_corr_input_table.csv, lightweight_runs_summary.json}`.

- **RUN1 — MM-GBSA ΔΔG ± SD (R8).** Mutant-minus-wild-type ΔG per compound+target with propagated SD (√ΣSD²): 12 mutants; **0** show significantly weaker binding at 95% CI; **1** significantly tighter; max |ΔΔG| = 5.37 kcal/mol. Machine-readable table: `mmgbsa_ddeltaG_pilot.csv`. Confirms the retention-not-gain reading of the >100% ratios.
- **RUN2 — Partial Spearman PNS–RRS controlling MW + Murcko-scaffold prevalence (R9).** n = 12 complete-two-target set: raw ρ(PNS,RRS) = −0.2098 → **partial ρ = −0.6154** after conditioning on molecular weight and scaffold prevalence. The association strengthens under controls ⇒ it is not a size/scaffold artifact. Honest label: companion-study TDA topology values are not available locally; this uses the manuscript's own docking RRS (complete-two-target mean).
- **RUN3 — Cohort-level bootstrap, B = 10⁴ (R3).** Class-fraction CI95 over n = 17: A* [0.118, 0.529], A [0.118, 0.529], B [0.118, 0.529], C [0.118, 0.529], D [0.000, 0.176]. Fraction of the 12 MMG mutant ratios above 100%: point 0.667, CI95 [0.417, 0.917]. ⚠️ *Note: these CIs come from the earlier `lightweight_runs_20260825.py` bootstrap (interval layout coarse for the sparse D class); the canonical class-fraction bootstrap is §8quater.0 RUN1 (`p2_rrs_polypharma_secondary_20260828.py`, class A point 0.059 with CI [0.000, 0.176], etc.), which is the record cited by the manuscript/Table S15. The present RUN3 block is retained as a dated historical checkpoint only; do not conflate the two. The docking CSV carries a single Vina score per system (no replicate dimension), so no score-level σ exists; only cohort-level resampling is reported, explicitly labeled.*

## Single-system GPU rerun — PP-01_PfCRT_WT replicate_1 (COMPLETE; QC PASS + MM-GBSA, 26 August 2026)

Discovered 26 Aug: the 25 Aug local GPU batch (`--n-candidates 1` launches both PP-01 systems) also produced an R2 **wild-type** pillar run. This addresses the replicate-consistency expectation previously listed under manuscript Limitations (author decision to revise the text remains).

- **Run directory:** `results/md_systems/set_c_preparation_20260812_v1/PP-01_PfCRT_WT/runs/20260825T063226Z/replicate_1/` — production 10 ns COMPLETE (« Finished mdrun » 2026-08-25T13:08:24Z, 5,000,000 steps, 36.9 ns/day); identical MDP/provenance schema as §5bis canonical runs. Canonical R1 remains run 15320 (`runs/20260815T052351Z`).
- **Trajectory QC: PASS** (`p2_setc_trajectory_qc.py --system PP-01_PfCRT_WT`, env `P2_SETC_ROOT` + `P2_SETC_QC_OUTPUT` versionné). CSV: `results/set_c_md/single_rerun_20260825/set_c_trajectory_qc_single_rerun.csv` (n_frames=1001, bound_fraction=1.000, mean min dist 3.20 Å, 10.0 ns).
- **MM-GBSA R2** (helper `scripts/p2_setc_mmgbsa_single.py`, protocole batch verbatim : gmx_MMPBSA v1.5, GB OBC2 igb=5, saltcon 0.15 M, frames 1–1000 interval 10 ; SLURM job **15502**, exit 0 à 2026-08-26T07:57Z) : ΔG = **−28.60** kcal/mol (SEM 0.43 ; SD intra-trajectoire 4.35). Sorties : `results/set_c_md/single_rerun_20260825/mmgbsa/PP-01_PfCRT_WT/`.
- **Réplicats R1 vs R2 (endpoint level, convention unifiée 26/08 = ± SEM sur 100 snapshots):** R1 = −30.61 ± 0.41 vs R2 = −28.60 ± 0.43 ; offset |R1−R2| = 2.01 kcal/mol (< 1 SD intra-trajectoire de chaque run : 4.12 / 4.35) ; moyenne des moyennes ± SD d'échantillon (n=2) = −29.61 ± 1.42. Lecture rigoureuse : sous hypothèse i.i.d.-frames l'offset dépasserait le SEM combiné naïf (0.59), mais l'autocorrélation temporelle invalide cette lecture → offset adopté comme **plancher de bruit empirique inter-réplicats ≈ 2 kcal/mol** pour l'interprétation des contrastes mutant-vs-WT en réplicas simples ; cohérence endpoint supportée, résidence long-timescale et convergence restent ouvertes.
- **Artefact de cohérence + table SM (26/08):** `scripts/p2_wt_replicate_consistency.py` parse les deux FINAL_RESULTS_MMPBSA.dat (sources de vérité) → `results/set_c_md/single_rerun_20260825/wt_replicate_consistency.{json,md}` + table générée `manuscript/LaTeX/Table_S10_WT_Replicate_Consistency.tex` insérée dans le SM (rendue « Table S12 », référencée depuis Limitations/H3 du main via xr).
- **Audit des conventions d'incertitude (26/08, corrections manuscrites):** découverte d'un mélange préexistant — main tab:mmgbsa citait le SEM sous le libellé « Std. dev. » ; SM tab:s8 affichait SD(Prop.) sous « SD » avec légende « within-trajectory standard deviation » (fausse). Unifié : ± cité = SEM ; colonnes secondaires relabellisées (`SEM` dans tab:mmgbsa ; `SD_prop` dans tab:s8 + légendes corrigées) ; phrase Methods ajoutée. NB : les premiers comptes-rendus de session citaient R2 « ± 3.07 » (SD Prop) vs R1 « ± 4.12 » (SD) — mélange désormais corrigé partout.
- **Artefacts d'analyse associés:** résumé endpoints + gate SEM<1 (17/17 systèmes PASS) dans `results/set_c_md/mmgbsa_convergence_20260826/` ; audit terminologique manuscrit dans `docs/P2_TERMINOLOGY_AUDIT_20260826.md`.
- **Mise à jour manuscrite (décision auteur 26/08):** phrase Limitations du main révisée — l'exigence « replicated simulations of at least one pillar system » est remplacée par le constat du réplicat WT indépendant (offset 2.01 kcal/mol < 1 SD, adopté comme plancher de bruit ; résidence long-timescale et convergence laissées ouvertes) + clause H3 (pilier WT = 2 productions cohérentes, mutants toujours single-replicate). Relecture de cohérence complète : refs croisées SM réparées via `xr` + `\externaldocument[SM-]{…}` (12 « ?? » préexistants), bib `largermodels2026` alignée v3 ; rebuild final main 41 pp. / SM 8 pp., 0 erreur / 0 undefined / 0 `??`.

## Single-system GPU rerun — PP-01_PfCRT_K76A replicate_1 (COMPLETE; QC PASS + MM-GBSA BOND overflow, 26 August 2026)

Production COMPLETE, QC PASS — MM-GBSA failed (diagnostic below). This run does not modify any canonical artifact of §5bis.

- **Launcher / provenance:** `mamba run -n malaria_md python scripts/p2_setc_md_workflow.py --n-candidates 1 --target-ns 10 --execute --backend gpu` — executed on the local workstation GPU (not SLURM), started 2026-08-25T06:32:26Z. **Production COMPLETE:** « Finished mdrun » 2026-08-26T09:18:55Z, 5,000,000 steps, provenance flip → `PRODUCTION_COMPLETED_REQUIRES_TRAJECTORY_QC`.
- **Run directory:** `results/md_systems/set_c_preparation_20260812_v1/PP-01_PfCRT_K76A/runs/20260825T063226Z/replicate_1/`.
- **Trajectory QC: PASS** (watcher-initiated chain, job 15503 → `chain_log.jsonl` : QC PASS 09:22:10Z). CSV: `results/set_c_md/single_rerun_20260825/qc_PP-01_PfCRT_K76A.csv` (n_frames=1001, bound_fraction=1.000, mean_min_dist=2.91 Å, 10.0 ns).
- **MM-GBSA: FAILED — BOND overflow (two attempts):**
  - Attempt 1 (job 15503, chain QC→MMGBSA, 09:22–09:42 UTC): `ValueError: could not convert string to float: '*************'` — BOND overflow in `amber_outputs.py` during parsing of receptor minimization output.
  - Attempt 2 (patched `p2_setc_mmgbsa_single.py` with PBC-whole retry: `gmx trjconv -pbc whole -mol` → rebuild with `-ct production_pbc.xtc`, job 15505, launched 15:44 UTC): **same BOND overflow.**
  - **Diagnosis:** the overflow occurs in 2/100 frames (~frames 89–90) during sander minimization of the **receptor alone** (without ligand/solvent). Atoms affected: ND2 #7041 (GMAX=2.53×10⁵, UB=7.99×10⁶) and N #7076 (GMAX=1.74×10⁵, UB=3.59×10⁶). The complex and ligand calculations are clean (100/100). The `trjconv -pbc whole -mol` correction resolves the periodic image of the full complex but does not prevent intra-receptor clashes when the receptor is extracted and minimized in isolation — a known limitation of single-trajectory MM-GBSA for membrane proteins with PBC-spanning conformations.
  - **No FINAL_RESULTS_MMPBSA.dat produced.** Intermediate files retained in run dir (`_GMXMMPBSA_*.mdout.0`, `_GMXMMPBSA_restrt.0`).
- **Scope note (honest):** the system is the PP-01 PfCRT **K76A mutant**, not the R2 pillar PP-01 wild type. Even if MM-GBSA succeeded, a single-replicate mutant endpoint is not a validated resilience claim. The WT pillar expectation is separately addressed by the PP-01_PfCRT_WT rerun section above.
- **Possible resolutions (author decision required):**
  1. Exclude the 2 problematic frames: relaunch with `startframe=1 endframe=880 interval=10` (88 frames; impact on mean < 0.5 kcal/mol).
  2. Add positional restraints on non-active-site residues during receptor minimization (`ntr=1` in sander input).
  3. Accept K76A without MM-GBSA in this iteration (single-replicate, non-reportable endpoint).

**Resolution checkpoint (26 August 2026):** option 1 was tested as SLURM job `15506` with `endframe=880` in the versioned output `results/set_c_md/k76a_frame880_20260826/`. The scheduler/process returned `exit=0` and `gmx_MMPBSA` wrote a final file, but the numerical QC failed: 11/88 sampled frames (`771, 781, ..., 871`, corresponding to 7.71–8.71 ns) retained receptor/complex BOND values up to `8.95e7` kcal mol⁻¹ and UB values up to `4.52e6` kcal mol⁻¹. The resulting `ΔTOTAL = -27.46` kcal mol⁻¹ is therefore an artificial complex-minus-receptor cancellation and is **not reportable**. The output manifest records `status=FAILED_NUMERICAL_QC`, `reportable=false`.

**Repaired whole-center run (26 August 2026, `k76a_repaired_whole_20260826`):** A fourth attempt using `production_whole_centered.xtc` (PBC-whole applied to the full trajectory) with 100 frames (interval 10) succeeded: `ΔTOTAL = -27.54 ± 1.89` kcal/mol, `numerical_qc.status = PASS`, `reportable = true`. This provides a second-replicate estimate for K76A PP-01 (different trajectory from the canonical 19-Aug run).

**Final author decision (28 August 2026):** Option A — retain the original canonical endpoint (−35.29 ± 1.17 kcal/mol, 19 Aug, rep1, 100 frames) in the manuscript tables. The repaired whole-center value (−27.54 ± 1.89 kcal/mol, rep2, 100 frames) is documented as inter-replicate sensitivity. The manuscript Limitations section includes an explicit caveat noting the 7.75 kcal/mol difference between replicates. The Submission Manifest and this DAR are updated to reflect the resolution. No further K76A relaunch is authorized for this submission cycle.

## Single-system GPU rerun — PP-01_PfDHFR_I164L replicate_1 (COMPLETE production + QC PASS; MM-GBSA COMPLETE 22:33Z)

- **Production COMPLETE:** `results/md_systems/set_c_preparation_20260812_v1/PP-01_PfDHFR_I164L/runs/20260825T063226Z/replicate_1/` — `Finished mdrun Fri Aug 28 17:25:47` (5,000,000 steps, 10 ns, 27.3 ns/day, GPU A4000) ; `production_provenance.json:3` `PRODUCTION_COMPLETED_REQUIRES_TRAJECTORY_QC` → `1.18 GB xtc`.
- **Trajectory QC: PASS** (`P2_SETC_ROOT` + `conda run -n malaria_md p2_setc_trajectory_qc.py --system PP-01_PfDHFR_I164L` 28 Aug 17:37Z): `n_frames=1001 bound_fraction=1.000 mean_min=2.86 Å 10.0 ns` (`setc_p2_minheavy_5A_ge10percent_v1`), CSV `results/set_c_md/set_c_trajectory_qc.csv`.
- **MM-GBSA: COMPLETE 28 Aug 22:33Z** (`scripts/p2_setc_mmgbsa_single.py PP-01_PfDHFR_I164L <run_dir>`, `P2_MMGBSA_ENDFRAME=880` to exclude BOND-overflow frames 851-991 from initial 18:55Z run): `endframe=880` (excludes frames 851, 881, 941, 971, 981, 991 BOND overflow), protocol batch verbatim `gmx_MMPBSA v1.5 GB OBC2 igb=5 saltcon 0.15 M frames 1-880 interval 10` + `mmgbsa_timeseries.csv` for convergence; exit 0, **numerical_qc PASS**, **ΔTOTAL = -24.36 ± 1.77 kcal/mol** (88 frames, 80% of original 100-frame range retained). Initial 100-frame run (PID 312119) failed with BOND overflow on 1 frame (frame 901, max 2.19e7 kcal/mol); `endframe=880` retry succeeded. Launch status: `results/set_c_md/single_rerun_20260825/mmgbsa/PP-01_PfDHFR_I164L/launch_status.json`.
- **Scope:** single-system rerun, integrated with canonical §5bis (16/16 pilot) as a non-canonical pillar; do not promote to Set-C claim.

**Updated:** 28 August 2026 22:35Z.

## 11. Implementation checkpoint 30 August 2026 — P2 V2609 narrative pivot audit

The P2 V2609 release manuscript `manuscript/LaTeX/Polypharmacology_MD_Validation_V2609.tex` was audited against the 12 recommendations of `docs/P2_V2609_NARRATIVE_PIVOT_PLAN.md` (29 Aug 2026); V2607 remains the immutable data/source release and V2609 is the canonical manuscript release for submission (decision 30 Aug PM, §0.4). The manuscript is **already substantially compliant** with the pivot: 10 of 12 recommendations are met without modification. V2609 is implemented as a narrative and audit refinement of the canonical V2607 dataset; canonical numerical results remain unchanged unless reconciled in this DAR.

| Pivot recommendation | Manuscript status | Evidence |
|---|---|---|
| Title uses methodological object (calibration/retention/triage), avoids "validated resistance" / "binding affinity" / "resistance-resilient" | OK (acceptable) | L65: "Resistance-Aware Docking Prioritization of Antimalarial Leads from African Natural Products" — uses *prioritization* (pivot §6 preferred term); no "validated", "binding affinity", or "resistance-resilient" claims |
| n=12 primary vs n=17 available distincts | OK | L141 (Methods), L151 (estimands section), Table S8 Cohort_Estimands |
| DEKOIS AUC = 0.45 [0.37, 0.53] visible in Results + Discussion | OK | Abstract L124; Results L214 ("DEKOIS 2.0 enrichment for PfDHFR with Vina alone was null (ROC-AUC 0.450, EF5% = 0.00)"); framed as "absence of demonstrated enrichment", not mechanistic proof |
| PNS ≠ causal network mechanism | OK | L139 ("centrality is a topological weighting heuristic rather than a causal measure of target essentiality") |
| MD = stress test, not affinity/kinetics/thermodynamics | OK | L250 ("pose-retention and local-geometry check, not as a measurement of residence time or converged free energy") |
| MM-GBSA = single-replicate endpoint, not validated free energy | OK | L252 (intra-trajectory SEM, not inter-replicate); L376 caption ("Single-replicate endpoints should be read only as within-protocol contrasts") |
| PP-01 = "passed two-target gate" / "selected for follow-up", not "validated/robust/eliminated" | OK | L370 ("PP-01 satisfied the two-target gate … in four of four mutants") |
| PP-02 = "did not pass the gate", not "eliminated" | OK | L370 ("PP-02 did not, because its PfDHFR states lack a docking wild-type anchor") |
| DEKOIS as absence of enrichment, not as mechanistic proof | OK | L214 ("score-based recovery of known actives is protocol- and library-dependent"); abstract L124 ("underscoring that the scores were used for within-panel prioritisation rather than calibrated affinity prediction") |
| PNS-RRS non confirmé | OK | L303 ("PNS and RRS were only weakly associated (ρ=-0.2098, adjusted p=1.0000)"); abstract L124 |
| Référentiel langage pivot §6 (avoid "validated resistance resilience", "biological", "thermodynamically unstable pose", etc.) | **Mitigated** | One borderline occurrence L331 ("robust H-bond network") reformulated to "stable H-bond network" |
| Cohortes n=12 / n=17 + Table S8 evidence boundary | OK | Table S8 Cohort_Estimands (estimands + denominators); Table S13 Evidence_Scope (claim–evidence–boundary) |

**Mitigation applied (1/12)** : L331 "engages in a robust H-bond network" → "engages in a stable H-bond network". The other usages of "robust" (e.g. "robustness analyses", "robustness checks", "robustness_transfer" in section/SM labels) refer to the statistical robustness analysis (different concept) and are pivot-compliant.

**Conclusion**: the V2609 pivot is implemented as a narrative refinement of the canonical V2607 dataset. The detailed execution sequence and exit criteria are maintained in `docs/P2_V2609_IMPLEMENTATION_PLAN.md`. The narrative framing ("resistance-aware prioritization" + "calibration of the interpretation of docking-derived RRS") is in place; the manuscript describes itself as a **calibration and triage** study, not a validation. Final author review remains required before any submission decision.

**Compilation**: MS 30 p., 0 LaTeX error (libxpdf xref "damaged" warning is a known artefact of `pdflatex` not affecting compilation).

## 12. Implementation checkpoint 30 August 2026 — P2 V2609 runs audit and Soares2023 alignment

**Audit of the 12 P2_V2609 pivot recommendations** (see `docs/P2_V2609_NARRATIVE_PIVOT_PLAN.md`) for **run suggestions** (new simulations required):

The pivot contains **1 explicit run suggestion** : the JCIM MD-reporting guidelines \citep{soares2023mdreport} (Soares et al., DOI 10.1021/acs.jcim.3c00599, *J Chem Inf Model* 2023) recommend **at least three replicates** per system with adequate duration and convergence. The pivot itself authorises the alternative *"si aucune nouvelle campagne n'est exécutée, le pilote doit rester explicitement secondaire, exploratoire et non thermodynamique"* (pivot §8 L214).

The P2 V2609 manuscript (`Polypharmacology_MD_Validation_V2609.tex`) **follows the alternative path** ("réduire la portée de la revendication") and explicitly declares at L250, L370, L436, L447 and L449 that the MD pilot is single-replicate, 10 ns, secondary, and is not a residence-time or converged free-energy measurement. No multi-replicate campaign was launched **for the V2609 submission** — i.e. the presented estimates are *not* extended to the three-replicate design recommended by Soares et al. ⚠️ *Note for internal consistency: the M1 run (§13–§15, launched 29 Aug, jobs 15711/15715) is a separate secondary robustness check of the pillar system (PP-01 PfDHFR WT, fresh seed, \qty{25}{\nano\second}); it is reported in the SI strictly as an archived structural-stress test outside the Set-C estimand (author decision, 30 Aug — see §16 décision n°2), so it does not constitute a multi-replicate campaign for the submission and does not contradict the single-replicate pilot framing.*

**Action applied** : the JCIM MD-reporting guidelines \citep{soares2023mdreport} are now cited in the manuscript §Limitations, and the choice *not* to launch a multi-replicate campaign for the presented estimates is stated explicitly in that paragraph: *"no multi-replicate campaign was launched to extend the presented estimates", with a single extended structural-stress trajectory (PP-01 PfDHFR WT, separate seed, 25 ns, QC-pass) reported in the SI strictly as a robustness check outside the Set-C estimand* (wording updated 30 Aug evening to keep the main-Limitations consistent with the M1 SM appendix).

**Bibliography addition** : one new entry, `soares2023mdreport`, added to `Bibliography_P2.bib`.

**Compilation** : MS 31 p. (was 30 p. pre-addition), 0 LaTeX error.

## 13. Implementation checkpoint 30 August 2026 — P2 M1 runbook path alignment

**`docs/P2_M1_RUNBOOK_20260829.md`** is the runbook for the PP-01 replication MD campaign (launched as job SLURM **15711**, array 0-11, 12 trajectories × 100 ns = 1,200 ns production, GPU A4000). ⚠️ *The snapshot below reflects the audit-time state (~30 Aug 13:00Z, job 15711 running 1h08min); it is superseded by §14–§15 — task 0 stopped by decision at 23.41 ns, tasks 1–11 cancelled, continuation job 15715 running towards 100 ns.*

**Audit** of the runbook against the actual execution path:

| Element | Runbook claim | Actual (sbatch + DAR canonical) | Status |
|---|---|---|---|
| Source root | `results/set_c_md/set_c_preparation_20260812_v1/` | `results/md_systems/set_c_preparation_20260812_v1/` | **Misaligned** (legacy path) |
| 4 systems × 3 replicates | PP-01_PfDHFR_WT, PP-01_PfCRT_WT, PP-01_PfDHFR_N51I, PP-01_PfCRT_K76T × {1,2,3} | Idem in `SYSTEMS=()` and `REPLICATES=(1 2 3)` | OK |
| Output root | `results/m1_replicated_md_20260829/` | `results/m1_replicated_md_20260829/` | OK |
| 12 tasks × 100 ns | "1,200 ns of production" | `SLURM --array=0-11%1` (concurrency 1) | OK |
| Witness throughput | 28.169 ns/day | DAR §4.1 (10 ns in 8.5 h, 27.3–36.9 ns/day) | OK |
| ETA | 2-4 calendar days | 15711 running 1h08min at audit time | Consistent |
| Interpretation gate | No affinity / resistance / kinetic claim | Conforms to pivot V2609 + Soares2023 (manuscript L250, L370, L447) | OK |

**Mitigation applied** : the runbook preflight and post-production `P2_SETC_ROOT` paths were corrected from the legacy `results/set_c_md/...` to the canonical `results/md_systems/...` path that `scripts/p2_m1_replicated_md.sbatch` actually reads and that the DAR consistently references. The path inside the launcher was already correct; only the documentation had drifted.

**Status of M1 at audit time** : job 15711 active, replicate_1 (task 0, PP-01_PfDHFR_WT) running, 11 tasks pending. **Superseded by §14–§15 (30 Aug PM):** task 0 stopped by decision at 23.41 ns, QC PASS, 11 tasks cancelled, continuation job 15715 running towards 100 ns.

## 14. Decision log — 30 August 2026 — P2 M1 scope decision (option A)

**Decision (user, option A):** complete replicate_1 (task 0, PP-01_PfDHFR_WT) and stop; do **not** run the 11 remaining replicates. Rationale: at the measured ~1.2 ns/h and the `%1` GPU throttle, the full 12-replicate × 100 ns array would need ~42 calendar days, which is incoherent with the submission timeline; M1 is already **optional** for the V2609 pivot (the manuscript is defensible without any new simulation).

**Actions taken:**
- Cancelled the 11 pending array tasks `15711_[1-11]` (used no resources under `%1`). Task 0 left untouched and running.
- Verified GPU is active in task 0: log header `Using GPU 8x4 nonbonded short-range kernels`, 1 compatible GPU, 8 OpenMP threads.

**Time-limit fact uncovered:** the running task 0 carries `TimeLimit=2-00:00:00` (48 h), although the launcher on disk now requests 96 h (edited *after* the job was submitted, so the *running* job kept 48 h). Extension of a running job was refused by SLURM (`Access/permission denied`).

**Consequence:** task 0 will be killed by SLURM at 48 h (~31 Aug 19:51Z), corresponding to roughly **50–60 ns** of continuous trajectory (at 1.19 ns/h from a ~23 ns baseline at 19.3 h), **not** the intended 100 ns.

**Status (superseded by §15):** `M1 = SINGLE-REPLICATE PARTIAL (task 0, ~50–60 ns, NOT 100 ns)` → the prediction above (48 h SLURM kill at ~50–60 ns) was **not what happened**: per the user decision in §15, task 0 was stopped early by `scancel` at **23.41 ns**, the post-kill QC PASSED (bound_fraction 1.0), and a **continuation (job 15715, 96 h) is running from the last checkpoint towards the full 100 ns** (ETA ~2 Sep 2026). Remains **NOT_COMPUTED / NOT_REPORTABLE** as a completed 100 ns replicate until the continuation finishes and the §16 reconciliation gate passes; not integrated into V2609. ⚠️ *Superseded (30 Aug evening): §14–§15 are archival decision/execution records; the M1 scope was later reduced to 25 ns (§17) and decision §16 n°2 was REVISED to integrate the 25.2 ns trajectory into the SM V2609 as an archival stress-test appendix (outside the Set-C estimand, not a multi-replicate campaign).*

**Follow-up QC gate trigger:** after task 0 is killed at 48 h, run trajectory QC (bound-fraction / min-heavy-atom / continuity over the achieved interval), record the true achieved duration in `m1_provenance.json` (currently hard-coded `duration_ns=100.0` and status `M1_PRODUCTION_COMPLETE_REQUIRES_QC_REVIEW` — must be corrected to reflect the partial length), then decide whether to (i) report as a short secondary pilot or (ii) relaunch a continuation for a full 100 ns.

**Prepared (30 Aug 2026):** `scripts/p2_m1_postkill_qc.py` implements this gate for the single partial replicate: it reads the REAL last step/time from `production.log` (validated on the live log: 11,617,000 steps → 23.23 ns, 0 integrity issues), refuses to run when runtime markers are present, computes bound-fraction QC on the achieved interval under rule `setc_p2_minheavy_5A_ge10percent_v1`, and writes a corrected `m1_provenance.json` with `status = M1_PRODUCTION_INTERRUPTED_PARTIAL` (or `..._COMPLETE...` only if ≥ target), true `achieved_ns`, `last_step`, `termination = SLURM_TIME_LIMIT_KILL`, and an explicit non-affinity/non-resistance interpretation. It refuses to overwrite an existing completed provenance (exit 3). `py_compile` PASS; `--help` PASS. Runbook updated (`docs/P2_M1_RUNBOOK_20260829.md`, single-partial-replicate path).

## 15. Execution record — 30 Aug 2026 (afternoon) — stop, QC, continuation

**Decision (user):** stop the interrupted replicate_1, exploit the obtained trajectory; if interesting, submit the manuscript while a relaunch to 100 ns continues in the background.

## 16. V2609 author decisions — open items (30 Aug 2026)

Author decisions required before the V2609 submission gate (mirrors `docs/P2_V2609_IMPLEMENTATION_PLAN.md` §11):

| # | Decision | Status / recommendation |
|---|---|---|
| 1 | Confirm the V2609 title | ✅ **Applied (30 Aug PM):** *Calibrating the Interpretation of Docking-Derived Resistance-Retention Scores with a Short Molecular-Dynamics Structural Stress Test* — set consistently in main, SM and cover letter |
| 2 | M1 integration into the manuscript | **REVISED (30 Aug, author decision following SM reaction): YES as an SI archival appendix only** — add a dedicated SI subsection reporting the 25.2 ns PP-01 PfDHFR WT trajectory (fresh seed, QC PASS, bound fraction 1.000, mean minimum distance 2.75 Å) strictly as a secondary structural-stress test outside the Set-C estimand, *not* as a multi-replicate campaign; main text unchanged |
| 3 | RRS margin analysis in the SI | Done (Table S18, `results/v2609_rrs_margin_20260830/`, `COMPUTED_SECONDARY_SENSITIVITY`) — confirm inclusion |
| 4 | Docking-RRS vs MD-RRS$_d$ figure | Done (scatter generated, `p2_setc_rrs_scatter.pdf`, SI Figure S3) — confirm readability |
| 5 | MM-GBSA detail level in main text | Current: summary + pointer to SI; confirm no table expansion in main |
| 6 | Final conclusion wording | Draft in pivot plan §5.7 — author to confirm |
| 7 | Independent final structural read before submission | Required (author), after §15 closure |
| 8 | Zenodo deposit and data-sharing policy | `pending` (DOI reserved 10.5281/zenodo.19608875 for the parent record; P2 snapshot deposit not yet made) |
| 9 | JCIM MD-reporting guidelines adherence (Soares et al., DOI 10.1021/acs.jcim.3c00599) | Declared in Limitations: no new replicate campaign; pilot reported strictly as secondary structural stress test |
| 10 | WHO malaria burden figures | Current: 282M cases / 610k deaths (2024, WMR 2025); the P5 manuscript uses 263M/597K (WMR 2024 for 2023) — verify per-journal consistency before any cross-paper claim |

**M1 reconciliation gate (mandatory before any M1 integration):** 100 ns completion (job 15715) → trajectory QC (bound-fraction rule `setc_p2_minheavy_5A_ge10percent_v1`) → provenance/hash verification → DAR status update → author decision on narrative integration. Until then, M1 remains `NOT_COMPUTED / NOT_REPORTABLE` for the 100 ns claim and the manuscript keeps the 10 ns single-replicate pilot framing (V2609 §Phase 8).

**Actions:**
- `scancel 15711_0` → job stopped at step 11,707,500 (23.41 ns); files frozen cleanly (xtc 2.775 GB, log 0 runtime markers).
- **Post-kill QC PASS** (`p2_m1_postkill_qc.py`, rule `setc_p2_minheavy_5A_ge10percent_v1`, full trajectory 2,342 frames / 23.4 ns): **bound_fraction = 1.0000, mean_min = 2.78 Å** — the PP-01 ligand remains continuously bound over the whole achieved interval. Corrected provenance written: `M1_PRODUCTION_INTERRUPTED_PARTIAL`, `achieved_ns = 23.41`, `last_step = 11707500`, `termination = SLURM_TIME_LIMIT_KILL` (note: this stop was a user decision, not the 48 h SLURM kill).
- **Continuation launcher** `scripts/p2_m1_continue_100ns.sbatch`: reuses the unchanged `production.tpr` (nsteps = 50,000,000 = 100 ns total) with `mdrun -cpi` from the latest checkpoint, same GPU offload path (`-nb gpu -pme gpu -bonded cpu -update cpu`), 96 h limit. **Diagnosed failure of first submission (job 15714, exit 141 = SIGPIPE):** the `ls -1t ... | head -1` checkpoint selection dies under `set -o pipefail` when `head` closes early; replaced with a pipe-free numeric-max loop (validated: selects step 11,707,500). **Job 15715 running** (started 15:38Z, confirmed `Restarting from checkpoint, appending to previous log file`; step advancing 11,724,000 → 23.45 ns at +2 min). ETA to 100 ns: ~64 h → ~2 Sep 2026.
- **Meaning for the manuscript (if used):** a single continuous trajectory now reaching ~23.4 ns+ (up to 100 ns when the continuation completes), bound over the whole interval; usable only as a secondary structural-stress pilot, never as affinity/resistance validation (V2609 framing). `m1_provenance.json` will be upgraded to `M1_PRODUCTION_COMPLETE_REQUIRES_QC_REVIEW` by the launcher's final QC call once 100 ns is reached.

## 17. Decision — 30 Aug 2026 (evening) — M1 target reduced 100 ns → 25 ns

**Decision (author):** the M1 continuation target is reduced from 100 ns to **25 ns**. Rationale: JCIM (Soares et al., DOI 10.1021/acs.jcim.3c00599) requires ≥ 3 replicates with *adequate* duration and convergence — it does **not** mandate a specific length (neither 10 nor 100 ns); 25 ns is a round, defensible length for the secondary structural-stress pilot and frees ~60 h GPU versus the 100 ns plan.

**Actions:**
- Added `--termination` option to `scripts/p2_m1_postkill_qc.py` (choices: `SLURM_TIME_LIMIT_KILL` (default, backward compatible) / `USER_DECISION` / `NATURAL_COMPLETION`) so the provenance honestly records the stop cause.
- New watcher `scripts/p2_m1_stop_at_25ns.sh` (launched 30 Aug, PID logged to `/tmp/m1_stop_at_25ns_watcher.log`): polls `production.log` every 120 s; when `step ≥ 12,500,000` (25 ns at dt = 0.002 ps) it runs `scancel 15715_0`, then executes post-kill QC with `--termination USER_DECISION --target-ns 25 --max-frames 100000` (full-trajectory sampling, not the 2,000-frame cap).
- **State at launch:** job 15715_0 running (56 min), step 12,144,000 → 24.29 ns; ~35 min GPU remaining to 25 ns.

**Outcome (30 Aug 2026, 17:09Z):** watcher job **15716** completed — `scancel 15715_0` at step 12,579,600 (25.16 ns), post-kill QC **PASS** on the full trajectory (`p2_m1_postkill_qc.py`, rule `setc_p2_minheavy_5A_ge10percent_v1`): **bound_fraction = 1.0000, mean_min = 2.753 Å, 2,517 frames, achieved 25.17 ns** (`M1_PRODUCTION_COMPLETE_REQUIRES_QC_REVIEW` because the 25 ns target was reached; `termination = USER_DECISION` — stopped by author decision via the watcher, not a natural run end; provenance updated accordingly). Interpretation: single continuous trajectory, PP-01 PfDHFR WT, ligand continuously bound over the full 25 ns — extends the 10 ns pilot beyond its original window and confirms the bound state is not an artefact of the 10 ns window on this pillar system. Following the SI author review (30 Aug, decision §16 n°2 REVISED), the 25.2 ns trajectory is integrated into the SM V2609 as an archival structural-stress appendix (`Extended structural stress test (PP-01 PfDHFR WT)`), explicitly framed as outside the Set-C estimand and not a multi-replicate campaign.
