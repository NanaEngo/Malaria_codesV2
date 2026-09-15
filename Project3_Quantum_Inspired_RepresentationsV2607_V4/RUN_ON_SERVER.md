# Running ChEMBL Endpoint Audit on Server

**Purpose:** Run the ChEMBL endpoint audit on a server with better network connectivity to avoid API timeout issues.

## Prerequisites

Ensure the server has:
- Python 3.8+
- `chembl_webresource_client` package
- `pandas` package

## Installation (if needed)

```bash
# If using conda/mamba
mamba install -c conda-forge chembl_webresource_client pandas

# Or using pip
pip install chembl_webresource_client pandas
```

## Step 1: Verify Connection

Test that the server can connect to ChEMBL API:

```bash
cd Project3_Quantum_Inspired_RepresentationsV2607_V4

# Run diagnostic script (takes ~30 seconds)
python scripts/test_chembl_connection.py
```

**Expected output:**
```
Testing ChEMBL API connection...
1. Testing target query...
   Found 56 P. falciparum targets
   Example: Cytochrome b
2. Testing basic activity query...
   Retrieved 10 sample activities
   Standard types found: {'IC50', 'EC50', ...}
...
```

If this works, proceed to Step 2.

## Step 2: Run Full Audit

Run the endpoint audit (may take 10-30 minutes):

```bash
# Run audit with output logging
python scripts/p3_chembl_endpoint_audit.py 2>&1 | tee results/server_audit_run.log
```

**What it does:**
1. Queries ChEMBL for all P. falciparum activities with pchembl_value
2. Groups by assay_id to find homogeneous endpoints
3. Applies criteria:
   - Minimum 500 compounds per endpoint
   - Minimum 100 compounds per class (active/inactive)
   - Single target per assay
   - Single standard type per assay
4. Saves report to `results/p3_chembl_endpoint_audit.json`

## Step 3: Review Results

Check the audit report:

```bash
# View summary
cat results/p3_chembl_endpoint_audit.json | python -m json.tool | head -50

# Or open in text editor
nano results/p3_chembl_endpoint_audit.json
```

**Key fields to check:**
- `viable_endpoints_count` - How many endpoints meet criteria
- `viable_endpoints` - List of endpoints with details

## Decision Based on Results

### If viable_endpoints_count >= 5:
✓ **Endpoint-specific analysis is feasible**
- Proceed with full implementation (see below)
- 3-5 days additional work
- Fully addresses Reviewer 1's request

### If viable_endpoints_count = 1-4:
⚠️ **Limited feasibility**
- Analysis possible but statistical power limited
- Decide based on time constraints
- Could report as "case studies" rather than comprehensive benchmark

### If viable_endpoints_count = 0:
✗ **Analysis not feasible**
- Submit with narrow scope (Option 2)
- Document why in Response to Reviewers
- No viable endpoints under frozen protocol

## Step 4: If Proceeding with Analysis

If audit shows ≥5 viable endpoints, proceed with endpoint-specific benchmark:

### 4a. Select Endpoints

Review `results/p3_chembl_endpoint_audit.json` and select 5-10 best endpoints based on:
- Largest sample size
- Best class balance
- Known important targets
- Diverse assay types

### 4b. Create Endpoint List

```bash
# Create a file listing selected endpoints
cat > results/selected_endpoints.txt << EOF
CHEMBL123456
CHEMBL789012
CHEMBL345678
...
EOF
```

### 4c. Download Endpoint Data

Create script to download full data for selected endpoints:

```python
# File: scripts/p3_download_endpoints.py
import json
from chembl_webresource_client.new_client import new_client
import pandas as pd

# Load selected endpoints
with open('results/selected_endpoints.txt') as f:
    assay_ids = [line.strip() for line in f if line.strip()]

# Download each endpoint
activity = new_client.activity

for assay_id in assay_ids:
    print(f"Downloading {assay_id}...")
    acts = activity.filter(assay_chembl_id=assay_id, pchembl_value__isnull=False)
    df = pd.DataFrame(acts)
    df.to_csv(f'results/endpoints/{assay_id}.csv', index=False)
    print(f"  Saved {len(df)} activities")
```

Run it:
```bash
mkdir -p results/endpoints
python scripts/p3_download_endpoints.py
```

### 4d. Run Descriptor Pipeline

Apply P3 descriptor pipeline (ECFP4, TFP, TNE, QKS) to each endpoint:

```bash
# This would be implemented based on existing P3 scripts
# Reuse descriptor generation code from zenodo_package_P3/scripts/
python scripts/p3_endpoint_benchmark.py --endpoints results/selected_endpoints.txt
```

### 4e. Generate Results Tables

Create per-endpoint results table for manuscript:

| Endpoint | Target | N | Active | Inactive | AUC_ECFP4 | AUC_TFP | AUC_TNE | AUC_QKS | p-value |
|----------|--------|---|--------|----------|-----------|---------|---------|---------|---------|
| CHEMBL... | PfDHFR | 1234 | 567 | 667 | 0.82 | 0.78 | 0.65 | 0.79 | 0.045 |
| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

### 4f. Update Manuscript

1. Add SI section: "Endpoint-specific ChEMBL benchmark"
2. Add SI table with per-endpoint results
3. Update main text Discussion with findings
4. Update Response to Reviewers with completed analysis

---

## Troubleshooting

### If Step 1 fails (connection test):
- Check internet connectivity: `ping www.ebi.ac.uk`
- Check if server firewall blocks HTTPS: `curl https://www.ebi.ac.uk/chembl/api/data/activity.json?limit=1`
- Try from different network/server

### If Step 2 times out:
- API still timing out (same issue as local)
- Use alternative: bulk ChEMBL database download
- Or: manual endpoint selection via ChEMBL web interface

### If Step 2 returns 0 endpoints:
- Criteria too strict (n≥500, both classes≥100)
- Option: Relax to n≥300, classes≥50
- Or: Accept narrow scope (Option 2)

---

## Expected Timeline

If audit succeeds and shows ≥5 viable endpoints:

- **Day 1:** Audit complete, endpoints selected
- **Day 2-3:** Download data, run descriptor pipeline per endpoint
- **Day 4:** Generate results tables, statistical analysis
- **Day 5:** Integrate into manuscript, update Response to Reviewers
- **Total: 5 days**

---

## Files Created by Audit

After successful run, you should have:

```
results/
├── p3_chembl_endpoint_audit.json     # Main audit report
├── server_audit_run.log              # Execution log
└── endpoints/                         # (if proceeding)
    ├── CHEMBL123456.csv
    ├── CHEMBL789012.csv
    └── ...
```

---

## Contact Information for Results

After running on server, report back:

1. **Success case:** Number of viable endpoints found
2. **Timeout case:** Where it failed (connection, query, parsing)
3. **Zero endpoints case:** Consider relaxing criteria or Option 2

**The audit script is designed to run unattended and produce a decision-ready report.**

Good luck! 🚀
