#!/usr/bin/env python3
"""
H1 Persistence vs. RRS Class Analysis (Cross-Paper P3 × P2)
Computes TFP H1 features on the 17 polypharm compounds and generates
violin plots split by RRS class (A vs. C/D), as planned in §4.7 of Paper 3.

Output:
    - results/figures/h1_rrs_class_violin.png  (300 DPI, publication quality)
    - results/p3_polypharm_tfp_rrs.csv          (data table)
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import warnings
warnings.filterwarnings('ignore')

from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem import rdMolDescriptors
import ripser
from scipy.spatial.distance import cdist
import os

# ─── Paths ───────────────────────────────────────────────────────────────────
BASE   = os.path.dirname(os.path.abspath(__file__))
PROJ2  = os.path.join(BASE, '..', '..', 'Project2_Polypharmacology_MD_ValidationV2607')
RRS_CSV = os.path.join(PROJ2, 'results', 'c_rrs_classification.csv')
OUT_DIR = os.path.join(BASE, '..', '..', 'Project2_Polypharmacology_MD_ValidationV2607', 'results', 'figures')
OUT_CSV = os.path.join(PROJ2, 'results', 'p3_polypharm_tfp_rrs.csv')
os.makedirs(OUT_DIR, exist_ok=True)

# ─── TFP computation ──────────────────────────────────────────────────────────
def mol_to_point_cloud(mol):
    """Generate 3D conformer and return atomic coordinates."""
    mol = Chem.AddHs(mol)
    params = AllChem.ETKDGv3()
    params.randomSeed = 42
    AllChem.EmbedMolecule(mol, params)
    try:
        AllChem.MMFFOptimizeMolecule(mol)
    except Exception:
        pass
    conf = mol.GetConformer()
    coords = np.array([list(conf.GetAtomPosition(i))
                       for i in range(mol.GetNumAtoms())])
    return coords

def compute_tfp(smiles):
    """Compute TFP H0/H1 persistence features from SMILES."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    try:
        coords = mol_to_point_cloud(mol)
        dgms = ripser.ripser(coords, maxdim=1)['dgms']
        # H0 features
        h0 = dgms[0]
        h0_finite = h0[h0[:, 1] < np.inf]
        h0_count = len(h0_finite)
        h0_mean_lifetime = float(np.mean(h0_finite[:, 1] - h0_finite[:, 0])) if len(h0_finite) > 0 else 0.0
        h0_max_lifetime = float(np.max(h0_finite[:, 1] - h0_finite[:, 0])) if len(h0_finite) > 0 else 0.0

        # H1 features
        h1 = dgms[1]
        h1_count = len(h1)
        if h1_count > 0:
            lifetimes = h1[:, 1] - h1[:, 0]
            h1_mean_lifetime = float(np.mean(lifetimes))
            h1_max_lifetime  = float(np.max(lifetimes))
            h1_total_persistence = float(np.sum(lifetimes))
        else:
            h1_mean_lifetime = 0.0
            h1_max_lifetime  = 0.0
            h1_total_persistence = 0.0

        return {
            'h0_count': h0_count,
            'h0_mean_lifetime': h0_mean_lifetime,
            'h0_max_lifetime': h0_max_lifetime,
            'h1_count': h1_count,
            'h1_mean_lifetime': h1_mean_lifetime,
            'h1_max_lifetime': h1_max_lifetime,
            'h1_total_persistence': h1_total_persistence,
        }
    except Exception as e:
        print(f"  TFP error: {e}")
        return None

# ─── Load RRS data ─────────────────────────────────────────────────────────────
print("Loading RRS classification data...")
rrs_df = pd.read_csv(RRS_CSV)
print(f"  Loaded {len(rrs_df)} compounds. Classes: {rrs_df['RRS_class'].value_counts().to_dict()}")

