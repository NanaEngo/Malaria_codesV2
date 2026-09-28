#!/bin/bash
#===============================================================================
# Auto-MMPBSA Monitor for 438_PfATP4
#
# Watches the production MD process on HPC and automatically launches
# gmx_MMPBSA when the simulation finishes.
#
# Usage:
#   On HPC: nohup bash auto_mmpbsa_438.sh > auto_mmpbsa_nohup.log 2>&1 &
#
# Dependencies:
#   - GROMACS 2025.4 (conda: malaria_md)
#   - gmx_MMPBSA (conda: malaria_md)
#   - ligand_438_fixed.mol2 (in MD_systems)
#===============================================================================

set -eo pipefail

# ─── Configuration ──────────────────────────────────────────────────────────
WORK_DIR="/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607/HPC_ready/438_PfATP4"
MD_SYSTEMS="/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607/MD_systems/438_PfATP4"
LOG_FILE="$WORK_DIR/auto_mmpbsa_monitor.log"
MMPBSA_LOG="$WORK_DIR/mmpbsa_post_prod.log"
MONITOR_INTERVAL=300  # 5 minutes in seconds

# ─── Environment ─────────────────────────────────────────────────────────────
source /home/nanaengo/miniforge3/etc/profile.d/conda.sh
conda activate malaria_md
export LD_LIBRARY_PATH=/home/nanaengo/miniforge3/envs/malaria_md/lib

# Verify critical executables exist
command -v gmx_MMPBSA >/dev/null 2>&1 || {
    echo "[FATAL] gmx_MMPBSA not found in PATH (malaria_md env)"
    echo "  Check: ls /home/nanaengo/miniforge3/envs/malaria_md/bin/gmx_MMPBSA"
    exit 1
}
command -v gmx >/dev/null 2>&1 || {
    echo "[FATAL] gmx not found in PATH (malaria_md env)"
    exit 1
}

# Wrapper to avoid Open MPI fork-kill issues with GROMACS
gmx_safe() {
    env -u OMPI_MCA_plm -u OMPI_MCA_mpi_warn_on_fork \
        -u OMPI_MCA_orte_base_help_aggregate \
        -u OPAL_PREFIX -u OMPI_BIN -u OMPI_LIBDIR -u PMIX_HOME \
        gmx "$@"
}

cd "$WORK_DIR"

# ─── Logging ─────────────────────────────────────────────────────────────────
log() {
    printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" | tee -a "$LOG_FILE"
}

log "╔═══════════════════════════════════════════════════════════════╗"
log "║  Auto-MMPBSA Monitor for 438_PfATP4                         ║"
log "║  Started: $(date)                    ║"
log "╚═══════════════════════════════════════════════════════════════╝"
log "Work directory: $WORK_DIR"
log "Monitor interval: ${MONITOR_INTERVAL}s"

# ─── Phase 1: Wait for production MD to finish ──────────────────────────────
log ""
log "─────────────────────────────────────────────────────────────────"
log "Phase 1: Waiting for mdrun production to finish..."
log "─────────────────────────────────────────────────────────────────"

WAIT_COUNT=0
FINISHED=false

