# Répliques MD courtes ciblées — protocole prospectif

## Périmètre recommandé

Commencer par PP-01 sur les états WT, PfDHFR mutant et PfCRT mutant les plus directement comparables au dossier canonique. Ajouter PP-15 uniquement après validation du premier lot.

## Paramètres

- Utiliser les systèmes préparés et hashés du périmètre Set-C.
- Conserver CHARMM36m/TIP3P et la déviation OpenFF 2.2.0 AM1-BCC uniquement lorsqu’elle est déclarée et approuvée dans le manifeste.
- Durée exploratoire : 1–2 ns par réplique, avec au moins 3 répliques indépendantes si la capacité GPU le permet.
- Utiliser des seeds distinctes et les inscrire dans le manifeste.
- QC obligatoire : complétude des fichiers, énergie, température, pression, LINCS/NaN, RMSD, RMSF et présence du ligand dans la boîte de liaison.

## Statut scientifique

Ces répliques sont une analyse de stabilité et de reproductibilité, non une estimation convergée de ΔG. Elles ne doivent pas être converties en MD-RRS avant le contrat QC préspécifié et l’analyse complète.

## Exécution

Le script `p2_setc_md_workflow.py` reste en préflight par défaut. Toute exécution doit fournir l’autorisation explicite prévue par `P2_MD_EXECUTE_CONFIRM=I_UNDERSTAND`; aucune commande HPC n’est lancée par ce protocole.
