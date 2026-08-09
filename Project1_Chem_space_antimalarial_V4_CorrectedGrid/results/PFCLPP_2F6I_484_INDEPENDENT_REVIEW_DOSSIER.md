# P1 V4 — Independent review dossier for the 484-centroid 2F6I panel

**Status:** `PENDING_INDEPENDENT_REVIEW` / `FAILED_CLOSED`

**Scope:** This dossier covers only the V4 replacement of the historical 4GM2-labelled PfClpP arm by genuine PfClpP structure 2F6I across the canonical 484 centroid rows. It does **not** review or authorize the V5 17-candidate × 4-target panel; that panel has a separate V5/V6 register.

## 1. Decision requested from the independent reviewer

The reviewer must independently determine whether the V4 replacement panel is complete and eligible for promotion. A signature must not be used to waive missing records or override a failed audit.

Required checks:

1. Confirm that 2F6I is the genuine PfClpP receptor and that 4GM2 is not used as PfClpP evidence.
2. Verify the canonical 484-row centroid-to-SMILES mapping and zero-based IDs.
3. Verify PDB/PDBQT frame equivalence and the chain-A catalytic-triad definition (Ser252/His223/Asp219).
4. Reproduce the declared 28 Å box and composite pose gate.
5. Inspect the complete raw accounting: 449/484 records passed the uniform audit and 35 failed.
6. Inspect the rescue sensitivity layer: 3/35 records passed the v2 rescue audit and 32/35 failed or lacked a valid rescue result.
7. Decide whether the remaining failures are resolved by a validated, pre-specified exclusion policy or require a new uniform rerun. No post-hoc element substitution, SMILES mutation, box relaxation, or pose translation is permitted.
8. Complete the signature fields only if the panel is acceptable for promotion. Otherwise return `FAIL` with reasons.

## 2. Evidence package

| Item | Artifact | Current state |
|---|---|---|
| Canonical source | `Project2_Polypharmacology_MD_ValidationV2607/data/from_project1/data/cluster_representatives_smiles.csv` | 484 rows |
| Receptor | `Project2_Polypharmacology_MD_ValidationV2607/data/proteins/2F6I.pdb` and `data/from_project1/data/proteins/2F6I.pdbqt` | frame verification required |
| Run manifest | `results/pfclpp_2f6i_484_run_manifests.json` | historical job/provenance record |
| Uniform raw root | `results/pfclpp_2f6i_484_uniform_seed20260809/` | 484 centroid directories |
| Uniform audit | `results/pfclpp_2f6i_484_uniform_aggregate_afterany/aggregation_failure.json` | `FAILED_CLOSED`, 449 pass, 35 failed |
| Rescue v2 root | `results/pfclpp_2f6i_484_rescue_seed20260809_v2/` | 35 requested IDs |
| Rescue audit | `results/pfclpp_2f6i_484_rescue_aggregate/rescue_audit_provenance.json` | `RESCUE_SENSITIVITY_INCOMPLETE` |
| Failure inventory | `results/pfclpp_2f6i_484_failure_inventory.json` | 3 pass, 32 failed; categories recorded |
| Gate validator | `scripts/p1_v4_validate_484_review_gate.py` | read-only, fail-closed |
| Failure inventory script | `scripts/p1_v4_inventory_484_failures.py` | deterministic, read-only derivation |

## 3. Failure inventory

The rescue v2 layer was not a complete repair. The 35 requested records are classified as:

| Category | Count |
|---|---:|
| RDKit deterministic embedding failure | 9 |
| Non-finite Gasteiger charge | 9 |
| Vina runtime failure | 7 |
| Composite biological gate failure | 6 |
| Multi-fragment input | 1 |
| Rescue pass | 3 |
| **Total** | **35** |

The failure inventory is descriptive provenance, not a justification for exclusion. Each category must be evaluated against a pre-specified scientific policy before any replacement panel can be promoted.

## 4. Promotion boundary

Until the reviewer accepts a complete, reproducible panel:

- the historical V4 scores remain unchanged but are not PfClpP-validated;
- the 449 uniform successes are diagnostic only;
- rescue outputs are sensitivity evidence only;
- no V4 consensus, RRS, PNS, or manuscript claim may use the replacement panel;
- V5/V6 registers must not be used as a substitute for this V4 review.

Current machine status:

```text
V4_REVIEW_GATE: FAIL_CLOSED_PENDING_INDEPENDENT_REVIEW
uniform: 449/484 pass; 35 failed
rescue_v2: 3/35 pass; 32 failed
accepted_for_promotion: false
```

## 5. Signature block

```text
reviewer_identity       : __________________________________________
affiliation             : __________________________________________
review_date_utc         : __________________________________________
independence_attestation: __________________________________________
conflict_declaration    : __________________________________________
V4 484-panel decision   : PASS / FAIL
comments                : __________________________________________
signature artifact      : __________________________________________
public-key artifact     : __________________________________________
```

The register `results/pfclpp_2f6i_484_independent_review.json` must be updated only through a verified review procedure. Non-empty fields or an automated audit do not constitute independent acceptance.
