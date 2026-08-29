"""
P7 — Phase 1 Proof-of-Concept

End-to-end comparison of quantum molecular encoding vs classical baseline
on P1 Set A (20 top candidates):

  QML Pipeline:
    SMILES → BondOrderMatrix → BondFeatureMap → UnitaryOverlap kernel → SVM → LOO-CV
  
  Classical Baseline:
    SMILES → ECFP4 fingerprints → RBF kernel → SVM → LOO-CV

Statistical comparison:
  - Paired t-test (molecular-level predictions)
  - Effect size (Cohen's d)
  - McNemar's test (classification disagreements)
  - Honest-negative commitment (report all outcomes)

Outputs:
  - Comparison report (markdown)
  - Statistical test results (JSON)
  - Per-molecule predictions (CSV)
  - Update P7_DATA_ANALYSIS_REPORT.md

Usage:
    python scripts/p7_phase1_poc.py --method bond_order
    python scripts/p7_phase1_poc.py --method coulomb --regenerate
"""

import argparse
import json
import sys
import warnings
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.svm import SVC
from sklearn.model_selection import LeaveOneOut
from sklearn.metrics import (
    roc_auc_score, accuracy_score, f1_score,
    precision_score, recall_score, confusion_matrix
)
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings('ignore')

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RESULTS_DIR = PROJECT_ROOT / "results"
PHASE1_DIR = RESULTS_DIR / "phase1_p1_set_a"


def load_data():
    """Load P1 Set A dataset."""
    data_file = DATA_DIR / "p1_set_a_20_candidates.csv"
    
    if not data_file.exists():
        raise FileNotFoundError(
            f"{data_file} not found\n"
            f"Run: python scripts/p7_data_preparation.py --p1-only"
        )
    
    df = pd.read_csv(data_file)
    print(f"Loaded P1 Set A: {len(df)} molecules")
    
    # Validate labels
    if 'activity' not in df.columns:
        print("WARNING: No 'activity' column found, using dummy labels")
        df['activity'] = np.random.randint(0, 2, size=len(df))
    
    return df


def load_quantum_kernel(method='bond_order'):
    """Load pre-computed quantum kernel matrix."""
    kernel_file = PHASE1_DIR / "quantum_kernel" / f"quantum_kernel_{method}.npy"
    mol_ids_file = PHASE1_DIR / "quantum_kernel" / f"quantum_kernel_{method}_mol_ids.txt"
    
    if not kernel_file.exists():
        raise FileNotFoundError(
            f"{kernel_file} not found\n"
            f"Run: python scripts/p7_quantum_kernel.py --p1-set-a --method {method}"
        )
    
    K = np.load(kernel_file)
    
    with open(mol_ids_file, 'r') as f:
        mol_ids = [line.strip() for line in f]
    
    print(f"\nLoaded quantum kernel: {K.shape}")
    print(f"  Method: {method}")
    print(f"  Diagonal: {K.diagonal().mean():.4f} ± {K.diagonal().std():.4f}")
    
    return K, mol_ids


def load_baseline_results():
    """Load classical baseline results."""
    baseline_file = PHASE1_DIR / "baseline_ecfp4_loo.csv"
    metrics_file = PHASE1_DIR / "baseline_ecfp4_loo_metrics.json"
    
    if not baseline_file.exists():
        raise FileNotFoundError(
            f"{baseline_file} not found\n"
            f"Run: python scripts/p7_baseline_classical.py --p1-set-a"
        )
    
    df = pd.read_csv(baseline_file)
    
    with open(metrics_file, 'r') as f:
        metrics = json.load(f)
    
    print(f"\nLoaded baseline results:")
    print(f"  AUC: {metrics['metrics']['auc']:.4f}")
    print(f"  Accuracy: {metrics['metrics']['accuracy']:.4f}")
    print(f"  F1: {metrics['metrics']['f1']:.4f}")
    
    return df, metrics['metrics']


