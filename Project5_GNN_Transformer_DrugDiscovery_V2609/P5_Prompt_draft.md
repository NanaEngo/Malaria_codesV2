# Teamwork Project Prompt — Refined (P5 V2609)

* **Status:** Ready for Execution / Teamwork Pipeline
* **Goal:** Produce a publication-ready LaTeX manuscript, Supporting Information package, and Cover Letter for Project 5 (P5 V2609) targeting *Journal of Computer-Aided Molecular Design* (JCAMD) / *Journal of Chemical Information and Modeling* (JCIM) with >95% acceptance probability.

---

### Title & Framing

**Canonical Title:** *Deconstructing Out-of-Distribution Extrapolation in Molecular Deep Learning: Structural Complexity, Topological Rescue, and Conformal Triage on African Antimalarial Natural Product Scaffolds*

---

### Core Scientific Thesis & 3 Pillars

1. **Theoretical Biophysical Cause (1-WL Expressivity Limit & PNA Complexity):**
   - Message-passing graph neural networks (e.g., GIN) are theoretically bounded by the 1-Weisfeiler-Lehman (1-WL) graph isomorphism test.
   - When evaluating African Natural Products (ANPDB / AfroDb) enriched in high fraction of $sp^3$ carbons ($F_{\text{sp3}} \ge 0.45$), complex polycyclic cores ($\ge 4$ rings), and stereocenters, local message aggregation induces manifold over-smoothing.
   - Multiscale topological descriptors (**GIN-TFP / Persistent Homology** $H_0, H_1$) inject a global topological inductive bias, restoring 36% of the raw GNN extrapolation deficit under scaffold splits ($\text{ROC-AUC} = 0.8138$ for GIN-TFP vs $0.8047$ for base GIN).

2. **Actionable Conformal Triage Protocol ($D_{\text{NN}} + \mathrm{ECE}$):**
   - **Cold OOD Tail ($D_{\text{NN}} < 0.40$, Deciles D1–D4):** Sparse bit fingerprints (**ECFP4-RF**) remain mandatory ($\text{ROC-AUC} = 0.779$ vs $0.752$ for GIN-TFP at decile D1).
   - **Familiar Chemistry / Interpolation ($0.40 \le D_{\text{NN}} \le 0.60$, Deciles D5–D8):** Statistical parity ($\Delta \text{AUC} \in [0.001, 0.007]$). **GIN-TFP** deployed safely.
   - **Calibration Guardrail ($\mathrm{ECE} > 0.08$):** Expected Calibration Error doubles under domain shift ($0.03 \to >0.12$). Requires Platt scaling/recalibration when breached.
   - **Operational Impact:** Boosts prospective virtual screening precision by **+14.2%**.

3. **Methodological Anti-Leakage Standard & Capacity Defense:**
   - **Anti-Leakage Protocol:** Fold-independent weight reset for molecular transformers (**ChemBERTa**) prior to each cross-validation fold.
   - **GNN Capacity Audit (SLURM Job 15617):** Scaling hidden dimensions ($h = 64, 128, 256$) and dropout ($0.1, 0.2$) bounds scaffold performance strictly between $0.8000$ and $0.8081$, proving the deficit is architectural (1-WL limits) rather than sub-optimal hyperparameter tuning.

---

### Requirements

#### R1. Submission-Ready LaTeX Package
- Produce self-contained LaTeX files for Main Manuscript (`Project5_GNN_Transformer_Antimalarial_main_V2609.tex`), Supporting Information (`Project5_GNN_Transformer_Antimalarial_SM_V2609.tex`), and Cover Letter (`Cover_Letter_P5_JCAMD.tex`).
- Must compile with 0 errors, 0 undefined citations, and 0 broken cross-references (`??` or `[?]`).

#### R2. Ethnobotanical Anchoring & Lineage Tracing
- Deeply ground the narrative in African Antimalarial Natural Products (19,836 expanded library molecules derived from 396 ANPDB / AfroDb seeds).
- Cite specific African medicinal flora (*Cryptolepis sanguinolenta*, *Enantia chlorantha*, *Nauclea latifolia*) and phytochemical classes (indole alkaloids, prenylated chromones, prenylated isoflavonoids, quassinoids).
- Explicitly trace lineage to companion studies P1 (polypharmacology RRS, ChemRxiv:10.26434/chemrxiv.15006437/v2) and P3 (topological/quantum representations, ChemRxiv:10.26434/chemrxiv.15007167/v1).
- Highlight the **ANPDB Scaffold Paradox**: 92.6% whole-molecule novelty ($Tanimoto < 0.40$) coexisting with 69.3% privileged African ring core retention.
- Emphasize computational sovereignty: 99.3% compute overhead reduction (1,936 centroid evaluations vs 263,000 full-matrix calculations) enabling high-throughput screening on regional academic HPC clusters (e.g., `penavoraserver`, Univ. Yaoundé I).

#### R3. Comprehensive Tables, Vector Graphics, and Code Listing
- **Table 1:** Benchmark performance across Random Split, Canonical Scaffold Split, and Butina Cluster Split ($C=0.55$).
- **Table 2:** Structural Complexity Breakdown ($F_{\text{sp3}} < 0.25$ vs $F_{\text{sp3}} \ge 0.45$ vs Rings $\ge 4$).
- **Table 3:** $NN$-Tanimoto Decile Stratification (D1–D10).
- **Executable Code:** Include the `conformal_triage_filter` Python function in Section S6 of the Supporting Information.

#### R4. Flawless Academic Prose, Citation Depth & Cover Letter Alignment
- Maintain strict academic tone free of internal report jargon, meta-commentary, or non-peer-reviewed phrasing.
- **Minimum Citation Threshold:** The manuscript must contain **at least 35–40 verified academic references** covering recent 2024–2026 foundation model benchmarks, topological deep learning, antimalarial pharmacopoeia, ANPDB, and companion papers P1/P3.
- Cover letter must highlight the 1-WL expressivity resolution on 3D PNA scaffolds, the +14.2% screening precision gain, and include 3 suggested international reviewers.

---

### Acceptance Criteria

- [ ] `pdflatex` compilation of Main and SI packages completes with exit code 0.
- [ ] Output PDFs contain zero broken links (`??`) and zero missing citations (`[?]`).
- [ ] Abstract is concise (<250 words) with zero in-text citations.
- [ ] Introduction explicitly states P1 and P3 DOI citations and ANPDB/AfroDb plant species.
- [ ] The bibliography contains at least 35 verified academic citations in BibTeX format.
- [ ] Table 2 shows GIN collapse ($0.773$) and GIN-TFP rescue ($0.811$, $+0.038$ gain) on high $F_{\text{sp3}}$ / polycyclic scaffolds.
- [ ] Conformal Triage Filter is mathematically formalized in main Methods (§5.4) and executable RDKit Python code is provided in SI (§S6).
- [ ] GNN Capacity Defense (Job 15617) is documented in Discussion (§3.4) and SI (§S3).
- [ ] Cover Letter is generated with 3 suggested international reviewers.
