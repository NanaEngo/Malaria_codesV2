# Adversarial Peer Review — V4 (Corrected Grid), 2026-07-26

**Reviewer stance:** skeptical senior JCIM reviewer looking for the weakest arguments,
unsupported claims, circular reasoning, overclaiming beyond the data, weak causal links,
and result–claim mismatches. Numbers below were re-derived from the V4 `.tex` files
(main `Antimalarial_Candidates_African_NP_V2607.tex`, SM `..._SM.tex`, `Cover_Letter.tex`)
and cross-checked arithmetically. Items already fixed on 2026-07-26 (S24, C3 framing,
C5 Conclusion wording, DOCK-1, anti-AI main-text prose, C6 subsection title, F3
Limitations caveat, AI-use disclosure) are NOT re-flagged here; only residuals and new
issues are reported.

**Headline verdict:** The manuscript's central validation is partly tautological, the one
genuine external benchmark fails, and the gap between them is bridged by an unsupported
causal claim. Several headline novelty numbers are either near-trivial, misattributed, or
internally inconsistent. As written, a methodologically literate JCIM reviewer will likely
recommend major revision or rejection on grounds that the "0.924–1.000" enrichment and
the "DiffDock provides the critical enrichment gain" claim are not actually demonstrated.

---

## CRITICAL

### C1. The "ROC-AUC 0.924–1.000" headline rests on a tautological validation for 2 of 4 targets
**Where:** Abstract (main 72); Results (main 216, Table at 228–231); Discussion (main 281);
Conclusion (main 317); SM validation strategy (SM 1275, 1336); SM detailed analysis (SM 1346).
**The problem.** For PfATP4 and PfClpP the "decoys" are not decoys. SM 1275/1336 state the
non-PfDHFR targets are validated by **"score-based classification (top 25% vs bottom 25%)"**
of MMV compounds — i.e. actives = top 25% by consensus score, "decoys" = bottom 25% by the
*same* consensus score. ROC-AUC of a score against a label that was *defined by splitting on
that score* is ~1.0 by construction. This is why PfATP4 and PfClpP report AUC = 1.000 with a
**zero-width bootstrap CI [1.000, 1.000]** (main 229, 231) — a degenerate interval that is
impossible for any genuine validation and diagnostic of a tautological split. The MMV Malaria
Box has **no real decoys** (all 400 are confirmed actives), so for these targets there is no
independent negative class. The abstract's "maintaining discriminatory power against the MMV
Malaria Box positive-control benchmark (consensus-score ROC-AUC 0.924–1.000)" therefore
advertises two numbers (1.000, 1.000) that are non-validations. The genuine per-target spread
is really 0.924 (PfDHFR) and 0.971 (PfCRT), and even those are in-distribution (no real decoys;
see C2, H3).
**Fix.** (a) Stop reporting the score-based-split AUCs as validation; either remove PfATP4/PfClpP
from the ROC-AUC range or relabel them explicitly as "score-separation on a positive-control set,
not decoy discrimination." (b) Reframe the abstract/Conclusion range to the only honestly
decoy-backed number (DEKOIS PfDHFR, AUC 0.450 — see C2) plus the in-distribution MMV numbers,
clearly labeled as positive-control sensitivity, not discrimination. (c) Add a sentence: "For
PfATP4 and PfClpP, no property-matched decoy set was available; the reported AUC reflects
score-based stratification of actives and is not an external discrimination test."

