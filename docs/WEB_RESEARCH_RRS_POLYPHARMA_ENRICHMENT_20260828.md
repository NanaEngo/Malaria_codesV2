# Web research — RRS + polypharmacology enrichment (28 August 2026)

> Companion layer to `WEB_RESEARCH_P2_P5V2_P6_REINFORCEMENT_20260827.md` (literature) and `GITHUB_APPS_SURVEY_20260827.md` (tools). This file is the **RRS + polypharmacology** specific layer: suggestions that strengthen the resistance-aware, multi-target narrative of P1/P2 (and, where noted, the cross-project frame P3/P5/P6).
>
> **Date:** 28 August 2026
> **Method:** targeted web searches (PubMed, ACS, Nature, Cell, MDPI, PMC, WHO). Publisher pages that returned 403/redirect errors (Cell Trends, MDPI IJMS) were not fully extracted; claims below are limited to accessible abstracts, snippets, and authoritative pages.
> **Status:** suggestions (citations, framing, optional light post-processing) — no new canonical metric, no canonical calculation modified. Manuscript edits remain an author decision.
> **Implementation (28 Aug 2026, evening):** S1–S4, S6, S7 applied to the P2 main manuscript (`Polypharmacology_MD_Validation_V2607.tex`) with 11 bib keys appended to `Bibliography_P2.bib`; P2 main (29 p.) + SM (15 p.) recompiled with 0 errors / 0 undefined refs. S5 implemented as `Project2_Polypharmacology_MD_ValidationV2607/scripts/p2_gnina_consensus_rescore.py` (fail-closed, GNINA 1.3.2 `--score_only` on MODEL 1, smoke-tested on EXT-001 PfCRT K76T: vina −6.665 / CNN 3.51); **pending the 320-pose array 15605 completion** — the script exits `BLOCKED_INCOMPLETE` until all 320 poses are present and scored. S7 (artemisinin context) was already present in the P2 Introduction; the WHO Q\&A citation was added.

---

## 1. Sources newly identified (28 Aug 2026)

| # | Source | DOI / URL | Relevance |
|---|---|---|---|
| 1 | **SDMT paradigm — single drugs, multiple targets** (Trends Parasitol. 2026) | https://www.cell.com/trends/parasitology/abstract/S1471-4922(26)00040-1 | P1/P2 headline frame: multi-target activity to raise the resistance barrier beyond combination-like effects |
| 2 | **Computational investigation of mutations in PfCRT and PfDHFR** (Ghosh, 2025) | https://pubmed.ncbi.nlm.nih.gov/40915500/ | WT-denominator justification; combined PfCRT+PfDHFR mutation panel rationale (already cited in `CENTRAL_QUESTIONS`) |
| 3 | **Antimalarial drug resistance and drug discovery: learning from the past** (2025) | https://pmc.ncbi.nlm.nih.gov/articles/PMC12296534/ | Discussion anchor: why resistance history motivates resistance-aware prioritisation |
| 4 | **AI-Driven Polypharmacology in Small-Molecule Drug Discovery** (Int. J. Mol. Sci. 2025, 26, 6996) | https://www.mdpi.com/1422-0067/26/14/6996 | Polypharmacology as resistance mitigation; AI multi-target workflows |
| 5 | **Trends and Pitfalls in Network Pharmacology** (Panossian et al., 2025) | https://pmc.ncbi.nlm.nih.gov/articles/PMC12030339/ | **Methodological honesty for PNS**: database/hub bias, over-interpretation of network scores |
| 6 | **WHO Compendium of molecular markers for antimalarial drug resistance** | https://www.who.int/tools/compendium-of-molecular-markers-for-antimalarial-drug-resistance | Clinical anchoring of the chosen mutant states (K76T, N51I, C59R, S108N, I164L) |
| 7 | **GNINA 1.3 — next increment in docking with deep learning** (J. Cheminform. 2025) | https://link.springer.com/article/10.1186/s13321-025-00973-x | Fresh reference for CNN scoring of existing poses (consensus layer) |
| 8 | **Benchmarking GNINA and AutoDock Vina for precision virtual screening** (2025) | https://pmc.ncbi.nlm.nih.gov/articles/PMC12388557/ | Vina-vs-GNINA consensus context (completes the 2025 Buccheri citation) |
| 9 | **Benchmarking Single-Pose Docking, Consensus Rescoring** (arXiv 2026) | https://arxiv.org/pdf/2605.01681 | Consensus-rescoring protocol reference for the 320 external poses |
| 10 | **MLSyPredC — ML synergy predictor for antimalarial combinations** (2024) | https://pmc.ncbi.nlm.nih.gov/articles/PMC11001753/ | Future work: bridge RRS A* multi-target candidates to combination-synergy prediction |
| 11 | **MD-Syn — synergistic drug combination prediction** (Front. Pharmacol. 2025) | https://www.frontiersin.org/journals/pharmacology/articles/10.3389/fphar.2025.1564339/full | MD-based synergy framing for the future-work bridge |
| 12 | **Artemisinin partial resistance / PfKelch13** (WHO Q&A 2025; van Loon 2025) | https://www.who.int/news-room/questions-and-answers/item/artemisinin-resistance ; https://pmc.ncbi.nlm.nih.gov/articles/PMC12135530/ | Discussion context: why resistance-aware design matters now; potential future target (NOT_COMPUTED) |