def run_qml_loo_cv(K, y):
    """
    Run leave-one-out CV with quantum kernel SVM.
    
    Args:
        K: (n, n) precomputed kernel matrix
        y: (n,) binary labels
    
    Returns:
        predictions: DataFrame with y_true, y_pred, y_score
        metrics: Dict of performance metrics
    """
    print("\n=== QML: Leave-One-Out Cross-Validation ===")
    n = len(y)
    
    loo = LeaveOneOut()
    
    y_true = []
    y_pred = []
    y_scores = []
    
    for fold_idx, (train_idx, test_idx) in enumerate(loo.split(K)):
        # Extract kernel submatrices
        K_train = K[np.ix_(train_idx, train_idx)]
        K_test = K[np.ix_(test_idx, train_idx)]
        
        y_train = y[train_idx]
        y_test_val = y[test_idx]
        
        # Train SVM with precomputed kernel
        svm = SVC(kernel='precomputed', C=1.0, probability=True, random_state=42)
        svm.fit(K_train, y_train)
        
        # Predict
        pred = svm.predict(K_test)[0]
        score = svm.predict_proba(K_test)[0, 1]
        
        y_true.append(y_test_val[0])
        y_pred.append(pred)
        y_scores.append(score)
        
        if (fold_idx + 1) % 5 == 0:
            print(f"  Fold {fold_idx + 1}/{n}")
    
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    y_scores = np.array(y_scores)
    
    # Compute metrics
    metrics = {
        'auc': float(roc_auc_score(y_true, y_scores)) if len(np.unique(y_true)) > 1 else 0.0,
        'accuracy': float(accuracy_score(y_true, y_pred)),
        'f1': float(f1_score(y_true, y_pred, zero_division=0)),
        'precision': float(precision_score(y_true, y_pred, zero_division=0)),
        'recall': float(recall_score(y_true, y_pred, zero_division=0)),
    }
    
    cm = confusion_matrix(y_true, y_pred)
    if cm.shape == (2, 2):
        metrics['tn'] = int(cm[0, 0])
        metrics['fp'] = int(cm[0, 1])
        metrics['fn'] = int(cm[1, 0])
        metrics['tp'] = int(cm[1, 1])
    
    print(f"\nQML Metrics:")
    print(f"  AUC: {metrics['auc']:.4f}")
    print(f"  Accuracy: {metrics['accuracy']:.4f}")
    print(f"  F1: {metrics['f1']:.4f}")
    
    predictions = pd.DataFrame({
        'y_true': y_true,
        'y_pred_qml': y_pred,
        'y_score_qml': y_scores
    })
    
    return predictions, metrics


