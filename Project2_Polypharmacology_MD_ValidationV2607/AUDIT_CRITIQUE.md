# Audit Critique — Project2_Polypharmacology_MD_Validation

**Date :** 4 juillet 2026  
**Répertoire :** `/home/taamangtchu/Documents/Github/Malaria_codes/Project2_Polypharmacology_MD_Validation`  
**Objet :** Audit complet du projet MD+MC Validation  
**Cible :** JCIM (IF 5.6) — Soumission janvier 2027  
**Version draft :** v0.6  
**Audit précédent :** 28 mai 2026 (`docs/audit_project_260528.md`)

---

## Vue d'ensemble

Projet avancé de validation MD+MC de 20 candidats polypharmacologiques antimalariaux. Contrairement à la version `Papers/`, ce répertoire contient :
- Un pipeline de scripts complet (15 scripts Python/Bash)
- Un dossier `Tuto_MD_MC/` de 88 fichiers (tutoriels, corrections, guides)
- Une documentation structurée (ROADMAP 628 lignes, METHODS 747 lignes)
- Un audit précédent (28 mai 2026) identifiant déjà des incohérences
- Une composante **Monte Carlo** (OpenMM) en plus de la MD (GROMACS)
- **30 000 ns** de MD et **220 systèmes** (vs 18 000 ns / 160 dans le manuscript)

**Paradoxe central** : Les scripts des Phases 2–6 sont déjà écrits, mais le manuscript est resté à v0.6 avec des tables Results vides. L'audit du 28 mai a identifié des problèmes qui **n'ont toujours pas été résoluits** 5 semaines plus tard.

---

## 1. PROBLÈMES CRITIQUES

### 1.1 Manuscript identique à la version Papers/ — Aucune progression

Le fichier `manuscript/LaTeX/Paper2_Draft_v0.6.tex` est **identique** (450 lignes, même contenu) à celui de `Papers/Polypharmacology_MD_Validation/`. Les tables Results restent vides :

| Table | Contenu | Statut |
|-------|---------|--------|
| `tab:homology` (L236–252) | 6 mutants, 0 valeurs QMEAN/GMQE | **VIDE** |
| `tab:rrs` (L258–275) | 5 ligands, 1 seule valeur | **VIDE** |
| `tab:pns` (L292–303) | 0 lignes de données | **VIDE** |
| `tab:mmgbsa` (L327–343) | 5 ligands, 0 ΔG_bind | **VIDE** |
| `tab:crossmetric` (L364–377) | 3 hypothèses, 0 résultats | **VIDE** |

**6 sections Results vides** : Docking Validation, MPO Sensitivity, ADMET Cross-Validation, Correlation Between Methods, Consensus Leads, Cross-Metric Correlation.

**6 figures planifiées** : AUCUNE figure n'est mentionnée comme existante dans les résultats.

### 1.2 Incohérence manuscript vs README — Chiffres contradictoires

| Element | Manuscript (v0.6) | README.md | Écart |
|---------|-------------------|-----------|-------|
| Total MD | 18 000 ns | 30 000 ns | **+67%** |
| Systèmes | 160 | 220 | **+37.5%** |
| Contrôles | 5 drugs × 4 targets = 20 | 5 drugs × 4 targets = 20 | OK |
| MC steps | Non mentionné | 2 200 000 | **Nouveau** |
| Métriques | 4 (RRS, ACSI, PNS, MM-GBSA) | 5 (+ MC landscapes) | **+1** |

Le manuscript n'a pas été mis à jour pour refléter l'ajout du Monte Carlo ni l'augmentation à 30 000 ns / 220 systèmes.

### 1.3 Bibliographie toujours fictive

Le fichier `Bibliography_Paper2.bib` est **identique** à la version Papers/ :
- ~80% des entrées avec `author = {Author, A. and Author, B.}`
- Volumes/pages sur `xxxx`
- `temgoua2026antimalarial` avec `doi = {pending}`
- **14 entrées critiques avec auteurs fictifs** : `computational_mutations_2025`, `ghana_resistance_2026`, `africa_resistance_2026`, `pfk13_resistance_2026`, `global_resistance_landscape_2026`, `anpdb_2026`, `anpdb_researchgate_2026`, `value_addition_african_np_2025`, `addressing_infectious_diseases_africa_2025`, `polypharmacology_malaria_2026`, `multi_target_antimalarials_2025`, `mmgbsa_best_practices_2025`, `network_pharmacology_malaria_2025`, `md_antimalarial_2026`

### 1.4 Audit du 28 mai — Problèmes non résolus

L'audit `docs/audit_project_260528.md` identifiait 4 actions prioritaires. **Aucune n'a été complétée** :

| Action demandée (28 mai) | Statut (4 juillet) |
|--------------------------|---------------------|
| Restaurer l'arborescence des résultats | ❌ `results/figures/`, `results/tables/`, `data/ligands/`, `data/md_inputs/`, `results/md_systems/` toujours absents |
| Générer Figure S1 (MPO heatmap) | ❌ Seul le CSV brut existe |
| Compiler Table S0 (docking validation) | ❌ Absente |
| Mettre à jour le ROADMAP.md | ❌ Phases 2–6 toujours "🔴 Not Started" malgré les scripts |
| Clôturer Phase 1 (ADMET) | ❌ Aucune trace de données ADMET |

### 1.5 Dossier Tuto_MD_MC — Encombrement majeur

