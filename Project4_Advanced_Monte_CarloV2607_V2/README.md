# P4 — Pareto-guided Monte Carlo and MCTS

**Status:** canonical v12-activity scalar benchmark complete; manuscript package aligned; final deposit/author review remains.
**DAR:** `P4_DATA_ANALYSIS_REPORT.md`

## Scientific question

Does Pareto-guided MCTS improve multi-objective candidate-set quality even when it does not maximise a scalar reward?

## Canonical results

| Method | Mean reward |
|---|---:|
| Random | 0.6724 ± 0.0056 |
| MCTS + ScafVAE | 0.6649 ± 0.0068 |
| GA | 0.6453 ± 0.0124 |
| Greedy | 0.4278 ± 0.0000 |

MCTS is below Random on the scalar benchmark (paired t₁₉=−4.97, p=0.000085) but above GA (p<0.0001). The separately locked pre-activity Pareto front contains four non-dominated solutions with hypervolume 1.2366. Its SYBA signal was constant during search and recomputed post hoc; it is not presented as informative historical optimisation.

## QMC boundary

Tier 1 SCF infrastructure is functional. Tier 2 candidate-level VMC/DMC remains diagnostic because of DMC population collapse; no publication-grade QMC energy claim is made.

## Canonical locations

- Scalar benchmark: `results/benchmark_molecules_opt_v12/`
- Pareto artifact: `results/pareto/`
- Manuscript/SM/cover: `manuscript/LaTeX/`
- Active data-analysis source: `P4_DATA_ANALYSIS_REPORT.md`

P1/P2-informed RRS/PNS terms are computational proxies, not direct biological or MD-RRS measurements.
