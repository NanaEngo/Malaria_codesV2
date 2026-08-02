# Editorial Critical Review — P3 Manuscript

**Project:** Persistent homology resolves the scaffold paradox in AI-generated African antimalarial candidates  
**Target:** *Journal of Cheminformatics*  
**Review date:** 2026-07-27  
**Reviewer pass:** editorial (anti-AI writing, structure, citation hygiene, journal fit)

---

## 1. Anti-AI writing scan

**Authoritative count: 6 hits** in `ROOT/manuscript/LaTeX/`.

| File | Line | Term | Original text (excerpt) | Concrete rewrite |
|------|------|------|-------------------------|------------------|
| `Cover_Letter_P3.tex` | 34 | demonstrate | "We demonstrate that persistent homology resolves the scaffold paradox..." | "Persistent homology resolves the scaffold paradox..." (drop the performative framing; state the finding directly). |
| `Paper3_Quantum_InspiredV2607.tex` | 118 | robust | "whether enrichment metrics are robust to clustering resolution" | "whether enrichment metrics are stable under clustering resolution" or "whether enrichment metrics vary with clustering resolution". |
| `Paper3_Quantum_InspiredV2607.tex` | 325 | robust | "the robust SELFIES string syntax inherently preserves valid cyclic macro-structures" | "the SELFIES string syntax inherently preserves valid cyclic macro-structures" (delete "robust"; the preservation is a design feature, not an empirical robustness claim). |
| `Paper3_Quantum_InspiredV2607.tex` | 379 | robust | "classical fingerprint-based distance metrics provide a simpler and more robust baseline" | "classical fingerprint-based distance metrics provide a simpler and more reliable baseline" or "a simpler baseline with stable performance". |
| `Paper3_Quantum_Inspired_SM_V2607.tex` | 608 | robust | "classical fingerprint-based distance metrics provide a simpler and more robust baseline" | Same rewrite as main L379; this sentence is duplicated verbatim in the SM Discussion. |
| `Paper3_Quantum_InspiredV2607.tex` | 479 | demonstrate | "We demonstrate the application of persistent homology to resolve a chemical space data inconsistency" | "Persistent homology resolves this chemical-space inconsistency" or "The analysis shows that persistent homology resolves...". |

**Note:** The Cover Letter also uses the phrase "We demonstrate that" in the opening summary. Cover letters are less strictly policed, but replacing the first sentence with a direct statement of the findings will make the pitch more concrete and less AI-generic.

---

## 2. Structure

### 2.1 SM Discussion duplication

**File:** `Paper3_Quantum_Inspired_SM_V2607.tex`, lines 582–644  
**Finding:** The SM "Discussion" section is not supplementary; it largely repeats the main Discussion.

- **L585–595 (`Mechanistic explanation for classical fingerprint superiority`)** is almost identical to main `Paper3_Quantum_InspiredV2607.tex` L493–497. It repeats the same ECFP4-vs-hybrid argument, the same local-atom-environment explanation, and the same Wesołowski citation.
- **L600–608 (`Quantum kernel density vs classical fingerprint discriminator`)** repeats the same applicability-domain argument that appears in main L491 and L528.
- **L625–630 (`TNE compression and scaffold information content`)** partly repeats compression numbers from the main Results/Discussion.
- **L634–643 (`Integration with resistance-resilient MD validation`)** repeats the main L509–524 finding about 20 leads and H₁ persistence, using the same figure.

**Recommendation:** The SM Discussion should be cut or reframed as *extra* material only. Concretely:
- Delete the full "Mechanistic explanation for classical fingerprint superiority" subsection (SM L585–595). The main Discussion already contains this argument; the SM should cite the main paper rather than restate it.
- Replace the "Quantum kernel density vs classical fingerprint discriminator" subsection with *only* the experimental details that did not fit in the main text (e.g., the exact `lightning.qubit` simulator settings, the mutation count, the seed pool composition, and the full Table S3/Figure S3 caption). Move interpretation back to the main Discussion.
- Keep the TNE compression subsection only if it adds a derivation or table not in the main text; otherwise merge it into the caption of the relevant SM table.
- Keep the MD-validation integration subsection only if it presents the expanded `n = 77` follow-up in detail. The pilot `n = 14` result should not be repeated verbatim from the main paper.

### 2.2 README contradictions vs manuscript

**File:** `README.md` at repository root.

