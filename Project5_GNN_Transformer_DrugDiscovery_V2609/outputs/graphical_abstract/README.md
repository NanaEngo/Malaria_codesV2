# Graphical Abstract Generation Package — P5 Antimalarial Benchmark
## Complete Files for AI-Assisted and Manual Creation

**Project:** Scaffold-Controlled Evaluation of Molecular Representations for Antimalarial Activity Prediction  
**Journal:** Journal of Computer-Aided Molecular Design (JCAMD)  
**Manuscript Version:** V2608  
**Package Created:** 2026-09-02

---

## 📦 Package Contents

This directory contains everything needed to generate a professional graphical abstract using multiple AI tools or manual design software.

```
outputs/graphical_abstract/
├── README.md                          ← You are here
├── 00_MASTER_PROMPT.md               ← Universal prompt (all tools)
├── 01_structured_elements.json       ← Machine-readable specifications
├── 02_detailed_storyboard.md         ← Panel-by-panel visual instructions
├── 03_molecular_examples.md          ← SMILES strings and structure specs
├── 04_color_palette.md               ← Hex codes + accessibility audit
├── 05_text_content.txt               ← All labels for copy-paste
└── 06_tool_specific_prompts/
    ├── nanobana_prompt.md            ← Optimized for Nano Banana/Scientific Schematics
    ├── chatgpt_prompt.txt            ← Optimized for ChatGPT/GPT-4
    ├── dalle_prompt.txt              ← Optimized for DALL-E image generation
    ├── midjourney_prompt.md          ← Optimized for Midjourney v6
    └── biorender_manual_guide.md     ← Step-by-step manual assembly
```

---

## 🎯 Quick Start Guide

### Option 1: Nano Banana / Scientific Schematics (RECOMMENDED)
**Best for:** Scientific diagrams with accurate data visualization

1. Open Nano Banana or Scientific Schematics tool
2. Load `06_tool_specific_prompts/nanobana_prompt.md`
3. Generate initial draft
4. Refine using `00_MASTER_PROMPT.md` for details
5. Import molecular structures from `03_molecular_examples.md`
6. Apply colors from `04_color_palette.md`

**Expected quality:** High (scientific conventions, clean lines, accurate charts)

---

### Option 2: ChatGPT (GPT-4 with Vision/DALL-E)
**Best for:** Iterative refinement with natural language guidance

1. Copy full content of `06_tool_specific_prompts/chatgpt_prompt.txt`
2. Paste into ChatGPT
3. Request initial generation
4. Iterate with refinements: "Make the ECFP4 bar more prominent", "Add patterns to bars for colorblind accessibility"
5. Use `02_detailed_storyboard.md` to correct specific elements

**Expected quality:** Medium to High (may need 3-5 iterations)

---

### Option 3: DALL-E (Standalone Image Generation)
**Best for:** Quick visual mockups, stylistic inspiration

1. Copy `06_tool_specific_prompts/dalle_prompt.txt`
2. Paste into DALL-E interface
3. Generate image
4. **Note:** Text may be illegible; expect to add text overlays manually
5. Use as visual base and add text/labels in PowerPoint or Illustrator

**Expected quality:** Medium (good visuals, imperfect text/accuracy)

---

### Option 4: Midjourney v6
**Best for:** Aesthetic quality, stylistic variants

1. Use `/imagine` command with `06_tool_specific_prompts/midjourney_prompt.md`
2. Generate multiple variants (expect 3-5 iterations)
3. Upscale best result (4x)
4. **Note:** Text rendering may be poor; plan to overlay text manually
5. Best used as artistic base + manual text addition

**Expected quality:** High aesthetics, Low accuracy (requires post-processing)

---

### Option 5: Manual Assembly (BioRender, PowerPoint, Illustrator, Inkscape)
**Best for:** Complete control, publication-ready precision

1. Follow step-by-step guide in `06_tool_specific_prompts/biorender_manual_guide.md`
2. Set up canvas: 170 mm × 100 mm at 300 DPI
3. Import molecular structures generated from `03_molecular_examples.md`
4. Build each panel following grid specifications
5. Apply colors from `04_color_palette.md`
6. Add patterns to bars for accessibility
7. Export as PDF (print) and PNG (web)

**Expected quality:** Highest (full control, guaranteed accuracy)  
**Time required:** 2-6 hours depending on experience

---

## 📊 What the Graphical Abstract Shows

### **Three-Panel Story:**

**Panel A: The Scientific Question**
- Left: ECFP4 fingerprints (classical cheminformatics)
- Right: Learned models (GNN, Topological, Transformer)
- Challenge: Can learned representations outperform classical fingerprints under scaffold extrapolation?

