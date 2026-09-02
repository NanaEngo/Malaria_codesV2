# Graphical Abstract — Master Prompt
## P5: Scaffold-Controlled Evaluation of Molecular Representations for Antimalarial Activity Prediction

**Target Journal:** Journal of Computer-Aided Molecular Design (JCAMD, Springer)  
**Manuscript Status:** Complete, under final review before submission  
**Visual Type:** Graphical abstract (single-page scientific illustration)  
**Orientation:** Landscape (horizontal)  
**Dimensions:** 170 mm width × 100 mm height (double-column width)  
**Resolution:** 300 DPI minimum  
**Color Palette:** Colorblind-safe (no red-green only)

---

## Scientific Story (Three-Panel Narrative)

### Panel A: THE QUESTION (Top third, ~30% vertical space)
**Visual Elements:**
- **Left side:** ECFP4 fingerprint representation (circular Morgan fingerprint visualization, 2048-bit)
  - Show molecular structure → hashed circular neighborhoods → bit vector
  - Label: "ECFP4 Fingerprints (classical)"
  
- **Center:** VS symbol (versus) with question mark
  
- **Right side:** Learned representations (three icons):
  1. **GNN** — Graph neural network (molecular graph with colored nodes/edges, message-passing arrows)
  2. **Topological** — Persistent homology (barcode diagram + 3D shape showing holes/cavities)
  3. **Transformer** — Sequence model (SMILES string with attention heads)
  
- **Below:** Chemical shift arrow
  - Label: "Under Scaffold Extrapolation (Bemis-Murcko split)"
  - Show 2-3 example scaffolds (ring systems) being held out

**Text Overlay:**
> **Can learned graph/sequence representations outperform ECFP4 fingerprints  
> on antimalarial natural products under chemical distribution shift?**

