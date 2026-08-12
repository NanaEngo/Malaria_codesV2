# P3 — quantum-inspired molecular representations

**Status:** canonical benchmarks and external validation complete; manuscript package ready for final author/deposit checks.
**DAR:** `BMAD_Q1_DATA_ANALYSIS_REPORT.md`
**Canonical manuscripts:** `manuscript/LaTeX/Paper3_Quantum_InspiredV2608.tex` and `Paper3_Quantum_Inspired_SM_V2608.tex`

## Scientific question

Do TFP, TNE, and QKS add useful information beyond classical molecular fingerprints for AI-generated African antimalarial candidates?

## Canonical results

| Representation/model | AUC |
|---|---:|
| ECFP4 | 0.9475 ± 0.0045 |
| Hybrid RF | 0.8876 ± 0.0065 |
| TFP | 0.8759 |
| TNE | 0.7219 |

Removing QK reduces hybrid AUC by 0.040. QKS is statistically comparable to RBF at n=5,000 and n=19,849; no quantum advantage is claimed. External descriptor validation retains the 351 TNE failures as an explicit ITT/complete-case sensitivity issue. The external QKS pilot gives quantum 0.8385 versus RBF 0.8423, p=0.374.

## Canonical locations

- Results and figures: `results/`
- Scripts: `scripts/`
- Main/SM/cover: `manuscript/LaTeX/`
- Older manuscript versions: `manuscript/LaTeX/archive/`

## Evidence boundary

The study supports complementary topological and tensor-network representations, not superiority over ECFP4 or RBF. TNE failures, sample-size effects, and the size-confounded H₁–RRS association remain explicit limitations. Zenodo DOI is reserved; upload is pending.