### C2. The core causal claim — "ML-based DiffDock rescoring provides the critical enrichment gain" — is never tested on a real decoy set
**Where:** Abstract (main 72); Results (main 216); Discussion (main 281); Conclusion (main 317,
319); SM validation table (SM 524, 530).
**The problem.** The manuscript's narrative is: DEKOIS PfDHFR with **Vina only** gives AUC 0.450
(near-random) → therefore the **Vina+DiffDock consensus** is essential → consensus AUC 0.924.
But the 0.450 (DEKOIS, 40 actives/1200 decoys, Vina only) and the 0.924 (MMV, no real decoys or
score-split "decoys", consensus) are computed on **different datasets with different methods**.
There is **no experiment in the paper that applies the Vina+DiffDock consensus to the DEKOIS
PfDHFR 40-actives/1200-decoys set**. The one apples-to-apples test that would actually support
the causal claim is absent. What the data actually show is: (i) on the only genuine decoy
benchmark, the method fails (0.450); (ii) on in-distribution/circular benchmarks, it "succeeds."
Inferring "DiffDock rescues enrichment" from that contrast is a cross-dataset leap, not a
demonstration. A JCIM reviewer will ask precisely for the missing DEKOIS-consensus number.
**Fix.** Dock the DEKOIS PfDHFR set (40 actives + 1200 decoys) with the **full Vina+DiffDock
consensus** and report ROC-AUC/EF5%/BEDROC. If it is ~0.9, the central claim is supported; if
not, the claim must be withdrawn. Until then, replace "DiffDock provides the critical enrichment
gain / essential contribution" (main 281, 317, 319) with "is hypothesized to contribute; this
was not tested on an independent decoy set."

---

## HIGH

### H1. MCMC "+0.0246 improvement" is internally inconsistent and oversold
**Where:** Methods (main 119–121); Conclusion (main 317).
**The problem.** (a) **Arithmetic mismatch:** main 121 reports "mean chain MPO improvement of
+0.0246 (library mean 0.742 → chain mean 0.751)," but 0.751 − 0.742 = **+0.009**, not +0.0246.
Either the means or the improvement is wrong; the headline number does not reproduce from the
stated before/after values. (b) **Surrogate too weak to support the claim:** the MPO being
"optimized" is predicted by a random-forest surrogate with validation **R² = 0.377** (≈38% of
variance explained), so the +0.0246 (or +0.009) is a shift in a *noisy proxy's prediction*, not
a measured MPO gain of real molecules. No CI/error bar is given; the uncertainty almost
certainly exceeds the effect. (c) **No new molecules:** points are decoded by **nearest-neighbour**
search in the original UMAP space, so "improved" latent points map back to **existing library
molecules* — the MCMC re-ranks the library via a weak surrogate, it does not generate anything.
(d) **Residual overclaim:** the Conclusion (main 317) still says "Metropolis–Hastings MCMC for
latent space **optimisation**" and "measurable MPO improvement (+0.0246)" — the subsection title
was softened to "exploration" (C6 fix) but the Conclusion was not, and "measurable" overstates a
≤0.025 shift on a 0–1 scale from an R²=0.377 surrogate.
**Fix.** (i) Reconcile +0.0246 vs the 0.742→0.751 means (state which is correct). (ii) Report the
*actual* MPO of the decoded nearest-neighbour molecules (recomputed, not surrogate-predicted)
with a CI; if the gain vanishes, say so. (iii) Replace "optimisation"→"exploration" and
"measurable MPO improvement"→"a small surrogate-predicted shift (+0.0246, within the noise
implied by R²=0.377), consistent with a non-flat latent landscape" in the Conclusion.

### H2. "92.6% unreachable" conflates two different analyses; the 1.84× ratio is near-trivial and the 1.2× comparison is likely misattributed
**Where:** Cover letter (35); Introduction (main 91); Results (main 150–152); Discussion (main
273); SM diversity table (SM 880).
**The problem.** Three distinct issues:
1. **Conflation.** 92.6% = fraction of generated molecules with max Tanimoto < 0.4 to the **396
   seed NPs** (a *dissimilarity-to-NPs* metric; mean max 0.206). The *unreachability-from-drugs*
   claim is the separate STONED-SELFIES scaffold-leap result (97.9% of 5525 mutations from 20
   seeds have no NN > 0.4 in the VAE library; mean max 0.238). The cover letter (35) and main 91
   present the 92.6% NP-dissimilarity number (with its 0.206 mean) **as** "chemotypes unreachable
   by local SELFIES perturbations of known drugs." That swaps the metric and the referent.
2. **1.84× ratio is expected by construction.** Scaffold-only Tanimoto (0.379) ≥ whole-molecule
   Tanimoto (0.206) is the *default*: scaffold fingerprints are coarser and ignore the
   substituents that differ, so a ratio > 1 is nearly guaranteed, not evidence of "systematic
   ring-system preservation." Calling it a "two-level exploration strategy" over-reads an
   arithmetic near-tautology.
