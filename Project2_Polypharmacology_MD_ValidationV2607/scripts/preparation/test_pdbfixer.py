#!/usr/bin/env python
"""
Quick test script to verify the PDBFixer missingResidues fix
"""

from pdbfixer import PDBFixer

# Test with existing file
pdb_file = "protein_prep/7F3Y_raw.pdb"

print("Testing PDBFixer missingResidues format...")
print("=" * 60)

fixer = PDBFixer(filename=pdb_file)

# Keep only chain A
chains_to_remove = []
for chain in fixer.topology.chains():
    if chain.id != "A":
        chains_to_remove.append(chain.index)

if chains_to_remove:
    fixer.removeChains(chainIds=chains_to_remove)
    print(f"Removed {len(chains_to_remove)} chain(s)")

# Find missing residues
fixer.findMissingResidues()

print(f"\nmissingResidues type: {type(fixer.missingResidues)}")
print(f"Number of entries: {len(fixer.missingResidues)}")

if fixer.missingResidues:
    print("\nInspecting missingResidues structure:")
    for key, value in fixer.missingResidues.items():
        print(f"  Key: {key} (type: {type(key)})")
        print(f"  Value: {value[:3] if len(value) > 3 else value}... (length: {len(value)})")
        print()

print("✓ Test complete")
