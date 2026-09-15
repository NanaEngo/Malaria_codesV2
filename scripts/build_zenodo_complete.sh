#!/bin/bash
# Complete Zenodo package builder — pulls from data-results and master branches
# Usage: bash scripts/build_zenodo_complete.sh

set -euo pipefail

REPO_ROOT="/home/vital/Documents/GitHub/Malaria_codesV2"
CURRENT_BRANCH=$(git -C "${REPO_ROOT}" branch --show-current)

echo "════════════════════════════════════════════════════════════════════"
echo "  ZENODO PACKAGES COMPLETE BUILD — P3, P4, P5"
echo "  Current branch: ${CURRENT_BRANCH}"
echo "  Started: $(date)"
echo "════════════════════════════════════════════════════════════════════"
echo ""

# ============================================================================
# P3 — Quantum-Inspired Representations
# ============================================================================
echo "[1/3] Building P3 Complete Package..."
P3_PKG="${REPO_ROOT}/Project3_Quantum_Inspired_RepresentationsV2607_V4/zenodo_package_P3"

# Data files (from current data-results branch)
echo "  → Copying P3 data files..."
cp "${REPO_ROOT}/Project3_Quantum_Inspired_RepresentationsV2607_V4/results/p3_labels_production.csv" \
   "${P3_PKG}/data/" 2>/dev/null && echo "    ✓ p3_labels_production.csv" || echo "    ⚠ p3_labels_production.csv not found"

cp "${REPO_ROOT}/Project3_Quantum_Inspired_RepresentationsV2607_V4/results/p3_tda_fingerprints.csv" \
   "${P3_PKG}/data/" 2>/dev/null && echo "    ✓ p3_tda_fingerprints.csv" || echo "    ⚠ p3_tda_fingerprints.csv not found"

cp "${REPO_ROOT}/Project3_Quantum_Inspired_RepresentationsV2607_V4/results/p3_tne_embeddings.csv" \
   "${P3_PKG}/data/" 2>/dev/null && echo "    ✓ p3_tne_embeddings.csv" || echo "    ⚠ p3_tne_embeddings.csv not found"

# Results (from current branch)
echo "  → Copying P3 results..."
mkdir -p "${P3_PKG}/results"
for file in p3_hybrid_benchmark.csv p3_qks_benchmark_v1.csv p3_sota_benchmark.csv \
            p3_external_validation.csv p3_chembl_expanded.csv; do
    if [ -f "${REPO_ROOT}/Project3_Quantum_Inspired_RepresentationsV2607_V4/results/${file}" ]; then
        cp "${REPO_ROOT}/Project3_Quantum_Inspired_RepresentationsV2607_V4/results/${file}" \
           "${P3_PKG}/results/" && echo "    ✓ ${file}"
    else
        echo "    ⚠ ${file} not found"
    fi
done

# Scripts (from master branch if available, or archived)
echo "  → Checking P3 scripts..."
if [ -d "${REPO_ROOT}/_archives/P3_V2607_archived_20260829/scripts" ]; then
    echo "    Found scripts in archive"
    mkdir -p "${P3_PKG}/scripts"
    cp "${REPO_ROOT}/_archives/P3_V2607_archived_20260829/scripts/"p3_*.py \
       "${P3_PKG}/scripts/" 2>/dev/null && echo "    ✓ Copied from archive" || echo "    ⚠ Script copy failed"
fi

# Documentation
echo "  → Copying P3 documentation..."
mkdir -p "${P3_PKG}/documentation"
cp "${REPO_ROOT}/Project3_Quantum_Inspired_RepresentationsV2607_V4/P3_DATA_ANALYSIS_REPORT.md" \
   "${P3_PKG}/documentation/" 2>/dev/null && echo "    ✓ P3_DATA_ANALYSIS_REPORT.md" || echo "    ⚠ DAR not found"

# LICENSE
cp "${REPO_ROOT}/LICENSE" "${P3_PKG}/LICENSE.txt" 2>/dev/null && echo "    ✓ LICENSE.txt" || echo "    ⚠ LICENSE not found"

echo "  ✅ P3 package populated"
echo ""

# ============================================================================
# P4 — Pareto-Guided MCTS
# ============================================================================
echo "[2/3] Building P4 Complete Package..."
P4_PKG="${REPO_ROOT}/Project4_Advanced_Monte_CarloV2607_V2/zenodo_package_P4"

# Results (from current branch)
echo "  → Copying P4 benchmark results..."
mkdir -p "${P4_PKG}/results"
if [ -d "${REPO_ROOT}/Project4_Advanced_Monte_CarloV2607_V2/results/benchmark_molecules_opt_v12" ]; then
    cp -r "${REPO_ROOT}/Project4_Advanced_Monte_CarloV2607_V2/results/benchmark_molecules_opt_v12" \
       "${P4_PKG}/results/" && echo "    ✓ benchmark_molecules_opt_v12/" || echo "    ⚠ v12 benchmark copy failed"