3. **Likely misattributed benchmark.** Discussion (main 273) claims the 1.84× "exceeds the
   ~1.2× ratios reported by Brown2019 and Blaschke2020REINVENT2A." GuacaMol (Brown2019) reports
   KLD/FCD distribution-learning metrics, and REINVENT2 (Blaschke2020) reports validity/novelty/
   SNN internals — neither reports a "scaffold-to-whole-molecule Tanimoto ratio" of ~1.2×. This
   looks like an invented comparison. The SM diversity table (SM 880) itself warns "Direct
   numerical comparison is limited by different evaluation frameworks," which directly
   contradicts the Discussion's point-by-point numerical comparison (92.6% > 85% > 80%; 1.84× >
   1.2×).
**Fix.** (a) Cover letter/main: separate the two results — state "92.6% of generated molecules
are dissimilar (Tanimoto < 0.4) to the 396 seed NPs" **and** separately "97.9% of 5525 local
SELFIES mutations from 20 seeds have no VAE-library neighbour above Tanimoto 0.4"; do not attach
the 0.206 mean to the unreachability claim. (b) Either cite the exact section/table of
Brown2019/Blaschke2020 that reports a 1.2× scaffold-to-whole Tanimoto ratio, or delete the 1.2×
comparison. (c) Reframe the 1.84× ratio as a consistency check, not a novelty result. (d)
Reconcile the SM "frameworks differ" caveat with the Discussion's direct numerical boasting.

### H3. Tartarus ρ=0.013 "confirms independence of MPO scoring dimensions" is a non sequitur and contradicts the SM's own non-independence disclosure
**Where:** Limitations (main 305); SM sensitivity methods (SM 198).
**The problem.** The Tartarus test correlates **Tartarus composite binding affinity** (QuickVina/
Smina on 3 unrelated targets) with the **weighted MPO score**. Finding ρ=0.013 says Tartarus
binding ≠ MPO ranking — it says **nothing** about whether the *five MPO components* (S_vina,
S_diff, QED, ADMET, Ro5) are mutually independent. Yet main 305 claims this "confirms the
independence of our MPO scoring dimensions." Worse, the SM (198) already discloses that **S_vina
and S_diff are back-calculated from a shared residual** (35:25 split) — i.e. two of the five
"dimensions" are **non-independent by construction**, and QED/Ro5 overlap (Ro5 violations are
partly captured in QED), and ADMET includes SA which overlaps with the separate SYBA filter. So
the components are *not* independent, and the Tartarus result cannot establish otherwise.
Additionally, the framing "MPO + docking ranking" (main 305) is conceptually muddled: MPO
already contains 60% docking (35% Vina + 25% DiffDock), so "combining MPO with docking" is partly
redundant — there is no separate docking score being combined. Finally, p=0.091 is
non-significant; "confirming independence" from a failure-to-reject is logically backwards.
**Fix.** Drop "confirms the independence of our MPO scoring dimensions." Replace with: "Tartarus
binding affinity (3 non-Pf targets) does not correlate with our MPO ranking (ρ=0.013, p=0.091),
indicating the MPO ranking is not simply rediscovering generic docking affinity; this is
consistent with, but not a test of, inter-component independence (S_vina and S_diff are derived
from a shared residual; see SM)." Remove the "MPO + docking" combination language or clarify that
MPO already includes docking.

### H4. ChEMBL enrichment table is framed as supportive but actually mostly fails or is degenerate
**Where:** SM Table `sm_s18b_chembl_enrichment` (SM 540–553).
**The problem.** Reading the table: PfDHFR EXCELLENT = 60.4% actives vs 11.1% inactives (5.43×,
genuine pass); PfDHFR GOOD = 100%/100% (no discrimination, "No"); **PfCRT EXCELLENT = 100%
actives vs 68.4% inactives** (only 1.46×, fails 2×, "No") — i.e. nearly 7 in 10 inactives also
pass the stringent threshold, showing the threshold is permissive for PfCRT; **PfATP4 EXCELLENT
= 0%/0%** (zero compounds reach EXCELLENT — yet "Pass = Yes", a degenerate 0≥2×0 pass); PfATP4
GOOD = 53.4% actives vs 63.2% inactives (**inactives pass MORE than actives** —
anti-enrichment). PfClpP excluded (API error). So of four targets, only PfDHFR EXCELLENT
genuinely supports the thresholds; PfCRT fails, PfATP4 is degenerate/anti-enriched, PfClpP
missing. The caption nevertheless calls this "validating the use of stringent binding
thresholds." Sample sizes are tiny (PfCRT n=12 actives/19 inactives).
**Fix.** Reword the caption/notes to state the result honestly: thresholds discriminate only for
PfDHFR; PfCRT is permissive (inactives 68.4% at EXCELLENT); PfATP4 reaches no EXCELLENT hits
(the "Pass=Yes" is a 0/0 artifact and should be marked "n/a"); PfClpP untested. Drop "validating"
until a target-by-target pass is demonstrated.

