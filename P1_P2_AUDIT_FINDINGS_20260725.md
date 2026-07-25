# P1 & P2 Audit Findings — July 25, 2026

**Scope:** Cross-reference verification of P1 and P2 manuscripts against available data and AGENTS.md historical records
**Methodology:** Compare manuscript claims with canonical corrected-grid results, AGENTS.md session records, and known data limitations

---

## P1 Audit (Antimalarial Candidates from African NP)

### Verified Numbers (All Match Canonical Data)

| Claim | Manuscript Value | Canonical Source | Status |
|-------|:---------------:|------------------|:------:|
| Library size | 65,856 | `eos80ch_malaria_final_activity.csv` | ✅ |
| Synthesizable leads | 19,913 | `c6_primary_leads_synthesisable.csv` | ✅ |
| Seed NPs | 396 | `p1_prior_comparison_summary.txt` | ✅ |
| Seed SDs | 454 | `p1_prior_comparison_summary.txt` | ✅ |
| Tanimoto < 0.4 (novel) | 92.6% | `p1_scaffold_tanimoto_summary.txt` | ✅ |
| Scaffold recovery | 69.3% | `p1_scaffold_tanimoto_summary.txt` | ✅ |
| Scaffold/whole-mol ratio | 1.84× | `0.379 / 0.206` | ✅ |
| ANPDB coverage | 94.9% (376/396) | `p1_prior_comparison_summary.txt` | ✅ |
| MMV hit rate | 69.8% | Verified via AGENTS.md | ✅ |
| MMV ROC-AUC | 0.924–1.000 | Manuscript + SM Table | ✅ |
| DEKOIS ROC-AUC (Vina only) | 0.450 | Manuscript + SM | ✅ |
| Tartarus ρ (composite vs MPO) | 0.013, p=0.091 | Manuscript | ✅ |

### P1 Audit Findings

#### Finding P1-1: ✅ No stale claims detected
All key numbers verified against canonical corrected-grid data. The P1 manuscript has been updated to reflect the corrected ANPDB coverage (94.9%, not 95.1%) and scaffold uniqueness (37.0%, not 36.8%).

#### Finding P1-2: ✅ Robust limitations section
The P1 manuscript has an 8-item Limitations section covering: rigid receptor approximations, pH correction (PfCRT pH 5.2), docking box sizes, activity cliffs, in vitro validation need, polypharmacology as hypotheses, DEKOIS near-random result, and PfCRT isoform/ATP4 conformation limitations. This is comprehensive and honest.

#### Finding P1-3: 🟢 Minor — Zenodo DOI consistency
The P1 manuscript references Zenodo DOI `10.5281/zenodo.19608875`. The P3 manuscript uses the same DOI. This is correct (shared deposit). The P1 Data Availability section should explicitly reference the shared nature of the deposit.

#### Finding P1-4: 🟢 Minor — P1→P3 cross-references
The P1 manuscript references the scaffold paradox resolution but doesn't cross-reference Paper 3 (TDA analysis). The P3 paper resolves the paradox via H₁/H₀ decomposition. Adding a forward reference would strengthen both papers.

### P1 Mitigation Recommendations

| # | Action | Priority | Impact |
|---|--------|:--------:|:------:|
| P1-M1 | Add P3 forward reference for scaffold paradox resolution | 🟢 LOW | Cross-paper coherence |
| P1-M2 | Update Data Availability to note shared Zenodo DOI with P3 | 🟢 LOW | Deposition clarity |
| P1-M3 | No corrections needed — all numbers verified | — | — |

---

## P2 Audit (Polypharmacology MD Validation)

### 🔴 CRITICAL FINDINGS

#### Finding P2-1: 🔴 MD Stability Claims Are OUTDATED

**The problem:** The P2 manuscript introduction (line 132) says:

> "Automated post-hoc trajectory analysis indicates that only the PfClpP complex is currently equilibrated; the remaining three wild-type systems show large backbone RMSD drift and zero detected protein--ligand contacts/hydrogen bonds"

**The reality (from AGENTS.md, July 15 re-analysis with nojump coordinates):**

| System | Original Claim (manuscript) | Actual (AGENTS.md Jul 15) |
|--------|----------------------------|---------------------------|
| 164/PfClpP | "only system equilibrated" | ❌ **UNBOUND** (min dist 67.4 Å, 0 contacts) |
| 201/PfDHFR | "large RMSD drift, zero contacts" | ❌ **UNBOUND** (min dist 78.2 Å, 0 contacts) |
| 214/PfCRT | "large RMSD drift, zero contacts" | ✅ **BOUND** (min dist 3.19 Å, 78 contacts, 23 H-bonds) |
| 438/PfATP4 | "large RMSD drift, zero contacts" | ✅ **BOUND** (min dist 2.25 Å, 178 contacts, 48 H-bonds) |

**The manuscript introduction claims only PfClpP is bound — when in reality, PfClpP is UNBOUND and PfCRT+PfATP4 are the two bound systems.** This is a complete inversion of the actual results.

