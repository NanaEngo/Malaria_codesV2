import argparse
from pathlib import Path
import re

def parse_gmx_log(log_path):
    """Parses a Gromacs log file to find the final thermodynamic averages"""
    if not log_path.exists():
        return None
        
    with open(log_path, 'r') as f:
        lines = f.readlines()
        
    text = "".join(lines)
    result = {}
    
    # Try to find the final statistics block in gromacs log
    # Usually it looks like:
    # <====  A V E R A G E S  ====>
    # ...
    # Total Energy             -4.13788e+06   6994.04   -4.13787e+06   -4.1379e+06  (kJ/mol)
    # Temperature              309.845        2.26194   309.851        309.84       (K)
    # Pressure                 0.957585       127.353   1.03604        0.793747     (bar)
    
    avg_block_match = re.search(r'<\s*====\s*A V E R A G E S\s*====\s*>.*?((?:\n.*)+)', text)
    if avg_block_match:
        avg_block = avg_block_match.group(1)
        
        # Parse fields
        for line in avg_block.split('\n'):
            if line.startswith('Total Energy'):
                parts = line.split()
                if len(parts) >= 3: result['Total Energy'] = parts[2]
            elif line.startswith('Temperature'):
                parts = line.split()
                if len(parts) >= 2: result['Temperature'] = parts[1]
            elif line.startswith('Pressure'):
                parts = line.split()
                if len(parts) >= 2: result['Pressure'] = parts[1]
                
        if result:
            return result
            
    # Fallback: Find all occurrences of the step data block
    blocks = re.findall(r'(Total Energy.*?)\n\s*([-\d\.e+]+)\s+([-\d\.e+]+)\s+([-\d\.e+]+)\s+([-\d\.e+]+)', text)
    if blocks:
        last_block = blocks[-1]
        result['Total Energy'] = last_block[1]
        result['Temperature'] = last_block[3]
        result['Pressure'] = last_block[4]
    else:
        # Maybe it's an NVT log (no pressure or pressure is different)
        blocks_nvt = re.findall(r'(Total Energy.*?)\n\s*([-\d\.e+]+)\s+([-\d\.e+]+)\s+([-\d\.e+]+)', text)
        if blocks_nvt:
            last_block = blocks_nvt[-1]
            result['Total Energy'] = last_block[1]
            result['Temperature'] = last_block[2]
            
    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--system", type=str, required=True, help="Path to MD system directory")
    args = parser.parse_args()
    
    sys_dir = Path(args.system)
    print(f"System: {sys_dir.name}")
    
    nvt_log = sys_dir / "nvt.log"
    npt_log = sys_dir / "npt.log"
    
    if nvt_log.exists():
        res = parse_gmx_log(nvt_log)
        if res:
            print(f"  NVT - Temp: {res.get('Temperature', 'N/A')} K, Energy: {res.get('Total Energy', 'N/A')} kJ/mol")
        else:
            print(f"  NVT log exists but parsing failed.")
    else:
        print(f"  NVT log not found: {nvt_log}")
        
    if npt_log.exists():
        res = parse_gmx_log(npt_log)
        if res:
            print(f"  NPT - Temp: {res.get('Temperature', 'N/A')} K, Pressure: {res.get('Pressure', 'N/A')} bar, Energy: {res.get('Total Energy', 'N/A')} kJ/mol")
        else:
            print(f"  NPT log exists but parsing failed.")
    else:
        print(f"  NPT log not found: {npt_log}")

if __name__ == "__main__":
    main()