### H5. MPO sensitivity: 72% of perturbations FAIL, yet framed as "stable"/"moderate"
**Where:** Results (main 206); SM Table `sm_s17_mpo_sensitivity` (SM 614, 627, 634).
**The problem.** Only **7/25 (28%)** of weight perturbations pass the stated stability criteria
(ρ>0.95 AND Jaccard≥0.70); **18/25 (72%) fail.** The top-20 hit-list Jaccard is **0.548** (≈45%
of the top-20 changes under perturbation), and ADMET −20% collapses ρ to **0.258** (near-random
ranking). The actionable outputs (the 76 centroids, the 19,913 leads, the top-20) are exactly the
fragile top-of-list objects, yet main 206 frames this as "moderate sensitivity" and the SM caption
as "MPO ranking is stable to moderate weight variations." The paper emphasizes the top-1000 ρ
(0.792, stable) and plays down the top-20 instability (0.548), but the top-20/76 is what is
carried forward.
**Fix.** State plainly: "18/25 (72%) of weight perturbations fail the stability criteria; the
top-20 hit list has a mean Jaccard of 0.548 and the ADMET-weight ranking collapses to ρ=0.258 at
−20%. The 76-centroid / top-20 selection is therefore sensitive to weight choice; the top-1000
ranking (ρ=0.792) is more stable." Adjust any downstream claim ("76 optimization-worthy
centroids") to note this fragility.

### H6. "19,913 synthesizable leads" inherit centroid MPO by cluster membership, but the paper's own data show centroid→member potency transfer is near-random
**Where:** Results (main 258–260); Discussion/activity-cliff analysis (main 277); SM workflow
(SM 181, 373); Limitations (main 311).
**The problem.** The 19,913 = members of the 53 expanded clusters with SYBA>0, where the
**cluster's centroid** had MPO≥0.40 (SM 181/373: "SYBA>0 plus the MPO≥0.40 centroid filter").
The member molecules' own MPO/docking is **not** computed for the 40,481 expansion (only the
top-20 clusters get full rescoring, main 277). The paper's own full-cluster rescoring finds the
Spearman correlation between Tanimoto-to-centroid and member Vina affinity is **0.025** — i.e.
centroid score is a "weak predictor of intra-cluster potency rank" (main 277). So the 19,913
"leads" are not validated as potent; they are SYBA-accessible members of clusters whose centroid
docked well, and the one test of centroid→member transfer shows it is essentially random.
Presenting 19,913 as "high-priority synthesizable leads" / "leads with favorable predicted
selectivity" overstates what the propagation supports.
**Fix.** Reframe 19,913 as "19,913 synthetically accessible cluster members of MPO≥0.40
centroids (member-level potency not individually computed; centroid→member potency transfer is
weak, ρ=0.025)." Reserve "lead" for the 76 centroids (or the top-20 rescoring subset) where
docking was actually performed.

