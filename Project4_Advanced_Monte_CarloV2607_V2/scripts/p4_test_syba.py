#!/usr/bin/env python3
import sys, traceback

print('start')
try:
    from syba.syba import SybaClassifier
    print('import ok')
    s = SybaClassifier()
    print('classifier ok')
    s.fitDefaultScore()
    print('fit ok')
    smiles = [
        'CNC(=O)c1ccc(OC(C)C(C)(C)C)c(OC)c1',
        'COc1c(C)cc(-c2ccc(S(N)(=O)=O)cc2)cc1C',
        'CC1CCC(n2cccn2)NC1(c1ccccc1)C1OCCO1',
        'COc1cc(CO)c(O)c(C)c1C',
    ]
    for smi in smiles:
        score = s.predict(smi)
        print(smi, '->', score)
except Exception as e:
    print('ERROR:', e)
    traceback.print_exc()
    sys.exit(1)
