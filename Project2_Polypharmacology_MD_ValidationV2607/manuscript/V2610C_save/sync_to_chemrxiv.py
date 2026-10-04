#!/usr/bin/env python3
"""
Sync updated content from JCIM version to ChemRxiv version.
Preserves ChemRxiv preamble and formatting while updating main content.
"""

import re
from pathlib import Path

def extract_main_content(jcim_file):
    """Extract content from \\begin{abstract} to \\bibliography from JCIM file."""
    with open(jcim_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find abstract start
    abstract_start = content.find(r'\begin{abstract}')
    if abstract_start == -1:
        raise ValueError("Could not find \\begin{abstract} in JCIM file")
    
    # Find bibliography
    bib_match = re.search(r'\\bibliography\{[^}]+\}', content)
    if not bib_match:
        raise ValueError("Could not find \\bibliography in JCIM file")
    
    bib_end = bib_match.end()
    
    return content[abstract_start:bib_end]

def replace_chemrxiv_content(chemrxiv_file, new_content):
    """Replace content between abstract and bibliography in ChemRxiv file."""
    with open(chemrxiv_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find positions
    abstract_start = content.find(r'\begin{abstract}')
    bib_match = re.search(r'\\bibliography\{[^}]+\}', content)
    
    if abstract_start == -1 or not bib_match:
        raise ValueError("Could not find content boundaries in ChemRxiv file")
    
    bib_end = bib_match.end()
    
    # Preserve preamble and end matter
    preamble = content[:abstract_start]
    end_matter = content[bib_end:]
    
    # Reconstruct
    new_file_content = preamble + new_content + end_matter
    
    # Write back
    with open(chemrxiv_file, 'w', encoding='utf-8') as f:
        f.write(new_file_content)
    
    return new_file_content

def main():
    base_dir = Path(__file__).parent
    jcim_file = base_dir / "Polypharmacology_MD_Validation_V2609C.tex"
    chemrxiv_file = base_dir / "ChemRxiv_version" / "P2_MD_Validation_ChemRxiv_Main.tex"
    
    print(f"Reading JCIM version: {jcim_file}")
    jcim_content = extract_main_content(jcim_file)
    print(f"  Extracted {len(jcim_content)} characters")
    
    print(f"\nUpdating ChemRxiv version: {chemrxiv_file}")
    new_content = replace_chemrxiv_content(chemrxiv_file, jcim_content)
    print(f"  New file has {len(new_content)} characters")
    
    print("\n✓ Content sync complete")
    print("\nKey changes transferred:")
    print("  - Central Finding paragraph in Results section")
    print("  - Labeled 'Estimand Divergence' subsection")
    print("  - Updated cross-references to SI Table S16")
    print("  - All latest manuscript improvements")

if __name__ == "__main__":
    main()
