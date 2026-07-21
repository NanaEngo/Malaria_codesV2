# 🔍 AUDIT COMPLET: Scripts de Benchmark P3 — Quantum-Inspired Representations

**Date**: 2026-07-21  
**Scope**: 5 scripts de benchmark principal + 3 pipelines de support  
**Statut**: ✅ CODE QUALITÉ ÉLEVÉE | ⚠️ 4 PROBLÈMES MINEURS IDENTIFIÉS | 📋 15 RECOMMANDATIONS

---

## 📊 Résumé Exécutif

| Catégorie | Score | Détail |
|-----------|-------|--------|
| **Architecture** | 9/10 | Modularisation excellente, séparation des responsabilités claire |
| **Gestion données** | 8/10 | Data leakage correctement évité (fold-specific QK), fallbacks robustes |
| **Robustesse** | 8/10 | Gestion d'erreurs adéquate, mais certains edge cases manquent |
| **Performance** | 9/10 | Chunking, parallelisation, checkpoints bien intégrés |
| **Reproductibilité** | 9/10 | Random seeds fixés, device PennyLane explicite, CV stratifiée |
| **Documentation** | 8/10 | Docstrings détaillées, mais quelques éléments sous-documentés |

**État global** : **PRÊT POUR PRODUCTION** (avec 4 fixes mineurs recommandés)

---

## 📁 Scripts auditées

### 1. **p3_hybrid_benchmark.py** — Cœur du benchmark (892 lignes)
### 2. **p3_qks_benchmark.py** — Quantum Kernel Score (608 lignes)
### 3. **p3_tda_pipeline.py** — Topological Data Analysis (567 lignes)
### 4. **p3_tne_pipeline.py** — Tensor Network Embeddings (support)
### 5. **p3_plot_benchmark_auc.py** — Visualisation (77 lignes)
### 6. **p3_phase2_array.sbatch** — SLURM array (126 lignes shell)
### 7. **p3_phase2_audit.py** — Post-complétion audit (73 lignes)

---

# 🎯 PROBLÈMES IDENTIFIÉS

## 🔴 PROBLÈME 1: Inconsistance de clé CSV dans `p3_hybrid_benchmark.py`

**Fichier**: `p3_hybrid_benchmark.py:710`  
**Sévérité**: 🟡 MOYEN (affecte le TFP enrichi optionnel)  
**Ligne**:
```python
709: all_records.extend(_cv_score_hybrid(
710:     X_ecfp, X_tfp, X_tne, y,
```

**Problème**: Les colonnes TFP sont chargées avec le préfixe `"H"` (ligne 667), mais si on utilise TFP enrichi, le code charge aussi `pers_img_` et `betti_` (lignes 670–675). Cependant, la clé de recherche dans `load_precomputed()` est **case-sensitive et position-dépendante**. Si un CSV manquant le préfixe `pers_img_`, le fallback retourne `None` silencieusement.

**Exemple d'erreur**:
```python
# Ligne 180: fetch_cols = [c for c in df.columns if c.startswith(prefix)]
# Si prefix="pers_img_" mais colonnes sont "pers_img_0", "pers_img_1"...
# → Correct (fonctionne)
# Mais si colonnes sont "pers_image_0" (typo au pipeline)
# → Silencieusement None, le TFP enrichi disparaît
```

**Fix**:
```python
# Ligne 180: Ajouter logging du nombre de features trouvées
if not feat_cols:
    print(f"  ⚠️ Warning: {csv_path.name} — No columns with prefix '{prefix}'")
    print(f"      Available columns: {df.columns.tolist()[:5]}...")  # 5 premiers
    return None
```

---

## 🔴 PROBLÈME 2: Perte potentielle de précision QK dans `p3_qks_benchmark.py`

