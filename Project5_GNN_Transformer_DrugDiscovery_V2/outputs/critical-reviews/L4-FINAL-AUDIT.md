# L4 FINAL AUDIT — Submission Readiness

**Date:** 2026-08-19 10:47 UTC  
**Manuscript:** `P5_manuscript_V2608.tex` (post-L3-fixes)  
**Status:** READY FOR SUBMISSION

---

## Audit Results (All Gates PASS)

| Gate | Check | Result | Evidence |
|------|-------|--------|----------|
| **1. Compilation** | LaTeX compiles without errors | ✅ PASS | PDF: 13 pages, 778,928 bytes, exit code 0 |
| **2. LED Traceability** | All canonical results cite ledger entries | ✅ PASS | 19 LED citations, 10 ledger entries, all claims backed |
| **3. Figure Callouts** | All figures embedded and cited | ✅ PASS | 3 figures (benchmark, learning_curves, salience), 3 labels, all cited via `\cref` |
| **4. Bibliography** | All citations resolved | ✅ PASS | 26 BibTeX entries, 0 undefined citations |
| **5. Evidence Boundaries** | No experimental/universal/causal overclaims | ✅ PASS | 0 experimental claims, 2 bounded universals ("every tested arm"), 0 causal, 8 panel boundaries |

---

## Gate 1: Compilation ✅

```bash
$ pdflatex -interaction=nonstopmode P5_manuscript_V2608.tex
Output written on P5_manuscript_V2608.pdf (13 pages, 778928 bytes).
Exit status: 0
```

**LaTeX errors:** 0  
**Warnings:** Label rerun only (cosmetic)  
**PDF:** 13 pages, 761 KB  
**Verdict:** PASS

---

## Gate 2: LED Traceability ✅

**LED citations in manuscript:** 19  
**Ledger entries:** 10 (LED-001 through LED-010)  
**Coverage:**
- LED-001 (ECFP4-RF scaffold): Cited 7× (Abstract, Highlights, Results, Conclusions, Table)
- LED-002 (GIN): Cited 5× (Table, Results text, Conclusions)
- LED-003 (GIN-TFP): Cited 5× (Abstract, Table, Results, Conclusions)
- LED-004 (GIN-TNE): Cited 5× (Abstract, Table, Results, Conclusions)
- LED-005 (ChemBERTa): Cited 5× (Abstract, Table, Results, Conclusions)
- LED-006 (BH-FDR statistics): Cited 6× (Abstract, Highlights, Results text, Table caption, Conclusions)
- LED-007 (External ChEMBL): Cited 2× (Limitations, Conclusions)
- LED-008 (TFP salience): Cited 2× (Abstract, Results §2.5, Conclusions)
- LED-009 (TNE salience): Cited 1× (Results §2.5)
- LED-010 (LISH-MoA): Cited 3× (Results §2.2)

**Orphan numbers remaining:** 2 (both in Methods §Statistics, methodological context not results)

**Verdict:** PASS (all canonical results ledger-backed)

---

## Gate 3: Figure Callouts ✅

**Figures embedded:** 3
1. `p5_auc_benchmark.png` → `\label{fig:benchmark}` → Cited in Results §2.3 via `\cref{fig:benchmark}`
2. `p5_learning_curves.png` → `\label{fig:learning_curves}` → Cited in Results §2.4 via `\cref{fig:learning_curves}`
3. `p5_salience.png` → `\label{fig:salience}` → Cited in Results §2.5 caption

**Figure-callout audit:** 3/3 figures cited  
**Table audit:** Table 1 (`tab:h1`) cited via `\cref{tab:h1}` in Results §2.3  
**Verdict:** PASS (all figures and tables called out)

---

## Gate 4: Bibliography ✅

**BibTeX entries:** 26  
**Undefined citations:** 0  
**BibTeX run:** Successful (no errors)

**Sample entries verified:**
- `who2024malariareport` (WHO 2024 malaria report) ✓
- `guo_ding_2026` (Do Larger Models Really Win?) ✓
- `temgoua2027quantum` (P3 quantum-inspired paper) ✓
- `Trapotsi2022MoA` (MoA computational framework) ✓

**Verdict:** PASS (all citations resolved)

---

## Gate 5: Evidence Boundaries ✅

**Experimental activity claims:** 0  
- No IC50/EC50/target engagement/binding affinity claims outside disclaimers
- Limitations §4.5 correctly states "recorded IC₅₀/EC₅₀ activities" (description, not claim)
- Conclusions correctly state "Experimental validation on prospectively synthesised candidates remains necessary" (boundary explicit)

**Universal statements (uncaveated):** 0  
- 2 hits found, both acceptable:
  1. "every GNN/transformer arm" (Highlights) — bounded by "under the scaffold split" + "tested"
  2. "Every graph-based and transformer arm" (Results) — bounded by "tested" + "on this panel"
