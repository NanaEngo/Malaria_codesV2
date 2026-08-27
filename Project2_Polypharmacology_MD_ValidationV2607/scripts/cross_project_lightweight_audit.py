#!/usr/bin/env python3
"""Consolidate existing lightweight audits without running scientific models."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "cross_project_audit_20260827"
OUT.mkdir(parents=True, exist_ok=True)

def sha(p: Path): return hashlib.sha256(p.read_bytes()).hexdigest()
def stat(p: Path): return {"path": str(p.relative_to(ROOT)), "exists": p.exists(), "sha256": sha(p) if p.exists() else None}

p2 = ROOT / "Project2_Polypharmacology_MD_ValidationV2607"
p5 = ROOT / "Project5_GNN_Transformer_DrugDiscovery_V2"
p6 = ROOT / "Project6_LISH_MoA_Structure_Phenotype"

p2_files=[p2/'results/robustness_transfer_20260827/external_docking_preflight_manifest.json',p2/'results/robustness_transfer_20260827/external_docking_panel_candidate_40_manifest.json',p2/'results/robustness_transfer_20260827/external_docking_launch_status.md']
p5_files=[p5/'results/extended_campaign_20260825/robustness/extended_analysis_summary.json',p5/'results/extended_campaign_20260825/robustness/paired_ablation_contrasts.csv',p5/'results/extended_campaign_20260825/robustness/split_audit.json']
p6_files=[p6/'results/p6_phase2/p6_lish_moa_phenotype_collision_group_folds.csv',p6/'results/p6_phase2/p6_lish_moa_structure_collision_group_rf_folds.csv',p6/'results/p6_phase2/p6_lish_moa_both_collision_group_rf_folds.csv',p6/'data/mappings/drugid_to_smiles_contract.json']
summary={"date":"2026-08-27","status":"COMPUTED_LIGHTWEIGHT_REPORTING_AUDIT","p2":{"files":[stat(x) for x in p2_files]},"p5":{"files":[stat(x) for x in p5_files]},"p6":{"files":[stat(x) for x in p6_files]}}

# P6 fold-level coverage and metric summaries, if available.
p6_rows=[]
for p in p6_files[:3]:
    if p.exists() and p.suffix=='.csv':
        d=pd.read_csv(p)
        p6_rows.append({"file":str(p.relative_to(ROOT)),"rows":len(d),"finite_metric_cells":int(d.select_dtypes('number').notna().all(axis=1).sum()),"mean_log_loss":float(d['mean_columnwise_log_loss'].mean()),"mean_auprc":float(d['macro_auprc'].mean()),"mean_auroc":float(d['macro_auroc'].mean()),"mean_brier":float(d['mean_brier'].mean()),"mean_ece":float(d['mean_ece'].mean()),"mean_labels_with_test_variation":float(d['n_labels_with_test_variation'].mean())})
summary['p6']['fold_summary']=p6_rows

# P5 available aggregate table is descriptive only.
p5agg=p5/'results/extended_campaign_20260825/robustness/extended_model_aggregates.csv'
if p5agg.exists():
    d=pd.read_csv(p5agg)
    summary['p5']['aggregate_columns']=list(d.columns)
    summary['p5']['aggregate_rows']=len(d)

(OUT/'cross_project_lightweight_audit.json').write_text(json.dumps(summary,indent=2)+'\n')
lines=['# Cross-project lightweight audit — 27 August 2026','','This report consolidates existing artifacts only. It does not run docking, MD, model training, hyperparameter search, or external data retrieval.','', '## P2', '', '- External docking panel and preflight are recorded separately.','- The external docking job remains governed by its own manifest and no result is promoted here.','- Existing ±1 kcal mol⁻¹ sensitivity remains deterministic rather than probabilistic.','', '## P5 V2', '', '- Existing extended GNN outputs are treated as secondary and panel-specific.','- ChemBERTa outputs remain subject to their completion and provenance gates.','- No canonical P5 estimate is overwritten by this audit.','', '## P6', '', '- Fold CSVs already contain log loss, macro-AUPRC, macro-AUROC, Brier score, ECE, and label-variation counts.','- Collision-safe grouping remains the primary split requirement.','- The summary below is descriptive and does not compare P6 metrics numerically with P5 ROC-AUC.','', '### P6 fold-level summary', '', '| Artifact | Rows | Log loss | AUROC | AUPRC | Brier | ECE | Labels varying |','|---|---:|---:|---:|---:|---:|---:|---:|']
for r in p6_rows:
    lines.append(f"| `{Path(r['file']).name}` | {r['rows']} | {r['mean_log_loss']:.5f} | {r['mean_auroc']:.5f} | {r['mean_auprc']:.5f} | {r['mean_brier']:.5f} | {r['mean_ece']:.5f} | {r['mean_labels_with_test_variation']:.1f} |")
lines += ['', '## Actions now supported by existing artifacts', '', '1. Use the P2 protocol-concordance and failure-accounting manifests after job completion.', '2. Add P5 practical-effect and calibration tables only after the pending ChemBERTa arm passes its completion gate.', '3. Use the P6 fold-level Brier/ECE and label-coverage fields in the manuscript/SI; do not silently drop rare labels.', '', '## Boundary', '', 'All future model, docking, and MD results remain `NOT_COMPUTED` until their jobs and QC gates complete.']
(OUT/'cross_project_lightweight_audit.md').write_text('\n'.join(lines)+'\n')
print(json.dumps(summary,indent=2))
