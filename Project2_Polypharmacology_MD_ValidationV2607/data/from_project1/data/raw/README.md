# Répertoire : Dataset_malaria_paper

Ce répertoire contient l'ensemble des données brutes et prétraitées utilisées pour les analyses de ce projet de découverte de médicaments contre le paludisme. Les fichiers sont principalement au format CSV et contiennent des informations sur les molécules, leurs structures et leurs propriétés.

## Description des Fichiers

- **`Afromalaria_DB.csv`**: Une base de données de composés provenant de sources africaines, potentiellement pertinents pour le paludisme.
- **`Antimalarial_NP.csv` / `Antimalarial_sp.csv`**: Fichiers contenant des produits naturels (NP) et des produits de synthèse (sp) ayant une activité antipaludique connue.
- **`MalariaBox400compoundsDec2014.csv`**: Contient les 400 composés de la "Malaria Box" de Medicines for Malaria Venture (MMV), un ensemble de composés à activité antipaludique confirmée.
- **`All_molecules.csv` / `all_molecules_inputs.csv`**: Fichiers centraux regroupant l'ensemble des molécules issues des différentes sources.
- **`All_mol_selfies.csv`**: Représentations SELFIES des molécules, un format textuel alternatif au SMILES, utilisé pour les modèles génératifs.
- **`all_molecules_prop.csv`**: Contient les propriétés physico-chimiques et ADMET (Absorption, Distribution, Métabolisme, Excrétion, Toxicité) calculées pour les molécules.
- **`admet.csv`**: Fichier dédié aux propriétés ADMET.
- **`pains.txt` / `wehi_pains.csv`**: Listes de sous-structures chimiques connues pour interférer avec les tests de criblage biologique (PAINS - Pan-Assay Interference Compounds). Utilisées pour filtrer les molécules indésirables.
- **`generated_dataset.csv` / `generated_data_filt_final.csv`**: Ensembles de données contenant les molécules générées par les modèles d'IA, après filtration.
- **`alphabet.txt`**: Dictionnaire des "mots" (tokens) SELFIES ou SMILES utilisé pour l'entraînement des modèles de deep learning.
- **`test.csv`**: Un sous-ensemble de données utilisé pour les tests.
- **`merged_cheese.csv` / `merged_cheese_clean.csv`**: Résultats de la recherche de similarité avec la base de données ChEMBL (probablement via un outil comme CHEESE).
- **`*.smi_out_...predictions.txt`**: Fichiers de sortie contenant les prédictions d'un modèle.
