# P2 Adversarial Audit, Rejection Root-Cause Analysis & Deep Scientific Refinements
**Project:** `Project2_Polypharmacology_MD_ValidationV2607` (Resistance-Aware Polypharmacology, MD Validation & Estimand Divergence)
**Revision:** rev 2.1 — 16 October 2026. rev 2: addendum folded into the body, retracted targets and unverifiable citations removed, evidence pinning added. rev 2.1: **§6 "wow" factor** (the referee-facing contribution) added; the former §6 (limits) is now §7.

## Audit pin

| Field | Value |
|---|---|
| Repository | `/home/nanaengo/Malaria_codesV2` (canonical single tree, `AGENTS.md` §0) |
| Branch / commit audited | `master` @ `1c9c38f2ec572d92f03073f765b6cd11b9b062a6` (2026-10-16T12:21:31+01:00) |
| Path convention | repo-relative only; no absolute `file://` links |
| Evidence rule | every factual claim carries a repository path **with sha256** or a DOI. A claim without one is `UNVERIFIED` |
| Auditor frameworks | BMAD multi-layer review (`bmad-code-review`), Scientific Critical Thinking, Hypothesis Generation, Experimental Design, Peer Review |
| Manuscript lineage in scope | canonical `V2609C` and the competing `V2609`; `P2_DATA_ANALYSIS_REPORT.md` (DAR) is authoritative for status |

**Superseded in rev 2 (do not re-assert):** the reading of Soares et al. (2023) as an "ns requirement" or as requiring "3 × 50 ns" (that ensemble is *our design choice*); the `±1.0 kcal/mol at 1/10 cost` rescaling claim; the citations "Pandas et al., *JCTC* 2023" and "Mobley et al., *Ann. Rep. Comput. Chem.* 2021" (not locatable; see §5); the framing of `3 × 10 ns` triplicate work as already fulfilling the JCIM replica guideline (the DAR records it as **PARTIAL**).

**Key literature anchors (verification status in §5):**
- Soares, Cournia, Naidoo, Amaro, Wahab, Merz, *J. Chem. Inf. Model.* **63**(11), 3227–3229 (2023), DOI 10.1021/acs.jcim.3c00599 — reporting guidelines: replicas from independent coordinates/velocities, disclosed seeds, discussed variance, convergence shown; **no ns cutoff**.
- Kim, Tan, Wicht et al., *Nature* **576**, 315–320 (2019) — PfCRT; PDB `6UKJ` is the 7G8 (T76) isoform (RCSB, checked 16 Oct 2026).
- Rocklin et al., *J. Chem. Phys.* **139**, 184103 (2013) — finite-size/charging corrections (PubMed 24320250, verified).
- Grundschober et al., *J. Chem. Theory Comput.* **21**(11), 5669 (2025) — limitations of co-alchemical charge changes (verified).
- Mey et al., *LiveCoMS* (2020), "Best Practices for Alchemical Free Energy Calculations [Article v1.0]" — practice anchor; retrieve the DOI from the LiveCoMS record before citing.
- Gapsys et al., *Chem. Sci.* **11**, 1140–1152 (2020) — non-equilibrium alchemy (not re-verified in this revision).

---

## 1. Executive summary & audit scorecard

Project 2 evaluates 17 ANP-inspired polypharmacological candidates (Set C) across wild-type and resistant-mutant panels of `PfDHFR` and `PfCRT`, combining static docking RRS with explicit-solvent MD and endpoint MM-GBSA on a 16-system pilot (`PP-01`, `PP-02`).