**Color Scheme:**
- ECFP4 side: Blue tones (#2E86AB, #A23B72)
- Learned side: Orange/Purple tones (#F18F01, #8E44AD)
- Background: Light gray (#F8F9FA)

---

### Panel B: THE EXPERIMENT (Middle third, ~35% vertical space)
**Visual Workflow (Left to Right):**

1. **Data** (leftmost)
   - Icon: Database cylinder
   - Label: "19,836 molecules"
   - Sub-label: "African antimalarial natural products"
   - Show 3-4 example molecular structures (diverse scaffolds)

2. **Arrow →**

3. **Splits** (center-left)
   - Two-path split:
     - **Top path:** "Random Split" (shuffled molecules icon)
     - **Bottom path:** "Scaffold Split" (grouped by framework)
   - Visual: Show molecule → scaffold extraction → group assignment
   - Key: Whole scaffold groups held out (not individual molecules)

4. **Arrow →**

5. **Models** (center-right)
   - Five model boxes stacked vertically:
     1. ECFP4-RF (500 trees)
     2. GIN (Graph Isomorphism Network)
     3. GIN-TFP (+ Persistent Homology)
     4. GIN-TNE (+ Tensor Network)
     5. ChemBERTa (Pretrained Transformer)
   - Icon for each: fingerprint/graph/topology/tensor/text

6. **Arrow →**

7. **Evaluation** (rightmost)
   - ROC curve icon
   - Label: "ROC AUC"
   - Sub-label: "5 folds × 5 seeds = 25 replicates"
   - Statistical test: "Paired t-test + BH correction"

**Background:** Gradient from light blue (left) to light orange (right)

---

### Panel C: THE RESULT (Bottom third, ~35% vertical space)
**Main Visual: Horizontal Bar Chart**

**Data (Mean ROC AUC under Scaffold Split):**
1. **ECFP4-RF:** 0.8300 (longest bar, blue, **bold border**)
2. **GIN-TFP:** 0.8138 (orange)
3. **GIN-TNE:** 0.8090 (purple)
4. **GIN:** 0.8047 (teal)
5. **ChemBERTa:** 0.7867 (red/pink)

**Bar styling:**
- X-axis: 0.75 to 0.85 (focused range to show differences)
- Error bars: ±SD across 5 per-seed means (thin black lines)
- Significance stars: *** above each learned model bar (p < 0.05 after BH correction)
- ECFP4-RF bar: Blue fill with gold star ⭐ at the end

**Callout Box (right side of bars):**
Title: **"Honest-Negative Finding"**
- ✅ ECFP4-RF wins under scaffold split
- ✅ Topological descriptors visible in fusion (high salience)
- ❌ But do NOT improve ranking vs. baseline
- 📊 Advantage concentrated in OOD tail (low-similarity deciles)

**Bottom Text Strip:**
> **Conclusion:** Classical fingerprints + random forests remain the reference  
> for antimalarial natural products under chemical extrapolation.  
> Learned representations show interpretable signal but do not close the predictive gap.

**Color Legend (small, bottom-right corner):**
- Blue: Classical (ECFP4)
- Orange/Purple/Teal: Graph-based (GNN + fusion)
- Pink: Transformer (ChemBERTa)

---

## Overall Layout Instructions

```
┌─────────────────────────────────────────────────────────────┐
│  PANEL A: THE QUESTION (30% height)                         │
│  ┌──────────┐       ┌──────────┐       ┌──────────┐        │
│  │  ECFP4   │  VS?  │   GNN    │       │Topologi- │        │
│  │Fingerprnt│       │Graph Net │       │cal + TF  │        │
│  └──────────┘       └──────────┘       └──────────┘        │
│           Under Scaffold Extrapolation →                    │
├─────────────────────────────────────────────────────────────┤
│  PANEL B: THE EXPERIMENT (35% height)                       │
│  [Data] → [Splits] → [Models] → [Evaluation]               │
│   19,836     Random     ECFP4-RF      ROC AUC               │
│  molecules  Scaffold      GIN        5×5 CV                 │
├─────────────────────────────────────────────────────────────┤
│  PANEL C: THE RESULT (35% height)                           │
│  ┌──────────────────────────────────────────────────┐      │
│  │ ECFP4-RF    ████████████████████ 0.8300 ⭐       │      │
│  │ GIN-TFP     ██████████████████ 0.8138 ***       │      │
│  │ GIN-TNE     █████████████████ 0.8090 ***        │      │
│  │ GIN         █████████████████ 0.8047 ***        │      │
│  │ ChemBERTa   ███████████████ 0.7867 ***          │      │
│  └──────────────────────────────────────────────────┘      │
│  [Honest-Negative Finding callout box]                      │
└─────────────────────────────────────────────────────────────┘
```

---

## Typography Guidelines

- **Title font:** Sans-serif, bold, 14-16 pt
- **Section headers:** Sans-serif, bold, 11-12 pt
- **Labels:** Sans-serif, regular, 9-10 pt
- **Data values:** Sans-serif, bold, 10 pt
- **Avoid:** Serif fonts, cursive, decorative fonts
- **Readability:** High contrast (dark text on light background)

---

## Accessibility Requirements

1. **Color blindness:** Use patterns/textures in addition to color
   - ECFP4 bar: Solid fill + diagonal hatching
   - GNN bars: Different patterns (dots, horizontal lines, vertical lines)
   
2. **High contrast:** All text >4.5:1 contrast ratio against background

3. **Text size:** Minimum 8 pt for all labels (prefer 9-10 pt)

4. **Alternative text description (for web):**
   > "Three-panel graphical abstract showing scaffold-controlled molecular representation benchmark. Panel A compares ECFP4 fingerprints versus learned graph/transformer models under chemical extrapolation. Panel B illustrates workflow from 19,836 antimalarial molecules through random and scaffold splits to five models evaluated by ROC AUC. Panel C shows horizontal bar chart where ECFP4-RF achieves highest ROC AUC (0.8300), statistically outperforming all learned models under scaffold split. Callout box emphasizes honest-negative finding: classical fingerprints remain reference despite interpretable topological signals in learned representations."

---

## Key Numbers to Include

- **Panel A:** Scaffold extrapolation (Bemis-Murcko)
- **Panel B:** 19,836 molecules, 5×5 CV (25 replicates)
- **Panel C:** 
  - ECFP4-RF: 0.8300
  - GIN-TFP: 0.8138 (Δ = -0.016)
  - GIN-TNE: 0.8090 (Δ = -0.021)
  - GIN: 0.8047 (Δ = -0.025)
  - ChemBERTa: 0.7867 (Δ = -0.043)

---

## Style References

**Molecular structures:** RDKit default rendering (2D, high quality)  
**Graph networks:** PyTorch Geometric style (colored nodes, thick edges)  
**Color palette:** ColorBrewer qualitative set (colorblind-safe)  
**Bar chart:** Matplotlib/Seaborn scientific style (grid lines, clean axes)

---

## Delivery Format

- **For print:** PDF, 300 DPI, CMYK color space
- **For web:** PNG, 300 DPI, RGB color space, transparent background optional
- **Vector preferred:** SVG or EPS for scalability
- **File naming:** `P5_GraphicalAbstract_JCAMD_v1.{pdf,png,svg}`

---

## Output Files in This Package

1. `00_MASTER_PROMPT.md` ← You are here
2. `01_structured_elements.json` — Machine-readable element specifications
3. `02_detailed_storyboard.md` — Panel-by-panel visual instructions
4. `03_molecular_examples.md` — SMILES strings and structure coordinates
5. `04_color_palette.md` — Hex codes and accessibility audit
6. `05_text_content.txt` — All text labels for copy-paste
7. `06_tool_specific_prompts/` — Optimized prompts for Nano Banana, ChatGPT, DALL-E, Midjourney

---

## Usage Instructions for AI Tools

### For Nano Banana / Scientific Schematics:
```
Use 00_MASTER_PROMPT.md + 01_structured_elements.json
Focus on scientific diagram conventions (clean lines, labeled arrows, clear data visualization)
```

### For ChatGPT / GPT-4 Vision:
```
Use 00_MASTER_PROMPT.md + 02_detailed_storyboard.md
Request iterative refinement: "Generate draft, then improve based on scientific poster standards"
```

### For DALL-E / Midjourney:
```
Use 06_tool_specific_prompts/dalle_prompt.txt or midjourney_prompt.txt
These are natural-language optimized for image generation models
```

### For BioRender / Manual Tools:
```
Use 02_detailed_storyboard.md + 03_molecular_examples.md
Follow layout grid and import molecular structures as SVG/PNG
```

---

**Generated:** 2026-09-02  
**Project:** P5 GNN/Transformer Antimalarial Benchmark  
**Manuscript Version:** V2608  
**Status:** Ready for graphical abstract generation
