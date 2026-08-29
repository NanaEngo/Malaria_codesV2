#!/bin/bash
# P7 Phase 1 Complete Execution Pipeline
# Runs all 5 scripts in sequence for P1 Set A (20 molecules)

set -e  # Exit on error

PROJECT_DIR="/home/vital/Documents/GitHub/Malaria_codesV2/Project7_Quantum_Molecular_Encoding_QML"
cd "$PROJECT_DIR"

echo "======================================================================"
echo "P7 Phase 1: Complete Execution Pipeline"
echo "======================================================================"
echo ""
echo "Dataset: P1 Set A (20 top candidates)"
echo "Method: BondOrderMatrix → BondFeatureMap → UnitaryOverlap"
echo "Validation: Leave-one-out cross-validation"
echo ""
echo "Estimated time: 15-25 minutes"
echo ""
echo "======================================================================"

# Check conda environment
if [[ "$CONDA_DEFAULT_ENV" != "malaria_qml" ]]; then
    echo "ERROR: Conda environment 'malaria_qml' not activated"
    echo "Run: conda activate malaria_qml"
    exit 1
fi

echo ""
echo "Step 1/5: Data Preparation (~1 minute)"
echo "----------------------------------------------------------------------"
python scripts/p7_data_preparation.py --p1-only
echo "✓ Data preparation complete"

echo ""
echo "Step 2/5: Classical Baseline (~5 minutes)"
echo "----------------------------------------------------------------------"
python scripts/p7_baseline_classical.py --p1-set-a
echo "✓ Baseline complete"

echo ""
echo "Step 3/5: Quantum Circuit Generation (~2 minutes)"
echo "----------------------------------------------------------------------"
python scripts/p7_quantum_circuits.py --p1-set-a --method bond_order
echo "✓ Quantum circuits complete"

echo ""
echo "Step 4/5: Quantum Kernel Computation (~5 minutes)"
echo "----------------------------------------------------------------------"
python scripts/p7_quantum_kernel.py --p1-set-a --method bond_order
echo "✓ Quantum kernel complete"

echo ""
echo "Step 5/5: Phase 1 Proof-of-Concept (~2 minutes)"
echo "----------------------------------------------------------------------"
python scripts/p7_phase1_poc.py --method bond_order
echo "✓ Phase 1 PoC complete"

echo ""
echo "======================================================================"
echo "✅ Phase 1 Pipeline Complete"
echo "======================================================================"
echo ""
echo "Results generated:"
echo "  1. Data: data/p1_set_a_20_candidates.csv"
echo "  2. Baseline: results/phase1_p1_set_a/baseline_ecfp4_loo.csv"
echo "  3. Circuits: results/phase1_p1_set_a/quantum_circuits/"
echo "  4. Kernel: results/phase1_p1_set_a/quantum_kernel/"
echo "  5. Comparison: results/phase1_p1_set_a/comparison/PHASE1_COMPARISON_REPORT_BOND_ORDER.md"
echo ""
echo "📊 View comparison report:"
echo "  cat results/phase1_p1_set_a/comparison/PHASE1_COMPARISON_REPORT_BOND_ORDER.md"
echo ""
echo "Next steps:"
echo "  - Review comparison report for Phase 1 results"
echo "  - Update P7_DATA_ANALYSIS_REPORT.md with findings"
echo "  - Proceed to Phase 2 (P3 benchmark) if results warrant"
echo ""
