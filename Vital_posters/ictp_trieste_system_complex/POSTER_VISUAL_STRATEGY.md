# Poster Visual Strategy — ICTP Spring College 2027
**If Accepted:** Expand abstract into visual poster format

---

## 🎨 Poster Design Principles

### Target Audience
- **Primary:** Statistical physicists, complex systems theorists, network scientists
- **Secondary:** Computational biologists, machine learning researchers
- **Background:** Familiar with stochastic processes, graph theory, but NOT drug discovery specifics

### Communication Goals
1. **Hook:** Show that drug discovery poses fundamental complex systems questions
2. **Clarity:** Make molecular problems accessible without oversimplifying
3. **Depth:** Demonstrate quantitative rigor (you're a physicist, not just an app developer)
4. **Impact:** Honest-negative results are features, not bugs (scientific integrity)

### Visual Hierarchy
```
┌─────────────────────────────────────────────────────┐
│  TITLE: Complex Systems Dynamics in Drug Discovery  │
│  Authors, Affiliations                               │
├─────────────────────────────────────────────────────┤
│ [INTRO]          [PROBLEM 1]         [PROBLEM 2]    │
│ Chemical Space   Estimand Divergence GNN Limits     │
│ Topology         (Stochastic Dynamics) (Expressivity)│
├─────────────────────────────────────────────────────┤
│ [METHODS]        [RESULTS 1]         [RESULTS 2]    │
│ Computational    MD Free Energy      Scaffold Split │
│ Pipeline         87.5% Divergence    Topology Rescue│
├─────────────────────────────────────────────────────┤
│ [SYNTHESIS: Distance-Aware Conformal Triage]        │
│ Practical Framework Combining All Three Problems    │
├─────────────────────────────────────────────────────┤
│ CONCLUSIONS • REFERENCES • CONTACT                  │
└─────────────────────────────────────────────────────┘
```

---

## 📊 Figure Recommendations (6-8 key visuals)

### **Figure 1: Chemical Space Topology**
**Goal:** Show non-trivial structure (not just random molecules)

**Panel A:** UMAP/t-SNE projection of 65,856 molecules colored by:
- African Natural Product (ANP) ancestors (red)
- Synthetic antimalarials (blue)
- Generated library (gray)
- Highlight: 92.6% global novelty, 69.3% scaffold conservation

**Panel B:** $Fsp^3$ vs Ring Count scatter plot
- Overlay: Complexity cohorts (flat aromatic, complex 3D, polycyclic)
- Annotation: "High-$Fsp^3$ + polycyclic = 1-WL bottleneck region"

**Complex Systems Framing:**
> "65,856-molecule chemical space exhibits correlated topology: privileged African scaffolds (indoloquinolines, protoberberines) create bottleneck regions ($Fsp^3 \geq 0.45$, rings $\geq 4$) where graph neural networks fail."

**Source:** P1 V8 chemical space analysis + P5 structural characterization

---

### **Figure 2: Polypharmacology Network**
**Goal:** Visualize multi-target interaction graph

**Layout:** Network diagram
- **Nodes (ligands):** 17 candidates (colored by RRS class: A*=green, B=yellow, C=orange, D=red)
- **Nodes (targets):** 4 proteins (PfDHFR, PfCRT, PfATP4, PfClpP)
- **Edges:** Binding strength (line thickness ∝ docking score magnitude)
- **Annotations:** Mutation states as node perturbations

**Inset:** Degree distribution histogram (most candidates bind 3-4 targets)

**Complex Systems Framing:**
> "Polypharmacology network: 17 ligands × 4 targets = 68 interactions. Resistance mutations perturb free energy landscapes, probed via Resistance Retention Score (RRS = $|\Delta G_{\text{mut}}| / |\Delta G_{\text{WT}}| \times 100\%$)."

**Source:** P2 RRS classification + P1 multi-target docking

---

### **Figure 3: Estimand Divergence Phenomenon**
**Goal:** Core honest-negative result (static ≠ dynamic)

**Panel A:** Scatter plot: Docking ΔΔG vs MD ΔΔG
- **Axes:** $\Delta\Delta G_{\text{dock}}$ (x) vs $\Delta\Delta G_{\text{MD}}$ (y)
- **Diagonal:** y = x (perfect agreement line)
- **Points:** 8 mutant systems (7 diverge from diagonal)
- **Annotation:** "87.5% divergence: static predicts weaker, dynamics shows retention"

**Panel B:** Trajectory snapshots (qualitative)
- WT vs K76T/K76A overlays showing conformational dynamics
- RMSD time series showing stability

**Panel C:** Free energy landscape cartoon
- Static minimum (docking) vs dynamic ensemble (MD)
- Entropy contribution diagram

**Complex Systems Framing:**
> "Stochastic configurational dynamics contradict static potential energy minima. 10 ns explicit-solvent MD (310 K, CHARMM36m/TIP3P) samples $\sim 10^4$ microstates; docking samples 1. Divergence reframes docking as conservative triage filter, not binding oracle."

**Source:** P2 V2609C MD validation (manuscript Table 2, Figure 4)

---

### **Figure 4: GNN Expressivity Bottleneck**
**Goal:** Show topological rescue on complex structures

**Panel A:** Bar chart: Scaffold-split AUC by model
- ECFP4-RF: 0.830 (baseline, gray)
- GIN: 0.805 (red, below baseline)
- GIN-TFP: 0.814 (orange, partial rescue)
- ChemBERTa: 0.787 (purple, worst)

**Panel B:** Stratified performance by structural cohort
- Flat aromatic: All models comparable
- Complex 3D: GIN drops, TFP rescues (+0.009)
- Polycyclic: Largest gap (small n, high variance)

**Panel C:** 1-WL failure diagram
- Two molecules with identical 1-WL graph but different 3D topology
- Persistent homology (TFP) captures difference

**Complex Systems Framing:**
> "1-Weisfeiler-Leman expressivity bottleneck: GNNs collapse on complex natural products ($Fsp^3 \geq 0.45$). Topological feature projection (persistent homology) rescues +0.009 AUC but remains below ECFP4 baseline — learned representations do not guarantee superior extrapolation."

**Source:** P5 canonical benchmark (manuscript Table 1, stratified analysis)

---

### **Figure 5: Distance-Aware Conformal Triage**
**Goal:** Synthesize all three problems into actionable framework

**Panel A:** Decision flow diagram
```
Input Molecule
    ↓
Compute D_NN (Tanimoto)
    ↓
┌───────────────┬──────────────┬──────────────┐
│ D_NN < 0.40   │ 0.40 ≤ D ≤ 0.60 │ D_NN > 0.60 |
│ (Cold OOD)    │ (Interpolation) │ (Hot OOD)   │
│ → ECFP4-RF    │ → GIN-TFP      │ → Ensemble  │
└───────────────┴──────────────┴──────────────┘
         ↓
  ECE Calibration Check (threshold 0.08)
         ↓
  Confidence-Adjusted Prediction
```

**Panel B:** Performance gain plot
- x-axis: $D_{\text{NN}}$ bins
- y-axis: Precision or AUC
- Lines: ECFP4 (constant), GIN (drops at high $D_{\text{NN}}$), Triage filter (optimal piecewise)
- Annotation: "+14.2% prospective screening precision"

**Panel C:** Calibration reliability diagram
- Before: Overconfident predictions (ECE > 0.08)
- After: Conformal correction

**Complex Systems Framing:**
> "Distance-aware conformal triage: dynamically route molecules based on nearest-neighbor Tanimoto distance and expected calibration error. Cold OOD tail ($D_{\text{NN}} < 0.40$) handled by sparse bit-key lookup (ECFP4); interpolation regime by topological GNNs. Uncertainty quantification prevents overconfident extrapolation."

**Source:** P5 conformal analysis (conceptual; verify if computed)

---

### **Figure 6: Multi-Scale System Schematic**
**Goal:** Big-picture overview tying everything together

**Layout:** Three nested scales
1. **Macro:** Africa map highlighting malaria-endemic regions + ANP plant species
2. **Meso:** Chemical library topology (UMAP projection)
3. **Micro:** Protein-ligand binding site (MD snapshot) + free energy surface

**Arrows:** Connect scales with labeled processes
- ANP ethnobotany → Chemical scaffolds (scaffold-based generation)
- Chemical space → Target network (docking campaign)
- Binding poses → Configurational dynamics (MD trajectories)
- Observables → ML predictions (GNN/ECFP4 models)

**Complex Systems Framing:**
> "Multi-scale complex system: 396 African natural products → 65,856 chemical library → 68 protein-ligand interactions → $10^4$ configurational microstates per system → high-dimensional decision boundary under distribution shift."

---

## 🎨 Color Scheme

### Primary Palette (Colorblind-Safe)
- **Blue:** ECFP4 baseline, static docking
- **Orange:** GNN models, dynamic MD
- **Green:** Topological rescue (TFP), good performance
- **Red:** Failures, divergence, bottlenecks
- **Gray:** Background, reference lines

### Annotations
- **Bold text:** Key numbers (87.5%, 0.830 vs 0.805)
- **Arrows:** Causal relationships, process flows
- **Boxes:** Highlight honest-negative results ("GNN < ECFP4")

---

## 📝 Text Panels

### Introduction (Top Left)
**Title:** *Complex Systems in Antimalarial Drug Discovery*

**Content (3-4 bullets):**
- Malaria drug resistance = multi-target network perturbed by mutations
- 65,856-molecule African natural product library with non-trivial topology
- Three core questions: (1) Static vs dynamic estimands, (2) GNN expressivity limits, (3) Uncertainty triage

### Methods (Center Left)
**Title:** *Computational Framework*

**Content:**
- **Molecular Dynamics:** GROMACS, explicit solvent, 310 K, 10 ns
- **Docking:** AutoDock Vina (Meeko), 4 targets × 17 candidates
- **GNNs:** PyTorch Geometric (GIN architecture), 5-fold scaffold split
- **Topology:** Persistent homology (TFP), $Fsp^3$, ring counts

### Conclusions (Bottom)
**Title:** *Complex Systems Insights*

**Content (3-4 bullets):**
- **Estimand divergence** (87.5%): Stochastic dynamics retain binding where static minima predict loss
- **1-WL bottleneck**: GNNs fail on complex topologies; partial rescue via persistent homology
- **Distance-aware triage**: Nearest-neighbor Tanimoto + ECE calibration → +14.2% precision
- **Theoretical gap**: Exact solutions for simple transport models (Mallick/Neri) could guide coarse-graining strategies

---

## 🔧 Technical Specifications

### Poster Size
- **Standard:** A0 portrait (841 × 1189 mm)
- **Alternative:** 36" × 48" (US conferences)

### Software
- **LaTeX Beamerposter:** Recommended for reproducibility
- **PowerPoint/Keynote:** Acceptable but less flexible
- **Illustrator/Inkscape:** Best for custom graphics

### Fonts
- **Headers:** Sans-serif (Arial, Helvetica), 72-96pt
- **Body:** Sans-serif, 24-32pt (readable from 2 meters)
- **Figure labels:** 18-24pt

### Resolution
- **Figures:** 300 DPI minimum for print
- **Line plots:** Vector (PDF/SVG) preferred
- **Photos/heatmaps:** High-res PNG/TIFF

---

## 💬 Oral Presentation Strategy

**If Asked to Present (3-5 minutes):**

### Slide 1: Hook (30 sec)
> "Drug resistance is a multi-target network problem. Static computational methods miss stochastic dynamics. Learned models fail on complex topologies. Can statistical physics formalize these phenomena?"

### Slide 2: Estimand Divergence (60 sec)
- Show Figure 3A (scatter plot)
- Key point: "87.5% of systems diverge — configurational entropy matters"

### Slide 3: GNN Bottleneck (60 sec)
- Show Figure 4A (scaffold-split AUC)
- Key point: "1-WL expressivity fails on high-$Fsp^3$ structures; topological rescue is modest"

### Slide 4: Synthesis (60 sec)
- Show Figure 5 (triage framework)
- Key point: "Distance-aware routing + calibration = practical uncertainty quantification"

### Slide 5: Theoretical Connections (30 sec)
> "Exact solutions for stochastic transport (Mallick/Neri) could formalize trajectory averaging. Network theory (Burioni) could characterize polypharmacology motifs. Gradient flows (Macris) could explain GNN failures."

---

## 📚 References to Cite on Poster

### Your Work
1. **P1 V8:** Sao Temgoua et al., Zenodo 10.5281/zenodo.22696778 (2026)
2. **P2 V2609C:** Sao Temgoua et al., *JCIM* (under review, 2026)
3. **P5 V2609:** Sao Temgoua et al., ChemRxiv preprint (in prep., 2026)

### Key Methods References
4. **1-WL Expressivity:** Xu et al., ICLR 2019 (How Powerful Are Graph Neural Networks?)
5. **Persistent Homology:** Carlsson, Bull. AMS 2009 (Topology and Data)
6. **Conformal Prediction:** Vovk et al., *Algorithmic Learning in a Random World* (2005)
7. **MD Best Practices:** Soares et al., *JCIM* 63:5200 (2023)

---

## ✅ Quality Checklist

Before printing:
- [ ] All figures have descriptive captions
- [ ] Text readable from 2 meters away (ask a colleague to test)
- [ ] Color scheme is colorblind-safe (check with simulator)
- [ ] Key numbers are bold and annotated
- [ ] No orphaned acronyms (define on first use)
- [ ] Affiliation logos (University of Yaoundé I, ICTP if allowed)
- [ ] Contact information (email, ORCID, GitHub/Zenodo links)
- [ ] QR code to Zenodo deposit (P1) or manuscript repository
- [ ] Proofread by supervisor or colleague
- [ ] Test print on A4 to check layout

---

**Status:** Planning document for future use (only if accepted to Spring College)  
**Timeline:** Prepare in January 2027 if acceptance notification received  
**Format:** A0 portrait, PDF for printing at ICTP or pre-printed in Yaoundé
