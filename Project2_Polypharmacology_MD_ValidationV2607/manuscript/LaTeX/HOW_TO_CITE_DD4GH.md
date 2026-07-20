# How to Consistently Reference dd4gh in Papers 2 & 3

## Overview

The **Drug Design for Global Health (dd4gh)** platform is a critical strategic reference for both papers. It validates your work's relevance, provides context for African-led AI drug discovery, and demonstrates alignment with global health initiatives.

---

## 📝 Citation Format (Use in Both Papers)

### In-Text Citation Examples

**Paper 2 (MD Validation):**
```latex
Our work aligns with emerging global health AI initiatives, including the recently 
launched Drug Design for Global Health (dd4gh) platform by Medicines for Malaria 
Venture (MMV) and deepmirror \cite{mmv2026dd4gh}. By providing the first 
resistance-informed polypharmacological antimalarial candidates from African natural 
products, our pipeline complements dd4gh's mission to democratize AI-driven drug 
discovery for neglected diseases.
```

**Paper 3 (Quantum-Inspired):**
```latex
The recent launch of dd4gh (Drug Design for Global Health) by MMV and deepmirror 
\cite{mmv2026dd4gh,techinformed2026dd4gh} demonstrates the growing recognition that 
AI-powered drug discovery must be accessible to researchers in low- and middle-income 
countries. Our quantum-inspired molecular representation framework provides a 
complementary methodology that can be integrated with dd4gh's predictive and 
generative AI capabilities.
```

---

## 📚 BibTeX Entries (Copy from Bibliography Files)

### Essential dd4gh Citations (Use ALL THREE in Both Papers)

```bibtex
@misc{mmv2026dd4gh,
  author       = {{Medicines for Malaria Venture} and {deepmirror}},
  title        = {Drug Design for Global Health (dd4gh): Free {AI} Platform for Neglected Disease Drug Discovery},
  howpublished = {\url{https://www.mmv.org/news-resources-search/free-ai-drug-discovery-platform-aims-level-playing-field-global-health}},
  year         = {2026},
  month        = mar,
  day          = {31},
  note         = {Accessed: 2026-04-08. Platform: \url{https://dd4gh.ai}}
}

@online{deepmirror2026dd4gh,
  author  = {{deepmirror}},
  title   = {Introducing dd4gh: Drug Design for Global Health},
  url     = {https://www.linkedin.com/posts/deepmirror-ltd_were-excited-to-officially-launch-dd4gh-activity-7444662316685524993-QOt7},
  year    = {2026},
  month   = mar,
  day     = {31},
  urldate = {2026-04-08}
}

@article{techinformed2026dd4gh,
  author  = {{TechInformed}},
  title   = {{MMV}, deepmirror launch free {AI} drug discovery platform},
  journal = {TechInformed},
  year    = {2026},
  month   = mar,
  day     = {31},
  url     = {https://techinformed.com/mmv-deepmirror-launch-free-ai-drug-discovery-platform/},
  urldate = {2026-04-08}
}
```

---

## 🎯 Where to Reference dd4gh in Each Paper

### Paper 2 (MD Validation)

| Section | How to Reference | Purpose |
|---------|------------------|---------|
| **Introduction** | Mention as context for global health AI landscape | Shows awareness of field |
| **Discussion** | Compare your resistance-informed approach with dd4gh's AI capabilities | Positions your work as complementary |
| **Future Directions** | Propose integration of your MD-validated candidates with dd4gh platform | Shows forward-thinking |
| **Conclusion** | Emphasize African-led contribution to dd4gh mission | Highlights impact |

**Example (Introduction):**
```latex
The global health drug discovery landscape is rapidly evolving with the integration 
of artificial intelligence. The recent launch of dd4gh (Drug Design for Global Health) 
by Medicines for Malaria Venture (MMV) and deepmirror \cite{mmv2026dd4gh} represents 
a milestone in democratizing access to AI-powered drug discovery tools for researchers 
in low- and middle-income countries. Building on this momentum, our work provides the 
first comprehensive molecular dynamics validation of polypharmacological antimalarial 
leads derived from African natural product chemical space, with explicit optimization 
against resistance mutations prevalent in African \textit{Plasmodium falciparum} populations.
```

