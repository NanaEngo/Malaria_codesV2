# Independent review — claim-to-ledger mapping (P4)

**Date:** 2026-08-17
**Trigger:** author instruction — "launch a read-only agent with fresh context on the claim-to-ledger mapping"
**Checker:** separate agent, fresh context, read-only tools. Maker (this session) did not supply the findings; maker re-verified them afterwards against primary source.
**Scope:** the maker≠checker gate recorded as open at `manuscript/LaTeX/SUBMISSION_MANIFEST.md:65`.

## Verdict

**No — qualified-negative.** The claim-to-ledger mapping does not pass. Three CRITICAL and six HIGH defects survive independent verification. The gate is closed in the sense that it ran; it is not satisfied.

**Maker's disposition after re-verification (step 5.2, run trying to reject the checker):**

- 3 CRITICAL — **upheld**, each re-derived from primary source by command. CRITICAL-1 sharpened with two facts the checker did not have.
- 1 CRITICAL — **RE-GRADED to MEDIUM** by the DC4 pass. The alleged panel substitution does not exist; the residual defect is a disclosure gap. See *Re-graded*.
- 5 HIGH — **upheld**. HIGH-2's mechanism is now decisive rather than inferential.
- 1 checker HIGH — **REJECTED**. The manuscript claim it alleged does not exist.
- 1 checker HIGH — **RE-GRADED to MEDIUM**. The number traces; the defect is attribution, not provenance.
- MEDIUM/LOW — recorded as checker-reported, **not independently re-verified**, except the two DC4 raised and proved by command (Conclusions omission; SM carries no inferential statistic).
- 1 defect **neither checker found**, surfaced while verifying DC4: the retained virtual loss printed in the manuscript is not the code default. Recorded as HIGH-3, which brings HIGH to six.

**Untouched by every finding:** the central negative result. Pareto-MCTS does not beat Random on scalar reward (paired t₁₉ = −4.97, p = 0.000085, Δ = −0.0075, 95 % CI [−0.0107, −0.0043]). No finding below bears on it in either direction.

## Done-criteria status

| | Criterion | Status |
|---|---|---|
| DC1 | Every numeric claim in main text + SM traced to a deposited artifact | **run** — 119 values: 109 TRACED, 6 MISMATCH, 4 UNTRACED |
| DC2 | Abstract/Conclusions numbers contained in the tables they cite, signs included | **PASS** — containment holds, all signs correct |
| DC3 | Hypervolume convention used consistently across both documents | **PASS** — no defect above LOW; three anti-comparison warnings present, all four 1.2366 sites consistent |
| DC4 | Negative result stated without softening across Abstract/Results/Discussion/Conclusions/Limitations | **PASS on integrity, FAIL on Limitations completeness** — no softening, no sign or bound error; Limitations omits six disclosable items |

### DC1 row-level inventory — NOT PERSISTED

The 119-row table was produced in the checker's context and never written to disk. Three recovery passes over the session transcripts failed (search by header text; search by size; search by table shape — "no table-shaped block found"). A candidate extract was misidentified and deleted rather than kept as a misleading artifact.

Only the counts survive: **119 values / 109 TRACED / 6 MISMATCH / 4 UNTRACED**. The row detail is regenerable **only by re-running DC1**. It must not be reconstructed from memory.

### DC2 detail

Every Abstract and Conclusions figure is contained in `tab:sm_benchmark`, `tab:sm_pareto` or the long-form DAR, with no value introduced downstream of its source, and the negative signs on Δ and on the confidence-interval bounds are carried correctly.

### DC3 detail — hypervolume convention consistency: PASS

Run as an independent read-only pass with fresh context, then re-verified here by command under step 5.2. **No defect above LOW.**

Confirmed by command:

- Three explicit anti-comparison warnings exist and sit at the cited lines. The two conventions are declared non-comparable in three places — the `tab:front_comp` caption, the `SM.tex` S2 hypervolume paragraph (`SM.tex:109`, "not numerically comparable with the hypervolumes reported for the"), and the Pareto-front-maintenance methods paragraph.
- All four sites printing 1.2366 use the front-internal convention with the bound $1.1^{4}=1.4641$; the cross-method sites use the $(1.1+1)^{4}=19.45$ bound. No site mixes them.
- The four-objective claim is independently grounded in `results/pareto/merged_pareto_front.csv` without reference to the recompute log: `sa` is constant at 3.0000 across all four rows, `syba` is not (1.0000, 1.0000, 0.0208, 0.9944), so `_detect_active_objectives()` drops `sa` alone and retains MPO, SYBA, RRS, PNS.
- The `n2_*_merged.csv` hypervolume columns are cited by **neither** `.tex`, which is what makes the withdrawn "convention-dependent conclusion" flag a non-issue rather than a suppressed one.
- `scripts/p4_pareto_provenance_check.py` contains **zero** occurrences of the string `assert`. Manifest note 57's word "asserts" is semantically accurate about what the script enforces but lexically wrong. Cosmetic.

LOW items, none blocking: the manifest's "asserts" wording above; ~~stale archival text at `outputs/analysis/number-reconciliation-20260815.md:81` and `:85` describing HV as three-objective (archival, not a submission file)~~ — **withdrawn 2026-08-18, the described text is not in that file**: `grep -n "three-objective\|three objective\|3-objective\|1\.1244" outputs/analysis/number-reconciliation-20260815.md` returns nothing across all 143 lines, and the H2 block at `:81`--91 in fact reads "For k = 4 that caps HV at 1.4641, and the SM's 1.2366 obeys it", which is the correct four-objective description. Whatever the checker read, it was not this file at these lines; and an optional strengthening — have `p4_pareto_provenance_check.py` assert `active == ["mpo","syba","rrs","pns"]` rather than only that `sa` is inactive. Adding a check is permitted; author's call.

**Now re-derived** (2026-08-18, closing the one item this record previously left open): the checker's three-objective figure is **confirmed exactly** and its subset identified. `scripts/p4_hv_independent_recheck.py` re-implements the algorithm from the spec at `scripts/p4_mcts_pareto.py:168`--198 and computes the hypervolume by exact inclusion--exclusion over the 15 nonempty subsets of the 4 front points, importing nothing from `p4_mcts_pareto`, so it cannot inherit an error in the method it checks. It reproduces the published four-objective **1.236644** against 1.2366 (gate satisfied first, as required), agrees with pymoo to 1e-9, and gives **1.124376 for the subset that drops `syba`** (MPO/RRS/PNS) — the checker's figure to all six digits.

One caution the re-derivation surfaced that the checker's 4-decimal quotation hid: dropping `pns` instead gives **1.124289**, a *different* subset agreeing to 4 decimal places and differing only at the 5th. So "1.1244" alone does not identify which objective was dropped; only the 6-digit form does. The script flags the two cases distinctly rather than reporting a match twice. This does not affect the finding — `syba` is non-constant on this front, so any three-objective recompute is the wrong computation regardless of which objective it omits — but it does mean the figure should be cited at six digits wherever it appears.

### DC4 detail — negative-result integrity: PASS on integrity, FAIL on Limitations completeness

Run as an independent read-only pass with fresh context. Every line citation checked under step 5.2 was exact; nothing in this pass failed verification. One of its findings **overturns a maker CRITICAL** — see *Re-graded*.

**DC4.2 — not softened. Confirmed.** No hedge, qualifier or comparative softener touches the head-to-head result. Loss-carrying verbs appear at `refined.tex:63, 64, 138, 248, 272, 342`, and MCTS is the grammatical subject of the losing verb at every one ("MCTS did not improve", "the MCTS deficit", "MCTS trails by") — the loss is never displaced onto a passive construction or onto the baseline. Every `comparable` in `SM.tex` (`:109`, `:238`) is about convention or ablation incommensurability, not about the benchmark.

**DC4.3 — no sign or bound error.** Signs on Δ, both CI bounds, and the arm assignment are all correct wherever they appear.

