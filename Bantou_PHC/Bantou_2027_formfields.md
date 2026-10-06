# Bantou 2027 — ECLECTUS form-field drafts

**Source:** `Bantou_2027_ProposalV261005.tex` (V261005, 6 October 2026)
**Limit:** 10 000 characters per field (spaces + line breaks + paragraphs included). Guardrail used here: **≤ 9 500 characters**.
**Language:** English (allowed). French equivalent can be produced on request.
**Author note:** text in `[[...]]` = fill before submission (team names, cooperation history). Numbers marked *check* = verify against final frozen data.

---

## Field 1 — Context and history (Contexte et historique)

**Target section:** V2 §1 + §2 + cooperation-history paragraph
**Characters:** 3 475

---

Malaria remains a devastating public health burden in sub-Saharan Africa. According to the WHO World Malaria Report 2025, the WHO African Region carried about 94% of global malaria cases (265 million of an estimated 282 million cases) and about 95% of malaria deaths (579,000 of an estimated 610,000 deaths) in 2024. Resistance to frontline antimalarials (chloroquine, sulfadoxine-pyrimethamine, artemisinin combinations) is spreading; novel multi-target scaffolds are urgently needed.

African natural products (ANPs) are an underexplored resource for this challenge. They combine high molecular complexity (Fsp3 often > 0.5, multiple stereocenters, polycyclic cores) with documented ethnobotanical antimalarial use (Cryptolepis sanguinolenta, Enantia chlorantha, Nauclea latifolia; Bero et al., 2009). AfroDb freely provides 3D structures for 1,008 natural products from African medicinal plants with a wide range of reported activities, antimalarial among them (Ntie-Kang et al., 2013). Yet classical computational chemistry systematically under-serves this chemical space.

Our team has completed five computational studies that map this failure precisely:

1. Chemical-space exploration: a 65,856-compound hybrid ANP-synthetic library with 69.3% scaffold conservation; 92.6% of molecules unreachable by ECFP4 similarity search; validated by DEKOIS 2.0, MMV enrichment and redocking (RMSD < 2.0 A). Full manuscript completed and validated; Zenodo DOI 10.5281/zenodo.22696778 (public); journal submission in progress following an editorial decision in September 2026.
2. Molecular dynamics validation: 16 protein-ligand systems (25 ns, OpenFF/CHARMM36m) showed 87.5% divergence between docking scores and MD-derived binding free energies — docking misses ANP flexibility. GNINA deep-learning rescoring agreed on 100% of Class-A ligands. Companion manuscript technically ready (current revision).
3. Quantum-inspired representations: quantum kernels and topological encodings showed NO quantum advantage over classical ECFP4-RF on a 19,849-molecule antimalarial benchmark (0.8876 vs 0.9475). Root cause: quantum-inspired methods re-encode flattened classical fingerprints and lose ANP stereochemistry. Honest-negative result; manuscript claim-calibrated, submission package ready (target: Journal of Computer-Aided Molecular Design).
4. Monte Carlo exploration: random sampling beat MCTS (AUC 0.6724 vs 0.6649) on scaffold-based multi-objective benchmarks.
5. Graph neural networks: on Bemis-Murcko scaffold splits, GNNs underperformed ECFP4-RF (AUC 0.649 vs 0.689). Root cause: 1-WL message passing cannot distinguish stereoisomers or ring fusions in high-Fsp3 ANPs.

Together, these studies demonstrate that classical fingerprints and quantum-inspired variants both lose the structural information that defines ANP bioactivity. True quantum machine learning with direct molecular encoding is the missing piece — the object of this proposal.

**History of Franco-Cameroonian cooperation** [[TO COMPLETE: date and venue of first meeting; previous visits/exchanges; joint publications to date; letters of support; ongoing co-supervision]]. The two teams bring complementary and genuinely two-sided expertise: French partners contribute quantum computing, ML and computational chemistry infrastructure; Cameroonian partners contribute ethnobotanical knowledge, governance of ANP metadata, local deployment of CPU-only pipelines, and connection to malaria-endemic communities.

---

## Field 2 — Project objectives (Objectifs)

