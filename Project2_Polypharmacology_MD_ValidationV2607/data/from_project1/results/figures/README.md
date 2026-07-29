# Publication Results

**English** | [Français](#répertoire-résultats-de-publication)

This directory archives publication-ready figures, plots, and visualizations generated for scientific papers, reports, and presentations.

---

## Overview

| Metric | Value |
|--------|-------|
| **Total Size** | 8.3 MB |
| **File Formats** | PNG, PDF |
| **Categories** | 8 |
| **Total Figures** | 35+ |

---

## Figure Categories

### 1. Chemical Space Analysis

| File | Description | Type |
|------|-------------|------|
| `chemical_space.pdf`, `chemical_space2d.pdf` | 2D/3D chemical space visualization | Space |
| `tsne_np.pdf`, `tsne_np.png` | t-SNE of natural products | Dimensionality reduction |
| `tsne_sd.pdf`, `tsne_sd.png` | t-SNE of synthetic drugs | Dimensionality reduction |
| `df1_umap.png` | UMAP visualization | Dimensionality reduction |

**Usage:** Show distribution of compound families in chemical space

---

### 2. Physicochemical Properties

| File | Description | Type |
|------|-------------|------|
| `phys_chem.pdf`, `phys_chem_poster.pdf` | Key property distributions | Properties |
| `pce_np.pdf`, `pce_sd.pdf` | Property comparison (NP vs SD) | Properties |
| `physicochemical_coherence_analysis.pdf` | Cluster property coherence | Analysis |
| `physicochemical_distributions_by_cluster.pdf` | Properties by cluster | Analysis |

**Properties Shown:**
- Molecular weight (MW)
- LogP (lipophilicity)
- H-bond donors/acceptors
- Rotatable bonds
- TPSA

---

### 3. ADMET Properties

| File | Description | Type |
|------|-------------|------|
| `admet_prop.pdf`, `admet_prop.png` | ADMET property distributions | ADMET |
| `admet_prop_poster.pdf` | Poster-quality ADMET figure | ADMET |

**ADMET Properties:**
- Solubility (LogS)
- Permeability (Caco-2)
- hERG inhibition
- CYP450 interactions
- Toxicity endpoints

---

### 4. Model Performance

| File | Description | Type |
|------|-------------|------|
| `ACTIVITY_PRED.pdf`, `ACTIVITY_PRED.png` | Activity prediction performance | ML |
| `32_smi_vae_training_history.pdf` | VAE 32-dim training curves | Training |
| `64_smi_vae_training_history.pdf` | VAE 64-dim training curves | Training |
| `structural_classification_np.pdf` | NP structural classification | Analysis |
| `structural_classification_sd.pdf` | SD structural classification | Analysis |

---

### 5. Clustering & Diversity

| File | Description | Type |
|------|-------------|------|
| `chemotype_diversity_purity.pdf` | Chemotype diversity metrics | Clustering |
| `intra_inter_cluster_similarity_distributions.pdf` | Cluster similarity analysis | Clustering |
| `expansion_claim_validation.pdf` | Chemical space expansion validation | Analysis |
| `seed_vs_generated_analysis.pdf` | Seed vs generated comparison | Generation |

---

### 6. Scaffold Analysis

| File | Description | Type |
|------|-------------|------|
| `top10_novel_reinvent_scaffolds.png` | Top 10 novel REINVENT scaffolds | Scaffolds |
| `top20_novel_reinvent_scaffolds.png` | Top 20 novel REINVENT scaffolds | Scaffolds |
| `lc_mal_like.pdf` | Malaria-like scaffolds | Scaffolds |
| `sd_np_dist.pdf` | SD/NP scaffold distribution | Scaffolds |

---

### 7. Docking Results

| File | Description | Type |
|------|-------------|------|
| `docking_summary_4panel.pdf` | 4-panel docking summary | Docking |

---

### 8. Interaction Diagrams (C14)

| File | Description | Type |
|------|-------------|------|
| `interaction_201.png` | Ligand 201 (PfDHFR) 2D interactions | 2D diagram |
| `interaction_214.png` | Ligand 214 (PfDHFR) 2D interactions | 2D diagram |
| `interaction_438.png` | Ligand 438 (PfATP4) 2D interactions | 2D diagram |

**Key Interactions Visualized:**
- Ligand 201: Asp54 (H-bond), Ile164 (Hydrophobic), Phe34 (Pi-stacking), Arg57 (H-bond)
- Ligand 214: Asp54 (H-bond), Ile164 (Hydrophobic), Phe34 (Pi-stacking), Arg122 (H-bond)
- Ligand 438: Glu328 (H-bond), Phe340 (Pi-stacking), Leu331 (Hydrophobic), Asn344 (H-bond)

---

### 9. Graphical Abstract

| File | Description | Specifications |
|------|-------------|----------------|
| `graphical_abstract.png` | JCIM graphical abstract | 1024x568, JPEG, RGB, 119 KB |

**Layout:** 3 panels (Chemical Space Mapping -> Generative Expansion -> Consensus Docking)
**Key Statistics:** 65,856 | 19,913 | >70

---

## File Formats

### PNG (`.png`)
- **Use:** Presentations, web, quick preview
- **Resolution:** High (300+ DPI)
- **Size:** Larger files

### PDF (`.pdf`)
- **Use:** Publications, papers, reports
- **Type:** Vector graphics (scalable)
- **Size:** Smaller files

### Recommendation

| Use Case | Format |
|----------|--------|
| Manuscript submission | PDF |
| Conference poster | PDF |
| Presentation slides | PNG |
| Web display | PNG |
| Further editing | PDF + source |

---

## Accessing Figures

### Python

```python
from malaria_explorer.utils.config import PAPER_RESULTS_DIR
import matplotlib.pyplot as plt
from PIL import Image

# Get path to figure
fig_path = PAPER_RESULTS_DIR / "chemical_space.pdf"

# Display in Jupyter
Image.open(fig_path)
```

### R

```r
# Load figure
fig_path <- "Paper_results/chemical_space.pdf"
img <- png::readPNG(fig_path)
```

---

## Regenerating Figures

Most figures can be regenerated by running the pipeline:

```bash
# Run full pipeline
jupyter notebook pipelines/08_chemical_evidence.ipynb

# Or specific analysis
jupyter notebook notebooks/Chemical_Space_AnalysisV241003.ipynb
```

---

## Citation

If using these figures in your work:

```bibtex
@software{malaria_codes,
  title = {Malaria Chemical Space Exploration},
  author = {Sao Temgoua, Vital},
  url = {https://github.com/Vital-Sao/Malaria_codes},
  year = {2026}
}
```

---

## Best Practices

### ✅ Do

- Use PDF for publications (vector quality)
- Cite the project appropriately
- Reference the specific notebook that generated the figure
- Check figure licenses before reuse

### ❌ Don't

- Modify figures without noting changes
- Use low-resolution PNGs for print
- Assume all figures are CC-BY licensed
- Remove axis labels or legends

---

## Répertoire Résultats de Publication

Ce répertoire contient les figures et visualisations pour les publications scientifiques.

### Catégories

1. **Espace Chimique** - Distribution des composés
2. **Propriétés Physico-chimiques** - MW, LogP, etc.
3. **ADMET** - Solubilité, perméabilité, toxicité
4. **Performance des Modèles** - VAE, CNN, MLP
5. **Clustering** - Diversité des chémotypes
6. **Scaffolds** - Structures de base

### Formats

| Format | Usage |
|--------|-------|
| PDF | Publications, posters |
| PNG | Présentations, web |

### Accès

```python
from malaria_explorer.utils.config import PAPER_RESULTS_DIR
fig_path = PAPER_RESULTS_DIR / "chemical_space.pdf"
```

---

**Location:** `Paper_results/`
**Size:** 8.3 MB
**Formats:** PNG, PDF
**Purpose:** Publication-ready figures

**Last Updated:** April 8, 2026
**Status:** Complete (C14 interaction diagrams + graphical abstract)
