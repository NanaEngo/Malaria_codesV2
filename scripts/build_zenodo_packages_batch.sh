#!/bin/bash
# Batch build Zenodo packages for P3, P4, P5
# Usage: bash scripts/build_zenodo_packages_batch.sh

set -euo pipefail

REPO_ROOT="/home/vital/Documents/GitHub/Malaria_codesV2"

echo "=== Building Zenodo Packages for P3, P4, P5 ==="
echo "Started: $(date)"
echo ""

# ============================================================================
# P3 — Quantum-inspired representations
# ============================================================================
echo "[1/3] Building P3 package..."
P3_PKG="${REPO_ROOT}/Project3_Quantum_Inspired_RepresentationsV2607_V4/zenodo_package_P3"

# Copy key data files
echo "  Copying P3 data files..."
cp "${REPO_ROOT}/Project3_Quantum_Inspired_RepresentationsV2607_V4/results/p3_labels_production.csv" \
   "${P3_PKG}/data/" 2>/dev/null || echo "    Warning: p3_labels_production.csv not found"

cp "${REPO_ROOT}/Project3_Quantum_Inspired_RepresentationsV2607_V4/results/p3_tda_fingerprints.csv" \
   "${P3_PKG}/data/" 2>/dev/null || echo "    Warning: p3_tda_fingerprints.csv not found"

cp "${REPO_ROOT}/Project3_Quantum_Inspired_RepresentationsV2607_V4/results/p3_tne_embeddings.csv" \
   "${P3_PKG}/data/" 2>/dev/null || echo "    Warning: p3_tne_embeddings.csv not found"

# Copy key results
echo "  Copying P3 results..."
cp "${REPO_ROOT}/Project3_Quantum_Inspired_RepresentationsV2607_V4/results/p3_hybrid_benchmark.csv" \
   "${P3_PKG}/results/" 2>/dev/null || echo "    Warning: p3_hybrid_benchmark.csv not found"

cp "${REPO_ROOT}/Project3_Quantum_Inspired_RepresentationsV2607_V4/results/p3_qks_benchmark_v1.csv" \
   "${P3_PKG}/results/" 2>/dev/null || echo "    Warning: p3_qks_benchmark_v1.csv not found"

cp "${REPO_ROOT}/Project3_Quantum_Inspired_RepresentationsV2607_V4/results/p3_sota_benchmark.csv" \
   "${P3_PKG}/results/" 2>/dev/null || echo "    Warning: p3_sota_benchmark.csv not found"

# Copy documentation
echo "  Copying P3 documentation..."
cp "${REPO_ROOT}/Project3_Quantum_Inspired_RepresentationsV2607_V4/P3_DATA_ANALYSIS_REPORT.md" \
   "${P3_PKG}/documentation/" 2>/dev/null || echo "    Warning: P3 DAR not found"

# Copy LICENSE
cp "${REPO_ROOT}/LICENSE" "${P3_PKG}/LICENSE.txt" 2>/dev/null || echo "    Warning: LICENSE not found"

echo "  ✓ P3 package structure created"
echo ""

# ============================================================================
# P4 — Monte Carlo Tree Search
# ============================================================================
echo "[2/3] Building P4 package..."
P4_PKG="${REPO_ROOT}/Project4_Advanced_Monte_CarloV2607_V2/zenodo_package_P4"

# Copy benchmark results
echo "  Copying P4 benchmark results..."
if [ -d "${REPO_ROOT}/Project4_Advanced_Monte_CarloV2607_V2/results/benchmark_molecules_opt_v12" ]; then
    cp -r "${REPO_ROOT}/Project4_Advanced_Monte_CarloV2607_V2/results/benchmark_molecules_opt_v12" \
       "${P4_PKG}/results/" 2>/dev/null || echo "    Warning: v12 benchmark not found"
elif [ -d "${REPO_ROOT}/Project4_Advanced_Monte_CarloV2607_V2/results/benchmark_molecules_opt" ]; then
    cp -r "${REPO_ROOT}/Project4_Advanced_Monte_CarloV2607_V2/results/benchmark_molecules_opt" \
       "${P4_PKG}/results/benchmark_molecules_opt_v12" 2>/dev/null || echo "    Warning: benchmark not found"
fi

# Copy Pareto results
echo "  Copying P4 Pareto results..."
if [ -d "${REPO_ROOT}/Project4_Advanced_Monte_CarloV2607_V2/results/pareto" ]; then
    cp -r "${REPO_ROOT}/Project4_Advanced_Monte_CarloV2607_V2/results/pareto" \
       "${P4_PKG}/results/" 2>/dev/null || echo "    Warning: Pareto results not found"
fi

