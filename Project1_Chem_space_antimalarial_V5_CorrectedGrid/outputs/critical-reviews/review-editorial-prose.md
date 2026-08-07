# Editorial Prose Review — V4 Corrected Manuscript

**Scope:** Main manuscript (`Antimalarial_Candidates_African_NP_V2607.tex`), supplementary material (`Antimalarial_Candidates_African_NP_V2607_SM.tex`), and cover letter (`Cover_Letter.tex`).

**Date:** 2026-07-26

---

## Anti-AI Lexicon Scan

- **Project-specific anti-AI lexicon file:** not found (`find` returned no `*lexicon*` file in the project tree).
- **User-supplied anti-AI scan:** **0 hits** on the three `.tex` files.
- **Broad grep for generic AI-style markers** (`leverage`, `delve`, `robust`, `furthermore`, `intricate`, `tapestry`, `notably`, `underscores`) returned only standard scientific usage (e.g., "landscape", "scaffold", "exhibit", "demonstrate") — none of these are egregious in a chemistry manuscript.
- **Verdict:** no AI-prose red flags requiring rewording. Continue to rely on standard scientific editing for the issues below.

---

## HIGH — Issues that should be fixed before submission

| # | File | Line | Issue | Why it matters | Suggested fix |
|---|------|------|-------|----------------|---------------|
| 1 | Main manuscript | 146 | `median SA score of $\num{3.51} \pm \num{1.45}` | Median values should not be reported with a standard deviation; this is a statistical convention error. | Report as `mean SA score of $3.51 \pm 1.45$` or, if the value is truly a median, give the median with IQR, e.g. `median SA score of $3.51$ [IQR $2.06$–$4.96$]`. |
| 2 | Main manuscript | 216 | Redocking described as `100.0% success rate (5/5)` | Omits that only 5 of 10 co-crystallized ligands were alignable; the other 5 were excluded due to SDF atom-ordering mismatches. This reads as success on all ligands. | Add the full context: `5/5 alignable ligands (5/10 overall; 5 excluded due to SDF atom-ordering mismatches)` or rephrase to avoid implying 100% success on the full set. |
| 3 | Main manuscript | 220 | Table caption: `N = number of MMV actives in the target subset` | The `N` values (399, 198, 399, 198) match the *total* compound counts in the SM summary table, not the active counts. The SM also contradicts itself (line 1042 says `PfDHFR: N = 399` actives; line 1267 says `Total = 399`, `Actives = 132`, `Decoys = 267`). | Update the caption to `N = total number of compounds in the target subset (actives + decoys)` and reconcile the SM active/decoy counts so that every table uses the same definitions. |
| 4 | SM | 292 | PCA table: `PC4 variance = 0.000`, `% explained = 1.1%`, `cumulative = 100.0%` | Numerically inconsistent: if variance is `0.000`, % explained should be `0.0%` and cumulative should be `98.9%`. | Recalculate and align the three columns, or remove PC4 if it contributes essentially zero variance. |
| 5 | SM | 851–868 | VAE comparison table populated entirely with `N/A` | The caption claims the table supports the choice of 64 latent dimensions, but no metrics are available. The table is therefore uninformative and weakens the argument. | Either populate the table with real validation metrics, replace it with a brief textual justification, or remove it if the data are unavailable. |

---

## MEDIUM — Clarity, consistency, or grammar issues