Le dossier `Tuto_MD_MC/` contient **88 fichiers** dont :
- ~30 fichiers `.md` de statut/session (SESSION_COMPLETE_SUMMARY.md, WHERE_WE_ARE_NOW.md, CURRENT_SITUATION_SUMMARY.md, etc.)
- ~20 scripts Python de test/debug (test_*.py, fix_*.py, check_*.py)
- ~10 guides de correction (CORRECTION_STRATEGY_SUMMARY.md, CHANGELOG_CORRECTIONS.md)
- Des sous-dossiers de données intermédiaires (ligand_prep/, protein_prep/, complex_assembly/)

Ce dossier est un **environnement de travail temporaire** qui ne devrait pas faire partie du repo principal. Il pollue l'arborescence et rend la navigation difficile.

---

## 2. PROBLÈMES MÉTHODOLOGIQUES

### 2.1 Monte Carlo — Non validé scientifiquement

L'ajout du MC (OpenMM, 10 000 steps/système) est une innovation par rapport au manuscript v0.6, mais :
- **Aucune référence bibliographique** ne justifie l'usage du MC comme complément au MD pour le binding free energy landscape
- Le script `mc_sampling_openMM.py` dans `docs/METHODS.md` utilise `amber14-all.xml` (force field AMBER) alors que le MD utilise CHARMM36m — **incohérence de force field entre MD et MC**
- Le threshold de convergence `|ΔG_MC - ΔG_MD| < 2 kcal/mol` n'est pas standard dans la littérature
- Le manuscript ne mentionne pas le MC du tout

### 2.2 Force field mixte — Toujours non discuté

Le manuscript utilise CGenFF pour PfCRT (membrane) et OpenFF 2.2 pour les autres cibles. Le biais introduit n'est toujours pas discuté dans les Limitations.

### 2.3 RRS — Formule basée sur le docking, pas le MD

Le RRS utilise des scores Vina (docking), mais le manuscript introduit le MC comme complément. Il faut clarifier :
- Le RRS est-il docking-only ?
- Une version MM-GBSA ou MC-enhanced est-elle prévue ?
- La corrélation RRS (docking) vs ΔG_MM-GBSA (MD) est-elle testée ?

### 2.4 ACSI — Poids toujours arbitraires

Les poids (0.40, 0.25, 0.20, 0.15) ne sont toujours pas justifiés empiriquement. La sensitivity analysis (Table S6) n'existe pas.

### 2.5 Cross-reference cassée vers Paper3

```latex
\externaldocument[P3-]{../../Quantum_Inspired_Representations/LaTeX/Paper3_Draft_v0.6}
```

Ce chemin est toujours relatif et fragile. De plus, le Paper3 n'est probablement pas dans cette arborescence.

---

## 3. PROBLÈMES D'ORGANISATION

### 3.1 Structure du répertoire — Comparaison avant/après

```
Project2_Polypharmacology_MD_Validation/
├── README.md                          ✅ Bien structuré, badges, Quick Start
├── PROJECT_COMPLETION_SUMMARY.md      ⚠️ Désuet — décrit une arborescence qui n'existe plus
├── REORGANIZATION_SUMMARY.md          ⚠️ Désuet — décrit des changements non maintenus
├── docs/
│   ├── ROADMAP.md                     ✅ 628 lignes, Mermaid Gantt, mais statuts obsolètes
│   ├── METHODS.md                     ✅ 747 lignes, code exemples, mais MC pas dans manuscript
│   └── audit_project_260528.md        ⚠️ Audit précédent non résolu
├── manuscript/
│   ├── LaTeX/Paper2_Draft_v0.6.tex    ❌ Identique à Papers/, tables vides
│   ├── LaTeX/Bibliography_Paper2.bib  ❌ ~80% auteurs fictifs
│   └── Methods/                       ✅ MD_Protocol.md, MM-GBSA_Methodology.md
├── scripts/                           ✅ 15 scripts pipeline (Python + Bash)
├── results/
│   └── candidate_selection/           ✅ CSVs Top 3/5/10/20/50 + MPO sensitivity
│   ├── figures/                       ❌ ABSENT
│   ├── tables/                        ❌ ABSENT
│   ├── md_systems/                    ❌ ABSENT
│   ├── trajectories/                  ❌ ABSENT
│   └── metrics/                       ❌ ABSENT
├── data/                              ⚠️ Sous-dossiers décrits dans README mais absents
├── environments/                      ✅ environment_md.yml
├── Tuto_MD_MC/                        ❌ 88 fichiers de debug/tutoriel — encombrement
└── test_pymol.py                      ⚠️ Script isolé à la racine
```

### 3.2 Fichiers désuets à nettoyer

| Fichier | Problème | Action |
|---------|----------|--------|
| `PROJECT_COMPLETION_SUMMARY.md` | Décrit une arborescence qui n'existe plus | Mettre à jour ou supprimer |
| `REORGANIZATION_SUMMARY.md` | Décrit des changements non maintenus | Mettre à jour ou supprimer |
| `Tuto_MD_MC/` (88 fichiers) | Environnement de debug/temporaire | Déplacer vers branche séparée ou .gitignore |
| `test_pymol.py` | Script isolé à la racine | Déplacer vers `scripts/` ou `Tuto_MD_MC/` |
| `Bibliography_Paper2.bib.txt` | Copie redondante | Supprimer si identique au .bib |
| `Bibliography_Paper3.bib` | Hors-scope Paper 2 | Déplacer vers Paper 3 |

---

## 4. SCRIPTS — ÉTAT D'AVANCEMENT

Les scripts du pipeline sont écrits mais **non exécutés** (pas de résultats dans `results/`) :

