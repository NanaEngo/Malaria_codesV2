#!/usr/bin/env python3
"""P4 — Molecular RL Environment for MCTS

Fragment-based molecular generation environment compatible with MCTSAgent.
Uses RDKit atom-map based fragment attachment to grow molecules step-by-step.

Interface expected by MCTSAgent:
    env.state              — current canonical SMILES (str)
    env.initial_smiles     — starting SMILES (str)
    env.step_count         — int
    env.max_steps          — int
    env.fragment_vocab     — list[str] of SMILES fragments
    env._fragment_set      — str
    env.randomize_attachment — bool
    env.reset()            -> str
    env.step(action: str)  -> (next_state: str, reward: float, done: bool, info: dict)
    env._is_terminal(state: str) -> bool

Fragment attachment strategy:
    For each step, a fragment SMILES is appended via a single-bond at a randomly
    chosen (or highest-degree) attachment point on the current molecule.
    RDKit's Chem.CombineMols + EditableMol is used for safe, valence-checked bonding.
    Invalid attachments fall back to returning the current state (no-op).
"""

from __future__ import annotations

import random
import warnings
from typing import Any, Optional

import numpy as np

try:
    from rdkit import Chem
    from rdkit.Chem import RWMol, AllChem, Descriptors
    HAS_RDKIT = True
except ImportError:
    HAS_RDKIT = False
    print("WARNING: RDKit not available. MolecularEnv will use string concatenation fallback.")


# ═══════════════════════════════════════════════════════════════════════════════
# Fragment Vocabulary — 108 fragments in 15 categories
# Selected for medicinal-chemistry relevance to antimalarial scaffolds (P1/P2)
# ═══════════════════════════════════════════════════════════════════════════════