| Audit layer | Status | Essential finding (evidence) |
|---|:---:|---|
| **1. MD protocol vs JCIM standards** | 🟠 **OPEN (partially fulfilled)** | Primary MD conclusions still rest on single-replicate 10 ns trajectories. The DAR is already explicit: triplicate work is **PARTIAL** and *"does NOT satisfy the Soares et al. ≥3-replicate requirement"* (DAR §7 tasks 0–9, §coherence audit). The defect is therefore in the **manuscript framing**, not in an unmet obligation the project believes it has met. |
| **2. "87.5 % Estimand Divergence" as a positive claim** | 🔴 **OPEN (editorial)** | `7/8` is an underpowered binomial ratio (95 % Wilson [52.9 %, 97.8 %]) computed over **two ligands**, so the unit is ligand, not trial. `V2609`/DAR §4.2 already document the divergence as a limitation ("neither method demonstrates resistance"); `V2609C` inverted it into a validated compensation mechanism. |
| **3. MM-GBSA RRS > 100 %** | 🔴 **OPEN** | `8/12` mutant systems show MM-GBSA RRS > 100 % (max 121.4 %; DAR §4.3 MM-GBSA table, row `PP-02 PfCRT K76T`: −30.45 ± 1.38 → 121.4), driven by continuum-solvent electrostatics, missing `−TΔS`, and inter-replicate spread. That spread is **this project's own measurement**: the K76A canonical endpoint `−35.29 ± 1.17` carries a `7.75 kcal/mol` inter-replicate diagnostic against `−27.54 ± 1.89` (DAR §4.3/SM Table S19). |
| **4. PfCRT transport biophysics** | 🟠 **PARTLY FIXED / OPEN** | The receptor/grid defect is corrected in-project (3D7-like LYS-76 preparation and cavity-anchored grid, archived in `docs/archive/V2_GRID_CITATION_UPDATE.md` and `P2_RECONFIGURATION_PLAN_P1_P2_20260910.md`; see also P1 `results/pfcrt_redock_v2grid_20260909/`). What remains open is the **physics framing**: `PfCRT` is treated as a neutral-pH static binder rather than a pH 5.2 proton-coupled vacuolar efflux transporter. |
| **5. Dual-manuscript governance** | 🟠 **OPEN** | `V2609C` diverges from the DAR (promotes `PP-02`/`PP-15`, empty/incorrect `.bib` reference, missing citation keys, unverified Zenodo DOI claim). The tree simultaneously carries `V2609C`, `V2610C_save`, `Submission_JCIM`, `submission_ACS_P2V2609C` and ChemRxiv variants. |

---

## 2. Diagnosis

### 2.1 The replica requirement, correctly stated
Soares et al. (2023) require **replicas from independent coordinates/velocities**, disclosed random seeds, an explicit variance discussion and convergence evidence. They set **no simulation-length cutoff**. The correct statement of our position is therefore:

- single-replicate 10 ns trajectories fail the *replica* requirement — not a *length* requirement;
- **3 × 50 ns** is a design choice we make for the lead compounds, to be justified by a convergence criterion and a compute budget (§3.5), not quoted as a published obligation.

Independent of replicas, the sampling limitation stands: a 10 ns window samples local side-chain jitter around the docked pose and cannot capture binding-mode transitions or resistance-induced dissociation. In the parent cohort this showed up concretely: 2 of 4 ligands fully dissociated (67.4 Å and 78.2 Å), and one system carried a `+473 kcal/mol` CHARMM36→AMBER van der Waals conversion corruption. In the Set-C pilot all 16 systems stayed within 5 Å (a trivially saturated retention ceiling of 1.000); the continuous minimum-heavy-atom-distance formulation (`MD-RRS_d`) shows no reproducible weakening signature (72.2–102.8 %).

### 2.2 The estimand-divergence claim
The `7/8` directional disagreement between static Vina RRS and 10 ns MD/MM-GBSA was honestly documented in `V2609` as a methodological limitation. `V2609C` converted it into the paper's centrepiece. Two independent defects make that conversion unsupportable as written:

1. **Denominator and unit.** Eight mutant comparisons derived from two ligands are not eight trials; the ligand-level (cluster-aware) interval is the correct one. Report per-ligand results and label the divergence **descriptive**.
2. **Noise misread as rescue.** With an inter-replicate spread of 7.75 kcal/mol (measured, K76A) and predictions that resistant mutants bind *more tightly* than wild type, "conformational rescue" is unfalsifiable without an experimental affinity control.

