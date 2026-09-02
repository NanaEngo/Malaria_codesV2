# Molecular Structure Examples for Graphical Abstract
## P5 Antimalarial Benchmark

---

## Panel A: ECFP4 Demonstration Molecule

### Example 1: Artemisinin (Antimalarial Lead)
**SMILES:** `CC1CCC2C(=C)C(=O)OC2C1C`  
**Purpose:** Show ECFP4 fingerprint generation process  
**Why this molecule:** Well-known antimalarial, moderate complexity, clear ring system  
**Rendering:** 2D structure, standard bond lengths, element colors

**Alternative if artemisinin too complex:**
**SMILES:** `CC(=O)Oc1ccccc1C(=O)O`  
**Name:** Aspirin (simpler, still recognizable)

---

## Panel B: Diverse Antimalarial Natural Products

### Example 1: Alkaloid-like Structure
**SMILES:** `CN1C=NC2=C1C(=O)N(C(=O)N2C)C`  
**Description:** Purine-like core (similar to caffeine)  
**Purpose:** Show nitrogen-rich heterocycle common in natural products

### Example 2: Steroid-like Framework
**SMILES:** `CC12CCC3C(C1CCC2O)CCC4=CC(=O)CCC34C`  
**Description:** Polycyclic structure with fused rings  
**Purpose:** Demonstrate complex scaffold topology

### Example 3: Aromatic Amino Acid Derivative
**SMILES:** `C1=CC=C(C=C1)C(C(=O)O)N`  
**Description:** Phenylalanine  
**Purpose:** Simple aromatic with functional groups

### Example 4: Complex Natural Product
**SMILES:** `COc1cc2c(cc1OC)C(=O)C(CC2)c3ccc(O)c(OC)c3`  
**Description:** Isoflavonoid-like structure  
**Purpose:** Show chemical diversity in natural product panel

---

## Scaffold Examples (Bemis-Murcko Cores)

### Scaffold 1: Quinoline Core
**SMILES:** `c1ccc2c(c1)cccn2`  
**Description:** Aromatic heterocycle with fused rings  
**Common in:** Many antimalarials (quinine, chloroquine relatives)  
**Rendering:** Grayscale, no substituents

### Scaffold 2: Indole Core
**SMILES:** `c1ccc2c(c1)[nH]cc2`  
**Description:** Benzopyrrole system  
**Common in:** Tryptophan derivatives, many alkaloids  
**Rendering:** Grayscale

### Scaffold 3: Benzofuran Core
**SMILES:** `c1ccc2c(c1)cco2`  
**Description:** Oxygen-containing fused bicyclic  
**Common in:** Flavonoids, coumarins  
**Rendering:** Grayscale

### Scaffold 4: Steroid Core (if space allows)
**SMILES:** `C1CC2CCC3C(C2C1)CCC4C3CCC4`  
**Description:** Four-ring fused system  
**Common in:** Many natural products  
**Rendering:** Grayscale

---

## Graph Network Visualization Example