**Target section:** V2 Abstract + §3 (hypothesis + aims)
**Characters:** 2 683

---

**Central hypothesis.** Hybrid quantum-classical machine-learning architectures that encode ANP topology and stereochemistry directly at the quantum-circuit level improve scaffold-generalization AUC by at least ΔAUC ≥ 0.02 over the classical ECFP4-RF baseline (AUC = 0.689), with the largest gains in the highest African-Chemotype Structural Index (ACSI) quartile; architectures that merely re-encode classical fingerprints will fail to exceed this margin.

This hypothesis is falsifiable. Pre-declared estimands, repeated scaffold-split statistics (≥10 seeds), DeLong/bootstrap confidence intervals, and TOST equivalence testing (margin ±0.01) will classify every outcome as advantage, equivalence, or underperformance. An honest-negative result — no quantum gain — remains a publishable scientific outcome (precedent: Study 3).

**Specific aims.**

Aim 1 (guaranteed): Quantum Molecular State Encoding (QMSE). Implement BondOrderMatrix encodings (bond orders, E/Z and R/S stereochemistry) and Coulomb-matrix 3D encodings (Rupp et al., 2012; Boy et al., 2025), mapped to quantum circuits in 2^n Hilbert space. Validate by kernel target alignment on the frozen 19,849-molecule benchmark and its ACSI-stratified ANP-rich subset; Set A (n=20) serves only as feasibility demonstration.

Aim 2 (QKT guaranteed; QFE/Q-GNN stretched): Hybrid architectures. (i) Quantum Feature Extractor — trainable PQC + classical readout (stretched); (ii) Quantum GNN — stretched objective; (iii) Quantum Kernel Transfer (guaranteed) — quantum kernels on ANP-rich subsets, then O(n) CPU-only inference on the full benchmark, designed for resource-limited African laboratories. Hyperparameter optimization runs on simulators only; hardware validation is a pre-declared subset, subject to IBM Quantum allocation.

Aim 3 (guaranteed): ANP-stratified evaluation. We define the ACSI a priori as a purely molecular score (weights fixed before training):

ACSI = 0.40 * Fsp3 + 0.30 * min(n_stereo/6, 1) + 0.30 * min(n_ring_atoms/15, 1)

Botanical origin is NOT part of the score (avoiding circularity); it is a separate stratification variable. Quartiles Q1–Q4 test whether quantum gains concentrate in high-ACSI (ANP-like) chemical space.

Aim 4 (stretched): Scaffold generalization. Repeated Bemis-Murcko splits on the frozen benchmark and an external ~10k set (InChIKey disjointiveness protocol, SHA-256 manifests). Success: ΔAUC ≥ +0.02 vs ECFP4-RF (0.689) with 95% CI excluding zero.

**Translational scope.** This is a computational project with no bioassay partner. It delivers a prioritized, ACSI-annotated candidate list plus an experimental validation protocol for a follow-on project — not IC50 data.

---

## Field 3 — Project description / methodology / planning (Description du projet)

**Target section:** V2 §4 + §5 + §6
**Characters:** 4 871

---

**Data and provenance.** Datasets: Study 1 Set A (n=20, feasibility only); Study 3 benchmark (19,849 molecules with antimalarial labels, internal ChEMBL-derived set; ChEMBL, Mendez et al., 2019); external validation (~10k) built from public collections (ChEMBL assays + AfroDb), frozen at a declared cut-off date. Disjointiveness protocol: compute InChIKeys across all sets, report molecule-level overlap (target: zero), freeze manifests with SHA-256 checksums before training. No checksum is claimed in this draft; manifests are generated at project start.

**Software.** Qiskit, PennyLane (IBM Quantum, subject to research allocation); PyTorch, scikit-learn, PyTorch Geometric; RDKit, OpenFF, GROMACS; Python/pandas/NumPy/SciPy.

**Cameroonian technical work packages (genuine two-way complementarity).**
- WP-CM1: ethnobotanical and ACSI annotation governance — Cameroonian team leads curation and QC of botanical-origin and traditional-use metadata.
- WP-CM2: local deployment and benchmarking of the CPU-only qml-anp pipeline on Cameroonian institutional infrastructure (demonstrates the accessibility claim end-to-end).
- WP-CM3: joint analysis, co-authorship, co-supervision of the Cameroonian PhD candidate.
- WP-CM4: ethics-governed ethnobotanical field protocol (institutional approval, informed consent, anonymization).

