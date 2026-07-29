# Clustering Results

**English** | [Français](#résultats-de-clustering)

This directory contains clustering algorithm outputs, latent vectors from VAE models, and evaluation metrics.

---

## Overview

| Metric | Value |
|--------|-------|
| **Total Size** | 27 MB |
| **VAE Dimensions** | 64 (ConvVAE-SMILES, selected) |
| **Algorithms** | K-Means (n=484, Silhouette=0.229, CH=1500.59, DB=1.233), BIRCH, Jarvis-Patrick |
| **File Formats** | `.npy`, `.csv`, `.txt` |

---

## File Structure

```
clustering_results/
├── 32_*.npy              # 32-dimensional VAE results
├── 64_*.npy              # 64-dimensional VAE results
├── *_latent_vectors*.npy # VAE latent space vectors
├── *_labels*.npy         # Cluster assignments
├── *_results*.csv        # Hyperparameter search results
├── *_metrics*.csv        # Evaluation metrics
└── *_summary*.txt        # Summary reports
```

---

## File Descriptions

### Latent Vectors

| File | Dimensions | Description | Size |
|------|------------|-------------|------|
| `32_smi_vae_latent_vectors_full.npy` | 32 | SMILES VAE latent vectors | ~16 MB |
| `64_smi_vae_latent_vectors_full.npy` | 64 | SMILES VAE latent vectors | ~16 MB |

**Usage:**
```python
import numpy as np

# Load latent vectors
latent_32 = np.load('clustering_results/32_smi_vae_latent_vectors_full.npy')
latent_64 = np.load('clustering_results/64_smi_vae_latent_vectors_full.npy')

print(f"32-dim shape: {latent_32.shape}")
print(f"64-dim shape: {latent_64.shape}")
```

---

### Cluster Labels

#### BIRCH Algorithm

| File | Dimensions | Description |
|------|------------|-------------|
| `32_birch_labels_full.npy` | 32 | BIRCH cluster assignments |
| `64_birch_labels_full.npy` | 64 | BIRCH cluster assignments |

#### KMeans Algorithm

| File | Dimensions | Description |
|------|------------|-------------|
| `32_kmeans_labels_full.npy` | 32 | KMeans cluster assignments |
| `64_kmeans_labels_full.npy` | 64 | KMeans cluster assignments |

**Usage:**
```python
# Load cluster labels
birch_labels = np.load('clustering_results/32_birch_labels_full.npy')
kmeans_labels = np.load('clustering_results/32_kmeans_labels_full.npy')

# Analyze cluster distribution
import pandas as pd
cluster_counts = pd.Series(birch_labels).value_counts()
print(f"Number of clusters: {len(cluster_counts)}")
print(f"Cluster sizes:\n{cluster_counts}")
```

---

### Hyperparameter Search Results

| File | Dimensions | Description |
|------|------------|-------------|
| `32_hyp_nn_smi_results_full.csv` | 32 | VAE hyperparameter search results |
| `64_hyp_nn_smi_results_full.csv` | 64 | VAE hyperparameter search results |

**Contents:**
- Hyperparameter combinations tested
- Training/validation losses
- Reconstruction accuracy
- KL divergence values

**Usage:**
```python
import pandas as pd

# Load hyperparameter results
results = pd.read_csv('clustering_results/32_hyp_nn_smi_results_full.csv')

# Find best configuration
best = results.loc[results['val_loss'].idxmin()]
print(f"Best hyperparameters: {best}")
```

---

### Evaluation Metrics

#### Jarvis-Patrick

| File | Dimensions | Description |
|------|------------|-------------|
| `32_final_evaluation_metrics_zai_full.csv` | 32 | Jarvis-Patrick metrics |
| `64_final_evaluation_metrics_zai_full.csv` | 64 | Jarvis-Patrick metrics |

**Metrics:**
- Silhouette score
- Davies-Bouldin index
- Calinski-Harabasz score
- Cluster statistics (min, max, mean size)

#### Summary Reports

| File | Dimensions | Description |
|------|------------|-------------|
| `32_clustering_comparison_summary_zai_full.txt` | 32 | BIRCH vs KMeans comparison |
| `64_clustering_comparison_summary_zai_full.txt` | 64 | BIRCH vs KMeans comparison |
| `32_summary_full.txt` | 32 | Jarvis-Patrick summary |
| `64_summary_full.txt` | 64 | Jarvis-Patrick summary |

---

## Clustering Algorithms

### BIRCH (Balanced Iterative Reducing and Clustering using Hierarchies)

**Parameters:**
- Threshold: 0.5
- Branching factor: 50
- n_clusters: None (auto)

**Best for:** Large datasets, hierarchical structure

### KMeans

**Parameters:**
- n_clusters: 484 (selected for manuscript)
- init: k-means++
- n_init: 10

**Metrics:**
- Silhouette Score: 0.229
- Calinski-Harabasz: 1500.59
- Davies-Bouldin: 1.233

**Selected for manuscript:** K-Means with n=484 centroids was chosen as the primary clustering method based on cluster quality metrics and interpretability. These centroids were used as representatives for dual-filter consensus docking (469 centroids × 4 targets).

**Best for:** Spherical clusters, balanced sizes

### Jarvis-Patrick

**Parameters:**
- k_neighbors: 10
- min_shared: 6

**Best for:** Arbitrary cluster shapes, noise tolerance

---

## Evaluation Metrics

### Silhouette Score

**Range:** [-1, 1]  
**Interpretation:**
- > 0.7: Strong structure
- 0.5 - 0.7: Reasonable structure
- 0.25 - 0.5: Weak structure
- < 0.25: No substantial structure

### Davies-Bouldin Index

**Range:** [0, ∞)  
**Interpretation:** Lower is better (0 = perfect)

### Calinski-Harabasz Score

**Range:** [0, ∞)  
**Interpretation:** Higher is better

---

## Regenerating Results

```python
# Run clustering pipeline
import numpy as np
from sklearn.cluster import Birch, KMeans

# Load latent vectors
latent = np.load('clustering_results/32_smi_vae_latent_vectors_full.npy')

# BIRCH
birch = Birch(threshold=0.5, branching_factor=50)
birch_labels = birch.fit_predict(latent)
np.save('clustering_results/32_birch_labels_full.npy', birch_labels)

# KMeans
kmeans = KMeans(n_clusters=10, random_state=42)
kmeans_labels = kmeans.fit_predict(latent)
np.save('clustering_results/32_kmeans_labels_full.npy', kmeans_labels)
```

---

## Accessing Results

### Python

```python
from malaria_explorer.utils.config import CLUSTERING_DIR
import numpy as np

# Load clustering results
labels_path = CLUSTERING_DIR / "32_birch_labels_full.npy"
labels = np.load(labels_path)
```

### With Molecules

```python
import pandas as pd
import numpy as np

# Load molecules
df = pd.read_csv('data/raw/All_molecules.csv')

# Load cluster labels
labels = np.load('clustering_results/32_birch_labels_full.npy')

# Assign to dataframe
df['cluster'] = labels

# Analyze cluster
cluster_0 = df[df['cluster'] == 0]
print(f"Cluster 0 has {len(cluster_0)} molecules")
```

---

## Résultats de Clustering

Ce répertoire contient les résultats des algorithmes de clustering et les vecteurs latents des modèles VAE.

### Fichiers Principaux

| Fichier | Description |
|---------|-------------|
| `32_smi_vae_latent_vectors_full.npy` | Vecteurs latents VAE (32-dim) |
| `64_smi_vae_latent_vectors_full.npy` | Vecteurs latents VAE (64-dim) |
| `32_birch_labels_full.npy` | Labels BIRCH (32-dim) |
| `32_kmeans_labels_full.npy` | Labels KMeans (32-dim) |

### Algorithmes

- **BIRCH** - Clustering hiérarchique
- **KMeans** - Partitionnement
- **Jarvis-Patrick** - Basé sur les voisins

### Métriques d'Évaluation

- **Silhouette score** - Cohésion des clusters
- **Davies-Bouldin** - Séparation des clusters
- **Calinski-Harabasz** - Variance inter/intra cluster

---

**Location:** `clustering_results/`
**Size:** 27 MB
**Algorithms:** K-Means (n=484 selected for manuscript), BIRCH, Jarvis-Patrick
**Dimensions:** 64 (ConvVAE-SMILES, selected)

**Last Updated:** April 8, 2026
**Status:** ✅ Verified (K-Means n=484 selected for manuscript)
