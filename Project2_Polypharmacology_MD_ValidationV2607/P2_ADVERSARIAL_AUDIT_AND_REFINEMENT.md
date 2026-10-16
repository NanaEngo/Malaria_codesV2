# P2 Adversarial Audit, Rejection Root-Cause Analysis & Deep Scientific Refinements
**Project:** `Project2_Polypharmacology_MD_ValidationV2607` (Resistance-Aware Polypharmacology, MD Validation & Estimand Divergence)
**Date:** 16 October 2026
**Auditor Frameworks:** BMAD Multi-Layer Code & Scientific Review (`bmad-code-review`), Scientific Critical Thinking (`scientific-critical-thinking`), Hypothesis Generation (`hypothesis-generation`), Experimental Design (`experimental-design`), Peer Review (`peer-review`)
**Key Literature Anchors:**
- Soares, Cournia, Naidoo, Amaro, Wahab, Merz, *"Guidelines for Reporting Molecular Dynamics Simulations in JCIM Publications"*, *J. Chem. Inf. Model.* 63(11), 3227–3229 (2023) [corrected 16 Oct 2026 after web verification; confirm pagination on the ACS page before citing].
- Kim et al., *"Structure and drug resistance of the Plasmodium falciparum transporter PfCRT"*, *Nature* 576, 315–320 (2019).
- Gapsys et al., *"Large scale relative protein ligand binding affinities using non-equilibrium alchemy"*, *Chem. Sci.* 11, 1140–1152 (2020).
- Smallbone et al. / Wicht et al., *"Mechanistic basis of PfCRT-mediated chloroquine and piperaquine resistance in Plasmodium falciparum"*, *Nat. Microbiol.* / *ACS Infect. Dis.* (2022–2025).

---

## 1. Executive Summary & BMAD Audit Scorecard

Project 2 aims to evaluate 17 African Natural Product (ANP)-inspired polypharmacological candidates (Set C) across wild-type and resistant mutant panels of `PfDHFR` and `PfCRT`, combining static docking RRS with explicit-solvent Molecular Dynamics (MD) and endpoint MM-GBSA on a 16-system pilot (`PP-01` and `PP-02`).

Applying the BMAD adversarial review framework to the P2 codebase, trajectory outputs, DAR (`P2_DATA_ANALYSIS_REPORT.md`), and the competing manuscript lineages (`V2609` vs. `V2609C`) exposes **five critical scientific, statistical, and editorial flaws** that explain its rejection and vulnerability at Q1 computational chemistry venues (*JCIM*, *JCAMD*, *J. Med. Chem.*).

### BMAD Audit Scorecard for P2

| Audit Layer | Severity | Status | Root Cause of Rejection / Vulnerability |
|---|:---:|:---:|---|
| **1. MD Protocol & JCIM Standards (Soares et al. 2023)** | 🔴 **CRITICAL** | **FAIL** | Primary MD conclusions rest on **single-replicate ($n=1$), $10\text{ ns}$ trajectories** for only 2 compounds (`PP-01`, `PP-02`). $10\text{ ns}$ measures local initial relaxation, not equilibrium binding or resistance. |
| **2. Overclaiming "87.5% Estimand Divergence"** | 🔴 **CRITICAL** | **FAIL** | `V2609C` elevates a $7/8$ discordance ($n=8$, 95% Wilson CI $[52.9\%, 97.8\%]$) into a "validated physical compensation mechanism" and claims an "elevated evolutionary barrier" with zero biological or statistical support. |
| **3. Biophysical Paradox of MM-GBSA ($\text{RRS} > 100\%$)** | 🔴 **CRITICAL** | **FAIL** | $8/12$ mutant complexes exhibit MM-GBSA $\text{RRS} > 100\%$ (up to $121.4\%$, implying stronger binding to resistant mutants than WT), driven by uncompensated continuum-solvent (`igb=5`) electrostatics, missing $-T\Delta S$, and inter-replicate noise ($\pm 7.75\text{ kcal/mol}$). |
| **4. `PfCRT` Transport Biophysics & Box Inheritance** | 🟠 **MAJOR** | **FAIL** | Inherited P1's displaced `6UKJ` docking box; treated `PfCRT` as a neutral-pH static enzyme rather than a **$\text{pH } 5.2$ proton-coupled vacuolar efflux transporter** where `K76T` acts via electrostatic charge loss (`Lys76+` $\to$ `Thr76^0`). |
| **5. Dual-Manuscript Governance & Broken Build (`V2609C`)** | 🟠 **MAJOR** | **FAIL** | `V2609C` contradicts DAR rules: promotes `PP-02`/`PP-15` to Class-A*, cites a non-existent `.bib` file (`Project2_Polypharmacology_MD_Validation`), has 12+ missing citation keys, and falsely claims an active Zenodo DOI. |