### H7. Generated analogues are predicted LESS active than the seeds by all three Ersilia models — buried as "statistical parity"
**Where:** Results (main 193); SM BH table (SM 769, 807).
**The problem.** Main 193: "NPs and SDs displayed higher median activity scores than generative
analogues across all models" (all 24 pairwise tests n.s. after BH; rank-biserial r<0.10). The SM
caption frames this as generated analogues "maintain statistical parity" with seeds. But the
direction is **uniformly against** the generated set: the generative output (the entire point of
the paper) is predicted *less* active than the starting NPs/synthetic drugs by the very activity
models the paper uses. The 19,913 leads are drawn from that less-predicted-active generated set.
For a generative antimalarial-discovery paper, this is a first-order negative result that is
soft-pedaled; the paper pivots to docking/MPO, but the most direct computational activity
estimate does not support the generated library.
**Fix.** State the direction explicitly in the main text: "generated analogues were predicted
*less* active than NPs/SDs by all three Ersilia models, though not significantly (r<0.10);
prioritization therefore rests on docking/MPO, not on the activity models." Add one sentence on
why docking-based prioritization of a less-predicted-active set is still defensible (or
acknowledge the tension).

### H8. "Mathematically prove … fundamentally unreachable" overstates an empirical Tanimoto-threshold observation
**Where:** Introduction (main 91); Discussion (main 273).
**The problem.** Main 91 says STONED-SELFIES analysis was "employed to mathematically prove that
our generative model accesses new scaffolds fundamentally unreachable by simple local search."
The actual result (main 273) is that 97.9% of 5525 SELFIES mutations from 20 seeds have no VAE-
library neighbour above a **chosen** Tanimoto cutoff of 0.4. This is an empirical,
cutoff-dependent enumeration, not a mathematical proof, and "fundamentally unreachable" is an
absolute claim resting on a tunable similarity threshold (at 0.6 or 0.8 the fraction would
shrink). "Mathematically prove" is exactly the kind of claim a JCIM reviewer flags.
**Fix.** Replace "mathematically prove" with "empirically demonstrate" and "fundamentally
unreachable" with "dissimilar beyond the Tanimoto-0.4 threshold." State the threshold dependence
explicitly.

### H9. TDA H0/H1 "explanation" and the TopologyNet/D-GRIL/Q2SAR/PACTNet paragraph invoke methods and computations not present in the paper
**Where:** Introduction (main 95); Discussion (main 273).
**The problem.** Main 273 offers a "topological explanation: H1 persistence (ring topology) is
preserved across generation while H0 (atom connectivity) diverges." No persistent homology is
computed anywhere in the paper — there is no TDA in Methods. This is an ad hoc post-hoc
rationalization, not a result. Main 95 additionally name-drops TopologyNet, D-GRIL, Q2SAR, and
PACTNet as "corroborating," and claims PACTNet is "directly validating the compression ratios
achieved by **our related tensor network framework**." No tensor network framework appears in
this manuscript (not in Methods, not in Results). A reviewer reads: what tensor network? It is
not here. The paragraph reads as novelty-padding to rebut the prior desk-rejection "no new
algorithm / insufficient general interest" — which risks reinforcing the editor's concern rather
than addressing it.
**Fix.** Either compute and report persistent homology (H0/H1) on the generated vs seed sets, or
delete the H0/H1 sentence. Remove "our related tensor network framework" (or move it to a cited
companion paper). Trim main 95 to citations that are actually used; do not claim external tools
"directly validate" a framework not present in this paper.

