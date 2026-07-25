#!/usr/bin/env python3
"""P4 — Molecular RL environment for MCTS-guided generator.

This module defines a Gym-compatible environment where:
- state  : a partial molecular graph / scaffold (SMILES string)
- action : attachment of a molecular fragment
- reward : composite pharmacological score (MPO, docking, SYBA, SA)

The environment uses RDKit (via datamol) to validate fragment attachments
and to combine molecules into chemically valid structures. Fragment
vocabulary has been expanded to cover common medicinal chemistry building
blocks.

Skills applied:
- datamol (scientific-agent-skills): simpler SMILES handling, validation
- rdkit (scientific-agent-skills): rdFingerprintGenerator API

Version: 0.9 — datamol integration + improved SMILES validation.
"""

from __future__ import annotations

import random
from typing import Any, Optional, Tuple

import logging
import datamol as dm
from rdkit import Chem
from rdkit.Chem import ValenceType
from rdkit.Chem.Lipinski import RotatableBondSmarts

logger = logging.getLogger(__name__)


# ── Medicinal chemistry fragment vocabulary ──────────────────────────
# Organised into categories for readability. SMILES use '*' as the
# attachment point where applicable (connected via a dummy atom).
FRAGMENT_LIBRARY: dict[str, list[tuple[str, str]]] = {
    "aromatic": [
        ("c1ccc([*])cc1",        "Phenyl"),
        ("c1cc([*])ccn1",        "4-Pyridyl"),
        ("c1c([*])nccn1",        "Pyrimidin-5-yl"),
        ("c1c([*])oco1",         "Furan-2-yl"),
        ("c1c([*])sc1",          "Thiophen-2-yl"),
        ("c1c([*])[nH]c1",       "Pyrrol-2-yl"),
        ("c1cn([*])cn1",         "Imidazol-1-yl"),
        ("c1c([*])ncs1",         "Thiazol-5-yl"),
    ],
    "saturated_heterocycle": [
        ("C1CC([*])NCC1",        "4-Piperidinyl"),
        ("C1COC([*])CN1",        "Morpholin-4-yl"),       # N-attachment
        ("C1CN([*])CCN1",        "Piperazin-1-yl"),       # N-attachment
        ("C1CC([*])CN1",         "Pyrrolidin-3-yl"),
    ],
    "alkyl": [
        ("[*]C",                 "Methyl"),
        ("[*]CC",                "Ethyl"),
        ("[*]C(C)C",             "Isopropyl"),
        ("[*]C(C)(C)C",          "tert-Butyl"),
        ("[*]C1CC1",             "Cyclopropyl"),
        ("[*]CC(F)(F)F",         "Trifluoroethyl"),
    ],
    "functional_group": [
        ("[*]O",                 "Hydroxyl"),
        ("[*]OC",                "Methoxy"),
        ("[*]OCC",               "Ethoxy"),
        ("[*]N",                 "Primary amine"),
        ("[*]N(C)C",             "Dimethylamino"),
        ("[*]C(=O)O",            "Carboxyl"),
        ("[*]C(=O)N",            "Primary amide"),
        ("[*]C(=O)OC",           "Methyl ester"),
        ("[*]S(=O)(=O)N",        "Sulfonamide"),
    ],
    "halogen_cn": [
        ("[*]F",                 "Fluoride"),
        ("[*]Cl",                "Chloride"),
        ("[*]Br",                "Bromide"),
        ("[*]C#N",               "Cyano"),
        ("[*]C(F)(F)F",          "Trifluoromethyl"),
        ("[*][N+](=O)[O-]",      "Nitro"),
    ],
    "fused_aromatic": [
        ("c1ccc2c([*])cccc2c1",   "1-Naphthyl"),
        ("c1cc([*])c2ccccc2n1",   "3-Quinolinyl"),
        ("c1c([*])cnc2ccccc12",   "4-Isoquinolinyl"),
        ("c1c([*])[nH]c2ccccc12",  "3-Indolyl"),
        ("c1c([*])nc2ccccc2n1",   "2-Quinazolinyl"),
        ("c1c([*])nc2ccccc2s1",   "2-Benzothiazolyl"),
        ("c1c([*])oc2ccccc12",    "2-Benzofuranyl"),
        ("c1c([*])sc2ccccc12",    "2-Benzothiophenyl"),
        ("c1nc2c([*])ncn2n1",     "8-Purinyl"),
        ("c1c([*])nc2[nH]cnc2n1", "6-Purinyl"),
        ("c1c([*])nc2ncnn2c1",    "2-Pteridinyl"),
        ("c1ccc2c([*])ncn2c1",    "4-Quinazolinyl"),
    ],
    "bridged_bicyclic": [
        ("C1CC2([*])CCC1C2",      "2-Bicyclo[2.2.1]heptanyl"),
        ("C1C2CC3([*])CC1CC(C2)C3", "1-Adamantyl"),
        ("C1CC2([*])CC1C2",       "2-Bicyclo[2.1.1]hexanyl"),
    ],
    "extended_alkyl": [
        ("[*]CCC",               "n-Propyl"),
        ("[*]CCCC",              "n-Butyl"),
        ("[*]CC(C)CC",           "Isobutyl"),
        ("[*]C1CCCC1",           "Cyclopentyl"),
        ("[*]C1CCCCC1",          "Cyclohexyl"),
        ("[*]CC1CC1",            "Cyclopropylmethyl"),
        ("[*]C(C)CC",            "sec-Butyl"),
        ("[*]CCCCCC",            "n-Hexyl"),
    ],
    "alkene_alkyne": [
        ("[*]C=C",               "Vinyl"),
        ("[*]CC=C",              "Allyl"),
        ("[*]C#C",               "Ethynyl"),
        ("[*]CC#C",              "Propargyl"),
        ("[*]/C=C/c1ccccc1",     "(E)-Styryl"),
        ("[*]C(C)=C",            "Isopropenyl"),
    ],
    "carbonyl": [
        ("[*]C(=O)C",            "Acetyl"),
        ("[*]C(=O)c1ccccc1",     "Benzoyl"),
        ("[*]C=O",               "Formyl"),
        ("[*]C(=O)CC",           "Propionyl"),
        ("[*]C(=O)OC(C)C",       "Isopropyl ester"),
        ("[*]C(=O)OCC",          "Ethyl ester"),
        ("[*]C(=O)N(C)C",        "N,N-Dimethylamide"),
        ("[*]C(=O)NC",           "N-Methylamide"),
        ("[*]C(=O)NH2",          "Carbamoyl"),
        ("[*]C(=O)NHOH",         "Hydroxamic acid"),
        ("[*]C(=O)CF",           "Fluoroacetyl"),
        ("[*]OC(=O)C",           "Acetoxy"),
    ],
    "sulfur_phosphorus": [
        ("[*]S(=O)(=O)C",        "Methylsulfonyl"),
        ("[*]S(=O)C",            "Methylsulfinyl"),
        ("[*]SC",                "Methylthio"),
        ("[*]S(=O)(=O)CF",       "Triflyl"),
        ("[*]S(=O)(=O)N(C)C",    "N,N-Dimethylsulfonamide"),
        ("[*]P(=O)(OC)OC",       "Dimethyl phosphate"),
        ("[*]S(=O)(=O)c1ccccc1", "Phenylsulfonyl"),
        ("[*]SCc1ccccc1",        "Benzylthio"),
    ],
    "more_heterocycles": [
        ("C1CC([*])OC1",         "3-Tetrahydrofuranyl"),
        ("C1CC([*])OCC1",        "4-Tetrahydropyranyl"),
        ("C1COC([*])O1",         "2-1,3-Dioxolanyl"),
        ("C1COC([*])OC1",        "4-1,3-Dioxanyl"),
        ("C1CC([*])NC1",         "3-Azetidinyl"),
        ("C1COC1([*])",          "3-Oxetanyl"),
        ("c1cn([*])nn1",          "1-Triazolyl"),
        ("c1c([*])nnn1",          "1-Tetrazolyl"),
        ("c1c([*])noc1",          "3-Isoxazolyl"),
        ("c1c([*])on1",           "3-Oxadiazolyl"),
        ("c1cn([*])nc1",          "1-Pyrazolyl"),
        ("c1c([*])n[nH]c1",       "4-Pyrazolyl"),
    ],
    "more_halogenated": [
        ("[*]C(F)F",             "Difluoromethyl"),
        ("[*]C(Cl)Cl",           "Dichloromethyl"),
        ("[*]CF",                "Fluoromethyl"),
        ("[*]OC(F)(F)F",         "Trifluoromethoxy"),
        ("[*]C(F)(F)CF",         "Pentafluoroethyl"),
        ("[*]SC(F)(F)F",         "Trifluoromethylthio"),
        ("[*]OC(F)F",            "Difluoromethoxy"),
    ],
    "amino_acid_like": [
        ("[*]CC(=O)O",           "Carboxyethyl"),
        ("[*]CC(=O)N",           "Carbamoylethyl"),
        ("[*]CN",                "Aminomethyl"),
        ("[*]CCN",               "Aminoethyl"),
        ("[*]CCCN",              "Aminopropyl"),
        ("[*]CN(C)C",            "N,N-Dimethylaminomethyl"),
        ("[*]CC(=O)NCC(=O)O",    "Glycylglycine-like"),
    ],
}

