
from pymol import cmd
cmd.load("/home/vital/Documents/GitHub/Malaria_codes/Project2_Polypharmacology_MD_Validation/scripts/data/proteins/7F3Y.pdb", "wt")
cmd.wizard("mutagenesis")
cmd.get_wizard().set_mode("ILE")
cmd.get_wizard().do_select("/A/51/")
cmd.get_wizard().apply()
cmd.set_wizard()
cmd.save("/home/vital/Documents/GitHub/Malaria_codes/Project2_Polypharmacology_MD_Validation/scripts/data/proteins/mutants/7F3Y_N51I.pdb", "wt")
cmd.quit()
