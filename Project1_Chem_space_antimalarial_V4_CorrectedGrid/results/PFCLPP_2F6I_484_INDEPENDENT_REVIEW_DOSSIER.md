# P1 V4 — Independent review dossier for the 484-centroid 2F6I panel

**Version:** 2.1 (2026-08-10) — supersedes v1 (pre-remediation) and v2.0 (final accounting) ; v2.1 adds §8 signature procedure (openssl/gpg + payload) and §9 validation record (positive + tamper + wrong-key controls all PASS)
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

---

## 8. Signature application procedure (openssl/gpg + apply script)

The reviewer signs an **immutable JSON payload**; the register is updated only by
the verified gate-opener `scripts/p1_v4_apply_review_signature.py` (fail-closed,
no bypass). The script binds the review to the **final accounting**
(`results/pfclpp_2f6i_484_final_accounting.json` + `.csv` : 484 rows, IDs 1–484,
`final_counts` summing to 484, canonical SMILES hash) — **not** to the obsolete
uniform-run aggregate (467 records), which cannot serve as review target.

### 8.1 Reviewer key generation (one time)

```bash
cd Project1_Chem_space_antimalarial_V4_CorrectedGrid/results
# Ed25519 key pair (openssl)
openssl genpkey -algorithm ed25519 -out reviewer_ed25519_private.pem
openssl pkey -in reviewer_ed25519_private.pem -pubout -out reviewer_ed25519_public.pem
# OR gpg alternative
# gpg --generate-key  &&  gpg --export --armor > reviewer_public.asc
# Fingerprint of the public key (trust anchor):
sha256sum reviewer_ed25519_public.pem
```

The public-key SHA-256 and the reviewer identity must be delivered to the author
by a **separate trusted channel** (not the same commit as the register) and set
as environment anchors before running the apply script:

```bash
export P1_TRUSTED_REVIEWER_PUBKEY_SHA256=<sha256-of-public-key>
export P1_TRUSTED_REVIEWER_IDENTITY="<reviewer identity exactly as in payload>"
```

### 8.2 Reviewer payload (immutable JSON, signed)

```bash
cat > v4_484_review_payload.json <<'JSON'
{
  "schema": "p1-v4-pfclpp-2f6i-484-review/v2",
  "target": "PfClpP",
  "pdb_id": "2F6I",
  "panel_size": 484,
  "reviewer_identity": "<IDENTITÉ_DU_RELECTEUR>",
  "review_date_utc": "2026-XX-XXT00:00:00+00:00",
  "review_decision": "PASS",
  "accepted_for_promotion": true,
  "reviewer_independence_attestation": true,
  "conflict_of_interest_declaration": "<explicit declaration>",
  "authorization_mode": "INDEPENDENT_REVIEW_REQUIRED",
  "internal_work_authorized": false,
  "current_accounting_artifact": "<abs-path>/results/pfclpp_2f6i_484_final_accounting.json",
  "current_accounting_sha256": "<sha256>",
  "current_accounting_csv_artifact": "<abs-path>/results/pfclpp_2f6i_484_final_accounting.csv",
  "current_accounting_csv_sha256": "<sha256>",
  "current_accounting_records": 484,
  "evidence": {"canonical_smiles_sha256": "<sha256-of-cluster_representatives_smiles.csv>"},
  "review_criteria": {
    "genuine_pfclpp_identity_2f6i": true,
    "all_484_centroid_inputs_bound_to_canonical_smiles": true,
    "pdb_pdbqt_frame_equivalence_verified": true,
    "target_specific_triad_box_reviewed": true,
    "final_accounting_reconciled_484": true,
    "protocol_exclusions_verified": true,
    "gate_and_embed_failures_verified": true,
    "final_accounting_reproducible_from_artifacts": true,
    "independent_reviewer_acceptance": true
  }
}
JSON
```

Hash placeholders can be filled with:

```bash
sha256sum results/pfclpp_2f6i_484_final_accounting.json
sha256sum results/pfclpp_2f6i_484_final_accounting.csv
sha256sum Project2_Polypharmacology_MD_ValidationV2607/data/from_project1/data/cluster_representatives_smiles.csv
```

### 8.3 Sign (detached) and verify

```bash
cd Project1_Chem_space_antimalarial_V4_CorrectedGrid/results
# hash the pre-signature payload
sha256sum v4_484_review_payload.json
# sign (detached, Ed25519)
openssl pkeyutl -sign -inkey reviewer_ed25519_private.pem -rawin \
    -in v4_484_review_payload.json -out v4_484_review_payload.json.sig
# independent verification with the public key
openssl pkeyutl -verify -pubin -inkey reviewer_ed25519_public.pem -rawin \
    -in v4_484_review_payload.json -sigfile v4_484_review_payload.json.sig
# gpg alternative: gpg --detach-sign v4_484_review_payload.json
```

### 8.4 Apply (register update only after full verification)

```bash
cd Project1_Chem_space_antimalarial_V4_CorrectedGrid
python scripts/p1_v4_apply_review_signature.py \
    --payload results/v4_484_review_payload.json \
    --sig results/v4_484_review_payload.json.sig \
    --pubkey results/reviewer_ed25519_public.pem
# expected: "V4 review applied" / status=INDEPENDENT_REVIEW_ACCEPTED accepted_for_promotion=true
```

The script fails closed (register untouched) on: bad signature, unbound public key
or identity, missing fields, non-PASS decision, missing criteria, accounting hash
mismatch, or any residual reference to the obsolete uniform audit. Tested on a
copy with a negative tamper control (see §9).

> **Portability note:** the payload binds absolute repository paths
> (`current_accounting_artifact` / `current_accounting_csv_artifact`). A reviewer
> working on a different checkout path will fail closed — the payload paths must
> match the HPC absolute paths. This is an intentional fail-closed trade-off.
> The script additionally verifies internal consistency between the final
> accounting CSV status distribution and the JSON `final_counts` (v2.1.1).

---

## 9. Procedure validation record (2026-08-10, on copies only)

Executed on `/tmp` copies (never the real register) to prove the signing path
works end-to-end with the final-accounting binding:

| Check | Procedure | Expected | Observed |
|---|---|---|---|
| Positive control | valid payload + Ed25519 signature + bound key + trust anchors | `INDEPENDENT_REVIEW_ACCEPTED`, `accepted_for_promotion=true`, register updated | ✅ RC=0, register → `INDEPENDENT_REVIEW_ACCEPTED` / `true` |
| Negative control (tamper) | valid signature on a **modified** payload (`current_accounting_records` 484→483) | FAIL-CLOSED, register untouched | ✅ RC=1, `FAIL-CLOSED: signed payload final-accounting record count is not 484`; register remains `PENDING_INDEPENDENT_REVIEW` / `false` |
| Negative control (bad key) | public key not bound to trust-anchor fingerprint | FAIL-CLOSED | ✅ RC=1, `FAIL-CLOSED: detached V4 signature verification failed`; register untouched |

This procedure validation is machine evidence for the reviewer; it does not
substitute for the independent review itself.
