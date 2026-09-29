#!/bin/bash
# Populate P2 Zenodo Package
# Created: 17 September 2026
# Purpose: Copy necessary files from project into Zenodo package structure

set -e

PROJECT_ROOT="/home/vital/Documents/GitHub/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607"
PACKAGE_DIR="$PROJECT_ROOT/zenodo_package_P2"

echo "======================================"
echo "Populating P2 Zenodo Package"
echo "======================================"
echo ""

# Create directories if they don't exist
mkdir -p "$PACKAGE_DIR/data"
mkdir -p "$PACKAGE_DIR/results"
mkdir -p "$PACKAGE_DIR/scripts"
mkdir -p "$PACKAGE_DIR/documentation"

echo "1. Copying core datasets to data/..."
cp -v "$PROJECT_ROOT/results/c_rrs_classification.csv" "$PACKAGE_DIR/data/"
cp -v "$PROJECT_ROOT/results/c_pns_ranking.csv" "$PACKAGE_DIR/data/"
cp -v "$PROJECT_ROOT/results/c_acsi_scores.csv" "$PACKAGE_DIR/data/"
cp -v "$PROJECT_ROOT/results/docking_mutants.csv" "$PACKAGE_DIR/data/c_docking_complete.csv"

echo ""
echo "2. Copying MD trajectory metrics..."
if [ -f "$PROJECT_ROOT/results/md_systems/set_c_preparation_20260812_v1/set_c_trajectory_qc_summary.csv" ]; then
    cp -v "$PROJECT_ROOT/results/md_systems/set_c_preparation_20260812_v1/set_c_trajectory_qc_summary.csv" \
       "$PACKAGE_DIR/data/set_c_trajectory_metrics_pilot.csv"
fi

echo ""
echo "3. Copying external docking data..."
if [ -d "$PROJECT_ROOT/results/external_docking_20260827" ]; then
    cp -v "$PROJECT_ROOT/results/external_docking_20260827/external_docking_rrs.csv" \
       "$PACKAGE_DIR/data/external_docking_scores.csv" 2>/dev/null || echo "  (external_docking_rrs.csv not found)"
fi

echo ""
echo "4. Copying analysis results..."
cp -v "$PROJECT_ROOT/results/cross_metric_statistical_audit.csv" "$PACKAGE_DIR/results/"
cp -v "$PROJECT_ROOT/results/pns_imputation_sensitivity.csv" "$PACKAGE_DIR/results/"
cp -v "$PROJECT_ROOT/results/c_acsi_weight_sensitivity.csv" "$PACKAGE_DIR/results/"
cp -v "$PROJECT_ROOT/results/c_rrs_sensitivity.csv" "$PACKAGE_DIR/results/"

echo ""
echo "5. Copying MD analysis results..."
if [ -d "$PROJECT_ROOT/results/md_systems" ]; then
    find "$PROJECT_ROOT/results/md_systems" -name "*.csv" -o -name "*.json" | while read f; do
        filename=$(basename "$f")
        cp -v "$f" "$PACKAGE_DIR/results/" 2>/dev/null || true
    done
fi

echo ""
echo "6. Copying analysis scripts..."
cp -v "$PROJECT_ROOT/scripts/p2_rigorous_audit.py" "$PACKAGE_DIR/scripts/" 2>/dev/null || echo "  (p2_rigorous_audit.py not found)"
cp -v "$PROJECT_ROOT/scripts/set_c_trajectory_qc.py" "$PACKAGE_DIR/scripts/" 2>/dev/null || echo "  (set_c_trajectory_qc.py not found)"
cp -v "$PROJECT_ROOT/scripts/p2_setc_md_rrs.py" "$PACKAGE_DIR/scripts/" 2>/dev/null || echo "  (p2_setc_md_rrs.py not found)"

# Copy environment if it exists
if [ -f "$PROJECT_ROOT/environment.yml" ]; then
    cp -v "$PROJECT_ROOT/environment.yml" "$PACKAGE_DIR/scripts/"
fi

echo ""
echo "7. Copying documentation..."
cp -v "$PROJECT_ROOT/docs/MMGBSA_JUSTIFICATION_ADDENDUM.md" "$PACKAGE_DIR/documentation/" 2>/dev/null || echo "  (MMGBSA_JUSTIFICATION_ADDENDUM.md not found)"
cp -v "$PROJECT_ROOT/P2_DATA_ANALYSIS_REPORT.md" "$PACKAGE_DIR/documentation/" 2>/dev/null || echo "  (P2_DATA_ANALYSIS_REPORT.md not found - checking BMAD)"
cp -v "$PROJECT_ROOT/../BMAD_Q1_DATA_ANALYSIS_REPORT.md" "$PACKAGE_DIR/documentation/P2_DATA_ANALYSIS_REPORT.md" 2>/dev/null || echo "  (BMAD report not found)"

echo ""
echo "8. Generating SHA256 checksums..."
cd "$PACKAGE_DIR"
find . -type f ! -name "sha256sums.txt" ! -name "populate_package.sh" -exec sha256sum {} \; | sort > sha256sums.txt

echo ""
echo "======================================"
echo "Package population complete!"
echo "======================================"
echo ""
echo "Files copied to: $PACKAGE_DIR"
echo ""
echo "Next steps:"
echo "  1. Review copied files"
echo "  2. Verify checksums: sha256sum -c sha256sums.txt"
echo "  3. Update MANIFEST.json with actual file list"
echo "  4. Review UPLOAD_CHECKLIST.md"
echo ""
