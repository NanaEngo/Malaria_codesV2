# Plan d'Intégration MD-RRS dans P2 — snapshot historique

> **DO NOT EXECUTE:** this plan contains the superseded 15106→15111→15117 chain and historical command examples. The current live witness is 15254→15259→15260; consult the active BMAD DAR before preparing a new full-panel execution. No Set-C MD-RRS result is currently available.

**Objectif :** intégrer les résultats du MD-RRS Set-C (16 systèmes, 2 candidats × 2 cibles × 4 états WT/mutant) dans le manuscrit P2 uniquement après une chaîne complète et un QC PASS. **État courant (12/08/2026) :** le témoin isolé 15254→15259→15260 est en cours; les anciens jobs 15106/15111/15117 sont historiques et aucun MD-RRS de cohorte n'est disponible.

## 1. Chaîne post-production (soumise)

```
15106 (eq, 16×) → 15111 (prod, 16×10 ns) → p2_setc_qc_and_md_rrs.sbatch
```

| Étape | Job/Script | Durée | Statut |
|-------|-----------|-------|--------|
| Équilibration | 15106 (16 tâches, array) | ~2 h | 4 RUNNING, 7 PENDING, 1 FAILED (N51I Verlet segfault) |
| Production | 15111 (16 × 10 ns, array) | ~40 h | PENDING (dépendance 15106) |
| Trajectory QC | `p2_setc_trajectory_qc.py` | ~10 min | PENDING (dépendance 15111) |
| MD-RRS | `p2_setc_md_rrs.py` | ~1 min | PENDING (après QC) |

**Soumission post-production :** `sbatch scripts/p2_setc_qc_and_md_rrs.sbatch` (déjà soumis avec `--dependency=afterok:15111`)

## 2. Sorties attendues

| Fichier | Contenu | Colonnes clés |
|---------|---------|--------------|
| `results/set_c_md/set_c_trajectory_qc.csv` | Trajectory QC (bound fraction, mean min dist) | `system`, `target`, `mutation`, `set_c_id`, `WT_bound_fraction`, `mutant_bound_fraction`, `mean_min_dist_A`, `n_frames` |
| `results/set_c_md/md_rrs_classification.csv` | MD-RRS par candidat | `candidate_id`, `MD_RRS_mean`, `MD_RRS_class`, `MD_RRS_targets_used` |
| `results/set_c_md/post_production_manifest.json` | Provenance (SHA-256, statuts, paramètres) | — |

## 3. Modifications du manuscrit P2

### 3.1 Abstract (L112)
**Actuel :** « …with set-C MD and Monte Carlo evaluation remaining future work. »
**Après MD-RRS :** « …while set-C MD-RRS across 16 mutant systems (2 polypharmacological candidates × 2 targets × 4 states) confirms the docking-based resilience classification for [X] of [Y] candidates (MD-RRS class A/B/C/D), with [Z] systems maintaining bound ligand throughout production. »

### 3.2 Introduction (L131)
**Actuel :** « The mutant systems have docking-based RRS classifications but no completed production MD; full mutant MD validation remains future work. »
**Après MD-RRS :** « The mutant systems have docking-based RRS classifications, now validated by 16-system production MD; [X] of [Y] mutants maintain bound ligand (bound fraction ≥ threshold), and the MD-RRS classification agrees with docking-based RRS for [Z]% of comparisons. »

### 3.3 Methods — Section « Monte Carlo assessment » (L254)
**Actuel :** « Candidate-specific production MD was likewise not obtained for the 16-system Set-C pilot; no Set-C MD-RRS estimate is reported. »
**Après MD-RRS :** Remplacer par : « Candidate-specific production MD was performed for the 16-system Set-C pilot (10 ns per system, 160 ns total). Trajectory QC computed bound fraction and mean minimum protein–ligand distance for each system … MD-RRS is defined as 100 × mutant bound_fraction / WT bound_fraction, following the same per-target classification as docking-RRS (Section 2.5). Systems with WT bound_fraction < 0.10 were excluded from MD-RRS (non-binding). »

### 3.4 Results — Nouvelle sous-section « Set-C MD-RRS validation »
À ajouter après la section RRS (3.3) ou comme dernière sous-section avant Discussion :
> **Set-C MD-RRS validation.** Sixteen production MD simulations (10 ns each, 160 ns total) were performed for the 2 highest-ranked polypharmacological candidates (PP-01, PP-02) against PfDHFR (WT, N51I, C59R, S108N, I164L) and PfCRT (WT, K76T, K76A). Trajectory QC (Table SX) shows that [X] of [Y] systems maintain the ligand within 5 Å of the initial binding pose (bound fraction ≥ 0.50). The MD-derived RRS (MD-RRS = 100 × mutant bound_fraction / WT bound_fraction) classifies [result summary]. Compared to the docking-based RRS (Table 3), the MD-RRS agrees for [Z] of [X] comparisons, confirming that the docking-based resilience framework is a conservative first-tier screen.

### 3.5 Limitations (L631, L657)
**Actuel :** « No production MD was completed for the 17 set-C candidates or their mutant systems »
**Après MD-RRS :** Adoucir : « Production MD was completed for the 2 highest-ranked set-C candidates (PP-01, PP-02) across 16 mutant systems (10 ns each, 160 ns total); the remaining 15 set-C candidates have docking-based RRS only. »

### 3.6 Conclusion (L680)
**Actuel :** « The mutant systems have docking-based RRS classifications awaiting full production MD validation. »
**Après MD-RRS :** « The mutant systems have docking-based RRS classifications, now supported by 16-system production MD validation for the two highest-ranked candidates (PP-01, PP-02). The remaining 15 candidates retain docking-based RRS pending full MD. »

## 4. Nouvelles figures/tables à ajouter

| Élément | Type | Description |
|---------|------|-------------|
| Table SX (nouveau) | SM | Bound fraction per system (16 rows), MD-RRS per candidate (2 rows) |
| Figure SX (nouveau) | SM | Violin plot of protein–ligand min distances for WT vs mutant systems |
| Résultat (main) | Texte | 1–2 phrases dans Results + mise à jour abstract/Limitations |

## 5. Dépendances et timing

| Prérequis | ETA | Action |
|-----------|-----|--------|
| 15106 eq complet | ~2 h | Vérifier les échecs (N51I → retry si nécessaire) |
| 15111 prod 16×10 ns | ~40 h après 15106 | Surveiller les logs |
| QC + MD-RRS | ~10 min après 15111 | Vérifier `md_rrs_classification.csv` |
| Intégration manuscrit | 30 min | Appliquer les modifications ci-dessus + recompiler |
| Validation | 10 min | Main 25 p. / SM 3 p. RC=0, 0 erreur |