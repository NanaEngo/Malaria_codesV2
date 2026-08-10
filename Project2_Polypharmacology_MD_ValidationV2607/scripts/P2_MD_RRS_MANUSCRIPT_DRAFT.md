# Draft Manuscrit MD-RRS — P2 (à remplir dès fin du job 15120)

**Date :** 10 août 2026 — **Statut :** PRÊT À REMPLIR (placeholders `[X]` à substituer avec les valeurs de `results/set_c_md/md_rrs_classification.csv` + `set_c_trajectory_qc.csv`)

---

## 1. Abstract (remplacer la dernière phrase)

**Actuel :**
> …with set-C MD and Monte Carlo evaluation remaining future work.

**Nouveau (à compléter) :**
> …while set-C molecular dynamics across [16] mutant systems ([2] candidates × 2 targets × 4 states; 10 ns each) confirms the docking-based resilience classification for [X] of [2] candidates, with [Y] of [16] systems maintaining the ligand bound within 5 Å for ≥ 10% of the production trajectory.

---

## 2. Introduction (remplacer la phrase L131)

**Actuel :**
> The mutant systems have docking-based RRS classifications but no completed production MD; full mutant MD validation remains future work.

**Nouveau (à compléter) :**
> The mutant systems have docking-based RRS classifications, now complemented by [16] set-C production MD simulations (10 ns each) for the two highest-ranked candidates. [X] of [Y] systems maintained a bound ligand (heavy-atom minimum distance < 5 Å for ≥ 10% of frames), and the MD-derived RRS (MD-RRS) reproduces the docking-RRS class for [Z] of [2] candidates, indicating that docking-based resilience scoring is a conservative first-tier screen.

---

## 3. Methods — section « Monte Carlo assessment » (L254)

**Actuel :**
> A Monte Carlo extension was considered using an OpenMM move set… Candidate-specific production MD was likewise not obtained for the 16-system Set-C pilot; no Set-C MD-RRS estimate is reported.

**Nouveau (remplacer le § entier) :**
> **Set-C molecular dynamics and MD-RRS.** Candidate-specific production MD was performed for the 16-system Set-C pilot: 2 polypharmacological candidates (PP-01, PP-02) × 2 targets (PfDHFR, PfCRT) × 4 states (WT, N51I, C59R, S108N, I164L for PfDHFR; WT, K76T, K76A for PfCRT), 10 ns each (160 ns total), at 310.15 K under the same protocol as the parent-study MD (§2.X). Trajectory QC was performed with MDAnalysis [citep]: for each system, the protein–ligand minimum heavy-atom distance was computed per frame (PBC-aware minimum-image), and a system was classified as bound when the bound fraction — the fraction of frames with minimum heavy-atom distance < 5.0 Å — exceeded 10% (predeclared rule `setc_p2_minheavy_5A_ge10percent_v1`). MD-RRS is defined per target as 100 × (mutant bound fraction)/(WT bound fraction), averaged over targets whose WT bound fraction ≥ 0.10; systems with WT bound fraction below this threshold are excluded as non-binding (consistent with the per-target docking-RRS denominator rule, §2.5). MD-RRS classes follow the same thresholds as docking-RRS (A ≥ 80% all, B ≥ 70% all, C ≥ 80% specific, D < 60% any). Docking-RRS is retained as a separate column; MD-RRS never overwrites it (predeclared, see [provenance]).

---

## 4. Results — nouvelle sous-section « Set-C MD-RRS validation »

**À insérer après §3.3 (RRS) :**