# Flatten to a single list of (smiles, name) pairs for runtime
FLATTENED_FRAGMENTS: list[tuple[str, str]] = [
    item for category in FRAGMENT_LIBRARY.values() for item in category
]


class MolecularEnv:
    """Molecular construction environment with expanded fragment vocabulary.

    Parameters
    ----------
    initial_smiles : str
        Starting scaffold SMILES.
    max_steps : int
        Maximum number of fragment additions before termination.
    fragment_set : str
        Which fragment set to use: "all" (default, 108 fragments, 14 categories), "minimal"
        (5 fragments, backward-compatible), or "aromatic_only".
    randomize_attachment : bool
        If True, randomly select attachment atoms instead of always picking
        the first available one. Adds stochasticity for exploration.
    """

    def __init__(
        self,
        initial_smiles: str = "C",
        max_steps: int = 10,
        fragment_set: str = "all",
        randomize_attachment: bool = False,
        seed: Optional[int] = None,
    ) -> None:
        # Standardize initial SMILES via datamol (handles tautomers, valences)
        initial_mol = dm.to_mol(initial_smiles)
        self.initial_smiles = dm.to_smiles(initial_mol) if initial_mol is not None else initial_smiles

        self.max_steps = max_steps
        self.state: str = self.initial_smiles
        self.step_count: int = 0
        self.randomize_attachment = randomize_attachment
        self._fragment_set = fragment_set
        self._rng = random.Random(seed)

        # Select fragment vocabulary
        if fragment_set == "all":
            self._fragment_vocab = [smi for smi, _ in FLATTENED_FRAGMENTS]
        elif fragment_set == "minimal":
            self._fragment_vocab: list[str] = [
                "c1ccccc1",  # phenyl
                "C",         # methyl
                "N",         # amine
                "O",         # hydroxyl
                "Cl",        # chloride
            ]
        elif fragment_set == "aromatic_only":
            self._fragment_vocab = [smi for smi, _ in FRAGMENT_LIBRARY["aromatic"]]
        else:
            self._fragment_vocab = [smi for smi, _ in FLATTENED_FRAGMENTS]

    @property
    def fragment_vocab(self) -> list[str]:
        """Return the list of available fragment actions."""
        return self._fragment_vocab

    @property
    def fragment_names(self) -> dict[str, str]:
        """Return a mapping from fragment SMILES to human-readable names."""
        return {smi: name for smi, name in FLATTENED_FRAGMENTS}

    def reset(self, initial_smiles: Optional[str] = None) -> str:
        """Reset the environment to the initial scaffold."""
        self.state = initial_smiles or self.initial_smiles
        self.step_count = 0
        return self.state

    def step(self, action: str) -> Tuple[str, float, bool, dict[str, Any]]:
        """Apply one fragment attachment and return (next_state, reward, done, info).

        Parameters
        ----------
        action : str
            SMILES fragment (with '*' attachment point) to attach.

        Returns
        -------
        tuple
            (next_state_smiles, reward, done, info)
        """
        self.state = self._attach_fragment(self.state, action)
        self.step_count += 1

        reward = self._dummy_reward(self.state)
        done = self.step_count >= self.max_steps or self._is_terminal(self.state)
        info = {
            "step": self.step_count,
            "smiles": self.state,
            "fragment": action,
            "fragment_name": self.fragment_names.get(action, "unknown"),
        }
        return self.state, reward, done, info

    def _find_attachment_atom(
        self, mol: Chem.RWMol, num_ref_atoms: int,
        is_fragment: bool = False, has_dummy: bool = False
    ) -> int | None:
        """Find a single atom for bond formation.

        For the scaffold (is_fragment=False): prefers aliphatic (non-ring)
        atoms with available implicit valence. Falls back to ring atoms.

        For the fragment (is_fragment=True): if has_dummy, returns the
        neighbour of the '*' dummy atom (preserving regiospecificity).
        Otherwise returns any atom with available valence.

        Parameters
        ----------
        mol : RWMol
            Combined molecule (scaffold + fragment).
        num_ref_atoms : int
            Number of atoms in the scaffold portion.
        is_fragment : bool
            If True, search in the fragment portion for attachment.
        has_dummy : bool
            If True, look for the '*' dummy atom's neighbour.

        Returns
        -------
        int | None
            Atom index for bond formation, or None if no suitable atom.
        """
        if is_fragment and has_dummy:
            # Find the dummy atom (atomic number 0) in the fragment portion
            for atom in mol.GetAtoms():
                if atom.GetAtomicNum() == 0 and atom.GetIdx() >= num_ref_atoms:
                    neighbors = [nbr.GetIdx() for nbr in atom.GetNeighbors()]
                    if neighbors:
                        return neighbors[0]
            return None

        # Determine which atoms to search
        if is_fragment:
            # Without dummy: use any fragment atom with implicit valence
            candidates = []
            for atom in mol.GetAtoms():
                idx = atom.GetIdx()
                if idx < num_ref_atoms:  # skip scaffold atoms
                    continue
                if atom.GetAtomicNum() == 0:  # skip dummy atoms
                    continue
                try:
                    if atom.GetValence(ValenceType.IMPLICIT) > 0:
                        candidates.append(idx)
                except Exception:
                    pass
            return candidates[0] if candidates else None

        # Scaffold attachment: find atoms with available valence
        candidates = []
        for atom in mol.GetAtoms():
            idx = atom.GetIdx()
            if idx >= num_ref_atoms:
                continue
            if atom.GetAtomicNum() == 0:
                continue
            try:
                implicit = atom.GetValence(ValenceType.IMPLICIT)
            except Exception:
                implicit = 0
            if implicit > 0:
                candidates.append(idx)

        if not candidates:
            return None

        if self.randomize_attachment:
            return self._rng.choice(candidates)

        # Prefer aliphatic (non-ring) attachment sites
        aliphatic = [i for i in candidates if not mol.GetAtomWithIdx(i).IsInRing()]
        if aliphatic:
            return aliphatic[0]
        return candidates[0]

    def _attach_fragment(self, state: str, fragment_smiles: str) -> str:
        """Attach a fragment to the current molecule using RDKit.

        The fragment SMILES may contain a '*' dummy atom as the attachment
        point. If present, the dummy atom is resolved to its neighbour(s)
        and bonded to the scaffold. If absent, any atom with available
        valence is used.

        Parameters
        ----------
        state : str
            Current molecular SMILES.
        fragment_smiles : str
            Fragment SMILES to attach.

        Returns
        -------
        str
            Resulting SMILES, or the original state if attachment fails.
        """
        mol1 = Chem.MolFromSmiles(state)
        if mol1 is None:
            return state

        # Handle fragments with '*' attachment points:
        # Keep the dummy atom through CombineMols to preserve regiospecificity.
        has_dummy = "*" in fragment_smiles
        frag_smi_clean = fragment_smiles.replace("[*]", "*") if has_dummy else fragment_smiles
        mol2 = Chem.MolFromSmiles(frag_smi_clean, sanitize=False)

        if mol2 is None:
            return state

        # Sanitize: try without dummy first, then with dummy present
        try:
            if not has_dummy:
                Chem.SanitizeMol(mol2)
        except Exception:
            return state

        # Combine molecules (dummy atom preserved in mol2)
        combined = Chem.CombineMols(mol1, mol2)
        rw_mol = Chem.RWMol(combined)
        num_mol1_atoms = mol1.GetNumAtoms()

        # Find the attachment point on the scaffold
        scaffold_attachment = self._find_attachment_atom(rw_mol, num_mol1_atoms, is_fragment=False)
        if scaffold_attachment is None:
            return state

        # Find the attachment point on the fragment
        fragment_attachment = self._find_attachment_atom(rw_mol, num_mol1_atoms, is_fragment=True, has_dummy=has_dummy)
        if fragment_attachment is None:
            return state

        # Create the bond
        rw_mol.AddBond(scaffold_attachment, fragment_attachment, Chem.BondType.SINGLE)

        # Remove the dummy atom if present
        if has_dummy:
            # Find dummy atom index (it's now in the combined mol)
            dummy_idx = None
            for atom in rw_mol.GetAtoms():
                if atom.GetAtomicNum() == 0 and atom.GetIdx() >= num_mol1_atoms:
                    dummy_idx = atom.GetIdx()
                    break
            if dummy_idx is not None:
                rw_mol.RemoveAtom(dummy_idx)

        try:
            Chem.SanitizeMol(rw_mol)
            result = Chem.MolToSmiles(rw_mol)
            if result == state:
                logger.warning("Fragment attachment produced no change: state=%s fragment=%s", state, fragment_smiles)
            return result
        except Exception as exc:
            logger.debug("Fragment attachment failed: state=%s fragment=%s error=%s", state, fragment_smiles, exc)
            return state

    def get_fragment_summary(self) -> str:
        """Return a summary of available fragments by category."""
        lines = ["Fragment Vocabulary Summary:", "─" * 50]
        for category, fragments in FRAGMENT_LIBRARY.items():
            lines.append(f"\n{category.upper()} ({len(fragments)} fragments):")
            for smi, name in fragments:
                lines.append(f"  {smi:20s} → {name}")
        return "\n".join(lines)

    def _dummy_reward(self, state: str) -> float:
        """Placeholder reward; the real reward is computed by MCTSAgent via oracle."""
        mol = Chem.MolFromSmiles(state)
        if mol is None:
            return 0.0
        # Simple heuristic: prefer larger molecules (more fragments attached)
        # up to a reasonable size, then plateau
        num_atoms = mol.GetNumAtoms()
        if num_atoms <= 5:
            return float(num_atoms) / 10.0
        elif num_atoms <= 20:
            return 0.5
        else:
            return 0.3  # decreasing reward for overly large molecules

    def _is_terminal(self, state: str) -> bool:
        """Check if the molecule is in a terminal state.

        Terminal if: no available valence sites remain on the scaffold,
        or the molecule is too large.
        """
        mol = Chem.MolFromSmiles(state)
        if mol is None:
            return True
        if mol.GetNumAtoms() > 50:
            return True
        # Check if any atom has available valence
        for atom in mol.GetAtoms():
            try:
                if atom.GetValence(ValenceType.IMPLICIT) > 0:
                    return False
            except Exception:
                pass
        return True


if __name__ == "__main__":
    # Quick test
    env = MolecularEnv(initial_smiles="C", max_steps=5, fragment_set="all",
                       randomize_attachment=True)
    env.reset()
    print(env.get_fragment_summary())
    print("\n--- Testing fragment attachments ---")
    vocab = env.fragment_vocab
    state = env.state
    print(f"Initial: {state}")
    for i, fragment in enumerate(vocab[:10]):
        state, reward, done, info = env.step(fragment)
        name = info.get("fragment_name", "unknown")
        print(f"  + {name:15s} ({fragment:20s}) → {state:30s} reward={reward:.3f} done={done}")
        if done:
            break
    print(f"\nTotal fragments in vocabulary: {len(vocab)}")
    print(f"Categories: {list(FRAGMENT_LIBRARY.keys())}")
