import numpy as np
from rdkit import Chem
from rdkit.Chem import Draw
from PIL.Image import Image
# Use local processing functions instead of external quantum_molecular_encodings package
from .processing import find_rs_stereoisomers, find_ze_conformers

AVERAGE_BOND_LENGTHS: dict[tuple[int, int, Chem.BondType], float] = {
    # ── H (1) bonds ────────────────────────────────────────────────────────
    (1,  6, Chem.BondType.SINGLE):   1.09,   # H-C
    (1,  7, Chem.BondType.SINGLE):   1.01,   # H-N
    (1,  8, Chem.BondType.SINGLE):   0.96,   # H-O
    (1, 16, Chem.BondType.SINGLE):   1.34,   # H-S
    # ── C-C (6,6) ──────────────────────────────────────────────────────────
    (6,  6, Chem.BondType.SINGLE):   1.54,
    (6,  6, Chem.BondType.DOUBLE):   1.34,
    (6,  6, Chem.BondType.TRIPLE):   1.20,
    (6,  6, Chem.BondType.AROMATIC): 1.41,
    # ── C-N (6,7) ──────────────────────────────────────────────────────────
    (6,  7, Chem.BondType.SINGLE):   1.47,
    (6,  7, Chem.BondType.DOUBLE):   1.25,
    (6,  7, Chem.BondType.TRIPLE):   1.15,
    (6,  7, Chem.BondType.AROMATIC): 1.35,
    # ── C-O (6,8) ──────────────────────────────────────────────────────────
    (6,  8, Chem.BondType.SINGLE):   1.43,
    (6,  8, Chem.BondType.DOUBLE):   1.23,
    (6,  8, Chem.BondType.TRIPLE):   1.13,
    (6,  8, Chem.BondType.AROMATIC): 1.38,
    # ── C-F (6,9) ──────────────────────────────────────────────────────────
    (6,  9, Chem.BondType.SINGLE):   1.35,   # C-F
    # ── C-Si (6,14) ────────────────────────────────────────────────────────
    (6, 14, Chem.BondType.SINGLE):   1.87,   # C-Si
    # ── C-P (6,15) ─────────────────────────────────────────────────────────
    (6, 15, Chem.BondType.SINGLE):   1.84,   # C-P
    (6, 15, Chem.BondType.DOUBLE):   1.67,   # C=P
    (6, 15, Chem.BondType.TRIPLE):   1.54,   # C≡P
    # ── C-S (6,16) ─────────────────────────────────────────────────────────
    (6, 16, Chem.BondType.SINGLE):   1.81,
    (6, 16, Chem.BondType.DOUBLE):   1.60,
    (6, 16, Chem.BondType.TRIPLE):   1.56,
    (6, 16, Chem.BondType.AROMATIC): 1.70,
    # ── C-Cl (6,17) ────────────────────────────────────────────────────────
    (6, 17, Chem.BondType.SINGLE):   1.77,   # C-Cl
    # ── C-Br (6,35) ────────────────────────────────────────────────────────
    (6, 35, Chem.BondType.SINGLE):   1.94,   # C-Br
    # ── C-I (6,53) ─────────────────────────────────────────────────────────
    (6, 53, Chem.BondType.SINGLE):   2.14,   # C-I
    # ── B (5) bonds ────────────────────────────────────────────────────────
    (5,  6, Chem.BondType.SINGLE):   1.56,   # B-C
    (5,  6, Chem.BondType.DOUBLE):   1.46,   # B=C
    (5,  6, Chem.BondType.TRIPLE):   1.38,
    (5,  6, Chem.BondType.AROMATIC): 1.50,
    (5,  7, Chem.BondType.SINGLE):   1.54,   # B-N
    (5,  7, Chem.BondType.DOUBLE):   1.43,
    (5,  7, Chem.BondType.AROMATIC): 1.48,
    (5,  8, Chem.BondType.SINGLE):   1.48,   # B-O
    (5, 17, Chem.BondType.SINGLE):   1.75,   # B-Cl
    # ── N-N (7,7) ──────────────────────────────────────────────────────────
    (7,  7, Chem.BondType.SINGLE):   1.47,
    (7,  7, Chem.BondType.DOUBLE):   1.24,
    (7,  7, Chem.BondType.TRIPLE):   1.10,
    (7,  7, Chem.BondType.AROMATIC): 1.36,
    # ── N-O (7,8) ──────────────────────────────────────────────────────────
    (7,  8, Chem.BondType.SINGLE):   1.44,
    (7,  8, Chem.BondType.DOUBLE):   1.20,
    (7,  8, Chem.BondType.AROMATIC): 1.32,
    # ── N-P (7,15) ─────────────────────────────────────────────────────────
    (7, 15, Chem.BondType.SINGLE):   1.77,
    (7, 15, Chem.BondType.DOUBLE):   1.63,
    (7, 15, Chem.BondType.AROMATIC): 1.70,
    # ── N-S (7,16) ─────────────────────────────────────────────────────────
    (7, 16, Chem.BondType.SINGLE):   1.63,   # N-S (sulfonamide)
    (7, 16, Chem.BondType.DOUBLE):   1.57,   # N=S
    (7, 16, Chem.BondType.AROMATIC): 1.60,
    # ── N-Cl (7,17) ────────────────────────────────────────────────────────
    (7, 17, Chem.BondType.SINGLE):   1.75,
    # ── N-Br (7,35) ────────────────────────────────────────────────────────
    (7, 35, Chem.BondType.SINGLE):   1.88,
    # ── O-O (8,8) ──────────────────────────────────────────────────────────
    (8,  8, Chem.BondType.SINGLE):   1.48,
    (8,  8, Chem.BondType.DOUBLE):   1.21,
    (8,  8, Chem.BondType.AROMATIC): 1.35,
    # ── O-S / S=O (8,16 same as 16,8) ─────────────────────────────────────
    (8, 16, Chem.BondType.SINGLE):   1.58,
    (8, 16, Chem.BondType.DOUBLE):   1.43,   # S=O (sulfonyl / sulfoxide)
    (8, 16, Chem.BondType.AROMATIC): 1.50,
    # ── O-Cl (8,17) ────────────────────────────────────────────────────────
    (8, 17, Chem.BondType.SINGLE):   1.69,
    # ── S-S (16,16) ────────────────────────────────────────────────────────
    (16, 16, Chem.BondType.SINGLE):  2.05,
    # ── S-O (16,8) — kept for backwards compat; same as (8,16) above ───────
    (16,  8, Chem.BondType.SINGLE):  1.58,
    (16,  8, Chem.BondType.DOUBLE):  1.43,
    (16,  8, Chem.BondType.AROMATIC):1.50,
    # ── S-Cl (16,17) ───────────────────────────────────────────────────────
    (16, 17, Chem.BondType.SINGLE):  2.07,
    # ── P=O (8,15) ─────────────────────────────────────────────────────────
    (8, 15, Chem.BondType.DOUBLE):   1.48,   # P=O
    (8, 15, Chem.BondType.SINGLE):   1.57,   # P-O
    # ── P-Cl (15,17) ───────────────────────────────────────────────────────
    (15, 17, Chem.BondType.SINGLE):  2.02,   # P-Cl
    # ── B-B (5,5) ──────────────────────────────────────────────────────────
    (5,  5, Chem.BondType.SINGLE):   1.72,   # B-B
    (5,  5, Chem.BondType.DOUBLE):   1.56,   # B=B (diborane-type)
    # ── C-P aromatic (6,15) ────────────────────────────────────────────────
    (6, 15, Chem.BondType.AROMATIC): 1.75,   # C-P aromatic (phosphole)
}

