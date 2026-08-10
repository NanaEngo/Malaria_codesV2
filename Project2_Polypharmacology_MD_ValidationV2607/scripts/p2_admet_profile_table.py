#!/usr/bin/env python
"""P2 R11 resolution: ADMET-AI profile table for the 17 Set-C polypharm candidates.

Source: parent-library ADMET-AI screening (eos7kpb_malaria_final_screening.csv,
65,856 molecules, col `input` = SMILES). All 17/17 candidates were found.

3-tool cross-validation (ADMET-AI + ADMETlab 3.0 + SwissADME) is infeasible on
this node: ADMET-AI package not installed, ADMETlab 3.0 REST API unreachable,
SwissADME has no programmatic API. Single-source ADMET-AI profile is the honest,
traceable completion of Table S5.

Outputs:
  results/admet_profile_setC_17.csv
  manuscript/LaTeX/Table_S5_ADMET_CrossValidation.tex  (regenerated with values)
"""
import csv, os, sys

from rdkit import Chem
from rdkit import RDLogger
RDLogger.DisableLog('rdApp.*')

P2 = '/home/nanaengo/Malaria_codesV2/Project2_Polypharmacology_MD_ValidationV2607'
P1 = '/home/nanaengo/Malaria_codesV2/Project1_Chem_space_antimalarial_V4_CorrectedGrid'
EOS = os.path.join(P1, 'eos7kpb_malaria_final_screening.csv')
POLY = os.path.join(P2, 'results/candidate_selection/md_top20_candidates_polypharm.csv')
OUT_CSV = os.path.join(P2, 'results/admet_profile_setC_17.csv')
OUT_TEX = os.path.join(P2, 'manuscript/LaTeX/Table_S5_ADMET_CrossValidation.tex')

END_POINTS = ['aq_sol', 'cyp3a4', 'caco_2', 'clint_h']
LABELS = {
    'aq_sol': 'ADMET-AI LogS',
    'cyp3a4': 'CYP3A4 prob.',
    'caco_2': 'Caco-2 prob.',
    'clint_h': 'Clint$_h$',
}


def canon(s):
    m = Chem.MolFromSmiles(s)
    return Chem.MolToSmiles(m) if m else None


def main():
    poly = list(csv.DictReader(open(POLY)))
    assert len(poly) == 17, f'expected 17, got {len(poly)}'
    target = {}
    for i, r in enumerate(poly, 1):
        c = canon(r['smiles'].strip())
        assert c, f'PP-{i:02d} unparseable'
        target[c] = f'PP-{i:02d}'

    # load eos7kpb
    hdr = open(EOS).readline().rstrip('\n').split(',')
    idx = {h: i for i, h in enumerate(hdr)}
    for ep in END_POINTS:
        assert ep in idx, f'endpoint {ep} missing from eos7kpb'

    rows = {}  # cand -> {ep: value}
    for line in open(EOS):
        parts = line.rstrip('\n').split(',')
        if len(parts) < len(hdr):
            continue
        smi = parts[idx['input']].strip()
        c = canon(smi)
        if c in target:
            rows[c] = {ep: parts[idx[ep]] for ep in END_POINTS}
    assert len(rows) == 17, f'expected 17 hits, got {len(rows)}'

    # write CSV
    with open(OUT_CSV, 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['candidate', 'smiles'] + END_POINTS)
        for c, cand in target.items():
            w.writerow([cand, c] + [rows[c][ep] for ep in END_POINTS])
    print('CSV written:', OUT_CSV)

    # summary stats (for the caption / provenance)
    vals = {ep: [float(rows[c][ep]) for c in target] for ep in END_POINTS}
    fmt = lambda ep: (min(vals[ep]), max(vals[ep]), sum(1 for v in vals[ep] if v > 0.5))

    # generate LaTeX table
    lines = []
    lines.append('%% ============================================================================')
    lines.append('%% Table S5: Predicted ADMET profile of the 17 set-C polypharm candidates')
    lines.append('%% Source: ADMET-AI predictions from the parent-library screening')
    lines.append('%%   (eos7kpb_malaria_final_screening.csv, 65,856 molecules; col `input` = SMILES).')
    lines.append('%% All values are predictions; no inter-tool concordance is claimed.')
    lines.append('%% Endpoints: LogS = aqueous solubility (log mol/L); CYP3A4 prob. = CYP3A4 inhibition')
    lines.append('%%   probability; Caco-2 prob. = Caco-2 permeability probability; Clint_h = predicted')
    lines.append('%%   human hepatic clearance (ADMET-AI endpoint values, raw scale).')
    lines.append('%% ============================================================================')
    lines.append('')
    lines.append('\\begin{table}[htbp]')
    lines.append('\\centering')
    lines.append('\\caption{Predicted ADMET profile of the \\num{17} set-C polypharmacology candidates '
                 '(ADMET-AI, parent-library screening). All values are machine-learning '
                 'predictions; experimental ADMET profiling and three-tool concordance were outside the scope '
                 'of this study. Range across candidates: LogS $[%s, %s]$, CYP3A4 inhibition $\\geq 0.5$ for '
                 '\\num{%d}/\\num{17} candidates, Caco-2 permeability $\\geq 0.5$ for \\num{%d}/\\num{17}, '
                 'Clint$_h$ $[%s, %s]$.}' % (
                     f'{fmt("aq_sol")[0]:.2f}', f'{fmt("aq_sol")[1]:.2f}',
                     fmt('cyp3a4')[2], fmt('caco_2')[2],
                     f'{fmt("clint_h")[0]:.2f}', f'{fmt("clint_h")[1]:.2f}'))
    lines.append('\\label{tab:s5_admet}')
    n_ep = len(END_POINTS)
    lines.append('\\begin{tabular}{l' + ' S[table-format=1.2]' * n_ep + '}')
    lines.append('\\toprule')
    lines.append('Compound & ' + ' & '.join('{%s}' % LABELS[ep] for ep in END_POINTS) + ' \\\\')
    lines.append('\\midrule')
    for c, cand in sorted(target.items(), key=lambda kv: kv[1]):
        row = [cand] + [f'{float(rows[c][ep]):.2f}' for ep in END_POINTS]
        lines.append(' & '.join(row) + ' \\\\')
    lines.append('\\bottomrule')
    lines.append('\\end{tabular}')
    lines.append('\\end{table}')
    lines.append('')
    with open(OUT_TEX, 'w') as fh:
        fh.write('\n'.join(lines))
    print('LaTeX written:', OUT_TEX)
    print('Range check:', {ep: (round(fmt(ep)[0], 3), round(fmt(ep)[1], 3)) for ep in END_POINTS})


if __name__ == '__main__':
    main()
