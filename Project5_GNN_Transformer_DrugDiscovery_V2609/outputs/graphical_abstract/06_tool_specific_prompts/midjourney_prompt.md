MIDJOURNEY PROMPT — P5 Graphical Abstract
==========================================

PRIMARY PROMPT:
/imagine prompt: Scientific infographic three-panel layout, landscape orientation, professional publication quality. TOP PANEL: molecular structure with blue circular fingerprint visualization versus orange graph network and purple topological shapes and red text sequence, "VS?" in center, arrow labeled "scaffold extrapolation" with held-out frameworks. MIDDLE PANEL: linear workflow diagram showing database icon with 19,836 molecules flowing through split paths (random and scaffold split emphasized) to five stacked model boxes in blue orange purple red, ending at ROC curve evaluation icon. BOTTOM PANEL: horizontal bar chart with five bars showing ROC AUC values 0.8300 (longest blue bar with gold star), 0.8138, 0.8090, 0.8047, 0.7867 (shortest red bar), patterns on each bar for accessibility, yellow callout box on right with "Honest-Negative Finding" title and checkmarks and X marks, gray conclusion strip at bottom. Clean modern scientific poster aesthetic, high contrast, colorblind-safe palette, sans-serif typography, 300 DPI quality, white background --ar 16:9 --style raw --v 6

---

PARAMETER BREAKDOWN:

ASPECT RATIO: --ar 16:9 (close to 170×100 mm landscape)

STYLE: --style raw (for clean, literal scientific diagram rather than artistic interpretation)

VERSION: --v 6 (latest Midjourney version for best text rendering)

QUALITY: --q 2 (high quality, worth the extra generation time)

---

ALTERNATIVE PROMPTS (Iterative Refinement):

PROMPT 2 (Simplified for better text):
/imagine prompt: Three-panel scientific diagram, landscape. Panel 1: blue molecular fingerprint VS orange graph network VS purple topology VS red transformer, question text overlay. Panel 2: workflow arrow diagram from database to evaluation through splits and models. Panel 3: horizontal bar chart with 5 bars showing values 0.83 to 0.79, blue bar longest with star, yellow callout box. Clean infographic style, high contrast, professional --ar 16:9 --style raw --v 6 --q 2

PROMPT 3 (Focus on bar chart panel):
/imagine prompt: Professional scientific bar chart showing ROC AUC comparison, five horizontal bars in blue purple orange red, values 0.8300 (top, longest, gold star) to 0.7867 (bottom), error bars, patterns on bars, grid lines, yellow callout box on right with bullet points, clean modern design --ar 3:2 --style raw --v 6

PROMPT 4 (Focus on workflow panel):
/imagine prompt: Scientific workflow diagram, left to right: database icon → split diagram with two paths → five stacked colored boxes → ROC curve icon, connected by arrows, clean modern infographic style, professional publication quality --ar 16:9 --style raw --v 6

---

KEYWORD GLOSSARY FOR MIDJOURNEY:

STYLE KEYWORDS:
- scientific infographic
- publication quality
- clean modern design
- professional poster aesthetic
- high contrast
- sans-serif typography
- medical illustration style
- technical diagram
- data visualization

LAYOUT KEYWORDS:
- three-panel layout
- horizontal panels
- landscape orientation
- stacked composition
- left-to-right workflow
- linear flow diagram

COLOR KEYWORDS:
- colorblind-safe palette
- blue orange purple red color scheme
- high contrast colors
- white background
- gold accent
- yellow callout box

TECHNICAL KEYWORDS:
- horizontal bar chart
- molecular structure
- graph network
- ROC curve
- error bars
- grid lines
- patterns and textures
- 300 DPI quality

---

POST-GENERATION REFINEMENT:

If text is illegible or poorly rendered:
1. Use --style raw and --v 6 explicitly
2. Simplify text to key numbers only (0.8300, etc.)
3. Generate panels separately and composite manually
4. Use upscale (U) buttons for better resolution

If colors are wrong:
1. Add explicit hex codes to prompt: "blue #2E86AB, orange #F18F01"
2. Use "vibrant" or "saturated" keywords
3. Avoid "pastel" or "muted" keywords

If layout is incorrect:
1. Generate each panel separately (use --ar 16:5 for panels)
2. Be more specific about element positions ("left third", "center", "right side")
3. Use reference images if available (--iw parameter)

---

ADVANCED PARAMETERS (optional):

--no photorealistic, watercolor, artistic (exclude unwanted styles)
--stylize 0 (minimize artistic interpretation, more literal)
--chaos 0 (more predictable, less variation)
--seed [number] (for reproducible iterations)

---

EXPECTED ITERATIONS:

Generation 1: Test overall composition, check if three panels are recognizable
Generation 2: Refine text legibility, adjust colors if needed
Generation 3: Focus on bar chart accuracy, ensure values are correct
Generation 4: Polish pass, verify all elements present
Generation 5 (if needed): Upscale and final export

---

EXPORT SETTINGS:

After generation:
1. Click "Upscale (4x)" for maximum resolution
2. Download PNG at highest quality
3. May need to add text overlays in Photoshop/Illustrator if Midjourney text is illegible
4. Convert to 170×100 mm at 300 DPI in design software

---

FALLBACK STRATEGY:

If Midjourney cannot render accurate scientific diagram:
- Use for visual inspiration only
- Generate molecular structures separately
- Generate bar chart in matplotlib or Excel
- Composite manually in design software using Midjourney as background/style reference

---

**Tool:** Midjourney v6  
**Difficulty:** Medium (text rendering may be imperfect, expect 3-5 iterations)  
**Recommended:** Best for visual aesthetic, may need manual text overlay
