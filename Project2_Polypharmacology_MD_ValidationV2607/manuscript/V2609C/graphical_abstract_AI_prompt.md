# Graphical Abstract — AI Image Generation Prompt
**Ready to paste into Midjourney / DALL·E / Stable Diffusion / Adobe Firefly / Canva AI / BioRender**

---

## JCIM Technical Requirements (mandatory canvas)

| Parameter | Value |
|---|---|
| Orientation | **Landscape** (horizontal only — portrait rejected by ACS) |
| Final print size | **9.0 cm wide × 3.5 cm tall** (ACS TOC standard for articles) |
| Pixel dimensions at 300 dpi | **≥ 1063 px wide × 414 px tall** |
| Pixel dimensions at 600 dpi (recommended for submission) | **≥ 2126 px wide × 827 px tall** |
| Preferred file format | TIFF (300 dpi) or high-res PNG; PDF also accepted by ACS Paragon |
| Colour space | RGB (sRGB IEC 61966-2.1) |
| Text in image | Minimal; all text must remain legible at print size |
| Portrait orientation | **Not acceptable** |

> **Aspect ratio to request from the AI: 1063 × 414 (≈ 5:2 or 2.57:1).**  
> In Midjourney use `--ar 5:2`. In DALL·E request a wide/landscape crop.

---

## Full Prompt (paste as-is)

```
Create a scientific graphical abstract for a computational chemistry paper titled
"Estimand Divergence: Static Docking Versus Dynamics for Antimalarial Triage",
to be published in the Journal of Chemical Information and Modeling (ACS, JCIM).

Canvas: wide landscape, aspect ratio 5:2. Off-white background (#F8F9FA). Clean,
minimal, journal-quality design. No data plots. No bar charts. No cartoon mosquitoes.
No red blood cells. No atoms shown as spheres. All text is short (≤5 words per label).

The image has four left-to-right panels with no box borders, separated by whitespace only.

PANEL 1 — LEFT (18% of width):
A flat, stylised silhouette of the African continent in muted green (#4E9060).
Below the continent: three small generic polycyclic molecule skeletons drawn as
skeletal line formulae (one flavonoid ring, one indole, one chromone) in dark near-black
(#1A1A2E). Label below: "African NPs · 17 candidates" in small sans-serif font.

PANEL 2 — CENTRE-LEFT (28% of width):
Four simplified protein target icons arranged in a 2×2 grid:
  top-left: a small α-helix ribbon icon labelled "PfDHFR"
  top-right: a small transmembrane channel/barrel icon labelled "PfCRT"
  bottom-left: a small membrane pump icon labelled "PfATP4"
  bottom-right: a small β-barrel icon labelled "PfClpR"
Each icon has a tiny ligand (filled circle) in its pocket.
All icons are in steel grey (#B0B8C4) with dark outlines.
Label below the grid: "136 docking systems · 4 targets"
To the right of the grid, a vertical stack of five small coloured tags:
  A* (deep green #2A9D5C), A (#75C09B), B (#F4C430), C (#E07B39), D (#CC3333)
labelled "RRS classes".

PANEL 3 — CENTRE-RIGHT (36% of width, visual focal point):
A bold amber arrow/fork (#E07B39) splitting into two horizontal lanes.
The fork should be prominent — the largest visual element in the figure.

  UPPER LANE — "Static docking":
    A simplified rigid protein outline in grey (#B0B8C4), no motion.
    Inside the pocket: a ligand shown with a small red downward arrow (▼) indicating
    score penalty.
    Lane label left-aligned in small caps: "Static ΔΔG · penalty predicted"

  LOWER LANE — "Explicit-solvent MD":
    The same protein outline but with faint concentric ripple lines or blurred edges
    suggesting molecular motion, in ACS blue (#3A7DC9).
    Inside the pocket: a ligand shown with a small green tick (✓) indicating retention.
    Lane label left-aligned in small caps: "MD relaxation · pose retained"

  Spanning both lanes, a large bold centre annotation:
    "7/8 states diverge"   [large, #1A1A2E, bold]
    "95% CI: 52.9–97.8%"  [smaller, italic, beneath]

PANEL 4 — RIGHT (18% of width):
Two small candidate indicators stacked vertically:
  Top: a deep green star (★) next to "PP-01 · Class A*" in bold small font
  Bottom: a grey circle next to "PP-02 · Class A" in regular small font
Below both, a downward arrow pointing to a simple flask/beaker icon labelled
"→ Prospective testing"

COLOUR PALETTE:
Background #F8F9FA, African continent #4E9060, static lane #B0B8C4, MD lane #3A7DC9,
fork arrow #E07B39, class A* #2A9D5C, class A #75C09B, class B #F4C430,
class C #E07B39, class D #CC3333, all text #1A1A2E.

Style: clean vector-like scientific illustration. No gradients except very subtle
on the fork arrow. No drop shadows. No neon. No photorealistic elements.
Sans-serif font throughout (e.g., Helvetica, Inter, or similar).
Colourblind-safe palette (deuteranopia-safe green/blue/amber scheme).
```

---

## Variant prompts for specific tools

### Midjourney (append to the prompt above)
```
--ar 5:2 --style raw --stylize 50 --no cartoon, photorealistic, mosquito, 
red blood cell, 3D render, drop shadow, rainbow gradient
```

### DALL·E 3 (system instruction prefix)
```
You are creating a scientific figure for a peer-reviewed chemistry journal.
The image must look like a professional vector illustration, not a photograph.
Avoid any photorealistic rendering. Keep all text labels short and legible.
```

### Stable Diffusion (negative prompt)
```
Negative: photorealistic, 3d render, cartoon, anime, mosquito, parasite,
red blood cell, rainbow, neon, drop shadow, gradient background, bar chart,
scatter plot, molecular surface, atom spheres
```

### BioRender / Canva
For these tools, use the `graphical_abstract_brief.md` layout guide instead
of this prompt. Build each panel manually using their icon libraries and export
at ≥ 300 dpi in landscape TIFF.

---

## Checklist before submission to ACS Paragon+

- [ ] Image is **landscape** (wider than tall)
- [ ] Width ≥ 9.0 cm at 300 dpi (≥ 1063 px)
- [ ] Height ≤ 3.5 cm at 300 dpi (≤ 414 px at 300 dpi, ≤ 827 px at 600 dpi)
- [ ] File is TIFF or high-res PNG, RGB colour space
- [ ] No copyrighted molecular structures or third-party logos
- [ ] All text is original (no reproduction from a published figure)
- [ ] Labels match the manuscript text (no new claims introduced in the image)
- [ ] "7/8 states diverge" is the only quantitative claim shown
- [ ] "95% CI: 52.9–97.8%" subtext is present
- [ ] No "active", "validated", "resistant", "binding energy", "IC50" in the image
- [ ] Class labels read A*, A, B, C, D (not 1–5 or other numbering)
- [ ] PP-01 labelled "Class A*", PP-02 labelled "Class A" — no other claims

---

## What a reviewer or editor reads from this image in 5 seconds

1. The input comes from African natural products screened against four malaria targets.
2. Docking and MD disagree: 7/8 states show divergence.
3. The divergence is the finding — two distinct estimands, not two measurements of the same thing.
4. One lead (PP-01, Class A*) passes the two-target pilot gate.
5. The output is a shortlist for prospective testing, not a validation.

If the image does not communicate all five points unaided (without reading the caption),
it needs revision before submission.
