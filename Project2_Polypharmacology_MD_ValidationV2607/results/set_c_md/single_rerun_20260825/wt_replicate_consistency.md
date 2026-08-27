# PP-01_PfCRT_WT — cohérence inter-réplicats (endpoint MM-GBSA)

- R1 canonique (batch 15320/20260819): -30.61 ± 4.12 kcal/mol (SD, 100 snap.; SEM 0.41)
- R2 rerun (job SLURM 15502): -28.60 ± 4.35 kcal/mol (SD, 100 snap.; SEM 0.43)
- Offset inter-réplicats |R1-R2| = 2.01 kcal/mol (< 1 SD intra-trajectoire de chaque run)
- Moyenne des moyennes ± SD d'échantillon (n=2): -29.61 ± 1.42 kcal/mol
- Caveat honnête: sous hypothèse i.i.d. des frames l'offset dépasserait le SEM combiné naïf (0.59); l'autocorrélation temporelle invalide cette lecture, deux réplicats ne permettent pas de trancher la significativité de l'offset.
- Adoption conservatrice: plancher de bruit empirique inter-réplicats ≈ 2.0 kcal/mol pour l'interprétation des contrastes mutant-vs-WT en réplicas simples.
