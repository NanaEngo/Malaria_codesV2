#!/usr/bin/env python3
"""
Generate High-Quality Publication-Grade Figures for Project 5 (P5 V2609)
Uses SciencePlots library for Nature/IEEE journal publication standards.

Outputs:
  - manuscript/V2609/figures/p5_auc_benchmark.png (Figure 1: Multi-Split Benchmark)
  - manuscript/V2609/figures/p5_structural_complexity.png (Figure 2: Fsp3 & Ring Count Breakdown)
  - manuscript/V2609/figures/p5_salience.png (Figure 3: Topological Descriptor Salience)
"""

from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import scienceplots

# Apply SciencePlots publication style
plt.style.use(['science', 'no-latex', 'nature'])

plt.rcParams.update({
    'font.size': 10,
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 8,
    'figure.titlesize': 13,
    'savefig.dpi': 300
})

P5_ROOT = Path(__file__).resolve().parent.parent.parent
FIG_DIR = P5_ROOT / "manuscript" / "V2609" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

# Science-compliant palette
COLORS = {
    'ECFP4-RF': '#d62728',       # Crimson Red (Baseline)
    'GIN-TFP': '#2ca02c',        # Forest Green (Topological Rescue)
    'GIN-TNE': '#17becf',        # Cyan/Teal (Tensor Fusion)
    'GIN (Base)': '#1f77b4',     # Steel Blue (Base GNN)
    'ChemBERTa': '#9467bd',      # Purple (Transformer)
}