while [ "$FINISHED" = false ]; do
    if pgrep -f "gmx_mpi mdrun.*md_production" > /dev/null 2>&1; then
        MD_PID=$(pgrep -f "gmx_mpi mdrun.*md_production" | head -1)
        CPU_PCT=$(ps -p "$MD_PID" -o %cpu --no-headers 2>/dev/null || echo "?")
        ELAPSED=$(ps -p "$MD_PID" -o etime --no-headers 2>/dev/null || echo "?")

        LAST_STEP=$(grep -oP "Step \K[0-9]+" md_production.log 2>/dev/null | tail -1)
        PCT="?"
        if [ -n "$LAST_STEP" ] && command -v bc >/dev/null 2>&1; then
            PCT=$(echo "scale=1; $LAST_STEP * 100 / 5000000" | bc 2>/dev/null || echo "?")
        fi

        WAIT_COUNT=$((WAIT_COUNT + 1))
        log "[Check $WAIT_COUNT] mdrun PID $MD_PID active | CPU: ${CPU_PCT}% | Elapsed: ${ELAPSED} | Step: ${LAST_STEP:-?} (${PCT}% of 10ns)"
        sleep "$MONITOR_INTERVAL"
    else
        log "mdrun process not found. Waiting 60s for confirmation..."
        sleep 60

        if pgrep -f "gmx_mpi mdrun.*md_production" > /dev/null 2>&1; then
            log "mdrun process reappeared — still running. Resuming monitor."
            continue
        fi

        log "mdrun process confirmed finished."

        if grep -q "Finished mdrun" md_production.log 2>/dev/null; then
            log "Production MD completed successfully! (Found 'Finished mdrun' in log)"
            FINISHED=true
        elif grep -q "Fatal error\|Error\|Segmentation fault" md_production.log 2>/dev/null; then
            log "WARNING: Production MD may have crashed! Check md_production.log for details."
            log "===== Last 10 lines of log ====="
            tail -10 md_production.log | tee -a "$LOG_FILE"
            log "+++++ Continuing anyway — MMPBSA may work with partial trajectory +++++"
            FINISHED=true
        else
            log "WARNING: mdrun ended but 'Finished mdrun' not found. Assuming completion."
            log "===== Last 10 lines of log ====="
            tail -10 md_production.log | tee -a "$LOG_FILE"
            FINISHED=true
        fi
    fi
done

# ─── Phase 2: Create nojump trajectory ──────────────────────────────────────
log ""
log "─────────────────────────────────────────────────────────────────"
log "Phase 2: Creating nojump trajectory..."
log "─────────────────────────────────────────────────────────────────"

printf "System\n" | gmx_safe trjconv -s md_production.tpr -f md_production.xtc \
    -o md_production_nojump.xtc -pbc nojump 2>&1 | tail -5 | tee -a "$LOG_FILE"

if [ -f md_production_nojump.xtc ]; then
    NOJUMP_SIZE=$(ls -lh md_production_nojump.xtc | awk '{print $5}')
    log "Nojump trajectory created: $NOJUMP_SIZE"
else
    log "Failed to create nojump trajectory. Trying without -pbc..."
    printf "System\n" | gmx_safe trjconv -s md_production.tpr -f md_production.xtc \
        -o md_production_nojump.xtc 2>&1 | tail -5 | tee -a "$LOG_FILE"
    if [ -f md_production_nojump.xtc ]; then
        log "Nojump trajectory created (no PBC correction)"
    else
        log "Cannot create trajectory. Aborting MMPBSA."
        exit 1
    fi
fi

# ─── Phase 3: Create MMPBSA input file ──────────────────────────────────────
log ""
log "─────────────────────────────────────────────────────────────────"
log "Phase 3: Creating MMPBSA input files..."
log "─────────────────────────────────────────────────────────────────"

cat > mmpbsa_438.in << 'EOF'
&general
startframe=1, endframe=1001, interval=10, verbose=1, keep_files=1,
/
&gb
igb=2, saltcon=0.15,
/
EOF
log "mmpbsa_438.in created (igb=2, saltcon=0.15M, frames 1-1001, interval=10)"

# ─── Phase 4: Copy ligand mol2 file ─────────────────────────────────────────
log ""
log "─────────────────────────────────────────────────────────────────"
log "Phase 4: Copying ligand mol2 file..."
log "─────────────────────────────────────────────────────────────────"

LIG_MOL2=""
for MOL2 in "ligand_438_fixed.mol2" "ligand_438_gaff.mol2" "ligand_438.mol2"; do
    if [ -f "$MD_SYSTEMS/$MOL2" ]; then
        LIG_MOL2="$MD_SYSTEMS/$MOL2"
        log "Found ligand mol2: $MOL2"
        break
    fi
done

if [ -n "$LIG_MOL2" ]; then
    cp -f "$LIG_MOL2" "$WORK_DIR/"
    LIG_MOL2_BASENAME=$(basename "$LIG_MOL2")
    log "Copied to: $LIG_MOL2_BASENAME"
