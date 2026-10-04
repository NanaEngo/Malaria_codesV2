#!/bin/bash
# Quick verification script for V2 grid citation updates
# P2 V2609C - 17 September 2026

echo "======================================"
echo "P2 V2609C: V2 Grid Citation Verification"
echo "======================================"
echo ""

cd "$(dirname "$0")"

echo "1. Checking for Temgoua2026 citations in main manuscript..."
MAIN_CITES=$(grep -c "citep{Temgoua2026}" Polypharmacology_MD_Validation_V2609C.tex 2>/dev/null || echo "0")
echo "   Found: $MAIN_CITES citation(s)"

echo ""
echo "2. Checking for Temgoua2026 in Table S1..."
TABLE_CITES=$(grep -c "citep{Temgoua2026}" Table_S0_Docking_Validation.tex 2>/dev/null || echo "0")
echo "   Found: $TABLE_CITES citation(s)"

echo ""
echo "3. Verifying Temgoua2026 in bibliography..."
if grep -q "@Article{Temgoua2026" Project2_Polypharmacology_MD_Validation.bib 2>/dev/null; then
    echo "   ✅ Temgoua2026 entry found in .bib file"
    grep -A 3 "@Article{Temgoua2026" Project2_Polypharmacology_MD_Validation.bib | head -4
else
    echo "   ❌ Temgoua2026 NOT found in .bib file"
fi

echo ""
echo "4. V2 grid mentions with citations:"
echo ""
grep -n "V2.*Temgoua2026" Polypharmacology_MD_Validation_V2609C.tex 2>/dev/null | cut -c1-100
grep -n "V2.*Temgoua2026" Table_S0_Docking_Validation.tex 2>/dev/null | cut -c1-100

echo ""
echo "======================================"
echo "Summary:"
echo "  Main manuscript citations: $MAIN_CITES (expected: 2)"
echo "  Table S1 citations: $TABLE_CITES (expected: 1)"
echo "  Total: $((MAIN_CITES + TABLE_CITES)) (expected: 3)"
echo "======================================"

if [ $((MAIN_CITES + TABLE_CITES)) -eq 3 ]; then
    echo "✅ All V2 grid citations present"
    exit 0
else
    echo "⚠️  Citation count mismatch"
    exit 1
fi
