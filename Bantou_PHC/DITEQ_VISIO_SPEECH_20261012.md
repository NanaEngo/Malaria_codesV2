# SPEECH VISIO DITEQ – PHC BANTOU 2027
**Date:** 12 octobre 2026, 14h00  
**Interlocuteur:** Frédéric (équipe DiTeQ, ICB UMR 6303)  
**Durée estimée:** 45–60 minutes

---

## **INTRODUCTION (2–3 minutes)**

*"Bonjour Frédéric, merci beaucoup d'avoir accepté cet échange aussi rapidement. Je suis ravi de pouvoir discuter avec l'équipe DiTeQ."*

*"Rapidement sur mon parcours : j'ai fait mon Master en Physique à Yaoundé 1, spécialisé en théorie quantique et information quantique. Mon projet de Master portait sur un réseau de neurones quantiques basé sur une mémoire associative quantique pour le diagnostic médical rapide. Ça m'a donné une base solide en QML, mais j'ai vite réalisé que beaucoup de ces modèles restaient très théoriques."*

*"Depuis 18 mois, j'ai pivoté vers un problème concret : la découverte de médicaments antipaludiques à partir de produits naturels africains. Et ce pivot m'a forcé à être beaucoup plus rigoureux : j'ai dû valider mes protocoles, publier des résultats négatifs, et remettre en question mes hypothèses initiales sur le quantum machine learning. C'est exactement ce parcours que je voudrais vous présenter aujourd'hui, parce qu'il m'amène à DiTeQ pour des raisons très précises."*

---

## **SLIDE MENTALE 1 : ÉCHEC DE GÉNÉRALISATION SCAFFOLD (4–5 minutes)**

*"Laissez-moi commencer par le problème de fond. En drug discovery computationnelle, on utilise massivement des modèles de machine learning pour prédire si une molécule va se lier à une protéine cible — donc prédire son activité biologique."*

*"Les approches standards aujourd'hui, ce sont les empreintes moléculaires 2D — typiquement ECFP4, qui encode un graphe moléculaire en vecteur binaire de 2048 bits — et plus récemment les Graph Neural Networks, les GNN, qui font du message passing sur le graphe moléculaire."*

*"Le problème, c'est que ces modèles performent très bien en interpolation — c'est-à-dire quand les molécules de test ressemblent beaucoup aux molécules d'entraînement — mais s'effondrent en extrapolation structurale."*

*"J'ai mesuré ça précisément dans mon Projet 5. J'ai utilisé un scaffold split de Bemis-Murcko : on sépare les molécules selon leur squelette structural core. Donc les scaffolds du set de test n'ont jamais été vus pendant l'entraînement. C'est l'estimand le plus dur en drug discovery, mais c'est exactement ce qu'on veut : généraliser vers de nouvelles familles chimiques."*

*"Résultat : mon meilleur GNN, un AttentiveFP qui fait du message passing avec mécanisme d'attention, atteint une AUC de 0,649. C'est en dessous de mon baseline ECFP4 avec un Random Forest classique, qui donne 0,689. Donc le GNN, malgré toute sa sophistication, perd 4 points d'AUC sous scaffold split."*

*"Pourquoi ? Parce que les GNN, même avec du message passing, restent fondamentalement des algorithmes 1-WL — Weisfeiler-Leman de premier ordre. Ils agrègent des voisinages locaux sur un graphe 2D topologique. Ils n'encodent pas la géométrie 3D. Ils ne voient pas les stéréocentres. Ils aplatissent toute la stéréochimie en topologie de graphe."*

*"Et ça devient dramatique quand on travaille sur les produits naturels africains — les ANPs, African Natural Products. Ces molécules ont typiquement un Fsp³, fraction sp³, entre 0,22 et 0,50 — donc beaucoup de carbones tétraédriques — et 3 à 5 stéréocentres. Ce sont des molécules chirales, tridimensionnelles, avec une complexité structurale énorme."*

*"Mon hypothèse, c'est que cette perte de généralisation n'est pas un problème de données ou d'overfitting. C'est un problème de représentation : les descripteurs 2D et les GNN 1-WL ne peuvent structurellement pas capturer l'information stéréochimique nécessaire pour extrapoler vers de nouveaux scaffolds chiraux."*

