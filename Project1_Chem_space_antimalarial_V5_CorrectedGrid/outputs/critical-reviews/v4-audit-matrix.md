# V4 Audit Matrix — verified against V4 actual files (2026-07-26)

**Method:** every item checked against V4's own `.tex`, `scripts/`, and data CSVs — NOT the
V3 tracking file (recorded against a different tree; was wrong once before).
**Data backbone:** `BMAD_Q1_DATA_ANALYSIS_REPORT.md` (parent folder) — authoritative per user.
**Principle:** trace every number to its source CSV + the report; new calculations only if a
contradiction is found; never invent a substitute to fill a gap (feedback memory).

## A. Numbers verified SOUND (trace to source, no action)

| Number | V4 location(s) | Source verified | Verdict |
|---|---|---|---|
| 65,856 | main 72,91,126,208,258; SM 92,177,208 | §1.8c (65,006->65,856 FIXED); eos/eos7kpb files | sound |
| 484 centroids | main 91,117,126,138,166,208,242,258; SM 177,178,363,921,941 | `v2_centroid_scores.csv` = 484 rows | sound |
| **76** (MPO>=0.40 centroids) | main 208,210,258,294; SM 180,181,190,202,326,365 | real weighted-MPO; floored proxy yields 483 not 76, so 76 != proxy; r8b top-20 centroid_MPO 0.770-0.823 | **sound -- NOT the floored proxy** |
| 53 unique clusters | main 208,258,281,287; SM 181,202 | canonical (§8) | sound |
| 40,481 expanded | main 177,208,258; SM 181,202 | canonical (§8); 53*763.8=40,481 | sound |
| 763.8 mean cluster size | main 177,258,281,287,319; SM 181 | 40481/53 | sound |
| **19,913** synthesizable leads | main 72,93,208,260,281,287,303,305,309,319; SM 181,202 | **`c6_primary_leads_synthesisable.csv` = 19,913 rows** (input,weighted_mpo_score,syba_score,sa_score,qed) | **sound -- NOT a hand-rescale** |
| 810 / 100% SI>10 | main 72,93,210,260,281,287; SM | **`c3_selectivity_index.csv` = 810 rows, all SI>10** (min 10.02, median 282.7, **max 106,773.8**); §1.4 | numerically true (BUT see C3 framing) |
| 396 seed NPs / 454 synth | main 72,91,93,126,208 | §1.2 | sound |
| 13 NP-related / 63 non-NP (of 76) | main 210,294; SM 190 | 13+63=76 | internally consistent |
| 7 secondary hits / 69 promising | main 210; SM 180 | 7+69=76 | internally consistent |
| MPO weight-sensitivity (S17) | SM 202, 585-635 | `p1_mpo_sensitivity.py`; §1.6 (ADMET rho->0.258) | sound (legit weight perturbation, NOT floored threshold sweep) |
| DEKOIS AUC 0.450 | main 72,134,216,265,281,311,317,319 | §1.8c | sound |
| MMV ROC 0.924-1.000 | main 72,93,126,216,265,281,317 | §1.8c (positive-control) | sound |
| pH 5.2 PfCRT rho=0.270, +2.2 kcal/mol | main 311 | §1.10 | sound |
| Tartarus orthogonality rho=0.013 (n=17,211) | main 305 | §5 | sound |
| MCMC +0.0246, top 0.801, R2=0.377 | main 119-121,317; §1.8b | §1.8b | sound |

## B. The S24 CRITICAL defect -- RESOLVED in V4

- No "483" anywhere in V4 SM. The bogus threshold-sweep table (`epic2_analysis.py:237`
  `MPO_proxy = 0.60*S_vina + 0.40`, flooring every centroid at 0.40 -> 483/484) is GONE.
