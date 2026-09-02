# Nano Banana Prompt — P5 Graphical Abstract
## Optimized for Scientific Schematics Tool

---

**Target:** Create a three-panel landscape scientific graphical abstract  
**Dimensions:** 170 mm × 100 mm at 300 DPI  
**Style:** Clean, professional, publication-ready for Journal of Computer-Aided Molecular Design

---

## High-Level Description

Create a three-panel horizontal layout showing a molecular machine learning benchmark:

1. **Top panel (30% height):** Comparison between classical ECFP4 fingerprints (left, blue) versus learned graph/transformer models (right, orange/purple/red) under scaffold extrapolation
2. **Middle panel (35% height):** Linear workflow from data (19,836 molecules) → splits (random/scaffold) → 5 models → ROC AUC evaluation
3. **Bottom panel (35% height):** Horizontal bar chart showing ECFP4-RF wins (0.8300 ROC AUC) with all learned models significantly lower, plus callout box emphasizing "honest-negative finding"

---

## Panel A Specifications

**Visual Layout:**
- Left third: ECFP4 fingerprint generation process
  - Molecular structure → circular neighborhoods (radius 2) → bit vector (2048 bits)
  - Use artemisinin or similar antimalarial as example structure
  - Blue color scheme (#2E86AB)
  
- Center: Large "VS?" text with question mark

- Right third: Three learned model icons stacked vertically
  - Graph Neural Network (molecular graph with message-passing arrows, orange)
  - Topological descriptors (persistent homology barcode + 3D shape, purple)
  - Transformer (SMILES sequence with attention, red)

- Bottom: Arrow labeled "Under Scaffold Extrapolation (Bemis-Murcko Split)" with 2-3 scaffold examples marked "HELD OUT"

**Key Text:**
> Can learned graph/sequence representations outperform ECFP4 fingerprints on antimalarial natural products under chemical distribution shift?

---

## Panel B Specifications

**Linear Workflow (4 steps, left to right):**

1. **DATA:** Database icon, label "19,836 molecules / African antimalarial natural products"
   - Show 4 diverse molecular structures below

2. **→ SPLITS:** Two-path diagram
   - Top path: "Random Split (Stratified 5-fold)" — light green background
   - Bottom path: "**Scaffold Split (Bemis-Murcko groups held out)**" — light orange background, **emphasized with bold border**
   - Show visual of molecules grouped by scaffold

3. **→ MODELS:** 5 stacked boxes, each a different color:
   - ECFP4-RF (blue)
   - GIN (orange)
   - GIN-TFP (purple)
   - GIN-TNE (dark purple)
   - ChemBERTa (red)

4. **→ EVALUATION:** ROC curve icon
   - Label: "ROC AUC / 5×5 CV = 25 replicates / Paired t-test + BH correction"

---

## Panel C Specifications

**Horizontal Bar Chart (60% of panel width):**
- X-axis: 0.75 to 0.85 (ROC AUC, Scaffold Split)
- Y-axis: 5 model names

**Bars (top to bottom):**
1. **ECFP4-RF:** 0.8300, blue, **bold border**, **gold star at end**, diagonal hatching pattern
2. **GIN-TFP:** 0.8138, purple, *** significance marker, horizontal line pattern
3. **GIN-TNE:** 0.8090, dark purple, ***, vertical line pattern
4. **GIN:** 0.8047, orange, ***, dot pattern
5. **ChemBERTa:** 0.7867, red, ***, cross-hatch pattern

Each bar includes error bars (thin black lines with caps).

**Callout Box (right, 35% of panel width):**
- Yellow background (#FFFACD), black border
- Title: "Honest-Negative Finding"
- 4 bullet points with icons:
  - ✅ ECFP4-RF wins under scaffold split
  - ✅ Topological descriptors visible in fusion (high salience)
  - ❌ But do NOT improve ranking vs. baseline
  - 📊 Advantage concentrated in OOD tail (low-similarity deciles)

**Bottom text strip:**
> Conclusion: Classical fingerprints + random forests remain the reference for antimalarial natural products under chemical extrapolation. Learned representations show interpretable signal but do not close the predictive gap.

---

## Style Requirements

- **Scientific diagram conventions:** Clean lines, clear labels, professional typography
- **Color palette:** Colorblind-safe (see `04_color_palette.md`)
- **Patterns:** Each bar has unique pattern in addition to color (accessibility)
- **Typography:** Arial or similar sans-serif, 8-14 pt range
- **High contrast:** All text readable at 300 DPI print resolution

---

## Key Emphasis Points

1. **ECFP4 wins** — Make this visually obvious (gold star, longest bar, bold)
2. **Scaffold split** — Emphasize this is the key protocol (bold border in Panel B)
3. **Honest-negative** — Not a failure, a methodologically rigorous result (callout box)
4. **Patterns + colors** — Ensure accessibility for colorblind viewers

---

## Technical Notes

- Export as PDF (CMYK, 300 DPI) for print submission
- Also export as PNG (RGB, 300 DPI) for web use
- Embed all fonts
- Use vector graphics where possible (molecular structures can be raster if high-res)

---

## Reference Files

- Master prompt: `00_MASTER_PROMPT.md`
- Structured elements: `01_structured_elements.json`
- Detailed layout: `02_detailed_storyboard.md`
- Molecular structures: `03_molecular_examples.md`
- Colors: `04_color_palette.md`
- Text labels: `05_text_content.txt`

---

**Tool:** Nano Banana / Scientific Schematics  
**Prompt Version:** 1.0  
**Date:** 2026-09-02