else
    log "WARNING: No ligand mol2 found in $MD_SYSTEMS!"
    LIG_MOL2_BASENAME=""
fi

# ─── Phase 5: Create index file ─────────────────────────────────────────────
log ""
log "─────────────────────────────────────────────────────────────────"
log "Phase 5: Creating index file..."
log "─────────────────────────────────────────────────────────────────"

if [ -f "$MD_SYSTEMS/438_index.ndx" ]; then
    log "Found existing index: $MD_SYSTEMS/438_index.ndx"
    cp -f "$MD_SYSTEMS/438_index.ndx" "$WORK_DIR/"
    log "Copied existing index file"
else
    log "Creating index from md_production.tpr..."
    # Groups from default make_ndx:
    #   1 = Protein (receptor)
    #  13 = UNL (ligand)
    # Keep only these two groups for a clean index
    printf "keep 1\nkeep 13\nq\n" | gmx_safe make_ndx -f md_production.tpr \
        -o 438_index.ndx 2>&1 | tail -5 | tee -a "$LOG_FILE"

    # Verify group 13 is UNL
    if grep -q "UNL" 438_index.ndx 2>/dev/null; then
        log "Verified: group 13 is UNL (ligand)"
    else
        log "WARNING: Group 13 may not be the ligand! Index groups:"
        printf "q\n" | gmx_safe make_ndx -f md_production.tpr -o /dev/null 2>&1 | \
            grep -E "^[[:space:]]*[0-9]+" | tee -a "$LOG_FILE"
        log "Check index before proceeding!"
    fi
    log "Index file created"
fi

# ─── Phase 6: Run gmx_MMPBSA ────────────────────────────────────────────────
log ""
log "─────────────────────────────────────────────────────────────────"
log "Phase 6: Running gmx_MMPBSA..."
log "─────────────────────────────────────────────────────────────────"

log "Input:  mmpbsa_438.in"
log "Tpr:    md_production.tpr"
log "XTC:    md_production_nojump.xtc"
log "Index:  438_index.ndx (groups: 1=receptor, 13=ligand)"
log "Mol2:   $LIG_MOL2_BASENAME"
log "Output: FINAL_RESULTS_MMPBSA_rebuild.dat / .csv"

# Build command array for safety (avoids eval issues)
MMPBSA_ARGS=(
    -O
    -i mmpbsa_438.in
    -cs md_production.tpr
    -ct md_production_nojump.xtc
    -ci 438_index.ndx
    -cg 1 13
    -o FINAL_RESULTS_MMPBSA_rebuild.dat
    -eo FINAL_RESULTS_MMPBSA_rebuild.csv
)

if [ -n "$LIG_MOL2_BASENAME" ]; then
    MMPBSA_ARGS+=(-lm "$LIG_MOL2_BASENAME")
fi

MMPBSA_ARGS+=(-nogui)

log "Running: gmx_MMPBSA ${MMPBSA_ARGS[*]}"
log ""

# Execute MMPBSA — capture to separate log
gmx_MMPBSA "${MMPBSA_ARGS[@]}" 2>&1 | tee "$MMPBSA_LOG"
MMPBSA_EXIT=${PIPESTATUS[0]}

if [ $MMPBSA_EXIT -eq 0 ]; then
    log "gmx_MMPBSA completed successfully!"
else
    log "gmx_MMPBSA finished with exit code $MMPBSA_EXIT (may still have partial results)"
fi

# ─── Phase 7: Extract and display results ────────────────────────────────────
log ""
log "═══════════════════════════════════════════════════════════════"
log "  RESULTS SUMMARY"
log "═══════════════════════════════════════════════════════════════"

DELTA_TOTAL=""
VDWAALS=""
EEL=""
EGB=""

