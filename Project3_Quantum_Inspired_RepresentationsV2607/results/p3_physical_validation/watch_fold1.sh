#!/usr/bin/env bash
# Watcher for P3 n=500/5-fold polypharmacology QKS run (Fold 1 completion)
set -euo pipefail

PID="${1:-23873}"
LOG="${2:-results/p3_physical_validation/p3_polypharm_n500.log}"
FLAG="results/p3_physical_validation/fold1_complete.flag"
WATCH_LOG="results/p3_physical_validation/watch_fold1.log"
MAX_WAIT_S="${3:-43200}"   # default 12 h

if ! kill -0 "$PID" 2>/dev/null; then
    echo "Process $PID not found" >&2
    exit 1
fi

START_EPOCH=$(date -d "$(ps -o lstart= -p "$PID")" +%s)
NOW=$(date +%s)
END_BY=$((NOW + MAX_WAIT_S))

echo "[$(date -Iseconds)] Watcher started for PID $PID (timeout in ${MAX_WAIT_S}s)" >> "$WATCH_LOG"

while true; do
    if ! kill -0 "$PID" 2>/dev/null; then
        echo "[$(date -Iseconds)] Monitored process $PID died before Fold 1 completed" > "$FLAG"
        exit 1
    fi

    NOW=$(date +%s)
    if [[ "$NOW" -gt "$END_BY" ]]; then
        echo "[$(date -Iseconds)] Watcher timed out after ${MAX_WAIT_S}s" >> "$WATCH_LOG"
        echo "Fold 1 did not complete within ${MAX_WAIT_S}s" > "$FLAG"
        exit 1
    fi

    if grep -q "Fold 2/5" "$LOG" 2>/dev/null; then
        ELAP=$((NOW - START_EPOCH))
        {
            printf 'Fold 1 completed in %d seconds (%dh %02dm %02ds)\n' "$ELAP" "$((ELAP/3600))" "$(((ELAP%3600)/60))" "$((ELAP%60))"
            echo "Process PID: $PID"
            echo "Timestamp: $(date -Iseconds)"
            echo "--- Last 30 log lines ---"
            tail -n 30 "$LOG"
        } > "$FLAG"
        echo "[$(date -Iseconds)] Fold 1 complete after ${ELAP}s" >> "$WATCH_LOG"
        cat "$FLAG"
        exit 0
    fi

    # heartbeat every ~5 minutes (every 10 iterations of 30s sleep)
    if [[ $((SECONDS % 300)) -lt 30 ]]; then
        echo "[$(date -Iseconds)] Still polling (PID $PID alive)" >> "$WATCH_LOG"
    fi

    sleep 30
done
