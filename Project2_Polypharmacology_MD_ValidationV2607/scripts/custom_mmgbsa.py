import re, math, statistics, sys, os
import argparse

def parse_md_gb(mdout_path):
    """Parse MMPBSA.py GB output files.
    
    Expected 4-line format per frame (AmberTools MM/GBSA):
      Line 1: BOND=...  ANGLE=...  DIHED=...
      Line 2: VDWAALS=...  EEL=...  EGB=...  (NOT UB/IMP/CMAP — that's an older format)
      Line 3: 1-4 VDW=...  1-4 EEL=...  RESTRAINT=...
      Line 4: ESURF=...
    """
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
        # Detect start of energy block: lines starting with " BOND"
        if len(line) >= 5 and line[0:5] == ' BOND':
            # --- Line 1: BOND, ANGLE, DIHED ---
            words = line.split()
            for key, idx in [('BOND',2), ('ANGLE',5), ('DIHED',8)]:
                try:
                    data[key].append(float(words[idx]))
                except (ValueError, IndexError):
                    data[key].append(float('nan'))
            
            # --- Line 2: VDWAALS, EEL, EGB (modern format) ---
            i += 1
            if i < len(lines):
                words = lines[i].split()
                # Try parsing as VDWAALS/EEL/EGB (modern format)
                parsed_ok = False
                if len(words) >= 9 and words[0] == 'VDWAALS':
                    for key, idx in [('VDWAALS',2), ('EEL',5), ('EGB',8)]:
                        try:
                            data[key].append(float(words[idx]))
                        except (ValueError, IndexError):
                            data[key].append(float('nan'))
                    parsed_ok = True
                # Fallback: UB/IMP/CMAP (older format)
                if not parsed_ok and len(words) >= 9:
                    for key, idx in [('UB',2), ('IMP',5), ('CMAP',8)]:
                        try:
                            data[key].append(float(words[idx]))
                        except (ValueError, IndexError):
                            data[key].append(float('nan'))
                # If neither worked, append NaN for all
                if not parsed_ok:
                    for key in ['VDWAALS','EEL','EGB']:
                        data[key].append(float('nan'))
            
            # --- Line 3: 1-4 VDW, 1-4 EEL (and RESTRAINT, ignored) ---
            i += 1
            if i < len(lines):
                words = lines[i].split()
                # After split: ['1-4','VDW','=','906290.8601','1-4','EEL','=','45423.0029','RESTRAINT','=','0.0']
                # indices:        0     1     2      3           4     5     6      7           8         9    10
                if len(words) >= 8 and words[0] == '1-4':
                    try:
                        data['1-4 VDW'].append(float(words[3]))
                    except (ValueError, IndexError):
                        data['1-4 VDW'].append(float('nan'))
                    try:
                        data['1-4 EEL'].append(float(words[7]))
                    except (ValueError, IndexError):
                        data['1-4 EEL'].append(float('nan'))
                else:
                    data['1-4 VDW'].append(float('nan'))
                    data['1-4 EEL'].append(float('nan'))
            
            # --- Line 4: ESURF (parsed separately from _gb_surf.dat.0) ---
            # (Not parsed here; handled below from the separate .dat file)
        
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
    parser = argparse.ArgumentParser(description='Parse MMPBSA.py GB output files.')
    parser.add_argument('--input', '-i', default=os.getcwd(),
                        help='Working directory containing *_gb.mdout.0 files')
    parser.add_argument('--label', default='default',
                        help='Label for the run (used in output filename)')
    parser.add_argument('--output', '-o', default=None,
                        help='Output CSV path (default: MMPBSA_<label>_results.csv in CWD)')
    parser.add_argument('--trajectory', help='Trajectory file (stored, not used in parsing)')
    parser.add_argument('--igb', type=int, default=8, help='GB model (stored for reference)')
    parser.add_argument('--membrane', action='store_true', help='Use membrane GB')
    parser.add_argument('--memb-thickness', type=float, default=30.0, help='Membrane thickness (A)')
    parser.add_argument('--saltcon', type=float, default=0.100, help='Salt concentration (M)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    args = parser.parse_args()
    
    wd = args.input
    label = args.label
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
    
    if args.output:
        outfile = args.output
    else:
        outfile = f'MMPBSA_{label}_results.csv'
    os.makedirs(os.path.dirname(outfile) or '.', exist_ok=True)
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
