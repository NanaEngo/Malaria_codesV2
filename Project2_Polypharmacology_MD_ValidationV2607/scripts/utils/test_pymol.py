#!/usr/bin/env python3

import sys
from pymol import cmd

try:
    print("Loading PDB file...")
    cmd.load("data/proteins/wild_type/7F3Y.pdb", "wt")
    
    print("Getting chains...")
    chains = cmd.get_chains("wt")
    print(f"Available chains: {chains}")
    
    if "A" not in chains:
        print("ERROR: Chain A not found")
        sys.exit(1)
    
    print("Checking residue 51...")
    selection = "/A/51/"
    atom_count = cmd.count_atoms(selection)
    print(f"Atoms in residue 51: {atom_count}")
    
    if atom_count == 0:
        print("ERROR: Residue 51 not found")
        sys.exit(1)
    
    print("Getting original sequence...")
    try:
        original_resn = cmd.get_fastastr("/A/51/").strip()
        print(f"Original residue at position 51: {original_resn}")
    except Exception as e:
        print(f"Error getting sequence: {e}")
    
    print("Starting mutagenesis...")
    cmd.wizard("mutagenesis")
    wizard = cmd.get_wizard()
    wizard.set_mode("ILE")
    wizard.do_select(selection)
    wizard.apply()
    cmd.set_wizard()
    
    print("Saving structure...")
    cmd.save("data/proteins/mutants/test_7F3Y_N51I.pdb", "wt")
    print("SUCCESS: Mutant saved")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    cmd.quit()