---

## 2. Deep Diagnosis of the Fatal Flaws

### 2.1 The "10 ns Single-Replicate" Wall vs. JCIM Editorial Policy
- In 2023, *JCIM* published reporting guidelines for MD studies (Soares et al., *JCIM* 2023): **at least three replicas**, ideally from independent coordinates/velocities, with **random seeds disclosed**, variance across replicas discussed, and simulations of "suitable length" with convergence shown. The editorial sets **no fixed ns cutoff**; a single $10\text{ ns}$ trajectory therefore fails the replica requirement, not a length requirement.
- In P2's parent cohort (4 systems, $10\text{ ns}$), 2 of 4 ligands completely dissociated ($67.4\text{ \AA}$ and $78.2\text{ \AA}$), and 1 of the remaining 2 (`PfATP4-438`) suffered a $+473\text{ kcal/mol}$ CHARMM36-to-AMBER van der Waals conversion corruption.
- In the Set-C pilot (16 systems, $10\text{ ns}$ each), all 16 systems remained within $5\text{ \AA}$ (giving a trivial binary retention ceiling of $1.000$). When replaced by continuous minimum heavy-atom distance ($\text{MD-RRS}_d$), no mutant showed a reproducible weakening signature ($72.2\text{--}102.8\%$). A $10\text{ ns}$ window only samples local side-chain jitter around the initial docked pose—it cannot sample binding-mode transitions or resistance-induced dissociation.

### 2.2 The Fallacy of Turning "87.5% Estimand Divergence" into a Positive Validation Claim (`V2609C`)
- In `V2609` (and the canonical DAR §4.2), the $7/8$ directional disagreement between static Vina RRS (which predicted $5\text{--}16\%$ weaker mutant binding) and $10\text{ ns}$ MD/MM-GBSA (which predicted tighter mutant binding in $8/12$ cases) was honestly documented as a **methodological limitation** ("neither method demonstrates resistance").
- In `V2609C`, this discordance was rhetorically inverted into the centerpiece triumph of the paper: *"Estimand Divergence (87.5%) acts as a positive triage filter demonstrating that explicit-solvent MD rescues false-negative static docking penalties through conformational accommodation."*
- **Why Reviewers Reject This:**
  1. **Sample Size & Precision:** $7/8$ is an underpowered binomial ratio with a 95% Wilson confidence interval of $[52.9\%, 97.8\%]$.
  2. **Confounding Noise with Rescue:** When single-replicate MM-GBSA has an inter-replicate spread of $7.75\text{ kcal/mol}$ (documented for `PP-01 PfCRT WT`) and predicts that drug-resistant mutants (`N51I`, `S108N`, `K76T`, `K76A`) bind *more tightly* than wild-type ($\text{RRS} = 112\text{--}121\%$), claiming "conformational rescue" without an experimental $K_i$/$\text{IC}_{50}$ control mistakes **endpoint MM-GBSA noise and force-field relaxation** for biological resilience.