| # | File | Line | Issue | Suggested fix |
|---|------|------|-------|---------------|
| 6 | SM | 496 | `a effective multi-dimensional filter` | Grammar error. | Change to `an effective multi-dimensional filter`. |
| 7 | Main manuscript | 317 | `latent space optimisation` (British spelling) | Inconsistent with `optimization` used elsewhere (e.g., lines 72, 181, 202). | Use `optimization` throughout. |
| 8 | SM | 181, 370, 373, 674 | `synthesizable` vs. `synthesisable` | Mixed British/American spelling. | Standardize to `synthesizable` (or `synthesisable`, but choose one and apply consistently). |
| 9 | Main manuscript | 72, 178, 281; SM 178, 518 | `dual-filter` vs. `dual-consensus` terminology | The protocol is referred to as `dual-filter consensus docking`, `dual-consensus scoring`, and `dual-consensus filter`. | Adopt one label, e.g. `dual-filter consensus docking/rescoring`, and use it in the main text, SM, and cover letter. |
| 10 | Main manuscript | 138, 311 | Grid box notation | Line 138 writes `\qty{25}{\angstrom}$^3$`; line 311 writes `\qty{25}{\angstrom}$\times$\qty{25}{\angstrom}$\times$\qty{25}{\angstrom}`. | Standardize on the expanded form (`25 Å × 25 Å × 25 Å`) to avoid ambiguity with cubic angstrom units. |
| 11 | Main manuscript / SM | 134, 249, 385, 826, 1126 | Target naming: `DHFR`, `PfDHFR`, `PfDHFR-TS` | The target name shifts between `DHFR`, `PfDHFR`, and `PfDHFR-TS` in methods, figures, and SM. | Define the full target once (`*P. falciparum* dihydrofolate reductase-thymidylate synthase, PfDHFR-TS / PfDHFR`) and use a consistent abbreviation thereafter. |
| 12 | SM | 177 vs. main 258 | `one centroid selected per cluster` vs. `multiple centroids can represent the same cluster` | The two statements can be reconciled, but the reader may be confused. | Clarify that cluster labels are distinct from representative molecules, and that several centroids may fall in the same chemical neighborhood. |
| 13 | Cover letter | 31–34 | `we are confident that ... the framework will accelerate` | Confident predictive language in a cover letter is acceptable, but the claim is strong given the manuscript's own caveats. | Soften to `we believe the framework has the potential to accelerate` or ensure the cover letter mirrors the manuscript's qualification language. |

---

## LOW — Polishing items

| # | File | Line | Issue | Suggested fix |
|---|------|------|-------|---------------|
| 14 | Main manuscript | 277 | Very long paragraph (activity-cliff validation) | Split into two paragraphs: one for cluster rescoring, one for STONED-SELFIES neighborhood validation. |
| 15 | Main manuscript | 305 | `Tartarus docking benchmark` reference | Ensure `nigam2023tartarus` is in the bibliography and the target list is accurate. | Double-check the .bib entry and the three-target claim against the actual Tartarus benchmark. |
| 16 | SM | 957 | `100.0% success rate for alignable ligands (5/5; 5/10 overall)` | The phrasing is correct but the percentage is redundant. | Optional: `All alignable ligands (5/5) reproduced the crystal pose within 2 Å; 5/10 overall were alignable.` |
| 17 | SM | 1344 | `132 actives and 267 carefully matched decoys` | This matches the summary table but contradicts the earlier `N = 399` actives framing. | Ensure the final paragraph uses the same active/decoy counts as the validation table. |

---

## Promotional / Hedging Balance

The manuscript is generally well balanced: it pairs strong performance claims with explicit limitations (grid-box size, pH, single static structures, activity-cliff risk, MMV as positive-control rather than independent decoy set, need for experimental validation). The only remaining promotional imbalance is the **redocking 100% success claim** (HIGH #2), which overstates the case by omitting the excluded ligands. The cover letter (MEDIUM #13) could also be softened slightly.

---

## Summary Counts

- **Anti-AI hits:** 0
- **HIGH issues:** 5
- **MEDIUM issues:** 8
- **LOW issues:** 4
- **Total prose/terminology issues:** 17

---

## Files Reviewed

- `/home/tchapet/Documents/GitHub/SAO/Malaria_codesV2/Project1_Chem_space_antimalarial_V4_CorrectedGrid/manuscript/Antimalarial_Candidates_African_NP_V2607.tex`
- `/home/tchapet/Documents/GitHub/SAO/Malaria_codesV2/Project1_Chem_space_antimalarial_V4_CorrectedGrid/manuscript/Antimalarial_Candidates_African_NP_V2607_SM.tex`
- `/home/tchapet/Documents/GitHub/SAO/Malaria_codesV2/Project1_Chem_space_antimalarial_V4_CorrectedGrid/manuscript/Cover_Letter.tex`
