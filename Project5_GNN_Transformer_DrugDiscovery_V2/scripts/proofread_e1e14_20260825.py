#!/usr/bin/env python3
"""Proofread pass E1-E14 on V2608.tex (V2). Every edit asserted."""
import re, sys

P = '/home/nanaengo/Malaria_codesV2/Project5_GNN_Transformer_DrugDiscovery_V2/manuscript/P5_manuscript_V2608.tex'
t = open(P).read()
n0 = len(t)

def sub(old, new, expect=1):
    global t
    c = t.count(old)
    assert c == expect, f'ANCHOR FAIL ({c}x): {old[:70]!r}'
    t = t.replace(old, new)

# E1 stale journal comment
sub('Journal of Cheminformatics', 'Journal of Computer-Aided Molecular Design (JCAMD)', 1) if 'Journal of Cheminformatics' in t.split('\n')[0] else None

# E2 deprecated siunitx option
if 'detect-all = true' in t:
    sub('detect-all = true', 'mode = match')

# E3 appositive comma
sub('ChemBERTa latent vectors has shown promise',
    'ChemBERTa latent vectors, has shown promise')

# E4 US spelling
sub('behaviour', 'behavior')

# E7 grammar cluster
sub('with few thousand labels', 'with a few thousand labels')
sub('Our H3 result adds a nuance:', 'The topological-fusion result adds a nuance:')
sub('not uninformative, they carry', 'not uninformative --- they carry')
sub('interpretable geometric signal but their marginal ranking',
    'interpretable geometric signal, but their marginal ranking')
sub('tests a different question whether graph',
    'tests a different question: whether graph')

# E9/E11 US spellings
sub('synthesised', 'synthesized')
sub('MIT licence', 'MIT license')

# E6 duplicate-title dedupe
sub('\\subsection{Why fingerprints hold: representation--task alignment}',
    '\\subsection{Why fingerprints hold: local substructure dominance}')

# E13 inaccurate parenthetical
sub('(CRediT roles and full author affiliations are listed on the title page.)',
    '(Full author affiliations are given on the title page.)')

# E12 name the replicated arm (LED-014 = ChemBERTa Scaffold Replication Run)
m = [ln for ln in t.split('\n') if 'LED-014' in ln]
assert len(m) == 1, f'LED-014 lines={len(m)}'
line = m[0]
if 'ChemBERTa' not in line:
    new = re.sub(r'(replication run|training run|evaluation)', r'\1 of the ChemBERTa arm', line, count=1)
    assert new != line, 'E12 insertion point not found'
    t = t.replace(line, new)

# E10 document permutation test in Methods/Statistics
anchor = 'four random comparisons.'
assert t.count(anchor) >= 1
add = (' As a distribution-free corroboration of these parametric comparisons, '
       'paired permutation tests were computed on the same five per-seed means '
       '(\\num{10000} sign-flip permutations under a fixed seed); they are reported '
       'alongside the $t$-tests in Results.')
i = t.index(anchor) + len(anchor)
t = t[:i] + add + t[i:]

# E5 tighten redundant learning-curves caption (exact string)
sub('Curves are available for GIN under random and scaffold splits, '
    'GIN--TFP and GIN--TNE under both random and scaffold splits, and ChemBERTa '
    'under both random and scaffold splits; each available arm contains five '
    'folds repeated over five seeds.',
    'Curves are available for every tested arm under both random and scaffold '
    'splits; each available arm contains five folds repeated over five seeds.')

open(P, 'w').write(t)
print(f'OK: {len(t)-n0:+d} chars; all asserts passed')