If the divergence is to be a result rather than a limitation, it needs the decomposition in §3.3 and an external anchor.

### 2.3 PfCRT resistance biophysics (the strongest scientific point in this audit)
`PfCRT` is a 10-transmembrane-helix transporter in the *P. falciparum* **acidic digestive vacuole (pH ≈ 5.0–5.4)**. Weak-base antimalarials accumulate there as diprotonated species. In wild-type `3D7`, the positively charged **Lys76⁺** lining the central cavity creates an electrostatic barrier that hinders `DrugH₂²⁺` permeation; in the resistant **`K76T` (Thr76⁰)** the charge is lost, the barrier falls, and the drug is effluxed out of the vacuole.

**The consequence for P2:** for a vacuolar substrate, *stronger* binding to the `K76T` pore can indicate **facilitated efflux** — i.e. susceptibility — unless the ligand locks `PfCRT` in an occluded, non-transporting conformation. Treating `PfCRT` `K76T` exactly like a soluble enzyme active site (`PfDHFR`) is the central conceptual error, and it is the error that produces RRS > 100 % "resilience".

### 2.4 Cohort shared with P1 and P7
The 17-molecule cohort is shared across projects: `Project7_.../data/p1_set_a/p1_set_a_17_candidates_anp_metadata.csv` (sha256 `b7d7c859…`) carries `cohort_id = P2_SET_C_POLYPHARM_17`, IDs `PP-01…PP-17`, and a single `p2_source_sha256`. P2's contribution must therefore read as a distinct **biophysical/free-energy** study, not a second report of the same docking table — and any overlap must be declared in both manuscripts.

---

## 3. Refinements

rev 1 numbering retained for continuity: rev 1 *Novelty 1* (non-equilibrium alchemical FEP) → §3.2; *Novelty 2* (dual-pH PfCRT mechanism, efflux vs occlusion) → §3.4; *Novelty 3* (physical decomposition of the divergence) → §3.3; *Novelty 4* (governance, triplicate compliance, controls) → §3.5 and §4. The estimand mapping (§3.1) is new in rev 2 and is a prerequisite for all of them.

### 3.1 Estimand mapping before estimator comparison (new, mandatory)
Define explicitly and in advance how `RRS` maps onto `ΔΔG_bind`: units, reference state, sign convention, and the transformation between the dimensionless ratio and a free-energy difference. No estimator comparison (Vina vs MM-GBSA vs alchemy) is interpretable until this mapping is fixed. This is the cheapest available fix for the divergence debate.

### 3.2 Direct mutational free energy (`pmx` / non-equilibrium alchemy) — with scope limits
Endpoint MM-GBSA computes large absolute numbers with a spread that cannot resolve `ΔΔG` shifts of 0.5–2.0 kcal/mol. Alchemical protein-mutation FEP supplies the missing estimand:
$$\Delta\Delta G_{\text{bind}}(\text{WT} \to \text{Mut}) = \Delta G_{\text{alchem}}^{\text{holo}}(\text{WT} \to \text{Mut}) - \Delta G_{\text{alchem}}^{\text{apo}}(\text{WT} \to \text{Mut})$$
Scope limits that must be stated wherever this is proposed:

1. **Charge-changing substitutions need extra machinery.** `K76T` (ΔQ = −1) and `C59R` (ΔQ = +1) require a co-alchemical ion plus finite-size/PME corrections (Rocklin et al. 2013; and see Grundschober et al. 2025 for the known limitations of co-alchemical charge changes); in a membrane dimer the correction is large and uncertain. **Run NEQ-FEP first on the net-charge-preserving PfDHFR substitutions (`S108N`, `I164L`, `N51I`) and mark all `PfCRT` FEP exploratory.**
2. **Do not rescale cost optimism.** Earlier drafts asserted "±1.0 kcal/mol at 1/10 the cost" on the basis of citations that could not be located. Any precision claim must come from a pilot on these systems, with the reported spread and the sampling per λ window.
3. **Protein-leg equilibration.** The mutation leg requires converged end-state side-chain rotamers and ≥3 independent replicas of the non-equilibrium ensemble.
4. **Controls decide validity.** Pyrimethamine, cycloguanil (WT-active, mutant-weak) and WR99210 (mutant-retaining) must reproduce the published ordering before any ANP lead is discussed.

