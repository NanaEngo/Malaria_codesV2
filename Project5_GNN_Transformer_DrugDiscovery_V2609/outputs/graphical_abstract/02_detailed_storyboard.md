# Detailed Visual Storyboard — P5 Graphical Abstract
## Panel-by-Panel Construction Guide

**Canvas:** 170 mm (width) × 100 mm (height) at 300 DPI  
**Export:** PDF (print) + PNG (web)

---

## PANEL A: THE QUESTION (0-30 mm vertical)

### Layout Grid
```
┌─────────────────────────────────────────────────────────────┐
│  [5mm margin]                                                │
│  ┌──────────────┐    ┌──────┐    ┌──────────────┐          │
│  │   ECFP4      │    │ VS?  │    │   LEARNED    │          │
│  │  Classical   │    │  ?   │    │ GNN/Topo/TF  │          │
│  │  [diagram]   │    └──────┘    │  [diagram]   │          │
│  └──────────────┘                 └──────────────┘          │
│          ↓ Under Scaffold Extrapolation ↓                   │
│  [Example scaffolds being held out]                         │
└─────────────────────────────────────────────────────────────┘
```

### Element 1: ECFP4 Fingerprint Visualization (Left, 10-55 mm horizontal)
**Components:**
1. **Molecular Structure** (top, 15×15 mm square)
   - Example: Artemisinin or simple antimalarial scaffold
   - SMILES: `CC1CCC2C(=C)C(=O)OC2C1C`
   - 2D structure, high quality, RDKit rendering
   - Black bonds, element colors (C=black, O=red, N=blue)

2. **Arrow Down** (5 mm)
   - Solid black, 2 pt width
   - Label: "radius=2"

3. **Circular Neighborhoods** (middle, 20×20 mm)
   - Show concentric circles emanating from atoms
   - Color code by atom: gray circles
   - 3-4 example neighborhoods highlighted
   - Dashed lines showing hashing

4. **Arrow Down** (5 mm)
   - Label: "hash → bits"