_FRAGMENTS: dict[str, list[str]] = {
    # 1. Simple aromatics (12)
    "simple_aromatics": [
        "c1ccccc1",           # benzene
        "c1ccncc1",           # pyridine
        "c1ccoc1",            # furan
        "c1ccsc1",            # thiophene
        "c1ccnc1",            # pyrrole
        "c1cncc1",            # imidazole
        "c1cncnc1",           # pyrimidine
        "c1cnccn1",           # pyrazine
        "c1ccco1",            # 2H-furan
        "c1cnoc1",            # isoxazole
        "c1cnsc1",            # thiazole
        "c1cncn1",            # 1,2,4-triazole
    ],
    # 2. Fused ring systems (10)
    "fused_rings": [
        "c1ccc2ccccc2c1",     # naphthalene
        "c1cnc2ccccc2c1",     # quinoline
        "c1ccc2ncccc2c1",     # isoquinoline
        "c1ccc2[nH]ccc2c1",   # indole
        "c1ccc2occc2c1",      # benzofuran
        "c1ccc2sccc2c1",      # benzothiophene
        "c1cnc2ccccn12",      # imidazo[1,2-a]pyridine
        "c1ccc2cnccc2c1",     # quinoxaline
        "c1cnc2ccccc2n1",     # benzimidazole
        "c1ccc2c(c1)ccs2",    # thieno[2,3-b]pyridine
    ],
    # 3. Aliphatic chains (8)
    "aliphatic_chains": [
        "CC",                 # ethyl
        "CCC",                # propyl
        "CCCC",               # butyl
        "CC(C)C",             # isobutyl
        "CC(C)(C)C",          # tert-butyl
        "CCCCC",              # pentyl
        "CCCCCC",             # hexyl
        "C(C)CC",             # 2-methylpropyl
    ],
    # 4. Saturated carbocycles (7)
    "saturated_carbocycles": [
        "C1CC1",              # cyclopropane
        "C1CCC1",             # cyclobutane
        "C1CCCC1",            # cyclopentane
        "C1CCCCC1",           # cyclohexane
        "C1CCCCCC1",          # cycloheptane
        "C1CCC2CCCCC2C1",     # decalin
        "C1CC2CCCC2CC1",      # bicyclo[2.2.2]octane
    ],
    # 5. N-heterocycles (saturated/partial) (10)
    "n_heterocycles": [
        "C1CCNC1",            # pyrrolidine
        "C1CCNCC1",           # piperidine
        "C1CNCCN1",           # piperazine
        "C1COCCN1",           # morpholine
        "C1CCSC1",            # thiolane
        "C1CN2CCCC2CC1",      # quinuclidine
        "C1CNCC1",            # azetidine
        "C1CC1N",             # cyclopropylamine
        "C1CCNCC1C",          # 3-methylpiperidine
        "N1CCOCC1",           # morpholine (alt)
    ],
    # 6. Oxygen-containing groups (8)
    "oxygen_groups": [
        "CO",                 # methanol
        "CCO",                # ethanol
        "C(O)C",              # isopropanol
        "OC(=O)C",            # acetic acid
        "COC",                # dimethyl ether
        "CCOC",               # diethyl ether
        "OCC",                # ethylene glycol unit
        "C1CCOC1",            # tetrahydrofuran
    ],
    # 7. Nitrogen-containing groups (10)
    "nitrogen_groups": [
        "CN",                 # methylamine
        "CCN",                # ethylamine
        "C(N)C",              # isopropylamine
        "NC(=O)C",            # acetamide
        "CNC",                # dimethylamine unit
        "N(C)C",              # trimethylamine unit
        "NCC",                # ethylenediamine unit
        "C(=N)N",             # guanidinium unit
        "NNC",                # hydrazine unit
        "NC(=O)N",            # urea
    ],
    # 8. Sulphur/halogen groups (8)
    "s_x_groups": [
        "CS",                 # methanethiol
        "CF",                 # fluoromethane
        "CCl",                # chloromethane
        "CBr",                # bromomethane
        "C(F)(F)F",           # trifluoromethyl
        "SC",                 # thioether
        "S(=O)(=O)N",         # sulfonamide
        "S(=O)C",             # sulfoxide
    ],
    # 9. Carbonyl/acid groups (8)
    "carbonyl_groups": [
        "C(=O)C",             # acetyl
        "C(=O)O",             # carboxyl
        "C(=O)N",             # amide
        "C(=O)OC",            # ester
        "CC(=O)C",            # ketone
        "C=O",                # aldehyde
        "C(=S)N",             # thioamide
        "C(=O)Cl",            # acid chloride
    ],
    # 10. Quinoline/antimalarial privileged scaffolds (10)
    "antimalarial_privileged": [
        "c1ccc2nc(Cl)ccc2c1",         # 4-chloroquinoline core (CQ-like)
        "c1ccc2nc(N)ccc2c1",          # 4-aminoquinoline
        "Clc1ccnc2ccccc12",           # 8-aminoquinoline-like
        "c1ccc2c(c1)cncc2",           # acridine core
        "c1cc2ccccn2cc1",             # 1,8-naphthyridine
        "c1ccc2[nH]cnc2c1",           # purine-like
        "c1cnc2c(n1)cccc2",           # 1,6-naphthyridine
        "O=C1c2ccccc2-c2ccccc21",     # anthraquinone
        "c1ccc(-c2ccncc2)cc1",        # 4-phenylpyridine
        "c1ccc2c(c1)-c1ccncc1-2",     # acridine variant
    ],
    # 11. Spacers/linkers (7)
    "linkers": [
        "CC#N",               # acetonitrile
        "C#C",                # alkyne
        "C=C",                # alkene
        "NCC",                # aminoethyl linker
        "OCC",                # hydroxyethyl linker
        "CCNCC",              # diamine linker
        "CC(=O)NCC",          # acetamide linker
    ],
    # 12. Spirocycles (4)
    "spirocycles": [
        "C1CCC2(CC1)CCCC2",   # spiro[5.5]undecane
        "C1CCC2(CC1)CCCCC2",  # spiro[5.5]undecane (large)
        "O=C1CCC2(CC1)CCCC2", # spiro ketone
        "N1CCC2(CC1)CCNC2=O", # spiro lactam
    ],
    # 13. Michael acceptors / warheads (4)
    "warheads": [
        "C=CC(=O)N",          # acrylamide
        "C#CC(=O)N",          # propiolamide
        "C=CS(=O)(=O)N",      # vinyl sulfonamide
        "C=CC#N",             # acrylonitrile
    ],
    # 14. Bioisosteres (4)
    "bioisosteres": [
        "S(=O)(=O)O",         # sulfonate
        "B(O)O",              # boronic acid
        "P(=O)(O)O",          # phosphonate
        "C(F)=O",             # fluoroketone
    ],
    # 15. Macrocycle building blocks (6)
    "macrocycle_units": [
        "CCCCCCCCCC(=O)O",    # decanoic acid unit
        "NCCCCCCN",           # hexanediamine unit
        "OC(=O)CCCCC(=O)O",   # adipic acid unit
        "CCCCNC(=O)C",        # amide + chain
        "c1ccc(CCCC)cc1",     # phenylbutyl
        "C1CCCCCC1C(=O)O",    # cycloheptane acid
    ],
}

