#!/usr/bin/env python3
"""Purge report-style tokens from P5-V2 manuscript (v2, scoped checks)."""
import re
P = 'manuscript/P5_manuscript_V2608.tex'
t = open(P).read()
orig_len = len(t)

subs = [
 (" --- computed from the per-seed arrays archived in the project's replication-statistics record.", "."),
 ("; and the raw per-fold statistics are archived in the replication table of the project record", ""),
 ("As a versioned secondary robustness campaign", "In a secondary robustness campaign"),
 ("with archived test probabilities", "with stored test probabilities"),
 ("computable from the archived vectors", "computable from the stored vectors"),
 ("A versioned audit of the frozen splits", "An audit of the frozen splits"),
 ("the separately versioned extended GNN campaign", "the separately run extended GNN campaign"),
 ("The separate extended ChemBERTa rerun was submitted after the GNN campaign and remains pending; no extended ChemBERTa metric is used here. ", ""),
 ("was launched after the pretrained snapshot became available locally (SLURM array 15490); it remains pending",
  "was launched once the pretrained snapshot became available on the cluster; it remains pending"),
 ("The extended campaign additionally archived individual vectors",
  "The extended campaign additionally stored individual vectors"),
]
applied = []
for a, b in subs:
    if a in t:
        t = t.replace(a, b, 1)
        applied.append(a[:48])

assert 'SLURM' not in t
assert 'archived' not in t.lower(), [l for l in t.splitlines() if 'archived' in l.lower()][:2]
assert t.count('versioned') == 2, t.count('versioned')   # only the two LISH data-description uses
assert t.count('project record') <= 1

open(P, 'w').write(t)
print(f"OK written {orig_len} -> {len(t)} bytes; edits applied: {len(applied)}")
for a in applied:
    print('  -', a)
