# External docking protocol reconciliation — 27 August 2026

## Resolution

The apparent 20 Å/25 Å discrepancy is resolved in favor of the audited executable V2 configuration:

- AutoDock Vina 1.2.7;
- exhaustiveness 64;
- 25 × 25 × 25 Å boxes;
- target-specific centers from the versioned V2 configuration files.

The 20 Å wording was an obsolete manuscript sentence and must not govern the external replication. Historical runs using exhaustiveness 128 and/or other box dimensions remain historical and are not silently merged.

## Execution boundary

This reconciliation does not itself authorize or imply completion of docking. The external array remains governed by its live scheduler state and the fail-closed aggregation gate. RRS is `NOT_COMPUTED` until all 320 expected ligand-state outputs are present, finite, and hash-audited.