# Subset definitions
_SUBSET_KEYS: dict[str, list[str]] = {
    "all": list(_FRAGMENTS.keys()),
    "medium": [
        "simple_aromatics", "aliphatic_chains", "n_heterocycles",
        "nitrogen_groups", "oxygen_groups", "antimalarial_privileged",
    ],
    "aromatic_only": [
        "simple_aromatics", "fused_rings",
    ],
    "minimal": [
        "simple_aromatics",
    ],
}

# Cache for filtered fragment vocabularies keyed by fragment_set
_FRAGMENT_VOCAB_CACHE: dict[str, list[str]] = {}


def _build_vocab(fragment_set: str) -> list[str]:
    """Return flat list of SMILES for the chosen fragment subset.

    Fragments that cannot be attached to a simple methane seed without
    triggering RDKit valence/kekulization errors are filtered out at build
    time. This prevents the environment from repeatedly trying invalid
    actions during MCTS/baseline runs.
    """
    if fragment_set in _FRAGMENT_VOCAB_CACHE:
        return _FRAGMENT_VOCAB_CACHE[fragment_set]

    keys = _SUBSET_KEYS.get(fragment_set, _SUBSET_KEYS["all"])
    raw: list[str] = []
    for k in keys:
        raw.extend(_FRAGMENTS[k])

    if not HAS_RDKIT:
        return raw

    # Canonicalize and deduplicate first
    canon: list[str] = []
    for smi in raw:
        mol = Chem.MolFromSmiles(smi)
        if mol is not None:
            canon.append(Chem.MolToSmiles(mol))
    canon = list(dict.fromkeys(canon))

    # Filter out fragments that cannot be attached to a methane seed.
    # This prevents the environment from repeatedly proposing invalid
    # actions during MCTS/baseline runs. Expected RDKit warnings are
    # suppressed here because failure is the signal we use for filtering.
    from rdkit import RDLogger
    RDLogger.DisableLog("rdApp.*")
    try:
        test_rng = np.random.default_rng(0)
        valid: list[str] = []
        for smi in canon:
            try:
                attached = _attach_fragment("C", smi, randomize=False, rng=test_rng)
                if attached is not None and attached != "C":
                    valid.append(smi)
            except Exception:
                pass
    finally:
        RDLogger.EnableLog("rdApp.*")

    if len(valid) < len(canon):
        warnings.warn(
            f"_build_vocab('{fragment_set}'): {len(canon) - len(valid)} of {len(canon)} "
            f"fragments removed because they cannot be attached to methane."
        )
    _FRAGMENT_VOCAB_CACHE[fragment_set] = valid
    return valid


# ─────────────────────────────────────────────────────────────────────────────
# Chemistry helpers
# ─────────────────────────────────────────────────────────────────────────────

def _canonicalize(smiles: str) -> Optional[str]:
    """Return canonical SMILES or None if invalid."""
    if not HAS_RDKIT:
        return smiles
    mol = Chem.MolFromSmiles(smiles)
    return Chem.MolToSmiles(mol) if mol is not None else None