### Résultats clés à mentionner :
- **P5 scaffold split:** GNN AttentiveFP AUC = 0.649 vs ECFP4-RF AUC = 0.689
- **ANPs:** Fsp³ = 0.22–0.50, 3–5 stéréocentres typiques
- **Diagnostic:** Problème de représentation, pas de données

---

## **SLIDE MENTALE 2 : VALIDATION STRUCTURE-BASED RIGOUREUSE (4–5 minutes)**

*"Maintenant, avant d'aller plus loin, je veux vous montrer que je ne travaille pas dans le vide. J'ai un cadre de validation très rigoureux."*

*"Mon Projet 1 — qui est maintenant à sa version V8, techniquement prêt pour soumission — c'est un pipeline complet de criblage virtuel structure-based sur quatre cibles parasitaires du Plasmodium falciparum : PfDHFR, PfCRT, PfATP4 et PfClpP. Ce sont des protéines à structures résolues, avec des mécanismes d'action documentés."*

*"J'ai construit des grilles de docking pour chacune, validées par redocking : je prends le ligand co-cristallisé, je le redocke, et je mesure le RMSD entre la pose prédite et la pose expérimentale. Toutes mes grilles donnent un RMSD inférieur à 2,0 Ångströms. Donc mes boîtes de docking sont géométriquement correctes."*

*"Ensuite, j'ai fait un benchmark externe avec DEKOIS 2.0 sur PfDHFR. DEKOIS, c'est une base de leurres exigeants — des molécules qui ressemblent physico-chimiquement aux actifs mais qui ne se lient pas. C'est le gold standard pour tester si un protocole de docking discrimine vraiment."*

*"Mon résultat : AUC de 0,45, avec un intervalle de confiance entre 0,37 et 0,53. C'est un résultat négatif. Mon protocole Meeko uniforme ne discrimine pas les actifs des leurres DEKOIS. Je l'assume complètement, c'est publié dans mon manuscrit."*

*"Pourquoi je vous dis ça ? Parce que ça montre que je ne suis pas là pour embellir mes résultats. Quand un benchmark externe échoue, je le documente et j'explique pourquoi."*

*"Projet 2, c'est la validation par dynamique moléculaire. J'ai pris 16 systèmes : deux composés leaders multipliés par quatre états de mutation des cibles PfDHFR et PfCRT. J'ai fait tourner 10 nanosecondes de MD explicite avec GROMACS, solvant explicite TIP3P, champ de force OpenFF 2.2.0 pour les ligands et CHARMM36m pour les protéines."*

*"Ensuite j'ai calculé les énergies de liaison avec MM/PBSA, et j'ai utilisé un classifieur CNN 3D — GNINA — pour prédire les poses de liaison à partir des trajectoires MD."*

*"Résultat : sur mes Class-A — les composés avec le meilleur score de docking et les meilleures prédictions MD — j'ai 100% d'accord entre le docking statique et la validation MD. Mais sur les autres classes, j'ai 87,5% de divergence : 28 systèmes sur 32 ne sont pas d'accord entre docking et MD."*

*"Et c'est là que j'ai fait un pivot conceptuel. Au lieu de voir cette divergence comme une invalidation, je la traite comme un filtre de triage. Le désaccord MD/docking devient un signal : 'attention, cette molécule a un comportement dynamique complexe, elle mérite une analyse expérimentale prioritaire.' C'est un changement d'estimand."*

*"Donc mes deux piliers de validation : docking structure-based avec benchmark externe négatif assumé, et MD validation sur 16 systèmes avec divergence documentée. Je ne prétends pas prédire l'activité phénotypique in vivo. Je reste strictement dans le cadre du binding computationnel."*

### Résultats clés à mentionner :
- **P1 V8:** 4 cibles (PfDHFR, PfCRT, PfATP4, PfClpP)
- **Redocking:** RMSD < 2.0 Å (toutes cibles validées)
- **DEKOIS 2.0 externe:** AUC = 0.45 [0.37, 0.53] — résultat négatif assumé
- **P2 MD validation:** 16 systèmes × 10 ns, Class-A 100% accord, divergence 87.5% (28/32) autres classes
- **Pivot conceptuel:** Divergence MD/docking = filtre de triage, pas invalidation

---

## **SLIDE MENTALE 3 : PHASE EXPLORATOIRE P7 RATÉE (3–4 minutes)**

