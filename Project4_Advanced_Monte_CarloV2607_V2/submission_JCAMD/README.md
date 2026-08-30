# P4 JCAMD Submission Package

**Journal:** Journal of Computer-Aided Molecular Design (JCAMD), Springer Nature
**Manuscript:** "Pareto-guided Monte Carlo tree search for analysing multi-objective alternatives in antimalarial molecular design"
**Compiled:** 30 August 2026
**Status:** Submission-ready (canonical manuscript in `../manuscript/LaTeX/`)

---

## Required files

- [x] **Main manuscript (TeX):** `P4_Pareto_MCTS_JCAMD.tex` (renamed from `P4_Pareto_MCTS_JoC_refined.tex`)
- [x] **Main manuscript (PDF):** `P4_Pareto_MCTS_JCAMD.pdf`
- [x] **Supporting Information (TeX):** `P4_Pareto_MCTS_JCAMD_SM.tex` (renamed from `P4_Pareto_MCTS_JoC_SM.tex`)
- [x] **Supporting Information (PDF):** `P4_Pareto_MCTS_JCAMD_SM.pdf`
- [x] **Bibliography:** `P4_Bibliography.bib` (target journal header updated to JCAMD)
- [x] **Cover Letter (TeX + PDF):** `Cover_Letter_P4_JCAMD.tex` / `Cover_Letter_P4_JCAMD.pdf`
- [x] **Manifest:** `SUBMISSION_MANIFEST_JCAMD.md`
- [x] **Graphics (figures):** `Graphics/`

## Source of truth

This package is a self-contained snapshot generated from `../manuscript/LaTeX/`. Any change to the canonical manuscript must be re-compiled and re-copied here.

## Notes

- Honest-negative scalar benchmark preserved (Random 0.6724 > MCTS 0.6649).
- Pareto front 4 non-dominated points, HV 1.2366 — exposed but not over-claimed.
- JCAMD traditional subscription (NO APC), in contrast to APC-bearing JoC.
- No journal-recommended reviewer list was added; JCAMD invitation via Springer Nature Editorial Manager.