### H10. Redocking "100% success (5/5)" is achieved by excluding the relevant DHFR inhibitor (MTX, failed) and counting glycerol/cofactors
**Where:** Results (main 216); SM redocking table (SM 957, 980); LigandExplorer table (SM 826–829).
**The problem.** Main 216 headlines "redocking validation achieved a 100.0% success rate (5/5
with RMSD < 2.0 Å)." The SM table (SM 980) shows the honest overall rate is **5/10 (50%)**: the
5 excluded are MTX (the pharmacologically relevant DHFR inhibitor, RMSD ~30 Å, **failure**) and
NDP (cofactor, N/A). The 5 "successes" are UMP (a nucleotide cofactor), **GOL (glycerol, a
crystallization artifact — see LigandExplorer SM 829: "Organic (crystallization), Artifact")**,
and Y01. So the perfect score is obtained by dropping the one true inhibitor (which failed) and
counting a crystallization artifact and cofactors. The main text does disclose the MTX failure in
the same paragraph, but the "100% success (5/5)" headline is misleading because the denominator
was cherry-picked. (Side issue: LigandExplorer labels MTX — a folate analog — as "peptide-like,"
UMP as "DNA-like," NDP as "RNA-like"; these GNN classifications are suspect and a reviewer may
question the tool's reliability.)
**Fix.** Report the rate as 5/10 (50%) overall, 5/5 only for the alignable subset, and state
explicitly that the relevant DHFR inhibitor MTX failed (~30 Å) while successes include a
crystallization artifact (GOL) and cofactors. Reconsider whether this constitutes meaningful
pose-reproduction validation for the DHFR target specifically.

---

## MEDIUM

### M1. Cover letter still says "validated generative scaffold-hopping framework" (C5-type overclaim not applied to the cover letter)
**Where:** Cover letter (35).
**The problem.** The C5 fix replaced "validated discovery" with "computational prioritization" in
the Conclusion (main 321), but the cover letter — the editor's first read — still opens with "This
work presents a **validated** generative scaffold-hopping framework" and "retrospectively predicts
(retrodicts) known ground-truth antimalarials … achieving 69.8% hit rates and consensus-score
ROC-AUC 0.924–1.000." Both prior JCIM desk rejections were for novelty/scope overclaiming; leading
the cover letter with "validated" + the tautological 1.000 range (C1) + the 92.6% conflation (H2)
repeats the exact pattern that triggered desk rejection.
**Fix.** Replace "validated generative scaffold-hopping framework" with "computational
scaffold-hopping framework for antimalarial prioritization"; drop "validated"; restate the 0.924
as a positive-control sensitivity (not decoy discrimination); separate the 92.6% NP-dissimilarity
from the 97.9% unreachability result.

### M2. "69.8% hit rate" and "more than 5-fold enrichment over random" — no decoy/inactive/random baseline exists for the MMV box
**Where:** Results (main 216); Discussion (main 281); Cover letter (35).
**The problem.** The MMV Malaria Box is 400 confirmed actives with no inactives. "69.8% of known
actives" is the fraction of actives scoring above the HIGH+MEDIUM threshold — i.e. sensitivity at
an arbitrary threshold, not enrichment. "More than 5-fold enrichment over random compound sets"
(main 216) has no defined random/inactive comparator in the paper. The 69.8% is real (SM 1047:
1381 total, 69.8%) but it is a within-actives pass rate, not enrichment.
**Fix.** Replace "more than 5-fold enrichment over random" with "69.8% (range 35.1–94.0%) of
confirmed MMV actives scored above the consensus HIGH/MEDIUM thresholds" and drop the
"enrichment-over-random" claim unless a random/inactive baseline is actually computed.

### M3. "Orthogonal experimental proxy" — a computational benchmark mislabeled as experimental
**Where:** Introduction (main 93).
**The problem.** Main 93: "This validated enrichment, combined with a synthetic accessibility
filter (SYBA>0), functions as an **orthogonal experimental proxy** that justifies hit
prioritization in the absence of prospective in vitro testing." The MMV retrodiction is a
**computational** benchmark that uses experimentally-confirmed actives; it is not an experimental
proxy (no experiment is performed), and "validated enrichment" inherits the C1/C2 problems.
**Fix.** Replace "orthogonal experimental proxy" with "computational positive-control benchmark"
and drop "validated."

### M4. PfCRT dominates the hits (87%), has the worst early enrichment (EF5%=1.11), and its 0.971 AUC is admitted (SM) to be a 90%-active-rate artifact — yet sits uncaveated in the headline range
**Where:** Main Table (main 230); SM detailed analysis (SM 1348); Limitations (main 311, F3 caveat).
**The problem.** PfCRT supplies 87% of centroid target assignments (421/484) and is the source of
most hits, but its EF5% is only **1.11** (vs 2.57 for PfDHFR) — negligible early enrichment. SM
1348 admits the 0.971 AUC "reflect[s] the dataset composition (359 actives, 40 decoys, 90% active
rate)." The F3 caveat was added in Limitations (main 311), but the abstract/main-table 0.924–1.000
range still includes the artifact-inflated 0.971 uncaveated. The dominant target is also the
weakest-enriching and most artifact-prone.
**Fix.** In the main text Table 1 caption or a Results sentence, flag that PfCRT's AUC is inflated
by a 90% active rate and its EF5% (1.11) shows negligible early enrichment; note that the
framework's hits are concentrated in the target where enrichment is weakest.