*"Maintenant, parlons de ce que j'ai essayé en quantum machine learning — et pourquoi ça n'a pas marché."*

*"Ma première approche, c'était classique : prendre mes empreintes ECFP4, les encoder dans un circuit quantique variationnel — un VQC, Variational Quantum Classifier — et utiliser les amplitudes de sortie du circuit comme features pour un classifieur."*

*"J'ai obtenu une AUC de 0,8474 sur mon Set A de molécules antipaludiques. Pas mal, non ? Sauf que quand j'ai creusé, j'ai réalisé que ce n'était pas un avantage quantique."*

*"J'ai construit un noyau quantique : une fonction de similarité K_Q entre deux molécules, calculée en mesurant le recouvrement entre leurs états quantiques après passage dans le VQC. Et j'ai comparé ce noyau quantique à un noyau RBF classique — un noyau gaussien standard."*

*"Résultat : les deux noyaux sont équivalents. J'ai fait des tests TOST — Two One-Sided Tests — pour tester statistiquement l'équivalence, et je ne peux pas rejeter l'hypothèse d'équivalence. Autrement dit : mon circuit quantique variationnel ne fait rien de plus qu'un noyau RBF classique bien calibré."*

*"Diagnostic : l'encodage amplitude-based est trop générique. Je prenais mes ECFP4 — qui sont déjà des descripteurs 2D aplatissant la stéréochimie — et je les passais dans un circuit quantique. Mais garbage in, garbage out : si mon input ne contient pas l'information 3D, le circuit quantique ne peut pas la créer ex nihilo."*

*"Donc en octobre dernier, le 6 octobre 2026 précisément, j'ai arrêté cette piste. J'ai archivé toutes ces phases exploratoires avec l'étiquette EXPLORATORY dans mon Data Analysis Report. Pas d'avantage quantique démontré, je ne vais pas continuer dans cette direction."*

*"Et c'est exactement ce pivot qui m'amène à vous aujourd'hui."*

### Résultats clés à mentionner :
- **Phase exploratoire P7 (pré-6-oct-2026):** ECFP4 + VQC, AUC = 0.8474
- **Noyau quantique K_Q ≈ noyau RBF classique K_C** (tests TOST, P3 V2609)
- **Diagnostic:** Encodage amplitude-based trop générique, pas de structure 3D
- **Décision:** Arrêt piste VQC, archivage EXPLORATORY (6 octobre 2026)

---

## **SLIDE MENTALE 4 : PIVOT QMSE STRUCTURE-DIRECT (5–6 minutes)**

*"Mon nouveau pipeline, depuis le refocus du 6 octobre, s'appuie sur un papier récent de Boy et collaborateurs, publié dans Machine Learning: Science and Technology en 2025. Le titre c'est Quantum Molecular State Encoding."*

*"L'idée, c'est de faire un encodage structure-direct : au lieu de partir d'empreintes 2D ou de descripteurs classiques, on part directement de la géométrie 3D de la molécule."*

*"Étape 1 : je prends ma molécule, je génère sa conformation 3D avec RDKit et un champ de force MMFF94 — pas de calcul DFT coûteux, juste une optimisation de géométrie rapide. Ensuite je construis deux matrices : la Bond Order Matrix, qui encode les ordres de liaison et l'aromaticité, et la Coulomb Matrix, qui encode les répulsions électrostatiques entre atomes en fonction de leurs positions 3D."*

*"Étape 2 : ces deux matrices sont passées dans un circuit quantique paramétré — un PQC, Parameterized Quantum Circuit. Ce circuit encode la molécule dans un espace de Hilbert de dimension 2^n, où n est le nombre de qubits. L'encodage préserve la topologie 3D, les stéréocentres, l'aromaticité."*

*"Étape 3 : ce circuit est intégré dans un modèle hybride TensorFlow. Je l'encapsule avec qml.qnn.KerasLayer de PennyLane, je rajoute une couche Dense classique en sortie, et j'entraîne le tout end-to-end avec backpropagation. Le circuit quantique lui-même est entraînable : ses portes de rotation sont des paramètres optimisés par gradient descent."*

*"Pourquoi c'est différent de mon approche précédente ? Parce que l'information 3D entre dès le départ dans le circuit. Je ne passe plus par des empreintes 2D. Je construis un état quantique qui reflète directement la géométrie moléculaire."*