BOND_ORDER: dict[Chem.BondType, float] = {
    Chem.BondType.SINGLE: 1,
    Chem.BondType.DOUBLE: 2,
    Chem.BondType.TRIPLE: 3,
    Chem.BondType.AROMATIC: 1.5,
    # Add more bonds as needed
}


class BaseMatrix:
    def __init__(self, bond_coupling: float = 1.0):
        """
        Base class for computing molecular matrices.

        Parameters:
        - bond_coupling (float): A factor to scale the bond interaction values.
        """
        self.bond_coupling = bond_coupling
        self.molecule = None

    def compute(self, smiles: str, add_hydrogens: bool = False, exponent: float = 3.0) -> np.ndarray:
        """
        Computes the molecular matrix for a given molecule specified by a SMILES string.

        Parameters:
        - smiles (str): The SMILES string representing the molecule.
        - add_hydrogens (bool): Whether to add hydrogen atoms to the molecule.

        Returns:
        - np.ndarray: The molecular matrix of the molecule.
        """
        molecule = Chem.MolFromSmiles(smiles)
        if add_hydrogens:
            molecule = Chem.AddHs(molecule)

        self.molecule = molecule  # Save the RDKit molecule object

        atomic_numbers = np.array([atom.GetAtomicNum() for atom in molecule.GetAtoms()])
        num_atoms = len(atomic_numbers)
        matrix = np.zeros((num_atoms, num_atoms))

        # Precompute diagonal elements
        diagonal_elements = 0.5 * atomic_numbers ** exponent

        # Find stereoisomers
        isomers = find_rs_stereoisomers(smiles)
        s_stereoisomers = isomers['S'] # if 'S' isomer, multiply by -1.
        
        # r_stereoisomers = isomers['R'] # if 'R' isomer, multiply by 1.

        # u_stereoisomers = isomers['U'] # unasigned stereoisomers
        
        for idx in s_stereoisomers:
            #print(f"S isomer at {idx}")
            diagonal_elements[idx] *= -1
        
        np.fill_diagonal(matrix, diagonal_elements)

        # Fill the matrix based on bond distances or bond orders
        matrix = self._fill_matrix(molecule, smiles, atomic_numbers, matrix)

        return matrix

    def _fill_matrix(self, molecule: Chem.Mol, smiles: str, atomic_numbers: np.ndarray,
                     matrix: np.ndarray) -> np.ndarray:
        """
        Abstract method to fill the matrix based on specific criteria.
        Must be implemented by subclasses.

        Parameters:
        - molecule (Chem.Mol): The RDKit molecule object.
        - atomic_numbers (np.ndarray): Array of atomic numbers.
        - matrix (np.ndarray): The matrix to be filled.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def draw_molecule(self, file_path: str = None) -> Image:
        """
        Draws the image of the molecule and optionally saves it to a file.

        Parameters:
        - file_path (str, optional): Path to save the image file. If None, the image is displayed.

        Returns:
        - PIL.Image.Image: Image of the molecule.
        """
        if self.molecule is None:
            raise ValueError("Molecule not initialized. Run `compute` method first.")

        # Draw the molecule image
        image = Draw.MolToImage(self.molecule)

        if file_path:
            image.save(file_path)

        return image


class CoulombMatrix(BaseMatrix):
    def __init__(self, bond_coupling: float = 1.0):
        """
        Class for computing Coulomb matrices using average bond lengths.

        Parameters:
        - bond_coupling (float): A factor to scale the bond interaction values.

        Example Usage:

        .. code-block:: python

            # Initialize CoulombMatrix instance
            cm = CoulombMatrix()

            # Compute Coulomb matrix for a water molecule (H2O)
            smiles = "O"
            matrix = cm.compute(smiles, add_hydrogens=True)

            print(matrix)

        """
        super().__init__(bond_coupling)
        self.average_bond_lengths: dict[tuple[int, int, Chem.BondType], float] = (
            AVERAGE_BOND_LENGTHS)

    def _fill_matrix(self, molecule: Chem.Mol, smiles: str, atomic_numbers: np.ndarray,
                     matrix: np.ndarray) -> np.ndarray:
        """
        Fills the matrix using average bond lengths.

        Parameters:
        - molecule (Chem.Mol): The RDKit molecule object.
        - smiles (str): The SMILES string of the molecule.
        - atomic_numbers (np.ndarray): Array of atomic numbers.
        - matrix (np.ndarray): The matrix to be filled.
        """
        for bond in molecule.GetBonds():
            i = bond.GetBeginAtomIdx()
            j = bond.GetEndAtomIdx()
            bond_type = bond.GetBondType()
            atom_pair = (
                min(atomic_numbers[i], atomic_numbers[j]),
                max(atomic_numbers[i], atomic_numbers[j]),
                bond_type
            )
            distance = self.average_bond_lengths.get(atom_pair)

            if distance is None:
                raise ValueError(f"Bond length not defined for atom pair: {atom_pair}")

            matrix[i, j] = (atomic_numbers[i] * atomic_numbers[j] / distance) * self.bond_coupling
            matrix[j, i] = matrix[i, j]

        return matrix


class BondOrderMatrix(BaseMatrix):
    def __init__(self, bond_coupling: float = 1.0):
        """
        Class for computing matrices using bond orders.

        Parameters:
        - bond_coupling (float): A factor to scale the bond interaction values.

        Example Usage:

        .. code-block:: python

            # Initialize BondOrderMatrix instance
            bom = BondOrderMatrix()

            # Compute BondOrder matrix for benzene (C6H6)
            smiles = "c1ccccc1"
            matrix = bom.compute(smiles, add_hydrogens=True)

            print(matrix)

        """
        super().__init__(bond_coupling)
        self.bond_orders: dict[Chem.BondType, float] = BOND_ORDER

    def _fill_matrix(self, molecule: Chem.Mol, smiles: str, atomic_numbers: np.ndarray,
                     matrix: np.ndarray) -> np.ndarray:
        """
        Fills the matrix using bond orders.

        Parameters:
        - molecule (Chem.Mol): The RDKit molecule object.
        - smiles (str): The SMILES string of the molecule.
        - atomic_numbers (np.ndarray): Array of atomic numbers.
        - matrix (np.ndarray): The matrix to be filled.
        """

        z_conformers = find_ze_conformers(smiles)['Z']
        
        for bond in molecule.GetBonds():
            i = bond.GetBeginAtomIdx()
            j = bond.GetEndAtomIdx()
            bond_type = bond.GetBondType()
            bond_order = self.bond_orders.get(bond_type)

            if bond_order == 2 and (i,j) in z_conformers:
                bond_order = -1 * bond_order

            if bond_order is None:
                raise ValueError(f"Bond order not defined for bond type: {bond_type}")

            matrix[i, j] = (atomic_numbers[i] * atomic_numbers[j] / bond_order) * self.bond_coupling
            matrix[j, i] = matrix[i, j]

        return matrix
