# Journal des implémentations — Project2 Polypharmacology_MD_ValidationV2607 (24–25 août 2026)

## 1. Audit adversarial & manuscrit
- Prompt adversarial régénéré (183 lignes, §1bis standards externes: Roux&Chipot JPCB2024, JCAMD2026, DDDT2025, DEKOIS2.0, PfCRT Kim2019 Nature).
- PASS1 verdict C-P2-01..08 ; passes 2–4 : tous corrigés dans V2607.tex (+SM) — voir AUDIT_MITIGATIONS_P2_20260824.md (passes 2/3/4bis/4 + passe figures).
- R1–R10 referees sévères traités ; R5 clause 400/900 remplacée par divulgation honnête (aucune donnée multi-seuils).
- Références : +6 canon ancrés (Jakalian2002, Kollman2000, Hou2011, RouxChipot2024, Spangenberg2013, Fidock2000) ; Kim2019PfCRT ajouté.
- Section « Data curation » créée (exigence JCIM) ; Data availability ajoutée (R10).

## 2. Données & DAR
- Chaîne post-production canonisée (manifest v3, 16/16, qc=0, md_rrs=0) dans BMAD_Q1_DATA_ANALYSIS_REPORT.md + P2_DATA_ANALYSIS_REPORT.md §5bis (couverture PP-01/PP-02 Classe A ; MM-GBSA 16 lignes = 12 mutantes + 4 WT, 8>100 % = rétention-pas-gain).
- CORRECTION DU 25 AOÛT (preuve disque) : les logs défaillants sont 15384 et **15385** (erreurs MDAnalysis XTCReader.timespan vérifiées par grep) ; le wrapper réussi est **15386**. Les mentions inverses (« 15386 cassé → autorité 15385 ») héritées du 24 août ont été retournées dans BMAD DAR, P2 DAR, AUDIT_MITIGATIONS et README. Les runbooks du 25 août avaient déjà la bonne attribution.

## 3. Figures
- rmsd_representative.pdf (stub 317 o) → figure3_rmsd_stability.pdf ; PPI_network.pdf (vectoriel vide) → PPI_network.png ; balayage rendu poppler (syntaxe `-r 40`) : 11/11 figures saines (% encre documentés).
- Répertoire canonique unique : manuscript/LaTeX/Graphics (transfert+fusion depuis ../Graphics, supprimé) ; \graphicspath SM élargi {{Graphics/}{../Graphics/}} ; recompiles propres.

## 4. Hygiène & cohérence
- Overfulls/siunitx/detect-all purgés (main+SM+cover letter 0 err/o/u ; cover letter 1 page marge 2 cm).
- README.md + SUBMISSION_MANIFEST.md (checksums sha256 recalculés) réalignés sur l'état canonique.
- Racine Malaria_codesV2 rangée ; strays renvoyés aux projets ; _unsorted_legacy créé.

## Passe lightweight (25 août 2026) — runs 1→2→3 exécutés (env `malaria_md`, seed 42)

| Run | Résultat clé |
|---|---|
| R8/1 ΔΔG±SD | 12 mutants tabulés (`results/lightweight_robustness/mmgbsa_ddeltaG_pilot.csv`); IC95 excluant zéro : **1/12** (0 affaiblissement significatif, 1 renforcement, max \|ΔΔG\|=5.37) → confirme « rétention, pas gain » |
| R9/2 Corrélation partielle | n=12 (panneau complet bi-cible) : ρ brut(PNS,RRS)=−0.2098 → ρ partiel \|MW+prévalence Murcko\|=**−0.6154** ; l'association se RENFORCE après conditionnement → non-artefact taille/scaffold (TDA compagne NON disponible localement — quantité propre au manuscrit, étiquetée honnête) |
| R3/3 Bootstrap classes | B=10⁴ sur n=17 : A* [0.118,0.529], B [0.118,0.529], C [0.118,0.529], D [0.000,0.176] ; fraction mutants MMG>100 % : 0.667 IC95 [0.417,0.917] ; pas de σ par score (CSV single-score → bootstrap cohorte uniquement, étiqueté honnête) |

Script: `scripts/lightweight_runs_20260825.py`; sorties: `results/lightweight_robustness/{mmgbsa_ddeltaG_pilot.csv, partial_corr_input_table.csv, lightweight_runs_summary.json}`.

## Audit léger Projets 1/3/4/5 (25 août 2026)

- **P1 V7 (déjà soumis, cible ACS)** — balayage existence uniquement : paquet de soumission intact dans `submission_ACS_P1V7/` (main PDF, Cover_Letter_P1_V7.pdf, Figure_3, etc.). Manifest = document de statut sans checksums → aucune retouche. Manuscrit sous revue non touché.
- **P3 Quantum-Inspired** — ligne canonique = **V4** (résultats actifs 08-25) ; V2607/V2 laissés en l'état (superseded, non supprimés). V4 ne contient aucun fichier md → rien à auditer.
- **P4 Monte-Carlo V2 (déjà soumis, Journal of Cheminformatics)** — manifest descriptif sans hashes ; sources LaTeX présentes (`P4_Pareto_MCTS_JoC_refined.tex` + SM). PDFs du paquet trouvés localement : 0 fichier(s) Pareto*, 1 cover-letter PDF — paquet déjà parti vers le journal.
- **P5 GNN-Transformer — pipeline complet : PASS.** Compilation main 0 err / 0 overfull / 0 undef + cover letter propre ; \title + abstract présents ; **3/3 figures saines et rendues** (PDF 13 p., XObject 3/3, rasters 3) ; DAR bien tenu (checkpoints « superseded » correctement étiquetés, framing honest-negative assumé) ; `SUBMISSION_MANIFEST.md` réparé (3 lignes sha256/taille recalculées : manuscrit, cover letter, bib ; note « Verified 25 August 2026 » ajoutée). Zenodo : statut « reserved, upload pending » honnête conservé.

Aucun manuscrit déjà soumis (P1/P3/P4/P5) n'a été modifié dans cette passe.