elif [ -d "${REPO_ROOT}/Project4_Advanced_Monte_CarloV2607_V2/results/benchmark_molecules_opt" ]; then
    cp -r "${REPO_ROOT}/Project4_Advanced_Monte_CarloV2607_V2/results/benchmark_molecules_opt" \
       "${P4_PKG}/results/benchmark_molecules_opt_v12" && echo "    ✓ benchmark_molecules_opt → v12" || echo "    ⚠ Benchmark copy failed"
fi

# Pareto results
if [ -d "${REPO_ROOT}/Project4_Advanced_Monte_CarloV2607_V2/results/pareto" ]; then
    cp -r "${REPO_ROOT}/Project4_Advanced_Monte_CarloV2607_V2/results/pareto" \
       "${P4_PKG}/results/" && echo "    ✓ pareto/" || echo "    ⚠ Pareto not found"
fi

# Scripts (from master branch via git show)
echo "  → Extracting P4 scripts from master branch..."
mkdir -p "${P4_PKG}/scripts"
cd "${REPO_ROOT}"

for script in p4_mcts_agent.py p4_mcts_policy.py p4_mcts_oracles.py p4_mcts_rl_env.py \
              p4_mcts_benchmark.py p4_mcts_pareto.py p4_mcts_baselines.py p4_mcts_ablation.py; do
    git show master:Project4_Advanced_Monte_CarloV2607_V2/scripts/${script} > "${P4_PKG}/scripts/${script}" 2>/dev/null \
        && echo "    ✓ ${script} (from master)" \
        || echo "    ⚠ ${script} not in master"
done

# Documentation
echo "  → Copying P4 documentation..."
mkdir -p "${P4_PKG}/documentation"
cp "${REPO_ROOT}/Project4_Advanced_Monte_CarloV2607_V2/P4_DATA_ANALYSIS_REPORT.md" \
   "${P4_PKG}/documentation/" 2>/dev/null && echo "    ✓ P4_DATA_ANALYSIS_REPORT.md" || echo "    ⚠ DAR not found"

# LICENSE
cp "${REPO_ROOT}/LICENSE" "${P4_PKG}/LICENSE.txt" 2>/dev/null && echo "    ✓ LICENSE.txt" || echo "    ⚠ LICENSE not found"

echo "  ✅ P4 package populated"
echo ""

# ============================================================================
# P5 — GNN/Transformer Benchmark
# ============================================================================
echo "[3/3] Building P5 Complete Package..."
P5_PKG="${REPO_ROOT}/Project5_GNN_Transformer_DrugDiscovery_V2609/zenodo_package_P5"

# Data (from current branch)
echo "  → Copying P5 data files..."
mkdir -p "${P5_PKG}/data"
for file in p5_panel_19836.csv p5_labels_production.csv; do
    if [ -f "${REPO_ROOT}/Project5_GNN_Transformer_DrugDiscovery_V2609/data/${file}" ]; then
        cp "${REPO_ROOT}/Project5_GNN_Transformer_DrugDiscovery_V2609/data/${file}" \
           "${P5_PKG}/data/" && echo "    ✓ ${file}"
    else
        echo "    ⚠ ${file} not found"
    fi
done

# Results (from current branch)
echo "  → Copying P5 results..."
mkdir -p "${P5_PKG}/results"
for file in p5_replication_stats.csv p5_ecfp4rf_random_baseline.json \
            p5_public_chembl_malaria_disjoint.csv; do
    if [ -f "${REPO_ROOT}/Project5_GNN_Transformer_DrugDiscovery_V2609/results/${file}" ]; then
        cp "${REPO_ROOT}/Project5_GNN_Transformer_DrugDiscovery_V2609/results/${file}" \
           "${P5_PKG}/results/" && echo "    ✓ ${file}"
    else
        echo "    ⚠ ${file} not found"
    fi
done

# Extended campaign (selective - summary files only to keep size manageable)
echo "  → Copying P5 extended campaign (summary files)..."
if [ -d "${REPO_ROOT}/Project5_GNN_Transformer_DrugDiscovery_V2609/results/extended_campaign_20260825" ]; then
    mkdir -p "${P5_PKG}/results/extended_campaign_20260825"
    
    # Copy summary files only (not all 625 prediction files)
    for file in campaign_config.json extended_campaign_summary.json completion_audit.json; do
        if [ -f "${REPO_ROOT}/Project5_GNN_Transformer_DrugDiscovery_V2609/results/extended_campaign_20260825/${file}" ]; then
            cp "${REPO_ROOT}/Project5_GNN_Transformer_DrugDiscovery_V2609/results/extended_campaign_20260825/${file}" \
               "${P5_PKG}/results/extended_campaign_20260825/" && echo "    ✓ ${file}"
        fi
    done
    echo "    ℹ Full prediction files available on request (625 files, large)"
