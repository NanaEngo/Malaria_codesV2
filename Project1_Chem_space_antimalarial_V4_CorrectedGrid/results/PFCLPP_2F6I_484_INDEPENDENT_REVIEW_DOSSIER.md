# P1 V4 — Independent review dossier for the 484-centroid 2F6I panel

**Version:** 2.0 (2026-08-10) — supersedes v1 (2026-08-09, pre-remediation)
**Status:** `PENDING_INDEPENDENT_REVIEW` — accounting **COMPLETE**, panel ready for review, promotion gated on independent acceptance
**Register:** `results/pfclpp_2f6i_484_independent_review.json`

**Scope:** This dossier covers only the V4 replacement of the historical 4GM2-labelled PfClpP arm by the genuine PfClpP structure **2F6I** across the canonical 484 centroid rows. It does **not** review or authorize the V5 17-candidate × 4-target panel; that panel has a separate V5/V6 register.

---

## 1. Executive summary — final 484 accounting

The 2F6I panel accounting is **complete and reproducible**:

```
484 = 448 historical uniform PASS (non-remediated, gate-verified)
    + 10 remediation PASS_RAW_VINA (gate-verified)
    +  1 PENDING_INDEPENDENT_REVIEW (centroid 171, MIXED audit flag)
    + 15 protocol exclusions (boron, unsupported element for AutoDock4)
    +  5 DOCKED_GATE_FAILED (pose outside catalytic-triad gate)
    +  5 EMBED_FAILURE (no 3D embedding across all strategies)
```

| Final status | Count | Category detail |
|---|:---:|---|
| **PASS** | **458** | 448 `HISTORICAL_UNIFORM_PASS` + 10 `REMEDIATION_PASS_RAW_VINA` |
| PENDING_INDEPENDENT_REVIEW | 1 | centroid 171 (`MIXED_OR_UNRESOLVED_REQUIRES_REVIEW`) |
| PROTOCOL_EXCLUSION | 15 | boron-containing centroids; AD4 has no boron atom type |
| DOCKED_GATE_FAILED | 5 | docked poses, triad contact > 10.0 Å |
| EMBED_FAILURE | 5 | no valid 3D ligand embedding |
| **Total** | **484** | |

**Reclassification notes (vs. the pre-remediation state):**
- **373** — was a rescue-v2-layer pass; re-docked in the remediation run → `DOCKED_GATE_FAILED` (triad contact 11.34 Å > 10.0 Å). Honest downgrade, documented.
- **136 / 170** — flipped from gate-fail to `PASS_RAW_VINA` after remediation re-dock (gate verified).
- **171** — flagged `MIXED_OR_UNRESOLVED_REQUIRES_REVIEW` by the excluded-centroids audit; kept `PENDING_INDEPENDENT_REVIEW`, **excluded from promotion** until reviewed.

**Gate definition applied (all PASS records):** 28³ Å box anchored on the 2F6I chain-A catalytic triad (Ser97–His123–Asp171 per construct numbering — numbering scheme is a review-check item, §6), minimum inside fraction 0.9, maximum triad contact 10.0 Å.

---

## 2. Decision requested from the independent reviewer

The reviewer must independently determine whether the V4 replacement panel is **complete, honest, and eligible for promotion**. A signature must not be used to waive missing records or override a failed audit.

Required checks (all must be reproducible from the artifacts in §3):

1. Confirm that **2F6I** is the genuine PfClpP receptor and that **4GM2 is not used as PfClpP evidence** anywhere in the panel.
2. Verify the canonical **484-row centroid-to-SMILES mapping** and zero-based IDs.
3. Verify **PDB/PDBQT frame equivalence** and the chain-A catalytic-triad definition — **confirm the residue-numbering scheme** (construct numbering Ser97/His123/Asp171 vs. full-length numbering Ser252/His223/Asp219) and that the gate anchor matches the docked receptor frame.
4. Reproduce the declared **28 Å box** and the **composite pose gate** (inside fraction ≥ 0.9, triad contact ≤ 10.0 Å).
5. Reconcile the **complete accounting** from the final accounting CSV/JSON: 484 = 458 PASS + 1 pending + 15 boron + 5 gate-failed + 5 embed-failure.
6. Inspect the **protocol exclusion policy** (§5): 15 boron-containing centroids excluded because AutoDock4 atom types do not support boron — is this pre-specified, deterministic, and scientifically justified?
7. Inspect the 5 `DOCKED_GATE_FAILED` and 5 `EMBED_FAILURE` records — are they genuine worker failures (not silent omissions)?
8. Decide whether the 1 pending record (171) and any excluded record require a **new uniform rerun** or are resolvable by the documented policy. **No post-hoc element substitution, SMILES mutation, box relaxation, or pose translation is permitted.**
9. Complete the signature fields only if the panel is acceptable for promotion. Otherwise return `FAIL` with reasons.

---

## 3. Evidence package

