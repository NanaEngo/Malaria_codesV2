"""
Quantum Molecular Structure Encoding (QMSE) Library

Based on Boy et al. (2025), arXiv:2507.20422
"Encoding molecular structures in quantum machine learning"

This is a local copy of the essential components from the quantum-molecular-encodings
library, adapted for use in Project7.
"""

from .matrix import BondOrderMatrix, CoulombMatrix, BaseMatrix
from .supporting_functions import coulomb_matrix, matrix_to_circuit

__all__ = [
    'BondOrderMatrix',
    'CoulombMatrix',
    'BaseMatrix',
    'coulomb_matrix',
    'matrix_to_circuit',
]

__version__ = '1.0.0-p7'
__author__ = 'Boy et al. (2025), adapted for Project7'