# Copy scripts
echo "  Copying P4 scripts..."
for script in p4_mcts_agent.py p4_mcts_policy.py p4_mcts_oracles.py p4_mcts_rl_env.py \
              p4_mcts_benchmark.py p4_mcts_pareto.py p4_mcts_baselines.py p4_mcts_ablation.py; do
    cp "${REPO_ROOT}/Project4_Advanced_Monte_CarloV2607_V2/scripts/${script}" \
       "${P4_PKG}/scripts/" 2>/dev/null || echo "    Warning: ${script} not found"
done

# Copy documentation
echo "  Copying P4 documentation..."
cp "${REPO_ROOT}/Project4_Advanced_Monte_CarloV2607_V2/P4_DATA_ANALYSIS_REPORT.md" \
   "${P4_PKG}/documentation/" 2>/dev/null || echo "    Warning: P4 DAR not found"

# Copy LICENSE
cp "${REPO_ROOT}/LICENSE" "${P4_PKG}/LICENSE.txt" 2>/dev/null || echo "    Warning: LICENSE not found"

echo "  ✓ P4 package structure created"
echo ""

# ============================================================================
# P5 — GNN/Transformer benchmark
# ============================================================================
echo "[3/3] Building P5 package..."
P5_PKG="${REPO_ROOT}/Project5_GNN_Transformer_DrugDiscovery_V2609/zenodo_package_P5"

# Copy core data
echo "  Copying P5 data files..."
cp "${REPO_ROOT}/Project5_GNN_Transformer_DrugDiscovery_V2609/data/p5_panel_19836.csv" \
   "${P5_PKG}/data/" 2>/dev/null || echo "    Warning: p5_panel_19836.csv not found"

# Copy results
echo "  Copying P5 results..."
cp "${REPO_ROOT}/Project5_GNN_Transformer_DrugDiscovery_V2609/results/p5_replication_stats.csv" \
   "${P5_PKG}/results/" 2>/dev/null || echo "    Warning: p5_replication_stats.csv not found"

cp "${REPO_ROOT}/Project5_GNN_Transformer_DrugDiscovery_V2609/results/p5_ecfp4rf_random_baseline.json" \
   "${P5_PKG}/results/" 2>/dev/null || echo "    Warning: ECFP4-RF baseline not found"

cp "${REPO_ROOT}/Project5_GNN_Transformer_DrugDiscovery_V2609/results/p5_public_chembl_malaria_disjoint.csv" \
   "${P5_PKG}/results/" 2>/dev/null || echo "    Warning: ChEMBL disjoint panel not found"

# Copy extended campaign if exists
if [ -d "${REPO_ROOT}/Project5_GNN_Transformer_DrugDiscovery_V2609/results/extended_campaign_20260825" ]; then
    echo "  Copying P5 extended campaign (this may take a moment)..."
    cp -r "${REPO_ROOT}/Project5_GNN_Transformer_DrugDiscovery_V2609/results/extended_campaign_20260825" \
       "${P5_PKG}/results/" 2>/dev/null || echo "    Warning: Extended campaign not found"
fi

# Copy documentation
echo "  Copying P5 documentation..."
cp "${REPO_ROOT}/Project5_GNN_Transformer_DrugDiscovery_V2609/P5_DATA_ANALYSIS_REPORT.md" \
   "${P5_PKG}/documentation/" 2>/dev/null || echo "    Warning: P5 DAR not found"

# Copy LICENSE
cp "${REPO_ROOT}/LICENSE" "${P5_PKG}/LICENSE.txt" 2>/dev/null || echo "    Warning: LICENSE not found"

echo "  ✓ P5 package structure created"
echo ""

# ============================================================================
# Generate checksums for all packages
# ============================================================================
echo "=== Generating SHA256 checksums ==="

for PKG in "${P3_PKG}" "${P4_PKG}" "${P5_PKG}"; do
    PROJECT=$(basename $(dirname "${PKG}"))
    echo "  Generating checksums for ${PROJECT}..."
    
    cd "${PKG}"
    find . -type f ! -name "sha256sums.txt" -exec sha256sum {} \; | sort > sha256sums.txt
    
    FILE_COUNT=$(wc -l < sha256sums.txt)
    TOTAL_SIZE=$(du -sh . | cut -f1)
    
    echo "    Files: ${FILE_COUNT}, Size: ${TOTAL_SIZE}"
done

echo ""
echo "=== Package Summary ==="
echo "P3: ${P3_PKG}"
echo "P4: ${P4_PKG}"
echo "P5: ${P5_PKG}"
echo ""
echo "Completed: $(date)"
echo ""
echo "Next steps:"
echo "1. Review each package's README.md and MANIFEST.json"
echo "2. Verify checksums: cd <package> && sha256sum -c sha256sums.txt"
echo "3. Reserve DOIs on Zenodo (P4 and P5 need new DOI reservations)"
echo "4. Upload to Zenodo following UPLOAD_INSTRUCTIONS.md"
