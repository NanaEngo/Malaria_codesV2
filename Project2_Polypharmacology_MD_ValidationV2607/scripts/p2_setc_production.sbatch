#!/bin/bash
#SBATCH --job-name=p2_setc_production_retired
#SBATCH --partition=production
#SBATCH --time=00:01:00
#SBATCH --mem=1G

# RETIRED: this launcher used the non-versioned results/md_systems/set_c root
# and filesystem-order ownership. It must not execute scientific production.
# Use p2_setc_preflight_then_gpu.sbatch, which passes the exact versioned root
# and explicit --system-name ownership to p2_setc_gpu_production.sbatch.
echo "FATAL: p2_setc_production.sbatch is retired; use the fail-closed versioned GPU chain" >&2
exit 90
