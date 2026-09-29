#!/usr/bin/env bash
#SBATCH --job-name=p2_redock_sens
#SBATCH --partition=production
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --time=04:00:00
#SBATCH --output=logs/p2_redock_sens_%A_%a.out
#SBATCH --error=logs/p2_redock_sens_%A_%a.err

# Targeted multi-seed redocking launcher. This script is intentionally
# fail-closed: it requires a versioned input manifest and explicit execution
# authorization. It never overwrites canonical docking outputs.
set -euo pipefail

: "${P2_REDOCK_INPUT_MANIFEST:?Set P2_REDOCK_INPUT_MANIFEST to a reviewed JSON manifest}"
: "${P2_REDOCK_CONFIRM:?Set P2_REDOCK_CONFIRM=I_UNDERSTAND after reviewing the manifest}"
[[ "$P2_REDOCK_CONFIRM" == I_UNDERSTAND ]] || { echo 'FAIL-CLOSED: authorization missing' >&2; exit 2; }
[[ -s "$P2_REDOCK_INPUT_MANIFEST" ]] || { echo 'FAIL-CLOSED: input manifest missing' >&2; exit 2; }

python - "$P2_REDOCK_INPUT_MANIFEST" <<'PY'
import json, sys
p=json.load(open(sys.argv[1]))
required={'scope','receptor','ligand','config','seeds','output_dir'}
missing=required-set(p)
if missing: raise SystemExit(f'FAIL-CLOSED: manifest missing {sorted(missing)}')
if p['scope'] != 'P2_TARGETED_REDOCK_SENSITIVITY': raise SystemExit('FAIL-CLOSED: invalid scope')
if not p['seeds'] or len(set(p['seeds'])) != len(p['seeds']): raise SystemExit('FAIL-CLOSED: invalid seeds')
for key in ('receptor','ligand','config'):
    if not isinstance(p[key], str) or not p[key]: raise SystemExit(f'FAIL-CLOSED: invalid {key}')
PY

MANIFEST="$P2_REDOCK_INPUT_MANIFEST"
OUT=$(python - "$MANIFEST" -c 'import json,sys; print(json.load(open(sys.argv[1]))["output_dir"])')
RECEPTOR=$(python - "$MANIFEST" -c 'import json,sys; print(json.load(open(sys.argv[1]))["receptor"])')
LIGAND=$(python - "$MANIFEST" -c 'import json,sys; print(json.load(open(sys.argv[1]))["ligand"])')
CONFIG=$(python - "$MANIFEST" -c 'import json,sys; print(json.load(open(sys.argv[1]))["config"])')
SEEDS=($(python - "$MANIFEST" -c 'import json,sys; print(*json.load(open(sys.argv[1]))["seeds"])'))
mkdir -p "$OUT"
[[ -s "$RECEPTOR" && -s "$LIGAND" && -s "$CONFIG" ]] || { echo 'FAIL-CLOSED: docking input missing' >&2; exit 3; }
command -v vina >/dev/null || { echo 'FAIL-CLOSED: vina unavailable' >&2; exit 3; }

python - "$MANIFEST" "$OUT" "$RECEPTOR" "$LIGAND" "$CONFIG" <<'PY'
import hashlib,json,sys
from pathlib import Path
manifest,out,*files=sys.argv[1:]
def h(p):
 d=hashlib.sha256();
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): d.update(b)
 return d.hexdigest()
p=json.load(open(manifest)); p.update({'status':'RUNNING','input_sha256':{x:h(x) for x in files},'manifest_sha256':h(manifest)})
Path(out).mkdir(parents=True,exist_ok=True)
json.dump(p,open(Path(out)/'redock_sensitivity_manifest.json','w'),indent=2)
PY

for seed in "${SEEDS[@]}"; do
  out="$OUT/seed_${seed}.pdbqt"
  log="$OUT/seed_${seed}.log"
  [[ -e "$out" ]] && { echo "Refusing to overwrite $out" >&2; exit 4; }
  vina --receptor "$RECEPTOR" --ligand "$LIGAND" --config "$CONFIG" --seed "$seed" --out "$out" --log "$log"
done

python - "$OUT" "${SEEDS[@]}" <<'PY'
import json,sys
from pathlib import Path
out=Path(sys.argv[1]); seeds=sys.argv[2:]
p=json.load(open(out/'redock_sensitivity_manifest.json'))
p['status']='COMPLETED_REQUIRES_POSE_QC'
p['outputs']=[str(out/f'seed_{s}.pdbqt') for s in seeds]
json.dump(p,open(out/'redock_sensitivity_manifest.json','w'),indent=2)
PY
