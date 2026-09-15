#!/usr/bin/env python3
"""Test ChEMBL API connection and basic queries"""

from chembl_webresource_client.new_client import new_client

print("Testing ChEMBL API connection...")

# Test 1: Basic target query
print("\n1. Testing target query...")
try:
    target = new_client.target
    pf_targets = target.filter(organism='Plasmodium falciparum')
    print(f"   Found {len(pf_targets)} P. falciparum targets")
    if len(pf_targets) > 0:
        print(f"   Example: {pf_targets[0]['pref_name']}")
except Exception as e:
    print(f"   ERROR: {e}")

# Test 2: Activity query without filters
print("\n2. Testing basic activity query...")
try:
    activity = new_client.activity
    # Very simple query first
    sample_acts = activity.filter(target_organism='Plasmodium falciparum').only(['activity_id', 'standard_type', 'pchembl_value'])[:10]
    print(f"   Retrieved {len(sample_acts)} sample activities")
    if len(sample_acts) > 0:
        print(f"   Standard types found: {set(a.get('standard_type') for a in sample_acts if a.get('standard_type'))}")
except Exception as e:
    print(f"   ERROR: {e}")

# Test 3: Activity query with pchembl_value
print("\n3. Testing activity query with pchembl_value...")
try:
    acts = activity.filter(
        target_organism='Plasmodium falciparum',
        pchembl_value__isnull=False
    )[:100]
    print(f"   Retrieved {len(acts)} activities with pchembl_value")
    
    if len(acts) > 0:
        # Check what standard types are available
        std_types = {}
        for a in acts:
            st = a.get('standard_type')
            if st:
                std_types[st] = std_types.get(st, 0) + 1
        
        print(f"   Standard types distribution:")
        for st, count in sorted(std_types.items(), key=lambda x: -x[1])[:10]:
            print(f"     {st}: {count}")
except Exception as e:
    print(f"   ERROR: {e}")

# Test 4: Check if IC50 data exists (not pIC50)
print("\n4. Testing IC50 query...")
try:
    ic50_acts = activity.filter(
        target_organism='Plasmodium falciparum',
        standard_type='IC50',
        standard_units='nM'
    )[:10]
    print(f"   Found {len(ic50_acts)} IC50 activities")
except Exception as e:
    print(f"   ERROR: {e}")

print("\n" + "="*80)
print("DIAGNOSIS:")
print("="*80)
print("If all tests show 0 results:")
print("  → ChEMBL API connection issue or query syntax problem")
print("  → Alternative: Use pre-downloaded ChEMBL data")
print("\nIf tests show >0 results but wrong standard_type:")
print("  → Need to convert IC50 to pIC50 locally")
print("  → Or adjust query to use IC50 instead of pIC50")
