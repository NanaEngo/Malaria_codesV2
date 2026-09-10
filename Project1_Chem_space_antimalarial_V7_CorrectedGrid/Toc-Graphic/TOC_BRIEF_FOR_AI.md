# TOC Graphic Brief — AI Generation Package
## Paper: "Target breadth and mutation resilience in African-natural-product-inspired antimalarial chemotypes: a computational analysis"
### Journal: Journal of Chemical Information and Modeling (JCIM / ACS)
### Version: V8 revision (2026-09-10)

---

## 1. MANDATORY TECHNICAL SPECIFICATIONS

These are non-negotiable ACS requirements. The AI tool must produce output that satisfies all of them.

| Parameter | Required value |
|---|---|
| **Width** | 3.25 inches (8.26 cm) |
| **Height** | 1.75 inches (4.45 cm) |
| **Aspect ratio** | 1.857 : 1 (landscape) |
| **Resolution** | ≥ 300 dpi (minimum); 1200 dpi preferred for text-bearing artwork |
| **Pixel size at 300 dpi** | 975 × 525 px |
| **Pixel size at 1200 dpi** | 3900 × 2100 px |
| **Color mode** | RGB (no CMYK, no transparency/alpha channel) |
| **File format (submission)** | TIFF with LZW compression + separate PDF vector |
| **Background** | Solid white (#FFFFFF) |
| **Font** | Readable at 300 dpi; minimum ~6 pt equivalent |
| **No decorative borders** | ACS prohibits decorative frames around the entire graphic |
| **No journal name, author names, or affiliation** | Must not appear in the image |
| **No promotional language** | "novel", "breakthrough", "superior" etc. are prohibited |

> If you are generating with ChatGPT/DALL-E or Gemini Imagen and cannot control exact DPI at generation time, generate at maximum resolution and we will resize/resample in post-processing. The image must be **exactly 3.25 × 1.75 inches** in the final submitted TIFF.

---

## 2. WHAT THE PAPER IS ABOUT (scientific context for the AI)

This is a **computational drug discovery** paper with an African-context angle. Here is the story in three sentences:

1. We built a large hybrid library (65,856 molecules) from **African natural products** (ANP) and synthetic antimalarials, then filtered it down to **19,913 synthesizable leads** using machine learning and multi-parameter optimization.
2. A **17-molecule polypharmacology cohort** was docked against **four drug targets** of *Plasmodium falciparum* (the malaria parasite): PfDHFR (folate metabolism), PfCRT (chloroquine-resistance transporter), PfClpP (proteostasis), PfATP4 (ion regulation).
3. For each molecule, we computed a **Resistance-Resilience Score (RRS)** by docking against drug-resistance mutants and measuring how much the docking score changes — yielding classes A* (most resilient), B, C. Five top candidates (PP-15, PP-05, PP-06, PP-11, PP-13) scored favorably on all four targets AND achieved A* resilience.

**The central message the TOC graphic must communicate:**
> African natural-product-inspired chemical space → multi-target computational screening → mutation-resilient antimalarial candidates

**The tone:** scientific, clean, informative. Not pharmaceutical-advertisement style. Not overly flashy. JCIM readers are computational chemists who value clarity over decoration.

---

## 3. PROPOSED VISUAL NARRATIVE (choose ONE of the three options below)

### Option A — "Three-panel funnel + heatmap strip" (RECOMMENDED)
This is the most scientifically informative and works well in 3.25 × 1.75 in.

**Left panel (~30% of width): Chemical space funnel**
- Top: small cluster of stylized molecules labeled "African Natural Products + Synthetic Antimalarials"
- Downward-pointing funnel arrow
- Middle: "65,856 molecules"
- Another narrowing arrow
- Bottom: "17-member cohort (Set C)"
- Color palette: warm earth tones (ochres, terracottas) to evoke Africa

**Center panel (~40% of width): Four-target docking**
- Four small protein silhouettes or schematic protein icons, labeled:
  - PfDHFR (enzyme, folate)
  - PfCRT (transporter, membrane)
  - PfClpP (protease barrel)
  - PfATP4 (P-type ATPase)
- Small molecule shown docking into each (stick representation or stylized binding pocket)
- Connecting lines from the "17-member cohort" to all four targets
- Color: cool blues/teals for the protein targets

**Right panel (~30% of width): RRS classification output**
- A simplified color-coded grid or bar:
  - A* (green, 7 candidates) — "Mutation-resilient"
  - B (yellow, 4 candidates)
  - C (orange, 6 candidates)
- Highlight: "5 candidates: 4/4 targets + A* class"
- A small star or diamond symbol marking the top candidates
- No numerical table — just the visual hierarchy

**Bottom text strip (very small, ~5pt):**
"Computational hypotheses only — no biological activity claimed"

---

### Option B — "Molecule + targets + RRS badge" (simpler, cleaner)
Good if the AI struggles with three-panel layouts.

**Left third:** One representative 2D chemical structure (use PP-15 SMILES below or the PNG in `reference_figures/structure_PP-15.png`). Label it "PP-15 (top candidate)". Surround it with a subtle warm-colored glow or halo.

**Center:** Four target labels arranged in a 2×2 grid with small icons:
```
PfDHFR    PfCRT
PfClpP    PfATP4
```
Dashed arrows from the molecule to all four targets. Label the arrows "AutoDock Vina docking".

**Right third:** A bold badge or seal:
```
A* Resilience
4/4 Targets
17-member cohort
```
With color coding: green for A*, teal for the target count, white background.

---

### Option C — "Workflow diagram" (most complex, most publishable)
Horizontal left-to-right workflow in five steps, each in a rounded rectangle:

```
[ANP Library] ──► [65,856 molecules] ──► [17-member cohort] ──► [4 targets docked] ──► [A*/B/C classes]
   396 seeds        Chemical-space           Set C               PfDHFR PfCRT          7 A* · 4 B · 6 C
   454 synthetics   expansion                polypharmacology    PfClpP PfATP4          5 top candidates
```

Color scheme: left warm (oranges/reds for library), center neutral (grays), right cool (greens for A*).

---

## 4. EXACT DATA TO INCLUDE (all numbers are from the manuscript — do not change them)

| Element | Value |
|---|---|
| Seed library | 396 African natural products + 454 synthetic antimalarials |
| Library size | 65,856 unique molecules |
| Prioritized leads | 19,913 synthesizable |
| Cohort | 17 candidates (Set C) |
| Targets | PfDHFR, PfCRT, PfClpP, PfATP4 |
| Docking pairs | 68/68 passing geometric criterion |
| RRS A* | 7 candidates |
| RRS B | 4 candidates |
| RRS C | 6 candidates |
| Top candidates | PP-15, PP-05, PP-06, PP-11, PP-13 (all: 4/4 targets + A*) |
| Best candidate | PP-15 (RRS_mean = 115.6%, the highest) |

**Numbers that must NOT appear in the TOC** (too detailed for TOC, could be misleading out of context):
- Exact Vina scores (kcal/mol values)
- p-values or rho values
- RMSD values
- AUC values

---

## 5. COLOR PALETTE (scientifically appropriate, accessible)

| Element | Color | Hex |
|---|---|---|
| Background | White | #FFFFFF |
| African NP / library (warm) | Terracotta | #C1440E |
| African NP / library (warm) | Warm ochre | #D4A017 |
| Protein targets (cool) | Teal | #0D9488 |
| Protein targets (cool) | Steel blue | #1D4ED8 |
| A* class (best) | Forest green | #15803D |
| B class | Amber | #D97706 |
| C class | Slate | #64748B |
| Text (main) | Near-black | #0F172A |
| Text (secondary) | Dark slate | #334155 |
| Evidence boundary note | Muted red | #7C2D12 |

> These are suggestions. The AI may adapt them, but the overall feel should be **clean, scientific, uncluttered**. Avoid neon, gradients that obscure text, or dark backgrounds that reduce contrast.

---

## 6. STYLE GUIDELINES

**Do:**
- Use clean sans-serif typography (Helvetica, Arial, or similar)
- Use simple geometric shapes for protein representations (no photorealistic protein ribbon diagrams — they are too complex at this size)
- Use thin arrows with arrowheads to show workflow direction
- Label every element; nothing should require legend-reading from the paper
- Leave adequate white space — this is a tiny canvas (3.25 × 1.75 in)
- Keep all text at minimum 6 pt equivalent at 300 dpi (i.e., ≥ 18 px tall at 300 dpi)

**Do not:**
- Include journal logos or ACS branding
- Use photorealistic protein 3D structures (too complex, unreadable at this size)
- Use more than 3–4 distinct colors
- Include the full 17-molecule structure grid (too dense)
- Use decorative clipart of Africa, mosquitoes, or pills (unprofessional for JCIM)
- Add shadows or 3D effects that clutter the layout
- Include copyright notices, DOIs, or URLs

---

## 7. REFERENCE MATERIALS IN THIS FOLDER

All files are in the `reference_figures/` subfolder.

| File | Description | Use for |
|---|---|---|
| `structure_PP-15.png` | 2D chemical structure of top candidate PP-15 | Option B (main molecule) or Option A decorative |
| `structure_PP-05.png` | 2D chemical structure of PP-05 | Optional |
| `structure_PP-06.png` | 2D chemical structure of PP-06 | Optional |
| `structure_PP-11.png` | 2D chemical structure of PP-11 | Optional |
| `structure_PP-13.png` | 2D chemical structure of PP-13 | Optional |
| `top5_structures_grid.png` | Grid of all 5 top structures side-by-side | Reference only (too dense for TOC) |
| `p1_v7_rrs_mutation_profiles.png` | Heatmap of RRS values (Figure 1 of paper) | Visual reference for RRS concept; do NOT reproduce directly |
| `p1_v7_chemical_space_coverage.png` | Chemical space scatter plot (SM Figure) | Visual reference for funnel concept |
| `p1_v7_targetwise_profile_summary.png` | Bar chart of per-target mean Vina scores | Visual reference for 4-target panel |
| `p1_v7_exploratory_metric_relationships.png` | Scatter plots PNS-RRS and ACSI-RRS | Background context only |
| `v7_toc_graphic_previous.tiff` | The V7 TOC graphic (previous submission) | See what the previous design looked like; the new one should be a significant improvement |

---

## 8. SMILES STRINGS FOR TOP 5 CANDIDATES

Use these if the AI tool accepts SMILES input for structure rendering.

```
PP-15:  COc1c(O)cc2c(c1O)C(=O)C([C@H](O)c1ccccc1)CO2
PP-05:  COc1ccc(-c2cc(=O)c3c(O)cc(O)cc3o2)cc1
PP-06:  COc1cc([C@@H]2CC(=O)c3ccc(O)cc3O2)cc(CC=C(C)C)c1O
PP-11:  COc1cc(O)c2c(=O)c(O)c(-c3ccc(O)c(OC)c3)oc2c1
PP-13:  CC(=O)OC1C(=O)c2c(O)cc(O)cc2O[C@H]1c1ccc(O)cc1
```

PP-15, PP-05, PP-06, and PP-11 are **flavonoid-like scaffolds** (oxygen-containing aromatic ring systems common in African plants). PP-13 has a chromone/flavanonol-type scaffold. These structural families are visually recognizable as plant-derived natural product chemotypes — important for the narrative.

---

## 9. PROMPTS FOR AI IMAGE GENERATION

### For ChatGPT (GPT-4o with DALL-E 3):

```
Create a publication-quality scientific graphic for a computational chemistry journal article.
The graphic must be exactly 3.25 inches wide by 1.75 inches tall (landscape orientation), white background, RGB color mode.

The graphic shows a three-panel workflow:
LEFT PANEL: A downward-pointing funnel showing chemical space reduction. Top: stylized molecular structures labeled "African Natural Products + Synthetic Antimalarials (65,856 molecules)". Bottom of funnel: "17-member cohort". Use warm terracotta and ochre colors.

CENTER PANEL: Four protein target boxes arranged in a 2×2 grid, labeled PfDHFR, PfCRT, PfClpP, PfATP4. Show dashed arrows from the funnel output to all four targets. Use teal and steel blue colors. Small chemical structure (flavonoid-like ring system) shown docking.

RIGHT PANEL: A color-coded bar or badge showing resistance-resilience classification: A* (7, forest green), B (4, amber), C (6, slate gray). Bold label: "5 candidates: 4/4 targets + A* resilience".

Style: Clean, minimal, scientific (Journal of Chemical Information and Modeling). No decorative clipart. Sans-serif typography. All text readable at small size. No borders around the entire image.
```

### For Google Gemini (Imagen 3):

```
Design a compact scientific infographic for a peer-reviewed computational drug discovery paper.
Format: 3.25 × 1.75 inch landscape, white background, RGB.

Tell this story visually in a left-to-right flow:
1. LEFT: Chemical library funnel — African plant-derived molecules (natural product ring systems) being filtered from 65,856 to 17 prioritized drug candidates. Warm orange/terracotta palette.
2. CENTER: The 17 candidates being computationally docked against 4 malaria parasite proteins (PfDHFR, PfCRT, PfClpP, PfATP4). Show a small flavonoid structure entering a protein binding pocket. Teal/blue palette.
3. RIGHT: Classification output — color-coded boxes for A* (green, 7 molecules), B (amber, 4), C (gray, 6). Star symbol for "5 top candidates with 4/4 target coverage and A* mutation resilience."

Scientific style — clean lines, no clipart, minimal decoration. Font: Helvetica or Arial equivalent. Suitable for Journal of Chemical Information and Modeling.
```

### For Adobe Firefly / Midjourney (image-to-image starting from reference):

Use `v7_toc_graphic_previous.tiff` as the starting reference image and add the prompt:
```
Redesign this scientific TOC graphic. Keep the three-panel layout and white background. Improve: replace text-only center with small 2D flavonoid chemical structure docking into a schematic protein binding pocket. Make the left funnel more visual with stylized molecular cluster icons. Make the right RRS panel cleaner with a color-coded A*/B/C legend. Maintain 3.25:1.75 inch landscape proportions. Scientific journal quality, sans-serif fonts, no decorative elements.
```

---

## 10. POST-GENERATION CHECKLIST (verify before submission)

After the AI generates the image, verify each item:

- [ ] Image dimensions exactly 3.25 × 1.75 inches when opened in image editor
- [ ] Resolution ≥ 300 dpi (check Image > Image Size in Photoshop/GIMP)
- [ ] Color mode is RGB (not CMYK, not Grayscale)
- [ ] No alpha/transparency channel
- [ ] Background is pure white (no off-white or cream)
- [ ] All text is readable (zoom to 100% at 300 dpi)
- [ ] No author names, journal name, DOI, or URLs visible
- [ ] No promotional language ("novel", "breakthrough")
- [ ] Saved as TIFF with LZW compression (not ZIP, not uncompressed)
- [ ] Also save a PDF vector version for LaTeX inclusion (`p1_v8_toc_graphic.pdf`)
- [ ] Filename for submission: `p1_v8_toc_graphic_ACS.tiff`

---

## 11. NOTES ON THE PREVIOUS (V7) TOC GRAPHIC

The file `reference_figures/v7_toc_graphic_previous.tiff` shows the old version. It is a **programmatically generated Matplotlib figure** — functional but purely text-based with colored boxes. It does NOT show any molecular structure, protein representation, or visual chemistry.

**What to improve in V8:**
1. Include at least one actual 2D chemical structure (PP-15 is the priority, as the top candidate)
2. Use proper protein schematic icons rather than just text boxes for the four targets
3. The funnel visualization should be more visual (molecular cluster → narrowing funnel → cohort)
4. The RRS output should use color coding more effectively
5. The overall composition should be immediately recognizable as a drug discovery paper

---

*Brief prepared: 2026-09-10 | Based on V8 manuscript (Main + SI fully read)*
*Paper DOI: to be assigned | Zenodo: https://doi.org/10.5281/zenodo.22686176*
