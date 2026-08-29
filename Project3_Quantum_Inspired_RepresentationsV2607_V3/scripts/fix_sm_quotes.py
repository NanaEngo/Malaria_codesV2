#!/usr/bin/env python3
"""Fix the escaped quotes in SM SOTA benchmark footnote."""
import pathlib

sm = pathlib.Path("/home/nanaengo/Malaria_codesV2/Project3_Quantum_Inspired_RepresentationsV2607/manuscript/LaTeX/Paper3_Quantum_Inspired_SM_V2607.tex")
txt = sm.read_text()

# Fix the problematic escaped quotes
old = r'\texttt{\\"balanced\\"}'
new = r"\texttt{balanced}"
txt = txt.replace(old, new)

# Also check for other problematic escaped quotes
old2 = r'\texttt{class\_weight} = \texttt{\\"balanced\\"}'
new2 = r"\texttt{class\_weight=balanced}"
txt = txt.replace(old2, new2)

sm.write_text(txt)
print("Fixed escaped quotes in SM file")
