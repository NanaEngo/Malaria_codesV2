import re, math, statistics, sys, os

def parse_md_gb(mdout_path):
    data = {
        'BOND': [], 'ANGLE': [], 'DIHED': [], 'UB': [], 'IMP': [], 'CMAP': [],
        'VDWAALS': [], 'EEL': [], 'EGB': [],
        '1-4 VDW': [], '1-4 EEL': [],
    }
    with open(mdout_path) as f:
        content = f.read()
    lines = content.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i]
        if len(line) >= 5 and line[0:5] == ' BOND':
            words = line.split()
            for key, idx in [('BOND',2), ('ANGLE',5), ('DIHED',8)]:
                try:
                    data[key].append(float(words[idx]))
                except (ValueError, IndexError):
                    data[key].append(float('nan'))
            
            i += 1
            if i < len(lines):
                words = lines[i].split()
                for key, idx in [('UB',2), ('IMP',5), ('CMAP',8)]:
                    try:
                        data[key].append(float(words[idx]))
                    except (ValueError, IndexError):
                        data[key].append(float('nan'))
            
            i += 1
            if i < len(lines):
                words = lines[i].split()
                for key, idx in [('VDWAALS',2), ('EEL',5), ('EGB',8)]:
                    try:
                        data[key].append(float(words[idx]))
                    except (ValueError, IndexError):
                        data[key].append(float('nan'))
            
            i += 1
            if i < len(lines):
                words = lines[i].split()
                for key, idx in [('1-4 VDW',3), ('1-4 EEL',7)]:
                    try:
                        data[key].append(float(words[idx]))
                    except (ValueError, IndexError):
                        data[key].append(float('nan'))
        
        i += 1
    
    base = mdout_path.replace('_gb.mdout.0', '')
    surf_path = base + '_gb_surf.dat.0'
    esurf = []
    try:
        with open(surf_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    parts = line.split()
                    if len(parts) >= 2:
                        try:
                            esurf.append(float(parts[1]))
                        except ValueError:
                            esurf.append(float('nan'))
    except FileNotFoundError:
        pass
    data['ESURF'] = esurf
    
    surften = 0.0072
    data['ESURF'] = [s * surften for s in esurf]
    
    n = len(data['BOND'])
    total = []
    for j in range(n):
        gas = 0.0
        for k in ['VDWAALS','EEL','1-4 VDW','1-4 EEL']:
            v = data[k][j] if j < len(data[k]) and not (isinstance(data[k][j], float) and math.isnan(data[k][j])) else 0.0
            gas += v
        egb = data['EGB'][j] if j < len(data['EGB']) and not math.isnan(data['EGB'][j]) else 0.0
        es = data['ESURF'][j] if j < len(data['ESURF']) and not math.isnan(data['ESURF'][j]) else 0.0
        total.append(gas + egb + es)
    data['TOTAL'] = total
    return data

def main():
    wd = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    label = sys.argv[2] if len(sys.argv) > 2 else 'default'
    os.chdir(wd)
    
    complex_d = parse_md_gb('_MMPBSA_complex_gb.mdout.0')
    receptor_d = parse_md_gb('_MMPBSA_receptor_gb.mdout.0')
    ligand_d = parse_md_gb('_MMPBSA_ligand_gb.mdout.0')
    
    n_frames = min(len(complex_d['BOND']), len(receptor_d['BOND']), len(ligand_d['BOND']))
    print(f"[{label}] Frames: {n_frames}")
    print(f"[{label}]   Complex: BOND={len(complex_d['BOND'])} (NaN={sum(1 for v in complex_d['BOND'] if math.isnan(v))}), "
          f"VDWAALS={len(complex_d['VDWAALS'])}")
    
    delta = {}
    for k in complex_d:
        delta[k] = []
        for j in range(n_frames):
            c = complex_d[k][j] if j < len(complex_d[k]) else 0.0
            r = receptor_d[k][j] if j < len(receptor_d[k]) else 0.0
            l = ligand_d[k][j] if j < len(ligand_d[k]) else 0.0
            if all(isinstance(v, (int, float)) and not (isinstance(v, float) and math.isnan(v)) for v in [c, r, l]):
                delta[k].append(c - r - l)
            else:
                delta[k].append(float('nan'))
    
    print(f"\n[{label}] MM-GBSA Results (kcal/mol):")
    print(f"{'Component':<15} {'Mean':>12} {'StdDev':>12} {'StdErr':>12}")
    print("-" * 55)
    for k in ['VDWAALS', 'EEL', 'EGB', 'ESURF', '1-4 VDW', '1-4 EEL', 'TOTAL']:
        vals = [v for v in delta[k] if isinstance(v, (int, float)) and not (isinstance(v, float) and math.isnan(v))]
        if vals:
            mean = statistics.mean(vals)
            stdev = statistics.stdev(vals) if len(vals) > 1 else 0.0
            stderr = stdev / math.sqrt(len(vals))
            print(f"{k:<15} {mean:>12.4f} {stdev:>12.4f} {stderr:>12.4f}")
        else:
            print(f"{k:<15} {'N/A':>12}")
    
    outfile = f'MMPBSA_{label}_results.csv'
    with open(outfile, 'w') as f:
        f.write('Frame,' + ','.join(delta.keys()) + '\n')
        for j in range(n_frames):
            row = [str(j+1)]
            for k in delta:
                v = delta[k][j]
                row.append(str(v) if not (isinstance(v, float) and math.isnan(v)) else 'NaN')
            f.write(','.join(row) + '\n')
    print(f"[{label}] Wrote {outfile} ({n_frames} frames)")

if __name__ == '__main__':
    main()
