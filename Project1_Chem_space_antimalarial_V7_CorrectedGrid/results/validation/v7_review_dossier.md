# V7 Evidence-Integrity Review Dossier

- Automated status: `AUDIT_WARN_REVIEW_REQUIRED`
- Pre-submission editorial restrictions: **INACTIVE**
- Independent review status: `PENDING` (truthful provenance; not an execution block)
- Future submission-facing acceptance: `false`

## Scope

This dossier checks file integrity, schema, counts, target metadata, canonical-SMILES cohort identity, and the hashes declared by the raw per-target Vina outputs. It does not certify biological validity, experimental binding, or independent scientific acceptance. Scientific development may continue; only explicit author reactivation can activate future submission-facing review controls.

## Target evidence

- **PfDHFR (7F3Y)** — decision `EVIDENCE_COMPLETE_AWAITING_REVIEW`; anchor: MTX catalytic-site copy A702 (33 atoms, centroid [-3.596, -5.249, -58.677])
- **PfCRT (6UKJ)** — decision `EVIDENCE_COMPLETE_AWAITING_REVIEW`; anchor: Y01 (cholesterol hemisuccinate) A501 — membrane-mimetic PROXY, not an inhibitor
- **PfClpP (2F6I)** — decision `EVIDENCE_COMPLETE_AWAITING_REVIEW`; anchor: Chain A catalytic triad Ser252/His223/Asp219 (centroid [-24.276, 17.28, -2.901])
- **PfATP4 (9N10)** — decision `EVIDENCE_COMPLETE_AWAITING_REVIEW`; anchor: Conserved P-type ATPase catalytic machinery: phospho-site CSDKTGT -> D451 (resi 449-458) + A-domain hinge DPPR (751-754), centroid [122.712, 125.545, 91.411]

## Automated findings

- No automated integrity errors detected.
- WARNING: `INDEPENDENT_REVIEW_PENDING: automated audit cannot authorize downstream claims`
- WARNING: `RRS_V5_JOIN_VERIFIED_BY_CANONICAL_SMILES`

## Human reviewer action

Scientific development may continue from these artifacts. If the author later explicitly reactivates submission/review restrictions, inspect the raw structures, poses, configurations, and hashes independently, then create the signed artifact specified in `docs/INDEPENDENT_REVIEW_PROTOCOL.md`. This script cannot sign the register or simulate acceptance.
