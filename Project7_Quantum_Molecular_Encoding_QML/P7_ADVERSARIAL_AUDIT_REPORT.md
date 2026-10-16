# P7 Adversarial Audit & Scientific Refinement Report
**Project:** `Project7_Quantum_Molecular_Encoding_QML` (Quantum Molecular Structure Encoding & Hybrid QML)
**Revision:** rev 2.1 — 16 October 2026. rev 2: addendum folded into the body, retracted targets removed, mis-attributed citations corrected, absolute `file://` links replaced by repo-relative paths, evidence pinning added. rev 2.1: **§8 "wow" factor** added with the new, committed `scripts/p7_chirality_fingerprint_probe.py` measurement (CHECK A and CHECK B); the former §8 (limits) is now §9.

## Audit pin

| Field | Value |
|---|---|
| Repository | `/home/nanaengo/Malaria_codesV2` (canonical single tree, `AGENTS.md` §0) |
| Branch / commit audited | `master` @ `1c9c38f2ec572d92f03073f765b6cd11b9b062a6` (2026-10-16T12:21:31+01:00) |
| Path convention | repo-relative only. rev 1 used `file:///home/taamangtchu/Documents/Malaria_codesV2/...`, which is **not** the canonical tree; those links are removed |
| Evidence rule | every factual claim carries a repository path **with sha256** or a DOI. A claim without one is `UNVERIFIED` |
| Auditor frameworks | BMAD multi-layer review (`bmad-code-review`), Scientific Critical Thinking, Peer Review |
| Cross-project context | P1 (chemical space, polypharmacology), P3 (quantum-inspired representations, scaffold paradox), P5 (scaffold generalization, surrogate-oracle caveat) |

**Superseded in rev 2 (do not re-assert):** "Thanasilp et al., *Quantum* 8, 1481 (2024)" (the paper is *Nature Communications* **15**, 5200 (2024)); "Huang et al., *Science* 2021" for projected quantum kernels (the paper is *Nature Communications* **12**, 2631 (2021)); the pre-registered superiority targets `AUC_PQK ≥ 0.70`, `ΔAUC ≥ +0.15` over 8-atom truncation, and "Var[PQK] decays polynomially"; "`PH-QMSE` solves the #1 bottleneck" (the ring-contraction theorem is unproven and needs its own fidelity analysis); and any "quantum advantage" framing.

**Key literature anchors (verification status in §6):**
- Boy, Altamura, Manawadu, Tavernelli, Mensa, Wales, *Mach. Learn.: Sci. Technol.* **6**, 045076 (2025), DOI 10.1088/2632-2153/ae304f / arXiv:2507.20422 — QMSE; reference implementation `stfc/quantum-molecular-encodings`.
- Thanasilp, Wang, Cerezo, Holmes, *Nature Communications* **15**, 5200 (2024) — exponential concentration in quantum kernels.
- Huang et al., *Nature Communications* **12**, 2631 (2021) — "Power of data in quantum machine learning" (projected quantum kernels, 1-RDM/2-RDM).
- Cerezo et al., *Nature Communications* **16**, 7907 (2025), DOI 10.1038/s41467-025-63099-6 — provable absence of barren plateaus implies (often) classical simulability.
- Bowles, Ahmed, Schuld, arXiv:2403.07059 (2024) — out-of-the-box classical models match or beat popular QML models; removing entanglement often did not hurt.
- Havlíček et al., *Nature* **567**, 209–212 (2019) — inversion test for fidelity kernels.

---

## 1. Executive summary & audit scorecard

Project 7 refocused on 06 October 2026 from an ECFP4-VQC architecture (archived as exploratory) to **Quantum Molecular Structure Encoding (QMSE)** embedded directly into parameterised circuits with a classical head. Reported outcome: **Scenario C** — AUC `0.6398 ± 0.0441` versus ECFP4-SVM `0.8693 ± 0.0265` (paired t-test p = 0.0009).

| Layer | Status | Summary |
|---|:---:|---|
| **1. ANP structural reality** | 🔴 **OPEN — implementation defects reproduced below** | The reported underperformance is produced by a CIP-parity bug, 2D-only bond-length matrices, and blind 8-atom truncation — not by an intrinsic limit of structure-direct quantum encoding. |
| **2. Quantum architecture** | 🔴 **OPEN — primary risk** | `p7_qmse_hybrid.py` applies independent 1-qubit `R_z` rotations where bond entanglers are required, so the "molecular bond encoding" is a product-state feature map and classically simulable by construction; the IBM script uses an `(2n+1)`-qubit SWAP test instead of an `n`-qubit inversion test. |
| **3. Provenance & codebase integrity** | 🟠 **CONFIRMED FAIL** | Five canonical scripts, three result directories and one figure claimed in the DAR are absent from the pinned commit (listing in §5). |
| **4. Manuscript & build reproducibility** | 🟠 **CONFIRMED FAIL** | `pdflatex` aborts on a raw `Δ` at `manuscript/sections/methods.tex:284` and on the missing `fig6_phased_results`. |
| **5. Claim calibration** | 🟡 **REVISED** | Scenario C must be reported as the combined effect of truncation and a non-entangling encoding; the publishable ceiling is parity or non-inferiority against matched classical baselines. |