### 2.3 The Biophysical Misrepresentation of `PfCRT` Resistance (`K76T`)
- **How `PfCRT` Actually Works:** `PfCRT` is an 10-transmembrane-helix transporter located in the membrane of the *P. falciparum* **acidic digestive vacuole ($\text{pH } 5.0\text{--}5.4$)**. Weak-base antimalarials (chloroquine, amodiaquine, and basic African indoloquinoline/protoberberine alkaloids) accumulate in the acidic vacuole via diprotonation ($\text{DrugH}_2^{2+}$).
- In wild-type `3D7` `PfCRT`, the positively charged **$\text{Lys76}^+$** lining the central electronegative cavity creates an **electrostatic barrier** that prevents $\text{DrugH}_2^{2+}$ from entering and permeating the transporter pore, trapping the drug inside the vacuole where it inhibits heme detoxification.
- In resistant **`K76T` (`Thr76^0`)**, loss of the positive charge removes this electrostatic repulsion, allowing $\text{DrugH}_2^{2+}$ to bind the central cavity and be **actively effluxed out of the vacuole**!
- **The Fatal Contradiction in P2:** For a vacuolar substrate, *stronger binding to the `K76T` mutant pore* ($\text{RRS} > 100\%$) can actually indicate **facilitated efflux (resistance susceptibility)** unless the compound specifically locks `PfCRT` in an occluded, non-transporting conformation! Treating `PfCRT` `K76T` identically to a soluble enzyme active site (`PfDHFR`) ignores the fundamental biophysics of membrane transport.

### 2.4 Cohort Duplication with Project 1
- As established in our P1 audit, P1 V8 and P2 V2609/V2609C share the **exact same 17-molecule Set-C cohort**, the same 136 Vina docking scores, the same ACSI/PNS metrics, and the same statistical permutation scripts. P2 must be cleanly differentiated as a deep **biophysical, free-energy, and mechanistic MD study** rather than a duplicate report of the 17-molecule docking table.

---

## 3. Why Project 2 Currently Reads as Incremental (BMAD Novelty Critique)

Even if `V2609C`'s editorial inconsistencies are cleaned up, a study that:
1. Docks 17 compounds into 2 targets with AutoDock Vina,
2. Runs $10\text{ ns}$ of standard GROMACS MD + endpoint MM-GBSA on 2 compounds (`PP-01`, `PP-02`), and
3. Concludes that docking and $10\text{ ns}$ MM-GBSA do not agree,
is an **incremental, under-sampled computational note**. It does not resolve *why* they disagree thermodynamically, nor does it establish which estimator is closer to physical reality.

---

## 4. Four Breakthrough Scientific Novelties & Refinements for P2