- The floored `epic2_analysis.py` is not present in V4/scripts.
- Replaced by the legitimate weight-perturbation sensitivity table (`tab:sm_s17_mpo_sensitivity`).
- The non-independence caveat (§1.8c issue #4) SURVIVED into V4 -- SM line 198 states
  Vina/DiffDock are back-calculated from the shared residual (35:25 split) because per-molecule
  scores were not retained; QED/ADMET/Ro5 are true independent variation.
- **S24 blocker cleared. 76 is sound. Residual reproducibility disclosure already present (SM 198).**

## C. Fixes already APPLIED in V4 (verified, no action)

| ID | Fix | V4 evidence |
|---|---|---|
| C1 | MMV decoy definition explicit | main 134 (DEKOIS 40 actives/1200 decoys; MMV 399 actives) |
| C2 | MMV reframed as positive-control | main 126 ("used here as a positive-control benchmark") |
| C4 | DEKOIS consensus-not-applied explained | main 134 ("single-method, no ML rescoring"); 216,311,317,319 |
| C6 | MCMC surrogate weakness + NN decoding disclosed | main 119-121 (R2=0.377, nearest-neighbour, "modest") -- residual: subsection title still "optimization" |
| F1 | V2 corrected PfDHFR grid | main 138 (8.340, -13.900, -41.754) |
| F2 | MTX RMSD ~30 A reframed as Vina limitation | main 216 |
| F4 | Title does not overstate polypharmacology | main 65 (neutral title) -- no change needed |
| 65,006->65,856 | Library size fix | §1.8c; V4 consistent at 65,856 |
| S24 (483 table) | Removed | see section B |
| Anti-AI SM 1532 | "robust to the precise MPO threshold" | disappeared with the bogus table |

## D. Confirmed MISSING in V4 -- NEEDS FIX (no new calculations)

| ID | Finding | V4 location | Fix |
|---|---|---|---|
| **C3** | SI_pred headlined as "100% selectivity / favorable predicted selectivity / therapeutic window" without "unvalidated prioritization heuristic" labeling. Max SI 106,773.8 shows DILI->1 inflation. Data TRUE (810/810>10); fix is FRAMING. | abstract main 72,93; results 210,260,281,287 | Label SI_pred as an unvalidated prioritization heuristic, not a true SI surrogate; soften "therapeutic window"; keep 810/100% as a reported result. |
| **C5** | "validated discovery of multiple antimalarial leads" | main 321 (Conclusion) | Replace with "computational prioritization" / "prioritized set of antimalarial leads". |
| **DOCK-1** | 67 NaN + 4 non-negative = 71/1,936 (3.7%) failed centroid dockings, undisclosed. Per-target NaN: pfDHFR 33, pfCRT 17, pfClpP 16, pfATP4 1. | nowhere | Add disclosure sentence to SM docking methods (+ optional main). Numbers verified from `v2_centroid_scores.csv`. |
| **Anti-AI** | (a) Cover Letter 35 "We demonstrate that 92.6%..."; (b) main 321 "offers a scalable solution" (+ same line has C5) | Cover_Letter.tex:35; main:321 | Reword both per anti-ai-writing. |

## E. Recommended (not blockers) -- author judgment

| ID | Finding | Status | Suggested action |
|---|---|---|---|
| C6-residual | MCMC subsection title still "Latent space optimization by MCMC sampling" | partial | Soften "optimization" -> "exploration" (body already honest). |
| F3 | Consensus-illusion Discussion paragraph absent (2.7% of centroids select PfDHFR; 0.924 reflects DiffDock compensating for Vina's per-target weakness). Data: pfCRT 421 (87%), pfATP4 49 (10.1%), pfDHFR 13 (2.7%). | missing | Add 2-3 sentence Discussion paragraph to preempt the reviewer who notices 87% of hits are PfCRT. |
| S23-1 / H1 | Confounded "44-fold CH" ECFP4-vs-VAE comparison REMOVED (good), BUT `tab:vae_comparison` (SM 853-876) is now ALL "N/A" (loss, KL, recon accuracy, Sil, CH, DB) and selected 64D KMeans row in `tab:clustering_comparison` (SM 941) is "N/A". VAE/clustering now under-characterized. | partial -- gutted | Either restore real values from VAE training logs (`32/64_smi_vae_training_history_full.pdf` exist, need numeric source) or reframe table. **Do NOT fabricate.** May need co-author. |
| Epic 3 (M2/M3/M5) | Tanimoto sensitivity curve; generated-vs-seed activity reframe; ASKCOS synthesizability softening | not started | MEDIUM -- optional for JCIM fresh submission. |

## F. Author-action items (need user confirmation)

| ID | Item | Detail |
|---|---|---|
| H5 | GitHub URL | Manuscript uses `github.com/Vital-Sao/Malaria_codes` (main 283,341; SM 75,718); README + .tex author line (Serge Guy Nana Engo) point at `NanaEngo` account. Confirm which is publicly accessible. |
| AI-use | AI-use disclosure | Add one sentence to Acknowledgments per ACS/JCIM policy if AI tools were used in preparation. |

## G. V4 vs V3 tree difference (why re-verification was mandatory)

V4 was copied from V2 *after a co-author updated it* -- it is NOT V3+fixes. The V3 tracking
file's "done" marks (recorded against V3) do not transfer. Verified result: most C1-C6/F1-F2
fixes ARE in V4, but C3 and C5 are NOT. This is exactly the "tracking-file status is a claim
to verify" lesson from the 2026-07-26 S24 audit.

## H. Audit artifacts NOT yet carried from V3 to V4 (optional now)

- `scripts/s24_vina_threshold_sweep.py`
- `outputs/epic2/s24_vina_absolute_sweep.csv`, `s24_vina_normalised_sweep.csv`, `s24_centroid_best_vina.csv`
- Optional now (the bogus table they counter is gone), but useful as reproducibility evidence.