5. **Bit Vector** (bottom, 40×8 mm bar)
   - Horizontal bar with 0/1 pattern
   - Color: Blue (#2E86AB) for "on" bits, white for "off"
   - Label below: "2048-bit fingerprint"

**Text Label (below diagram):**
> **ECFP4 Fingerprints**  
> (Classical Cheminformatics)

**Color:** Blue border (#2E86AB, 2pt)

---

### Element 2: Versus Symbol (Center, 75-85 mm horizontal)
**Design:**
- Large "VS?" text
- Font: Arial Bold, 24 pt
- Color: Dark gray (#212529)
- Centered vertically in panel
- Optional: Lightning bolt or question mark icon above

---

### Element 3: Learned Representations (Right, 95-160 mm horizontal)
**Three Sub-Panels (Stacked Vertically):**

#### 3a. Graph Neural Network (Top)
- **Icon:** Molecular graph with colored nodes
  - 8-10 atoms arranged as benzene + side chains
  - Nodes: Circles (5mm diameter), colored by atom type
  - Edges: Black lines (1pt)
  - Message-passing arrows: Orange curved arrows (#F18F01)
- **Label:** "GNN (Graph Isomorphism)"
- **Color:** Orange border (#F18F01)

#### 3b. Topological Descriptors (Middle)
- **Icon:** Persistent homology barcode + 3D shape
  - Left: Barcode diagram (5 horizontal bars at different heights)
  - Right: 3D torus or shape with hole showing topological feature
  - Color: Purple (#8E44AD)
- **Label:** "Persistent Homology (TDA)"
- **Color:** Purple border (#8E44AD)

#### 3c. Transformer (Bottom)
- **Icon:** SMILES string with attention mechanism
  - Text: "C C ( = O ) O ..."
  - Curved attention lines connecting tokens
  - Multi-head attention visualization
  - Color: Red/pink (#E74C3C)
- **Label:** "ChemBERTa Transformer"
- **Color:** Red border (#E74C3C)

---

### Element 4: Scaffold Extrapolation Caption (Bottom of Panel A)
**Position:** 5 mm from bottom edge, centered, full width

**Visual:**
- Horizontal arrow (left to right, 80 mm long)
- Label: **"Under Scaffold Extrapolation (Bemis-Murcko Split)"**
- Font: Arial Bold, 11 pt

**Scaffold Examples (below arrow):**
- Show 3 molecular scaffolds (just the core rings, no substituents)
- Example scaffolds:
  1. Quinoline: `c1ccc2c(c1)cccn2`
  2. Indole: `c1ccc2c(c1)[nH]cc2`
  3. Benzofuran: `c1ccc2c(c1)cco2`
- Each 10×10 mm, grayscale
- Red X or "HELD OUT" stamp overlaid

---

### Question Text (Overlaid, centered, top 3mm of panel)
**Text:**
> **Can learned graph/sequence representations outperform ECFP4 fingerprints  
> on antimalarial natural products under chemical distribution shift?**

**Styling:**
- Font: Arial Bold, 10 pt
- Color: Dark blue (#2E86AB)
- Background: Light yellow box (#FFFACD), 80% opacity
- Padding: 2 mm

---

## PANEL B: THE EXPERIMENT (30-65 mm vertical)

### Layout: Linear Workflow (Left to Right)
```
┌─────────────────────────────────────────────────────────────┐
│  [DATA] ──→ [SPLITS] ──→ [MODELS] ──→ [EVALUATION]         │
│   19K       Random        5 arms        ROC AUC             │
│  mols      Scaffold      ECFP4-RF       5×5 CV              │
└─────────────────────────────────────────────────────────────┘
```

---

### Step 1: DATA (10-40 mm horizontal)
**Icon:** Database cylinder (3D)
- Color: Light blue (#AED6F1)
- Size: 20×15 mm
- Label inside: "DB"

**Text (below icon):**
> **19,836 molecules**  
> African antimalarial  
> natural products

**Example Structures (below text):**
- Show 4 diverse molecular structures (each 12×12 mm)
- SMILES examples:
  1. `CN1C=NC2=C1C(=O)N(C(=O)N2C)C` (caffeine-like)
  2. `CC12CCC3C(C1CCC2O)CCC4=CC(=O)CCC34C` (steroid-like)
  3. `C1=CC=C(C=C1)C(C(=O)O)N` (aromatic amino acid)
  4. `COc1cc2c(cc1OC)C(=O)C(CC2)c3ccc(O)c(OC)c3` (natural product)
- Arranged in 2×2 grid

---

### Arrow 1 (40-45 mm horizontal)
- Solid black arrow (3 pt width)
- Label above: "split"

---

### Step 2: SPLITS (45-75 mm horizontal)
**Two-Path Diagram:**

#### Upper Path: Random Split
- Icon: Shuffled molecules (5 colored circles mixed)
- Text: "Random Split"
- Sub-text: "Stratified 5-fold"
- Color: Light green background (#D5F4E6)

#### Lower Path: Scaffold Split (emphasized)
- Icon: Molecules grouped by framework
  - Show 3 groups of molecules with same core scaffold
  - Group 1: Red border
  - Group 2: Blue border
  - Group 3: Green border
  - Arrow showing one group → TEST FOLD
- Text: "**Scaffold Split**" (bold)
- Sub-text: "Bemis-Murcko groups held out"
- Color: Light orange background (#FDE4CF)
- **Bold border** (this is the key protocol)

**Visual Detail:**
- Show molecular structure → extract scaffold → group assignment
- 3 steps illustrated with small diagrams

---

### Arrow 2 (75-80 mm horizontal)
- Solid black arrow
- Label above: "train"

---

### Step 3: MODELS (80-120 mm horizontal)
**Five Stacked Boxes (8 mm height each, 38 mm width):**

1. **ECFP4-RF** (top)
   - Icon: Fingerprint + tree
   - Color: Blue (#2E86AB)
   - Text: "ECFP4-RF (500 trees)"

2. **GIN**
   - Icon: Graph network
   - Color: Orange (#F18F01)
   - Text: "GIN (3 layers)"

3. **GIN-TFP**
   - Icon: Graph + topology barcode
   - Color: Purple (#8E44AD)
   - Text: "GIN-TFP (+PersHomology)"

4. **GIN-TNE**
   - Icon: Graph + tensor
   - Color: Dark purple (#9B59B6)
   - Text: "GIN-TNE (+TensorNet)"

5. **ChemBERTa** (bottom)
   - Icon: Text/attention
   - Color: Red (#E74C3C)
   - Text: "ChemBERTa (pretrained)"

**Label above boxes:** "5 Models Evaluated"

---

### Arrow 3 (120-125 mm horizontal)
- Solid black arrow
- Label above: "evaluate"

---

### Step 4: EVALUATION (125-165 mm horizontal)
**ROC Curve Icon (stylized):**
- Diagonal curve from (0,0) to (1,1)
- True Positive Rate vs False Positive Rate
- AUC shaded area
- Size: 25×25 mm

**Text (below curve):**
> **ROC AUC**  
> 5 folds × 5 seeds  
> = 25 replicates

**Statistics Box (bottom):**
- Border: Dashed gray
- Text: "Paired *t*-test + BH correction"
- Font: 8 pt, italic

---

## PANEL C: THE RESULT (65-100 mm vertical)

### Layout
```
┌─────────────────────────────────────────────────────────────┐
│  [Bar Chart: 60% width]    [Callout Box: 35% width]        │
│                                                              │
│  ECFP4-RF  ████████████████████ 0.8300 ⭐                   │
│  GIN-TFP   ██████████████████ 0.8138 ***                   │
│  GIN-TNE   █████████████████ 0.8090 ***                    │
│  GIN       █████████████████ 0.8047 ***                    │
│  ChemBERTa ███████████████ 0.7867 ***                      │
│                                                              │
│  [Conclusion text strip at bottom]                          │
└─────────────────────────────────────────────────────────────┘
```

---

### Bar Chart (10-105 mm horizontal)
**Chart Specifications:**
- Type: Horizontal bar chart
- Bars: 8 mm height each, 2 mm spacing
- X-axis: 0.75 to 0.85 (ROC AUC)
- Grid lines: Vertical, light gray, every 0.02 units

**Bar Details:**

1. **ECFP4-RF** (top bar)
   - Fill: Solid blue (#2E86AB)
   - Pattern: Diagonal hatching overlay
   - Border: Bold black (3 pt)
   - Length: Maps to 0.8300 on x-axis
   - Error bar: ±0.0023 (thin black lines with caps)
   - End marker: Gold star ⭐ (5 mm)
   - Label (right of bar): "**0.8300**" (bold)

2. **GIN-TFP**
   - Fill: Purple (#8E44AD)
   - Length: 0.8138
   - Error bar: ±0.0107
   - Significance: *** (above bar)
   - Label: "0.8138"

3. **GIN-TNE**
   - Fill: Dark purple (#9B59B6)
   - Length: 0.8090
   - Error bar: ±0.0149
   - Significance: ***
   - Label: "0.8090"

4. **GIN**
   - Fill: Orange (#F18F01)
   - Length: 0.8047
   - Error bar: ±0.0141
   - Significance: ***
   - Label: "0.8047"

5. **ChemBERTa** (bottom bar)
   - Fill: Red (#E74C3C)
   - Length: 0.7867
   - Error bar: ±0.0054
   - Significance: ***
   - Label: "0.7867"

**Y-Axis Labels (left of bars):**
- Font: Arial, 9 pt
- Color: Match bar color
- Model names left-aligned

**X-Axis:**
- Label (below): "ROC AUC (Scaffold Split)"
- Font: Arial Bold, 10 pt
- Tick marks: 0.75, 0.77, 0.79, 0.81, 0.83, 0.85

**Title (above chart):**
> **Mean ROC AUC under Scaffold Split**
- Font: Arial Bold, 11 pt
- Centered above bars

---

### Callout Box (110-165 mm horizontal)
**Box Styling:**
- Border: 2 pt solid black
- Background: Light yellow (#FFFACD)
- Padding: 5 mm
- Size: 50 mm width × 30 mm height

**Title (inside box, top):**
> **Honest-Negative Finding**
- Font: Arial Bold, 11 pt
- Underlined

**Content (4 bullet points):**
1. ✅ **ECFP4-RF wins** under scaffold split
2. ✅ **Topological descriptors visible** in fusion  
   (high projection-weight salience)
3. ❌ **But do NOT improve ranking** vs. baseline
4. 📊 **Advantage concentrated in OOD tail**  
   (low-similarity deciles)

**Styling:**
- Bullets: Icons (checkmark, cross, chart)
- Font: Arial, 9 pt
- Line spacing: 1.5
- Key phrases bolded

---

### Conclusion Text Strip (Bottom of Panel C)
**Position:** Full width, 3 mm from bottom

**Background:** Light gray (#E9ECEF)

**Text:**
> **Conclusion:** Classical fingerprints + random forests remain the reference for antimalarial natural products under chemical extrapolation. Learned representations show interpretable signal but do not close the predictive gap.

**Styling:**
- Font: Arial, 9 pt
- Color: Dark text (#212529)
- Padding: 2 mm vertical

---

## Cross-Panel Elements

### Separators Between Panels
- Horizontal lines (1 pt, light gray)
- Position: Between panels A-B (at 30 mm) and B-C (at 65 mm)

### Margin Consistency
- All panels: 5 mm margin on all sides
- Text never closer than 3 mm to panel edges

---

## Rendering Notes

1. **Layer Order (back to front):**
   - Background colors
   - Grid lines
   - Bars/shapes
   - Icons/diagrams
   - Text labels
   - Borders

2. **Anti-aliasing:** Enable for all curves and text

3. **Export Settings:**
   - PDF: Embed all fonts, CMYK color space
   - PNG: RGB, transparent background optional, 300 DPI

4. **Accessibility Check:**
   - Run color-blind simulator (Deuteranopia, Protanopia)
   - Verify all text >8 pt
   - Confirm patterns distinguishable in grayscale

---

## Measurement Reference
```
Full canvas: 170 × 100 mm
Panel A: 0-30 mm vertical (height: 30 mm)
Panel B: 30-65 mm vertical (height: 35 mm)
Panel C: 65-100 mm vertical (height: 35 mm)

Margins: 5 mm all sides
Usable width: 160 mm
Panel spacing: 3 mm
```

---

**Storyboard Version:** 1.0  
**Date:** 2026-09-02  
**Status:** Ready for rendering
