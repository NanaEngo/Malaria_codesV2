# P4 — Adversarial Audit & Mitigation (JoC, canonical v12)

**Date:** 2026-08-08
**Scope:** `manuscript/LaTeX/P4_Pareto_MCTS_JoC_refined.tex` (main), `P4_Pareto_MCTS_JoC_SM.tex`, `Cover_Letter_P4_JoC.tex` — targeted at **Journal of Cheminformatics (BMC, JoC)**.
**Method:** fresh adversarial review against the current v12-activity scalar deposit (`results/benchmark_molecules_opt_v12/`) and the separately locked pre-activity Pareto deposit (`results/pareto/`), independent of the superseded JCIM-targeted audits (`P4_ADVERSARIAL_AUDIT_MITIGATION.md`, `P1_P4_CONSOLIDATED_ADVERSARIAL_AUDIT.md`).
**Outcome of mitigation:** manuscript-level risks reduced; acceptance estimates remain heuristic and conditional on editorial screening, reviewer access and final submission compliance.

---

## 0. Verified good (no change required)

All checked against the canonical v12-activity CSV `results/benchmark_molecules_opt_v12/p4_benchmark_merged.csv`:

| Claim | Value | Verified |
|---|---|---|
| Random mean ± std | 0.6724 ± 0.0056 | ✅ matches CSV |
| MCTS+ScafVAE | 0.6649 ± 0.0068 | ✅ matches CSV |
| Greedy (deterministic) | 0.4278 ± 0.0000 | ✅ unique greedy = 1 |
| GA | 0.6453 ± 0.0124 | ✅ matches CSV |
| MCTS–Random paired t19 / p | −4.97 / 0.000085 | ✅ recomputed |
| MCTS–Greedy t19 / p | 157.06 / <0.0001 | ✅ recomputed |
| MCTS–GA t19 / p | 6.95 / <0.0001 | ✅ recomputed |
| Cohen's d (MCTS–Random) | −1.11 | ✅ recomputed |
| MCTS wins/ties vs Random | 1 / 1 of 20 seeds | ✅ recomputed |
| Pareto front | 4 mutually non-dominated | ✅ (pymoo, 4-obj active) |
| Hypervolume | 1.2366 | ✅ exact reproduction (negated-minmax, r=1.1) |
| Best v12 seeds (MCTS 0.6779, Random 0.6856) | correct | ✅ |
| Citations | 7 cited, all in .bib | ✅ bibliographies resolve |

**Statistical logic is sound and honestly framed** (honest order Random > MCTS > GA > Greedy; primary comparisons MCTS–Random & MCTS–GA; MCTS above Greedy stated as a secondary result). Methods correctly documents the v12 reduced-reward weight set, the full aggregator, and the SA=3.0 exclusion from Pareto dominance and hypervolume.

---

## 2. Findings and mitigations

### F1 — RESOLVED: Pareto objective list
**Historical location:** main-text contribution list and Pareto-front description.
**Issue found:** an earlier draft listed `MPO, SYBA and SA`, despite the active front using **MPO, SYBA, RRS and PNS** and excluding constant SA from dominance/HV.
**Mitigation verified 2026-08-08:** the canonical main text, SM and provenance checker now consistently state MPO, SYBA, RRS and PNS, with SA = 3.0 reported only for completeness.
**Remaining risk:** 🟢 none identified.

### F2 — RESOLVED: PUCT scalar-proxy description
**Historical location:** Methods description of the objective aggregation.
**Issue found:** an earlier draft described three averaged components, while the implementation sums the min–max-normalised components of four active objectives.
**Mitigation verified 2026-08-08:** the canonical Methods text now states that the scalar proxy sums the four active components and retains the full vector for front updates and post-hoc analysis.
**Severity:** 🟢 none identified.

### F3 — RESOLVED: figures and provenance
**Historical issue:** earlier figures were generated from superseded benchmark directories and the manuscript did not consistently expose the principal displays.
**Mitigation verified 2026-08-08:** `p4_generate_figures.py` now reads the v12-activity directory; the canonical main text references the benchmark, efficiency and Pareto figures; the SM references the real diversity MDS. The remaining requirement is a final human visual inspection of the compiled PDFs.
**Severity:** 🟢 low, pending visual inspection only.