### 3.3 Physical decomposition of the divergence
Across triplicate trajectories, quantify three components rather than asserting one:

1. **Side-chain rotamer relaxation** — χ₁/χ₂ distribution shifts of Asn108, Leu164, Phe58, Ile14 in MD versus the rigid grid (the mechanism by which 0.8–1.5 Å pocket breathing relieves an artificial rigid-receptor clash).
2. **Bridging-water networks** — occupancy of waters bridging ligand heteroatoms to mutant backbone carbonyls (PfDHFR Ile164/Asp54; PfCRT Thr76/Gln161) at > 60 % residence, which continuum-desolvated scoring cannot see.
3. **Ligand pre-organization** — ligand RMSF and internal torsional entropy for rigid fused ANP cores versus flexible synthetic linkers.

### 3.4 PfCRT mechanism study: state the claim the model can support
1. Model `3D7`-like WT (Lys76⁺), `K76T` and `K76A` in a **membrane-embedded** system at both protonation regimes (pH 5.2 vacuolar; pH 7.4 cytosolic).
2. Quantify `ΔE_Coulomb` at residue 76 and the transmembrane pore hydration profile across replicates.
3. Discriminate **efflux-susceptible substrates** (weak WT binding through electrostatic repulsion at pH 5.2; strong `K76T` binding with a hydrated cytoplasmic gate) from **occluded-state inhibitors** (anchored by hydrophobic/aromatic contacts in both states, dehydrating the pore).
4. **Bounded claim.** A docking or endpoint binding calculation cannot establish transport. Either estimate a transport-relevant quantity (pore hydration free-energy profile / gating coordinate) or narrow the claim to binding competence and label the efflux interpretation as a hypothesis.

### 3.5 Statistical hygiene and compute budget
- **Unit of inference:** the ligand (chemistry series), not the mutant system or the replicate. Report per-ligand results with cluster-aware intervals; label anything else descriptive.
- **Convergence package:** block-averaged `ΔG` versus block size, integrated autocorrelation time, replica-to-replica SD, and a **pre-declared equilibration-exclusion rule**. Report "not converged" where that is the finding.
- **Compute budget:** measure ns/day per system on the RTX A4000 and write the budget into the DAR **before** committing to the ensemble and the FEP legs.
- **Governance:** one canonical manuscript with a changelog; retire the parallel version directories.

---

## 4. Action plan and gates

| # | Action | Gate |
|---|---|---|
| 1 | Merge into a single canonical manuscript with a reconciled `.bib` | 0 unresolved citations; 0 undefined references on build |
| 2 | Restate the replica position (design choice, not requirement) and report triplicate status honestly | Text matches the DAR "PARTIAL" status |
| 3 | Analyse the running triplicate with seeds listed | `RRS_MD ± SD` across replicas; convergence package present |
| 4 | Extend to 3 × 50 ns for `PP-01`/`PP-02` only, if the measured budget allows | Convergence criteria met, or reported as not met |
| 5 | Fix the estimand mapping `RRS ↔ ΔΔG` (§3.1) | Mapping stated in Methods before any estimator comparison |
| 6 | NEQ-FEP on net-charge-preserving PfDHFR substitutions, with controls | Controls reproduce the known resistance ordering, else no claim |
| 7 | pH 5.2 versus 7.4 PfCRT protonation audit | Reported as exploratory; no mechanistic claim without a transport-relevant observable |
| 8 | Re-label the divergence as descriptive; drop the "validated compensation" framing | Ligand-level interval presented; per-ligand table present |

