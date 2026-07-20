#!/usr/bin/env python3
"""
MD Convergence Validation Script
Calculates the cumulative RMSD and average slope over the last 100 ns of a molecular dynamics trajectory.
A slope close to 0 Å/ns indicates thermodynamic convergence and structural stability.
"""

import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import linregress
import os

def check_convergence(rmsd_xvg, last_ns=100.0):
    """
    Reads an XVG file containing RMSD over time and checks convergence
    on the last `last_ns` nanoseconds.
    """
    time_ps = []
    rmsd_nm = []
    
    with open(rmsd_xvg, 'r') as f:
        for line in f:
            if line.startswith('@') or line.startswith('#'):
                continue
            parts = line.split()
            if len(parts) >= 2:
                time_ps.append(float(parts[0]))
                rmsd_nm.append(float(parts[1]))
                
    time_ns = np.array(time_ps) / 1000.0
    rmsd_A = np.array(rmsd_nm) * 10.0
    
    total_time = time_ns[-1]
    start_time = max(0, total_time - last_ns)
    
    mask = time_ns >= start_time
    time_last = time_ns[mask]
    rmsd_last = rmsd_A[mask]
    
    # Calculate slope
    slope, intercept, r_value, p_value, std_err = linregress(time_last, rmsd_last)
    
    mean_rmsd = np.mean(rmsd_last)
    std_rmsd = np.std(rmsd_last)
    
    print(f"=== Convergence Analysis ({start_time:.1f} ns to {total_time:.1f} ns) ===")
    print(f"Mean RMSD: {mean_rmsd:.2f} ± {std_rmsd:.2f} Å")
    print(f"RMSD Slope: {slope:.6f} Å/ns")
    
    if abs(slope) < 0.05:
        print("Verdict: CONVERGED (Slope ~ 0)")
    else:
        print("Verdict: NOT CONVERGED (Significant drift)")

    # Plot
    plt.figure(figsize=(8, 5))
    plt.plot(time_ns, rmsd_A, alpha=0.5, label='RMSD')
    plt.plot(time_last, intercept + slope * time_last, 'r-', linewidth=2, 
             label=f'Fit slope: {slope:.4f} Å/ns')
    plt.xlabel('Time (ns)')
    plt.ylabel('RMSD (Å)')
    plt.title('MD Trajectory Convergence')
    plt.legend()
    
    out_img = rmsd_xvg.replace('.xvg', '_convergence.png')
    plt.savefig(out_img, dpi=300)
    print(f"Plot saved to {out_img}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check MD trajectory convergence")
    parser.add_argument("rmsd_xvg", help="Path to RMSD .xvg file")
    parser.add_argument("--last_ns", type=float, default=100.0, help="Last N nanoseconds to check")
    args = parser.parse_args()
    
    check_convergence(args.rmsd_xvg, args.last_ns)
