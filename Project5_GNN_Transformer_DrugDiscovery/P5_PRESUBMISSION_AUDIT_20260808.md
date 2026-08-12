# P5 — Pre-Submission Audit Report (peer-review skill workflow)

**Date:** 8 August 2026
**Tooling:** local peer-review skill v2.0 CLIs (deterministic, no external calls)
**Review ID:** `P5-PRESUBMISSION-LOCAL` (author-requested quality check, local-only)
**Status:** ✅ No blocker-level claim/evidence mismatch found by the automated gates; human verification still required before submission.

---

## 1. Process gates

| Gate | Tool | Result |
|------|------|--------|
| Intake / authorization | `validate_review_intake.py` | ✅ `READY_FOR_LOCAL_REVIEW` (author_request, single_anonymized, local-only, disclosure planned) |
| Reporting guideline selection | `select_reporting_guidelines.py` | ✅ **TRIPOD-AI-2024** selected (27 items; prediction-model reporting standard) |
| Statistics & reproducibility | `audit_statistics_reproducibility.py` | ✅ **`VALID_NO_RECORDED_GAPS`** — 22 items: 20 `verified_present`, 2 `not_applicable`, 0 gaps |
| Review scaffold | `generate_review_scaffold.py` | ✅ generated (private working draft) |
| Citation audit | `audit_citations.py` | not run on LaTeX source (Pandoc-style citation audit targets `.md`); LaTeX compile itself reports 0 undefined references |

## 2. Statistics/reproducibility coverage (22 items)

All 22 items verified against the frozen data and manuscript:

- **Question/design:** estimand = mean test ROC AUC per split over 25 fold–seed replicates; unit = molecule; stratified random + Bemis–Murcko scaffold 5-fold × 5 seeds, frozen and released.
- **Analysis:** paired t on the **5 per-seed means (df=4)** — not 25 independent observations; BH-FDR applied separately across the 4 scaffold and 4 random comparisons; Shapiro–Wilk OK; Wilcoxon consistent (p=0.0625).
- **Results:** mean ± population SD across the five per-seed means for the manuscript table; raw 25-fold SD retained as `std25`; Δ vs ECFP4; t(4) and p-values; 95% CIs in figure; identical denominators across arms.
- **Reproducibility:** frozen panel (19,836), frozen splits (`.npy`, hashed), per-fold CSVs + salience JSONs + checkpoints released; pinned environment (torch 2.13.0+cu130, PyG 2.8.0, transformers 5.14.1); `SHA256SUMS` (40 entries).
- **Integrity:** ChemBERTa cross-fold leak found → corrected (per-fold weight reset) → contaminated checkpoints discarded; initial misaligned p-values corrected (audit 06/08); no selective reporting.

## 3. Bench numbers locked (8 August 2026)

| Arm | Random | Scaffold |
|-----|-------:|---------:|
| ECFP4–RF | **0.9433 ± 0.0003** | **0.8300 ± 0.0023** |
| ChemBERTa | 0.9121 ± 0.0012 | 0.7867 ± 0.0054 |
| GIN | 0.9098 ± 0.0022 | 0.8047 ± 0.0141 |
| GIN–TFP | 0.9084 ± 0.0012 | 0.8138 ± 0.0107 |
| GIN–TNE | 0.8918 ± 0.0018 | 0.8090 ± 0.0149 |

Every GNN/transformer arm is significantly below ECFP4–RF on **both** splits (paired t, df=4; BH-adjusted p < 0.05).

## 4. What independent validation of P5 requires

The manuscript is a controlled, honest-negative benchmark. Its claims are self-contained, but reviewers and the acceptance estimate (80–86 %) are strengthened by the following **independent-validation actions**, in increasing order of effort:

1. **Complete the Zenodo deposit** (DOI 10.5281/zenodo.19608875 reserved, upload pending). Publish the frozen panel, frozen splits, per-fold result CSVs, salience JSONs, checkpoint manifests, and the `SHA256SUMS`. This turns "available in GitHub" into "archived, versioned, citable" and is the single highest-value, lowest-effort step.
2. **External computational replication.** Have a reviewer (or an independent script, e.g. `p5_rerun_all.sh`) rerun ECFP4-RF and one GNN arm on the frozen splits with the pinned environment and confirm mean AUC within tolerance (sanity gate already proves 0.9433 ≈ P3 0.9475). A short "replication note" in the SM is enough; no new biology is needed.
3. **Independent statistical re-derivation.** Recompute the paired-t (df=4) and BH-FDR from the raw per-seed means (all published in CSVs). A one-page appendix table with t, raw p, adjusted p for all 8 arm×split cells removes any reviewer doubt.
4. **Out-of-panel generalization check (optional, medium effort).** Run the same protocol (ECFP4-RF vs GIN vs ChemBERTa, scaffold split) on a public benchmark (e.g. a MoleculeNet/antimalarial public set) to show the verdict is not panel-specific. This is the strongest independent evidence but requires additional compute and is not required for submission.
5. **Not required, and not claimable:** wet-lab experimental validation. The paper explicitly does not claim it; the honest-negative framing depends on this boundary being respected.

**Recommendation:** actions 1–3 before submission; action 4 as a follow-up or second paper; action 5 out of scope.

---

*This report records automated completeness/consistency gates only. It is not a peer-review decision, a quality score, or a publication recommendation. Human review by the authors remains mandatory.*
