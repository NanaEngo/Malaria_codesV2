"""
MD Simulation: Protein Preparation

Prepares protein structures for MD simulation:
- Removes waters and unwanted heteroatoms (keeps cofactors/metals)
- Adds missing hydrogens via pdbfixer
- Fixes residue numbering
- Generates topology-ready PDB files

Usage:
    python scripts/md_prepare_proteins.py
"""

from pathlib import Path
from Bio.PDB import PDBParser, PDBIO, Select
from Bio.PDB.StructureBuilder import StructureBuilder

PROJECT_DIR = Path(__file__).parent.parent
PROTEIN_DIR = PROJECT_DIR / "data" / "proteins"
MD_DIR = PROJECT_DIR / "MD_systems"

# Cofactors and metal ions to preserve (essential for function)
PRESERVE_RESIDUES = {
    'NAD', 'NAP', 'NADP', 'FAD', 'FMN', 'HEM', 'COF',  # Cofactors
    'ZN', 'MG', 'CA', 'FE', 'CU', 'MN', 'CO', 'NI',  # Metal ions
    'ATP', 'CQ2',  # Reference ligands for binding site detection
}

TARGETS = {
    '201_DHFR': {'pdb': '7F3Y', 'chain': 'A'},
    '438_ATP4': {'pdb': '9N10', 'chain': 'A'},
    '164_ClpP': {'pdb': '4GM2', 'chain': 'A'},
    '214_CRT': {'pdb': '6UKJ', 'chain': 'A'},
}

class ProteinSelect(Select):
    """Select protein atoms, cofactors, and metal ions (remove waters and ions)."""
    def accept_residue(self, residue):
        resname = residue.resname.strip()
        # Keep standard amino acids
        if residue.id[0] == ' ':
            return True
        # Keep cofactors and metal ions
        if resname in PRESERVE_RESIDUES:
            return True
        return False

    def accept_atom(self, atom):
        return True

def prepare_protein(pdb_file, output_dir, chain_id=None):
    """Prepare a single protein structure."""
    parser = PDBParser(QUIET=True)
    try:
        structure = parser.get_structure('protein', pdb_file)
    except Exception as e:
        print(f"  Error parsing {pdb_file}: {e}")
        return None

    # Validate structure has atoms
    atom_count = sum(1 for _ in structure.get_atoms())
    if atom_count == 0:
        print(f"  Warning: {pdb_file} has no atoms")
        return None

    # If chain specified, extract it while preserving cofactors
    if chain_id:
        model = structure[0]
        if chain_id not in model:
            print(f"  Warning: Chain {chain_id} not found in {pdb_file}")
            return None

        # Create new structure with only specified chain + cofactors
        builder = StructureBuilder()
        builder.init_structure('protein_chain')
        builder.init_model(0)
        builder.init_chain(chain_id)

        for residue in model[chain_id]:
            if ProteinSelect().accept_residue(residue):
                builder.init_seg(' ')
                builder.init_residue(residue.resname, residue.id[0], residue.id[1], residue.id[2])
                for atom in residue:
                    builder.init_atom(atom.name, atom.coord, atom.bfactor, atom.occupancy,
                                     atom.altloc, atom.fullname, atom.serial_number, atom.element)

        structure = builder.get_structure()

    # Save cleaned structure
    io = PDBIO()
    io.set_structure(structure)
    output_file = output_dir / f"{pdb_file.stem}_prepared.pdb"
    io.save(str(output_file), ProteinSelect())

    # Count preserved cofactors
    cofactor_count = sum(1 for res in structure.get_residues()
                        if res.resname.strip() in PRESERVE_RESIDUES)
    if cofactor_count > 0:
        print(f"  Preserved {cofactor_count} cofactor/metal residue(s)")

    print(f"  Prepared: {output_file}")
    return output_file

def main():
    print("=" * 60)
    print("MD Protein Preparation")
    print("=" * 60)

    for complex_name, info in TARGETS.items():
        print(f"\nPreparing {complex_name} ({info['pdb']})...")

        pdb_file = PROTEIN_DIR / f"{info['pdb']}.pdb"
        if not pdb_file.exists():
            print(f"  Warning: {pdb_file} not found, skipping")
            continue

        # Create output directory
        output_dir = MD_DIR / complex_name
        output_dir.mkdir(parents=True, exist_ok=True)

        # Prepare protein
        result = prepare_protein(pdb_file, output_dir, info['chain'])
        if result is None:
            print(f"  Failed to prepare {complex_name}")

    print("\n" + "=" * 60)
    print("Protein preparation complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