---

## 2. Cross-project context

### 2.1 ANP chemical space (P1/P2)
ANP sets (NANPDB/EANPDB) show high `Fsp³` and 4–10+ stereocentres in rigid fused networks. P1's generative expansion of 396 ANP seeds (STONED-SELFIES + CHEESE) produced a 65,856-compound library in which 92.6 % of molecules were ECFP4-unreachable (Tanimoto distance > 0.30 from classical synthetic drug space) while 69.3 % of Bemis–Murcko natural-product cores were retained.

### 2.2 Topological persistence and the scaffold paradox (P3)
Persistent homology separated conserved 1D cycles (`H₁`, mean 3.61 cycles — the polycyclic/macrocyclic signature) from divergent 0D connectivity (`H₀` — peripheral substitution). P3's quantum-kernel arm took **ECFP4 compressed via UMAP** as input, so the circuit never had access to the chiral/3D/polycyclic features it was meant to exploit (AUC 0.8385 vs ECFP4-SVM 0.9475).

### 2.3 Structural limitations of the encoding (new in rev 2)
Project 7 inherits the surrogate-oracle problem documented in P5: the benchmark panel's labels come from Ersilia `eos80ch`, whose model family was trained on stage-specific antimalarial screening data (asexual blood stage vs gametocyte; van Heerden et al., *ACS Omega* 8(46), 43813–43826, 2023). A stereochemistry-sensitive encoder evaluated against a stereochemistry-blind surrogate measures alignment with the teacher, not chemical fidelity. Any Tier-A/B/C benchmark must therefore be built on experimental labels.

---

## 3. Chemical and representation audit

### 3.1 RDKit chirality parity bug (critical)
In `scripts/qmse_lib/processing.py` (`find_rs_stereoisomers`) the CIP label returned by `Chem.FindMolChiralCenters` is discarded (`for idx, _ in chiral_cc:`) and replaced by `atom.GetChiralTag()`, which encodes **SMILES traversal parity**, not configuration:

```python
for idx, _ in chiral_cc:                       # BUG: discards the CIP label
    atom = mol.GetAtomWithIdx(idx)
    if atom.GetChiralTag() == Chem.rdchem.ChiralType.CHI_TETRAHEDRAL_CCW:
        rs_stereoisomers['R'].append(idx)
    elif atom.GetChiralTag() == Chem.rdchem.ChiralType.CHI_TETRAHEDRAL_CW:
        rs_stereoisomers['S'].append(idx)
```

For (S)-alanine the tag is `CW` under `N[C@@H](C)C(=O)O` but `CCW` under the equivalent `C[C@H](N)C(=O)O`, so the assigned `R`/`S` label depends on where the SMILES string starts. `scripts/qmse_lib/matrix.py` converts that label into a sign flip on the diagonal (`Matrix[i,i] = −0.5·Z_i³`), so for molecules with `k` stereocentres the state vector can differ in `2^k` parity combinations between equivalent SMILES. ANPs carry 4–10+ stereocentres, which is exactly the regime where this is fatal.

**Fix (adopted):** keep the CIP descriptor returned by `Chem.FindMolChiralCenters` after `Chem.AssignStereochemistry(mol, cleanIt=True, force=True)`, and route `'U'` (unassigned) to its own bucket instead of guessing.

**Verified at the pinned commit (rev 2.1).** The defect is present, and so is a second, more serious one:

1. `scripts/qmse_lib/processing.py` (sha256 `3163b80d…`) defines `find_rs_stereoisomers` at line 33 and reads `atom.GetChiralTag()` at line 44 — the parity-based mapping is exactly as quoted above. `scripts/qmse_lib/matrix.py` (sha256 `7da75402…`) imports it (line 6), builds `diagonal_elements = 0.5 * atomic_numbers ** exponent` (line 151), and **multiplies the diagonal by −1 for every atom the function labels `'S'`** (lines 154–161). An ordering-dependent label therefore flips diagonal signs, i.e. up to `2^k` diagonal-sign patterns for the same molecule with `k` stereocentres.
2. **The project's own stereochemistry test encodes the same bug.** `test_qmse_stereochemistry.py` (repo root, sha256 `a50bd1be…`) re-implements `find_rs_stereoisomers` with the identical `CCW → 'R' / CW → 'S'` mapping (lines 12–30) and exercises it at lines 59 and 120–121. A regression test that asserts the wrong invariant cannot detect the defect it was written to protect, which is why the bug survived to the reported Scenario C. The replacement test is CHECK B of `scripts/p7_chirality_fingerprint_probe.py` (§8.2), which asserts the **CIP** invariant instead of the tag.

### 3.2 Blind 8-atom truncation amputates the `H₁` core
Phase D truncated molecules to the first 8 heavy atoms in SMILES order. ANP polycyclic cores need 18–35 heavy atoms; an 8-atom cut slices through the fused ring system, removing pharmacophoric features (e.g. the artemisinin endoperoxide bridge) and most stereocentres. Because STONED-SELFIES mutates the periphery preferentially, truncation in SMILES order systematically encodes the **mutated periphery** (`H₀`) while discarding the **conserved core** (`H₁`).

**Fix:** replace linear slicing with an explicit, fidelity-checked reduction, and report the contraction fidelity (see §4.4) before scaling to 25–40-atom molecules.