def _get_attachment_atom(mol: Any, randomize: bool, rng: np.random.Generator) -> Optional[int]:
    """
    Select an atom index suitable for fragment attachment.
    Prefers atoms with free valence (not fully saturated).
    """
    from rdkit.Chem import Atom

    candidates = []
    for atom in mol.GetAtoms():
        # Only C, N, O, S attachment points
        if atom.GetAtomicNum() not in (6, 7, 8, 16):
            continue
        # Skip aromatic atoms (would break aromaticity)
        if atom.GetIsAromatic():
            continue
        # Require at least one implicit H (free valence)
        if atom.GetTotalNumHs() > 0:
            candidates.append(atom.GetIdx())

    if not candidates:
        # Fallback: any non-H atom
        candidates = [a.GetIdx() for a in mol.GetAtoms() if a.GetAtomicNum() != 1]

    if not candidates:
        return None

    if randomize:
        return int(rng.choice(candidates))
    # Deterministic: pick atom with highest degree (most connected)
    return max(candidates, key=lambda i: mol.GetAtomWithIdx(i).GetDegree())


def _attach_fragment(mol_smiles: str, frag_smiles: str,
                     randomize: bool, rng: np.random.Generator) -> Optional[str]:
    """
    Attach fragment to molecule via a new single bond.
    Returns canonical SMILES of the combined molecule, or None if attachment fails.
    """
    if not HAS_RDKIT:
        return mol_smiles + "." + frag_smiles

    mol = Chem.MolFromSmiles(mol_smiles)
    frag = Chem.MolFromSmiles(frag_smiles)
    if mol is None or frag is None:
        return None

    # Select attachment atoms
    mol_attach = _get_attachment_atom(mol, randomize, rng)
    frag_attach = _get_attachment_atom(frag, randomize, rng)
    if mol_attach is None or frag_attach is None:
        return None

    # Combine molecules
    combo = Chem.RWMol(Chem.CombineMols(mol, frag))
    frag_offset = mol.GetNumAtoms()
    frag_atom_idx = frag_offset + frag_attach

    try:
        combo.AddBond(mol_attach, frag_atom_idx, Chem.BondType.SINGLE)
        Chem.SanitizeMol(combo)
    except Exception:
        return None

    result_smi = Chem.MolToSmiles(combo)
    # Validate result
    if Chem.MolFromSmiles(result_smi) is None:
        return None
    return result_smi


def _compute_mw(smiles: str) -> float:
    """Molecular weight for terminal condition (MW > 800 → too large)."""
    if not HAS_RDKIT:
        return 0.0
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return 0.0
    return Descriptors.MolWt(mol)


# ═══════════════════════════════════════════════════════════════════════════════
# MolecularEnv
# ═══════════════════════════════════════════════════════════════════════════════

