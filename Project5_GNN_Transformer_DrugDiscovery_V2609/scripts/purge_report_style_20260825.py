#!/usr/bin/env python3
"""Anti-AI-jargon / report-style purge on P5_manuscript_V2608.tex (V2)."""
import re, sys
P = 'manuscript/P5_manuscript_V2608.tex'
t = open(P).read()
n0 = len(t)

def sub1(old, new, tag):
    global t
    assert t.count(old) == 1, f'{tag}: {t.count(old)} matches'
    t = t.replace(old, new)
    print(f'OK {tag}')

sub1('computed from the per-seed arrays archived in the project\'s replication-statistics record',
     'computed from the five per-seed mean AUCs', 'L111')
sub1(', and the raw per-fold statistics are archived in the replication table of the project record',
     '', 'L127')
sub1('As a versioned secondary robustness campaign', 'As a secondary robustness campaign', 'L182a')
sub1('archived test probabilities', 'stored test probabilities', 'L182b')
sub1('computable from the archived vectors', 'computable from the stored vectors', 'L182c')
sub1('A versioned audit of the frozen splits', 'An audit of the frozen splits', 'L182d')
sub1('the separately versioned extended GNN campaign', 'the separately run extended GNN campaign', 'L182e')

# duplicate ChemBERTa-pending sentence: remove first occurrence (keep SLURM one rewritten)
dup = ('The separate extended ChemBERTa rerun was submitted after the GNN campaign and '
       'remains pending; no extended ChemBERTa metric is used here. ')
assert t.count(dup) == 1, f'dup: {t.count(dup)}'
t = t.replace(dup, '')
print('OK dup-removed')

# SLURM sentence rewrite without job id (second occurrence remains unique now)
slurm = re.search(r'\(SLURM array \d+\)[^\.]*\.', t)
assert slurm, 'slurm sentence not found'
old = slurm.group(0)
new = ('The separate extended ChemBERTa rerun was launched after the pretrained snapshot '
       'became available on the cluster; it remains pending and contributes no metric to this manuscript.')
t = t.replace(old, new)
print(f'OK slurm ({len(old)}->{len(new)} chars)')

# safety sweep: no residual report tokens
for tok in ('versioned', 'archived', 'project record', 'SLURM'):
    assert tok.lower() not in t.lower(), f'residual {tok}'
open(P, 'w').write(t)
print(f'DONE net={len(t)-n0:+d} chars')
