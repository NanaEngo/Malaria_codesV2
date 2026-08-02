# P3 Critical Review Plan — Phase 5 (control-tower PLAN artifact)

**Manuscript:** *Persistent homology resolves the scaffold paradox in AI-generated African antimalarial candidates: a topological and tensor-network fingerprinting study* (Paper 3)
**Target journal:** Journal of Cheminformatics
**Session goal:** Phase 5 critical review passes (DELEGATE → VERIFY)
**Date:** 2026-07-27
**Model:** Opus 4.8 (judgment passes) / Sonnet (editorial)

## 1. Context

P3 is at ~85% with a prior adversarial audit (`P3_ADVERSARIAL_AUDIT_MITIGATION.md`) already done. This Phase 5 cycle is **not** a repeat of that audit: it (a) verifies the audit's claimed mitigations actually landed in the `.tex`, (b) cross-checks every number against its source CSV + generating script (author's standing priority), and (c) runs independent reviewer lenses the prior audit did not.

Files (absolute, ROOT = this project dir):
- Main: `manuscript/LaTeX/Paper3_Quantum_InspiredV2607.tex` (565 lines)
- SM: `manuscript/LaTeX/Paper3_Quantum_Inspired_SM_V2607.tex` (686 lines)
- Bib: `manuscript/LaTeX/Bibliography_Paper3.bib` (629 lines)
- Prior audit: `P3_ADVERSARIAL_AUDIT_MITIGATION.md`; Roadmap: `P3_SUBMISSION_ROADMAP_85PCT.md`; README (partly STALE)
- Scripts: `scripts/*.py` (40 files); Result CSVs: `results/*.csv`, `results/p3_*/*.csv` (45 files)
- Env: `source /home/tchapet/VirtualEnv/bin/activate` (Python 3.12.3) before any Python. If an import needs the conda env `malaria_md`, mark `[UNVERIFIED-needs-conda]`.

## 2. Review passes (parallel; model-routed)

| Pass | File | Lens | Model |
|------|------|------|-------|
| A | review-numbers-and-sources.md | Trace every number to CSV+script; reconcile main↔SM↔README↔audit | opus |
| B | review-claims-and-rigor.md | Adversarial + scientific-critical-thinking: overclaiming, falsifiability, unsupported claims | opus |
| C | review-scholar-eval-and-edge-cases.md | ScholarEval quantitative scoring + edge cases + reproducibility | opus |
| D | review-editorial.md | anti-AI, prose, structure, J. Cheminformatics fit | sonnet |
| E | review-death-angle.md | Divergence only (generative, unvalidated) | opus |

**Reviewer-gate discipline:** each pass writes its FULL findings to its file and returns only a compact summary (1-sentence verdict + top 2–5 findings with file:line + path). Reviewers must NOT edit any manuscript/script. Mark anything unverifiable `[UNVERIFIED]`; never fabricate.

**Divergence ordering note:** Pass E (death-angle) is launched in parallel with A–D for efficiency. Its outputs are tagged `[speculative]`/`[to verify]` and will be routed to a **follow-up verification round** — they never enter the manuscript as fact unverified (Integrity rule 8).

## 3. Verified seed findings (from PLAN-phase read; each confirmed in the cited file:line)

These are confirmed present in the files — passes must cross-check each against its source CSV and go beyond.

### CRITICAL
- **S1 — H₁-RRS Spearman ρ has four different values.** Main abstract L99, L513, L520: `ρ=0.916, p<0.0001, n=14`. SM L104, L639: `ρ=0.947 (pilot, n=14) → 0.361, p=0.001 (n=77)`. Prior audit doc §Weakness#2: canonical `0.312, p=0.006, n=77`. The audit's claimed mitigation (canonize 0.312) was **not applied to the main manuscript**, which still headlines 0.916. Resolve via `p3_h1_rrs_correlation_final.csv`, `p3_rrs_tfp_final.csv`, `p3_rrs_expanded_with_tfp*.csv` + `p3_rrs_tfp_expansion.py`/`p3_rrs_tfp_merge.py`.
- **S2 — Methods vs Results sample-size contradiction.** Methods L134 "primary dataset consists of 65856 molecules"; L238 "5-fold CV on all 65856 molecules". Results L256 and all benchmark tables: `19849`. Explain or confirm as error via CSV row counts (`p3_tda_fingerprints.csv`, `p3_hybrid_benchmark.csv`).
- **S3 — Tartarus target/PDB labels contradict between main and SM.** Main L459: `1SYH/PfDHFR, 6Y2F/PfATP4, 4LDE/PfCRT`. SM L573: `1SYH/PfDHFR, 6Y2F/PfCRT, 4LDE/PfClpP`. ChEMBL enrichment SM L448 uses a third set: `PfDHFR/7F3Y, PfATP4/9N10, PfCRT/6UKJ`. Resolve against `p3_tne_regression.csv`.
- **S4 — PHCO AUC has three different values.** Main L312/L295/L491: `0.500 (exactly random)`. SM L232: `0.801 (after SparseBitVect bug fix)`. SM effect-size table L421: `0.912`. Reconcile against the bug-fix narrative + CSV.
- **S5 — Promiscuity correlations differ between main and SM.** Main L465: `H0 count −0.248, H0 entropy −0.243, H1 entropy −0.190, N=17011`. SM L579: `H0 max persistence −0.167, H1 entropy −0.161`. Different features, different values. Ground-truth: `p3_tda_promiscuity.csv`.

