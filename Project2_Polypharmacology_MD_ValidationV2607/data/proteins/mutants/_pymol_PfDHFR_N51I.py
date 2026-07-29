
from pymol import cmd
from pymol.wizard import mutagenesis
cmd.load("/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607/data/proteins/7F3Y.pdb", "wt")
cmd.wizard("mutagenesis")
cmd.get_wizard().set_mode("ILE")
cmd.get_wizard().do_select("/A/51/")
cmd.get_wizard().apply()
cmd.set_wizard()
cmd.save("/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607/data/proteins/mutants/7F3Y_N51I.pdb", "wt")
cmd.quit()