| Script | Phase | Statut | Résultat disponible |
|--------|-------|--------|---------------------|
| `md_prepare_ligands.py` | Phase 4 | ✅ Écrit | ❌ Non exécuté |
| `md_prepare_proteins.py` | Phase 4 | ✅ Écrit | ❌ Non exécuté |
| `md_build_complexes.py` | Phase 4 | ✅ Écrit | ❌ Non exécuté |
| `md_homology_mutants.py` | Phase 2 | ✅ Écrit | ❌ Non exécuté |
| `md_calculate_rrs_acsi_pns.py` | Phase 3 | ✅ Écrit | ❌ Non exécuté |
| `md_analyse_trajectories.py` | Phase 6 | ✅ Écrit | ❌ Non exécuté |
| `md_full_pipeline.sh` | Phase 5 | ✅ Écrit | ❌ Non exécuté |
| `md_run_minimisation.sh` | Phase 5 | ✅ Écrit | ❌ Non exécuté |
| `md_run_nvt.sh` | Phase 5 | ✅ Écrit | ❌ Non exécuté |
| `md_run_npt.sh` | Phase 5 | ✅ Écrit | ❌ Non exécuté |
| `md_run_production.sh` | Phase 5 | ✅ Écrit | ❌ Non exécuté |

**Constat** : Le code est prêt, mais aucune simulation n'a été lancée. Le bottleneck n'est pas le développement logiciel mais l'exécution computationnelle.

---

## 5. RÉSULTATS EXISTANTS

### 5.1 Candidate Selection (Phase 1 — Complète)

| Fichier | Contenu | Statut |
|---------|---------|--------|
| `md_top50_candidates.csv` | 5 lignes (Top 5 sur 50), colonnes: rank, smiles, weighted_mpo_score, syba_score, SI, sa_score, qed, MPO_multi, MPO_per_target, Hit_Tier, ClinTox, AMES, hERG, DILI | ⚠️ Incomplet (5 lignes au lieu de 50) |
| `md_top20_candidates.csv` | Top 20 candidats | ✅ |
| `md_top20_smiles.smi` | SMILES des Top 20 | ✅ |
| `mpo_sensitivity_analysis.csv` | Analyse de sensibilité MPO | ✅ mais figure absente |

### 5.2 Ce qui manque

- **Aucune trajectoire MD** (results/trajectories/ absent)
- **Aucun snapshot MC** (results/mc_snapshots/ absent)
- **Aucun résultat MM-GBSA** (results/metrics/ absent)
- **Aucune figure** (results/figures/ absent)
- **Aucune table formatée** (results/tables/ absent)
- **Aucune structure mutant** (results/mutant_structures/ absent)
- **Aucun système MD préparé** (results/md_systems/ absent)

---

## 6. RÉSUMÉ DES SCORES

| Aspect | Score | Commentaire |
|--------|-------|-------------|
| **Structure du projet** | 7/10 | Bien organisée, README professionnel, mais fichiers désuets |
| **Documentation** | 7/10 | ROADMAP et METHODS complets, mais statuts obsolètes |
| **Scripts pipeline** | 8/10 | 15 scripts écrits, couverture complète du workflow |
| **Manuscript** | 3/10 | Identique à v0.6, tables vides, chiffres obsolètes |
| **Bibliographie** | 3/10 | ~80% auteurs fictifs, inchangée depuis l'audit |
| **Résultats** | 2/10 | Seule la sélection de candidats existe, rien d'autre |
| **Cohérence manuscript/projet** | 2/10 | 18k ns vs 30k ns, 160 vs 220 systèmes, MC absent |
| **Résolution des audits précédents** | 1/10 | Audit du 28 mai non résolu |
| **Nettoyage du dossier** | 3/10 | Tuto_MD_MC (88 fichiers) encombre le projet |

---

## 7. PLAN D'ACTION

### Priorité 1 — Blocage (immédiat)

1. **Lancer les simulations MD** — Le code est prêt, il faut exécuter. Estimer les ressources GPU nécessaires (4× A100 pour ~45 jours).
2. **Mettre à jour le manuscript** — Harmoniser les chiffres (30 000 ns, 220 systèmes), ajouter le MC dans les Methods.
3. **Corriger la bibliographie** — Vérifier les 14 entrées fictives via CrossRef API.

### Priorité 2 — Cohérence (semaine prochaine)

4. **Mettre à jour le ROADMAP.md** — Changer les statuts des Phases 2–6 en "🟡 Scripts Ready / Pending Execution".
5. **Résoudre l'audit du 28 mai** — Les 5 actions identifiées restent valides.
6. **Ajouter le MC dans le manuscript** — Nouvelle section Methods, références, force field AMBER→CHARMM.

### Priorité 3 — Nettoyage (ce mois)