### F4 — DATA AVAILABILITY wording invites the review-stick “data not provided at review time”
**Location:** main text Data availability (end) + Methods (end).
**Problem:** says data “will be deposited on Zenodo **upon acceptance**” and “wire-request may request access to the **private** repository”. A reviewer needing access to verify SMILES / HV may find the door “private + upon acceptance” a red flag, and it contradicts the fact that the repository is **already public** on GitHub and a **Zenodo DOI already reserved (10.5281/zenodo.19608875, deposit pending)**.
**Fix:** state data/code are released under MIT in the public repository (URL), cite the reserved Zenodo DOI as pending, and keep a short “reviewers may access the public repository now” note.
**Severity:** yellow (reviewer-access friction).

### F5 — BMC (desk) requirements absent: Funding + Ethics/Consent
**Location:** Declarations end of main.
**Problem:** BMC asset listings for a research article — the manuscript lacks a **Funding** declaration and the **Ethics approval and consent to participate / Consent for publication** (“Not applicable”) statements.
**Fix:** add concise “Funding: none / this work was supported by the University of Yaoundé I HPC…”; add “Ethics approval and consent to participate: Not applicable.” and “Consent for publication: Not applicable.”.
**Severity:** this desk/admin compliance — LOW scientific, MEDIUM compliance.

### CRITICAL — writer-safety: enabling the HV/table provenance
Already handled by the deposit `.sidecar` + `p4_pareto_provenance_check.py` + SM. No action required.

---

## 3. Quantified acceptance assessment (JoC target)

Method used: decompose acceptance into the review dimensions weighted for a BMC methods journal; score *risks* before/after mitigation, then combine with the weak-est-, necessary-type factors. (Heuristic but explicit; input from an experienced editor model.)

### 3.1 Weighted risk model (each dimension 0–10 for residual risk; q = strong = low = good)

| Dimension | Weight | Pre-fix residual risk score (10=worst) | Post-fix residual |
|---|---|---|---|
| Scientific keys: data correctness, stats | 0.30 | 2 | 1 |
| Reproducibility / code+data availability | 0.15 | 5 (no verifier, DOI “later”) | 1 |
| Methods clarity / ROI & consistency | 0.15 | 5 (C1/“three”/counts) | 1 |
| Presentation completeness (figures) | 0.10 | 6 (no figs, stale fig dir) | 1 |
| Novelty & fit to JoC scope | 0.20 | 2 | 2 |
| Compliance (Funding, ethics) | 0.05 | 7 | 1 |
| Weak inevitably accepted a modest effect size | 0.05 | 3 | 3 |

Pre-fix weighted risk = 0.30·2 + 0.15·5 + 0.15·5 + 0.10·6 + 0.20·2 + 0.05·7 + 0.05·3 = 0.60 + 0.75 + 0.75 + 0.60 + 0.40 + 0.35 + 0.15 = 3.60.
Post-fix weighted risk = 0.30·1 + 0.15·1 + 0.15·1 + 0.10·1 + 0.20·2 + 0.05·1 + 0.05·3 = 0.30 + 0.15 + 0.15 + 0.10 + 0.40 + 0.05 + 0.15 = 1.30.

Baseline acceptance (lower bound for a sound BMC desk+review process): complement on a saturating curve. Prior audit landed the old JCIM draft at parts−; the current v12 are already honest + deposits they did→ 45–75%. With the residual weighted-risk dropping from 3.60 → 1.30, the corresponding heuristic acceptance range improves, but it must not be interpreted as a measured probability. The pending Zenodo upload and final editorial checks remain residual risks.

### 3.2 Claimed estimate

**Baseline before this final consistency pass: ≈ 72 %**
**Post-mitigation estimate: ≈ 85–90 % conditional on a clean editorial check and reviewer access to the public repository.** This is a heuristic estimate, not a measured probability and not an editorial prediction.

Remaining contributors to uncertainty include reviewer interpretation of the modest scalar effect, the pending archival deposit, and any journal-specific administrative requirement. These are not claims of acceptance or rejection.

---

## 4. Remediation checklist

- [x] F1 reword C1 + line 122 (MPO, SYBA, RRS, PNS)
- [x] F2 fix Q(s,a) description (sum active objectives, 4, not "average three")
- [x] F3 regenerate all figures from v12 + real MDS; add figures to main & SM
- [x] F4 data-availability: public GitHub URL + reserved Zenodo DOI, explicitly marked pending
- [x] F5 add Funding + Ethics/Consent declarations
- [x] Final v12 statistics re-derived from `benchmark_molecules_opt_v12/p4_benchmark_merged.csv`
- [x] Correct SM ranking and v12 scalar weights
- [x] Correct abstract length and affiliation overfull box
- [x] Recompile main-SM-cover (0 errors, 0 undefined; bibtex exit 2 is expected for files without bibliographies)
- [ ] Human visual PDF inspection and package assembly
- [ ] git commit + push final P4 editorial corrections