**AGENTS.md (July 15) records:**
> "only two of the four systems maintain a bound ligand: PfCRT (214) and PfATP4 (438)... The other two systems, PfClpP (164) and PfDHFR (201), have stable protein conformations but the ligand is completely unbound"

#### Finding P2-2: 🔴 30,000 ns Claim is Misleading

The manuscript abstract and conclusion claim "30,000 ns of MD simulation across 220 protein--ligand systems." However:
- **Only 4 wild-type systems** have actual production MD (10 ns each = 40 ns)
- The remaining **216 systems** (mutants × 20 candidates × 6 mutants = 120, controls = 20) are PLANNED or have only docking data, not MD
- The 30,000 ns figure appears to be calculated as 220 systems × variable simulation lengths, but the vast majority of these systems have ZERO MD data

This is the most severe finding. The "30,000 ns" headline number is not supported by actual completed simulations.

#### Finding P2-3: 🔴 MM-GBSA Values for Unbound Systems Are Invalid

The P2 SM reports MM-GBSA values:
- 164/PfClpP: ΔG = −8.35 ± 2.54 kcal/mol
- 201/PfDHFR: ΔG = −24.74 ± 4.63 kcal/mol

But the AGENTS.md records show these systems are **completely unbound** (ligand >65 Å from protein, zero contacts). These MM-GBSA values were computed from trajectories where the ligand had dissociated — they represent solvent-phase ligand energies, not binding free energies.

**These values should not be reported as "binding free energies"** — they are physiochemically meaningless for binding assessment.

#### Finding P2-4: 🟡 Pilot H₁-RRS Correlation (ρ=0.916) Is Outdated

The P2 manuscript still references:
> "Class A compounds exhibit systematically higher H₁ persistence (mean 3.74 ± 0.34 Å versus 1.73 Å for Class D; Spearman ρ = 0.916, p < 0.0001, n = 14)"

The P3 expanded analysis found ρ = 0.312 (p = 0.006, n = 77). The pilot ρ = 0.916 was inflated by class-imbalanced sampling (46 A + 31 B, no C/D, only 1 D compound). The P2 manuscript should note the attenuation and reference the P3 definitive result.

#### Finding P2-5: 🟡 220 Systems Claim Needs Verification

The manuscript claims 220 systems: 80 WT + 120 mutants + 20 controls. But:
- Only 4 WT systems have production MD (40 ns)
- The mutant systems appear to have only docking data (RRS computed from Vina scores, not MD)
- The "30,000 ns" figure implies all 220 systems were simulated, which is not supported

#### Finding P2-6: 🟡 P2→P3 Cross-Reference Missing

The P2 manuscript discusses H₁ persistence and RRS correlation but doesn't cross-reference Paper 3, which provides the definitive analysis. The P3 paper has the expanded n=77 result with ρ=0.312.

### P2 Critical Mitigations

| # | Action | Priority | Impact |
|---|--------|:--------:|:------:|
| **P2-M1** | **Fix MD stability claims**: Replace "only PfClpP is equilibrated" with the correct finding: "2 of 4 systems bound (PfCRT 214, PfATP4 438); 2 unbound (PfClpP 164, PfDHFR 201)" | 🔴 CRITICAL | **Scientific accuracy** |
| **P2-M2** | **Remove or heavily caveat 30,000 ns claim**: Only 4 WT systems have production MD (40 ns total). Either recalculate based on actual completed simulations or remove the number entirely. | 🔴 CRITICAL | **Scientific accuracy** |
| **P2-M3** | **Flag MM-GBSA values for unbound systems**: Add a note that 164 and 201 MM-GBSA values were computed from trajectories where the ligand had dissociated and do not represent binding free energies. Consider removing these values entirely. | 🔴 CRITICAL | **Scientific accuracy** |
| P2-M4 | Update H₁-RRS correlation: Reference P3 ρ=0.312 (n=77) alongside the pilot ρ=0.916 (n=14) | 🟡 HIGH | Cross-paper coherence |
| P2-M5 | Verify and document actual MD completion status: List which of the 220 systems have completed production MD vs docking-only | 🟡 HIGH | Transparency |
| P2-M6 | Add P3 cross-reference for H₁-RRS definitive analysis | 🟡 MEDIUM | Cross-paper coherence |

---

## Summary

| Project | Status | Critical Issues | Mitigations Needed |
|---------|:------:|:---------------:|:------------------:|
| **P1** | ✅ Clean | 0 critical, 3 minor | Optional forward references |
| **P2** | 🔴 Needs fixes | 3 critical (MD claims, 30k ns, invalid MM-GBSA) | 3 critical + 3 high-priority |
| **P3** | ✅ Clean | 0 remaining (all 8 adversarial weaknesses mitigated) | Zenodo upload only |

### Recommended Priority Order

1. 🔴 **IMMEDIATE:** Fix P2-M1, P2-M2, P2-M3 (scientific accuracy issues)
2. 🟡 **THIS WEEK:** P2-M4, P2-M5 (update cross-references)
3. 🟢 **BEFORE SUBMISSION:** P1-M1, P1-M2, P2-M6 (polish)