**Example (Discussion):**
```latex
Our resistance-informed design approach complements emerging AI platforms such as 
dd4gh \cite{mmv2026dd4gh,techinformed2026dd4gh}, which combines predictive and 
generative AI for neglected disease drug discovery. While dd4gh provides accessible 
pre-trained models for global health researchers, our pipeline contributes 
experimentally validated binding free energies (MM-GBSA) and resistance resilience 
scores (RRS) for 20 polypharmacological candidates—data that can serve as high-quality 
training sets for next-generation AI models. The integration of our MD-validated 
compounds with dd4gh's active learning framework could accelerate the discovery of 
resistance-resilient antimalarials.
```

---

### Paper 3 (Quantum-Inspired Methods)

| Section | How to Reference | Purpose |
|---------|------------------|---------|
| **Introduction** | Position quantum-inspired methods as complementary to dd4gh's classical AI | Shows breadth of approach |
| **Methods** | Mention dd4gh as potential deployment platform for TDA/tensor methods | Practical application |
| **Discussion** | Compare your 65,856-molecule benchmark with dd4gh's datasets | Validates scale |
| **Future Directions** | Propose integrating TDA/tensor representations with dd4gh models | Collaboration opportunity |

**Example (Introduction):**
```latex
The democratization of AI-driven drug discovery is gaining momentum with initiatives 
such as dd4gh (Drug Design for Global Health) \cite{mmv2026dd4gh,deepmirror2026dd4gh}, 
which provides free access to predictive and generative AI tools for malaria, 
tuberculosis, and neglected tropical disease research. While dd4gh focuses on 
classical machine learning approaches, our work explores quantum-inspired molecular 
representations—topological data analysis, tensor networks, and quantum kernels—that 
capture molecular structure and interactions beyond the reach of traditional 
fingerprints. These methods can complement dd4gh's capabilities by providing richer 
molecular descriptors for activity prediction and virtual screening.
```

**Example (Future Directions):**
```latex
The dd4gh platform \cite{mmv2026dd4gh} uses active learning to continuously improve 
predictions as new experimental data becomes available. Our topological fingerprints 
(TFP) and tensor network embeddings (TNE) could serve as enhanced molecular 
representations within dd4gh's framework, potentially improving activity prediction 
accuracy by 9--13\% over classical ECFP4 fingerprints (Section 3.1). We envision a 
future integration where quantum-inspired descriptors augment dd4gh's pre-trained 
models, providing researchers in resource-limited settings with state-of-the-art 
molecular representations without requiring quantum computing infrastructure.
```

---

## 🔑 Key Facts to Reference

### Platform Details (Safe to Cite)

| Fact | Source |
|------|--------|
| **Full name:** Drug Design for Global Health (dd4gh) | MMV Press Release |
| **Launch date:** March 31, 2026 | All sources |
| **Developers:** MMV + deepmirror (partnership) | MMV, TechInformed |
| **Funding:** Partially supported by Gates Foundation | TechInformed |
| **Platform URL:** https://dd4gh.ai | deepmirror LinkedIn |
| **Target diseases:** Malaria, TB, NTDs | All sources |
| **AI capabilities:** Predictive + generative AI, active learning | TechInformed |
| **Access model:** Free, non-commercial, individual researchers | TechInformed |
| **Data privacy:** User data remains private, not shared | TechInformed |
| **Development:** Co-designed with 40+ scientists in Geneva | TechInformed |
| **Quote:** "AI tools for drug discovery are known to researchers in resource-limited settings, but licensing costs can still put them out of reach." — Caroline Maina, UCT PhD candidate | TechInformed |

### Strategic Context (Use in Papers)

**Funding Gap:**
- Global neglected-disease R&D funding: $4.17B in 2023
- Still ~$650M below 2018 peak
- >70% concentrated in HIV/AIDS, TB, and malaria

**Your Positioning:**
- African-led research (University of Yaoundé I, Cameroon)
- 65,856 molecules (large-scale dataset)
- Open-source pipeline (aligns with dd4gh mission)
- Resistance-informed design (addresses African malaria burden)

---

## 📖 Complete Citation Paragraphs (Ready to Use)

### Option 1: Brief Mention (Introduction/Discussion)