Two MEDIUM omissions, both proved by command here:

- **The Conclusions omit the larger effect.** Under the full 80-fragment vocabulary the deficit is ≈ 3× the headline: −0.0214 versus −0.0075. The value 0.0214 appears at `refined.tex:63` (Abstract) and `:248` (Results) and **nowhere else**; `:342` (Conclusions) carries 0.000085, 0.0043, 0.0075 and 0.0107 but not 0.0214. A reader who reads the Conclusions alone meets only the smaller of the two deficits.
- **The SM prints no inferential statistic anywhere.** A grep for `4.97|0.000085|t_{19}|Delta|95\%|CI ` across `SM.tex` returns only the factorial-ablation Δ values at `:226`–`:229` (+0.148, +0.108, +0.079, +0.055) and the table header at `:243`. The paired t, the p value and the confidence interval live only in the main text.

Two LOW: "modest margin" at `refined.tex:272` and `:342` (accurate, but the softest available phrasing for a significant deficit); and the Highlights never state the loss at all.

**DC4.4 — Limitations completeness: FAIL.** `\subsection{Limitations}` at `refined.tex:284` runs to two paragraphs only — `:286` on fragment vocabulary and `:288` on the scoring functions being computational proxies. That structure is itself the proof: six disclosable items cannot be in it.

| | Item | Grade | Note |
|---|---|---|---|
| i | Greedy scored under a different rule (terminal, not best-intermediate) | CRITICAL | Actively contradicted at `refined.tex:318`. Same defect as CRITICAL-1. |
| ii | Fragment priors are heuristic, not ChEMBL27-derived | CRITICAL | Actively contradicted at `refined.tex:313`. Same defect as CRITICAL-2. |
| iii | Multi-objective benchmark reads the v11 directory | HIGH | Same defect as CRITICAL-3, undisclosed. |
| iv | RF training panel is 74.2 % active (14721 / 5115 of 19836) | MEDIUM | Row count is correctly reported; the **class prevalence** conditioning AUC 0.9479 ± 0.0040 is not disclosed. Re-graded down from the maker's CRITICAL-4 — see *Re-graded*. |
| v | Benzene versus methane root across the two sbatch configurations | HIGH | Same defect as HIGH-1. |
| vi | Three of five "retained" hyperparameters never screened | HIGH | Mechanism now decisive — see HIGH-2. |
| vii | Table 4 per-seed artifact absent | **DISCLOSED** | `refined.tex:358`, cross-referenced at `:346`. Not a completeness failure. |

Item (vii) is the one DC4 candidate that the manuscript already handles. Items (i) and (ii) are worse than omissions: the text asserts the opposite of the code.

**Spot-checked, not exhaustively re-walked:** DC4.1's ~20-line enumeration of every locus where the negative result is stated. Confirmed at the loci level (63, 64, 138, 248, 272, 342) rather than line by line.

## CRITICAL

### CRITICAL-1 — Greedy is scored under a different rule from every method it is compared to

`scripts/p4_mcts_benchmark.py` returns the best *intermediate* reward for Random and GA, and the *terminal* reward for Greedy:

```
147:    return best_smiles, best_reward, time.perf_counter() - t0      # run_random  — BEST intermediate
179:    return best_smiles, oracle(state), time.perf_counter() - t0    # run_greedy  — TERMINAL state
215:    return best_smiles, best_reward, time.perf_counter() - t0      # run_ga      — BEST intermediate
```

Inside `run_greedy` the best intermediate is tracked and then discarded:

```python
def run_greedy(env, oracle, args):
    best_reward, best_smiles = oracle(state), state
        if r > best_reward:
            best_reward, best_smiles = r, state
    return best_smiles, oracle(state), time.perf_counter() - t0
```

The deposited pair is therefore internally inconsistent: `best_smiles` is the best intermediate molecule, the reward printed beside it belongs to the terminal state.

Two aggravating facts established on re-verification, beyond the checker's framing:

- `manuscript/LaTeX/P4_Pareto_MCTS_JoC_refined.tex:318` states the very rule Greedy violates: "During each rollout the oracle is therefore evaluated at every construction step; the highest-scoring intermediate---rather than the terminal state---is returned."
- `refined.tex:282` claims that correction as contribution (iii): "a rollout-degradation failure mode is diagnosed and corrected."

Line 179 is the uncorrected path. The paper claims the fix as a contribution while one baseline still runs the bug.

The authoritative ledger documents the bug and then mis-states its status — `../docs/archive/md_full_20260812/P4_DATA_ANALYSIS_REPORT.md:496`:

> "**Greedy reporting bug (bonus finding):** `p4_mcts_benchmark.py:179` returns `oracle(state)` (final state) instead of `best_reward` (best intermediate). True greedy reward ~0.645, not 0.428. Fixed in v12; allfrag greedy shows same pattern (reported 0.459 vs actual ~0.645)."

"Fixed in v12" is false — line 179 is unchanged — and the sentence self-contradicts, since an allfrag greedy still showing "the same pattern" is not a fixed path.

**Blast radius.** `refined.tex` lines 63, 72, 113, 125 (`Greedy & 0.4278 & 0.0000 & 0.4278 & 0.4278 & 1.9`), 138, 224, 232, 260 (`Greedy & 0.4593 & 0.0000 …`), 278; plus `SM.tex:214`. `refined.tex:276` opens `\subsection{Why greedy collapses under activity-augmented reward}` and 278 builds on it: "The most striking result in \Cref{tab:benchmark} is the deterministic greedy baseline scoring 0.4278---0.2446 below random search, with zero variance across seeds." That mechanism story rests on the residue of the bug the paper says it fixed.

**Every honest disposition changes a published number and deletes or rewrites §276–278.** Author's decision; no fix applied.

### CRITICAL-2 — Fragment priors are heuristic, described in the manuscript as ChEMBL27-derived

`scripts/p4_mcts_policy.py:33–45`:

```python
# NOTE: These priors are NOT derived from actual ChEMBL27 data.
# They are heuristic values based on medicinal chemistry experience.
...
# These values were calibrated to give reasonable exploration
# diversity in early MCTS iterations. They work adequately for
# the current benchmark but are not quantitatively grounded.
FRAGMENT_PRIORS: dict[str, float] = {
    "c1ccc([*])cc1":     0.95,   # Phenyl - most common
```

`refined.tex:313` claims the priors come from "ChEMBL27 fragment frequencies, scaffold Tanimoto compatibility and a reactivity penalty via a softmax." The source file states the opposite in its own comment.

### CRITICAL-3 — Multi-objective benchmark reads the v11 directory while v12 exists

`scripts/p4_benchmark_multiobj.py`:

```
27:  BENCH = PROJECT / "results" / "benchmark_molecules_opt"
41:  for f in sorted(BENCH.glob("p4_benchmark_molecules_seed_*.csv")):
```

Both `results/benchmark_molecules_opt` and `results/benchmark_molecules_opt_v12` exist, 20 seed CSVs each. A wrong constant, not a missing-directory fallback. Checker's overlap test: 59/59 molecules present in v11, 24/59 in v12, 55 unique to v12.

Maker's own uniqueness count was non-decisive (`cut -d, -f1 | sort -u` returned 5 for both directories — wrong column) and is not relied on. The decisive fact is that `BENCH` names the v11 directory while both directories exist.

*(CRITICAL-4 was withdrawn on re-verification and moved to* Re-graded *— the two panel files are distinct and each is cited correctly.)*

## HIGH

