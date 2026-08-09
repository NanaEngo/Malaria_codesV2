# P1 V6 — Project Tracking

- **Canonical tree:** `Project1_Chem_space_antimalarial_V6_CorrectedGrid/`
- **Parent inputs:** V4 chemical-space/MPO; V5 corrected target-anchored Vina; P2 corrected RRS/polypharmacology.
- **Current phase:** V6 evidence integration and automated integrity audit; V5 molecular mapping resolved, V4 2F6I replacement pending.
- **Status:** `EVIDENCE_INTEGRITY_PASS_PENDING_INDEPENDENT_REVIEW`
- **Independent review:** `PENDING_INDEPENDENT_REVIEW`; no self-authorization or bypass exists.
- **V5 evidence boundary:** 17 candidates × 4 target-anchored Vina outputs are complete raw evidence (68/68 composite-gate records), imported as pending/raw evidence, not silently promoted.
- **Molecular mapping:** `MOLECULAR_KEY_VERIFIED_ROW_WISE_CANONICAL_SMILES`; V6 manifest, V5 68-row manifest, P2 source, audit hash, and validator hash are bound in the V4 overlay provenance sidecar.
- **V4 replacement boundary:** uniform 2F6I array `13451` runs in V4; merge `13452` is `afterok`, audit `13972` is `afterany`; partial output is not accepted.
- **RRS boundary:** PfDHFR and PfCRT mutant RRS only; no PfClpP/PfATP4 RRS claim without a validated mutant panel.
- **MD boundary:** historical parent MD systems 201/438/164/214 remain separate from the 17-candidate V6 cohort.
- **Next gate:** rerun `scripts/v6_validate_evidence.py` after any source change, then provide the updated dossier to an independent reviewer. The register remains unsigned and fail-closed.
- **Submission rule:** V6 may be drafted as a computational hypothesis-generating study, but final consensus/RRS/PNS claims require the signed independent-review artifact and accountable author approval.