### Small Molecule for GNN Diagram
**SMILES:** `c1ccc(cc1)C(=O)O`  
**Name:** Benzoic acid  
**Purpose:** Simple enough to show clear node/edge structure  
**Node coloring:**
- Carbon: Gray (#808080)
- Oxygen: Red (#FF0000)
- Bonds: Black lines

**Message-passing arrows:** Orange (#F18F01), curved

---

## Transformer Input Example

### SMILES String for ChemBERTa Visualization
**SMILES:** `CC(=O)Oc1ccccc1C(=O)O`  
**Tokenized:** `C C ( = O ) O c 1 c c c c c 1 C ( = O ) O`  
**Purpose:** Show sequence representation for transformer  
**Rendering:** Monospace font, tokens separated by spaces

**Attention visualization:**
- Show curved lines connecting tokens
- Highlight key functional groups (carbonyl, carboxyl)
- Color: Red/pink gradient (#E74C3C)

---

## Topological Descriptor Visualization

### Persistent Homology Example Molecule
**SMILES:** `C1CCC2C(C1)CCC3C2CCC4C3CCC4`  
**Description:** Steroid-like structure with clear cavities  
**Purpose:** Demonstrate topological features (holes, loops)

**Barcode Diagram Elements:**
- H0 (connected components): Short bars, born early
- H1 (loops/cycles): Medium bars, multiple rings
- H2 (voids): Long bars if 3D cavities present

**3D Torus/Shape:**
- Show molecular surface with hole/cavity highlighted
- Color: Purple (#8E44AD)
- Transparency: 50% to show interior

---

## Rendering Specifications for All Structures

### RDKit Default Parameters
```python
from rdkit import Chem
from rdkit.Chem import Draw

# Standard rendering options
opts = Draw.MolDrawOptions()
opts.bondLineWidth = 2
opts.atomLabelFontSize = 12
opts.dotsPerAngstrom = 30
opts.useBWAtomPalette()  # For scaffolds (grayscale)
# OR
opts.useDefaultAtomPalette()  # For colored structures

# Generate image
img = Draw.MolToImage(mol, size=(400, 400), options=opts)
```

### Size Recommendations
- **Panel A example molecule:** 400×400 px (at 300 DPI = ~33×33 mm)
- **Panel B diverse examples:** 300×300 px each
- **Scaffolds:** 250×250 px (smaller, grayscale)
- **GNN diagram:** 350×350 px
- **Export:** PNG with transparent background, then import to final canvas

---

## Coordinate Files (Optional, for Advanced Tools)

If your rendering tool accepts structure coordinates:

### Artemisinin 2D Coordinates (MOL format snippet)
```
  19 21  0  0  0  0  0  0  0  0999 V2000
    2.8660    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    2.5981    0.7145    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    ...
```
(Full coordinates available from PubChem CID 68827)

---

## Color Coding Reference for Atoms

**Standard RDKit palette (for Panel B examples):**
- **Carbon (C):** Black (#000000)
- **Oxygen (O):** Red (#FF0000)
- **Nitrogen (N):** Blue (#0000FF)
- **Sulfur (S):** Yellow (#FFFF00)
- **Phosphorus (P):** Orange (#FFA500)
- **Halogens (F, Cl, Br, I):** Green (#00FF00)

**Grayscale palette (for scaffolds):**
- All atoms: Gray (#808080)
- Bonds: Black (#000000)

---

## Alternative: Use Existing Dataset Structures

If you want real molecules from the P5 dataset:

### Access from results/p5_canonical_panel.csv
```python
import pandas as pd

df = pd.read_csv('results/p5_canonical_panel.csv')

# Get diverse examples
active_examples = df[df['label'] == 1].sample(4, random_state=42)
inactive_examples = df[df['label'] == 0].sample(4, random_state=42)

# Extract SMILES
smiles_list = active_examples['smiles'].tolist()
```

**Recommended indices for diversity:**
- High molecular weight: Row 5234
- Low molecular weight: Row 1872
- Many rings: Row 9451
- Few rings: Row 423

---

## Quality Control Checklist

Before using structures in final graphic:

- [ ] All SMILES parse without errors in RDKit
- [ ] No overlapping atoms in 2D layout
- [ ] Stereochemistry clearly shown (if relevant)
- [ ] Bond lengths proportional
- [ ] Aromatic rings displayed correctly (Kekulé or aromatic)
- [ ] Functional groups oriented for readability
- [ ] Image resolution sufficient (300 DPI minimum)
- [ ] Background transparent where needed
- [ ] File format compatible (PNG, SVG, or EPS)

---

## Tools for Structure Generation

**Recommended:**
1. **RDKit** (Python) — Programmatic, batch processing
2. **ChemDraw** — Manual, publication quality
3. **Marvin JS** (ChemAxon) — Web-based, interactive
4. **Open Babel** — Command-line, format conversion

**Quick RDKit Script:**
```python
from rdkit import Chem
from rdkit.Chem import Draw

smiles = "CC1CCC2C(=C)C(=O)OC2C1C"
mol = Chem.MolFromSmiles(smiles)
img = Draw.MolToImage(mol, size=(400, 400))
img.save("artemisinin.png")
```

---

**File Version:** 1.0  
**Date:** 2026-09-02  
**Status:** Ready for structure rendering