| README line | README claim | Manuscript claim | Issue |
|-------------|--------------|------------------|-------|
| L28 / L41 | Novelty claim N1: **15.6×** TNE compression | Main abstract L99: **5.9×** real compression; main conclusion L540: "mean real ratio 5.9×" | README uses the padded ratio, manuscript uses the real ratio. Pick one and be consistent. If both are reported, label them clearly as "padded" vs "real". |
| L43 | "10-fold Stratified Cross-Validation" | Main L530: "5-fold cross-validation" (and SM L123: "5-fold stratified cross-validation") | README says 10-fold; manuscript says 5-fold. Correct README to 5-fold. |
| L19 / L29–32 | Novelty IDs **N1–N4** | Main text / manuscript narrative uses different framing (TFP, TNE, QKS, scaffold paradox) | README introduces internal IDs N1–N4 that do not appear in the manuscript. Either add these labels to the manuscript or remove them from the README to avoid reviewer confusion. |
| L73 | `conda activate malaria_md` | No environment name specified in manuscript; project uses mixed conda/venv language | README mentions a specific env name (`malaria_md`) that may not match the actual project setup. Verify or make it generic (e.g., "activate your project environment"). |
| L62 | Manuscript filename: `Paper3_Quantum_Inspired_v0.7_V2607.tex` | Actual file: `Paper3_Quantum_InspiredV2607.tex` | README points to a non-existent filename. Update to `Paper3_Quantum_InspiredV2607.tex`. |
| L39 | "19,913 molecules × 3 P. falciparum docking targets" | Main abstract L99: 19,849 candidates | README says 19,913; manuscript says 19,849. Reconcile — likely the docking oracle covered 19,913 but the analyzed library is 19,849. State that distinction explicitly. |

**Concrete fixes for README:**
- L28 / L41: Replace "15.6× compression" with "5.9× real-atom compression (15.6× padded)".
- L43: Replace "10-fold" with "5-fold".
- L62: Replace `Paper3_Quantum_Inspired_v0.7_V2607.tex` with `Paper3_Quantum_InspiredV2607.tex`.
- L73: Verify environment name; if not project-specific, write "conda activate <your-env>" or "activate the environment specified in `environment.yml`".
- L29–32: Either map N1–N4 to manuscript sections or remove the internal ID column.
- L39: Clarify "19,913 molecules docked; 19,849 passed quality control and entered the TFP/TNE/QKS benchmark".

---

## 3. Citations

### 3.1 Companion-study keys (`temgoua`)

**Command:** `grep -ni 'temgoua' Bibliography_Paper3.bib`  
**Result:** Both keys are defined:
- `temgoua2026antimalarial` (Bib L7)
- `temgoua2027md` (Bib L19)

**Manuscript usage check:**
- Main L118 and L325 cite `temgoua2026antimalarial` — OK.
- Main L511 and L520 cite `temgoua2027md` — OK.
- SM L637 cites `temgoua2026antimalarial` — OK.

**No action required** on the keys themselves, but verify that `temgoua2027md` is actually a published or deposited work; the title is not visible in this excerpt and the author list is truncated as "and others". If it is a preprint or companion submission, the journal may require a status note.

### 3.2 Missing bibliography entry for Wesołowski

**Command:** `grep -rni 'wesolowski\|weso' manuscript/LaTeX/`  
**Result:** Two bare-text citations:
- Main `Paper3_Quantum_InspiredV2607.tex` **L497**: `(Weso\l{}owski et al., 2025)`
- SM `Paper3_Quantum_Inspired_SM_V2607.tex` **L594**: `(Weso\l{}owski et al., 2025)`

**Bib check:** `grep -ni 'weso\|Weso\|WESO' Bibliography_Paper3.bib` returned **no output**.  
**Issue:** The citation is hard-coded plain text, not a `\citep` key, and there is no corresponding BibTeX entry. This will produce a missing-reference warning and breaks the author-year citation style.

**Concrete fix:**
1. Add a `wesolowski2025spectral` (or similar) entry to `Bibliography_Paper3.bib`.
2. Replace both `(Weso\l{}owski et al., 2025)` instances with `\citep{wesolowski2025spectral}`.
3. If the work is not yet published, use a `unpublished` or `misc` entry and note the status in the manuscript.

### 3.3 Manual footnote `[1]` in SM

**File:** `Paper3_Quantum_Inspired_SM_V2607.tex` **L658** and **L662**  
**Issue:** The SM uses a manual, numbered footnote `[1]` for a PyTorch C++ extension URL instead of the natbib/author-year citation system. This is inconsistent with the rest of the manuscript, which uses `\citep`/`\citet` and `unsrtnat` style.

**Concrete fix:** Create a `@misc` or `@online` entry (e.g., `pytorch_cpp_extension`) in the bibliography and replace the manual `[1]` with `\citep{pytorch_cpp_extension}`. Then delete the footnote definition at L662.

---

## 4. Journal of Cheminformatics fit

**All items in this section are marked [UNVERIFIED-journal] where the specific journal requirement cannot be confirmed from the manuscript alone.**