7. **Déplacer Tuto_MD_MC/** — Vers une branche séparée, un repo séparé, ou le .gitignore.
8. **Nettoyer les fichiers désuets** — PROJECT_COMPLETION_SUMMARY.md, REORGANIZATION_SUMMARY.md, test_pymol.py.
9. **Créer l'arborescence results/** — Sous-dossiers figures/, tables/, md_systems/, trajectories/, metrics/.
10. **Séparer les fichiers hors-scope** — Bibliography_Paper3.bib, HOW_TO_CITE_DD4GH.md, USEFUL_RESOURCES_LIKE_DD4GH.md.

### Priorité 4 — Soumission JCIM

11. **Générer les figures** — 7 figures main text + supplementary.
12. **Préparer le Supporting Information** — Tables S0–S6, Figures S1–S6.
13. **Migrer vers achemso** — Template JCIM.
14. **Rédiger la cover letter** — Angle "African-led, resistance-informed, open-source, MC-enhanced".

---

## 8. ÉCHÉANCIER RÉVISÉ

| Échéance | Action | Dépendance |
|----------|--------|------------|
| **Juillet 2026** | Lancer MD WT (80 systèmes × 200 ns) | GPU allocation |
| **Juillet 2026** | Mettre à jour manuscript (chiffres + MC) | Aucune |
| **Juillet 2026** | Corriger bibliographie (14 entrées fictives) | Aucune |
| **Août 2026** | Lancer MD mutants (120 systèmes × 100 ns) | WT terminés |
| **Août 2026** | Générer homology models (6 mutants) | Script prêt |
| **Sept 2026** | Lancer MC sampling (220 × 10k steps) | MD terminés |
| **Oct 2026** | Trajectory analysis + MM-GBSA | MC terminés |
| **Nov 2026** | Calculer RRS, ACSI, PNS | Données disponibles |
| **Nov 2026** | Générer 7 figures | Données disponibles |
| **Déc 2026** | Rédiger Discussion + Conclusion | Toutes données |
| **Déc 2026** | Préparer SI (Tables S0–S6) | Toutes données |
| **Jan 2027** | Review interne + soumission | Draft complet |

---

## 9. CONCLUSION

Ce répertoire représente un **projet mature sur le plan logiciel** (15 scripts, documentation complète, pipeline automatisé) mais **immature sur le plan scientifique** (manuscript v0.6 inchangé, aucune simulation exécutée, bibliographie fictive).

L'audit du 28 mai 2026 a identifié des problèmes qui n'ont toujours pas été résoluits 5 semaines plus tard. Le bottleneck principal est **l'exécution des simulations MD** (30 000 ns sur 220 systèmes), pas le développement de code.

**Estimation de complétion** : ~25% (scripts prêts, données de sélection disponibles, mais aucune simulation, aucun résultat, manuscript obsolète).

**Risque principal** : Si les simulations MD ne démarrent pas d'ici août 2026, la date de soumission (janvier 2027) est compromise.

---

*Audit généré le 4 juillet 2026.*

---

## 10. SOLUTIONS DÉTAILLÉES PAR PROBLÈME

---

### 10.1 Mettre à jour le manuscript (chiffres + MC)

#### 10.1.1 Corriger les incohérences chiffrées

Dans `manuscript/LaTeX/Paper2_Draft_v0.6.tex`, remplacer :

```latex
% L97 — Abstract : remplacer 18 000 ns par 30 000 ns
% Avant :
Here we validate the 20 highest-ranked candidates by molecular dynamics
simulations totaling \SI{18000}{\nano\second} across 160 protein--ligand systems

% Après :
Here we validate the 20 highest-ranked candidates by molecular dynamics
simulations totaling \SI{30000}{\nano\second} across 220 protein--ligand systems
```

```latex
% L116 — Introduction : idem
Here we perform \SI{30000}{\nano\second} of MD simulation across
220 protein--ligand systems
```

```latex
% L126 — Methods : corriger le calcul
% Avant : 20 WT + 6×20 mutants + 20 controls = 160
% Après : 20 WT + 6×20 mutants + 20 controls = 160 WT/mutants + 60 controls = 220
% Vérifier : 20 ligands × 4 WT = 80 WT systems
%           20 ligands × 6 mutants = 120 mutant systems
%           5 drugs × 4 WT = 20 control systems
%           Total = 80 + 120 + 20 = 220 ✓
```

#### 10.1.2 Ajouter le Monte Carlo dans les Methods

Ajouter une nouvelle subsection après la section MM-GBSA (après L204) :

```latex
\subsection{Monte Carlo Binding Free Energy Landscapes}

Monte Carlo (MC) sampling was performed using OpenMM 8.1 to explore
binding free energy landscapes from the final MD frame of each stable
system. The Metropolis criterion was applied with a move set comprising
ligand translation (0.5 \AA, 40\%), rotation (15$^\circ$, 30\%),
side-chain torsion (30$^\circ$, 20\%), and protein side-chain rotation
(10\% weight). Each system was sampled for \num{10000} MC steps at
\SI{300}{\kelvin}, with snapshots saved every 100 steps for
rescoring by MM-GBSA. The acceptance rate was monitored and systems
with rates outside 20--40\% were flagged for move-set adjustment.

MC-derived binding free energies ($\Delta G_{\mathrm{MC}}$) were
compared with MD-derived MM-GBSA values ($\Delta G_{\mathrm{MD}}$)
to assess convergence. Systems where
$|\Delta G_{\mathrm{MC}} - \Delta G_{\mathrm{MD}}| >
\SI{2}{\kcal\per\mol}$ were flagged as sampling-limited and
discussed as limitations.
```

#### 10.1.3 Mettre à jour la section Limitations

```latex
\subsection{Limitations}

% ... texte existant ...

\textbf{Force field heterogeneity.}
Ligands bound to PfCRT (membrane protein) were parameterised with
CGenFF v4.4, while ligands bound to PfDHFR, PfATP4, and PfClpP
(soluble proteins) were parameterised with OpenFF 2.2 (Sage).
While this choice reflects best practices for each environment,
it introduces a systematic heterogeneity that may affect
inter-target comparisons.

\textbf{Monte Carlo force field mismatch.}
MC sampling used the AMBER14 force field (via OpenMM), while MD
simulations used CHARMM36m (via GROMACS). Although both are
well-validated for protein-ligand systems, the force field
difference introduces a systematic offset in absolute binding
free energies. We address this by focusing on relative rankings
and convergence metrics rather than absolute values.
```

#### 10.1.4 Ajouter le MC dans la Conclusion

```latex
% Remplacer L422 par :
We present a resistance-aware computational framework for antimalarial
lead validation that integrates \SI{30000}{\nano\second} of molecular
dynamics simulation with Monte Carlo binding free energy landscape
exploration across 220 protein--ligand systems. Three novel scoring
metrics are introduced: the Resistance Resilience Score classifies
polypharmacological leads by their ability to maintain binding
affinity across six African-prevalent resistance mutations; the
African Chemical Space Index quantifies the degree to which generated
compounds preserve the structural character of African natural
products; and the Polypharmacology Network Score weights
multi-target engagement by the topological importance of each target
in the \textit{P. falciparum} interactome. All scripts, trajectories,
and scoring metrics are deposited on Zenodo and GitHub to support
resistance-aware antimalarial discovery.
```

---

### 10.2 Corriger la bibliographie fictive

#### 10.2.1 Script de vérification automatique

```python
#!/usr/bin/env python3
"""verify_bib_project2.py — Identifier les entrées fictives dans Bibliography_Paper2.bib"""

import re
import sys
from pathlib import Path

def check_bib(filepath):
    content = Path(filepath).read_text(encoding="utf-8")

    # Trouver toutes les entrées
    pattern = r'@\w+\{(\w+),\s*\n(.*?)\n\}'
    entries = re.findall(pattern, content, re.DOTALL)

    suspicious = []
    real = []
    for key, block in entries:
        if 'Author, A.' in block or 'Author, B.' in block:
            suspicious.append(key)
        elif 'xxxx' in block or 'xxx' in block:
            suspicious.append(key)
        else:
            real.append(key)

    print(f"Entrées réelles : {len(real)} / {len(entries)}")
    print(f"Entrées fictives/suspectes : {len(suspicious)} / {len(entries)}")
    print()
    print("=== Entrées à corriger ===")
    for s in suspicious:
        print(f"  - {s}")
    print()
    print("=== Entrées valides ===")
    for r in real:
        print(f"  - {r}")

    return suspicious

if __name__ == "__main__":
    bib_path = sys.argv[1] if len(sys.argv) > 1 else "manuscript/LaTeX/Bibliography_Paper2.bib"
    check_bib(bib_path)
```

```bash
cd /home/taamangtchu/Documents/Github/Malaria_codes/Project2_Polypharmacology_MD_Validation
python verify_bib_project2.py
```

#### 10.2.2 Script de recherche DOI via CrossRef

```python
#!/usr/bin/env python3
"""find_doi_crossref.py — Rechercher le DOI d'un article via CrossRef API"""

import requests
import time
import sys

def find_doi(title,作者=None):
    """Rechercher un article par titre sur CrossRef."""
    url = "https://api.crossref.org/works"
    params = {
        "query.title": title,
        "rows": 3,
        "sort": "relevance"
    }
    try:
        r = requests.get(url, params=params, timeout=15)
        if r.status_code == 200:
            items = r.json()["message"]["items"]
            for item in items:
                doi = item.get("DOI", "")
                author_list = [a.get("family", "") for a in item.get("author", [])]
                journal = item.get("container-title", [""])[0]
                year = str(item.get("published-print", {}).get("date-parts", [[""]])[0][0])
                print(f"  Candidat: {doi}")
                print(f"    Auteurs: {', '.join(author_list[:3])}")
                print(f"    Journal: {journal}")
                print(f"    Année: {year}")
                return doi
        else:
            print(f"  Erreur HTTP {r.status_code}")
    except Exception as e:
        print(f"  Erreur: {e}")
    return None

# Entrées à vérifier (extraits du .bib)
entries_to_check = [
    "Computational investigation of mutations in PfCRT and PfDHFR",
    "Profiling antimalarial drug-resistant haplotypes in Pfcrt",
    "Antimalarial drug resistance mechanisms and treatment outcomes",
    "Molecular markers of antimalarial drug resistance in pfk13",
    "The global landscape of Plasmodium falciparum drug resistance markers",
    "African Natural Products Database",
    "Value addition to African natural product-based drug discovery",
    "Addressing infectious diseases in Africa by accelerating AI/ML",
    "Polypharmacology in malaria treatment single drugs multiple targets",
    "Recent insights in multi-target drugs in pharmacology",
    "Best practices for MM-GBSA binding free energy calculations",
    "Network pharmacology molecular docking molecular dynamics CE-326597",
    "Molecular Dynamics in Antimalarial Drug Design",
]

if __name__ == "__main__":
    for title in entries_to_check:
        print(f"\nRecherche: {title[:60]}...")
        find_doi(title)
        time.sleep(1)  # Rate limiting
```

#### 10.2.3 Entrées prioritaires à corriger

**Catégorie A — Citées dans le texte (doivent être correctes)** :

| Key | Problème | Action |
|-----|----------|--------|
| `temgoua2026antimalarial` | `doi = {pending}`, `pages = {xxxx}` | Vérifier si paper 1 est soumis/publié |
| `who_malaria_2025` | OK (URL correcte) | ✓ |
| `charmm36m_2017` | OK (DOI correct) | ✓ |
| `gromacs_2015` | OK (DOI correct) | ✓ |
| `gmx_mmpbsa_2021` | OK (DOI correct) | ✓ |
| `mdanalysis_2019` | **Key faux** : publication 2011, key 2019 | Corriger en `mdanalysis_2011` |

**Catégorie B — Fictives (à compléter ou supprimer)** :

| Key | Journal suggéré | Action |
|-----|-----------------|--------|
| `computational_mutations_2025` | Acta Tropica | CrossRef search |
| `ghana_resistance_2026` | Malaria Journal | CrossRef search |
| `africa_resistance_2026` | Inconnu | CrossRef search |
| `pfk13_resistance_2026` | Malaria Journal | CrossRef search |
| `global_resistance_landscape_2026` | Lancet Microbe | CrossRef search |
| `anpdb_2026` | Inconnu | PubMed search |
| `anpdb_researchgate_2026` | Preprint | Vérifier si publié |
| `value_addition_african_np_2025` | J. Nat. Prod. | DOI déjà présent → vérifier |
| `addressing_infectious_diseases_africa_2025` | Nature Comm | URL présente → vérifier |
| `polypharmacology_malaria_2026` | Trends Parasitol. | CrossRef search |
| `multi_target_antimalarials_2025` | ChemMedChem | DOI déjà présent → vérifier |
| `mmgbsa_best_practices_2025` | JCIM | DOI déjà présent → vérifier |
| `network_pharmacology_malaria_2025` | MalariaWorld | URL présente → vérifier |
| `md_antimalarial_2026` | Springer book | ISBN manquant → cherche |

---

### 10.3 Mettre à jour le ROADMAP.md

#### 10.3.1 Changer les statuts des phases

Dans `docs/ROADMAP.md`, remplacer :

```markdown
### Phase 2: Resistance Mutation Modeling (June 2026)
**Status:** 🔴 Not Started

% Par :
**Status:** 🟡 Scripts Ready / Pending Execution
- ✅ `scripts/md_homology_mutants.py` — script d'homology modeling écrit
- ⏳ En attente d'allocation GPU pour exécution
```

```markdown
### Phase 3: Novel Metrics Development (June 2026)
**Status:** 🔴 Not Started

% Par :
**Status:** 🟡 Scripts Ready / Pending Execution
- ✅ `scripts/md_calculate_rrs_acsi_pns.py` — calcul RRS, ACSI, PNS écrit
- ⏳ En attente des résultats MD/MM-GBSA
```

```markdown
### Phase 4: System Preparation (July 2026)
**Status:** 🔴 Not Started

% Par :
**Status:** 🟡 Scripts Ready / Pending Execution
- ✅ `scripts/md_prepare_ligands.py` — préparation ligands écrite
- ✅ `scripts/md_prepare_proteins.py` — préparation protéines écrit
- ✅ `scripts/md_build_complexes.py` — assemblage complexes écrit
- ⏳ En attente d'allocation GPU
```

```markdown
### Phase 5: Production MD + MC (Aug-Oct 2026)
**Status:** 🔴 Not Started

% Par :
**Status:** 🟡 Scripts Ready / Pending Execution
- ✅ `scripts/md_full_pipeline.sh` — pipeline complet écrit
- ✅ `scripts/md_run_*.sh` — scripts de run écrits
- ✅ MC sampling implémenté dans docs/METHODS.md
- ⏳ En attente de Phase 4
```

```markdown
### Phase 6: Analysis (November 2026)
**Status:** 🔴 Not Started

% Par :
**Status:** 🟡 Scripts Ready / Pending Execution
- ✅ `scripts/md_analyse_trajectories.py` — analysis écrite
- ⏳ En attente de Phase 5
```

#### 10.3.2 Ajouter une section "Code Status" dans le ROADMAP

```markdown
## Code Development Status

| Phase | Script | Status | Blocking |
|-------|--------|--------|----------|
| Phase 2 | `md_homology_mutants.py` | ✅ Written | GPU allocation |
| Phase 3 | `md_calculate_rrs_acsi_pns.py` | ✅ Written | Phase 5 output |
| Phase 4 | `md_prepare_ligands.py` | ✅ Written | GPU allocation |
| Phase 4 | `md_prepare_proteins.py` | ✅ Written | GPU allocation |
| Phase 4 | `md_build_complexes.py` | ✅ Written | GPU allocation |
| Phase 5 | `md_full_pipeline.sh` | ✅ Written | Phase 4 output |
| Phase 5 | `md_run_minimisation.sh` | ✅ Written | Phase 4 output |
| Phase 5 | `md_run_nvt.sh` | ✅ Written | minimisation output |
| Phase 5 | `md_run_npt.sh` | ✅ Written | NVT output |
| Phase 5 | `md_run_production.sh` | ✅ Written | NPT output |
| Phase 6 | `md_analyse_trajectories.py` | ✅ Written | Phase 5 output |

**Conclusion:** All scripts are developed. The bottleneck is GPU execution, not code development.
```

---

### 10.4 Résoudre l'audit du 28 mai

#### 10.4.1 Restaurer l'arborescence results/

```bash
#!/bin/bash
# create_results_structure.sh — Créer l'arborescence results/ manquante

PROJECT="/home/taamangtchu/Documents/Github/Malaria_codes/Project2_Polypharmacology_MD_Validation"

mkdir -p "$PROJECT/results/figures"
mkdir -p "$PROJECT/results/tables"
mkdir -p "$PROJECT/results/md_systems"
mkdir -p "$PROJECT/results/trajectories"
mkdir -p "$PROJECT/results/mc_snapshots"
mkdir -p "$PROJECT/results/metrics"
mkdir -p "$PROJECT/results/mutant_structures"
mkdir -p "$PROJECT/results/analysis"

# Créer un .gitkeep pour garder les dossiers vides dans git
for dir in figures tables md_systems trajectories mc_snapshots metrics mutant_structures analysis; do
    touch "$PROJECT/results/$dir/.gitkeep"
done

echo "✓ Arborescence results/ créée"
ls -la "$PROJECT/results/"
```

#### 10.4.2 Générer la Figure S1 (MPO Sensitivity Heatmap)

```python
#!/usr/bin/env python3
"""generate_figure_s1.py — Générer la heatmap de sensibilité MPO"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

# Charger les données
df = pd.read_csv("results/candidate_selection/mpo_sensitivity_analysis.csv")
print(f"Colonnes: {list(df.columns)}")
print(f"Lignes: {len(df)}")
print(df.head())

# Extraire les poids et la similarité de Jaccard
# Adapter selon le format réel du CSV
# Exemple si le CSV a: vina_weight, diffdock_weight, qed_weight, admet_weight, ro5_weight, jaccard

fig, ax = plt.subplots(figsize=(10, 8))

# Créer une heatmap 5×5 pour les variations de poids
# (adapter selon la structure réelle des données)
weight_cols = [c for c in df.columns if 'weight' in c.lower()]
if len(weight_cols) >= 2:
    pivot = df.pivot_table(
        values='jaccard' if 'jaccard' in df.columns else df.columns[-1],
        index=weight_cols[0],
        columns=weight_cols[1],
        aggfunc='mean'
    )
    im = ax.imshow(pivot.values, cmap='RdYlGn', vmin=0.5, vmax=1.0, aspect='auto')
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels([f"{x:.2f}" for x in pivot.columns], rotation=45)
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels([f"{x:.2f}" for x in pivot.index])
    ax.set_xlabel(weight_cols[1].replace('_', ' ').title())
    ax.set_ylabel(weight_cols[0].replace('_', ' ').title())
    ax.set_title("MPO Weight Sensitivity Analysis\n(Jaccard Similarity to Original Top-20)")
    plt.colorbar(im, ax=ax, label="Jaccard Index")
    plt.tight_layout()
    plt.savefig("results/figures/figure_s1_mpo_sensitivity.pdf", dpi=300)
    plt.savefig("results/figures/figure_s1_mpo_sensitivity.png", dpi=300)
    plt.close()
    print("✓ Figure S1 générée")
else:
    print("⚠ Format CSV non reconnu — adapter le script")
```

#### 10.4.3 Compiler la Table S0 (Docking Validation)

Le script `md_homology_mutants.py` ou les résultats de docking de Project 1 devraient contenir les données de redocking. Sinon :

```python
#!/usr/bin/env python3
"""generate_table_s0.py — Compiler la table de validation du docking"""

import pandas as pd

# Si les données de redocking existent dans Project 1 :
# redocking_data = pd.read_csv("../../../results/docking_validation.csv")

# Sinon, créer un template :
data = {
    "Target": ["PfDHFR", "PfCRT", "PfATP4", "PfClpP"],
    "PDB": ["7F3Y", "6UKJ", "9N10", "4GM2"],
    "Co-crystal ligand": ["PYR", "CQ", "CIP", "ADEP"],
    "RMSD (Å)": ["[à remplir]"] * 4,
    "ROC-AUC": ["[à remplir]"] * 4,
    "EF1%": ["[à remplir]"] * 4,
    "EF5%": ["[à remplir]"] * 4,
    "BEDROC": ["[à remplir]"] * 4,
}

df = pd.DataFrame(data)
df.to_csv("results/tables/table_s0_docking_validation.csv", index=False)
print("✓ Template Table S0 créé — à remplir avec les données de Project 1")
```

---

### 10.5 Nettoyer le dossier Tuto_MD_MC

#### 10.5.1 Option A — Déplacer vers une branche séparée (recommandée)

```bash
cd /home/taamangtchu/Documents/Github/Malaria_codes/Project2_Polypharmacology_MD_Validation

# Créer une branche pour les tutos
git checkout -b tutorials/md-mc-setup

# Déplacer le dossier
git mv Tuto_MD_MC/ tutorials/Tuto_MD_MC/

# Commit
git add -A
git commit -m "refactor: move tutorial files to separate branch"

# Revenir sur main
git checkout main
```

#### 10.5.2 Option B — Supprimer du repo principal

```bash
# Si les tutos ne sont plus nécessaires
git rm -r Tuto_MD_MC/
git commit -m "chore: remove temporary tutorial files (88 files)"
```

#### 10.5.3 Option C — Ajouter au .gitignore

```bash
# Ajouter au .gitignore
echo "Tuto_MD_MC/" >> .gitignore
git rm -r --cached Tuto_MD_MC/
git commit -m "chore: ignore Tuto_MD_MC directory"
```

---

### 10.6 Résoudre la cross-reference cassée

Dans `manuscript/LaTeX/Paper2_Draft_v0.6.tex`, remplacer L46 :

```latex
% Avant :
\externaldocument[P3-]{../../Quantum_Inspired_Representations/LaTeX/Paper3_Draft_v0.6}

% Après (solution robuste) :
\IfFileExists{../../Quantum_Inspired_Representations/LaTeX/Paper3_Draft_v0.6.aux}{%
  \externaldocument[P3-]{../../Quantum_Inspired_Representations/LaTeX/Paper3_Draft_v0.6}%
}{%
  \typeout{WARNING: Paper3 aux file not found - cross-references disabled}%
}
```

---

### 10.7 Nettoyer les fichiers désuets

```bash
cd /home/taamangtchu/Documents/Github/Malaria_codes/Project2_Polypharmacology_MD_Validation

# 1. Supprimer les fichiers de réorganisation désuets
git rm PROJECT_COMPLETION_SUMMARY.md
git rm REORGANIZATION_SUMMARY.md

# 2. Déplacer test_pymol.py
git mv test_pymol.py scripts/test_pymol.py

# 3. Supprimer la copie .txt redondante (si identique au .bib)
diff manuscript/LaTeX/Bibliography_Paper2.bib manuscript/LaTeX/Bibliography_Paper2.bib.txt
# Si identique :
git rm manuscript/LaTeX/Bibliography_Paper2.bib.txt

# 4. Déplacer Bibliography_Paper3.bib vers Paper 3
# (si Paper 3 existe dans le même workspace)
# git mv manuscript/LaTeX/Bibliography_Paper3.bib ../../Quantum_Inspired_Representations/LaTeX/

# 5. Déplacer les guides hors-scope
# git mv manuscript/LaTeX/HOW_TO_CITE_DD4GH.md ../../docs/
# git mv manuscript/LaTeX/USEFUL_RESOURCES_LIKE_DD4GH.md ../../docs/

git commit -m "chore: clean up obsolete files and reorganize"
```

---

### 10.8 Résoudre le problème de force field MC vs MD

#### 10.8.1 Option A — Utiliser CHARMM36m dans le MC (recommandé)

Modifier le script MC dans `docs/METHODS.md` :

```python
# Avant (L302) :
forcefield = app.ForceField('amber14-all.xml', 'amber14/tip3p.xml')

# Après :
forcefield = app.ForceField('charmm36.xml', 'charmm36/tip3p-pme-b.yaml')
```

**Attention** : OpenMM supporte CHARMM36 via les fichiers XML de la distribution OpenMM. Vérifier la disponibilité.

#### 10.8.2 Option B — Justifier le mismatch

Ajouter dans les Limitations :

```latex
\textbf{Monte Carlo force field mismatch.}
MC sampling used the AMBER14 force field (via OpenMM), while MD
simulations used CHARMM36m (via GROMACS). This choice reflects
software constraints (OpenMM's native AMBER support vs GROMACS'
CHARMM integration). To mitigate the resulting systematic offset,
we focus on relative rankings and MC/MD convergence metrics
rather than absolute binding free energies. A sensitivity test
using CHARMM36m in OpenMM is planned for future work.
```

---

### 10.9 Générer les 7 figures du manuscript

```python
#!/usr/bin/env python3
"""generate_all_figures.py — Générer les 7 figures du main text"""

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import numpy as np
import pandas as pd

OUTPUT = "results/figures"

def figure1_acsi_distribution():
    """F1: ACSI distribution for 65,856-molecule library."""
    # Charger les scores ACSI (une fois calculés)
    # acsi_scores = pd.read_csv("results/metrics/acsi_scores.csv")["acsi"]
    # plt.figure(figsize=(8, 5))
    # plt.hist(acsi_scores, bins=50, color='steelblue', edgecolor='black', alpha=0.7)
    # plt.axvline(x=0.5, color='red', linestyle='--', label='Mean threshold')
    # plt.xlabel('ACSI Score')
    # plt.ylabel('Count')
    # plt.title('African Chemical Space Index Distribution (n=65,856)')
    # plt.legend()
    # plt.tight_layout()
    # plt.savefig(f"{OUTPUT}/figure1_acsi_distribution.pdf", dpi=300)
    # plt.close()
    print("F1: ACSI distribution — en attente des calculs ACSI")

def figure2_ppi_network():
    """F2: P. falciparum PPI network with target highlighting."""
    print("F2: PPI network — en attente du calcul STRING + networkx")

def figure3_rmsd_stability():
    """F3: Representative RMSD trajectories (stable vs unstable)."""
    print("F3: RMSD stability — en attente des simulations MD")

def figure4_hbond_heatmap():
    """F4: H-bond occupancy heatmap for key residues."""
    print("F4: H-bond heatmap — en attente des simulations MD")

def figure5_mc_landscapes():
    """F5: MC binding free energy landscapes."""
    print("F5: MC landscapes — en attente du MC sampling")

def figure6_mc_poses():
    """F6: MC pose clustering."""
    print("F6: MC pose clusters — en attente du MC sampling")

def figure7_crossmetric():
    """F7: Cross-metric correlation matrix (RRS, ACSI, PNS, MM-GBSA)."""
    print("F7: Cross-metric — en attente de toutes les métriques")

if __name__ == "__main__":
    figure1_acsi_distribution()
    figure2_ppi_network()
    figure3_rmsd_stability()
    figure4_hbond_heatmap()
    figure5_mc_landscapes()
    figure6_mc_poses()
    figure7_crossmetric()
    print("\n=== Résumé ===")
    print("Toutes les figures nécessitent les résultats de simulation.")
    print("Priorité : lancer les simulations MD (Phase 5).")
```

---

### 10.10 Résumé des actions par échéancier

| Semaine | Action | Effort | Bloqué par |
|---------|--------|--------|------------|
| **S1 (7-13 juil.)** | Mettre à jour manuscript (chiffres + MC) | 2h | Aucun |
| **S1** | Corriger bibliographie (14 entrées fictives) | 3-4h | Aucun |
| **S1** | Créer arborescence results/ | 15min | Aucun |
| **S1** | Mettre à jour ROADMAP statuts | 1h | Aucun |
| **S2 (14-20 juil.)** | Nettoyer Tuto_MD_MC (déplacer/supprimer) | 30min | Aucun |
| **S2** | Supprimer fichiers désuets | 15min | Aucun |
| **S2** | Générer Figure S1 (MPO heatmap) | 1h | CSV déjà présent |
| **S2** | Compiler Table S0 (docking) | 2h | Données Project 1 |
| **S3-4 (21 juil.-3 août)** | Lancer MD WT (80 systèmes × 200 ns) | ~20 jours GPU | Allocation GPU |
| **Août** | Lancer MD mutants (120 × 100 ns) | ~15 jours GPU | WT terminés |
| **Sept** | MC sampling (220 × 10k steps) | ~3 jours GPU | MD terminés |
| **Oct** | Trajectory analysis + MM-GBSA | ~1 semaine | MC terminés |
| **Nov** | Calculer RRS, ACSI, PNS + figures | ~1 semaine | Toutes données |
| **Déc** | Rédiger Discussion + SI | ~2 semaines | Toutes données |
| **Jan 2027** | Review + soumission | ~2 semaines | Draft complet |

---

*Audit complet avec solutions — 4 juillet 2026.*
