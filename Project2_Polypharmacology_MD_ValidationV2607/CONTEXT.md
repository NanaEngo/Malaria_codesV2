# Project 2 Domain Model — CONTEXT.md

This document defines the canonical domain vocabulary for Project 2 (Polypharmacology & MD Validation). It contains domain concepts and glossary definitions only, devoid of code implementation details.

---

## Glossary & Domain Concepts

### 1. Estimand Divergence
The systematic quantitative discrepancy between static grid docking affinity estimates ($\Delta G_{\text{grid}}$) and explicit-solvent molecular dynamics pose retention ($\mathrm{MD\text{-}RRS}_{\text{distance}}$). Static grid docking interprets fixed-grid steric collisions as a loss of binding ($87.5\%$ divergence), whereas explicit-solvent MD allows active-site conformational relaxation to maintain tight ligand anchoring ($< 3.5\text{ \AA}$).

### 2. Relative Resistance Score (RRS)
A per-target quantitative resilience metric defined as:
$$\mathrm{RRS}_t = \frac{|\Delta G_{\mathrm{mutant}, t}|}{|\Delta G_{\mathrm{WT}, t}|} \times 100$$
To prevent division-by-zero artifacts, candidates with non-binding wild-type denominators ($|\Delta G_{\mathrm{WT}, t}| < 5.0\text{ kcal/mol}$) are strictly excluded.

### 3. RRS Classification Tiers
- **Class A* (Pillar Lead):** All available mutant RRS values $\ge 80\%$ with strong wild-type binding anchor ($\Delta G_{\mathrm{WT}} \le -8.0\text{ kcal/mol}$).
- **Class A (Resilient Lead):** All available mutant RRS values $\ge 80\%$.
- **Class B (Moderate Resilience):** All available mutant RRS values $\ge 70\%$ (but not all $\ge 80\%$).
- **Class C (Partial Resilience):** At least one mutant RRS $\ge 80\%$, but not all $\ge 70\%$.
- **Class D (Susceptible):** No mutant RRS reaches $80\%$.

### 4. Antimalarial Chemical Space Index (ACSI)
A composite chemical-space metric evaluating candidate drug-likeness, combining Quantitative Estimate of Drug-likeness ($\text{QED}$), Synthetic Accessibility ($\text{SYBA}$), fraction of $sp^3$ carbons ($Fsp^3$), and Multiparameter Optimization ($\text{MPO}$).

### 5. Polypharmacological Network Score (PNS)
A target-weighted network centrality metric quantifying multi-target engagement across *Plasmodium falciparum* resistance targets (PfDHFR, PfCRT, PfATP4, PfClpP).

### 6. PfCRT Vacuolar Protonation State
The specific protonation regime of the PfCRT transporter under acidic digestive vacuole conditions ($\text{pH } 5.2$), requiring protonated histidine residues (His97/His53) and basic ligand sites.
