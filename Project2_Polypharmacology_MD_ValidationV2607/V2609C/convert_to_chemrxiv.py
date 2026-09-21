#!/usr/bin/env python3
"""
Convert P2 V2609C JCIM-formatted manuscripts to ChemRxiv article class format.
Based on P1 Submission_DD conversion template.
"""

import re
import shutil
from pathlib import Path

def convert_achemso_to_article(input_file, output_file, is_si=False):
    """Convert achemso class document to article class."""
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace documentclass
    if is_si:
        content = re.sub(
            r'\\documentclass\[journal=jcisd8,manuscript=suppinfo,layout=traditional\]\{achemso\}',
            r'\\documentclass[11pt,a4paper]{article}',
            content
        )
    else:
        content = re.sub(
            r'\\documentclass\[journal=jcisd8,manuscript=article,layout=traditional\]\{achemso\}',
            r'\\documentclass[11pt,a4paper]{article}',
            content
        )
    
    # Add geometry package after documentclass
    content = re.sub(
        r'(\\documentclass\[11pt,a4paper\]\{article\})',
        r'\1\n\n\\usepackage[margin=1in]{geometry}',
        content
    )
    
    # Remove achemso-specific comments
    content = re.sub(
        r'% journal=jcisd8.*?\n.*?numbered-superscript citation style.*?\n.*?separately -- achemso already requires it internally under this option\)\.',
        '',
        content,
        flags=re.DOTALL
    )
    
    # Add ORCID icon definition for article class (from P1 template)
    orcid_definition = r"""
% ORCID icon defined locally for the article class
\providecommand{\textorcid}{%
	\begin{tikzpicture}[baseline=0.0ex,line width=0.6,scale=0.65]
		\fill[rounded corners=0.5,fill=green!60!black,draw=green!50!black] (0,0) circle (0.65ex);
		\node[white,font=\bfseries\sffamily\tiny] at (0,0) {iD};
	\end{tikzpicture}%
}
\RequirePackage{tikz}"""
    
    # Insert ORCID definition after first tikz package if not already there
    if 'providecommand{\\textorcid}' not in content:
        content = re.sub(
            r'(\\usepackage\{tikz\})',
            r'\1' + orcid_definition,
            content,
            count=1
        )
    
    # Update citation package from achemso.bst to natbib
    content = re.sub(
        r'% Cross-referencing - load after achemso/hyperref',
        r'\\usepackage[numbers,sort&compress]{natbib}\n% Cross-referencing',
        content
    )
    
    # Remove tocentry environment (JCIM-specific)
    content = re.sub(
        r'% ============================================================================\n% GRAPHICAL TABLE OF CONTENTS.*?\n% ============================================================================\n\\begin\{tocentry\}.*?\\end\{tocentry\}\n\n',
        '',
        content,
        flags=re.DOTALL
    )
    
    # Convert author block from achemso to article class
    if not is_si:
        # Extract title
        title_match = re.search(r'\\title\{(.+?)\}', content, re.DOTALL)
        title = title_match.group(1) if title_match else "Untitled"
        
        # Extract authors and affiliations
        author_block = extract_author_block(content)
        
        # Replace the entire author section
        content = re.sub(
            r'\\title\{.*?\}.*?\\keywords\{.*?\}',
            create_article_title_block(title, author_block),
            content,
            flags=re.DOTALL
        )
    
    # Remove \maketitle if it exists (we'll add manual title formatting)
    content = re.sub(r'\\maketitle\n', '', content)
    
    # Remove \emergencystretch and \sloppy
    content = re.sub(r'\\emergencystretch=.*?\n', '', content)
    content = re.sub(r'\\sloppy\n', '', content)
    
    # Update bibliography style
    content = re.sub(
        r'\\bibliography\{(.*?)\}',
        r'\\bibliographystyle{unsrtnat}\n\\bibliography{\1}',
        content
    )
    
    # For SI: update cross-reference to main document
    if is_si:
        content = re.sub(
            r'\\externaldocument\[MAIN-\]\{Polypharmacology_MD_Validation_V2609C\}',
            r'\\externaldocument[MAIN-]{P2_MD_Validation_ChemRxiv_Main}',
            content
        )
    else:
        # For main: update cross-reference to SI
        content = re.sub(
            r'\\externaldocument\[SM-\]\{Polypharmacology_MD_Validation_SM_V2609C\}',
            r'\\externaldocument[SM-]{P2_MD_Validation_ChemRxiv_SM}',
            content
        )
    
    # Add date suppression
    if '\\date{}' not in content and not is_si:
        content = re.sub(
            r'(\\title\{.*?\})',
            r'\1\n\n\\date{}',
            content,
            flags=re.DOTALL
        )
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Converted: {input_file} → {output_file}")