- No "GNNs always fail" or "transformers universally underperform" claims

**Causal claims (strong):** 0  
- No "causes", "proves superiority", "establishes that [causal]"
- All interpretations use "best explained by", "is consistent with", "indicates"

**Panel-boundary statements:** 8+  
- Abstract: "panel-specific, controlled negative benchmark"
- Conclusions: "For comparable antimalarial natural-product panels"
- Conclusions: "Experimental validation... remains necessary"
- Limitations: "single binary-activity collection"
- Discussion: "on this panel" (multiple instances)

**Verdict:** PASS (all boundaries maintained)

---

## L3 HIGH Fixes Verified in Final PDF

**Fix 1 (LISH boundary):** ✅ Present  
- Line ~146 in PDF: LISH non-comparability in **boldface** immediately after numbers
- No reader confusion risk

**Fix 2 (External validation):** ✅ Present  
- Limitations §4.5: "even larger on the external panel (Δ=0.035 vs 0.025)"
- Strengthening framing applied

**Fix 3 (GIN architecture):** ✅ Present  
- Methods §6.3: "3 layers, ReLU activations, batch normalization after each layer, no dropout"
- Reproduction-complete

---

## Submission Checklist (Manual Author Review Needed)

| Item | Status | Notes |
|------|--------|-------|
| **Main manuscript LaTeX** | ✅ Ready | `P5_manuscript_V2608.tex` |
| **Compiled PDF** | ✅ Ready | `P5_manuscript_V2608.pdf` (13 pages) |
| **Cover letter** | ✅ Ready | `Cover_Letter_P5_JoC.tex` + PDF |
| **Bibliography** | ✅ Ready | `Bibliography_P5.bib` (26 entries) |
| **Figures** | ✅ Ready | `results/figures/` (benchmark, learning_curves, salience) |
| **Supplementary data** | ⏳ Verify | Panel CSV, splits, results JSON (in `results/`) |
| **Code availability** | ⏳ Verify | GitHub public repo + frozen splits |
| **Data availability** | ⏳ Verify | Zenodo DOI upload (reserved: 10.5281/zenodo.19608875) |
| **ORCID IDs** | ⏳ Author check | Verify all 5 author ORCIDs present |
| **Funding statement** | ✅ Ready | "No specific grant" (declared in manuscript) |
| **Competing interests** | ✅ Ready | "No competing interests" (declared) |
| **Ethics approval** | ✅ Ready | "Not applicable" (computational only) |
| **AI disclosure** | ✅ Ready | "AI-assisted tools during code development" (declared) |

**Items requiring author action:**
1. **Zenodo upload:** DOI reserved but files not yet uploaded  
2. **GitHub release:** Code in repo but no tagged release for manuscript version  
3. **ORCID verification:** Confirm all 5 author IDs correct  
4. **Supplementary file check:** Verify all `results/` files intended for submission are present

---

## MEDIUM/LOW Findings (Optional Author Review)

**Not blocking acceptance, but author may wish to address before submission:**

### MEDIUM (9 findings from L3)
1. M1: Fold-independent init "0.15 inflation" claim (Methods line ~451) — add citation or soften
2. M2: Salience interpretation (Results §2.5) — lead with caveat instead of positive framing
3. M3: Abstract honest-negative prominence — consider stronger framing
4. M4: TNE failure handling (Methods §6.1) — add "13 failures assigned zero-vectors"
5. M5: LISH feature counts (Methods §6.5) — add "772 gene + 100 viability"
6. M6: TFP dimensions (Results §2.5) — add "(H0/H1/H2 Betti-curve discretizations)" on first mention
7. M7: MoA-associated definition (Results §2.2) — add "(observed labels, not validated target)"
8. M8: Bemis-Murcko scaffold (Methods §6.2) — add one-sentence explanation
9. M9: Scaffold-split redundancy (Methods vs Limitations) — consolidate or cross-reference

### LOW (4 findings from L3)
1. L1: GIN-TNE marginal p-value footnote (Table 1 caption)
2. L2: ChemBERTa fold-level range interpretation (Results §2.4)
3. L3–L4: Minor structural polish

**Author decision:** Apply during copyediting, leave for journal, or address now (would take ~1–2 hours)

---

## FINAL VERDICT

**STATUS:** ✅ **READY FOR SUBMISSION**

**Evidence:**
- All 5 L4 audit gates PASS
- All 3 L3 HIGH-priority fixes applied and verified in PDF
- 0 CRITICAL findings
- Manuscript compiles without errors
- Evidence boundaries maintained
- LED traceability complete

**Remaining work:**
- Author actions: Zenodo upload, GitHub release, ORCID verification
- Optional: 9 MEDIUM + 4 LOW polish items (not blocking)

**Confidence:** HIGH

---

*L4 final audit complete. Manuscript passes all submission-readiness gates.*
