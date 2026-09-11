# Abstract Summary for CODATA-RDA Research Data Science Summer School

**Event:** CODATA-RDA Research Data Science Summer School and Advanced Workshops (smr 4320)  
**Location:** ICTP, Trieste, Italy  
**Dates:** November 9-20, 2026  
**Deadline:** September 4, 2026  
**File:** `SAO_abstract.tex` → `SAO_abstract.pdf`

## Workshop Focus vs. Abstract Strategy

**Workshop Topics:**
- AI-assisted Research Data Management (RDM)
- Open and Responsible Research
- Python and AI Coding tools
- Machine Learning and Artificial Neural Networks
- Computational Infrastructure
- AI-assisted Data Analysis
- Urban Data (not relevant to our work)

**Our Strategic Focus:**
Unlike the Addis Ababa biophysics workshop, this CODATA-RDA event emphasizes **data science, computational infrastructure, reproducibility, and open science practices**. The abstract therefore highlights the RDM and computational provenance aspects of P1-P6 rather than molecular biology details.

## Abstract Content Overview

### Title Focus
"Open Research Data Infrastructure for Reproducible Antimalarial Drug Discovery: AI-Assisted Workflows and Computational Provenance"

**Keywords emphasized:** Open, Research Data, Infrastructure, Reproducible, AI-Assisted, Workflows, Computational Provenance

### Authors and Affiliations
**Complete Author List (from P1 V7):**
1. **Myke Vital Sao Temgoua** (presenting author, underlined) - Department of Physics, University of Yaoundé I, Cameroon
2. **Jean-Pierre Tchapet Njafa** - Department of Physics, University of Yaoundé I, Cameroon
3. **Penabei Samafou** - Université de Sherbrooke, Canada
4. **Wilfred Fon Mbacham** - Department of Biochemistry, University of Yaoundé I, Cameroon
5. **Serge Guy Nana Engo** - Department of Physics, University of Yaoundé I, Cameroon

## Key Messages by Workshop Topic

### 1. AI-Assisted RDM (Primary Focus)
**What we present:**
- Fail-closed validation gates preventing invalid data progression
- Versioned computational artifacts with SHA256 hashes
- Machine-readable audit trails for 15,000+ computational jobs
- Separation of exploratory vs. validated results in JSON manifests
- Frozen scripts and locked dependencies for reproduction

**Why it matters:** Demonstrates industrial-grade RDM practices in academic research

### 2. Python and AI Coding Tools
**What we present:**
- Python automation for SLURM HPC job arrays
- PyTorch Geometric for graph neural networks
- Transformer encoders (ChemBERTa)
- Version-controlled conda environments
- Trajectory QC pipelines

**Why it matters:** Shows practical AI/ML implementation in scientific workflows

### 3. Open and Responsible Research
**What we present:**
- Preregistered analysis protocols
- Public deposition plans (Zenodo with reserved DOIs)
- FAIR-compliant metadata schemas
- Honest-negative benchmarking (reporting when novel methods fail)
- Transparent computational cost reporting

**Why it matters:** Exemplifies responsible science with negative results published

### 4. Computational Infrastructure
**What we present:**
- Open-source tools (OpenFF, scikit-learn, RDKit)
- Deployable on modest HPC resources
- GPU-accelerated workflows (GROMACS 2025.4)
- 99.3% cost reduction through optimization
- Suitable for African research institutions

**Why it matters:** Shows how to do cutting-edge science with limited resources

### 5. Machine Learning & Neural Networks
**What we present:**
- Graph Neural Networks (GIN architecture)
- Transformer-based molecular encoders
- Quantum-inspired topological descriptors
- Honest benchmarking (classical baselines vs. novel methods)
- Human-verifiable decision boundaries

**Why it matters:** Demonstrates responsible AI where interpretability is maintained

## Scale and Scope Highlighted

**Data Scale:**
- 65,856 compounds in chemical library
- 19,836 curated activity labels
- 16 MD systems × 10 ns each
- 15,000+ computational jobs tracked
- Multi-project integration (P1-P5)

**Computational Provenance:**
- Software versions documented (GROMACS 2025.4, RDKit, PyTorch)
- Execution environments recorded
- Parameter freezing before execution
- Hash-based artifact verification
- Reproducible workflows

## What's Different from Addis Ababa Abstract

| Aspect | Addis Ababa (Biophysics) | Trieste (Data Science) |
|--------|--------------------------|------------------------|
| **Focus** | Molecular mechanisms, MD simulation physics | RDM infrastructure, computational provenance |
| **Language** | PfDHFR, force fields, binding trajectories | Versioned artifacts, fail-closed gates, FAIR metadata |
| **Results** | Resistance-resilient candidates, RRS classes | 15,000+ tracked jobs, SHA256 hashes, reproducible workflows |
| **Methods** | OpenFF 2.2.0, CHARMM36m, GPU acceleration | Python automation, SLURM arrays, version control |
| **Value Prop** | New antimalarial candidates | Reusable RDM framework for any field |
| **Audience** | Experimental & computational biophysicists | Data scientists, research data managers, AI practitioners |

## Workshop Alignment Score

