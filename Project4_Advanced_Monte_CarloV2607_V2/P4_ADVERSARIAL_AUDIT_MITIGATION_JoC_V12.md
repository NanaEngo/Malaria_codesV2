# P4 — Adversarial Audit & Mitigation (JoC, canonical v12)

**Date:** 2026-08-08
**Scope:** `manuscript/LaTeX/P4_Pareto_MCTS_JoC_refined.tex` (main), `P4_Pareto_MCTS_JoC_SM.tex`, `Cover_Letter_P4_JoC.tex` — targeted at **Journal of Cheminformatics (BMC, JoC)**.
**Method:** fresh adversarial review against the current v12-activity scalar deposit (`results/benchmark_molecules_opt_v12/`) and the separately locked pre-activity Pareto deposit (`results/pareto/`), independent of the superseded JCIM-targeted audits (`P4_ADVERSARIAL_AUDIT_MITIGATION.md`, `P1_P4_CONSOLIDATED_ADVERSARIAL_AUDIT.md`).
**Outcome of mitigation:** manuscript-level risks reduced; editorial disposition remains unquantified and conditional on editorial screening, reviewer access and final submission compliance.

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
| Historical Pareto artifact | 4 mutually non-dominated after post-hoc SYBA re-derivation | ✅ provenance lock; SYBA was constant during search |
| Hypervolume | 1.2366 | ✅ exact reproduction (negated-minmax, r=1.1) |
| Best v12 seeds (MCTS 0.6779, Random 0.6856) | correct | ✅ |
| Citations | 7 cited, all in .bib | ✅ bibliographies resolve |

**Statistical logic is sound and honestly framed** (honest order Random > MCTS > GA > Greedy; primary comparisons MCTS–Random & MCTS–GA; MCTS above Greedy stated as a secondary result). Methods correctly documents the v12 reduced-reward weight set, the full aggregator, and the SA=3.0 exclusion from Pareto dominance and hypervolume.

---

## 2. Findings and mitigations

### F1 — RESOLVED: Pareto objective list
**Historical location:** main-text contribution list and Pareto-front description.
**Issue found:** an earlier draft listed `MPO, SYBA and SA`, despite the audited post-hoc front displaying **MPO, recomputed SYBA, RRS and PNS** and excluding constant SA from the final hypervolume.
**Mitigation verified 2026-08-08:** the canonical main text, SM and provenance checker now distinguish the historical search-time schema from the post-hoc SYBA re-derived front, with SA = 3.0 reported only for completeness.
**Remaining risk:** 🟢 none identified.

### F2 — RESOLVED: PUCT scalar-proxy description
**Historical location:** Methods description of the objective aggregation.
**Issue found:** an earlier draft described three averaged components, while the implementation uses a scalar proxy over the components that vary in a given run and stores the full vector for post-hoc front analysis.
**Mitigation verified 2026-08-08:** the canonical Methods text now states that the historical constant SYBA fallback contributed no information to search-time selection and that the final front was re-derived after SYBA recomputation.
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

### F6 — CRITICAL: historical Pareto run used a constant SYBA fallback
**Location:** canonical per-seed Pareto CSVs, front provenance, and any claim that all four displayed dimensions were actively optimised.

**Finding:** every historical per-seed CSV contains `syba=0.0`; the non-zero SYBA values in the merged four-point front were generated by `p4_recompute_pareto_syba.py` after the search. The original run therefore did not optimise an informative SYBA signal. This is not fixed by prose alone.

**Mitigation applied:** the main manuscript, SM, cover letter, README and data-analysis report now label the artifact as a post-hoc SYBA re-derivation and remove claims of informative four-way historical optimisation. The runner now fails closed when SYBA cannot initialise or remains constant during a publication rerun; legacy artefact re-scoring is handled only by dedicated post-processing scripts. A future validated pre-activity rerun must use a separate output directory and cannot silently replace the locked historical artifact.

**Residual status:** yellow until the validated rerun completes; the current manuscript is evidence-bounded only if this limitation remains visible.

### F7 — CRITICAL: proxy biology is not direct validation
**Location:** RRS/PNS terminology throughout the manuscript and cover letter.

**Finding:** RRS is Morgan/Tanimoto similarity to P2 reference chemotypes, and PNS averages three Tartarus score columns. Neither propagates P2 WT/mutant ratios, nor constitutes a four-target PfDHFR/PfCRT/PfATP4/PfClpP or experimental IC50/EC50 validation.

