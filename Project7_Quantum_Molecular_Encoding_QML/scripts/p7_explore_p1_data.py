#!/usr/bin/env python3
"""
P7 Data Explorer - Find and inspect P1 Set A data
"""
import os
import sys
from pathlib import Path

def explore_p1_data():
    """Explore P1 project structure to find Set A data"""
    
    print("=" * 60)
    print("P7 Data Explorer - Looking for P1 Set A")
    print("=" * 60)
    print()
    
    # Get project root
    script_dir = Path(__file__).parent.parent
    project_root = script_dir.parent
    
    print(f"Current location: {script_dir.parent}")
    print(f"Project root: {project_root}")
    print()
    
    # Look for P1 projects
    p1_candidates = [
        "Project1_Chem_space_antimalarial_V7_CorrectedGrid",
        "Project1_Chem_space_antimalarial_V8",
        "Project1_Chem_space_antimalarial_V2607_CorrectedGrid"
    ]
    
    print("Looking for P1 projects...")
    for p1_name in p1_candidates:
        p1_path = project_root / p1_name
        if p1_path.exists():
            print(f"✓ Found: {p1_name}")
            
            # Look for results directory
            results_dir = p1_path / "results"
            if results_dir.exists():
                print(f"  ✓ Results directory exists")
                
                # List files in results
                print(f"  Files in results/:")
                for item in sorted(results_dir.iterdir())[:20]:  # First 20
                    if item.is_file():
                        size_kb = item.stat().st_size / 1024
                        print(f"    - {item.name} ({size_kb:.1f} KB)")
                    elif item.is_dir():
                        print(f"    - {item.name}/ (directory)")
            
            # Look for data directory
            data_dir = p1_path / "data"
            if data_dir.exists():
                print(f"  ✓ Data directory exists")
                print(f"  Files in data/:")
                for item in sorted(data_dir.iterdir())[:20]:
                    if item.is_file():
                        size_kb = item.stat().st_size / 1024
                        print(f"    - {item.name} ({size_kb:.1f} KB)")
                    elif item.is_dir():
                        print(f"    - {item.name}/ (directory)")
            
            # Look for submission package
            submission_dirs = [
                p1_path / "submission_ACS_P1V7",
                p1_path / "submission_ACS_P1V8"
            ]
            for sub_dir in submission_dirs:
                if sub_dir.exists():
                    print(f"  ✓ Submission package: {sub_dir.name}")
            
            print()
        else:
            print(f"✗ Not found: {p1_name}")
    
    print()
    print("=" * 60)
    print("Looking for Set A / Set C specific files...")
    print("=" * 60)
    print()
    
    # Search for CSV files containing "set" or "candidate"
    search_terms = ["set_a", "set_c", "candidate", "top_20", "pp-", "mpo"]
    
    for p1_name in p1_candidates:
        p1_path = project_root / p1_name
        if not p1_path.exists():
            continue
        
        print(f"\nSearching in {p1_name}...")
        
        # Recursive search for relevant files
        found_files = []
        for pattern in ["*.csv", "*.json", "*.txt"]:
            for file_path in p1_path.rglob(pattern):
                file_name_lower = file_path.name.lower()
                if any(term in file_name_lower for term in search_terms):
                    found_files.append(file_path)
        
        if found_files:
            print(f"  Found {len(found_files)} potentially relevant files:")
            for file_path in sorted(found_files)[:15]:  # First 15
                rel_path = file_path.relative_to(p1_path)
                size_kb = file_path.stat().st_size / 1024
                print(f"    - {rel_path} ({size_kb:.1f} KB)")
        else:
            print(f"  No files matching search terms found")
    
    print()
    print("=" * 60)
    print("Recommendations:")
    print("=" * 60)
    print()
    print("Based on the files found above, please tell me:")
    print("1. Which P1 project directory to use? (V7, V8, or V2607?)")
    print("2. Which specific file contains the 20 Set A candidates?")
    print("3. Or should I use Set C (17 candidates) instead?")
    print()
    print("Example answers:")
    print("  'Use Project1_V8, file results/set_a_candidates.csv'")
    print("  'Use Set C from P2 instead (17 polypharmacology candidates)'")
    print()

if __name__ == "__main__":
    try:
        explore_p1_data()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