Per `AGENTS.md` rule 8: **no manuscript claim changes from incomplete or failed runs.**

---

## 5. Verification ledger (claim → evidence)

| Claim | Status | Evidence |
|---|---|---|
| Soares et al. 2023 = *JCIM* 63(11), 3227–3229; ≥3 replicas; no ns cutoff | ✅ Verified | DOI 10.1021/acs.jcim.3c00599 (ACS/PMC records) |
| `6UKJ` = 7G8 (T76) isoform; WT 3D7 (K76) must be built | ✅ Verified | RCSB entry + FASTA, 16 Oct 2026 |
| Corrected LYS-76 receptor and cavity grid exist in-project | ✅ Verified | `Project1_Chem_space_antimalarial_V7_CorrectedGrid/results/pfcrt_redock_v2grid_20260909/manifest.json` (sha256 `ca1c7cd3…`); P2 `docs/archive/V2_GRID_CITATION_UPDATE.md` |
| Triplicate MD does **not** yet satisfy the ≥3-replica guideline | ✅ Verified | DAR §7 tasks 0–9 and coherence audit ("does NOT satisfy … no new MD-RRS or MM-GBSA endpoints promoted") |
| 7.75 kcal/mol inter-replicate spread is an in-house measurement | ✅ Verified | DAR §4.3 / SM Table S19 (K76A: −35.29 ± 1.17 vs −27.54 ± 1.89) |
| MM-GBSA RRS > 100 % up to 121.4 % | ✅ Verified | DAR line 91 (`PP-02 PfCRT K76T −30.45 ± 1.38 → 121.4`) |
| Rocklin et al. *J. Chem. Phys.* 139, 184103 (2013) | ✅ Verified | PubMed 24320250 |
| Grundschober et al. *JCTC* 21(11), 5669 (2025) | ✅ Verified | ACS record |
| PfCRT transports peptides; resistance mutations reduce transport capacity | ✅ Verified (rev 2.1) | Shafik et al., *Nat. Commun.* **11**, 3922 (2020), DOI 10.1038/s41467-020-17781-6 |
| PfCRT CQ-versus-peptide transport conflict mapped structurally | ✅ Verified (rev 2.1) | Tanner et al., *Nat. Commun.* **16**, 2987 (2025), DOI 10.1038/s41467-025-58244-0 |
| "Pandas et al., *JCTC* 2023 (MM-GBSA bootstrap)" | 🚫 Not locatable | Two literature searches; removed, including the `±1.5 kcal/mol` claim |
| "Mobley et al., *Ann. Rep. Comput. Chem.* 2021 (SD 7.75 kcal/mol typical)" | 🚫 Not locatable | Two searches; the value is the project's own spread, not literature. Correct anchor: Mey et al., *LiveCoMS* (2020) |
| Gapsys et al. *Chem. Sci.* 11, 1140 (2020) | ⏸ Not re-checked | Retained as an anchor; verify before citing |
| "3 × 50 ns required by JCIM" | ⏹ Withdrawn | No such requirement exists |

---

## 6. The "wow" factor — what should make a referee or editor say *waouh*

**The one line.**

> This is the first resistance-aware polypharmacology study in which the **sign of the resistance ratio is itself the hypothesis**: at a vacuolar transporter, `RRS > 100 %` is reframed from an embarrassment into a testable *efflux-versus-occlusion* discriminator, and the discriminator is measured with an observable that does not share the docking estimator's assumptions — pore hydration and the residue-76 electrostatic barrier across independent replicas at the two physiological pH regimes.

### 6.1 Why it lands

The current centrepiece of `V2609C` — "87.5 % estimand divergence" — is the weakest thing in the paper, because 7/8 is an underpowered binomial over two ligands (Wilson [52.9 %, 97.8 %]) and because "resistant mutants bind more tightly than wild type" reads as an error until it is given a mechanism. The reframing turns the same observations into the strongest thing in the paper:

