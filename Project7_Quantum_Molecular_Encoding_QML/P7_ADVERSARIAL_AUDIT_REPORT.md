# P7 Adversarial Audit & Scientific Refinement Report
**Project:** `Project7_Quantum_Molecular_Encoding_QML` (Quantum Molecular Structure Encoding & Hybrid QML)
**Date:** 16 October 2026
**Auditor Frameworks:** BMAD Multi-Layer Review (`bmad-code-review`), Scientific Critical Thinking, Peer Review
**Cross-Project Context:** Integrated with findings from **P1** (Chemical Space & Polypharmacology), **P3** (Quantum-Inspired Representations & Scaffold Paradox), and **P5** (Scaffold Generalization in GNNs/Transformers).
**Literature Anchors:**
- Boy, Altamura, Manawadu, Tavernelli, Mensa, Wales, *"Encoding molecular structures in quantum machine learning"*, *Mach. Learn.: Sci. Technol.* 6, 045076 (2025) / [arXiv:2507.20422](https://arxiv.org/abs/2507.20422).
- Havlíček et al., *"Supervised learning with quantum-enhanced feature spaces"*, *Nature* 567, 209–212 (2019).
- Huang et al., *"Quantum advantage in learning from experiments"*, *Science* 376, 1182–1186 (2022).
- Thanasilp et al., *"Exponential concentration and untrainability in quantum kernel methods"*, *Quantum* 8, 1481 (2024).

---

## 1. Executive Summary & Audit Scorecard

Project 7 refocused on 06 October 2026 from an ECFP4-VQC architecture (archived as exploratory) to **Quantum Molecular Structure Encoding (QMSE)** directly embedded into parameterized quantum circuits with a classical head. The reported benchmark outcome is **Scenario C** (AUC $0.6398 \pm 0.0441$ vs. ECFP4-SVM $0.8693 \pm 0.0265$, paired $t$-test $p = 0.0009$).

An adversarial code and scientific audit was conducted across the entire codebase (`scripts/`, `qmse_lib/`), data manifests, the Data Analysis Report (`P7_DATA_ANALYSIS_REPORT.md`), the manuscript (`manuscript/`), and the structural empirical observations from **P1** and **P3** regarding **African Natural Products (ANP)**.

The audit reveals that Project 7's central hypothesis—that structure-direct quantum encoding can overcome the representation blind spots documented in P1, P3, and P5—is fundamentally compromised by implementation bugs and representation pathologies that specifically destroy African Natural Product molecular architectures.

### Audit Scorecard

| Layer | Severity | Status | Summary of Core Finding |
|---|:---:|:---:|---|
| **1. ANP Structural & Chemical Reality** | 🔴 **CRITICAL** | **FAIL** | ANP features identified in P1/P3 (multi-chiral centers, persistent $H_1$ ring cycles, bridged polycycles) are systematically destroyed by an RDKit traversal parity bug, 2D-only lookup matrices, and blind 8-qubit truncation. |
| **2. Quantum Architecture & Circuit Design** | 🔴 **CRITICAL** | **FAIL** | `p7_qmse_hybrid.py` applies independent 1-qubit $R_z$ rotations instead of 2-qubit entanglers for bonds; IBM hardware script employs a 51-qubit CSWAP test rather than an $n$-qubit inversion test. |
| **3. Provenance & Codebase Integrity** | 🟠 **MAJOR** | **FAIL** | Canonical scripts (`p7_qmse_preprocess.py`, `p7_phase_d_canonical.py`, `p7_stereo_probe.py`, `p7_ibm_kernel_aer.py`, `p7_generate_fig6.py`) and result JSONs claimed in DAR are **missing from Git**. |
| **4. Manuscript & Build Reproducibility** | 🟠 **MAJOR** | **FAIL** | LaTeX compilation aborts: `fig6_phased_results` is missing and a raw unicode character (`Δ` in `methods.tex`) causes pdflatex to crash. |
| **5. Scientific Claim Calibration** | 🟡 **MODERATE** | **FLAGGED** | Scenario C underperformance (AUC 0.640) is framed as a quantum limitation, but is largely an artifact of 8-atom arbitrary truncation and broken bond entangling. |

---

## 2. Cross-Project Context: ANP Structural Discoveries in P1 and P3

To understand why Project 7 failed to achieve its goals, we must contextualize it within the structural discoveries of the companion projects:

### 2.1 The Nature of African Natural Product Chemical Space (P1 & P2 Findings)
1. **High 3D Complexity & Saturation:**
   African natural products (isolated from databases such as NANPDB and EANPDB, analyzed in P1/P2) exhibit substantially higher fractions of $sp^3$ carbons ($Fsp^3 \approx 0.22 - 0.60$) and high chiral center counts compared to synthetic screening libraries.
2. **Dense Stereocenters:**
   Typical antimalarial natural product scaffolds (e.g. artemisinin, quinine, secosteroids, voacamine, naphthylisoquinolines) contain between **4 and 10+ chiral centers** arranged in rigid, stereodefined fused ring networks.
3. **The "ECFP4-Unreachable" Space:**
   In P1, generative expansion of 396 ANP seeds via STONED-SELFIES and CHEESE yielded a 65,856-compound library where **92.6% of molecules were ECFP4-unreachable** (Tanimoto distance $> 0.30$ from classical synthetic drug space), yet retained **69.3% of the Bemis–Murcko natural product cores**. Classical 2D fingerprints flatten stereocenters and struggle with bridged/caged natural product topologies.

### 2.2 Topological Persistence & The "Scaffold Paradox" (P3 Findings)
1. **The Scaffold Paradox ($H_1$ vs. $H_0$):**
   In P3, Topological Data Analysis (TDA) using persistent homology decomposed the ANP library into:
   - **Persistent 1D cycles ($H_1$ features):** Strongly conserved between ANP seeds and generated candidates (mean $H_1 = 3.61$). These represent the rigid polycyclic and macrocyclic rings characteristic of African antimalarials.
   - **0D connectivity ($H_0$ features):** Substantially divergent, capturing side-chain mutations and functional group substitutions.
2. **Why P3 Quantum-Inspired Kernels (QKS) Collapsed to Classical RBF:**
   In P3, PennyLane simulated quantum kernels (QKS via `IQPEmbedding`) failed to beat classical ECFP4-SVM (AUC 0.8385 vs. 0.9475; stacking $\Delta\text{AUC} = -0.0002$).
   **The root cause discovered in P3:** QKS took **ECFP4 compressed via UMAP** as its input! Because the classical input had already flattened the chiral, 3D, and polycyclic features of the ANP space, the quantum circuit was powerless to reconstruct them.

---

## 3. Layer 1: Chemical & Representation Audit — How P7 Collides with ANP Architecture

Project 7 refocused on QMSE (Boy et al. 2025) with the explicit goal of bypassing ECFP4 and encoding molecular graphs directly into quantum states. However, an adversarial audit reveals that P7's implementation creates a catastrophic mismatch with ANP structural reality:

### 3.1 The RDKit Chirality Tag Parity Bug (Critical Flaw)

In [`scripts/qmse_lib/processing.py`](file:///home/taamangtchu/Documents/Malaria_codesV2/Project7_Quantum_Molecular_Encoding_QML/scripts/qmse_lib/processing.py#L33-L52) and [`test_qmse_stereochemistry.py`](file:///home/taamangtchu/Documents/Malaria_codesV2/Project7_Quantum_Molecular_Encoding_QML/test_qmse_stereochemistry.py#L22-L25):

```python
def find_rs_stereoisomers(smiles):
    mol = Chem.MolFromSmiles(smiles)
    Chem.AssignAtomChiralTagsFromStructure(mol)
    chiral_cc = Chem.FindMolChiralCenters(mol, includeUnassigned=True)
    rs_stereoisomers = {'R': [], 'S': [], 'U': []}

    for idx, _ in chiral_cc:               # <--- BUG: Discards the CIP label!
        atom = mol.GetAtomWithIdx(idx)
        chiral_tag = atom.GetChiralTag()
        if chiral_tag == Chem.rdchem.ChiralType.CHI_TETRAHEDRAL_CCW:
            rs_stereoisomers['R'].append(idx)
        elif chiral_tag == Chem.rdchem.ChiralType.CHI_TETRAHEDRAL_CW:
            rs_stereoisomers['S'].append(idx)
```

#### Collision with ANP Complexity:
1. `Chem.FindMolChiralCenters(mol)` outputs `[(atom_idx, 'R'), (atom_idx, 'S')]`. The code discards the true Cahn-Ingold-Prelog (CIP) label with `_` and uses `atom.GetChiralTag()` instead.
2. In RDKit, `CHI_TETRAHEDRAL_CW` (`@@`) and `CHI_TETRAHEDRAL_CCW` (`@`) represent **internal atom ordering parity along the SMILES traversal**, NOT the invariant CIP $(R/S)$ configuration:
   - For $(S)$-alanine (`N[C@@H](C)C(=O)O`): tag is `CW` (`@@`), assigned `'S'`.
   - For $(S)$-alanine (`C[C@H](N)C(=O)O`): tag is `CCW` (`@`), assigned `'R'`.
   - For $(R)$-cysteine (`N[C@@H](CS)C(=O)O`): tag is `CW` (`@@`), erroneously assigned `'S'`.
3. In [`scripts/qmse_lib/matrix.py`](file:///home/taamangtchu/Documents/Malaria_codesV2/Project7_Quantum_Molecular_Encoding_QML/scripts/qmse_lib/matrix.py#L161-L163), this flips the sign of `diagonal_elements[idx]` for all atoms assigned to `'S'`:
   $$\text{Matrix}[i, i] = -0.5 \cdot Z_i^3$$
4. **Impact on ANPs:** ANPs carry 4–10+ chiral centers. When traversing complex polycyclic ANP SMILES, RDKit's internal node ordering changes depending on where the string begins or whether salts/side-chains are reordered. Because the parity tag flips arbitrarily between `@` and `@@`, the quantum feature map produces **exponentially corrupt state vectors** ($2^k$ parity combinations across $k$ stereocenters) for identical natural products.

### 3.2 Blind 8-Qubit Truncation Amputates ANP $H_1$ Ring Systems

- In Phase D, molecules were truncated to `n_qubits = 8` (the first 8 heavy atoms in the SMILES string).
- In P3, the mean $H_1$ ring feature count for ANPs was **3.61 cycles**, requiring 18–35 heavy atoms to form the complete polycyclic core.
- **The Pathology:** Truncating to 8 atoms in SMILES order literally slices through the middle of the fused ring system. For example:
  - In an artemisinin analogue (15+ heavy atoms, 7 stereocenters, endoperoxide bridge), an 8-atom truncation retains an arbitrary aliphatic or ester fragment and amputates the endoperoxide pharmacophore and 5 of the 7 chiral centers.
  - In a quinoline/acridine alkaloid, 8 atoms leaves a broken pyridine fragment and discards the antimalarial basic side-chain.
- **Divergence from Boy et al. (2025):** Boy et al.'s primary theoretical contribution was the **Fidelity-Preserving Chain-Contraction Theorem**, specifically formulated for long linear alkyl chains (e.g. fatty acids) where repetitive linear groups can be mathematically compressed. Applying blind 8-qubit truncation to rigid polycyclic ANPs violates the mathematics of QMSE, destroying both $H_1$ ring topology and stereochemical integrity.

### 3.3 The 2D-Lookup CoulombMatrix Blind Spot on 3D Conformations

In [`scripts/qmse_lib/matrix.py`](file:///home/taamangtchu/Documents/Malaria_codesV2/Project7_Quantum_Molecular_Encoding_QML/scripts/qmse_lib/matrix.py#L244-L261), `CoulombMatrix` does NOT compute physical 3D interatomic distances ($r_{ij} = \|\mathbf{R}_i - \mathbf{R}_j\|$) from a generated conformer. Instead, it queries an `AVERAGE_BOND_LENGTHS` dictionary of 2D bonded pairs:
$$\text{Matrix}[i, j] = \frac{Z_i \cdot Z_j}{d_{ij}^{\text{avg}}} \quad \text{if bonded, else } 0$$

#### Impact on ANPs:
- ANPs function biologically through 3D conformational shape, transannular interactions, and cavity electrostatics (e.g. binding deep inside the PfCRT transporter pore or the PfDHFR catalytic cleft, as shown in P1/P2).
- Setting non-bonded interatomic matrix elements to zero transforms the Coulomb matrix into a glorified 2D bond-length graph. Through-space electrostatic fields and chiral pocket geometries are completely lost.

### 3.4 The Role & Pitfalls of STONED-SELFIES in P7

While STONED-SELFIES is not executed directly inside `Project7_Quantum_Molecular_Encoding_QML`, it is the **foundational generative engine that created P7's entire data universe**:

#### 1. Upstream Data Provenance
- P7's canonical benchmark panel (`p3_benchmark_19849.csv`, 19,849 molecules) and external evaluation pool (`eos80ch_malaria_final_activity.csv`, 65,856 molecules) are direct outputs of the **STONED-SELFIES expansion** performed in P1 from 396 African Natural Product seeds and 454 synthetic antimalarials.
- Therefore, every model evaluated in P7 inherits the structural, topological, and stereochemical artifacts of STONED-SELFIES.

#### 2. The Core vs. Periphery Conflict (The "Scaffold Paradox" Collision)
- In P3, persistent homology demonstrated that STONED-SELFIES mutates peripheral functional groups (divergent $H_0$ connectivity, whole-molecule Tanimoto distance 0.206) while strictly conserving the rigid cyclic macro-structures and polycycles (conserved $H_1$ ring topology, mean 3.61 cycles, scaffold Tanimoto 0.379).
- **The Fatal Conflict with 8-Qubit Truncation:**
  When P7 truncated molecules to `n_qubits = 8` using RDKit's linear SMILES sequence, RDKit's serializer frequently began indexing at the mutated terminal side-chains. Slicing at atom index 8 means **P7 systematically encoded the mutated peripheral side-chain noise ($H_0$) while discarding the conserved natural product core scaffold ($H_1$)!**
  This explains why the QNN model's predictive performance plummeted to AUC 0.640: the model was trained on the stochastic side-chain permutations of STONED-SELFIES, while remaining completely blind to the antimalarial natural product scaffold.

#### 3. Stereochemical Incompatibility of Unconstrained SELFIES Mutations
- Standard STONED-SELFIES operates via string-level insertions, deletions, and substitutions on SELFIES tokens. While this guarantees 100% chemical validity (no valence violations), it **does not preserve or constrain 3D tetrahedral stereochemistry**:
  - Random SELFIES mutations frequently introduce undefined or inverted stereocenters (`CHI_UNSPECIFIED`).
  - In `qmse_lib/processing.py`, the `add_rs_stereochemistry()` function attempts to brute-force all combinations of `@` and `@@` for unspecified stereocenters ($2^k$ combinations), which compounds with the RDKit parity bug to generate dozens of unphysical stereoisomers.
  - If P7 claims to be the first architecture to evaluate structure-direct quantum stereochemical sensitivity, testing on uncurated STONED-SELFIES variants with scrambled stereocenters fundamentally compromises the experimental estimand.

#### 4. Prospective Recommendation: Should STONED-SELFIES Be Used Inside P7?
- **NOT as an unconstrained generative explorer:** Random SELFIES mutation will continue to scramble the delicate chiral networks of ANP polycycles.
- **ONLY as a chirality-locked perturbation probe:** STONED-SELFIES can be refined into an adversarial probe for quantum kernels by restricting mutations to achiral peripheral chains while freezing the core $H_1$ scaffold and CIP-verified stereocenters. This would test whether the quantum kernel $K(A, B)$ smoothly reflects structural edits or collapses into exponential concentration.

---

## 4. Layer 2: Quantum Architecture & Circuit Design Audit

### 4.1 Non-Entangling Bond Encodings in `p7_qmse_hybrid.py`

In [`scripts/p7_qmse_hybrid.py`](file:///home/taamangtchu/Documents/Malaria_codesV2/Project7_Quantum_Molecular_Encoding_QML/scripts/p7_qmse_hybrid.py#L159-L164):
```python
# CURRENT IMPLEMENTATION:
for i in range(self.n_qubits):
    for j in range(i+1, self.n_qubits):
        angle = np.arctan(submatrix[i, j]) if submatrix[i, j] != 0 else 0
        qml.RZ(angle, wires=i)
        qml.RZ(angle, wires=j)
```
- Applying $R_z(\theta)$ to wire $i$ and $R_z(\theta)$ to wire $j$ is a product of local single-qubit rotations: $U_{ij} = R_z(\theta)_i \otimes R_z(\theta)_j$.
- **Zero quantum entanglement is generated between bonded atoms.**
- Furthermore, the diagonal elements $\text{submatrix}[i, i]$ (atomic charges $Z_i$ and stereochemical signs) are completely omitted from the circuit.
- As written, the circuit is merely a parameter-free tensor product of local $Z$-rotations followed by a variational ansatz. The claim that molecular bond topology is encoded into the quantum state is mathematically incorrect for this script.

### 4.2 SWAP Test Scalability Disaster in `p7_ibm_quantum_kernel_svm.py`

In [`scripts/p7_ibm_quantum_kernel_svm.py`](file:///home/taamangtchu/Documents/Malaria_codesV2/Project7_Quantum_Molecular_Encoding_QML/scripts/p7_ibm_quantum_kernel_svm.py#L255-L277):
- To compute fidelity $K(A, B) = |\langle\psi_A|\psi_B\rangle|^2$, the code implements a **SWAP test**:
  $$2n + 1 \text{ qubits, with } n \text{ controlled-SWAP (Fredkin) gates}$$
- For a 25-atom ANP pair, this requires 51 qubits.
- On physical IBM heavy-hex processors (e.g. `ibm_brisbane`), a Fredkin gate decomposes into 7+ CNOT gates. Over 25 non-adjacent physical qubits, SWAP routing requires hundreds of two-qubit gates, causing total state decoherence and exponential concentration.
- **The Standard Solution:** In quantum kernel methods (Havlíček et al., *Nature* 2019), fidelity is computed via the **inversion test** ($U_B^\dagger U_A |0\rangle$):
  $$K(A, B) = |\langle 0| U_B^\dagger U_A |0\rangle|^2 = P(|00\dots0\rangle)$$
  This uses **$n$ qubits** instead of $2n+1$, and **zero CSWAP gates**.

---

## 5. Layer 3: Provenance & Repository Integrity Audit

A strict audit against Git history (`git status`, `git log`) reveals significant provenance divergence:

```
Claimed in DAR §6 (08-14 Oct)                  Actual State in Git Repository
-----------------------------------------       ------------------------------------
scripts/p7_qmse_preprocess.py                   ❌ MISSING (not in tree)
scripts/p7_phase_d_canonical.py                 ❌ MISSING (not in tree)
scripts/p7_stereo_probe.py                      ❌ MISSING (not in tree)
scripts/p7_ibm_kernel_aer.py                    ❌ MISSING (not in tree)
scripts/p7_generate_fig6.py                     ❌ MISSING (not in tree)
results/phase_d_canonical/*.json                ❌ MISSING (not in tree)
results/stereo_probe/*.json                     ❌ MISSING (not in tree)
results/phase_c_hpo/*.csv                       ❌ MISSING (not in tree)
manuscript/figures/fig6_phased_results.pdf      ❌ MISSING (compilation crashes)
```

**Audit Verdict:** Commit `9d55bea60` updated the DAR narrative and LaTeX text with Phase D results, but the scripts and data outputs were never committed to git.

---

## 6. Layer 4: Manuscript & Build Reproducibility Audit

Testing `pdflatex` directly on [`manuscript/main.tex`](file:///home/taamangtchu/Documents/Malaria_codesV2/Project7_Quantum_Molecular_Encoding_QML/manuscript/main.tex) reveals two immediate fatal errors:

1. **LaTeX Error:** `Unicode character Δ (U+0394)` at [`manuscript/sections/methods.tex:284`](file:///home/taamangtchu/Documents/Malaria_codesV2/Project7_Quantum_Molecular_Encoding_QML/manuscript/sections/methods.tex#L284).
   - Needs replacement with `$\Delta$`.
2. **LaTeX Error:** `File 'fig6_phased_results' not found` at [`manuscript/sections/results.tex:480`](file:///home/taamangtchu/Documents/Malaria_codesV2/Project7_Quantum_Molecular_Encoding_QML/manuscript/sections/results.tex#L480).
   - `fig6_phased_results.pdf` is missing from the `figures/` directory.

---

## 7. Layer 5: Re-calibrating "Scenario C" in Light of ANP Chemistry

In Phase D, the reported AUC is $0.6398 \pm 0.0441$ compared to classical ECFP4-SVM $0.8693 \pm 0.0265$ ($p = 0.0009$).
The manuscript frames this as an inherent limitation of quantum computing for molecular representations ("Scenario C honest negative").

**Critical Scientific Re-assessment:**
This underperformance is NOT proof that quantum molecular representations cannot encode chemistry. It is the deterministic mathematical outcome of:
1. **Truncation Amputation:** Slicing off 70% of each ANP molecule, breaking the conserved $H_1$ ring cycles identified in P3.
2. **Chiral Randomization:** The RDKit parity bug randomly assigning inverted diagonal signs to multi-chiral ANP stereocenters based on atom-traversal order.
3. **Pseudo-Entanglement:** Omitting two-qubit entangling gates for bonds in the hybrid model.

Framing an implementation artifact as an intrinsic quantum limitation misleads the drug discovery community. The manuscript must clarify that 8-atom truncation and 2D bond approximations destroy the pharmacophore of complex natural products.

---

## 8. Actionable Refinements & Complete Code Patches

### Refinement 1: Fix CIP Stereochemistry in `qmse_lib/processing.py`

Modify [`scripts/qmse_lib/processing.py`](file:///home/taamangtchu/Documents/Malaria_codesV2/Project7_Quantum_Molecular_Encoding_QML/scripts/qmse_lib/processing.py) to guarantee that absolute stereochemistry is invariant to SMILES atom ordering:

```python
def find_rs_stereoisomers(smiles: str) -> dict:
    """
    Accurately identify R/S stereocenters using Cahn-Ingold-Prelog (CIP) descriptors.
    Essential for African Natural Products with dense chiral centers.
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return {'R': [], 'S': [], 'U': []}

    Chem.AssignStereochemistry(mol, cleanIt=True, force=True, flagPossibleStereoCenters=True)
    chiral_centers = Chem.FindMolChiralCenters(mol, includeUnassigned=True)

    rs_stereoisomers = {'R': [], 'S': [], 'U': []}
    for idx, cip in chiral_centers:
        if cip == 'R':
            rs_stereoisomers['R'].append(idx)
        elif cip == 'S':
            rs_stereoisomers['S'].append(idx)
        else:
            rs_stereoisomers['U'].append(idx)

    return rs_stereoisomers
```

### Refinement 2: True 3D Conformer Coulomb Matrix for ANPs

Modify [`scripts/qmse_lib/matrix.py`](file:///home/taamangtchu/Documents/Malaria_codesV2/Project7_Quantum_Molecular_Encoding_QML/scripts/qmse_lib/matrix.py) to compute physical 3D through-space distances, capturing the chiral pockets and spatial cavities of ANPs:

```python
def compute_3d_coulomb_matrix(smiles: str, num_atoms_max: int = 24) -> np.ndarray:
    """
    Computes true 3D Coulomb matrix using ETKDGv3 conformer coordinates.
    Captures non-bonded through-space interactions vital for polycyclic ANPs.
    """
    mol = Chem.MolFromSmiles(smiles)
    mol = Chem.AddHs(mol)
    params = AllChem.ETKDGv3()
    params.randomSeed = 42
    if AllChem.EmbedMolecule(mol, params) != 0:
        AllChem.EmbedMolecule(mol, useRandomCoords=True)

    mol = Chem.RemoveHs(mol)
    conf = mol.GetConformer()
    n_atoms = mol.GetNumAtoms()

    matrix = np.zeros((num_atoms_max, num_atoms_max))
    limit = min(n_atoms, num_atoms_max)

    # 1. Diagonal: 0.5 * Z_i^2.4
    for i in range(limit):
        Zi = mol.GetAtomWithIdx(i).GetAtomicNum()
        matrix[i, i] = 0.5 * (Zi ** 2.4)

    # 2. Off-diagonal: Physical 3D Coulomb potential Z_i * Z_j / ||R_i - R_j||
    for i in range(limit):
        pos_i = np.array(conf.GetAtomPosition(i))
        Zi = mol.GetAtomWithIdx(i).GetAtomicNum()
        for j in range(i + 1, limit):
            pos_j = np.array(conf.GetAtomPosition(j))
            Zj = mol.GetAtomWithIdx(j).GetAtomicNum()
            dist = np.linalg.norm(pos_i - pos_j)
            val = (Zi * Zj) / max(dist, 0.1)
            matrix[i, j] = val
            matrix[j, i] = val

    return matrix
```

### Refinement 3: Replace SWAP Test with Inversion Test in `p7_ibm_quantum_kernel_svm.py`

Modify [`scripts/p7_ibm_quantum_kernel_svm.py`](file:///home/taamangtchu/Documents/Malaria_codesV2/Project7_Quantum_Molecular_Encoding_QML/scripts/p7_ibm_quantum_kernel_svm.py):

```python
def build_inversion_circuit(qc_A: QuantumCircuit, qc_B: QuantumCircuit) -> QuantumCircuit:
    """
    Computes |<ψ_B|ψ_A>|^2 using exactly n qubits (Inversion Test):
    |0> ---> U_A ---> U_B^† ---> Measure in |0...0> basis.
    Eliminates 2n+1 qubit overhead and destructive CSWAP gates on IBM hardware.
    """
    n_qubits = qc_A.num_qubits
    qc_inv = QuantumCircuit(n_qubits, n_qubits)

    # 1. Apply U_A
    qc_inv.compose(qc_A, inplace=True)

    # 2. Apply U_B^\dagger (inverse unitary)
    qc_inv.compose(qc_B.inverse(), inplace=True)

    # 3. Measure in computational basis
    qc_inv.measure(range(n_qubits), range(n_qubits))
    return qc_inv

def compute_fidelity_from_counts(counts: dict, total_shots: int) -> float:
    """Fidelity is the exact probability of measuring the all-zero state."""
    num_qubits = len(next(iter(counts.keys())))
    zero_key = '0' * num_qubits
    return counts.get(zero_key, 0) / float(total_shots)
```

### Refinement 4: Genuine Bond Entanglement for Hybrid Models

Modify [`scripts/p7_qmse_hybrid.py`](file:///home/taamangtchu/Documents/Malaria_codesV2/Project7_Quantum_Molecular_Encoding_QML/scripts/p7_qmse_hybrid.py):

```python
def encode_qmse_circuit(submatrix: np.ndarray, wires: list):
    """
    Proper QMSE encoding following Boy et al. (2025):
    - Single-qubit rotations for atomic numbers and CIP stereochemistry.
    - Two-qubit IsingZZ entangling gates for chemical bonds.
    """
    n_qubits = len(wires)

    # 1. Diagonal: Single-qubit rotation from atomic charges
    for i in range(n_qubits):
        angle_diag = submatrix[i, i]
        qml.RY(angle_diag, wires=wires[i])

    # 2. Off-diagonal: Two-qubit entangling gates for chemical bonds
    for i in range(n_qubits):
        for j in range(i + 1, n_qubits):
            val = submatrix[i, j]
            if abs(val) > 1e-5:
                # IsingZZ creates genuine two-qubit entanglement for bond (i, j)
                qml.IsingZZ(val, wires=[wires[i], wires[j]])
```

### Refinement 5: Fix LaTeX Manuscript Compilation
1. In [`manuscript/sections/methods.tex:284`](file:///home/taamangtchu/Documents/Malaria_codesV2/Project7_Quantum_Molecular_Encoding_QML/manuscript/sections/methods.tex#L284):
   - Replace `(Δ~$= 0.003$` with `($\Delta = 0.003$`.
2. Generate `manuscript/figures/fig6_phased_results.pdf` from DAR canonical values to satisfy `\includegraphics[width=\linewidth]{fig6_phased_results}` in `manuscript/sections/results.tex`.

---

## 9. Prioritized Implementation Roadmap

```
Step 1: Chemical Core & ANP Geometry Alignment
 ├── Patch qmse_lib/processing.py with true CIP stereochemistry
 ├── Introduce 3D conformer generation in qmse_lib/matrix.py for CoulombMatrix
 └── Replace linear atom slicing with a pharmacophore-aware subgraph reduction

Step 2: Quantum Circuit & Protocol Repairs
 ├── Update p7_qmse_hybrid.py with true IsingZZ bond entanglers
 └── Replace CSWAP test with Inversion test in p7_ibm_quantum_kernel_svm.py

Step 3: Manuscript Build & Provenance Recovery
 ├── Patch unicode Δ in manuscript/sections/methods.tex
 ├── Generate missing fig6_phased_results.pdf
 ├── Re-commit missing canonical scripts (p7_qmse_preprocess.py, p7_phase_d_canonical.py, etc.)
 └── Verify clean pdflatex build (0 errors)

Step 4: Manuscript Narrative Realignment
 └── Contextualize Scenario C: explain how 8-atom truncation amputated the conserved H_1
     polycyclic cores of African Natural Products documented in P1 and P3.
```

---

## 10. BMAD Novelty Audit: Why Project 7 Currently Reads as Incremental

Applying the BMAD `scientific-critical-thinking` (Construct Validity & Logical Fallacy Analysis) and `peer-review` frameworks exposes **four structural reasons** why Project 7, in its current form, would be judged by Q1 journal reviewers (*JCIM*, *RSC Digital Discovery*, *Machine Learning: Science and Technology*) as an **incremental derivative study**:

### 10.1 The "Method X on Dataset Y" Trap
- Project 7 directly imports the `qmse_lib` repository from Boy et al. (*Mach. Learn.: Sci. Technol.* 6, 045076, 2025) and applies it—with an arbitrary 8-qubit truncation—to the P3 antimalarial dataset.
- No new mathematical theorem, no new quantum circuit ansatz, and no domain-specific encoding adaptation for complex polycyclic natural products was introduced beyond adding 24 average bond lengths to a lookup dictionary.

### 10.2 The Circular Construct Validity Fallacy (`eos80ch` Surrogate Labels)
- **Fatal Epistemological Flaw:** P7 evaluates whether a stereochemically sensitive quantum encoding (QMSE) can outperform ECFP4 at predicting binary activity labels generated by **Ersilia `eos80ch`** (`p3_benchmark_19849.csv`).
- **Why this is circular:** `eos80ch` is itself a classical machine learning model trained on 2D Morgan/ECFP fingerprints! Because `eos80ch` is 100% blind to 3D stereochemistry ($R/S$ enantiomers receive the exact same `eos80ch` prediction), **ECFP4 is mathematically guaranteed to have maximal mutual information with `eos80ch` labels.**
- Any chiral or 3D conformational variance injected by QMSE acts as *orthogonal label noise* when evaluated against an ECFP-derived surrogate oracle. Testing a stereochemical quantum model on a stereochemistry-blind surrogate label is a classic **Construct Validity Failure**.

### 10.3 Redundant "Honest-Negative" Conclusion
- P3 already established that quantum-inspired kernels (QKS) on compressed fingerprints do not surpass classical ECFP4-RBF.
- P5 already established that deep graph/transformer representations degrade under scaffold splitting relative to ECFP4.
- Reporting a third negative result (AUC $0.640 < 0.869$) that is trivially explained by slicing off 70% of the molecule (8-atom truncation) does not advance quantum chemical theory.

### 10.4 Failure to Leverage the Unique Biophysical Assets of P1–P5
- Across P1–P5, this research program generated rare, high-value biophysical data: multi-target resistance resilience ratios (RRS) across wild-type and mutant *P. falciparum* targets (`PfDHFR`, `PfCRT`, `PfATP4`, `PfClpP`), explicit-solvent MD trajectories showing 87.5% static-vs-dynamic *Estimand Divergence* (P2), vacuolar pH 5.2 protonation states (P2), and $H_1$ persistent homology decompositions of African Natural Products (P3).
- P7 ignores all of these biophysical endpoints, regressing to a generic 1,000-compound binary classification benchmark.

---

## 11. Four Breakthrough Scientific Gaps & Novelties (BMAD Hypothesis Generation)

To transform Project 7 from an incremental replication into a **high-impact, genuinely novel contribution**, we formulate four competing/complementary methodological innovations grounded in the 2024–2026 QML literature:

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                 TRANSFORMATION OF PROJECT 7: INCREMENTAL → NOVEL                 │
├───────────────────────────┬──────────────────────────────────────────────────────┤
│ CURRENT P7 (Incremental)  │ PROPOSED P7 (Breakthrough Novelty)                   │
├───────────────────────────┼──────────────────────────────────────────────────────┤
│ Naive 8-atom slicing      │ Novelty 1: Topology-Guided Ring Contraction (PH-QMSE)│
│ (destroys H1 ANP cores)   │ Maps 1 qubit = 1 persistent H1 ring/pharmacophore    │
├───────────────────────────┼──────────────────────────────────────────────────────┤
│ Global fidelity K(A,B)    │ Novelty 2: Projected Quantum Kernels (1-RDM / 2-RDM) │
│ (O(N²) cost + exp. conc.) │ O(N) Classical Shadows; defeats barren plateaus      │
├───────────────────────────┼──────────────────────────────────────────────────────┤
│ 2D-lookup Coulomb & buggy │ Novelty 3: Parity-Odd 3D Chiral Volume Determinant   │
│ @/@@ traversal parity     │ SO(3)-invariant signed tetrahedral volume encoding   │
├───────────────────────────┼──────────────────────────────────────────────────────┤
│ Circular eos80ch labels   │ Novelty 4: Stereoisomer Activity Cliffs (ChEMBL 34)  │
│ (2D fingerprint surrogate)│ & P2 MD-RRS / pH 5.2 Vacuolar Transport Benchmarks   │
└───────────────────────────┴──────────────────────────────────────────────────────┘
```

### Novelty 1: Persistent-Homology Coarse-Grained QMSE (`PH-QMSE`) — Extending Boy et al. from 1D Chains to Polycyclic Natural Products
* **The Literature Gap:** Boy et al. (2025) proved a *Fidelity-Preserving Chain-Contraction Theorem* that compresses repetitive 1D linear alkyl chains ($-\text{CH}_2-$) into a single effective qubit rotation. However, their theorem breaks down on **2D/3D fused, bridged, and spiro polycyclic ring systems ($H_1 \ge 3$)**, which P1 and P3 proved are the defining topological signature of African Natural Products (mean $H_1 = 3.61$ cycles).
* **The Proposed Innovation:** Formulate **Topological Ring-Contraction QMSE (`PH-QMSE`)**, directly uniting P3 and P7:
  1. Decompose each molecule into its **Junction Tree / Persistent Homology $H_1$ ring cliques** and **chiral pharmacophore nodes** (typically 6–12 nodes per 35-atom ANP).
  2. Assign **1 qubit per $H_1$ ring cycle or chiral center** (instead of 1 qubit per arbitrary atom).
  3. Encode ring aromaticity, heteroatom count, and persistent homology birth–death lifetime $(\text{persistence } \tau = d - b)$ into single-qubit rotations $R_y(\theta_i), R_z(\phi_i)$.
  4. Encode ring-fusion bonds, spiro junctions, and inter-ring 3D dihedral angles into two-qubit entangling gates (`RXX`, `RYY`, `RZZ`).
* **Why This is High-Impact:** It solves the #1 bottleneck in quantum drug discovery—**how to fit a 35-heavy-atom natural product onto an 8–12 qubit NISQ processor without truncating a single pharmacophoric feature.**

### Novelty 2: Chiral Projected Quantum Kernels (`Chiral-PQK`) via Reduced Density Matrix Classical Shadows
* **The Literature Gap:** Standard fidelity quantum kernels $K(A,B) = |\langle\psi_A|\psi_B\rangle|^2$ suffer from two fatal flaws on drug datasets:
  1. **Exponential Concentration (Thanasilp et al., *Quantum* 2024):** As qubit count $n$ and entanglement grow, inner products between distinct states concentrate exponentially toward $2^{-n}$, turning the Gram matrix into $K \approx I$ (already observed in P7's 17-qubit Aer run where off-diagonal mean dropped to $0.059$ and AUC collapsed to $0.067$).
  2. **Quadratic Circuit Scaling ($O(N^2)$):** Computing a kernel for $N = 19,849$ molecules requires $\sim 1.97 \times 10^8$ pairwise circuit executions—impossible on IBM Quantum hardware.
* **The Proposed Innovation:** Replace global fidelity overlap with **Projected Quantum Kernels (PQK)** (Huang et al., *Science* 2021) using 1-qubit and 2-qubit **Reduced Density Matrices (1-RDM / 2-RDM)**:
  1. Execute the $n$-qubit QMSE circuit **only once per molecule ($O(N)$ scaling!)** and measure local Pauli expectation values $\mathbf{s}_i(M) = \left(\langle X_i \rangle, \langle Y_i \rangle, \langle Z_i \rangle\right)$ and bonded two-qubit correlators $\mathbf{c}_{ij}(M) = \left(\langle X_i X_j \rangle, \langle Y_i Y_j \rangle, \langle Z_i Z_j \rangle\right)$.
  2. Construct the Projected Quantum Kernel in classical post-processing:
     $$K_{\text{PQK}}(A, B) = \exp\left(-\gamma \sum_{i} \|\rho_i^{(1)}(A) - \rho_i^{(1)}(B)\|_F^2 - \beta \sum_{\langle i,j \rangle} \|\rho_{ij}^{(2)}(A) - \rho_{ij}^{(2)}(B)\|_F^2\right)$$
* **Why This is High-Impact:**
  - Reduces quantum hardware circuit executions on P3 ($N = 19,849$) from **197,000,000 circuits to 19,849 circuits** (a $10,000\times$ reduction!).
  - Mathematically provable immunity to global exponential kernel concentration while preserving genuine two-body quantum entanglement correlations across stereocenters.

### Novelty 3: $SO(3)$-Invariant, Parity-Odd Chiral Volume Determinant Encoding
* **The Literature Gap:** Standard GNNs (1-WL in P5), ECFP4 (P1/P3), and distance-only 3D Coulomb matrices ($Z_i Z_j / r_{ij}$) are **even under spatial inversion ($O(3)$-invariant)**—meaning a right-handed $(R)$-enantiomer and a left-handed $(S)$-enantiomer have identical distance matrices! Boy et al.'s ad-hoc heuristic (multiplying diagonal elements by $-1$) breaks continuity and fails on conformational ensembles.
* **The Proposed Innovation:** Introduce a physically rigorous **Parity-Odd Chiral Pseudoscalar Phase** at every tetrahedral center $i$ using the 3D coordinates of its four bonded neighbors $(\mathbf{r}_1, \mathbf{r}_2, \mathbf{r}_3, \mathbf{r}_4)$ ordered by CIP priority:
  $$\chi_i = \frac{\det\left[\mathbf{r}_1 - \mathbf{r}_4, \, \mathbf{r}_2 - \mathbf{r}_4, \, \mathbf{r}_3 - \mathbf{r}_4\right]}{\|\mathbf{r}_1 - \mathbf{r}_4\| \|\mathbf{r}_2 - \mathbf{r}_4\| \|\mathbf{r}_3 - \mathbf{r}_4\|} \in [-1, +1]$$
  - Encode symmetric electrostatics into polar qubit rotations $R_y(\theta_i)$ and the parity-odd chiral volume $\chi_i$ into the **azimuthal quantum phase** $R_z(\pi \chi_i / 2)$.
  - Under spatial reflection $\mathbf{r} \mapsto -\mathbf{r}$, $\chi_i \mapsto -\chi_i$, which applies the exact complex conjugation operator $\mathcal{K}$ to the quantum state $|\psi(R)\rangle = \mathcal{K}|\psi(S)\rangle$, while remaining strictly invariant under 3D rigid rotations $SO(3)$!
* **Why This is High-Impact:** Provides a rigorous group-theoretic ($SO(3)$-invariant, $O(3)$-covariant) quantum encoding of molecular chirality, directly linking 3D stereochemical geometry to Bloch-sphere phase coherence.

### Novelty 4: Eliminating the Surrogate Oracle — Benchmarking on Experimental Stereoisomer Cliffs & Biophysical RRS
* **The Methodological Gap:** As diagnosed in §10.2, benchmarking on `eos80ch` tests whether QML can imitate an ECFP4 model.
* **The Proposed Innovation:** Establish a three-tier **Stereochemically & Biophysically Grounded Benchmark** using data already curated in the repository:
  1. **Tier A — ChEMBL 34 Stereoisomer Activity Cliffs (The "ECFP4-Blind" Regime):**
     Extract all stereoisomer pairs (enantiomers and diastereomers, e.g., quinine vs. quinidine, artemisinin epimers, mefloquine erythro/threo isomers) from the 22,447 ChEMBL 34 experimental antimalarial dataset (`IC50` $\le 10\,\mu\text{M}$).
     - On these pairs, **ECFP4 Tanimoto similarity is 1.000**, so ECFP4-SVM and 1-WL GNNs achieve **exact random chance (AUC = 0.500)** on pair-ranking!
     - Demonstrate that `Chiral-PQK` / `PH-QMSE` achieves statistically significant discrimination ($\text{AUC} > 0.75$) on experimental stereoisomer activity cliffs.
  2. **Tier B — P1/P2 Resistance Resilience Score (RRS) & Vacuolar pH 5.2 Protonation:**
     Use `PH-QMSE` to predict target-specific RRS across `PfDHFR` (WT vs. quadruple mutant) and `PfCRT` (WT vs. `K76T` at digestive vacuole pH 5.2 vs. cytosolic pH 7.4), encoding pH-dependent formal charges into the diagonal qubit rotations.
  3. **Tier C — P2 Static-vs-MD *Estimand Divergence* Triage:**
     Test whether 3D conformational ensemble quantum shadows can distinguish the 12.5% true MD-stable polypharmacological leads from the 87.5% static-docking false positives identified in P2.

---

## 12. BMAD Experimental Design & Falsifiable Hypotheses for the Upgraded P7

Following the `hypothesis-generation` and `experimental-design` skills, we structure the upgraded Project 7 around three falsifiable hypotheses with pre-specified decision gates:

| Hypothesis | Mechanistic Claim | Control / Baseline | Primary Metric & Falsification Gate |
|---|---|---|---|
| **H1: Stereoisomer Cliff Resolution** | $SO(3)$-invariant parity-odd phase encoding ($R_z(\pi\chi_i/2)$) separates experimental ChEMBL 34 stereoisomer pairs that collide in 2D fingerprint space. | ECFP4-SVM & 1-WL GIN (both structurally locked at AUC = 0.50 on pure stereoisomer pairs). | Pairwise concordance / AUC on ChEMBL stereoisomer cliffs. **Gate:** $\text{AUC}_{\text{PQK}} \ge 0.70$ ($p < 0.01$, permutation test). |
| **H2: Topological Ring Contraction (`PH-QMSE`)** | Coarse-graining 25–40 atom ANPs into 8–12 $H_1$ ring/pharmacophore qubits preserves whole-molecule predictive signal lost by 8-atom SMILES truncation. | Naive 8-atom truncated QMSE (Phase D baseline, AUC $0.640$) & Boy et al. 1D chain contraction. | 5-fold CV AUC on experimental ChEMBL 34 & P3 panels. **Gate:** $\Delta\text{AUC} \ge +0.15$ over naive 8-qubit truncation ($p < 0.001$). |
| **H3: Projected Quantum Kernel (`PQK`) vs. Fidelity Kernel** | Local 1-RDM/2-RDM classical shadows prevent exponential kernel concentration as qubit count scales from $n=8$ to $n=20$. | Standard global overlap kernel $K(A,B) = |\langle\psi_A|\psi_B\rangle|^2$. | Off-diagonal kernel variance $\text{Var}[K_{ij}]$ and KTA across $n \in \{8, 12, 16, 20\}$. **Gate:** $\text{Var}[K_{\text{PQK}}]$ decays polynomially, whereas $\text{Var}[K_{\text{Fid}}] \propto 2^{-n}$. |