if [ -f FINAL_RESULTS_MMPBSA_rebuild.dat ]; then
    log "=== New MM-GBSA Results (HPC_ready/438_PfATP4) ==="
    grep -A 20 "DELTA TOTAL" FINAL_RESULTS_MMPBSA_rebuild.dat | tee -a "$LOG_FILE"

    DELTA_TOTAL=$(grep -A 20 "DELTA TOTAL" FINAL_RESULTS_MMPBSA_rebuild.dat | \
        grep "TOTAL" | tail -1 | awk '{print $2}')
    VDWAALS=$(grep -A 20 "DELTA TOTAL" FINAL_RESULTS_MMPBSA_rebuild.dat | \
        grep "VDWAALS" | tail -1 | awk '{print $2}')
    EEL=$(grep -A 20 "DELTA TOTAL" FINAL_RESULTS_MMPBSA_rebuild.dat | \
        grep "EEL" | tail -1 | awk '{print $2}')
    EGB=$(grep -A 20 "DELTA TOTAL" FINAL_RESULTS_MMPBSA_rebuild.dat | \
        grep "EGB" | tail -1 | awk '{print $2}')

    log ""
    log "=== Key Binding Components (kcal/mol) ==="
    log "  VDWAALS (van der Waals):  ${VDWAALS:-N/A}"
    log "  EEL     (Electrostatic):  ${EEL:-N/A}"
    log "  EGB     (GB solvation):   ${EGB:-N/A}"
    log "  TOTAL   (Binding energy): ${DELTA_TOTAL:-N/A}"
else
    log "FINAL_RESULTS_MMPBSA_rebuild.dat not found!"
fi

# ─── Phase 8: Compare with old result ────────────────────────────────────────
log ""
log "─────────────────────────────────────────────────────────────────"
log "Phase 8: Comparison with old MM-GBSA result (+473 kcal/mol)"
log "─────────────────────────────────────────────────────────────────"

OLD_DELTA=""
if [ -f "$MD_SYSTEMS/FINAL_RESULTS_MMPBSA_438.dat" ]; then
    OLD_DELTA=$(grep -A 20 "DELTA TOTAL" "$MD_SYSTEMS/FINAL_RESULTS_MMPBSA_438.dat" | \
        grep "TOTAL" | tail -1 | awk '{print $2}')
    log "Old MM-GBSA (MD_systems): DG_total = ${OLD_DELTA} kcal/mol"
else
    log "Old MM-GBSA result not found at $MD_SYSTEMS/FINAL_RESULTS_MMPBSA_438.dat"
fi

if [ -n "$OLD_DELTA" ] && [ -n "$DELTA_TOTAL" ]; then
    DIFF=$(echo "$OLD_DELTA - $DELTA_TOTAL" | bc 2>/dev/null || echo "?")
    log "New MM-GBSA (HPC_ready):   DG_total = ${DELTA_TOTAL} kcal/mol"
    log ""

    if [ "$(echo "$DELTA_TOTAL < 0" | bc 2>/dev/null 2>/dev/null)" = "1" ]; then
        log "SUCCESS: Binding energy is NEGATIVE! Clash resolved!"
        log "   Improvement: ${DIFF} kcal/mol"
        log "   The re-docked pose (Vina exhaustiveness=128) fixed the clash."
    elif command -v bc >/dev/null 2>&1 && [ "$(echo "$DELTA_TOTAL < $OLD_DELTA" | bc 2>/dev/null)" = "1" ]; then
        log "Improvement: DG improved by ${DIFF} kcal/mol (but still positive)"
        log "   The re-docked pose reduced the clash but may need more refinement."
    else
        log "No improvement: DG = ${DELTA_TOTAL} kcal/mol (old: ${OLD_DELTA})"
        log "   The re-docked pose did not resolve the clash. Consider Gnina re-docking."
    fi
fi

log ""
log "═══════════════════════════════════════════════════════════════"
log "Auto-MMPBSA script completed at $(date)"
log "═══════════════════════════════════════════════════════════════"
log ""
log "Results saved to:"
log "  - $WORK_DIR/FINAL_RESULTS_MMPBSA_rebuild.dat"
log "  - $WORK_DIR/FINAL_RESULTS_MMPBSA_rebuild.csv"
log "  - $WORK_DIR/auto_mmpbsa_monitor.log (full log)"
log "  - $WORK_DIR/mmpbsa_post_prod.log (MMPBSA output)"
