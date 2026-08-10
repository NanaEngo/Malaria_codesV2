#!/usr/bin/env python3
"""Generate meticulous submission manifests (inventory + SHA-256 + status) for P1 V6 / P2 / P3 / P4 / P5.

Each manifest is written next to the manuscript files as SUBMISSION_MANIFEST.md.
A central index README_SUBMISSION.md is written at the repo root.
"""
import hashlib
import os
from datetime import datetime, timezone

ROOT = '/home/nanaengo/Malaria_codesV2'

PROJECTS = [
    {
        'id': 'P1 V6',
        'journal': 'Journal of Chemical Information and Modeling (JCIM, ACS)',
        'dir': 'Project1_Chem_space_antimalarial_V6_CorrectedGrid/manuscript',
        'files': [
            'P1_V6_Integrated_Polypharmacology_RRS.tex',
            'P1_V6_Integrated_Polypharmacology_RRS.pdf',
            'P1_V6_Integrated_Polypharmacology_RRS_SM.tex',
            'P1_V6_Integrated_Polypharmacology_RRS_SM.pdf',
            'Cover_Letter_P1_V6.tex',
            'Cover_Letter_P1_V6.pdf',
        ],
        'graphics': ['p1_v6_toc_graphic.pdf', 'p1_v6_toc_graphic_ACS.tiff', 'p1_v6_toc_graphic_ACS_1200dpi.tiff'],
        'pages': 'main 19 p. / SM 5 p. / cover 1 p. (verified 10/08/2026)',
        'status': 'SUBMISSION-READY — R1–R5 cleared, register INTERNAL_WORK_AUTHORIZED, ACS package assembled',
        'notes': [
            'TOC graphic ACS-compliant: 3.25x1.75 in, RGB TIFF 300 dpi + 1200 dpi (line art) + vector PDF.',
            'ACS submission package: submission_ACS_P1V6/ with README + Paragon Plus checklist.',
            'TOC graphic present (p1_v6_toc_graphic.pdf).',
            'Use of AI declaration added (main + SM).',
            'Docking protocol validation subsubsection (redocking 5/5, MMV, DEKOIS).',
            'Author Contributions + Competing Interests + Data Availability present.',
            'Numerically audited 10/08/2026 — all values traceable to source CSVs.',
        ],
    },
    {
        'id': 'P2',
        'journal': 'Journal of Chemical Information and Modeling (JCIM, ACS)',
        'dir': 'Project2_Polypharmacology_MD_ValidationV2607/manuscript/LaTeX',
        'files': [
            'Polypharmacology_MD_Validation_V2607.tex',
            'Polypharmacology_MD_Validation_V2607.pdf',
            'Polypharmacology_MD_Validation_SM_V2607.tex',
            'Polypharmacology_MD_Validation_SM_V2607.pdf',
            'Cover_Letter.tex',
            'Cover_Letter.pdf',
            'Table_S0_Docking_Validation.tex',
            'Table_S5_ADMET_CrossValidation.tex',
            'Table_S6_ACSI_Weight_Sensitivity.tex',
            'Bibliography_Polypharmacology_MD_Validation.bib',
        ],
        'graphics': ['TOC_graphic.pdf', 'TOC_graphic.png'],
        'pages': 'main 25 p. / SM 4 p. / cover 1 p. (verified 10/08/2026)',
        'status': 'SUBMISSION-READY (main) — MD-RRS optional strengthening in progress',
        'notes': [
            'TOC graphic present.',
            'Use of AI declaration added (main + SM).',
            'Table S5 ADMET completed with real values (R11 resolved).',
            'RRS table 17 rows verified against c_rrs_classification.csv.',
            'MD-RRS (jobs 15106/15111) may replace "future work" wording; not blocking.',
        ],
    },
    {
        'id': 'P3',
        'journal': 'Journal of Cheminformatics (Springer)',
        'dir': 'Project3_Quantum_Inspired_RepresentationsV2607/manuscript/LaTeX',
        'files': [
            'Paper3_Quantum_InspiredV2608.tex',
            'Paper3_Quantum_InspiredV2608.pdf',
            'Paper3_Quantum_Inspired_SM_V2608.tex',
            'Paper3_Quantum_Inspired_SM_V2608.pdf',
            'Cover_Letter_P3.tex',
            'Cover_Letter_P3.pdf',
            'Bibliography_Paper3.bib',
        ],
        'graphics': ['Graphical_Abstract_P3.png'],
        'pages': 'main 12 p. / SM 17 p. / cover 1 p. (verified 10/08/2026)',
        'status': 'SUBMISSION-READY — SOTA reconciled, external validation integrated, audit COMPLETE_EXPLORATORY_NOT_CONFIRMATORY',
        'notes': [
            'External validation on ChEMBL malaria (22,447 mol) integrated.',
            'SOTA benchmark full-run values reconciled main/SM/BMAD.',
            'JoC house style: siunitx + cleveref, Use of AI, Declarations complete.',
            'Mandatory Contribution heading added to abstract (10/08/2026).',
            'Optional graphical abstract 920×300 px, 82 KB (<150 KB) — Graphical_Abstract_P3.png.',
            'Zenodo deposit deferred by author (DOI reserved 10.5281/zenodo.19608875).',
        ],
    },
    {
        'id': 'P4',
        'journal': 'Journal of Cheminformatics (Springer)',
        'dir': 'Project4_Advanced_Monte_CarloV2607/manuscript/LaTeX',
        'files': [
            'P4_Pareto_MCTS_JoC_refined.tex',
            'P4_Pareto_MCTS_JoC_refined.pdf',
            'P4_Pareto_MCTS_JoC_SM.tex',
            'P4_Pareto_MCTS_JoC_SM.pdf',
            'Cover_Letter_P4_JoC.tex',
            'Cover_Letter_P4_JoC.pdf',
            'P4_Bibliography.bib',
        ],
        'graphics': ['Graphical_Abstract_P4.png'],
        'pages': 'main 13 p. / SM / cover 1 p. (verified 10/08/2026)',
        'status': 'SUBMISSION-READY — v12-activity results integrated, DAR coherent',
        'notes': [
            'Activity oracle integrated into Pareto MCTS reward (v12).',
            'DAR §6.12 ↔ manuscript identical.',
            'JoC house style complete.',
            'Contribution heading aligned to journal wording (10/08/2026).',
            'Optional graphical abstract 920×300 px, 73 KB (<150 KB) — Graphical_Abstract_P4.png.',
        ],
    },
    {
        'id': 'P5',
        'journal': 'Journal of Cheminformatics (Springer)',
        'dir': 'Project5_GNN_Transformer_DrugDiscovery/manuscript',
        'files': [
            'P5_manuscript_V2608.tex',
            'P5_manuscript_V2608.pdf',
            'Cover_Letter_P5_JoC.tex',
            'Cover_Letter_P5_JoC.pdf',
            'Bibliography_P5.bib',
        ],
        'graphics': [],
        'pages': 'main 12 p. / cover 1 p. — no SM (none referenced) (verified 10/08/2026)',
        'status': 'SUBMISSION-READY — external MoleculeNet validation + audit v2 + leak-audited benchmarks',
        'notes': [
            'External ChEMBL/MoleculeNet validation complete.',
            'Independent replication verification PASS (Δmean −0.00014).',
            'JoC Declarations complete (Availability, Funding, Ethics, Use of AI).',
            'No SM file needed — no supplementary references in main.',
        ],
    },
]