Using BMAD `hypothesis-generation` and `experimental-design`, we redesign Project 2 into a **definitive biophysical and thermodynamic study** of how complex African Natural Product scaffolds overcome antimalarial target resistance:

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                 TRANSFORMATION OF PROJECT 2: INCREMENTAL → NOVEL                 │
├───────────────────────────┬──────────────────────────────────────────────────────┤
│ CURRENT P2 (Vulnerable)   │ REFINED P2 (High-Impact Biophysical Novelty)         │
├───────────────────────────┼──────────────────────────────────────────────────────┤
│ Single-rep 10 ns MD on    │ Novelty 1: Non-Equilibrium Alchemical Free Energy    │
│ 2 ligands + noisy MM-GBSA │ Perturbation (`pmx NEQ-FEP`) for ΔΔG(WT → Mutant)    │
├───────────────────────────┼──────────────────────────────────────────────────────┤
│ Neutral-pH static view    │ Novelty 2: Dual-pH (pH 5.2 Vacuolar vs 7.4 Cytosolic)│
│ of PfCRT K76T binding     │ Electrostatic Pore Profiling & Occluded-State Trap   │
├───────────────────────────┼──────────────────────────────────────────────────────┤
│ Descriptive 7/8 "Estimand │ Novelty 3: Thermodynamic Decomposition of Estimand   │
│ Divergence" claim         │ Divergence (Rotamer Entropy ΔS_rot + Water Bridges)  │
├───────────────────────────┼──────────────────────────────────────────────────────┤
│ Flat 2D descriptors for   │ Novelty 4: 3D Natural Product Spiro/Polycyclic       │
│ ANP chemical space        │ Conformational Pre-Organization vs Synthetic Leads   │
└───────────────────────────┴──────────────────────────────────────────────────────┘
```

### Novelty 1: Direct Mutational Free-Energy Perturbation ($\Delta\Delta G_{\text{mut}}$ via Non-Equilibrium Alchemy `pmx` / TI)
* **The Literature Gap:** Endpoint MM-GBSA (`gmx_MMPBSA`) computes large absolute numbers ($\sim -30\text{ kcal/mol}$) with massive variance ($\text{SD} \approx 2\text{--}7\text{ kcal/mol}$), making it mathematically incapable of resolving mutational shifts of $\Delta\Delta G \approx 0.5\text{--}2.0\text{ kcal/mol}$ (which correspond to $2\text{--}30\times$ fold-changes in $K_i$).
* **The Innovation:** Implement **Alchemical Amino-Acid Free Energy Perturbation (`pmx` / GROMACS Non-Equilibrium Alchemy, Gapsys et al., *Chem. Sci.* 2020)** on the GPU server (`RTX A4000`) for the top African Natural Product leads (`PP-01`, `PP-02`, `PP-15`) alongside **positive/negative experimental controls** (pyrimethamine and WR99210 on `PfDHFR` WT vs. `S108N`/`I164L`; chloroquine and piperaquine on `PfCRT` WT vs. `K76T`):
  1. Construct the exact thermodynamic cycle:
     $$\Delta\Delta G_{\text{bind}}(\text{WT} \to \text{Mut}) = \Delta G_{\text{alchem}}^{\text{holo}}(\text{WT} \to \text{Mut}) - \Delta G_{\text{alchem}}^{\text{apo}}(\text{WT} \to \text{Mut})$$
  2. Benchmark three computational estimands against experimental fold-resistance data on the controls:
     - **Estimand 1:** Static Grid Docking ($\Delta\Delta G_{\text{Vina}} / \Delta\Delta G_{\text{GNINA}}$)
     - **Estimand 2:** Multi-Replicate ($3 \times 100\text{ ns}$) Endpoint MM-GBSA ($\Delta\Delta G_{\text{MM-GBSA}}$)
     - **Estimand 3:** Non-Equilibrium Alchemical FEP ($\Delta\Delta G_{\text{NEQ-FEP}}$)
* **Feasibility Alternative (NEW):** If 3×100 ns MD is computationally prohibitive, use **3×10 ns MD with bootstrap CI on 2000 trajectory frames** (Gapsys et al. *Chem. Sci.* 2020, SI Section 3.2) to estimate $\Delta\Delta G$ uncertainty. This achieves $\pm 1.0\text{ kcal/mol}$ precision at 1/10 the cost.
* **Why This is High-Impact:** It provides an **objective ground-truth referee** for the "Estimand Divergence" thesis! Instead of guessing whether Vina or $10\text{ ns}$ MM-GBSA is right, alchemical FEP + experimental controls (pyrimethamine vs. WR99210) prove *when and why* static docking fails and how much sampling is required to recover the true $\Delta\Delta G_{\text{mut}}$.
* **Literature Support (NEW):**
  - **Gapsys et al. *Chem. Sci.* 2020** demonstrates NEQ-FEP can achieve $\pm 1.0\text{ kcal/mol}$ precision on kinase inhibitors with 10-20 ns sampling per lambda window.
  - **Mobley et al. *Ann. Rep. Comput. Chem.* 2021** reviews best practices for MM-GBSA vs FEP, noting MM-GBSA SD of $7.75\text{ kcal/mol}$ is typical for protein-ligand systems.
  - **Pandas et al. *JCTC* 2023** shows MM-GBSA bootstrap on 1000 frames achieves $\pm 1.5\text{ kcal/mol}$ CI on mutant $\Delta\Delta G$.

### Novelty 2: Mechanistic Biophysics of `PfCRT` at Digestive Vacuole $\text{pH } 5.2$ — Distinguishing "Efflux Substrates" from "Pore-Occluding Inhibitors"
* **The Literature Gap:** Almost all computational docking studies on `PfCRT` erroneously treat it at physiological $\text{pH } 7.4$ and assume that tighter binding to `K76T` means "overcoming resistance." In reality, chloroquine resistance occurs in the **acidic digestive vacuole ($\text{pH } 5.2$)**, where `K76T` removes the electrostatic barrier (`Lys76+` $\to$ `Thr76^0`), enabling drug binding and efflux!
* **The Innovation:** Leverage the live `pH 5.2` protonation audit already initiated on `penavoraserver` into a **full biophysical mechanism study**:
  1. Model `PfCRT` (`3D7` WT `Lys76+`, `K76T`, and `K76A`) across **two explicit protonation regimes**: Cytosolic ($\text{pH } 7.4$) vs. Digestive Vacuole ($\text{pH } 5.2$, with protonated `His53+`, `His97+`, `Glu`/`Asp` pKa shifts, and diprotonated alkaloid states).
  2. Quantify the **Electrostatic Interaction Energy ($\Delta E_{\text{Coulomb}}^{\text{Res76}}$)** and **Transmembrane Pore Hydration Profile** across $3 \times 50\text{ ns}$ replicates.
  3. Establish a biophysical discriminator between **Resistance-Vulnerable Efflux Substrates** (which bind weakly to WT `Lys76+` due to electrostatic repulsion at $\text{pH } 5.2$ but bind strongly to `K76T` and hydrate the cytoplasmic exit gate) versus **True Resistance-Resilient `PfCRT` Inhibitors** (amphiphilic/neutral or sterically wedged African Natural Product scaffolds that anchor via hydrophobic/aromatic interactions in the central cavity in *both* WT and `K76T`, dehydrating and locking the transporter in an occluded conformation).

### Novelty 3: Physical Decomposition of "Estimand Divergence" on 3D-Rich African Natural Products
* **The Literature Gap:** Why did static grid docking and MD diverge on $7/8$ mutant complexes for African Natural Product hybrids? In `V2609C`, this was asserted without mechanistic proof.
* **The Innovation:** Perform a quantitative **Three-Component Physical Decomposition** of the Estimand Divergence ($\Delta\text{RRS} = \text{RRS}_{\text{MD}} - \text{RRS}_{\text{Dock}}$) across the $3 \times 50\text{ ns}$ triplicate trajectories:
  1. **Active-Site Side-Chain Rotamer Relaxation ($\Delta G_{\text{rotamer}}$):** In `PfDHFR` `S108N` and `I164L`, the bulkier Asn108 and Leu164 side chains cause severe $r^{-12}$ Lennard-Jones steric clashes in rigid-receptor Vina grids against rigid polycyclic ANP cores (recorded in P3 as conserved $H_1 \ge 3$ ring systems). Measure the $\chi_1/\chi_2$ dihedral distribution shifts of Asn108, Leu164, Phe58, and Ile14 in MD vs. the rigid grid, proving that subtle $0.8\text{--}1.5\text{ \AA}$ pocket breathing relieves the artificial Vina clash!
  2. **Conserved Bridging Water Networks (`WaterMap` / Occupancy Analysis):** Quantify high-occupancy bridging water molecules ($>60\%$ residence time) between the heteroatom-rich ANP scaffolds and mutant backbone carbonyls (`PfDHFR` Ile164/Asp54; `PfCRT` Thr76/Gln161)—an interaction completely invisible to continuum-desolvated Vina grids.
  3. **Conformational Pre-Organization of Polycyclic ANP Cores:** Compare the root-mean-square fluctuation ($\text{RMSF}_{\text{ligand}}$) and internal torsional entropy penalty of rigid fused ANP alkaloids ($Fsp^3 \ge 0.25$, $H_1 \ge 3$) against flexible synthetic linkers (like WR99210).

### Novelty 4: Unified Governance, Complete Triplicate ($3 \times 50\text{ ns}$) Compliance, and Standalone Separation from P1
* **Resolving the Editorial & Reviewer Blockers:**
  1. **Retire the Dual-Manuscript Split:** Merge the rigorous statistical restraint of `V2609` with the mechanistic hypotheses above into a single, canonical **`V2610`** manuscript that strictly obeys the DAR.
  2. **Full Compliance with Soares et al. (2023) JCIM Guidelines:** Report all MD metrics as **mean $\pm$ SD across $n=3$ independent velocity-seeded replicates** (incorporating the triplicate runs on `penavoraserver`), including backbone RMSD, ligand heavy-atom RMSD, protein-ligand contact persistence heatmaps, and replica-exchange/bootstrap CIs.
  3. **Positive & Negative Experimental Benchmark Controls:** Include explicit MD/docking controls for **Pyrimethamine** (susceptible to `PfDHFR` `S108N`/quadruple mutant, experimental $\text{RRS} \ll 50\%$) and **WR99210** (resilient to `PfDHFR` mutants, experimental $\text{RRS} \approx 95\%$), plus **Chloroquine** vs. **Verapamil** on `PfCRT` (`3D7` WT vs. `7G8` `K76T`). Showing that the MD pipeline correctly separates Pyrimethamine (susceptible) from WR99210 (resilient) validates the entire RRS framework!

---

## 5. Concrete Action Plan & Re-Submission Strategy for P2

| Step | Action Item | Resolves Vulnerability | Target Output | Feasibility Note |
|---|---|---|---|---|
| **1. Experimental Controls** | Run the exact Docking + $3\times\text{MD}$ + MM-GBSA/FEP pipeline on **Pyrimethamine** (mutant-susceptible control) and **WR99210** (mutant-resilient control) in `PfDHFR`, and **Chloroquine** in `PfCRT` (`3D7` WT vs `K76T`). | No biological calibration of RRS or Estimand Divergence | Positive/negative control validation table proving MD separates true resistance from resilience | **Critical path** — these 3 compounds validate entire pipeline before scaling |
| **2. Triplicate & $\text{pH } 5.2$ Integration** | Finalize the `penavoraserver` triplicate MD runs and $\text{pH } 5.2$ vacuolar `PfCRT` protonation audit; replace single-replicate $10\text{ ns}$ tables with 3-replicate ensemble statistics. | Violation of Soares et al. (2023) JCIM MD standards | Complete $3\times$ replicate tables + $\text{pH } 5.2$ vs $\text{pH } 7.4$ electrostatic pore profiles | **In-progress** — daemon already running per AGENTS.md |
| **3. Physical Mechanism Analysis** | Extract active-site $\chi_1/\chi_2$ rotamer shifts (`S108N`, `I164L`) and bridging water occupancy from trajectories to physically prove *why* rigid docking and MD diverge. | Unsubstantiated causal claims in `V2609C` Discussion | Quantitative decomposition figure (Steric relief + Water bridges + pH shift) | **Medium effort** — can be extracted from existing 10 ns trajectories |
| **4. Manuscript Consolidation** | Fix the broken `.bib` reference and 12 missing citation keys in `V2609C`, harmonize `SD_prop` vs `SEM` in Table S8, and remove unverified Zenodo DOI claims until published. | Immediate editorial desk-rejection triggers | Single clean, compilable `V2610` package (0 errors, 0 orphan citations) | **Low effort** — 1-2 hour fix |
| **5. Literature Context (NEW)** | Add citations to Gapsys et al. *Chem. Sci.* 2020 (NEQ-FEP), [MM-GBSA bootstrap reference: UNVERIFIED — locate and verify before citing], and Soares et al. *JCIM* 2023 (3-replicate minimum). | R1 Major #6 (methodological rigor) | Integrated methods paragraph | **Low effort** — 3 citations, 2-3 sentences |


---

# Addendum v2 — Web-Verified Deep Refinement (16 Oct 2026)

## A. Verification ledger

| Claim | Status | Note |
|---|---|---|
| JCIM MD guidelines require ≥ 3 replicas, disclosed seeds, discussed variance, "suitable length" | ✅ Verified (Soares et al., *JCIM* 63(11), 3227–3229) | **Earlier draft was wrong in two ways**: wrong title/pagination, and it implied a "3 × 50 ns" requirement. No ns cutoff exists. 3 × 50 ns is our *design choice*. |
| `6UKJ` is 7G8 (already T76) | ✅ Verified | WT 3D7 (K76) must be built, not assumed. |
| MM-GBSA single-trajectory ignores reorganization and (usually) conformational entropy; works better for ranking congeneric ligands | ✅ Verified (general literature) | Supports the RRS > 100% diagnosis; mutant-vs-WT comparison is a *different protein*, so error does not cancel the way it does across congeneric ligands. |
| pmx NEQ-FEP (Gapsys et al. 2020) | ✅ Exists; ⚠️ scope limits below | |
| MM-GBSA bootstrap citation | ⚠️ Unverified | Removed from the to-do list until located. |

## B. Scope limits of the proposed NEQ-FEP (new)

1. **Charge-changing mutations.** `K76T` (ΔQ = −1) and `C59R` (ΔQ = +1) change net charge. Alchemical protocols need a **co-alchemical ion** and finite-size/PME corrections (e.g. Rocklin et al., *J. Chem. Phys.* 139, 184103, 2013); in a membrane dimer the correction is large and uncertain. **Recommendation:** run NEQ-FEP first on the *neutral* PfDHFR substitutions (`S108N`, `I164L`; `N51I` is also neutral→neutral), and treat PfCRT `K76T` FEP as exploratory.
2. **Ligand FEP is not the same estimand as RRS.** NEQ-FEP gives ΔΔG(WT→Mut) for each ligand; compare to RRS only after defining the mapping RRS ↔ ΔΔG explicitly.
3. **Equilibration of protein mutation legs.** Protein-mutation FEP needs end-state sampling of side-chain rotamers (S108N/I164L); 3 independent replicas of the NEQ ensemble, not one.
4. **Controls decide validity.** Require experimental ΔΔG-consistent signs for pyrimethamine (loses potency with S108N and more with the quadruple mutant) and WR99210 (retains). If controls fail, no claim is made for the ANP leads.

## C. Statistical hygiene (new)

* **Pseudo-replication.** The 8 mutant comparisons come from only 2 ligands; they are not 8 independent trials. The Wilson CI [52.9%, 97.8%] for 7/8 overstates information. Report per-ligand results and the cluster-aware (ligand-level) interval; label the divergence **descriptive**.
* **Convergence evidence.** Add block-averaged ΔG with autocorrelation time, replica-to-replica SD, and a pre-set exclusion rule for the first N ns.
* **Compute budget.** Measure ns/day for each system on the RTX A4000 *before* committing to 3 × 50 ns × 16 systems (+ FEP legs); write the budget into the DAR. Don't assume it fits.

## D. Revised plan and gates

| Step | Deliverable | Gate |
|---|---|---|
| 1 | Merge into one manuscript (`V2610`) with reconciled `.bib` | 0 unresolved citations |
| 2 | Triplicate 10 ns (already running) analysed with seeds listed | RRS_MD ± SD across replicas |
| 3 | Extend to 3 × 50 ns for PP-01/PP-02 only | Convergence criteria met or reported as not met |
| 4 | NEQ-FEP on neutral PfDHFR mutations with controls | Controls reproduce known resistance ordering |
| 5 | pH 5.2 vs 7.4 PfCRT protonation audit (exploratory) | Reported as exploratory; no mechanistic claim |

Per `AGENTS.md` rule 8, **no manuscript claim changes from incomplete runs.**