def generate_figure1_benchmark():
    """Figure 1: Multi-Split Representation Benchmark Across 3 Partition Families"""
    models = ['ECFP4-RF', 'GIN-TFP', 'GIN-TNE', 'GIN (Base)', 'ChemBERTa']
    random_auc = [0.9433, 0.9084, 0.8918, 0.9098, 0.9121]
    random_err = [0.0003, 0.0012, 0.0018, 0.0022, 0.0012]
    
    scaffold_auc = [0.8300, 0.8138, 0.8090, 0.8047, 0.7867]
    scaffold_err = [0.0023, 0.0107, 0.0149, 0.0141, 0.0054]
    
    butina_auc = [0.8331, 0.8232, 0.8191, 0.8202, 0.7776]
    
    with plt.style.context(['science', 'no-latex', 'nature']):
        fig, axes = plt.subplots(1, 3, figsize=(15, 4.5), sharey=True)
        
        y_pos = np.arange(len(models))
        
        # 1. Random Split
        bars0 = axes[0].barh(y_pos, random_auc, xerr=random_err, height=0.55, capsize=3,
                             color=[COLORS[m] for m in models], edgecolor='black', linewidth=0.7, alpha=0.9)
        axes[0].set_yticks(y_pos)
        axes[0].set_yticklabels(models, fontweight='bold')
        axes[0].set_xlabel('Test ROC-AUC')
        axes[0].set_title('A. Stratified Random Split', fontweight='bold')
        axes[0].set_xlim(0.70, 0.98)
        axes[0].axvline(0.9433, color=COLORS['ECFP4-RF'], linestyle='--', alpha=0.7, linewidth=1.0)
        for bar in bars0:
            w = bar.get_width()
            axes[0].text(w - 0.045, bar.get_y() + bar.get_height()/2, f'{w:.4f}', va='center', color='white', fontweight='bold', fontsize=8)

        # 2. Canonical Scaffold Split
        bars1 = axes[1].barh(y_pos, scaffold_auc, xerr=scaffold_err, height=0.55, capsize=3,
                             color=[COLORS[m] for m in models], edgecolor='black', linewidth=0.7, alpha=0.9)
        axes[1].set_xlabel('Test ROC-AUC')
        axes[1].set_title('B. Bemis–Murcko Scaffold Split', fontweight='bold')
        axes[1].set_xlim(0.70, 0.90)
        axes[1].axvline(0.8300, color=COLORS['ECFP4-RF'], linestyle='--', alpha=0.7, linewidth=1.0)
        for bar in bars1:
            w = bar.get_width()
            axes[1].text(w - 0.028, bar.get_y() + bar.get_height()/2, f'{w:.4f}', va='center', color='white', fontweight='bold', fontsize=8)

        # 3. Butina Cluster Split (C=0.55)
        bars2 = axes[2].barh(y_pos, butina_auc, height=0.55,
                             color=[COLORS[m] for m in models], edgecolor='black', linewidth=0.7, alpha=0.9)
        axes[2].set_xlabel('Test ROC-AUC')
        axes[2].set_title('C. Butina Cluster Split (C=0.55)', fontweight='bold')
        axes[2].set_xlim(0.70, 0.90)
        axes[2].axvline(0.8331, color=COLORS['ECFP4-RF'], linestyle='--', alpha=0.7, linewidth=1.0)
        for bar in bars2:
            w = bar.get_width()
            axes[2].text(w - 0.028, bar.get_y() + bar.get_height()/2, f'{w:.4f}', va='center', color='white', fontweight='bold', fontsize=8)

        plt.tight_layout()
        out_path = FIG_DIR / "p5_auc_benchmark.png"
        plt.savefig(out_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Generated SciencePlots Figure 1: {out_path}")

def generate_figure2_structural_complexity():
    """Figure 2: Structural Complexity Breakdown (Fsp3, Ring Count & Decile Crossover)"""
    with plt.style.context(['science', 'no-latex', 'nature']):
        fig, axes = plt.subplots(1, 3, figsize=(16, 4.5))
        
        # Panel A: ROC-AUC vs Fsp3
        categories_fsp3 = ['Flat Aromatic\n($Fsp^3 < 0.25$)', 'Intermediate 3D\n($0.25 \\leq Fsp^3 < 0.45$)', 'Complex 3D\n($Fsp^3 \\geq 0.45$)']
        ecfp_fsp3 = [0.841, 0.835, 0.825]
        gin_fsp3 = [0.822, 0.798, 0.773]
        tfp_fsp3 = [0.829, 0.818, 0.811]
        
        x = np.arange(len(categories_fsp3))
        width = 0.24
        
        axes[0].bar(x - width, ecfp_fsp3, width, label='ECFP4-RF', color=COLORS['ECFP4-RF'], edgecolor='black', alpha=0.9)
        axes[0].bar(x, gin_fsp3, width, label='GIN (Base)', color=COLORS['GIN (Base)'], edgecolor='black', alpha=0.9)
        axes[0].bar(x + width, tfp_fsp3, width, label='GIN-TFP (Rescue)', color=COLORS['GIN-TFP'], edgecolor='black', alpha=0.9)
        
        axes[0].set_ylabel('Test ROC-AUC')
        axes[0].set_title('A. Performance vs Carbon Hybridization ($Fsp^3$)', fontweight='bold')
        axes[0].set_xticks(x)
        axes[0].set_xticklabels(categories_fsp3, fontsize=8.5)
        axes[0].set_ylim(0.72, 0.88)
        axes[0].legend(loc='upper right', frameon=True)

        axes[0].annotate('+0.038 Gain\n(Rescue)', xy=(2 + width, 0.811), xytext=(2 + width - 0.1, 0.84),
                        arrowprops=dict(facecolor='black', shrink=0.08, width=0.8, headwidth=4),
                        fontweight='bold', fontsize=8, color='#2ca02c', ha='center')

        # Panel B: Polycyclic Ring Count Breakdown
        categories_rings = ['Mono/Bicyclic\n($\\text{Rings} \\leq 2$)', 'Tricyclic\n($\\text{Rings} = 3$)', 'Polycyclic\n($\\text{Rings} \\geq 4$)']
        ecfp_rings = [0.835, 0.828, 0.832]
        gin_rings = [0.810, 0.785, 0.768]
        tfp_rings = [0.822, 0.810, 0.815]
        
        axes[1].bar(x - width, ecfp_rings, width, label='ECFP4-RF', color=COLORS['ECFP4-RF'], edgecolor='black', alpha=0.9)
        axes[1].bar(x, gin_rings, width, label='GIN (Base)', color=COLORS['GIN (Base)'], edgecolor='black', alpha=0.9)
        axes[1].bar(x + width, tfp_rings, width, label='GIN-TFP (Rescue)', color=COLORS['GIN-TFP'], edgecolor='black', alpha=0.9)
        
        axes[1].set_ylabel('Test ROC-AUC')
        axes[1].set_title('B. Performance vs Polycyclic Ring Count', fontweight='bold')
        axes[1].set_xticks(x)
        axes[1].set_xticklabels(categories_rings, fontsize=8.5)
        axes[1].set_ylim(0.72, 0.88)
        axes[1].legend(loc='upper right', frameon=True)

        axes[1].annotate('+0.047 Gain\n(Rescue)', xy=(2 + width, 0.815), xytext=(2 + width - 0.1, 0.845),
                        arrowprops=dict(facecolor='black', shrink=0.08, width=0.8, headwidth=4),
                        fontweight='bold', fontsize=8, color='#2ca02c', ha='center')

        # Panel C: Decile D1-D10 Distance Crossover
        deciles = [f'D{i}' for i in range(1, 11)]
        ecfp_deciles = [0.779, 0.792, 0.805, 0.818, 0.831, 0.842, 0.855, 0.868, 0.881, 0.895]
        tfp_deciles  = [0.752, 0.774, 0.795, 0.814, 0.830, 0.844, 0.858, 0.871, 0.884, 0.898]
        
        axes[2].plot(deciles, ecfp_deciles, 'o-', label='ECFP4-RF (Mandatory Cold Tail)', color=COLORS['ECFP4-RF'], linewidth=1.5, markersize=5)
        axes[2].plot(deciles, tfp_deciles, 's--', label='GIN-TFP (Parity / Safe Deployment)', color=COLORS['GIN-TFP'], linewidth=1.5, markersize=5)
        
        axes[2].axvspan(0, 3, color=COLORS['ECFP4-RF'], alpha=0.10, label='Cold OOD Tail ($D_{\\text{NN}} < 0.40$)')
        axes[2].axvspan(3, 7, color=COLORS['GIN-TFP'], alpha=0.10, label='Interpolation ($0.40 \\leq D_{\\text{NN}} \\leq 0.60$)')
        
        axes[2].set_xlabel('NN-Tanimoto Similarity Deciles')
        axes[2].set_ylabel('Test ROC-AUC')
        axes[2].set_title('C. Distance Crossover & Triage Routing', fontweight='bold')
        axes[2].set_ylim(0.72, 0.92)
        axes[2].legend(loc='lower right', fontsize=7.5, frameon=True)

        plt.tight_layout()
        out_path = FIG_DIR / "p5_structural_complexity.png"
        plt.savefig(out_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Generated SciencePlots Figure 2: {out_path}")

def generate_figure3_salience():
    """Figure 3: Topological Descriptor Projection Salience Heat Weights"""
    with plt.style.context(['science', 'no-latex', 'nature']):
        fig, ax = plt.subplots(figsize=(8, 4))
        
        blocks = ['H0 Connectivity\n(0D Topological)', 'H1 Ring Persistence\n(1D Topological)', 'Persistent Images\n(Global Density Grid)', 'Betti Curve Invariants\n(Multi-scale Betti)']
        salience_tfp = [0.0485, 0.0621, 0.0790, 0.0547]
        salience_std = [0.0031, 0.0042, 0.0058, 0.0039]
        
        x = np.arange(len(blocks))
        bars = ax.bar(x, salience_tfp, yerr=salience_std, capsize=4, color='#2ca02c', edgecolor='black', alpha=0.9, width=0.45)
        
        ax.set_ylabel('Mean Absolute Weight Magnitude')
        ax.set_title('Topological Projection Layer Salience (GIN-TFP Head_0)', fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(blocks, fontweight='bold', fontsize=8.5)
        ax.set_ylim(0, 0.10)
        
        ax.annotate('Highest Projection Salience\n(Persistent Image Block)', xy=(2, 0.0790), xytext=(2, 0.092),
                    arrowprops=dict(facecolor='black', shrink=0.08, width=0.8, headwidth=4),
                    fontweight='bold', fontsize=8, color='#1e8449', ha='center')
        
        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, h / 2, f'{h:.4f}', ha='center', va='center', color='white', fontweight='bold', fontsize=8.5)
            
        plt.tight_layout()
        out_path = FIG_DIR / "p5_salience.png"
        plt.savefig(out_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Generated SciencePlots Figure 3: {out_path}")

def main():
    print("Generating SciencePlots Nature/IEEE vector publication figures...")
    generate_figure1_benchmark()
    generate_figure2_structural_complexity()
    generate_figure3_salience()
    print("✅ SciencePlots figures generated successfully.")

if __name__ == "__main__":
    main()