*"Ma question de recherche reformulée est maintenant très précise : 'Est-ce qu'un encodage quantique structure-direct surpasse les descripteurs 3D classiques — comme E3FP, USRCAT, ou Autocorr3D — sur les quartiles de haute complexité ACSI, sous scaffold split ?' "*

*"Parce que je ne suis pas naïf : il existe des descripteurs 3D classiques qui capturent la stéréochimie. E3FP, par exemple, c'est des empreintes 3D basées sur des conformations. USRCAT, c'est de la reconnaissance de forme ultra-rapide avec des moments pharmacophoriques. Ces méthodes marchent."*

*"Donc mon benchmark va inclure ces descripteurs classiques. Si E3FP ou USRCAT suffisent à résoudre mon problème de scaffold split, alors je n'ai pas besoin de QML. Je publierai un papier méthodologique expliquant pourquoi l'encodage quantique n'apporte rien. Résultat négatif honnête, comme pour DEKOIS."*

*"Mais si QMSE surpasse systématiquement les descripteurs 3D classiques — avec un Cohen's d supérieur à 0,5, et des tests TOST montrant une supériorité significative — alors on aura quelque chose d'intéressant. Et surtout, on aura besoin de comprendre théoriquement pourquoi."*

*"Et c'est là que DiTeQ entre en jeu."*

### Pipeline QMSE (Boy et al. 2025) :
1. **Input:** BondOrderMatrix + Coulomb Matrix (géométrie 3D MMFF94, pas DFT)
2. **Circuit quantique QMSE:** PQC PennyLane → encodage Hilbert 2^n (topologie 3D + aromaticité + stéréocentres)
3. **Hybride TensorFlow:** `qml.qnn.KerasLayer` (PQC) + Dense classique, end-to-end trainable

### Question de recherche reformulée :
*"Un PQC structure-direct surpasse-t-il les descripteurs 3D classiques (E3FP, USRCAT, Autocorr3D) sur les quartiles ACSI élevés (complexité africaine) sous scaffold split ?"*

### Benchmark prévu :
- **Descripteurs 3D classiques:** E3FP, USRCAT, Autocorr3D, RDF
- **Baseline 2D:** ECFP4, MACCS
- **Critère:** Cohen's d > 0.5 + tests TOST pour supériorité
- **Si équivalence → résultat négatif honnête publié**

---

## **SLIDE MENTALE 5 : POURQUOI DITEQ — BESOINS PRÉCIS (4–5 minutes)**

*"Voilà pourquoi je vous contacte spécifiquement."*

### **Besoin 1 : Optimisation expressivité PQC**

*"Premier besoin : l'optimisation de l'expressivité des circuits quantiques paramétrés. Mon pipeline QMSE, tel que décrit par Boy et al., c'est un ansatz générique. Mais il y a des dizaines de questions ouvertes : quel ansatz choisir ? Quelle profondeur de circuit ? Quelle structure d'entanglement entre qubits ? Comment éviter les barren plateaus — ces régions où le gradient s'effondre exponentiellement et l'entraînement bloque ?"*

*"Ces questions, ce sont des questions de contrôle quantique. C'est exactement l'expertise de DiTeQ. Vous travaillez sur l'optimisation de circuits NISQ, sur les algorithmes variationnels comme VQE, sur la dynamique moléculaire quantique. Vous savez comment construire des circuits qui restent entraînables à 10, 15, 20 qubits."*

### **Besoin 2 : Formalisation théorique avantage quantique**

*"Deuxième besoin : la formalisation théorique de l'avantage quantique. Si mon QMSE performe mieux qu'E3FP, je dois comprendre pourquoi. Est-ce que c'est vraiment l'expressivité de l'espace de Hilbert 2^n ? Est-ce que c'est parce que le circuit peut capturer des corrélations non locales entre atomes distants en 3D ? Ou est-ce que c'est juste un artefact — plus de paramètres, donc plus de capacité à overfitter ?"*

*"Il y a un cadre théorique rigoureux pour ça, c'est la théorie des noyaux quantiques. Un noyau quantique K_Q, calculé comme le recouvrement entre deux états quantiques, peut avoir une plus grande capacité de séparation qu'un noyau classique K_C si et seulement si il vit dans un Reproducing Kernel Hilbert Space de dimension effective plus élevée. Mais prouver ça formellement, ça demande une expertise en théorie quantique que je n'ai pas seul."*

