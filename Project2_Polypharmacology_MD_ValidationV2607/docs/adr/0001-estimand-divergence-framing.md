# ADR 0001: Estimand Divergence Framing for Docking vs MD

- **Status:** Accepted
- **Date:** 12 September 2026
- **Deciders:** Lead Researcher & Computational Chemistry Team

---

## Context & Problem Statement

In Project 2, comparing static Vina grid docking scores ($\Delta G_{\text{grid}}$) with explicit-solvent molecular dynamics trajectories (10-ns MD pose retention) revealed an $87.5\%$ divergence: docking scores frequently predicted weaker binding on mutant structures, whereas explicit-solvent MD showed full pose retention and minimum distances $< 3.5\text{ \AA}$. How should this discrepancy be framed in the manuscript and data analysis pipeline?

---

## Decision Drivers

1. **Avoid False Positive Clinical Claims:** Docking and short MD measure local geometric and thermodynamic proxies, not measured biological resistance or clinical efficacy.
2. **Methodological Rigor:** Presenting docking and MD as competing predictors creates a false dichotomy; they measure different computational estimands.
3. **JCIM Reporting Guidelines:** Align with Soares et al. (2023) guidelines on reporting MD simulations transparently.

---

## Considered Options

1. **Option A (Superficial Resolution):** Force docking scores and MD energies into a single averaged composite score.
2. **Option B (Rejection of Docking):** Dismiss static docking entirely as inaccurate.
3. **Option C (Estimand Divergence Framing - Selected):** Frame the mismatch as *Estimand Divergence*—static grid docking serves as an initial high-throughput screening filter, while short explicit-solvent MD acts as an essential structural stress test that filters rigid-grid artifacts.

---

## Decision Outcome

**Chosen Option:** **Option C**. 

### Positive Consequences
- Establishes a novel, rigorous conceptual framework (*Estimand Divergence*) for evaluating natural products against mutant panels.
- Explains why static grid docking over-penalizes flexible natural products while MD recovers resilient binding geometries.
- Provides a clean defense against reviewer critiques regarding docking/MD correlation.

### Negative Consequences / Trade-offs
- Requires explicit caveats in the manuscript stating that 10-ns MD measures local geometric pose retention rather than binding free energy or measured biological resistance.
