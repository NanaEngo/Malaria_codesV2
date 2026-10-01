#!/usr/bin/env python3
"""
Adapt JCAMD Supporting Information to Malaria Journal format
Created: 28 September 2026

Malaria Journal SI requirements:
- No structured abstract needed (SI doesn't have abstract)
- No Abbreviations section needed (only in main manuscript)
- Update cross-references to main manuscript (if any)
- Keep all content otherwise unchanged
"""

import re

def main():
    """Adapt Supporting Information for Malaria Journal"""
    
    # Read source file
    source_path = '../Submission_JCAMD/P1_Integrated_Polypharmacology_RRS_SM_JCAMD.tex'
    print(f"Reading source file: {source_path}")
    
    with open(source_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("Applying Malaria Journal SI adaptations:")
    
    # Update document comment
    print("  1. Updating title comment...")
    content = re.sub(
        r'% Supporting Information.*?\n',
        '% Supporting Information for Malaria Journal\n',
        content
    )
    
    # Update any references to "JCAMD" or "JCIM" in text
    print("  2. Updating journal references...")
    content = re.sub(
        r'\b(JCAMD|JCIM)\b',
        'Malaria Journal',
        content
    )
    
    # Update cross-references to main manuscript sections
    print("  3. Updating cross-references to main manuscript...")
    # These typically reference "Section X.Y of the main text"
    # The section numbering should be preserved, so no changes needed
    # Just verify the pattern exists
    main_text_refs = re.findall(r'Section \d+\.\d+(\.\d+)? of the main text', content)
    print(f"     Found {len(main_text_refs)} cross-references to main text")
    
    # Write output file
    output_path = 'P1_Integrated_Polypharmacology_RRS_SM_MalJ.tex'
    print(f"\nWriting adapted Supporting Information: {output_path}")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✓ Malaria Journal SI adaptation complete!")
    print("\nKey changes applied:")
    print("  - Updated document comment to Malaria Journal")
    print(f"  - Preserved {len(main_text_refs)} cross-references to main text sections")
    print("  - All content, tables, figures, and sections preserved")
    print("\nNext steps:")
    print("  1. Compile SI: pdflatex P1_Integrated_Polypharmacology_RRS_SM_MalJ.tex (2x)")
    print("  2. Verify all figures and tables compile correctly")
    print("  3. Check that all cross-references to main text are accurate")
    print("  4. Final package ready for submission")


if __name__ == '__main__':
    main()