**Panel B: The Experimental Workflow**
- Data: 19,836 antimalarial molecules
- Splits: Random vs. Scaffold (Bemis-Murcko, held-out frameworks)
- Models: 5 approaches (ECFP4-RF, GIN, GIN-TFP, GIN-TNE, ChemBERTa)
- Evaluation: ROC AUC with 5×5 cross-validation (25 replicates)

**Panel C: The Result (Honest-Negative Finding)**
- Bar chart: ECFP4-RF wins (0.8300 ROC AUC) ⭐
- All learned models significantly lower (0.7867-0.8138)
- Callout: Topological descriptors visible but don't improve ranking
- Conclusion: Classical methods remain the reference

---

## 🎨 Key Visual Elements

### Must-Have Features:
1. ✅ **Gold star** on ECFP4-RF bar (winner emphasis)
2. ✅ **Bold border** around scaffold split box (key protocol)
3. ✅ **Patterns** on all bars (colorblind accessibility)
4. ✅ **Yellow callout box** with "Honest-Negative Finding"
5. ✅ **Error bars** on all 5 ROC AUC bars
6. ✅ **Significance stars (*** )** on learned model bars
7. ✅ **High contrast** text (readable at 300 DPI print)

### Color Palette (Colorblind-Safe):
- **ECFP4/Classical:** Blue #2E86AB
- **GNN:** Orange #F18F01
- **Topological:** Purple #8E44AD
- **Tensor Network:** Dark Purple #9B59B6
- **Transformer:** Red #E74C3C
- **Winner Accent:** Gold #FFD700
- **Background:** Off-white #F8F9FA

*(Full palette with accessibility audit in `04_color_palette.md`)*

---

## 📐 Technical Specifications

- **Dimensions:** 170 mm width × 100 mm height (landscape)
- **Orientation:** Landscape (horizontal)
- **Resolution:** 300 DPI minimum
- **Color Space:** RGB for web, CMYK for print
- **File Format:** PDF (print submission), PNG (web display)
- **Typography:** Sans-serif (Arial or similar), 8-14 pt range
- **Accessibility:** WCAG AA compliant, colorblind-safe, patterns on bars

---

## 🔍 File Guide

### Core Documentation:
- **`00_MASTER_PROMPT.md`** — Start here. Universal prompt that works for all AI tools. Contains complete visual description, layout instructions, and style guidelines.

- **`01_structured_elements.json`** — Machine-readable specifications for programmatic rendering. Use if building custom rendering pipeline.

- **`02_detailed_storyboard.md`** — Panel-by-panel construction guide with exact measurements, element positions, and styling. Essential for manual assembly.

### Supporting Materials:
- **`03_molecular_examples.md`** — SMILES strings, rendering specifications, and RDKit/ChemDraw instructions for generating molecular structures.

- **`04_color_palette.md`** — Complete color specifications with hex codes, RGB/CMYK values, contrast ratios, colorblind simulation results, and pattern recommendations.

- **`05_text_content.txt`** — All text labels in plain format for easy copy-paste. Includes numerical data, abbreviations, and SMILES strings.

### Tool-Specific Prompts:
- **`nanobana_prompt.md`** — Optimized for scientific diagram tools (Nano Banana, scientific-schematics skill)
- **`chatgpt_prompt.txt`** — Natural language prompt for ChatGPT with iterative refinement strategy
- **`dalle_prompt.txt`** — Image generation prompt for DALL-E with visual style parameters
- **`midjourney_prompt.md`** — Keyword-optimized prompt with Midjourney parameters and iteration strategy
- **`biorender_manual_guide.md`** — Step-by-step assembly guide for manual design tools (328 lines, most detailed)

---

## ✅ Quality Checklist

Before finalizing your graphical abstract, verify:

### Content Accuracy:
- [ ] All ROC AUC values correct (0.8300, 0.8138, 0.8090, 0.8047, 0.7867)
- [ ] Panel count correct (19,836 molecules)
- [ ] Replication scheme stated (5 folds × 5 seeds = 25 replicates)
- [ ] Statistical method mentioned (Paired t-test + BH correction)
- [ ] All 5 models labeled correctly

### Visual Elements:
- [ ] Gold star visible on ECFP4-RF bar
- [ ] Bold border around scaffold split box
- [ ] Patterns visible on all bars (not just colors)
- [ ] Error bars present on all 5 bars
- [ ] Significance markers (*** ) on learned model bars
- [ ] Yellow callout box stands out
- [ ] Molecular structures high quality (no pixelation)

### Accessibility:
- [ ] Colorblind-safe palette (no red-green only)
- [ ] Patterns distinguish bars in grayscale
- [ ] All text ≥8 pt (prefer 9-10 pt)
- [ ] High contrast text (>4.5:1 ratio)
- [ ] Alternative text description provided