| Item | Artifact | Current state |
|---|---|---|
| Canonical source | `Project2_Polypharmacology_MD_ValidationV2607/data/from_project1/data/cluster_representatives_smiles.csv` | 484 rows |
| Receptor | `Project2_Polypharmacology_MD_ValidationV2607/data/proteins/2F6I.pdb` and `data/from_project1/data/proteins/2F6I.pdbqt` | frame verification required |
| Run manifest | `results/pfclpp_2f6i_484_run_manifests.json` | historical job/provenance record |
| Uniform raw root | `results/pfclpp_2f6i_484_uniform_seed20260809/` | 484 centroid directories (jobs 13451/13452) |
| Uniform audit | `results/pfclpp_2f6i_484_uniform_aggregate_afterany/aggregation_failure.json` | 449 pass, 35 failed |
| Rescue v2 root | `results/pfclpp_2f6i_484_rescue_seed20260809_v2/` | 35 requested IDs (jobs 13478/13479) |
| Rescue audit | `results/pfclpp_2f6i_484_rescue_aggregate/rescue_audit_provenance.json` | 3 pass, 32 failed/incomplete |
| Failure inventory | `results/pfclpp_2f6i_484_failure_inventory.json` | per-category failure provenance |
| **Remediation root** | `results/pfclpp_2f6i_484_remediation_20260809/` | 35/35 records (array 15016 + aggregate 15044) |
| **Remediation summary** | `results/pfclpp_2f6i_484_remediation_20260809/c_v4_2f6i_remediation_summary.csv` | 10 PASS, 5 gate-failed, 5 embed, 15 boron |
| **Remediation provenance** | `results/pfclpp_2f6i_484_remediation_20260809/c_v4_2f6i_remediation_provenance.json` | 35 requested, 35 found, 0 missing |
| **Final accounting CSV** | `results/pfclpp_2f6i_484_final_accounting.csv` | 484 rows, per-centroid final status |
| **Final accounting JSON** | `results/pfclpp_2f6i_484_final_accounting.json` | full ID lists + gate details |
| Excluded-centroids audit | `results/pfclpp_2f6i_484_excluded_centroids_audit.json` | flags 171 as `MIXED_OR_UNRESOLVED_REQUIRES_REVIEW` |
| Gate validator | `scripts/p1_v4_validate_484_review_gate.py` | read-only, fail-closed |
| Failure inventory script | `scripts/p1_v4_inventory_484_failures.py` | deterministic, read-only derivation |

---

## 4. Layer-by-layer provenance timeline

| Layer | Jobs | Result | Status |
|---|---|---|---|
| 1. Uniform 484 run | 13451 (array) + 13452 (merge) | **449 pass / 35 failed** | ✅ audited |
| 2. Rescue sensitivity (v2) | 13478 + 13479 | **3 / 35 pass**; 32 failed or incomplete | ⚠️ sensitivity only |
| 3. Targeted remediation | 15016 (array) + 15044 (aggregate) | **10 PASS_RAW_VINA / 5 gate-failed / 5 embed / 15 boron** (35/35 accounted, 0 missing) | ✅ complete |
| 4. Final accounting | — | **484 = 458 PASS + 1 pending + 25 non-pass** | ✅ complete |

The remediation is **exploratory QC**, explicitly **not** a silent override of the uniform layer: `canonical_outputs_modified = false`. Every record is either PASS, policy-excluded with a reason, or flagged for review — nothing is dropped silently.

---

## 5. Protocol exclusion policy (pre-specified)

**Boron exclusion (15 centroids):** AutoDock4 atom types do not include boron. Boron-containing centroids cannot be parameterized in the AD4 preparation pipeline used uniformly across the panel. Exclusion is **deterministic** (element detection at preparation time), **consistent** (same policy across all runs), and **pre-specified** (not invented post-hoc for individual failures). IDs: 13, 40, 47, 73, 99, 100, 257, 358, 368, 408, 423, 435, 440, 452, 468.

**Embed failure (5):** no valid 3D ligand embedding across all attempted strategies. IDs: 30, 70, 167, 194, 361.

**Gate failure (5):** ligand docked but pose centroid outside the catalytic-triad gate (triad contact > 10.0 Å). IDs: 145, 189, 373, 390, 416 (gate metrics in the final accounting JSON).

**Pending review (1):** 171 — mixed audit signals, kept out of promotion pending reviewer decision.

---

## 6. Promotion boundary

Until the reviewer accepts a complete, reproducible panel:

- PASS records (458) are **ready for manuscript use** but the panel as a whole remains gated;
- the **1 pending record (171)** and the 25 non-pass records **must not** enter any consensus, RRS, PNS, or manuscript claim;
- the final accounting **must not** be relabelled as 484/484;
- V5/V6 registers must not be used as a substitute for this V4 review.

Current machine status:

```text
V4_REVIEW_GATE: FAIL_CLOSED_PENDING_INDEPENDENT_REVIEW
final accounting: 484 = 458 PASS + 1 PENDING + 15 BORON + 5 GATE + 5 EMBED
accepted_for_promotion: false
reviewer fields: null (awaiting independent reviewer)
```

**Pre-submission development note:** per the register's `development_policy`, this pending status does **not** block scientific reruns, QC, analysis, or manuscript development. It blocks only the *promotion of un-reviewed records into final manuscript claims* and will remain active until the author explicitly lifts submission restrictions after independent review.

---

## 7. Signature block

```text
reviewer_identity       : __________________________________________
affiliation             : __________________________________________
review_date_utc         : __________________________________________
independence_attestation: __________________________________________
conflict_declaration    : __________________________________________
V4 484-panel decision   : PASS / FAIL
  - accounting reconciled (458+1+15+5+5=484): YES / NO
  - 2F6I genuine & 4GM2 absent             : YES / NO
  - gate reproducible                      : YES / NO
  - boron policy justified                 : YES / NO
  - pending record 171 disposition         : PROMOTE / EXCLUDE / RERUN
comments                : __________________________________________
signature artifact      : __________________________________________
public-key artifact     : __________________________________________
```

The register `results/pfclpp_2f6i_484_independent_review.json` must be updated only through a verified review procedure. Non-empty fields or an automated audit do not constitute independent acceptance.