```latex
Our work contributes to the growing ecosystem of accessible AI-driven drug discovery 
tools for global health, including the recently launched dd4gh platform by MMV and 
deepmirror \cite{mmv2026dd4gh}. By providing MD-validated, resistance-resilient 
antimalarial candidates from African natural products, our pipeline offers 
high-quality training data and novel molecular descriptors that can augment dd4gh's 
predictive models.
```

### Option 2: Detailed Integration (Discussion/Future Work)

```latex
The launch of dd4gh (Drug Design for Global Health) by Medicines for Malaria Venture 
and deepmirror marks a significant milestone in democratizing AI-powered drug 
discovery for neglected diseases \cite{mmv2026dd4gh,techinformed2026dd4gh}. This 
open-access platform combines predictive and generative AI with active learning, 
enabling researchers in low- and middle-income countries to design and optimize 
compounds without costly commercial software licenses.

Our work complements dd4gh's capabilities in three key ways:
(1) \textbf{Validated training data:} Our 20 MD-validated polypharmacological 
candidates with MM-GBSA binding free energies provide high-quality experimental 
proxies for dd4gh's active learning framework.
(2) \textbf{Resistance-informed design:} Our Resistance Resilience Score (RRS) 
metric can be integrated with dd4gh's generative models to optimize compounds 
against African-prevalent resistance mutations (PfDHFR-N51I, C59R, S108N; 
PfCRT-K76T, K76A).
(3) \textbf{Enhanced molecular representations:} Our topological fingerprints 
(TFP) and tensor network embeddings (TNE) achieve 9--13\% improvement in activity 
prediction accuracy over classical ECFP4, offering dd4gh users richer molecular 
descriptors without quantum hardware requirements.

We envision future integration where our quantum-inspired methods augment dd4gh's 
pre-trained models, providing researchers across Africa and other endemic regions 
with state-of-the-art computational tools for resistance-aware antimalarial 
discovery.
```

### Option 3: African-Led Narrative (Cover Letter/Impact Statement)

```latex
As researchers based at the University of Yaoundé I (Cameroon), we are particularly 
encouraged by initiatives that democratize access to AI-driven drug discovery tools. 
The recent launch of dd4gh by MMV and deepmirror \cite{mmv2026dd4gh} directly 
addresses the resource barriers that have historically limited computational drug 
discovery in African institutions. Our pipeline—developed with limited computing 
infrastructure and open-source tools—demonstrates that high-impact antimalarial 
discovery research can originate from the continent most affected by malaria. By 
focusing on African natural product chemical space (396 NPs) and explicitly 
optimizing against resistance mutations prevalent in African \textit{P. falciparum} 
populations, our work embodies dd4gh's mission to level the playing field for global 
health drug discovery.
```

---

## ⚠️ What NOT to Cite

**Avoid these claims (not verified):**
- ❌ "dd4gh uses quantum computing" (FALSE - classical AI only)
- ❌ "dd4gh has validated X compounds" (no data available yet)
- ❌ "dd4gh will replace commercial tools" (speculative)
- ❌ Specific accuracy metrics for dd4gh models (not published)

**Safe claims:**
- ✅ dd4gh is free, open-access, non-commercial
- ✅ Combines predictive + generative AI
- ✅ Uses active learning for continuous improvement
- ✅ Targets malaria, TB, NTDs
- ✅ Co-designed with 40+ scientists
- ✅ Funded partially by Gates Foundation

---

## 📝 Summary: Citation Checklist

### For Both Papers:

- [ ] Cite MMV press release (`mmv2026dd4gh`)
- [ ] Cite TechInformed article (`techinformed2026dd4gh`)
- [ ] Mention dd4gh in Introduction (context)
- [ ] Mention dd4gh in Discussion (comparison/integration)
- [ ] Mention dd4gh in Future Directions (collaboration opportunity)
- [ ] Use full name first: "Drug Design for Global Health (dd4gh)"
- [ ] Provide URL: https://dd4gh.ai
- [ ] Emphasize alignment with African-led, open-source, global health mission

---

**Document Version:** 1.0  
**Created:** April 8, 2026  
**For:** Papers 2 & 3 (MD Validation + Quantum-Inspired Methods)  
**Author:** Nana Engo