1. **A physically motivated sign.** PfCRT is a proton-coupled transporter in the acidic digestive vacuole (pH ≈ 5.0–5.4) that normally transports peptides; resistance-conferring mutations reduce peptide transport capacity and substrate range (Shafik et al., *Nat. Commun.* **11**, 3922 (2020), DOI 10.1038/s41467-020-17781-6), and the CQ/peptide transport conflict has since been mapped structurally (Tanner et al., *Nat. Commun.* **16**, 2987 (2025), DOI 10.1038/s41467-025-58244-0). For such a substrate, tighter binding to `K76T` can mean *facilitated efflux* — susceptibility — unless the ligand occludes the pore. Treating a transporter exactly like a soluble enzyme active site is the conceptual error that produces `RRS > 100 %`; naming it converts 8/12 of the project's own MM-GBSA results (max **121.4 %**) from a liability into a signal.
2. **An honest premise.** The project's own pilot says why a *continuous* observable is required: all 16 Set-C systems remained within 5 Å, so the binary retention readout is saturated at 1.000, while the continuous `MD-RRS_d` spans 72.2–102.8 %. The parent cohort shows the MD *can* produce extreme events (2 of 4 ligands fully dissociated at 67.4 Å and 78.2 Å; one system carried a +473 kcal/mol CHARMM36→AMBER van der Waals corruption) — so a hydration/barrier observable has room to separate classes where the binding readout does not.
3. **A guarantee for the comparison.** §3.1 already makes the estimand mapping `RRS ↔ ΔΔG_bind` a prerequisite; once stated, the divergence question becomes well-posed ("where are two estimators self-consistent, and why do they part") instead of a contest between two differently biased numbers.
4. **The new evidence is already on disk.** The HPC triplicate and pH 5.2 daemon is running on `penavoraserver` (`AGENTS.md` §3; log `/home/nanaengo/hpc_md_execution.log`) for `PP-01_PfCRT_WT`, `PP-01_PfCRT_K76T`, `PP-01_PfDHFR_WT` plus a protonated-His97/His53 and ligand-basic-site audit. The marginal cost of the decisive experiment is **analysis**, not simulation — rare in a revision plan, and editors notice it.

### 6.2 Wow at a glance

| Element | Value | Evidence |
|---|---|---|
| The liability being converted | 8/12 mutant systems with MM-GBSA `RRS > 100 %`, max **121.4 %** (`PP-02` PfCRT K76T: −30.45 ± 1.38 → 121.4) | `Project2_Polypharmacology_MD_ValidationV2607/P2_DATA_ANALYSIS_REPORT.md` §4.3 (sha256 `51304461…`) |
| The noise floor that makes `>100 %` unremarkable | K76A endpoint −35.29 ± 1.17 vs −27.54 ± 1.89 → 7.75 kcal/mol inter-replicate diagnostic (in-house measurement) | same, DAR §4.3 / SM Table S19 |
| Saturation of the current readout | 16/16 systems within 5 Å (ceiling 1.000); continuous `MD-RRS_d` 72.2–102.8 % | same, DAR §4.3 |
| Divergence, correctly sized | 7/8 over **two** ligands; Wilson 95 % [52.9 %, 97.8 %]; unit of inference is the ligand | `V2609C` / DAR §4.2 (superseded framing withdrawn) |
| Mechanism anchors | PfCRT peptide transport (Shafik 2020); CQ/peptide transport conflict (Tanner 2025); charge-change corrections (Rocklin, *J. Chem. Phys.* **139**, 184103 (2013); Grundschober, *JCTC* **21**(11), 5669 (2025)) | DOIs in §5 |
| Free evidence already computed | triplicate MD on the Class-A* lead + pH 5.2 protonation audit | `AGENTS.md` §3; `/home/nanaengo/hpc_md_execution.log` |

### 6.3 The artifact that carries it — one figure

