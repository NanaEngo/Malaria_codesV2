# Bantou 2027 Campus France Proposal

## Overview

This is a research proposal for the **PHC BANTOU 2027** program (France-Cameroon Scientific Cooperation), focusing on **Hybrid Quantum-Classical Machine Learning for African Natural Products Drug Discovery**.

---

## Key Information

**Project Title:** Hybrid Quantum-Classical Machine Learning for African Natural Products Drug Discovery: A Computational Framework for Antimalarial Development

**Program:** PHC BANTOU 2027 (Campus France)

**Duration:** 1 year (2027)

**Total Budget:** €15,000 (€7,500 French side + €7,500 Cameroonian side)

**Document:** `Bantou_2027_Proposal.tex` (16-page LaTeX proposal)

---

## Scientific Focus

### Central Hypothesis

Can hybrid quantum-classical machine learning architectures capture the three-dimensional structural complexity of African natural products (ANPs) that classical fingerprints and quantum-inspired methods miss, thereby improving antimalarial activity prediction and scaffold generalization?

### The ANP Challenge

African natural products are structurally complex:
- **High Fsp³** (>0.5 vs. 0.3-0.4 for synthetic drugs)
- **Multiple stereocenters** (chiral centers, E/Z configurations)
- **3D polycyclic scaffolds** (macrocycles, ring fusions)
- **Conformational flexibility** (defeats static docking)

### Why Classical Methods Fail

1. **P1/P2:** Static docking → 87.5% divergence with MD simulations (ANP flexibility)
2. **P3:** Quantum-inspired methods lose stereochemistry (QKS ≈ RBF, no advantage)
3. **P5:** GNN 1-WL bottleneck on scaffold splits (AUC 0.649 < ECFP4-RF 0.689)

### P7 Solution: True Quantum ML

- **Quantum Molecular State Encoding (QMSE):** Preserves stereochemistry, bond topology, 3D geometry
- **Hybrid Architectures:** QFE, Q-GNN, QKT for ANP structure capture
- **ANP-Stratified Evaluation:** Determine when quantum helps vs. classical suffices
- **Computational Accessibility:** QKT enables CPU-only inference for African labs

---

## Proposal Structure

### 1. Scientific Background (Section 1)
- Malaria burden in Africa
- ANP structural uniqueness and ethnobotanical heritage
- Computational limitations of classical methods
- Quantum ML as principled solution

### 2. Preliminary Work (Section 2)
- **P1:** Chemical space exploration (65,856 library, 69.3% ANP scaffold conservation)
- **P2:** MD validation (87.5% docking-MD divergence on ANPs)
- **P3:** Quantum-inspired representations (honest-negative: no advantage)
- **P4:** Monte Carlo optimization (random > MCTS on scaffolds)
- **P5:** GNN bottleneck (0.649 scaffold split, ANP defeat 1-WL)

### 3. Proposed Research (Section 3)
- **Aim 1:** QMSE development (BondOrderMatrix, Coulomb matrix)
- **Aim 2:** Hybrid architectures (QFE, Q-GNN, QKT)
- **Aim 3:** ANP-stratified evaluation (ACSI quartile analysis)
- **Aim 4:** Scaffold generalization validation (target AUC > 0.70)

### 4. Methodology (Section 4)
- Datasets: P1 Set A (n=20), P3 benchmark (19,849), external (10K)
- Software: Qiskit, PennyLane, PyTorch, RDKit, GROMACS
- Quantum hardware: IBM Quantum (127-qubit Eagle), NISQ error mitigation
- Statistical framework: Three distinct estimands (accuracy, encoding fidelity, generalization)

### 5. Work Plan (Section 5)
- **Phase 1 (Mo 1-4):** QMSE development + Mobility 1 (France → Cameroon)
- **Phase 2 (Mo 5-8):** Hybrid training + Mobility 2 (Cameroon → France)
- **Phase 3 (Mo 9-11):** External validation + Mobility 3 (France → Cameroon)
- **Phase 4 (Mo 12):** Dissemination + Mobility 4 (Joint conference)

### 6. Budget (Section 6)
- French: 4 mobilities + computing + workshop (€7,500)
- Cameroonian: 2 mobilities + ANP database + ethnobotany + workshop (€7,500)

### 7. Impact (Section 7)
- **Scientific:** First true QML for ANPs, honest assessment framework
- **Translational:** Antimalarial candidates, traditional medicine validation
- **Capacity:** African quantum computing expertise, Franco-Cameroonian network
- **Cultural:** Honor ethnobotanical heritage, equitable benefit-sharing

### 8. Team (Section 9)
- French: PIs (quantum ML, comp chem), PhD/postdoc (1)
- Cameroonian: PIs (natural products, ethnobotany), PhD (1)
- Joint supervision, co-authorship, shared IP

---

## Alignment with PHC Bantou Priorities

✓ **Excellence:** Cutting-edge quantum ML + urgent African health challenge  
✓ **New collaborations:** Novel quantum-ANP partnership  
✓ **Young researchers:** Central role for PhD students (4 mobilities, training, co-authorship)  
✓ **Structuring:** Open-source tools, training materials, joint supervision  
✓ **EU integration:** Aligns with Horizon Europe (quantum tech, global health)  
✓ **Accessibility:** QKT designed for resource-limited settings  

---

## Key Deliverables

