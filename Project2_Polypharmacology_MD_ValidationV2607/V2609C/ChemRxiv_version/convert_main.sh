#!/bin/bash
# Convert P2 V2609C main manuscript from JCIM achemso to article class

FILE="P2_MD_Validation_ChemRxiv_Main.tex"

echo "Converting $FILE to article class format..."

# 1. Replace documentclass
sed -i 's/\\documentclass\[journal=jcisd8,manuscript=article,layout=traditional\]{achemso}/\\documentclass[11pt,a4paper]{article}\n\\usepackage[margin=1in]{geometry}/' "$FILE"

# 2. Remove achemso comments (multi-line)
sed -i '/^% journal=jcisd8/,/separately -- achemso already requires it internally under this option\)\./d' "$FILE"

# 3. Add natbib before cleveref
sed -i '/% Cross-referencing - load after achemso\/hyperref/i \\usepackage[numbers,sort\&compress]{natbib}' "$FILE"

# 4. Remove tocentry environment
sed -i '/% GRAPHICAL TABLE OF CONTENTS/,/\\end{tocentry}/d' "$FILE"

# 5. Remove \maketitle, \emergencystretch, \sloppy
sed -i '/\\maketitle/d' "$FILE"
sed -i '/\\emergencystretch/d' "$FILE"
sed -i '/\\sloppy/d' "$FILE"

# 6. Update SM cross-reference filename
sed -i 's/\\externaldocument\[SM-\]{Polypharmacology_MD_Validation_SM_V2609C}/\\externaldocument[SM-]{P2_MD_Validation_ChemRxiv_SM}/' "$FILE"

# 7. Add bibliography style
sed -i 's/\\bibliography{\(.*\)}/\\bibliographystyle{unsrtnat}\n\\bibliography{\1}/' "$FILE"

# 8. Convert author block - this needs to be done more carefully
# We'll add ORCID icon definition after tikz
sed -i '/\\usepackage{tikz}/a \\n% ORCID icon for article class\n\\providecommand{\\textorcid}{%\n\t\\begin{tikzpicture}[baseline=0.0ex,line width=0.6,scale=0.65]\n\t\t\\fill[rounded corners=0.5,fill=green!60!black,draw=green!50!black] (0,0) circle (0.65ex);\n\t\t\\node[white,font=\\bfseries\\sffamily\\tiny] at (0,0) {iD};\n\t\\end{tikzpicture}%\n}' "$FILE"

echo "✅ Main file converted!"
echo "⚠️  Manual steps still needed:"
echo "   1. Convert \\author{} blocks to article class format"
echo "   2. Add \\date{} after \\title{}"
echo "   3. Create manual title page with author affiliations"
echo "   4. Remove \\keywords{} (not standard in article class)"
echo "   5. Add abstract manually after title page"