def sha256(path: str) -> str:
    d = hashlib.sha256()
    with open(path, 'rb') as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b''):
            d.update(block)
    return d.hexdigest()


def main() -> int:
    now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    index_lines = [
        '# Submission Packages Index',
        '',
        f'**Generated:** {now}  ',
        '**Scope:** canonical manuscripts P1 V6, P2, P3, P4, P5 — meticulous submission manifests.',
        '',
        '| Package | Journal | Pages | Status | Manifest |',
        '|---|---|---|---|---|',
    ]

    for proj in PROJECTS:
        base = os.path.join(ROOT, proj['dir'])
        lines = [
            f"# Submission Manifest — {proj['id']}",
            '',
            f"**Journal:** {proj['journal']}",
            f"**Pages:** {proj['pages']}",
            f"**Status:** {proj['status']}",
            f"**Generated:** {now}",
            '',
            '## File inventory (SHA-256)',
            '',
            '| File | Size (B) | SHA-256 |',
            '|---|---|---|',
        ]
        missing = []
        for f in proj['files']:
            p = os.path.join(base, f)
            if os.path.exists(p):
                lines.append(f'| {f} | {os.path.getsize(p)} | `{sha256(p)}` |')
            else:
                lines.append(f'| {f} | — | **MISSING** |')
                missing.append(f)
        if proj['graphics']:
            lines.append('')
            lines.append('## Graphics')
            lines.append('')
            lines.append('| File | SHA-256 |')
            lines.append('|---|---|')
            for g in proj['graphics']:
                p = os.path.join(base, 'Graphics', g)
                if os.path.exists(p):
                    lines.append(f'| {g} | `{sha256(p)}` |')
                else:
                    # try other known locations
                    alt = os.path.join(base, g)
                    if os.path.exists(alt):
                        lines.append(f'| {g} | `{sha256(alt)}` |')
                    else:
                        lines.append(f'| {g} | **MISSING** |')
                        missing.append(g)
        lines.append('')
        lines.append('## Notes')
        lines.append('')
        for n in proj['notes']:
            lines.append(f'- {n}')
        if missing:
            lines.append('')
            lines.append('## ⚠️ Missing files')
            lines.append('')
            for m in missing:
                lines.append(f'- {m}')
        manifest_path = os.path.join(base, 'SUBMISSION_MANIFEST.md')
        with open(manifest_path, 'w') as fh:
            fh.write('\n'.join(lines) + '\n')
        status_icon = '✅' if not missing else '⚠️'
        index_lines.append(
            f"| {proj['id']} | {proj['journal']} | {proj['pages'].split(' (')[0]} | {status_icon} {proj['status']} | `{proj['dir']}/SUBMISSION_MANIFEST.md` |"
        )
        print(f'{proj["id"]}: manifest written ({len(lines)} lines) missing={missing}')

    index_lines.append('')
    index_lines.append('## Notes')
    index_lines.append('')
    index_lines.append('- Manifests list canonical submission files with SHA-256 hashes for integrity verification.')
    index_lines.append('- Zenodo deposit (P3) deferred by author; DOI reserved 10.5281/zenodo.19608875.')
    index_lines.append('- P2 MD-RRS (jobs 15106/15111) may strengthen the manuscript; not blocking.')
    index_lines.append('- Regenerate any manifest with: python scripts/make_submission_manifests.py')
    with open(os.path.join(ROOT, 'README_SUBMISSION.md'), 'w') as fh:
        fh.write('\n'.join(index_lines) + '\n')
    print('README_SUBMISSION.md written')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