### Scientific Outputs
1. Peer-reviewed manuscript (high-impact journal: JCIM, JCAMD, npj Comp Mat, Digital Discovery)
2. Open-source software: `qml-anp` package (Python, BSD license, documented)
3. Benchmark dataset: ANP-stratified antimalarial activities with ACSI annotations
4. Technical report: Quantum hardware performance comparison

### Training Outcomes
1. 2 PhD students trained (1 French, 1 Cameroonian)
2. 1 postdoc trained in ANP computational chemistry
3. Joint supervision framework established

### Capacity Building
1. Workshop: "Quantum Machine Learning for African Drug Discovery"
2. Computational infrastructure roadmap for Cameroonian institutions
3. Franco-Cameroonian quantum computing working group

---

## Honest-Negative Commitment

Following P3 precedent, **all three outcomes are valid scientific results:**
- **Quantum advantage:** ΔAUC ≥ 0.01, p < 0.05 → publish advantage
- **Quantum equivalence:** |ΔAUC| < 0.01 or p > 0.05 → publish equivalence (honest-negative)
- **Quantum underperformance:** ΔAUC < -0.01, p < 0.05 → publish limitation and identify root cause

**Goal:** Determine *when* and *how* quantum helps ANPs, not claim universal advantage.

---

## Key References (From Preliminary Work)

### P1: Chemical Space (JCIM submission V8)
- 65,856 hybrid ANP-synthetic library
- DEKOIS 2.0 validation, MMV enrichment
- Zenodo DOI: 10.5281/zenodo.22696778

### P2: MD Validation (JCIM ready V2609C)
- 87.5% docking-MD estimand divergence
- OpenFF 2.2.0 + CHARMM36m/TIP3P
- 39-ligand GNINA CNN validation

### P3: Quantum-Inspired (JCAMD ready V2609)
- QKS ≈ RBF, no advantage (honest-negative)
- ECFP4-RF baseline 0.9475
- Root cause: flattened features lose stereochemistry

### P5: GNN Bottleneck (JCAMD ready)
- Scaffold split: GNN 0.649 < ECFP4-RF 0.689
- 1-WL expressivity limitation on high-Fsp³ ANPs
- Topological fusion modestly complementary

---

## Timeline

| Phase | Months | Key Activities | Mobility |
|-------|--------|----------------|----------|
| **Phase 1** | 1-4 | QMSE development, P1 Set A validation | France → Cameroon (2 weeks) |
| **Phase 2** | 5-8 | Hybrid training, ACSI-stratified eval | Cameroon → France (2 weeks) |
| **Phase 3** | 9-11 | External validation, scaffold split | France → Cameroon (1 week) |
| **Phase 4** | 12 | Manuscript, code release, workshop | Joint conference |

---

## Next Steps

### Before Submission (Deadline: TBD 2026)

1. **Team finalization:**
   - Identify French PI and co-investigators
   - Identify Cameroonian PI and co-investigators
   - Confirm institutional support letters

2. **Budget refinement:**
   - Confirm airfare estimates (Yaoundé ↔ Paris)
   - Finalize per diem rates (French/Cameroonian standards)
   - Secure ANP database licensing quotes

3. **Online submission:**
   - Campus France ECLECTUS platform
   - Co-deposit requirement (both sides)
   - Supporting documents upload

4. **Cameroonian coordination:**
   - MINRESI notification
   - Parallel Cameroonian submission process

### After Submission

- Evaluation: Joint Franco-Cameroonian selection committee (Mid-2027)
- Notification: Results via Campus France extranet (TBD 2027)
- Project start: March 15 - December 31, 2027

---

## Contact Information

### French Side
**Campus France - PHC Management**  
28, rue de la Grange aux Belles  
75010 Paris, FRANCE  
Tel: +33 (0)1 40 40 58 48  
Email: phc@campusfrance.org

### Cameroonian Side
**Ministère de la Recherche Scientifique et de l'Innovation (MINRESI)**  
Direction des relations extérieures et institutionnelles  
Yaoundé, Cameroon

### Scientific Attachés
**Stéphanie Mailleз Viard** (Attachée de Coopération Scientifique et Universitaire)  
**Cédric Mayrargue** (Conseiller Technique Recherche & Innovation)  
French Embassy in Cameroon

---

## Acknowledgments

This project will be supported by the **"PHC BANTOU"** program, funded by:
- French Ministry for Europe and Foreign Affairs (MEAE)
- French Ministry for Higher Education, Research and Space (MESRE)
- Cameroonian Ministry for Scientific Research and Innovation (MINRESI)

---

## Document Files

- **LaTeX source:** `Bantou_2027_Proposal.tex`
- **Compiled PDF:** `Bantou_2027_Proposal.pdf` (16 pages, 360 KB)
- **This README:** `Bantou_2027_Proposal_README.md`

---

**Last Updated:** September 25, 2026  
**Status:** Draft ready for team review and institutional approval

---

## How to Compile

```bash
# Compile LaTeX to PDF
pdflatex Bantou_2027_Proposal.tex
pdflatex Bantou_2027_Proposal.tex  # Run twice for cross-references

# Or use latexmk
latexmk -pdf Bantou_2027_Proposal.tex
```

---

## Notes for Customization

Before final submission, update:
1. **Team names and institutions** (Section 9)
2. **Budget details** (Section 6) with actual quotes
3. **Mobility dates** (Section 5) based on team availability
4. **Institution support letters** as required by Campus France
5. **CV attachments** for PIs and co-investigators
6. **Publication list** demonstrating preliminary work (P1-P5 status)

---

**For questions or collaboration inquiries, contact the project coordinators.**
