# Supplementary Material: Clustering Algorithms Evaluation

To evaluate the embedded chemical space representations produced by our Variational Autoencoder models, we ran a comprehensive hyperparameter search over different clustering algorithms for the structured dataset ($N = 65,856$ distinct SMILES strings).

Below, we detail the performance of **K-Means** and **BIRCH** clustering algorithms applied to both 32- and 64-dimensional latent space representations, optimized within a target range of 150 to 500 clusters. The quality of the formed clusters was measured using three main internal cluster validity indices: Silhouette Score, Calinski-Harabasz Index, and Davies-Bouldin Index.

## K-Means Clustering

K-Means demonstrated robust separation and relatively well-balanced clusters compared to BIRCH. The 64-dimensional latent space demonstrated slightly better separation capabilities resulting in a higher Silhouette Score and Calinski-Harabasz index compared to the 32-dimensional model. In a direct head-to-head comparison against BIRCH, **K-Means performed as the overall best clustering algorithm**.

**Table S1. K-Means Clustering Results and Metrics**

| Metric | 32-Dimensional Latent Space | 64-Dimensional Latent Space |
| :--- | :--- | :--- |
| **Best `n_clusters`** | 499 | 484 |
| **Silhouette Score** | 0.1820 | 0.2285 |
| **Calinski-Harabasz Index** | 874.6800 | 1500.5897 |
| **Davies-Bouldin Index** | 1.3924 | 1.2325 |
| **Min Cluster Size** | 12 | 11 |
| **Max Cluster Size** | 454 | 519 |
| **Mean Cluster Size** | 132.0 | 136.1 |


## BIRCH Clustering

BIRCH (Balanced Iterative Reducing and Clustering using Hierarchies) was evaluated as an alternative owing to its efficiency with large datasets. The algorithm was optimized over the branching factor and cluster radius threshold. Despite tuning these hyperparameters, BIRCH resulted in slightly lower separation metrics (lower Silhouette and Calinski-Harabasz scores, and generally heavily skewed max cluster capacities) when compared to K-Means. 

**Table S2. BIRCH Clustering Results and Metrics**

| Metric | 32-Dimensional Latent Space | 64-Dimensional Latent Space |
| :--- | :--- | :--- |
| **Best `n_clusters`** | 490 | 489 |
| **Best `threshold`** | 0.1141 | 0.1001 |
| **Best `branching_factor`** | 30 | 75 |
| **Silhouette Score** | 0.1216 | 0.1620 |
| **Calinski-Harabasz Index** | 702.6001 | 1187.4375 |
| **Davies-Bouldin Index** | 1.5846 | 1.4052 |
| **Min Cluster Size** | 13 | 11 |
| **Max Cluster Size** | 820 | 858 |
| **Mean Cluster Size** | 134.4 | 134.7 |
