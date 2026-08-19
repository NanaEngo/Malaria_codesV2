# Graphical Abstract Specification — Paper 4

**Paper:** Pareto-guided Monte Carlo tree search for analysing multi-objective alternatives in antimalarial molecular design
**Target journal:** Journal of Cheminformatics (Springer / BioMed Central)
**Prepared:** 2026-08-15
**Audience for this document:** the AI/design tool that will construct the graphical abstract

---

## 0. Read this first — the one thing that must not go wrong

This paper reports an **honest negative result**. Random search beats the proposed method on the
scalar reward. The contribution is *not* that Pareto-MCTS wins; it is that a Pareto archive
preserves chemically distinct decision options that a single weighted score destroys, and that the
paper measures the cost of doing so.

**A graphical abstract that implies the proposed method outperforms the baselines is scientifically
false and will be rejected.** The previous version failed on exactly this point. Every design
decision below follows from that constraint.

Two claims must survive the reader's five-second glance:

1. Random search obtains the highest mean scalar reward; MCTS does not.
2. MCTS returns a four-point non-dominated front spanning a potency–accessibility trade-off that no
   single fixed weighting recovers.

If a viewer could come away thinking "their method scored best", the figure is wrong.

---

## 1. What the study actually did

Molecules are built fragment by fragment from benzene, at most 10 additions, using a Monte Carlo
tree search whose PUCT prior is scaffold-aware (fragment frequencies from ChEMBL27, scaffold
Tanimoto compatibility, reactivity penalty). Two things are then measured, and they are deliberately
kept separate:

- **A scalar benchmark** (efficiency): four methods — MCTS+ScafVAE, random, greedy, genetic
  algorithm — under one weighted reward, 20 seeds, 1000 iterations each.
- **A candidate-level Pareto analysis** (decision support): which distinct trade-off profiles remain
  visible when objectives are examined jointly instead of collapsed into one number.

The scalar benchmark answers "which method gets the biggest number". The Pareto analysis answers
"which chemically distinct compromises are still on the table". Treating these as one question is
the confusion the paper exists to dismantle, so the graphical abstract must keep them visually
distinct.

---

## 2. Numbers you may use — all verified, none may be altered

Everything is in `data/`. Use these values exactly; do not round further, recompute, or "clean up".
If a value you want is not listed here, it is not available — leave it out rather than invent it.

### 2.1 Scalar benchmark, medium vocabulary (37 fragments) — `data/benchmark_v12_medium.csv`

| Method | Mean reward | SD | Mean time (s) |
|---|---:|---:|---:|
| Random | 0.6724 | 0.0056 | 50.4 |
| MCTS+ScafVAE | 0.6649 | 0.0068 | 92.1 |
| Genetic algorithm | 0.6453 | 0.0124 | 2.0 |
| Greedy | 0.4278 | 0.0000 | 1.9 |

MCTS versus random: Δ = −0.0075, 95 % CI [−0.0107, −0.0043], t₁₉ = −4.97, p = 0.000085.
MCTS versus GA: t₁₉ = 6.95, p < 0.0001.
Greedy is deterministic — its SD is exactly zero because it returns the same molecule every seed.

### 2.2 The four-point Pareto front — `data/pareto_front_4_candidates.csv`

Merged from 20 independent seeds. Hypervolume 1.2366.

| Label | SMILES | MPO | SYBA | SA⁻¹ | RRS | PNS | Seed |
|---|---|---:|---:|---:|---:|---:|---:|
| P1 | `CNC(=O)c1ccc(OC(C)C(C)(C)C)c(OC)c1` | 0.910 | 1.000 | 0.778 | 0.211 | 1.0 | 13 |
| P2 | `COc1c(C)cc(-c2ccc(S(N)(=O)=O)cc2)cc1C` | 0.945 | 1.000 | 0.778 | 0.196 | 1.0 | 18 |
| P3 | `CC1CCC(n2cccn2)NC1(c1ccccc1)C1OCCO1` | 0.946 | 0.021 | 0.778 | 0.141 | 0.0 | 5 |
| P4 | `COc1cc(CO)c(O)c(C)c1C` | 0.729 | 0.994 | 0.778 | 0.223 | 1.0 | 6 |

SA is constant at 3.0 for all four; SA⁻¹ = (10 − SA)/9 = 0.778. Because it does not vary, **SA is
not a discriminating axis — never plot it as one.**

### 2.3 The decision insight — `data/scalar_weight_sweep.csv`

Across the normalised MPO–SYBA weight space, P2 is the scalar argmax over 95.6 % of it, and **P3 is
selected only when w_MPO ≳ 0.997 — 0.3 % of the space.** P3 is the highest-MPO molecule in the
study (0.946), and a fixed-weight scalar score would discard it in all but a degenerate corner. This
single fact is the strongest argument in the paper and is the best candidate for the figure's
right-hand panel.

### 2.4 Optional supporting numbers

- Full 80-fragment vocabulary (`data/benchmark_v12_allfrag.csv`): the gap **widens**, Δ = −0.0214,
  random above MCTS in 19 of 20 seeds. Use only if there is room; it reinforces panel B's message.
- Ablation main effects (`data/ablation_main_effects.csv`): ScafVAE +0.148, Pareto +0.108. **These
  come from a different reward configuration and are not comparable to the rewards in 2.1** — if you
  show them, separate them visually and label them "within-ablation effect".
- Front comparison (`data/front_comparison_by_method.csv`): MCTS front hypervolume 18.99, C-metric
  0.824. **A different hypervolume convention from the 1.2366 in 2.2** — see §4.

---

## 3. Required panel structure

A three-panel left-to-right narrative, 920 × 300 px. The order encodes the argument.