### Technical:
- [ ] Dimensions 170×100 mm at 300 DPI
- [ ] PDF export with embedded fonts (for print)
- [ ] PNG export at 300 DPI (for web)
- [ ] File size reasonable (<10 MB)
- [ ] Print preview looks professional

---

## 🚀 Workflow Recommendations

### For Maximum Quality (Publication Submission):
1. **Generate with Nano Banana** → Get accurate scientific diagram base
2. **Import to Illustrator/Inkscape** → Refine text, adjust spacing
3. **Add patterns manually** → Ensure accessibility
4. **Export as PDF** → High-quality vector for print
5. **Generate PNG** → For online supplementary materials

### For Speed (Conference Poster):
1. **Generate with ChatGPT** → Quick first draft
2. **Refine with 2-3 iterations** → Correct any inaccuracies
3. **Add text overlays in PowerPoint** → Fix illegible labels
4. **Export as PNG** → Good enough for poster

### For Exploration (Multiple Variants):
1. **Try Midjourney + DALL-E** → Generate 5-10 variants with different styles
2. **Select best aesthetic** → Choose most professional-looking
3. **Manual assembly** → Rebuild selected design with accurate data
4. **Final polish** → Export publication-ready version

---

## 📞 Support & Troubleshooting

### If text is illegible (DALL-E, Midjourney):
- Use generated image as background/style reference only
- Add all text overlays manually in PowerPoint or Illustrator
- Copy exact labels from `05_text_content.txt`

### If colors are wrong:
- Check `04_color_palette.md` for exact hex codes
- Use eyedropper tool to match colors
- Convert to CMYK for print using color profile "ISO Coated v2"

### If layout is off:
- Follow grid specifications in `02_detailed_storyboard.md`
- Use guides at: 5mm, 30mm, 65mm, 95mm (horizontal separators)
- Maintain 5mm margins on all sides

### If molecular structures are pixelated:
- Generate new structures at 400×400 px minimum
- Use RDKit script from `03_molecular_examples.md`
- Export as PNG at 300 DPI before importing

### If patterns don't show:
- Manually add patterns in design software
- PowerPoint: Format Shape → Pattern Fill
- Illustrator: Swatches → New Pattern
- Ensure 50% opacity overlay (not 100%)

---

## 📚 Additional Resources

### Molecular Structure Generation:
- **RDKit** (Python): `from rdkit import Chem; from rdkit.Chem import Draw`
- **ChemDraw**: Manual drawing with professional quality
- **Marvin JS** (ChemAxon): Web-based, free for academic use
- **PubChem**: Download existing structures by CID

### Color Testing:
- **Coblis**: https://www.color-blindness.com/coblis-color-blindness-simulator/
- **WebAIM Contrast Checker**: https://webaim.org/resources/contrastchecker/
- **ColorBrewer**: https://colorbrewer2.org/ (scientific palettes)

### Design Software (Free):
- **Inkscape**: https://inkscape.org/ (vector graphics, like Illustrator)
- **GIMP**: https://www.gimp.org/ (raster graphics, like Photoshop)
- **BioRender**: https://biorender.com/ (scientific illustrations, free tier)

---

## 📝 Citation & Attribution

When using AI-generated graphical abstract in publication:

**In Methods or Acknowledgments:**
> "The graphical abstract was generated using [Tool Name] with human review and editing. All data representations were verified against the manuscript results."

**AI Disclosure (if required by journal):**
> "AI tools were used to assist with graphical abstract design. All scientific content was verified by the authors. No AI system is listed as an author."

---

## 📄 License & Usage

This package is part of the P5 antimalarial benchmark project:
- **Code Repository:** https://github.com/NanaEngo/Malaria_codesV2
- **License:** MIT (for prompt files and specifications)
- **Manuscript Status:** Under final review before JCAMD submission
- **Zenodo DOI:** 10.5281/zenodo.19608875 (upload pending)

You may adapt these prompts for your own scientific graphical abstracts. Please cite the P5 manuscript if using this package as a template for similar benchmark studies.

---

## ✨ Version History

- **v1.0** (2026-09-02): Initial release
  - 7 core files + 5 tool-specific prompts
  - Colorblind-safe palette with accessibility audit
  - Comprehensive manual assembly guide
  - All molecular structures and exact data values

---

## 📧 Contact

For questions about this graphical abstract package:
- **Primary Contact:** Myke Vital Sao Temgoua (myke-vital.sao@facsciences-uy1.cm)
- **Project Repository:** https://github.com/NanaEngo/Malaria_codesV2
- **Issues/Feedback:** Open an issue on the repository

---

**Good luck with your graphical abstract generation!**  
Remember: Iterate, verify, and always check against the manuscript data. 🎯