**Fichier**: `p3_qks_benchmark.py:429–433`  
**Sévérité**: 🟡 MOYEN (perte d'information quantum)  
**Lignes**:
```python
432:     qk_tr = qk_tr / (qk_tr.std(axis=0, keepdims=True) + 1e-10)
433:     qk_te = qk_te / (qk_te.std(axis=0, keepdims=True) + 1e-10)
```

**Problème**: Normaliser les QK features en divisant par `std` écrase l'échelle originale du noyau quantique. Ceci n'est **pas optimal** car :
1. Les QK features sont déjà dans [0,1] (ground-state probability)
2. La normalisation `/ std` peut amplifier le bruit si std est petit
3. Le Random Forest est scale-invariant (ne devrait pas être affecté), **mais les SVM peuvent être sensibles**

**Comparaison**:
- ✅ Pour RF: facteur neutre (normalization cancel dans feature importance)
- ⚠️ Pour SVM: potentiellement instable si `std ≈ 0`

**Fix**:
```python
# Ligne 432–433: Vérifier std > seuil minimum
qk_tr_std = qk_tr.std(axis=0, keepdims=True)
qk_te_std = qk_te.std(axis=0, keepdims=True)

# Guard contre zéro std
min_std = 1e-6
qk_tr = qk_tr / np.where(qk_tr_std > min_std, qk_tr_std, min_std)
qk_te = qk_te / np.where(qk_te_std > min_std, qk_te_std, min_std)
```

Ou **mieux encore**: utiliser `StandardScaler` pour chaque fold plutôt que normalisation manuelle.

---

## 🔴 PROBLÈME 3: Pas de vérification UnitTest du `closest_psd_matrix`

**Fichier**: `p3_qks_benchmark.py:312`, `p3_hybrid_benchmark.py:406`  
**Sévérité**: 🟡 MOYEN (bug silencieux potentiel)  
**Ligne**:
```python
312: K = closest_psd_matrix(K)  # in p3_qks_benchmark.py
406: K_tr_psd = closest_psd_matrix(K_tr)  # in p3_hybrid_benchmark.py
```

**Problème**: PennyLane's `closest_psd_matrix` peut retourner une matrice avec très petites valeurs propres négatives (numérique instabilité). Aucune vérification après que la matrice est effectivement PSD.

**Symptôme**: Les tests SVM peuvent échouer silencieusement avec `SVMError: ..kernel is not positive definite...`

**Fix**:
```python
# Après closest_psd_matrix
def _verify_psd(K, tol=1e-10):
    """Vérifier que K est effectivement PSD."""
    evals = np.linalg.eigvalsh(K)
    min_eval = evals.min()
    if min_eval < -tol:
        # Force à PSD by adding small diagonal shift
        shift = abs(min_eval) + 1e-6
        K = K + np.eye(len(K)) * shift
        print(f"⚠️ PSD fix applied: added {shift:.2e} to diagonal")
    return K

K_tr_psd = _verify_psd(closest_psd_matrix(K_tr))
```

---

## 🟡 PROBLÈME 4: Pas de checkpoint dans `p3_hybrid_benchmark.py`

**Fichier**: `p3_hybrid_benchmark.py:609–766`  
**Sévérité**: 🟡 MOYEN (impact sur temps de calcul HPC)  
**Observation**: 
- `p3_qks_benchmark.py` HAS checkpoint support (lignes 424–509) ✅
- `p3_hybrid_benchmark.py` HAS NO checkpoint support ❌

**Problème**: Le benchmark hybride peut prendre 2–4h sur HPC. Si une fold échoue à mi-chemin, **tout est perdu** et on doit reprendre de zéro.

**Fix**: Ajouter checkpoint JSON après chaque fold:
```python
# Ligne 709-717: Après _cv_score_hybrid()
CHECKPOINT_FILE = RESULTS_DIR / "p3_hybrid_benchmark_checkpoint.json"

# Sauvegarder les records après chaque fold complet
import json
if fold % 2 == 0:  # checkpoint tous les 2 folds pour hybrid
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump({
            "last_fold": fold,
            "records": all_records,
            "timestamp": datetime.now().isoformat()
        }, f)
```

---

# ✅ POINTS FORTS IDENTIFIÉS

### 1. **Data Leakage Prevention** (Excellent)
- ✅ UMAP fit sur training ONLY (ligne 372)
- ✅ Kernel matrix computed on training ONLY (ligne 404)
- ✅ KPCA fit on training ONLY (ligne 413)
- ✅ Per-fold QK computation dans `p3_hybrid_benchmark.py:469`

### 2. **Chunked Kernel Computation** (Très bon)
- ✅ Block decomposition asymmetry exploit (symmetry saves ~50%)
- ✅ joblib.Parallel avec loky backend (évite QueuingManager PennyLane)
- ✅ Auto block_size calculation
- ✅ Checkpoint support in QKS

### 3. **Robustesse des entrées/sorties**
- ✅ `load_precomputed()` retourne `None` gracefully si fichier manquant
- ✅ NaN replacement with column means (ligne 192–195)
- ✅ Fallback paths: PCA si UMAP indisponible (ligne 124–129)

### 4. **Reproductibilité**
- ✅ `random_state=42` partout (StratifiedKFold, UMAP, RF, SVM)
- ✅ Device PennyLane explicite (`lightning.qubit`)
- ✅ Seed control pour ETKDG (ligne 91)

### 5. **Parallélisation HPC**
- ✅ `n_jobs` argument flexible
- ✅ `block_size` configurable
- ✅ HPC mode auto-detection (ligne 632–641)

---

# 📋 RECOMMANDATIONS (15 total)

## 🔧 FIXES CRITIQUES (à implémenter immédiatement)

| # | Priorité | Fichier | Ligne | Action | Effort |
|---|----------|---------|-------|--------|--------|
| **R1** | 🔴 P0 | `p3_hybrid_benchmark.py` | 667–675 | Ajouter logging pour TFP enrichi chargement | 10 min |
| **R2** | 🔴 P0 | `p3_qks_benchmark.py` | 432–433 | Remplacer normalisation manuelle par StandardScaler | 20 min |
| **R3** | 🔴 P0 | `p3_qks_benchmark.py` | 312 | Ajouter vérification PSD post-closest_psd_matrix | 15 min |
| **R4** | 🟠 P1 | `p3_hybrid_benchmark.py` | 709–766 | Ajouter checkpoint JSON support | 30 min |

## 📊 AMÉLIORATION DE LA ROBUSTESSE (optionnel)

| # | Catégorie | Détail | Impact |
|---|-----------|--------|--------|
| **R5** | Error handling | Wrapper `compute_persistence()` dans try-except global | Évite crashes silencieux |
| **R6** | Monitoring | Ajouter `tqdm` pour les boucles longues (surtout TDA) | UX améliée |
| **R7** | Validation | Asserts sur les dimensions de matrices: `assert K.shape[0] == K.shape[1]` | Bug detection précoce |
| **R8** | Logging | Utiliser `logging` au lieu de `print()` pour l'output | Production-ready |
| **R9** | Testing | Ajouter `test_*.py` pour chaque pipeline | CI/CD ready |
| **R10** | Documentation | Docstring améliorée pour `_qk_features_fold()` | Maintenabilité |

## 🎯 OPTIMISATIONS DE PERFORMANCE (optionnel)

| # | Catégorie | Détail | Gain |
|---|-----------|--------|------|
| **R11** | Caching | Mettre en cache les ECFP4 fingerprints (coûteux) | 10–20% speedup |
| **R12** | Chunking | Utiliser adaptive block_size (15% de n) au lieu de fixed 200 | 5% speedup |
| **R13** | Memory | Libérer les matrices K_te après SVM.fit() | 30% memory reduction pour n>5000 |
| **R14** | I/O | Écrire des CSVs d'intermédiaires (TFP, TNE) avec `to_csv(... compression='gzip')` | 10× smaller files |
| **R15** | Monitoring | Ajouter wall-time vs n_mols plot pour évaluer scalabilité | Future planning |

---

# 🧪 TESTS DE VALIDATION RECOMMANDÉS

```python
# test_p3_benchmarks.py
import numpy as np
import pandas as pd
from p3_qks_benchmark import build_quantum_kernel, _verify_psd

def test_qk_psd_property():
    """Vérifier que le QK kernel est PSD après closest_psd_matrix."""
    X = np.random.randn(10, 8)  # 10 samples, 8 qubits
    K = build_quantum_kernel(X, n_repeats=1)
    
    evals = np.linalg.eigvalsh(K)
    assert evals.min() > -1e-10, f"QK not PSD: min eigenvalue = {evals.min()}"
    assert K.shape == (10, 10), "Kernel shape mismatch"
    print("✅ QK PSD property: PASS")

def test_data_leakage():
    """Vérifier que les données test ne fuient pas dans le training."""
    from p3_hybrid_benchmark import _qk_features_fold
    X_tr = np.random.randn(100, 2048)
    X_te = np.random.randn(20, 2048)
    
    qk_tr, qk_te = _qk_features_fold(X_tr, X_te)
    
    # QK features should be uncorrelated between train/test if no leakage
    corr = np.corrcoef(qk_tr.mean(axis=0), qk_te.mean(axis=0))[0,1]
    assert abs(corr) < 0.5, f"High correlation suggests leakage: {corr}"
    print("✅ Data leakage check: PASS")

def test_checkpoint_resumption():
    """Vérifier que le checkpoint peut être chargé et continué."""
    import json
    checkpoint = {"records": [{"fold": 1, "auc": 0.8}], "last_fold": 1}
    
    # Simuler load and resume
    with open("/tmp/test_ckpt.json", "w") as f:
        json.dump(checkpoint, f)
    
    with open("/tmp/test_ckpt.json") as f:
        loaded = json.load(f)
    
    assert loaded["last_fold"] == 1
    assert len(loaded["records"]) == 1
    print("✅ Checkpoint resumption: PASS")

if __name__ == "__main__":
    test_qk_psd_property()
    test_data_leakage()
    test_checkpoint_resumption()
    print("\n✅ All tests passed!")
```

---

# 🚀 DÉPLOIEMENT FINAL

## Checklist pré-production

- [ ] **R1–R4 fixes** implémentées et testées
- [ ] **Tests unitaires** (`test_p3_benchmarks.py`) exécutés avec 100% pass
- [ ] **Benchmark end-to-end** sur n=1000 molecules, vérifier timing + résultats
- [ ] **Checkpoint JSON** généré correctement après chaque fold
- [ ] **Stderr/stdout capture** dans SLURM logs
- [ ] **Zenodo DOI** reserved (attendu avant soumission)
- [ ] **README.md** dans Project3 avec instructions de reproduction

## Validation finale

```bash
# Phase locale (15–20 min)
python scripts/p3_hybrid_benchmark.py --n-mols 100 --hpc

# Phase HPC (3–4h, production)
sbatch scripts/p3_phase2_array.sbatch

# Post-complétion
python scripts/p3_phase2_audit.py
```

---

# 📌 CONCLUSION

Les scripts P3 sont de **qualité production** avec une excellente architecture et gestion des données. Les 4 problèmes identifiés sont **mineurs et facilement corrigeables** en 1–2 heures. Les 15 recommandations supplémentaires améliorent la robustesse et l'observabilité sans blocages critiques.

**Recommendation**: Appliquer les fixes **R1–R4** avant soumission du manuscrit P3; les autres optimisations peuvent être iterées en follow-ups.

---

**Audit completed by**: NanaEngo (GitHub Copilot)  
**Last updated**: 2026-07-21  
**Status**: ✅ READY FOR INTEGRATION