fi

# NN-Tanimoto deciles
if [ -d "${REPO_ROOT}/Project5_GNN_Transformer_DrugDiscovery_V2609/results/nn_tanimoto_deciles_20260829" ]; then
    cp -r "${REPO_ROOT}/Project5_GNN_Transformer_DrugDiscovery_V2609/results/nn_tanimoto_deciles_20260829" \
       "${P5_PKG}/results/" && echo "    ✓ nn_tanimoto_deciles_20260829/" || echo "    ⚠ NN-Tanimoto not found"
fi

# Butina cluster
if [ -d "${REPO_ROOT}/Project5_GNN_Transformer_DrugDiscovery_V2609/results/butina_cluster_20260829" ]; then
    mkdir -p "${P5_PKG}/results/butina_cluster_20260829"
    # Copy summary and splits, skip large prediction files
    cp "${REPO_ROOT}/Project5_GNN_Transformer_DrugDiscovery_V2609/results/butina_cluster_20260829/butina_summary.json" \
       "${P5_PKG}/results/butina_cluster_20260829/" 2>/dev/null && echo "    ✓ butina_summary.json"
    
    if [ -d "${REPO_ROOT}/Project5_GNN_Transformer_DrugDiscovery_V2609/results/butina_cluster_20260829/splits" ]; then
        cp -r "${REPO_ROOT}/Project5_GNN_Transformer_DrugDiscovery_V2609/results/butina_cluster_20260829/splits" \
           "${P5_PKG}/results/butina_cluster_20260829/" && echo "    ✓ splits/"
    fi
fi

# Scripts (from master branch via git show)
echo "  → Extracting P5 scripts from master branch..."
mkdir -p "${P5_PKG}/scripts"

for script in p5_benchmark.py p5_butina_cluster.py p5_calibration_posthoc.py \
              p5_chemberta.py p5_data.py p5_ecfp4rf_scaffold_preds.py \
              p5_extended_campaign.py p5_knn_ecfp4.py p5_nn_tanimoto_deciles.py; do
    git show master:Project5_GNN_Transformer_DrugDiscovery_V2609/scripts/${script} > "${P5_PKG}/scripts/${script}" 2>/dev/null \
        && echo "    ✓ ${script} (from master)" \
        || echo "    ⚠ ${script} not in master"
done

# Documentation
echo "  → Copying P5 documentation..."
mkdir -p "${P5_PKG}/documentation"
cp "${REPO_ROOT}/Project5_GNN_Transformer_DrugDiscovery_V2609/P5_DATA_ANALYSIS_REPORT.md" \
   "${P5_PKG}/documentation/" 2>/dev/null && echo "    ✓ P5_DATA_ANALYSIS_REPORT.md" || echo "    ⚠ DAR not found"

# LICENSE
cp "${REPO_ROOT}/LICENSE" "${P5_PKG}/LICENSE.txt" 2>/dev/null && echo "    ✓ LICENSE.txt" || echo "    ⚠ LICENSE not found"

echo "  ✅ P5 package populated"
echo ""

# ============================================================================
# Generate checksums for all packages
# ============================================================================
echo "════════════════════════════════════════════════════════════════════"
echo "  GENERATING SHA256 CHECKSUMS"
echo "════════════════════════════════════════════════════════════════════"

for PKG in "${P3_PKG}" "${P4_PKG}" "${P5_PKG}"; do
    PROJECT=$(basename $(dirname "${PKG}"))
    echo ""
    echo "  → ${PROJECT}..."
    
    cd "${PKG}"
    find . -type f ! -name "sha256sums.txt" -exec sha256sum {} \; | sort > sha256sums.txt
    
    FILE_COUNT=$(wc -l < sha256sums.txt)
    TOTAL_SIZE=$(du -sh . | cut -f1)
    
    echo "    Files: ${FILE_COUNT}"
    echo "    Size:  ${TOTAL_SIZE}"
done

cd "${REPO_ROOT}"

echo ""
echo "════════════════════════════════════════════════════════════════════"
echo "  BUILD COMPLETE ✓"
echo "════════════════════════════════════════════════════════════════════"
echo ""
echo "Package Locations:"
echo "  P3: ${P3_PKG}"
echo "  P4: ${P4_PKG}"
echo "  P5: ${P5_PKG}"
echo ""
echo "Next Steps:"
echo "  1. Verify checksums:  cd <package> && sha256sum -c sha256sums.txt"
echo "  2. Reserve DOIs for P4 and P5 on Zenodo"
echo "  3. Review README.md and MANIFEST.json in each package"
echo "  4. Upload to Zenodo following UPLOAD_INSTRUCTIONS.md"
echo ""
echo "Completed: $(date)"
echo "════════════════════════════════════════════════════════════════════"
