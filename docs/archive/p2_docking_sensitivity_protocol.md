# Protocoles docking ciblés — exécution contrôlée

## Multi-seed PP-01 / PP-15

- Utiliser exactement les mêmes récepteurs, grilles, ligand preparation, exhaustiveness et scoring que le run canonique.
- Lancer au minimum 5 seeds indépendantes par couple candidat–cible.
- Conserver chaque sortie dans un répertoire versionné, sans écraser les poses canoniques.
- Rapporter moyenne, écart-type, étendue et fréquence de récupération de la pose canonique.
- Ne pas agréger des scores issus de grilles ou protonations différentes sans les étiqueter.

## PfCRT protonation/pH alternatif

- Conserver le modèle structural et la boîte canoniques.
- Préparer explicitement une condition alternative documentée, par exemple pH 5.2, seulement avec un outil et une version enregistrés.
- Comparer score, contacts et RMSD avec la condition canonique.
- Le résultat est une analyse de sensibilité, pas une preuve de protonation physiologique.

## Garde-fous

- Toute exécution doit être autorisée séparément par l’opérateur.
- Avant lancement : vérifier disponibilité de `run_redock_hpc.sh`, des récepteurs, ligands, grilles et de l’exécutable Vina/GNINA.
- Produire un manifeste contenant commandes exactes, versions, seeds, hash des entrées et statut de chaque run.
- En cas de sortie incomplète, conserver `FAILED` ou `PENDING`; ne jamais compléter les valeurs manuellement.