### **Besoin 3 : Infrastructure simulation haute performance**

*"Troisième besoin : l'infrastructure. Pour entraîner ces modèles hybrides, j'ai besoin de simulateurs quantiques haute performance. Qiskit Aer avec GPU, PennyLane Lightning, éventuellement accès à des backends NISQ réels via TeleMAQ si on veut scale-up après la proof-of-concept. DiTeQ a ces ressources."*

### **Besoin 4 : Benchmarking honnête & co-encadrement rigoureux**

*"Quatrième besoin : le benchmarking honnête. Je veux un co-encadrement qui m'empêchera de revendiquer un avantage quantique s'il n'existe pas. Mes travaux P1 à P7 montrent que je suis capable de publier des résultats négatifs — DEKOIS, équivalence VQC/RBF, divergence MD/docking. Je ne veux pas d'une collaboration où on embelli les résultats pour faire passer du quantum hype. Je veux une rigueur scientifique absolue."*

*"Et c'est pour ça que DiTeQ est le laboratoire idéal. Vous n'êtes pas une équipe qui fait du QML parce que c'est à la mode. Vous faites du contrôle quantique, de l'optimisation de circuits, de la physique quantique fondamentale. Si mon QMSE ne tient pas la route théoriquement, vous allez me le dire. Et c'est exactement ce dont j'ai besoin."*

### Synthèse des besoins DiTeQ :
1. **Optimisation PQC:** Choix ansatz, profondeur, entanglement, éviter barren plateaus
2. **Formalisation théorique:** Quand K_Q > K_C ? RKHS dimension effective ? Corrélations non locales 3D ?
3. **Infrastructure:** Qiskit Aer GPU, PennyLane Lightning, accès TeleMAQ (scale-up)
4. **Rigueur scientifique:** Co-encadrement empêchant quantum hype, publication résultats négatifs si nécessaire

---

## **CONCLUSION & OUVERTURE VERS QUESTIONS (2 minutes)**

*"Donc voilà où j'en suis. J'ai un problème de généralisation validé empiriquement — scaffold split failure sur ANPs complexes. J'ai un pipeline QMSE structure-direct qui préserve la géométrie 3D et que je veux benchmarker honnêtement contre des descripteurs classiques. Et j'ai besoin de l'expertise DiTeQ pour optimiser les circuits, formaliser l'avantage quantique, et m'empêcher de sur-interpréter mes résultats."*

*"Le cadre PHC BANTOU, c'est 7 500 euros par équipe pour financer des mobilités bilatérales en 2027. Moi je viendrais deux ou trois fois à Dijon pour des séjours de deux semaines, on travaillerait ensemble sur l'optimisation des ansatz et l'analyse des résultats. L'équipe camerounaise de son côté gère les données ethnobotaniques, l'indexation ACSI, et la démonstration d'inférence sur infrastructure locale CPU-only."*

*"La deadline ECLECTUS, c'est le 29 octobre. Donc on a deux semaines pour formaliser une lettre d'intention si vous êtes intéressés."*

*"Voilà, je m'arrête là. J'ai hâte d'entendre vos réactions, vos questions, et de voir si ce projet peut trouver sa place chez vous."*

---

## **QUESTIONS À POSER À FRÉDÉRIC**

### Questions techniques :
1. *"Avez-vous déjà travaillé sur des problèmes d'encodage moléculaire en QML, ou principalement contrôle/dynamique ?"*
2. *"Quelle est votre position sur les travaux récents (Huang et al. 2021, Skolik et al. 2021) montrant que les QNN peuvent souffrir de barren plateaus sur des problèmes haute dimension ?"*
3. *"Pensez-vous qu'un PQC structure-direct (Boy et al. 2025) évite ces pièges grâce à l'encodage géométrique ?"*

### Questions collaboration :
4. *"Seriez-vous disposé à co-encadrer ce volet circuit quantique variationnel, ou plutôt en conseil méthodologique ponctuel ?"*
5. *"Le lab a-t-il des doctorants/postdocs actuels travaillant sur VQE/QML avec qui je pourrais échanger ?"*