**Mitigation applied:** all canonical documents use “RRS-informed chemotype-similarity proxy” and “PNS-informed Tartarus docking proxy,” report the narrow/discrete ranges, and state that biological validation remains future work.

**Residual status:** yellow; a true WT/mutant or experimental validation would be a new study, not an editorial wording fix.

## 3. Editorial decision assessment (JoC target)

This local audit does not assign an acceptance probability. Editorial decisions depend on journal scope, novelty relative to the submitted literature, reviewer assessment, policy compliance, and whether reviewers can inspect the evidence. A risk register is more defensible than a pseudo-quantitative acceptance model.

### 3.1 Residual issues requiring explicit disclosure

- **Scalar result:** Random exceeds MCTS on the canonical v12 scalar reward; the paper must not claim algorithmic scalar superiority.
- **Historical Pareto provenance:** SYBA was constant at its fallback during the original search and was recomputed before the locked front was re-derived; the manuscript must describe this as post hoc.
- **Biological scope:** RRS and PNS are informed computational proxies, not WT/mutant, four-target, or experimental IC50/EC50 validation.
- **Archival status:** GitHub is the current reviewer-access path; the reserved Zenodo DOI remains pending.
- **Validation status:** the separate fail-closed SYBA rerun is not evidence until all seeds, provenance, front comparison and manuscript reconciliation pass.

### 3.2 Editorial decision boundary

The defensible mitigation is transparent claim–evidence binding, not a numerical acceptance forecast. The manuscript is submission-ready only if these limitations remain visible, the public GitHub reviewer path functions, and the final package passes the compilation and provenance gates.

---

## 4. Remediation checklist

- [x] F1 reword C1 + line 122 (MPO, SYBA, RRS, PNS)
- [x] F2 fix Q(s,a) description (varying search-time components; post-hoc front explicitly qualified)
- [x] F3 regenerate all figures from v12 + real MDS; add figures to main & SM
- [x] F4 data-availability: public GitHub URL + reserved Zenodo DOI, explicitly marked pending
- [x] F5 add Funding + Ethics/Consent declarations
- [x] Final v12 statistics re-derived from `benchmark_molecules_opt_v12/p4_benchmark_merged.csv`
- [x] Correct SM ranking and v12 scalar weights
- [x] Correct abstract length and affiliation overfull box
- [x] Recompile main-SM-cover (0 errors, 0 undefined; bibtex exit 2 is expected for files without bibliographies)
- [ ] Complete 20-seed validated pre-activity SYBA rerun in `results/pareto_syba_validated/` (not required for the current evidence-bounded submission, but required before any claim of informative search-time SYBA optimisation)
- [ ] Human visual PDF inspection and package assembly
- [ ] git commit + push final P4 editorial corrections

## 5. Final editorial pass — 2026-08-10

**Substantive prose revision (same date):** the article was restructured around two explicit estimands: scalar search efficiency and candidate-set geometry. The title and abstract no longer imply that MCTS causally preserves alternatives or is scalar-superior. The journal-required `Contribution` heading now states the methodological contribution without using unverified pre-registration language. The introduction presents a testable decision-oriented question; Results report the scalar benchmark before the candidate-level front; Discussion interprets rather than inventories audit events. RRS/PNS remain computational proxies and the historical accessibility recomputation remains disclosed once in the appropriate methodological context.

- [x] Harmonised the main, SM and cover-letter title: “Pareto-guided Monte Carlo tree search exposes multi-objective trade-offs in antimalarial molecular generation”.
- [x] Labelled the hypervolume 18.99 as a secondary baseline re-scoring analysis, distinct from the canonical post-hoc Pareto-front hypervolume 1.2366.
- [x] Removed internal result-file paths from main-text captions where they were not needed for scientific interpretation; repository-level data availability remains at the end of the article.
- [x] Downgraded RRS/PNS wording to resistance-informed and docking-informed computational proxies; no direct biological validation claim remains.
- [x] Reframed greedy convergence as repeated path collapse within the evaluated fragment space rather than proof of a globally unique reward attractor.
- [x] Confirmed that QMC/VMC/DMC is absent from the canonical main, SM and cover letter.
- [x] Confirmed final source compilation and provenance checks; one minor cover-letter overfull box remains for human visual review.
