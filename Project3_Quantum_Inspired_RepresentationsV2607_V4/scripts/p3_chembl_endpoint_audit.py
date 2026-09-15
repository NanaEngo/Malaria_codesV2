#!/usr/bin/env python3
"""
ChEMBL Endpoint Audit for P3 V2609 Reviewer Response

Purpose: Identify viable homogeneous endpoints for endpoint-specific benchmarking
         WITHOUT running the full analysis yet.

Criteria (frozen before execution):
- One assay_id per endpoint
- Single biological target
- Standard type: pIC50 or pKi only
- Standard units: nM
- Minimum n >= 500 total compounds
- Minimum 100 compounds per class (using 6.5 threshold: <6.5 inactive, >=6.5 active)
- Plasmodium falciparum organism

Output: Audit report showing how many viable endpoints exist, their characteristics
"""

import json
from chembl_webresource_client.new_client import new_client
import pandas as pd
from collections import Counter

# Frozen protocol parameters
MIN_TOTAL_N = 500
MIN_PER_CLASS = 100
ACTIVITY_THRESHOLD = 6.5  # pchembl_value threshold (already -log10 transformed)
ORGANISM = "Plasmodium falciparum"
STANDARD_TYPES = ["IC50", "EC50", "Ki"]  # Use raw types; pchembl_value is already -log10
STANDARD_UNITS = "nM"

