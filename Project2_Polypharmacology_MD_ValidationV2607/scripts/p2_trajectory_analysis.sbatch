#!/bin/bash
# P2 MD Trajectory Analysis — RMSD, Rg, RMSF
# Runs GROMACS analysis on completed production trajectories
source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate malaria_md

PROJECT_ROOT="/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607"
MD_DIR="${PROJECT_ROOT}/MD_systems"
RESULTS_DIR="${PROJECT_ROOT}/results/md_results"
mkdir -p "${RESULTS_DIR}"

echo "============================================================"
echo "P2 MD Trajectory Analysis started: $(date)"
echo "============================================================"

# Function to run gmx rmsd
run_rmsd() {
    local sys=$1
    local tpr=$2
    local xtc=$3
    local outprefix=$4
    local ref_group=$5
    local sel_group=$6

    echo "  RMSD: ${sys} (${ref_group} vs ${sel_group})"
    echo "${ref_group} ${sel_group}" | gmx rms -s "${tpr}" -f "${xtc}" -o "${RESULTS_DIR}/${outprefix}_rmsd.xvg" -tu ns 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "    OK"
    else
        echo "    FAILED"
    fi
}

# Function to run gmx gyrate
run_gyrate() {
    local sys=$1
    local tpr=$2
    local xtc=$3
    local outprefix=$4

    echo "  Rg: ${sys}"
    echo "Protein" | gmx gyrate -s "${tpr}" -f "${xtc}" -o "${RESULTS_DIR}/${outprefix}_gyrate.xvg" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "    OK"
    else
        echo "    FAILED"
    fi
}

# Function to run gmx rmsf
run_rmsf() {
    local sys=$1
    local tpr=$2
    local xtc=$3
    local outprefix=$4

    echo "  RMSF: ${sys}"
    echo "Protein" | gmx rmsf -s "${tpr}" -f "${xtc}" -o "${RESULTS_DIR}/${outprefix}_rmsf.xvg" -res 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "    OK"
    else
        echo "    FAILED"
    fi
}

# --- 438_PfATP4 ---
SYS="438_PfATP4"
echo ""
echo "=== ${SYS} ==="
TPR="${MD_DIR}/${SYS}/md_production.tpr"
XTC="${MD_DIR}/${SYS}/md_production_nojump.xtc"
if [ -f "${TPR}" ] && [ -f "${XTC}" ]; then
    run_rmsd "${SYS}" "${TPR}" "${XTC}" "438_PfATP4_backbone" "Backbone" "Backbone"
    run_rmsd "${SYS}" "${TPR}" "${XTC}" "438_PfATP4_ligand" "LIG" "System"
    run_gyrate "${SYS}" "${TPR}" "${XTC}" "438_PfATP4"
    run_rmsf "${SYS}" "${TPR}" "${XTC}" "438_PfATP4"
else
    echo "  MISSING files: tpr=${TPR} xtc=${XTC}"
fi

# --- 214_PfCRT ---
SYS="214_PfCRT"
echo ""
echo "=== ${SYS} ==="
TPR="${MD_DIR}/${SYS}/md_production.tpr"
XTC="${MD_DIR}/${SYS}/md_production_nojump.xtc"
if [ -f "${TPR}" ] && [ -f "${XTC}" ]; then
    run_rmsd "${SYS}" "${TPR}" "${XTC}" "214_PfCRT_backbone" "Backbone" "Backbone"
    run_rmsd "${SYS}" "${TPR}" "${XTC}" "214_PfCRT_ligand" "LIG" "System"
    run_gyrate "${SYS}" "${TPR}" "${XTC}" "214_PfCRT"
    run_rmsf "${SYS}" "${TPR}" "${XTC}" "214_PfCRT"
else
    echo "  MISSING files: tpr=${TPR} xtc=${XTC}"
fi

# --- 164_PfClpP ---
SYS="164_PfClpP"
echo ""
echo "=== ${SYS} ==="
TPR="${MD_DIR}/${SYS}/md_production.tpr"
XTC="${MD_DIR}/${SYS}/md_production_nojump.xtc"
if [ -f "${TPR}" ] && [ -f "${XTC}" ]; then
    run_rmsd "${SYS}" "${TPR}" "${XTC}" "164_PfClpP_backbone" "Backbone" "Backbone"
    run_rmsd "${SYS}" "${TPR}" "${XTC}" "164_PfClpP_ligand" "LIG" "System"
    run_gyrate "${SYS}" "${TPR}" "${XTC}" "164_PfClpP"
    run_rmsf "${SYS}" "${TPR}" "${XTC}" "164_PfClpP"
else
    echo "  MISSING files: tpr=${TPR} xtc=${XTC}"
fi

# --- 201_PfDHFR ---
SYS="201_PfDHFR"
echo ""
echo "=== ${SYS} ==="
TPR="${MD_DIR}/${SYS}/md_production.tpr"
XTC="${MD_DIR}/${SYS}/md_production_nojump.xtc"
if [ -f "${TPR}" ] && [ -f "${XTC}" ]; then
    run_rmsd "${SYS}" "${TPR}" "${XTC}" "201_PfDHFR_backbone" "Backbone" "Backbone"
    run_rmsd "${SYS}" "${TPR}" "${XTC}" "201_PfDHFR_ligand" "LIG" "System"
    run_gyrate "${SYS}" "${TPR}" "${XTC}" "201_PfDHFR"
    run_rmsf "${SYS}" "${TPR}" "${XTC}" "201_PfDHFR"
else
    echo "  MISSING files: tpr=${TPR} xtc=${XTC}"
fi

# --- Summary ---
echo ""
echo "============================================================"
echo "P2 MD Trajectory Analysis complete: $(date)"
echo "Results: ${RESULTS_DIR}/"
ls -la "${RESULTS_DIR}/"*.xvg 2>/dev/null | wc -l
echo " xvg files generated"
echo "============================================================"