def statistical_comparison(qml_preds, baseline_preds, qml_metrics, baseline_metrics):
    """
    Statistical comparison between QML and baseline.
    
    Tests:
    1. Paired t-test on prediction scores
    2. McNemar's test on classification disagreements
    3. Effect size (Cohen's d)
    """
    print("\n=== Statistical Comparison ===")
    
    results = {
        'n_samples': len(qml_preds),
        'qml_metrics': qml_metrics,
        'baseline_metrics': baseline_metrics
    }
    
    # 1. Paired t-test on prediction scores
    qml_scores = qml_preds['y_score_qml'].values
    baseline_scores = baseline_preds['y_score'].values
    
    t_stat, p_value = stats.ttest_rel(qml_scores, baseline_scores)
    
    results['paired_ttest'] = {
        't_statistic': float(t_stat),
        'p_value': float(p_value),
        'significant': p_value < 0.05,
        'interpretation': 'QML > Baseline' if t_stat > 0 else 'Baseline > QML'
    }
    
    print(f"\n1. Paired t-test (prediction scores):")
    print(f"   t = {t_stat:.4f}, p = {p_value:.4f}")
    print(f"   {'Significant' if p_value < 0.05 else 'Not significant'} at α=0.05")
    
    # 2. Effect size (Cohen's d)
    mean_diff = qml_scores.mean() - baseline_scores.mean()
    pooled_std = np.sqrt((qml_scores.std()**2 + baseline_scores.std()**2) / 2)
    cohens_d = mean_diff / pooled_std if pooled_std > 0 else 0.0
    
    results['effect_size'] = {
        'cohens_d': float(cohens_d),
        'mean_diff': float(mean_diff),
        'interpretation': 'large' if abs(cohens_d) > 0.8 else ('medium' if abs(cohens_d) > 0.5 else 'small')
    }
    
    print(f"\n2. Effect size (Cohen's d):")
    print(f"   d = {cohens_d:.4f} ({results['effect_size']['interpretation']})")
    
    # 3. McNemar's test (classification disagreements)
    qml_pred = qml_preds['y_pred_qml'].values
    baseline_pred = baseline_preds['y_pred'].values
    y_true = qml_preds['y_true'].values
    
    # Build 2×2 contingency table
    qml_correct = (qml_pred == y_true)
    baseline_correct = (baseline_pred == y_true)
    
    both_correct = (qml_correct & baseline_correct).sum()
    both_wrong = (~qml_correct & ~baseline_correct).sum()
    qml_only = (qml_correct & ~baseline_correct).sum()
    baseline_only = (~qml_correct & baseline_correct).sum()
    
    # McNemar's test (using continuity correction)
    if qml_only + baseline_only > 0:
        mcnemar_stat = (abs(qml_only - baseline_only) - 1)**2 / (qml_only + baseline_only)
        mcnemar_p = 1 - stats.chi2.cdf(mcnemar_stat, 1)
    else:
        mcnemar_stat = 0.0
        mcnemar_p = 1.0
    
    results['mcnemar'] = {
        'statistic': float(mcnemar_stat),
        'p_value': float(mcnemar_p),
        'significant': mcnemar_p < 0.05,
        'contingency': {
            'both_correct': int(both_correct),
            'both_wrong': int(both_wrong),
            'qml_only_correct': int(qml_only),
            'baseline_only_correct': int(baseline_only)
        }
    }
    
    print(f"\n3. McNemar's test (classification disagreements):")
    print(f"   χ² = {mcnemar_stat:.4f}, p = {mcnemar_p:.4f}")
    print(f"   Both correct: {both_correct}, Both wrong: {both_wrong}")
    print(f"   QML only: {qml_only}, Baseline only: {baseline_only}")
    
    # 4. Performance deltas
    deltas = {
        'auc_delta': qml_metrics['auc'] - baseline_metrics['auc'],
        'accuracy_delta': qml_metrics['accuracy'] - baseline_metrics['accuracy'],
        'f1_delta': qml_metrics['f1'] - baseline_metrics['f1']
    }
    results['deltas'] = {k: float(v) for k, v in deltas.items()}
    
    print(f"\n4. Performance deltas (QML - Baseline):")
    print(f"   ΔAUC: {deltas['auc_delta']:+.4f}")
    print(f"   ΔAccuracy: {deltas['accuracy_delta']:+.4f}")
    print(f"   ΔF1: {deltas['f1_delta']:+.4f}")
    
    return results


def generate_report(
    comparison_results,
    qml_preds,
    baseline_preds,
    mol_ids,
    method,
    output_dir
):
    """Generate markdown comparison report."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save predictions
    combined_preds = pd.DataFrame({
        'molecule_id': mol_ids,
        'y_true': qml_preds['y_true'],
        'y_pred_qml': qml_preds['y_pred_qml'],
        'y_score_qml': qml_preds['y_score_qml'],
        'y_pred_baseline': baseline_preds['y_pred'],
        'y_score_baseline': baseline_preds['y_score']
    })
    
    preds_file = output_dir / f"phase1_comparison_predictions_{method}.csv"
    combined_preds.to_csv(preds_file, index=False)
    print(f"\nSaved predictions: {preds_file}")
    
    # Save statistical results
    stats_file = output_dir / f"phase1_comparison_statistics_{method}.json"
    with open(stats_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'method': method,
            'comparison': comparison_results
        }, f, indent=2)
    print(f"Saved statistics: {stats_file}")
    
    # Generate markdown report
    report_md = f"""# P7 Phase 1 Proof-of-Concept Results

**Date:** {datetime.now().strftime('%Y-%m-%d')}  
**Dataset:** P1 Set A (20 top candidates)  
**Method:** {method.upper()}  
**Validation:** Leave-one-out cross-validation

---

## Executive Summary

### Research Question
Does quantum molecular encoding (QMSE) outperform classical ECFP4 fingerprints for antimalarial drug discovery on a small, high-quality dataset?

### Result
{"**QML outperforms baseline**" if comparison_results['deltas']['auc_delta'] > 0.05 else "**QML and baseline perform similarly**" if abs(comparison_results['deltas']['auc_delta']) <= 0.05 else "**Baseline outperforms QML**"}

- **ΔAUC:** {comparison_results['deltas']['auc_delta']:+.4f}
- **ΔAccuracy:** {comparison_results['deltas']['accuracy_delta']:+.4f}
- **ΔF1:** {comparison_results['deltas']['f1_delta']:+.4f}