**Statistical framework (pre-declared).**
- Estimand 1 (accuracy): ΔAUC vs ECFP4-RF on repeated scaffold splits (≥10 seeds); 95% bootstrap CIs + DeLong tests (DeLong et al., 1988). Advantage: ΔAUC ≥ 0.01 with CI excluding 0 (minimal-advantage category; the project-level success threshold for the central hypothesis is ΔAUC ≥ 0.02, Estimand 3). Equivalence: TOST margin ±0.01 (Lakens, 2017) — non-significance alone is not equivalence. Underperformance: ΔAUC ≤ −0.01 with CI excluding 0.
- Estimand 2 (encoding fidelity): kernel target alignment stratified by ACSI quartiles, gradient Q1→Q4 with bootstrap CIs. Success criterion (Aim 1): Δalignment ≥ +0.05 vs ECFP4 on the ANP-rich subset with bootstrap 95% CI excluding zero.
- Estimand 3 (scaffold generalization): ΔAUC vs ECFP4-RF on repeated Bemis-Murcko splits; success threshold ΔAUC ≥ +0.02, CI excluding 0.

**Ethics.** Nagoya Protocol principles apply where traditional knowledge informs compound selection (prior informed consent / mutually agreed terms, where applicable). Ethnobotanical interviews: institutional ethics approval, informed consent, anonymization. Databases (AfroDb, ANPDB, ChEMBL) are freely downloadable — no licence-fee budget line. Public code/data deposits are subject to PPST (intellectual-property) review before release.

**Work plan 2027 (civil year; start 15 March, end 31 December; funds non-carried-over; PHC-funded mobilities run only on the France–Cameroon corridor; engagement forms ≥3 weeks before departure).**

- Phase 1 (Mar–Jun): QMSE encodings; kernel alignment on benchmark + ANP subset; Set A feasibility. Mobility 1 (FR→CM, May, 8 d, solo): PI FR. Mobility 2b (CM→FR, Jun, 8 d, solo): PI CM.
- Phase 2 (Jul–Oct): QKT training (guaranteed core), QFE/Q-GNN as resources allow (stretched); ACSI quartile analysis; HPO on simulators. Mobility 1b (FR→CM, Jul, 15 d, solo): postdoc FR. Mobility 2 (CM→FR, Aug, 21 d, solo): Cameroonian PhD candidate (dedicated training mobility). Mobility 3a (FR→CM, Sep, 21 d, solo): PhD FR; hosts the joint workshop "QML for African Drug Discovery" in Cameroon (costs: laboratory means). Co-investigators participate by videoconference at no PHC cost.
- Phase 3 (Oct–Dec): repeated scaffold-split external validation; FR/CM comparative report. Mobility 4 (CM→FR, Nov, 15 d, solo): Cameroonian postdoc.
- Phase 4 (Nov–Dec + final report ≤3 months): manuscript, GitHub/Zenodo release (post-PPST), final joint analysis meeting (videoconference). International conference presentations: laboratory means / other grants (not PHC).
- Final scientific and financial report (French PI: Campus France model via ECLECTUS; Cameroonian PI: MINRESI format) due ≤3 months after project end.

**Budget compliance.** PHC funds cover mobility only on the France–Cameroon corridor, each envelope financing its own team's travellers (FR→CM trips paid by France; CM→FR trips paid by Cameroun). Each mobility is a solo trip costed bottom-up at the official Bantou rates (senior 125 EUR/day, stays 5–14 d; junior 62 EUR/day, stays 15–30 d; ticket budgeted 1,200 EUR against the 1,500 EUR ceiling): 6,732 EUR per face + 768 EUR airfare contingency = the full envelope. France ≤7,500 EUR across 3 solo mobilities (M1 PI 8 d; M1b postdoc 15 d; M3a PhD 21 d). Cameroun ≤7,500 EUR across 3 solo mobilities (M2b PI 8 d; M2 PhD 21 d; M4 postdoc 15 d), including 2 dedicated PhD mobilities across the two faces. Third-country conference travel and all other costs sit in laboratory co-financing (4,800 EUR indicative), outside the request.

