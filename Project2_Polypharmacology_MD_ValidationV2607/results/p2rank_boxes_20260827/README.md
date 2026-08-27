# P2Rank independent pocket validation — 27 August 2026

**Tool:** P2Rank 2.5.1 (rdk/p2rank, https://github.com/rdk/p2rank), Java 17 (`conda env jdk17`), extracted to `/home/nanaengo/software/p2rank_2.5.1/`.

**Purpose:** independent, machine-learning-based ligandable-pocket prediction on the four P2 receptors, compared with the fixed Vina grid boxes used for docking (receptor-boundary audit; answers "how were the grid boxes chosen?").

## Inputs

| Receptor | Target | PDB used | Frame note |
|---|---|---|---|
| 7F3Y | PfDHFR | `results/md_systems/set_c_preparation_20260812_v1/PP-01_PfDHFR_WT/receptor_fixed.pdb` | MD-prepared frame |
| 6UKJ | PfCRT | `.../PP-01_PfCRT_WT/receptor_fixed.pdb` | MD-prepared frame |
| 9N10 | PfATP4 | `data/from_project1/docking/Docking_9N10/9N10.pdbqt` → ATOM lines | docking frame |
| 2F6I | PfClpP | `data/proteins/2F6I.pdb` | raw frame; no P2 Vina grid exists for 2F6I (ClpP docking was run in P1 V4/V7) |

## Vina grid boxes (from `data/from_project1/docking/Docking_*/config.txt`)

| Receptor | center (x, y, z) | size (Å) |
|---|---|---|
| 7F3Y | (1.33, -1.733, -23.842) | 25³ |
| 6UKJ | (152.99, 151.042, 159.379) | 25³ |
| 9N10 | (134.84, 133.10, 97.63) | 25³ |

## P2Rank top-3 pockets and distance to the Vina box center

### 7F3Y (PfDHFR)
| pocket | score | prob | center (x,y,z) | dist to Vina box (Å) |
|---|---|---|---|---|
| pocket1 | 44.90 | 0.972 | (0.08, 33.43, -4.59) | 40.1 |
| pocket2 | 44.35 | 0.972 | (0.80, -5.21, -62.36) | 38.7 |
| pocket3 | 36.73 | 0.956 | (-12.01, -15.01, -6.72) | 25.5 |

### 6UKJ (PfCRT) — concordance forte
| pocket | score | prob | center (x,y,z) | dist to Vina box (Å) |
|---|---|---|---|---|
| **pocket1** | **162.66** | **0.999** | (151.18, 152.11, 154.09) | **5.7** |
| pocket2 | 28.73 | 0.927 | (152.13, 169.25, 137.73) | 28.3 |
| pocket3 | 8.11 | 0.431 | (164.64, 155.95, 164.00) | 13.5 |

### 9N10 (PfATP4)
| pocket | score | prob | center (x,y,z) | dist to Vina box (Å) |
|---|---|---|---|---|
| pocket1 | 12.82 | 0.663 | (115.86, 133.94, 121.49) | 30.5 |
| pocket2 | 11.42 | 0.610 | (127.00, 118.53, 140.07) | 45.6 |
| pocket3 | 8.07 | 0.429 | (125.24, 129.52, 76.56) | 23.4 |

### 2F6I (PfClpP) — top pockets, frame-independent (no P2 grid to compare)
| pocket | score | prob | center (x,y,z) |
|---|---|---|---|
| pocket1 | 6.05 | 0.299 | (20.06, 16.76, 1.72) |
| pocket2 | 5.50 | 0.262 | (-7.89, 67.46, 24.52) |
| pocket3 | 5.10 | 0.233 | (-14.04, 51.67, 8.35) |

## Interpretation (honest, with caveats)

1. **PfCRT (6UKJ):** the top P2Rank pocket is by far the most ligandable site (score 162.7, prob 0.999, >5× the second pocket) and its center lies **5.7 Å** from the Vina box center — well inside the 25 Å box. Independent corroboration of the docking box.
2. **PfDHFR (7F3Y):** P2Rank top pockets lie 25–40 Å from the Vina box center. Frame mismatch is possible (the `config.txt` was generated in the P1 docking workflow, possibly on a different receptor preparation than `receptor_fixed.pdb`); this comparison is therefore **not a clean refutation or confirmation**. It flags a provenance caveat for the 7F3Y box, not a docking-quality verdict.
3. **PfATP4 (9N10):** top pockets 23–46 Å from the box center; same frame caveat as 7F3Y. The 9N10 input was derived from the docking PDBQT, so the frame should match — the 23–30 Å separations indicate the box may not coincide with the strongest predicted pockets, worth a manual recheck of the 9N10 pocket definition.
4. **PfClpP (2F6I):** low scores (≈5–6) and low probabilities (0.23–0.30) — the raw 2F6I structure presents weak pocket signals to P2Rank; the P1 V4 2F6I remediation used a curated box. Frame-independent report only.

**Status:** `COMPUTED_EXPLORATORY_BOUNDARY_AUDIT`. Not a docking-quality metric; does not change any canonical score, RRS classification, or manuscript claim. Raw outputs: `*_predictions.csv`, `*_residues.csv` in `out/`.
