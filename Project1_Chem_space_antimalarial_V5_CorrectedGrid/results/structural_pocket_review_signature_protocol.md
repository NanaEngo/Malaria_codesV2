# V5 independent structural-pocket review — signature protocol

This protocol defines what a future reviewer must provide before any DiffDock full-run authorization can be considered.

## Required artifacts

1. `structural_pocket_independent_review.json`
   - `status = STRUCTURAL_POCKET_REVIEWED_AND_ACCEPTED`
   - non-empty `reviewer_identity`
   - `review_date`
   - `signed_review_artifact`
   - `signed_review_sha256`
   - all four target decisions = `PASS`
   - all acceptance criteria = `true`
2. A detached signature file for the review JSON, generated with a trusted institutional/private key.
3. The corresponding trusted public key or certificate, supplied through a separately reviewed provenance channel.

## Verification requirements

The full-run gate must verify:

- SHA-256 of the review JSON;
- SHA-256 of the detached signature;
- the detached signature against the review JSON using the pinned trusted public key/certificate;
- reviewer identity and review date;
- target-specific PASS decisions for PfDHFR, PfCRT, PfClpP, and PfATP4;
- exact receptor/grid/smoke hashes.

A matching SHA-256 alone is **not** a digital signature and cannot establish reviewer independence.

## Current status

No reviewer identity, signed review, public key, or acceptance decision exists in the repository. The current register is intentionally `PENDING_INDEPENDENT_REVIEW`; the 68-pair run remains blocked.