### Questions PHC BANTOU :
6. *"Avez-vous déjà participé à des programmes PHC (Hubert Curien) ? Le process de dépôt ECLECTUS côté français vous est familier ?"*
7. *"Deadline 29 octobre : est-ce faisable pour vous de co-signer une lettre d'intention avant cette date ?"*

---

## **DOCUMENTS DE RÉFÉRENCE À AVOIR SOUS LA MAIN**

### Documents principaux :
- `Bantou_2027_ProposalV261005.pdf` (proposition complète 24 pages)
- **P7 DAR:** `Project7_Quantum_Molecular_Encoding_QML/P7_DATA_ANALYSIS_REPORT.md` (checkpoint refocus 06-oct-2026)
- **P5 DAR:** `P5_DATA_ANALYSIS_REPORT.md` (scaffold split failure)
- **CV détaillé**

### Figures clés (si disponibles) :
- Courbe ROC P5 : GNN AttentiveFP vs ECFP4-RF sous scaffold split
- Architecture QMSE (Boy et al. 2025, Fig. 1)
- Schéma pipeline hybride TensorFlow + PennyLane

---

## **PIÈGES À ÉVITER**

❌ **Ne pas survendre le quantique** : "Je ne prétends pas que QML résout tout. J'ai des résultats négatifs publiés et je cherche à comprendre *quand* et *pourquoi* ça pourrait marcher."

❌ **Ne pas ignorer les descripteurs 3D classiques** : "Mon benchmark inclut E3FP, USRCAT, Autocorr3D. Si ils suffisent, je publierai un papier négatif QML."

❌ **Ne pas négliger la complexité biologique** : "Je modélise uniquement le binding structure-based 4 cibles. Pas de prétention phénotypique in vivo."

❌ **Ne pas être déférent** : Vous êtes un pair junior qui apporte un problème concret, pas un étudiant qui quémande.

---

## **STRUCTURE TEMPORELLE PROPOSÉE (45–60 min)**

| Temps | Section | Contenu |
|-------|---------|---------|
| 0–5 min | **Intro rapide** | Parcours (Master QML diagnostic médical → pivot drug discovery) |
| 5–15 min | **Le problème** | P5 scaffold split failure + P1/P2 validation rigoureuse |
| 15–25 min | **Phase exploratoire ratée** | VQC amplitude-based (P7 pré-oct) : équivalence, pas avantage |
| 25–35 min | **Pivot QMSE structure-direct** | Boy et al. 2025 → PQC préservant 3D, pourquoi DiTeQ |
| 35–45 min | **Questions techniques** | Barren plateaus, expressivité, benchmark honnête |
| 45–55 min | **Cadre PHC BANTOU** | Timeline, mobilités, co-encadrement |
| 55–60 min | **Next steps** | Lettre d'intention avant 29 oct ? Points à clarifier ? |

---

## **MESSAGE DE CLÔTURE (dernières 2 minutes)**

*"Je cherche un encadrement rigoureux qui m'empêchera de revendiquer un avantage quantique s'il n'existe pas. Mes travaux P1–P7 montrent que je suis capable de publier des résultats négatifs honnêtes. Si QMSE ne surpasse pas E3FP/USRCAT, je publierai un papier méthodologique expliquant pourquoi. Mais si ça marche, on aura un cadre théorique solide pour comprendre *pourquoi* l'encodage Hilbert 2^n aide sur la stéréochimie africaine complexe."*

---

## **CHECKLIST FINALE PRÉ-VISIO**

✅ Relire **P7 DAR §2 refocus checkpoint 06-oct-2026**  
✅ Avoir sous les yeux les AUC précis : P5 GNN 0.649 vs ECFP4-RF 0.689  
✅ Préparer 1–2 questions techniques pointues sur PQC (montre connaissance littérature)  
✅ Vérifier disponibilités semaine prochaine si Frédéric propose follow-up  
✅ Avoir CV + Bantou proposal PDF prêts à envoyer post-visio  

---

## **TON GÉNÉRAL À ADOPTER**

**Confiant mais humble** – Vous avez des résultats solides, mais vous reconnaissez les limites  
**Rigoureux scientifiquement** – Transparence absolue sur les échecs et résultats négatifs  
**Enthousiaste mais réaliste** – Passion pour le QML, mais pas de quantum hype  
**Pair junior, pas suppliant** – Vous apportez un problème concret et cherchez l'expertise contrôle quantique

---

**Bonne visio, Myke ! 🚀**