class MolecularEnv:
    """
    Fragment-based molecular generation RL environment.

    Parameters
    ----------
    initial_smiles : str
        Starting molecule SMILES (default: 'C' = methane).
    max_steps : int
        Maximum number of fragment addition steps (default: 8).
    fragment_set : str
        Vocabulary subset: 'all' | 'medium' | 'aromatic_only' | 'minimal'.
    randomize_attachment : bool
        If True, attachment point is chosen randomly; else by highest degree.
    max_mw : float
        Molecular weight ceiling; stepping above this triggers done=True.
    seed : int or None
        RNG seed for reproducibility.
    """

    def __init__(
        self,
        initial_smiles: str = "C",
        max_steps: int = 8,
        fragment_set: str = "all",
        randomize_attachment: bool = False,
        max_mw: float = 800.0,
        seed: Optional[int] = None,
    ) -> None:
        # Canonicalize initial SMILES
        canon = _canonicalize(initial_smiles)
        if canon is None:
            raise ValueError(f"Invalid initial_smiles: {initial_smiles!r}")

        self.initial_smiles: str = canon
        self.max_steps: int = max_steps
        self._fragment_set: str = fragment_set
        self.randomize_attachment: bool = randomize_attachment
        self.max_mw: float = max_mw

        # Build vocabulary
        self.fragment_vocab: list[str] = _build_vocab(fragment_set)
        if not self.fragment_vocab:
            raise ValueError(f"Empty vocabulary for fragment_set={fragment_set!r}")

        # RNG (instance-level, thread-safe)
        self._rng: np.random.Generator = np.random.default_rng(seed)

        # State
        self.state: str = self.initial_smiles
        self.step_count: int = 0

    # ── Gym-like interface ──────────────────────────────────────────────────

    def reset(self) -> str:
        """Reset environment to initial state. Returns initial SMILES."""
        self.state = self.initial_smiles
        self.step_count = 0
        return self.state

    def step(self, action: str) -> tuple[str, float, bool, dict]:
        """
        Apply fragment addition action.

        Parameters
        ----------
        action : str
            Fragment SMILES to attach to the current molecule.

        Returns
        -------
        next_state : str
            SMILES after attachment (or unchanged if attachment fails).
        reward : float
            0.0 — reward is computed externally by the oracle in MCTSAgent.
        done : bool
            True if max_steps reached or MW ceiling exceeded.
        info : dict
            {'valid': bool, 'mw': float, 'n_atoms': int}
        """
        new_smiles = _attach_fragment(
            self.state, action,
            randomize=self.randomize_attachment,
            rng=self._rng,
        )

        if new_smiles is not None and new_smiles != self.state:
            self.state = new_smiles
            valid = True
        else:
            # No-op: attachment failed; state unchanged
            valid = False

        self.step_count += 1
        mw = _compute_mw(self.state)
        done = self.step_count >= self.max_steps or mw > self.max_mw

        info = {
            "valid": valid,
            "mw": mw,
            "n_atoms": Chem.MolFromSmiles(self.state).GetNumAtoms()
            if HAS_RDKIT and Chem.MolFromSmiles(self.state) is not None
            else 0,
        }
        return self.state, 0.0, done, info

    def _is_terminal(self, state: str) -> bool:
        """
        Check if state is terminal (MW ceiling or invalid SMILES).
        Called by MCTSAgent rollout to determine early stopping.
        """
        if not HAS_RDKIT:
            return False
        mol = Chem.MolFromSmiles(state)
        if mol is None:
            return True
        return Descriptors.MolWt(mol) > self.max_mw

    # ── Serialization helpers (for MCTSAgent._make_env_copy) ───────────────

    def get_config(self) -> dict:
        """Return constructor kwargs for lightweight copying."""
        return {
            "initial_smiles": self.initial_smiles,
            "max_steps": self.max_steps,
            "fragment_set": self._fragment_set,
            "randomize_attachment": self.randomize_attachment,
            "max_mw": self.max_mw,
        }

    def __repr__(self) -> str:
        return (
            f"MolecularEnv(state={self.state!r}, step={self.step_count}/{self.max_steps}, "
            f"vocab_size={len(self.fragment_vocab)}, set={self._fragment_set!r})"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# Smoke test
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="MolecularEnv smoke test")
    parser.add_argument("--fragment-set", default="medium",
                        choices=["all", "medium", "aromatic_only", "minimal"])
    parser.add_argument("--steps", type=int, default=5)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    print(f"=== MolecularEnv Smoke Test ===")
    env = MolecularEnv(
        initial_smiles="c1ccc2nc(Cl)ccc2c1",  # 4-chloroquinoline (CQ scaffold)
        max_steps=args.steps,
        fragment_set=args.fragment_set,
        randomize_attachment=True,
        seed=args.seed,
    )

    print(f"  Vocab size ({args.fragment_set}): {len(env.fragment_vocab)}")
    print(f"  Initial state:   {env.state}")
    print()

    rng = np.random.default_rng(args.seed)
    state = env.reset()
    for i in range(args.steps):
        action = env.fragment_vocab[rng.integers(len(env.fragment_vocab))]
        next_state, reward, done, info = env.step(action)
        print(f"  Step {i+1}: action={action!r:20s} → valid={info['valid']} "
              f"MW={info['mw']:.1f} atoms={info['n_atoms']} done={done}")
        if done:
            break

    print(f"\n  Final state: {env.state}")
    print(f"  Steps taken: {env.step_count}")
    print(f"\n  Subset sizes:")
    for subset in ["all", "medium", "aromatic_only", "minimal"]:
        v = _build_vocab(subset)
        print(f"    {subset:20s}: {len(v):3d} fragments")