**Figure S (pore state versus resistance sign)**: for WT (Lys76⁺) vs `K76T` vs `K76A`, at pH 5.2 and 7.4, per replicate: (i) residue-76 `ΔE_Coulomb` and (ii) the transmembrane pore water-occupancy profile, with every ligand placed by (binding-ratio sign, pore-hydration class) and the *reference drugs* plotted at their expected positions. The caption states the two-class decision rule — **efflux-susceptible** (weak WT binding through electrostatic repulsion at pH 5.2; strong `K76T` binding with a hydrated cytoplasmic gate) versus **occluded inhibitor** (hydrophobic/aromatic anchoring in both states with a dehydrated pore) — and the sample size behind each cell.

### 6.4 The decisive, cheap experiments

| # | Action | Cost | Gate |
|---|---|---|---|
| W1 | Analyse the running triplicates with seeds listed: per-replicate `ΔE_Coulomb` at residue 76 and pore-water occupancy profiles | analysis of existing trajectories | Values reported per replicate with SD, not pooled |
| W2 | Fit and freeze the two-class rule (efflux-susceptible vs occluded) on the **reference drugs** (CQ, PPQ, verapamil-type modulator) before any ANP lead is classified | analysis only | Pre-registered rule; ANP leads scored only after freeze |
| W3 | PfDHFR NEQ-FEP on the net-charge-preserving substitutions (S108N, I164L, N51I) with pyrimethamine/cycloguanil/WR99210 controls | limited alchemical budget on the A4000 | Controls reproduce the published resistance ordering, else no claim |
| W4 | Re-label the 87.5 % divergence as descriptive, with ligand-level intervals | analysis only | No "validated compensation" framing anywhere |
| W5 | Publish ns/day per system measured on the RTX A4000 *before* committing to the 3 × 50 ns extension | benchmark run | Budget written into the DAR first |

### 6.5 The controls that make it credible

The measured self-mutation null (`RRS_null` [99.4, 100.5] for PfCRT, `K76A`/`NULL` deviations 0.51–1.2 pp); the reference-drug ordering as a *pre-registered* gate; charge-change scope limits declared up front (K76T/C59R need co-alchemical ions and finite-size corrections; they are marked **exploratory**); and the replica requirement stated as our design choice with disclosed seeds and a variance discussion, not as a published obligation (Soares et al., *JCIM* **63**(11), 3227–3229 (2023), DOI 10.1021/acs.jcim.3c00599, sets no ns cutoff; practice anchor Mey et al., *LiveCoMS* (2020)).

### 6.6 What must not be claimed

- No transport mechanism from a binding calculation: the class rule is a *classification*, and the efflux interpretation stays a hypothesis until a transport-relevant observable (pore hydration free-energy profile / gating coordinate) is reported.
- No FEP precision claim without a pilot (the "±1.0 kcal/mol at 1/10 the cost" rescaling is withdrawn).
- No "validated compensation" reading of the divergence.
- No new endpoints promoted from incomplete or failed runs (`AGENTS.md` rule 8).

### 6.7 What would falsify it

If the pore-hydration and barrier profiles do **not** separate the reference drugs into the two predicted classes, the efflux framing is not supported at this resolution and the paper keeps only the descriptive divergence result — which is why W2 freezes the rule on known drugs before any lead is scored.

### 6.8 Cover-letter line (for the editor)

> "We report a resistance score whose *sign* is a mechanism hypothesis, and we test that hypothesis against an independent transport-proximal observable computed from the same trajectories — with the classifier frozen on approved antimalarials before any of our own leads are scored."

---

## 7. Limits of this audit

- Trajectories, MM-GBSA endpoints and the FEP are not re-executed or re-derived here; values are read from the DAR at the pinned commit.
- The Wilson interval for 7/8 was not recomputed in this revision (the value is reproduced from `V2609C`).
- Computed ns/day on the RTX A4000 has not been measured; §3.5 makes that a prerequisite rather than a claim.
- Nothing here asserts a mechanism for efflux; §3.4(4) deliberately bounds the claim.