**Panel A — the method (left, ~30 % width).**
Fragment assembly as a search tree rooted at a benzene ring, branching into partially built
molecules, with the retained non-dominated candidates highlighted at the frontier. Convey: fragments
in, tree search, an archive of survivors out. Label the archive "non-dominated archive", not "best
molecules".

**Panel B — the honest benchmark (centre, ~30 %).**
Four bars, mean reward with SD error bars, ordered as they actually rank: Random 0.6724 > MCTS
0.6649 > GA 0.6453 > Greedy 0.4278. **Random must read as first and must not be de-emphasised.** Do
not colour MCTS as the "hero" bar. A short annotation carrying the paired result (Δ = −0.0075,
p = 0.000085) belongs here.

**Panel C — what the archive buys you (right, ~40 %).**
The four candidates in the MPO–SYBA plane, with a weight-space bar or inset showing that P2 wins
95.6 % of weightings while P3 survives only above w_MPO ≈ 0.997. Render the structures from the
SMILES in 2.2 if space allows; P2 and P3 are the essential pair, since they carry the trade-off.
This is where the reader should end.

**Bottom strip (optional, full width).** One sentence, plain type:
*"Random search wins the scalar reward; the Pareto archive keeps the options a single weighting
would discard."*

---

## 4. Scientific accuracy rules — non-negotiable

1. **Never imply MCTS superiority on scalar reward.** No upward arrows, trophies, checkmarks, green
   ticks, or "improved / optimised / superior" wording attached to the method.
2. **Two hypervolume conventions exist and are not interchangeable.** 1.2366 is over three active
   objectives, bounded by 1.1³ = 1.331. The 13.85–18.99 range in the front comparison is a
   four-objective convention with negated normalised vectors, bounded by 2.1⁴ = 19.45. **Never place
   them on one axis or in one legend.** If you show only one, show 1.2366 with its bound.
3. **RRS and PNS are computational proxies, not biology.** RRS is Morgan/Tanimoto similarity to
   docking-derived reference chemotypes. PNS is an average of three docking columns. Do not label
   them "resistance", "polypharmacology", "target engagement", "binding" or "activity" without the
   qualifier "-informed proxy". No protein ribbons, no binding-pocket cartoons, no parasite imagery
   implying a measured biological effect.
4. **No IC₅₀, EC₅₀, potency, efficacy or activity claims.** MPO is a computed multi-parameter score.
   The activity term is Tanimoto proximity to known actives — a similarity, not a measurement.
5. **No molecular dynamics anywhere.** No trajectories, no simulation boxes. None was run for this
   paper.
6. **SA is constant.** Never use it as a varying axis or as a size/colour channel.
7. **Greedy's zero variance is real**, not a plotting artefact. If error bars are shown, greedy's is
   legitimately absent — do not fake one, and do not drop greedy from the chart.
8. **The structures must be rendered from the exact SMILES given.** Do not redraw from imagination,
   substitute similar-looking scaffolds, or "beautify" the chemistry.

---

## 5. Format requirements

| Property | Value |
|---|---|
| Dimensions | 920 × 300 px (matches the existing asset; confirm against current JoC author guidelines before submission) |
| File size | under 150 KB |
| Format | PNG, RGB |
| Minimum font size | 8 pt equivalent at final size — must stay legible at 50 % zoom |
| Colour | colour-blind safe; never encode a distinction by red/green alone |
| Text | self-contained; no reliance on the article body, no citations, no reference numbers |
| Background | white or transparent |

The graphical abstract is uploaded as a standalone asset and is **not** referenced by
`\includegraphics` in the manuscript source — do not add a caption or a "Figure N" label.

---

## 6. Files supplied

```
Graphical_Abstract_Brief/
├── Graphical_Abstract_Specification.md   this document
├── Graphical_Abstract_Template.txt       layout template / prompt for the tool
├── data/
│   ├── pareto_front_4_candidates.csv     the 4 candidates, SMILES + objectives (real artifact)
│   ├── benchmark_v12_medium.csv          Table 1, the canonical scalar benchmark
│   ├── benchmark_v12_allfrag.csv         Table 4, 80-fragment vocabulary
│   ├── scalar_weight_sweep.csv           Table 2, the weight-space argument
│   ├── ablation_main_effects.csv         within-ablation effects, different reward config
│   └── front_comparison_by_method.csv    per-method fronts, 4-objective HV convention (real artifact)
└── reference/
    ├── CURRENT_graphical_abstract_REJECTED.png   the version being replaced — do not imitate
    ├── figure1_benchmark_bar.png                 the paper's own benchmark figure
    └── figure2_pareto_front.png                  the paper's own Pareto figure
```

`pareto_front_4_candidates.csv` and `front_comparison_by_method.csv` are copied unmodified from the
study's result directories. The remaining CSVs are summary tables transcribed from the manuscript,
each carrying a header comment naming its source and its interpretation limits.

---

## 7. Acceptance checklist

The result is acceptable only if every line is true:

- [ ] Random is shown obtaining the highest mean scalar reward, unambiguously.
- [ ] Nothing suggests the proposed method won the scalar comparison.
- [ ] The four Pareto candidates match the supplied SMILES exactly.
- [ ] Only one hypervolume convention appears, with its bound stated.
- [ ] RRS/PNS, if shown, are labelled as computational proxies.
- [ ] No biological, binding or activity claim appears in any form, including imagery.
- [ ] SA is not used as a varying axis.
- [ ] Greedy is present and its zero variance is not disguised.
- [ ] 920 × 300 px, under 150 KB, legible at 50 % zoom.
- [ ] The trade-off between P2 and P3 is legible without reading the paper.