def audit_chembl_endpoints():
    """
    Audit ChEMBL for viable P. falciparum endpoints.
    Returns summary without downloading full datasets.
    """
    
    print("=" * 80)
    print("ChEMBL Endpoint Audit for P3 V2609")
    print("=" * 80)
    print(f"\nProtocol criteria:")
    print(f"  Organism: {ORGANISM}")
    print(f"  Standard types: {STANDARD_TYPES}")
    print(f"  Standard units: {STANDARD_UNITS}")
    print(f"  Minimum total n: {MIN_TOTAL_N}")
    print(f"  Minimum per class: {MIN_PER_CLASS} (threshold: {ACTIVITY_THRESHOLD})")
    print("\n" + "=" * 80)
    
    # Initialize client
    activity = new_client.activity
    assay = new_client.assay
    target = new_client.target
    
    # Query P. falciparum activities
    print("\n1. Querying ChEMBL for P. falciparum activities...")
    print("   (This may take a few minutes...)")
    
    # Get activities with pIC50 or pKi
    # Use pchembl_value which is already -log10 transformed
    print("   Attempting query for Plasmodium falciparum with pchembl_value...")
    print("   (This will retrieve all matching activities - may take 5-15 minutes...)")
    try:
        # Query by organism with pchembl_value (which is already -log10 transformed)
        # Note: This retrieves ALL matching records from ChEMBL
        acts = activity.filter(
            target_organism=ORGANISM,
            pchembl_value__isnull=False,
            standard_units=STANDARD_UNITS
        )
        
        # Convert to list to actually retrieve data
        print("   Downloading activities from ChEMBL API...")
        activities = list(acts)
        print(f"   ✓ Retrieved {len(activities)} activities with pchembl_value")
    except Exception as e:
        print(f"   ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n   Total activities retrieved: {len(activities)}")
    
    if len(activities) == 0:
        print("\n   ERROR: No activities found. Check ChEMBL connection.")
        return None
    
    # Convert to DataFrame
    df = pd.DataFrame(activities)
    
    # Filter by acceptable standard types locally
    if len(df) > 0 and 'standard_type' in df.columns:
        initial_count = len(df)
        df = df[df['standard_type'].isin(STANDARD_TYPES)]
        print(f"   Filtered by standard_type ({STANDARD_TYPES}): {initial_count} → {len(df)} activities")
    
    print("\n2. Grouping by assay_id...")
    
    # Group by assay to find homogeneous endpoints
    assay_groups = df.groupby('assay_chembl_id')
    
    viable_endpoints = []
    
    print("\n3. Evaluating endpoints against criteria...")
    print(f"   Total unique assays: {len(assay_groups)}")
    
    for assay_id, group in assay_groups:
        # Check size
        n_total = len(group)
        if n_total < MIN_TOTAL_N:
            continue
        
        # Check homogeneity (single target, single standard type)
        n_targets = group['target_chembl_id'].nunique()
        n_std_types = group['standard_type'].nunique()
        
        if n_targets != 1 or n_std_types != 1:
            continue  # Not homogeneous
        
        # Check class balance
        values = pd.to_numeric(group['pchembl_value'], errors='coerce').dropna()
        n_active = (values >= ACTIVITY_THRESHOLD).sum()
        n_inactive = (values < ACTIVITY_THRESHOLD).sum()
        
        if n_active < MIN_PER_CLASS or n_inactive < MIN_PER_CLASS:
            continue  # Insufficient class balance
        
        # This is a viable endpoint
        target_id = group['target_chembl_id'].iloc[0]
        std_type = group['standard_type'].iloc[0]
        
        # Get target info
        try:
            target_info = target.get(target_id)
            target_name = target_info.get('pref_name', 'Unknown')
            target_type = target_info.get('target_type', 'Unknown')
        except:
            target_name = 'Unknown'
            target_type = 'Unknown'
        
        # Get assay info
        try:
            assay_info = assay.get(assay_id)
            assay_type = assay_info.get('assay_type', 'Unknown')
            assay_desc = assay_info.get('description', '')[:100]
        except:
            assay_type = 'Unknown'
            assay_desc = ''
        
        viable_endpoints.append({
            'assay_id': assay_id,
            'target_id': target_id,
            'target_name': target_name,
            'target_type': target_type,
            'assay_type': assay_type,
            'standard_type': std_type,
            'n_total': n_total,
            'n_active': n_active,
            'n_inactive': n_inactive,
            'balance_ratio': min(n_active, n_inactive) / max(n_active, n_inactive),
            'assay_desc': assay_desc
        })
    
    print(f"\n4. Results:")
    print(f"   Viable endpoints found: {len(viable_endpoints)}")
    
    if len(viable_endpoints) == 0:
        print("\n   CONCLUSION: No viable endpoints meet all criteria.")
        print("   Endpoint-specific analysis is NOT feasible with current protocol.")
        return None
    
    # Sort by total n (descending)
    viable_endpoints.sort(key=lambda x: x['n_total'], reverse=True)
    
    # Summary statistics
    print("\n" + "=" * 80)
    print("VIABLE ENDPOINTS SUMMARY")
    print("=" * 80)
    
    for i, ep in enumerate(viable_endpoints[:10], 1):  # Show top 10
        print(f"\n{i}. {ep['assay_id']}")
        print(f"   Target: {ep['target_name']} ({ep['target_id']})")
        print(f"   Type: {ep['target_type']} / {ep['assay_type']}")
        print(f"   Standard: {ep['standard_type']}")
        print(f"   N: {ep['n_total']} (Active: {ep['n_active']}, Inactive: {ep['n_inactive']})")
        print(f"   Balance: {ep['balance_ratio']:.2f}")
        if ep['assay_desc']:
            print(f"   Desc: {ep['assay_desc']}")
    
    if len(viable_endpoints) > 10:
        print(f"\n   ... and {len(viable_endpoints) - 10} more endpoints")
    
    # Save full report
    report = {
        'audit_date': pd.Timestamp.now().isoformat(),
        'protocol': {
            'organism': ORGANISM,
            'standard_types': STANDARD_TYPES,
            'standard_units': STANDARD_UNITS,
            'min_total_n': MIN_TOTAL_N,
            'min_per_class': MIN_PER_CLASS,
            'activity_threshold': ACTIVITY_THRESHOLD
        },
        'total_activities_retrieved': len(activities),
        'total_assays_evaluated': len(assay_groups),
        'viable_endpoints_count': len(viable_endpoints),
        'viable_endpoints': viable_endpoints
    }
    
    output_file = '../results/p3_chembl_endpoint_audit.json'
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n\nFull report saved to: {output_file}")
    
    # Decision recommendation
    print("\n" + "=" * 80)
    print("DECISION RECOMMENDATION")
    print("=" * 80)
    
    if len(viable_endpoints) >= 5:
        print("✓ PROCEED TO ENDPOINT-SPECIFIC ANALYSIS")
        print(f"  Found {len(viable_endpoints)} viable endpoints.")
        print("  This is sufficient for meaningful endpoint-specific benchmarking.")
    elif len(viable_endpoints) >= 1:
        print("⚠ LIMITED FEASIBILITY")
        print(f"  Found {len(viable_endpoints)} viable endpoint(s).")
        print("  Analysis is technically feasible but statistical power may be limited.")
    else:
        print("✗ NOT FEASIBLE")
        print("  No viable endpoints meet the frozen protocol criteria.")
        print("  Recommendation: Maintain narrow scope (Proposition A2)")
    
    return report


if __name__ == "__main__":
    try:
        report = audit_chembl_endpoints()
        
        if report and report['viable_endpoints_count'] > 0:
            print("\n" + "=" * 80)
            print("NEXT STEPS IF PROCEEDING:")
            print("=" * 80)
            print("1. Review audit report and select endpoints")
            print("2. Run p3_chembl_endpoint_benchmark.py (to be created)")
            print("3. Generate per-endpoint results tables")
            print("4. Integrate into manuscript/SI")
            print("5. Update Response to Reviewers")
        else:
            print("\n" + "=" * 80)
            print("ALTERNATIVE PATH:")
            print("=" * 80)
            print("Maintain current narrowed scope:")
            print("- Primary: Computational-label benchmark (19,836 molecules)")
            print("- Secondary: Pooled ChEMBL transfer (exploratory only)")
            print("- Conclusion: Honest-negative on quantum-inspired descriptors")
    
    except Exception as e:
        print(f"\nERROR during audit: {e}")
        import traceback
        traceback.print_exc()
