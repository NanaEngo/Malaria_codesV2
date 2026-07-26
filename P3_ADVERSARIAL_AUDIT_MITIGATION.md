# P3 Adversarial Audit \& Mitigation Report

**Date:** July 25, 2026 (evening)
**Scope:** Critical self-assessment of P3 manuscript from a Q1 journal reviewer perspective
**Methodology:** Identify weaknesses a reviewer would flag, assess severity, propose mitigations

---

## Weakness #1: Activity Labels Are Computational, Not Experimental

**Severity:** 🔴 **CRITICAL** (reviewer will flag this first)

**What a reviewer will say:** "The entire activity prediction benchmark uses Ersilia model predictions (eos80ch) as ground truth. These are ML-based predictions, not experimental IC\textsubscript{50} values. The authors' own ChEMBL search found only 7/231 structural analogues (3.0\%), and only 3 are experimentally active. How can the key finding — that PersStats RF matches ECFP4 — be trusted when the labels themselves are uncertain?"

**Mitigation implemented:**
1. ChEMBL expanded validation (77 compounds, 231 pairs, 3 active PfATP4 hits) — documented in SM §9C
2. Docking enrichment benchmark (PfDHFR 5.43× fold enrichment) — validates protocol against known actives
3. Limitations explicitly acknowledge this as the first concern
4. Both Honest about limitation while providing orthogonal validation (docking enrichment)

**Remaining risk:** Reviewer may still demand experimental IC\textsubscript{50} validation for top candidates. Accept this as a legitimate limitation and frame the paper as providing the computational foundation for future experimental work.

---

## Weakness #2: PersStats RF Only Marginally Exceeds ECFP4 ($d = +0.85$, Not Significant)

**Severity:** 🟡 **MEDIUM** (reviewer will note this is a marginal improvement)

**What a reviewer will say:** "The key SOTA benchmark result — PersStats+RF AUC 0.873 vs ECFP4 0.868 — has \textDelta AUC = +0.005 with $p > 0.05$. This is numerical parity, not superiority. The Cohen'\'s $d$ of +0.85 is large, but with only 5 folds, the statistical power is insufficient to distinguish the methods. How do the authors justify claiming this as a SOTA result?"

**Mitigation implemented:**
1. Cohen'\'s $d$ effect sizes added to SM SOTA table (July 25) — quantifies practical magnitude
2. Limitations explicitly frame this as "numerical parity" not "superiority"
3. Fold-level standard deviations reported transparently
4. Honest negative framing: "classical fingerprints remain the recommended baseline"

**Remaining risk:** Increase n\_folds to 10 for better statistical power, or acknowledge that with only 22 features, PersStats cannot meaningfully outperform 2048-bit ECFP4.

---

## Weakness #3: Quantum Kernel Shows No Advantage Over Classical RBF

**Severity:** 🔴 **CRITICAL** ("quantum-inspired" branding may be seen as hype)

**What a reviewer will say:** "Despite the 'quantum-inspired' framing, the quantum kernel (IQPEmbedding, 8 qubits) shows no statistical advantage over classical RBF ($p > 0.05$). The earlier claim of 0.936 vs 0.105 was an artefact. The GA discriminator shows QK performs near-random (AUC 0.425-0.511). What is the quantum contribution beyond a classical RBF kernel with kernel PCA?"

**Mitigation implemented:**
1. Honest correction of the 0.936/0.105 artefact — framed as positive methodological contribution
2. All three kernels reported as statistically indistinguishable
3. QKS contribution framed through ablation: removing QKS drops hybrid AUC from 0.842 to 0.608
4. Kernel PCA (10 components) identified as the mechanism preserving quantum Hilbert space structure
5. Limitations §4 explicitly addresses this

**Remaining risk:** The "quantum-inspired" title may attract scrutiny. Consider reframing as "topology-inspired" or emphasizing TDA as the primary contribution. The quantum component is the KERNEL PCA (not the raw kernel), which is mathematically equivalent to a classical kernel method.

---

## Weakness #4: H\textsubscript{1}-RRS Correlation Attenuates ($\rho$ = 0.947 → 0.312)

**Severity:** 🟡 **MEDIUM** (pilot inflated, expanded attenuated)

**What a reviewer will say:** "The H\textsubscript{1}-RRS correlation dropped from $\rho$ = 0.947 ($n$ = 14) to $\rho$ = 0.312 ($n$ = 77). This is a 67\% attenuation. The pilot effect was severely inflated by class imbalance (no Class C/D). The abstract and conclusion still prominently feature the 0.947 value. Does the paper over-interpret a weak correlation?"

**Mitigation implemented:**
1. Abstract reports both pilot AND expanded values with honest framing
2. Limitations §3 methodologically frames the attenuation as a discovery: "balanced resistance-class sampling is essential"
3. Closing emphasizes $\rho$ = 0.312 ($p$ = 0.006, $n$ = 77) as the more honest estimate
4. Cross-paper figure in SM shows the full distribution

**Remaining risk:** The 0.947 value in the abstract may still be seen as cherry-picking. Consider moving the pilot value to SM only and using $\rho$ = 0.312 as the canonical result.

---

## Weakness #5: GA Discriminator AUC = 1.000 Is Trivial

**Severity:** 🟢 **LOW** (acknowledged in text, but still a valid criticism)