1. **Root molecule contradicted between the two search configurations.** `scripts/p4_benchmark_molecules_opt_v12_array.sbatch:70` sets `INITIAL_SMILES="${INITIAL_SMILES:-C}"` (methane, passed at :93); `scripts/p4_pareto_array.sbatch:63` sets `INITIAL_SMILES="${INITIAL_SMILES:-c1ccccc1}"` (benzene). Benzene is correct for the Pareto search and wrong for the v12 scalar benchmark. `refined.tex:306` and `SM.tex:51` say "rooted at benzene" with no distinction.
2. **Three of five "retained" hyperparameters were never screened, and a fourth is printed at a value the screen never produced.** The mechanism is now decisive rather than inferential. `scripts/p4_mcts_hparam_search.py` defines two grids; the manuscript's "32 configurations" at `refined.tex:100` identifies the screen as `QUICK_GRID`, which is $2^{5}=32$ cells:

   ```python
   QUICK_GRID: dict[str, list[float]] = {
       "pw_alpha":       [0.3, 0.7],
       "pw_k":           [0.5, 2.0],
       "virtual_loss":   [0.01, 0.2],
       "c_puct":         [0.5, 5.0],
       "temperature":    [0.5, 1.0],
   }
   ```

   The retained configuration displayed at `refined.tex:102`–`106` is $c_{\text{PUCT}}=5.0$, $\nu=0.01$, $pw_{\alpha}=0.5$, $pw_{k}=1.0$, $T=0.8$. Only $c_{\text{PUCT}}=5.0$ and $\nu=0.01$ are QUICK_GRID levels. **$pw_{\alpha}=0.5$, $pw_{k}=1.0$ and $T=0.8$ appear in none of its level sets** — and each equals the runner's own default (`pw_alpha=0.5`, `pw_k=1.0`, `temperature=0.8`). They were not selected by the screen; they are the values the screen never varied. This also explains the identical 0.3165 marginals: a marginal over a factor held constant is the grand mean.
3. **Retained virtual loss is not the code default, and the manuscript does not say which value ran** — a finding neither checker reported, surfaced while verifying DC4. `refined.tex:103` prints $\nu=0.01$ as retained, while the runner defaults `virtual_loss=0.05`. Unlike the three above, $\nu$ *was* screened (levels 0.01 and 0.2), so 0.01 is a legitimate selection — but any run that did not pass `virtual_loss` explicitly used 0.05, and nothing on disk states which of the two produced the reported benchmark. Either confirm 0.01 was passed to the production runs, or report 0.05.
4. **Table 4 has no primary artifact.** `results/benchmark_v12_allfrag/` is absent; the only on-disk trace is a 4-row transcription at `manuscript/Graphical_Abstract_Brief/data/benchmark_v12_allfrag.csv`. The "19 of 20" claim is uncheckable in principle from summary statistics. Disclosed at `refined.tex:358`.
5. **Environment claim names a file that does not exist.** `refined.tex:336` cites Python 3.11 plus an environment file; no `environment.y*ml` or `requirements*.txt` exists under P4 (only Project3 ×4 and Project5).
6. **"30 iterations" screening budget untraced** — script default is 50.

## Re-graded