| Workshop Topic | Relevance | How We Address It |
|----------------|-----------|-------------------|
| AI-assisted RDM | ⭐⭐⭐⭐⭐ | Core focus: fail-closed gates, audit trails, provenance tracking |
| Python & AI Coding | ⭐⭐⭐⭐⭐ | PyTorch, conda environments, SLURM automation |
| Open & Responsible Research | ⭐⭐⭐⭐⭐ | Preregistered protocols, honest-negative results, FAIR metadata |
| Computational Infrastructure | ⭐⭐⭐⭐⭐ | Open-source stack, modest HPC, African context |
| Machine Learning & ANNs | ⭐⭐⭐⭐ | GNNs, transformers, responsible AI practices |
| AI-assisted Data Analysis | ⭐⭐⭐⭐ | Ensemble workflows, human-verifiable decisions |
| Unix Environments | ⭐⭐⭐ | Implicit (SLURM, conda, version control) |
| Author Carpentry | ⭐⭐⭐ | Implicit (manuscript preparation, citations) |
| Urban Data | ⭐ | Not relevant to our work |

**Overall Alignment: 90%** - Excellent fit for 8/9 workshop topics

## Unique Value Propositions

**1. Real-World Scale:**
Not a toy dataset - 65K compounds, 15K jobs, multi-year project

**2. Honest Science:**
Reports negative results (quantum methods didn't win, MCTS didn't beat random)

**3. Resource Awareness:**
Designed for African institutions with modest computational resources

**4. Reusability:**
Framework is field-agnostic - applicable beyond drug discovery

**5. Complete Provenance:**
Every result traceable to frozen inputs, locked dependencies, versioned code

**6. AI Responsibility:**
Maintains human-verifiable decision boundaries despite using AI

## Format Compliance

✅ One page (including references)  
✅ LaTeX article class with template specifications  
✅ Title capitalized  
✅ Author affiliations with superscripts  
✅ Presenting author underlined  
✅ References formatted correctly  
✅ PDF ready (90 KB)

## References Strategy

**Four citations covering:**
1. **P1 (RRS/Polypharmacology)** - Main computational framework, provenance practices
2. **P5 (GNN)** - Machine learning and neural network applications
3. **P3 (Quantum-inspired)** - Python automation, version control, honest benchmarking
4. **P4 (MCTS)** - AI-assisted workflows, optimization

## Poster Presentation Strategy

**For the poster, emphasize:**

### Section 1: RDM Infrastructure
- Flowchart: Data → Validation Gates → Versioned Artifacts → Audit Trail
- Example: SHA256 hash verification workflow
- Metric: 15,000+ jobs with complete provenance

### Section 2: AI-Assisted Workflows
- Diagram: SLURM orchestration of parallel jobs
- Python code snippets (clean, well-commented)
- Tools: PyTorch, conda, version control

### Section 3: Open Science Practices
- FAIR principles implementation
- Zenodo deposition workflow
- Honest-negative results table (methods that didn't win)

### Section 4: Computational Infrastructure
- Resource requirements vs. results achieved
- Cost reduction strategies (99.3% via optimization)
- Deployment on modest HPC

### Section 5: Reproducibility
- Before/after comparison: ad-hoc vs. systematic provenance
- Independent reproduction checklist
- Version control best practices

## Audience Engagement Points

**For Data Scientists:**
"How do you ensure 15,000 jobs remain reproducible across years?"

**For AI Practitioners:**
"How do you balance AI automation with human verification?"

**For RDM Professionals:**
"What's your fail-closed validation gate architecture?"

**For Open Science Advocates:**
"How do you handle honest-negative results in publications?"

**For African Researchers:**
"How deployable is this on limited HPC resources?"

**For Python Developers:**
"Show me your conda environment lock and version control workflow"

## Key Talking Points

1. **Scale:** Not a demo - production RDM for real research
2. **Honesty:** We publish when methods fail (quantum, MCTS)
3. **Automation:** Python orchestrates everything, humans verify decisions
4. **Provenance:** Every result traceable to frozen inputs
5. **Openness:** Zenodo deposition, FAIR metadata, open-source stack
6. **Accessibility:** Works on modest HPC typical of African institutions
7. **Reusability:** Framework applicable to any computational science field

## Differentiation from Other Posters

**Likely other posters will show:**
- Urban data analysis (we don't have this - skip those discussions)
- Social science RDM (we have hard computational science)
- Small-scale Python tutorials (we have production-scale workflows)

**Our unique angle:**
- **Industrial-grade RDM in academic research** (15K jobs, SHA256 hashes, fail-closed gates)
- **Honest-negative AI benchmarking** (we report when novel methods lose)
- **Resource-constrained reproducibility** (designed for African HPC constraints)
- **Multi-year, multi-project integration** (P1-P5 with consistent provenance)

## Success Metrics for the Poster Session

**Engagement indicators:**
- Questions about reproducibility workflows
- Interest in fail-closed validation gates
- Requests for Python code/scripts
- Discussions about resource-constrained RDM
- Connections with open science initiatives
- Potential collaborations on RDM infrastructure

**Follow-up opportunities:**
- Share Zenodo DOI when deposited
- Provide GitHub repo for RDM scripts
- Connect with CODATA/RDA working groups
- Discuss African research infrastructure needs

## Technical Depth to Prepare

Be ready to discuss:
1. **Validation gates:** How do you prevent bad data from propagating?
2. **Version locking:** conda, pip freeze, container strategies
3. **Provenance tracking:** JSON manifests, hash verification
4. **SLURM automation:** Job arrays, dependency management
5. **FAIR metadata:** Schema design, implementation
6. **Honest benchmarking:** When to report negative results
7. **Cost optimization:** 99.3% reduction strategies
8. **Reproducibility testing:** How to verify independent reproduction

This abstract positions your work as a **model RDM infrastructure** for computationally intensive research, emphasizing practices that are workshop-central (data management, provenance, reproducibility, open science) rather than domain-specific results (antimalarial candidates).
