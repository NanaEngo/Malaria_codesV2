# Lightweight robustness outputs

These files are local, deterministic sensitivity analyses over the canonical
17-candidate P2 Set-C docking cohort.

- `rrs_threshold_sensitivity.csv`: WT eligibility thresholds 4, 5, 6 and 7 kcal mol⁻¹ crossed with retention rules 70/80, 75/85 and 80/90 percent.
- `rrs_leave_one_mutant_out.csv`: canonical threshold with each mutant omitted in turn.
- `docking_score_perturbation.csv`: deterministic score perturbations of −20%, −10%, +10% and +20%.
- `lightweight_analysis_manifest.json`: input hash, scope, analysis parameters and explicit STRING multi-threshold status.

STRING 400/700/900 sensitivity remains `NOT_COMPUTED_MISSING_THRESHOLD_SPECIFIC_STRING_MATRICES`; no threshold-specific network result is inferred from the canonical 700 matrix.

These outputs assess robustness of operational docking-RRS summaries. They are
not independent validation, biochemical affinity estimates, or evidence of
resistance circumvention. They must not replace the canonical RRS outputs or be
silently promoted into manuscript claims without an explicit dated audit.
