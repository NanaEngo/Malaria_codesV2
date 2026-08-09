#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import pandas as pd
from rdkit import Chem

def sha256(p: Path) -> str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1<<20), b''): h.update(b)
    return h.hexdigest()

def norm(s: str) -> str:
    """Return an RDKit canonical SMILES as the molecular join key."""
    mol = Chem.MolFromSmiles(str(s))
    if mol is None:
        raise SystemExit(f'Unparseable SMILES in molecular mapping: {s}')
    return Chem.MolToSmiles(mol, canonical=True)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args=ap.parse_args(); root=args.root
    repo=root.parent
    v5=repo/'Project1_Chem_space_antimalarial_V5_CorrectedGrid/results/v5_four_target_vina_affinities.csv'
    v5_manifest=repo/'Project1_Chem_space_antimalarial_V5_CorrectedGrid/results/diffdock_polypharm/diffdock_input_manifest.csv'
    v6_mapping=repo/'Project1_Chem_space_antimalarial_V6_CorrectedGrid/results/v6_candidate_manifest.csv'
    v6_audit=repo/'Project1_Chem_space_antimalarial_V6_CorrectedGrid/results/validation/v6_integrity_audit.json'
    v6_validator=repo/'Project1_Chem_space_antimalarial_V6_CorrectedGrid/scripts/v6_validate_evidence.py'
    cand=repo/'Project2_Polypharmacology_MD_ValidationV2607/results/candidate_selection/md_top20_candidates_polypharm.csv'
    rrs=repo/'Project2_Polypharmacology_MD_ValidationV2607/results/c_rrs_classification.csv'
    acsi=repo/'Project2_Polypharmacology_MD_ValidationV2607/results/c_acsi_scores.csv'
    pns=repo/'Project2_Polypharmacology_MD_ValidationV2607/results/c_pns_ranking.csv'
    for required_path in [v5_manifest,v6_mapping,v6_audit,v6_validator]:
        if not required_path.is_file(): raise SystemExit(f'Missing provenance input: {required_path}')
    v6_audit_data=json.loads(v6_audit.read_text())
    if v6_audit_data.get('errors') != [] or v6_audit_data.get('candidate_manifest',{}).get('usable') is not True:
        raise SystemExit('V6 integrity audit is not clean/usable; refusing integration')
    if v6_audit_data.get('candidate_manifest',{}).get('sha256') != sha256(v6_mapping):
        raise SystemExit('V6 audit candidate-manifest hash does not match current mapping file')
    vs=pd.read_csv(v5); vm=pd.read_csv(v5_manifest); v6=pd.read_csv(v6_mapping); cs=pd.read_csv(cand); rs=pd.read_csv(rrs); a=pd.read_csv(acsi); ps=pd.read_csv(pns)
    if len(vs)!=17 or len(v6)!=17 or len(cs)!=17 or len(rs)!=17 or len(a)!=17 or len(ps)!=17: raise SystemExit('Expected 17 rows in every source')
    required_v6={'candidate_id','canonical_smiles','v5_source_smiles','p2_source_rank','p2_source_smiles','p2_source_sha256'}
    if not required_v6.issubset(v6.columns): raise SystemExit(f'V6 molecular mapping missing columns: {sorted(required_v6-set(v6.columns))}')
    if not v6.candidate_id.is_unique or not vm.candidate_id.nunique()==17: raise SystemExit('Candidate IDs are not unique in molecular mapping inputs')
    if len(vm)!=68: raise SystemExit(f'V5 manifest must contain exactly 68 rows, found {len(vm)}')
    expected_targets={'PfDHFR','PfCRT','PfClpP','PfATP4'}
    vm_counts=vm.groupby('candidate_id')['target'].agg(lambda x: set(x))
    if set(vm_counts.index)!=set(v6.candidate_id): raise SystemExit('V6 mapping and V5 manifest candidate IDs disagree')
    if any(targets != expected_targets for targets in vm_counts): raise SystemExit('V5 manifest does not contain exactly four expected targets per candidate')
    if vm.groupby('candidate_id')['ligand_description'].nunique().max()!=1: raise SystemExit('V5 manifest has inconsistent ligand SMILES within a candidate')
    if vm.groupby('candidate_id')['candidate_rank'].nunique().max()!=1: raise SystemExit('V5 manifest has inconsistent candidate ranks within a candidate')
    if set(v6.candidate_id) != set(vs.candidate_id): raise SystemExit('V6 mapping and V5 affinity candidate IDs disagree')
    if 'smiles' not in rs or 'smiles' not in a or 'smiles' not in ps or 'smiles' not in cs: raise SystemExit('SMILES key missing')
    maps=[]
    for df,name in [(cs,'candidate'),(rs,'rrs'),(a,'acsi'),(ps,'pns')]:
        d=df.copy(); d['_key']=d.smiles.map(norm); maps.append((name,d))
    v6['_key']=v6.canonical_smiles.map(norm)
    v6_smiles=set(v6['_key'])
    v5_manifest_unique=vm.drop_duplicates('candidate_id').copy()
    v5_manifest_unique['_key']=v5_manifest_unique.ligand_description.map(norm)
    v5_by_id=dict(zip(v5_manifest_unique.candidate_id,v5_manifest_unique._key))
    for _, row in v6.iterrows():
        if v5_by_id.get(row.candidate_id) != row['_key']:
            raise SystemExit(f'V6/V5 row-wise molecular mismatch for {row.candidate_id}')
    p2_by_rank={int(row['rank']):norm(row['smiles']) for _,row in cs.iterrows()}
    for _, row in v6.iterrows():
        if p2_by_rank.get(int(row.p2_source_rank)) != row['_key']:
            raise SystemExit(f'V6/P2 row-wise molecular mismatch for {row.candidate_id}')
    if set(v6.p2_source_smiles.map(norm)) != set(v6['_key']): raise SystemExit('V6 mapping does not preserve P2 SMILES set')
    if set(v6.p2_source_sha256) != {sha256(cand)}: raise SystemExit('V6 mapping is not bound to current P2 candidate source hash')
    keys=[set(d['_key']) for _,d in maps]
    if not all(k==keys[0] for k in keys[1:]): raise SystemExit('SMILES key sets disagree across P2 sources')
    p2=maps[0][1][['_key','smiles']].copy()
    for _,d in maps[1:]: p2=p2.merge(d.drop(columns=['smiles']),on='_key',how='inner',validate='one_to_one')
    # Join the V5 affinities to P2 by the V6 canonical-SMILES manifest, never by row order.
    p2=p2.merge(v6[['candidate_id','_key']],on='_key',how='inner',validate='one_to_one')
    if len(p2)!=17 or set(p2.candidate_id)!=set(vs.candidate_id): raise SystemExit('V6 molecular join did not produce exactly 17 candidates')
    vina=vs.merge(v6[['candidate_id','_key']],on='candidate_id',how='inner',validate='one_to_one')
    if len(vina)!=17: raise SystemExit('V5 affinity join did not produce exactly 17 candidates')
    out=p2[['candidate_id','smiles','RRS_mean','RRS_class','ACSI','PNS','n_targets']].copy()
    out=out.merge(vina[['candidate_id','aff_PfDHFR','aff_PfCRT','aff_PfClpP','aff_PfATP4']],on='candidate_id',how='inner',validate='one_to_one')
    out['mean_vina']=out[['aff_PfDHFR','aff_PfCRT','aff_PfClpP','aff_PfATP4']].mean(axis=1)
    out=out[['candidate_id','smiles','aff_PfDHFR','aff_PfCRT','aff_PfClpP','aff_PfATP4','mean_vina','RRS_mean','RRS_class','PNS','ACSI','n_targets']]
    outdir=root/'results'; outpath=outdir/'v5_rrs_polypharm_integrated.csv'; metapath=outdir/'v5_rrs_polypharm_integrated.provenance.json'; map_path=outdir/'v5_p2_candidate_mapping.csv'
    out.to_csv(outpath,index=False)
    mapping=pd.DataFrame({'candidate_id':out.candidate_id,'v5_affinity_row':out.candidate_id.map(dict(zip(vs.candidate_id,range(1,18)))),'p2_candidate_rank':out.candidate_id.map(dict(zip(v6.candidate_id,v6.p2_source_rank))),'smiles':out.smiles,'canonical_smiles':out.smiles.map(norm)})
    mapping.to_csv(map_path,index=False)
    meta={'schema':'p1-v4-cross-source-v5-vina-rrs-polypharm-overlay/v3','status':'COMPUTATIONAL_OVERLAY_ONLY','join_key':'canonical SMILES via V6 candidate manifest; V5 affinity rows are joined by candidate_id only after the V6 manifest verifies candidate_id-to-SMILES identity against the V5 and P2 source manifests','mapping_status':'MOLECULAR_KEY_VERIFIED_ROW_WISE_CANONICAL_SMILES','sources':{str(p.relative_to(repo)):sha256(p) for p in [v5,v5_manifest,v6_mapping,cand,rrs,acsi,pns]},'v6_validation_audit':str(v6_audit.relative_to(repo)),'v6_validation_audit_sha256':sha256(v6_audit),'v6_validator_sha256':sha256(v6_validator),'mapping_file':str(map_path.relative_to(repo)),'n_rows':len(out),'columns':list(out.columns),'caveats':['Vina scores are docking estimates, not experimental free energies','RRS is docking-derived and target-specific; not MD-RRS','PNS/ACSI are computational prioritization scores','The overlay does not represent a common-protocol recalculation or causal model','V5 review register remains independent-review pending']}
    metapath.write_text(json.dumps(meta,indent=2)+'\n')
    print(outpath); print(metapath); print(map_path); print(out.to_string(index=False))
if __name__=='__main__': main()