### M5. SI_pred definitional conflation: Results define SI as an IC50 ratio but compute a probability ratio
**Where:** Results (main 260); MPO section (main 210).
**The problem.** The C3 fix labelled SI_pred an "unvalidated prioritization heuristic" and noted
DILI inflation (main 210). But the Results lead-identification paragraph (main 260) still says
"100% exhibited a predicted selectivity index > 10 (**defined as IC50,HepG2 / IC50,Pf3D7**)," while
the actual SI_pred = eos7kpb / (1 − DILI) is a ratio of two probabilities (a Pf activity
probability over a non-hepatotoxicity probability), not a ratio of two IC50s. Equating the
computed probability ratio with the experimental IC50-ratio definition is a definitional mismatch
distinct from the framing issue C3 addressed.
**Fix.** At main 260, replace "defined as IC50,HepG2 / IC50,Pf3D7" with "a probability-ratio
heuristic, eos7kpb/(1−DILI), used as a proxy for the experimental selectivity index
IC50,HepG2/IC50,Pf3D7, which it is not equivalent to."

### M6. PfDHFR validation N is inconsistent across three locations; PfATP4 N inconsistent (184 vs 198)
**Where:** Main Table 1 (main 228–229); SM validation table (SM 524); SM MMV table (SM 1044); SM
validation composition (SM 1267–1268); SM detailed analysis (SM 1344).
**The problem.** PfDHFR: main Table 1 reports N=399; SM validation table (524) reports "399
actives / 399 decoys"; SM validation composition (1267) and detailed analysis (1344) report
"132 actives / 267 decoys (MMV+DEKOIS)." These are three different stories for the same 0.924.
The 399 "decoys" are unexplained (MMV has no decoys; DEKOIS has 1200). PfATP4: SM MMV table
(1044) reports N=184 (rotatable-bond filter), but main Table 1 (229), SM validation table (525),
and SM validation composition (1268) all report 198. The 1381 overall (SM 1047) only reconciles
with 184 (399+399+184+399=1381), not 198 (would be 1395). A reviewer cross-checking Table 1
against the SM tables will find the PfDHFR actives/decoys and the PfATP4 N do not agree.
**Fix.** Reconcile to a single, explicit PfDHFR validation definition (which 399? which 132/267?
where do 399 "decoys" come from?) and a single PfATP4 N (184 or 198) across main Table 1 and all
SM tables; add a footnote mapping each number to its source CSV.

---

## LOW

### L1. PCA table arithmetic inconsistency
**Where:** SM PCA table (SM 292). PC4 "Variance = 0.000" but "% Explained = 1.1%" and "Cumulative
= 100.0%." If PC4 variance is 0.000 it explains 0%, and PC1–3 cumulative (82.3%) cannot jump to
100% via a zero-variance PC. Either the 0.000 or the 1.1%/100.0% is wrong.
**Fix.** Correct PC4 variance/%/cumulative to be internally consistent.

### L2. Seed-scaffold count 101 vs 246 unexplained
**Where:** Results (main 148: 70/101 seed scaffolds, 69.3% recovery); Discussion (main 289:
91/246 Bemis–Murcko frameworks). 101 (seed NP scaffolds) and 246 (curated seed scaffolds vs
ANPDB) are different denominators but the switch is not explained; a reader may think 70/101 and
91/246 contradict.
**Fix.** Add a clause distinguishing "101 seed-NP Bemis–Murcko scaffolds" from "246 curated
hybrid seed scaffolds."

### L3. "Zero fabrication protocol" section protests too much and conflicts with the score-based split
**Where:** SM 1209–1217. "No arbitrary thresholds … No data manipulation" sits uneasily beside the
score-based 25% split (C1) and the ChEMBL-calibrated thresholds. Reviewers often read such
sections as a red flag rather than reassurance.
**Fix.** Consider removing or toning down; let the provenance/CSV list carry the transparency
message.

### L4. DEKOIS EF5% = 0.00 is worse than "near-random"
**Where:** Results (main 216); SM (SM 530). EF5%=0.00 means zero actives in the top 5% — the top
of the ranked list is enriched in decoys, which is anti-enrichment, not merely "near-random"
(random ≈ EF 1.0). "Near-random" understates a negative top-rank result.
**Fix.** State "EF5% = 0.00 (no actives in the top 5%, below the random-expectation of 1.0)."

