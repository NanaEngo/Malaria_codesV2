#!/bin/bash
# Compilation script for P3 V2609 Springer Nature manuscript
# Location: sn-article-template/COMPILE.sh

set -e

echo "==================================================================="
echo "P3 V2609 Springer Nature Manuscript Compilation"
echo "==================================================================="
echo ""

# Ensure we're in the correct directory
cd "$(dirname "$0")"

# Check if required files exist
if [ ! -f "sn-article.tex" ]; then
    echo "ERROR: sn-article.tex not found!"
    exit 1
fi

if [ ! -f "Bibliography_Paper3.bib" ]; then
    echo "ERROR: Bibliography_Paper3.bib not found!"
    exit 1
fi

if [ ! -f "sn-mathphys-num.bst" ]; then
    echo "Copying bibliography style file..."
    cp bst/sn-mathphys-num.bst .
fi

echo "Step 1/4: First LaTeX pass..."
pdflatex -interaction=nonstopmode sn-article.tex > compile_pass1.log 2>&1
if [ $? -ne 0 ]; then
    echo "ERROR: First LaTeX pass failed. Check compile_pass1.log"
    exit 1
fi
echo "  ✓ Pass 1 complete"

echo "Step 2/4: BibTeX pass..."
bibtex sn-article > compile_bibtex.log 2>&1
if [ $? -ne 0 ]; then
    echo "ERROR: BibTeX pass failed. Check compile_bibtex.log"
    exit 1
fi
echo "  ✓ BibTeX complete"

echo "Step 3/4: Second LaTeX pass..."
pdflatex -interaction=nonstopmode sn-article.tex > compile_pass2.log 2>&1
if [ $? -ne 0 ]; then
    echo "ERROR: Second LaTeX pass failed. Check compile_pass2.log"
    exit 1
fi
echo "  ✓ Pass 2 complete"

echo "Step 4/4: Final LaTeX pass..."
pdflatex -interaction=nonstopmode sn-article.tex > compile_pass3.log 2>&1
if [ $? -ne 0 ]; then
    echo "ERROR: Final LaTeX pass failed. Check compile_pass3.log"
    exit 1
fi
echo "  ✓ Pass 3 complete"

# Check if PDF was generated
if [ -f "sn-article.pdf" ]; then
    PDF_SIZE=$(ls -lh sn-article.pdf | awk '{print $5}')
    PDF_PAGES=$(pdfinfo sn-article.pdf 2>/dev/null | grep "^Pages:" | awk '{print $2}')
    echo ""
    echo "==================================================================="
    echo "SUCCESS: Compilation complete!"
    echo "==================================================================="
    echo "  Output: sn-article.pdf"
    echo "  Size: ${PDF_SIZE}"
    echo "  Pages: ${PDF_PAGES}"
    echo ""
    echo "Next steps:"
    echo "  1. Review CONVERSION_SUMMARY.md for details"
    echo "  2. Open sn-article.pdf to verify content"
    echo "  3. Check for any remaining warnings in compile logs"
    echo ""
else
    echo "ERROR: PDF file was not generated!"
    exit 1
fi

# Optional: Clean up auxiliary files (commented out by default)
# echo "Cleaning up auxiliary files..."
# rm -f *.aux *.log *.out *.toc *.bbl *.blg *.bcf *.run.xml

echo "Compilation script finished successfully."