# ─── Compute TFP for all polypharm compounds ───────────────────────────────────
print("Computing TFP features (3D conformers via ETKDGv3 + MMFF)...")
records = []
for i, row in rrs_df.iterrows():
    smi = row['smiles']
    rrs_class = row['RRS_class']
    rrs_mean = row['RRS_mean']
    print(f"  [{i+1}/{len(rrs_df)}] Class {rrs_class} | RRS={rrs_mean:.1f}")
    tfp = compute_tfp(smi)
    if tfp is not None:
        records.append({
            'smiles': smi,
            'RRS_mean': rrs_mean,
            'RRS_class': rrs_class,
            **tfp
        })
    else:
        print(f"    → FAILED: {smi[:50]}")

df = pd.DataFrame(records)
df.to_csv(OUT_CSV, index=False)
print(f"\nSaved TFP data: {OUT_CSV} ({len(df)} compounds)")
print(df.groupby('RRS_class')[['h1_count', 'h1_mean_lifetime', 'h1_total_persistence']].describe())

# ─── Violin Plot ──────────────────────────────────────────────────────────────
print("\nGenerating violin plot...")

# Map classes to display labels
class_order = sorted(df['RRS_class'].unique())
class_labels = {c: f'Class {c}' for c in class_order}
class_counts = df['RRS_class'].value_counts()

# Color palette (colorblind-safe)
class_colors = {
    'A': '#2196F3',  # Blue — resistance-resilient
    'B': '#4CAF50',  # Green
    'C': '#FF9800',  # Orange — intermediate
    'D': '#F44336',  # Red — resistance-vulnerable
}

fig, axes = plt.subplots(1, 3, figsize=(12, 5))
fig.suptitle('H$_1$ Topological Persistence vs. Resistance Resilience Class\n'
             '(Cross-Paper P3 × P2: 17 Polypharmacological Leads)',
             fontsize=13, fontweight='bold', y=1.02)

metrics = [
    ('h1_count',             'H$_1$ Feature Count\n(ring topology)',      'Count'),
    ('h1_mean_lifetime',     'H$_1$ Mean Lifetime\n(persistence)',         'Lifetime (Å)'),
    ('h1_total_persistence', 'H$_1$ Total Persistence\n(cumulative rings)', 'Total (Å)'),
]

for ax, (col, ylabel, unit) in zip(axes, metrics):
    groups = [df.loc[df['RRS_class'] == c, col].values for c in class_order]
    colors = [class_colors.get(c, '#888888') for c in class_order]

    # Violin
    parts = ax.violinplot(groups, positions=range(len(class_order)),
                           showmeans=True, showmedians=True, showextrema=True)

    for i, (pc, col_c) in enumerate(zip(parts['bodies'], colors)):
        pc.set_facecolor(col_c)
        pc.set_alpha(0.65)
        pc.set_edgecolor('black')
        pc.set_linewidth(0.8)

    for part_name in ['cmeans', 'cmedians', 'cbars', 'cmaxes', 'cmins']:
        if part_name in parts:
            parts[part_name].set_color('black')
            parts[part_name].set_linewidth(1.2)

    # Scatter overlay (jitter)
    for i, (grp, col_c) in enumerate(zip(groups, colors)):
        jitter = np.random.uniform(-0.08, 0.08, size=len(grp))
        ax.scatter(np.full(len(grp), i) + jitter, grp,
                   color=col_c, edgecolors='black', linewidths=0.5,
                   s=40, zorder=5, alpha=0.9)

    ax.set_xticks(range(len(class_order)))
    ax.set_xticklabels([f'Class {c}\n(n={class_counts.get(c, 0)})' for c in class_order],
                        fontsize=10)
    ax.set_ylabel(unit, fontsize=10)
    ax.set_title(ylabel, fontsize=11, pad=8)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='y', alpha=0.3, linestyle='--')

# Legend
patches = [mpatches.Patch(color=class_colors.get(c, '#888'), label=f'Class {c}')
           for c in class_order]
fig.legend(handles=patches, loc='upper right', fontsize=9,
           title='RRS Class', title_fontsize=9, framealpha=0.8)