**What a reviewer will say:** "The GA discriminator benchmark shows ECFP4 Tanimoto AUC = 1.000 at all $N$. With only 2 SELFIES-character mutations, some generated molecules are structurally identical to seeds — this is a trivial result. The quantum kernel's near-random performance (0.425-0.511) is not a fair comparison because it operates on UMAP-reduced features."

**Mitigation implemented:**
1. SM discussion explicitly notes seed-identical molecules as a caveat
2. The benchmark is framed as an applicability domain analysis, not a classifier comparison
3. QKS standalone AUC (0.751) is positioned as the fair comparison point

**Remaining risk:** Remove the GA discriminator from the main manuscript and keep it in SM only — it adds little to the core contribution.

---

## Weakness #6: No True TopologyNet/D-GRIL Comparison

**Severity:** 🟡 **MEDIUM** (related work claims not backed by benchmarks)

**What a reviewer will say:** "The introduction positions TopologyNet and D-GRIL as key related works, but the benchmarks are only against classical fingerprints. The MLP analog (AUC 0.799 vs RF 0.860) is a weak surrogate — it uses static summary statistics, not the end-to-end differentiable multi-parameter PH that defines D-GRIL. Where is the head-to-head comparison?"

**Mitigation implemented:**
1. MLP analog benchmark added to SM §9D — shows neural networks don'\'t improve over RF on static PH features
2. D-GRIL build attempted and documented (C++ extension compiled, linker blocked by libc10.so ABI) — BMAD §3.19
3. Limitations §5 references TopologyNet analog + D-GRIL gap honestly
4. Both papers framed as operating on different paradigms (static vs differentiable PH)

**Remaining risk:** Accept that a head-to-head D-GRIL comparison is not feasible. Frame the MLP analog as a feature-based comparison and note that end-to-end differentiable PH is a distinct paradigm requiring different infrastructure.

---

## Weakness #7: Quantum Parameter Grid Search Limited to $n$ = 1000

**Severity:** 🟢 **LOW** (documented, but a power concern)

**What a reviewer will say:** "The quantum circuit hyperparameter search used $n$ = 200 for the grid and $n$ = 1000 for re-benchmarking. With only 5 folds, the per-fold samples are 200 and 40 respectively. The optimal configuration ($d$ = 6, $n\_\text{rep}$ = 1, $n\_\text{kpca}$ = 30, AUC 0.828) may not generalize to the full library. The default $d$ = 8 is used for the headline benchmark — why wasn'\'t the optimal configuration used?"

**Mitigation implemented:**
1. SM Table S5 clearly states the $n$ = 1000 re-benchmarking and grid search sample sizes
2. Headline benchmark uses the default $d$ = 8 for consistency across the paper
3. The optimal configuration is documented for reproducibility

**Remaining risk:** Either re-run the full benchmark with optimal parameters ($d$ = 6, $n\_\text{rep}$ = 1, $n\_\text{kpca}$ = 30, $n$ = 19,849) or clearly state this as a limitation and a direction for future work.

---

## Weakness #8: Library Bias Toward African NP Space

**Severity:** 🟢 **LOW** (acknowledged, intentional)

**What a reviewer will say:** "The library is generated from 396 African NP and 454 synthetic drug seeds. The conclusions about TDA superiority or PersStats performance may not generalize to DrugBank, ChEMBL, or other chemical spaces. The paper claims 'African NP space is underrepresented' — but doesn'\'t this mean the findings are niche?"

**Mitigation implemented:**
1. Limitations §6 explicitly acknowledges the library bias
2. The focus on African NP space is framed as a deliberate contribution, not a limitation
3. Comparison with COCONUT and DrugBank datasets provides context

**Remaining risk:** Add a brief note that future work should validate PersStats on broader datasets (e.g., MoleculeNet, Therapeutics Data Commons).

---

## Overall Assessment

| Factor | Score | Notes |
|--------|:-----:|-------|
| Novelty | 7/10 | TDA + TNE + hybrid is novel for African NP space; quantum component adds little |
| Rigor | 8/10 | SOTA benchmark at n=19,849, 5-fold CV, Cohen'\'s d, honest negatives |
| Biological validity | 5/10 | Computational labels, only 7/231 ChEMBL matches, no experimental IC\textsubscript{50} |
| Clarity | 7/10 | Well-structured, Limitations trimmed, but abstract pitches pilot 0.947 too prominently |
| Impact | 6/10 | Scaffold paradox resolution is elegant; quantum contribution is weak |
| **Overall** | **6.6/10** | **Estimated acceptance probability: 65-75\%** |

### Actions to Reach 85\%

| # | Action | Impact | Effort |
|---|--------|:------:|:------:|
| 1 | Move pilot $\rho$ = 0.947 to SM only; use $\rho$ = 0.312 as canonical in abstract | +5\% | Low |
| 2 | Re-frame "quantum-inspired" → emphasize TDA as primary contribution | +5\% | Medium |
| 3 | Cohen'\'s $d$ added to SOTA table (DONE July 25) | +5\% | ✅ Done |
| 4 | Expand RRS cohort to include Class C/D ($n \geq 80$ for 80\% power) | +5\% | High (HPC) |
| 5 | Zenodo deposit with all benchmark CSVs + scripts | +5\% | Medium |
| 6 | Trim Discussion verbosity; move secondary figures to SM | +3\% | Low |

**After actions 1-6: 85-95\% acceptance probability.**
