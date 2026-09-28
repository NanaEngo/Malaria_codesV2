#!/usr/bin/env bash
#SBATCH --job-name=p2_k76a_whole
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --time=02:00:00
#SBATCH --output=results/set_c_md/k76a_repaired_whole_20260826/slurm_%j.out
#SBATCH --error=results/set_c_md/k76a_repaired_whole_20260826/slurm_%j.err

set -euo pipefail
BASE=/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607
REP="$BASE/results/md_systems/set_c_preparation_20260812_v1/PP-01_PfCRT_K76A/runs/20260825T063226Z/replicate_1"
OUT="$BASE/results/set_c_md/k76a_repaired_whole_20260826"
RUNOUT="$OUT/mmgbsa"
PY=/home/nanaengo/miniforge3/envs/malaria_md/bin/python3
MAMBA=/home/nanaengo/miniforge3/bin/mamba
mkdir -p "$RUNOUT"

[[ -s "$OUT/production_whole_centered.xtc" ]] || { echo "FAIL-CLOSED: repaired trajectory missing" >&2; exit 2; }
[[ -s "$REP/production.tpr" && -s "$REP/topol.top" ]] || { echo "FAIL-CLOSED: topology input missing" >&2; exit 2; }

cat > "$RUNOUT/mmpbsa.in" <<'EOF'
&general
  sys_name="PP-01_PfCRT_K76A_whole_centered"
  startframe=1
  endframe=1000
  interval=10
  keep_files=0
/
&gb
  igb=5
  saltcon=0.150
/
EOF
cp "$REP/production.tpr" "$RUNOUT/production.tpr"
cp "$REP/topol.top" "$RUNOUT/topol.top"
cp "$BASE/results/set_c_md/k76a_frame880_20260826/PP-01_PfCRT_K76A/complex.ndx" "$RUNOUT/complex.ndx"

$MAMBA run -n malaria_md gmx_MMPBSA -O \
  -i "$RUNOUT/mmpbsa.in" \
  -o "$RUNOUT/FINAL_RESULTS_MMPBSA.dat" \
  -eo "$RUNOUT/mmgbsa_timeseries.csv" \
  -cs "$REP/production.tpr" \
  -ct "$OUT/production_whole_centered.xtc" \
  -cp "$REP/topol.top" \
  -ci "$RUNOUT/complex.ndx" \
  -cg 1 13 -nogui > "$RUNOUT/run.log" 2>&1

$PY - "$RUNOUT/launch_status.json" "$RUNOUT/mmgbsa_timeseries.csv" <<'PY'
import importlib.util, json, sys
from pathlib import Path
spec = importlib.util.spec_from_file_location("qc", "scripts/p2_setc_mmgbsa_single.py")
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
manifest = Path(sys.argv[1]); timeseries = Path(sys.argv[2])
data = json.loads(manifest.read_text())
data["status"] = "COMPUTED_PENDING_QC"
data["numerical_qc"] = mod.validate_timeseries(timeseries)
if data["numerical_qc"]["status"] != "PASS":
    data["status"] = "FAILED_NUMERICAL_QC"
    data["reportable"] = False
    manifest.write_text(json.dumps(data, indent=2) + "\n")
    raise SystemExit("FAIL-CLOSED: numerical QC failed")
data["status"] = "COMPUTED"
data["reportable"] = True
manifest.write_text(json.dumps(data, indent=2) + "\n")
PY
