# BioRender / Manual Assembly Guide — P5 Graphical Abstract
## For PowerPoint, Illustrator, Inkscape, or BioRender

---

## Setup

**Canvas:**
- Dimensions: 170 mm × 100 mm (6.7" × 3.9")
- Resolution: 300 DPI
- Color mode: RGB (convert to CMYK for print)
- Background: White (#FFFFFF)

**Tools:**
- **BioRender:** Use "Custom Canvas" → 170×100 mm
- **PowerPoint:** Page Setup → Custom → 6.7" × 3.9"
- **Illustrator:** New Document → 170×100 mm, 300 PPI
- **Inkscape:** File → Document Properties → 170×100 mm

---

## Grid Layout (use guides)

Horizontal guides at:
- 0 mm (top edge)
- 5 mm (top margin)
- 30 mm (Panel A/B boundary)
- 65 mm (Panel B/C boundary)
- 95 mm (bottom margin)
- 100 mm (bottom edge)

Vertical guides at:
- 0 mm, 5 mm (left edge, left margin)
- 85 mm (center)
- 165 mm, 170 mm (right margin, right edge)

---

## Panel A: The Question (0-30 mm vertical)

### Step 1: Background boxes
- Rectangle: 5-30 mm vertical, 10-55 mm horizontal, fill #E3F2FD (light blue)
- Rectangle: 5-30 mm vertical, 95-160 mm horizontal, fill #FFF3E0 (light orange)

### Step 2: ECFP4 side (left)
1. **Import molecular structure** (artemisinin from `03_molecular_examples.md`)
   - Position: 20-35 mm horizontal, 8-18 mm vertical
   - Size: 15×10 mm
   - Source: RDKit PNG or ChemDraw export

2. **Add arrow down**
   - Line: 27.5 mm horizontal, 18-20 mm vertical
   - Style: Solid, 2 pt, black
   - Label: "radius=2" (Arial, 8 pt)

3. **Draw circular neighborhoods**
   - 5-7 concentric circles (gray #808080, 1 pt, dashed)
   - Center: 27.5 mm horizontal, 22.5 mm vertical
   - Radii: 3, 5, 7 mm

4. **Add arrow down**
   - Same as previous
   - Label: "hash → bits"

5. **Create bit vector bar**
   - Rectangle: 15-40 mm horizontal, 26-28 mm vertical
   - Fill: Horizontal stripes (blue #2E86AB and white)
   - Border: Black, 1 pt
   - Label below: "2048-bit fingerprint" (Arial, 8 pt)

6. **Text label**
   - Position: Centered below (17-38 mm horizontal, 28.5 mm vertical)
   - Text: "ECFP4 Fingerprints\n(Classical Cheminformatics)"
   - Font: Arial Bold, 9 pt, center-aligned

### Step 3: VS symbol (center)
- Position: 82-88 mm horizontal, 12-20 mm vertical
- Text: "VS?" (Arial Black, 24 pt, #212529)
- Optional: Question mark icon above

### Step 4: Learned models side (right)
**Three stacked icons:**

1. **GNN (top, 97-158 mm horizontal, 8-13 mm vertical)**
   - Import molecular graph PNG or draw:
     - 8 circles (5 mm diameter, colored by atom)
     - Black lines between circles (1 pt)
     - Orange curved arrows (#F18F01, 2 pt)
   - Label right: "GNN\n(Graph Isomorphism)" (Arial, 8 pt)
   - Border: Orange #F18F01, 1 pt

2. **Topological (middle, 97-158 mm, 14-19 mm)**
   - Draw barcode diagram (5 horizontal bars at different heights, purple)
   - Import 3D torus PNG or draw oval with hole
   - Label: "Persistent Homology\n(TDA)" (Arial, 8 pt)
   - Border: Purple #8E44AD, 1 pt

3. **Transformer (bottom, 97-158 mm, 20-25 mm)**
   - Text: "C C ( = O ) O ..." (Courier, 8 pt, monospace)
   - Curved lines connecting letters (red #E74C3C, 1 pt, dashed)
   - Label: "ChemBERTa\nTransformer" (Arial, 8 pt)
   - Border: Red #E74C3C, 1 pt

### Step 5: Bottom caption
- Rectangle: 5-165 mm horizontal, 26-29 mm vertical, fill #FFFACD
- Arrow: Left to right, 2 pt, black
- Text: "Under Scaffold Extrapolation (Bemis-Murcko Split)" (Arial Bold, 10 pt)
- Import 3 scaffold structures (gray, 10×10 mm each)
- Overlay red "X" or "HELD OUT" stamp on each

### Step 6: Question overlay
- Rectangle: 10-160 mm horizontal, 2-5 mm vertical
- Fill: #FFFACD, 80% opacity
- Border: None
- Text: "Can learned graph/sequence representations outperform ECFP4 fingerprints on antimalarial natural products under chemical distribution shift?"
- Font: Arial Bold, 9 pt, center-aligned

---

## Panel B: The Experiment (30-65 mm vertical)

### Step 1: Workflow elements (left to right)

**Element 1: DATA (10-40 mm horizontal)**
- Draw database cylinder (3D effect):
  - Top oval: 25 mm horizontal, 37 mm vertical, 10 mm wide, 3 mm tall
  - Side rectangles: Light blue fill #AED6F1
- Text above: "19,836 molecules" (Arial Bold, 10 pt)
- Text below: "African antimalarial\nnatural products" (Arial, 8 pt)
- Import 4 molecular structures in 2×2 grid below (12×12 mm each)

**Arrow 1 (40-45 mm horizontal)**
- Black arrow, 3 pt, pointing right
- Label above: "split" (Arial, 8 pt)

**Element 2: SPLITS (45-75 mm horizontal)**
- Two rectangles stacked:
  - Top: 46-74 mm horizontal, 35-40 mm vertical, fill #D5F4E6 (light green)
    - Text: "Random Split\nStratified 5-fold" (Arial, 8 pt)
    - Icon: Shuffled circles
  - Bottom: 46-74 mm horizontal, 42-52 mm vertical, fill #FDE4CF (light orange)
    - Text: "Scaffold Split\nBemis-Murcko groups held out" (Arial Bold, 9 pt)
    - Border: **Black, 3 pt, bold**
    - Visual: 3 groups of molecules (same scaffold, different colors)

**Arrow 2 (75-80 mm horizontal)**
- Label: "train"

**Element 3: MODELS (80-120 mm horizontal)**
- 5 stacked rectangles (38 mm wide, 6 mm tall each, 1 mm spacing):
  1. 81-119 mm, 36-42 mm: Blue #2E86AB, text "ECFP4-RF (500 trees)"
  2. 81-119 mm, 43-49 mm: Orange #F18F01, text "GIN (3 layers)"
  3. 81-119 mm, 50-56 mm: Purple #8E44AD, text "GIN-TFP (+PersHomology)"
  4. 81-119 mm, 57-63 mm: Dark purple #9B59B6, text "GIN-TNE (+TensorNet)"
  5. 81-119 mm, 64-70 mm: Red #E74C3C, text "ChemBERTa (pretrained)"
- All text: White, Arial Bold, 9 pt, centered
- Label above: "5 Models Evaluated" (Arial, 8 pt)

**Arrow 3 (120-125 mm horizontal)**
- Label: "evaluate"

**Element 4: EVALUATION (125-165 mm horizontal)**
- Draw ROC curve (simple):
  - Axes: 130-155 mm horizontal, 35-60 mm vertical
  - Diagonal curve from (0,0) to (1,1), blue #2E86AB, 2 pt
  - Shaded area under curve, light blue fill
- Text below: "ROC AUC\n5 folds × 5 seeds\n= 25 replicates" (Arial, 8 pt)
- Box below: Dashed gray border, text "Paired t-test + BH correction" (Arial Italic, 7 pt)

---

## Panel C: The Result (65-100 mm vertical)

### Step 1: Bar chart (10-105 mm horizontal)

**Setup:**
- X-axis: 15-100 mm horizontal, 90 mm vertical
  - Scale: 0.75 to 0.85
  - Ticks: 0.75, 0.77, 0.79, 0.81, 0.83, 0.85
  - Label: "ROC AUC (Scaffold Split)" (Arial Bold, 10 pt)
- Y-axis: 15 mm horizontal, 70-90 mm vertical
  - 5 tick positions (one per model)
- Grid: Vertical lines at each x-tick, light gray #DEE2E6, 0.5 pt
- Title: "Mean ROC AUC under Scaffold Split" (Arial Bold, 11 pt, centered above)

**Bars (8 mm tall each, 2 mm spacing):**
1. **ECFP4-RF (topmost, 70-78 mm vertical)**
   - Length: 0.8300 → 97 mm horizontal (from scale)
   - Fill: Blue #2E86AB
   - Pattern: Diagonal hatching (45°, 2 pt lines, 3 mm spacing, overlay at 50% opacity)
   - Border: Black, 3 pt
   - Error bar: ±0.0023 (horizontal line with caps at 97±2 mm)
   - Label left: "ECFP4-RF" (Arial, 9 pt, blue)
   - Label right: "**0.8300**" (Arial Bold, 10 pt)
   - Marker: Gold star (⭐, 5 mm) at bar end

2. **GIN-TFP (79-87 mm vertical)**
   - Length: 0.8138 → 85 mm
   - Fill: Purple #8E44AD
   - Pattern: Horizontal lines (1 pt, 2 mm spacing)
   - Error bar: ±0.0107
   - Label left: "GIN-TFP" (purple)
   - Label right: "0.8138 ***"

3. **GIN-TNE (88-96 mm vertical)**
   - Length: 0.8090 → 82 mm
   - Fill: Dark purple #9B59B6
   - Pattern: Vertical lines (1 pt, 2 mm spacing)
   - Error bar: ±0.0149
   - Label: "GIN-TNE ... 0.8090 ***"

4. **GIN (97-105 mm vertical)**
   - Length: 0.8047 → 78 mm
   - Fill: Orange #F18F01
   - Pattern: Dots (2 mm diameter, 4 mm grid)
   - Error bar: ±0.0141
   - Label: "GIN ... 0.8047 ***"

5. **ChemBERTa (106-114 mm vertical)**
   - Length: 0.7867 → 60 mm
   - Fill: Red #E74C3C
   - Pattern: Cross-hatch (±45°)
   - Error bar: ±0.0054
   - Label: "ChemBERTa ... 0.7867 ***"

### Step 2: Callout box (110-165 mm horizontal, 68-90 mm vertical)
- Rectangle: 50 mm wide × 22 mm tall
- Fill: Yellow #FFFACD
- Border: Black, 2 pt
- Padding: 2 mm all sides

**Content:**
- Title: "Honest-Negative Finding" (Arial Bold, 11 pt, underlined, centered)
- 4 bullet points (Arial, 8 pt, 1.5 line spacing):
  - ✅ (green checkmark icon, 4 mm) "**ECFP4-RF wins** under scaffold split"
  - ✅ "**Topological descriptors visible** in fusion\n   (high projection-weight salience)"
  - ❌ (red X icon, 4 mm) "**But do NOT improve ranking** vs. baseline"
  - 📊 (chart icon, 4 mm) "**Advantage concentrated in OOD tail**\n   (low-similarity deciles)"
- Bold key phrases

### Step 3: Conclusion strip (bottom, 5-165 mm horizontal, 91-96 mm vertical)
- Rectangle: Fill #E9ECEF (light gray)
- Text: "Conclusion: Classical fingerprints + random forests remain the reference for antimalarial natural products under chemical extrapolation. Learned representations show interpretable signal but do not close the predictive gap."
- Font: Arial, 8 pt, black, center-aligned
- Padding: 1 mm vertical

---

## Asset Imports

**Molecular structures:**
- Generate from SMILES (see `03_molecular_examples.md`) using:
  - RDKit (Python script)
  - ChemDraw (manual)
  - Marvin JS (web)
- Export as PNG at 400×400 px, 300 DPI
- Import and resize to specified dimensions

**Icons:**
- Database, ROC curve, checkmarks, X, chart: Use BioRender library or noun project
- Alternative: FontAwesome icons or manual drawing

---

## Pattern Fills (Accessibility)

If your tool doesn't support pattern fills directly:

**PowerPoint:**
- Insert shape → Right-click → Format Shape → Fill → Pattern Fill → Choose pattern

**Illustrator:**
- Swatches panel → New Swatch → Pattern → Create pattern

**Inkscape:**
- Object → Fill and Stroke → Pattern → Choose pattern

**BioRender:**
- May not support patterns directly → Export and add patterns in post-processing

---

## Export Settings

**For print submission:**
- File → Export → PDF
- High Quality Print preset
- Embed all fonts
- CMYK color mode (convert in Acrobat if needed)
- 300 DPI minimum

**For web display:**
- File → Export → PNG
- RGB color mode
- 300 DPI
- Transparent background: No (use white)

---

## Quality Checklist

Before finalizing:
- [ ] All text readable at 100% zoom (minimum 8 pt)
- [ ] Colors match hex codes in `04_color_palette.md`
- [ ] Patterns visible on all bars
- [ ] Gold star present on ECFP4-RF bar
- [ ] Scaffold split box has bold border
- [ ] All molecular structures high quality (no pixelation)
- [ ] Grid lines subtle but visible
- [ ] Error bars present on all 5 bars
- [ ] Conclusion strip text fits without wrapping awkwardly
- [ ] File size reasonable (<10 MB for PNG, <5 MB for PDF)
- [ ] Print preview at actual size (170×100 mm) looks professional

---

## Estimated Assembly Time

- **Experienced user:** 2-3 hours
- **First-time user:** 4-6 hours
- **Using pre-made templates:** 1-2 hours

---

**Tool:** Manual assembly (PowerPoint, Illustrator, Inkscape, BioRender)  
**Difficulty:** Medium to High  
**Advantages:** Full control over every element, guaranteed accuracy  
**Disadvantages:** Time-consuming, requires design software familiarity