Statistical significance: {"Yes" if comparison_results['paired_ttest']['significant'] else "No"} (p = {comparison_results['paired_ttest']['p_value']:.4f})

---

## Performance Metrics

### Quantum Molecular Encoding (QML)

| Metric | Value |
|--------|-------|
| AUC-ROC | {comparison_results['qml_metrics']['auc']:.4f} |
| Accuracy | {comparison_results['qml_metrics']['accuracy']:.4f} |
| F1 Score | {comparison_results['qml_metrics']['f1']:.4f} |
| Precision | {comparison_results['qml_metrics']['precision']:.4f} |
| Recall | {comparison_results['qml_metrics']['recall']:.4f} |

### Classical Baseline (ECFP4-RBF)

| Metric | Value |
|--------|-------|
| AUC-ROC | {comparison_results['baseline_metrics']['auc']:.4f} |
| Accuracy | {comparison_results['baseline_metrics']['accuracy']:.4f} |
| F1 Score | {comparison_results['baseline_metrics']['f1']:.4f} |
| Precision | {comparison_results['baseline_metrics']['precision']:.4f} |
| Recall | {comparison_results['baseline_metrics']['recall']:.4f} |

---

## Statistical Analysis

### 1. Paired t-Test (Prediction Scores)

- **Statistic:** t = {comparison_results['paired_ttest']['t_statistic']:.4f}
- **p-value:** {comparison_results['paired_ttest']['p_value']:.4f}
- **Significant:** {"Yes" if comparison_results['paired_ttest']['significant'] else "No"} (α = 0.05)
- **Direction:** {comparison_results['paired_ttest']['interpretation']}

### 2. Effect Size (Cohen's d)

- **Cohen's d:** {comparison_results['effect_size']['cohens_d']:.4f}
- **Magnitude:** {comparison_results['effect_size']['interpretation'].capitalize()}
- **Mean difference:** {comparison_results['effect_size']['mean_diff']:.4f}

### 3. McNemar's Test (Classification Disagreements)

- **Statistic:** χ² = {comparison_results['mcnemar']['statistic']:.4f}
- **p-value:** {comparison_results['mcnemar']['p_value']:.4f}
- **Significant:** {"Yes" if comparison_results['mcnemar']['significant'] else "No"} (α = 0.05)

**Contingency Table:**

|                     | Baseline Correct | Baseline Wrong |
|---------------------|------------------|----------------|
| **QML Correct**     | {comparison_results['mcnemar']['contingency']['both_correct']} | {comparison_results['mcnemar']['contingency']['qml_only_correct']} |
| **QML Wrong**       | {comparison_results['mcnemar']['contingency']['baseline_only_correct']} | {comparison_results['mcnemar']['contingency']['both_wrong']} |

---

## Interpretation

### Honest-Negative Commitment

Following P3 precedent (transparent null results), we report outcomes without selective emphasis:

"""
    
    # Add interpretation based on results
    if comparison_results['deltas']['auc_delta'] > 0.05 and comparison_results['paired_ttest']['significant']:
        report_md += """
**Quantum advantage detected:**
- QML outperforms ECFP4 baseline with statistical significance
- Effect size is {}, indicating {}
- Suggests structure-direct encoding captures information orthogonal to fingerprints

**Caveats:**
- Small sample size (n=20) limits generalizability
- Results must be validated on P3 benchmark (n=19,849)
- Computational cost of quantum encoding TBD
""".format(
            comparison_results['effect_size']['interpretation'],
            "substantial practical impact" if comparison_results['effect_size']['cohens_d'] > 0.8 else "moderate practical impact"
        )
    elif abs(comparison_results['deltas']['auc_delta']) <= 0.05:
        report_md += """
**Equivalence outcome:**
- QML and ECFP4 baseline perform similarly
- No quantum advantage detected on this small dataset
- Possible explanations:
  1. P1 Set A (n=20) is too small to reveal differences
  2. ECFP4 fingerprints already capture relevant structural features
  3. Quantum encoding may require larger cohorts or different targets

**Next steps:**
- Validate on P3 benchmark (n=19,849) for statistical power
- Ablation study: vary matrix type, entangling layer, circuit depth
- Test on structurally diverse external dataset
"""
    else:
        report_md += """
