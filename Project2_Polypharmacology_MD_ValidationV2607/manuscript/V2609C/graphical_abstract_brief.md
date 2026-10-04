# Graphical Abstract — Science Brief
**Paper:** Estimand Divergence: Static Docking Versus Dynamics for Antimalarial Triage  
**Journal:** Journal of Chemical Information and Modeling (JCIM), ACS  
**Version:** V2609C  
**Prepared for:** AI image generator / scientific illustrator  

---

## The one message this image must deliver

Static grid docking and short molecular dynamics simulations disagree directionally in 7 out of 8
matched resistance-mutant states: where docking predicted score penalties, explicit-solvent MD
retained stable binding poses. These are two non-equivalent estimands — not two measurements of
the same thing. The image should show that contrast as a triage decision point.

---

## Mandatory elements (every element that is absent is a failure)

### Panel 1 — INPUT (left third)
- A stylised African continent silhouette (flat, single colour, no map detail)
- Three small molecule structures drawn as skeletal/line formulae (or schematic rings) to represent
  the African natural product chemical space; these are **not** specific compounds — use
  generic polycyclic / flavonoid-style skeletons
- Label: "African Natural Products  n = 17 candidates"

### Panel 2 — DOCKING SCREEN (centre-left)
- Four protein target icons arranged as a 2×2 grid or a small cluster:
  - PfDHFR (label: "PfDHFR")
  - PfCRT  (label: "PfCRT")
  - PfATP4 (label: "PfATP4")
  - PfClpR  (label: "PfClpR")
- Each target icon: a simplified ribbon/cartoon helix or β-sheet stub — no full structure needed
- A small ligand (dot or wedge) docking into each protein pocket
- Label below the cluster: "136 docking systems  AutoDock Vina"
- RRS class badges next to the target cluster: five small coloured tags labelled A*, A, B, C, D
  (no text beyond the letter; use a gradient or colour ramp from green → yellow → red)

### Panel 3 — ESTIMAND DIVERGENCE (centre-right, the visual focal point)
This panel shows the split/fork between the two methods.

- A FORK or two-lane split:
  - **Upper lane** (Static Docking):
    - A rigid protein backbone (grey/pale outline, no movement)
    - A ligand being "repelled" or shown with a downward arrow / red signal
    - Label: "Static ΔΔG  score penalty"
  - **Lower lane** (Explicit-solvent MD):
    - The same protein shown with subtle motion cues (e.g., blurred outline or small motion
      arrows on side chains)
    - The ligand retained in pocket, shown with a tick or stable green signal
    - Label: "MD trajectory  pose retained"
- A bold annotation bridging both lanes:
  **"7/8 states diverge (87.5%)"**
  Subtext in smaller font: "95% CI: 52.9–97.8%"

### Panel 4 — OUTCOME (right third, small)
- Two candidates highlighted:
  - PP-01 with a star ★ and label "Class A*  two-target"
  - PP-02 with a circle and label "Class A  single-target"
- A downward arrow to a flask / beaker icon labelled "Prospective testing"
- No claim of activity, resistance, or binding energy

---

## What must NOT appear

- No numerical Vina scores (e.g., −7.2 kcal/mol) — too technical for a visual abstract
- No structural protein PDB ribbons with atom-level detail — simplified icons only
- No bar charts, scatter plots, or data panels — this is a concept figure, not a results figure
- No text blocks longer than 5 words per label
- No "validated", "confirmed", "active", "resistant" language anywhere in the image
- No molecular dynamics trajectory plots or RMSD curves

---

## Text elements (exact strings to use verbatim)

| Location | Text |
|---|---|
| Top or bottom banner (optional) | "Estimand Divergence: Docking vs. Dynamics" |
| Panel 1 label | "African NPs · 17 candidates" |
| Panel 2 label | "136 docking systems · 4 targets" |
| RRS classes | A* · A · B · C · D |
| Central annotation | "7/8 states diverge" |
| CI subtext | "95% CI: 52.9–97.8%" |
| Lower-left (docking lane) | "Static ΔΔG · penalty predicted" |
| Lower-right (MD lane) | "MD relaxation · pose retained" |
| Outcome | "PP-01 ★ Class A*" |
| Arrow target | "→ Prospective testing" |

---

## Colour palette (JCIM-appropriate, accessible)

| Role | Hex | Use |
|---|---|---|
| African continent | #4E9060 (muted green) | Continental silhouette |
| Docking / static | #B0B8C4 (steel grey) | Rigid structures, upper lane |
| MD / dynamic | #3A7DC9 (ACS-blue) | Motion cues, lower lane |
| Divergence arrow | #E07B39 (amber) | The fork itself |
| Class A* | #2A9D5C (deep green) | Best-class badge |
| Class A | #75C09B (light green) | — |
| Class B | #F4C430 (amber-yellow) | — |
| Class C | #E07B39 (orange) | — |
| Class D | #CC3333 (red) | — |
| Background | #F8F9FA (off-white) | — |
| All text | #1A1A2E (near-black) | — |

This palette is colourblind-safe (deuteranopia-checked) and passes WCAG AA contrast on the
off-white background.

---

## Do NOT use

- Rainbow gradients
- Neon colours
- Drop shadows (or very subtle only)
- Clip art or cartoon-style icons of malaria parasites (no red blood cells, no mosquitoes — this
  is a computational chemistry paper)

---

## Layout guidance

Landscape orientation (mandatory for ACS TOC/graphical abstract).  
Suggested proportional column widths: Panel 1 (18%) | Panel 2 (28%) | Panel 3 (36%) | Panel 4 (18%).  
All four panels share a single baseline and top line; no box borders around panels — use
whitespace as separator.  
The fork in Panel 3 is the visual centre of gravity; make it the largest element.