def extract_author_block(content):
    """Extract author information from achemso format."""
    authors = []
    
    # Find all author entries
    author_pattern = r'\\author\{(.*?)\}.*?\\affiliation\[.*?\]\{(.*?)\}'
    for match in re.finditer(author_pattern, content, re.DOTALL):
        name = match.group(1).strip()
        affiliation = match.group(2).strip()
        
        # Check if this is corresponding author
        email_match = re.search(r'\\email\{(.*?)\}', content)
        email = email_match.group(1) if email_match and name in content[:email_match.start()] else None
        
        authors.append({
            'name': name,
            'affiliation': affiliation,
            'email': email
        })
    
    # Extract keywords
    keywords_match = re.search(r'\\keywords\{(.*?)\}', content)
    keywords = keywords_match.group(1) if keywords_match else ""
    
    return {'authors': authors, 'keywords': keywords}

def create_article_title_block(title, author_block):
    """Create article-class title block from extracted information."""
    
    # Build author list with ORCID placeholders
    author_list = []
    affiliations = {}
    affil_counter = 1
    
    for author in author_block['authors']:
        # Map affiliation to number
        affil = author['affiliation']
        if affil not in affiliations:
            affiliations[affil] = affil_counter
            affil_counter += 1
        
        affil_num = affiliations[affil]
        
        # Build author string with ORCID icon placeholder
        author_str = f"{author['name']}\\href{{https://orcid.org/XXXX-XXXX-XXXX-XXXX}}{{\\textsuperscript{{\\textorcid}}}}$^{{{affil_num}}}$"
        
        if author['email']:
            author_str += f"\\footnotemark[1]"
        
        author_list.append(author_str)
    
    # Build affiliation list
    affil_lines = []
    for affil, num in sorted(affiliations.items(), key=lambda x: x[1]):
        affil_lines.append(f"{{\\small $^{{{num}}}${affil}}}")
    
    # Build full title block
    title_block = f"""
\\title{{{title}}}

\\date{{}}

\\begin{{document}}
	
{{\\centering\\Large\\bfseries {title}\\par}}
\\vspace{{1em}}
{{\\centering
	{',\n\t'.join(author_list)}\\\\[0.5em]
	{'\\\\'.join(affil_lines)}\\par}}

\\begin{{abstract}}"""
    
    # Add footnote for corresponding author
    abstract_start = "\\begin{abstract}"
    for author in author_block['authors']:
        if author['email']:
            footnote = f"\\footnotetext[1]{{Corresponding author: \\texttt{{{author['email']}}}}}\n\n"
            title_block = title_block.replace(abstract_start, footnote + abstract_start)
            break
    
    return title_block + "\n" + "	% Abstract content continues here"

def main():
    """Main conversion function."""
    
    base_dir = Path("/home/vital/Documents/GitHub/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607/V2609C")
    chemrxiv_dir = base_dir / "ChemRxiv_version"
    
    # Ensure output directory exists
    chemrxiv_dir.mkdir(exist_ok=True)
    
    # Copy Graphics directory if not already there
    graphics_src = base_dir / "Graphics"
    graphics_dst = chemrxiv_dir / "Graphics"
    if graphics_src.exists() and not graphics_dst.exists():
        shutil.copytree(graphics_src, graphics_dst)
        print(f"✅ Copied Graphics directory")
    
    # Copy table files
    table_files = list(base_dir.glob("Table_*.tex"))
    for table_file in table_files:
        shutil.copy(table_file, chemrxiv_dir / table_file.name)
    print(f"✅ Copied {len(table_files)} table files")
    
    # Convert main manuscript
    main_input = base_dir / "Polypharmacology_MD_Validation_V2609C.tex"
    main_output = chemrxiv_dir / "P2_MD_Validation_ChemRxiv_Main.tex"
    convert_achemso_to_article(main_input, main_output, is_si=False)
    
    # Convert SI
    si_input = base_dir / "Polypharmacology_MD_Validation_SM_V2609C.tex"
    si_output = chemrxiv_dir / "P2_MD_Validation_ChemRxiv_SM.tex"
    convert_achemso_to_article(si_input, si_output, is_si=True)
    
    # Copy bibliography file
    bib_file = base_dir / "P2_V2609C_bibliography.bib"
    if bib_file.exists():
        shutil.copy(bib_file, chemrxiv_dir / bib_file.name)
        print(f"✅ Copied bibliography file")
    
    print("\n🎉 Conversion complete!")
    print(f"📁 Output directory: {chemrxiv_dir}")
    print("\n⚠️  Manual steps required:")
    print("1. Update ORCID URLs with actual ORCID IDs")
    print("2. Verify author affiliations and numbering")
    print("3. Check abstract formatting")
    print("4. Verify all cross-references (\\cref, \\ref)")
    print("5. Compile and check for LaTeX errors")
    print("6. Update bibliography file path if needed")

if __name__ == "__main__":
    main()