Sources 1–2 were already used in `CENTRAL_QUESTIONS_PROJECTS.md`; sources 3–12 are new to the docs set.

---

## 2. S1 — SDMT framing for the P1/P2 headline (free, text only)

**Suggestion.** The Trends in Parasitology 2026 SDMT review formalises exactly the P1/P2 premise: a single drug engaging several targets raises the resistance barrier in a way that combinations alone do not. Use it explicitly in the P2 Introduction and Discussion:

- P2 Intro: state that multi-target engagement is pursued *specifically* as a resistance-management strategy (SDMT), not merely as a breadth descriptor.
- P2 Discussion: interpret the **A\*** class (candidates favourable on ≥4 target profiles, e.g. PP-15/PP-06/PP-11) as SDMT-style resistance-barrier hypotheses: RRS quantifies the mutational-resilience axis of the same candidates whose breadth is quantified by the four-target matrix.
- Keep the boundary: SDMT is a *rationale*, not evidence of measured multi-target engagement; docking profiles remain computational prioritisation.

**Draft (P2 Discussion):**

> Multi-target engagement is pursued here not only as a breadth descriptor but as a resistance-management strategy: single drugs acting on several Plasmodium targets are proposed to raise the genetic barrier to resistance beyond what combination therapy alone achieves (SDMT paradigm)~\\citep{sdmt2026trends}. Within this frame, our class-A* candidates—favourable across the four-target wild-type matrix and resilient across the PfDHFR/PfCRT mutant panels—instantiate the two axes that SDMT requires: breadth (target coverage) and resilience (per-target RRS retention).

---

## 3. S2 — Clinical anchoring of mutant states (free, text + SI table)

**Suggestion.** The chosen mutation states (PfCRT K76T/K76A; PfDHFR N51I/C59R/S108N/I164L) are all WHO-listed molecular markers of antimalarial resistance. Add one sentence in Methods citing the WHO Compendium, and optionally one SI row mapping each mutation to its WHO marker entry and clinical relevance. This converts an apparently arbitrary mutant panel into a clinically justified design choice — a frequent reviewer question.

**Draft (P2 Methods):**

> The mutant states were selected among established molecular markers of antimalarial drug resistance compiled by the WHO: PfCRT K76T (chloroquine-resistance marker) and the PfDHFR quintuple-associated positions N51I, C59R, S108N and I164L (antifolate-resistance markers)~\\citep{who_compendium}. K76A was included as a charge-neutralising isosteric perturbation of the canonical K76T resistance substitution.

---

## 4. S3 — Mechanistic replication for PfCRT (free, text only)

**Suggestion.** The 2025 atomistic study by Tanner, Richards & Corry (130 µs MD, PfCRT CQ-sensitive vs resistant) is already drafted in `WEB_SEARCH_REFINEMENTS_20260826.md` (§1.1). Reinforce its use:

- Cite it also in **Methods** when justifying the WT-vs-mutant design for PfCRT (K76 as charged anchor / cavity-charge gating).
- In **Discussion**, note that our MD-RRS pilot and MM-GBSA contrasts (mutant vs WT) are consistent with this established charged-cavity picture — *consistency*, not validation.
- Bib key already available: `tanner2025pfcrt` (added in the P2 `.bib`).

---

## 5. S4 — Network-pharmacology pitfalls for the PNS reading (free, text only)

**Suggestion.** `CENTRAL_QUESTIONS_PROJECTS.md` already reports PNS–RRS ρ = −0.559, p = 0.020, *not* Bonferroni-significant. The 2025 Panossian review on network-pharmacology pitfalls is the ideal citation to pre-empt a reviewer who either (a) over-reads the PNS result as network validation, or (b) dismisses network scores as meaningless. Add one sentence in P2 Discussion/Limitations:

**Draft (P2 Limitations):**

> Network-pharmacology scores are sensitive to database coverage, hub bias, and the choice of network weighting~\\citep{panossian2025pitfalls}. Our PNS is a docking-derived, cohort-bounded ranking heuristic; the exploratory PNS–RRS association did not survive multiplicity correction and is reported as a hypothesis-generating trend, not as a validated network property.

---

## 6. S5 — CNN consensus rescoring of the 320 external poses (light post-processing, after array 15605)

**Suggestion.** When the external docking array (40 ligands × 8 states = 320 poses) completes, run **GNINA 1.3** CNN rescoring on the *existing Vina poses* (post-processing only, no re-docking) as a consensus sensitivity:

- Predeclare the rule: report per-system Vina score and GNINA CNN score side-by-side; RRS recomputed under each scoring layer; a class change between layers reported as a consensus discordance, never silently resolved.
- Cite GNINA 1.3 (J. Cheminform. 2025) and the Vina-vs-GNINA benchmark (2025); use the arXiv consensus-rescoring study as protocol reference.
- This directly reuses the local `/home/nanaengo/gnina/gnina` v1.3.2 and answers the "single scoring function" reviewer objection with a consensus layer, while keeping Vina-only as the canonical estimand.
- **Boundary (from the P2 DAR):** the earlier preserved GNINA attempt wrote an empty output; the full 17×4 GNINA panel statement remains withdrawn until a non-empty manifest is produced. The 320-pose CNN rescoring must therefore be fail-closed (non-empty output required) before any CNN-based claim.

---

## 7. S6 — RRS → synergy-prediction bridge (future work, NOT_COMPUTED)

**Suggestion.** Record as explicit future work: the multi-target A* candidates identified by the four-target matrix + RRS are natural inputs to ML-based antimalarial combination-synergy predictors (MLSyPredC; MD-Syn). This is a *future-work* statement in P2 Discussion, not a calculation:

> The multi-target, mutation-resilient candidates prioritised here are testable inputs for ML-based combination-synergy prediction (e.g., MLSyPredC), in which the same molecular features would be scored for pairwise synergy; such predictions are outside the scope of the present study and remain future work.

Keep it honest: no synergy metric is computed, and no claim that RRS predicts synergy.

---

## 8. S7 — Artemisinin partial resistance context (free, Discussion P1/P2)

**Suggestion.** One or two sentences in the P1 or P2 Introduction situating the work against artemisinin partial resistance (PfKelch13-mediated, WHO-recognised):

> With artemisinin partial resistance now documented across Africa, resistance-aware prioritisation of next-generation chemotypes—broad target coverage coupled with per-target mutational retention—is a timely design objective rather than a purely academic exercise.

Do **not** add PfKelch13 as a fifth docking target: no receptor/labels are prepared and any such claim would violate the frozen four-target panel. PfKelch13 is explicitly `NOT_COMPUTED` / future work.

---

## 9. Cross-project additions (P3/P5/P6, optional)

- **P3/P5 Discussion:** the AI-driven polypharmacology review (IJMS 2025) can frame why multi-target descriptors (TFP/TNE/QKS) are complementary to activity prediction: they encode features that matter for breadth/resistance even when they do not improve single-task AUC. Keep the honest-negative intact — no claim of predictive superiority.
- **P6 Discussion:** the "learning from the past" resistance review (2025) and the synergy-prediction references are *not* P6-relevant; do not add them there.

---

## 10. Prioritisation

| # | Action | Cost | Gate | When |
|---|---|---|---|---|
| S1 | SDMT framing P2 Intro/Discussion | free (text) | none | before final author read |
| S2 | WHO compendium citation + SI marker table | free (text) | none | before final author read |
| S3 | Tanner et al. Methods/Discussion reinforcement | free (text) | none | before final author read |
| S4 | Panossian pitfalls citation (PNS honesty) | free (text) | none | before final author read |
| S7 | Artemisinin partial-resistance context sentence | free (text) | none | before final author read |
| S5 | GNINA consensus rescoring of 320 poses | light (post-processing) | array 15605 COMPLETE + fail-closed manifest | after external RRS |
| S6 | RRS→synergy bridge | none (future-work statement) | — | Discussion only |

**Deliberately NOT recommended now:** PfKelch13 docking target (frozen 4-target panel), synergy prediction computation (new heavy campaign), re-docking with GNINA (the consensus layer uses existing poses only).

---

## 11. Bibliography keys to add (append only)

| Key | Reference |
|---|---|
| `sdmt2026trends` | Trends in Parasitology 2026 — single drugs, multiple targets (SDMT) |
| `who_compendium_markers` | WHO Compendium of molecular markers for antimalarial drug resistance |
| `panossian2025pitfalls` | Panossian et al., 2025 — Trends and pitfalls in network pharmacology |
| `gnina2025v13` | GNINA 1.3, J. Cheminform. 2025 |
| `vina_gnina_benchmark2025` | Benchmarking GNINA and AutoDock Vina, 2025 |
| `consensus_rescoring2026` | Single-pose docking, consensus rescoring benchmark, arXiv 2026 |
| `mlsypredc2024` | MLSyPredC — ML synergy predictor for antimalarials, 2024 |
| `mdsyn2025` | MD-Syn, Front. Pharmacol. 2025 |
| `ai_polypharmacology2025` | AI-Driven Polypharmacology, Int. J. Mol. Sci. 2025, 26, 6996 |
| `resistance_lessons2025` | Antimalarial drug resistance and drug discovery: learning from the past, 2025 |
| `artemisinin_partial_resistance` | WHO Q&A — artemisinin partial resistance; van Loon et al. 2025 |