### 4.1 Abstract format and length
**File:** `Paper3_Quantum_InspiredV2607.tex` **L98–L100**  
**Finding:** The abstract is a single long paragraph (~150 words). [UNVERIFIED-journal] *Journal of Cheminformatics* typically uses unstructured abstracts for research articles, but some article types require a structured abstract (Background / Methods / Results / Conclusions). The current abstract is dense and mentions four key numbers (92.6%, 69.3%, 5.9×, 0.916). It is readable, but it could be tightened: the phrase "a global topological phenomenon that classical extended-connectivity fingerprints fail to capture" repeats a claim already made in the first clause.  
**Action:** Verify current abstract guidelines on the journal website. If unstructured is allowed, keep; if structured is required, split into Background / Methods / Results / Conclusions. Either way, trim the redundancy.

### 4.2 Data availability statement
**Main:** `Paper3_Quantum_InspiredV2607.tex` **L546–L548** uses placeholder `10.5281/zenodo.XXXXXXX, to be minted upon manuscript acceptance`.  
**README:** L92 cites `10.5281/zenodo.19608875`.  
**SM:** `Paper3_Quantum_Inspired_SM_V2607.tex` **L110** cites `https://doi.org/10.5281/zenodo.19608875`.  
**Issue:** The main manuscript has a placeholder DOI while the README and SM already cite a real DOI. This is a direct contradiction.  
**Action:** Update the main manuscript Data Availability statement to the real DOI `10.5281/zenodo.19608875` (or, if the deposit is still pending, reconcile all three documents to the same status). [UNVERIFIED-journal] Most journals require the data availability statement to match the actual repository record at submission.

### 4.3 Code availability statement
**Finding:** The main manuscript mentions "mirrored at https://github.com/NanaEngo/Malaria_codesV2 under the MIT licence" and lists deposit components, but there is no explicit "Code Availability" section. [UNVERIFIED-journal] *Journal of Cheminformatics* strongly encourages (and often requires) a separate code availability statement with a link to a persistent repository and a software license.  
**Action:** Add a dedicated "Code Availability" subsection under Data Availability (or as a separate section) that names the GitHub repository, the license (MIT), and the key analysis scripts. This is especially important because the paper introduces new descriptors (TFP, TNE, QKS) whose reproducibility depends on the code.

### 4.4 R7–R10 reviewer-response residue
**File:** `Paper3_Quantum_InspiredV2607.tex` **L118**  
**Finding:** The paragraph "Relationship to prior antimalarial screening" frames the paper as answering four reviewer critiques (R7–R10) from a previous study. This reads as a leftover response-to-reviewers section rather than an independent standalone methods paper. It may confuse readers and reviewers of *Journal of Cheminformatics*, who expect the introduction to motivate the study on its own terms.

**Concrete fix:**
- Remove the (R7)–(R10) labels and the phrase "raised during the peer review of our initial antimalarial screening study".
- Rephrase as: "This study extends the antimalarial screening framework of \citep{temgoua2026antimalarial} by addressing four methodological questions: (i) whether VAE latent-space diversity reflects scaffold diversity; (ii) whether enrichment metrics vary with clustering resolution; (iii) the applicability domain of activity predictions; and (iv) whether the generative protocol generalises beyond African NP seed space."
- If the R7–R10 numbering must be retained for internal tracking, move it to the SM or to a cover letter, not the introduction.

---

## 5. Clarity issue: "20 high-confidence leads" vs `n = 14` correlation

**File:** `Paper3_Quantum_InspiredV2607.tex` **L511**, **L513**, **L520**  
**Finding:** The text says "The 20 high-confidence polypharmacological leads identified in our companion molecular dynamics validation study..." (L511), but the correlation with H₁ persistence is reported as Spearman `ρ = 0.916`, `p < 0.0001`, `n = 14` (L513 and L520). This leaves a gap: why is the correlation based on 14 compounds when the lead set has 20? The SM L639 clarifies that the pilot subset was `n = 14` and that an expansion to `n = 77` yielded `ρ = 0.361`, but the main text does not explain the missing 6 compounds.

**Concrete fix:**
- In the main text, add one sentence after L511: "Of these 20 leads, the initial correlation analysis was performed on the 14 compounds with complete TFP and resistance-resilience classifications; the remaining 6 compounds were excluded because [reason, e.g., missing conformer / incomplete RRS]."
- Alternatively, change the lead count in the main text to "14 high-confidence leads" if the entire correlation analysis is restricted to that subset, and relegate the `n = 77` follow-up to the SM.

---

## Summary verdict

The manuscript is scientifically coherent but needs an editorial pass before submission. The highest-priority issues are: (1) the placeholder-vs-real Zenodo DOI contradiction across documents; (2) the missing Wesołowski bibliography entry and the two bare-text citations; (3) the SM Discussion that repeats rather than supplements the main Discussion; and (4) the R7–R10 reviewer-response framing in the introduction. Fixing these will make the paper read as a standalone contribution rather than an appendix to a prior review round.
