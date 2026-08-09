# P1 V6 — Project Tracking

- **Canonical tree:** `Project1_Chem_space_antimalarial_V6_CorrectedGrid/`
- **Parent inputs:** V4 chemical-space/MPO; V5 corrected target-anchored Vina; P2 corrected RRS/polypharmacology.
- **Current phase:** V6 evidence integration completed; automated integrity audit and manuscript rebuild passed, while independent structural review remains pending for any stronger submission-facing structural conclusion.
- **Status:** `EVIDENCE_INTEGRITY_PASS_PENDING_INDEPENDENT_REVIEW`
- **Independent review:** `PENDING_INDEPENDENT_REVIEW`; no self-authorization or bypass exists.
- **V5 evidence boundary:** 17 candidates × 4 target-anchored Vina outputs are complete raw evidence (68/68 composite-gate records), imported as pending/raw evidence, not silently promoted.
- **Molecular mapping:** `MOLECULAR_KEY_VERIFIED_ROW_WISE_CANONICAL_SMILES`; V6 manifest, V5 68-row manifest, P2 source, audit hash, and validator hash are bound in the V4 overlay provenance sidecar.
- **V4 replacement boundary:** uniform 2F6I array `13451`, rescue `13478`, and associated merge/audit jobs `13452`, `13479`, and `13972` have no active scheduler entry in the current query; final accounting states are not recoverable from that query. Audit `13972` rejected the panel (449/484 raw passes, 35 worker failures); partial output is not accepted and no replacement was promoted. V4 requires a distinct review artifact for this 484-centroid panel; the V6 four-target register covers only the V5 17×4 evidence and is not a substitute.
- **RRS boundary:** PfDHFR and PfCRT mutant RRS only; no PfClpP/PfATP4 RRS claim without a validated mutant panel.
- **MD boundary:** historical parent MD systems 201/438/164/214 remain separate from the 17-candidate V6 cohort.
- **Current integrated result (9 August 2026):** 17/17 candidate identities matched by canonical SMILES; 68/68 V5 target-wise Vina records passed the automated geometric gate; consolidated-table values were consistent with raw target CSVs (204 values checked, zero mismatches); the 136-row WT/mutant panel was complete; 82 RRS values were independently recomputed with zero mean/class/value mismatches. Derived outputs include the integrated 17-row metrics table and three regenerated 300-dpi figure files. These are reproducible computational outputs, not experimental or independent structural validation.
- **Manuscript state:** V6 main, SM, and cover letter rebuilt successfully (13, 5, and 1 pages, respectively); RRS eligibility is explicitly sourced from the separate `docking_mutants.csv` panel rather than the four-target V5 WT matrix; figures are synchronized into `manuscript/Graphics/`.
- **Next gate:** rerun `scripts/v6_validate_evidence.py` after any source change, then provide the updated dossier to an independent reviewer. The register remains unsigned and fail-closed for submission-facing promotion, without blocking pre-submission scientific development.
- **Submission rule:** V6 may be drafted as a computational hypothesis-generating study, but final consensus/RRS/PNS claims require the signed independent-review artifact and accountable author approval.