plt.tight_layout()
out_fig = os.path.join(OUT_DIR, 'h1_rrs_class_violin.png')
plt.savefig(out_fig, dpi=300, bbox_inches='tight')
print(f"Saved figure: {out_fig}")

# ─── Summary statistics ───────────────────────────────────────────────────────
print("\n=== Summary Statistics ===")
for cls in class_order:
    sub = df[df['RRS_class'] == cls]
    print(f"Class {cls} (n={len(sub)}): "
          f"H1 count={sub['h1_count'].mean():.2f}±{sub['h1_count'].std():.2f}, "
          f"H1 mean lifetime={sub['h1_mean_lifetime'].mean():.3f}±{sub['h1_mean_lifetime'].std():.3f}, "
          f"H1 total={sub['h1_total_persistence'].mean():.3f}±{sub['h1_total_persistence'].std():.3f}")

# ─── Statistical validation (Small N robust methods) ─────────────────────────
from scipy import stats

def exact_permutation_test(x, y, num_permutations=10000):
    """Compute exact permutation p-value for Spearman rho."""
    obs_rho, _ = stats.spearmanr(x, y)
    count_extreme = 0
    y_perm = np.array(y)
    np.random.seed(42) # Replicability
    for _ in range(num_permutations):
        np.random.shuffle(y_perm)
        perm_rho, _ = stats.spearmanr(x, y_perm)
        if abs(perm_rho) >= abs(obs_rho):
            count_extreme += 1
    p_exact = count_extreme / num_permutations
    return obs_rho, p_exact

def bootstrap_ci_spearman(x, y, num_bootstraps=1000, alpha=0.05):
    """Compute bootstrap confidence interval for Spearman rho."""
    rhos = []
    n = len(x)
    x = np.array(x)
    y = np.array(y)
    np.random.seed(42) # Replicability
    for _ in range(num_bootstraps):
        idx = np.random.choice(n, n, replace=True)
        if len(np.unique(x[idx])) > 1 and len(np.unique(y[idx])) > 1:
            rho, _ = stats.spearmanr(x[idx], y[idx])
            if not np.isnan(rho):
                rhos.append(rho)
    
    rhos = np.sort(rhos)
    lower = np.percentile(rhos, 100 * (alpha / 2))
    upper = np.percentile(rhos, 100 * (1 - alpha / 2))
    return lower, upper

print("\n=== Statistical Validation (n=14) ===")
# Drop NaNs
valid_df = df.dropna(subset=['RRS_mean', 'h1_total_persistence', 'h1_count'])

# H1 Total Persistence
rho_tot, p_asymp_tot = stats.spearmanr(valid_df['RRS_mean'], valid_df['h1_total_persistence'])
_, p_exact_tot = exact_permutation_test(valid_df['RRS_mean'], valid_df['h1_total_persistence'])
ci_lower_tot, ci_upper_tot = bootstrap_ci_spearman(valid_df['RRS_mean'], valid_df['h1_total_persistence'])

print(f"RRS_mean vs H1_total_persistence:")
print(f"  Spearman ρ: {rho_tot:.3f} [95% CI: {ci_lower_tot:.3f}, {ci_upper_tot:.3f}]")
print(f"  p-value (asymptotic): {p_asymp_tot:.4f}")
print(f"  p-value (permutation): {p_exact_tot:.4f}")

# H1 Count
rho_cnt, p_asymp_cnt = stats.spearmanr(valid_df['RRS_mean'], valid_df['h1_count'])
_, p_exact_cnt = exact_permutation_test(valid_df['RRS_mean'], valid_df['h1_count'])
ci_lower_cnt, ci_upper_cnt = bootstrap_ci_spearman(valid_df['RRS_mean'], valid_df['h1_count'])

print(f"\nRRS_mean vs H1_count:")
print(f"  Spearman ρ: {rho_cnt:.3f} [95% CI: {ci_lower_cnt:.3f}, {ci_upper_cnt:.3f}]")
print(f"  p-value (asymptotic): {p_asymp_cnt:.4f}")
print(f"  p-value (permutation): {p_exact_cnt:.4f}")