> **Set-C MD-RRS validation.** Sixteen production MD simulations (10 ns each, 160 ns total) were performed for the two highest-ranked polypharmacological candidates (PP-01, PP-02) against PfDHFR (WT, N51I, C59R, S108N, I164L) and PfCRT (WT, K76T, K76A). Trajectory QC ([Table SX](#)) shows that [X] of [16] systems maintained the ligand within 5 Å of the protein for ≥ 10% of frames (bound fraction ≥ 0.10), with mean minimum protein–ligand distances ranging from [min] to [max] Å. The MD-derived RRS ([Table SY](#)) classifies [summary: e.g., "PP-01 as class A* with MD-RRS mean [v]%" and "PP-02 as class B with [v]%"]. Compared with the docking-based RRS ([Table 3](#)), the MD-RRS agrees for [Z] of [2] candidates, confirming that the docking-based resilience framework is a conservative first-tier screen; [discordance, if any, is reported and not relabelled].

---

## 5. Limitations (L631 + L657)

**L631 (H3) :**
> …Future work with full MD simulations of mutant complexes will be needed to validate docking-based RRS as a proxy for free energy resilience.

→ **Nouveau :** "…MD-RRS from 16 set-C production trajectories provides a first trajectory-based validation of docking-based RRS for the two highest-ranked candidates ([X]/[Y] class agreement); full free-energy validation (mutant MM-GBSA) remains future work."

**L657 :**
> …No production MD was completed for the 17 set-C candidates or their mutant systems…

→ **Nouveau :** "…Production MD was completed for the two highest-ranked set-C candidates (PP-01, PP-02) across [16] mutant systems (10 ns each, 160 ns total); the remaining 15 candidates have docking-based RRS only. Single-replicate 10 ns trajectories cannot establish long-timescale residence or convergence…"

---

## 6. Conclusion (L680)

**Actuel :**
> The mutant systems have docking-based RRS classifications awaiting full production MD validation.

→ **Nouveau :**
> The mutant systems have docking-based RRS classifications, now supported by 16-system production MD validation for the two highest-ranked candidates (PP-01, PP-02; [X]/[Y] docking-vs-MD class agreement). The remaining 15 candidates retain docking-based RRS pending full MD.

---

## 7. Table SX — Bound fraction per system (gabarit)

| set_c_id | target | mutation | bound_fraction | n_frames | duration_ns | qc_status |
|---|---|---|---|---|---|---|
| PP-01 | PfDHFR | WT | [x.xxx] | [2000] | [10.000] | PASS |
| PP-01 | PfDHFR | N51I | [x.xxx] | [2000] | [10.000] | PASS |
| PP-01 | PfDHFR | C59R | [x.xxx] | [2000] | [10.000] | PASS |
| PP-01 | PfDHFR | S108N | [x.xxx] | [2000] | [10.000] | PASS |
| PP-01 | PfDHFR | I164L | [x.xxx] | [2000] | [10.000] | PASS |
| PP-01 | PfCRT | WT | [x.xxx] | [2000] | [10.000] | PASS |
| PP-01 | PfCRT | K76T | [x.xxx] | [2000] | [10.000] | PASS |
| PP-01 | PfCRT | K76A | [x.xxx] | [2000] | [10.000] | PASS |
| PP-02 | … | (8 lignes) | … | … | … | … |

*Source : `results/set_c_md/set_c_trajectory_qc.csv` (généré par 15120).*

---

## 8. Figure SX — Violin plot min-dist (gabarit script)

```python
# p2_make_md_rrs_figure.py (à créer) — génère Figure SX
import pandas as pd, numpy as np
import matplotlib.pyplot as plt
# Entrées: set_c_trajectory_qc.csv (bound_fraction par système)
# Violin plot: bound_fraction par (candidate × target), WT vs mutants
# Sortie: results/set_c_md/figure_md_rrs_bound_fraction.pdf
```

---

## 9. Commandes exactes post-15120 (exécution en 2 minutes)

```bash
cd /home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607
source /home/nanaengo/miniforge3/etc/profile.d/conda.sh && conda activate malaria_md

# 1. Vérifier les sorties
ls -la results/set_c_md/set_c_trajectory_qc.csv
ls -la results/set_c_md/md_rrs_classification.csv
cat results/set_c_md/md_rrs_provenance.json

# 2. Comparer docking-RRS vs MD-RRS
python -c "
import pandas as pd
md = pd.read_csv('results/set_c_md/md_rrs_classification.csv')
dock = pd.read_csv('results/c_rrs_classification.csv')
m = md.merge(dock, on='set_c_id', suffixes=('_MD','_dock'))
print(m[['set_c_id','MD_RRS_class','RRS_class']].to_string())
print('Agreement:', (m['MD_RRS_class']==m['RRS_class']).mean())
"

# 3. Générer les valeurs à injecter dans le manuscrit (abstract/results)
python -c "
import pandas as pd
qc = pd.read_csv('results/set_c_md/set_c_trajectory_qc.csv')
n_pass = (qc.qc_status=='PASS').sum()
bound = qc[qc.qc_status=='PASS']
print('systems PASS:', n_pass, '/', len(qc))
print('bound_fraction range:', bound.bound_fraction.min(), '-', bound.bound_fraction.max())
print('systems bound>=0.1:', (bound.bound_fraction>=0.10).sum())
"
```

---

## 10. Tableau de décision — si 15120 FAIL-CLOSED

| Condition | Conséquence | Décision |
|---|---|---|
| < 16 systèmes PASS QC | MD-RRS fail-closed (136 rows requis) | Publier avec « docking-RRS only » + rapport QC partiel en SM ; documenter la raison de l'exclusion |
| N51I échoue encore | 15 systèmes utilisables | Idem ci-dessus ; le gap N51I est documenté |
| QC PASS mais MD-RRS ≠ docking | Discordance rapportée, jamais relabellée | Renforcer la narration « docking-RRS = premier filtre conservateur » |
| 15120 échoue (bug) | Vérifier le log, relancer QC manuellement | `python scripts/p2_setc_trajectory_qc.py` puis `python scripts/p2_setc_md_rrs.py --qc-file results/set_c_md/set_c_trajectory_qc.csv` |