---

## Field 4 — Perspective / expected results (Perspective et résultats attendus)

**Target section:** V2 §7 + §8 + §9 + §11
**Characters:** 2 561

---

**Scientific impact.** (i) Among the first genuine quantum-ML pipelines for ANP chemical space, moving beyond quantum-inspired re-encodings of classical fingerprints. (ii) An honest-assessment framework: advantage, TOST-tested equivalence, and limitation are all reportable outcomes. (iii) Direct attack on the 1-WL scaffold-generalization bottleneck (Study 5) via non-local quantum representations. (iv) A reusable, CPU-only quantum-kernel-transfer workflow designed for African laboratories.

**Translational impact.** Deliverables are a ranked, ACSI-annotated list of ANP-derived antimalarial candidates and a ready-to-use experimental validation protocol (IC50, resistance profiling) for a follow-on project with an experimental partner. The project does not itself promise bioassay data. Computational evidence will also support — and ethically contextualize — ethnobotanical antimalarial knowledge, following Nagoya principles.

**Capacity building and structuring.** Joint supervision of 2 PhD candidates (1 French, 1 Cameroonian; recruitment in progress) with dedicated training mobilities; open-source qml-anp deposited with Zenodo DOI, containers, and tutorials; CPU-only deployment on Cameroonian infrastructure; French-Cameroonian quantum-ML working group linked to European networks.

**European integration (programme priority).** EuroQCI-affiliated quantum-chemistry workshops and the international conference slot (workshops joinable by videoconference from each side); Horizon Europe alignment at the intersection of Cluster 4 (quantum technologies) and Cluster 1 (health); follow-on Horizon Europe and ANR-MINRESI proposals built on this bilateral base; the same theme may be resubmitted to other bilateral PHC-type programmes, as the call allows.

**Risks and realism.** Guaranteed scope = Aim 1 + Aim 3 + QKT (QMSE, ACSI stratification, quantum-kernel transfer). QFE/Q-GNN training and the full 10k validation are pre-declared stretched objectives (Risk 3). If IBM Quantum allocation is not granted in time, core estimands complete on simulators and hardware validation is reported as NOT_COMPUTED. If quantum methods show no advantage, the ACSI-stratified analysis still identifies where classical methods suffice — a publishable honest-negative result.

**Sustainability.** Open data/code (post-PPST), joint authorship, co-tutelle pathway, roadmap for computational infrastructure in Cameroonian institutions, and a pan-African quantum-ML-for-health network. All publications will acknowledge MEAE/MESRE/MINRESI and the PHC project number.

---

## Pre-submission checklist (author)

- [ ] Fill all `[[...]]` and `[TO COMPLETE]` fields (teams, cooperation history, letters of support)
- [ ] Verify frozen-data figures (19,849 / 0.689 / 0.649) still match final frozen manifests
- [ ] French version of the four fields if the MINRESI evaluation reads French
- [ ] ECLECTUS initiated by the French partner ≥48 h before 29 Oct 2026
- [ ] Confirm with MINRESI whether a parallel national filing is required
- [ ] Declare **resoumission Oui/Non** in ECLECTUS (Oui if any PHC/Bantou-type proposal was filed by either team in a previous cycle; Non otherwise)
- [ ] Select **domain of research** among the 10 ECLECTUS choices — suggested: computational chemistry / cheminformatics, machine learning, quantum computing/information, natural products, tropical diseases/public health
- [ ] **Keywords** for ECLECTUS (suggested): African natural products; antimalarial drug discovery; quantum machine learning; molecular encoding; scaffold generalization; computational accessibility; Franco-Cameroonian collaboration
- [ ] Attachments in JPG/GIF/PNG/PDF (unprotected) only; PDF of this proposal only if the form allows
- [ ] Engagement forms filed ≥3 weeks before each mobility (PHC-funded mobilities = France–Cameroon corridor only)