### L5. LigandExplorer GNN classifications are suspect
**Where:** SM 826–829. MTX (methotrexate, a folate/small-molecule DHFR inhibitor) is labelled
"Peptide-like ligand"; UMP (a nucleotide) "DNA-like"; NDP (NADPH) "RNA-like." These are odd
labels for a tool whose classifications are then used to assert "biologically relevant ligands
rather than crystallization artifacts."
**Fix.** Either correct the labels or add a note that the GNN coarse classes are used only to
flag crystallization artifacts (GOL), not to assert mechanistic identity.

---

## Quick-reference: severity-ordered hit list

| # | Sev | One-line | Primary loc |
|---|---|---|---|
| C1 | CRITICAL | 1.000 AUCs are tautological (score-based 25% split; no real decoys) | main 72,216,229,231; SM 1275,1336 |
| C2 | CRITICAL | "DiffDock gives the enrichment gain" never tested on a real decoy set | main 216,281,317; SM 530 |
| H1 | HIGH | MCMC +0.0246 ≠ stated 0.742→0.751 (=+0.009); surrogate R²=0.377; NN decode; "optimisation" remains | main 119-121,317 |
| H2 | HIGH | 92.6% conflates NP-dissimilarity with unreachability; 1.84× near-trivial; 1.2× likely misattributed | cover 35; main 91,150-152,273; SM 880 |
| H3 | HIGH | Tartarus ρ=0.013 ≠ "MPO-component independence"; contradicts SM non-independence disclosure | main 305; SM 198 |
| H4 | HIGH | ChEMBL table: only PfDHFR EXCELLENT passes; PfCRT fails; PfATP4 0/0 degenerate "Yes" | SM 540-553 |
| H5 | HIGH | 72% of MPO perturbations fail; top-20 Jaccard 0.548; framed as "stable" | main 206; SM 614,627,634 |
| H6 | HIGH | 19,913 "leads" inherit centroid MPO; own data show centroid→member ρ=0.025 | main 258-260,277; SM 181,373 |
| H7 | HIGH | Generated set predicted LESS active than seeds by all 3 Ersilia models; buried as "parity" | main 193; SM 769,807 |
| H8 | HIGH | "Mathematically prove … fundamentally unreachable" overstates a cutoff-dependent enumeration | main 91,273 |
| H9 | HIGH | TDA H0/H1 + TopologyNet/D-GRIL/Q2SAR/PACTNet + "our tensor network framework" not in paper | main 95,273 |
| H10 | HIGH | Redocking "100% (5/5)" excludes failed MTX and counts glycerol artifact | main 216; SM 957,980,829 |
| M1 | MEDIUM | Cover letter still "validated … framework" (C5 not applied to cover letter) | cover 35 |
| M2 | MEDIUM | "69.8% hit rate" / "5× enrichment over random" — no decoy/random baseline | main 216,281; cover 35 |
| M3 | MEDIUM | "Orthogonal experimental proxy" — computational benchmark mislabeled | main 93 |
| M4 | MEDIUM | PfCRT 87% of hits, EF5%=1.11, 0.971 AUC admitted artifact; uncaveated in headline | main 230; SM 1348 |
| M5 | MEDIUM | SI_pred defined as IC50 ratio but computed as probability ratio | main 260 |
| M6 | MEDIUM | PfDHFR N inconsistent (399/399 vs 132/267 vs 399); PfATP4 184 vs 198 | main 228-229; SM 524,1044,1267 |
| L1 | LOW | PCA PC4 0.000 variance but 1.1%/100% cumulative | SM 292 |
| L2 | LOW | Seed scaffolds 101 vs 246 unexplained | main 148,289 |
| L3 | LOW | "Zero fabrication protocol" protests too much | SM 1209 |
| L4 | LOW | DEKOIS EF5%=0.00 is below random, not "near-random" | main 216; SM 530 |
| L5 | LOW | LigandExplorer labels MTX "peptide-like", UMP "DNA-like", NDP "RNA-like" | SM 826-829 |