### HIGH
- **S6 — SM effect-size table (L415–424) contradicts main benchmark.** TFP 0.630 (main 0.587), TNE 0.630 (main 0.606; **identical** to TFP row), FCFP4 0.932 (main 0.845), PHCO 0.912 (main 0.500). ΔAUC signs positive imply a baseline ~0.300 (below random) — nonsensical. Caption says 200-mol dev set, but TFP=TNE identical values suggest a bug.
- **S7 — README stale vs manuscript.** 10-fold CV (README L43) vs 5-fold (ms); N1–N4 (README) vs N5–N8 (ms L120); 15.6× headline (README N1) vs 5.9× real (ms); `conda activate malaria_md` (README) vs venv.
- **S8 — "20 high-confidence leads" (main L511) vs "n=14" correlation (L513/L520).** 20 vs 14 unexplained; class counts A=3, D=1 ⇒ B+C=10.
- **S9 — Malformed citations.** Bare `(Wesołowski et al., 2025)` with no `\citep` key — main L497, SM L594. Manual `[1]` footnote SM L658 mixed with natbib authoryear. Two companion bibkeys: `temgoua2026antimalarial` (L116) vs `temgoua2027md` (L511).
- **S10 — Data-availability DOI mismatch.** Main L548: `10.5281/zenodo.XXXXXXX, to be minted upon acceptance`. README + SM L110: `10.5281/zenodo.19608875`. Audit says Zenodo upload still PENDING.
- **S11 — Tartarus N per target.** Main L461: `N=11878 / 17075 / 17074` (17075 vs 17074 off-by-one; none equals 19,913). Confirm vs `p3_tne_regression.csv`.

### MEDIUM
- **S12 — TFP and TNE identical per-fold values** (SM Table S4, L146–156): both `0.600/0.800/0.500/0.667/0.583`. Bug or real?
- **S13 — Silhouette 0.350 vs target ">0.35"** (L234, L389): equal, not exceeded; "exceeding the VAE baseline" is loose wording.
- **S14 — 15.6× (padded upper bound) used as README headline** N1, overstated vs 5.9× real the ms actually uses.
- **S15 — Novelty numbering scheme inconsistent across docs.** ms N5–N8 (implies N1–N4 belong to a prior paper); README reuses N1–N4 for THIS paper.
- **S16 — SM duplicates main Discussion.** SM "Discussion" section L585–663 repeats main Discussion content (mechanistic explanation, TNE compression, kernel indistinguishability). Structural redundancy.
- **S17 — QKS polypharmacology "advantage" Δ=+0.010 (σ=0.008)** framed as "task-specific quantum kernel sensitivity" (L365, L463): Δ/σ≈1.25, no corrected p-value — borderline overclaim.
- **S18 — Abstract overclaim.** L99: hybrid "revealing non-linear ring-topology features critical for ANP scaffolds that ECFP4 cannot capture" — overstated given hybrid only *matches* (doesn't beat) ECFP4 and TFP standalone AUC=0.587.

## 4. Strengths (for balance; scholar-eval must weigh these)
Honest negative results (QKS no advantage after RBF tuning; TFP/TNE don't beat ECFP4); the RBF-tuning cautionary tale is a genuine methodological contribution; Bonferroni correction + Cohen's d effect sizes; ChEMBL external-validation attempt; power-analysis mention; open data/code deposit (Zenodo + GitHub); NISQ-era caveat stated upfront; D-GRIL build barrier documented transparently.

## 5. VERIFY phase (after passes return)
For each pass, check its output against its done-criteria trying to reject it ("what would prove this pass missed something?"). Findings that survive → fix queue (suggested fix per CRITICAL). Failed passes → targeted retry (max 2 loops, 2nd escalates sonnet→opus). Record all in `project-tracking.md` Critical Review Log.