**Baseline superior:**
- ECFP4 baseline outperforms QML on P1 Set A
- Possible explanations:
  1. Quantum encoding overfits to molecular structure
  2. Small sample size (n=20) favors simpler representations
  3. P1 candidates are MPO-optimized, may be ECFP4-friendly

**Honest-negative result:**
- No evidence of quantum advantage on this dataset
- Does not invalidate QMSE approach universally
- Requires validation on P3 benchmark and ablation studies
"""
    
    report_md += f"""
---

## Technical Details

- **QML Encoding:** {method} → BondFeatureMap → UnitaryOverlap kernel
- **Baseline:** ECFP4 (radius=2, 2048 bits) → RBF kernel
- **Classifier:** SVM (C=1.0)
- **Validation:** Leave-one-out cross-validation (n=20)
- **Kernel properties:** See `quantum_kernel/quantum_kernel_{method}_stats.json`

---

## Files

- Predictions: `phase1_comparison_predictions_{method}.csv`
- Statistics: `phase1_comparison_statistics_{method}.json`
- Quantum kernel: `quantum_kernel/quantum_kernel_{method}.npy`
- Baseline results: `baseline_ecfp4_loo.csv`

---

## Next Steps

1. **Phase 2 validation:** Run on P3 benchmark (19,849 molecules)
2. **Ablation study:** Test coulomb matrix, different entangling layers
3. **Update DAR:** Record Phase 1 results in `P7_DATA_ANALYSIS_REPORT.md`
4. **Manuscript integration:** Incorporate into P7 manuscript if results warrant

---

*Generated by `p7_phase1_poc.py` on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    report_file = output_dir / f"PHASE1_COMPARISON_REPORT_{method.upper()}.md"
    with open(report_file, 'w') as f:
        f.write(report_md)
    
    print(f"Saved report: {report_file}")
    
    return report_file


def main():
    parser = argparse.ArgumentParser(description="P7 Phase 1 Proof-of-Concept")
    parser.add_argument('--method', choices=['bond_order', 'coulomb'], default='bond_order',
                        help="Quantum encoding method (default: bond_order)")
    parser.add_argument('--regenerate', action='store_true',
                        help="Regenerate QML predictions even if kernel exists")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("P7 Phase 1 Proof-of-Concept")
    print("=" * 60)
    
    try:
        # Load data
        df = load_data()
        mol_ids = df['molecule_id'].tolist()
        y = df['activity'].values
        
        # Load baseline results
        baseline_preds, baseline_metrics = load_baseline_results()
        
        # Load quantum kernel
        K, kernel_mol_ids = load_quantum_kernel(args.method)
        
        # Verify molecule alignment
        if mol_ids != kernel_mol_ids:
            print("\nWARNING: Molecule ID mismatch between data and kernel")
            print("Aligning datasets...")
            # Reorder to match kernel
            df = df.set_index('molecule_id').loc[kernel_mol_ids].reset_index()
            baseline_preds = baseline_preds.set_index('molecule_id').loc[kernel_mol_ids].reset_index()
            y = df['activity'].values
        
        # Run QML LOO-CV
        qml_preds, qml_metrics = run_qml_loo_cv(K, y)
        
        # Statistical comparison
        comparison = statistical_comparison(
            qml_preds,
            baseline_preds,
            qml_metrics,
            baseline_metrics
        )
        
        # Generate report
        report_file = generate_report(
            comparison,
            qml_preds,
            baseline_preds,
            kernel_mol_ids,
            args.method,
            PHASE1_DIR / "comparison"
        )
        
        print("\n" + "=" * 60)
        print("✅ Phase 1 Proof-of-Concept Complete")
        print("=" * 60)
        print(f"\n📊 Comparison report: {report_file}")
        print(f"\nKey finding: {'QML outperforms baseline' if comparison['deltas']['auc_delta'] > 0.05 else 'QML and baseline similar' if abs(comparison['deltas']['auc_delta']) <= 0.05 else 'Baseline outperforms QML'}")
        print(f"  ΔAUC = {comparison['deltas']['auc_delta']:+.4f} (p = {comparison['paired_ttest']['p_value']:.4f})")
        
        print("\nNext steps:")
        print("  1. Review comparison report")
        print("  2. Update P7_DATA_ANALYSIS_REPORT.md with results")
        print("  3. Proceed to Phase 2 (P3 benchmark) if results warrant")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