*(rev 2.1 note: the truncation logic reproduced above is in the Phase-D script `scripts/p7_phase_d_canonical.py`, which remains ABSENT from the tree — see §5. This defect therefore stays an inference from the audit's excerpt.)*

### 3.3 2D bond-length "Coulomb matrix"
`scripts/qmse_lib/matrix.py` fills off-diagonal elements only for bonded pairs, using an `AVERAGE_BOND_LENGTHS` lookup and zero elsewhere:
`Matrix[i,j] = Z_i·Z_j / d_ij^avg` if bonded, else `0`.
Setting non-bonded elements to zero discards through-space electrostatics and chiral pocket geometry — the features that distinguish polycyclic natural products in a binding site.

**Fix:** compute true 3D distances from an ETKDGv3 conformer (`Z_i·Z_j / ‖R_i − R_j‖` for all pairs within the truncation window), and, if a 2D-only fallback is retained for speed, report both matrices side by side rather than silently substituting one for the other.

### 3.4 Chirality must be parity-odd, and provably so
Distance-only representations (including `Z_i Z_j / r_ij`) are invariant under spatial inversion, so enantiomers are indistinguishable. The heuristic of flipping diagonal signs breaks continuity. A physically coherent alternative is the parity-odd pseudoscalar at each tetrahedral centre,
$$\chi_i = \frac{\det[\mathbf{r}_1-\mathbf{r}_4,\ \mathbf{r}_2-\mathbf{r}_4,\ \mathbf{r}_3-\mathbf{r}_4]}{\|\mathbf{r}_1-\mathbf{r}_4\|\,\|\mathbf{r}_2-\mathbf{r}_4\|\,\|\mathbf{r}_3-\mathbf{r}_4\|} \in [-1, +1],$$
encoded as an azimuthal phase `R_z(π χ_i / 2)`. This is `SO(3)`-invariant and flips sign under reflection.

**Requirement:** prove it numerically before any ML run — the feature must flip sign for known enantiomer pairs and be invariant under random rotations — and benchmark against a **classical** 3D chirality baseline so that any gain is attributable.

---

## 4. Quantum architecture audit

### 4.1 Non-entangling "bond" encoding (the central risk)
`scripts/p7_qmse_hybrid.py` applies `R_z(θ)` to wire `i` and separately to wire `j` for each bonded pair, i.e. `U_ij = R_z(θ)_i ⊗ R_z(θ)_j`. That is a product of local rotations: **no entanglement is generated**, the diagonal elements (`Z_i` and the stereochemical sign) are omitted, and the circuit is a parameter-free product-state feature map followed by a variational ansatz. Any reported result from such an encoder is classically simulable by construction — cf. Cerezo et al. (2025) and the benchmark result that removing entanglement often did not hurt classical comparisons (Bowles et al. 2024).

**Verified at the pinned commit (rev 2.1), with one correction to the paragraph above.** `scripts/p7_qmse_hybrid.py` (sha256 `648892b9…`) contains the encoding loop at lines 156–163: for each pair `i < j` it computes `angle = arctan(submatrix[i,j])` and applies `qml.RZ(angle, wires=i)` and `qml.RZ(angle, wires=j)`. Two facts follow, and one over-claim must be withdrawn:

- **Confirmed:** every piece of matrix information enters through *single-qubit* Z rotations on each wire, so the QMSE encoding is a product-state feature map; and the loop never touches `submatrix[i,i]`, so **the diagonal — atomic number and the stereochemical sign flip — is never encoded at all**.
- **Withdrawn as too strong:** “no entanglement is generated”. The variational ansatz (lines 166–181) does contain an entangling layer, selectable as `cnot`, `cz`, or `IsingZZ(0.1, …)`. The correct statement is narrower and stronger: the entangler is **fixed at strength 0.1** and applied only between **adjacent wires** (`qubit, qubit + 1`), i.e. on a linear topology unrelated to the molecular bond graph. The circuit therefore carries entanglement that is *molecularly uninformative*, while all molecular information is injected without entanglement.

**Fix:** single-qubit rotations from the diagonal (atomic number and CIP/stereo phase) plus genuine two-qubit entanglers **driven by the off-diagonal matrix elements on the bond graph**, with an **entanglement ablation** (with vs without entangler layers, and fixed vs matrix-driven strength) reported as a first-class result.

### 4.2 SWAP test instead of inversion test
`scripts/p7_ibm_quantum_kernel_svm.py` computes `K(A,B) = |⟨ψ_A|ψ_B⟩|²` with a SWAP test: `2n+1` qubits and `n` Fredkin gates; for a 25-atom pair that is 51 qubits, and each Fredkin expands to 7+ CNOTs, with SWAP routing across non-adjacent physical qubits. The standard construction is the **inversion test** (Havlíček et al. 2019): `K(A,B) = |⟨0|U_B†U_A|0⟩|² = P(|0…0⟩)` on **n** qubits and **zero** CSWAP gates.

### 4.3 Kernel diagnostics and the concentration check
Report, before any AUC: kernel-target alignment, effective dimension, and the **off-diagonal kernel variance as a function of qubit count** for `n ∈ {8, 12, 16, 20}`. Exponential concentration toward `2^{-n}` is a diagnosable property (Thanasilp et al. 2024), and a projected-kernel construction (1-RDM/2-RDM local Pauli expectations, Huang et al. 2021) reduces circuit executions from `O(N²)` to `O(N)`. Any claimed reduction must come with a cost table (circuits × shots × wall-clock), not a ratio.

### 4.4 Contraction fidelity: no appeal to an unproven theorem
Boy et al.'s fidelity-preserving chain-contraction theorem is stated for repeated **linear** substructures, with an application to long-chain fatty acids (abstract of arXiv:2507.20422). Extending contraction to fused/bridged/spiro ring systems is a **new, unproven** statement.

**Requirement:** on molecules small enough for the uncontracted circuit, report the fidelity `‖⟨ψ_full|ψ_contracted⟩‖²` (or kernel-matrix agreement) and its decay with the number of contracted rings, before applying ring contraction to 25–40-atom ANPs.

---

## 5. Provenance and build audit (confirmed)

| Claimed in DAR §6 (08–14 Oct) | State at pinned commit |
|---|---|
| `scripts/p7_qmse_preprocess.py` | ❌ ABSENT |
| `scripts/p7_phase_d_canonical.py` | ❌ ABSENT |
| `scripts/p7_stereo_probe.py` | ❌ ABSENT |
| `scripts/p7_ibm_kernel_aer.py` | ❌ ABSENT |
| `scripts/p7_generate_fig6.py` | ❌ ABSENT |
| `results/phase_d_canonical/*` | ❌ ABSENT |
| `results/stereo_probe/*` | ❌ ABSENT |
| `results/phase_c_hpo/*` | ❌ ABSENT |
| `manuscript/figures/fig6_phased_results.pdf` | ❌ ABSENT (compilation aborts) |

`manuscript/sections/methods.tex:284` contains a raw U+0394: `(Δ~$= 0.003$`. Both defects reproduce at the pinned commit.

**Repair requirements:** re-commit the scripts and result JSONs (or withdraw the affected DAR claims); hash the benchmark CSVs into the manifest; fix the raw `Δ`; generate the figure or remove the `\includegraphics`; add a CI LaTeX build that fails on errors and undefined references.

---

## 6. Verification ledger (claim → evidence)

| Claim | Status | Evidence |
|---|---|---|
| Boy et al. 2025, *MLST* 6, 045076 | ✅ Verified | DOI 10.1088/2632-2153/ae304f; arXiv:2507.20422 |
| Chain-contraction theorem applies to repeated **linear** substructures | ✅ Verified | arXiv abstract ("…with an application to long-chain fatty acids"); ring extension is a new statement |
| Reference QMSE implementation is public | ✅ Verified | `stfc/quantum-molecular-encodings` (GitHub) |
| Thanasilp et al. exponential concentration | ✅ **Corrected citation** | *Nature Communications* **15**, 5200 (2024) — previously cited as *Quantum* 8, 1481 |
| Projected quantum kernels (1-RDM/2-RDM) | ✅ **Corrected citation** | Huang et al., *Nature Communications* **12**, 2631 (2021) — previously cited as *Science* 2021 |
| Cerezo et al. barren plateaus ⇒ simulability | ✅ Verified | *Nature Communications* **16**, 7907 (2025), DOI 10.1038/s41467-025-63099-6 |
| "Better than classical?" benchmarking | ✅ Verified | arXiv:2403.07059 (2024) |
| `eos80ch` labels are stage-specific | ✅ Verified (cross-project) | van Heerden et al., *ACS Omega* 8(46), 43813–43826 (2023); see P5 audit §5 |
| STONED/SELFIES does not preserve stereo by default | ✅ Verified | Static string mutation; stereo must be handled externally in RDKit |
| Canonical scripts/results missing; `Δ` breaks the build | ✅ **Confirmed** | Direct tree inspection at the pinned commit (table in §5) |
| "PH-QMSE solves the #1 bottleneck" | ⏹ Withdrawn target | Requires its own fidelity proof (§4.4) |
| `AUC_PQK ≥ 0.70`; `ΔAUC ≥ +0.15` over 8-atom truncation; polynomial `Var[PQK]` decay | ⏹ Withdrawn targets | Outcome is **measured**; the comparator must be a matched classical baseline, not a broken one |
| Default Morgan/ECFP4-class fingerprints cannot separate enantiomers; chirality-aware ones can | ✅ **Verified (measured, rev 2.1)** | `scripts/p7_chirality_fingerprint_probe.py` CHECK A (sha256 `565abd0b…`, RDKit 2026.03.4): Tanimoto 1.0000 (default) vs 0.7333 / 0.5833 (chirality-aware) |
| CIP labels are invariant to SMILES re-rooting; raw `ChiralTag` is not | ✅ **Verified (measured, rev 2.1)** | same probe, CHECK B: CIP preserved 71/71 variants; tag flipped in 22, incl. artemisinin 15/20 |
| Encoder reads the QMSE diagonal? | ❌ **No — source-confirmed (rev 2.1)** | `scripts/p7_qmse_hybrid.py` lines 156–163 use only `submatrix[i,j]`, `i < j` (sha256 `648892b9…`) |
| “No entanglement is generated” (rev 2 §4.1 headline) | ⏹ **Withdrawn as too strong (rev 2.1)** | lines 166–181 contain a `cnot`/`cz`/`IsingZZ(0.1,…)` layer between adjacent wires; the accurate statement is *molecularly uninformative, fixed-strength* entanglement |
| SWAP test with `2n+1` qubits and CSWAPs (rev 2 §4.2) | ✅ **Source-confirmed (rev 2.1)** | `scripts/p7_ibm_quantum_kernel_svm.py` lines 226–276 (sha256 `eb96cc7c…`): `QuantumCircuit(2*n_qubits + 1, 1)`, `cswap(0, i+1, i+n_qubits+1)` |
| Code defects in §3.1–§4.2 | 🟡 §3.1, §4.1, §4.2 source-confirmed (§3.1 also measured); §3.2–§3.4, §4.3, §4.4 ⏸ assessed from quoted code | §3.1: `processing.py:33/44` + `matrix.py:151/154–161` + `test_qmse_stereochemistry.py:12–30`; §4.1: `p7_qmse_hybrid.py:156–181`; §4.2: `p7_ibm_quantum_kernel_svm.py:226–276` |

---

## 7. Refinement programme

rev 1 numbering retained for continuity: rev 1 §8 code patches → Appendix A; rev 1 §10 novelty audit → §1 and §7.4; rev 1 §11 novelties 1–4 (PH-QMSE, Chiral-PQK, parity-odd encoding, benchmark tiers) → §4.4, §4.3, §3.4 and §7.3 respectively; rev 1 §12 hypotheses H1–H3 → §7.5 below; rev 1 addendum C ladder R1–R4 → §7.1.

### 7.1 Decisive experiment ladder (each rung has a stop rule)

| Rung | Test | Stop rule |
|---|---|---|
| **R1** | Product-state QMSE versus a **matched classical kernel on the identical hybrid Coulomb-adjacency features** (8 qubits) | Parity ⇒ report parity; proceed only for the chirality question |
| **R2** | Add entangler layers; ablate with/without | No gain ⇒ drop all entanglement claims |
| **R3** | Ring/chain contraction versus 8-atom truncation versus ECFP4, scaffold-held-out; report contraction fidelity (§4.4) | Fidelity decay unacceptable ⇒ contraction withdrawn |
| **R4** | Chirality features on experimental stereoisomer pairs (ChEMBL), against a classical 3D baseline | Report AUROC of "which enantiomer is more active" with CI |

### 7.2 Port validation before application
Run the published Boy et al. benchmarks (state-phase classification, boiling-point regression) with the **reference implementation** as a regression test of the local port. This is the cheapest way to separate "our encoding is broken" from "QMSE is limited".

### 7.3 Benchmark design
Build the three-tier benchmark on **experimental** labels, not the `eos80ch` surrogate:
- **Tier A — stereoisomer activity cliffs** (enantiomer/diastereomer pairs from curated experimental antimalarial data; ECFP4 similarity 1.000, so fingerprint and 1-WL baselines sit at chance on pair ranking);
- **Tier B — resistance/biophysical endpoints** (P1/P2 sets), framed as **estimand-relative** comparisons;
- **Tier C — static-versus-MD divergence triage**, framed as a consistency study.

**Constraint:** P2's RRS and the static-vs-MD divergence are contested measurements (see the P1/P2 audits). They may be used as *targets of a consistency question*, not as ground truth for validating a new estimator.

### 7.4 Report ceiling
Following Cerezo et al. (2025) and Bowles et al. (2024), the realistic publishable outcome is **parity with, or no advantage over, matched classical baselines**, with a clear statement of where the encoding fails. Do not write "quantum advantage". Any positive result goes to the P7 DAR first, and manuscript claims follow only from completed, QC-passed runs (`AGENTS.md` rule 8).

---

### 7.5 Falsifiable hypotheses (rev 1 table, gates corrected)

| Hypothesis | Mechanistic claim | Control / baseline | Metric and decision rule (no pre-claimed values) |
|---|---|---|---|
| **H1 — Stereoisomer cliff resolution** | `SO(3)`-invariant, parity-odd phase encoding separates experimental stereoisomer pairs that collide in 2D fingerprint space | ECFP4-SVM and 1-WL GIN (structurally at chance on pure stereoisomer pairs) **plus a classical 3D chirality baseline** | Pairwise concordance/AUROC with CI. Decision: the **classical 3D baseline** must be beaten with a CI excluding zero. An absolute AUC target is not pre-claimed |
| **H2 — Topological ring contraction** | Coarse-graining 25–40-atom ANPs into 8–12 `H₁`-ring/chiral nodes preserves whole-molecule signal lost by 8-atom SMILES truncation | Naive 8-atom QMSE (Phase D baseline), Boy et al. 1D chain contraction, **and ECFP4** | Scaffold-held-out AUC with CI, after the contraction-fidelity check (§4.4). Decision: contraction beats naive truncation **and** is not worse than its matched classical kernel. The rev 1 gate `ΔAUC ≥ +0.15` is withdrawn |
| **H3 — Projected vs fidelity kernel** | Local 1-RDM/2-RDM features avoid the exponential concentration of global overlap kernels as qubit count grows | Global fidelity kernel `K(A,B) = ‖⟨ψ_A\|ψ_B⟩‖²` | Measured off-diagonal kernel variance across `n ∈ {8, 12, 16, 20}`, plus KTA and effective dimension. Decision: report the scaling **as measured**; the rev 1 claim of polynomial `Var[PQK]` decay is withdrawn |

---

## 8. The "wow" factor — what should make a referee or editor say *waouh*

**The one line.**

> A **refutation-ready quantum encoder**: its invariances are proved numerically *before* any ML claim, the published reference implementation is reproduced as a regression test so a null result can be attributed to physics rather than to a broken port, and the experiment that would end the programme is pre-registered.

### 8.1 Why it lands

Quantum machine learning has a credibility problem of its own making: benchmark claims against unverified baselines and undisclosed classical comparators, in a literature that has already shown out-of-the-box classical models matching or beating popular QML models (Bowles, Ahmed, Schuld, arXiv:2403.07059 (2024)) and that provable absence of barren plateaus tends to imply classical simulability (Cerezo et al., *Nat. Commun.* **16**, 7907 (2025), DOI 10.1038/s41467-025-63099-6). The paper's credibility therefore cannot come from a larger AUC; it has to come from **measurement hygiene that a referee can re-run**. Four things deliver that, and all four are cheap:

1. **The encoder's own defects are located in the tree *and* measured.** The claims in §3.1 are now both source-confirmed (`processing.py:33/44`, `matrix.py:151/154–161`) and numerically reproduced by a committed, read-only probe; §4.1–§4.2 were source-confirmed in the same pass, and one rev 2 headline was corrected in the process (“no entanglement is generated” → *fixed-strength, molecule-independent entanglement*, because the encoding uses only `i < j` off-diagonals and never reads the matrix diagonal). See §8.2. The finding that should worry a reviewer most is that **the project's own `test_qmse_stereochemistry.py` re-implements the same parity-based mapping**, so the test suite could not have caught the defect. The CIP/tag finding is not a code-reading opinion: the raw chiral tag **changed in 22 of 71 equivalent-SMILES variants**, and for **artemisinin** (7 stereocentres, the flagship polycyclic natural-product-like case) it changed in **15 of 20** — while the CIP descriptor was preserved in **71/71**. That is precisely the regime P7 operates in, and it converts the project's most damaging implementation finding into a quantified, reproducible statement about stereochemical encodings of ANP-like chemistry.
2. **A port regression test instead of an unverified implementation.** Running the published Boy et al. benchmarks (state-phase classification, boiling-point regression) with the public reference implementation `stfc/quantum-molecular-encodings` inside CI is the cheapest way to separate "our encoding is broken" from "QMSE is limited" (Boy et al., *Mach. Learn.: Sci. Technol.* **6**, 045076 (2025), DOI 10.1088/2632-2153/ae304f). Almost no QML paper does this; reviewers' first question is exactly whether the port is faithful.
3. **The seam is defined by the task, not by a race.** A stereo/chirality benchmark only means something when the strongest classical comparator is included — and the probe shows why: a *default* Morgan fingerprint cannot see chirality at all (Tanimoto 1.0000 on enantiomer pairs), whereas `includeChirality=True` separates them (0.7333 / 0.5833). A stereo result benchmarked against the default fingerprint is therefore vacuous, and the matched classical comparator must be the chirality-aware fingerprint **plus** a 3D shape/pharmacophore or 3D-chirality descriptor computed from the same conformers.
4. **Pre-registered stop rules and a declared ceiling.** The R1–R4 ladder (§7.1) states in advance which observation terminates which claim, and §7.4 states the publishable ceiling as **parity with matched classical baselines**. Saying up front what result would end the project is the single least common, most trust-generating sentence in this literature.

### 8.2 Wow at a glance (measured on 16 Oct 2026)

Command: `python3 scripts/p7_chirality_fingerprint_probe.py` → exit status **0** (script sha256 `565abd0b…`; RDKit **2026.03.4**; read-only, writes nothing).

| Result | Value | Evidence |
|---|---|---|
| Default fingerprint cannot rank enantiomers | Morgan r = 2, 2048 bits, count fingerprints: Tanimoto **1.0000** for alanine, threonine and lactic-acid pairs | `scripts/p7_chirality_fingerprint_probe.py` CHECK A |
| Chirality-aware fingerprint can | `includeChirality=True`: **0.7333** (alanine), **0.5833** (threonine), **0.7333** (lactic acid) | same |
| CIP label is ordering-invariant | preserved in **71/71** re-rooted SMILES variants (5 molecules, 1–7 stereocentres) | same, CHECK B |
| Raw chiral tag is not | flipped in **22** variants; artemisinin **15/20**; threonine 2/8; quinine 4/25 | same, CHECK B |
| The bug in the tree (source locations) | `scripts/qmse_lib/processing.py` line 33 / line 44 (sha256 `3163b80d…`); `scripts/qmse_lib/matrix.py` lines 151, 154–161 (sha256 `7da75402…`) | tree inspection at the pinned commit |
| The same bug in the project's own test | `test_qmse_stereochemistry.py` lines 12–30, used at 59 and 120–121 (sha256 `a50bd1be…`) — the regression test asserts the wrong invariant | tree inspection at the pinned commit |
| The bug's consequence in the encoder | `matrix.py` builds `diagonal = 0.5·Z^exponent` (line 151) and multiplies it by **−1** for every atom labelled `'S'` (lines 154–161), so equivalent SMILES can differ in up to `2^k` diagonal-sign patterns | report §3.1 |
| …and the encoder never reads that diagonal | the encoding loop covers only `i < j` (`submatrix[i,j]`), so the charge/stereo diagonal never reaches the circuit at all | `scripts/p7_qmse_hybrid.py` lines 156–163 (sha256 `648892b9…`) |
| Entanglement in the circuit is molecularly uninformative | the entangler is fixed at strength `0.1` and applied only between adjacent wires, independent of bonds or matrix values | `scripts/p7_qmse_hybrid.py` lines 166–181 (sha256 `648892b9…`) |
| Port test target | `stfc/quantum-molecular-encodings`; Boy et al. 2025 | report §6 |
| Executions saved by the inversion test | `n` qubits / 0 CSWAP instead of `2n+1` qubits / `n` Fredkin gates | Havlíček et al., *Nature* **567**, 209–212 (2019) |
| Concentration diagnostic | off-diagonal kernel variance vs `n`; PQK (1-RDM/2-RDM) cuts executions `O(N²)` → `O(N)` | Thanasilp et al., *Nat. Commun.* **15**, 5200 (2024); Huang et al., *Nat. Commun.* **12**, 2631 (2021) |
| Declared ceiling | parity with, or no advantage over, matched classical baselines | Cerezo 2025; Bowles 2024; §7.4 |

**Scope note:** `scripts/p7_chirality_fingerprint_probe.py` is **new work added by this revision**, not one of the five scripts reported ABSENT in §5; that table remains accurate and unchanged.

### 8.3 The artifact that carries it — one panel

**Figure P7-F ("the falsification panel"), four tiles**: (i) the committed probe table (default vs chirality-aware separability, CIP/tag invariance) with the CI exit status; (ii) the port regression result against the published QMSE benchmarks; (iii) the R1 parity plot — quantum versus **matched classical kernel on identical hybrid Coulomb-adjacency features** at 8 qubits; (iv) off-diagonal kernel variance as a function of qubit count `n ∈ {8, 12, 16, 20}`. Caption line: *"Our first result is a harness that fails the encoder when the physics is wrong."*

### 8.4 The decisive, cheap experiments

| # | Action | Cost | Gate |
|---|---|---|---|
| W1 | Run the probe in CI; fail the build if the CIP/tag invariance behaviour changes | minutes | Exit 0 on PASS; the probe is the regression test for the §3.1 fix |
| W2 | Port regression: reproduce the published QMSE benchmarks with the reference implementation | days | Published metric reported side by side with ours, with tolerance |
| W3 | **R1**: matched classical kernel on the *identical* hybrid Coulomb-adjacency features, 8 qubits | simulator hours | Parity ⇒ report parity, and the programme continues only on the chirality question |
| W4 | **R2**: entanglement ablation (with vs without entangler layers), reported as a first-class result | simulator hours | No gain ⇒ drop all entanglement claims |
| W5 | Numeric proof harness for the parity-odd `χ_i` (sign flip on known enantiomer pairs; invariance under random `SO(3)` rotations) *before* any ML run | minutes | Both properties must hold, else the stereochemistry programme stops here |
| W6 | **R3**: ring/chain contraction vs 8-atom truncation vs `ECFP4`, scaffold-held-out, with the contraction-fidelity check (§4.4) | simulator hours | Fidelity decay reported; unacceptable decay ⇒ contraction withdrawn |

### 8.5 The controls that make it credible

Matched classical kernel on identical features; classical comparators on the same conformers (chirality-aware fingerprint + 3D shape/pharmacophore + 3D chirality descriptor); the reference-implementation regression test; `n`-qubit inversion test rather than a `2n+1`-qubit SWAP test; explicit entanglement ablation; fidelity check before any contraction claim; and experimental (not surrogate) labels for the stereochemistry tier (§7.3).

### 8.6 What must not be claimed

- No "quantum advantage" framing; the declared ceiling is parity.
- No pre-claimed `AUC_PQK ≥ 0.70` or `ΔAUC ≥ +0.15` (withdrawn).
- No extension of Boy et al.'s chain-contraction theorem to fused/bridged/spiro rings without its own fidelity proof.
- No stereo claim benchmarked against a constitution-only fingerprint — the separator must be the chirality-aware classical comparator (measured in §8.2).
- No new manuscript claim from a run that has not passed QC (`AGENTS.md` rule 8).

### 8.7 What would falsify it

If **R1** reaches parity on *identical* features, the encoding contributes nothing beyond the classical kernel and the paper reduces to the chirality question; if the parity-odd `χ_i` fails the reflection/rotation harness (**W5**), the stereochemistry programme stops there; and if the port regression fails, no benchmark claim in the manuscript is admissible until it passes.

### 8.8 Cover-letter line (for the editor)

> "Our first quantum result is a falsification harness: we measure our own encoder's stereochemical defect (CIP preserved in 71/71 equivalent SMILES writes, raw parity not — 15/20 variants for artemisinin), we reproduce the published reference implementation as a regression test, and we pre-register the experiment whose parity outcome would end the claim."

---

## Appendix A — Code patches retained from rev 1

These are the rev 1 repair patches, kept for continuity. None of them may be claimed to improve performance until the §7.1 ladder has been run; they fix correctness first.

**A1 — CIP stereochemistry invariant to SMILES ordering** (`scripts/qmse_lib/processing.py`):

```python
def find_rs_stereoisomers(smiles: str) -> dict:
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return {'R': [], 'S': [], 'U': []}
    Chem.AssignStereochemistry(mol, cleanIt=True, force=True, flagPossibleStereoCenters=True)
    rs = {'R': [], 'S': [], 'U': []}
    for idx, cip in Chem.FindMolChiralCenters(mol, includeUnassigned=True):
        rs[cip if cip in ('R', 'S') else 'U'].append(idx)
    return rs
```

**A2 — True 3D Coulomb matrix from an ETKDGv3 conformer** (`scripts/qmse_lib/matrix.py`):

```python
def compute_3d_coulomb_matrix(smiles: str, num_atoms_max: int = 24) -> np.ndarray:
    mol = Chem.AddHs(Chem.MolFromSmiles(smiles))
    params = AllChem.ETKDGv3(); params.randomSeed = 42
    if AllChem.EmbedMolecule(mol, params) != 0:
        AllChem.EmbedMolecule(mol, useRandomCoords=True)
    mol = Chem.RemoveHs(mol)
    conf, n = mol.GetConformer(), mol.GetNumAtoms()
    m = np.zeros((num_atoms_max, num_atoms_max))
    lim = min(n, num_atoms_max)
    for i in range(lim):
        Zi = mol.GetAtomWithIdx(i).GetAtomicNum()
        m[i, i] = 0.5 * (Zi ** 2.4)
        for j in range(i + 1, lim):
            Zj = mol.GetAtomWithIdx(j).GetAtomicNum()
            d = np.linalg.norm(np.array(conf.GetAtomPosition(i)) - np.array(conf.GetAtomPosition(j)))
            m[i, j] = m[j, i] = (Zi * Zj) / max(d, 0.1)
    return m
```

**A3 — Inversion test instead of SWAP test** (`scripts/p7_ibm_quantum_kernel_svm.py`):

```python
def build_inversion_circuit(qc_A, qc_B):
    n = qc_A.num_qubits
    qc = QuantumCircuit(n, n)
    qc.compose(qc_A, inplace=True)
    qc.compose(qc_B.inverse(), inplace=True)
    qc.measure(range(n), range(n))
    return qc

def compute_fidelity_from_counts(counts: dict, total_shots: int) -> float:
    n = len(next(iter(counts)))
    return counts.get('0' * n, 0) / float(total_shots)
```

**A4 — Genuine two-qubit bond entanglement** (`scripts/p7_qmse_hybrid.py`):

```python
def encode_qmse_circuit(submatrix, wires):
    n = len(wires)
    for i in range(n):                      # diagonal: charge + stereo phase
        qml.RY(float(submatrix[i, i]), wires=wires[i])
    for i in range(n):                      # off-diagonal: bonds entangle
        for j in range(i + 1, n):
            v = submatrix[i, j]
            if abs(v) > 1e-5:
                qml.IsingZZ(float(v), wires=[wires[i], wires[j]])
```

**A5 — Manuscript build repairs:** replace the raw `Δ` at `manuscript/sections/methods.tex:284` with `$\Delta$`; generate `manuscript/figures/fig6_phased_results.{pdf,png}` from the canonical DAR values or remove the `\includegraphics`; add a CI `pdflatex` build that fails on errors and undefined references.

---

## 9. Limits of this audit

- No quantum circuit was executed and no model retrained. The Scenario C numbers (AUC 0.6398 ± 0.0441 vs 0.8693 ± 0.0265) are quoted from the DAR at the pinned commit.
- **Source-confirmed at the pinned commit in this revision:** §3.1 (`scripts/qmse_lib/processing.py:33/44`; `scripts/qmse_lib/matrix.py:151/154–161`; `test_qmse_stereochemistry.py:12–30`) — and measured by the committed probe (§8.2); §4.1 (`scripts/p7_qmse_hybrid.py:156–181`), where the rev 2 headline “no entanglement is generated” is withdrawn as too strong; §4.2 (`scripts/p7_ibm_quantum_kernel_svm.py:226–276`).
- **Not re-inspected in this revision:** §3.2 and §3.3 (the truncation and 2-D-matrix code lives in `scripts/p7_phase_d_canonical.py` and the preprocessing scripts, which remain ABSENT from the tree) and §4.3–§4.4 (diagnostics and contraction fidelity are proposals, not implemented code). Their verdicts remain inferences from the excerpts quoted in this report.
- The probe's CHECK B was run on five molecules (1–7 stereocentres, including artemisinin). It shows that the raw chiral tag is ordering-dependent and the CIP label is not; it does not, and cannot, quantify the resulting end-to-end AUC effect of the encoder bug.
- "PH-QMSE", `Chiral-PQK` and the Tier A/B/C benchmarks are proposals, not results.
- The reference-implementation regression test (§7.2) has not been run.