**Activity-oracle training panel — CRITICAL (maker's CRITICAL-4) → MEDIUM (undisclosed class prevalence).** The alleged substitution does not exist. The two file names are two different panels, and each document cites the one its own pipeline reads:

```
Project5_GNN_Transformer_DrugDiscovery/results/p5_public_chembl_malaria.csv   22447 rows   19321 active / 3126 inactive
Project5_GNN_Transformer_DrugDiscovery/results/p5_canonical_panel.csv         19836 rows   14721 active / 5115 inactive
```

`SM.tex:97` reads "panel (\num{22447} molecules, including \num{19321} active entries)" — the reward-proximity panel, and `scripts/p4_mcts_oracles.py:130` plus `scripts/p4_activity_oracle_validation.py:10,51` are exactly the scripts that read it. `refined.tex:288` reports the 19 836-row figure — the RF training panel, matching `scripts/p4_activity_rf_oracle.py:24` and `results/pareto/p4_activity_rf_oracle.json` (`"p5_n": 19836`, `"p5_active": 14721`). Row counts and active counts are correct on both sides; no number is wrong and no file is misnamed.

The residual defect is a disclosure gap, not a provenance error: the RF training panel is **74.2 % active** (14 721 / 5 115), and that class prevalence is nowhere stated. AUC 0.9479 ± 0.0040 on a panel three-quarters positive is not the same evidence as the same AUC on a balanced one. One sentence in Limitations closes it. See DC4.4 item (iv).

**"Factor of approximately 2.6" — HIGH (UNTRACED) → MEDIUM (attribution).** `refined.tex:318` names its referent explicitly ("relative to the agent without global best-molecule tracking") and the arithmetic checks: v6 0.280 → v11 0.7276 = 2.599. The number traces. The real defect is confounding — other changes landed between v6 and v11, so the factor is not isolated by a controlled ablation. The project's own audit note already says so: "C9 rollout +2.6× | partly (uncertainty) | narratif non isolé par ablation contrôlée."

## Rejected

**Progressive widening "5--20 vs code's 31" — WITHDRAWN.** The alleged manuscript range does not exist. `refined.tex:313` gives the formula `\max(5,\,k\,N^{\alpha})` with k = 1.0, α = 0.5, which matches `scripts/p4_mcts_agent.py:381` exactly:

```python
max_actions = max(5, int(self.pw_k * (N ** self.pw_alpha)))
```

Neither document contains "5--20" or "5-20". The checker's own line citations for this item and for the 2.6× item were inaccurate, which is how both errors surfaced.

## MEDIUM / LOW — checker-reported, not independently re-verified

- `IGD_loo` internal inconsistency: GA and `baselines_pooled` byte-identical at 0.30684960014869395 although pooled ⊋ GA; `mcts_canon` has `igd_loo == igd` = 0.49202497393571343, violating the manuscript's own definition at `refined.tex:217`.
- `tab:scalar_sweep` omits cand_idx 0 = P1, and prints P2's lower bound as 0.0000 where the source is 1e-05.
- ANOVA F = 350.1 reported with df_between only; df_within = 36 omitted.
- `CombiMOTS2026` carries `year = 2025`.
- `Temgoua2026b` is MD-titled but cited for a docking-derived, MD-free signal (`refined.tex:83`, `332`, `292`).
- Three ledger-staleness items in which the manuscript is the correct party.

## What this gate did and did not establish

**Did:** ran an independent checker over the claim-to-ledger mapping; produced a traceability count for DC1; confirmed Abstract/Conclusions containment with correct signs (DC2); confirmed hypervolume-convention consistency with no defect above LOW (DC3); confirmed the negative result is stated without softening and with no sign or bound error, while failing Limitations on completeness (DC4); surfaced three CRITICAL defects that survive re-verification from primary source; and surfaced one defect neither checker reported — the retained virtual loss printed at `refined.tex:103` is not the runner's default.

**Did not:** persist the DC1 row-level inventory — only its counts survive, and the detail is regenerable only by re-running DC1, not by reconstruction from memory; or re-verify any MEDIUM/LOW item.

**Closed after the fact (2026-08-18):** the three-objective figure, listed here as not re-derived when this record was first written, now *is* re-derived — independently, by `scripts/p4_hv_independent_recheck.py`, which passed the required four-objective gate (1.236644 vs the published 1.2366) before its three-objective output was used, and identified 1.124376 as the drop-`syba` subset. See the "Now re-derived" paragraph above for the result and the 4-decimal-collision caveat.

**Also established: both makers are fallible, in both directions.** Two checker findings did not survive re-verification — one rejected outright (the alleged progressive-widening range, present in neither document) and one downgraded (the 2.6× rollout factor, which traces but is not isolated by a controlled ablation), both with inaccurate line citations. One of *this session's own* upheld findings did not survive either: recorded CRITICAL-4 alleged a substituted activity panel, and counting both CSVs by command showed two distinct panels each cited correctly, so it was withdrawn and re-graded to a MEDIUM disclosure gap. That is why the CRITICAL count fell from four to three, and it is the clearest evidence in this record that a finding is worth only the command that re-derives it.
